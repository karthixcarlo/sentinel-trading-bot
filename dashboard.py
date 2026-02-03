"""
Project Sentinel - Interactive Dashboard

Main Streamlit application providing a user-friendly interface for:
- Stock discovery and analysis
- Portfolio tracking
- Trade execution
- Performance monitoring
"""

import streamlit as st
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Project Sentinel",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Main container improvements */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Headers */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid #1f77b4;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    
    h3 {
        color: #34495e;
        font-weight: 500;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #7f8c8d;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1f77b4 0%, #1565c0 100%);
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
        padding: 1rem 1.5rem;
    }
    
    /* Tables */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    
    /* Sidebar improvements */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    [data-testid="stSidebar"] hr {
        margin: 1rem 0;
        border: none;
        border-top: 2px solid #dee2e6;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        font-weight: 600;
        font-size: 1.1rem;
        border-radius: 8px;
        background-color: #f8f9fa;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e9ecef;
    }
    
    /* Custom badges */
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 0.9rem;
        font-weight: 700;
        line-height: 1;
        color: #fff;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 12px;
        margin: 0 0.25rem;
    }
    
    .badge-success {
        background-color: #28a745;
    }
    
    .badge-danger {
        background-color: #dc3545;
    }
    
    .badge-warning {
        background-color: #ffc107;
        color: #212529;
    }
    
    .badge-info {
        background-color: #17a2b8;
    }
    
    /* Cards */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    
    .card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transition: all 0.3s ease;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #1f77b4;
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e9ecef;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #1f77b4;
        box-shadow: 0 0 0 0.2rem rgba(31, 119, 180, 0.25);
    }
    
    /* Number input */
    .stNumberInput > div > div > input {
        border-radius: 8px;
    }
    
    /* Select box */
    .stSelectbox > div > div {
        border-radius: 8px;
    }
    
    /* Slider */
    .stSlider > div > div > div > div {
        background-color: #1f77b4;
    }
    
    /* Success/Error messages with icons */
    .element-container:has(.stSuccess) {
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/trading.png", width=80)
    st.title("Project Sentinel")
    st.markdown("---")
    
    selected = option_menu(
        menu_title="Navigation",
        options=["Home", "Discover", "Analyze", "Portfolio", "Trade", "Settings", "Performance"],
        icons=["house", "search", "graph-up", "briefcase", "currency-exchange", "gear", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#1f77b4", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee",
            },
            "nav-link-selected": {"background-color": "#1f77b4"},
        }
    )
    
    st.markdown("---")
    
    # Market region selector
    market_region = st.selectbox(
        "Market Region",
        options=["INDIA", "US"],
        index=0,
        help="Select market region for trading"
    )
    
    # Store in session state
    st.session_state.market_region = market_region
    
    st.markdown("---")
    st.caption("© 2026 Project Sentinel")
    st.caption("Autonomous Trading Agent")


# Main content area
def main():
    """Main application controller."""
    
    # Route to appropriate page based on selection
    if selected == "Home":
        try:
            from dashboard_components.market_overview import render_market_overview
            render_market_overview()
        except Exception as e:
            st.error(f"Error loading Home page: {str(e)}")
    
    elif selected == "Discover":
        try:
            from dashboard_components.stock_discovery import render_stock_discovery
            render_stock_discovery()
        except Exception as e:
            st.error(f"Error loading Discover page: {str(e)}")
    
    elif selected == "Analyze":
        try:
            from dashboard_components.stock_analyzer import render_stock_analyzer
            render_stock_analyzer()
        except Exception as e:
            st.error(f"Error loading Analyze page: {str(e)}")
            render_analyze_page()  # Fallback to placeholder
    
    elif selected == "Portfolio":
        try:
            from dashboard_components.portfolio_tracker import render_portfolio_page
            render_portfolio_page()
        except Exception as e:
            st.error(f"Error loading Portfolio page: {str(e)}")
            render_portfolio_page()  # Fallback to placeholder
    
    elif selected == "Trade":
        try:
            from dashboard_components.trade_executor import render_trade_page
            render_trade_page()
        except Exception as e:
            st.error(f"Error loading Trade page: {str(e)}")
            render_trade_page()  # Fallback to placeholder
    
    elif selected == "Settings":
        render_settings_page()
    
    elif selected == "Performance":
        render_performance_page()


def render_analyze_page():
    """Render stock analysis page (placeholder)."""
    st.title("📊 Stock Analysis")
    
    st.info("🚧 Stock Analyzer - Coming Soon!")
    
    st.markdown("""
    This page will provide:
    - Deep technical analysis of selected stocks
    - Price charts with indicators (RSI, MACD, SMA)
    - News sentiment analysis
    - AI-powered recommendations (BUY/SELL/HOLD)
    - Position sizing calculator
    - One-click trade execution
    """)
    
    # Stock symbol input
    symbol = st.text_input("Enter Stock Symbol", placeholder="e.g., RELIANCE, TCS, INFY")
    
    if symbol:
        if st.button("Analyze", type="primary"):
            st.success(f"Analysis for {symbol} - Feature under development")


def render_portfolio_page():
    """Render portfolio tracking page (placeholder)."""
    st.title("💼 Portfolio")
    
    st.info("🚧 Portfolio Tracker - Coming Soon!")
    
    st.markdown("""
    This page will display:
    - Current open positions with live P&L
    - Holdings (delivery positions)
    - Today's trades and performance
    - Account balance and margin
    - Position distribution charts
    - Auto-refresh every 30 seconds
    """)
    
    # Mock data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Portfolio Value", value="₹1,00,000")
    
    with col2:
        st.metric(label="Today's P&L", value="₹2,500", delta="+2.5%")
    
    with col3:
        st.metric(label="Total P&L", value="₹15,000", delta="+15%")
    
    with col4:
        st.metric(label="Open Positions", value="3")


def render_trade_page():
    """Render manual trade execution page (placeholder)."""
    st.title("💰 Execute Trade")
    
    st.info("🚧 Trade Executor - Coming Soon!")
    
    st.markdown("""
    This page will allow you to:
    - Manually submit buy/sell orders
    - Choose order type (Market, Limit, Stop-Loss)
    - Validate against risk limits
    - View order confirmations
    - Track order status
    """)
    
    # Trade form
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("Stock Symbol", placeholder="e.g., RELIANCE")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        order_type = st.selectbox("Order Type", ["MARKET", "LIMIT", "STOP_LOSS"])
    
    with col2:
        side = st.radio("Side", ["BUY", "SELL"], horizontal=True)
        if order_type != "MARKET":
            price = st.number_input("Price (₹)", min_value=0.0, value=0.0, step=0.5)
        
        if st.button("Submit Order", type="primary", use_container_width=True):
            st.success("Order submission - Feature under development")


def render_settings_page():
    """Render settings configuration page."""
    st.title("⚙️ Settings")
    
    st.markdown("### Risk Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_position_pct = st.slider(
            "Max Position Size (%)",
            min_value=1,
            max_value=10,
            value=5,
            help="Maximum percentage of portfolio for a single position"
        )
        
        max_risk_pct = st.slider(
            "Max Risk Per Trade (%)",
            min_value=0.5,
            max_value=3.0,
            value=1.0,
            step=0.25,
            help="Maximum risk as percentage of portfolio per trade"
        )
    
    with col2:
        hurdle_rate = st.slider(
            "Hurdle Rate (%)",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="Minimum expected profit after costs"
        )
        
        account_balance = st.number_input(
            "Account Balance (₹)",
            min_value=1000.0,
            value=100000.0,
            step=1000.0,
            help="Total account balance"
        )
    
    st.markdown("### Trading Mode")
    
    trading_mode = st.radio(
        "Select Mode",
        ["Paper Trading (Simulated)", "Live Trading (Real Money)"],
        help="Paper trading uses simulated orders, Live trading uses real broker API"
    )
    
    if trading_mode == "Live Trading (Real Money)":
        st.warning("⚠️ Live trading requires Zerodha Kite Connect subscription (₹2,000/month)")
    
    st.markdown("### Data Settings")
    
    cache_ttl = st.slider(
        "Cache TTL (seconds)",
        min_value=60,
        max_value=600,
        value=300,
        help="How long to cache market data"
    )
    
    if st.button("💾 Save Settings", type="primary"):
        # Store in session state
        st.session_state.max_position_pct = max_position_pct
        st.session_state.max_risk_pct = max_risk_pct
        st.session_state.hurdle_rate = hurdle_rate
        st.session_state.account_balance = account_balance
        st.session_state.trading_mode = trading_mode
        st.session_state.cache_ttl = cache_ttl
        
        st.success("✅ Settings saved successfully!")


def render_performance_page():
    """Render performance analytics page (placeholder)."""
    st.title("📈 Performance Analytics")
    
    st.info("🚧 Performance Analytics - Coming Soon!")
    
    st.markdown("""
    This page will show:
    - Equity curve chart
    - Win rate and profit factor
    - Maximum drawdown
    - Sharpe ratio
    - Trade history with filters
    - Monthly/weekly performance breakdown
    """)
    
    # Mock metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Total Trades", value="47")
    
    with col2:
        st.metric(label="Win Rate", value="63.8%")
    
    with col3:
        st.metric(label="Profit Factor", value="1.85")
    
    with col4:
        st.metric(label="Max Drawdown", value="-5.2%")


# Run the application
if __name__ == "__main__":
    main()
