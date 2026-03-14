# -*- coding: utf-8 -*-
"""
Database Manager - Stores agent thoughts and trading history

Provides persistence for:
- Agent conversation logs (for God Mode UI)
- Trade execution history
- Portfolio state snapshots
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd


# Database file location
DB_PATH = Path(__file__).parent.parent / "sentinel.db"


def init_database():
    """
    Initialize database schema
    
    Creates tables for agent thoughts and trade history
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Agent thoughts table (for God Mode UI)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_thoughts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            agent_name TEXT NOT NULL,
            message TEXT NOT NULL,
            state_snapshot TEXT,
            iteration INTEGER,
            workflow_id TEXT
        )
    ''')
    
    # Trade history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            total_value REAL NOT NULL,
            brokerage REAL NOT NULL,
            status TEXT NOT NULL,
            workflow_id TEXT
        )
    ''')
    
    # Workflow execution log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id TEXT UNIQUE NOT NULL,
            start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            end_time DATETIME,
            status TEXT NOT NULL,
            final_ticker TEXT,
            final_signal TEXT,
            trade_executed BOOLEAN,
            error_count INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")


def log_agent_thought(
    agent_name: str,
    message: str,
    state: Dict[str, Any] = None,
    iteration: int = 0,
    workflow_id: str = None
):
    """
    Log an agent's message/thought to database
    
    Args:
        agent_name: Name of the agent (Scout, Analyst, Risk, Trader, Supervisor)
        message: The message content
        state: Current state snapshot (optional)
        iteration: Current iteration number
        workflow_id: Unique workflow execution ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    state_json = json.dumps(state) if state else None
    
    cursor.execute('''
        INSERT INTO agent_thoughts 
        (agent_name, message, state_snapshot, iteration, workflow_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (agent_name, message, state_json, iteration, workflow_id))
    
    conn.commit()
    conn.close()


def log_trade(
    ticker: str,
    side: str,
    quantity: int,
    price: float,
    total_value: float,
    brokerage: float,
    status: str,
    workflow_id: str = None
):
    """
    Log a trade execution to database
    
    Args:
        ticker: Stock symbol
        side: BUY or SELL
        quantity: Number of shares
        price: Execution price
        total_value: Total order value
        brokerage: Brokerage fee
        status: EXECUTED, REJECTED, FAILED
        workflow_id: Unique workflow execution ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trade_history 
        (ticker, side, quantity, price, total_value, brokerage, status, workflow_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticker, side, quantity, price, total_value, brokerage, status, workflow_id))
    
    conn.commit()
    conn.close()


def start_workflow(workflow_id: str):
    """
    Log the start of a workflow execution
    
    Args:
        workflow_id: Unique workflow execution ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO workflow_runs (workflow_id, status)
        VALUES (?, 'RUNNING')
    ''', (workflow_id,))
    
    conn.commit()
    conn.close()


def end_workflow(
    workflow_id: str,
    status: str,
    final_ticker: str = None,
    final_signal: str = None,
    trade_executed: bool = False,
    error_count: int = 0
):
    """
    Log the end of a workflow execution
    
    Args:
        workflow_id: Unique workflow execution ID
        status: COMPLETED, FAILED, STOPPED
        final_ticker: Last ticker analyzed
        final_signal: Final trading signal
        trade_executed:Whether trade was executed
        error_count: Number of errors encountered
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE workflow_runs 
        SET end_time = CURRENT_TIMESTAMP,
            status = ?,
            final_ticker = ?,
            final_signal = ?,
            trade_executed = ?,
            error_count = ?
        WHERE workflow_id = ?
    ''', (status, final_ticker, final_signal, trade_executed, error_count, workflow_id))
    
    conn.commit()
    conn.close()


def get_recent_thoughts(limit: int = 100) -> pd.DataFrame:
    """
    Get recent agent thoughts for God Mode UI
    
    Args:
        limit: Number of recent thoughts to retrieve
        
    Returns:
        DataFrame with agent thoughts
    """
    conn = sqlite3.connect(DB_PATH)
    
    df = pd.read_sql_query(f'''
        SELECT 
            timestamp,
            agent_name,
            message,
            iteration,
            workflow_id
        FROM agent_thoughts
        ORDER BY timestamp DESC
        LIMIT {limit}
    ''', conn)
    
    conn.close()
    
    return df


def get_recent_trades(limit: int = 50) -> pd.DataFrame:
    """
    Get recent trade history
    
    Args:
        limit: Number of recent trades to retrieve
        
    Returns:
        DataFrame with trade history
    """
    conn = sqlite3.connect(DB_PATH)
    
    df = pd.read_sql_query(f'''
        SELECT *
        FROM trade_history
        ORDER BY timestamp DESC
        LIMIT {limit}
    ''', conn)
    
    conn.close()
    
    return df


def get_workflow_stats() -> Dict[str, Any]:
    """
    Get workflow execution statistics
    
    Returns:
        Dict with workflow stats
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total runs
    cursor.execute('SELECT COUNT(*) FROM workflow_runs')
    total_runs = cursor.fetchone()[0]
    
    # Successful trades
    cursor.execute('SELECT COUNT(*) FROM workflow_runs WHERE trade_executed = 1')
    successful_trades = cursor.fetchone()[0]
    
    # Average errors per run
    cursor.execute('SELECT AVG(error_count) FROM workflow_runs')
    avg_errors = cursor.fetchone()[0] or 0
    
    # Recent runs
    cursor.execute('''
        SELECT workflow_id, status, final_signal, trade_executed
        FROM workflow_runs
        ORDER BY start_time DESC
        LIMIT 10
    ''')
    recent_runs = cursor.fetchall()
    
    conn.close()
    
    return {
        'total_runs': total_runs,
        'successful_trades': successful_trades,
        'avg_errors': round(avg_errors, 2),
        'recent_runs': recent_runs
    }


def clear_old_data(days: int = 30):
    """
    Clear agent thoughts older than specified days
    
    Args:
        days: Number of days to keep
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM agent_thoughts
        WHERE timestamp < datetime('now', '-' || ? || ' days')
    ''', (days,))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"✅ Deleted {deleted} old agent thoughts")


# Auto-initialize on import
init_database()


if __name__ == "__main__":
    # Test database
    print("Testing database...")
    
    # Log some test thoughts
    log_agent_thought("Scout", "Found RELIANCE.NS (+5.2%)", iteration=1, workflow_id="test-001")
    log_agent_thought("Analyst", "BUY signal with 85% confidence", iteration=1, workflow_id="test-001")
    log_agent_thought("Risk", "APPROVED - Max position ₹2,000", iteration=1, workflow_id="test-001")
    log_agent_thought("Trader", "EXECUTED BUY 1 share @ ₹2,450", iteration=1, workflow_id="test-001")
    
    # Log a test trade
    log_trade("RELIANCE.NS", "BUY", 1, 2450.0, 2450.0, 0.74, "EXECUTED", "test-001")
    
    # Get recent thoughts
    thoughts = get_recent_thoughts(10)
    print("\n📝 Recent Thoughts:")
    print(thoughts)
    
    # Get stats
    stats = get_workflow_stats()
    print("\n📊 Workflow Stats:")
    print(stats)
    
    print("\n✅ Database test complete!")
