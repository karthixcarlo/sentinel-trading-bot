"""
Unit tests for Scout Agent

Tests signal collection, candidate filtering, and scoring logic.
"""

import pytest
import asyncio
from sentinel.agents import ScoutAgent, AgentState


@pytest.mark.asyncio
async def test_scout_agent_initialization():
    """Test scout agent initialization"""
    scout = ScoutAgent(min_score=70.0)
    
    assert scout.name == "Scout"
    assert scout.min_score == 70.0
    assert scout.execution_count == 0


@pytest.mark.asyncio
async def test_scout_finds_candidates():
    """Test scout finds candidates above threshold"""
    scout = ScoutAgent(min_score=60.0)
    state = AgentState(tickers=["AAPL", "MSFT", "GOOGL"])
    
    result = await scout.execute(state)
    
    assert result.success is True
    assert isinstance(result.data, list)
    assert len(result.data) > 0  # Should find at least some candidates
    assert result.latency_ms > 0


@pytest.mark.asyncio
async def test_scout_candidate_structure():
    """Test scout candidate has correct structure"""
    scout = ScoutAgent(min_score=50.0)
    state = AgentState(tickers=["AAPL"])
    
    result = await scout.execute(state)
    
    assert result.success is True
    candidates = result.data
    
    if len(candidates) > 0:
        candidate = candidates[0]
        assert "ticker" in candidate
        assert "score" in candidate
        assert "signals" in candidate
        assert "timestamp" in candidate
        
        # Check signals structure
        signals = candidate["signals"]
        assert "price" in signals
        assert "news" in signals
        assert "technical" in signals
        assert "supply_chain" in signals


@pytest.mark.asyncio
async def test_scout_filters_low_scores():
    """Test scout filters candidates below threshold"""
    scout = ScoutAgent(min_score=95.0)  # Very high threshold
    state = AgentState(tickers=["AAPL", "MSFT"])
    
    result = await scout.execute(state)
    
    assert result.success is True
    # With high threshold, should filter out most/all candidates
    assert len(result.data) <= 1  # Might get lucky with one


@pytest.mark.asyncio
async def test_scout_sorts_by_score():
    """Test scout sorts candidates by score (highest first)"""
    scout = ScoutAgent(min_score=50.0)
    state = AgentState(tickers=["AAPL", "MSFT", "GOOGL", "TSLA"])
    
    result = await scout.execute(state)
    
    assert result.success is True
    candidates = result.data
    
    if len(candidates) > 1:
        # Check descending order
        for i in range(len(candidates) - 1):
            assert candidates[i]["score"] >= candidates[i + 1]["score"]


@pytest.mark.asyncio
async def test_scout_handles_empty_tickers():
    """Test scout handles empty ticker list"""
    scout = ScoutAgent()
    state = AgentState(tickers=[])
    
    result = await scout.execute(state)
    
    assert result.success is True
    assert len(result.data) == 0


@pytest.mark.asyncio
async def test_scout_parallel_collection():
    """Test scout collects signals in parallel (fast)"""
    scout = ScoutAgent()
    state = AgentState(tickers=["AAPL", "MSFT", "GOOGL"])
    
    result = await scout.execute(state)
    
    assert result.success is True
    # Should be fast due to parallel collection
    # 3 tickers * ~100ms sequential = 300ms
    # Parallel should be ~150ms
    assert result.latency_ms < 300


@pytest.mark.asyncio
async def test_scout_metrics():
    """Test scout tracks metrics"""
    scout = ScoutAgent()
    state = AgentState(tickers=["AAPL"])
    
    await scout.execute(state)
    await scout.execute(state)
    
    metrics = scout.get_metrics()
    
    assert metrics["name"] == "Scout"
    assert metrics["execution_count"] == 2
    assert metrics["avg_latency_ms"] > 0


@pytest.mark.asyncio
async def test_scout_with_circuit_breaker():
    """Test scout respects circuit breaker"""
    from sentinel.circuit_breaker import CircuitBreaker
    
    breaker = CircuitBreaker(
        failure_threshold=1,
        state_file=":memory:"
    )
    
    # Open circuit
    await breaker.record_failure("Test failure")
    
    scout = ScoutAgent(circuit_breaker=breaker)
    state = AgentState(tickers=["AAPL"])
    
    result = await scout.execute(state)
    
    # Should be blocked by circuit breaker
    assert result.success is False
    assert "circuit breaker" in result.error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
