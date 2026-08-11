"""
Trade Request Validation — Unit Tests

Covers the fix for a cash-minting bug: TradeExecuteRequest previously
accepted negative quantity/limit_price, letting a BUY with a negative
limit price *increase* the caller's cash balance instead of debiting it.
"""

import pytest
from pydantic import ValidationError

from backend.routers.trade import TradeExecuteRequest, TradeRequest


class TestTradeExecuteRequestValidation:
    def test_rejects_zero_quantity(self):
        with pytest.raises(ValidationError):
            TradeExecuteRequest(user_id="u", symbol="TCS", action="BUY", quantity=0)

    def test_rejects_negative_quantity(self):
        with pytest.raises(ValidationError):
            TradeExecuteRequest(user_id="u", symbol="TCS", action="BUY", quantity=-5)

    def test_rejects_negative_limit_price(self):
        with pytest.raises(ValidationError):
            TradeExecuteRequest(
                user_id="u", symbol="TCS", action="BUY", quantity=1, limit_price=-100
            )

    def test_rejects_zero_limit_price(self):
        with pytest.raises(ValidationError):
            TradeExecuteRequest(
                user_id="u", symbol="TCS", action="BUY", quantity=1, limit_price=0
            )

    def test_accepts_valid_values(self):
        req = TradeExecuteRequest(
            user_id="u", symbol="TCS", action="BUY", quantity=1, limit_price=100.0
        )
        assert req.quantity == 1
        assert req.limit_price == 100.0

    def test_limit_price_defaults_to_none_for_market_orders(self):
        req = TradeExecuteRequest(user_id="u", symbol="TCS", action="BUY", quantity=1)
        assert req.limit_price is None


class TestTradeRequestValidation:
    def test_rejects_non_positive_quantity(self):
        with pytest.raises(ValidationError):
            TradeRequest(user_id="u", symbol="TCS", action="BUY", quantity=0)

    def test_accepts_positive_quantity(self):
        req = TradeRequest(user_id="u", symbol="TCS", action="BUY", quantity=5)
        assert req.quantity == 5
