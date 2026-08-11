import os
import sqlite3
from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field
from services import auth_manager as auth
from backend.deps import get_current_user, validate_ticker, resolve_user_id, logger, ROOT_DIR, limiter
import yfinance as yf

router = APIRouter(prefix="/api/trade", tags=["trade"])

_DEMO_DB = os.path.join(ROOT_DIR, "sentinel.db")


# --- Demo SQLite helpers ---

def _demo_ensure_tables():
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS demo_portfolios (
        user_id TEXT PRIMARY KEY, cash_balance REAL DEFAULT 100000.0)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS demo_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, ticker TEXT,
        qty REAL, price REAL, side TEXT, timestamp TEXT)""")
    conn.commit()
    conn.close()


def _demo_get_cash(user_id: str) -> float:
    _demo_ensure_tables()
    conn = sqlite3.connect(_DEMO_DB)
    row = conn.execute("SELECT cash_balance FROM demo_portfolios WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row:
        return float(row[0])
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute("INSERT OR IGNORE INTO demo_portfolios (user_id, cash_balance) VALUES (?,?)", (user_id, 100000.0))
    conn.commit()
    conn.close()
    return 100000.0


def _demo_get_positions(user_id: str) -> list:
    _demo_ensure_tables()
    conn = sqlite3.connect(_DEMO_DB)
    rows = conn.execute(
        "SELECT ticker, qty, price, side FROM demo_transactions WHERE user_id=? ORDER BY id", (user_id,)
    ).fetchall()
    conn.close()
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


def _demo_log_tx(user_id, ticker, qty, price, side):
    _demo_ensure_tables()
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute(
        "INSERT INTO demo_transactions (user_id,ticker,qty,price,side,timestamp) VALUES (?,?,?,?,?,?)",
        (user_id, ticker, qty, price, side, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def _demo_update_cash(user_id, new_balance):
    _demo_ensure_tables()
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute("INSERT OR REPLACE INTO demo_portfolios (user_id,cash_balance) VALUES (?,?)", (user_id, new_balance))
    conn.commit()
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
    """Executes a BUY or SELL trade."""
    try:
        resolved_user = resolve_user_id(current_user, req.user_id)

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

        supabase_portfolio = auth.get_user_portfolio(resolved_user)
        use_supabase = supabase_portfolio.get("success", False)

        if use_supabase:
            cash = supabase_portfolio.get("cash", 0.0)
            positions = supabase_portfolio.get("positions", [])
        else:
            cash = _demo_get_cash(resolved_user)
            positions = _demo_get_positions(resolved_user)

        total_cost = req.quantity * exec_price
        brokerage = round(total_cost * 0.0003, 2)
        final_cost = round(total_cost + brokerage, 2)

        if req.action == "BUY":
            if cash < final_cost:
                raise HTTPException(status_code=400, detail=f"Insufficient funds. Have ₹{cash:,.2f}, need ₹{final_cost:,.2f}")

            new_cash = round(cash - final_cost, 2)

            if use_supabase:
                tx_r = auth.log_transaction(resolved_user, full_symbol, req.quantity, exec_price, "BUY")
                ca_r = auth.update_cash_balance(resolved_user, new_cash)
                if not (tx_r.get("success") and ca_r.get("success")):
                    _demo_log_tx(resolved_user, full_symbol, req.quantity, exec_price, "BUY")
                    _demo_update_cash(resolved_user, new_cash)
            else:
                _demo_log_tx(resolved_user, full_symbol, req.quantity, exec_price, "BUY")
                _demo_update_cash(resolved_user, new_cash)

            return {
                "status": "success", "action": "BUY", "symbol": req.symbol,
                "quantity": req.quantity, "price": exec_price, "brokerage": brokerage,
                "total_cost": final_cost, "new_cash": new_cash,
                "message": f"BUY order executed: {req.quantity} × {req.symbol} @ ₹{exec_price:,.2f}"
            }

        elif req.action == "SELL":
            existing = next(
                (p for p in positions if p.get("symbol", "").upper() in [full_symbol, req.symbol.upper()]),
                None
            )
            if not existing:
                raise HTTPException(status_code=400, detail=f"No position found for {req.symbol}")
            held = existing.get("quantity", 0)
            if held < req.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient shares. Have {held}, selling {req.quantity}")

            proceeds = round((req.quantity * exec_price) - brokerage, 2)
            new_cash = round(cash + proceeds, 2)

            if use_supabase:
                tx_r = auth.log_transaction(resolved_user, full_symbol, req.quantity, exec_price, "SELL")
                ca_r = auth.update_cash_balance(resolved_user, new_cash)
                if not (tx_r.get("success") and ca_r.get("success")):
                    _demo_log_tx(resolved_user, full_symbol, req.quantity, exec_price, "SELL")
                    _demo_update_cash(resolved_user, new_cash)
            else:
                _demo_log_tx(resolved_user, full_symbol, req.quantity, exec_price, "SELL")
                _demo_update_cash(resolved_user, new_cash)

            return {
                "status": "success", "action": "SELL", "symbol": req.symbol,
                "quantity": req.quantity, "price": exec_price, "brokerage": brokerage,
                "proceeds": proceeds, "new_cash": new_cash,
                "message": f"SELL order executed: {req.quantity} × {req.symbol} @ ₹{exec_price:,.2f}"
            }
        else:
            raise HTTPException(status_code=400, detail="Action must be BUY or SELL")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade Execute Error: {e}")
        raise HTTPException(status_code=500, detail="Trade execution failed. Please try again.")
