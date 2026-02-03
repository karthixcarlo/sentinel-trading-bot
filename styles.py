"""
Groww-Style CSS Injection & Styling Module

This module provides the visual foundation for the Groww-inspired dashboard.
Includes color palette, CSS overrides, and reusable styling functions.
"""

import streamlit as st

# ============================================================================
# GROWW COLOR PALETTE
# ============================================================================

class GrowwColors:
    """Groww investment platform color scheme"""
    
    # Primary Colors
    PRIMARY_GREEN = "#00D09C"      # Main brand color (profits, CTA)
    DANGER_RED = "#EB5B3C"         # Losses, sell actions
    
    # Backgrounds
    APP_BG = "#F4F6F8"             # Main app background (light gray)
    CARD_BG = "#FFFFFF"            # Card backgrounds (white)
    HOVER_BG = "#F8F9FA"           # Hover state
    
    # Text Colors
    TEXT_PRIMARY = "#44475B"       # Main text
    TEXT_SECONDARY = "#7C7E8C"     # Secondary text, labels
    TEXT_MUTED = "#A0A4B8"         # Disabled, placeholder text
    
    # Borders & Dividers
    BORDER_LIGHT = "#E5E7EB"       # Light borders
    BORDER_DARK = "#D1D5DB"        # Darker borders
    
    # Status Colors
    SUCCESS_BG = "#D1FAE5"         # Success background
    SUCCESS_TEXT = "#047857"       # Success text
    ERROR_BG = "#FEE2E2"           # Error background
    ERROR_TEXT = "#DC2626"         # Error text
    WARNING_BG = "#FEF3C7"         # Warning background
    WARNING_TEXT = "#D97706"       # Warning text
    
    # Chart Colors
    CHART_GREEN = "#10B981"        # Positive movement
    CHART_RED = "#EF4444"          # Negative movement
    CHART_BLUE = "#3B82F6"         # Neutral data


# ============================================================================
# CSS INJECTION
# ============================================================================

def inject_groww_styles():
    """
    Inject custom CSS to transform Streamlit into Groww-like UI.
    
    This function:
    1. Hides Streamlit defaults (hamburger menu, footer)
    2. Applies Groww color scheme
    3. Styles components as cards
    4. Removes default padding
    5. Customizes scrollbars
    """
    
    css = f"""
    <style>
    /* ===== GLOBAL STYLES ===== */
    
    /* Import Inter font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Set root background */
    .stApp {{
        background-color: {GrowwColors.APP_BG};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Remove default Streamlit padding */
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }}
    
    /* ===== HIDE STREAMLIT DEFAULTS ===== */
    
    /* Hide hamburger menu */
    #MainMenu {{
        visibility: hidden;
    }}
    
    /* Hide Streamlit footer */
    footer {{
        visibility: hidden;
    }}
    
    /* Hide "Deploy" button */
    .stDeployButton {{
        display: none;
    }}
    
    /* Hide header */
    header {{
        visibility: hidden;
    }}
    
    /* ===== CUSTOM SCROLLBAR ===== */
    
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {GrowwColors.APP_BG};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {GrowwColors.BORDER_DARK};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {GrowwColors.TEXT_SECONDARY};
    }}
    
    /* ===== CARD STYLING ===== */
    
    /* Style all containers as cards */
    div[data-testid="stVerticalBlock"] > div {{
        background-color: {GrowwColors.CARD_BG};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }}
    
    /* Metric cards */
    div[data-testid="stMetric"] {{
        background-color: {GrowwColors.CARD_BG};
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    /* Metric label text */
    div[data-testid="stMetric"] label {{
        color: {GrowwColors.TEXT_SECONDARY} !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Metric value text */
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {GrowwColors.TEXT_PRIMARY} !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }}
    
    /* Metric delta (positive) */
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] > div {{
        color: {GrowwColors.PRIMARY_GREEN} !important;
    }}
    
    /* ===== BUTTON STYLING ===== */
    
    /* Primary button (Buy/CTA) */
    .stButton > button[kind="primary"] {{
        background-color: {GrowwColors.PRIMARY_GREEN} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(0, 208, 156, 0.25) !important;
    }}
    
    .stButton > button[kind="primary"]:hover {{
        background-color: #00B887 !important;
        box-shadow: 0 6px 16px rgba(0, 208, 156, 0.35) !important;
        transform: translateY(-1px);
    }}
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {{
        background-color: white !important;
        color: {GrowwColors.TEXT_PRIMARY} !important;
        border: 1px solid {GrowwColors.BORDER_LIGHT} !important;
        border-radius: 8px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        background-color: {GrowwColors.HOVER_BG} !important;
        border-color: {GrowwColors.BORDER_DARK} !important;
    }}
    
    /* ===== INPUT STYLING ===== */
    
    /* Text inputs */
    .stTextInput > div > div > input {{
        background-color: white !important;
        border: 1px solid {GrowwColors.BORDER_LIGHT} !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        color: {GrowwColors.TEXT_PRIMARY} !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {GrowwColors.PRIMARY_GREEN} !important;
        box-shadow: 0 0 0 2px rgba(0, 208, 156, 0.1) !important;
    }}
    
    /* Number inputs */
    .stNumberInput > div > div > input {{
        background-color: white !important;
        border: 1px solid {GrowwColors.BORDER_LIGHT} !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        color: {GrowwColors.TEXT_PRIMARY} !important;
    }}
    
    /* Select boxes */
    .stSelectbox > div > div {{
        background-color: white !important;
        border: 1px solid {GrowwColors.BORDER_LIGHT} !important;
        border-radius: 8px !important;
    }}
    
    /* ===== DATAFRAME STYLING ===== */
    
    /* DataFrames */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    /* ===== TABS STYLING ===== */
    
    /* Tab buttons */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
        border-bottom: 2px solid {GrowwColors.BORDER_LIGHT};
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: {GrowwColors.TEXT_SECONDARY};
        font-weight: 500;
        padding: 0.75rem 1.5rem;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: {GrowwColors.HOVER_BG};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: transparent;
        color: {GrowwColors.PRIMARY_GREEN} !important;
        border-bottom: 3px solid {GrowwColors.PRIMARY_GREEN};
    }}
    
    /* ===== ALERTS STYLING ===== */
    
    /* Success alert */
    .stSuccess {{
        background-color: {GrowwColors.SUCCESS_BG} !important;
        color: {GrowwColors.SUCCESS_TEXT} !important;
        border-left: 4px solid {GrowwColors.PRIMARY_GREEN} !important;
        border-radius: 8px !important;
    }}
    
    /* Error alert */
    .stError {{
        background-color: {GrowwColors.ERROR_BG} !important;
        color: {GrowwColors.ERROR_TEXT} !important;
        border-left: 4px solid {GrowwColors.DANGER_RED} !important;
        border-radius: 8px !important;
    }}
    
    /* Warning alert */
    .stWarning {{
        background-color: {GrowwColors.WARNING_BG} !important;
        color: {GrowwColors.WARNING_TEXT} !important;
        border-left: 4px solid #F59E0B !important;
        border-radius: 8px !important;
    }}
    
    /* Info alert */
    .stInfo {{
        background-color: #DBEAFE !important;
        color: #1E40AF !important;
        border-left: 4px solid {GrowwColors.CHART_BLUE} !important;
        border-radius: 8px !important;
    }}
    
    /* ===== EXPANDER STYLING ===== */
    
    .streamlit-expanderHeader {{
        background-color: white;
        border-radius: 8px;
        font-weight: 600;
        color: {GrowwColors.TEXT_PRIMARY};
    }}
    
    /* ===== DIVIDER STYLING ===== */
    
    hr {{
        margin: 2rem 0;
        border: none;
        border-top: 1px solid {GrowwColors.BORDER_LIGHT};
    }}
    
    /* ===== TYPOGRAPHY ===== */
    
    /* Headers */
    h1, h2, h3 {{
        color: {GrowwColors.TEXT_PRIMARY} !important;
        font-weight: 700 !important;
    }}
    
    h1 {{
        font-size: 2.5rem !important;
    }}
    
    h2 {{
        font-size: 2rem !important;
    }}
    
    h3 {{
        font-size: 1.5rem !important;
    }}
    
    /* Paragraph text */
    p {{
        color: {GrowwColors.TEXT_SECONDARY};
        font-size: 0.95rem;
        line-height: 1.6;
    }}
    
    /* ===== CUSTOM CLASSES ===== */
    
    /* Price display (large, bold) */
    .price-display {{
        font-size: 2.5rem;
        font-weight: 800;
        color: {GrowwColors.TEXT_PRIMARY};
        line-height: 1;
    }}
    
    /* Positive change */
    .positive {{
        color: {GrowwColors.PRIMARY_GREEN} !important;
    }}
    
    /* Negative change */
    .negative {{
        color: {GrowwColors.DANGER_RED} !important;
    }}
    
    /* Card container */
    .card {{
        background-color: {GrowwColors.CARD_BG};
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }}
    
    /* Card hover effect */
    .card-hover {{
        transition: all 0.2s ease;
    }}
    
    .card-hover:hover {{
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }}
    
    /* Stock card for discovery grid */
    .stock-card {{
        background-color: {GrowwColors.CARD_BG};
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.2s ease;
        cursor: pointer;
        border: 1px solid transparent;
    }}
    
    .stock-card:hover {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-3px);
        border-color: {GrowwColors.PRIMARY_GREEN}30;
    }}
    
    /* Stock card ticker */
    .stock-ticker {{
        font-weight: 700;
        font-size: 1rem;
        color: {GrowwColors.TEXT_PRIMARY};
        margin-bottom: 0.5rem;
    }}
    
    /* Stock card price */
    .stock-price {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {GrowwColors.TEXT_PRIMARY};
        margin: 0.75rem 0 0.25rem 0;
    }}
    
    /* Stock card change badge */
    .stock-change {{
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }}
    
    .stock-change.positive {{
        background-color: {GrowwColors.PRIMARY_GREEN}20;
        color: {GrowwColors.PRIMARY_GREEN};
    }}
    
    .stock-change.negative {{
        background-color: {GrowwColors.DANGER_RED}20;
        color: {GrowwColors.DANGER_RED};
    }}
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)


# ============================================================================
# HELPER FUNCTIONS FOR CUSTOM COMPONENTS
# ============================================================================

def create_metric_card(label: str, value: str, delta: str = None, delta_color: str = "green"):
    """
    Create a Groww-style metric card with custom HTML.
    
    Args:
        label: Metric label (e.g., "Total Value")
        value: Main value to display (e.g., "₹1,23,456")
        delta: Change indicator (e.g., "+2.5%")
        delta_color: "green" for positive, "red" for negative
    """
    
    delta_html = ""
    if delta:
        color = GrowwColors.PRIMARY_GREEN if delta_color == "green" else GrowwColors.DANGER_RED
        delta_html = f'<div style="color: {color}; font-size: 0.9rem; font-weight: 600; margin-top: 0.5rem;">{delta}</div>'
    
    html = f"""
    <div class="card" style="text-align: center;">
        <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.875rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 0.5rem;">
            {label}
        </div>
        <div class="price-display">
            {value}
        </div>
        {delta_html}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def create_stock_card(symbol: str, name: str, price: float, change_pct: float):
    """
    Create a stock card for the watchlist/discovery view.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE.NS")
        name: Company name
        price: Current price
        change_pct: Percentage change
    """
    
    change_color = GrowwColors.PRIMARY_GREEN if change_pct >= 0 else GrowwColors.DANGER_RED
    change_sign = "+" if change_pct >= 0 else ""
    
    html = f"""
    <div class="card card-hover" style="display: flex; justify-content: space-between; align-items: center; cursor: pointer;">
        <div>
            <div style="font-weight: 600; font-size: 1rem; color: {GrowwColors.TEXT_PRIMARY};">
                {symbol.replace('.NS', '')}
            </div>
            <div style="font-size: 0.85rem; color: {GrowwColors.TEXT_SECONDARY}; margin-top: 0.25rem;">
                {name}
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 700; font-size: 1.1rem; color: {GrowwColors.TEXT_PRIMARY};">
                ₹{price:,.2f}
            </div>
            <div style="font-weight: 600; font-size: 0.9rem; color: {change_color}; margin-top: 0.25rem;">
                {change_sign}{change_pct:.2f}%
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def create_cta_button(text: str, color: str = "green", icon: str = ""):
    """
    Create a custom CTA button with Groww styling.
    
    Args:
        text: Button text
        color: "green" or "red"
        icon: Emoji icon
    """
    
    bg_color = GrowwColors.PRIMARY_GREEN if color == "green" else GrowwColors.DANGER_RED
    
    html = f"""
    <div style="
        background-color: {bg_color};
        color: white;
        text-align: center;
        padding: 1rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 208, 156, 0.25);
        transition: all 0.2s ease;
    "
    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px rgba(0, 208, 156, 0.35)';"
    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0, 208, 156, 0.25)';"
    >
        {icon} {text}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def create_ticker_strip(indices: dict):
    """
    Create a horizontal ticker strip like Groww's market indices bar.
    
    Args:
        indices: Dict with format {"NIFTY 50": {"price": 21500, "change": 1.2}, ...}
    """
    
    cards_html = ""
    for name, data in indices.items():
        price = data.get('price', 0)
        change = data.get('change', 0)
        color = GrowwColors.PRIMARY_GREEN if change >= 0 else GrowwColors.DANGER_RED
        sign = "+" if change >= 0 else ""
        
        cards_html += f"""
        <div class="card" style="
            flex: 1;
            min-width: 200px;
            margin-right: 1rem;
            text-align: center;
        ">
            <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; font-weight: 500; margin-bottom: 0.5rem;">
                {name}
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {GrowwColors.TEXT_PRIMARY};">
                {price:,.2f}
            </div>
            <div style="color: {color}; font-weight: 600; font-size: 0.95rem; margin-top: 0.25rem;">
                {sign}{change:.2f}%
            </div>
        </div>
        """
    
    html = f"""
    <div style="
        display: flex;
        overflow-x: auto;
        gap: 1rem;
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    ">
        {cards_html}
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


# ============================================================================
# NAVIGATION BAR (Horizontal)
# ============================================================================

def create_horizontal_nav():
    """
    Create Groww-style horizontal navigation bar to replace sidebar.
    Uses streamlit-option-menu with horizontal orientation.
    """
    from streamlit_option_menu import option_menu
    
    selected = option_menu(
        menu_title=None,  # No title
        options=["Home", "Discover", "Analyze", "Portfolio", "Trade", "Settings"],
        icons=["house-fill", "search", "graph-up", "briefcase-fill", "currency-exchange", "gear-fill"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0.5rem 0",
                "background-color": GrowwColors.CARD_BG,
                "border-bottom": f"1px solid {GrowwColors.BORDER_LIGHT}",
            },
            "icon": {
                "color": GrowwColors.TEXT_SECONDARY,
                "font-size": "1.1rem"
            },
            "nav-link": {
                "font-size": "0.95rem",
                "font-weight": "500",
                "color": GrowwColors.TEXT_SECONDARY,
                "text-align": "center",
                "margin": "0 0.5rem",
                "padding": "0.75rem 1.5rem",
                "border-radius": "8px",
                "transition": "all 0.2s ease",
            },
            "nav-link-selected": {
                "background-color": f"{GrowwColors.PRIMARY_GREEN}15",
                "color": GrowwColors.PRIMARY_GREEN,
                "font-weight": "600",
            },
        }
    )
    
    return selected
