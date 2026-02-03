"""
📊 Market Overview - Multi-Page Dashboard
Shows market indices, portfolio summary, and positions
"""

import streamlit as st
import yfinance as yf
from datetime import datetime
import pytz

st.set_page_config(page_title="Market Overview", page_icon=":material/bar_chart:", layout="wide", initial_sidebar_state="collapsed")

# Inject premium theme
import sys
sys.path.insert(0, 'c:\\Users\\Karthi\\Desktop\\Agent\\dashboard_v3')
from premium_theme import inject_premium_theme
inject_premium_theme()

# Top Navigation
from navigation import render_top_nav
render_top_nav("Market Overview")

# Initialize session state if not exists
if 'paper_portfolio' not in st.session_state:
    st.session_state.paper_portfolio = {
        'cash': 100000.0,
        'positions': [],
        'orders': []
    }

if 'settings' not in st.session_state:
    st.session_state.settings = {
        'initial_capital': 100000.0
    }

# ============================================================================
# CACHING - Performance Optimization
# ============================================================================

@st.cache_data(ttl=300)  # 5-minute cache
def fetch_market_indices():
    """Fetch live market index data with caching"""
    
    sample_indices = {
        "Nifty 50": {"value": 22150.50, "change": 1.25},
        "Bank Nifty": {"value": 48250.75, "change": -0.85},
        "Sensex": {"value": 73280.30, "change": 0.95}
    }
    
    indices_data = {}
    
    index_symbols = [
        ("^NSEI", "Nifty 50"),
        ("^NSEBANK", "Bank Nifty"),
        ("^BSESN", "Sensex")
    ]
    
    for symbol, name in index_symbols:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='2d')
            
            if len(hist) >= 2:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = current - prev
                change_pct = (change / prev) * 100
                
                indices_data[name] = {
                    "value": current,
                    "change": change_pct
                }
            else:
                indices_data[name] = sample_indices[name]
        except:
            indices_data[name] = sample_indices[name]
    
    return indices_data

# ============================================================================
# MAIN PAGE
# ============================================================================

st.title(":material/bar_chart: Market Overview")

# Market Indices
st.subheader("Market Indices")

with st.spinner("Loading market data..."):
    indices_data = fetch_market_indices()

with st.container(horizontal=True):
    for name, data in indices_data.items():
        st.metric(
            label=name,
            value=f"₹{data['value']:,.2f}",
            delta=f"{data['change']:+.2f}%",
            border=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# PORTFOLIO SUMMARY
# ============================================================================

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

with st.container(border=True):
    st.subheader(":material/account_balance_wallet: Your Portfolio")
    
    with st.container(horizontal=True):
        st.metric(
            "Portfolio Value",
            f"₹{portfolio_value:,.2f}",
            delta=f"{returns_pct:+.2f}%",
            border=True
        )
        st.metric(
            "Cash Available",
            f"₹{cash:,.2f}",
            border=True
        )
        st.metric(
            "Holdings Value",
            f"₹{total_holdings_value:,.2f}",
            border=True
        )
        st.metric(
            "Number of Holdings",
            f"{len(positions)}",
            border=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# QUICK ACTIONS
# ============================================================================

st.subheader(":material/bolt: Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### :material/search: Discover Stocks")
        st.caption("Find top gainers, losers, and active stocks")
        if st.button("Discover Now", use_container_width=True, type="primary"):
            st.switch_page("pages/2_🔍_Stock_Discovery.py")

with col2:
    with st.container(border=True):
        st.markdown("### :material/analytics: Analyze Stock")
        st.caption("Deep analysis with charts and signals")
        if st.button("Analyze Now", use_container_width=True):
            st.switch_page("pages/3_📈_Stock_Analyzer.py")

with col3:
    with st.container(border=True):
        st.markdown("###  :material/currency_rupee: Place Trade")
        st.caption("Quick order execution")
        if st.button("Trade Now", use_container_width=True):
            st.switch_page("pages/5_⚡_Trade_Executor.py")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# CURRENT POSITIONS
# ============================================================================

if positions:
    st.subheader(":material/bookmark: Your Positions")
    
    for pos in positions[:5]:  # Show top 5
        symbol = pos.get('symbol', '')
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        quantity = pos.get('quantity', 0)
        average_price = pos.get('average_price', 0)
        current_price = pos.get('current_price', average_price)
        
        position_value = quantity * current_price
        cost_basis = quantity * average_price
        pnl = position_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{clean_symbol}**")
                st.caption(f"{quantity} shares @ ₹{average_price:,.2f}")
            
            with col2:
                st.metric("Current", f"₹{current_price:,.2f}", label_visibility="collapsed")
            
            with col3:
                st.metric("Value", f"₹{position_value:,.2f}", label_visibility="collapsed")
            
            with col4:
                st.metric("P&L", f"₹{pnl:,.2f}", delta=f"{pnl_pct:+.2f}%", label_visibility="collapsed")
    
    if len(positions) > 5:
        st.caption(f"...and {len(positions) - 5} more positions")
        if st.button("View All Positions"):
            st.switch_page("pages/4_💼_Portfolio.py")

else:
    st.info("No positions yet. Start trading to see your holdings here!", icon=":material/info:")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# MARKET STATUS
# ============================================================================

IST = pytz.timezone('Asia/Kolkata')
now = datetime.now(IST)
hour = now.hour

is_open = (9 <= hour < 16) and (now.weekday() < 5)

if is_open:
    st.success(":material/check_circle: Market is OPEN - Trading hours: 9:15 AM - 3:30 PM IST")
else:
    st.info(":material/schedule: Market is CLOSED - Opens tomorrow at 9:15 AM IST")
