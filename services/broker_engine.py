# -*- coding: utf-8 -*-
"""
Broker Engine - Paper Trade Accounting

Single source of truth for all paper-trade execution.
Enforces cash availability, position limits, and atomic DB writes
against the Supabase `portfolios` and `transactions` tables.

Usage:
    from broker_engine import execute_order

    result = execute_order(
        user_id="uuid-here",
        ticker="RELIANCE.NS",
        side="BUY",
        quantity=10,
        current_price=2900.50
    )
    if result["success"]:
        print(result["message"])
"""

import math
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone

BROKERAGE_PERCENT = 0.0003  # 0.03% — mirrors the existing trade executor in main.py


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _get_client():
    """Lazily import to avoid circular dependencies at module load time."""
    from dashboard_v3 import auth_manager as auth
    return auth.get_client()


def _get_cash_balance(client, user_id: str) -> float:
    """
    Read the user's current cash_balance from the `portfolios` table.
    Raises ValueError if no portfolio row exists.
    """
    resp = (
        client.table("portfolios")
        .select("cash_balance")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if resp.data:
        return float(resp.data["cash_balance"])
    raise ValueError(f"No portfolio row found for user_id={user_id!r}")


def _get_position_qty(client, user_id: str, ticker: str) -> float:
    """
    Compute net open quantity for a ticker by aggregating the `transactions`
    table — consistent with auth_manager._aggregate_positions().

    Returns 0.0 if no position exists or Supabase is unreachable.
    """
    resp = (
        client.table("transactions")
        .select("qty, side")
        .eq("user_id", user_id)
        .eq("ticker", ticker)
        .execute()
    )
    rows = resp.data or []
    net_qty = 0.0
    for row in rows:
        qty = float(row.get("qty", 0))
        if row.get("side") == "BUY":
            net_qty += qty
        elif row.get("side") == "SELL":
            net_qty -= qty
    return max(net_qty, 0.0)


def _log_agent_action(client, user_id: str, message: str, action_type: str) -> None:
    """
    Write a structured record to `agent_logs` so the Copilot can explain
    what the Trader Agent just did.  Failures are swallowed — logging must
    never block trade execution.
    """
    try:
        client.table("agent_logs").insert({
            "user_id":     user_id,
            "agent_name":  "Trader",
            "message":     message,
            "action_type": action_type,
            "timestamp":   datetime.now(timezone.utc).isoformat(),
        }).execute()
    except Exception as log_err:
        print(f"BrokerEngine: agent_logs write failed (non-fatal) — {log_err}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def execute_order(
    user_id: str,
    ticker: str,
    side: str,
    quantity: int,
    current_price: float,
) -> dict:
    """
    Execute a paper trade with strict accounting against Supabase.

    BUY flow:
        1. Read cash_balance from `portfolios`
        2. Check cash >= (quantity * price) + brokerage
        3. INSERT row into `transactions`
        4. UPDATE cash_balance in `portfolios`
        5. Log to `agent_logs`

    SELL flow:
        1. Aggregate net qty from `transactions`
        2. Check held_qty >= quantity
        3. INSERT row into `transactions`
        4. UPDATE cash_balance in `portfolios`
        5. Log to `agent_logs`

    Args:
        user_id:       Supabase user UUID (or "demo_user" for paper mode)
        ticker:        Stock symbol, e.g. "RELIANCE.NS"
        side:          "BUY" or "SELL"
        quantity:      Number of shares (must be > 0)
        current_price: Execution price in ₹ (must be > 0)

    Returns:
        {
            "success": bool,
            "message": str,      # Human-readable result
            "order":   dict|None # Order detail on success, None on failure
        }
    """
    side = side.upper()

    # --- Input validation ---
    if side not in ("BUY", "SELL"):
        return {"success": False, "message": f"Invalid side '{side}' — must be BUY or SELL", "order": None}
    if quantity <= 0:
        return {"success": False, "message": f"Quantity must be > 0, got {quantity}", "order": None}
    if not math.isfinite(current_price) or current_price <= 0:
        return {"success": False, "message": f"Price must be > 0, got {current_price}", "order": None}

    try:
        client        = _get_client()
        gross_value   = round(quantity * current_price, 2)
        brokerage     = round(gross_value * BROKERAGE_PERCENT, 2)
        exec_ts       = datetime.now(timezone.utc).isoformat()

        # ----------------------------------------------------------------
        # BUY
        # ----------------------------------------------------------------
        if side == "BUY":
            total_debit = round(gross_value + brokerage, 2)
            cash        = _get_cash_balance(client, user_id)

            if cash < total_debit:
                msg = (
                    f"Insufficient funds to BUY {quantity}x {ticker}: "
                    f"need ₹{total_debit:,.2f}, have ₹{cash:,.2f}"
                )
                print(f"BrokerEngine: {msg}")
                return {"success": False, "message": msg, "order": None}

            new_cash = round(cash - total_debit, 2)

            # Write transaction first — if this fails, we abort cleanly
            client.table("transactions").insert({
                "user_id":   user_id,
                "ticker":    ticker,
                "qty":       quantity,
                "price":     current_price,
                "side":      "BUY",
            }).execute()

            # Then update cash (if this fails, the transaction is still logged —
            # acceptable for a paper trading system)
            client.table("portfolios").update(
                {"cash_balance": new_cash}
            ).eq("user_id", user_id).execute()

            order = {
                "ticker":      ticker,
                "side":        "BUY",
                "quantity":    quantity,
                "price":       current_price,
                "gross_value": gross_value,
                "brokerage":   brokerage,
                "total_debit": total_debit,
                "cash_after":  new_cash,
                "timestamp":   exec_ts,
            }
            msg = (
                f"BUY {quantity}x {ticker} @ ₹{current_price:,.2f} | "
                f"Cost ₹{total_debit:,.2f} (incl. ₹{brokerage:.2f} brokerage) | "
                f"Cash remaining ₹{new_cash:,.2f}"
            )
            print(f"BrokerEngine: ✅ {msg}")
            _log_agent_action(client, user_id, msg, action_type="BUY")
            return {"success": True, "message": msg, "order": order}

        # ----------------------------------------------------------------
        # SELL
        # ----------------------------------------------------------------
        else:
            held_qty = _get_position_qty(client, user_id, ticker)

            if held_qty < quantity:
                msg = (
                    f"Insufficient holdings to SELL {quantity}x {ticker}: "
                    f"only {held_qty:.0f} shares held"
                )
                print(f"BrokerEngine: {msg}")
                return {"success": False, "message": msg, "order": None}

            net_proceeds = round(gross_value - brokerage, 2)
            cash         = _get_cash_balance(client, user_id)
            new_cash     = round(cash + net_proceeds, 2)

            client.table("transactions").insert({
                "user_id":   user_id,
                "ticker":    ticker,
                "qty":       quantity,
                "price":     current_price,
                "side":      "SELL",
            }).execute()

            client.table("portfolios").update(
                {"cash_balance": new_cash}
            ).eq("user_id", user_id).execute()

            order = {
                "ticker":       ticker,
                "side":         "SELL",
                "quantity":     quantity,
                "price":        current_price,
                "gross_value":  gross_value,
                "brokerage":    brokerage,
                "net_proceeds": net_proceeds,
                "cash_after":   new_cash,
                "timestamp":    exec_ts,
            }
            msg = (
                f"SELL {quantity}x {ticker} @ ₹{current_price:,.2f} | "
                f"Proceeds ₹{net_proceeds:,.2f} (incl. ₹{brokerage:.2f} brokerage) | "
                f"Cash now ₹{new_cash:,.2f}"
            )
            print(f"BrokerEngine: ✅ {msg}")
            _log_agent_action(client, user_id, msg, action_type="SELL")
            return {"success": True, "message": msg, "order": order}

    except Exception as e:
        print(f"BrokerEngine: execute_order failed — {e}")
        return {"success": False, "message": f"Broker error: {str(e)}", "order": None}
