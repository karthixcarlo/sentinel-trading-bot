"""
WebSocket Auth — Unit Tests

Covers the fix for /ws/neural-feed silently accepting unauthenticated
connections whenever the client simply omitted the ?token= query param,
even when a JWT secret was configured on the server.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import jwt as pyjwt

from backend.routers import ws as ws_router


def _mock_websocket(token=None):
    mock_ws = MagicMock()
    mock_ws.query_params.get.return_value = token
    mock_ws.close = AsyncMock()
    mock_ws.accept = AsyncMock()
    return mock_ws


class TestWebSocketAuth:
    def test_rejects_missing_token_when_secret_configured(self, monkeypatch):
        monkeypatch.setattr(ws_router, "_JWT_SECRET", "test-secret")
        mock_ws = _mock_websocket(token=None)

        asyncio.run(ws_router.websocket_neural_feed(mock_ws))

        mock_ws.close.assert_awaited_once()
        mock_ws.accept.assert_not_called()

    def test_rejects_invalid_token_when_secret_configured(self, monkeypatch):
        monkeypatch.setattr(ws_router, "_JWT_SECRET", "test-secret")
        bad_token = pyjwt.encode({"sub": "u"}, "wrong-secret", algorithm="HS256")
        mock_ws = _mock_websocket(token=bad_token)

        asyncio.run(ws_router.websocket_neural_feed(mock_ws))

        mock_ws.close.assert_awaited_once()
        mock_ws.accept.assert_not_called()

    def test_allows_missing_token_in_demo_mode(self, monkeypatch):
        # No JWT secret configured at all == demo mode, no real accounts to protect.
        monkeypatch.setattr(ws_router, "_JWT_SECRET", "")
        mock_ws = _mock_websocket(token=None)
        mock_ws.send_json = AsyncMock(side_effect=RuntimeError("stop after accept"))

        asyncio.run(ws_router.websocket_neural_feed(mock_ws))

        mock_ws.accept.assert_awaited_once()
