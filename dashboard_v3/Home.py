# -*- coding: utf-8 -*-
"""
Sentinel Trading Platform - Home Dashboard
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from layout import setup_page_config, render_navigation, apply_groww_theme

# Page setup
setup_page_config("Sentinel - Dashboard", "📊")

# Apply Groww theme
apply_groww_theme()

# Navigation
render_navigation()

# Main content
st.title("Dashboard")

st.markdown("""
Welcome to **Sentinel Trading Platform** - Your AI-powered trading assistant for Indian markets.
""")

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Portfolio Value", "₹1,00,000", "+5.2%")

with col2:
    st.metric("Today's P&L", "+₹2,450", "+2.45%")

with col3:
    st.metric("Active Positions", "3", None)

with col4:
    st.metric("AI Status", "Active", None)

st.markdown("---")

# Quick actions
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.button("Explore Stocks", use_container_width=True, type="primary")

with col2:
    st.button("View Portfolio", use_container_width=True)

with col3:
    st.button("Start AI Trading", use_container_width=True)
