"""Fractional order quantities must be rejected.

Shares in this market model are whole units, so a fractional quantity
is not executable. It currently passes validation.
"""

from services.broker_engine import execute_order


def test_fractional_quantity_rejected():
    result = execute_order(
        user_id="test", ticker="TCS.NS", side="BUY",
        quantity=1.5, current_price=3500.0,
    )
    assert result["success"] is False
    assert "whole" in result["message"].lower() or "integer" in result["message"].lower()
