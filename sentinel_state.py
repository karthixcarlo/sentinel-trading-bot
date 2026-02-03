# -*- coding: utf-8 -*-
"""
Sentinel State - Shared state for LangGraph multi-agent system
"""

from typing import TypedDict, List, Annotated, Dict, Any
from langchain_core.messages import BaseMessage
import operator


class SentinelState(TypedDict):
    """
    Shared state that flows through all agents in the Sentinel Hive
    
    This state is passed between agents and updated at each step.
    LangGraph manages state transitions automatically.
    """
    
    # Message history (agent conversations)
    messages: Annotated[List[BaseMessage], operator.add]
    
    # Current workflow data
    current_ticker: str              # e.g., "RELIANCE.NS"
    market_data: Dict[str, Any]      # OHLCV, technicals, price
    analyst_signal: Dict[str, Any]   # {signal, confidence, reasoning, stop_loss, take_profit}
    risk_approval: bool              # Risk Manager's decision
    trade_status: str                # "PENDING", "EXECUTED", "REJECTED"
    
    # Control flow
    next_agent: str                  # Supervisor's decision on next agent
    iteration_count: int             # Loop counter (prevent infinite loops)
    
    # Error tracking
    errors: List[str]                # Error log for debugging
    
    # Metadata
    timestamp: str                   # Current timestamp
    portfolio_snapshot: Dict[str, Any]  # Current portfolio state


def create_initial_state() -> SentinelState:
    """
    Create a fresh initial state for a new workflow run
    
    Returns:
        SentinelState: Clean initial state
    """
    from datetime import datetime
    
    return SentinelState(
        messages=[],
        current_ticker="",
        market_data={},
        analyst_signal={},
        risk_approval=False,
        trade_status="PENDING",
        next_agent="scout",  # Always start with scout
        iteration_count=0,
        errors=[],
        timestamp=datetime.now().isoformat(),
        portfolio_snapshot={}
    )
