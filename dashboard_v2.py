"""
Project Sentinel - Professional Trading Dashboard
Built with native Streamlit components and proper theming
"""

import streamlit as st
from streamlit_option_menu import option_menu

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Sentinel - Smart Trading",
    page_icon=":material/analytics:",
    layout="wide",
   
    initial_sidebar_state="collapsed"
)

# ============================================================================
# HEADER
# ============================================================================

header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

with header_col1:
    st.markdown("### :material/trending_up: **Sentinel**")

with header_col2:
    search_query = st.text_input(
        "Search",
        placeholder=":material/search: Search stocks, IPOs, mutual funds...",
        label_visibility="collapsed",
        key="global_search"
    )

with header_col3:
    st.markdown(":material/account_circle: **Your account**", unsafe_allow_html=True)

# ============================================================================
# NAVIGATION
# ============================================================================

selected_page = option_menu(
    menu_title=None,
    options=["Home", "Discover", "Analyze", "Portfolio", "Trade", "Settings"],
    icons=["house", "search", "graph-up", "briefcase", "arrow-left-right", "gear"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#FFFFFF"},
        "icon": {"color": "#7C7E8C", "font-size": "18px"},
        "nav-link": {
            "font-size": "14px",
            "text-align": "center",
            "margin": "0px",
            "padding": "12px 24px",
            "color": "#44475B",
            "font-weight": "500",
        },
        "nav-link-selected": {
            "background-color": "#E6FAF5",
            "color": "#00D09C",
            "font-weight": "600",
        },
    },
)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# ROUTE TO PAGES
# ============================================================================

if selected_page == "Home":
    from dashboard_components.home_v2 import render_home_page
    render_home_page()

elif selected_page == "Discover":
    from dashboard_components.stock_discovery_v2 import render_stock_discovery  
    render_stock_discovery()

elif selected_page == "Analyze":
    from dashboard_components.stock_analyzer_v2 import render_stock_analyzer
    render_stock_analyzer()

elif selected_page == "Portfolio":
    from dashboard_components.portfolio_tracker_v2 import render_portfolio_tracker
    render_portfolio_tracker()

elif selected_page == "Trade":
    from dashboard_components.trade_executor_v2 import render_trade_executor
    render_trade_executor()

elif selected_page == "Settings":
    st.title(":material/settings: Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.subheader("Market preferences")
            market_region = st.selectbox("Market region", options=["INDIA", "US"], index=0)
    
    with col2:
        with st.container(border=True):
            st.subheader("Risk management")
            max_position = st.number_input("Max position size (₹)", min_value=1000, max_value=1000000, value=50000, step=1000)
    
    if st.button("Save settings", type="primary", use_container_width=True, icon=":material/save:"):
        st.success("Settings saved successfully!", icon=":material/check_circle:")
