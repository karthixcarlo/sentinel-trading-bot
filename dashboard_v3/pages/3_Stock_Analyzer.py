# -*- coding: utf-8 -*-
"""
Stock Analyzer - Multi-Page Dashboard
Deep analysis with BUY/SELL signals, charts, and fundamentals
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

# Add parent directory (dashboard_v3/) and project root to path
PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
DASH_DIR  = os.path.dirname(PAGES_DIR)
ROOT_DIR  = os.path.dirname(DASH_DIR)
sys.path.insert(0, ROOT_DIR)   # project root (for database_manager etc.)
sys.path.insert(0, DASH_DIR)   # dashboard_v3/ (for layout, auth_manager)


try:
    import yfinance as yf
except ImportError:
    yf = None

STOCK_SEARCH_AVAILABLE = False  # complete_nse_stocks was removed; yfinance used directly


try:
    from stock_signal_indicator import display_stock_signal
    SIGNAL_AVAILABLE = True
except ImportError:
    SIGNAL_AVAILABLE = False

from layout import setup_page_config, render_navigation, apply_groww_theme

# Page setup
setup_page_config("Stock Analyzer", "📈")

# Apply theme
apply_groww_theme()

# Navigation
render_navigation()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def init_session_state():
    """Initialize session state if not already done"""
    defaults = {
        'paper_portfolio': {
            'cash': 100000.0,
            'positions': [],
            'orders': []
        },
        'watchlist': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS'],
        'settings': {
            'theme': 'light',
            'auto_refresh': True,
            'refresh_interval': 60,
            'initial_capital': 100000.0
        },
        'filters': {
            'discovery_category': 'gainers',
            'sector_filter': 'All',
            'min_price': 0,
            'max_price': 100000
        },
        'selected_stock': None
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize state
init_session_state()

# ============================================================================
# CACHING - Performance Optimization
# ============================================================================

@st.cache_data(ttl=60)  # 1-minute cache for stock prices
def fetch_stock_data(symbol):
    """Fetch stock data with caching"""
    
    if not yf:
        return None
    
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='6mo')
        info = ticker.info
        
        return {
            'history': hist,
            'info': info
        }
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

# ============================================================================
# MAIN PAGE
# ============================================================================

st.title("Stock Analyzer")

# Stock selector
st.subheader("Select Stock to Analyze")

# Get default from session state (if user clicked Analyze in Discovery)
default_stock = st.session_state.get('selected_stock', "RELIANCE.NS")
if default_stock.endswith(".NS"):
    default_stock = default_stock[:-3]

# Search box
user_input = st.text_input("Enter NSE Stock Symbol (e.g., RELIANCE, TCS, INFY)", value=default_stock).strip().upper()

if not user_input:
    st.info("Please enter a stock symbol to analyze.")
    st.stop()

# Ensure we have .NS suffix for Indian stocks
symbol = f"{user_input}.NS" if not user_input.endswith(".NS") else user_input
st.session_state['selected_stock'] = symbol


# ============================================================================
# BUY/SELL SIGNAL
# ============================================================================

if SIGNAL_AVAILABLE:
    with st.spinner("Analyzing stock signals..."):
        try:
            recommendation, confidence = display_stock_signal(symbol)
        except:
            st.warning("Signal indicator unavailable")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# STOCK DATA & CHART
# ============================================================================

with st.spinner(f"Loading data for {symbol}..."):
    data = fetch_stock_data(symbol)

if not data or data['history'].empty:
    st.error("No data found for this stock")
    st.stop()

hist = data['history']
info = data['info']

# Stock info header
col1, col2, col3, col4 = st.columns(4)

current_price = hist['Close'].iloc[-1]
prev_close = info.get('previousClose', current_price)
change = current_price - prev_close
change_pct = (change / prev_close * 100) if prev_close else 0

with col1:
    st.metric("Current Price", f"₹{current_price:,.2f}", delta=f"{change:+.2f} ({change_pct:+.2f}%)")

with col2:
    st.metric("Day High", f"₹{info.get('dayHigh', 0):,.2f}")

with col3:
    st.metric("Day Low", f"₹{info.get('dayLow', 0):,.2f}")

with col4:
    volume = info.get('volume', 0)
    st.metric("Volume", f"{volume:,}")

# Price chart with Moving Averages
st.subheader("Price Chart with Indicators")

# Calculate Moving Averages
hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
hist['SMA_200'] = hist['Close'].rolling(window=200).mean()

# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

hist['RSI'] = calculate_rsi(hist['Close'])

# Calculate MACD
exp1 = hist['Close'].ewm(span=12, adjust=False).mean()
exp2 = hist['Close'].ewm(span=26, adjust=False).mean()
hist['MACD'] = exp1 - exp2
hist['Signal_Line'] = hist['MACD'].ewm(span=9, adjust=False).mean()

fig = go.Figure()

# Groww-style colors based on change
if change_pct >= 0:
    line_color = "#00D09C"  # Green
    fill_color = "rgba(0, 208, 156, 0.1)"
else:
    line_color = "#EB5B3C"  # Red
    fill_color = "rgba(235, 91, 60, 0.1)"

# Price line
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['Close'],
    mode='lines',
    name='Close Price',
    line=dict(color=line_color, width=2),
    fill='tozeroy',
    fillcolor=fill_color
))

# 20-day SMA (short term)
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['SMA_20'],
    mode='lines',
    name='SMA 20',
    line=dict(color='#FFA500', width=1, dash='dot')
))

# 50-day SMA (medium term)
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['SMA_50'],
    mode='lines',
    name='SMA 50',
    line=dict(color='#4A90E2', width=1.5)
))

# 200-day SMA (long term trend)
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['SMA_200'],
    mode='lines',
    name='SMA 200',
    line=dict(color='#9B59B6', width=2)
))

fig.update_layout(
    height=400,
    margin=dict(l=0, r=0, t=0, b=0),
    plot_bgcolor='white',
    paper_bgcolor='white',
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='#F0F2F6'),
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig, use_container_width=True)

# Trading Signal Analysis
st.markdown("---")
st.subheader("🎯 Technical Indicators")

col1, col2 = st.columns(2)

with col1:
    # RSI Chart
    st.markdown("**RSI (Relative Strength Index)**")
    
    fig_rsi = go.Figure()
    
    current_rsi = hist['RSI'].iloc[-1]
    
    # RSI line
    fig_rsi.add_trace(go.Scatter(
        x=hist.index,
        y=hist['RSI'],
        mode='lines',
        name='RSI',
        line=dict(color='#4A90E2', width=2)
    ))
    
    # Overbought line (70)
    fig_rsi.add_hline(
        y=70, 
        line_dash="dash", 
        line_color="#EB5B3C",
        annotation_text="Overbought (70)",
        annotation_position="right"
    )
    
    # Oversold line (30)
    fig_rsi.add_hline(
        y=30, 
        line_dash="dash", 
        line_color="#00D09C",
        annotation_text="Oversold (30)",
        annotation_position="right"
    )
    
    fig_rsi.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(range=[0, 100], showgrid=True, gridcolor='#F0F2F6'),
        xaxis=dict(showgrid=False)
    )
    
    st.plotly_chart(fig_rsi, use_container_width=True)
    
    # RSI Interpretation
    if current_rsi > 70:
        st.error(f"RSI: {current_rsi:.1f} - **OVERBOUGHT** 🔴 Consider selling")
    elif current_rsi < 30:
        st.success(f"RSI: {current_rsi:.1f} - **OVERSOLD** 🟢 Consider buying")
    else:
        st.info(f"RSI: {current_rsi:.1f} - **NEUTRAL** 🔵")

with col2:
    # MACD Chart
    st.markdown("**MACD (Moving Average Convergence Divergence)**")
    
    fig_macd = go.Figure()
    
    # MACD line
    fig_macd.add_trace(go.Scatter(
        x=hist.index,
        y=hist['MACD'],
        mode='lines',
        name='MACD',
        line=dict(color='#4A90E2', width=2)
    ))
    
    # Signal line
    fig_macd.add_trace(go.Scatter(
        x=hist.index,
        y=hist['Signal_Line'],
        mode='lines',
        name='Signal',
        line=dict(color='#FFA500', width=1.5)
    ))
    
    # Histogram (MACD - Signal)
    macd_histogram = hist['MACD'] - hist['Signal_Line']
    colors = ['#00D09C' if x > 0 else '#EB5B3C' for x in macd_histogram]
    
    fig_macd.add_trace(go.Bar(
        x=hist.index,
        y=macd_histogram,
        name='Histogram',
        marker_color=colors,
        opacity=0.3
    ))
    
    fig_macd.update_layout(
        height=250,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='white',
        paper_bgcolor='white',
        yaxis=dict(showgrid=True, gridcolor='#F0F2F6'),
        xaxis=dict(showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    
    st.plotly_chart(fig_macd, use_container_width=True)
    
    # MACD Interpretation
    current_macd = hist['MACD'].iloc[-1]
    current_signal = hist['Signal_Line'].iloc[-1]
    
    if current_macd > current_signal:
        st.success("MACD > Signal - **BULLISH** 🟢 Uptrend")
    else:
        st.error("MACD < Signal - **BEARISH** 🔴 Downtrend")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# AI ANALYST INSIGHT PANEL (GEMINI-POWERED)
# ============================================================================

st.markdown("---")
st.subheader("AI Analyst Insight")

# Import Gemini analyst and news loader
try:
    from analyst_agent_gemini import AgenticAnalyst
    from dashboard_v3.news_loader import fetch_stock_news, get_news_summary, get_sentiment_indicator
    GEMINI_AVAILABLE = True
except ImportError as e:
    GEMINI_AVAILABLE = False
    st.warning(f"AI Analyst not available: {e}")

if GEMINI_AVAILABLE:
    # Create 2 columns: Left for news, Right for AI insight
    col_news, col_ai = st.columns([1, 1])
    
    with col_news:
        st.markdown("### Recent News")
        
        with st.spinner("Fetching latest news..."):
            news_items = fetch_stock_news(symbol, max_results=3)
        
        if news_items:
            for item in news_items:
                sentiment = get_sentiment_indicator(item['title'])
                with st.expander(f"{sentiment} {item['title'][:60]}...", expanded=False):
                    st.markdown(f"**Source:** {item['source']}")
                    st.markdown(f"**Date:** {item['published_at']}")
                    if item.get('snippet') or item.get('description'):
                        snippet = item.get('snippet') or item.get('description', '')
                        st.markdown(f"_{snippet[:150]}..._")
        else:
            st.info("No recent news available")
    
    with col_ai:
        st.markdown("### Gemini AI Analysis")
        
        with st.spinner("Gemini is analyzing market sentiment & technicals..."):
            try:
                # Initialize analyst
                analyst = AgenticAnalyst()
                
                # Prepare technical data for Gemini
                tech_data = {
                    'rsi': round(current_rsi, 2),
                    'macd': round(current_macd, 2),
                    'macd_signal': 'Bullish' if current_macd > current_signal else 'Bearish',
                    'sma_20': round(hist['SMA_20'].iloc[-1], 2),
                    'sma_50': round(hist['SMA_50'].iloc[-1], 2),
                    'sma_200': round(hist['SMA_200'].iloc[-1], 2),
                    'volume': f"{info.get('volume', 0):,}",
                    'trend': 'Bullish' if change_pct > 0 else 'Bearish'
                }
                
                # Get news summary
                news_summary = get_news_summary(symbol)
                
                # Get AI signal
                signal = analyst.analyze_ticker(
                    ticker=symbol,
                    current_price=current_price,
                    technical_data=tech_data,
                    news_summary=news_summary
                )
                
                # Display signal badge
                if signal.signal == "BUY":
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #00D09C 0%, #00B386 100%); 
                                color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                        <h2 style='margin:0; color: white;'>
                            BUY SIGNAL
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                elif signal.signal == "AVOID":
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #EB5B3C 0%, #D14426 100%); 
                                color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                        <h2 style='margin:0; color: white;'>
                            AVOID SIGNAL
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                else:  # WAIT
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #8B92A0 0%, #6B7280 100%); 
                                color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                        <h2 style='margin:0; color: white;'>
                            WAIT
                        </h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Confidence meter
                confidence_pct = int(signal.confidence * 100)
                st.markdown(f"**Confidence Level:** {confidence_pct}%")
                st.progress(signal.confidence)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # AI Reasoning
                st.markdown("**💭 AI Reasoning:**")
                st.info(signal.reasoning)
                
                # Risk Management
                if signal.stop_loss or signal.take_profit:
                    st.markdown("**🎯 Risk Management:**")
                    risk_col1, risk_col2 = st.columns(2)
                    with risk_col1:
                        if signal.stop_loss:
                            st.metric("Stop Loss", f"₹{signal.stop_loss:,.2f}")
                    with risk_col2:
                        if signal.take_profit:
                            st.metric("Take Profit", f"₹{signal.take_profit:,.2f}")
                
            except Exception as e:
                st.error(f"AI Analysis failed: {str(e)}")
                st.info("Fallback: Use technical indicators above for decision making")

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# KEY FUNDAMENTALS
# ============================================================================

st.subheader("📋 Key Metrics")

with st.container(horizontal=True):
    st.metric(
        "Market Cap",
        f"₹{info.get('marketCap', 0) / 10000000:,.2f} Cr",
        border=True
    )
    st.metric(
        "P/E Ratio",
        f"{info.get('trailingPE', 0):.2f}",
        border=True
    )
    st.metric(
        "52W High",
        f"₹{info.get('fiftyTwoWeekHigh', 0):,.2f}",
        border=True
    )
    st.metric(
        "52W Low",
        f"₹{info.get('fiftyTwoWeekLow', 0):,.2f}",
        border=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# QUICK TRADE
# ============================================================================

st.subheader("Quick Trade")

with st.form("quick_trade_form"):
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        side = st.radio("Action", ["BUY", "SELL"], horizontal=True)
    
    with col2:
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
    
    with col3:
        order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
    
    if order_type == "LIMIT":
        limit_price = st.number_input("Limit Price", min_value=0.01, value=float(current_price), step=0.01)
    else:
        limit_price = current_price
    
    # Calculate totals
    total_value = quantity * limit_price
    brokerage = total_value * 0.0003  # 0.03% brokerage
    total_cost = total_value + brokerage
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Value", f"₹{total_value:,.2f}")
    with col2:
        st.metric("Brokerage", f"₹{brokerage:,.2f}")
    with col3:
        st.metric("Total Cost", f"₹{total_cost:,.2f}")
    
    # Submit button - Note: Label can't be dynamic in Streamlit forms
    submitted = st.form_submit_button(
        f"{side} Shares" if side == "BUY" else "Sell Shares",
        type="primary",
        use_container_width=True
    )

    
    if submitted:
        # Check market hours first
        from market_hours import is_market_open
        
        market_open, market_msg = is_market_open()
        
        if not market_open:
            st.error(f"{market_msg}")
            st.info("Orders can only be placed during market hours: **Monday-Friday, 9:15 AM - 3:30 PM IST**")
        else:
            portfolio = st.session_state.paper_portfolio
            cash = portfolio['cash']
            
            # Validation
            if side == "BUY" and cash < total_cost:
                st.error(f"Insufficient funds! Available: ₹{cash:,.2f}, Required: ₹{total_cost:,.2f}")
            elif side == "SELL":
                # Check if position exists
                existing_pos = next((p for p in portfolio['positions'] if p['symbol'] == symbol), None)
                if not existing_pos or existing_pos.get('quantity', 0) < quantity:
                    st.error(f"Insufficient shares! You need {quantity} shares to sell.")
                else:
                    # Execute sell
                    existing_pos['quantity'] -= quantity
                    if existing_pos['quantity'] == 0:
                        portfolio['positions'].remove(existing_pos)
                    
                    portfolio['cash'] += total_value - brokerage
                    portfolio['orders'].append({
                        'symbol': symbol,
                        'side': side,
                        'quantity': quantity,
                        'price': limit_price,
                        'timestamp': st._config.get_option('server.headless')
                    })
                    
                    st.success(f"SOLD {quantity} shares of {symbol.replace('.NS', '')} @ ₹{limit_price:,.2f}")
                    st.balloons()
                    st.toast(f"Order placed: SELL {quantity} shares")
            else:
                # Execute buy
                portfolio['cash'] -= total_cost
                
                # Add/update position
                existing_pos = next((p for p in portfolio['positions'] if p['symbol'] == symbol), None)
                if existing_pos:
                    total_qty = existing_pos['quantity'] + quantity
                    total_cost_basis = (existing_pos['quantity'] * existing_pos['average_price']) + (quantity * limit_price)
                    existing_pos['quantity'] = total_qty
                    existing_pos['average_price'] = total_cost_basis / total_qty
                    existing_pos['current_price'] = current_price
                else:
                    portfolio['positions'].append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'average_price': limit_price,
                        'current_price': current_price
                    })
                
                portfolio['orders'].append({
                    'symbol': symbol,
                    'side': side,
                    'quantity': quantity,
                    'price': limit_price,
                    'timestamp': st._config.get_option('server.headless')
                })
                
                st.success(f"BOUGHT {quantity} shares of {symbol.replace('.NS', '')} @ ₹{limit_price:,.2f}")
                st.balloons()
                st.toast(f"Order placed: BUY {quantity} shares")
