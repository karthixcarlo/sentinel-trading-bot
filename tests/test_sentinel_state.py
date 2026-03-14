"""
Sentinel State — Unit Tests

Tests for the shared LangGraph state schema and initial state factory.
"""

from agents.sentinel_state import create_initial_state, SentinelState


def test_create_initial_state_returns_dict():
    state = create_initial_state()
    assert isinstance(state, dict)


def test_initial_state_has_required_keys():
    state = create_initial_state()
    required_keys = [
        "messages", "current_ticker", "market_data", "analyst_signal",
        "risk_approval", "trade_status", "next_agent", "iteration_count",
        "errors", "timestamp", "portfolio_snapshot", "user_id",
        "user_settings", "broadcast_callback",
    ]
    for key in required_keys:
        assert key in state, f"Missing key: {key}"


def test_initial_state_defaults():
    state = create_initial_state()
    assert state["messages"] == []
    assert state["current_ticker"] == ""
    assert state["risk_approval"] is False
    assert state["trade_status"] == "PENDING"
    assert state["next_agent"] == "scout"
    assert state["iteration_count"] == 0
    assert state["errors"] == []
    assert state["user_id"] == "demo_user"
    assert state["user_settings"] == {}
    assert state["broadcast_callback"] is None


def test_initial_state_timestamp_is_iso():
    state = create_initial_state()
    # ISO format: YYYY-MM-DDTHH:MM:SS
    assert "T" in state["timestamp"]
    assert len(state["timestamp"]) >= 19
