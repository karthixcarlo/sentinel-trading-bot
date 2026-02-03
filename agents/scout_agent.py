# -*- coding: utf-8 -*-
"""
Scout Agent - Finds trading opportunities by scanning the market

Responsibility: Market scanning and opportunity discovery
Logic:
    1. Fetch top gainers/losers/active stocks from NSE
    2. Filter out stocks already traded today
    3. Select the highest confidence opportunity
    4. Update state.current_ticker
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from typing import List
from langchain_core.messages import HumanMessage

from sentinel_state import SentinelState


# NSE Top stocks universe
NSE_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "TITAN.NS",
    "SUNPHARMA.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS", "WIPRO.NS",
    "HCLTECH.NS", "TATASTEEL.NS", "TATAMOTORS.NS", "ADANIPORTS.NS", "ONGC.NS"
]


def discover_opportunities() -> pd.DataFrame:
    """
    Scan market for trading opportunities
    
    Returns:
        DataFrame with columns: symbol, price, change_percent, volume
    """
    opportunities = []
    
    for symbol in NSE_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if len(hist) < 2:
                continue
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            change_percent = ((current_price - prev_price) / prev_price) * 100
            volume = hist['Volume'].iloc[-1]
            
            opportunities.append({
                'symbol': symbol,
                'price': current_price,
                'change_percent': change_percent,
                'volume': volume,
                'abs_change': abs(change_percent)
            })
            
        except Exception as e:
            # Skip if data fetch fails
            continue
    
    df = pd.DataFrame(opportunities)
    
    if df.empty:
        return df
    
    # Sort by absolute change (biggest movers)
    df = df.sort_values('abs_change', ascending=False)
    
    return df


def get_todays_trades(portfolio: dict) -> List[str]:
    """
    Get list of stocks traded today
    
    Args:
        portfolio: Current portfolio state
        
    Returns:
        List of symbols traded today
    """
    today = datetime.now().date()
    traded_today = []
    
    for order in portfolio.get('orders', []):
        # Check if order timestamp is today
        # (In production, parse actual timestamp)
        traded_today.append(order.get('symbol', ''))
    
    return traded_today


def scout_node(state: SentinelState) -> SentinelState:
    """
    Scout Agent - Find the next trading opportunity
    
    Process:
    1. Scan market for top movers
    2. Filter already traded stocks
    3. Select best opportunity
    4. Update state
    
    Args:
        state: Current SentinelState
        
    Returns:
        Updated SentinelState with current_ticker set
    """
    
    print("🕵️  Scout Agent: Scanning market for opportunities...")
    
    try:
        # 1. Discover opportunities
        opportunities = discover_opportunities()
        
        if opportunities.empty:
            state['current_ticker'] = ""
            state['errors'].append("Scout: No opportunities found")
            state['messages'].append(
                HumanMessage(content="🕵️ Scout: No tradable opportunities found in market scan")
            )
            return state
        
        # 2. Filter already traded (use portfolio from state)
        portfolio = state.get('portfolio_snapshot', {'orders': []})
        traded_today = get_todays_trades(portfolio)
        
        # Filter out traded stocks
        available = opportunities[~opportunities['symbol'].isin(traded_today)]
        
        if available.empty:
            # All stocks already traded today
            state['current_ticker'] = ""
            state['messages'].append(
                HumanMessage(content="🕵️ Scout: All top opportunities already traded today. Waiting for new signals.")
            )
            return state
        
        # 3. Select best opportunity (top mover)
        best = available.iloc[0]
        selected_symbol = best['symbol']
        change_pct = best['change_percent']
        
        # 4. Update state
        state['current_ticker'] = selected_symbol
        state['market_data'] = {
            'price': float(best['price']),
            'change_percent': float(change_pct),
            'volume': int(best['volume'])
        }
        
        # 5. Log message
        direction = "🟢 UP" if change_pct > 0 else "🔴 DOWN"
        state['messages'].append(
            HumanMessage(
                content=f"🕵️ Scout: Found opportunity → {selected_symbol.replace('.NS', '')} {direction} {abs(change_pct):.2f}% | Price: ₹{best['price']:,.2f}"
            )
        )
        
        print(f"✅ Scout: Selected {selected_symbol} ({change_pct:+.2f}%)")
        
    except Exception as e:
        # Error handling
        state['errors'].append(f"Scout error: {str(e)}")
        state['current_ticker'] = ""
        state['messages'].append(
            HumanMessage(content=f"🕵️ Scout: Error during market scan - {str(e)}")
        )
        print(f"❌ Scout error: {e}")
    
    return state


# Test function
if __name__ == "__main__":
    import sys
    sys.path.insert(0, 'C:\\Users\\Karthi\\Desktop\\Agent')
    from sentinel_state import create_initial_state
    
    print("Testing Scout Agent...")
    state = create_initial_state()
    
    # Add mock portfolio
    state['portfolio_snapshot'] = {
        'cash': 100000,
        'positions': [],
        'orders': []
    }
    
    # Run scout
    result = scout_node(state)
    
    print(f"\n📊 Result:")
    print(f"   Ticker: {result['current_ticker']}")
    print(f"   Market Data: {result['market_data']}")
    print(f"   Messages: {len(result['messages'])}")
    
    for msg in result['messages']:
        print(f"   - {msg.content}")
