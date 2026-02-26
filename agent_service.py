# -*- coding: utf-8 -*-
"""
Agent Service - FastAPI Integration for Autonomous Trading

Unified agent service that runs the REAL LangGraph multi-agent pipeline
(sentinel_hive.py) from within FastAPI, with live WebSocket streaming.

Architecture:
    Frontend → /api/agent/start → AgentService._autonomous_loop()
        → sentinel_hive.create_sentinel_graph() → LangGraph StateGraph
            → Supervisor (Gemini routing)
            → Scout (yfinance, sector-filtered)
            → Analyst (Gemini 2.5 Flash AI)
            → Risk (configurable thresholds)
            → Trader (broker_engine → SQLite/Supabase)
        → WebSocket broadcast → God Mode + Neural Feed UI
"""

import asyncio
import json
import queue
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent / "sentinel.db"


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class Position:
    symbol: str
    quantity: int
    average_price: float
    stop_loss: float = 0.0
    take_profit: float = 0.0
    entry_date: str = ""

    @property
    def current_price(self) -> float:
        return self.average_price

    @property
    def market_value(self) -> float:
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.average_price) * self.quantity


@dataclass
class Portfolio:
    user_id: str
    cash: float = 100000.0
    positions: Dict[str, Position] = field(default_factory=dict)

    def total_value(self) -> float:
        return self.cash + sum(p.market_value for p in self.positions.values())

    def to_dict(self) -> dict:
        return {
            "cash": self.cash,
            "positions": {
                symbol: {
                    "quantity": pos.quantity,
                    "average_price": pos.average_price,
                    "current_price": pos.current_price,
                    "market_value": pos.market_value,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "stop_loss": pos.stop_loss,
                    "take_profit": pos.take_profit,
                    "entry_date": pos.entry_date,
                }
                for symbol, pos in self.positions.items()
            },
            "total_value": self.total_value(),
        }


@dataclass
class AgentThought:
    agent_name: str
    message: str
    timestamp: str
    iteration: int = 0
    workflow_id: str = ""

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_name,
            "thought": self.message,
            "timestamp": self.timestamp,
            "iteration": self.iteration,
            "workflow_id": self.workflow_id,
        }


# ---------------------------------------------------------------------------
# Sector → stock mapping (shared with scout_agent)
# ---------------------------------------------------------------------------

SECTOR_STOCKS = {
    "IT":         ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
    "Banking":    ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS"],
    "Energy":     ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
    "Automobile": ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS"],
    "FMCG":       ["ITC.NS", "HINDUNILVR.NS", "BRITANNIA.NS"],
    "Pharma":     ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
    "Metals":     ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS"],
}


def _extract_agent_name(content: str) -> str:
    """Extract agent name from a LangGraph message like '👔 Supervisor: Next → ...'."""
    agents = ["Supervisor", "Scout", "Analyst", "Risk", "Trader", "System"]
    for name in agents:
        if name in content:
            return name
    return "System"


class AgentService:
    """
    Core agent service that runs the real LangGraph multi-agent pipeline.
    Integrates with FastAPI via WebSocket for real-time updates.
    """

    CYCLE_SLEEP = 300       # 5 min between cycles
    ERROR_SLEEP = 60        # 1 min after error
    MAX_ERRORS = 5          # pause after this many consecutive errors

    def __init__(self, user_id: str = "demo_user"):
        self.user_id = user_id
        self.status = AgentStatus.IDLE
        self.workflow_id = ""
        self.start_time: Optional[datetime] = None   # set when agent starts, cleared on stop
        self.current_thoughts: List[AgentThought] = []
        self.websocket_callback: Optional[Callable] = None
        self.portfolio = Portfolio(user_id=user_id, cash=100000.0)
        self.performance_stats: Dict[str, Any] = {}

        # User-configurable constraints (overridden by update_config / loaded from DB)
        self.risk_appetite = "Moderate"
        self.max_position_pct = 0.10
        self.allowed_sectors: List[str] = list(SECTOR_STOCKS.keys())

        # Thread-safe queue for sync→async thought bridging
        self._thought_queue: queue.Queue = queue.Queue()

        # Load persisted portfolio + saved settings
        self._load_portfolio()
        self._load_settings()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def update_config(self, settings: dict):
        """Apply user settings from the Control Center to the live agent."""
        self.risk_appetite = settings.get("risk_appetite", "Moderate")
        pct = settings.get("max_position_size", 10)
        self.max_position_pct = pct / 100.0
        sectors = settings.get("allowed_sectors", list(SECTOR_STOCKS.keys()))
        self.allowed_sectors = sectors if sectors else list(SECTOR_STOCKS.keys())

    def _load_settings(self):
        """Load saved settings from SQLite on startup."""
        try:
            conn = sqlite3.connect(DB_PATH)
            row = conn.execute(
                "SELECT risk_appetite, max_position_size, allowed_sectors "
                "FROM agent_settings WHERE user_id=?",
                (self.user_id,),
            ).fetchone()
            conn.close()
            if row:
                self.update_config({
                    "risk_appetite": row[0],
                    "max_position_size": row[1],
                    "allowed_sectors": json.loads(row[2] or "[]"),
                })
                logger.info(f"Loaded settings: {self.risk_appetite}, {self.max_position_pct:.0%}, {self.allowed_sectors}")
        except Exception as e:
            logger.debug(f"No saved settings found: {e}")

    # ------------------------------------------------------------------
    # WebSocket / broadcast
    # ------------------------------------------------------------------

    def set_websocket_callback(self, callback: Callable):
        """Set WebSocket callback for real-time updates."""
        self.websocket_callback = callback

    async def broadcast_thought(self, agent_name: str, message: str, iteration: int = 0):
        """Broadcast an agent thought to all connected WebSocket clients."""
        thought = AgentThought(
            agent_name=agent_name,
            message=message,
            timestamp=datetime.now().isoformat(),
            iteration=iteration,
            workflow_id=self.workflow_id,
        )
        self.current_thoughts.append(thought)
        self._log_agent_thought(thought)
        if self.websocket_callback:
            try:
                await self.websocket_callback(thought.to_dict())
            except Exception:
                pass

    def sync_broadcast(self, agent_name: str, message: str, iteration: int = 0):
        """Thread-safe broadcast (called from sync LangGraph nodes via callback)."""
        self._thought_queue.put((agent_name, message, iteration))

    async def _drain_thought_queue(self):
        """Drain queued thoughts from sync agent nodes and broadcast them."""
        while not self._thought_queue.empty():
            try:
                agent_name, message, iteration = self._thought_queue.get_nowait()
                await self.broadcast_thought(agent_name, message, iteration)
            except queue.Empty:
                break

    def _log_agent_thought(self, thought: AgentThought):
        """Log thought to SQLite database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "INSERT INTO agent_thoughts (agent_name, message, iteration, workflow_id) VALUES (?,?,?,?)",
                (thought.agent_name, thought.message, thought.iteration, thought.workflow_id),
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.debug(f"Thought log error: {e}")

    # ------------------------------------------------------------------
    # Autonomous mode start/stop
    # ------------------------------------------------------------------

    async def start_autonomous_mode(self):
        """Start the autonomous trading loop using the real LangGraph pipeline."""
        self.status = AgentStatus.RUNNING
        self.start_time = datetime.utcnow()
        self.workflow_id = f"auto-{uuid.uuid4().hex[:8]}"
        await self.broadcast_thought("System", "🚀 Autonomous mode started — LangGraph pipeline active")
        asyncio.create_task(self._autonomous_loop())

    async def stop_autonomous_mode(self):
        """Stop the autonomous trading loop."""
        self.status = AgentStatus.STOPPED
        self.start_time = None
        await self.broadcast_thought("System", "🛑 Autonomous mode stopped")

    # ------------------------------------------------------------------
    # The REAL autonomous loop — invokes LangGraph
    # ------------------------------------------------------------------

    async def _autonomous_loop(self):
        """Run the real LangGraph multi-agent pipeline in a continuous loop."""
        from sentinel_hive import create_sentinel_graph
        from sentinel_state import create_initial_state

        iteration = 0
        consecutive_errors = 0

        while self.status == AgentStatus.RUNNING:
            try:
                iteration += 1
                self.workflow_id = f"auto-{uuid.uuid4().hex[:8]}"

                await self.broadcast_thought(
                    "Supervisor",
                    f"━━━ Starting LangGraph cycle #{iteration} ━━━",
                    iteration,
                )

                # 1. Build initial state with user settings + portfolio
                state = create_initial_state()
                state["user_id"] = self.user_id
                state["user_settings"] = {
                    "risk_appetite": self.risk_appetite,
                    "max_position_pct": self.max_position_pct,
                    "allowed_sectors": self.allowed_sectors,
                }
                state["portfolio_snapshot"] = {
                    "cash": self.portfolio.cash,
                    "positions": [
                        {"symbol": s, "quantity": p.quantity, "average_price": p.average_price}
                        for s, p in self.portfolio.positions.items()
                    ],
                    "orders": [],
                }

                # Inject sync broadcast callback so agents can stream thoughts
                state["broadcast_callback"] = lambda name, msg, it=iteration: self.sync_broadcast(name, msg, it)

                # 2. Run LangGraph in a thread (it's synchronous)
                graph = create_sentinel_graph()
                final_state = await asyncio.to_thread(graph.invoke, state)

                # 3. Drain any queued thoughts from agent nodes
                await self._drain_thought_queue()

                # 4. Broadcast final results from state.messages
                for msg in final_state.get("messages", []):
                    content = msg.content if hasattr(msg, "content") else str(msg)
                    await self.broadcast_thought(
                        _extract_agent_name(content),
                        content,
                        iteration,
                    )

                # 5. Report summary
                ticker = final_state.get("current_ticker", "N/A")
                signal = final_state.get("analyst_signal", {}).get("signal", "N/A")
                confidence = final_state.get("analyst_signal", {}).get("confidence", 0.0)
                trade_status = final_state.get("trade_status", "PENDING")
                errors = final_state.get("errors", [])

                summary = (
                    f"Cycle #{iteration} complete | {ticker} | "
                    f"Signal: {signal} ({confidence:.0%}) | "
                    f"Trade: {trade_status} | Errors: {len(errors)}"
                )
                await self.broadcast_thought("System", summary, iteration)

                # Reload portfolio (broker_engine may have written to DB)
                self._load_portfolio()

                consecutive_errors = 0

                # 6. Wait before next cycle
                await self.broadcast_thought(
                    "System",
                    f"💤 Next cycle in {self.CYCLE_SLEEP // 60} minutes...",
                    iteration,
                )
                await asyncio.sleep(self.CYCLE_SLEEP)

            except Exception as e:
                consecutive_errors += 1
                await self.broadcast_thought(
                    "System",
                    f"❌ Cycle #{iteration} error: {str(e)[:200]}",
                    iteration,
                )
                logger.error(f"Autonomous loop error: {e}", exc_info=True)

                if consecutive_errors >= self.MAX_ERRORS:
                    await self.broadcast_thought(
                        "System",
                        f"⚠️ {consecutive_errors} consecutive errors — pausing agent",
                        iteration,
                    )
                    self.status = AgentStatus.PAUSED
                    break

                await asyncio.sleep(self.ERROR_SLEEP)

    # ------------------------------------------------------------------
    # Portfolio persistence
    # ------------------------------------------------------------------

    def _load_portfolio(self):
        """Load portfolio from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT cash_balance FROM portfolios WHERE user_id = ?", (self.user_id,))
            row = cursor.fetchone()
            if row:
                self.portfolio.cash = row[0]

            cursor.execute(
                "SELECT symbol, quantity, avg_price, stop_loss, take_profit, entry_date "
                "FROM positions WHERE user_id = ?",
                (self.user_id,),
            )
            self.portfolio.positions.clear()
            for row in cursor.fetchall():
                self.portfolio.positions[row[0]] = Position(
                    symbol=row[0],
                    quantity=row[1],
                    average_price=row[2],
                    stop_loss=row[3] or 0.0,
                    take_profit=row[4] or 0.0,
                    entry_date=row[5] or "",
                )

            conn.close()
        except Exception as e:
            logger.debug(f"Portfolio load: {e}")

    def _save_portfolio(self):
        """Save portfolio to database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""CREATE TABLE IF NOT EXISTS portfolios (
                user_id TEXT PRIMARY KEY, cash_balance REAL DEFAULT 100000.0)""")
            cursor.execute("""CREATE TABLE IF NOT EXISTS positions (
                user_id TEXT, symbol TEXT, quantity INTEGER, avg_price REAL,
                stop_loss REAL DEFAULT 0, take_profit REAL DEFAULT 0, entry_date TEXT,
                PRIMARY KEY (user_id, symbol))""")

            cursor.execute(
                "INSERT OR REPLACE INTO portfolios (user_id, cash_balance) VALUES (?, ?)",
                (self.user_id, self.portfolio.cash),
            )
            for symbol, pos in self.portfolio.positions.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO positions "
                    "(user_id, symbol, quantity, avg_price, stop_loss, take_profit, entry_date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (self.user_id, symbol, pos.quantity, pos.average_price,
                     pos.stop_loss, pos.take_profit, pos.entry_date),
                )

            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Portfolio save error: {e}")

    # ------------------------------------------------------------------
    # Query methods (called by FastAPI endpoints)
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        """Get current agent status."""
        return {
            "running": self.status == AgentStatus.RUNNING,
            "status": self.status.value,
            "workflow_id": self.workflow_id,
            "start_time": self.start_time.isoformat() + "Z" if self.start_time else None,
            "portfolio": self.portfolio.to_dict(),
            "performance": self.performance_stats,
            "recent_thoughts": [t.to_dict() for t in self.current_thoughts[-20:]],
        }

    def get_portfolio(self) -> dict:
        return self.portfolio.to_dict()

    def get_thoughts(self, limit: int = 50) -> List[dict]:
        """Get recent agent thoughts from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT agent_name, message, timestamp, iteration, workflow_id "
                "FROM agent_thoughts ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {"agent": r[0], "thought": r[1], "timestamp": r[2], "iteration": r[3], "workflow_id": r[4]}
                for r in rows
            ]
        except Exception:
            return []

    def get_trade_history(self, limit: int = 50) -> List[dict]:
        """Get trade history from database."""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ticker, side, quantity, price, total_value, status, timestamp "
                "FROM trade_history ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            conn.close()
            return [
                {"symbol": r[0], "side": r[1], "quantity": r[2], "price": r[3],
                 "total_value": r[4], "status": r[5], "timestamp": r[6]}
                for r in rows
            ]
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_agent_service: Optional[AgentService] = None


def get_agent_service(user_id: str = "demo_user") -> AgentService:
    """Get or create the global agent service."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService(user_id=user_id)
    return _agent_service
