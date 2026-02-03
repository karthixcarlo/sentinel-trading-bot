"""
Portfolio Tracker Component

Track and display paper trading portfolio with live P&L.
"""

import streamlit as st
from paper_trading_portfolio import PaperTradingPortfolio

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def render_portfolio_page():
    """Main function to render the portfolio tracking page."""
    
    st.title("💼 Portfolio Tracker (Paper Trading)")
    
    st.markdown("""
    **Paper Trading Mode** - Practice with virtual money, zero risk!
    - Track positions and P&L in real-time
    - Learn trading strategies safely
    - Build confidence before live trading
    """)
    
    st.divider()
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    # Portfolio controls
    display_portfolio_controls(portfolio)
    
    st.divider()
    
    # Update prices if positions exist
    if portfolio.positions and YFINANCE_AVAILABLE:
        update_portfolio_prices(portfolio)
    
    # Portfolio summary
    display_portfolio_summary(portfolio)
    
    st.divider()
    
    # Positions table
    display_positions(portfolio)
    
    st.divider()
    
    # Recent orders
    display_recent_orders(portfolio)
    
    st.divider()
    
    # Closed trades
    display_closed_trades(portfolio)


def display_portfolio_controls(portfolio: PaperTradingPortfolio):
    """Display portfolio control buttons."""
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Prices", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📊 View Stats", use_container_width=True):
            st.session_state.show_stats = True
    
    with col3:
        if st.button("🔴 Reset Portfolio", use_container_width=True):
            st.session_state.show_reset_confirm = True
    
    # Reset confirmation dialog
    if st.session_state.get('show_reset_confirm', False):
        st.warning("⚠️ This will delete all positions and reset to ₹1,00,000. Are you sure?")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Yes, Reset", type="primary"):
                portfolio.reset_portfolio()
                st.session_state.show_reset_confirm = False
                st.success("Portfolio reset successfully!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel"):
                st.session_state.show_reset_confirm = False
                st.rerun()


def update_portfolio_prices(portfolio: PaperTradingPortfolio):
    """Update current prices for all positions."""
    
    symbols = list(portfolio.positions.keys())
    
    if not symbols:
        return
    
    try:
        with st.spinner("Updating prices..."):
            prices = {}
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                    
                    if current_price > 0:
                        prices[symbol] = current_price
                
                except:
                    # Use last known price
                    prices[symbol] = portfolio.positions[symbol].current_price
            
            portfolio.update_prices(prices)
    
    except Exception as e:
        st.warning(f"Could not update all prices: {str(e)}")


def display_portfolio_summary(portfolio: PaperTradingPortfolio):
    """Display portfolio summary metrics."""
    
    st.markdown("### 📈 Portfolio Summary")
    
    stats = portfolio.get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Value",
            value=f"₹{stats['portfolio_value']:,.2f}",
            delta=f"{stats['total_pnl_pct']:+.2f}%"
        )
    
    with col2:
        st.metric(
            label="Cash Balance",
            value=f"₹{stats['cash']:,.2f}"
        )
    
    with col3:
        pnl = stats['unrealized_pnl'] + stats['realized_pnl']
        st.metric(
            label="Total P&L",
            value=f"₹{abs(pnl):,.2f}",
            delta=f"{pnl:+.2f}",
            delta_color="normal" if pnl >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            label="Open Positions",
            value=stats['positions_count']
        )
    
    # Additional stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Unrealized P&L",
            value=f"₹{abs(stats['unrealized_pnl']):,.2f}",
            delta=f"{stats['unrealized_pnl']:+.2f}",
            delta_color="normal" if stats['unrealized_pnl'] >= 0 else "inverse"
        )
    
    with col2:
        st.metric(
            label="Realized P&L",
            value=f"₹{abs(stats['realized_pnl']):,.2f}",
            delta=f"{stats['realized_pnl']:+.2f}",
            delta_color="normal" if stats['realized_pnl'] >= 0 else "inverse"
        )
    
    with col3:
        st.metric(
            label="Total Trades",
            value=stats['total_trades']
        )
    
    with col4:
        st.metric(
            label="Win Rate",
            value=f"{stats['win_rate']:.1f}%"
        )


def display_positions(portfolio: PaperTradingPortfolio):
    """Display current positions table."""
    
    st.markdown("### 📋 Current Positions")
    
    if not portfolio.positions:
        st.info("No open positions. Go to **Trade** page to place your first order!")
        return
    
    # Build positions table
    positions_data = []
    
    for symbol, pos in portfolio.positions.items():
        pnl_color = "🟢" if pos.pnl >= 0 else "🔴"
        
        positions_data.append({
            "Symbol": symbol,
            "Qty": pos.quantity,
            "Entry Price": f"₹{pos.entry_price:,.2f}",
            "Current Price": f"₹{pos.current_price:,.2f}",
            "Market Value": f"₹{pos.market_value:,.2f}",
            "P&L": f"{pnl_color} ₹{abs(pos.pnl):,.2f}",
            "P&L %": f"{pos.pnl_pct:+.2f}%",
            "Entry Date": pos.entry_date
        })
    
    st.dataframe(
        positions_data,
        use_container_width=True,
        hide_index=True
    )


def display_recent_orders(portfolio: PaperTradingPortfolio):
    """Display recent orders."""
    
    st.markdown("### 📜 Recent Orders")
    
    if not portfolio.orders:
        st.info("No orders yet.")
        return
    
    # Show last 10 orders
    recent_orders = portfolio.orders[-10:][::-1]  # Reverse to show newest first
    
    orders_data = []
    
    for order in recent_orders:
        side_color = "🟢 BUY" if order.side == "BUY" else "🔴 SELL"
        
        orders_data.append({
            "Time": order.timestamp,
            "Symbol": order.symbol,
            "Side": side_color,
            "Qty": order.quantity,
            "Price": f"₹{order.price:,.2f}",
            "Total": f"₹{order.quantity * order.price:,.2f}",
            "Status": order.status
        })
    
    st.dataframe(
        orders_data,
        use_container_width=True,
        hide_index=True
    )


def display_closed_trades(portfolio: PaperTradingPortfolio):
    """Display closed trades."""
    
    st.markdown("### 💰 Closed Trades")
    
    if not portfolio.closed_trades:
        st.info("No closed trades yet.")
        return
    
    # Show last 10 closed trades
    recent_trades = portfolio.closed_trades[-10:][::-1]
    
    trades_data = []
    
    for trade in recent_trades:
        pnl_color = "🟢" if trade['pnl'] >= 0 else "🔴"
        
        trades_data.append({
            "Symbol": trade['symbol'],
            "Qty": trade['quantity'],
            "Entry": f"₹{trade['entry_price']:,.2f}",
            "Exit": f"₹{trade['exit_price']:,.2f}",
            "P&L": f"{pnl_color} ₹{abs(trade['pnl']):,.2f}",
            "P&L %": f"{trade['pnl_pct']:+.2f}%",
            "Exit Date": trade['exit_date']
        })
    
    st.dataframe(
        trades_data,
        use_container_width=True,
        hide_index=True
    )
    
    # Summary stats for closed trades
    if portfolio.closed_trades:
        total_realized = sum(t['pnl'] for t in portfolio.closed_trades)
        winning_trades = len([t for t in portfolio.closed_trades if t['pnl'] > 0])
        total_trades = len(portfolio.closed_trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Realized P&L",
                value=f"₹{abs(total_realized):,.2f}",
                delta=f"{total_realized:+.2f}",
                delta_color="normal" if total_realized >= 0 else "inverse"
            )
        
        with col2:
            st.metric(
                label="Winning Trades",
                value=f"{winning_trades}/{total_trades}"
            )
        
        with col3:
            st.metric(
                label="Win Rate",
                value=f"{win_rate:.1f}%"
            )
