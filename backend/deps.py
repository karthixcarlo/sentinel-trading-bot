"""
Shared dependencies for all backend routers.
Centralizes auth, logging, paths, and common utilities.
"""
import os
import logging
import jwt as _jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import re

# Project root (one level up from backend/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logging
logger = logging.getLogger("sentinel")

# JWT auth
_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")
_http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(_http_bearer)
) -> str:
    """
    Extracts and verifies the Supabase JWT from the Authorization header.
    Returns the user's UUID (sub claim).
    Falls back to 'demo_user' when Supabase is not configured or no token provided.
    """
    if credentials is None:
        return "demo_user"
    token = credentials.credentials
    if not _JWT_SECRET:
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
    except _jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


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
