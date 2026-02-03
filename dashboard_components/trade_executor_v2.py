"""
Trade Executor - Clean Native Design
"""

import streamlit as st
from datetime import datetime
try:
    import yfinance as yf
except ImportError:
    yf = None

def render_trade_executor():
    """Render trade execution interface"""
    
    st.title(":material/currency_rupee: Place trade")
    
    # Portfolio stats
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
    
    # Quick stats
    with st.container(horizontal=True):
        st.metric("Cash available", f"₹{cash:,.2f}", border=True)
        st.metric("Portfolio value", f"₹{portfolio_value:,.2f}", border=True)
        st.metric("Active positions", len(positions), border=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Order form
    with st.container(border=True):
        st.subheader(":material/shopping_cart: Quick order")
        
        # Symbol input
        symbol = st.text_input(
            "Stock symbol",
            placeholder="e.g., RELIANCE.NS, TCS.NS",
            key="trade_symbol"
        )
        
        if symbol and yf:
            current_price = fetch_price(symbol)
            
            if current_price:
                st.metric("Current price", f"₹{current_price:,.2f}", border=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Order details
                col1, col2 = st.columns(2)
                
                with col1:
                    order_side = st.radio("Order type", ["BUY", "SELL"], horizontal=True)
                
                with col2:
                    quantity = st.number_input("Quantity", min_value=1, max_value=10000, value=1, step=1)
                
                # Calculate costs
                total_value = current_price * quantity
                brokerage = total_value * 0.001
                total_cost = total_value + (brokerage if order_side == "BUY" else -brokerage)
                
                with st.container(border=True):
                    st.markdown("**Order summary**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.caption("Total value")
                        st.caption("Brokerage (0.1%)")
                        st.caption("**Total cost**")
                    
                    with col2:
                        st.caption(f"₹{total_value:,.2f}")
                        st.caption(f"₹{brokerage:,.2f}")
                        st.caption(f"**₹{total_cost:,.2f}**")
                
                # Validation
                warnings = []
                
                if order_side == "BUY" and total_cost > cash:
                    warnings.append("Insufficient cash balance")
                
                if order_side == "SELL" and symbol not in positions:
                    warnings.append("No position in this stock")
                elif order_side == "SELL" and symbol in positions:
                    available_qty = positions[symbol].get('quantity', 0)
                    if quantity > available_qty:
                        warnings.append(f"You only have {available_qty} shares")
                
                if warnings:
                    for warning in warnings:
                        st.warning(warning, icon=":material/warning:")
                
                # Execute button
                if st.button(
                    f"{order_side} {quantity} shares",
                    type="primary",
                    use_container_width=True,
                    disabled=len(warnings) > 0,
                    icon=":material/check_circle:"
                ):
                    execute_order(symbol, order_side, quantity, current_price, portfolio_data)
                    st.balloons()
                    st.toast(f"Order executed: {order_side} {quantity} shares", icon=":material/check_circle:")
                    st.rerun()
            
            else:
                st.error("Could not fetch price for this symbol", icon=":material/error:")
        
        elif symbol:
            st.warning("yfinance not available", icon=":material/warning:")
        
        else:
            st.info("Enter a stock symbol to begin", icon=":material/info:")


def fetch_price(symbol):
    """Fetch current stock price"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='1d')
        return hist['Close'].iloc[-1] if not hist.empty else None
    except:
        return None


def execute_order(symbol, side, quantity, price, portfolio_data):
    """Execute paper trading order"""
    
    total_value = price * quantity
    brokerage = total_value * 0.001
    
    if side == "BUY":
        total_cost = total_value + brokerage
        portfolio_data['cash'] -= total_cost
        
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
        portfolio_data['cash'] += total_proceeds
        
        if symbol in portfolio_data['positions']:
            pos = portfolio_data['positions'][symbol]
            pos['quantity'] -= quantity
            
            if pos['quantity'] <= 0:
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
    st.session_state.paper_portfolio = portfolio_data
