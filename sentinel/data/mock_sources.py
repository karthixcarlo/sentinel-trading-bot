"""
Mock Data Sources for Testing

Provides simulated data for testing the trading system without external API dependencies.
"""

import random
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class MockPriceProvider:
    """Mock price data provider"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        
        # Base prices for common tickers
        self.base_prices = {
            "AAPL": 150.0,
            "MSFT": 380.0,
            "GOOGL": 140.0,
            "TSLA": 180.0,
            "AMZN": 170.0,
            "NVDA": 500.0,
            "META": 350.0,
        }
    
    async def get_price(self, ticker: str) -> Dict:
        """Get current price with simulated delay"""
        await self._simulate_latency(10, 30)  # 10-30ms
        
        base_price = self.base_prices.get(ticker, 100.0)
        
        # Add random variation (±2%)
        variation = random.uniform(-0.02, 0.02)
        current_price = base_price * (1 + variation)
        
        return {
            "ticker": ticker,
            "price": round(current_price, 2),
            "volume": random.randint(500000, 2000000),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _simulate_latency(self, min_ms: int, max_ms: int):
        """Simulate network latency"""
        import asyncio
        latency = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(latency)


class MockNewsProvider:
    """Mock news sentiment provider"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
    
    async def get_sentiment(self, ticker: str) -> Dict:
        """Get news sentiment score"""
        await self._simulate_latency(20, 50)  # 20-50ms
        
        # Simulate sentiment score (0-100, higher is more bullish)
        sentiment = random.uniform(40, 90)
        
        # Simulate headline
        headlines = [
            f"{ticker} announces strong quarterly results",
            f"Analysts upgrade {ticker} price target",
            f"{ticker} launches new product line",
            f"Market optimistic about {ticker} growth",
            f"{ticker} expands into new markets"
        ]
        
        return {
            "ticker": ticker,
            "sentiment_score": round(sentiment, 1),
            "headline": random.choice(headlines),
            "confidence": random.uniform(0.7, 0.95),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _simulate_latency(self, min_ms: int, max_ms: int):
        """Simulate network latency"""
        import asyncio
        latency = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(latency)


class MockTechnicalProvider:
    """Mock technical indicators provider"""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
    
    async def get_indicators(self, ticker: str) -> Dict:
        """Get technical indicators"""
        await self._simulate_latency(15, 40)  # 15-40ms
        
        # RSI (30-70 range, 50 is neutral)
        rsi = random.uniform(35, 70)
        
        # MACD (positive or negative)
        macd = random.uniform(-2, 3)
        
        # Moving averages
        ma_20 = random.uniform(145, 155)
        ma_50 = random.uniform(140, 160)
        
        return {
            "ticker": ticker,
            "rsi": round(rsi, 1),
            "macd": round(macd, 2),
            "ma_20": round(ma_20, 2),
            "ma_50": round(ma_50, 2),
            "signal": "BUY" if rsi < 50 and macd > 0 else "NEUTRAL",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def _simulate_latency(self, min_ms: int, max_ms: int):
        """Simulate network latency"""
        import asyncio
        latency = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(latency)


class MockSupplyChainProvider:
    """Mock supply chain data provider"""
    
    def __init__(self):
        # Simplified supply chain relationships
        self.supply_chains = {
            "AAPL": {
                "suppliers": ["TSMC", "FOXCONN", "QCOM"],
                "subsidiaries": ["BEATS", "SHAZAM"],
                "risk_score": 35.2
            },
            "TSLA": {
                "suppliers": ["PANASONIC", "LG", "CATL"],
                "subsidiaries": ["SOLARCITY"],
                "risk_score": 52.8
            },
            "MSFT": {
                "suppliers": ["INTC", "AMD", "NVDA"],
                "subsidiaries": ["LINKEDIN", "GITHUB"],
                "risk_score": 28.5
            },
            "GOOGL": {
                "suppliers": ["INTC", "NVDA", "TSMC"],
                "subsidiaries": ["YOUTUBE", "WAYMO"],
                "risk_score": 31.2
            }
        }
    
    async def get_supply_chain(self, ticker: str) -> Dict:
        """Get supply chain data (fast, from cache)"""
        await self._simulate_latency(2, 8)  # 2-8ms (cached)
        
        data = self.supply_chains.get(ticker, {
            "suppliers": [],
            "subsidiaries": [],
            "risk_score": 50.0
        })
        
        return {
            "ticker": ticker,
            **data,
            "last_updated": datetime.utcnow().isoformat(),
            "cached": True
        }
    
    async def _simulate_latency(self, min_ms: int, max_ms: int):
        """Simulate cache lookup latency"""
        import asyncio
        latency = random.uniform(min_ms, max_ms) / 1000
        await asyncio.sleep(latency)


# Singleton instances
_price_provider = None
_news_provider = None
_technical_provider = None
_supply_chain_provider = None


def get_price_provider() -> MockPriceProvider:
    """Get singleton price provider"""
    global _price_provider
    if _price_provider is None:
        _price_provider = MockPriceProvider()
    return _price_provider


def get_news_provider() -> MockNewsProvider:
    """Get singleton news provider"""
    global _news_provider
    if _news_provider is None:
        _news_provider = MockNewsProvider()
    return _news_provider


def get_technical_provider() -> MockTechnicalProvider:
    """Get singleton technical provider"""
    global _technical_provider
    if _technical_provider is None:
        _technical_provider = MockTechnicalProvider()
    return _technical_provider


def get_supply_chain_provider() -> MockSupplyChainProvider:
    """Get singleton supply chain provider"""
    global _supply_chain_provider
    if _supply_chain_provider is None:
        _supply_chain_provider = MockSupplyChainProvider()
    return _supply_chain_provider
