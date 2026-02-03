"""
Home Page - Groww Style
Modern card-based market overview with ticker strip and quick actions
"""

import streamlit as st
from datetime import datetime
import pytz
from styles import GrowwColors, create_ticker_strip, create_metric_card, create_stock_card

try:
    import yfinance as yf
except ImportError:
    yf = None


def render_home_page():
    """Render the Groww-style home page"""
    
    # ========================================================================
    # MARKET INDICES TICKER STRIP
    # ========================================================================
    
    st.markdown(f"<h2 style='color: {GrowwColors.TEXT_PRIMARY}; margin-bottom: 1.5rem;'>📊 Market Overview</h2>", unsafe_allow_html=True)
    
    # Fetch indices data
    indices_data = fetch_indices_data()
    create_ticker_strip(indices_data)
    
    # ========================================================================
    # PORTFOLIO SUMMARY & QUICK ACTIONS
    # ========================================================================
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_portfolio_summary_card()
    
    with col2:
        render_quick_actions()
    
    # ========================================================================
    # WATCHLIST
    # ========================================================================
    
    st.markdown(f"<h3 style='color: {GrowwColors.TEXT_PRIMARY}; margin: 2rem 0 1rem 0;'>📌 Your Watchlist</h3>", unsafe_allow_html=True)
    render_watchlist()
    
    # ========================================================================
    # MARKET STATUS
    # ========================================================================
    
    st.markdown("<br>", unsafe_allow_html=True)
    render_market_status()


def fetch_indices_data():
    """Fetch current market indices data"""
    
    indices = {}
    
    if yf:
        try:
            # Fetch Nifty 50
            nifty = yf.Ticker("^NSEI")
            nifty_hist = nifty.history(period='2d')
            if len(nifty_hist) >= 2:
                current = nifty_hist['Close'].iloc[-1]
                prev = nifty_hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                indices["NIFTY 50"] = {"price": current, "change": change}
            
            # Fetch Bank Nifty
            banknifty = yf.Ticker("^NSEBANK")
            bn_hist = banknifty.history(period='2d')
            if len(bn_hist) >= 2:
                current = bn_hist['Close'].iloc[-1]
                prev = bn_hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                indices["BANK NIFTY"] = {"price": current, "change": change}
            
            # Fetch Sensex
            sensex = yf.Ticker("^BSESN")
            sensex_hist = sensex.history(period='2d')
            if len(sensex_hist) >= 2:
                current = sensex_hist['Close'].iloc[-1]
                prev = sensex_hist['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                indices["SENSEX"] = {"price": current, "change": change}
        
        except:
            pass
    
    # Fallback data if fetch fails
    if not indices:
        indices = {
            "NIFTY 50": {"price": 21500, "change": 0.75},
            "BANK NIFTY": {"price": 45200, "change": -0.35},
            "SENSEX": {"price": 71000, "change": 0.50}
        }
    
    return indices


def render_portfolio_summary_card():
    """Render portfolio summary as a large card"""
    
    # Get portfolio data from session state
    if 'paper_portfolio' in st.session_state:
        portfolio = st.session_state.paper_portfolio
        cash = portfolio.get('cash', 100000)
        positions = portfolio.get('positions', {})
        
        # Calculate portfolio value
        portfolio_value = cash
        unrealized_pnl = 0
        
        for symbol, pos in positions.items():
            portfolio_value += pos.get('market_value', 0)
            unrealized_pnl += pos.get('pnl', 0)
        
        total_pnl_pct = ((portfolio_value - 100000) / 100000) * 100 if portfolio_value > 0 else 0
    else:
        portfolio_value = 100000
        unrealized_pnl = 0
        total_pnl_pct = 0
    
    # Determine colors
    pnl_color = GrowwColors.PRIMARY_GREEN if unrealized_pnl >= 0 else GrowwColors.DANGER_RED
    pnl_sign = "+" if unrealized_pnl >= 0 else ""
    
    html = f"""
    <div class="card" style="background: linear-gradient(135deg, {GrowwColors.PRIMARY_GREEN}15 0%, {GrowwColors.CARD_BG} 100%);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.9rem; font-weight: 500; margin-bottom: 0.5rem;">
                    Total Portfolio Value
                </div>
                <div class="price-display">
                    ₹{portfolio_value:,.2f}
                </div>
                <div style="margin-top: 1rem; display: flex; gap: 2rem;">
                    <div>
                        <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.25rem;">
                            Today's P&L
                        </div>
                        <div style="color: {pnl_color}; font-size: 1.1rem; font-weight: 700;">
                            {pnl_sign}₹{abs(unrealized_pnl):,.2f}
                        </div>
                    </div>
                    <div>
                        <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.25rem;">
                            Total Return
                        </div>
                        <div style="color: {pnl_color}; font-size: 1.1rem; font-weight: 700;">
                            {pnl_sign}{total_pnl_pct:.2f}%
                        </div>
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 3rem; opacity: 0.3;">💼</div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def render_quick_actions():
    """Render quick action cards"""
    
    st.markdown(f"""
    <div class="card">
        <h4 style='color: {GrowwColors.TEXT_PRIMARY}; margin-top: 0;'>Quick Actions</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Discover button
    st.markdown(f"""
    <div class="card card-hover" style="background-color: {GrowwColors.PRIMARY_GREEN}15; border: 2px solid {GrowwColors.PRIMARY_GREEN}30; cursor: pointer; text-align: center; padding: 1.25rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔍</div>
        <div style="font-weight: 600; color: {GrowwColors.TEXT_PRIMARY}; font-size: 1rem;">
            Discover Stocks
        </div>
        <div style="font-size: 0.85rem; color: {GrowwColors.TEXT_SECONDARY}; margin-top: 0.25rem;">
            Find trending opportunities
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analyze button
    st.markdown(f"""
    <div class="card card-hover" style="background-color: {GrowwColors.CHART_BLUE}15; border: 2px solid {GrowwColors.CHART_BLUE}30; cursor: pointer; text-align: center; padding: 1.25rem;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
        <div style="font-weight: 600; color: {GrowwColors.TEXT_PRIMARY}; font-size: 1rem;">
            Analyze Stock
        </div>
        <div style="font-size: 0.85rem; color: {GrowwColors.TEXT_SECONDARY}; margin-top: 0.25rem;">
            Technical analysis & charts
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Trade button
    st.markdown(f"""
    <div class="card card-hover" style="background-color: {GrowwColors.PRIMARY_GREEN}; cursor: pointer; text-align: center; padding: 1.25rem; box-shadow: 0 4px 12px rgba(0, 208, 156, 0.25);">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">💰</div>
        <div style="font-weight: 600; color: white; font-size: 1rem;">
            Place Trade
        </div>
        <div style="font-size: 0.85rem; color: white; opacity: 0.9; margin-top: 0.25rem;">
            Buy or sell stocks
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_watchlist():
    """Render watchlist with stock cards"""
    
    # Sample watchlist stocks
    watchlist = [
        {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "price": 2450.50, "change": 1.25},
        {"symbol": "TCS.NS", "name": "Tata Consultancy Services", "price": 3680.20, "change": -0.45},
        {"symbol": "INFY.NS", "name": "Infosys", "price": 1520.75, "change": 0.80},
        {"symbol": "HDFCBANK.NS", "name": "HDFC Bank", "price": 1645.30, "change": 0.35},
    ]
    
    for stock in watchlist:
        create_stock_card(
            symbol=stock["symbol"],
            name=stock["name"],
            price=stock["price"],
            change_pct=stock["change"]
        )
        st.markdown("<br>", unsafe_allow_html=True)


def render_market_status():
    """Show market open/closed status"""
    
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    
    # Market hours: 9:15 AM - 3:30 PM IST (Mon-Fri)
    market_open_time = now.replace(hour=9, minute=15, second=0)
    market_close_time = now.replace(hour=15, minute=30, second=0)
    
    is_market_open = (
        now.weekday() < 5 and  # Monday = 0, Friday = 4
        market_open_time <= now <= market_close_time
    )
    
    if is_market_open:
        status_color = GrowwColors.PRIMARY_GREEN
        status_text = "🟢 Market is OPEN"
        status_desc = "Live trading until 3:30 PM IST"
    else:
        status_color = GrowwColors.DANGER_RED
        status_text = "🔴 Market is CLOSED"
        if now.weekday() >= 5:
            status_desc = "Opens Monday at 9:15 AM IST"
        else:
            status_desc = "Opens tomorrow at 9:15 AM IST"
    
    html = f"""
    <div class="card" style="background-color: {status_color}10; border-left: 4px solid {status_color};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: 700; font-size: 1.1rem; color: {status_color};">
                    {status_text}
                </div>
                <div style="font-size: 0.9rem; color: {GrowwColors.TEXT_SECONDARY}; margin-top: 0.25rem;">
                    {status_desc}
                </div>
            </div>
            <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.9rem;">
                {now.strftime('%I:%M %p IST')}
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
