# -*- coding: utf-8 -*-
"""
Auth Manager - Supabase Authentication & Database Module
Handles all user authentication and database operations for Project Sentinel
"""

import os
try:
    import streamlit as st
except ImportError:
    st = None  # Optional when running FastAPI backend (no Streamlit)
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------
# Startup Check — fail fast if env vars are missing
# ----------------------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # Don't crash at import — let the UI show a friendly error
    _supabase_client = None
else:
    try:
        from supabase import create_client
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        _supabase_client = None


def get_client():
    """Return Supabase client or raise if not configured."""
    if _supabase_client is None:
        raise RuntimeError(
            "Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY "
            "in your environment variables (Railway dashboard or .env file)."
        )
    return _supabase_client


# ----------------------------------------------------------------
# AUTH METHODS
# ----------------------------------------------------------------

def sign_up(email: str, password: str, full_name: str) -> dict:
    """
    Register a new user via Supabase Auth.
    The on_auth_user_created trigger auto-creates their portfolio row.

    Returns:
        dict: {"success": True, "user": ...} or {"success": False, "error": "..."}
    """
    try:
        client = get_client()
        response = client.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}}
        })
        if response.user:
            return {"success": True, "user": response.user}
        return {"success": False, "error": "Sign up failed — no user returned."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_in(email: str, password: str) -> dict:
    """
    Authenticate an existing user.

    Returns:
        dict: {"success": True, "user": ..., "session": ...} or {"success": False, "error": "..."}
    """
    try:
        client = get_client()
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user:
            return {
                "success": True,
                "user": response.user,
                "session": response.session
            }
        return {"success": False, "error": "Invalid credentials."}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_out() -> None:
    """Sign out the current user and clear Streamlit session."""
    try:
        client = get_client()
        client.auth.sign_out()
    except Exception:
        pass
    if st is not None:
        for key in ["user_id", "user_email", "user_name", "authenticated"]:
            st.session_state.pop(key, None)


# ----------------------------------------------------------------
# DATABASE METHODS
# ----------------------------------------------------------------

def initialize_user_portfolio(user_id: str) -> dict:
    """
    Called automatically on sign-up (via Supabase trigger),
    but can also be called manually as a fallback.

    Inserts an initial portfolio row with ₹1,00,000 virtual cash.
    """
    try:
        client = get_client()
        client.table("portfolios").upsert({
            "user_id": user_id,
            "cash_balance": 100000.0
        }, on_conflict="user_id").execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_user_portfolio(user_id: str) -> dict:
    """
    Fetch the user's portfolio from Supabase.

    Returns:
        dict: {
            "cash": float,
            "positions": list,   # from transactions table (aggregated)
            "orders": list       # raw transaction history
        }
    """
    try:
        client = get_client()

        # Get cash balance
        portfolio_resp = client.table("portfolios").select("cash_balance").eq(
            "user_id", user_id
        ).single().execute()
        cash = portfolio_resp.data["cash_balance"] if portfolio_resp.data else 100000.0

        # Get transaction history
        tx_resp = client.table("transactions").select("*").eq(
            "user_id", user_id
        ).order("timestamp", desc=True).limit(100).execute()
        orders = tx_resp.data or []

        # Aggregate positions from transactions
        positions = _aggregate_positions(orders)

        return {
            "success": True,
            "cash": cash,
            "positions": positions,
            "orders": orders
        }
    except Exception as e:
        # Fallback to session state if DB is unavailable
        return {
            "success": False,
            "error": str(e),
            "cash": 100000.0,
            "positions": [],
            "orders": []
        }


def update_cash_balance(user_id: str, new_balance: float) -> dict:
    """Update the user's cash balance after a trade."""
    try:
        client = get_client()
        client.table("portfolios").update(
            {"cash_balance": new_balance}
        ).eq("user_id", user_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def log_transaction(user_id: str, ticker: str, qty: float, price: float, side: str) -> dict:
    """
    Write a trade to the Supabase transactions table.

    Args:
        user_id: The authenticated user's UUID
        ticker: Stock symbol e.g. "RELIANCE.NS"
        qty: Number of shares
        price: Execution price
        side: "BUY" or "SELL"
    """
    try:
        client = get_client()
        client.table("transactions").insert({
            "user_id": user_id,
            "ticker": ticker,
            "qty": qty,
            "price": price,
            "side": side
        }).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


# ----------------------------------------------------------------
# HELPERS
# ----------------------------------------------------------------

def _aggregate_positions(orders: list) -> list:
    """
    Aggregate raw transaction rows into net open positions.
    BUYs increase quantity, SELLs decrease it.
    """
    holdings = {}

    for order in reversed(orders):  # Chronological order
        ticker = order["ticker"]
        qty = float(order["qty"])
        price = float(order["price"])
        side = order["side"]

        if ticker not in holdings:
            holdings[ticker] = {"symbol": ticker, "quantity": 0, "average_price": 0.0, "cost_basis": 0.0}

        if side == "BUY":
            h = holdings[ticker]
            new_cost = h["cost_basis"] + (qty * price)
            new_qty = h["quantity"] + qty
            holdings[ticker]["quantity"] = new_qty
            holdings[ticker]["cost_basis"] = new_cost
            holdings[ticker]["average_price"] = new_cost / new_qty if new_qty > 0 else 0

        elif side == "SELL":
            holdings[ticker]["quantity"] = max(0, holdings[ticker]["quantity"] - qty)

    # Return only positions with qty > 0
    return [
        {"symbol": h["symbol"], "quantity": h["quantity"], "average_price": h["average_price"], "current_price": h["average_price"]}
        for h in holdings.values() if h["quantity"] > 0
    ]


def is_configured() -> bool:
    """Check if Supabase env vars are set."""
    return bool(SUPABASE_URL and SUPABASE_KEY)
