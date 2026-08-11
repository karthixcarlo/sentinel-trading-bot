"""
Shared dependencies for all backend routers.
Centralizes auth, logging, paths, and common utilities.
"""
import os
import logging
from typing import Optional
import jwt as _jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
import re

from services import auth_manager as _auth_manager

# Shared rate limiter instance — imported by every router
limiter = Limiter(key_func=get_remote_address)

# Project root (one level up from backend/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logging
logger = logging.getLogger("sentinel")

# JWT auth
_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")
_http_bearer = HTTPBearer(auto_error=False)


def _real_auth_required() -> bool:
    """
    True when Supabase is configured, meaning this deployment has real user
    accounts and unauthenticated requests must NOT be treated as a trusted
    identity. False only in genuine demo mode (no Supabase configured at all),
    where there are no real accounts to impersonate.
    """
    return _auth_manager.is_configured()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_http_bearer)
) -> str:
    """
    Extracts and verifies the Supabase JWT from the Authorization header.
    Returns the user's UUID (sub claim).

    In demo mode (Supabase not configured), falls back to 'demo_user' when no
    token is provided — there are no real accounts to protect. When Supabase
    IS configured, missing/invalid credentials or a missing JWT secret are
    treated as authentication failures (fail closed) rather than silently
    granting a spoofable 'demo_user' identity.
    """
    auth_required = _real_auth_required()

    if credentials is None:
        if auth_required:
            raise HTTPException(status_code=401, detail="Authentication required.")
        return "demo_user"

    token = credentials.credentials

    if not _JWT_SECRET:
        if auth_required:
            # Supabase is configured but the server is missing the JWT secret
            # needed to verify tokens — this is a misconfiguration, not a
            # valid "no auth" state. Never trust an unverified token here.
            raise HTTPException(status_code=401, detail="Authentication is not available.")
        try:
            payload = _jwt.decode(token, options={"verify_signature": False})
            return payload.get("sub", "demo_user")
        except Exception:
            return "demo_user"

    try:
        payload = _jwt.decode(
            token, _JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload["sub"]
    except _jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except _jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Security(_http_bearer)
) -> Optional[str]:
    """
    Soft-auth dependency for endpoints that must stay publicly accessible but
    should recognize the caller's identity when a valid token is supplied
    (e.g. to decide whether to include that specific user's private data).
    Never raises — returns None for missing, malformed, or unverifiable
    tokens instead of granting any identity.
    """
    if credentials is None:
        return None
    token = credentials.credentials
    if not _JWT_SECRET:
        return None
    try:
        payload = _jwt.decode(
            token, _JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload.get("sub")
    except _jwt.InvalidTokenError:
        return None


# Ticker validation
_VALID_TICKER = re.compile(r'^[A-Z0-9&-]{1,20}(?:\.(?:NS|BO))?$')


def validate_ticker(ticker: str) -> str:
    """Validate and sanitize a stock ticker symbol."""
    t = ticker.upper().strip()
    if not _VALID_TICKER.match(t):
        raise HTTPException(status_code=400, detail="Invalid ticker format")
    return t


def resolve_user_id(current_user: str, fallback_id: str) -> str:
    """Use JWT identity when available, fall back to provided ID in demo mode."""
    return current_user if current_user != "demo_user" else fallback_id
