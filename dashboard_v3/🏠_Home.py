"""
🏠 Sentinel Trading Bot - Home
Production-grade multi-page trading dashboard
"""

import streamlit as st
from datetime import datetime
import pytz

# ============================================================================
# PAGE CONFIGURATION (MUST BE FIRST)
# ============================================================================

st.set_page_config(
    page_title="Sentinel Trading Bot",
    page_icon="📈",
    layout="wide",  # Full screen width
    initial_sidebar_state="expanded"
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize all session state variables for the entire app"""
    
    defaults = {
        'paper_portfolio': {
            'cash': 100000.0,
            'positions': [],
            'orders': []
        },
        'watchlist': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'],
        'settings': {
            'theme': 'light',
            'auto_refresh': True,
            'refresh_interval': 60,
            'initial_capital': 100000.0
        },
        'filters': {
            'discovery_category': 'gainers',
            'sector_filter': 'All',
            'min_price': 0,
            'max_price': 100000
        },
        'selected_stock': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize state
init_session_state()

# ============================================================================
# HEADER
# ============================================================================

col1, col2, col3 = st.columns([2, 4, 2])

with col1:
    st.markdown("""
    <div style='padding: 1rem 0;'>
        <h1 style='color: #00D09C; margin: 0; font-weight: 800;'>
            📈 Sentinel
        </h1>
        <p style='color: #7C7E8C; margin: 0; font-size: 14px;'>
            AI-Powered Trading Bot
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.text_input(
        "Search",
        placeholder="Search stocks, orders, portfolio...",
        label_visibility="collapsed",
        key="global_search"
    )

with col3:
    IST = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(IST)
    
    if 9 <= current_time.hour < 16 and current_time.weekday() < 5:
        market_status = "🟢 Market Open"
        status_color = "#00D09C"
    else:
        market_status = "🔴 Market Closed"
        status_color = "#EB5B3C"
    
    st.markdown(f"""
    <div style='text-align: right; padding: 1rem 0;'>
        <div style='color: {status_color}; font-weight: 600; font-size: 14px;'>
            {market_status}
        </div>
        <div style='color: #7C7E8C; font-size: 12px;'>
            {current_time.strftime('%I:%M %p IST')}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# WELCOME MESSAGE
# ============================================================================

st.title("Welcome to Sentinel Trading Bot")

st.markdown("""
**Sentinel** is your AI-powered trading assistant for the Indian stock market. 
Analyze stocks, execute trades, and track your portfolio—all in one place.

### 🚀 Quick Start

Use the **sidebar** to navigate through different features:

- **📊 Market Overview** - View market indices, watchlist, and portfolio summary
- **🔍 Stock Discovery** - Find top gainers, losers, and most active stocks
- **📈 Stock Analyzer** - Deep analysis with BUY/SELL signals and charts
- **💼 Portfolio** - Track your holdings, P&L, and order history
- **⚡ Trade Executor** - Place buy/sell orders with validation
- **⚙️ Settings** - Configure your preferences

---
""")

# ============================================================================
# PORTFOLIO SNAPSHOT
# ============================================================================

st.subheader("📊 Portfolio Snapshot")

portfolio = st.session_state.paper_portfolio
cash = portfolio['cash']
positions = portfolio['positions']

# Calculate portfolio value
total_holdings_value = 0
for pos in positions:
    total_holdings_value += pos.get('quantity', 0) * pos.get('current_price', pos.get('average_price', 0))

portfolio_value = cash + total_holdings_value
initial_capital = st.session_state.settings['initial_capital']
total_returns = portfolio_value - initial_capital
returns_pct = (total_returns / initial_capital) * 100 if initial_capital > 0 else 0

# Display metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Portfolio Value",
        f"₹{portfolio_value:,.2f}",
        delta=f"{returns_pct:+.2f}%",
        border=True
    )

with col2:
    st.metric(
        "Cash Available",
        f"₹{cash:,.2f}",
        border=True
    )

with col3:
    st.metric(
        "Holdings Value",
        f"₹{total_holdings_value:,.2f}",
        border=True
    )

with col4:
    st.metric(
        "Total P&L",
        f"₹{total_returns:,.2f}",
        delta=f"{returns_pct:+.2f}%",
        border=True
    )

# ============================================================================
# RECENT ACTIVITY
# ============================================================================

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Watchlist")
    
    watchlist = st.session_state.watchlist
    
    if watchlist:
        for symbol in watchlist[:5]:  # Show top 5
            clean_symbol = symbol.replace('.NS', '')
            st.markdown(f"**{clean_symbol}**")
        
        if len(watchlist) > 5:
            st.caption(f"...and {len(watchlist) - 5} more")
    else:
        st.info("No stocks in watchlist")
    
    if st.button("➕ Add to Watchlist", use_container_width=True):
        st.switch_page("pages/2_🔍_Stock_Discovery.py")

with col2:
    st.subheader("📈 Recent Orders")
    
    recent_orders = portfolio['orders'][-5:] if portfolio['orders'] else []
    
    if recent_orders:
        for order in reversed(recent_orders):
            side_color = "#00D09C" if order['side'] == "BUY" else "#EB5B3C"
            st.markdown(f"""
            <div style='margin-bottom: 8px;'>
                <span style='color: {side_color}; font-weight: 600;'>{order['side']}</span>
                <span style='color: #2E3338;'>{order['quantity']} × {order['symbol'].replace('.NS', '')}</span>
                <span style='color: #7C7E8C; font-size: 12px;'>@ ₹{order['price']:,.2f}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No recent orders")
    
    if st.button("⚡ Place Order", use_container_width=True):
        st.switch_page("pages/5_⚡_Trade_Executor.py")

# ============================================================================
# QUICK ACTIONS
# ============================================================================

st.markdown("---")
st.subheader("⚡ Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Discover Stocks", use_container_width=True, type="primary"):
        st.switch_page("pages/2_🔍_Stock_Discovery.py")

with col2:
    if st.button("📈 Analyze Stock", use_container_width=True):
        st.switch_page("pages/3_📈_Stock_Analyzer.py")

with col3:
    if st.button("💼 View Portfolio", use_container_width=True):
        st.switch_page("pages/4_💼_Portfolio.py")

with col4:
    if st.button("⚡ Execute Trade", use_container_width=True):
        st.switch_page("pages/5_⚡_Trade_Executor.py")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("💡 Tip: Use the sidebar to navigate between pages. All trading is simulated (paper trading).")
