# -*- coding: utf-8 -*-
"""
Trader Agent - Executes trades

Responsibility: Execute approved trades
Logic:
    1. Calculate position size based on risk
    2. Get current market price
    3. Place order (paper trading mode)
    4. Update portfolio
    5. Update state.trade_status
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from datetime import datetime
from langchain_core.messages import AIMessage

from sentinel_state import SentinelState


# Trading configuration
BROKERAGE_PERCENT = 0.0003  # 0.03% brokerage
MAX_POSITION_SIZE_PERCENT = 0.02  # 2% of capital


def get_current_price(ticker: str) -> float:
    """
    Fetch current market price for a stock
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE.NS")
        
    Returns:
        float: Current price
    """
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        
        if len(data) == 0:
            return 0.0
        
        return float(data['Close'].iloc[-1])
        
    except Exception as e:
        print(f"❌ Price fetch error: {e}")
        return 0.0


def calculate_position_size(cash: float, price: float, max_percent: float = 0.02) -> int:
    """
    Calculate how many shares to buy
    
    Args:
        cash: Available cash
        price: Stock price
        max_percent: Max % of capital to risk
        
    Returns:
        int: Number of shares
    """
    max_investment = cash * max_percent
    shares = int(max_investment / price)
    
    return max(shares, 1)  # At least 1 share


def execute_trade(ticker: str, signal: str, quantity: int, price: float) -> dict:
    """
    Execute a paper trade
    
    Args:
        ticker: Stock symbol
        signal: BUY or SELL
        quantity: Number of shares
        price: Execution price
        
    Returns:
        dict: Order details
    """
    total_value = quantity * price
    brokerage = total_value * BROKERAGE_PERCENT
    
    order = {
        'symbol': ticker,
        'side': signal,
        'quantity': quantity,
        'price': price,
        'total_value': total_value,
        'brokerage': brokerage,
        'net_amount': total_value + brokerage,
        'timestamp': datetime.now().isoformat(),
        'status': 'EXECUTED'
    }
    
    return order


def trader_node(state: SentinelState) -> SentinelState:
    """
    Trader Agent - Execute the trade
    
    Process:
    1. Verify risk approval
    2. Get current price
    3. Calculate position size
    4. Execute order
    5. Update portfolio
    6. Update state
    
    Args:
        state: Current SentinelState
        
    Returns:
        Updated SentinelState with trade_status set
    """
    
    # Check risk approval
    if not state.get('risk_approval', False):
        state['trade_status'] = "REJECTED"
        state['messages'].append(
            AIMessage(content="⚡ Trader: Trade BLOCKED - Risk Manager didn't approve")
        )
        print("❌ Trader: Blocked by Risk Manager")
        return state
    
    ticker = state.get('current_ticker', '')
    signal_data = state.get('analyst_signal', {})
    portfolio = state.get('portfolio_snapshot', {})
    
    signal = signal_data.get('signal', 'WAIT')
    
    print(f"⚡ Trader Agent: Executing {signal} order for {ticker}...")
    
    try:
        # 1. Get current price
        current_price = get_current_price(ticker)
        
        if current_price == 0:
            state['trade_status'] = "FAILED"
            state['errors'].append(f"Trader: Could not get price for {ticker}")
            state['messages'].append(
                AIMessage(content=f"⚡ Trader: FAILED - Could not fetch price for {ticker}")
            )
            return state
        
        # 2. Calculate position
        cash = portfolio.get('cash', 100000)
        quantity = calculate_position_size(cash, current_price, MAX_POSITION_SIZE_PERCENT)
        
        # 3. Execute order
        order = execute_trade(ticker, signal, quantity, current_price)
        
        # 4. Update state
        state['trade_status'] = "EXECUTED"
        
        # 5. Log message
        ticker_clean = ticker.replace('.NS', '')
        state['messages'].append(
            AIMessage(
                content=f"⚡ Trader: ✅ EXECUTED {signal} | {ticker_clean} x {quantity} @ ₹{current_price:,.2f} | Total: ₹{order['net_amount']:,.2f}"
            )
        )
        
        print(f"✅ Trader: Executed {signal} {quantity} shares @ ₹{current_price:,.2f}")
        
        # Store order in state for portfolio update
        if 'executed_order' not in state:
            state['executed_order'] = order
        
    except Exception as e:
        # Error handling
        state['trade_status'] = "FAILED"
        state['errors'].append(f"Trader error: {str(e)}")
        state['messages'].append(
            AIMessage(content=f"⚡ Trader: FAILED - {str(e)}")
        )
        print(f"❌ Trader error: {e}")
    
    return state


# Test function
if __name__ == "__main__":
    from sentinel_state import create_initial_state
    
    print("Testing Trader Agent...")
    
    # Test 1: Approved trade
    print("\n=== Test 1: Approved Trade ===")
    state = create_initial_state()
    state['current_ticker'] = "RELIANCE.NS"
    state['risk_approval'] = True
    state['analyst_signal'] = {
        'signal': 'BUY',
        'confidence': 0.85,
        'reasoning': 'Strong signals'
    }
    state['portfolio_snapshot'] = {'cash': 100000}
    
    result = trader_node(state)
    print(f"Trade Status: {result['trade_status']}")
    
    # Test 2: Rejected by risk
    print("\n=== Test 2: Risk Rejected ===")
    state2 = create_initial_state()
    state2['current_ticker'] = "TCS.NS"
    state2['risk_approval'] = False  # Risk rejected
    state2['analyst_signal'] = {
        'signal': 'BUY',
        'confidence': 0.55
    }
    state2['portfolio_snapshot'] = {'cash': 100000}
    
    result2 = trader_node(state2)
    print(f"Trade Status: {result2['trade_status']}")
    
    print("\n✅ All tests complete!")
