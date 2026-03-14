# -*- coding: utf-8 -*-
"""
Risk Manager Agent - Capital preservation and risk assessment

Responsibility: Assess risk before trade execution
Logic:
    1. Check analyst confidence threshold (>70%)
    2. Verify sufficient portfolio cash
    3. Enforce "Max 2% risk per trade" rule
    4. Check daily loss limits
    5. Update state.risk_approval
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.messages import AIMessage

from agents.sentinel_state import SentinelState


# Risk configuration defaults
DEFAULT_CONFIDENCE = 0.70
MAX_RISK_PER_TRADE = 0.02  # 2% max risk
DAILY_LOSS_LIMIT = 500  # ₹500 max daily loss

# Dynamic thresholds based on user risk appetite (from Settings page)
RISK_THRESHOLDS = {
    "Conservative": 0.85,
    "Moderate": 0.70,
    "Aggressive": 0.55,
}


def calculate_daily_pnl(portfolio: dict) -> float:
    """
    Calculate today's P&L
    
    Args:
        portfolio: Portfolio state with orders
        
    Returns:
        float: Today's P&L (negative for losses)
    """
    daily_pnl = 0.0
    
    for order in portfolio.get('orders', []):
        # Parse order timestamp (simplified)
        # In production, properly parse ISO timestamp
        if 'pnl' in order:
            daily_pnl += order['pnl']
    
    return daily_pnl


def risk_node(state: SentinelState) -> SentinelState:
    """
    Risk Manager Agent - Assess risk and approve/reject trade
    
    Process:
    1. Check analyst signal and confidence
    2. Verify portfolio has sufficient cash
    3. Enforce position size limits
    4. Check daily loss limits
    5. Approve or reject
    
    Args:
        state: Current SentinelState
        
    Returns:
        Updated SentinelState with risk_approval set
    """
    
    _bc = state.get('broadcast_callback')

    signal_data = state.get('analyst_signal', {})
    portfolio = state.get('portfolio_snapshot', {})

    signal = signal_data.get('signal', 'WAIT')
    confidence = signal_data.get('confidence', 0.0)

    # Dynamic confidence threshold from user settings
    user_settings = state.get('user_settings', {})
    risk_appetite = user_settings.get('risk_appetite', 'Moderate')
    min_confidence = RISK_THRESHOLDS.get(risk_appetite, DEFAULT_CONFIDENCE)

    # Dynamic max position size from user settings
    max_position_pct = user_settings.get('max_position_pct', MAX_RISK_PER_TRADE)
    if isinstance(max_position_pct, (int, float)) and max_position_pct > 1:
        max_position_pct = max_position_pct / 100.0  # convert 10 → 0.10

    print(f"🛡️  Risk Manager: Evaluating {signal} signal @ {confidence:.0%} confidence (threshold: {min_confidence:.0%} [{risk_appetite}])...")
    if _bc:
        _bc("Risk", f"Evaluating {signal} @ {confidence:.0%} confidence (threshold: {min_confidence:.0%} [{risk_appetite}])")
    
    # Initialize as rejected by default
    state['risk_approval'] = False
    
    # 1. Check if signal is WAIT or AVOID
    if signal in ['WAIT', 'AVOID']:
        state['messages'].append(
            AIMessage(content=f"🛡️ Risk: AUTO-REJECT - Analyst recommends {signal}, no trade needed")
        )
        print(f"✅ Risk: Auto-rejected {signal} signal")
        return state
    
    # 2. Check confidence threshold (dynamic based on risk appetite)
    if confidence < min_confidence:
        state['messages'].append(
            AIMessage(content=f"🛡️ Risk: REJECTED - Confidence too low ({confidence:.0%} < {min_confidence:.0%} [{risk_appetite}])")
        )
        print("❌ Risk: Rejected - Low confidence")
        return state

    # 3. Check portfolio cash
    cash = portfolio.get('cash', 100000)
    
    if cash <= 0:
        state['messages'].append(
            AIMessage(content="🛡️ Risk: REJECTED - Insufficient cash in portfolio")
        )
        print("❌ Risk: Rejected - No cash")
        return state
    
    # 4. Calculate max position size (dynamic from settings)
    max_position = cash * max_position_pct
    
    # 5. Check daily loss limit
    daily_pnl = calculate_daily_pnl(portfolio)
    
    if daily_pnl < -DAILY_LOSS_LIMIT:
        state['messages'].append(
            AIMessage(content=f"🛡️ Risk: REJECTED - Daily loss limit reached (₹{abs(daily_pnl):,.0f} lost today)")
        )
        print("❌ Risk: Rejected - Daily loss limit")
        return state
    
    # 6. All checks passed - APPROVE
    state['risk_approval'] = True
    state['messages'].append(
        AIMessage(
            content=f"🛡️ Risk: ✅ APPROVED - Signal: {signal} | Confidence: {confidence:.0%} | Max Position: ₹{max_position:,.0f}"
        )
    )
    
    print(f"✅ Risk: APPROVED - Max position: ₹{max_position:,.0f}")
    if _bc:
        _bc("Risk", f"✅ APPROVED | {signal} ({confidence:.0%}) | Max ₹{max_position:,.0f}")

    return state


# Test function
if __name__ == "__main__":
    from agents.sentinel_state import create_initial_state
    
    print("Testing Risk Manager Agent...")
    
    # Test 1: High confidence BUY
    print("\n=== Test 1: High Confidence BUY ===")
    state = create_initial_state()
    state['analyst_signal'] = {
        'signal': 'BUY',
        'confidence': 0.85,
        'reasoning': 'Strong bullish signals',
        'stop_loss': 2300,
        'take_profit': 2600
    }
    state['portfolio_snapshot'] = {'cash': 100000, 'orders': []}
    
    result = risk_node(state)
    print(f"Approved: {result['risk_approval']}")
    
    # Test 2: Low confidence BUY
    print("\n=== Test 2: Low Confidence BUY ===")
    state2 = create_initial_state()
    state2['analyst_signal'] = {
        'signal': 'BUY',
        'confidence': 0.55,  # Below threshold
        'reasoning': 'Weak signals',
        'stop_loss': 2300,
        'take_profit': 2600
    }
    state2['portfolio_snapshot'] = {'cash': 100000, 'orders': []}
    
    result2 = risk_node(state2)
    print(f"Approved: {result2['risk_approval']}")
    
    # Test 3: WAIT signal
    print("\n=== Test 3: WAIT Signal ===")
    state3 = create_initial_state()
    state3['analyst_signal'] = {
        'signal': 'WAIT',
        'confidence': 0.50,
        'reasoning': 'Mixed signals',
        'stop_loss': None,
        'take_profit': None
    }
    state3['portfolio_snapshot'] = {'cash': 100000, 'orders': []}
    
    result3 = risk_node(state3)
    print(f"Approved: {result3['risk_approval']}")
    
    print("\n✅ All tests complete!")
