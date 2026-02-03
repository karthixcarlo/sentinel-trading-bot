import streamlit as st
import plotly.graph_objects as go
try:
    import yfinance as yf
except ImportError:
    yf = None

try:
    from complete_nse_stocks import search_nse_stocks, get_comprehensive_nse_list
    STOCK_SEARCH_AVAILABLE = True
except ImportError:
    STOCK_SEARCH_AVAILABLE = False

def render_stock_analyzer():
    """Render stock analyzer with clean chart"""
    
    st.title(":material/analytics: Stock analyzer")
    
    # Stock search with autocomplete
    if STOCK_SEARCH_AVAILABLE:
        all_stocks = get_comprehensive_nse_list()
        all_stocks_clean = [s.replace('.NS', '') for s in all_stocks]
        st.caption(f"🇮🇳 Search from **{len(all_stocks)} NSE stocks**")
        
        selected = st.selectbox(
            "Select stock",
            options=all_stocks_clean,
            index=None,
            placeholder="Type to search (e.g., RELIANCE, ADANIENT, TCS)...",
            key="stock_selectbox"
        )
        
        if selected:
            symbol = f"{selected}.NS"
        else:
            symbol = None
    else:
        # Fallback to text input
        symbol_input = st.text_input(
            "Enter stock symbol",
            placeholder="e.g., RELIANCE, TCS, INFY",
            value=st.session_state.get('selected_stock', ''),
            key="analyzer_symbol_input"
        )
        
        # Auto-add .NS if not present
        if symbol_input:
            if not symbol_input.endswith('.NS') and not symbol_input.endswith('.BO'):
                symbol = f"{symbol_input}.NS"
            else:
                symbol = symbol_input
        else:
            symbol = None
    
    if not symbol:
        st.info("Enter a stock symbol to analyze", icon=":material/info:")
        return
    
    if not yf:
        st.error("yfinance not available", icon=":material/error:")
        return
    
    # ========================================================================
    # SIGNAL INDICATOR (BUY/SELL/HOLD)
    # ========================================================================
    
    try:
        from stock_signal_indicator import display_stock_signal
        
        with st.spinner("Analyzing stock signals..."):
            recommendation, confidence = display_stock_signal(symbol)
    except ImportError:
        st.warning("Signal indicator not available")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # STOCK ANALYSIS
    # ========================================================================
    
    # Fetch data
    with st.spinner(f"Analyzing {symbol}..."):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period='1mo')
            info = ticker.info
            
            if hist.empty:
                st.error(f"No data found for {symbol}", icon=":material/error:")
                return
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            change = current_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price else 0
            
            # Price header
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.metric(
                    label=symbol.replace('.NS', '').replace('.BO', ''),
                    value=f"₹{current_price:,.2f}",
                    delta=f"{change_pct:+.2f}%",
                    border=True
                )
            
            with col2:
                pass  # Placeholder for action button
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Chart
            with st.container(border=True):
                st.subheader(":material/show_chart: Price chart")
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=hist.index,
                    y=hist['Close'],
                    mode='lines',
                    name='Price',
                    line=dict(color='#00D09C' if change >= 0 else '#EB5B3C', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0, 208, 156, 0.1)' if change >= 0 else 'rgba(235, 91, 60, 0.1)'
                ))
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    xaxis=dict(showgrid=True, gridcolor='#F4F6F8'),
                    yaxis=dict(showgrid=True, gridcolor='#F4F6F8'),
                    plot_bgcolor='white',
                    paper_bgcolor='white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Fundamentals
            st.subheader(":material/analytics: Key metrics")
            
            with st.container(horizontal=True):
                st.metric(
                    "Market cap",
                    f"₹{info.get('marketCap', 0) / 1e9:.2f}B" if info.get('marketCap') else "N/A",
                    border=True
                )
                st.metric(
                    "P/E ratio",
                    f"{info.get('trailingPE', 0):.2f}" if info.get('trailingPE') else "N/A",
                    border=True
                )
                st.metric(
                    "Beta",
                    f"{info.get('beta', 0):.2f}" if info.get('beta') else "N/A",
                    border=True
                )
                st.metric(
                    "ROE",
                    f"{info.get('returnOnEquity', 0) * 100:.2f}%" if info.get('returnOnEquity') else "N/A",
                    border=True
                )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Quick trade section
            with st.container(border=True):
                st.subheader(":material/currency_rupee: Quick trade")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    order_side = st.radio("Order type", ["BUY", "SELL"], horizontal=True)
                
                with col2:
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                
                with col3:
                    total = current_price * quantity
                    st.metric("Total", f"₹{total:,.2f}")
                
                if st.button(f"{order_side} {quantity} shares", type="primary", use_container_width=True, icon=":material/shopping_cart:"):
                    # Execute trade logic here
                    st.balloons()
                    st.toast(f"Order placed: {order_side} {quantity} shares @ ₹{current_price:,.2f}", icon=":material/check_circle:")
        
        except Exception as e:
            st.error(f"Error analyzing stock: {str(e)}", icon=":material/error:")
