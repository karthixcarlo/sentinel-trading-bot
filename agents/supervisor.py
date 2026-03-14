# -*- coding: utf-8 -*-
"""
Supervisor Agent - Orchestrates the multi-agent workflow

Responsibility: Decide which agent runs next
Logic:
    - Uses Gemini Pro to make intelligent routing decisions
    - Follows defined workflow rules
    - Prevents infinite loops
    - Handles errors gracefully
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

from agents.sentinel_state import SentinelState

load_dotenv()

# Supervisor system prompt
SUPERVISOR_PROMPT = """You are the Investment Manager supervising an AI trading team.

Your team of specialized agents:
- **Scout**: Finds trading opportunities by scanning the market
- **Analyst**: Analyzes stocks using AI and technical indicators
- **Risk**: Assesses risk and approves/rejects trades
- **Trader**: Executes approved orders

**Decision Rules (Follow EXACTLY):**

1. If no ticker selected → output "Scout"
2. If ticker exists but no analyst_signal → output "Analyst"
3. If analyst_signal.signal == "BUY" and confidence >= 0.7 → output "Risk"
4. If analyst_signal.signal == "WAIT" or "AVOID" → output "Scout" (find new opportunity)
5. If risk_approval == True → output "Trader"
6. If trade_status == "EXECUTED" or "REJECTED" → output "Scout" (find next opportunity)
7. If iteration_count > 10 → output "FINISH" (prevent infinite loops)
8. If errors exist → output "Scout" (retry with new ticker)

**CRITICAL:** Respond with ONLY ONE WORD - the next agent name or "FINISH".
Valid responses: Scout, Analyst, Risk, Trader, FINISH

Do NOT explain your reasoning. Just output the agent name.
"""


def supervisor_node(state: SentinelState) -> SentinelState:
    """
    Supervisor Agent - Decides which agent runs next
    
    Uses Gemini Pro to intelligently route workflow based on current state
    
    Args:
        state: Current SentinelState
        
    Returns:
        Updated SentinelState with next_agent set
    """
    
    # Prepare context summary
    context = f"""
Current State:
- Ticker: {state.get('current_ticker', 'None')}
- Analyst Signal: {state.get('analyst_signal', {}).get('signal', 'None')}
- Analyst Confidence: {state.get('analyst_signal', {}).get('confidence', 0.0):.0%}
- Risk Approval: {state.get('risk_approval', False)}
- Trade Status: {state.get('trade_status', 'PENDING')}
- Iteration: {state.get('iteration_count', 0)}
- Errors: {len(state.get('errors', []))}
"""
    
    _bc = state.get('broadcast_callback')

    print(f"👔 Supervisor: Evaluating workflow state (iteration {state.get('iteration_count', 0)})...")
    if _bc:
        _bc("Supervisor", f"Evaluating workflow state (iteration {state.get('iteration_count', 0)})")

    try:
        # Call Gemini for decision
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",  # Use stable model
            temperature=0.0  # Deterministic decisions
        )
        
        messages = [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=context)
        ]
        
        response = llm.invoke(messages)
        next_agent = response.content.strip().lower()
        
        # Validate response
        valid_agents = ['scout', 'analyst', 'risk', 'trader', 'finish']
        
        if next_agent not in valid_agents:
            # Fallback logic if LLM returns invalid response
            print(f"⚠️ Supervisor: Invalid response '{next_agent}', using fallback logic")
            next_agent = fallback_decision(state)
        
        # Update state
        state['next_agent'] = next_agent
        state['iteration_count'] = state.get('iteration_count', 0) + 1
        
        # Log decision
        emoji_map = {
            'scout': '🕵️',
            'analyst': '🧠',
            'risk': '🛡️',
            'trader': '⚡',
            'finish': '🏁'
        }
        
        emoji = emoji_map.get(next_agent, '🤖')
        state['messages'].append(
            HumanMessage(content=f"👔 Supervisor: Next → {emoji} {next_agent.upper()}")
        )
        
        print(f"✅ Supervisor: Routing to {next_agent.upper()}")
        if _bc:
            _bc("Supervisor", f"Routing → {emoji} {next_agent.upper()}")
        
    except Exception as e:
        # Error handling - use fallback logic
        print(f"❌ Supervisor error: {e}")
        next_agent = fallback_decision(state)
        state['next_agent'] = next_agent
        state['errors'].append(f"Supervisor error: {str(e)}")
    
    return state


def fallback_decision(state: SentinelState) -> str:
    """
    Deterministic fallback logic when LLM fails
    
    Args:
        state: Current SentinelState
        
    Returns:
        str: Next agent name
    """
    # Check iteration limit
    if state.get('iteration_count', 0) > 10:
        return 'finish'
    
    # Check if ticker is selected
    if not state.get('current_ticker'):
        return 'scout'
    
    # Check if analyst has run
    if not state.get('analyst_signal'):
        return 'analyst'
    
    # Check analyst decision
    signal = state.get('analyst_signal', {}).get('signal', 'WAIT')
    confidence = state.get('analyst_signal', {}).get('confidence', 0.0)
    
    if signal in ['WAIT', 'AVOID']:
        return 'scout'
    
    # --- DYNAMIC RULES ENGINE INTEGRATION ---
    threshold = 0.7 # Default Moderate
    if 'user_settings' in state and state['user_settings']:
        risk = state['user_settings'].get('risk_appetite', 'Moderate')
        if risk == 'Conservative':
            threshold = 0.85
        elif risk == 'Aggressive':
            threshold = 0.55
            
    if signal == 'BUY' and confidence >= threshold:
        # Check if risk has approved
        if state.get('risk_approval') is False and state.get('trade_status') == 'PENDING':
            return 'risk'
        
        # If risk approved, execute trade
        if state.get('risk_approval') is True and state.get('trade_status') == 'PENDING':
            return 'trader'
    
    # After trade execution or rejection
    if state.get('trade_status') in ['EXECUTED', 'REJECTED']:
        return 'scout'
    
    # Default: find new opportunity
    return 'scout'


# Test function
if __name__ == "__main__":
    from agents.sentinel_state import create_initial_state
    
    print("Testing Supervisor Agent...")
    
    # Test 1: Initial state - should route to Scout
    print("\n=== Test 1: Initial State ===")
    state1 = create_initial_state()
    result1 = supervisor_node(state1)
    print(f"Decision: {result1['next_agent']}")
    assert result1['next_agent'] == 'scout', "Should route to Scout initially"
    
    # Test 2: Ticker found - should route to Analyst
    print("\n=== Test 2: Ticker Found ===")
    state2 = create_initial_state()
    state2['current_ticker'] = "RELIANCE.NS"
    result2 = supervisor_node(state2)
    print(f"Decision: {result2['next_agent']}")
    assert result2['next_agent'] == 'analyst', "Should route to Analyst when ticker exists"
    
    # Test 3: BUY signal with high confidence - should route to Risk
    print("\n=== Test 3: BUY Signal ===")
    state3 = create_initial_state()
    state3['current_ticker'] = "RELIANCE.NS"
    state3['analyst_signal'] = {
        'signal': 'BUY',
        'confidence': 0.85,
        'reasoning': 'Strong signals'
    }
    result3 = supervisor_node(state3)
    print(f"Decision: {result3['next_agent']}")
    assert result3['next_agent'] == 'risk', "Should route to Risk for BUY signal"
    
    # Test 4: WAIT signal - should route back to Scout
    print("\n=== Test 4: WAIT Signal ===")
    state4 = create_initial_state()
    state4['current_ticker'] = "TCS.NS"
    state4['analyst_signal'] = {
        'signal': 'WAIT',
        'confidence': 0.50,
        'reasoning': 'Mixed signals'
    }
    result4 = supervisor_node(state4)
    print(f"Decision: {result4['next_agent']}")
    assert result4['next_agent'] == 'scout', "Should route to Scout for WAIT signal"
    
    print("\n✅ All supervisor tests passed!")
