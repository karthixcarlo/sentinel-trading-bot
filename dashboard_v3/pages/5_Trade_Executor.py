# -*- coding: utf-8 -*-
"""
Trade Executor - Writes trades to Supabase transactions table
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout import setup_page_config, render_navigation, apply_groww_theme
import auth_manager as auth

setup_page_config("Trade Executor", "⚡")
apply_groww_theme()
render_navigation()

# ── Auth guard ─────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    st.warning("Please log in to trade.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

st.title("Trade Executor")

user_id = st.session_state["user_id"]

# Fetch live portfolio from Supabase
with st.spinner("Loading portfolio..."):
    portfolio = auth.get_user_portfolio(user_id)

cash = portfolio.get("cash", 0.0)
positions = portfolio.get("positions", [])

total_holdings = sum(
    p.get("quantity", 0) * p.get("current_price", p.get("average_price", 0))
    for p in positions
)
portfolio_value = cash + total_holdings

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Cash Available", f"₹{cash:,.2f}", border=True)
    with col2:
        st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}", border=True)
    with col3:
        st.metric("Active Positions", len(positions), border=True)

st.markdown("---")
st.subheader("Place Order")

default_stock = st.session_state.get("selected_stock", "")
if default_stock:
    default_stock = default_stock.replace(".NS", "")

with st.form("trade_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Stock Symbol", value=default_stock, placeholder="e.g., RELIANCE, TCS")
    with col2:
        side = st.radio("Action", ["BUY", "SELL"], horizontal=True)

    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])

    if order_type == "LIMIT":
        limit_price = st.number_input("Limit Price (₹)", min_value=0.01, value=100.0, step=0.01)
    else:
        limit_price = 0

    submitted = st.form_submit_button("Place Order", type="primary", use_container_width=True)

    if submitted:
        if not symbol:
            st.error("Please enter a stock symbol.")
        else:
            full_symbol = f"{symbol}.NS" if not symbol.endswith(".NS") else symbol

            # Fetch market price for MARKET orders
            if order_type == "MARKET":
                try:
                    import yfinance as yf
                    ticker_obj = yf.Ticker(full_symbol)
                    hist = ticker_obj.history(period="1d")
                    if hist.empty:
                        st.error(f"Could not fetch price for {symbol}. Use LIMIT order.")
                        st.stop()
                    limit_price = float(hist["Close"].iloc[-1])
                except Exception as e:
                    st.error(f"Price fetch failed: {e}. Use LIMIT order.")
                    st.stop()

            total_cost = quantity * limit_price
            brokerage = total_cost * 0.0003
            final_cost = total_cost + brokerage

            if side == "BUY":
                if cash < final_cost:
                    st.error(f"Insufficient funds! Available: ₹{cash:,.2f}, Required: ₹{final_cost:,.2f}")
                else:
                    new_cash = cash - final_cost

                    # Write trade to Supabase
                    tx_result = auth.log_transaction(user_id, full_symbol, quantity, limit_price, "BUY")
                    cash_result = auth.update_cash_balance(user_id, new_cash)

                    if tx_result["success"] and cash_result["success"]:
                        st.success(f"BUY order executed: {quantity} × {symbol} @ ₹{limit_price:,.2f}")
                        st.balloons()
                        st.toast(f"Bought {quantity} shares of {symbol}")
                        st.rerun()
                    else:
                        err = tx_result.get("error") or cash_result.get("error")
                        st.error(f"Trade failed to save: {err}")

            elif side == "SELL":
                existing_pos = next(
                    (p for p in positions if p["symbol"] == full_symbol), None
                )

                if not existing_pos:
                    st.error(f"You don't own any shares of {symbol}.")
                elif existing_pos.get("quantity", 0) < quantity:
                    st.error(
                        f"Insufficient shares. You have {existing_pos['quantity']}, "
                        f"trying to sell {quantity}."
                    )
                else:
                    proceeds = total_cost - brokerage
                    new_cash = cash + proceeds

                    tx_result = auth.log_transaction(user_id, full_symbol, quantity, limit_price, "SELL")
                    cash_result = auth.update_cash_balance(user_id, new_cash)

                    if tx_result["success"] and cash_result["success"]:
                        st.success(f"SELL order executed: {quantity} × {symbol} @ ₹{limit_price:,.2f}")
                        st.balloons()
                        st.toast(f"Sold {quantity} shares of {symbol}")
                        st.rerun()
                    else:
                        err = tx_result.get("error") or cash_result.get("error")
                        st.error(f"Trade failed to save: {err}")

st.markdown("---")
st.caption("All trades are paper trades. No real money is involved.")
