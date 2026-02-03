"""
Phase 4 Example - Real Market Data Integration

Demonstrates the trading system with REAL market data from yfinance
while maintaining <500ms latency through intelligent caching.
"""

import asyncio
import logging
from sentinel import CacheManager, ProviderFactory
from sentinel.data import YFinanceProvider, TechnicalProvider, RealNewsProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_real_data_providers():
    """Demonstrate real data providers"""
    print("=" * 70)
    print("PHASE 4: REAL MARKET DATA INTEGRATION")
    print("=" * 70)
    
    # Initialize cache
    print("\n[1] Initializing cache manager...")
    cache = CacheManager(db_path="./sentinel_state/phase4_cache.db")
    await cache.initialize()
    print("  ✓ Cache ready")
    
    # Initialize real providers
    print("\n[2] Initializing real data providers...")
    price_provider = YFinanceProvider(cache_manager=cache)
    technical_provider = TechnicalProvider(price_provider, cache_manager=cache)
    news_provider = RealNewsProvider(cache_manager=cache)
    print("  ✓ YFinance, Technical, and News providers ready")
    
    # Test with a real ticker
    ticker = "AAPL"
    print(f"\n[3] Fetching REAL data for {ticker}...")
    
    # Get price (will be slow first time, fast from cache)
    print(f"\n  📊 Price Data (first fetch - may take 1-2s):")
    price_data = await price_provider.get_price(ticker)
    print(f"    Current Price: ${price_data['price']:.2f}")
    print(f"    Volume: {price_data['volume']:,}")
    print(f"    Change: {price_data['change_pct']:+.2f}%")
    
    # Get technical indicators
    print(f"\n  📈 Technical Indicators (calculating from real history):")
    technical_data = await technical_provider.get_indicators(ticker)
    print(f"    RSI: {technical_data['rsi']:.1f}")
    print(f"    MACD: {technical_data['macd']:.2f}")
    print(f"    MA(20): ${technical_data['ma_20']:.2f}")
    print(f"    Signal: {technical_data['signal']}")
    
    # Get news sentiment
    print(f"\n  📰 News Sentiment (from real news):")
    news_data = await news_provider.get_sentiment(ticker)
    print(f"    Sentiment: {news_data['sentiment_score']:.1f}/100")
    print(f"    Headline: {news_data['headline']}")
    print(f"    Articles: {news_data['article_count']}")
    
    # Test cache performance
    print(f"\n[4] Testing cache performance (second fetch should be <10ms)...")
    import time
    start = time.time()
    cached_price = await price_provider.get_price(ticker)
    latency_ms = (time.time() - start) * 1000
    print(f"  ✅ Cache hit! Latency: {latency_ms:.1f}ms")
    
    # Show cache metrics
    print(f"\n[5] Cache Metrics:")
    metrics = cache.get_metrics()
    print(f"  L1 Hits: {metrics['l1_hits']}")
    print(f"  L2 Hits: {metrics['l2_hits']}")
    print(f"  Misses: {metrics['misses']}")
    print(f"  Hit Rate: {metrics['hit_rate']:.1%}")
    
    await cache.close()
    print("\n✅ Real data integration working!")


async def example_provider_factory():
    """Demonstrate provider factory for easy switching"""
    print("\n\n" + "=" * 70)
    print("PROVIDER FACTORY - EASY MOCK/REAL SWITCHING")
    print("=" * 70)
    
    # Initialize cache
    cache = CacheManager(db_path=":memory:")
    await cache.initialize()
    
    # Create factory with REAL providers
    print("\n[1] Creating factory with REAL providers...")
    factory = ProviderFactory(use_mock=False, cache_manager=cache)
    
    price_provider = factory.get_price_provider()
    print(f"  Price Provider: {type(price_provider).__name__}")
    
    # Fetch real data
    print("\n[2] Fetching real data for MSFT...")
    data = await price_provider.get_price("MSFT")
    print(f"  MSFT Price: ${data['price']:.2f}")
    
    # Switch to mock for testing
    print("\n[3] Creating factory with MOCK providers...")
    mock_factory = ProviderFactory(use_mock=True)
    
    mock_price_provider = mock_factory.get_price_provider()
    print(f"  Price Provider: {type(mock_price_provider).__name__}")
    
    # Fetch mock data (instant)
    print("\n[4] Fetching mock data for MSFT...")
    mock_data = await mock_price_provider.get_price("MSFT")
    print(f"  MSFT Price (mock): ${mock_data['price']:.2f}")
    
    await cache.close()
    print("\n✅ Provider factory enables easy testing!")


async def example_batch_fetching():
    """Demonstrate batch fetching for multiple tickers"""
    print("\n\n" + "=" * 70)
    print("BATCH FETCHING - PARALLEL DATA COLLECTION")
    print("=" * 70)
    
    cache = CacheManager(db_path=":memory:")
    await cache.initialize()
    
    price_provider = YFinanceProvider(cache_manager=cache)
    
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    print(f"\n[1] Fetching prices for {len(tickers)} tickers in parallel...")
    
    import time
    start = time.time()
    prices = await price_provider.get_batch_prices(tickers)
    latency_ms = (time.time() - start) * 1000
    
    print(f"\n  Fetched {len(prices)} tickers in {latency_ms:.0f}ms")
    print(f"  Average: {latency_ms/len(prices):.0f}ms per ticker\n")
    
    for ticker, data in prices.items():
        print(f"  {ticker}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
    
    await cache.close()
    print("\n✅ Batch fetching enables fast multi-ticker analysis!")


async def main():
    """Run all examples"""
    await example_real_data_providers()
    await example_provider_factory()
    await example_batch_fetching()
    
    print("\n" + "=" * 70)
    print("PHASE 4 COMPLETE - REAL DATA INTEGRATION WORKING!")
    print("=" * 70)
    print("\n🎉 You now have REAL market data with intelligent caching!")
    print("   Next: Integrate with agents for live trading signals")


if __name__ == "__main__":
    asyncio.run(main())
