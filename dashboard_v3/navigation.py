"""
Navigation component for all pages
"""
import streamlit as st

def render_top_nav(current_page="Home"):
    """Render top navigation bar"""
    
    # Hide sidebar
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    
    with col1:
        if st.button("⌂ Home", key="nav_home", use_container_width=True, type="primary" if current_page == "Home" else "secondary"):
            st.switch_page("Home.py")
    
    with col2:
        if st.button("◈ Market", key="nav_market", use_container_width=True, type="primary" if current_page == "Market" else "secondary"):
            st.switch_page("pages/1_📊_Market_Overview.py")
    
    with col3:
        if st.button("◉ Discovery", key="nav_discovery", use_container_width=True, type="primary" if current_page == "Discovery" else "secondary"):
            st.switch_page("pages/2_🔍_Stock_Discovery.py")
    
    with col4:
        if st.button("〄 Analyzer", key="nav_analyzer", use_container_width=True, type="primary" if current_page == "Analyzer" else "secondary"):
            st.switch_page("pages/3_📈_Stock_Analyzer.py")
    
    with col5:
        if st.button("◫ Portfolio", key="nav_portfolio", use_container_width=True, type="primary" if current_page == "Portfolio" else "secondary"):
            st.switch_page("pages/4_💼_Portfolio.py")
    
    with col6:
        if st.button("⚡ Trade", key="nav_trade", use_container_width=True, type="primary" if current_page == "Trade" else "secondary"):
            st.switch_page("pages/5_⚡_Trade_Executor.py")
    
    with col7:
        if st.button("◐ Settings", key="nav_settings", use_container_width=True, type="primary" if current_page == "Settings" else "secondary"):
            st.switch_page("pages/6_⚙️_Settings.py")
    
    st.markdown("---")

# Alias for compatibility
render_top_navigation = render_top_nav
