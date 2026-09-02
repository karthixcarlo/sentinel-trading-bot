# -*- coding: utf-8 -*-
"""
Scout Agent - Market Scanner with Rolling Batch Strategy

Responsibility: Find trading opportunities from the full NSE universe
Strategy:
    - Uses Rolling Batch Funnel (50 stocks per cycle)
    - Parallel download using yfinance threads
    - Smart filtering (volume, price, liquidity)
    - Momentum-based selection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
import pandas as pd
from typing import Dict, List, Tuple
from langchain_core.messages import HumanMessage

from agents.sentinel_state import SentinelState
from services.database_manager import log_agent_thought
from services.market_loader import get_market_loader


# Smart filtering thresholds
MIN_VOLUME = 100_000  # Minimum daily volume (liquidity filter)
MIN_PRICE = 20.0      # Minimum stock price (avoid penny stocks)
BATCH_SIZE = 50       # Number of stocks to analyze per cycle


def download_batch_data(tickers: List[str]) -> Dict[str, pd.DataFrame]:
    """
    Download market data for multiple stocks in parallel
    
    Uses yfinance's threading for fast bulk download
    
    Args:
        tickers: List of stock symbols
        
    Returns:
        Dict mapping ticker to DataFrame
    """
    try:
        # Bulk download with threading
        print(f"📊 Downloading data for {len(tickers)} stocks (parallel)...")
        
        data = yf.download(
            tickers,
            period="1d",
            interval="1d",
            group_by='ticker',
            threads=True,
            progress=False,
            show_errors=False
        )
        
        # Parse results into dict
        result = {}
        
        if len(tickers) == 1:
            # Single ticker returns different structure
            ticker = tickers[0]
            if not data.empty:
                result[ticker] = data
        else:
            # Multiple tickers
            for ticker in tickers:
                try:
                    ticker_data = data[ticker]
                    if not ticker_data.empty and len(ticker_data) > 0:
                       result[ticker] = ticker_data
                except (KeyError, AttributeError):
                    continue
        
        print(f"✅ Downloaded {len(result)} valid datasets")
        return result
        
    except Exception as e:
        print(f"❌ Batch download error: {e}")
        return {}


def filter_junk_stocks(data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Filter out illiquid and penny stocks
    
    Criteria:
    - Volume >= 100,000 (liquidity)
    - Close Price >= ₹20 (avoid penny stocks)
    
    Args:
        data_dict: Dict of ticker -> DataFrame
        
    Returns:
        Filtered dict with only quality stocks
    """
    filtered = {}
    junk_count = 0
    
    for ticker, df in data_dict.items():
        try:
            if df.empty or len(df) == 0:
                junk_count += 1
                continue
            
            # Get latest data
            latest = df.iloc[-1]
            
            # Check volume
            volume = latest.get('Volume', 0)
            if volume < MIN_VOLUME:
                junk_count += 1
                continue
            
            # Check price
            close_price = latest.get('Close', 0)
            if close_price < MIN_PRICE:
                junk_count += 1
                continue
            
            # Passed filters
            filtered[ticker] = df
            
        except Exception:
            junk_count += 1
            continue
    
    print(f"🗑️  Filtered out {junk_count} junk stocks (low volume/price)")
    print(f"✅ {len(filtered)} quality stocks remain")
    
    return filtered


def calculate_momentum(data_dict: Dict[str, pd.DataFrame]) -> List[Tuple[str, float, float]]:
    """
    Calculate momentum (% change) for each stock
    
    Args:
        data_dict: Dict of ticker -> DataFrame
        
    Returns:
        List of (ticker, momentum_pct, price) sorted by momentum
    """
    momentum_list = []
    
    for ticker, df in data_dict.items():
        try:
            if df.empty or len(df) == 0:
                continue
            
            latest = df.iloc[-1]
            
            open_price = latest.get('Open', 0)
            close_price = latest.get('Close', 0)
            
            if open_price == 0:
                continue
            
            # Calculate percentage change
            momentum = ((close_price - open_price) / open_price) * 100
            
            momentum_list.append((ticker, momentum, close_price))
            
        except Exception:
            continue
    
    # Sort by momentum (descending)
    momentum_list.sort(key=lambda x: x[1], reverse=True)
    
    return momentum_list


def scout_node(state: SentinelState) -> SentinelState:
    """
    Scout Agent - Find best trading opportunity using Rolling Batch Strategy
    
    Process:
    1. Get random batch of 50 stocks from full NSE universe
    2. Parallel download market data
    3. Filter junk stocks (volume, price)
    4. Calculate momentum for remaining stocks
    5. Select stock with highest positive momentum
    6. Update state
    
    Args:
        state: Current SentinelState
        
    Returns:
        Updated SentinelState with selected ticker
    """
    
    _bc = state.get('broadcast_callback')

    print("\n🕵️  Scout Agent: Scanning market using Rolling Batch strategy...\n")
    if _bc:
        _bc("Scout", "🔍 Scanning market using Rolling Batch strategy...")

    try:
        # --- Sector filtering from user settings ---
        user_settings = state.get('user_settings', {})
        allowed_sectors = user_settings.get('allowed_sectors', [])

        SECTOR_STOCKS = {
            "IT":         ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
            "Banking":    ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS"],
            "Energy":     ["RELIANCE.NS", "ONGC.NS", "BPCL.NS"],
            "Automobile": ["MARUTI.NS", "TATAMOTORS.NS", "BAJAJ-AUTO.NS"],
            "FMCG":       ["ITC.NS", "HINDUNILVR.NS", "BRITANNIA.NS"],
            "Pharma":     ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS"],
            "Metals":     ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS"],
        }

        if allowed_sectors:
            # Build sector-specific universe
            sector_tickers = set()
            for sector in allowed_sectors:
                sector_tickers.update(SECTOR_STOCKS.get(sector, []))
            if _bc:
                _bc("Scout", f"Filtering by sectors: {', '.join(allowed_sectors)} ({len(sector_tickers)} stocks)")
        else:
            sector_tickers = None  # no filtering

        # Get market loader
        loader = get_market_loader()

        # Get random batch
        batch = loader.get_smart_batch(size=BATCH_SIZE)

        # Apply sector filter if configured
        if sector_tickers:
            batch = [t for t in batch if t in sector_tickers]
            # If filtered batch is too small, use sector tickers directly
            if len(batch) < 5:
                batch = list(sector_tickers)

        print(f"🔭 Scouting batch: {batch[:5]}... (+{max(len(batch)-5, 0)} more)")

        # Filter already traded stocks
        traded_tickers = state.get('traded_tickers', [])
        batch = [t for t in batch if t not in traded_tickers]
        
        if len(batch) == 0:
            state['messages'].append(
                HumanMessage(content="🕵️ Scout: All stocks in batch already traded. Skipping cycle.")
            )
            return state
        
        # Download batch data in parallel
        data_dict = download_batch_data(batch)
        
        if not data_dict:
            state['errors'].append("Scout: No valid data in batch")
            state['messages'].append(
                HumanMessage(content="🕵️ Scout: ❌ No valid data in this batch")
            )
            return state
        
        #Filter junk stocks
        quality_stocks = filter_junk_stocks(data_dict)
        
        if not quality_stocks:
            state['messages'].append(
                HumanMessage(content=f"🕵️ Scout: All {len(data_dict)} stocks filtered as junk")
            )
            return state
        
        # Calculate momentum
        momentum_list = calculate_momentum(quality_stocks)
        
        if not momentum_list:
            state['messages'].append(
                HumanMessage(content="🕵️ Scout: No stocks with calculable momentum")
            )
            return state
        
        positive_momentum_list = [entry for entry in momentum_list if entry[1] > 0]
        
        if not positive_momentum_list:
            state['messages'].append(
                HumanMessage(content="🕵️ Scout: No stocks with positive momentum in this batch")
            )
            return state
        
        # Select best stock (highest positive momentum)
        best_ticker, best_momentum, best_price = positive_momentum_list[0]
        
        # Update state
        state['current_ticker'] = best_ticker
        
        # Create market data dict for analyst
        state['market_data'] = {
            'price': best_price,
            'momentum': best_momentum,
            'data': quality_stocks[best_ticker]
        }
        
        # Log message
        direction = "🟢 UP" if best_momentum > 0 else "🔴 DOWN"
        message = f"🕵️ Scout: Found opportunity → {best_ticker.replace('.NS', '')} {direction} {abs(best_momentum):.2f}% | Price: ₹{best_price:,.2f}"
        state['messages'].append(HumanMessage(content=message))
        if _bc:
            _bc("Scout", f"📈 {best_ticker.replace('.NS', '')} {direction} {abs(best_momentum):.2f}% @ ₹{best_price:,.2f} (from {len(quality_stocks)} quality stocks)")
        
        # Log to database
        try:
            log_agent_thought(
                "Scout",
                f"Scanned {len(batch)} stocks, filtered {len(batch) - len(quality_stocks)} junk. Best: {best_ticker.replace('.NS', '')} ({best_momentum:+.2f}%)",
                state,
                state.get('iteration_count', 0),
                state.get('workflow_id')
            )
        except Exception:
            pass
        
        print(f"\n✅ Scout: Selected {best_ticker} ({best_momentum:+.2f}%)")
        print(f"📊 Scan Stats: {len(batch)} downloaded → {len(quality_stocks)} quality → {len(momentum_list)} analyzed\n")
        
    except Exception as e:
        # Error handling
        state['errors'].append(f"Scout error: {str(e)}")
        state['messages'].append(
            HumanMessage(content=f"🕵️ Scout: ❌ Error - {str(e)}")
        )
        print(f"❌ Scout error: {e}")
    
    return state


# Test function
if __name__ == "__main__":
    from agents.sentinel_state import create_initial_state
    
    print("Testing upgraded Scout Agent...")
    
    state = create_initial_state()
    state['traded_tickers'] = []  # Empty for test
    
    result = scout_node(state)
    
    print("\n" + "="*60)
    print("RESULTS:")
    print(f"Selected Ticker: {result.get('current_ticker')}")
    print(f"Errors: {result.get('errors')}")
    print("\nMessages:")
    for msg in result.get('messages', []):
        print(f"  - {msg.content}")
    print("="*60)
    
    print("\n✅ Test complete!")
