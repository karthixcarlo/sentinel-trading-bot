"""
Market Overview Component

Displays real-time market status, indices, and trading hours.
"""

import streamlit as st
from datetime import datetime, timedelta

try:
    from sentinel.indian_market_config import (
        is_market_open,
        time_until_market_open,
        MARKET_OPEN_TIME,
        MARKET_CLOSE_TIME,
        IST,
        INDIAN_INDICES
    )
    SENTINEL_AVAILABLE = True
except ImportError:
    SENTINEL_AVAILABLE = False
    import pytz
    IST = pytz.timezone('Asia/Kolkata')

try:
    from dashboard_utils import (
        format_time_ist,
        format_datetime_ist,
        get_market_status_color,
        run_async,
        format_percentage
    )
except ImportError:
    # Fallback implementations
    def format_time_ist(dt=None):
        if dt is None:
            dt = datetime.now(IST)
        return dt.strftime("%I:%M %p IST")
    
    def get_market_status_color(is_open):
        return "green" if is_open else "red"
    
    def run_async(coro):
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    def format_percentage(value):
        return f"{value*100:.2f}%"


def display_market_status():
    """Display current market status for Indian markets."""
    
    # Current time
    now = datetime.now(IST)
    current_time = format_time_ist(now)
    
    # Market status - simplified if sentinel unavailable
    if SENTINEL_AVAILABLE:
        market_open = is_market_open(now)
    else:
        # Simple check: 9:15 AM - 3:30 PM IST on weekdays
        hour = now.hour
        minute = now.minute
        is_weekday = now.weekday() < 5
        market_open = is_weekday and ((hour == 9 and minute >= 15) or (10 <= hour < 15) or (hour == 15 and minute <= 30))
    
    status_text = "🟢 OPEN" if market_open else "🔴 CLOSED"
    
    # Display in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"### Market Status")
        if market_open:
            st.markdown(f"<h2 style='color: green;'>{status_text}</h2>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h2 style='color: red;'>{status_text}</h2>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### Current Time")
        st.markdown(f"<h2>{current_time}</h2>", unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"### Market Hours")
        st.markdown(f"<h2>9:15 AM - 3:30 PM IST</h2>", unsafe_allow_html=True)
    
    # Display countdown if market is closed
    if not market_open:
        st.info("⏰ Market is currently closed. Open hours: Mon-Fri 9:15 AM - 3:30 PM IST")


def display_index_quotes():
    """Display Indian market indices quotes."""
    
    st.markdown("### 📊 Market Indices")
    
    if not SENTINEL_AVAILABLE:
        st.warning("📡 Live market data unavailable. Install all dependencies to see real-time indices.")
        return
    
    try:
        from sentinel import ProviderFactory
        
        # Initialize provider
        factory = ProviderFactory(market_region="INDIA")
        price_provider = factory.get_price_provider()
        
        # Get index quotes
        indices_to_display = ["^NSEI", "^NSEBANK"]  # Nifty 50, Bank Nifty
        index_names = ["Nifty 50", "Bank Nifty"]
        
        cols = st.columns(len(indices_to_display))
        
        for idx, (index_symbol, index_name) in enumerate(zip(indices_to_display, index_names)):
            with cols[idx]:
                try:
                    # Simplified - use yfinance directly
                    import yfinance as yf
                    ticker = yf.Ticker(index_symbol)
                    info = ticker.info
                    
                    current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                    prev_close = info.get('previousClose', current_price)
                    change = current_price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close else 0
                    
                    delta_str = f"{change:+.2f} ({change_pct:+.2f}%)"
                    
                    st.metric(
                        label=index_name,
                        value=f"{current_price:,.2f}",
                        delta=delta_str
                    )
                    
                except Exception as e:
                    st.warning(f"{index_name}: Loading...")
    
    except Exception as e:
        st.error(f"Unable to load indices. Error: {str(e)[:100]}")


def display_quick_stats():
    """Display quick statistics and summary."""
    
    st.markdown("### 📈 Quick Stats")
    
    # Initialize session state for stats
    if 'portfolio_value' not in st.session_state:
        st.session_state.portfolio_value = 100000  # Default
        st.session_state.daily_pnl = 0
        st.session_state.total_pnl = 0
        st.session_state.positions_count = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Portfolio Value",
            value=f"₹{st.session_state.portfolio_value:,.2f}"
        )
    
    with col2:
        daily_pnl = st.session_state.daily_pnl
        st.metric(
            label="Today's P&L",
            value=f"₹{abs(daily_pnl):,.2f}",
            delta=f"{daily_pnl:+.2f}",
            delta_color="normal" if daily_pnl >= 0 else "inverse"
        )
    
    with col3:
        total_pnl = st.session_state.total_pnl
        st.metric(
            label="Total P&L",
            value=f"₹{abs(total_pnl):,.2f}",
            delta=f"{total_pnl:+.2f}",
            delta_color="normal" if total_pnl >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            label="Open Positions",
            value=st.session_state.positions_count
        )


def render_market_overview():
    """Main function to render the complete market overview."""
    
    st.title("🏠 Project Sentinel - Market Overview")
    
    # Display all components
    display_market_status()
    
    st.divider()
    
    display_index_quotes()
    
    st.divider()
    
    display_quick_stats()
    
    # Auto-refresh button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
