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

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone

BROKERAGE_PERCENT = 0.0003  # 0.03% — mirrors the existing trade executor in main.py

# Error codes raised by the execute_trade_atomic() Postgres function
# (see supabase_setup.sql) and recognized here to produce friendly messages.
_KNOWN_RPC_ERRORS = (
    "insufficient_funds",
    "insufficient_shares",
    "portfolio_not_found",
    "invalid_side",
    "invalid_quantity",
    "invalid_price",
    "unauthorized",
)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _get_client():
    """Lazily import to avoid circular dependencies at module load time."""
    from services import auth_manager as auth
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
        .eq("status", "EXECUTED")
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


def _extract_rpc_error_code(err: Exception) -> str | None:
    """
    The execute_trade_atomic() Postgres function signals failures by raising
    a plain EXCEPTION whose message is one of _KNOWN_RPC_ERRORS. supabase-py
    surfaces this as some flavor of PostgrestAPIError whose exact shape
    varies by version, so match on the stringified error instead of a
    specific exception type/attribute.
    """
    err_str = str(err)
    for code in _KNOWN_RPC_ERRORS:
        if code in err_str:
            return code
    return None


def _execute_trade_atomic(client, user_id: str, ticker: str, side: str, quantity: float, price: float, brokerage: float) -> dict:
    """
    Calls the execute_trade_atomic() Postgres function (see
    supabase_setup.sql), which locks the user's portfolio row, validates
    funds/holdings, inserts the transaction, and updates cash_balance — all
    inside one database transaction. This is what actually closes the
    check-then-act race between reading a balance/position and writing the
    result of a trade against it.

    Returns {"new_cash_balance": float, "transaction_id": str}.
    Raises RuntimeError with one of _KNOWN_RPC_ERRORS as the message on a
    recognized failure (insufficient funds/shares/etc), or re-raises the
    original exception for anything unexpected.
    """
    try:
        resp = client.rpc("execute_trade_atomic", {
            "p_user_id": user_id,
            "p_ticker": ticker,
            "p_side": side,
            "p_qty": quantity,
            "p_price": price,
            "p_brokerage": brokerage,
        }).execute()
    except Exception as rpc_err:
        code = _extract_rpc_error_code(rpc_err)
        if code:
            raise RuntimeError(code) from rpc_err
        raise

    rows = resp.data or []
    if not rows:
        raise RuntimeError("execute_trade_atomic returned no rows")
    row = rows[0] if isinstance(rows, list) else rows
    return {
        "new_cash_balance": float(row["new_cash_balance"]),
        "transaction_id": row.get("transaction_id"),
    }


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
    Execute a paper trade with strict, atomic accounting against Supabase.

    The actual balance check, transaction insert, and cash_balance update
    all happen inside a single Postgres function call (execute_trade_atomic,
    defined in supabase_setup.sql) that locks the user's portfolio row for
    its duration. This prevents two concurrent trades for the same user
    from both reading a stale cash/position value and producing a lost
    update (overspend) or an oversold position.

    Args:
        user_id:       Supabase user UUID (or "demo_user" for paper mode)
        ticker:        Stock symbol, e.g. "RELIANCE.NS"
        side:          "BUY" or "SELL"
        quantity:      Number of whole shares (must be a positive integer)
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
    if quantity != int(quantity):
        return {"success": False, "message": f"Quantity must be a whole number of shares, got {quantity}", "order": None}
    if current_price <= 0:
        return {"success": False, "message": f"Price must be > 0, got {current_price}", "order": None}

    try:
        client        = _get_client()
        gross_value   = round(quantity * current_price, 2)
        brokerage     = round(gross_value * BROKERAGE_PERCENT, 2)
        exec_ts       = datetime.now(timezone.utc).isoformat()

        try:
            result = _execute_trade_atomic(client, user_id, ticker, side, quantity, current_price, brokerage)
        except RuntimeError as atomic_err:
            code = str(atomic_err)
            if code == "insufficient_funds":
                total_debit = round(gross_value + brokerage, 2)
                cash = _get_cash_balance(client, user_id)
                msg = (
                    f"Insufficient funds to BUY {quantity}x {ticker}: "
                    f"need ₹{total_debit:,.2f}, have ₹{cash:,.2f}"
                )
            elif code == "insufficient_shares":
                held_qty = _get_position_qty(client, user_id, ticker)
                msg = (
                    f"Insufficient holdings to SELL {quantity}x {ticker}: "
                    f"only {held_qty:.0f} shares held"
                )
            elif code == "portfolio_not_found":
                msg = f"No portfolio found for user_id={user_id!r}"
            else:
                msg = f"Trade rejected: {code}"
            print(f"BrokerEngine: {msg}")
            return {"success": False, "message": msg, "order": None}

        new_cash = result["new_cash_balance"]

        if side == "BUY":
            total_debit = round(gross_value + brokerage, 2)
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
        else:
            net_proceeds = round(gross_value - brokerage, 2)
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
        _log_agent_action(client, user_id, msg, action_type=side)
        return {"success": True, "message": msg, "order": order}

    except Exception as e:
        print(f"BrokerEngine: execute_order failed — {e}")
        return {"success": False, "message": f"Broker error: {str(e)}", "order": None}
