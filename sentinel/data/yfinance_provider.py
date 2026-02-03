"""
YFinance Provider - Real Stock Market Data

Fetches real-time stock prices and data using yfinance with caching support.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
import yfinance as yf

from ..async_utils import retry_with_backoff

logger = logging.getLogger(__name__)


class YFinanceProvider:
    """
    Real stock price provider using yfinance.
    
    Features:
    - Real-time price data
    - Volume and market cap
    - Batch ticker support
    - Automatic retry on failures
    - Cache integration
    """
    
    def __init__(self, cache_manager=None, cache_ttl: int = 300):
        """
        Initialize YFinance provider.
        
        Args:
            cache_manager: Optional CacheManager for caching
            cache_ttl: Cache time-to-live in seconds (default 5 minutes)
        """
        self.cache_manager = cache_manager
        self.cache_ttl = cache_ttl
    
    async def get_price(self, ticker: str) -> Dict:
        """
        Get current price data for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with price data
        """
        # Check cache first
        if self.cache_manager:
            cache_key = f"price:{ticker}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"Price cache hit for {ticker}")
                return cached
        
        # Fetch from yfinance
        try:
            data = await self._fetch_price(ticker)
            
            # Cache result
            if self.cache_manager and data:
                cache_key = f"price:{ticker}"
                await self.cache_manager.set(cache_key, data, ttl=self.cache_ttl)
            
            return data
        
        except Exception as e:
            logger.error(f"Failed to fetch price for {ticker}: {e}")
            raise
    
    async def _fetch_price(self, ticker: str) -> Dict:
        """Fetch price data from yfinance"""
        # Run in thread pool since yfinance is synchronous
        loop = asyncio.get_event_loop()
        
        def _fetch():
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get current price
            current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
            
            # Get previous close for change calculation
            previous_close = info.get('previousClose', current_price)
            change_pct = ((current_price - previous_close) / previous_close * 100) if previous_close else 0
            
            return {
                "ticker": ticker,
                "price": round(current_price, 2),
                "volume": info.get('volume', 0),
                "market_cap": info.get('marketCap', 0),
                "change_pct": round(change_pct, 2),
                "previous_close": round(previous_close, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Execute with retry
        data = await retry_with_backoff(
            lambda: loop.run_in_executor(None, _fetch),
            max_retries=2,
            initial_delay=1.0
        )
        
        return data
    
    async def get_batch_prices(self, tickers: List[str]) -> Dict[str, Dict]:
        """
        Get prices for multiple tickers in parallel.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dictionary mapping ticker to price data
        """
        tasks = [self.get_price(ticker) for ticker in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        price_data = {}
        for ticker, result in zip(tickers, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch {ticker}: {result}")
            else:
                price_data[ticker] = result
        
        return price_data
    
    async def get_historical(
        self,
        ticker: str,
        period: str = "1mo",
        interval: str = "1d"
    ) -> Dict:
        """
        Get historical price data for technical analysis.
        
        Args:
            ticker: Stock ticker symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            Dictionary with historical data
        """
        # Check cache
        if self.cache_manager:
            cache_key = f"historical:{ticker}:{period}:{interval}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"Historical cache hit for {ticker}")
                return cached
        
        # Fetch from yfinance
        loop = asyncio.get_event_loop()
        
        def _fetch():
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period, interval=interval)
            
            if hist.empty:
                return None
            
            return {
                "ticker": ticker,
                "period": period,
                "interval": interval,
                "data": hist.to_dict('records'),
                "close_prices": hist['Close'].tolist(),
                "volumes": hist['Volume'].tolist(),
                "timestamps": [ts.isoformat() for ts in hist.index]
            }
        
        data = await loop.run_in_executor(None, _fetch)
        
        # Cache result (longer TTL for historical data)
        if self.cache_manager and data:
            cache_key = f"historical:{ticker}:{period}:{interval}"
            await self.cache_manager.set(cache_key, data, ttl=3600)  # 1 hour
        
        return data
