# -*- coding: utf-8 -*-
"""
Sentinel Trading Platform - Home Dashboard
Gatekeeper: requires Supabase authentication before showing the app.
"""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layout import setup_page_config, apply_groww_theme

# ── Startup check ─────────────────────────────────────────────
import auth_manager as auth

# Page config (always runs first)
setup_page_config("Sentinel - Dashboard", "📊")
apply_groww_theme()

# ── ENV CHECK ─────────────────────────────────────────────────
if not auth.is_configured():
    st.error("⚠️ Supabase not configured. Set SUPABASE_URL and SUPABASE_KEY in Railway environment variables.")
    st.stop()

# ── AUTH GATEKEEPER ───────────────────────────────────────────
if not st.session_state.get("authenticated"):

    # Hide sidebar completely until logged in
    st.markdown("""
        <style>
            [data-testid="stSidebar"] { display: none !important; }
            [data-testid="collapsedControl"] { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # ── Login / Signup Card ──────────────────────────────────
    st.markdown("""
        <div style="max-width:420px; margin:60px auto 0 auto;">
            <div style="text-align:center; margin-bottom:32px;">
                <h1 style="font-size:2rem; font-weight:800; color:#1A1D29;">Sentinel</h1>
                <p style="color:#7C7E8C; margin-top:4px;">AI-Powered Trading Platform</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_left, card_col, col_right = st.columns([1, 2, 1])

    with card_col:
        tab_login, tab_signup = st.tabs(["Login", "Create Account"])

        # ── LOGIN TAB ──
        with tab_login:
            with st.form("login_form"):
                st.markdown("##### Welcome back")
                email = st.text_input("Email", placeholder="you@example.com", key="login_email")
                password = st.text_input("Password", type="password", key="login_password")
                submitted = st.form_submit_button(
                    "Sign In", type="primary", use_container_width=True
                )

            if submitted:
                if not email or not password:
                    st.error("Please enter your email and password.")
                else:
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

        # ── SIGNUP TAB ──
        with tab_signup:
            with st.form("signup_form"):
                st.markdown("##### Create your account")
                full_name = st.text_input("Full Name", placeholder="Your Name", key="signup_name")
                new_email = st.text_input("Email", placeholder="you@example.com", key="signup_email")
                new_password = st.text_input("Password", type="password", key="signup_password")
                confirm_password = st.text_input(
                    "Confirm Password", type="password", key="signup_confirm"
                )
                submitted_signup = st.form_submit_button(
                    "Create Account", type="primary", use_container_width=True
                )

            if submitted_signup:
                if not full_name or not new_email or not new_password:
                    st.error("Please fill all fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    with st.spinner("Creating your account..."):
                        result = auth.sign_up(new_email, new_password, full_name)
                    if result["success"]:
                        # Auto-initialize portfolio
                        auth.initialize_user_portfolio(result["user"].id)
                        st.success("Account created! Please check your email to confirm, then log in.")
                    else:
                        st.error(f"Sign up failed: {result['error']}")

    st.stop()  # Block the rest of the page until authenticated

# ── AUTHENTICATED: Show Dashboard ─────────────────────────────
from layout import render_navigation
render_navigation()

# Sign Out button in sidebar
with st.sidebar:
    st.markdown("---")
    user_name = st.session_state.get("user_name", "User")
    user_email = st.session_state.get("user_email", "")
    st.markdown(f"**{user_name}**")
    st.caption(user_email)
    if st.button("Sign Out", use_container_width=True, type="secondary"):
        auth.sign_out()
        st.rerun()

# ── Dashboard Content ─────────────────────────────────────────
st.title("Dashboard")
st.markdown(f"Welcome back, **{st.session_state.get('user_name', 'Trader')}**!")

# Fetch live portfolio from Supabase
user_id = st.session_state["user_id"]
portfolio = auth.get_user_portfolio(user_id)

cash = portfolio.get("cash", 100000.0)
positions = portfolio.get("positions", [])
orders = portfolio.get("orders", [])

total_holdings = sum(
    p.get("quantity", 0) * p.get("current_price", p.get("average_price", 0))
    for p in positions
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
