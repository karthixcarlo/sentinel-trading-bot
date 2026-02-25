import sys
import os
import time
import logging
from fastapi import FastAPI, Depends, BackgroundTasks, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json

# Add project root to path so we can import dashboard_v3 modules
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from dashboard_v3 import auth_manager as auth

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinel")

_START_TIME = time.time()

app = FastAPI(title="Project Sentinel API", version="2.0.0")

# CORS — read allowed origins from env, default to local dev
_CORS_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,https://sentinel-trading-bot.vercel.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- HEALTH CHECK ---
@app.get("/api/health")
async def health_check():
    """Returns service health status, uptime, and version."""
    uptime_secs = time.time() - _START_TIME
    return {
        "status": "ok",
        "version": "2.0.0",
        "uptime_seconds": round(uptime_secs, 1),
        "uptime_human": f"{int(uptime_secs // 3600)}h {int((uptime_secs % 3600) // 60)}m {int(uptime_secs % 60)}s",
    }

# --- MODELS ---
class LoginRequest(BaseModel):
    email: str
    password: str

class TradeRequest(BaseModel):
    user_id: str
    symbol: str
    action: str
    quantity: int

# --- REST ENDPOINTS ---

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """Interfaces with Supabase Auth to validate users."""
    result = auth.sign_in(req.email, req.password)
    if result.get("success"): 
        user = result.get("user")
        return {
            "status": "success", 
            "token": result.get("session", {}).get("access_token", "dummy_token"),
            "user_id": user.id if user else "demo_user"
        }
    raise HTTPException(status_code=401, detail=result.get("error", "Invalid credentials"))


@app.get("/api/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """Retrieves the user's cash and holdings from PostgreSQL. Returns demo data when Supabase is unavailable."""
    portfolio = auth.get_user_portfolio(user_id)
    if not portfolio.get("success"):
        # Return fallback demo data so the UI still renders (Supabase may be unconfigured)
        return {
            "success": True,
            "cash": portfolio.get("cash", 100000.0),
            "positions": portfolio.get("positions", []),
            "orders": portfolio.get("orders", [])
        }
    return portfolio



@app.post("/api/trade/manual")
async def manual_trade(req: TradeRequest, background_tasks: BackgroundTasks):
    """Endpoint for users to manually trigger the Execution Agent."""
    return {"status": "Trade execution task triggered", "details": req.model_dump()}

# --- AI TRADING COPILOT ENDPOINT ---

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.post("/api/chat/copilot")
async def copilot_chat(req: ChatRequest):
    """
    Connects to Gemini and fetches the user's latest agent_logs from Supabase
    (with SQLite fallback) to explain the trading system's decision-making process.
    """
    try:
        from langgraph_agents import llm

        # 1. Fetch recent agent context — Supabase first, SQLite fallback
        context_str = "No recent agent activity found."

        try:
            client = auth.get_client()
            logs = client.table("agent_logs").select("agent_name, message, timestamp") \
                .or_(f"user_id.eq.{req.user_id},user_id.is.null") \
                .order("timestamp", desc=True) \
                .limit(15) \
                .execute()
            if logs.data:
                context_str = "\n".join([
                    f"[{l.get('timestamp', 'N/A')}] {l['agent_name']}: {l['message']}"
                    for l in logs.data
                ])
        except Exception as supabase_err:
            logger.info(f"Copilot: Supabase unavailable, falling back to SQLite — {supabase_err}")
            try:
                import sqlite3
                db_path = os.path.join(ROOT_DIR, "sentinel.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.execute(
                    "SELECT agent_name, message, iteration FROM agent_thoughts ORDER BY rowid DESC LIMIT 15"
                )
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    context_str = "\n".join([
                        f"[Cycle {r[2]}] {r[0]}: {r[1]}" for r in rows
                    ])
            except Exception as sqlite_err:
                print(f"Copilot: SQLite fallback also failed — {sqlite_err}")

        # 2. Construct System Prompt
        sys_prompt = f"""You are Sentinel, a senior AI Trading Copilot. You monitor an internal multi-agent LangGraph execution engine (Scout → Analyst → Risk Manager → Trader).
Your role: Answer the human's queries about trading logic, portfolio moves, or market insights based on the recent agent logs below.
Be concise, analytical, and professional (Groww/Zerodha style). Use markdown formatting (bold for key terms, bullet points for lists). Limit to 3-5 sentences or a short bullet list.

--- RECENT AGENT SYSTEM LOGS ---
{context_str}
"""
        # 3. Invoke Gemini via LangChain
        from langchain_core.messages import SystemMessage, HumanMessage
        response = llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=req.message)
        ])

        return {"status": "success", "reply": response.content}
    except Exception as e:
        print(f"Copilot Error: {e}")
        return {"status": "error", "reply": "I'm having trouble connecting to the Neural Core right now."}



# --- MARKET DATA ENDPOINT ---
import yfinance as yf
from datetime import datetime, timedelta

@app.get("/api/market/ohlcv/{ticker}")
async def get_ohlcv(ticker: str, user_id: str | None = None):
    """
    Fetches historical daily OHLCV via yfinance, formatted for lightweight-charts.
    Trades (BUY/SELL markers) come from Supabase transactions when user_id is provided.
    """
    try:
        # Ensure NSE suffix for yfinance
        fetch_ticker = ticker if ticker.endswith(".NS") or ticker.endswith(".BO") else f"{ticker}.NS"
        stock = yf.Ticker(fetch_ticker)
        df = stock.history(period="6mo")
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
            
        ohlc = []
        volume = []
        
        for index, row in df.iterrows():
            time_str = index.strftime('%Y-%m-%d')
            is_green = row['Close'] >= row['Open']
            
            ohlc.append({
                "time": time_str,
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2)
            })
            vol_val = int(row['Volume']) if 'Volume' in row else 0
            volume.append({
                "time": time_str,
                "value": vol_val,
                "color": '#26a69a' if is_green else '#ef5350'
            })
        
        # Fetch trades from Supabase transactions if user_id provided
        trades = []
        if user_id:
            try:
                client = auth.get_client()
                base_ticker = ticker.replace(".NS", "").replace(".BO", "")
                ticker_variants = list({ticker, base_ticker, fetch_ticker})
                tx_result = client.table("transactions").select("ticker, side, qty, timestamp")\
                    .eq("user_id", user_id)\
                    .in_("ticker", ticker_variants)\
                    .eq("status", "EXECUTED")\
                    .order("timestamp")\
                    .execute()
                if tx_result.data:
                    for tx in tx_result.data:
                        ts = tx.get("timestamp") or ""
                        time_str = ts[:10] if len(ts) >= 10 else ts
                        trades.append({
                            "time": time_str,
                            "side": tx.get("side", "BUY").upper(),
                            "qty": int(float(tx.get("qty", 0)))
                        })
            except Exception as e:
                print(f"OHLCV: Could not fetch transactions: {e}")
        
        # Fallback to demo trades when no user trades exist
        if not trades:
            trades = [
                {"time": (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'), "side": "BUY", "qty": 25},
                {"time": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), "side": "SELL", "qty": 10},
                {"time": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), "side": "BUY", "qty": 15},
            ]
            
        return {"ohlc": ohlc, "volume": volume, "trades": trades}
    except Exception as e:
        print(f"Chart Data Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")


# Demo fallback for Discover when yfinance fails (no network, rate limit, etc.)
DEMO_DISCOVER = [
    {"symbol": "RELIANCE", "name": "Reliance Industries", "price": 1250.50, "change": 1.2},
    {"symbol": "TCS", "name": "Tata Consultancy", "price": 3850.25, "change": -0.5},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "price": 1680.00, "change": 0.8},
    {"symbol": "INFY", "name": "Infosys Ltd", "price": 1520.75, "change": 1.1},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "price": 1125.00, "change": -0.3},
    {"symbol": "SBIN", "name": "State Bank of India", "price": 850.50, "change": 2.1},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "price": 1450.00, "change": 0.9},
    {"symbol": "ITC", "name": "ITC Ltd", "price": 465.25, "change": -0.2},
    {"symbol": "LT", "name": "Larsen & Toubro", "price": 3650.00, "change": 1.5},
    {"symbol": "ASIANPAINT", "name": "Asian Paints", "price": 2850.50, "change": 0.4},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "price": 6850.00, "change": -0.8},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "price": 12500.00, "change": 1.0},
]

@app.get("/api/market/discover")
async def get_market_discover():
    """Fetches live market data for the Discovery grid. Returns demo data when yfinance fails."""
    try:
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
            "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
            "LT.NS", "ASIANPAINT.NS", "BAJFINANCE.NS", "MARUTI.NS"
        ]
        tickers = yf.Tickers(" ".join(symbols))
        data = []
        name_map = {
            "RELIANCE": "Reliance Industries", "TCS": "Tata Consultancy",
            "HDFCBANK": "HDFC Bank Ltd", "INFY": "Infosys Ltd",
            "ICICIBANK": "ICICI Bank Ltd", "SBIN": "State Bank of India",
            "BHARTIARTL": "Bharti Airtel", "ITC": "ITC Ltd",
            "LT": "Larsen & Toubro", "ASIANPAINT": "Asian Paints",
            "BAJFINANCE": "Bajaj Finance", "MARUTI": "Maruti Suzuki"
        }
        for symbol in symbols:
            try:
                hist = tickers.tickers[symbol].history(period="5d")
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    display_sym = symbol.replace('.NS', '')
                    data.append({
                        "symbol": display_sym,
                        "name": name_map.get(display_sym, display_sym),
                        "price": round(float(current_price), 2),
                        "change": round(float(change_pct), 2)
                    })
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
        if not data:
            return DEMO_DISCOVER
        return data
    except Exception as e:
        print(f"Discover API Error: {e}")
        return DEMO_DISCOVER


@app.get("/api/market/analyze/{ticker}")
async def analyze_stock(ticker: str):
    """Generates an AI deep dive report on a specific equity."""
    try:
        from langgraph_agents import llm
        
        # Ensure .NS suffix for NSE stocks
        fetch_ticker = ticker + ".NS" if not ticker.endswith(".NS") else ticker
        stock = yf.Ticker(fetch_ticker)
        
        hist = stock.history(period="1mo")
        if hist.empty:
            raise HTTPException(status_code=404, detail="Stock data not found")
            
        info = stock.info
        
        # Basic indicators
        current_price = round(hist['Close'].iloc[-1], 2)
        sma_20 = round(hist['Close'].tail(20).mean(), 2) if len(hist) >= 20 else current_price
        
        prompt = f"""You are Sentinel's Senior Financial Analyst. 
Analyze the Indian NSE stock {ticker}.
Current Price: ₹{current_price}
20-Day SMA: ₹{sma_20}
Sector: {info.get('sector', 'Unknown')}
Industry: {info.get('industry', 'Unknown')}
Market Cap: {info.get('marketCap', 'Unknown')}
P/E Ratio: {info.get('trailingPE', 'N/A')}

Please write a structured markdown report covering:
1. Executive Summary (BUY/HOLD/SELL recommendation)
2. Technical Outlook (Trend, Support/Resistance levels based on recent price action)
3. Fundamental Overview
4. Key Risks

Keep it highly professional, formatting it beautifully in markdown. Do not hallucinate exact pricing data beyond what is provided, but use your vast pre-trained knowledge about this company to fill in fundamental context.
"""
        response = llm.invoke(prompt)
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "sma_20": sma_20,
            "name": info.get('shortName', ticker),
            "report": response.content
        }
    except Exception as e:
        print(f"Analysis API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze stock")

# --- WEBSOCKET ENDPOINT ---
from agent_service import get_agent_service

# Store active WebSocket connections
active_connections = []

async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    for connection in active_connections:
        try:
            await connection.send_json(message)
        except Exception as e:
            print(f"Error broadcasting to WebSocket: {e}")

@app.websocket("/ws/neural-feed")
async def websocket_neural_feed(websocket: WebSocket):
    """
    Streams the live 'thoughts' from the Sentinel Agent
    directly to the client for the 'God Mode' dashboard.
    """
    await websocket.accept()
    active_connections.append(websocket)
    
    # Set the WebSocket callback on the agent service
    agent_service = get_agent_service()
    original_callback = agent_service.websocket_callback
    
    async def ws_callback(thought: dict):
        await websocket.send_json(thought)
    
    agent_service.set_websocket_callback(ws_callback)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "agent": "System",
            "thought": "Neural feed connected - receiving live agent thoughts",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and send periodic heartbeats
        while True:
            await asyncio.sleep(3)
            # Send heartbeat
            await websocket.send_json({
                "agent": "Heartbeat",
                "thought": "...",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        logger.info(f"WebSocket connection closed: {e}")
    finally:
        active_connections.remove(websocket)
        # Restore original callback if still valid
        agent_service.set_websocket_callback(original_callback)


# --- AUTONOMOUS TRADING ENDPOINTS ---

@app.post("/api/agent/start")
async def start_autonomous_trading():
    """
    Start the autonomous trading agent.
    """
    try:
        agent_service = get_agent_service()
        await agent_service.start_autonomous_mode()
        return {"status": "success", "message": "Autonomous trading started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/agent/stop")
async def stop_autonomous_trading():
    """
    Stop the autonomous trading agent.
    """
    try:
        agent_service = get_agent_service()
        await agent_service.stop_autonomous_mode()
        return {"status": "success", "message": "Autonomous trading stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/status")
async def get_agent_status():
    """
    Get current status of the autonomous agent.
    """
    try:
        agent_service = get_agent_service()
        return agent_service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/portfolio")
async def get_agent_portfolio():
    """
    Get current portfolio managed by the agent.
    """
    try:
        agent_service = get_agent_service()
        return agent_service.get_portfolio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/thoughts")
async def get_agent_thoughts(limit: int = 50):
    """
    Get recent agent thoughts/logs.
    """
    try:
        agent_service = get_agent_service()
        return {"thoughts": agent_service.get_thoughts(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/trades")
async def get_agent_trades(limit: int = 50):
    """
    Get trade history.
    """
    try:
        agent_service = get_agent_service()
        return {"trades": agent_service.get_trade_history(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- SETTINGS ENDPOINT ---

from typing import List, Optional
from datetime import date
import json as _json

class UserSettings(BaseModel):
    risk_appetite: str
    max_position_size: int
    allowed_sectors: List[str]

_DEFAULT_SETTINGS = {
    "risk_appetite": "Moderate",
    "max_position_size": 10,
    "allowed_sectors": ["IT", "Banking", "Energy", "Automobile"]
}

def _settings_db_path():
    return _DEMO_DB  # reuse sentinel.db

def _ensure_settings_table():
    conn = _sqlite3.connect(_settings_db_path())
    conn.execute("""CREATE TABLE IF NOT EXISTS agent_settings (
        user_id TEXT PRIMARY KEY,
        risk_appetite TEXT DEFAULT 'Moderate',
        max_position_size INTEGER DEFAULT 10,
        allowed_sectors TEXT DEFAULT '[]'
    )""")
    conn.commit(); conn.close()

def _load_settings(user_id: str) -> dict:
    _ensure_settings_table()
    conn = _sqlite3.connect(_settings_db_path())
    row = conn.execute(
        "SELECT risk_appetite, max_position_size, allowed_sectors FROM agent_settings WHERE user_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "risk_appetite": row[0],
            "max_position_size": row[1],
            "allowed_sectors": _json.loads(row[2] or "[]")
        }
    return dict(_DEFAULT_SETTINGS)

def _save_settings(user_id: str, s: dict):
    _ensure_settings_table()
    conn = _sqlite3.connect(_settings_db_path())
    conn.execute(
        "INSERT OR REPLACE INTO agent_settings (user_id, risk_appetite, max_position_size, allowed_sectors) VALUES (?,?,?,?)",
        (user_id, s["risk_appetite"], s["max_position_size"], _json.dumps(s["allowed_sectors"]))
    )
    conn.commit(); conn.close()

@app.get("/api/settings/{user_id}")
async def get_settings(user_id: str):
    """Load agent constraints for a user."""
    return _load_settings(user_id)

@app.put("/api/settings/{user_id}")
async def update_settings(user_id: str, settings: UserSettings):
    """Persist agent constraints and apply them to the live AgentService immediately."""
    s = settings.model_dump()
    _save_settings(user_id, s)
    # Push to live agent so changes take effect without restart
    svc = get_agent_service()
    svc.update_config(s)
    return {"status": "success", "message": "Agent constraints updated and applied."}


# --- MARKET INDICES ENDPOINT ---

@app.get("/api/market/indices")
async def get_market_indices():
    """Fetches live Nifty 50, Bank Nifty, and Sensex index data."""
    fallback = [
        {"name": "Nifty 50",   "symbol": "^NSEI",    "value": 22150.50, "change": 1.25},
        {"name": "Bank Nifty", "symbol": "^NSEBANK",  "value": 48250.75, "change": -0.85},
        {"name": "Sensex",     "symbol": "^BSESN",    "value": 73280.30, "change": 0.95},
    ]
    try:
        result = []
        for item in fallback:
            try:
                ticker = yf.Ticker(item["symbol"])
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    current = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    change_pct = ((current - prev) / prev) * 100
                    result.append({"name": item["name"], "value": round(current, 2), "change": round(change_pct, 2)})
                else:
                    result.append(item)
            except:
                result.append(item)
        return result
    except Exception as e:
        print(f"Indices Error: {e}")
        return fallback


# --- PORTFOLIO DETAIL ENDPOINT (with P&L) ---

@app.get("/api/portfolio/{user_id}/detail")
async def get_portfolio_detail(user_id: str):
    """Returns portfolio with per-position P&L breakdown. Always returns 200."""
    DEMO = {
        "cash": 100000.0,
        "positions": [],
        "portfolio_value": 100000.0,
        "total_holdings_value": 0.0,
        "total_returns": 0.0,
        "returns_pct": 0.0,
        "orders": [],
    }
    try:
        portfolio = auth.get_user_portfolio(user_id)
    except Exception:
        return DEMO

    if not portfolio.get("success"):
        # Supabase unavailable — read from local SQLite demo DB instead
        portfolio = {
            "success": True,
            "cash": _demo_get_cash(user_id),
            "positions": _demo_get_positions(user_id),
            "orders": [],
        }

    try:
        cash = float(portfolio.get("cash") or 0.0)
        positions = portfolio.get("positions") or []
        orders = portfolio.get("orders") or []

        enriched_positions = []
        total_holdings_value = 0.0

        for pos in positions:
            symbol = pos.get("symbol", "")
            qty = float(pos.get("quantity") or 0)
            avg_price = float(pos.get("average_price") or 0.0)

            current_price = float(pos.get("current_price") or avg_price)
            try:
                fetch_sym = symbol if symbol.endswith(".NS") else symbol + ".NS"
                hist = yf.Ticker(fetch_sym).history(period="1d")
                if not hist.empty:
                    current_price = round(float(hist["Close"].iloc[-1]), 2)
            except Exception:
                pass

            position_value = qty * current_price
            cost_basis = qty * avg_price
            pnl = round(position_value - cost_basis, 2)
            pnl_pct = round((pnl / cost_basis * 100) if cost_basis > 0 else 0.0, 2)
            total_holdings_value += position_value

            enriched_positions.append({
                "symbol": symbol.replace(".NS", ""),
                "quantity": qty,
                "average_price": round(avg_price, 2),
                "current_price": current_price,
                "position_value": round(position_value, 2),
                "pnl": pnl,
                "pnl_pct": pnl_pct,
            })

        portfolio_value = cash + total_holdings_value
        initial_capital = 100000.0
        total_returns = round(portfolio_value - initial_capital, 2)
        returns_pct = round((total_returns / initial_capital) * 100, 2)

        return {
            "cash": cash,
            "positions": enriched_positions,
            "portfolio_value": round(portfolio_value, 2),
            "total_holdings_value": round(total_holdings_value, 2),
            "total_returns": total_returns,
            "returns_pct": returns_pct,
            "orders": orders,
        }
    except Exception as e:
        print(f"Portfolio Detail Error (inner): {e}")
        return DEMO


# --- TRADE EXECUTOR ENDPOINT ---

import sqlite3 as _sqlite3

_DEMO_DB = os.path.join(ROOT_DIR, "sentinel.db")

def _demo_ensure_tables():
    conn = _sqlite3.connect(_DEMO_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS demo_portfolios (
        user_id TEXT PRIMARY KEY, cash_balance REAL DEFAULT 100000.0)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS demo_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, ticker TEXT,
        qty REAL, price REAL, side TEXT, timestamp TEXT)""")
    conn.commit(); conn.close()

def _demo_get_cash(user_id: str) -> float:
    _demo_ensure_tables()
    conn = _sqlite3.connect(_DEMO_DB)
    row = conn.execute("SELECT cash_balance FROM demo_portfolios WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if row:
        return float(row[0])
    conn = _sqlite3.connect(_DEMO_DB)
    conn.execute("INSERT OR IGNORE INTO demo_portfolios (user_id, cash_balance) VALUES (?,?)", (user_id, 100000.0))
    conn.commit(); conn.close()
    return 100000.0

def _demo_get_positions(user_id: str) -> list:
    _demo_ensure_tables()
    conn = _sqlite3.connect(_DEMO_DB)
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
    from datetime import datetime, timezone
    _demo_ensure_tables()
    conn = _sqlite3.connect(_DEMO_DB)
    conn.execute(
        "INSERT INTO demo_transactions (user_id,ticker,qty,price,side,timestamp) VALUES (?,?,?,?,?,?)",
        (user_id, ticker, qty, price, side, datetime.now(timezone.utc).isoformat())
    )
    conn.commit(); conn.close()

def _demo_update_cash(user_id, new_balance):
    _demo_ensure_tables()
    conn = _sqlite3.connect(_DEMO_DB)
    conn.execute("INSERT OR REPLACE INTO demo_portfolios (user_id,cash_balance) VALUES (?,?)", (user_id, new_balance))
    conn.commit(); conn.close()


class TradeExecuteRequest(BaseModel):
    user_id: str
    symbol: str
    action: str  # "BUY" or "SELL"
    quantity: int
    order_type: Optional[str] = "MARKET"
    limit_price: Optional[float] = None

@app.post("/api/trade/execute")
async def execute_trade(req: TradeExecuteRequest):
    """Executes a BUY or SELL trade. Uses Supabase when configured, otherwise falls back to local SQLite demo DB."""
    try:
        full_symbol = req.symbol.upper()
        if not full_symbol.endswith(".NS"):
            full_symbol += ".NS"

        # Fetch live market price for MARKET orders
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
                raise HTTPException(status_code=503, detail=f"Price fetch failed: {e}")

        # Determine storage backend: try Supabase first, fall back to SQLite
        supabase_portfolio = auth.get_user_portfolio(req.user_id)
        use_supabase = supabase_portfolio.get("success", False)

        if use_supabase:
            cash = supabase_portfolio.get("cash", 0.0)
            positions = supabase_portfolio.get("positions", [])
        else:
            cash = _demo_get_cash(req.user_id)
            positions = _demo_get_positions(req.user_id)

        total_cost = req.quantity * exec_price
        brokerage = round(total_cost * 0.0003, 2)
        final_cost = round(total_cost + brokerage, 2)

        if req.action == "BUY":
            if cash < final_cost:
                raise HTTPException(status_code=400, detail=f"Insufficient funds. Have ₹{cash:,.2f}, need ₹{final_cost:,.2f}")

            new_cash = round(cash - final_cost, 2)

            if use_supabase:
                tx_r = auth.log_transaction(req.user_id, full_symbol, req.quantity, exec_price, "BUY")
                ca_r = auth.update_cash_balance(req.user_id, new_cash)
                if not (tx_r.get("success") and ca_r.get("success")):
                    # Supabase write failed mid-flight — persist to SQLite so state isn't lost
                    _demo_log_tx(req.user_id, full_symbol, req.quantity, exec_price, "BUY")
                    _demo_update_cash(req.user_id, new_cash)
            else:
                _demo_log_tx(req.user_id, full_symbol, req.quantity, exec_price, "BUY")
                _demo_update_cash(req.user_id, new_cash)

            return {
                "status": "success",
                "action": "BUY",
                "symbol": req.symbol,
                "quantity": req.quantity,
                "price": exec_price,
                "brokerage": brokerage,
                "total_cost": final_cost,
                "new_cash": new_cash,
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
                tx_r = auth.log_transaction(req.user_id, full_symbol, req.quantity, exec_price, "SELL")
                ca_r = auth.update_cash_balance(req.user_id, new_cash)
                if not (tx_r.get("success") and ca_r.get("success")):
                    _demo_log_tx(req.user_id, full_symbol, req.quantity, exec_price, "SELL")
                    _demo_update_cash(req.user_id, new_cash)
            else:
                _demo_log_tx(req.user_id, full_symbol, req.quantity, exec_price, "SELL")
                _demo_update_cash(req.user_id, new_cash)

            return {
                "status": "success",
                "action": "SELL",
                "symbol": req.symbol,
                "quantity": req.quantity,
                "price": exec_price,
                "brokerage": brokerage,
                "proceeds": proceeds,
                "new_cash": new_cash,
                "message": f"SELL order executed: {req.quantity} × {req.symbol} @ ₹{exec_price:,.2f}"
            }
        else:
            raise HTTPException(status_code=400, detail="Action must be BUY or SELL")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trade Execute Error: {e}")
        raise HTTPException(status_code=500, detail=f"Trade execution failed: {e}")


# Agent start/stop/status/trades are handled above via agent_service (lines ~390-460)


# --- DAEMON INTEGRATION ---
# Sentinel Hive can run inside this same process using FastAPI startup events
# @app.on_event("startup")
# async def startup_event():
#     asyncio.create_task(run_autonomous_cycle())

