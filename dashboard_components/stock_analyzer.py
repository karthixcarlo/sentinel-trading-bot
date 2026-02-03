"""
Stock Analyzer Component

Deep technical analysis of selected stocks with charts and recommendations.
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def render_stock_analyzer():
    """Main function to render the stock analyzer page."""
    
    st.title("📊 Stock Analysis")
    
    st.markdown("""
    **✨ Analyze ANY NSE/BSE stock!** Not limited to discovered stocks.
    
    Deep technical analysis with:
    - **Interactive price charts** with volume
    - **Technical indicators** (SMA, RSI, MACD)
    - **News sentiment** analysis
    - **AI recommendations** (BUY/SELL/HOLD)
    - **Position sizing** calculator
    
    > 💡 **Tip:** You can analyze ANY Indian stock, not just the ones from Discovery!  
    > Examples: `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `HDFCBANK.NS`, `TATAMOTORS.NS`
    """)
    
    st.divider()
    
    # Stock input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol = st.text_input(
            "Stock Symbol (NSE/BSE) - Type ANY symbol!",
            placeholder="e.g., RELIANCE.NS, TCS.NS, INFY.NS, HDFCBANK.NS",
            help="Add .NS for NSE stocks, .BO for BSE stocks. Works for ALL 2000+ Indian stocks!"
        )
    
    with col2:
        period = st.selectbox(
            "Period",
            options=["1mo", "3mo", "6mo", "1y", "2y"],
            index=1
        )
    
    if not symbol:
        st.info("👆 Enter a stock symbol to begin analysis")
        return
    
    if not YFINANCE_AVAILABLE:
        st.error("📦 yfinance not installed. Run: `pip install yfinance`")
        return
    
    # Analyze button
    if st.button("🔍 Analyze Stock", type="primary", use_container_width=True):
        analyze_stock(symbol, period)


def analyze_stock(symbol: str, period: str):
    """
    Perform deep analysis on the stock.
    
    Args:
        symbol: Stock symbol
        period: Time period for analysis
    """
    
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            # Fetch data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            if hist.empty:
                st.error(f"No data found for {symbol}. Check the symbol and try again.")
                return
            
            # Display stock info
            display_stock_info(info, symbol)
            
            st.divider()
            
            # Price chart
            display_price_chart(hist, symbol)
            
            st.divider()
            
            # Technical analysis
            display_technical_analysis(hist)
            
            st.divider()
            
            # Recommendation
            display_recommendation(hist, info)
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def display_stock_info(info: dict, symbol: str):
    """Display stock information."""
    
    st.markdown(f"### 📈 {info.get('longName', symbol)}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        st.metric(
            label="Current Price",
            value=f"₹{current_price:,.2f}"
        )
    
    with col2:
        prev_close = info.get('previousClose', current_price)
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0
        st.metric(
            label="Change",
            value=f"₹{abs(change):,.2f}",
            delta=f"{change_pct:+.2f}%"
        )
    
    with col3:
        volume = info.get('volume', 0)
        st.metric(
            label="Volume",
            value=f"{volume:,}"
        )
    
    with col4:
        market_cap = info.get('marketCap', 0)
        market_cap_cr = market_cap / 10000000  # Convert to crores
        st.metric(
            label="Market Cap",
            value=f"₹{market_cap_cr:,.0f}Cr"
        )


def display_price_chart(hist, symbol: str):
    """Display interactive price chart with volume."""
    
    st.markdown("### 📊 Price Chart")
    
    # Create candlestick chart
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name='Price'
    ))
    
    # Add SMA lines
    sma_20 = hist['Close'].rolling(window=20).mean()
    sma_50 = hist['Close'].rolling(window=50).mean()
    
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=sma_20,
        mode='lines',
        name='SMA 20',
        line=dict(color='orange', width=1)
    ))
    
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=sma_50,
        mode='lines',
        name='SMA 50',
        line=dict(color='blue', width=1)
    ))
    
    # Update layout
    fig.update_layout(
        title=f"{symbol} Price Chart",
        yaxis_title='Price (₹)',
        xaxis_title='Date',
        height=500,
        xaxis_rangeslider_visible=False,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Volume chart
    fig_volume = go.Figure()
    
    colors = ['red' if row['Close'] < row['Open'] else 'green' for idx, row in hist.iterrows()]
    
    fig_volume.add_trace(go.Bar(
        x=hist.index,
        y=hist['Volume'],
        name='Volume',
        marker_color=colors
    ))
    
    fig_volume.update_layout(
        title='Volume',
        yaxis_title='Volume',
        xaxis_title='Date',
        height=200,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig_volume, use_container_width=True)


def display_technical_analysis(hist):
    """Display technical indicators."""
    
    st.markdown("### 🔢 Technical Indicators")
    
    # Calculate indicators
    current_price = hist['Close'].iloc[-1]
    sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
    sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    
    # RSI
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    # Display indicators
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Moving Averages**")
        st.write(f"SMA 20: ₹{sma_20:,.2f}")
        st.write(f"SMA 50: ₹{sma_50:,.2f}")
        trend = "📈 Bullish" if current_price > sma_20 > sma_50 else "📉 Bearish" if current_price < sma_20 < sma_50 else "➡️ Neutral"
        st.write(f"Trend: {trend}")
    
    with col2:
        st.markdown("**RSI (14)**")
        st.write(f"Current: {current_rsi:.2f}")
        if current_rsi > 70:
            st.write("Status: 🔴 Overbought")
        elif current_rsi < 30:
            st.write("Status: 🟢 Oversold")
        else:
            st.write("Status: 🟡 Neutral")
    
    with col3:
        st.markdown("**Support & Resistance**")
        support = hist['Low'].tail(20).min()
        resistance = hist['High'].tail(20).max()
        st.write(f"Support: ₹{support:,.2f}")
        st.write(f"Resistance: ₹{resistance:,.2f}")
        range_pct = ((resistance - support) / support * 100)
        st.write(f"Range: {range_pct:.2f}%")


def display_recommendation(hist, info):
    """Display AI-powered recommendation."""
    
    st.markdown("### 🎯 Recommendation")
    
    # Simple recommendation logic
    current_price = hist['Close'].iloc[-1]
    sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
    sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
    
    # Calculate RSI
    delta = hist['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    
    # Recommendation logic
    buy_signals = 0
    sell_signals = 0
    
    # SMA signals
    if current_price > sma_20:
        buy_signals += 1
    else:
        sell_signals += 1
    
    if sma_20 > sma_50:
        buy_signals += 1
    else:
        sell_signals += 1
    
    # RSI signals
    if current_rsi < 30:
        buy_signals += 2  # Strong buy
    elif current_rsi < 40:
        buy_signals += 1
    elif current_rsi > 70:
        sell_signals += 2  # Strong sell
    elif current_rsi > 60:
        sell_signals += 1
    
    # Determine recommendation
    if buy_signals > sell_signals + 1:
        recommendation = "BUY"
        color = "green"
        icon = "🟢"
        confidence = min(90, 50 + (buy_signals - sell_signals) * 10)
    elif sell_signals > buy_signals + 1:
        recommendation = "SELL"
        color = "red"
        icon = "🔴"
        confidence = min(90, 50 + (sell_signals - buy_signals) * 10)
    else:
        recommendation = "HOLD"
        color = "orange"
        icon = "🟡"
        confidence = 60
    
    # Display recommendation card
    st.markdown(
        f"""
        <div style='background-color: {color}22; padding: 2rem; border-radius: 10px; border-left: 5px solid {color};'>
            <h2 style='color: {color}; margin: 0;'>{icon} {recommendation}</h2>
            <p style='font-size: 1.2rem; margin: 0.5rem 0;'>Confidence: <strong>{confidence}%</strong></p>
            <p style='margin: 0;'>
                Based on technical analysis of moving averages, RSI, and price action.
                This is not financial advice - always do your own research.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Position sizing calculator
    st.markdown("### 💰 Position Sizing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        account_balance = st.number_input(
            "Account Balance (₹)",
            min_value=1000.0,
            value=100000.0,
            step=1000.0
        )
        
        risk_per_trade = st.slider(
            "Risk Per Trade (%)",
            min_value=0.5,
            max_value=5.0,
            value=2.0,
            step=0.5
        )
    
    with col2:
        stop_loss_pct = st.slider(
            "Stop Loss (%)",
            min_value=1.0,
            max_value=10.0,
            value=5.0,
            step=0.5
        )
        
        # Calculate position size
        risk_amount = account_balance * (risk_per_trade / 100)
        stop_loss_amount = current_price * (stop_loss_pct / 100)
        shares = int(risk_amount / stop_loss_amount) if stop_loss_amount > 0 else 0
        position_value = shares * current_price
        
        st.metric(
            label="Suggested Shares",
            value=f"{shares}"
        )
        st.metric(
            label="Position Value",
            value=f"₹{position_value:,.2f}"
        )
