"""
Backtest Agent - Verify Gemini Analyst Performance
Tests AI trading signals against historical data
"""

import sys
sys.path.insert(0, 'c:\\Users\\Karthi\\Desktop\\Agent')

from analyst_agent_gemini import AgenticAnalyst
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculate_technical_indicators(df):
    """Calculate RSI and MACD for a dataframe"""
    # RSI
    delta = df['Close'].diff()  
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['Close'].ewm(span=12, adjust=False).mean()
    exp2 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    return df


def backtest_stock(ticker: str, days: int = 30):
    """
    Backtest Gemini analyst on historical data
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE.NS")
        days: Number of days to backtest
        
    Returns:
        Dictionary with backtest results
    """
    
    logger.info(f"Starting backtest for {ticker} over {days} days...")
    
    # Initialize analyst
    analyst = AgenticAnalyst()
    
    # Fetch historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days+60)  # Extra for indicators
    
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty:
            logger.error(f"No data found for {ticker}")
            return None
        
        # Calculate indicators
        hist = calculate_technical_indicators(hist)
        
        # Backtesting variables
        trades = []
        capital = 100000.0
        position = None
        wins = 0
        losses = 0
        
        # Get the last N days for backtesting
        test_data = hist.tail(days)
        
        for date, row in test_data.iterrows():
            if pd.isna(row['RSI']) or pd.isna(row['MACD']):
                continue
            
            current_price = row['Close']
            
            # Prepare technical data
            tech_data = {
                'rsi': round(row['RSI'], 2),
                'macd': round(row['MACD'], 2),
                'macd_signal': 'Bullish' if row['MACD'] > row['Signal_Line'] else 'Bearish',
                'volume': f"{row['Volume']:,.0f}",
                'trend': 'Bullish' if row['Close'] > row['Close_prev'] if 'Close_prev' in row else True else 'Bearish'
            }
            
            # Get Gemini signal
            signal = analyst.analyze_ticker(
                ticker=ticker,
                current_price=current_price,
                technical_data=tech_data,
                news_summary=f"Historical data for {date.strftime('%Y-%m-%d')}"
            )
            
            # Execute trade logic
            if signal.signal == "BUY" and position is None and signal.confidence > 0.7:
                # Open long position
                shares = capital / current_price
                position = {
                    'entry_price': current_price,
                    'shares': shares,
                    'entry_date': date,
                    'stop_loss': signal.stop_loss
                }
                logger.info(f"{date.strftime('%Y-%m-%d')}: BUY @ ₹{current_price:.2f} (Confidence: {signal.confidence*100:.0f}%)")
                
            elif signal.signal == "SELL" and position is not None:
                # Close position
                exit_price = current_price
                pnl = (exit_price - position['entry_price']) * position['shares']
                pnl_pct = ((exit_price / position['entry_price']) - 1) * 100
                
                if pnl > 0:
                    wins += 1
                else:
                    losses += 1
                
                capital += pnl
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': date,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
                
                logger.info(f"{date.strftime('%Y-%m-%d')}: SELL @ ₹{exit_price:.2f} | P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
                
                position = None
            
            # Check stop loss
            elif position and signal.stop_loss and current_price <= signal.stop_loss:
                # Stop loss hit
                exit_price = signal.stop_loss
                pnl = (exit_price - position['entry_price']) * position['shares']
                pnl_pct = ((exit_price / position['entry_price']) - 1) * 100
                
                losses += 1
                capital += pnl
                
                trades.append({
                    'entry_date': position['entry_date'],
                    'exit_date': date,
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'reason': 'Stop Loss'
                })
                
                logger.warning(f"{date.strftime('%Y-%m-%d')}: STOP LOSS @ ₹{exit_price:.2f} | P&L: ₹{pnl:,.2f} ({pnl_pct:+.2f}%)")
                
                position = None
        
        # Calculate results
        total_trades = wins + losses
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        total_return = ((capital / 100000.0) - 1) * 100
        
        results = {
            'ticker': ticker,
            'days_tested': days,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': win_rate,
            'starting_capital': 100000.0,
            'ending_capital': capital,
            'total_return': total_return,
            'trades': trades
        }
        
        return results
        
    except Exception as e:
        logger.error(f"Backtest failed: {e}")
        return None


def generate_report(results):
    """Generate markdown report from backtest results"""
    
    if not results:
        return "# Backtest Failed\n\nNo results available."
    
    report = f"""# Backtest Report: {results['ticker']}

## Summary
- **Testing Period:** {results['days_tested']} days
- **Total Trades:** {results['total_trades']}
- **Wins:** {results['wins']} | **Losses:** {results['losses']}
- **Win Rate:** {results['win_rate']:.1f}%

## Performance
- **Starting Capital:** ₹{results['starting_capital']:,.2f}
- **Ending Capital:** ₹{results['ending_capital']:,.2f}
- **Total Return:** {results['total_return']:+.2f}%

## Trade History
"""
    
    for i, trade in enumerate(results['trades'], 1):
        reason = f" ({trade.get('reason', 'Signal')})" if 'reason' in trade else ""
        report += f"\n{i}. **{trade['entry_date'].strftime('%Y-%m-%d')} → {trade['exit_date'].strftime('%Y-%m-%d')}{reason}**\n"
        report += f"   - Entry: ₹{trade['entry_price']:.2f} | Exit: ₹{trade['exit_price']:.2f}\n"
        report += f"   - P&L: ₹{trade['pnl']:,.2f} ({trade['pnl_pct']:+.2f}%)\n"
    
    return report


if __name__ == "__main__":
    print("=" * 60)
    print("🔬 GEMINI ANALYST BACKTEST")
    print("=" * 60)
    
    # Test with RELIANCE
    ticker = "RELIANCE.NS"
    days = 30
    
    results = backtest_stock(ticker, days=days)
    
    if results:
        report = generate_report(results)
        print("\n" + report)
        
        # Save report
        with open('backtest_report.md', 'w') as f:
            f.write(report)
        
        print("\n✅ Report saved to backtest_report.md")
    else:
        print("\n❌ Backtest failed")
