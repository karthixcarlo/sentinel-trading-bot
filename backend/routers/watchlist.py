import os
import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services import auth_manager as auth
from backend.deps import get_current_user, ROOT_DIR

router = APIRouter(prefix="/api/watchlist", tags=["watchlist"])

_DEMO_DB = os.path.join(ROOT_DIR, "sentinel.db")


def _ensure_watchlist_table():
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS watchlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        ticker TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(user_id, ticker)
    )""")
    conn.commit()
    conn.close()


class WatchlistAddRequest(BaseModel):
    ticker: str


@router.get("")
async def get_watchlist(current_user: str = Depends(get_current_user)):
    """Returns the authenticated user's watchlist tickers."""
    # Try Supabase first
    try:
        client = auth.get_client()
        result = client.table("watchlists").select("id, ticker, created_at") \
            .eq("user_id", current_user).order("created_at", desc=True).execute()
        return {"items": result.data or []}
    except Exception:
        pass
    # SQLite fallback
    _ensure_watchlist_table()
    conn = sqlite3.connect(_DEMO_DB)
    rows = conn.execute(
        "SELECT id, ticker, created_at FROM watchlists WHERE user_id=? ORDER BY id DESC",
        (current_user,)
    ).fetchall()
    conn.close()
    return {"items": [{"id": r[0], "ticker": r[1], "created_at": r[2]} for r in rows]}


@router.post("")
async def add_to_watchlist(req: WatchlistAddRequest, current_user: str = Depends(get_current_user)):
    """Adds a ticker to the user's watchlist."""
    ticker = req.ticker.upper().strip()
    # Try Supabase first
    try:
        client = auth.get_client()
        client.table("watchlists").insert({"user_id": current_user, "ticker": ticker}).execute()
        return {"status": "success", "ticker": ticker}
    except Exception:
        pass
    # SQLite fallback
    _ensure_watchlist_table()
    try:
        conn = sqlite3.connect(_DEMO_DB)
        conn.execute("INSERT OR IGNORE INTO watchlists (user_id, ticker) VALUES (?,?)", (current_user, ticker))
        conn.commit()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "success", "ticker": ticker}


@router.delete("/{ticker}")
async def remove_from_watchlist(ticker: str, current_user: str = Depends(get_current_user)):
    """Removes a ticker from the user's watchlist."""
    ticker = ticker.upper().strip()
    # Try Supabase first
    try:
        client = auth.get_client()
        client.table("watchlists").delete() \
            .eq("user_id", current_user).eq("ticker", ticker).execute()
        return {"status": "success", "ticker": ticker}
    except Exception:
        pass
    # SQLite fallback
    _ensure_watchlist_table()
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute("DELETE FROM watchlists WHERE user_id=? AND ticker=?", (current_user, ticker))
    conn.commit()
    conn.close()
    return {"status": "success", "ticker": ticker}
