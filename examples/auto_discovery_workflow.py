"""
AUTOMATED INDIAN STOCK DISCOVERY & DEEP SEARCH

This example demonstrates:
1. Auto-discovery from Moneycontrol (top gainers, losers, most active)
2. Deep search on discovered stocks
3. Intelligent screening and analysis
4. Actionable trade recommendations

No manual stock selection needed - fully autonomous!
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.indian_market_discovery import IndianMarketDiscovery, deep_search_stock
from sentinel.indian_market_config import IST
from sentinel import ProviderFactory, ConservativeRiskModel

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run automated discovery and deep search"""
    
    print("=" * 80)
    print("🔍 AUTOMATED INDIAN STOCK DISCOVERY & DEEP SEARCH")
    print("=" * 80)
    
    now = datetime.now(IST)
    print(f"\n⏰ IST Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Initialize discovery scanner
    print("\n" + "=" * 80)
    print("[1] Initializing Market Discovery Scanner...")
    print("=" * 80)
    
    try:
        discovery = IndianMarketDiscovery(cache_ttl=300)
        print("  ✓ Discovery scanner ready")
        print("  ✓ Will scrape: Moneycontrol, NSE India")
    except ImportError as e:
        print(f"\n⚠️  Missing dependencies: {e}")
        print("\nInstall with:")
        print("  pip install beautifulsoup4 requests")
        return
    
    # Run discovery across all categories
    print("\n" + "=" * 80)
    print("[2] Discovering Trending Stocks...")
    print("=" * 80)
    print("  🌐 Scraping Moneycontrol...")
    
    try:
        # Discover top stocks from all categories
        results = await discovery.discover_all(limit_per_category=10)
        
        # Display results
        print(f"\n📊 DISCOVERY RESULTS:\n")
        
        # Top Gainers
        gainers = results.get('top_gainers', [])
        if gainers:
            print(f"🚀 TOP GAINERS ({len(gainers)}):")
            for i, stock in enumerate(gainers[:5], 1):
                print(f"  {i}. {stock['symbol']:15} ₹{stock['price']:>8.2f}  "
                      f"📈 {stock['change_percent']:>6.2f}%")
        
        # Top Losers
        losers = results.get('top_losers', [])
        if losers:
            print(f"\n📉 TOP LOSERS ({len(losers)}):")
            for i, stock in enumerate(losers[:5], 1):
                print(f"  {i}. {stock['symbol']:15} ₹{stock['price']:>8.2f}  "
                      f"📉 {stock['change_percent']:>6.2f}%")
        
        # Most Active
        active = results.get('most_active', [])
        if active:
            print(f"\n🔥 MOST ACTIVE ({len(active)}):")
            for i, stock in enumerate(active[:5], 1):
                volume_str = f"{stock.get('volume', 0):,}" if stock.get('volume') else"N/A"
                print(f"  {i}. {stock['symbol']:15} ₹{stock['price']:>8.2f}  "
                      f"Vol: {volume_str}")
        
        # Get unique symbols for deep search
        unique_symbols = discovery.get_unique_symbols(results)
        print(f"\n✅ Total unique stocks discovered: {len(unique_symbols)}")
        
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Deep search on top candidates
    if not unique_symbols:
        print("\n⚠️  No stocks discovered. Market may be closed or site unavailable.")
        return
    
    print("\n" + "=" * 80)
    print("[3] DEEP SEARCH on Top Candidates...")
    print("=" * 80)
    
    # Initialize providers for deep search
    try:
        factory = ProviderFactory(use_mock=False, market_region="INDIA")
        price_provider = factory.get_price_provider()
        print("  ✓ Price provider ready (Yahoo Finance India)")
    except Exception as e:
        print(f"  ⚠️  Using mock data: {e}")
        factory = ProviderFactory(use_mock=True)
        price_provider = factory.get_price_provider()
    
    # Risk model for position sizing
    risk_model = ConservativeRiskModel(
        account_balance=100000.0,  # ₹1 lakh
        market_region="INDIA",
        currency="INR"
    )
    
    # Deep search top 5 stocks
    top_candidates = unique_symbols[:5]
    print(f"\n🔬 Analyzing {len(top_candidates)} stocks in detail...\n")
    
    recommendations = []
    
    for symbol in top_candidates:
        print(f"  Analyzing {symbol}...")
        
        try:
            # Deep search
            analysis = await deep_search_stock(
                symbol=symbol,
                price_provider=price_provider,
                news_provider=None  # Can add news provider later
            )
            
            if analysis['price_data']:
                price = analysis['price_data']['price']
                change = analysis['price_data']['change_percent']
                
                # Calculate position size
                stop_loss = price * 0.98  # 2% stop
                shares, risk_params = risk_model.calculate_position_size(
                    entry_price=price,
                    stop_loss_price=stop_loss,
                    confidence=0.7
                )
                
                recommendations.append({
                    'symbol': symbol,
                    'price': price,
                    'change_percent': change,
                    'shares': shares,
                    'position_value': risk_params.position_value,
                    'recommendation': analysis['recommendation']
                })
                
                print(f"    ✓ ₹{price:.2f} ({change:+.2f}%) - {analysis['recommendation']}")
            
        except Exception as e:
            logger.debug(f"Error analyzing {symbol}: {e}")
            print(f"    ⚠️  Analysis failed")
    
    # Display final recommendations
    if recommendations:
        print("\n" + "=" * 80)
        print("📋 TRADING RECOMMENDATIONS")
        print("=" * 80)
        
        # Sort by recommendation strength
        rec_order = {'STRONG_BUY': 0, 'BUY': 1, 'HOLD': 2, 'SELL': 3, 'STRONG_SELL': 4}
        recommendations.sort(key=lambda x: rec_order.get(x['recommendation'], 5))
        
        for rec in recommendations:
            action_emoji = {
                'STRONG_BUY': '🟢🟢',
                'BUY': '🟢',
                'HOLD': '🟡',
                'SELL': '🔴',
                'STRONG_SELL': '🔴🔴'
            }.get(rec['recommendation'], '⚪')
            
            print(f"\n{action_emoji} {rec['symbol']}")
            print(f"   Price: ₹{rec['price']:.2f} ({rec['change_percent']:+.2f}%)")
            print(f"   Action: {rec['recommendation']}")
            print(f"   Suggested Size: {rec['shares']} shares (₹{rec['position_value']:,.0f})")
    
    print("\n" + "=" * 80)
    print("✅ DISCOVERY & ANALYSIS COMPLETE!")
    print("=" * 80)
    
    print("\n💡 Summary:")
    print(f"  • Stocks Discovered: {len(unique_symbols)}")
    print(f"  • Deep Analysis: {len(recommendations)}")
    print(f"  • Data Source: Moneycontrol + Yahoo Finance")
    print(f"  • Market: NSE/BSE")
    
    print("\n🤖 This system runs fully autonomous!")
    print("   No manual stock selection needed - it finds opportunities for you!")


if __name__ == "__main__":
    asyncio.run(main())
