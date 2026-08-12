"""
News Loader for Stock Analyzer - Web Scraping (No API Required)
Fetches recent news headlines using web scraping
"""

import logging
import re
from typing import List, Dict
from urllib.parse import quote_plus
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NewsLoader:
    """
    News fetcher using web scraping (no API keys needed)
    """
    
    def __init__(self):
        """Initialize NewsLoader"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def get_stock_news(self, ticker: str, limit: int = 3) -> List[Dict]:
        """
        Fetch recent news for a stock ticker using web scraping
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS", "TCS.NS")
            limit: Maximum number of news articles to fetch (default: 3)
            
        Returns:
            List of dictionaries containing news articles
        """
        
        # Clean ticker for search
        cleaned_name = self._clean_ticker(ticker)
        
        # Try Google Finance first
        news = self._scrape_google_finance(cleaned_name, limit)
        
        if news:
            return news[:limit]
        
        # Fallback to generic news
        return self._get_fallback_news(ticker)[:limit]
    
    def _scrape_google_finance(self, company_name: str, limit: int) -> List[Dict]:
        """Scrape news from Google Finance"""
        try:
            # Google search for recent news
            search_query = f"{company_name} stock news"
            url = f"https://www.google.com/search?q={quote_plus(search_query)}&tbm=nws"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            news_items = []
            
            # Parse news results
            for item in soup.find_all('div', class_='SoaBEf')[:limit]:
                try:
                    title_elem = item.find('div', class_='mCBkyc')
                    source_elem = item.find('div', class_='CEMjEf')
                    
                    if title_elem:
                        news_items.append({
                            'title': title_elem.get_text(strip=True),
                            'source': source_elem.get_text(strip=True) if source_elem else 'Google News',
                            'published_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'url': '#',
                            'description': ''
                        })
                except Exception as e:
                    logger.debug(f"Error parsing news item: {e}")
                    continue
            
            if news_items:
                logger.info(f"Scraped {len(news_items)} news items")
                return news_items
            
            return []
            
        except Exception as e:
            logger.error(f"Google Finance scraping failed: {e}")
            return []
    
    def _clean_ticker(self, ticker: str) -> str:
        """
        Clean ticker symbol for news search
        
        Examples:
            "RELIANCE.NS" -> "Reliance Industries"
            "TCS.NS" -> "Tata Consultancy Services"
        """
        # Remove exchange suffixes
        ticker = ticker.replace(".NS", "").replace(".BO", "").replace("NSE:", "")
        
        # Map common tickers to full company names
        ticker_map = {
            "RELIANCE": "Reliance Industries",
            "TCS": "Tata Consultancy Services",
            "INFY": "Infosys",
            "HDFCBANK": "HDFC Bank",
            "ICICIBANK": "ICICI Bank",
            "HINDUNILVR": "Hindustan Unilever",
            "ITC": "ITC Limited",
            "SBIN": "State Bank of India",
            "BHARTIARTL": "Bharti Airtel",
            "KOTAKBANK": "Kotak Mahindra Bank",
            "LT": "Larsen & Toubro",
            "AXISBANK": "Axis Bank",
            "ASIANPAINT": "Asian Paints",
            "MARUTI": "Maruti Suzuki",
            "SUNPHARMA": "Sun Pharmaceutical",
            "TITAN": "Titan Company",
            "WIPRO": "Wipro",
            "ULTRACEMCO": "UltraTech Cement",
            "NESTLEIND": "Nestle India",
            "BAJFINANCE": "Bajaj Finance",
            "HCLTECH": "HCL Technologies",
            "TECHM": "Tech Mahindra",
            "TATAMOTORS": "Tata Motors",
            "TATASTEEL": "Tata Steel",
            "M&M": "Mahindra & Mahindra",
            "ADANIENT": "Adani Enterprises",
            "ADANIPORTS": "Adani Ports"
        }
        
        # Return full name if available, otherwise use ticker
        return ticker_map.get(ticker.upper(), ticker)
    
    def _get_fallback_news(self, ticker: str) -> List[Dict]:
        """
        Generate fallback news when scraping fails
        """
        cleaned_name = self._clean_ticker(ticker)
        
        return [
            {
                'title': f"{cleaned_name}: Trading within expected range",
                'source': 'Market Summary',
                'published_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': '#',
                'description': 'Stock shows normal volatility patterns'
            },
            {
                'title': f"{cleaned_name}: Technical indicators show mixed signals",
                'source': 'Market Analysis',
                'published_at': (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
                'url': '#',
                'description': 'Analysts recommend monitoring key support levels'
            },
            {
                'title': f"{cleaned_name}: Volume remains steady",
                'source': 'Trading Desk',
                'published_at': (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M:%S'),
                'url': '#',
                'description': 'No significant market-moving events detected'
            }
        ]
    
    def get_news_summary(self, ticker: str) -> str:
        """
        Get a brief text summary of recent news for AI analysis.

        This text is scraped from a public search results page and is
        untrusted — it gets embedded directly into the prompt sent to the
        trading AI (see agents/analyst_agent_gemini.py), so it's stripped
        of control/formatting characters and length-capped here before it
        ever reaches that prompt, on top of the delimiting done there.
        """
        news_items = self.get_stock_news(ticker, limit=3)

        if not news_items:
            return "No recent news available"

        # Combine headlines into summary
        summary_parts = [_sanitize_headline(item['title']) for item in news_items]
        return " | ".join(p for p in summary_parts if p)


_MAX_HEADLINE_LEN = 200


def _sanitize_headline(text: str) -> str:
    """
    Strips control/newline characters and caps length on scraped headline
    text before it's joined into the AI prompt context — reduces (does not
    by itself eliminate) the surface for prompt-injection via a manipulated
    search-result page. See the delimiting done around this text in
    agents/analyst_agent_gemini.py for the primary mitigation.
    """
    if not text:
        return ""
    cleaned = re.sub(r"[\x00-\x1f\x7f]+", " ", text).strip()
    return cleaned[:_MAX_HEADLINE_LEN]


# Convenience functions (backward compatible)
def fetch_stock_news(ticker: str, max_results: int = 3) -> List[Dict]:
    """Fetch stock news"""
    loader = NewsLoader()
    return loader.get_stock_news(ticker, limit=max_results)


def get_news_summary(ticker: str) -> str:
    """Get news summary"""
    loader = NewsLoader()
    return loader.get_news_summary(ticker)


def get_sentiment_indicator(title: str) -> str:
    """
    Simple sentiment analysis based on keywords
    """
    title_lower = title.lower()
    
    positive_keywords = [
        'growth', 'profit', 'gain', 'surge', 'approval', 'expansion',
        'bullish', 'upgrade', 'record', 'strong', 'beats', 'positive',
        'rally', 'boost', 'rise', 'jump', 'success', 'win', 'high'
    ]
    
    negative_keywords = [
        'loss', 'decline', 'fall', 'crash', 'investigation', 'fire',
        'bearish', 'downgrade', 'weak', 'misses', 'negative', 'concern',
        'slump', 'plunge', 'drop', 'fail', 'warning', 'risk', 'low'
    ]
    
    positive_count = sum(1 for word in positive_keywords if word in title_lower)
    negative_count = sum(1 for word in negative_keywords if word in title_lower)
    
    if positive_count > negative_count:
        return "🟢 Positive"
    elif negative_count > positive_count:
        return "🔴 Negative"
    else:
        return "🔵 Neutral"


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("📰 NEWS LOADER TEST - Web Scraping")
    print("=" * 60)
    
    # Initialize loader
    loader = NewsLoader()
    
    # Test with Indian stock
    ticker = "RELIANCE.NS"
    print(f"\n📊 Fetching news for {ticker}...")
    print("-" * 60)
    
    news = loader.get_stock_news(ticker, limit=3)
    
    for i, item in enumerate(news, 1):
        print(f"\n{i}. {item['title']}")
        print(f"   Source: {item['source']}")
        print(f"   Published: {item['published_at']}")
        print(f"   Sentiment: {get_sentiment_indicator(item['title'])}")
    
    print("\n\n💡 Summary for AI:")
    print(f"{loader.get_news_summary(ticker)}")
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
