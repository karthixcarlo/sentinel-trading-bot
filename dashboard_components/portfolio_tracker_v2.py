"""
Portfolio Tracker - Clean Native Design
"""

import streamlit as st
try:
    import yfinance as yf
except ImportError:
    yf = None

def render_portfolio_tracker():
    """Render portfolio with holdings and orders"""
    
    st.title(":material/account_balance_wallet: Portfolio")
    
    # Initialize portfolio
    if 'paper_portfolio' not in st.session_state:
        st.session_state.paper_portfolio = {
            'cash': 100000,
            'positions': {},
            'orders': [],
            'closed_trades': []
        }
    
    portfolio_data = st.session_state.paper_portfolio
    cash = portfolio_data.get('cash', 100000)
    positions = portfolio_data.get('positions', {})
    orders = portfolio_data.get('orders', [])
    
    # Calculate totals
    portfolio_value = cash
    unrealized_pnl = 0
    
    for pos in positions.values():
        portfolio_value += pos.get('market_value', 0)
        unrealized_pnl += pos.get('pnl', 0)
    
    total_returns = portfolio_value - 100000
    returns_pct = (total_returns / 100000 * 100) if 100000 else 0
    
    # Summary
    with st.container(horizontal=True):
        st.metric(
            "Portfolio value",
            f"₹{portfolio_value:,.2f}",
            border=True
        )
        st.metric(
            "Cash available",
            f"₹{cash:,.2f}",
            border=True
        )
        st.metric(
            "Total returns",
            f"₹{total_returns:,.2f}",
            delta=f"{returns_pct:+.2f}%",
            border=True
        )
        st.metric(
            "Holdings",
            len(positions),
            border=True
        )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Holdings
    if positions:
        st.subheader(":material/trending_up: Your holdings")
        
        if st.button(":material/refresh: Refresh prices", type="secondary"):
            refresh_prices(positions)
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        for symbol, pos in positions.items():
            clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
            quantity = pos.get('quantity', 0)
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('current_price', entry_price)
            market_value = pos.get('market_value', 0)
            pnl = pos.get('pnl', 0)
            pnl_pct = pos.get('pnl_pct', 0)
            
            with st.container(border=True):
                col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**{clean_symbol}**")
                    st.caption(f"{quantity} shares")
                
                with col2:
                    st.metric("Avg price", f"₹{entry_price:,.2f}", label_visibility="collapsed")
                
                with col3:
                    st.metric("Current", f"₹{current_price:,.2f}", label_visibility="collapsed")
                
                with col4:
                    st.metric("Value", f"₹{market_value:,.2f}", label_visibility="collapsed")
                
                with col5:
                    st.metric("P&L", f"₹{pnl:,.2f}", delta=f"{pnl_pct:+.2f}%", label_visibility="collapsed")
    else:
        with st.container(border=True):
            st.info("No holdings yet. Start trading to build your portfolio!", icon=":material/shopping_bag:")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Recent orders
    if orders:
        st.subheader(":material/receipt_long: Recent orders")
        
        for order in orders[-5:][::-1]:
            symbol = order.get('symbol', 'N/A').replace('.NS', '').replace('.BO', '')
            side = order.get('side', 'BUY')
            quantity = order.get('quantity', 0)
            price = order.get('price', 0)
            timestamp = order.get('timestamp', 'N/A')
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    badge_color = "green" if side == "BUY" else "red"
                    st.markdown(f":{badge_color}-badge[{side}] **{symbol}**")
                    st.caption(timestamp)
                
                with col2:
                    st.metric("Qty", quantity, label_visibility="collapsed")
                
                with col3:
                    st.metric("Price", f"₹{price:,.2f}", label_visibility="collapsed")


def refresh_prices(positions):
    """Refresh current prices"""
    if not yf:
        return
    
    for symbol, position in positions.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1d')
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                position['current_price'] = current_price
                
                quantity = position.get('quantity', 0)
                entry_price = position.get('entry_price', 0)
                
                position['market_value'] = current_price * quantity
                position['pnl'] = (current_price - entry_price) * quantity
                position['pnl_pct'] = ((current_price - entry_price) / entry_price * 100) if entry_price else 0
        except:
            pass
    
    st.toast("Prices refreshed!", icon=":material/check_circle:")
