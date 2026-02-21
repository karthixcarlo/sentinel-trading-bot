"""
Universal Navigation & Layout - Reverted to "Old" Premium Theme
Restores the Google Fonts, styling, and icon-based navigation requested by the user.
"""
import streamlit as st

# ==============================================================================
# PREMIUM THEME (Restored from premium_theme.py)
# ==============================================================================

# Import Google Fonts for distinctive typography
PREMIUM_THEME = """
<!-- Google Fonts: DM Sans (clean, modern) + JetBrains Mono (data) -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    /* ============================================ */
    /* GROWW-INSPIRED LIGHT THEME */
    /* ============================================ */
    
    :root {
        /* Light backgrounds */
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #f3f4f6;
        
        /* Card styling */
        --card-bg: #ffffff;
        --card-border: #e5e7eb;
        --card-shadow: rgba(0, 0, 0, 0.05);
        
        /* Text colors */
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        
        /* Groww green accent */
        --accent-green: #00D09C;
        --accent-green-light: #e6f9f5;
        --accent-green-dark: #00b386;
        
        /* Status colors */
        --success: #00D09C;
        --error: #EB5B3C;
        --warning: #f59e0b;
    }
    
    /* ============================================ */
    /* BASE STYLING */
    /* ============================================ */
    
    /* Main app background */
    .stApp {
        background: var(--bg-secondary);
        color: var(--text-primary);
        font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* ============================================ */
    /* CLEAN CARDS (Groww-style) */
    /* ============================================ */
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
        padding: 1.25rem !important;
        box-shadow: 0 1px 3px var(--card-shadow) !important;
        transition: all 0.2s ease !important;
    }
    
    /* Subtle hover effect */
    [data-testid="stMetric"]:hover {
        box-shadow: 0 4px 12px rgba(0, 208, 156, 0.1) !important;
        border-color: var(--accent-green) !important;
        transform: translateY(-2px);
    }
    
    /* ============================================ */
    /* TYPOGRAPHY */
    /* ============================================ */
    
    /* Metric values - Use monospace for data clarity */
    [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', 'SF Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        color: var(--text-primary) !important;
        letter-spacing: -0.02em !important;
        font-variant-numeric: tabular-nums;
    }
    
    /* Metric labels */
    [data-testid="stMetricLabel"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.8125rem !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: 0.01em !important;
    }
    
    /* Positive changes */
    [data-testid="stMetricDelta"] svg[fill*="171"] {
        fill: var(--success) !important;
    }
    
    /* Headings with distinctive spacing */
    h1 {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em !important;
    }
    
    h2, h3 {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.01em !important;
    }
    
    /* ============================================ */
    /* BUTTONS (Groww green) */
    /* ============================================ */
    
    /* Primary buttons */
    .stButton > button[kind="primary"],
    .stButton > button:first-child {
        background: var(--accent-green) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.625rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
    }
    
    .stButton > button:hover {
        background: var(--accent-green-dark) !important;
        box-shadow: 0 4px 8px rgba(0, 208, 156, 0.2) !important;
        transform: translateY(-1px);
    }
    
    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background: white !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 6px !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        border-color: var(--accent-green) !important;
        color: var(--accent-green) !important;
    }
    
    /* ============================================ */
    /* INPUTS & SELECTS */
    /* ============================================ */
    
    /* Text inputs */
    .stTextInput > div > div > input {
        background: white !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
        padding: 0.625rem 0.875rem !important;
        font-size: 0.9375rem !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--accent-green) !important;
        box-shadow: 0 0 0 3px var(--accent-green-light) !important;
        outline: none !important;
    }
    
    /* Select boxes */
    .stSelectbox > div > div {
        background: white !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 6px !important;
    }
    
    .stSelectbox > div > div:hover,
    .stSelectbox > div > div:focus-within {
        border-color: var(--accent-green) !important;
    }
    
    /* ============================================ */
    /* TABS (Clean style) */
    /* ============================================ */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid var(--card-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1rem;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--accent-green);
        background: var(--accent-green-light);
        border-radius: 6px;
    }
    
    .stTabs [aria-selected="true"] {
        color: var(--accent-green) !important;
        border-bottom: 2px solid var(--accent-green) !important;
        background: transparent !important;
    }
    
    /* ============================================ */
    /* HIDE SIDEBAR & STREAMLIT ELEMENTS */
    /* ============================================ */
    
    section[data-testid="stSidebar"] {
        display: none !important;
        width: 0px !important;
    }
    
    button[kind="header"] {
        display: none !important;
    }
    
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
</style>
"""

def setup_page_config(title="Sentinel Trading", icon="📊"):
    """Configure page with standard settings"""
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="collapsed"
    )

def apply_groww_theme():
    """Apply the restored Premium Theme"""
    st.markdown(PREMIUM_THEME, unsafe_allow_html=True)

def render_navigation():
    """Render the old style navigation with icon buttons"""
    
    # Force sidebar collapse and hide again in case theme didn't catch it
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {display: none !important;}
            [data-testid="collapsedControl"] {display: none !important;}
        </style>
    """, unsafe_allow_html=True)
    
    # Navigation buttons - 9 columns for full coverage
    cols = st.columns(9)
    
    with cols[0]:
        if st.button("⌂ Home", key="nav_home", use_container_width=True):
            st.switch_page("Home.py")
            
    with cols[1]:
        if st.button("◈ Market", key="nav_market", use_container_width=True):
            st.switch_page("pages/1_Market.py")
    
    with cols[2]:
        if st.button("◉ Discovery", key="nav_explore", use_container_width=True):
            st.switch_page("pages/2_Stock_Discovery.py")
    
    with cols[3]:
        if st.button("〄 Analyzer", key="nav_stocks", use_container_width=True):
            st.switch_page("pages/3_Stock_Analyzer.py")
    
    with cols[4]:
        if st.button("◫ Portfolio", key="nav_portfolio", use_container_width=True):
            st.switch_page("pages/4_Portfolio.py")
    
    with cols[5]:
        if st.button("⚡ Trade", key="nav_orders", use_container_width=True):
            st.switch_page("pages/5_Trade_Executor.py")
            
    with cols[6]:
        if st.button("⚙️ Settings", key="nav_settings", use_container_width=True):
            st.switch_page("pages/6_Settings.py")
            
    with cols[7]:
        if st.button("🧠 Monitor", key="nav_monitor", use_container_width=True):
            st.switch_page("pages/7_God_Mode.py")
            
    with cols[8]:
        if st.button("🤖 AI Control", key="nav_ai", use_container_width=True):
            st.switch_page("pages/8_Autonomous_Control.py")
    
    st.markdown("---")
