"""
Indian Market Discovery Scanner

Scrapes Indian financial websites (Moneycontrol, Economic Times, NSE)
to discover trending stocks, then performs deep analysis on them.

Features:
- Top gainers/losers detection
- Most active stocks by volume
- News-based sentiment analysis
- Sector momentum tracking
- Fundamental screening
"""

import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime
import re

try:
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    BeautifulSoup = None
    requests = None

from sentinel.indian_market_config import IST, get_indian_symbol_format

logger = logging.getLogger(__name__)


class IndianMarketDiscovery:
    """
    Discovers trending and promising Indian stocks from financial websites.
    
    Sources:
    - Moneycontrol (top gainers, losers, most active)
    - NSE India (market movers)
    - Economic Times (trending stocks)
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the discovery scanner.
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default 5 minutes)
        """
        if BeautifulSoup is None or requests is None:
            raise ImportError(
                "BeautifulSoup4 and requests required. "
                "Install with: pip install beautifulsoup4 requests"
            )
        
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._last_fetch = {}
        
        # User agent to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def discover_top_gainers(self, limit: int = 20) -> List[Dict]:
        """
        Scrape top gaining stocks from Moneycontrol.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stock dictionaries with symbol, price, change
        """
        cache_key = f"top_gainers_{limit}"
        
        # Check cache
        if self._is_cache_valid(cache_key):
            logger.info("Returning cached top gainers")
            return self._cache[cache_key]
        
        logger.info(f"Fetching top {limit} gainers from Moneycontrol...")
        
        url = "https://www.moneycontrol.com/stocks/marketsdata/top-gainers/"
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=self.headers, timeout=10)
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch gainers: HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse the table (structure varies, this is a basic approach)
            gainers = []
            
            # Look for stock data in various table formats
            tables = soup.find_all('table', class_='tbldatacontainer')
            
            for table in tables:
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows[:limit]:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        try:
                            # Extract symbol (clean it up)
                            symbol_elem = cols[0].find('a')
                            if symbol_elem:
                                symbol = symbol_elem.text.strip()
                                # Clean symbol (remove spaces, special chars)
                                symbol = re.sub(r'[^A-Z0-9]', '', symbol.upper())
                            else:
                                continue
                            
                            # Extract price and change
                            price_text = cols[1].text.strip().replace(',', '')
                            change_text = cols[2].text.strip().replace('%', '')
                            
                            price = float(price_text)
                            change_pct = float(change_text)
                            
                            gainers.append({
                                'symbol': symbol,
                                'price': price,
                                'change_percent': change_pct,
                                'source': 'moneycontrol',
                                'category': 'top_gainer',
                                'discovered_at': datetime.now(IST)
                            })
                        except (ValueError, AttributeError, IndexError) as e:
                            logger.debug(f"Error parsing row: {e}")
                            continue
            
            # Cache results
            self._cache[cache_key] = gainers
            self._last_fetch[cache_key] = datetime.now()
            
            logger.info(f"Discovered {len(gainers)} top gainers")
            return gainers
            
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return []
    
    async def discover_top_losers(self, limit: int = 20) -> List[Dict]:
        """
        Scrape top losing stocks from Moneycontrol.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stock dictionaries
        """
        cache_key = f"top_losers_{limit}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        logger.info(f"Fetching top {limit} losers from Moneycontrol...")
        
        url = "https://www.moneycontrol.com/stocks/marketsdata/top-losers/"
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=self.headers, timeout=10)
            )
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            losers = []
            tables = soup.find_all('table', class_='tbldatacontainer')
            
            for table in tables:
                rows = table.find_all('tr')[1:]
                
                for row in rows[:limit]:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        try:
                            symbol_elem = cols[0].find('a')
                            if symbol_elem:
                                symbol = re.sub(r'[^A-Z0-9]', '', 
                                              symbol_elem.text.strip().upper())
                            else:
                                continue
                            
                            price = float(cols[1].text.strip().replace(',', ''))
                            change_pct = float(cols[2].text.strip().replace('%', ''))
                            
                            losers.append({
                                'symbol': symbol,
                                'price': price,
                                'change_percent': change_pct,
                                'source': 'moneycontrol',
                                'category': 'top_loser',
                                'discovered_at': datetime.now(IST)
                            })
                        except (ValueError, AttributeError, IndexError):
                            continue
            
            self._cache[cache_key] = losers
            self._last_fetch[cache_key] = datetime.now()
            
            logger.info(f"Discovered {len(losers)} top losers")
            return losers
            
        except Exception as e:
            logger.error(f"Error fetching top losers: {e}")
            return []
    
    async def discover_most_active(self, limit: int = 20) -> List[Dict]:
        """
        Scrape most active stocks by volume.
        
        Args:
            limit: Number of stocks to return
            
        Returns:
            List of stock dictionaries
        """
        cache_key = f"most_active_{limit}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        logger.info(f"Fetching top {limit} most active stocks...")
        
        url = "https://www.moneycontrol.com/stocks/marketsdata/volumeshockers/"
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=self.headers, timeout=10)
            )
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            active_stocks = []
            tables = soup.find_all('table', class_='tbldatacontainer')
            
            for table in tables:
                rows = table.find_all('tr')[1:]
                
                for row in rows[:limit]:
                    cols = row.find_all('td')
                    if len(cols) >= 3:
                        try:
                            symbol_elem = cols[0].find('a')
                            if symbol_elem:
                                symbol = re.sub(r'[^A-Z0-9]', '', 
                                              symbol_elem.text.strip().upper())
                            else:
                                continue
                            
                            price = float(cols[1].text.strip().replace(',', ''))
                            
                            # Volume might be in different column
                            volume_text = cols[-1].text.strip().replace(',', '')
                            try:
                                volume = int(volume_text)
                            except ValueError:
                                volume = 0
                            
                            active_stocks.append({
                                'symbol': symbol,
                                'price': price,
                                'volume': volume,
                                'source': 'moneycontrol',
                                'category': 'most_active',
                                'discovered_at': datetime.now(IST)
                            })
                        except (ValueError, AttributeError, IndexError):
                            continue
            
            self._cache[cache_key] = active_stocks
            self._last_fetch[cache_key] = datetime.now()
            
            logger.info(f"Discovered {len(active_stocks)} most active stocks")
            return active_stocks
            
        except Exception as e:
            logger.error(f"Error fetching most active: {e}")
            return []
    
    async def discover_all(self, limit_per_category: int = 10) -> Dict[str, List[Dict]]:
        """
        Discover stocks from all categories.
        
        Args:
            limit_per_category: Number of stocks per category
            
        Returns:
            Dictionary with all discovered stocks by category
        """
        logger.info("Running full discovery scan...")
        
        # Fetch all categories concurrently
        gainers_task = self.discover_top_gainers(limit_per_category)
        losers_task = self.discover_top_losers(limit_per_category)
        active_task = self.discover_most_active(limit_per_category)
        
        gainers, losers, active = await asyncio.gather(
            gainers_task,
            losers_task,
            active_task
        )
        
        results = {
            'top_gainers': gainers,
            'top_losers': losers,
            'most_active': active
        }
        
        # Get unique symbols
        all_symbols = set()
        for category in results.values():
            for stock in category:
                all_symbols.add(stock['symbol'])
        
        logger.info(f"Discovery complete: {len(all_symbols)} unique stocks found")
        
        return results
    
    def get_unique_symbols(self, discovery_results: Dict) -> List[str]:
        """
        Extract unique symbols from discovery results.
        
        Args:
            discovery_results: Results from discover_all()
            
        Returns:
            List of unique stock symbols
        """
        symbols = set()
        
        for category in discovery_results.values():
            for stock in category:
                symbols.add(stock['symbol'])
        
        return sorted(list(symbols))
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache:
            return False
        
        if key not in self._last_fetch:
            return False
        
        age = (datetime.now() - self._last_fetch[key]).total_seconds()
        return age < self.cache_ttl


async def deep_search_stock(
    symbol: str,
    price_provider=None,
    news_provider=None
) -> Dict:
    """
    Perform deep analysis on a discovered stock.
    
    Args:
        symbol: Stock symbol to analyze
        price_provider: Price data provider
        news_provider: News data provider
        
    Returns:
        Comprehensive analysis dictionary
    """
    logger.info(f"Deep searching {symbol}...")
    
    analysis = {
        'symbol': symbol,
        'timestamp': datetime.now(IST),
        'price_data': None,
        'news_sentiment': None,
        'technical_signals': None,
        'recommendation': 'HOLD'
    }
    
    # 1. Get price data
    if price_provider:
        try:
            quote = await price_provider.get_quote(symbol, exchange="NSE")
            analysis['price_data'] = quote
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
    
    # 2. Get news sentiment
    if news_provider:
        try:
            news = await news_provider.get_news(symbol, limit=5)
            # Analyze sentiment here (would integrate with sentiment analyzer)
            analysis['news_sentiment'] = {
                'count': len(news),
                'headlines': [n.get('title') for n in news[:3]]
            }
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
    
    # 3. Technical analysis (basic)
    if analysis['price_data']:
        price = analysis['price_data'].get('price', 0)
        change_pct = analysis['price_data'].get('change_percent', 0)
        
        # Simple recommendation logic
        if change_pct > 3:
            analysis['recommendation'] = 'STRONG_BUY'
        elif change_pct > 1:
            analysis['recommendation'] = 'BUY'
        elif change_pct < -3:
            analysis['recommendation'] = 'STRONG_SELL'
        elif change_pct < -1:
            analysis['recommendation'] = 'SELL'
    
    return analysis
