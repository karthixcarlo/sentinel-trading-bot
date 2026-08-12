"""
Trade Router — Unit Tests

Covers the atomic SQLite demo-trade helper in backend/routers/trade.py.
Uses a real temporary SQLite file (no mocking) since the whole point of
the fix is real transaction/locking behavior.
"""

import importlib


def _fresh_trade_module(tmp_path, monkeypatch):
    """
    Reloads backend.routers.trade with ROOT_DIR patched to a temp dir, so
    each test gets its own isolated sentinel.db instead of touching the
    real one in the repo root.
    """
    import backend.deps as deps
    monkeypatch.setattr(deps, "ROOT_DIR", str(tmp_path))
    import backend.routers.trade as trade
    importlib.reload(trade)
    return trade


class TestDemoExecuteTradeAtomic:
    def test_buy_debits_cash_and_records_transaction(self, tmp_path, monkeypatch):
        trade = _fresh_trade_module(tmp_path, monkeypatch)

        result = trade._demo_execute_trade_atomic("u1", "TCS.NS", "BUY", 10, 100.0)

        assert result["success"] is True
        # 100000 - (1000 gross + 0.3 brokerage)
        assert result["order"]["cash_after"] == 98999.7
        assert trade._demo_get_cash("u1") == 98999.7
        positions = trade._demo_get_positions("u1")
        assert len(positions) == 1
        assert positions[0]["symbol"] == "TCS.NS"
        assert positions[0]["quantity"] == 10

    def test_buy_insufficient_funds_rejected_without_mutating_state(self, tmp_path, monkeypatch):
        trade = _fresh_trade_module(tmp_path, monkeypatch)

        result = trade._demo_execute_trade_atomic("u2", "TCS.NS", "BUY", 100000, 100.0)

        assert result["success"] is False
        assert "Insufficient funds" in result["message"]
        assert trade._demo_get_cash("u2") == 100000.0
        assert trade._demo_get_positions("u2") == []

    def test_sell_without_position_rejected(self, tmp_path, monkeypatch):
        trade = _fresh_trade_module(tmp_path, monkeypatch)

        result = trade._demo_execute_trade_atomic("u3", "TCS.NS", "SELL", 5, 100.0)

        assert result["success"] is False
        assert "Insufficient shares" in result["message"]
        assert trade._demo_get_cash("u3") == 100000.0

    def test_sell_credits_cash_after_buy(self, tmp_path, monkeypatch):
        trade = _fresh_trade_module(tmp_path, monkeypatch)

        trade._demo_execute_trade_atomic("u4", "TCS.NS", "BUY", 10, 100.0)
        result = trade._demo_execute_trade_atomic("u4", "TCS.NS", "SELL", 10, 110.0)

        assert result["success"] is True
        assert trade._demo_get_positions("u4") == []
        # 98999.7 + (1100 gross - 0.33 brokerage)
        assert trade._demo_get_cash("u4") == round(98999.7 + 1100 - 0.33, 2)

    def test_sequential_buys_never_lose_an_update(self, tmp_path, monkeypatch):
        # Simulates what a race would corrupt: many trades against the same
        # user must all be reflected in the final balance, not just some of
        # them (a real concurrent test would need threads; this at least
        # proves the read-check-write sequence is internally consistent
        # across repeated calls against the same connection-per-call design).
        trade = _fresh_trade_module(tmp_path, monkeypatch)

        for _ in range(5):
            result = trade._demo_execute_trade_atomic("u5", "TCS.NS", "BUY", 1, 100.0)
            assert result["success"] is True

        positions = trade._demo_get_positions("u5")
        assert positions[0]["quantity"] == 5
        # 5 buys of 1 share @ 100 with 0.03% brokerage each
        expected_cash = 100000.0
        for _ in range(5):
            expected_cash = round(expected_cash - round(100 + round(100 * 0.0003, 2), 2), 2)
        assert trade._demo_get_cash("u5") == expected_cash
