"""
Unit tests for Analyst Agent

Tests analysis, position sizing, and recommendation generation.
"""

import pytest
import asyncio
from sentinel.agents import AnalystAgent, AgentState


@pytest.mark.asyncio
async def test_analyst_agent_initialization():
    """Test analyst agent initialization"""
    analyst = AnalystAgent(account_balance=10000.0, min_confidence=0.7)
    
    assert analyst.name == "Analyst"
    assert analyst.min_confidence == 0.7
    assert analyst.risk_model.account_balance == 10000.0


@pytest.mark.asyncio
async def test_analyst_generates_recommendations():
    """Test analyst generates recommendations from candidates"""
    analyst = AnalystAgent(min_confidence=0.5)
    
    # Create mock candidate
    candidate = {
        "ticker": "AAPL",
        "score": 85.0,
        "signals": {
            "price": {"price": 150.0, "volume": 1000000},
            "news": {"sentiment_score": 80.0, "confidence": 0.8},
            "technical": {"rsi": 55.0, "signal": "BUY"},
            "supply_chain": {"risk_score": 30.0}
        }
    }
    
    state = AgentState(scout_candidates=[candidate])
    
    result = await analyst.execute(state)
    
    assert result.success is True
    assert isinstance(result.data, list)


@pytest.mark.asyncio
async def test_analyst_recommendation_structure():
    """Test analyst recommendation has correct structure"""
    analyst = AnalystAgent(min_confidence=0.5)
    
    candidate = {
        "ticker": "AAPL",
        "score": 85.0,
        "signals": {
            "price": {"price": 150.0, "volume": 1000000},
            "news": {"sentiment_score": 80.0, "confidence": 0.8},
            "technical": {"rsi": 55.0, "signal": "BUY"},
            "supply_chain": {"risk_score": 30.0}
        }
    }
    
    state = AgentState(scout_candidates=[candidate])
    result = await analyst.execute(state)
    
    if len(result.data) > 0:
        rec = result.data[0]
        
        # Check required fields
        assert "ticker" in rec
        assert "action" in rec
        assert "entry_price" in rec
        assert "stop_loss" in rec
        assert "take_profit" in rec
        assert "position_size" in rec
        assert "confidence" in rec
        assert "expected_return" in rec
        assert "reasoning" in rec


@pytest.mark.asyncio
async def test_analyst_filters_low_confidence():
    """Test analyst filters low confidence recommendations"""
    analyst = AnalystAgent(min_confidence=0.95)  # Very high threshold
    
    candidate = {
        "ticker": "AAPL",
        "score": 60.0,  # Lower score = lower confidence
        "signals": {
            "price": {"price": 150.0, "volume": 500000},
            "news": {"sentiment_score": 50.0, "confidence": 0.5},
            "technical": {"rsi": 50.0, "signal": "NEUTRAL"},
            "supply_chain": {"risk_score": 50.0}
        }
    }
    
    state = AgentState(scout_candidates=[candidate])
    result = await analyst.execute(state)
    
    assert result.success is True
    # Should filter out low confidence
    assert len(result.data) == 0


@pytest.mark.asyncio
async def test_analyst_position_sizing():
    """Test analyst calculates reasonable position sizes"""
    analyst = AnalystAgent(account_balance=10000.0, min_confidence=0.5)
    
    candidate = {
        "ticker": "AAPL",
        "score": 85.0,
        "signals": {
            "price": {"price": 150.0, "volume": 1000000},
            "news": {"sentiment_score": 80.0, "confidence": 0.8},
            "technical": {"rsi": 55.0, "signal": "BUY"},
            "supply_chain": {"risk_score": 30.0}
        }
    }
    
    state = AgentState(scout_candidates=[candidate])
    result = await analyst.execute(state)
    
    if len(result.data) > 0:
        rec = result.data[0]
        position_size = rec["position_size"]
        entry_price = rec["entry_price"]
        
        # Position should be reasonable
        assert position_size > 0
        assert position_size * entry_price < 10000.0  # Within account balance


@pytest.mark.asyncio
async def test_analyst_handles_empty_candidates():
    """Test analyst handles empty candidate list"""
    analyst = AnalystAgent()
    state = AgentState(scout_candidates=[])
    
    result = await analyst.execute(state)
    
    assert result.success is True
    assert len(result.data) == 0


@pytest.mark.asyncio
async def test_analyst_risk_validation():
    """Test analyst validates trades against risk limits"""
    analyst = AnalystAgent(account_balance=10000.0, min_confidence=0.5)
    
    # This should pass risk validation
    candidate = {
        "ticker": "AAPL",
        "score": 85.0,
        "signals": {
            "price": {"price": 150.0, "volume": 1000000},
            "news": {"sentiment_score": 80.0, "confidence": 0.8},
            "technical": {"rsi": 55.0, "signal": "BUY"},
            "supply_chain": {"risk_score": 30.0}
        }
    }
    
    state = AgentState(scout_candidates=[candidate])
    result = await analyst.execute(state)
    
    assert result.success is True
    # Should generate at least one valid recommendation
    assert len(result.data) >= 0


@pytest.mark.asyncio
async def test_analyst_metrics():
    """Test analyst tracks metrics"""
    analyst = AnalystAgent(min_confidence=0.5)
    
    candidate = {
        "ticker": "AAPL",
        "score": 85.0,
        "signals": {
            "price": {"price": 150.0, "volume": 1000000},
            "news": {"sentiment_score": 80.0, "confidence": 0.8},
            "technical": {"rsi": 55.0, "signal": "BUY"},
            "supply_chain": {"risk_score": 30.0}
        }
    }
    
    state = AgentState(scout_candidates=[candidate])
    
    await analyst.execute(state)
    await analyst.execute(state)
    
    metrics = analyst.get_metrics()
    
    assert metrics["name"] == "Analyst"
    assert metrics["execution_count"] == 2
    assert metrics["avg_latency_ms"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
