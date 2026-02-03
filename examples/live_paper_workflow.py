"""
LIVE PAPER TRADING WORKFLOW

Complete autonomous trading system with:
- Real market data from yfinance
- Real order execution via Alpaca
- Full Scout → Analyst → Executioner workflow
"""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel import (
    CacheManager,
    CircuitBreaker,
    ProviderFactory,
    AlpacaClient,
    PaperTradingExecutor,
    PortfolioManager
)
from sentinel.agents import ScoutAgent, AnalystAgent, ExecutionerAgent, AgentState
from sentinel.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, has_alpaca_credentials

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run complete live paper trading workflow"""
    print("=" * 80)
    print("🚀 LIVE PAPER TRADING WORKFLOW - REAL DATA + REAL EXECUTION")
    print("=" * 80)
    
    # Check Alpaca credentials
    if not has_alpaca_credentials():
        print("\n❌ Alpaca credentials not configured")
        return
    
    # Initialize infrastructure
    print("\n[1] Initializing infrastructure...")
    
    cache = CacheManager(db_path="./sentinel_state/live_trading_cache.db")
    await cache.initialize()
    print("  ✓ Cache manager ready")
    
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=60.0,
        state_file="./sentinel_state/circuit_breaker.json"
    )
    print(f"  ✓ Circuit breaker ready (state: {breaker.state.name})")
    
    # Initialize Alpaca
    print("\n[2] Connecting to Alpaca paper trading...")
    alpaca_client = AlpacaClient(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=True
    )
    
    # Get account info
    account = await alpaca_client.get_account()
    print(f"  ✓ Connected! Account: ${account['equity']:,.2f}")
    
    # Initialize portfolio manager
    portfolio = PortfolioManager(alpaca_client)
    
    # Initialize paper trading executor
    paper_executor = PaperTradingExecutor(alpaca_client)
    print("  ✓ Paper trading executor ready")
    
    # Initialize real data providers
    print("\n[3] Initializing REAL data providers...")
    provider_factory = ProviderFactory(use_mock=False, cache_manager=cache)
    print("  ✓ Real market data providers ready")
    
    # Initialize agents
    print("\n[4] Initializing trading agents...")
    
    scout = ScoutAgent(circuit_breaker=breaker, min_score=60.0)
    scout.price_provider = provider_factory.get_price_provider()
    scout.news_provider = provider_factory.get_news_provider()
    scout.technical_provider = provider_factory.get_technical_provider()
    scout.supply_chain_provider = provider_factory.get_supply_chain_provider()
    
    analyst = AnalystAgent(
        circuit_breaker=breaker,
        account_balance=account['cash'],
        min_confidence=0.65
    )
    
    # Use Alpaca executor instead of slippage simulator
    executioner = ExecutionerAgent(circuit_breaker=breaker)
    print("  ✓ Scout, Analyst, Executioner ready")
    
    # Define tickers
    tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
    print(f"\n[5] Starting workflow for {len(tickers)} tickers: {', '.join(tickers)}")
    print("    (Fetching REAL market data...)")
    
    state = AgentState(tickers=tickers)
    
    # PHASE 1: SCOUT
    print("\n" + "=" * 80)
    print("PHASE 1: SCOUT - Discovering opportunities from REAL market")
    print("=" * 80)
    
    scout_result = await scout.execute(state)
    
    if scout_result.success:
        state.scout_candidates = scout_result.data
        state.scout_latency_ms = scout_result.latency_ms
        
        print(f"\n✅ Found {len(state.scout_candidates)} candidates ({scout_result.latency_ms:.0f}ms)")
        
        for i, candidate in enumerate(state.scout_candidates[:3], 1):
            signals = candidate['signals']
            print(f"\n   #{i} {candidate['ticker']} (score: {candidate['score']:.1f}/100)")
            print(f"      Price: ${signals['price']['price']:.2f}")
            print(f"      RSI: {signals['technical']['rsi']:.1f}, Signal: {signals['technical']['signal']}")
    else:
        print(f"\n❌ Scout failed: {scout_result.error}")
        await cache.close()
        return
    
    if not state.scout_candidates:
        print("\n⚠️  No candidates found")
        await cache.close()
        return
    
    # PHASE 2: ANALYST
    print("\n" + "=" * 80)
    print("PHASE 2: ANALYST - Analyzing with risk management")
    print("=" * 80)
    
    analyst_result = await analyst.execute(state)
    
    if analyst_result.success:
        state.analyst_recommendations = analyst_result.data
        state.analyst_latency_ms = analyst_result.latency_ms
        
        print(f"\n✅ Generated {len(state.analyst_recommendations)} recommendations ({analyst_result.latency_ms:.0f}ms)")
        
        for i, rec in enumerate(state.analyst_recommendations, 1):
            print(f"\n   #{i} {rec['action']} {rec['ticker']}")
            print(f"      Entry: ${rec['entry_price']:.2f}, Position: {rec['position_size']} shares")
            print(f"      Confidence: {rec['confidence']:.2%}, Expected Return: {rec['expected_return']:.2%}")
    else:
        print(f"\n❌ Analyst failed: {analyst_result.error}")
        await cache.close()
        return
    
    if not state.analyst_recommendations:
        print("\n⚠️  No recommendations generated")
        await cache.close()
        return
    
    # PHASE 3: EXECUTIONER - REAL ALPACA EXECUTION
    print("\n" + "=" * 80)
    print("PHASE 3: EXECUTIONER - EXECUTING REAL PAPER TRADES ON ALPACA")
    print("=" * 80)
    
    execution_results = []
    
    for rec in state.analyst_recommendations:
        print(f"\n📤 Submitting {rec['action']} order for {rec['ticker']}...")
        
        try:
            result = await paper_executor.execute_trade(rec)
            execution_results.append(result)
            
            if result['status'] == 'EXECUTED':
                print(f"   ✅ Order filled: {result['filled_qty']} @ ${result['avg_fill_price']:.2f}")
                print(f"      Order ID: {result['order_id']}")
                print(f"      Slippage: {result['slippage_pct']:.3f}%")
            else:
                print(f"   ⚠️  Order status: {result['status']}")
        
        except Exception as e:
            print(f"   ❌ Execution failed: {e}")
    
    state.execution_results = execution_results
    
    # SUMMARY
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE - SUMMARY")
    print("=" * 80)
    
    total_latency = scout_result.latency_ms + analyst_result.latency_ms
    
    print(f"\n📊 Performance:")
    print(f"   Scout: {scout_result.latency_ms:.0f}ms")
    print(f"   Analyst: {analyst_result.latency_ms:.0f}ms")
    print(f"   Total: {total_latency:.0f}ms")
    
    print(f"\n📈 Trading Results:")
    print(f"   Candidates: {len(state.scout_candidates)}")
    print(f"   Recommendations: {len(state.analyst_recommendations)}")
    print(f"   Executed: {len([r for r in execution_results if r.get('status') == 'EXECUTED'])}")
    
    # Show updated portfolio
    print(f"\n💼 Updated Portfolio:")
    summary = await portfolio.get_summary()
    print(f"   Equity: ${summary['equity']:,.2f}")
    print(f"   Cash: ${summary['cash']:,.2f}")
    
    positions = await portfolio.get_positions()
    if positions:
        print(f"\n   Positions ({len(positions)}):")
        for pos in positions:
            print(f"   • {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
            print(f"     Current: ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pl']:.2f}")
    
    await cache.close()
    
    print("\n" + "=" * 80)
    print("🎉 LIVE PAPER TRADING WORKFLOW COMPLETE!")
    print("=" * 80)
    print("\n✨ You just ran a fully autonomous trading system with:")
    print("   • REAL stock prices from yfinance")
    print("   • REAL technical analysis")
    print("   • REAL news sentiment")
    print("   • REAL paper trades on Alpaca")
    print("\n🚀 Check your Alpaca dashboard to see the orders!")


if __name__ == "__main__":
    asyncio.run(main())
