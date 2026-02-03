"""
Portfolio Tracker - Groww Style
Clean row-based holdings view with investment banner
"""

import streamlit as st
from styles import GrowwColors

try:
    import yfinance as yf
except ImportError:
    yf = None


def render_portfolio_tracker():
    """Render the Groww-style portfolio tracker page"""
    
    st.markdown(f"<h1 style='color: {GrowwColors.TEXT_PRIMARY};'>💼 Portfolio</h1>", unsafe_allow_html=True)
    
    # Initialize portfolio from session state
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = {
            'cash': 100000,
            'positions': {},
            'orders': [],
            'closed_trades': []
        }
    
    portfolio_data = st.session_state.paper_portfolio
    
    # ========================================================================
    # TOTAL INVESTMENT BANNER
    # ========================================================================
    
    render_investment_banner(portfolio_data)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # HOLDINGS LIST
    # ========================================================================
    
    positions = portfolio_data.get('positions', {})
    
    if positions:
        st.markdown(f"<h3 style='color: {GrowwColors.TEXT_PRIMARY};'>Your Holdings</h3>", unsafe_allow_html=True)
        
        # Refresh prices button
        if st.button("🔄 Refresh Prices", key="refresh_prices"):
            refresh_all_prices(positions)
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Render each holding as a row
        for symbol, position in positions.items():
            render_holding_row(symbol, position)
    else:
        # Empty state
        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">📊</div>
            <h3 style="color: {GrowwColors.TEXT_PRIMARY};">No holdings yet</h3>
            <p style="color: {GrowwColors.TEXT_SECONDARY};">
                Start trading to build your portfolio
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # ========================================================================
    # RECENT ORDERS
    # ========================================================================
    
    orders = portfolio_data.get('orders', [])
    
    if orders:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: {GrowwColors.TEXT_PRIMARY};'>Recent Orders</h3>", unsafe_allow_html=True)
        
        # Show last 5 orders
        for order in orders[-5:][::-1]:
            render_order_row(order)


def render_investment_banner(portfolio_data):
    """Render the full-width investment summary banner"""
    
    cash = portfolio_data.get('cash', 100000)
    positions = portfolio_data.get('positions', {})
    
    # Calculate portfolio value
    portfolio_value = cash
    total_invested = 100000  # Initial amount
    unrealized_pnl = 0
    
    for symbol, pos in positions.items():
        market_value = pos.get('market_value', 0)
        pnl = pos.get('pnl', 0)
        portfolio_value += market_value
        unrealized_pnl += pnl
    
    # Calculate returns
    total_returns = portfolio_value - total_invested
    returns_pct = (total_returns / total_invested * 100) if total_invested else 0
    
    # Determine colors
    is_positive = total_returns >= 0
    returns_color = GrowwColors.PRIMARY_GREEN if is_positive else GrowwColors.DANGER_RED
    returns_sign = "+" if is_positive else ""
    
    html = f"""
    <div class="card" style="
        background: linear-gradient(135deg, {GrowwColors.PRIMARY_GREEN}10 0%, {GrowwColors.CARD_BG} 100%);
        padding: 2rem;
        margin-bottom: 2rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.95rem; margin-bottom: 0.5rem;">
                    Current Value
                </div>
                <div style="font-size: 3rem; font-weight: 800; color: {GrowwColors.TEXT_PRIMARY};">
                    ₹{portfolio_value:,.2f}
                </div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.9rem; margin-top: 0.5rem;">
                    Cash: ₹{cash:,.2f} | Holdings: {len(positions)}
                </div>
            </div>
            <div style="text-align: right;">
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.95rem; margin-bottom: 0.5rem;">
                    Total Returns
                </div>
                <div style="font-size: 2.5rem; font-weight: 800; color: {returns_color};">
                    {returns_sign}₹{abs(total_returns):,.2f}
                </div>
                <div style="
                    background-color: {returns_color}20;
                    color: {returns_color};
                    display: inline-block;
                    padding: 0.5rem 1rem;
                    border-radius: 8px;
                    font-weight: 700;
                    margin-top: 0.5rem;
                ">
                    {returns_sign}{returns_pct:.2f}%
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def render_holding_row(symbol, position):
    """Render a single holding as a custom row"""
    
    clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
    quantity = position.get('quantity', 0)
    entry_price = position.get('entry_price', 0)
    current_price = position.get('current_price', entry_price)
    market_value = position.get('market_value', 0)
    pnl = position.get('pnl', 0)
    pnl_pct = position.get('pnl_pct', 0)
    
    # Determine P&L color
    is_positive = pnl >= 0
    pnl_color = GrowwColors.PRIMARY_GREEN if is_positive else GrowwColors.DANGER_RED
    pnl_sign = "+" if is_positive else ""
    
    html = f"""
    <div class="card card-hover" style="
        margin-bottom: 0.75rem;
        border: 1px solid {GrowwColors.BORDER_LIGHT};
    ">
        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr; gap: 1rem; align-items: center;">
            <div>
                <div style="font-weight: 700; font-size: 1.1rem; color: {GrowwColors.TEXT_PRIMARY};">
                    {clean_symbol}
                </div>
                <div style="font-size: 0.85rem; color: {GrowwColors.TEXT_SECONDARY};">
                    Qty: {quantity}
                </div>
            </div>
            <div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem;">Avg Price</div>
                <div style="font-weight: 600; color: {GrowwColors.TEXT_PRIMARY};">₹{entry_price:,.2f}</div>
            </div>
            <div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem;">Current</div>
                <div style="font-weight: 600; color: {GrowwColors.TEXT_PRIMARY};">₹{current_price:,.2f}</div>
            </div>
            <div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem;">Value</div>
                <div style="font-weight: 600; color: {GrowwColors.TEXT_PRIMARY};">₹{market_value:,.2f}</div>
            </div>
            <div>
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem;">P&L</div>
                <div style="font-weight: 700; color: {pnl_color}; font-size: 1.1rem;">
                    {pnl_sign}₹{abs(pnl):,.2f}
                </div>
                <div style="color: {pnl_color}; font-weight: 600; font-size: 0.85rem;">
                    ({pnl_sign}{pnl_pct:.2f}%)
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("📊 Analyze", key=f"analyze_{symbol}", use_container_width=True):
            st.session_state.selected_stock = symbol
            st.session_state.nav_selection = "Analyze"
            st.rerun()
    
    with col3:
        if st.button("💰 Sell", key=f"sell_{symbol}", use_container_width=True, type="secondary"):
            st.session_state.quick_sell_symbol = symbol
            st.session_state.quick_sell_qty = quantity
            st.toast(f"Ready to sell {clean_symbol}. Go to Trade page.", icon="💰")


def render_order_row(order):
    """Render a single order in the order history"""
    
    symbol = order.get('symbol', 'N/A').replace('.NS', '').replace('.BO', '')
    side = order.get('side', 'BUY')
    quantity = order.get('quantity', 0)
    price = order.get('price', 0)
    timestamp = order.get('timestamp', 'N/A')
    
    # Icon and color based on side
    if side == "BUY":
        icon = "🟢"
        color = GrowwColors.PRIMARY_GREEN
    else:
        icon = "🔴"
        color = GrowwColors.DANGER_RED
    
    html = f"""
    <div class="card" style="
        margin-bottom: 0.5rem;
        padding: 1rem;
        border-left: 4px solid {color};
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; gap: 1rem; align-items: center;">
                <div style="font-size: 1.5rem;">{icon}</div>
                <div>
                    <div style="font-weight: 700; color: {GrowwColors.TEXT_PRIMARY};">
                        {side} {quantity} {symbol}
                    </div>
                    <div style="font-size: 0.85rem; color: {GrowwColors.TEXT_SECONDARY};">
                        @ ₹{price:,.2f}
                    </div>
                </div>
            </div>
            <div style="text-align: right;">
                <div style="font-weight: 600; color: {GrowwColors.TEXT_PRIMARY};">
                    ₹{quantity * price:,.2f}
                </div>
                <div style="font-size: 0.85rem; color: {GrowwColors.TEXT_SECONDARY};">
                    {timestamp}
                </div>
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def refresh_all_prices(positions):
    """Refresh current prices for all positions"""
    
    if not yf:
        st.warning("yfinance not available. Cannot refresh prices.")
        return
    
    for symbol, position in positions.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                position['current_price'] = current_price
                
                # Recalculate market value and P&L
                quantity = position.get('quantity', 0)
                entry_price = position.get('entry_price', 0)
                
                position['market_value'] = current_price * quantity
                position['pnl'] = (current_price - entry_price) * quantity
                position['pnl_pct'] = ((current_price - entry_price) / entry_price * 100) if entry_price else 0
        
        except:
            pass  # Keep old price if update fails
    
    st.toast("Prices updated!", icon="✅")
