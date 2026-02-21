# -*- coding: utf-8 -*-
"""
Sentinel Trading Platform - Home Dashboard
"""

import streamlit as st
import sys
import os

DASH_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DASH_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, DASH_DIR)

from layout import setup_page_config, apply_groww_theme, render_navigation

setup_page_config("Sentinel - Dashboard", "📊")
apply_groww_theme()

# ── Auto-initialize session (no login wall) ───────────────────
if not st.session_state.get("authenticated"):
    st.session_state["authenticated"] = True
    st.session_state["user_id"] = "demo-user"
    st.session_state["user_email"] = "demo@sentinel.ai"
    st.session_state["user_name"] = "Demo Trader"
    st.session_state["demo_mode"] = True

if "paper_portfolio" not in st.session_state:
    st.session_state["paper_portfolio"] = {
        "cash": 100000.0, "positions": [], "orders": []
    }
if "settings" not in st.session_state:
    st.session_state["settings"] = {
        "initial_capital": 100000.0, "auto_refresh": True, "refresh_interval": 60
    }
if "watchlist" not in st.session_state:
    st.session_state["watchlist"] = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]

# ── Render dashboard ──────────────────────────────────────────
render_navigation()

st.title("Dashboard")
st.markdown("Welcome to **Sentinel** — AI-Powered Trading Platform for NSE/BSE markets.")

p = st.session_state["paper_portfolio"]
cash = p["cash"]
positions = p["positions"]
orders = p["orders"]
total_holdings = sum(pos.get("quantity", 0) * pos.get("current_price", pos.get("average_price", 0)) for pos in positions)
portfolio_value = cash + total_holdings
total_returns = portfolio_value - 100000.0
returns_pct = (total_returns / 100000.0) * 100

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Portfolio Value", f"₹{portfolio_value:,.0f}", delta=f"{returns_pct:+.2f}%", border=True)
with col2:
    st.metric("Cash Available", f"₹{cash:,.0f}", border=True)
with col3:
    st.metric("Active Positions", len(positions), border=True)
with col4:
    st.metric("Total Trades", len(orders), border=True)

st.markdown("---")
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Explore Stocks", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Stock_Discovery.py")
with col2:
    if st.button("My Portfolio", use_container_width=True):
        st.switch_page("pages/4_Portfolio.py")
with col3:
    if st.button("AI Analysis", use_container_width=True):
        st.switch_page("pages/3_Stock_Analyzer.py")

st.markdown("---")

# Market overview
st.subheader("Market Overview")
try:
    import yfinance as yf
    from datetime import datetime
    import pytz

    indices = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "BANK NIFTY": "^NSEBANK"
    }

    cols = st.columns(3)
    for i, (name, ticker) in enumerate(indices.items()):
        try:
            data = yf.Ticker(ticker).history(period="2d")
            if len(data) >= 2:
                current = data["Close"].iloc[-1]
                prev = data["Close"].iloc[-2]
                change = current - prev
                pct = (change / prev) * 100
                with cols[i]:
                    st.metric(name, f"{current:,.0f}", delta=f"{pct:+.2f}%", border=True)
        except Exception:
            with cols[i]:
                st.metric(name, "Loading...", border=True)
except Exception:
    st.info("Market data loading...")
