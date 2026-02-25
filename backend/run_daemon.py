# -*- coding: utf-8 -*-
"""
Sentinel Autonomous Trading Daemon
====================================
Runs indefinitely as a background process.

Behaviour:
  - Checks if NSE is open (09:15–15:30 IST, Mon–Fri)
  - If CLOSED  → sleeps 15 minutes, then checks again
  - If OPEN    → fetches all users with auto_trade_enabled=True from Supabase
              → runs one full LangGraph workflow cycle per user
              → sleeps 5 minutes, then repeats

Fault tolerance:
  - A Gemini/yfinance API timeout for one user never crashes the daemon
  - A Supabase outage falls back to a single demo_user
  - An unexpected top-level exception sleeps 60 s then retries forever

Usage:
    python backend/run_daemon.py
"""

import sys
import os
import time
from datetime import datetime

# Add project root to sys.path so we can import sentinel_hive, broker_engine, etc.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import pytz

from sentinel_hive import run_workflow
from sentinel_state import create_initial_state


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IST = pytz.timezone("Asia/Kolkata")

MARKET_OPEN  = (9,  15)   # (hour, minute)
MARKET_CLOSE = (15, 30)   # (hour, minute)

CYCLE_SLEEP_SEC  = 300    # 5 minutes between active trading cycles
CLOSED_SLEEP_SEC = 900    # 15 minutes when market is closed
ERROR_SLEEP_SEC  = 60     # Safety pause after an unexpected top-level crash


# ---------------------------------------------------------------------------
# Market hours
# ---------------------------------------------------------------------------

def is_market_open() -> bool:
    """
    Returns True if NSE is currently open for trading.

    Rules:
        - Monday–Friday only (weekday() 0–4)
        - 09:15 IST  <=  now  <  15:30 IST
    """
    now     = datetime.now(IST)
    weekday = now.weekday()          # 0 = Monday … 6 = Sunday

    if weekday >= 5:                 # Saturday or Sunday
        return False

    current  = now.hour * 60 + now.minute
    opens_at = MARKET_OPEN[0]  * 60 + MARKET_OPEN[1]
    closes_at = MARKET_CLOSE[0] * 60 + MARKET_CLOSE[1]

    return opens_at <= current < closes_at


def time_until_open_minutes() -> int:
    """
    Return minutes until the next NSE open (useful for smarter sleep).
    Returns 0 if the market is currently open.
    """
    now      = datetime.now(IST)
    opens_at = now.replace(hour=MARKET_OPEN[0], minute=MARKET_OPEN[1], second=0, microsecond=0)

    if now >= opens_at:
        # Already past open — next open is tomorrow (or Monday)
        from datetime import timedelta
        opens_at += timedelta(days=1)

    diff = (opens_at - now).total_seconds() / 60
    return max(int(diff), 0)


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

def get_active_users() -> list:
    """
    Fetch the list of user_ids that have opted-in to autonomous trading.

    Queries the `profiles` table for rows where auto_trade_enabled = True.
    Falls back to ["demo_user"] if:
        - Supabase is unconfigured / unreachable
        - The `profiles` table doesn't exist yet
        - No users have enabled auto-trading
    """
    try:
        from dashboard_v3 import auth_manager as auth
        client = auth.get_client()

        resp = (
            client.table("profiles")
            .select("user_id")
            .eq("auto_trade_enabled", True)
            .execute()
        )
        users = [row["user_id"] for row in (resp.data or []) if row.get("user_id")]

        if not users:
            print("Daemon: No auto-trade users found in Supabase — running in demo mode.")
            return ["demo_user"]

        return users

    except Exception as e:
        print(f"Daemon: Could not fetch users ({e}) — running in demo mode.")
        return ["demo_user"]


# ---------------------------------------------------------------------------
# Per-user cycle
# ---------------------------------------------------------------------------

def run_cycle_for_user(user_id: str) -> None:
    """
    Execute one full Sentinel workflow (Scout → Analyst → Risk → Trader)
    for the given user.

    Any exception is caught and printed — it must never crash the daemon.
    """
    print(f"  Daemon: Starting cycle for user={user_id} ...")
    try:
        # 1. Build initial state
        state = create_initial_state()
        state["user_id"] = user_id

        # 2. Hydrate portfolio from Supabase so the Risk Manager has real cash figures
        try:
            from dashboard_v3 import auth_manager as auth
            portfolio = auth.get_user_portfolio(user_id)
            if portfolio.get("success"):
                state["portfolio_snapshot"] = {
                    "cash":      portfolio.get("cash", 100000),
                    "positions": portfolio.get("positions", []),
                    "orders":    portfolio.get("orders", []),
                }
                print(f"  Daemon: Portfolio loaded — cash ₹{state['portfolio_snapshot']['cash']:,.2f}")
        except Exception as e:
            print(f"  Daemon: Portfolio load failed ({e}) — using ₹1,00,000 default.")

        # 3. Run the LangGraph workflow
        final_state = run_workflow(state)

        # 4. Report outcome
        ticker       = final_state.get("current_ticker", "N/A")
        trade_status = final_state.get("trade_status",   "UNKNOWN")
        signal       = final_state.get("analyst_signal", {}).get("signal", "N/A")
        confidence   = final_state.get("analyst_signal", {}).get("confidence", 0.0)
        errors       = final_state.get("errors", [])

        print(
            f"  Daemon: Cycle done — user={user_id} | "
            f"ticker={ticker} | signal={signal} ({confidence:.0%}) | "
            f"trade_status={trade_status} | errors={len(errors)}"
        )
        if errors:
            for err in errors[-3:]:   # Show last 3 errors max
                print(f"    ⚠  {err}")

    except Exception as e:
        # CRITICAL: Swallow all exceptions so one user never stops the daemon
        print(f"  Daemon: ❌ Cycle FAILED for user={user_id} — {e}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("=" * 60)
    print("    SENTINEL AUTONOMOUS TRADING DAEMON")
    print("    Project Sentinel — Auto-Trade Engine v1.0")
    print("=" * 60)
    print(f"  Market open  : {MARKET_OPEN[0]:02d}:{MARKET_OPEN[1]:02d} IST")
    print(f"  Market close : {MARKET_CLOSE[0]:02d}:{MARKET_CLOSE[1]:02d} IST")
    print(f"  Cycle sleep  : {CYCLE_SLEEP_SEC // 60} min")
    print(f"  Closed sleep : {CLOSED_SLEEP_SEC // 60} min")
    print("=" * 60)
    print()

    cycle_count = 0

    while True:
        try:
            now_str = datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")

            # ----------------------------------------------------------------
            # Market closed — wait and retry
            # ----------------------------------------------------------------
            if not is_market_open():
                print(f"[{now_str}] Market CLOSED — sleeping {CLOSED_SLEEP_SEC // 60} min ...")
                time.sleep(CLOSED_SLEEP_SEC)
                continue

            # ----------------------------------------------------------------
            # Market open — run one cycle for every opted-in user
            # ----------------------------------------------------------------
            cycle_count += 1
            print(f"\n[{now_str}] ═══ CYCLE #{cycle_count} ═══")

            active_users = get_active_users()
            print(f"Daemon: {len(active_users)} active user(s): {active_users}")

            for user_id in active_users:
                run_cycle_for_user(user_id)

            # Sleep between cycles to respect Gemini / yfinance rate limits
            next_str = datetime.now(IST).strftime("%H:%M:%S IST")
            print(f"\nDaemon: Cycle #{cycle_count} complete @ {next_str}. "
                  f"Next cycle in {CYCLE_SLEEP_SEC // 60} min ...")
            time.sleep(CYCLE_SLEEP_SEC)

        except KeyboardInterrupt:
            print("\nDaemon: ^C received — shutting down cleanly.")
            break

        except Exception as top_err:
            # Top-level safety net — the daemon NEVER dies from an unexpected error
            print(f"\nDaemon: ⚠ Unexpected top-level error — {top_err}")
            print(f"Daemon: Retrying in {ERROR_SLEEP_SEC} seconds ...")
            time.sleep(ERROR_SLEEP_SEC)


if __name__ == "__main__":
    main()
