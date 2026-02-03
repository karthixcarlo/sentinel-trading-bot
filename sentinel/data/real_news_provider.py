"""
Real News Provider - Sentiment Analysis

Fetches real news and calculates sentiment scores using yfinance news data.
"""

import asyncio
import logging
from typing import Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class RealNewsProvider:
    """
    Real news sentiment provider using yfinance news.
    
    Features:
    - Fetches recent news from yfinance
    - Keyword-based sentiment scoring
    - Aggregates multiple articles
    - Cache support
    """
    
    # Positive and negative keywords for sentiment
    POSITIVE_KEYWORDS = [
        'growth', 'profit', 'surge', 'beat', 'strong', 'upgrade',
        'bullish', 'gain', 'rise', 'positive', 'success', 'record',
        'outperform', 'exceed', 'boost', 'rally'
    ]
    
    NEGATIVE_KEYWORDS = [
        'loss', 'decline', 'fall', 'miss', 'weak', 'downgrade',
        'bearish', 'drop', 'negative', 'concern', 'risk', 'warning',
        'underperform', 'cut', 'layoff', 'lawsuit'
    ]
    
    def __init__(self, cache_manager=None, cache_ttl: int = 21600):
        """
        Initialize News provider.
        
        Args:
            cache_manager: Optional CacheManager
            cache_ttl: Cache TTL in seconds (default 6 hours)
        """
        self.cache_manager = cache_manager
        self.cache_ttl = cache_ttl
    
    async def get_sentiment(self, ticker: str) -> Dict:
        """
        Get news sentiment for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with sentiment data
        """
        # Check cache
        if self.cache_manager:
            cache_key = f"news:{ticker}"
            cached = await self.cache_manager.get(cache_key)
            if cached:
                logger.debug(f"News cache hit for {ticker}")
                return cached
        
        # Fetch news
        try:
            sentiment_data = await self._fetch_sentiment(ticker)
            
            # Cache result
            if self.cache_manager:
                cache_key = f"news:{ticker}"
                await self.cache_manager.set(cache_key, sentiment_data, ttl=self.cache_ttl)
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Failed to fetch news for {ticker}: {e}")
            return self._get_default_sentiment(ticker)
    
    async def _fetch_sentiment(self, ticker: str) -> Dict:
        """Fetch and analyze news sentiment"""
        import yfinance as yf
        
        loop = asyncio.get_event_loop()
        
        def _fetch():
            stock = yf.Ticker(ticker)
            
            try:
                # Get news
                news = stock.news
                
                if not news:
                    return self._get_default_sentiment(ticker)
                
                # Analyze sentiment from headlines
                sentiments = []
                headlines = []
                
                for article in news[:5]:  # Analyze top 5 articles
                    title = article.get('title', '')
                    headlines.append(title)
                    
                    # Calculate sentiment score
                    score = self._calculate_sentiment(title)
                    sentiments.append(score)
                
                # Aggregate sentiment
                avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 50.0
                
                # Calculate confidence based on article count
                confidence = min(len(news) / 10, 1.0)  # Max confidence at 10+ articles
                
                return {
                    "ticker": ticker,
                    "sentiment_score": round(avg_sentiment, 1),
                    "headline": headlines[0] if headlines else f"{ticker} news",
                    "confidence": round(confidence, 2),
                    "article_count": len(news),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            except Exception as e:
                logger.warning(f"Error fetching news for {ticker}: {e}")
                return self._get_default_sentiment(ticker)
        
        return await loop.run_in_executor(None, _fetch)
    
    def _calculate_sentiment(self, text: str) -> float:
        """Calculate sentiment score from text using keywords"""
        text_lower = text.lower()
        
        # Count positive and negative keywords
        positive_count = sum(1 for word in self.POSITIVE_KEYWORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_KEYWORDS if word in text_lower)
        
        # Calculate score (50 = neutral, 0-100 scale)
        if positive_count + negative_count == 0:
            return 50.0
        
        # Weight positive more heavily (bullish bias)
        score = 50 + (positive_count * 15) - (negative_count * 10)
        
        # Clamp to 0-100
        return max(0, min(100, score))
    
    def _get_default_sentiment(self, ticker: str) -> Dict:
        """Return default sentiment when fetch fails"""
        return {
            "ticker": ticker,
            "sentiment_score": 50.0,
            "headline": f"{ticker} - No recent news",
            "confidence": 0.5,
            "article_count": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
