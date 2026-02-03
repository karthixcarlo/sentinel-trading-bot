"""
Stock Analyzer - Groww Style
Split view layout with clean charts and sticky order panel
"""

import streamlit as st
from styles import GrowwColors

try:
    import yfinance as yf
    import plotly.graph_objects as go
    import pandas as pd
except ImportError:
    yf = None
    go = None
    pd = None


def render_stock_analyzer():
    """Render the Groww-style stock analyzer page with split view"""
    
    st.markdown(f"<h1 style='color: {GrowwColors.TEXT_PRIMARY};'>📊 Stock Analysis</h1>", unsafe_allow_html=True)
    
    # ========================================================================
    # STOCK INPUT
    # ========================================================================
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., RELIANCE.NS, TCS.NS, INFY.NS",
            label_visibility="collapsed",
            key="stock_symbol_input"
        )
    
    with col2:
        period = st.selectbox(
            "Period",
            options=["1mo", "3mo", "6mo", "1y", "2y"],
            index=1,
            label_visibility="collapsed"
        )
    
    if not symbol:
        # Empty state
        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 3rem; margin-top: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">📈</div>
            <h3 style="color: {GrowwColors.TEXT_PRIMARY};">Enter a stock symbol to analyze</h3>
            <p style="color: {GrowwColors.TEXT_SECONDARY};">
                Get detailed technical analysis, charts, and AI recommendations
            </p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # ========================================================================
    # FETCH STOCK DATA
    # ========================================================================
    
    if yf is None or go is None:
        st.error("Missing dependencies. Please install yfinance and plotly.")
        return
    
    with st.spinner(f"Analyzing {symbol}..."):
        stock_data = fetch_stock_data(symbol, period)
    
    if stock_data is None:
        st.error(f"Could not fetch data for {symbol}. Please check the symbol and try again.")
        return
    
    # ========================================================================
    # SPLIT VIEW LAYOUT
    # ========================================================================
    
    col_main, col_action = st.columns([3, 1])
    
    # LEFT SIDE - Main Analysis
    with col_main:
        render_price_header(stock_data)
        st.markdown("<br>", unsafe_allow_html=True)
        render_stock_chart(stock_data, period)
        st.markdown("<br>", unsafe_allow_html=True)
        render_fundamentals_strip(stock_data)
    
    # RIGHT SIDE - Order Panel
    with col_action:
        render_order_panel(stock_data)


def fetch_stock_data(symbol, period):
    """Fetch stock data from yfinance"""
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
        
        info = ticker.info
        
        # Get current price
        current_price = hist['Close'].iloc[-1]
        prev_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) >= 2 else current_price)
        
        # Calculate change
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        
        return {
            'symbol': symbol,
            'hist': hist,
            'info': info,
            'current_price': current_price,
            'prev_close': prev_close,
            'change': change,
            'change_pct': change_pct
        }
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None


def render_price_header(stock_data):
    """Render the huge price display with change badge"""
    
    symbol = stock_data['symbol'].replace('.NS', '').replace('.BO', '')
    current_price = stock_data['current_price']
    change = stock_data['change']
    change_pct = stock_data['change_pct']
    
    # Determine color
    is_positive = change >= 0
    change_color = GrowwColors.PRIMARY_GREEN if is_positive else GrowwColors.DANGER_RED
    change_sign = "+" if is_positive else ""
    arrow = "↗" if is_positive else "↘"
    
    html = f"""
    <div style="margin-bottom: 1.5rem;">
        <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 1.5rem; font-weight: 600; margin-bottom: 0.5rem;">
            {symbol}
        </div>
        <div style="display: flex; align-items: baseline; gap: 1rem;">
            <div style="font-size: 3.5rem; font-weight: 800; color: {GrowwColors.TEXT_PRIMARY}; line-height: 1;">
                ₹{current_price:,.2f}
            </div>
            <div style="
                background-color: {change_color}20;
                color: {change_color};
                padding: 0.5rem 1rem;
                border-radius: 8px;
                font-size: 1.1rem;
                font-weight: 700;
            ">
                {arrow} {change_sign}₹{abs(change):.2f} ({change_sign}{change_pct:.2f}%)
            </div>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)


def render_stock_chart(stock_data, period):
    """Render clean Plotly area chart (Groww style)"""
    
    hist = stock_data['hist']
    is_positive = stock_data['change_pct'] >= 0
    
    # Color based on overall trend
    line_color = GrowwColors.PRIMARY_GREEN if is_positive else GrowwColors.DANGER_RED
    fill_color = f"{GrowwColors.PRIMARY_GREEN}20" if is_positive else f"{GrowwColors.DANGER_RED}20"
    
    # Create area chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Close'],
        mode='lines',
        name='Price',
        line=dict(color=line_color, width=3),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate='₹%{y:,.2f}<extra></extra>'
    ))
    
    # Clean minimal layout (Groww style)
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=20, l=0, r=0, b=40),
        height=400,
        showlegend=False,
        hovermode='x unified',
        xaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            title=None,
            tickfont=dict(size=11, color=GrowwColors.TEXT_SECONDARY)
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            zeroline=False,
            title=None,
            tickformat='₹,.0f',
            tickfont=dict(size=11, color=GrowwColors.TEXT_SECONDARY)
        )
    )
    
    # Configure interactivity
    config = {
        'displayModeBar': False,
        'displaylogo': False
    }
    
    st.plotly_chart(fig, use_container_width=True, config=config)


def render_fundamentals_strip(stock_data):
    """Render 4-metric fundamentals strip"""
    
    info = stock_data['info']
    
    # Extract metrics
    market_cap = info.get('marketCap', 0)
    pe_ratio = info.get('trailingPE', 0)
    beta = info.get('beta', 0)
    roe = info.get('returnOnEquity', 0)
    
    # Format market cap
    if market_cap >= 1e12:
        market_cap_str = f"₹{market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        market_cap_str = f"₹{market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        market_cap_str = f"₹{market_cap/1e6:.2f}M"
    else:
        market_cap_str = f"₹{market_cap:,.0f}"
    
    # Create 4-column grid
    cols = st.columns(4)
    
    metrics = [
        ("Market Cap", market_cap_str),
        ("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A"),
        ("Beta", f"{beta:.2f}" if beta else "N/A"),
        ("ROE", f"{roe*100:.2f}%" if roe else "N/A")
    ]
    
    for col, (label, value) in zip(cols, metrics):
        with col:
            html = f"""
            <div class="card" style="text-align: center; padding: 1rem;">
                <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.5rem;">
                    {label}
                </div>
                <div style="color: {GrowwColors.TEXT_PRIMARY}; font-size: 1.3rem; font-weight: 700;">
                    {value}
                </div>
            </div>
            """
            st.markdown(html, unsafe_allow_html=True)


def render_order_panel(stock_data):
    """Render the sticky order panel (right sidebar)"""
    
    symbol = stock_data['symbol']
    current_price = stock_data['current_price']
    
    # Wrap in styled container
    st.markdown(f"""
    <div style="
        border: 1px solid {GrowwColors.BORDER_LIGHT};
        border-radius: 12px;
        padding: 1.5rem;
        background-color: {GrowwColors.CARD_BG};
        position: sticky;
        top: 1rem;
    ">
        <h3 style="color: {GrowwColors.TEXT_PRIMARY}; margin-top: 0; margin-bottom: 1rem;">
            Place Order
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Buy/Sell Toggle
    st.markdown(f"<div style='margin-top: -1rem;'></div>", unsafe_allow_html=True)
    
    order_type = st.radio(
        "Order Type",
        options=["BUY", "SELL"],
        horizontal=True,
        label_visibility="collapsed",
        key="order_type_toggle"
    )
    
    # Current Price Display
    st.markdown(f"""
    <div style="
        background-color: {GrowwColors.APP_BG};
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    ">
        <div style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.85rem; margin-bottom: 0.25rem;">
            Current Price
        </div>
        <div style="color: {GrowwColors.TEXT_PRIMARY}; font-size: 1.5rem; font-weight: 700;">
            ₹{current_price:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quantity Input
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=10000,
        value=1,
        step=1,
        key="order_quantity"
    )
    
    # Calculate total
    total_value = current_price * quantity
    
    st.markdown(f"""
    <div style="
        padding: 0.75rem;
        background-color: {GrowwColors.APP_BG};
        border-radius: 8px;
        margin: 1rem 0;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.9rem;">Total Value</span>
            <span style="color: {GrowwColors.TEXT_PRIMARY}; font-weight: 700; font-size: 1.1rem;">₹{total_value:,.2f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Massive BUY/SELL button
    button_color = GrowwColors.PRIMARY_GREEN if order_type == "BUY" else GrowwColors.DANGER_RED
    button_text = f"{order_type} {quantity} {'share' if quantity == 1 else 'shares'}"
    
    st.markdown(f"""
    <div style="
        background-color: {button_color};
        color: white;
        text-align: center;
        padding: 1.25rem;
        border-radius: 8px;
        font-weight: 700;
        font-size: 1.2rem;
        cursor: pointer;
        box-shadow: 0 4px 12px {button_color}40;
        transition: all 0.2s ease;
        margin-top: 1.5rem;
    "
    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 16px {button_color}60';"
    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px {button_color}40';"
    >
        {button_text.upper()}
    </div>
    """, unsafe_allow_html=True)
    
    # Actual button (hidden but functional)
    if st.button(f"{order_type}", key="execute_order", use_container_width=True):
        execute_order(symbol, order_type, quantity, current_price)


def execute_order(symbol, side, quantity, price):
    """Execute the paper trading order"""
    
    try:
        # Import portfolio
        from paper_trading_portfolio import PaperTradingPortfolio
        
        # Initialize portfolio from session state
        if 'paper_portfolio' not in st.session_state:
            st.session_state.paper_portfolio = {
                'cash': 100000,
                'positions': {},
                'orders': [],
                'closed_trades': []
            }
        
        portfolio = PaperTradingPortfolio(
            initial_cash=st.session_state.paper_portfolio.get('cash', 100000)
        )
        
        # Load existing state
        portfolio.positions = st.session_state.paper_portfolio.get('positions', {})
        portfolio.orders = st.session_state.paper_portfolio.get('orders', [])
        portfolio.closed_trades = st.session_state.paper_portfolio.get('closed_trades', [])
        
        # Execute order
        success = portfolio.execute_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price
        )
        
        if success:
            # Save back to session state
            st.session_state.paper_portfolio = {
                'cash': portfolio.cash,
                'positions': portfolio.positions,
                'orders': portfolio.orders,
                'closed_trades': portfolio.closed_trades
            }
            
            st.success(f"✅ {side} order executed! {quantity} shares @ ₹{price:,.2f}")
            st.balloons()
        else:
            st.error(f"❌ Order failed. Please check your balance/position.")
    
    except Exception as e:
        st.error(f"Error executing order: {str(e)}")
