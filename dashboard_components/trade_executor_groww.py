"""
Trade Executor - Groww Style
Quick order pad with big number inputs and toast notifications
"""

import streamlit as st
from styles import GrowwColors
from datetime import datetime

try:
    import yfinance as yf
except ImportError:
    yf = None


def render_trade_executor():
    """Render the Groww-style quick order pad"""
    
    st.markdown(f"<h1 style='color: {GrowwColors.TEXT_PRIMARY};'>💰 Trade</h1>", unsafe_allow_html=True)
    
    # ========================================================================
    # QUICK STATS
    # ========================================================================
    
    portfolio_data = st.session_state.get('paper_portfolio', {
        'cash': 100000,
        'positions': {},
        'orders': [],
        'closed_trades': []
    })
    
    cash = portfolio_data.get('cash', 100000)
    positions = portfolio_data.get('positions', {})
    
    portfolio_value = cash
    for pos in positions.values():
        portfolio_value += pos.get('market_value', 0)
    
    # Quick stats banner
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.25rem;">
                Cash Available
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {GrowwColors.TEXT_PRIMARY};">
                ₹{cash:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.25rem;">
                Portfolio Value
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {GrowwColors.TEXT_PRIMARY};">
                ₹{portfolio_value:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.25rem;">
                Open Positions
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {GrowwColors.TEXT_PRIMARY};">
                {len(positions)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # ========================================================================
    # QUICK ORDER PAD
    # ========================================================================
    
    st.markdown(f"<h2 style='color: {GrowwColors.TEXT_PRIMARY};'>Quick Order</h2>", unsafe_allow_html=True)
    
    # Order form in a centered card
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        render_order_form(cash, positions)


def render_order_form(cash, positions):
    """Render the quick order form"""
    
    st.markdown(f"""
    <div class="card" style="padding: 2rem;">
    </div>
    """, unsafe_allow_html=True)
    
    # Stock symbol input
    symbol = st.text_input(
        "Stock Symbol",
        placeholder="e.g., RELIANCE.NS, TCS.NS",
        key="trade_symbol_input"
    )
    
    # Buy/Sell toggle
    st.markdown("<br>", unsafe_allow_html=True)
    
    order_side = st.radio(
        "Order Type",
        options=["BUY", "SELL"],
        horizontal=True,
        key="order_side_radio"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Fetch current price if symbol provided
    current_price = None
    if symbol and yf:
        with st.spinner("Fetching price..."):
            current_price = fetch_current_price(symbol)
    
    if current_price:
        st.markdown(f"""
        <div style="
            background-color: {GrowwColors.APP_BG};
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin: 1rem 0;
        ">
            <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.9rem; margin-bottom: 0.5rem;">
                Current Price
            </div>
            <div style="font-size: 2.5rem; font-weight: 800; color: {GrowwColors.TEXT_PRIMARY};">
                ₹{current_price:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # BIG NUMBER quantity input (ATM-style)
    st.markdown(f"""
    <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.9rem; margin: 1rem 0 0.5rem 0; font-weight: 600;">
        QUANTITY
    </div>
    """, unsafe_allow_html=True)
    
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=10000,
        value=1,
        step=1,
        label_visibility="collapsed",
        key="trade_quantity_input"
    )
    
    # Calculate total
    if current_price:
        total_value = current_price * quantity
        brokerage = total_value * 0.001  # 0.1%
        total_cost = total_value + brokerage if order_side == "BUY" else total_value - brokerage
        
        st.markdown(f"""
        <div style="
            background-color: {GrowwColors.APP_BG};
            padding: 1rem;
            border-radius: 8px;
            margin: 1.5rem 0;
        ">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: {GrowwColors.TEXT_SECONDARY};">Total Value</span>
                <span style="color: {GrowwColors.TEXT_PRIMARY}; font-weight: 600;">₹{total_value:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: {GrowwColors.TEXT_SECONDARY};">Brokerage (0.1%)</span>
                <span style="color: {GrowwColors.TEXT_PRIMARY}; font-weight: 600;">₹{brokerage:,.2f}</span>
            </div>
            <div style="border-top: 1px solid {GrowwColors.BORDER_LIGHT}; margin: 0.5rem 0; padding-top: 0.5rem;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {GrowwColors.TEXT_PRIMARY}; font-weight: 700;">Total Cost</span>
                    <span style="color: {GrowwColors.TEXT_PRIMARY}; font-weight: 700; font-size: 1.2rem;">₹{total_cost:,.2f}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Validation warnings
        warnings = []
        
        if order_side == "BUY" and total_cost > cash:
            warnings.append("⚠️ Insufficient cash balance")
        
        if order_side == "SELL" and symbol not in positions:
            warnings.append("⚠️ No position in this stock")
        elif order_side == "SELL" and symbol in positions:
            available_qty = positions[symbol].get('quantity', 0)
            if quantity > available_qty:
                warnings.append(f"⚠️ You only have {available_qty} shares")
        
        for warning in warnings:
            st.warning(warning)
        
        # MASSIVE ORDER BUTTON
        button_disabled = len(warnings) > 0
        button_color = GrowwColors.PRIMARY_GREEN if order_side == "BUY" else GrowwColors.DANGER_RED
        button_text = f"{order_side} {quantity} {'SHARE' if quantity == 1 else 'SHARES'}"
        
        st.markdown(f"""
        <div style="
            background-color: {button_color if not button_disabled else GrowwColors.TEXT_MUTED};
            color: white;
            text-align: center;
            padding: 1.5rem;
            border-radius: 12px;
            font-weight: 800;
            font-size: 1.5rem;
            cursor: {'pointer' if not button_disabled else 'not-allowed'};
            box-shadow: 0 6px 16px {button_color}40;
            margin-top: 2rem;
            transition: all 0.2s ease;
            opacity: {1 if not button_disabled else 0.5};
        "
        onmouseover="if(!{str(button_disabled).lower()}) {{this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 20px {button_color}60';}}"
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 6px 16px {button_color}40';"
        >
            {button_text}
        </div>
        """, unsafe_allow_html=True)
        
        # Hidden functional button
        if st.button("Execute Order", key="execute_order_btn", disabled=button_disabled):
            execute_order(symbol, order_side, quantity, current_price)
    
    else:
        st.info("💡 Enter a stock symbol to see current price and place order")


def fetch_current_price(symbol):
    """Fetch current stock price"""
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        
        if not hist.empty:
            return hist['Close'].iloc[-1]
    except:
        pass
    
    return None


def execute_order(symbol, side, quantity, price):
    """Execute paper trading order with toast notifications"""
    
    try:
        # Get portfolio from session state
        if 'paper_portfolio' not in st.session_state:
            st.session_state.paper_portfolio = {
                'cash': 100000,
                'positions': {},
                'orders': [],
                'closed_trades': []
            }
        
        portfolio_data = st.session_state.paper_portfolio
        
        # Calculate costs
        total_value = price * quantity
        brokerage = total_value * 0.001
        
        if side == "BUY":
            total_cost = total_value + brokerage
            
            # Deduct cash
            portfolio_data['cash'] -= total_cost
            
            # Add/update position
            if symbol not in portfolio_data['positions']:
                portfolio_data['positions'][symbol] = {
                    'quantity': quantity,
                    'entry_price': price,
                    'current_price': price,
                    'market_value': total_value,
                    'pnl': 0,
                    'pnl_pct': 0
                }
            else:
                # Average up
                pos = portfolio_data['positions'][symbol]
                old_qty = pos['quantity']
                old_avg = pos['entry_price']
                new_qty = old_qty + quantity
                new_avg = ((old_qty * old_avg) + (quantity * price)) / new_qty
                
                pos['quantity'] = new_qty
                pos['entry_price'] = new_avg
                pos['current_price'] = price
                pos['market_value'] = price * new_qty
                pos['pnl'] = (price - new_avg) * new_qty
                pos['pnl_pct'] = ((price - new_avg) / new_avg * 100) if new_avg else 0
        
        else:  # SELL
            total_proceeds = total_value - brokerage
            
            # Add cash
            portfolio_data['cash'] += total_proceeds
            
            # Reduce/close position
            if symbol in portfolio_data['positions']:
                pos = portfolio_data['positions'][symbol]
                pos['quantity'] -= quantity
                
                if pos['quantity'] <= 0:
                    # Close position
                    del portfolio_data['positions'][symbol]
        
        # Record order
        order = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'FILLED'
        }
        
        portfolio_data['orders'].append(order)
        
        # Save back to session state
        st.session_state.paper_portfolio = portfolio_data
        
        # SUCCESS FEEDBACK
        st.balloons()  # Celebration animation
        st.toast(f"✅ {side} order executed! {quantity} shares @ ₹{price:,.2f}", icon="🎉")
        
        st.rerun()
    
    except Exception as e:
        st.toast(f"❌ Order failed: {str(e)}", icon="⚠️")
        st.error(f"Error: {str(e)}")
