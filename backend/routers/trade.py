import os
import sqlite3
from contextlib import closing
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field
from services import auth_manager as auth
from services import broker_engine
from backend.deps import get_current_user, validate_ticker, resolve_user_id, logger, ROOT_DIR, limiter
import yfinance as yf

router = APIRouter(prefix="/api/trade", tags=["trade"])

_DEMO_DB = os.path.join(ROOT_DIR, "sentinel.db")


# --- Demo SQLite helpers ---

def _demo_ensure_tables():
    with closing(sqlite3.connect(_DEMO_DB)) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS demo_portfolios (
            user_id TEXT PRIMARY KEY, cash_balance REAL DEFAULT 100000.0)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS demo_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, ticker TEXT,
            qty REAL, price REAL, side TEXT, timestamp TEXT)""")
        conn.commit()


def _demo_get_cash(user_id: str) -> float:
    """Read-only helper — also used by portfolio.py for display purposes."""
    _demo_ensure_tables()
    with closing(sqlite3.connect(_DEMO_DB)) as conn:
        row = conn.execute("SELECT cash_balance FROM demo_portfolios WHERE user_id=?", (user_id,)).fetchone()
        if row:
            return float(row[0])
        conn.execute("INSERT OR IGNORE INTO demo_portfolios (user_id, cash_balance) VALUES (?,?)", (user_id, 100000.0))
        conn.commit()
        return 100000.0


def _demo_get_positions(user_id: str) -> list:
    """Read-only helper — also used by portfolio.py for display purposes."""
    _demo_ensure_tables()
    with closing(sqlite3.connect(_DEMO_DB)) as conn:
        rows = conn.execute(
            "SELECT ticker, qty, price, side FROM demo_transactions WHERE user_id=? ORDER BY id", (user_id,)
        ).fetchall()
    holdings: dict = {}
    for ticker, qty, price, side in rows:
        h = holdings.setdefault(ticker, {"symbol": ticker, "quantity": 0.0, "total_cost": 0.0})
        if side == "BUY":
            h["total_cost"] += qty * price
            h["quantity"] += qty
        elif side == "SELL":
            h["quantity"] -= qty
    return [{"symbol": h["symbol"], "quantity": h["quantity"],
             "average_price": round(h["total_cost"] / h["quantity"], 2) if h["quantity"] > 0 else 0}
            for h in holdings.values() if h["quantity"] > 0]


def _demo_execute_trade_atomic(user_id: str, ticker: str, side: str, qty: float, price: float) -> dict:
    """
    Validates and records a demo (SQLite) trade inside a single explicit
    transaction, so the funds/holdings check and the resulting write can't
    be split across two connections. Without this, two concurrent requests
    for the same demo user could each read the same starting cash/position,
    both "pass" their check against that stale value, and both write —
    silently overspending cash or overselling a position (a lost update).

    BEGIN IMMEDIATE acquires the write lock upfront rather than after the
    read, so a second concurrent call blocks (up to busy_timeout) instead
    of racing to upgrade its own lock after already having read.

    Returns {"success": bool, "message": str, "order": dict|None}.
    """
    _demo_ensure_tables()
    gross = round(qty * price, 2)
    brokerage = round(gross * 0.0003, 2)

    conn = sqlite3.connect(_DEMO_DB, timeout=10)
    conn.isolation_level = None  # manual transaction control below
    try:
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("BEGIN IMMEDIATE")

        row = conn.execute("SELECT cash_balance FROM demo_portfolios WHERE user_id=?", (user_id,)).fetchone()
        if row is None:
            conn.execute("INSERT INTO demo_portfolios (user_id, cash_balance) VALUES (?,?)", (user_id, 100000.0))
            cash = 100000.0
        else:
            cash = float(row[0])

        if side == "BUY":
            total_debit = round(gross + brokerage, 2)
            if cash < total_debit:
                conn.execute("ROLLBACK")
                return {
                    "success": False,
                    "message": f"Insufficient funds. Have ₹{cash:,.2f}, need ₹{total_debit:,.2f}",
                    "order": None,
                }
            new_cash = round(cash - total_debit, 2)
            order = {"brokerage": brokerage, "total_cost": total_debit, "cash_after": new_cash}
        else:
            held_row = conn.execute(
                "SELECT COALESCE(SUM(CASE WHEN side='BUY' THEN qty ELSE -qty END), 0) "
                "FROM demo_transactions WHERE user_id=? AND ticker=?",
                (user_id, ticker),
            ).fetchone()
            held = float(held_row[0] or 0)
            if held < qty:
                conn.execute("ROLLBACK")
                return {
                    "success": False,
                    "message": f"Insufficient shares. Have {held:g}, selling {qty:g}",
                    "order": None,
                }
            proceeds = round(gross - brokerage, 2)
            new_cash = round(cash + proceeds, 2)
            order = {"brokerage": brokerage, "proceeds": proceeds, "cash_after": new_cash}

        conn.execute(
            "INSERT INTO demo_transactions (user_id,ticker,qty,price,side,timestamp) VALUES (?,?,?,?,?,?)",
            (user_id, ticker, qty, price, side, datetime.now(timezone.utc).isoformat()),
        )
        conn.execute(
            "INSERT OR REPLACE INTO demo_portfolios (user_id,cash_balance) VALUES (?,?)",
            (user_id, new_cash),
        )
        conn.execute("COMMIT")
        return {"success": True, "message": "ok", "order": order}
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()


# --- Models ---

class TradeRequest(BaseModel):
    user_id: str
    symbol: str
    action: str
    quantity: int = Field(gt=0)


class TradeExecuteRequest(BaseModel):
    user_id: str
    symbol: str
    action: str  # "BUY" or "SELL"
    quantity: int = Field(gt=0)
    order_type: Optional[str] = "MARKET"
    limit_price: Optional[float] = Field(default=None, gt=0)


# --- Endpoints ---

@router.post("/manual")
@limiter.limit("10/minute")
async def manual_trade(request: Request, req: TradeRequest, background_tasks: BackgroundTasks, current_user: str = Depends(get_current_user)):
    """Endpoint for users to manually trigger the Execution Agent."""
    return {"status": "Trade execution task triggered", "details": req.model_dump()}


@router.post("/execute")
@limiter.limit("10/minute")
async def execute_trade(request: Request, req: TradeExecuteRequest, current_user: str = Depends(get_current_user)):
    """
    Executes a BUY or SELL trade.

    The funds/holdings check and the resulting ledger write happen
    atomically — either through the execute_trade_atomic() Postgres
    function (see supabase_setup.sql) when Supabase is configured, or
    through a single SQLite transaction in demo mode. Neither path falls
    back to the other mid-request: mixing the two silently on a write
    failure would fork a user's real portfolio from a completely separate
    demo ledger without any indication that happened.
    """
    try:
        resolved_user = resolve_user_id(current_user, req.user_id)

        if req.action not in ("BUY", "SELL"):
            raise HTTPException(status_code=400, detail="Action must be BUY or SELL")

        full_symbol = validate_ticker(req.symbol)
        if not full_symbol.endswith(".NS") and not full_symbol.endswith(".BO"):
            full_symbol += ".NS"

        exec_price = req.limit_price or 0.0
        if req.order_type == "MARKET" or not exec_price:
            try:
                hist = yf.Ticker(full_symbol).history(period="1d")
                if hist.empty:
                    raise HTTPException(status_code=404, detail=f"Cannot fetch live price for {req.symbol}")
                exec_price = round(float(hist["Close"].iloc[-1]), 2)
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Price fetch failed for {full_symbol}: {e}")
                raise HTTPException(status_code=503, detail="Price fetch failed. Please try again.")

        if auth.is_configured():
            result = broker_engine.execute_order(
                user_id=resolved_user, ticker=full_symbol, side=req.action,
                quantity=req.quantity, current_price=exec_price,
            )
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["message"])
            order = result["order"]
            response = {
                "status": "success", "action": req.action, "symbol": req.symbol,
                "quantity": req.quantity, "price": exec_price, "brokerage": order["brokerage"],
                "new_cash": order["cash_after"], "message": result["message"],
            }
            if req.action == "BUY":
                response["total_cost"] = order["total_debit"]
            else:
                response["proceeds"] = order["net_proceeds"]
            return response
        else:
            result = _demo_execute_trade_atomic(resolved_user, full_symbol, req.action, req.quantity, exec_price)
            if not result["success"]:
                raise HTTPException(status_code=400, detail=result["message"])
            order = result["order"]
            response = {
                "status": "success", "action": req.action, "symbol": req.symbol,
                "quantity": req.quantity, "price": exec_price, "brokerage": order["brokerage"],
                "new_cash": order["cash_after"],
                "message": f"{req.action} order executed: {req.quantity} × {req.symbol} @ ₹{exec_price:,.2f}",
            }
            if req.action == "BUY":
                response["total_cost"] = order["total_cost"]
            else:
                response["proceeds"] = order["proceeds"]
            return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade Execute Error: {e}")
        raise HTTPException(status_code=500, detail="Trade execution failed. Please try again.")
