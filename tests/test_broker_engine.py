"""
Broker Engine — Unit Tests

Tests for input validation and the atomic trade-execution path (mocked
Supabase client) in the trade execution engine.
"""

from unittest.mock import MagicMock

import pytest
from services import broker_engine
from services.broker_engine import execute_order


class TestBrokerValidation:
    def test_invalid_side_rejected(self):
        result = execute_order(
            user_id="test", ticker="TCS.NS", side="HOLD",
            quantity=1, current_price=3500.0,
        )
        assert result["success"] is False
        assert "Invalid side" in result["message"]

    def test_zero_quantity_rejected(self):
        result = execute_order(
            user_id="test", ticker="TCS.NS", side="BUY",
            quantity=0, current_price=3500.0,
        )
        assert result["success"] is False
        assert "quantity" in result["message"].lower() or "Quantity" in result["message"]

    def test_negative_price_rejected(self):
        result = execute_order(
            user_id="test", ticker="TCS.NS", side="BUY",
            quantity=1, current_price=-100.0,
        )
        assert result["success"] is False
        assert "price" in result["message"].lower() or "Price" in result["message"]

    def test_negative_quantity_rejected(self):
        result = execute_order(
            user_id="test", ticker="TCS.NS", side="SELL",
            quantity=-5, current_price=3500.0,
        )
        assert result["success"] is False

    def test_fractional_quantity_rejected(self):
        result = execute_order(
            user_id="test", ticker="TCS.NS", side="BUY",
            quantity=1.5, current_price=3500.0,
        )
        assert result["success"] is False
        assert "whole number" in result["message"]


def _mock_client(rpc_return=None, rpc_side_effect=None):
    client = MagicMock()
    rpc_result = MagicMock()
    if rpc_side_effect is not None:
        rpc_result.execute.side_effect = rpc_side_effect
    else:
        rpc_result.execute.return_value = MagicMock(data=rpc_return)
    client.rpc.return_value = rpc_result
    return client


class TestExecuteOrderAtomic:
    """
    Verifies execute_order() delegates the actual balance check + write to
    the execute_trade_atomic() Postgres RPC (see supabase_setup.sql) instead
    of doing a non-atomic read-then-write from Python, and that each known
    RPC failure mode maps back to the existing friendly message contract.
    """

    def test_buy_success_calls_rpc_with_correct_params(self, monkeypatch):
        client = _mock_client(rpc_return=[{"new_cash_balance": 97000.0, "transaction_id": "tx-1"}])
        monkeypatch.setattr(broker_engine, "_get_client", lambda: client)
        monkeypatch.setattr(broker_engine, "_log_agent_action", lambda *a, **k: None)

        result = execute_order(user_id="user-1", ticker="TCS.NS", side="BUY", quantity=10, current_price=300.0)

        assert result["success"] is True
        assert result["order"]["cash_after"] == 97000.0
        client.rpc.assert_called_once()
        rpc_name, rpc_args = client.rpc.call_args[0]
        assert rpc_name == "execute_trade_atomic"
        assert rpc_args["p_user_id"] == "user-1"
        assert rpc_args["p_side"] == "BUY"
        assert rpc_args["p_qty"] == 10
        assert rpc_args["p_price"] == 300.0

    def test_sell_success_returns_net_proceeds(self, monkeypatch):
        client = _mock_client(rpc_return=[{"new_cash_balance": 103000.0, "transaction_id": "tx-2"}])
        monkeypatch.setattr(broker_engine, "_get_client", lambda: client)
        monkeypatch.setattr(broker_engine, "_log_agent_action", lambda *a, **k: None)

        result = execute_order(user_id="user-1", ticker="TCS.NS", side="SELL", quantity=10, current_price=300.0)

        assert result["success"] is True
        assert result["order"]["cash_after"] == 103000.0
        assert result["order"]["side"] == "SELL"

    def test_buy_insufficient_funds_returns_friendly_message(self, monkeypatch):
        client = _mock_client(rpc_side_effect=Exception("insufficient_funds"))
        monkeypatch.setattr(broker_engine, "_get_client", lambda: client)
        monkeypatch.setattr(broker_engine, "_get_cash_balance", lambda c, u: 100.0)

        result = execute_order(user_id="user-1", ticker="TCS.NS", side="BUY", quantity=10, current_price=300.0)

        assert result["success"] is False
        assert "Insufficient funds" in result["message"]

    def test_sell_insufficient_shares_returns_friendly_message(self, monkeypatch):
        client = _mock_client(rpc_side_effect=Exception("insufficient_shares"))
        monkeypatch.setattr(broker_engine, "_get_client", lambda: client)
        monkeypatch.setattr(broker_engine, "_get_position_qty", lambda c, u, t: 2.0)

        result = execute_order(user_id="user-1", ticker="TCS.NS", side="SELL", quantity=10, current_price=300.0)

        assert result["success"] is False
        assert "Insufficient holdings" in result["message"]

    def test_portfolio_not_found_returns_friendly_message(self, monkeypatch):
        client = _mock_client(rpc_side_effect=Exception("portfolio_not_found"))
        monkeypatch.setattr(broker_engine, "_get_client", lambda: client)

        result = execute_order(user_id="ghost-user", ticker="TCS.NS", side="BUY", quantity=10, current_price=300.0)

        assert result["success"] is False
        assert "No portfolio found" in result["message"]

    def test_unrecognized_rpc_error_surfaces_as_broker_error(self, monkeypatch):
        client = _mock_client(rpc_side_effect=Exception("some totally unexpected db error"))
        monkeypatch.setattr(broker_engine, "_get_client", lambda: client)

        result = execute_order(user_id="user-1", ticker="TCS.NS", side="BUY", quantity=10, current_price=300.0)

        assert result["success"] is False
        assert "Broker error" in result["message"]
