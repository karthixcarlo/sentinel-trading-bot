# -*- coding: utf-8 -*-
"""
Analyst Agent - Deep analysis using Gemini AI

Responsibility: Analyze stocks and generate trading signals
Logic:
    1. Fetch technical indicators (RSI, MACD, Volume, Trend)
    2. Scrape recent news
    3. Call Gemini AI via AgenticAnalyst
    4. Update state.analyst_signal
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from langchain_core.messages import AIMessage

from agents.sentinel_state import SentinelState
from agents.analyst_agent_gemini import AgenticAnalyst
from services.news_loader import get_news_summary


def calculate_technical_indicators(ticker: str) -> dict:
    """
    Calculate technical indicators for a stock
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE.NS")
        
    Returns:
        dict with RSI, MACD, Volume, Trend
    """
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        
        if len(hist) < 50:
            return {}
        
        # RSI Calculation
        delta = hist['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = -delta.where(delta < 0, 0).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = float(rsi.iloc[-1])
        
        # MACD Calculation
        exp1 = hist['Close'].ewm(span=12).mean()
        exp2 = hist['Close'].ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        current_macd = float(macd.iloc[-1])
        current_signal = float(signal.iloc[-1])
        
        # Volume Analysis
        avg_volume = hist['Volume'].rolling(window=20).mean()
        current_volume = hist['Volume'].iloc[-1]
        volume_ratio = float(current_volume / avg_volume.iloc[-1])
        
        # Trend Analysis (50-day SMA)
        sma_50 = hist['Close'].rolling(window=50).mean()
        current_price = hist['Close'].iloc[-1]
        
        if current_price > sma_50.iloc[-1]:
            trend = "Bullish"
        elif current_price < sma_50.iloc[-1]:
            trend = "Bearish"
        else:
            trend = "Neutral"
        
        return {
            'RSI': round(current_rsi, 2),
            'MACD': round(current_macd, 2),
            'MACD_Signal': round(current_signal, 2),
            'Volume_Ratio': round(volume_ratio, 2),
            'Trend': trend,
            'Price': float(current_price),
            'SMA_50': float(sma_50.iloc[-1])
        }
        
    except Exception as e:
        print(f"❌ Technical indicators error: {e}")
        return {}


def analyst_node(state: SentinelState) -> SentinelState:
    """
    Analyst Agent - Analyze ticker using Gemini AI
    
    Process:
    1. Get ticker from state
    2. Fetch technical data
    3. Scrape news
    4. Call Gemini for analysis
    5. Update state with signal
    
    Args:
        state: Current SentinelState
        
    Returns:
        Updated SentinelState with analyst_signal set
    """
    
    ticker = state.get('current_ticker', '')
    
    if not ticker:
        state['errors'].append("Analyst: No ticker provided")
        state['messages'].append(
            AIMessage(content="🧠 Analyst: ERROR - No ticker to analyze")
        )
        return state
    
    _bc = state.get('broadcast_callback')

    print(f"🧠 Analyst Agent: Analyzing {ticker}...")
    if _bc:
        _bc("Analyst", f"📊 Analyzing {ticker} with Gemini AI...")

    try:
        # 1. Fetch technical data
        technical_data = calculate_technical_indicators(ticker)
        
        if not technical_data:
            state['errors'].append(f"Analyst: Failed to get technical data for {ticker}")
            state['analyst_signal'] = {
                'signal': 'WAIT',
                'confidence': 0.0,
                'reasoning': 'Insufficient technical data',
                'stop_loss': None,
                'take_profit': None
            }
            state['messages'].append(
                AIMessage(content=f"🧠 Analyst: WAIT | No technical data available for {ticker}")
            )
            return state
        
        current_price = technical_data['Price']
        
        # 2. Get news
        try:
            news_summary = get_news_summary(ticker.replace('.NS', ''))
        except Exception:
            news_summary = "No recent news available"
        
        # 3. Call Gemini AI
        analyst = AgenticAnalyst(model_name="gemini-2.5-flash")
        signal = analyst.analyze_ticker(
            ticker=ticker,
            current_price=current_price,
            technical_data=technical_data,
            news_summary=news_summary
        )
        
        # 4. Update state
        state['analyst_signal'] = {
            'signal': signal.signal,
            'confidence': signal.confidence,
            'reasoning': signal.reasoning,
            'stop_loss': signal.stop_loss,
            'take_profit': signal.take_profit
        }
        
        # Update market data with technicals
        state['market_data'].update(technical_data)
        
        # 5. Log message
        confidence_pct = signal.confidence * 100
        signal_emoji = {
            'BUY': '🟢',
            'WAIT': '⚪',
            'AVOID': '🔴'
        }.get(signal.signal, '⚪')
        
        message = f"🧠 Analyst: {signal_emoji} {signal.signal} | Confidence: {confidence_pct:.0f}% | {signal.reasoning}"
        
        if signal.signal == 'BUY' and signal.stop_loss and signal.take_profit:
            message += f" | SL: ₹{signal.stop_loss:,.0f} | TP: ₹{signal.take_profit:,.0f}"
        
        state['messages'].append(AIMessage(content=message))
        
        print(f"✅ Analyst: {signal.signal} @ {confidence_pct:.0f}% confidence")
        if _bc:
            _bc("Analyst", f"{'🟢' if signal.signal == 'BUY' else '🔴' if signal.signal == 'AVOID' else '⚪'} {signal.signal} ({confidence_pct:.0f}%) — {signal.reasoning[:150]}")
        
    except Exception as e:
        # Error handling
        state['errors'].append(f"Analyst error: {str(e)}")
        state['analyst_signal'] = {
            'signal': 'WAIT',
            'confidence': 0.0,
            'reasoning': f'Analysis error: {str(e)}',
            'stop_loss': None,
            'take_profit': None
        }
        state['messages'].append(
            AIMessage(content=f"🧠 Analyst: ERROR - {str(e)}")
        )
        print(f"❌ Analyst error: {e}")
    
    return state


# Test function
if __name__ == "__main__":
    from agents.sentinel_state import create_initial_state
    
    print("Testing Analyst Agent...")
    state = create_initial_state()
    
    # Add ticker from Scout
    state['current_ticker'] = "RELIANCE.NS"
    state['market_data'] = {'price': 2450.0}
    
    # Run analyst
    result = analyst_node(state)
    
    print("\n📊 Result:")
    print(f"   Signal: {result['analyst_signal'].get('signal')}")
    print(f"   Confidence: {result['analyst_signal'].get('confidence'):.0%}")
    print(f"   Reasoning: {result['analyst_signal'].get('reasoning')}")
    
    for msg in result['messages']:
        print(f"   - {msg.content}")
