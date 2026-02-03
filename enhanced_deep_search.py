"""
Enhanced Deep Search with Confidence Calculation

Improves the deep_search_stock function to calculate proper confidence scores.
"""

import yfinance as yf
from typing import Dict
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')


async def enhanced_deep_search(symbol: str) -> Dict:
    """
    Perform enhanced deep analysis with confidence scoring.
    
    Args:
        symbol: Stock symbol to analyze
        
    Returns:
        Analysis dictionary with recommendation and confidence
    """
    
    analysis = {
        'symbol': symbol,
        'timestamp': datetime.now(IST),
        'recommendation': 'HOLD',
        'confidence': 0.5,
        'technical_analysis': {},
        'trade_details': {},
        'news_summary': 'No news data available'
    }
    
    try:
        # Get stock data
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='3mo')
        info = ticker.info
        
        if hist.empty:
            return analysis
        
        # Calculate technical indicators
        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['Close'].rolling(window=20).mean().iloc[-1] if len(hist) >= 20 else current_price
        sma_50 = hist['Close'].rolling(window=50).mean().iloc[-1] if len(hist) >= 50 else current_price
        
        # RSI calculation
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
        
        # Price change
        prev_close = info.get('previousClose', current_price)
        change_pct = ((current_price - prev_close) / prev_close * 100) if prev_close else 0
        
        # Trading signals
        buy_signals = 0
        sell_signals = 0
        
        # Signal 1: SMA trend
        if current_price > sma_20:
            buy_signals += 1
        else:
            sell_signals += 1
            
        if sma_20 > sma_50:
            buy_signals += 1
        else:
            sell_signals += 1
        
        # Signal 2: RSI
        if current_rsi < 30:
            buy_signals += 2  # Strong signal
        elif current_rsi < 45:
            buy_signals += 1
        elif current_rsi > 70:
            sell_signals += 2  # Strong signal
        elif current_rsi > 55:
            sell_signals += 1
        
        # Signal 3: Price momentum
        if change_pct > 3:
            buy_signals += 2
        elif change_pct > 1:
            buy_signals += 1
        elif change_pct < -3:
            sell_signals += 2
        elif change_pct < -1:
            sell_signals += 1
        
        # Determine recommendation and confidence
        total_signals = buy_signals + sell_signals
        
        if buy_signals > sell_signals + 1:
            analysis['recommendation'] = 'BUY'
            # Confidence based on signal strength
            signal_diff = buy_signals - sell_signals
            analysis['confidence'] = min(0.95, 0.6 + (signal_diff * 0.08))
        elif sell_signals > buy_signals + 1:
            analysis['recommendation'] = 'SELL'
            signal_diff = sell_signals - buy_signals
            analysis['confidence'] = min(0.95, 0.6 + (signal_diff * 0.08))
        else:
            analysis['recommendation'] = 'HOLD'
            analysis['confidence'] = 0.5 + (abs(buy_signals - sell_signals) * 0.05)
        
        # Technical analysis details
        sma_trend = "Bullish" if current_price > sma_20 > sma_50 else "Bearish" if current_price < sma_20 < sma_50 else "Neutral"
        
        if current_rsi > 70:
            rsi_signal = "Overbought"
        elif current_rsi < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"
        
        analysis['technical_analysis'] = {
            'rsi': f"{current_rsi:.1f}",
            'rsi_signal': rsi_signal,
            'sma_trend': sma_trend,
            'macd_signal': 'N/A'  # Placeholder
        }
        
        # Trade details
        position_size = int(10000 / current_price) if current_price > 0 else 0
        
        analysis['trade_details'] = {
            'entry_price': current_price,
            'shares': position_size,
            'position_value': position_size * current_price
        }
        
        # News summary
        analysis['news_summary'] = f"Price: ₹{current_price:.2f} | Change: {change_pct:+.2f}% | RSI: {current_rsi:.1f} | Trend: {sma_trend}"
        
    except Exception as e:
        # On error, return minimal analysis
        analysis['news_summary'] = f"Error analyzing {symbol}: {str(e)[:50]}"
    
    return analysis
