# -*- coding: utf-8 -*-
"""
Settings - Multi-Page Dashboard
Configure preferences and manage watchlist
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path so we can import layout
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout import setup_page_config, render_navigation, apply_groww_theme

# Page setup
setup_page_config("Settings", "⚙️")

# Apply theme
apply_groww_theme()

# Navigation
render_navigation()

st.title("Settings")

# App settings
st.subheader("App Preferences")

# Ensure session state is initialized
if 'settings' not in st.session_state:
    st.session_state.settings = {
        'initial_capital': 100000.0,
        'refresh_interval': 60,
        'auto_refresh': True
    }

if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ['RELIANCE.NS', 'TCS.NS']

with st.form("settings_form"):
    auto_refresh = st.checkbox(
        "Auto-refresh data",
        value=st.session_state.settings.get('auto_refresh', True)
    )
    
    refresh_interval = st.slider(
        "Refresh interval (seconds)",
        min_value=30,
        max_value=300,
        value=st.session_state.settings.get('refresh_interval', 60),
        step=30
    )
    
    initial_capital = st.number_input(
        "Initial Capital (₹)",
        min_value=10000,
        max_value=10000000,
        value=int(st.session_state.settings.get('initial_capital', 100000)),
        step=10000
    )
    
    if st.form_submit_button("Save Settings", type="primary"):
        st.session_state.settings.update({
            'auto_refresh': auto_refresh,
            'refresh_interval': refresh_interval,
            'initial_capital': initial_capital
        })
        st.success("Settings saved!")
        st.toast("Settings updated")

st.markdown("---")

# Watchlist management
st.subheader("Watchlist Management")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Current Watchlist**")
    
    watchlist = st.session_state.watchlist
    
    if watchlist:
        for i, stock in enumerate(watchlist):
            col_a, col_b = st.columns([4, 1])
            with col_a:
                st.text(stock.replace('.NS', ''))
            with col_b:
                if st.button("Remove", key=f"remove_{i}"):
                    watchlist.remove(stock)
                    st.rerun()
    else:
        st.info("Watchlist is empty")

with col2:
    st.markdown("**Add to Watchlist**")
    
    new_stock = st.text_input("Stock symbol", placeholder="e.g., RELIANCE, TCS")
    
    if st.button("Add Stock"):
        if new_stock:
            if not new_stock.endswith('.NS'):
                new_stock = f"{new_stock}.NS"
            
            if new_stock not in watchlist:
                watchlist.append(new_stock)
                st.success(f"Added {new_stock.replace('.NS', '')} to watchlist")
                st.rerun()
            else:
                st.warning("Stock already in watchlist")
        else:
            st.error("Please enter a stock symbol")

# Import/Export watchlist
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Import Watchlist**")
    
    uploaded = st.file_uploader(
        "Upload CSV file",
        type=['csv', 'txt'],
        help="Upload a CSV file with stock symbols (one per line)"
    )
    
    if uploaded:
        try:
            df = pd.read_csv(uploaded, header=None)
            imported_stocks = df[0].tolist()
            
            # Add .NS suffix if missing
            imported_stocks = [s if s.endswith('.NS') else f"{s}.NS" for s in imported_stocks]
            
            # Merge with existing watchlist
            st.session_state.watchlist = list(set(watchlist + imported_stocks))
            
            st.success(f"Imported {len(imported_stocks)} stocks!")
            st.rerun()
        except Exception as e:
            st.error(f"Error importing: {str(e)}")

with col2:
    st.markdown("**Export Watchlist**")
    
    if watchlist:
        watchlist_csv = "\n".join([s.replace('.NS', '') for s in watchlist])
        
        st.download_button(
            label="Download Watchlist",
            data=watchlist_csv,
            file_name="watchlist.csv",
            mime="text/csv"
        )
    else:
        st.info("Watchlist is empty")

st.markdown("---")

# Reset portfolio
st.subheader("Reset Portfolio")

st.warning("This will reset your portfolio to initial state and delete all positions and orders!")

if st.button("Reset Portfolio", type="secondary"):
    st.session_state.paper_portfolio = {
        'cash': st.session_state.settings['initial_capital'],
        'positions': [],
        'orders': []
    }
    st.success("Portfolio reset!")
    st.toast("Portfolio reset to initial state")
    st.rerun()
