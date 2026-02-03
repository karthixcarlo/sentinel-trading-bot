"""
Indian Price Provider

Provides real-time and historical price data for Indian stocks (NSE/BSE)
using Yahoo Finance as the data source.
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio

from sentinel.indian_market_config import (
    get_indian_symbol_format,
    is_market_open,
    IST
)

logger = logging.getLogger(__name__)


class IndianPriceProvider:
    """
    Price data provider for Indian stocks (NSE/BSE).
    
    Uses Yahoo Finance for data with proper Indian symbol formatting.
    Handles IST timezone and Indian market hours.
    """
    
    def __init__(
        self,
        cache_manager=None,
        cache_ttl: int = 300,  # 5 minutes
        exchange: str = "NSE"
    ):
        """
        Initialize Indian price provider.
        
        Args:
            cache_manager: Optional CacheManager for caching data
            cache_ttl: Cache time-to-live in seconds
            exchange: Default exchange ("NSE" or "BSE")
        """
        self.cache_manager = cache_manager
        self.cache_ttl = cache_ttl
        self.exchange = exchange
        
        # Import yfinance lazily
        try:
            import yfinance as yf
            self.yf = yf
            logger.info(f"IndianPriceProvider initialized (exchange={exchange})")
        except ImportError:
            logger.error("yfinance not installed. Install with: pip install yfinance")
            raise
    
    async def get_quote(self, symbol: str, exchange: Optional[str] = None) -> Dict:
        """
        Get current quote for an Indian stock.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            exchange: Exchange override ("NSE" or "BSE")
            
        Returns:
            Quote dictionary with price, volume, change, etc.
        """
        exchange = exchange or self.exchange
        yf_symbol = get_indian_symbol_format(symbol, exchange)
        
        # Check cache
        if self.cache_manager:
            cache_key = f"ind_quote:{yf_symbol}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"Quote cache hit: {yf_symbol}")
                return cached
        
        # Fetch from Yahoo Finance
        loop = asyncio.get_event_loop()
        quote = await loop.run_in_executor(None, self._fetch_quote, yf_symbol, symbol)
        
        # Cache the result
        if self.cache_manager and quote:
            await self.cache_manager.set(cache_key, quote, ttl=self.cache_ttl)
        
        return quote
    
    def _fetch_quote(self, yf_symbol: str, original_symbol: str) -> Dict:
        """Synchronous quote fetch for thread executor"""
        try:
            ticker = self.yf.Ticker(yf_symbol)
            info = ticker.info
            
            # Get latest price data
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                logger.warning(f"No data available for {yf_symbol}")
                return {}
            
            latest = hist.iloc[-1]
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', latest['Close']))
            
            current_price = float(latest['Close'])
            change = current_price - previous_close
            change_pct = (change / previous_close) * 100 if previous_close else 0
            
            quote = {
                "symbol": original_symbol,
                "exchange": self.exchange,
                "price": current_price,
                "open": float(info.get('open', latest['Open'])),
                "high": float(info.get('dayHigh', latest['High'])),
                "low": float(info.get('dayLow', latest['Low'])),
                "volume": int(latest['Volume']),
                "previous_close": float(previous_close),
                "change": change,
                "change_percent": change_pct,
                "timestamp": datetime.now(IST),
                "market_open": is_market_open(),
                "currency": "INR"
            }
            
            logger.info(f"Fetched quote for {original_symbol}: ₹{current_price:.2f}")
            return quote
            
        except Exception as e:
            logger.error(f"Failed to fetch quote for {yf_symbol}: {e}")
            return {}
    
    async def get_historical(
        self,
        symbol: str,
        period: str = "1mo",
        interval: str = "1d",
        exchange: Optional[str] = None
    ) -> Dict:
        """
        Get historical price data for an Indian stock.
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            exchange: Exchange override
            
        Returns:
            Dictionary with historical data
        """
        exchange = exchange or self.exchange
        yf_symbol = get_indian_symbol_format(symbol, exchange)
        
        # Check cache
        if self.cache_manager:
            cache_key = f"ind_hist:{yf_symbol}:{period}:{interval}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"Historical cache hit: {yf_symbol}")
                return cached
        
        # Fetch from Yahoo Finance
        loop = asyncio.get_event_loop()
        hist_data = await loop.run_in_executor(
            None,
            self._fetch_historical,
            yf_symbol,
            symbol,
            period,
            interval
        )
        
        # Cache the result (longer TTL for historical data)
        if self.cache_manager and hist_data:
            await self.cache_manager.set(cache_key, hist_data, ttl=self.cache_ttl * 12)  # 1 hour
        
        return hist_data
    
    def _fetch_historical(
        self,
        yf_symbol: str,
        original_symbol: str,
        period: str,
        interval: str
    ) -> Dict:
        """Synchronous historical data fetch"""
        try:
            ticker = self.yf.Ticker(yf_symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                logger.warning(f"No historical data for {yf_symbol}")
                return {}
            
            # Convert to dictionary format
            data = {
                "symbol": original_symbol,
                "exchange": self.exchange,
                "period": period,
                "interval": interval,
                "data_points": len(hist),
                "prices": hist['Close'].tolist(),
                "opens": hist['Open'].tolist(),
                "highs": hist['High'].tolist(),
                "lows": hist['Low'].tolist(),
                "volumes": hist['Volume'].tolist(),
                "timestamps": [ts.isoformat() for ts in hist.index],
                "currency": "INR"
            }
            
            logger.info(
                f"Fetched {len(hist)} historical data points for {original_symbol} "
                f"({period}, {interval})"
            )
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch historical data for {yf_symbol}: {e}")
            return {}
    
    async def get_batch_quotes(self, symbols: list, exchange: Optional[str] = None) -> Dict[str, Dict]:
        """
        Get quotes for multiple stocks in batch.
        
        Args:
            symbols: List of stock symbols
            exchange: Exchange override
            
        Returns:
            Dictionary mapping symbols to their quotes
        """
        tasks = [self.get_quote(symbol, exchange) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        quotes = {}
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {symbol}: {result}")
            elif result:
                quotes[symbol] = result
        
        return quotes
    
    async def get_index_quote(self, index_name: str) -> Dict:
        """
        Get quote for an Indian market index.
        
        Args:
            index_name: Index name (e.g., "NIFTY", "SENSEX", "BANKNIFTY")
            
        Returns:
            Index quote dictionary
        """
        from sentinel.indian_market_config import INDIAN_INDICES
        
        yf_symbol = INDIAN_INDICES.get(index_name.upper())
        if not yf_symbol:
            logger.error(f"Unknown index: {index_name}")
            return {}
        
        loop = asyncio.get_event_loop()
        quote = await loop.run_in_executor(None, self._fetch_index_quote, yf_symbol, index_name)
        
        return quote
    
    def _fetch_index_quote(self, yf_symbol: str, index_name: str) -> Dict:
        """Fetch index quote synchronously"""
        try:
            ticker = self.yf.Ticker(yf_symbol)
            info = ticker.info
            hist = ticker.history(period="1d", interval="1m")
            
            if hist.empty:
                return {}
            
            latest = hist.iloc[-1]
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', latest['Close']))
            
            current_value = float(latest['Close'])
            change = current_value - previous_close
            change_pct = (change / previous_close) * 100 if previous_close else 0
            
            quote = {
                "index": index_name,
                "symbol": yf_symbol,
                "value": current_value,
                "open": float(latest['Open']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "previous_close": float(previous_close),
                "change": change,
                "change_percent": change_pct,
                "timestamp": datetime.now(IST),
                "market_open": is_market_open()
            }
            
            logger.info(f"Fetched index quote for {index_name}: {current_value:.2f}")
            return quote
            
        except Exception as e:
            logger.error(f"Failed to fetch index quote for {yf_symbol}: {e}")
            return {}
