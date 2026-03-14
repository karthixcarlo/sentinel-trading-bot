# -*- coding: utf-8 -*-
"""
Sentinel Hive - LangGraph Multi-Agent Trading System

This is the main orchestration engine that wires all agents together
using LangGraph's StateGraph.

Architecture:
    Supervisor → Scout → Analyst → Risk → Trader → (loop back to Supervisor)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END
from typing import Literal

from agents.sentinel_state import SentinelState, create_initial_state
from agents.supervisor import supervisor_node
from agents.scout_agent import scout_node
from agents.analyst_agent import analyst_node
from agents.risk_manager import risk_node
from agents.trader_agent import trader_node


def route_workflow(state: SentinelState) -> Literal["scout", "analyst", "risk", "trader", "__end__"]:
    """
    Routing function for LangGraph conditional edges
    
    Routes based on supervisor's decision in state.next_agent
    
    Args:
        state: Current SentinelState
        
    Returns:
        str: Next node name or END
    """
    next_agent = state.get('next_agent', 'scout').lower()
    
    # Map to node names
    if next_agent == 'finish':
        return END
    elif next_agent in ['scout', 'analyst', 'risk', 'trader']:
        return next_agent
    else:
        # Default fallback
        return 'scout'


def create_sentinel_graph():
    """
    Create the LangGraph multi-agent system
    
    Returns:
        Compiled StateGraph ready for execution
    """
    
    print("🏗️  Building Sentinel Hive graph...")
    
    # 1. Initialize StateGraph
    workflow = StateGraph(SentinelState)
    
    # 2. Add all agent nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("scout", scout_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("risk", risk_node)
    workflow.add_node("trader", trader_node)
    
    # 3. Define workflow routing
    # Start with supervisor
    workflow.set_entry_point("supervisor")
    
    # Supervisor makes decisions using conditional edges
    workflow.add_conditional_edges(
        "supervisor",
        route_workflow,
        {
            "scout": "scout",
            "analyst": "analyst",
            "risk": "risk",
            "trader": "trader",
            END: END
        }
    )
    
    # All agents return to supervisor for next decision
    workflow.add_edge("scout", "supervisor")
    workflow.add_edge("analyst", "supervisor")
    workflow.add_edge("risk", "supervisor")
    workflow.add_edge("trader", "supervisor")
    
    # 4. Compile the graph
    app = workflow.compile()
    
    print("✅ Sentinel Hive graph compiled successfully!")
    
    return app


def run_workflow(initial_state: SentinelState = None, max_iterations: int = 15):
    """
    Run a single workflow execution
    
    Args:
        initial_state: Starting state (or None to create fresh)
        max_iterations: Safety limit to prevent infinite loops
        
    Returns:
        Final state after workflow completion
    """
    
    if initial_state is None:
        initial_state = create_initial_state()
        # Add mock portfolio
        initial_state['portfolio_snapshot'] = {
            'cash': 100000,
            'positions': [],
            'orders': []
        }
    
    # Create graph
    graph = create_sentinel_graph()
    
    print("\n🚀 Starting Sentinel Hive workflow...\n")
    print("=" * 60)
    
    # Run the graph
    final_state = graph.invoke(initial_state)
    
    print("=" * 60)
    print("\n🏁 Workflow complete!")
    
    return final_state


# Test function
if __name__ == "__main__":
    print("Testing Sentinel Hive LangGraph System...")
    
    # Create initial state
    state = create_initial_state()
    state['portfolio_snapshot'] = {
        'cash': 100000,
        'positions': [],
        'orders': []
    }
    
    # Run workflow
    result = run_workflow(state, max_iterations=10)
    
    # Display results
    print("\n" + "=" * 60)
    print("📊 WORKFLOW RESULTS")
    print("=" * 60)
    print(f"Final Ticker: {result.get('current_ticker', 'None')}")
    print(f"Analyst Signal: {result.get('analyst_signal', {}).get('signal', 'None')}")
    print(f"Confidence: {result.get('analyst_signal', {}).get('confidence', 0.0):.0%}")
    print(f"Risk Approved: {result.get('risk_approval', False)}")
    print(f"Trade Status: {result.get('trade_status', 'PENDING')}")
    print(f"Iterations: {result.get('iteration_count', 0)}")
    print(f"Errors: {len(result.get('errors', []))}")
    
    print("\n📝 Agent Messages:")
    print("-" * 60)
    for i, msg in enumerate(result.get('messages', []), 1):
        print(f"{i}. {msg.content}")
    
    print("\n✅ Test complete!")
