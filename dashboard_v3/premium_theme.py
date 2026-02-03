"""
Groww-Inspired Premium Theme for Streamlit Trading Dashboard
Light, minimal, professional - enhanced with distinctive design touches
"""

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
    /* STATUS INDICATORS */
    /* ============================================ */
    
    /* Success/Info boxes */
    .stSuccess {
        background: var(--accent-green-light) !important;
        border-left: 3px solid var(--success) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
    }
    
    .stInfo {
        background: #eff6ff !important;
        border-left: 3px solid #3b82f6 !important;
        border-radius: 6px !important;
    }
    
    .stError {
        background: #fef2f2 !important;
        border-left: 3px solid var(--error) !important;
        border-radius: 6px !important;
    }
    
    .stWarning {
        background: #fffbeb !important;
        border-left: 3px solid var(--warning) !important;
        border-radius: 6px !important;
    }
    
    /* ============================================ */
    /* EXPANDERS (Clean accordion) */
    /* ============================================ */
    
    .streamlit-expanderHeader {
        background: white !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 6px !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--accent-green) !important;
        background: var(--accent-green-light) !important;
    }
    
    .streamlit-expanderContent {
        background: white !important;
        border: 1px solid var(--card-border) !important;
        border-top: none !important;
        border-radius: 0 0 6px 6px !important;
    }
    
    /* ============================================ */
    /* PROGRESS BARS */
    /* ============================================ */
    
    .stProgress > div > div {
        background: var(--bg-tertiary) !important;
        border-radius: 6px !important;
        height: 8px !important;
    }
    
    .stProgress > div > div > div {
        background: var(--accent-green) !important;
        border-radius: 6px !important;
    }
    
    /* ============================================ */
    /* DATAFRAMES & TABLES */
    /* ============================================ */
    
    .stDataFrame {
        background: white !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
    }
    
    /* ============================================ */
    /* SCROLLBAR (Minimal) */
    /* ============================================ */
    
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--card-border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }
    
    /* ============================================ */
    /* CHARTS (Clean style) */
    /* ============================================ */
    
    .js-plotly-plot {
        background: white !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 8px !important;
        padding: 0.5rem;
    }
    
    /* ============================================ */
    /* ANIMATIONS (Subtle) */
    /* ============================================ */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Smooth entrance for metrics */
    [data-testid="stMetric"] {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Stagger effect */
    [data-testid="column"]:nth-child(1) [data-testid="stMetric"] {
        animation-delay: 0s;
    }
    [data-testid="column"]:nth-child(2) [data-testid="stMetric"] {
        animation-delay: 0.05s;
    }
    [data-testid="column"]:nth-child(3) [data-testid="stMetric"] {
        animation-delay: 0.1s;
    }
    [data-testid="column"]:nth-child(4) [data-testid="stMetric"] {
        animation-delay: 0.15s;
    }
    
    /* ============================================ */
    /* SIDEBAR (If ever needed) */
    /* ============================================ */
    
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid var(--card-border);
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary);
    }
    
    /* ============================================ */
    /* HIDE STREAMLIT BRANDING */
    /* ============================================ */
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ============================================ */
    /* CUSTOM UTILITIES */
    /* ============================================ */
    
    /* Clean separator */
    hr {
        border: none;
        border-top: 1px solid var(--card-border);
        margin: 2rem 0;
    }
    
    /* Links */
    a {
        color: var(--accent-green);
        text-decoration: none;
    }
    
    a:hover {
        color: var(--accent-green-dark);
        text-decoration: underline;
    }
    
</style>
"""

def inject_premium_theme():
    """
    Inject Groww-inspired clean theme CSS into Streamlit app
    Call this at the top of your main page
    """
    import streamlit as st
    st.markdown(PREMIUM_THEME, unsafe_allow_html=True)
