"""
Stock Discovery - Groww Style
Card-based grid layout with sparkline charts and interactive cards
"""

import streamlit as st
import asyncio
from styles import GrowwColors

try:
    from dashboard_utils import run_async, show_success, show_error, show_info
except ImportError:
    def run_async(coro):
        return asyncio.run(coro)
    def show_success(msg): st.success(msg)
    def show_error(msg): st.error(msg)
    def show_info(msg): st.info(msg)


def render_stock_discovery():
    """Render the Groww-style stock discovery page"""
    
    st.markdown(f"<h1 style='color: {GrowwColors.TEXT_PRIMARY};'>🔍 Discover Stocks</h1>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='color: {GrowwColors.TEXT_SECONDARY}; font-size: 0.95rem; margin-bottom: 1.5rem;'>
        Find trending stocks across NSE based on real-time market movements
    </div>
    """, unsafe_allow_html=True)
    
    # ========================================================================
    # CONTROLS
    # ========================================================================
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        limit_per_category = st.slider(
            "Stocks per category",
            min_value=8,
            max_value=20,
            value=12,
            step=4
        )
    
    with col2:
        deep_search_count = st.slider(
            "Deep analysis count",
            min_value=4,
            max_value=12,
            value=8,
            step=2
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Discover", type="primary", use_container_width=True):
            run_discovery(limit_per_category, deep_search_count)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ========================================================================
    # RESULTS DISPLAY
    # ========================================================================
    
    if 'discovery_results' in st.session_state and st.session_state.discovery_results:
        display_discovery_results()
    else:
        # Empty state
        st.markdown(f"""
        <div class="card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 4rem; margin-bottom: 1rem; opacity: 0.5;">📊</div>
            <h3 style="color: {GrowwColors.TEXT_PRIMARY};">No stocks discovered yet</h3>
            <p style="color: {GrowwColors.TEXT_SECONDARY};">
                Click "Discover" to find trending stocks in the market
            </p>
        </div>
        """, unsafe_allow_html=True)


def run_discovery(limit_per_category, deep_search_count):
    """Run the stock discovery process"""
    
    with st.spinner("🔍 Discovering trending stocks..."):
        try:
            from sentinel.indian_market_discovery import IndianMarketDiscovery, deep_search_stock
            from sentinel import ProviderFactory
            
            # Initialize discovery
            discovery = IndianMarketDiscovery(cache_ttl=300)
            
            # Initialize providers for deep search
            factory = ProviderFactory(market_region="INDIA")
            price_provider = factory.get_price_provider()
            
            # Run discovery
            results = run_async(discovery.discover_all(limit_per_category=limit_per_category))
            
            # Check if Moneycontrol scraping worked
            total_found = sum(len(stocks) for stocks in results.values())
            
            if total_found == 0:
                st.warning("⚠️ Moneycontrol scraping returned no results. Using fallback discovery...")
                
                # Use fallback discovery with yfinance
                from fallback_discovery import discover_all_fallback
                results = run_async(discover_all_fallback(limit_per_category=limit_per_category))
                st.info("📡 Using Yahoo Finance data for discovery")
            
            # Store results in session state
            st.session_state.discovery_results = results
            
            # Get unique symbols
            all_symbols = set()
            for category, stocks in results.items():
                for stock in stocks:
                    all_symbols.add(stock['symbol'])
            
            # Deep search on top candidates
            unique_symbols = list(all_symbols)[:deep_search_count]
            deep_results = []
            
            # Try enhanced deep search first
            try:
                from enhanced_deep_search import enhanced_deep_search
                
                for symbol in unique_symbols:
                    result = run_async(enhanced_deep_search(symbol))
                    if result:
                        deep_results.append(result)
            
            except ImportError:
                # Fallback to original deep_search_stock
                for symbol in unique_symbols:
                    result = run_async(deep_search_stock(
                        symbol=symbol,
                        price_provider=price_provider,
                        news_provider=None
                    ))
                    if result:
                        if 'confidence' not in result:
                            result['confidence'] = 0.5
                        deep_results.append(result)
            
            st.session_state.deep_search_results = deep_results
            
            show_success(f"✅ Discovery complete! Found {len(all_symbols)} stocks, analyzed {len(deep_results)} deeply")
            st.rerun()
            
        except Exception as e:
            show_error(f"Discovery failed: {str(e)}")
            st.exception(e)


def display_discovery_results():
    """Display discovered stocks in tabbed card grid layout"""
    
    results = st.session_state.discovery_results
    
    # Create tabs
    tabs = st.tabs(["🟢 Top Gainers", "🔴 Top Losers", "🔥 Most Active"])
    
    # Top Gainers
    with tabs[0]:
        gainers = results.get('top_gainers', results.get('gainers', []))
        if gainers:
            display_stock_grid(gainers, "gainer")
        else:
            st.info("No gainers data available")
    
    # Top Losers
    with tabs[1]:
        losers = results.get('top_losers', results.get('losers', []))
        if losers:
            display_stock_grid(losers, "loser")
        else:
            st.info("No losers data available")
    
    # Most Active
    with tabs[2]:
        active = results.get('most_active', [])
        if active:
            display_stock_grid(active, "active")
        else:
            st.info("No active stocks data available")
    
    # Deep Analysis Section
    if 'deep_search_results' in st.session_state and st.session_state.deep_search_results:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: {GrowwColors.TEXT_PRIMARY};'>🎯 Deep Analysis</h2>", unsafe_allow_html=True)
        display_deep_analysis_results()


def display_stock_grid(stocks, category_type):
    """Display stocks in a 4-column grid of cards"""
    
    # Display in rows of 4
    num_cols = 4
    
    for i in range(0, len(stocks), num_cols):
        cols = st.columns(num_cols)
        
        for idx, stock in enumerate(stocks[i:i+num_cols]):
            with cols[idx]:
                create_stock_card(stock, category_type)


def create_stock_card(stock, category_type):
    """Create a single stock card with sparkline"""
    
    symbol = stock.get('symbol', 'N/A')
    price = stock.get('price', 0)
    change_pct = stock.get('change_percent', 0)
    
    # Determine color based on change
    is_positive = change_pct >= 0
    change_color = GrowwColors.PRIMARY_GREEN if is_positive else GrowwColors.DANGER_RED
    change_class = "positive" if is_positive else "negative"
    change_sign = "+" if is_positive else ""
    
    # Icon based on category
    if category_type == "gainer":
        icon = "📈"
    elif category_type == "loser":
        icon = "📉"
    else:
        icon = "🔥"
    
    # Create sparkline SVG (simple trending line)
    sparkline_svg = create_sparkline_svg(is_positive)
    
    # Clean symbol (remove .NS/.BO)
    clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
    
    # Create the card
    html = f"""
    <div class="stock-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <div style="font-size: 1.5rem;">{icon}</div>
            <div class="stock-ticker">{clean_symbol}</div>
        </div>
        
        <div style="margin: 1rem 0;">
            {sparkline_svg}
        </div>
        
        <div class="stock-price">
            ₹{price:,.2f}
        </div>
        
        <div>
            <span class="stock-change {change_class}">
                {change_sign}{change_pct:.2f}%
            </span>
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)
    
    # Analyze button
    if st.button(f"📊 Analyze", key=f"analyze_{symbol}", use_container_width=True):
        st.session_state.selected_stock = symbol
        st.session_state.nav_selection = "Analyze"
        st.rerun()


def create_sparkline_svg(is_positive):
    """Create a simple SVG sparkline chart"""
    
    color = GrowwColors.PRIMARY_GREEN if is_positive else GrowwColors.DANGER_RED
    
    # Simple trending line
    if is_positive:
        # Upward trend
        path = "M 0,40 L 20,35 L 40,30 L 60,20 L 80,10"
    else:
        # Downward trend
        path = "M 0,10 L 20,15 L 40,25 L 60,30 L 80,40"
    
    svg = f"""
    <svg width="100%" height="50" viewBox="0 0 80 50" style="display: block;">
        <path d="{path}" stroke="{color}" stroke-width="2" fill="none" opacity="0.8"/>
        <circle cx="80" cy="{'10' if is_positive else '40'}" r="3" fill="{color}"/>
    </svg>
    """
    
    return svg


def display_deep_analysis_results():
    """Display deep analysis results in expandable cards"""
    
    results = st.session_state.deep_search_results
    
    for result in results:
        symbol = result.get('symbol', 'N/A')
        recommendation = result.get('recommendation', 'HOLD')
        confidence = result.get('confidence', 0.5)
        
        # Icon and color based on recommendation
        if recommendation in ['BUY', 'STRONG_BUY']:
            icon = "🟢"
            rec_color = GrowwColors.PRIMARY_GREEN
        elif recommendation in ['SELL', 'STRONG_SELL']:
            icon = "🔴"
            rec_color = GrowwColors.DANGER_RED
        else:
            icon = "⚪"
            rec_color = GrowwColors.TEXT_SECONDARY
        
        # Clean symbol
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        with st.expander(
            f"{icon} **{clean_symbol}** - {recommendation} (Confidence: {confidence:.0%})",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Recommendation**")
                st.markdown(f"<div style='font-size: 1.5rem; font-weight: 700; color: {rec_color};'>{recommendation}</div>", unsafe_allow_html=True)
                st.markdown(f"**Confidence:** {confidence:.1%}")
            
            with col2:
                technical = result.get('technical_analysis', {})
                if technical:
                    st.markdown("**Technical Indicators**")
                    st.write(f"RSI: {technical.get('rsi', 'N/A')}")
                    st.write(f"Trend: {technical.get('sma_trend', 'N/A')}")
            
            # Trade details
            trade_details = result.get('trade_details', {})
            if trade_details:
                st.markdown("**Trade Details**")
                st.write(f"Entry Price: ₹{trade_details.get('entry_price', 0):,.2f}")
                st.write(f"Suggested Shares: {trade_details.get('shares', 0)}")
            
            # News summary
            news = result.get('news_summary', '')
            if news:
                st.markdown("**Market Summary**")
                st.info(news)
