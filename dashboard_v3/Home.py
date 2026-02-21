# -*- coding: utf-8 -*-
"""
Sentinel Trading Platform - Home Dashboard
Supports DEMO MODE (no Supabase) and LIVE MODE (with Supabase auth).
"""

import streamlit as st
import sys
import os

# Add dashboard_v3/ dir and project root to path
DASH_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(DASH_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, DASH_DIR)

from layout import setup_page_config, apply_groww_theme

setup_page_config("Sentinel - Dashboard", "📊")
apply_groww_theme()

# ── Check if Supabase is configured ──────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_ENABLED = bool(SUPABASE_URL and SUPABASE_KEY)

# ── DEMO MODE: auto-login without Supabase ────────────────────
if not SUPABASE_ENABLED:
    if not st.session_state.get("authenticated"):
        st.session_state["authenticated"] = True
        st.session_state["user_id"] = "demo-user"
        st.session_state["user_email"] = "demo@sentinel.ai"
        st.session_state["user_name"] = "Demo Trader"
        st.session_state["demo_mode"] = True
        # Initialize in-memory portfolio for demo
        if "paper_portfolio" not in st.session_state:
            st.session_state["paper_portfolio"] = {
                "cash": 100000.0,
                "positions": [],
                "orders": []
            }

# ── LIVE MODE: Supabase auth gatekeeper ───────────────────────
elif not st.session_state.get("authenticated"):
    import auth_manager as auth

    # Hide sidebar until logged in
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="text-align:center; margin-top:60px; margin-bottom:32px;">
            <h1 style="font-size:2rem; font-weight:800;">Sentinel</h1>
            <p style="color:#7C7E8C;">AI-Powered Trading Platform</p>
        </div>
    """, unsafe_allow_html=True)

    col_left, card_col, col_right = st.columns([1, 2, 1])
    with card_col:
        tab_login, tab_signup = st.tabs(["Login", "Create Account"])

        with tab_login:
            with st.form("login_form"):
                st.markdown("##### Welcome back")
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

            if submitted:
                if email and password:
                    with st.spinner("Signing in..."):
                        result = auth.sign_in(email, password)
                    if result["success"]:
                        user = result["user"]
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user.id
                        st.session_state["user_email"] = user.email
                        st.session_state["user_name"] = (
                            user.user_metadata.get("full_name", email.split("@")[0])
                            if user.user_metadata else email.split("@")[0]
                        )
                        st.rerun()
                    else:
                        st.error(f"Login failed: {result['error']}")
                else:
                    st.error("Enter email and password.")

        with tab_signup:
            with st.form("signup_form"):
                st.markdown("##### Create your account")
                full_name = st.text_input("Full Name", placeholder="Your Name")
                new_email = st.text_input("Email", placeholder="you@example.com")
                new_password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted_signup = st.form_submit_button("Create Account", type="primary", use_container_width=True)

            if submitted_signup:
                if not full_name or not new_email or not new_password:
                    st.error("Please fill all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating account..."):
                        result = auth.sign_up(new_email, new_password, full_name)
                    if result["success"]:
                        auth.initialize_user_portfolio(result["user"].id)
                        st.success("Account created! Check your email to confirm, then log in.")
                    else:
                        st.error(f"Sign up failed: {result['error']}")

    st.stop()

# ── AUTHENTICATED: Main Dashboard ────────────────────────────
from layout import render_navigation
render_navigation()

# Sidebar: user info + sign out
with st.sidebar:
    st.markdown("---")
    is_demo = st.session_state.get("demo_mode", False)
    user_name = st.session_state.get("user_name", "Trader")
    user_email = st.session_state.get("user_email", "")
    st.markdown(f"**{user_name}**")
    if is_demo:
        st.caption("🟡 Demo Mode")
    else:
        st.caption(user_email)
        if st.button("Sign Out", use_container_width=True, type="secondary"):
            import auth_manager as auth
            auth.sign_out()
            st.rerun()

# ── Dashboard content ─────────────────────────────────────────
st.title("Dashboard")
st.markdown(f"Welcome back, **{st.session_state.get('user_name', 'Trader')}**!")

if st.session_state.get("demo_mode"):
    st.info("🟡 Running in Demo Mode — data resets on page refresh. Connect Supabase for persistent accounts.")

# Portfolio data — from session state (demo) or Supabase (live)
if SUPABASE_ENABLED and not st.session_state.get("demo_mode"):
    import auth_manager as auth
    user_id = st.session_state["user_id"]
    portfolio = auth.get_user_portfolio(user_id)
    cash = portfolio.get("cash", 100000.0)
    positions = portfolio.get("positions", [])
    orders = portfolio.get("orders", [])
else:
    p = st.session_state.get("paper_portfolio", {"cash": 100000.0, "positions": [], "orders": []})
    cash = p["cash"]
    positions = p["positions"]
    orders = p["orders"]

total_holdings = sum(
    pos.get("quantity", 0) * pos.get("current_price", pos.get("average_price", 0))
    for pos in positions
)
portfolio_value = cash + total_holdings

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Portfolio Value", f"₹{portfolio_value:,.0f}", border=True)
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
