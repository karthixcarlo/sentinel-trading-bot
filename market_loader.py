"""
NSE Market Loader - Production-Ready
Dynamically fetches ALL active NSE stocks using nselib
Author: Financial Systems Specialist
"""

import random
from typing import List, Optional
import pandas as pd

try:
    from nselib import capital_market
    NSELIB_AVAILABLE = True
except ImportError:
    NSELIB_AVAILABLE = False
    print("WARNING: nselib not installed. Install with: pip install nselib")


# Nifty 50 Fallback (used if NSE connection fails)
NIFTY_50_FALLBACK = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BHARTIARTL.NS", "BPCL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS",
    "INDUSINDBK.NS", "INFY.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS",
    "LTIM.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS",
    "SBIN.NS", "SUNPHARMA.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TATACONSUM.NS",
    "TCS.NS", "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "WIPRO.NS"
]


def load_all_nse_stocks(filter_eq_only: bool = True) -> List[str]:
    """
    Load complete list of active NSE stocks using nselib
    
    Args:
        filter_eq_only: If True, only return EQ series stocks (default: True)
                       EQ = Standard Equity (most liquid)
                       Excludes BE (Book Entry), BZ, etc.
    
    Returns:
        List of stock symbols with .NS suffix (e.g., ['RELIANCE.NS', 'TCS.NS', ...])
    
    Raises:
        None - Returns fallback list if connection fails
    """
    
    if not NSELIB_AVAILABLE:
        print("⚠️  nselib not available, using Nifty 50 fallback")
        return NIFTY_50_FALLBACK.copy()
    
    try:
        print("📡 Fetching live NSE equity list...")
        
        # Fetch equity list from NSE
        equity_list = capital_market.equity_list()
        
        if equity_list is None or equity_list.empty:
            raise ValueError("Empty response from NSE")
        
        # Filter for EQ series only (standard equity)
        if filter_eq_only:
            if 'SERIES' in equity_list.columns:
                equity_list = equity_list[equity_list['SERIES'] == 'EQ']
                print(f"✅ Filtered to EQ series: {len(equity_list)} stocks")
            else:
                print("⚠️  SERIES column not found, using all stocks")
        
        # Extract symbols
        if 'SYMBOL' in equity_list.columns:
            symbols = equity_list['SYMBOL'].tolist()
        elif 'symbol' in equity_list.columns:
            symbols = equity_list['symbol'].tolist()
        else:
            # Try first column
            symbols = equity_list.iloc[:, 0].tolist()
        
        # Append .NS suffix for yfinance compatibility
        symbols_with_ns = [f"{symbol}.NS" for symbol in symbols]
        
        print(f"✅ Loaded {len(symbols_with_ns)} NSE stocks")
        
        return symbols_with_ns
    
    except Exception as e:
        print(f"❌ Error loading from NSE: {str(e)}")
        print(f"📋 Using Nifty 50 fallback ({len(NIFTY_50_FALLBACK)} stocks)")
        return NIFTY_50_FALLBACK.copy()


def get_random_batch(batch_size: int = 50, filter_eq_only: bool = True) -> List[str]:
    """
    Get a random batch of stocks to prevent API rate limits
    
    Args:
        batch_size: Number of stocks to return (default: 50)
        filter_eq_only: Only include EQ series stocks (default: True)
    
    Returns:
        List of random stock symbols with .NS suffix
    
    Example:
        >>> random_stocks = get_random_batch(batch_size=20)
        >>> print(random_stocks[:5])
        ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS']
    """
    
    all_stocks = load_all_nse_stocks(filter_eq_only=filter_eq_only)
    
    # Ensure batch size doesn't exceed available stocks
    actual_batch_size = min(batch_size, len(all_stocks))
    
    # Return random sample
    random_batch = random.sample(all_stocks, actual_batch_size)
    
    print(f"🎲 Selected random batch of {actual_batch_size} stocks")
    
    return random_batch


def get_nifty_50() -> List[str]:
    """
    Get Nifty 50 stocks (fallback list)
    
    Returns:
        List of Nifty 50 stock symbols with .NS suffix
    """
    return NIFTY_50_FALLBACK.copy()


def search_stocks(query: str, filter_eq_only: bool = True) -> List[str]:
    """
    Search for stocks matching a query
    
    Args:
        query: Search term (e.g., 'ADANI', 'TATA', 'RELIANCE')
        filter_eq_only: Only search EQ series stocks (default: True)
    
    Returns:
        List of matching stock symbols
    """
    
    all_stocks = load_all_nse_stocks(filter_eq_only=filter_eq_only)
    query_upper = query.upper()
    
    matches = [stock for stock in all_stocks if query_upper in stock.upper()]
    
    return matches


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("NSE MARKET LOADER - TEST")
    print("=" * 60)
    
    # Test 1: Load all stocks
    print("\n[TEST 1] Loading all NSE stocks...")
    all_stocks = load_all_nse_stocks()
    print(f"Total stocks loaded: {len(all_stocks)}")
    print(f"First 5 stocks: {all_stocks[:5]}")
    print(f"Last 5 stocks: {all_stocks[-5:]}")
    
    # Test 2: Random batch
    print("\n[TEST 2] Getting random batch of 50 stocks...")
    batch = get_random_batch(batch_size=50)
    print(f"Batch size: {len(batch)}")
    print(f"Random sample: {batch[:10]}")
    
    # Test 3: Search functionality
    print("\n[TEST 3] Searching for 'ADANI' stocks...")
    adani_stocks = search_stocks("ADANI")
    print(f"Found {len(adani_stocks)} ADANI stocks:")
    for stock in adani_stocks:
        print(f"  - {stock}")
    
    # Test 4: Nifty 50 fallback
    print("\n[TEST 4] Getting Nifty 50 stocks...")
    nifty_50 = get_nifty_50()
    print(f"Nifty 50 count: {len(nifty_50)}")
    print(f"Sample: {nifty_50[:5]}")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60)
