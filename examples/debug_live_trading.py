"""
Debug Live Trading Workflow

Shows detailed output of what happened during execution.
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
from sentinel.config import ALPACA_API_KEY, ALPACA_SECRET_KEY

# Set logging to DEBUG to see everything
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Debug workflow with detailed logging"""
    print("=" * 80)
    print("🔍 DEBUG: Live Paper Trading Workflow")
    print("=" * 80)
    
    # Initialize
    cache = CacheManager(db_path=":memory:")
    await cache.initialize()
    
    breaker = CircuitBreaker(failure_threshold=3, state_file=":memory:")
    
    alpaca_client = AlpacaClient(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=True
    )
    
    account = await alpaca_client.get_account()
    print(f"\n💰 Account Balance: ${account['cash']:,.2f}")
    
    paper_executor = PaperTradingExecutor(alpaca_client)
    provider_factory = ProviderFactory(use_mock=False, cache_manager=cache)
    
    # Initialize agents
    scout = ScoutAgent(circuit_breaker=breaker, min_score=50.0)  # Lower threshold
    scout.price_provider = provider_factory.get_price_provider()
    scout.news_provider = provider_factory.get_news_provider()
    scout.technical_provider = provider_factory.get_technical_provider()
    scout.supply_chain_provider = provider_factory.get_supply_chain_provider()
    
    analyst = AnalystAgent(
        circuit_breaker=breaker,
        account_balance=account['cash'],
        min_confidence=0.5  # Lower threshold
    )
    
    # Test with fewer tickers
    tickers = ["AAPL", "MSFT"]
    print(f"\n📊 Analyzing: {', '.join(tickers)}")
    
    state = AgentState(tickers=tickers)
    
    # SCOUT
    print("\n" + "=" * 80)
    print("PHASE 1: SCOUT")
    print("=" * 80)
    
    scout_result = await scout.execute(state)
    
    if scout_result.success:
        state.scout_candidates = scout_result.data
        print(f"\n✅ Scout found {len(state.scout_candidates)} candidates")
        
        for candidate in state.scout_candidates:
            print(f"\n  {candidate['ticker']}:")
            print(f"    Score: {candidate['score']:.1f}/100")
            print(f"    Price: ${candidate['signals']['price']['price']:.2f}")
            print(f"    RSI: {candidate['signals']['technical']['rsi']:.1f}")
            print(f"    Signal: {candidate['signals']['technical']['signal']}")
            print(f"    Sentiment: {candidate['signals']['news']['sentiment_score']:.1f}/100")
    else:
        print(f"❌ Scout failed: {scout_result.error}")
        await cache.close()
        return
    
    if not state.scout_candidates:
        print("\n⚠️  No candidates found - scores too low")
        await cache.close()
        return
    
    # ANALYST
    print("\n" + "=" * 80)
    print("PHASE 2: ANALYST")
    print("=" * 80)
    
    analyst_result = await analyst.execute(state)
    
    if analyst_result.success:
        state.analyst_recommendations = analyst_result.data
        print(f"\n✅ Analyst generated {len(state.analyst_recommendations)} recommendations")
        
        for rec in state.analyst_recommendations:
            print(f"\n  {rec['ticker']}:")
            print(f"    Action: {rec['action']}")
            print(f"    Entry: ${rec['entry_price']:.2f}")
            print(f"    Position: {rec['position_size']} shares")
            print(f"    Confidence: {rec['confidence']:.2%}")
            print(f"    Expected Return: {rec['expected_return']:.2%}")
            print(f"    Reasoning: {rec['reasoning']}")
    else:
        print(f"❌ Analyst failed: {analyst_result.error}")
        await cache.close()
        return
    
    if not state.analyst_recommendations:
        print("\n⚠️  No recommendations - filtered by confidence or risk model")
        await cache.close()
        return
    
    # EXECUTIONER
    print("\n" + "=" * 80)
    print("PHASE 3: EXECUTIONER - SUBMITTING TO ALPACA")
    print("=" * 80)
    
    for rec in state.analyst_recommendations:
        print(f"\n📤 Submitting {rec['action']} order for {rec['ticker']}...")
        print(f"   Quantity: {rec['position_size']} shares")
        print(f"   Expected price: ${rec['entry_price']:.2f}")
        
        try:
            result = await paper_executor.execute_trade(rec)
            
            print(f"\n   Result:")
            print(f"   Status: {result['status']}")
            if result.get('order_id'):
                print(f"   Order ID: {result['order_id']}")
                print(f"   Filled: {result['filled_qty']}/{result['intended_qty']}")
                print(f"   Fill Price: ${result.get('avg_fill_price', 0):.2f}")
            if result.get('error'):
                print(f"   Error: {result['error']}")
        
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Check positions
    print("\n" + "=" * 80)
    print("FINAL PORTFOLIO")
    print("=" * 80)
    
    portfolio = PortfolioManager(alpaca_client)
    positions = await portfolio.get_positions()
    
    if positions:
        print(f"\n✅ {len(positions)} positions:")
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
    else:
        print("\n⚠️  No positions (orders may have been rejected)")
    
    await cache.close()
    
    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
