# -*- coding: utf-8 -*-
"""
Portfolio - Multi-Page Dashboard
Track holdings, P&L, and order history with export functionality
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add parent directory to path so we can import layout
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from layout import setup_page_config, render_navigation, apply_groww_theme

# Page setup
setup_page_config("Portfolio", "💼")

# Apply theme
apply_groww_theme()

# Navigation
render_navigation()

st.title("Portfolio")

if 'paper_portfolio' not in st.session_state:
    st.session_state.paper_portfolio = {
        'cash': 100000.0,
        'positions': [],
        'orders': []
    }

portfolio = st.session_state.paper_portfolio
cash = portfolio['cash']
positions = portfolio['positions']
orders = portfolio['orders']

# Calculate totals
total_holdings_value = 0
for pos in positions:
    total_holdings_value += pos.get('quantity', 0) * pos.get('current_price', pos.get('average_price', 0))

portfolio_value = cash + total_holdings_value
initial_capital = st.session_state.settings['initial_capital']
total_returns = portfolio_value - initial_capital
returns_pct = (total_returns / initial_capital) * 100 if initial_capital > 0 else 0

# Summary metrics
with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Portfolio Value", f"₹{portfolio_value:,.2f}", delta=f"{returns_pct:+.2f}%", border=True)
    with col2:
        st.metric("Cash Available", f"₹{cash:,.2f}", border=True)
    with col3:
        st.metric("Holdings Value", f"₹{total_holdings_value:,.2f}", border=True)
    with col4:
        st.metric("Total Returns", f"₹{total_returns:,.2f}", delta=f"{returns_pct:+.2f}%", border=True)

st.markdown("<br>", unsafe_allow_html=True)

# Holdings
st.subheader("Current Holdings")

if positions:
    for pos in positions:
        symbol = pos.get('symbol', '')
        clean_symbol = symbol.replace('.NS', '')
        quantity = pos.get('quantity', 0)
        avg_price = pos.get('average_price', 0)
        current_price = pos.get('current_price', avg_price)
        
        position_value = quantity * current_price
        cost_basis = quantity * avg_price
        pnl = position_value - cost_basis
        pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0
        
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{clean_symbol}**")
                st.caption(f"{quantity} shares @ ₹{avg_price:,.2f}")
            
            with col2:
                st.metric("Current", f"₹{current_price:,.2f}", label_visibility="collapsed")
            
            with col3:
                st.metric("Value", f"₹{position_value:,.2f}", label_visibility="collapsed")
            
            with col4:
                st.metric("P&L", f"₹{pnl:,.2f}", delta=f"{pnl_pct:+.2f}%", label_visibility="collapsed")
            
            with col5:
                if st.button("Sell", key=f"sell_{symbol}", use_container_width=True):
                    st.session_state.selected_stock = symbol
                    st.switch_page("pages/5_Trade_Executor.py")
    
    # Download portfolio
    st.markdown("---")
    
    portfolio_df = pd.DataFrame([{
        'Symbol': pos.get('symbol', '').replace('.NS', ''),
        'Quantity': pos.get('quantity', 0),
        'Avg Price': pos.get('average_price', 0),
        'Current Price': pos.get('current_price', 0),
        'Value': pos.get('quantity', 0) * pos.get('current_price', 0),
        'P&L': (pos.get('quantity', 0) * pos.get('current_price', 0)) - (pos.get('quantity', 0) * pos.get('average_price', 0)),
        'P&L %': ((pos.get('current_price', 0) - pos.get('average_price', 0)) / pos.get('average_price', 1) * 100)
    } for pos in positions])
    
    csv = portfolio_df.to_csv(index=False)
    
    st.download_button(
        label="Download Portfolio Report",
        data=csv,
        file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=False
    )
else:
    st.info("No holdings yet. Start trading to build your portfolio!")

st.markdown("<br>", unsafe_allow_html=True)

# Order history
st.subheader("Order History")

if orders:
    for order in reversed(orders[-10:]):  # Last 10 orders
        side_color = "#00D09C" if order['side'] == "BUY" else "#EB5B3C"
        st.markdown(f"""
        <div style='padding: 12px; background-color: #F6F8FA; border-radius: 8px; margin-bottom: 8px;'>
            <span style='color: {side_color}; font-weight: 700;'>{order['side']}</span>
            <span style='color: #2E3338; margin-left: 8px;'>{order['quantity']} × {order['symbol'].replace('.NS', '')}</span>
            <span style='color: #7C7E8C; margin-left: 8px;'>@ ₹{order['price']:,.2f}</span>
        </div>
        """, unsafe_allow_html=True)
    
    if len(orders) > 10:
        st.caption(f"...and {len(orders) - 10} more orders")
else:
    st.info("No orders yet")
