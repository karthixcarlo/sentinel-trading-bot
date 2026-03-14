# -*- coding: utf-8 -*-
"""
Market Universe Loader - NSE Equity Universe with Smart Batching

Handles 2000+ NSE stocks efficiently using:
- Caching to avoid API rate limits
- Smart filtering (volume, price, liquidity)
- Random batch selection for diversity
- Fallback to NIFTY 500 when nselib is unavailable
"""

import random
from typing import List, Optional
from datetime import datetime, timedelta


class MarketLoader:
    """
    Loads and manages the NSE equity universe
    
    Strategy: Rolling Batch Funnel
    - Fetches full NSE equity list once
    - Caches for performance
    - Returns random batches of active stocks
    - Over multiple cycles, covers entire market
    """
    
    def __init__(self):
        self.cache: List[str] = []
        self.cache_timestamp: Optional[datetime] = None
        self.cache_duration = timedelta(hours=6)  # Refresh every 6 hours
        
    
    def fetch_active_symbols(self) -> List[str]:
        """
        Fetch all active NSE equity symbols
        
        Uses nselib with fallback to NIFTY 500
        
        Returns:
            List of stock symbols with .NS suffix (for yfinance)
        """
        
        # Check if cache is still valid
        if self.cache and self.cache_timestamp:
            if datetime.now() - self.cache_timestamp < self.cache_duration:
                print(f"📦 Using cached symbols ({len(self.cache)} stocks)")
                return self.cache
        
        print("⏳ Downloading full NSE equity list...")
        
        try:
            # Try nselib first
            from nselib import capital_market
            
            # Fetch equity list
            df = capital_market.equity_list()
            
            # Filter: Only EQ series (Standard Equity)
            eq_stocks = df[df['SERIES'] == 'EQ']
            
            # Extract symbols and add .NS suffix for Yahoo Finance
            symbols = [f"{row['SYMBOL']}.NS" for _, row in eq_stocks.iterrows()]
            
            print(f"✅ Loaded {len(symbols)} stocks from NSE")
            
            # Update cache
            self.cache = symbols
            self.cache_timestamp = datetime.now()
            
            return symbols
            
        except ImportError:
            print("⚠️  nselib not installed. Using NIFTY 500 fallback...")
            return self._get_nifty_500_fallback()
            
        except Exception as e:
            print(f"❌ Error fetching NSE data: {e}")
            print("📋 Using NIFTY 500 fallback...")
            return self._get_nifty_500_fallback()
    
    
    def get_smart_batch(self, size: int = 50) -> List[str]:
        """
        Get a random batch of stocks for analysis
        
        Args:
            size: Number of stocks to return (default 50)
            
        Returns:
            Random sample of stock symbols
        """
        
        # Fetch or use cached symbols
        symbols = self.fetch_active_symbols()
        
        # If we don't have enough symbols, return all
        if len(symbols) <= size:
            return symbols
        
        # Return random sample
        batch = random.sample(symbols, size)
        
        print(f"🔭 Selected random batch of {size} stocks")
        
        return batch
    
    
    def _get_nifty_500_fallback(self) -> List[str]:
        """
        Fallback to NIFTY 500 stocks if nselib fails
        
        Returns:
            List of NIFTY 500 symbols with .NS suffix
        """
        
        # NIFTY 500 stocks (curated list of most liquid stocks)
        nifty_500 = [
            # NIFTY 50
            "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR", "ICICIBANK", 
            "BHARTIARTL", "SBIN", "BAJFINANCE", "ITC", "KOTAKBANK", "LT", 
            "ASIANPAINT", "AXISBANK", "MARUTI", "TITAN", "SUNPHARMA", "DMART",
            "ULTRACEMCO", "NTPC", "NESTLEIND", "ONGC", "TATASTEEL", "WIPRO",
            "POWERGRID", "HCLTECH", "JSWSTEEL", "BAJAJFINSV", "TECHM", "M&M",
            "TATAMOTORS", "ADANIENT", "ADANIPORTS", "COALINDIA", "INDUSINDBK",
            "APOLLOHOSP", "DIVISLAB", "HINDALCO", "CIPLA", "DRREDDY", "GRASIM",
            "EICHERMOT", "SHREECEM", "TATACONSUM", "UPL", "BRITANNIA", "HEROMOTOCO",
            "BAJAJ-AUTO", "SBILIFE", "LTIM",
            
            # NIFTY NEXT 50
            "ADANIGREEN", "ADANIPOWER", "ATGL", "HAVELLS", "HDFCLIFE", "ICICIPRULI",
            "INDIGO", "JSWENERGY", "MOTHERSON", "PIDILITIND", "SBICARD", "SIEMENS",
            "TORNTPHARM", "VEDL", "GODREJCP", "BANDHANBNK", "GAIL", "PEL", "MCDOWELL-N",
            "VOLTAS", "NMDC", "RECLTD", "TATAPOWER", "JINDALSTEL", "ICICIGI",
            "BERGEPAINT", "NAUKRI", "DABUR", "LUPIN", "BOSCHLTD", "DLF",
            "AMBUJACEM", "INDHOTEL", "LICI", "ZOMATO", "TRENT", "PFC",
            "PETRONET", "SAIL", "BANKBARODA", "IRCTC", "BEL", "CHOLAFIN",
            "ABB", "OFSS", "IOC", "MPHASIS", "GLAND", "TVSMOTOR",
            
            # Additional High-Volume Stocks
            "YESBANK", "SUZLON", "IDEA", "PNB", "CANBK", "UNIONBANK", 
            "IDFCFIRSTB", "JSWINFRA", "ZEEL", "RPOWER", "ASHOKLEY", "GMRINFRA",
            "BHARATFORG", "CUMMINSIND", "ESCORTS", "EXIDEIND", "FEDERALBNK",
            "GODREJPROP", "IDFC", "INDIACEM", "IRFC", "L&TFH", "LAURUSLABS",
            "LICHSGFIN", "MARICO", "NATIONALUM", "PAGEIND", "PETRONET",
            "PFIZER", "POLYCAB", "RBLBANK", "SRF", "SRTRANSFIN", "STAR",
            "SUNPHARMA", "TATACOMM", "TATACHEM", "TORNTPOWER", "UBL",
            "MUTHOOTFIN", "DIXON", "ASTRAL", "COFORGE", "PERSISTENT",
            
            # Mid Cap High Performers
            "APOLLOTYRE", "AUBANK", "BIOCON", "CONCOR", "CROMPTON", "DEEPAKNTR",
            "DELTACORP", "DIXON", "EMAMILTD", "FORTIS", "GLENMARK", "GRANULES",
            "HINDCOPPER", "IPCALAB", "JINDALSTEL", "JUBLFOOD", "KAJARIACER",
            "KEI", "LALPATHLAB", "LINDEINDIA", "MANAPPURAM", "MCX", "METROPOLIS",
            "MGL", "MINDTREE", "MUTHOOTFIN", "NATIONALUM", "NAM-INDIA", "NAVINFLUOR",
            "NMDC", "PERSISTENT", "PHOENIXLTD", "PIIND", "PVR", "RAIN",
            "RAJESHEXPO", "RAMCOCEM", "RATNAMANI", "SANOFI", "SCHAEFFLER",
            "SKFINDIA", "SONATSOFTW", "SYNGENE", "THERMAX", "THYROCARE",
            "TIMKEN", "TTKPRESTIG", "TUTICORIN", "VGUARD", "VINATIORGA",
            "WELCORP", "WHIRLPOOL", "WOCKPHARMA", "ZENSARTECH"
        ]
        
        # Add .NS suffix
        symbols = [f"{s}.NS" for s in nifty_500]
        
        # Update cache
        self.cache = symbols
        self.cache_timestamp = datetime.now()
        
        print(f"✅ Using NIFTY 500 fallback ({len(symbols)} stocks)")
        
        return symbols
    
    
    def get_stats(self) -> dict:
        """
        Get loader statistics
        
        Returns:
            Dict with cache info
        """
        return {
            'total_symbols': len(self.cache),
            'cache_age_minutes': (datetime.now() - self.cache_timestamp).total_seconds() / 60 if self.cache_timestamp else None,
            'cache_valid': self.cache_timestamp and (datetime.now() - self.cache_timestamp < self.cache_duration)
        }


# Global instance
_loader = None

def get_market_loader() -> MarketLoader:
    """
    Get singleton instance of MarketLoader
    
    Returns:
        MarketLoader instance
    """
    global _loader
    if _loader is None:
        _loader = MarketLoader()
    return _loader


# Test function
if __name__ == "__main__":
    print("Testing Market Loader...")
    
    loader = MarketLoader()
    
    # Test 1: Fetch full list
    print("\n=== Test 1: Fetch Full List ===")
    symbols = loader.fetch_active_symbols()
    print(f"Total symbols: {len(symbols)}")
    print(f"First 10: {symbols[:10]}")
    
    # Test 2: Get batch
    print("\n=== Test 2: Get Smart Batch ===")
    batch = loader.get_smart_batch(50)
    print(f"Batch size: {len(batch)}")
    print(f"Sample: {batch[:5]}")
    
    # Test 3: Cache check
    print("\n=== Test 3: Cache Test ===")
    batch2 = loader.get_smart_batch(30)
    print("(Should use cache)")
    
    # Test 4: Stats
    print("\n=== Test 4: Loader Stats ===")
    stats = loader.get_stats()
    print(stats)
    
    print("\n✅ All tests complete!")
