"""
Trade Executor Component

Execute paper trading orders with validation.
"""

import streamlit as st
from paper_trading_portfolio import PaperTradingPortfolio

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def render_trade_page():
    """Main function to render the trade execution page."""
    
    st.title("💰 Execute Trade (Paper Trading)")
    
    st.markdown("""
    **Paper Trading Mode** - All orders are simulated!
    - Practice placing orders risk-free
    - Learn order types and execution
    - Build trading confidence
    """)
    
    st.divider()
    
    # Initialize portfolio
    portfolio = PaperTradingPortfolio()
    
    # Display current portfolio status
    display_quick_stats(portfolio)
    
    st.divider()
    
    # Order entry form
    display_order_form(portfolio)
    
    st.divider()
    
    # Quick actions for existing positions
    display_quick_actions(portfolio)


def display_quick_stats(portfolio: PaperTradingPortfolio):
    """Display quick portfolio stats."""
    
    stats = portfolio.get_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Cash Available",
            value=f"₹{stats['cash']:,.2f}"
        )
    
    with col2:
        st.metric(
            label="Portfolio Value",
            value=f"₹{stats['portfolio_value']:,.2f}"
        )
    
    with col3:
        st.metric(
            label="Open Positions",
            value=stats['positions_count']
        )


def display_order_form(portfolio: PaperTradingPortfolio):
    """Display order entry form."""
    
    st.markdown("### 📝 Place Order")
    
    col1, col2 = st.columns(2)
    
    with col1:
        symbol = st.text_input(
            "Stock Symbol",
            placeholder="e.g., RELIANCE.NS, TCS.NS, INFY.NS",
            help="Add .NS for NSE stocks, .BO for BSE stocks"
        )
        
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1,
            help="Number of shares to buy/sell"
        )
        
        order_type = st.selectbox(
            "Order Type",
            options=["MARKET", "LIMIT"],
            help="MARKET: Execute at current price, LIMIT: Execute at specified price"
        )
    
    with col2:
        side = st.radio(
            "Side",
            options=["BUY", "SELL"],
            horizontal=True,
            help="BUY: Open new position, SELL: Close existing position"
        )
        
        # Get current price if symbol is entered
        current_price = 0.0
        if symbol and YFINANCE_AVAILABLE:
            try:
                with st.spinner("Fetching price..."):
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
                    
                    if current_price > 0:
                        st.info(f"💹 Current Price: ₹{current_price:,.2f}")
            except:
                pass
        
        if order_type == "LIMIT":
            limit_price = st.number_input(
                "Limit Price (₹)",
                min_value=0.0,
                value=current_price if current_price > 0 else 0.0,
                step=0.5,
                help="Price at which to execute the order"
            )
        else:
            limit_price = current_price
    
    # Order preview
    if symbol and quantity and current_price > 0:
        st.markdown("### 📊 Order Preview")
        
        execution_price = limit_price if order_type == "LIMIT" else current_price
        total_value = quantity * execution_price
        brokerage = total_value * 0.001  # 0.1%
        total_cost = total_value + brokerage if side == "BUY" else total_value - brokerage
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Execution Price",
                value=f"₹{execution_price:,.2f}"
            )
        
        with col2:
            st.metric(
                label="Total Value",
                value=f"₹{total_value:,.2f}"
            )
        
        with col3:
            st.metric(
                label="Estimated Total",
                value=f"₹{total_cost:,.2f}",
                help="Includes 0.1% simulated brokerage"
            )
        
        # Validation checks
        warnings = []
        
        if side == "BUY" and total_cost > portfolio.cash:
            warnings.append("⚠️ Insufficient cash balance!")
        
        if side == "SELL":
            if symbol not in portfolio.positions:
                warnings.append("⚠️ No position in this stock!")
            elif portfolio.positions[symbol].quantity < quantity:
                warnings.append(f"⚠️ Insufficient shares! You only have {portfolio.positions[symbol].quantity}")
        
        for warning in warnings:
            st.warning(warning)
        
        # Submit button
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button(
                f"{'🟢 ' if side == 'BUY' else '🔴 '}{side} {quantity} shares",
                type="primary",
                use_container_width=True,
                disabled=len(warnings) > 0
            ):
                # Execute order
                success = portfolio.execute_order(
                    symbol=symbol,
                    side=side,
                    quantity=quantity,
                    price=execution_price
                )
                
                if success:
                    st.success(f"✅ Order executed successfully!\n\n{side} {quantity} shares of {symbol} at ₹{execution_price:,.2f}")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Order execution failed. Please check your inputs and try again.")


def display_quick_actions(portfolio: PaperTradingPortfolio):
    """Display quick actions for existing positions."""
    
    if not portfolio.positions:
        return
    
    st.markdown("### ⚡ Quick Actions")
    
    st.info("Click a position to quickly close it")
    
    for symbol, pos in portfolio.positions.items():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.write(f"**{symbol}**")
            st.caption(f"{pos.quantity} shares @ ₹{pos.entry_price:,.2f}")
        
        with col2:
            current_value = pos.market_value
            st.write(f"₹{current_value:,.2f}")
        
        with col3:
            pnl_color = "🟢" if pos.pnl >= 0 else "🔴"
            st.write(f"{pnl_color} {pos.pnl_pct:+.2f}%")
        
        with col4:
            if st.button(f"Sell All", key=f"sell_{symbol}", type="secondary"):
                if YFINANCE_AVAILABLE:
                    try:
                        ticker = yf.Ticker(symbol)
                        info = ticker.info
                        current_price = info.get('regularMarketPrice', info.get('currentPrice', pos.current_price))
                        
                        success = portfolio.execute_order(
                            symbol=symbol,
                            side="SELL",
                            quantity=pos.quantity,
                            price=current_price
                        )
                        
                        if success:
                            st.success(f"✅ Sold all {pos.quantity} shares of {symbol}")
                            st.rerun()
                        else:
                            st.error("Failed to execute sell order")
                    except:
                        st.error("Unable to fetch current price")
