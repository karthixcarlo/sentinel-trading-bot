"""
Phase 2 Examples - Cache Manager and Circuit Breaker

Demonstrates the new Phase 2 modules in action.
"""

import asyncio
from sentinel import CacheManager, CircuitBreaker, gather_with_timeout, AsyncTimer


async def example_cache_manager():
    """Demonstrate cache manager functionality"""
    print("=" * 60)
    print("EXAMPLE 1: Cache Manager")
    print("=" * 60)
    
    # Create cache manager
    cache = CacheManager(db_path=":memory:", l1_max_size=5)
    await cache.initialize()
    
    # Set some values
    print("\n[1] Setting cache values...")
    await cache.set("ticker:AAPL", {"price": 150.25, "volume": 1000000}, ttl=60)
    await cache.set("ticker:MSFT", {"price": 380.50, "volume": 800000}, ttl=60)
    await cache.set("ticker:GOOGL", {"price": 140.75, "volume": 600000}, ttl=60)
    
    # Get values (L1 hit)
    print("\n[2] Retrieving from cache (L1 hits)...")
    aapl = await cache.get("ticker:AAPL")
    print(f"  AAPL: ${aapl['price']:.2f}")
    
    # Clear L1 and get again (L2 hit)
    print("\n[3] Clearing L1 cache...")
    await cache.l1_cache.clear()
    
    print("\n[4] Retrieving from cache (L2 hit)...")
    msft = await cache.get("ticker:MSFT")
    print(f"  MSFT: ${msft['price']:.2f}")
    
    # Show metrics
    print("\n[5] Cache Metrics:")
    metrics = cache.get_metrics()
    print(f"  L1 Hits: {metrics['l1_hits']}")
    print(f"  L2 Hits: {metrics['l2_hits']}")
    print(f"  Misses: {metrics['misses']}")
    print(f"  Hit Rate: {metrics['hit_rate']:.2%}")
    
    await cache.close()
    print("\n✓ Cache manager demo complete")


async def example_circuit_breaker():
    """Demonstrate circuit breaker functionality"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 2: Circuit Breaker")
    print("=" * 60)
    
    # Create circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=2.0,
        state_file=":memory:"  # Use memory for demo
    )
    
    print("\n[1] Initial state: CLOSED")
    can_execute, reason = await breaker.can_execute()
    print(f"  Can execute: {can_execute} - {reason}")
    
    # Simulate failures
    print("\n[2] Simulating failures...")
    for i in range(3):
        await breaker.record_failure(f"API error {i+1}")
        print(f"  Failure #{i+1} recorded")
    
    # Should be OPEN now
    print("\n[3] After 3 failures: OPEN")
    can_execute, reason = await breaker.can_execute()
    print(f"  Can execute: {can_execute} - {reason}")
    
    # Wait for recovery
    print("\n[4] Waiting for recovery timeout (2s)...")
    await asyncio.sleep(2.1)
    
    # Should transition to HALF_OPEN
    print("\n[5] After timeout: HALF_OPEN")
    can_execute, reason = await breaker.can_execute()
    print(f"  Can execute: {can_execute} - {reason}")
    
    # Successful recovery
    print("\n[6] Recording successful operation...")
    await breaker.record_success()
    
    # Should be CLOSED again
    print("\n[7] After success: CLOSED")
    status = breaker.get_status()
    print(f"  State: {status['state']}")
    print(f"  Total failures: {status['failure_count']}")
    print(f"  Total successes: {status['success_count']}")
    
    print("\n✓ Circuit breaker demo complete")


async def example_async_utils():
    """Demonstrate async utilities"""
    print("\n\n" + "=" * 60)
    print("EXAMPLE 3: Async Utilities")
    print("=" * 60)
    
    # Mock async functions
    async def fetch_price(ticker):
        await asyncio.sleep(0.1)
        return {"ticker": ticker, "price": 150.0}
    
    async def fetch_news(ticker):
        await asyncio.sleep(0.15)
        return {"ticker": ticker, "sentiment": 75.0}
    
    async def fetch_technical(ticker):
        await asyncio.sleep(0.05)
        return {"ticker": ticker, "rsi": 65.0}
    
    # Parallel execution with timeout
    print("\n[1] Parallel signal collection with timeout...")
    async with AsyncTimer() as timer:
        results = await gather_with_timeout(
            fetch_price("AAPL"),
            fetch_news("AAPL"),
            fetch_technical("AAPL"),
            timeout=1.0
        )
    
    print(f"  Collected {len(results)} signals in {timer.elapsed_ms:.0f}ms")
    for i, result in enumerate(results, 1):
        if isinstance(result, dict):
            print(f"  Signal {i}: {list(result.keys())}")
    
    print("\n✓ Async utilities demo complete")


async def main():
    """Run all examples"""
    await example_cache_manager()
    await example_circuit_breaker()
    await example_async_utils()
    
    print("\n" + "=" * 60)
    print("All Phase 2 examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
