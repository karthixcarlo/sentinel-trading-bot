"""
Stock Discovery Component

Auto-discovery of trending stocks from Indian markets.
"""

import streamlit as st
import asyncio
from datetime import datetime

try:
    from dashboard_utils import (
        run_async,
        format_currency,
        format_percentage,
        show_success,
        show_error,
        show_info
    )
except ImportError:
    def run_async(coro):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)
    
    def format_currency(amount, currency="INR", decimals=2):
        return f"₹{amount:,.{decimals}f}"
    
    def format_percentage(value, decimals=2, show_sign=True):
        pct = value * 100 if abs(value) < 1 else value
        sign = "+" if pct > 0 and show_sign else ""
        return f"{sign}{pct:.{decimals}f}%"
    
    def show_success(msg):
        st.success(f"✅ {msg}")
    
    def show_error(msg):
        st.error(f"❌ {msg}")
    
    def show_info(msg):
        st.info(f"ℹ️ {msg}")



def run_stock_discovery():
    """Run the auto-discovery workflow and display results."""
    
    st.markdown("### 🔍 Stock Discovery")
    
    st.info("Discover trending stocks from NSE using Moneycontrol data scraping")
    
    # Discovery parameters
    col1, col2 = st.columns(2)
    
    with col1:
        limit_per_category = st.slider(
            "Stocks per category",
            min_value=5,
            max_value=20,
            value=10,
            help="Number of stocks to discover in each category (gainers, losers, active)"
        )
    
    with col2:
        deep_search_count = st.slider(
            "Deep analysis count",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of top stocks to analyze deeply"
        )
    
    # Discovery button
    if st.button("🚀 Discover Stocks", type="primary", use_container_width=True):
        
        with st.spinner("Discovering trending stocks... This may take 1-2 minutes"):
            try:
                from sentinel.indian_market_discovery import IndianMarketDiscovery, deep_search_stock
                from sentinel import ProviderFactory
                
                # Initialize discovery (no price_provider param needed)
                discovery = IndianMarketDiscovery(cache_ttl=300)
                
                # Initialize providers for deep search
                factory = ProviderFactory(market_region="INDIA")
                price_provider = factory.get_price_provider()
                
                # Run discovery
                st.write("**Step 1/3:** Scraping Moneycontrol for trending stocks...")
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
                
                st.write(f"**Step 2/3:** Found {len(all_symbols)} unique stocks")
                
                # Deep search on top candidates
                st.write(f"**Step 3/3:** Performing deep analysis on top {deep_search_count} stocks...")
                
                unique_symbols = list(all_symbols)[:deep_search_count]
                deep_results = []
                
                # Try enhanced deep search first, fallback to original if not available
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
                            # Add confidence if missing
                            if 'confidence' not in result:
                                result['confidence'] = 0.5
                            deep_results.append(result)
                
                st.session_state.deep_search_results = deep_results
                
                show_success(f"Discovery complete! Found {len(all_symbols)} stocks, analyzed {len(deep_results)} deeply")
                
            except Exception as e:
                show_error(f"Discovery failed: {str(e)}")
                st.exception(e)


def display_discovery_results():
    """Display the discovered stocks in tables."""
    
    if 'discovery_results' not in st.session_state:
        show_info("No discovery results yet. Click 'Discover Stocks' to start.")
        return
    
    results = st.session_state.discovery_results
    
    # Display each category in tabs
    tabs = st.tabs(["🟢 Top Gainers", "🔴 Top Losers", "🔥 Most Active"])
    
    # Top Gainers - check both possible keys
    with tabs[0]:
        gainers = results.get('top_gainers', results.get('gainers', []))
        if gainers:
            display_stock_table(gainers, "gainers")
        else:
            st.warning("No gainers data available")
    
    # Top Losers - check both possible keys
    with tabs[1]:
        losers = results.get('top_losers', results.get('losers', []))
        if losers:
            display_stock_table(losers, "losers")
        else:
            st.warning("No losers data available")
    
    # Most Active
    with tabs[2]:
        active = results.get('most_active', [])
        if active:
            display_stock_table(active, "active")
        else:
            st.warning("No active stocks data available")


def display_stock_table(stocks: list, category: str):
    """
    Display stocks in a formatted table.
    
    Args:
        stocks: List of stock dictionaries
        category: Category name (gainers, losers, active)
    """
    
    if not stocks:
        st.info("No stocks in this category")
        return
    
    # Create table data
    table_data = []
    
    for stock in stocks:
        symbol = stock.get('symbol', 'N/A')
        price = stock.get('price', 0)
        change_pct = stock.get('change_percent', 0)
        volume = stock.get('volume', 0)
        
        # Format change with color
        if change_pct > 0:
            change_str = f"🟢 +{change_pct:.2f}%"
        elif change_pct < 0:
            change_str = f"🔴 {change_pct:.2f}%"
        else:
            change_str = f"⚪ {change_pct:.2f}%"
        
        table_data.append({
            "Symbol": symbol,
            "Price": f"₹{price:,.2f}",
            "Change": change_str,
            "Volume": f"{volume:,}" if volume else "N/A"
        })
    
    # Display as dataframe
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )


def display_deep_analysis_results():
    """Display deep analysis results."""
    
    if 'deep_search_results' not in st.session_state:
        return
    
    st.markdown("### 📊 Deep Analysis Results")
    
    results = st.session_state.deep_search_results
    
    if not results:
        st.info("No deep analysis results available")
        return
    
    # Display each analyzed stock
    for result in results:
        symbol = result.get('symbol', 'Unknown')
        recommendation = result.get('recommendation', 'HOLD')
        confidence = result.get('confidence', 0.5)
        
        # Color code recommendation
        if recommendation == 'BUY':
            rec_color = "🟢"
            badge_color = "green"
        elif recommendation == 'SELL':
            rec_color = "🔴"
            badge_color = "red"
        else:
            rec_color = "🟡"
            badge_color = "orange"
        
        with st.expander(f"{rec_color} **{symbol}** - {recommendation} (Confidence: {confidence:.0%})"):
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Technical Analysis:**")
                technical = result.get('technical_analysis', {})
                st.write(f"- RSI: {technical.get('rsi', 'N/A')}")
                st.write(f"- MACD: {technical.get('macd_signal', 'N/A')}")
                st.write(f"- SMA Trend: {technical.get('sma_trend', 'N/A')}")
            
            with col2:
                st.markdown("**Trade Details:**")
                trade = result.get('trade_details', {})
                st.write(f"- Entry Price: ₹{trade.get('entry_price', 0):.2f}")
                st.write(f"- Position Size: {trade.get('shares', 0)} shares")
                st.write(f"- Position Value: ₹{trade.get('position_value', 0):,.2f}")
            
            # News sentiment if available
            if 'news_summary' in result:
                st.markdown("**News Sentiment:**")
                st.write(result['news_summary'])


def render_stock_discovery():
    """Main function to render the stock discovery page."""
    
    st.title("🔍 Stock Discovery")
    
    st.markdown("""
    Automatically discover trending stocks from NSE/BSE markets using:
    - **Moneycontrol** data scraping (top gainers, losers, most active)
    - **Deep analysis** using technical indicators and risk models
    - **AI-powered recommendations** from Scout and Analyst agents
    
    **✨ Works 24/7!** Discover stocks anytime:
    - 📊 **During market hours:** Real-time trending stocks
    - 🌙 **After market closes:** Review today's movers for tomorrow's planning
    - 🌅 **Before market opens:** Prepare your watchlist for the day ahead
    """)
    
    # Add market status indicator
    try:
        from datetime import datetime
        import pytz
        IST = pytz.timezone('Asia/Kolkata')
        now = datetime.now(IST)
        hour = now.hour
        minute = now.minute
        is_weekday = now.weekday() < 5
        market_open = is_weekday and ((hour == 9 and minute >= 15) or (10 <= hour < 15) or (hour == 15 and minute <= 30))
        
        if market_open:
            st.success("🟢 Market is OPEN - Real-time discovery available!")
        else:
            st.info("🌙 Market is CLOSED - Analyzing recent data for tomorrow's opportunities")
    except:
        pass
    
    st.divider()
    
    # Discovery controls
    run_stock_discovery()
    
    st.divider()
    
    # Display results
    display_discovery_results()
    
    st.divider()
    
    # Deep analysis results
    display_deep_analysis_results()
