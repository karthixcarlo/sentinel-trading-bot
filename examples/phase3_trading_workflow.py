"""
Phase 3 Example - Complete Trading Workflow

Demonstrates the full multi-agent trading system from signal collection
to trade execution with <500ms latency target.
"""

import asyncio
import logging
from sentinel.orchestrator import TradingOrchestrator
from sentinel.circuit_breaker import CircuitBreaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_trading_workflow():
    """Demonstrate complete trading workflow"""
    print("=" * 70)
    print("PROJECT SENTINEL - PHASE 3: MULTI-AGENT TRADING WORKFLOW")
    print("=" * 70)
    
    # Initialize circuit breaker
    print("\n[1] Initializing circuit breaker...")
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=60.0,
        state_file="./sentinel_state/circuit_breaker.json"
    )
    print(f"  Circuit breaker state: {breaker.state.name}")
    
    # Initialize orchestrator
    print("\n[2] Initializing trading orchestrator...")
    orchestrator = TradingOrchestrator(
        circuit_breaker=breaker,
        account_balance=10000.0
    )
    print("  ✓ Scout, Analyst, and Executioner agents ready")
    
    # Define tickers to analyze
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
    print(f"\n[3] Starting workflow for {len(tickers)} tickers: {', '.join(tickers)}")
    
    # Execute workflow
    print("\n" + "=" * 70)
    state = await orchestrator.execute_workflow(tickers)
    print("=" * 70)
    
    # Display results
    print("\n" + "=" * 70)
    print("WORKFLOW RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Performance Metrics:")
    print(f"  Scout latency:      {state.scout_latency_ms:>6.0f}ms")
    print(f"  Analyst latency:    {state.analyst_latency_ms:>6.0f}ms")
    print(f"  Executioner latency:{state.executioner_latency_ms:>6.0f}ms")
    print(f"  {'─' * 35}")
    print(f"  Total latency:      {state.total_latency_ms:>6.0f}ms")
    
    # Check latency target
    if state.total_latency_ms < 500:
        print(f"\n  ✅ LATENCY TARGET MET (<500ms)")
    else:
        print(f"\n  ⚠️  Latency target missed (>{state.total_latency_ms:.0f}ms)")
    
    print(f"\n🔍 Scout Results:")
    print(f"  Candidates found: {len(state.scout_candidates)}")
    if state.scout_candidates:
        print(f"  Top candidate: {state.scout_candidates[0]['ticker']} (score={state.scout_candidates[0]['score']:.1f})")
    
    print(f"\n📈 Analyst Results:")
    print(f"  Recommendations: {len(state.analyst_recommendations)}")
    for rec in state.analyst_recommendations:
        print(f"    {rec['action']} {rec['ticker']} @ ${rec['entry_price']:.2f}")
        print(f"      Position: {rec['position_size']} shares")
        print(f"      Confidence: {rec['confidence']:.2f}")
        print(f"      Expected return: {rec['expected_return']:.2%}")
    
    print(f"\n💼 Execution Results:")
    print(f"  Trades executed: {len(state.execution_results)}")
    total_cost = 0
    total_slippage = 0
    
    for result in state.execution_results:
        print(f"    {result['status']}: {result['action']} {result['ticker']}")
        print(f"      Filled: {result['filled_qty']}/{result['intended_qty']} @ ${result['avg_fill_price']:.2f}")
        print(f"      Slippage: {result['slippage_pct']:.3f}% (${result['slippage_cost']:.2f})")
        print(f"      Total cost: ${result['total_cost']:.2f}")
        total_cost += result['total_cost']
        total_slippage += result['slippage_cost']
    
    if state.execution_results:
        print(f"\n  Total invested: ${total_cost:.2f}")
        print(f"  Total slippage: ${total_slippage:.2f}")
    
    # Errors
    if state.errors:
        print(f"\n⚠️  Errors encountered:")
        for error in state.errors:
            print(f"    - {error}")
    
    # Agent metrics
    print(f"\n📊 Agent Metrics:")
    metrics = orchestrator.get_metrics()
    for agent_name, agent_metrics in metrics.items():
        print(f"  {agent_name.capitalize()}:")
        print(f"    Executions: {agent_metrics['execution_count']}")
        print(f"    Avg latency: {agent_metrics['avg_latency_ms']:.0f}ms")
        print(f"    Errors: {agent_metrics['error_count']}")
    
    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE! 🎉")
    print("=" * 70)


async def example_circuit_breaker_protection():
    """Demonstrate circuit breaker protecting the system"""
    print("\n\n" + "=" * 70)
    print("EXAMPLE: CIRCUIT BREAKER PROTECTION")
    print("=" * 70)
    
    # Create breaker with low threshold for demo
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=5.0,
        state_file=":memory:"
    )
    
    orchestrator = TradingOrchestrator(
        circuit_breaker=breaker,
        account_balance=10000.0
    )
    
    print("\n[1] Simulating failures to trigger circuit breaker...")
    
    # Simulate failures
    await breaker.record_failure("Simulated API error 1")
    await breaker.record_failure("Simulated API error 2")
    
    print(f"  Circuit breaker state: {breaker.state.name}")
    
    # Try to execute workflow (should be blocked)
    print("\n[2] Attempting to execute workflow...")
    can_execute, reason = await breaker.can_execute()
    
    if not can_execute:
        print(f"  ❌ Workflow blocked: {reason}")
    
    print("\n[3] Waiting for recovery timeout (5s)...")
    await asyncio.sleep(5.1)
    
    # Should transition to HALF_OPEN
    can_execute, reason = await breaker.can_execute()
    print(f"  Circuit breaker state: {breaker.state.name}")
    print(f"  Can execute: {can_execute}")
    
    # Simulate success to close circuit
    print("\n[4] Recording successful operation...")
    await breaker.record_success()
    print(f"  Circuit breaker state: {breaker.state.name}")
    
    print("\n✅ Circuit breaker protection demonstrated!")


async def main():
    """Run all examples"""
    await example_trading_workflow()
    await example_circuit_breaker_protection()


if __name__ == "__main__":
    asyncio.run(main())
