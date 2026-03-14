"""
Agent Service — Unit Tests

Tests for AgentService configuration, status reporting, and portfolio management.
"""

import json
import pytest
from agents.agent_service import AgentService, AgentStatus, Portfolio, Position, SECTOR_STOCKS


class TestAgentStatus:
    def test_status_values(self):
        assert AgentStatus.IDLE.value == "idle"
        assert AgentStatus.RUNNING.value == "running"
        assert AgentStatus.PAUSED.value == "paused"
        assert AgentStatus.STOPPED.value == "stopped"


class TestPortfolio:
    def test_default_cash(self):
        p = Portfolio(user_id="test")
        assert p.cash == 100000.0
        assert p.positions == {}

    def test_total_value_cash_only(self):
        p = Portfolio(user_id="test", cash=50000.0)
        assert p.total_value() == 50000.0

    def test_total_value_with_positions(self):
        p = Portfolio(user_id="test", cash=50000.0)
        p.positions["TCS.NS"] = Position(
            symbol="TCS.NS", quantity=10, average_price=3500.0
        )
        # current_price == average_price in the Position dataclass
        assert p.total_value() == 50000.0 + (10 * 3500.0)

    def test_to_dict(self):
        p = Portfolio(user_id="test", cash=100000.0)
        d = p.to_dict()
        assert d["cash"] == 100000.0
        assert d["positions"] == {}
        assert d["total_value"] == 100000.0


class TestPosition:
    def test_market_value(self):
        pos = Position(symbol="INFY.NS", quantity=5, average_price=1500.0)
        assert pos.market_value == 7500.0

    def test_unrealized_pnl_zero(self):
        pos = Position(symbol="INFY.NS", quantity=5, average_price=1500.0)
        # current_price == average_price so PnL is 0
        assert pos.unrealized_pnl == 0.0


class TestAgentServiceConfig:
    def test_default_config(self):
        svc = AgentService(user_id="test_ci")
        assert svc.risk_appetite == "Moderate"
        assert svc.max_position_pct == 0.10
        assert svc.allowed_sectors == list(SECTOR_STOCKS.keys())

    def test_update_config(self):
        svc = AgentService(user_id="test_ci")
        svc.update_config({
            "risk_appetite": "Aggressive",
            "max_position_size": 25,
            "allowed_sectors": ["IT", "Banking"],
        })
        assert svc.risk_appetite == "Aggressive"
        assert svc.max_position_pct == 0.25
        assert svc.allowed_sectors == ["IT", "Banking"]

    def test_update_config_empty_sectors_defaults(self):
        svc = AgentService(user_id="test_ci")
        svc.update_config({"allowed_sectors": []})
        assert svc.allowed_sectors == list(SECTOR_STOCKS.keys())

    def test_get_status_idle(self):
        svc = AgentService(user_id="test_ci")
        status = svc.get_status()
        assert status["running"] is False
        assert status["status"] == "idle"
        assert status["start_time"] is None
        assert "portfolio" in status
