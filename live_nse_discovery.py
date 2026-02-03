"""
Live NSE Stock Discovery - Fetch real-time data for ALL NSE stocks
"""

import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from nse_stock_universe import get_all_nse_stocks, get_nifty_100
import streamlit as st

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_data(symbol):
    """Fetch data for a single stock"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='2d')
        
        if len(hist) >= 2:
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change = current_price - prev_price
            change_percent = (change / prev_price) * 100
            
            return {
                'symbol': symbol,
                'price': current_price,
                'change': change,
                'change_percent': change_percent,
                'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0
            }
    except:
        pass
    
    return None

def discover_live_stocks(category="gainers", limit=50, use_nifty_100=True):
    """
    Fetch live stock data from NSE
    
    Args:
        category: "gainers", "losers", or "active"
        limit: Number of stocks to return
        use_nifty_100: If True, only fetch Nifty 100 stocks (faster)
    """
    
    # Choose stock universe
    stocks = get_nifty_100() if use_nifty_100 else get_all_nse_stocks()
    
    results = []
    
    # Fetch data in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_stock = {executor.submit(fetch_stock_data, stock): stock for stock in stocks}
        
        for future in as_completed(future_to_stock):
            data = future.result()
            if data:
                results.append(data)
    
    # Sort based on category
    if category == "gainers":
        results = sorted(results, key=lambda x: x['change_percent'], reverse=True)
    elif category == "losers":
        results = sorted(results, key=lambda x: x['change_percent'])
    elif category == "active":
        results = sorted(results, key=lambda x: x['volume'], reverse=True)
    
    return results[:limit]

def discover_stocks_by_sector(sector, limit=20):
    """Discover stocks from a specific sector"""
    from nse_stock_universe import get_stocks_by_sector
    
    stocks = get_stocks_by_sector(sector)
    results = []
    
    for stock in stocks:
        data = fetch_stock_data(stock)
        if data:
            results.append(data)
    
    # Sort by change percent
    results = sorted(results, key=lambda x: x['change_percent'], reverse=True)
    return results[:limit]
