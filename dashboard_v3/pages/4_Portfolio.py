# -*- coding: utf-8 -*-
"""
Portfolio - Persistent multi-tenant portfolio from Supabase
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout import setup_page_config, render_navigation, apply_groww_theme
import auth_manager as auth

setup_page_config("Portfolio", "💼")
apply_groww_theme()
render_navigation()

# ── Auth guard ─────────────────────────────────────────────────
if not st.session_state.get("authenticated"):
    st.warning("Please log in to view your portfolio.")
    if st.button("Go to Login"):
        st.switch_page("Home.py")
    st.stop()

st.title("Portfolio")

user_id = st.session_state["user_id"]

with st.spinner("Loading your portfolio..."):
    portfolio = auth.get_user_portfolio(user_id)

if not portfolio.get("success"):
    st.error(f"Could not load portfolio: {portfolio.get('error')}")
    st.info("Showing cached data if available.")

cash = portfolio.get("cash", 0.0)
positions = portfolio.get("positions", [])
orders = portfolio.get("orders", [])

# ── Summary metrics ─────────────────────────────────────────────
total_holdings_value = 0
for pos in positions:
    total_holdings_value += pos.get("quantity", 0) * pos.get("current_price", pos.get("average_price", 0))

portfolio_value = cash + total_holdings_value
initial_capital = 100000.0
total_returns = portfolio_value - initial_capital
returns_pct = (total_returns / initial_capital) * 100

with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}", delta=f"{returns_pct:+.2f}%", border=True)
    with col2:
        st.metric("Cash Available", f"₹{cash:,.2f}", border=True)
    with col3:
        st.metric("Holdings Value", f"₹{total_holdings_value:,.2f}", border=True)
    with col4:
        st.metric("Total Returns", f"₹{total_returns:,.2f}", delta=f"{returns_pct:+.2f}%", border=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Current Holdings ────────────────────────────────────────────
st.subheader("Current Holdings")

if positions:
    for pos in positions:
        symbol = pos.get("symbol", "")
        clean_symbol = symbol.replace(".NS", "")
        quantity = pos.get("quantity", 0)
        avg_price = pos.get("average_price", 0)
        current_price = pos.get("current_price", avg_price)

        position_value = quantity * current_price
        cost_basis = quantity * avg_price
        pnl = position_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0

        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            with col1:
                st.markdown(f"**{clean_symbol}**")
                st.caption(f"{quantity} shares @ ₹{avg_price:,.2f}")
            with col2:
                st.metric("CMP", f"₹{current_price:,.2f}", label_visibility="collapsed")
            with col3:
                st.metric("Value", f"₹{position_value:,.2f}", label_visibility="collapsed")
            with col4:
                st.metric("P&L", f"₹{pnl:,.2f}", delta=f"{pnl_pct:+.2f}%", label_visibility="collapsed")
            with col5:
                if st.button("Sell", key=f"sell_{symbol}", use_container_width=True):
                    st.session_state["selected_stock"] = symbol
                    st.switch_page("pages/5_Trade_Executor.py")

    st.markdown("---")
    portfolio_df = pd.DataFrame([{
        "Symbol": p.get("symbol", "").replace(".NS", ""),
        "Quantity": p.get("quantity", 0),
        "Avg Price (₹)": round(p.get("average_price", 0), 2),
        "Current Price (₹)": round(p.get("current_price", 0), 2),
        "Value (₹)": round(p.get("quantity", 0) * p.get("current_price", 0), 2),
        "P&L (₹)": round(
            (p.get("quantity", 0) * p.get("current_price", 0)) -
            (p.get("quantity", 0) * p.get("average_price", 0)), 2
        )
    } for p in positions])

    st.download_button(
        label="Download Portfolio CSV",
        data=portfolio_df.to_csv(index=False),
        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.info("No open positions. Start trading to build your portfolio!")

st.markdown("<br>", unsafe_allow_html=True)

# ── Order History (from Supabase transactions table) ────────────
st.subheader("Trade History")

if orders:
    for order in orders[:20]:  # Last 20 trades
        side_color = "#00D09C" if order.get("side") == "BUY" else "#EB5B3C"
        ticker = order.get("ticker", "").replace(".NS", "")
        qty = order.get("qty", 0)
        price = order.get("price", 0)
        ts = order.get("timestamp", "")
        side = order.get("side", "")

        st.markdown(f"""
        <div style='padding:12px; background:#F6F8FA; border-radius:8px; margin-bottom:8px;'>
            <span style='color:{side_color}; font-weight:700;'>{side}</span>
            <span style='color:#2E3338; margin-left:8px;'>{qty} × {ticker}</span>
            <span style='color:#7C7E8C; margin-left:8px;'>@ ₹{float(price):,.2f}</span>
            <span style='color:#B0B3C1; margin-left:12px; font-size:0.8em;'>{str(ts)[:16]}</span>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No trades yet.")
