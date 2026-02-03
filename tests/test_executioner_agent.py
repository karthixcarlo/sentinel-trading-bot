"""
Unit tests for Executioner Agent

Tests trade execution, slippage simulation, and validation.
"""

import pytest
import asyncio
from sentinel.agents import ExecutionerAgent, AgentState
from sentinel.slippage_simulator import MarketCondition


@pytest.mark.asyncio
async def test_executioner_agent_initialization():
    """Test executioner agent initialization"""
    executioner = ExecutionerAgent()
    
    assert executioner.name == "Executioner"
    assert executioner.slippage_simulator is not None


@pytest.mark.asyncio
async def test_executioner_executes_trades():
    """Test executioner executes trade recommendations"""
    executioner = ExecutionerAgent()
    
    # Create mock recommendation
    recommendation = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_price": 150.0,
        "stop_loss": 147.0,
        "take_profit": 156.0,
        "position_size": 50,
        "confidence": 0.8
    }
    
    state = AgentState(analyst_recommendations=[recommendation])
    
    result = await executioner.execute(state)
    
    assert result.success is True
    assert isinstance(result.data, list)
    assert len(result.data) > 0


@pytest.mark.asyncio
async def test_executioner_result_structure():
    """Test executioner result has correct structure"""
    executioner = ExecutionerAgent()
    
    recommendation = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_price": 150.0,
        "stop_loss": 147.0,
        "take_profit": 156.0,
        "position_size": 50,
        "confidence": 0.8
    }
    
    state = AgentState(analyst_recommendations=[recommendation])
    result = await executioner.execute(state)
    
    assert result.success is True
    
    if len(result.data) > 0:
        execution = result.data[0]
        
        # Check required fields
        assert "status" in execution
        assert "ticker" in execution
        assert "action" in execution
        assert "avg_fill_price" in execution
        assert "filled_qty" in execution
        assert "slippage_pct" in execution
        assert "slippage_cost" in execution
        assert "total_cost" in execution


@pytest.mark.asyncio
async def test_executioner_applies_slippage():
    """Test executioner applies slippage to fills"""
    executioner = ExecutionerAgent()
    
    recommendation = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_price": 150.0,
        "stop_loss": 147.0,
        "take_profit": 156.0,
        "position_size": 100,
        "confidence": 0.8
    }
    
    state = AgentState(analyst_recommendations=[recommendation])
    result = await executioner.execute(state)
    
    assert result.success is True
    
    if len(result.data) > 0:
        execution = result.data[0]
        
        # Should have slippage
        assert execution["slippage_pct"] > 0
        assert execution["slippage_cost"] > 0
        
        # Fill price should be different from intended
        assert execution["avg_fill_price"] != recommendation["entry_price"]


@pytest.mark.asyncio
async def test_executioner_handles_empty_recommendations():
    """Test executioner handles empty recommendation list"""
    executioner = ExecutionerAgent()
    state = AgentState(analyst_recommendations=[])
    
    result = await executioner.execute(state)
    
    assert result.success is True
    assert len(result.data) == 0


@pytest.mark.asyncio
async def test_executioner_market_conditions():
    """Test executioner respects market conditions"""
    # Normal conditions
    executioner_normal = ExecutionerAgent(market_condition=MarketCondition.NORMAL)
    
    # Volatile conditions
    executioner_volatile = ExecutionerAgent(market_condition=MarketCondition.VOLATILE)
    
    recommendation = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_price": 150.0,
        "stop_loss": 147.0,
        "take_profit": 156.0,
        "position_size": 100,
        "confidence": 0.8
    }
    
    state_normal = AgentState(analyst_recommendations=[recommendation])
    state_volatile = AgentState(analyst_recommendations=[recommendation.copy()])
    
    result_normal = await executioner_normal.execute(state_normal)
    result_volatile = await executioner_volatile.execute(state_volatile)
    
    # Both should succeed
    assert result_normal.success is True
    assert result_volatile.success is True


@pytest.mark.asyncio
async def test_executioner_multiple_trades():
    """Test executioner handles multiple recommendations"""
    executioner = ExecutionerAgent()
    
    recommendations = [
        {
            "ticker": "AAPL",
            "action": "BUY",
            "entry_price": 150.0,
            "stop_loss": 147.0,
            "take_profit": 156.0,
            "position_size": 50,
            "confidence": 0.8
        },
        {
            "ticker": "MSFT",
            "action": "BUY",
            "entry_price": 380.0,
            "stop_loss": 372.0,
            "take_profit": 395.0,
            "position_size": 25,
            "confidence": 0.75
        }
    ]
    
    state = AgentState(analyst_recommendations=recommendations)
    result = await executioner.execute(state)
    
    assert result.success is True
    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_executioner_metrics():
    """Test executioner tracks metrics"""
    executioner = ExecutionerAgent()
    
    recommendation = {
        "ticker": "AAPL",
        "action": "BUY",
        "entry_price": 150.0,
        "stop_loss": 147.0,
        "take_profit": 156.0,
        "position_size": 50,
        "confidence": 0.8
    }
    
    state = AgentState(analyst_recommendations=[recommendation])
    
    await executioner.execute(state)
    await executioner.execute(state)
    
    metrics = executioner.get_metrics()
    
    assert metrics["name"] == "Executioner"
    assert metrics["execution_count"] == 2
    assert metrics["avg_latency_ms"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
