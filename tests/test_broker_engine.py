"""
Broker Engine — Unit Tests

Tests for input validation in the trade execution engine.
"""

import pytest
from broker_engine import execute_order


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
