"""
Backend Auth — Unit Tests

Covers the auth-bypass fix in backend/deps.py: unauthenticated requests and
requests with an unverifiable token must NOT be trusted as a real (or
client-chosen) identity once Supabase/real accounts are configured. Demo
mode (no Supabase configured) must keep working exactly as before.
"""

import asyncio

import jwt as pyjwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from backend import deps


def _creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


class TestGetCurrentUserDemoMode:
    """Supabase not configured — no real accounts exist, permissive fallback is safe."""

    def test_no_credentials_returns_demo_user(self, monkeypatch):
        monkeypatch.setattr(deps._auth_manager, "is_configured", lambda: False)
        result = asyncio.run(deps.get_current_user(credentials=None))
        assert result == "demo_user"

    def test_unsigned_token_trusted_when_no_secret_configured(self, monkeypatch):
        monkeypatch.setattr(deps._auth_manager, "is_configured", lambda: False)
        monkeypatch.setattr(deps, "_JWT_SECRET", "")
        token = pyjwt.encode({"sub": "abc-123"}, "irrelevant", algorithm="HS256")
        result = asyncio.run(deps.get_current_user(credentials=_creds(token)))
        assert result == "abc-123"


class TestGetCurrentUserRealAuthRequired:
    """Supabase IS configured — real accounts exist, must fail closed."""

    def test_missing_credentials_rejected(self, monkeypatch):
        monkeypatch.setattr(deps._auth_manager, "is_configured", lambda: True)
        with pytest.raises(HTTPException) as exc:
            asyncio.run(deps.get_current_user(credentials=None))
        assert exc.value.status_code == 401

    def test_missing_jwt_secret_rejected_even_with_a_token(self, monkeypatch):
        # Regression guard: previously any unsigned token was trusted here,
        # letting a caller impersonate any user by forging {"sub": "<uuid>"}.
        monkeypatch.setattr(deps._auth_manager, "is_configured", lambda: True)
        monkeypatch.setattr(deps, "_JWT_SECRET", "")
        token = pyjwt.encode({"sub": "victim-uuid"}, "whatever", algorithm="HS256")
        with pytest.raises(HTTPException) as exc:
            asyncio.run(deps.get_current_user(credentials=_creds(token)))
        assert exc.value.status_code == 401

    def test_valid_signed_token_accepted(self, monkeypatch):
        monkeypatch.setattr(deps._auth_manager, "is_configured", lambda: True)
        monkeypatch.setattr(deps, "_JWT_SECRET", "test-secret")
        token = pyjwt.encode(
            {"sub": "user-123", "aud": "authenticated"}, "test-secret", algorithm="HS256"
        )
        result = asyncio.run(deps.get_current_user(credentials=_creds(token)))
        assert result == "user-123"

    def test_invalid_signature_rejected(self, monkeypatch):
        monkeypatch.setattr(deps._auth_manager, "is_configured", lambda: True)
        monkeypatch.setattr(deps, "_JWT_SECRET", "test-secret")
        token = pyjwt.encode(
            {"sub": "user-123", "aud": "authenticated"}, "wrong-secret", algorithm="HS256"
        )
        with pytest.raises(HTTPException) as exc:
            asyncio.run(deps.get_current_user(credentials=_creds(token)))
        assert exc.value.status_code == 401


class TestGetOptionalUser:
    """Soft-auth dependency used by public endpoints (e.g. market data)."""

    def test_no_credentials_returns_none(self, monkeypatch):
        monkeypatch.setattr(deps, "_JWT_SECRET", "test-secret")
        result = asyncio.run(deps.get_optional_user(credentials=None))
        assert result is None

    def test_never_raises_on_bad_token(self, monkeypatch):
        monkeypatch.setattr(deps, "_JWT_SECRET", "test-secret")
        token = pyjwt.encode(
            {"sub": "user-123", "aud": "authenticated"}, "wrong-secret", algorithm="HS256"
        )
        result = asyncio.run(deps.get_optional_user(credentials=_creds(token)))
        assert result is None

    def test_valid_token_returns_identity(self, monkeypatch):
        monkeypatch.setattr(deps, "_JWT_SECRET", "test-secret")
        token = pyjwt.encode(
            {"sub": "user-123", "aud": "authenticated"}, "test-secret", algorithm="HS256"
        )
        result = asyncio.run(deps.get_optional_user(credentials=_creds(token)))
        assert result == "user-123"


class TestResolveUserId:
    def test_demo_user_falls_back_to_client_supplied_id(self):
        assert deps.resolve_user_id("demo_user", "requested-id") == "requested-id"

    def test_real_identity_is_never_overridden(self):
        # Even if a caller supplies someone else's id, a verified identity wins.
        assert deps.resolve_user_id("real-uuid", "someone-elses-uuid") == "real-uuid"
