"""
Technical Indicators Provider - Real Technical Analysis

Calculates real technical indicators from historical price data.
"""

import asyncio
import logging
import numpy as np
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class TechnicalProvider:
    """
    Real technical indicators provider.
    
    Calculates indicators from historical price data:
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - Moving Averages (SMA 20, 50)
    - Trading signals
    """
    
    def __init__(self, price_provider, cache_manager=None, cache_ttl: int = 3600):
        """
        Initialize Technical provider.
        
        Args:
            price_provider: YFinanceProvider instance
            cache_manager: Optional CacheManager
            cache_ttl: Cache TTL in seconds (default 1 hour)
        """
        self.price_provider = price_provider
        self.cache_manager = cache_manager
        self.cache_ttl = cache_ttl
    
    async def get_indicators(self, ticker: str) -> Dict:
        """
        Get technical indicators for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with technical indicators
        """
        # Check cache
        if self.cache_manager:
            cache_key = f"technical:{ticker}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"Technical cache hit for {ticker}")
                return cached
        
        # Get historical data
        try:
            hist_data = await self.price_provider.get_historical(
                ticker,
                period="3mo",
                interval="1d"
            )
            
            if not hist_data or not hist_data.get('close_prices'):
                logger.warning(f"No historical data for {ticker}")
                return self._get_default_indicators(ticker)
            
            # Calculate indicators
            close_prices = np.array(hist_data['close_prices'])
            
            indicators = {
                "ticker": ticker,
                "rsi": self._calculate_rsi(close_prices),
                "macd": self._calculate_macd(close_prices),
                "ma_20": self._calculate_sma(close_prices, 20),
                "ma_50": self._calculate_sma(close_prices, 50),
                "signal": "NEUTRAL",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Generate trading signal
            indicators["signal"] = self._generate_signal(indicators)
            
            # Cache result
            if self.cache_manager:
                cache_key = f"technical:{ticker}"
                await self.cache_manager.set(cache_key, indicators, ttl=self.cache_ttl)
            
            return indicators
        
        except Exception as e:
            logger.error(f"Failed to calculate indicators for {ticker}: {e}")
            return self._get_default_indicators(ticker)
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        # Calculate price changes
        deltas = np.diff(prices)
        
        # Separate gains and losses
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        # Calculate average gains and losses
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 1)
    
    def _calculate_macd(self, prices: np.ndarray) -> float:
        """Calculate MACD (12, 26, 9)"""
        if len(prices) < 26:
            return 0.0
        
        # Calculate EMAs
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        macd = ema_12 - ema_26
        
        return round(macd, 2)
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_sma(self, prices: np.ndarray, period: int) -> float:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return round(float(np.mean(prices)), 2)
        
        return round(float(np.mean(prices[-period:])), 2)
    
    def _generate_signal(self, indicators: Dict) -> str:
        """Generate trading signal from indicators"""
        rsi = indicators["rsi"]
        macd = indicators["macd"]
        
        # Simple signal logic
        if rsi < 40 and macd > 0:
            return "BUY"
        elif rsi > 60 and macd < 0:
            return "SELL"
        else:
            return "NEUTRAL"
    
    def _get_default_indicators(self, ticker: str) -> Dict:
        """Return default indicators when calculation fails"""
        return {
            "ticker": ticker,
            "rsi": 50.0,
            "macd": 0.0,
            "ma_20": 0.0,
            "ma_50": 0.0,
            "signal": "NEUTRAL",
            "timestamp": datetime.utcnow().isoformat()
        }
