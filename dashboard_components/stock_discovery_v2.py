"""
Stock Discovery - Clean Native Design
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fallback_discovery import discover_stocks_fallback
except ImportError:
    discover_stocks_fallback = None

try:
    from enhanced_deep_search import perform_deep_analysis
except ImportError:
    perform_deep_analysis = None

# NEW: Import live NSE discovery
try:
    from live_nse_discovery import discover_live_stocks
    from nse_stock_universe import get_stock_count
    LIVE_DISCOVERY_AVAILABLE = True
except ImportError:
    LIVE_DISCOVERY_AVAILABLE = False

def render_stock_discovery():
    """Render stock discovery page with native components"""
    
    st.title(":material/search: Discover stocks")
    
    # Show total stock count
    if LIVE_DISCOVERY_AVAILABLE:
        stock_count = get_stock_count()
        st.caption(f"🇮🇳 **{stock_count}+ NSE stocks** available for discovery")
    
    # Tabs for different categories
    tab1, tab2, tab3 = st.tabs([
        ":green-badge[Top Gainers]",
        ":red-badge[Top Losers]",
        ":blue-badge[Most Active]"
    ])
    
    with tab1:
        render_stock_list("gainers")
    
    with tab2:
        render_stock_list("losers")
    
    with tab3:
        render_stock_list("active")


def render_stock_list(category):
    """Render a list of stocks in a category"""
    
    # Comprehensive NSE stocks - Indian market only
    sample_stocks = {
        "gainers": [
            # IT Sector
            {"symbol": "TCS.NS", "price": 3680.75, "change_percent": 2.8},
            {"symbol": "INFY.NS", "price": 1540.20, "change_percent": 3.2},
            {"symbol": "WIPRO.NS", "price": 445.80, "change_percent": 2.5},
            {"symbol": "HCLTECH.NS", "price": 1280.50, "change_percent": 2.1},
            {"symbol": "TECHM.NS", "price": 1150.30, "change_percent": 1.9},
            
            # Banking & Finance
            {"symbol": "HDFCBANK.NS", "price": 1650.00, "change_percent": 2.3},
            {"symbol": "ICICIBANK.NS", "price": 980.50, "change_percent": 2.7},
            {"symbol": "AXISBANK.NS", "price": 1050.30, "change_percent": 2.4},
            {"symbol": "KOTAKBANK.NS", "price": 1780.90, "change_percent": 1.8},
            {"symbol": "SBIN.NS", "price": 620.30, "change_percent": 2.9},
            
            # Energy & Power
            {"symbol": "RELIANCE.NS", "price": 2450.50, "change_percent": 3.1},
            {"symbol": "ONGC.NS", "price": 245.80, "change_percent": 2.2},
            {"symbol": "POWERGRID.NS", "price": 285.60, "change_percent": 1.7},
            {"symbol": "NTPC.NS", "price": 335.40, "change_percent": 1.9},
            
            # Pharma
            {"symbol": "DRREDDY.NS", "price": 5880.50, "change_percent": 2.6},
            {"symbol": "CIPLA.NS", "price": 1420.30, "change_percent": 2.1},
            {"symbol": "DIVISLAB.NS", "price": 3650.75, "change_percent": 1.8},
            
            # Auto
            {"symbol": "TATAMOTORS.NS", "price": 775.50, "change_percent": 3.5},
            {"symbol": "M&M.NS", "price": 1820.90, "change_percent": 2.4},
            {"symbol": "BAJAJ-AUTO.NS", "price": 9250.40, "change_percent": 1.9},
            
            # Infrastructure
            {"symbol": "LT.NS", "price": 3420.90, "change_percent": 2.8},
            {"symbol": "ULTRACEMCO.NS", "price": 9150.30, "change_percent": 2.2},
            {"symbol": "ADANIPORTS.NS", "price": 1185.60, "change_percent": 3.0},
            
            # FMCG
            {"symbol": "HINDUNILVR.NS", "price": 2380.90, "change_percent": 1.6},
            {"symbol": "ITC.NS", "price": 425.60, "change_percent": 1.8},
        ],
        
        "losers": [
            # Telecom
            {"symbol": "BHARTIARTL.NS", "price": 1180.50, "change_percent": -2.1},
            
            # Paints & Chemicals
            {"symbol": "ASIANPAINT.NS", "price": 2850.75, "change_percent": -1.8},
            {"symbol": "PIDILITIND.NS", "price": 2680.30, "change_percent": -1.2},
            
            # Auto
            {"symbol": "MARUTI.NS", "price": 10250.20, "change_percent": -1.9},
            {"symbol": "EICHERMOT.NS", "price": 4580.50, "change_percent": -1.5},
            {"symbol": "HEROMOTOCO.NS", "price": 4250.80, "change_percent": -1.3},
            
            # Pharma
            {"symbol": "SUNPHARMA.NS", "price": 1450.00, "change_percent": -1.7},
            {"symbol": "LUPIN.NS", "price": 1680.40, "change_percent": -1.4},
            
            # Metals
            {"symbol": "TATASTEEL.NS", "price": 135.70, "change_percent": -2.3},
            {"symbol": "HINDALCO.NS", "price": 625.30, "change_percent": -1.9},
            {"symbol": "JSWSTEEL.NS", "price": 885.60, "change_percent": -1.6},
            
            # Retail
            {"symbol": "TITAN.NS", "price": 3280.50, "change_percent": -1.2},
            {"symbol": "DMART.NS", "price": 3850.90, "change_percent": -1.5},
            
            # Cement
            {"symbol": "GRASIM.NS", "price": 2150.30, "change_percent": -1.4},
            {"symbol": "AMBUJACEM.NS", "price": 580.20, "change_percent": -1.1},
        ],
        
        "active": [
            # Most traded stocks
            {"symbol": "RELIANCE.NS", "price": 2450.50, "change_percent": 0.8},
            {"symbol": "SBIN.NS", "price": 620.30, "change_percent": -0.5},
            {"symbol": "TATAMOTORS.NS", "price": 775.50, "change_percent": 1.2},
            {"symbol": "HDFCBANK.NS", "price": 1650.00, "change_percent": 0.3},
            {"symbol": "ICICIBANK.NS", "price": 980.50, "change_percent": -0.4},
            {"symbol": "INFY.NS", "price": 1540.20, "change_percent": 0.9},
            {"symbol": "ITC.NS", "price": 425.60, "change_percent": -0.2},
            {"symbol": "HINDUNILVR.NS", "price": 2380.90, "change_percent": 0.6},
            {"symbol": "BHARTIARTL.NS", "price": 1180.50, "change_percent": -0.7},
            {"symbol": "AXISBANK.NS", "price": 1050.30, "change_percent": 0.5},
            {"symbol": "LT.NS", "price": 3420.90, "change_percent": 0.4},
            {"symbol": "TCS.NS", "price": 3680.75, "change_percent": 0.7},
            {"symbol": "KOTAKBANK.NS", "price": 1780.90, "change_percent": -0.3},
            {"symbol": "MARUTI.NS", "price": 10250.20, "change_percent": 0.2},
            {"symbol": "SUNPHARMA.NS", "price": 1450.00, "change_percent": -0.6},
            {"symbol": "WIPRO.NS", "price": 445.80, "change_percent": 0.8},
        ]
    }
    
    with st.spinner(f"Loading {category}..."):
        try:
            results = None
            
            # Priority 1: Try live NSE discovery (REAL-TIME DATA for ALL NSE stocks)
            if LIVE_DISCOVERY_AVAILABLE:
                try:
                    with st.spinner("Fetching live data from NSE..."):
                        results = discover_live_stocks(category=category, limit=24, use_nifty_100=True)
                        if results and len(results) > 0:
                            st.success(f"✅ Loaded {len(results)} live stocks from NSE", icon=":material/check_circle:")
                except Exception as e:
                    st.warning(f"Live discovery unavailable: {str(e)}", icon=":material/warning:")
                    results = None
            
            # Priority 2: Try fallback_discovery module
            if not results and discover_stocks_fallback:
                try:
                    results = discover_stocks_fallback(category="gainers" if category == "gainers" else "losers")
                except:
                    results = None
            
            # Priority 3: Use sample data
            if not results or len(results) == 0:
                results = sample_stocks.get(category, sample_stocks["gainers"])
                st.info("Showing sample data", icon=":material/info:")
            
            # Display as cards
            for i in range(0, len(results[:24]), 4):
                cols = st.columns(4)
                
                for j, col in enumerate(cols):
                    if i + j < len(results):
                        stock = results[i + j]
                        
                        with col:
                            with st.container(border=True):
                                symbol = stock.get('symbol', 'N/A')
                                price = stock.get('price', 0)
                                change = stock.get('change_percent', 0)
                                
                                clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
                                st.markdown(f"**{clean_symbol}**")
                                st.metric(
                                    label="Price",
                                    value=f"₹{price:,.2f}",
                                    delta=f"{change:+.2f}%",
                                    label_visibility="collapsed"
                                )
                                
                                if st.button("Analyze", key=f"analyze_{symbol}_{i}_{j}", use_container_width=True, icon=":material/analytics:"):
                                    st.session_state.selected_stock = symbol
                                    st.session_state.nav_selection = "Analyze"
                                    st.rerun()
        
        except Exception as e:
            st.error(f"Error loading stocks: {str(e)}", icon=":material/error:")
    
    # Deep Analysis Section
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader(":material/query_stats: Deep analysis")
    
    with st.expander("Run deep market analysis", icon=":material/insights:"):
        if st.button("Analyze market signals", type="primary", icon=":material/play_arrow:", key=f"deep_analysis_{category}"):
            if perform_deep_analysis:
                with st.spinner("Running deep analysis..."):
                    deep_results = perform_deep_analysis() 
                    
                    if deep_results:
                        st.success(f"Found {len(deep_results)} signals", icon=":material/check_circle:")
                        
                        for result in deep_results[:5]:
                            with st.container(border=True):
                                st.markdown(f"**{result.get('symbol', 'N/A')}**")
                                st.caption(result.get('reasoning', 'No details'))
            else:
                st.warning("Deep analysis module not available")
