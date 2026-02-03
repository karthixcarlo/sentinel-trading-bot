"""
⚡ Trade Executor - Multi-Page Dashboard
Quick order placement with validation and confirmation
"""

import streamlit as st

st.set_page_config(page_title="Trade Executor", page_icon=":material/bolt:", layout="wide")

st.title(":material/bolt: Trade Executor")

# Quick stats
portfolio = st.session_state.paper_portfolio
cash = portfolio['cash']
positions = portfolio['positions']

total_holdings = sum([p.get('quantity', 0) * p.get('current_price', p.get('average_price', 0)) for p in positions])
portfolio_value = cash + total_holdings

with st.container(horizontal=True):
    st.metric("Cash Available", f"₹{cash:,.2f}", border=True)
    st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}", border=True)
    st.metric("Active Positions", f"{len(positions)}", border=True)

st.markdown("---")

# Trade form
st.subheader("📋 Place Order")

# Check if stock was pre-selected
default_stock = st.session_state.get('selected_stock', '')
if default_stock:
    default_stock = default_stock.replace('.NS', '')

with st.form("trade_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input("Stock Symbol", value=default_stock, placeholder="e.g., RELIANCE, TCS")
    
    with col2:
        side = st.radio("Action", ["BUY", "SELL"], horizontal=True)
    
    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
    
    if order_type == "LIMIT":
        limit_price = st.number_input("Limit Price (₹)", min_value=0.01, value=100.0, step=0.01)
    else:
        limit_price = 0  # Will be filled with current market price
    
    submitted = st.form_submit_button("Place Order", type="primary", use_container_width=True)
    
    if submitted:
        if not symbol:
            st.error("Please enter a stock symbol")
        else:
            # Add .NS if not present
            if not symbol.endswith('.NS'):
                full_symbol = f"{symbol}.NS"
            else:
                full_symbol = symbol
            
            # For MARKET orders, fetch current price
            if order_type == "MARKET":
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(full_symbol)
                    limit_price = ticker.history(period='1d')['Close'].iloc[-1]
                except:
                    st.error("Could not fetch current price. Please use LIMIT order.")
                    st.stop()
            
            total_cost = quantity * limit_price
            brokerage = total_cost * 0.0003
            final_cost = total_cost + brokerage
            
            # Validation
            if side == "BUY":
                if cash < final_cost:
                    st.error(f"❌ Insufficient funds! Available: ₹{cash:,.2f}, Required: ₹{final_cost:,.2f}")
                else:
                    # Execute BUY
                    portfolio['cash'] -= final_cost
                    
                    existing_pos = next((p for p in positions if p['symbol'] == full_symbol), None)
                    if existing_pos:
                        total_qty = existing_pos['quantity'] + quantity
                        total_cost_basis = (existing_pos['quantity'] * existing_pos['average_price']) + (quantity * limit_price)
                        existing_pos['quantity'] = total_qty
                        existing_pos['average_price'] = total_cost_basis / total_qty
                        existing_pos['current_price'] = limit_price
                    else:
                        positions.append({
                            'symbol': full_symbol,
                            'quantity': quantity,
                            'average_price': limit_price,
                            'current_price': limit_price
                        })
                    
                    portfolio['orders'].append({
                        'symbol': full_symbol,
                        'side': side,
                        'quantity': quantity,
                        'price': limit_price
                    })
                    
                    st.success(f":material/check_circle: Order placed: BUY {quantity} shares of {symbol} @ ₹{limit_price:,.2f}")
                    st.balloons()
                    st.toast(f"Bought {quantity} shares of {symbol}", icon=":material/check:")
            
            elif side == "SELL":
                existing_pos = next((p for p in positions if p['symbol'] == full_symbol), None)
                
                if not existing_pos:
                    st.error(f"❌ You don't own any shares of {symbol}")
                elif existing_pos.get('quantity', 0) < quantity:
                    st.error(f"❌ Insufficient shares! You have {existing_pos['quantity']} shares, trying to sell {quantity}")
                else:
                    # Execute SELL
                    existing_pos['quantity'] -= quantity
                    
                    if existing_pos['quantity'] == 0:
                        positions.remove(existing_pos)
                    
                    portfolio['cash'] += (total_cost - brokerage)
                    portfolio['orders'].append({
                        'symbol': full_symbol,
                        'side': side,
                        'quantity': quantity,
                        'price': limit_price
                    })
                    
                    st.success(f":material/check_circle: Order placed: SELL {quantity} shares of {symbol} @ ₹{limit_price:,.2f}")
                    st.balloons()
                    st.toast(f"Sold {quantity} shares of {symbol}", icon=":material/check:")

st.markdown("---")
st.caption(":material/info: All trades are simulated (paper trading). No real money is involved.")
