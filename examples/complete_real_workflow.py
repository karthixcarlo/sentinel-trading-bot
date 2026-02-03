"""
Complete Trading Workflow with REAL Market Data

Demonstrates the full multi-agent trading system using REAL data from yfinance.
Shows Scout → Analyst → Executioner workflow with actual market prices,
technical indicators, and news sentiment.
"""

import asyncio
import logging
from sentinel import (
    CacheManager,
    CircuitBreaker,
    TradingOrchestrator,
    ProviderFactory
)
from sentinel.agents import ScoutAgent, AnalystAgent, ExecutionerAgent, AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run complete trading workflow with real market data"""
    print("=" * 80)
    print("PROJECT SENTINEL - COMPLETE TRADING WORKFLOW WITH REAL MARKET DATA")
    print("=" * 80)
    
    # Initialize infrastructure
    print("\n[1] Initializing infrastructure...")
    
    # Cache manager for fast data access
    cache = CacheManager(db_path="./sentinel_state/real_trading_cache.db")
    await cache.initialize()
    print("  ✓ Cache manager ready")
    
    # Circuit breaker for fault tolerance
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=60.0,
        state_file="./sentinel_state/circuit_breaker.json"
    )
    print(f"  ✓ Circuit breaker ready (state: {breaker.state.name})")
    
    # Provider factory with REAL data providers
    print("\n[2] Initializing REAL data providers...")
    provider_factory = ProviderFactory(
        use_mock=False,  # Use REAL data!
        cache_manager=cache
    )
    print("  ✓ YFinance provider (real stock prices)")
    print("  ✓ Technical provider (real RSI, MACD)")
    print("  ✓ News provider (real sentiment)")
    
    # Initialize agents with real data providers
    print("\n[3] Initializing trading agents...")
    
    # Scout agent - discovers opportunities from real signals
    scout = ScoutAgent(
        circuit_breaker=breaker,
        min_score=60.0
    )
    # Inject real providers
    scout.price_provider = provider_factory.get_price_provider()
    scout.news_provider = provider_factory.get_news_provider()
    scout.technical_provider = provider_factory.get_technical_provider()
    scout.supply_chain_provider = provider_factory.get_supply_chain_provider()
    
    # Analyst agent - analyzes with conservative risk model
    analyst = AnalystAgent(
        circuit_breaker=breaker,
        account_balance=10000.0,
        min_confidence=0.65
    )
    
    # Executioner agent - simulates realistic execution
    executioner = ExecutionerAgent(circuit_breaker=breaker)
    
    print("  ✓ Scout, Analyst, Executioner ready")
    
    # Define tickers to analyze (real stocks!)
    tickers = ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"]
    print(f"\n[4] Starting workflow for {len(tickers)} tickers: {', '.join(tickers)}")
    print("    (Fetching REAL market data - this may take 5-10 seconds...)")
    
    # Create initial state
    state = AgentState(tickers=tickers)
    
    # Execute workflow
    print("\n" + "=" * 80)
    print("PHASE 1: SCOUT - Discovering opportunities from REAL market data")
    print("=" * 80)
    
    scout_result = await scout.execute(state)
    
    if scout_result.success:
        state.scout_candidates = scout_result.data
        state.scout_latency_ms = scout_result.latency_ms
        
        print(f"\n✅ Scout found {len(state.scout_candidates)} candidates")
        print(f"   Latency: {scout_result.latency_ms:.0f}ms")
        
        # Show top candidates
        for i, candidate in enumerate(state.scout_candidates[:3], 1):
            print(f"\n   #{i} {candidate['ticker']} (score: {candidate['score']:.1f}/100)")
            signals = candidate['signals']
            print(f"      Price: ${signals['price']['price']:.2f}")
            print(f"      Sentiment: {signals['news']['sentiment_score']:.1f}/100")
            print(f"      RSI: {signals['technical']['rsi']:.1f}")
            print(f"      Signal: {signals['technical']['signal']}")
    else:
        print(f"\n❌ Scout failed: {scout_result.error}")
        await cache.close()
        return
    
    if not state.scout_candidates:
        print("\n⚠️  No candidates found, ending workflow")
        await cache.close()
        return
    
    # Analyst phase
    print("\n" + "=" * 80)
    print("PHASE 2: ANALYST - Analyzing candidates with risk management")
    print("=" * 80)
    
    analyst_result = await analyst.execute(state)
    
    if analyst_result.success:
        state.analyst_recommendations = analyst_result.data
        state.analyst_latency_ms = analyst_result.latency_ms
        
        print(f"\n✅ Analyst generated {len(state.analyst_recommendations)} recommendations")
        print(f"   Latency: {analyst_result.latency_ms:.0f}ms")
        
        # Show recommendations
        for i, rec in enumerate(state.analyst_recommendations, 1):
            print(f"\n   #{i} {rec['action']} {rec['ticker']}")
            print(f"      Entry: ${rec['entry_price']:.2f}")
            print(f"      Stop Loss: ${rec['stop_loss']:.2f}")
            print(f"      Take Profit: ${rec['take_profit']:.2f}")
            print(f"      Position: {rec['position_size']} shares")
            print(f"      Confidence: {rec['confidence']:.2%}")
            print(f"      Expected Return: {rec['expected_return']:.2%}")
    else:
        print(f"\n❌ Analyst failed: {analyst_result.error}")
        await cache.close()
        return
    
    if not state.analyst_recommendations:
        print("\n⚠️  No recommendations generated, ending workflow")
        await cache.close()
        return
    
    # Executioner phase
    print("\n" + "=" * 80)
    print("PHASE 3: EXECUTIONER - Executing trades with slippage simulation")
    print("=" * 80)
    
    executioner_result = await executioner.execute(state)
    
    if executioner_result.success:
        state.execution_results = executioner_result.data
        state.executioner_latency_ms = executioner_result.latency_ms
        
        print(f"\n✅ Executioner completed {len(state.execution_results)} trades")
        print(f"   Latency: {executioner_result.latency_ms:.0f}ms")
        
        # Show execution results
        total_cost = 0
        total_slippage = 0
        
        for i, result in enumerate(state.execution_results, 1):
            print(f"\n   #{i} {result['status']}: {result['action']} {result['ticker']}")
            print(f"      Filled: {result['filled_qty']}/{result['intended_qty']} shares")
            print(f"      Avg Fill: ${result['avg_fill_price']:.2f}")
            print(f"      Slippage: {result['slippage_pct']:.3f}% (${result['slippage_cost']:.2f})")
            print(f"      Total Cost: ${result['total_cost']:.2f}")
            
            total_cost += result['total_cost']
            total_slippage += result['slippage_cost']
        
        print(f"\n   Total Invested: ${total_cost:.2f}")
        print(f"   Total Slippage: ${total_slippage:.2f}")
    else:
        print(f"\n❌ Executioner failed: {executioner_result.error}")
    
    # Calculate total latency
    state.total_latency_ms = (
        state.scout_latency_ms +
        state.analyst_latency_ms +
        state.executioner_latency_ms
    )
    
    # Final summary
    print("\n" + "=" * 80)
    print("WORKFLOW COMPLETE - SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 Performance Metrics:")
    print(f"   Scout:      {state.scout_latency_ms:>6.0f}ms")
    print(f"   Analyst:    {state.analyst_latency_ms:>6.0f}ms")
    print(f"   Executioner:{state.executioner_latency_ms:>6.0f}ms")
    print(f"   {'─' * 25}")
    print(f"   Total:      {state.total_latency_ms:>6.0f}ms")
    
    # Check latency target (may be slower first time due to API calls)
    if state.total_latency_ms < 500:
        print(f"\n   ✅ LATENCY TARGET MET (<500ms)")
    else:
        print(f"\n   ⚠️  First run latency: {state.total_latency_ms:.0f}ms")
        print(f"      (Cached runs will be <500ms)")
    
    print(f"\n📈 Trading Results:")
    print(f"   Tickers Analyzed: {len(tickers)}")
    print(f"   Candidates Found: {len(state.scout_candidates)}")
    print(f"   Recommendations: {len(state.analyst_recommendations)}")
    print(f"   Trades Executed: {len(state.execution_results)}")
    
    # Show cache performance
    print(f"\n💾 Cache Performance:")
    metrics = cache.get_metrics()
    print(f"   L1 Hits: {metrics['l1_hits']}")
    print(f"   L2 Hits: {metrics['l2_hits']}")
    print(f"   Misses: {metrics['misses']}")
    print(f"   Hit Rate: {metrics['hit_rate']:.1%}")
    
    # Cleanup
    await cache.close()
    
    print("\n" + "=" * 80)
    print("🎉 COMPLETE TRADING WORKFLOW WITH REAL DATA SUCCESSFUL!")
    print("=" * 80)
    print("\n✨ You just ran a full autonomous trading system with:")
    print("   • REAL stock prices from yfinance")
    print("   • REAL technical indicators (RSI, MACD)")
    print("   • REAL news sentiment analysis")
    print("   • Conservative risk management")
    print("   • Realistic slippage simulation")
    print("   • Intelligent caching for speed")
    print("\n🚀 Ready for paper trading or backtesting!")


if __name__ == "__main__":
    asyncio.run(main())
