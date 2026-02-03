"""
Project Sentinel - Groww-Style Dashboard
Modern, card-based fintech UI with horizontal navigation
"""

import streamlit as st
from styles import inject_groww_styles, create_horizontal_nav, GrowwColors

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Project Sentinel - Smart Trading",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"  # Collapse sidebar (we won't use it)
)

# ============================================================================
# INJECT GROWW STYLES
# ============================================================================

inject_groww_styles()

# ============================================================================
# HEADER WITH LOGO & SEARCH
# ============================================================================

# Create header container
header_col1, header_col2, header_col3 = st.columns([1, 3, 1])

with header_col1:
    st.markdown(f"""
    <div style='padding: 1rem 0;'>
        <h2 style='color: {GrowwColors.PRIMARY_GREEN}; margin: 0; font-weight: 800;'>
            📈 Sentinel
        </h2>
    </div>
    """, unsafe_allow_html=True)

with header_col2:
    # Large search bar
    search_query = st.text_input(
        "Search",
        placeholder="🔍 Search stocks, mutual funds, IPOs...",
        label_visibility="collapsed",
        key="global_search"
    )

with header_col3:
    st.markdown(f"""
    <div style='padding: 1rem 0; text-align: right;'>
        <span style='color: {GrowwColors.TEXT_SECONDARY}; font-weight: 500;'>
            👤 Your Account
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# HORIZONTAL NAVIGATION
# ============================================================================

selected_page = create_horizontal_nav()

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# SETTINGS PAGE (Define before routing)
# ============================================================================

def render_settings_page():
    """Render the settings page with Groww-style cards"""
    
    st.markdown(f"<h1 style='color: {GrowwColors.TEXT_PRIMARY};'>⚙️ Settings</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card">
            <h3 style='color: {GrowwColors.TEXT_PRIMARY}; margin-top: 0;'>Market Preferences</h3>
        </div>
        """, unsafe_allow_html=True)
        
        market_region = st.selectbox(
            "Market Region",
            options=["INDIA", "US"],
            index=0
        )
    
    with col2:
        st.markdown(f"""
        <div class="card">
            <h3 style='color: {GrowwColors.TEXT_PRIMARY}; margin-top: 0;'>Risk Management</h3>
        </div>
        """, unsafe_allow_html=True)
        
        max_position = st.number_input(
            "Max Position Size (₹)",
            min_value=1000,
            max_value=1000000,
            value=50000,
            step=1000
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Save button
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.success("✅ Settings saved successfully!")


# ============================================================================
# ROUTE TO SELECTED PAGE
# ============================================================================

if selected_page == "Home":
    from dashboard_components.home import render_home_page
    render_home_page()

elif selected_page == "Discover":
    from dashboard_components.stock_discovery_groww import render_stock_discovery
    render_stock_discovery()

elif selected_page == "Analyze":
    from dashboard_components.stock_analyzer_groww import render_stock_analyzer
    render_stock_analyzer()

elif selected_page == "Portfolio":
    from dashboard_components.portfolio_tracker_groww import render_portfolio_tracker
    render_portfolio_tracker()

elif selected_page == "Trade":
    from dashboard_components.trade_executor_groww import render_trade_executor
    render_trade_executor()

elif selected_page == "Settings":
    render_settings_page()
