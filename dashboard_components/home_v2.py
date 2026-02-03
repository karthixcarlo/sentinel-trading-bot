"""
Home Page - Clean Streamlit Native Design
"""

import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

def render_home_page():
    """Render home page with native Streamlit components"""
    
    st.title(":material/home: Market overview")
    
    # ========================================================================
    # MARKET INDICES
    # ========================================================================
    
    # Sample fallback data
    sample_indices = {
        "Nifty 50": {"value": 22150.50, "change": 1.25},
        "Bank Nifty": {"value": 48250.75, "change": -0.85},
        "Sensex": {"value": 73280.30, "change": 0.95}
    }
    
    with st.container(horizontal=True):
        indices = [
            ("^NSEI", "Nifty 50"),
            ("^NSEBANK", "Bank Nifty"),
            ("^BSESN", "Sensex")
        ]
        
        for symbol, name in indices:
            try:
                if yf:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='2d')
                    
                    if len(hist) >= 2:
                        current = hist['Close'].iloc[-1]
                        prev = hist['Close'].iloc[-2]
                        change = current - prev
                        change_pct = (change / prev) * 100
                        
                        st.metric(
                            label=name,
                            value=f"₹{current:,.2f}",
                            delta=f"{change_pct:+.2f}%",
                            border=True
                        )
                    else:
                        raise Exception("Not enough data")
                else:
                    raise Exception("yfinance not available")
            except:
                # Use sample data
                data = sample_indices.get(name, {"value": 0, "change": 0})
                st.metric(
                    label=name,
                    value=f"₹{data['value']:,.2f}",
                    delta=f"{data['change']:+.2f}%",
                    border=True
                )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # PORTFOLIO SUMMARY
    # ========================================================================
    
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = {
            'cash': 100000,
            'positions': {},
            'orders': [],
            'closed_trades': []
        }
    
    portfolio_data = st.session_state.paper_portfolio
    cash = portfolio_data.get('cash', 100000)
    positions = portfolio_data.get('positions', {})
    
    portfolio_value = cash
    unrealized_pnl = 0
    
    for pos in positions.values():
        portfolio_value += pos.get('market_value', 0)
        unrealized_pnl += pos.get('pnl', 0)
    
    total_returns = portfolio_value - 100000
    returns_pct = (total_returns / 100000 * 100) if 100000 else 0
    
    with st.container(border=True):
        st.subheader(":material/account_balance_wallet: Your portfolio")
        
        with st.container(horizontal=True):
            st.metric(
                "Portfolio value",
                f"₹{portfolio_value:,.2f}",
                delta=None,
                border=True
            )
            st.metric(
                "Today's P&L",
                f"₹{unrealized_pnl:,.2f}",
                delta=None,
                border=True
            )
            st.metric(
                "Total returns",
                f"₹{total_returns:,.2f}",
                delta=f"{returns_pct:+.2f}%",
                border=True
            )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # QUICK ACTIONS
    # ========================================================================
    
    st.subheader(":material/bolt: Quick actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            st.markdown("### :material/search: Discover stocks")
            st.caption("Find top gainers, losers, and active stocks")
            if st.button("Discover now", use_container_width=True, key="discover_btn"):
                st.session_state.nav_selection = "Discover"
                st.rerun()
    
    with col2:
        with st.container(border=True):
            st.markdown("### :material/analytics: Analyze stock")
            st.caption("Deep analysis with charts and fundamentals")
            if st.button("Analyze now", use_container_width=True, key="analyze_btn"):
                st.session_state.nav_selection = "Analyze"
                st.rerun()
    
    with col3:
        with st.container(border=True):
            st.markdown("### :material/currency_rupee: Place trade")
            st.caption("Quick order execution")
            if st.button("Trade now", use_container_width=True, key="trade_btn"):
                st.session_state.nav_selection = "Trade"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # WATCHLIST
    # ========================================================================
    
    if positions:
        st.subheader(":material/bookmark: Your positions")
        
        for symbol, pos in list(positions.items())[:5]:
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            current_price = pos.get('current_price', 0)
            pnl = pos.get('pnl', 0)
            pnl_pct = pos.get('pnl_pct', 0)
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**{clean_symbol}**")
                    st.caption(f"{pos.get('quantity', 0)} shares")
                
                with col2:
                    st.metric("Current", f"₹{current_price:,.2f}", label_visibility="collapsed")
                
                with col3:
                    st.metric("P&L", f"₹{pnl:,.2f}", delta=f"{pnl_pct:+.2f}%", label_visibility="collapsed")
    
    # ========================================================================
    # MARKET STATUS
    # ========================================================================
    
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    hour = now.hour
    
    is_open = (9 <= hour < 16) and (now.weekday() < 5)
    
    if is_open:
        st.success("Market is OPEN", icon=":material/check_circle:")
    else:
        st.info("Market is CLOSED", icon=":material/schedule:")
