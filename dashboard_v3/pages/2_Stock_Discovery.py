# -*- coding: utf-8 -*-
"""
Stock Discovery - Multi-Page Dashboard
Find top gainers, losers, and most active stocks with live data
"""

import streamlit as st
import sys
import os

# Add parent directory to path so we can import layout
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from live_nse_discovery import discover_live_stocks
    from nse_stock_universe import get_stock_count
    LIVE_DISCOVERY_AVAILABLE = True
except ImportError:
    LIVE_DISCOVERY_AVAILABLE = False

from layout import setup_page_config, render_navigation, apply_groww_theme

# Page setup
setup_page_config("Stock Discovery", "🔍")

# Apply theme
apply_groww_theme()

# Navigation
render_navigation()

# ============================================================================
# CACHING - Performance Optimization
# ============================================================================

@st.cache_data(ttl=180)  # 3-minute cache for stock discovery
def cached_discover_stocks(category, limit=24):
    """Cached stock discovery to reduce API calls"""
    
    if LIVE_DISCOVERY_AVAILABLE:
        try:
            return discover_live_stocks(category=category, limit=limit, use_nifty_100=True)
        except Exception as e:
            st.warning(f"Live discovery failed: {str(e)}")
    
    # Fallback sample data
    sample_stocks = {
        "gainers": [
            {"symbol": "TCS.NS", "price": 3680.75, "change_percent": 2.8},
            {"symbol": "INFY.NS", "price": 1540.20, "change_percent": 3.2},
            {"symbol": "RELIANCE.NS", "price": 2450.50, "change_percent": 3.1},
            {"symbol": "HDFCBANK.NS", "price": 1650.00, "change_percent": 2.3},
        ],
        "losers": [
            {"symbol": "BHARTIARTL.NS", "price": 1180.50, "change_percent": -2.1},
            {"symbol": "MARUTI.NS", "price": 10250.20, "change_percent": -1.9},
        ],
        "active": [
            {"symbol": "RELIANCE.NS", "price": 2450.50, "change_percent": 0.8},
            {"symbol": "SBIN.NS", "price": 620.30, "change_percent": -0.5},
        ]
    }
    
    return sample_stocks.get(category, sample_stocks["gainers"])

# ============================================================================
# MAIN PAGE
# ============================================================================

st.title("Stock Discovery")

if LIVE_DISCOVERY_AVAILABLE:
    stock_count = get_stock_count()
    st.caption(f"Scanning **{stock_count}+ NSE stocks** for opportunities")
else:
    st.caption("Showing sample NSE stocks")

# Tabs for different categories
tab1, tab2, tab3 = st.tabs([
    "Top Gainers",
    "Top Losers",
    "Most Active"
])

# ============================================================================
# TOP GAINERS
# ============================================================================

with tab1:
    st.subheader("Top Gainers")
    
    # Progress bar while loading
    with st.spinner("Fetching top gainers..."):
        gainers = cached_discover_stocks("gainers", limit=24)
    
    st.write(f"Found {len(gainers)} gainers")

    # Display as cards
    for i in range(0, min(len(gainers), 24), 4):
        cols = st.columns(4)
        
        for j, col in enumerate(cols):
            if i + j < len(gainers):
                stock = gainers[i + j]
                symbol = stock.get('symbol', 'N/A')
                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                price = stock.get('price', 0)
                change = stock.get('change_percent', 0)
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{clean_symbol}**")
                        st.metric(
                            label="Price",
                            value=f"₹{price:,.2f}",
                            delta=f"{change:+.2f}%",
                            label_visibility="collapsed"
                        )
                        if st.button(
                            "Analyze",
                            key=f"analyze_{symbol}_{i}_{j}",
                            use_container_width=True
                        ):
                            st.session_state.selected_stock = symbol
                            st.switch_page("pages/3_Stock_Analyzer.py")

# ============================================================================
# TOP LOSERS
# ============================================================================

with tab2:
    st.subheader("Top Losers")
    
    with st.spinner("Fetching top losers..."):
        losers = cached_discover_stocks("losers", limit=24)
    
    st.write(f"Found {len(losers)} losers")
    
    # Display as cards
    for i in range(0, min(len(losers), 24), 4):
        cols = st.columns(4)
        
        for j, col in enumerate(cols):
            if i + j < len(losers):
                stock = losers[i + j]
                symbol = stock.get('symbol', 'N/A')
                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                price = stock.get('price', 0)
                change = stock.get('change_percent', 0)
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{clean_symbol}**")
                        st.metric(
                            label="Price",
                            value=f"₹{price:,.2f}",
                            delta=f"{change:+.2f}%",
                            label_visibility="collapsed"
                        )
                        if st.button(
                            "Analyze",
                            key=f"analyze_{symbol}_{i}_{j}",
                            use_container_width=True
                        ):
                            st.session_state.selected_stock = symbol
                            st.switch_page("pages/3_Stock_Analyzer.py")

# ============================================================================
# MOST ACTIVE
# ============================================================================

with tab3:
    st.subheader("Most Active")
    
    with st.spinner("Fetching most active stocks..."):
        active = cached_discover_stocks("active", limit=24)
    
    st.write(f"Found {len(active)} active stocks")
    
    # Display as cards
    for i in range(0, min(len(active), 24), 4):
        cols = st.columns(4)
        
        for j, col in enumerate(cols):
            if i + j < len(active):
                stock = active[i + j]
                symbol = stock.get('symbol', 'N/A')
                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                price = stock.get('price', 0)
                change = stock.get('change_percent', 0)
                
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{clean_symbol}**")
                        st.metric(
                            label="Price",
                            value=f"₹{price:,.2f}",
                            delta=f"{change:+.2f}%",
                            label_visibility="collapsed"
                        )
                        if st.button(
                            "Analyze",
                            key=f"analyze_{symbol}_{i}_{j}",
                            use_container_width=True
                        ):
                            st.session_state.selected_stock = symbol
                            st.switch_page("pages/3_Stock_Analyzer.py")

# ============================================================================
# REFRESH DATA
# ============================================================================

st.markdown("---")

col1, col2 = st.columns([3, 1])

with col1:
    st.caption("Data cached for 3 minutes. Click refresh to get latest prices.")

with col2:
    if st.button("Refresh Data", use_container_width=True):
        cached_discover_stocks.clear()
        st.success("Data refreshed!")
        st.rerun()
