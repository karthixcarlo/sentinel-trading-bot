"""
Unit tests for Trading Orchestrator

Tests end-to-end workflow coordination and agent integration.
"""

import pytest
import asyncio
from sentinel.orchestrator import TradingOrchestrator
from sentinel.circuit_breaker import CircuitBreaker


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization"""
    orchestrator = TradingOrchestrator(account_balance=10000.0)
    
    assert orchestrator.scout is not None
    assert orchestrator.analyst is not None
    assert orchestrator.executioner is not None


@pytest.mark.asyncio
async def test_orchestrator_complete_workflow():
    """Test orchestrator executes complete workflow"""
    orchestrator = TradingOrchestrator(account_balance=10000.0)
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    state = await orchestrator.execute_workflow(tickers)
    
    assert state is not None
    assert state.tickers == tickers
    assert state.total_latency_ms > 0


@pytest.mark.asyncio
async def test_orchestrator_scout_phase():
    """Test orchestrator scout phase"""
    orchestrator = TradingOrchestrator()
    
    tickers = ["AAPL", "MSFT"]
    state = await orchestrator.execute_workflow(tickers)
    
    # Scout should have executed
    assert state.scout_latency_ms > 0
    assert isinstance(state.scout_candidates, list)


@pytest.mark.asyncio
async def test_orchestrator_analyst_phase():
    """Test orchestrator analyst phase"""
    orchestrator = TradingOrchestrator()
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    state = await orchestrator.execute_workflow(tickers)
    
    # If scout found candidates, analyst should have executed
    if len(state.scout_candidates) > 0:
        assert state.analyst_latency_ms > 0
        assert isinstance(state.analyst_recommendations, list)


@pytest.mark.asyncio
async def test_orchestrator_executioner_phase():
    """Test orchestrator executioner phase"""
    orchestrator = TradingOrchestrator()
    
    tickers = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    state = await orchestrator.execute_workflow(tickers)
    
    # If analyst generated recommendations, executioner should have executed
    if len(state.analyst_recommendations) > 0:
        assert state.executioner_latency_ms > 0
        assert isinstance(state.execution_results, list)


@pytest.mark.asyncio
async def test_orchestrator_empty_tickers():
    """Test orchestrator handles empty ticker list"""
    orchestrator = TradingOrchestrator()
    
    state = await orchestrator.execute_workflow([])
    
    assert state.total_latency_ms > 0
    assert len(state.scout_candidates) == 0


@pytest.mark.asyncio
async def test_orchestrator_with_circuit_breaker():
    """Test orchestrator with circuit breaker"""
    breaker = CircuitBreaker(
        failure_threshold=5,
        state_file=":memory:"
    )
    
    orchestrator = TradingOrchestrator(circuit_breaker=breaker)
    
    tickers = ["AAPL"]
    state = await orchestrator.execute_workflow(tickers)
    
    # Should execute normally with closed circuit
    assert state.total_latency_ms > 0


@pytest.mark.asyncio
async def test_orchestrator_metrics():
    """Test orchestrator provides agent metrics"""
    orchestrator = TradingOrchestrator()
    
    # Run workflow
    await orchestrator.execute_workflow(["AAPL", "MSFT"])
    
    metrics = orchestrator.get_metrics()
    
    assert "scout" in metrics
    assert "analyst" in metrics
    assert "executioner" in metrics
    
    # Each agent should have metrics
    assert metrics["scout"]["execution_count"] > 0
    assert metrics["analyst"]["execution_count"] > 0
    assert metrics["executioner"]["execution_count"] > 0


@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """Test orchestrator handles errors gracefully"""
    orchestrator = TradingOrchestrator()
    
    # Even with potential errors, should complete
    state = await orchestrator.execute_workflow(["AAPL"])
    
    assert state is not None
    assert isinstance(state.errors, list)


@pytest.mark.asyncio
async def test_orchestrator_latency_target():
    """Test orchestrator meets latency target"""
    orchestrator = TradingOrchestrator()
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    state = await orchestrator.execute_workflow(tickers)
    
    # Should meet <500ms target (with mock data)
    assert state.total_latency_ms < 500, f"Latency {state.total_latency_ms}ms exceeds 500ms target"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
