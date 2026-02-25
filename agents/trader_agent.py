# -*- coding: utf-8 -*-
"""
Trader Agent - Executes approved trades via the Broker Engine

Responsibility:
    Receive a Risk-Manager-approved signal and commit an actual paper trade
    to the Supabase `transactions` + `portfolios` tables via broker_engine.

Flow:
    1. Verify risk_approval == True
    2. Fetch live price via yfinance
    3. Calculate position size (2% of available cash)
    4. Call broker_engine.execute_order() — real DB writes
    5. Log to agent_logs and update state.trade_status
"""

import sys
import os
# Add project root to path so we can import broker_engine and sentinel_state
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from datetime import datetime
from langchain_core.messages import AIMessage

from sentinel_state import SentinelState
from broker_engine import execute_order as broker_execute_order


# Position sizing — 2% of available cash per trade
MAX_POSITION_SIZE_PERCENT = 0.02


def get_current_price(ticker: str) -> float:
    """
    Fetch the latest closing price for a stock via yfinance.

    Args:
        ticker: Stock symbol, e.g. "RELIANCE.NS"

    Returns:
        float: Current price, or 0.0 on failure.
    """
    try:
        data = yf.Ticker(ticker).history(period="1d")
        if data.empty:
            return 0.0
        return float(data["Close"].iloc[-1])
    except Exception as e:
        print(f"Trader: Price fetch error for {ticker} — {e}")
        return 0.0


def calculate_position_size(cash: float, price: float, max_pct: float = MAX_POSITION_SIZE_PERCENT) -> int:
    """
    Determine how many whole shares to buy without exceeding max_pct of cash.

    Returns at least 1 share (position-size floor).
    """
    if price <= 0:
        return 0
    shares = int((cash * max_pct) / price)
    return max(shares, 1)


def trader_node(state: SentinelState) -> SentinelState:
    """
    Trader Agent node — wired to broker_engine for real Supabase accounting.

    When risk_approval is True:
        - Gets live price
        - Calls broker_engine.execute_order() → writes to Supabase
        - Updates state.trade_status = "EXECUTED" or "FAILED"

    When risk_approval is False:
        - Sets state.trade_status = "REJECTED" and returns immediately.

    Args:
        state: Current SentinelState (must have user_id set)

    Returns:
        Updated SentinelState
    """

    _bc = state.get('broadcast_callback')

    # --- Guard: only proceed if Risk Manager approved ---
    if not state.get("risk_approval", False):
        state["trade_status"] = "REJECTED"
        state["messages"].append(
            AIMessage(content="Trader: Trade BLOCKED — Risk Manager did not approve.")
        )
        print("Trader: Blocked by Risk Manager.")
        return state

    ticker      = state.get("current_ticker", "")
    signal_data = state.get("analyst_signal", {})
    portfolio   = state.get("portfolio_snapshot", {})
    user_id     = state.get("user_id", "demo_user")
    signal      = signal_data.get("signal", "WAIT")

    print(f"Trader: Executing {signal} order for {ticker} (user={user_id})...")
    if _bc:
        _bc("Trader", f"💰 Executing {signal} order for {ticker.replace('.NS','')}...")

    try:
        # 1. Fetch live price
        current_price = get_current_price(ticker)

        if current_price <= 0:
            state["trade_status"] = "FAILED"
            state["errors"].append(f"Trader: Could not fetch live price for {ticker}")
            state["messages"].append(
                AIMessage(content=f"Trader: FAILED — could not fetch live price for {ticker}.")
            )
            print(f"Trader: Price fetch failed for {ticker}.")
            return state

        # 2. Calculate position size from portfolio cash
        cash     = portfolio.get("cash", 100000)
        quantity = calculate_position_size(cash, current_price, MAX_POSITION_SIZE_PERCENT)

        if quantity <= 0:
            state["trade_status"] = "FAILED"
            state["errors"].append(f"Trader: Position size calculated as 0 for {ticker}")
            state["messages"].append(
                AIMessage(content=f"Trader: FAILED — calculated position size is 0.")
            )
            return state

        # 3. Execute via Broker Engine (real Supabase writes)
        result = broker_execute_order(
            user_id=user_id,
            ticker=ticker,
            side=signal,          # "BUY" (SELL signals go through same path)
            quantity=quantity,
            current_price=current_price,
        )

        ticker_clean = ticker.replace(".NS", "").replace(".BO", "")

        if result["success"]:
            # 4a. Success path
            state["trade_status"] = "EXECUTED"
            state["messages"].append(
                AIMessage(
                    content=(
                        f"Trader: ✅ EXECUTED {signal} | "
                        f"{ticker_clean} × {quantity} @ ₹{current_price:,.2f} | "
                        f"{result['message']}"
                    )
                )
            )
            # Persist order detail in state for downstream inspection
            state["executed_order"] = result.get("order", {})
            print(f"Trader: ✅ {result['message']}")
            if _bc:
                _bc("Trader", f"✅ {signal} {ticker_clean} × {quantity} @ ₹{current_price:,.2f}")
        else:
            # 4b. Broker rejected the order (insufficient funds, no position, etc.)
            state["trade_status"] = "FAILED"
            state["errors"].append(f"Trader: Broker rejected — {result['message']}")
            state["messages"].append(
                AIMessage(
                    content=f"Trader: FAILED — {result['message']}"
                )
            )
            print(f"Trader: Broker rejected order — {result['message']}")

    except Exception as e:
        state["trade_status"] = "FAILED"
        state["errors"].append(f"Trader unexpected error: {str(e)}")
        state["messages"].append(
            AIMessage(content=f"Trader: FAILED — unexpected error: {str(e)}")
        )
        print(f"Trader: Unexpected error — {e}")

    return state


# ---------------------------------------------------------------------------
# Quick standalone test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from sentinel_state import create_initial_state

    print("=== Trader Agent Standalone Test ===\n")

    # Test 1: Approved trade (will hit broker engine — needs Supabase or will fail gracefully)
    print("Test 1: Approved BUY")
    s = create_initial_state()
    s["current_ticker"]    = "RELIANCE.NS"
    s["risk_approval"]     = True
    s["analyst_signal"]    = {"signal": "BUY", "confidence": 0.85}
    s["portfolio_snapshot"] = {"cash": 100000}
    s["user_id"]           = "demo_user"

    result = trader_node(s)
    print(f"  trade_status : {result['trade_status']}")
    print(f"  last message : {result['messages'][-1].content if result['messages'] else 'none'}")

    # Test 2: Risk-rejected
    print("\nTest 2: Risk Rejected")
    s2 = create_initial_state()
    s2["risk_approval"] = False
    result2 = trader_node(s2)
    print(f"  trade_status : {result2['trade_status']}")

    print("\n✅ Tests complete.")
