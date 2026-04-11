"""
Project Sentinel API — thin aggregator.
All endpoint logic lives in backend/routers/*.py; this file handles
app init, CORS, health check, and router registration.
"""
import sys
import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from backend.deps import limiter

# Add project root to path so we can import shared modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

_START_TIME = time.time()

app = FastAPI(title="Project Sentinel API", version="2.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — explicit origins only; wildcard + credentials is a spec violation.
_CORS_RAW = os.environ.get("ALLOWED_ORIGINS", "")
_CORS_ORIGINS = [o.strip() for o in _CORS_RAW.split(",") if o.strip()] if _CORS_RAW else [
    "https://sentinel-trading-bot.vercel.app",
    "http://localhost:5173",
]

# Guarantee required origins are always present
for _origin in [
    "https://sentinel-trading-bot.vercel.app",
    "http://localhost:5173",
]:
    if _origin not in _CORS_ORIGINS:
        _CORS_ORIGINS.append(_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# --- Health check (kept here — it's the only non-router endpoint) ---
@app.get("/api/health")
@limiter.limit("30/minute")
async def health_check(request: Request):
    """Returns service health status, uptime, and version."""
    uptime_secs = time.time() - _START_TIME
    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": round(uptime_secs, 1),
        "uptime_human": f"{int(uptime_secs // 3600)}h {int((uptime_secs % 3600) // 60)}m {int(uptime_secs % 60)}s",
    }


# --- Register all routers ---
from backend.routers.auth import router as auth_router
from backend.routers.chat import router as chat_router
from backend.routers.market import router as market_router
from backend.routers.portfolio import router as portfolio_router
from backend.routers.trade import router as trade_router
from backend.routers.agent import router as agent_router
from backend.routers.settings import router as settings_router
from backend.routers.watchlist import router as watchlist_router
from backend.routers.ws import router as ws_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(market_router)
app.include_router(portfolio_router)
app.include_router(trade_router)
app.include_router(agent_router)
app.include_router(settings_router)
app.include_router(watchlist_router)
app.include_router(ws_router)
