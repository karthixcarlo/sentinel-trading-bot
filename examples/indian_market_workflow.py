"""
INDIAN MARKET TRADING WORKFLOW

Complete autonomous trading system adapted for Indian markets (NSE/BSE) with:
- Real market data from Yahoo Finance India
- Indian stock symbols (RELIANCE, TCS, INFY, etc.)
- IST timezone handling
- INR currency calculations
- STT tax calculations
- SEBI regulatory compliance
- Auto square-off before 3:20 PM IST

This workflow demonstrates the system running in mock mode (no broker credentials required).
"""

import asyncio
import logging
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel import (
    CacheManager,
    CircuitBreaker,
    ProviderFactory,
    ConservativeRiskModel,
    SlippageSimulator,
    MarketCondition
)
from sentinel.indian_market_config import (
    is_market_open,
    should_auto_squareoff,
    time_until_market_open,
    IST,
    POPULAR_INDIAN_STOCKS,
    calculate_indian_trading_costs,
    TradingSegments
)
from sentinel.config import is_indian_market

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Run Indian market trading workflow"""
    print("=" * 80)
    print("🇮🇳 INDIAN MARKET TRADING WORKFLOW - NSE/BSE")
    print("=" * 80)
    
    # Get current IST time
    now = datetime.now(IST)
    print(f"\n⏰ Current IST Time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Check market status
    market_open = is_market_open(now)
    print(f"📊 Market Status: {'🟢 OPEN' if market_open else '🔴 CLOSED'}")
    
    if not market_open:
        time_to_open = time_until_market_open()
        hours = int(time_to_open.total_seconds() // 3600)
        minutes = int((time_to_open.total_seconds() % 3600) // 60)
        print(f"⏳ Time until market opens: {hours}h {minutes}m")
    
    # Check auto square-off requirement
    should_squareoff = should_auto_squareoff(now)
    if should_squareoff:
        print("⚠️  AUTO SQUARE-OFF TIME: All intraday positions must be closed!")
    
    print("\n" + "=" * 80)
    print("[1] Initializing Indian Market Infrastructure...")
    print("=" * 80)
    
    # Initialize cache
    cache = CacheManager(db_path="./sentinel_state/indian_market_cache.db")
    await cache.initialize()
    print("  ✓ Cache manager ready")
    
    # Initialize circuit breaker
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=60.0,
        state_file="./sentinel_state/circuit_breaker_india.json"
    )
    print(f"  ✓ Circuit breaker ready (state: {breaker.state.name})")
    
    # Initialize risk model for Indian market
    risk_model = ConservativeRiskModel(
        account_balance=1_00_000.0,  # ₹1 lakh
        market_region="INDIA",
        currency="INR"
    )
    print(f"  ✓ Risk model initialized (₹{risk_model.account_balance:,.0f})")
    
    # Initialize slippage simulator for Indian market
    slippage_sim = SlippageSimulator(
        condition=MarketCondition.NORMAL,
        spread_bps=10.0,  # Indian markets have wider spreads
        market_region="INDIA"
    )
    print("  ✓ Slippage simulator ready (Indian market profiles)")
    
    # Initialize data providers for Indian market
    print("\n[2] Initializing Indian Market Data Providers...")
    provider_factory = ProviderFactory(
        use_mock=False,  # Use real Yahoo Finance data
        cache_manager=cache,
        market_region="INDIA"
    )
    price_provider = provider_factory.get_price_provider()
    print("  ✓ Indian price provider ready (Yahoo Finance India)")
    
    # Select Indian stocks
    tickers = POPULAR_INDIAN_STOCKS["NIFTY_50"][:5]  # Top 5 Nifty stocks
    print(f"\n[3] Analyzing {len(tickers)} Indian Stocks...")
    print(f"    Tickers: {', '.join(tickers)}")
    
    # Fetch quotes
    print("\n" + "=" * 80)
    print("FETCHING REAL-TIME NSE DATA")
    print("=" * 80)
    
    quotes = await price_provider.get_batch_quotes(tickers, exchange="NSE")
    
    if not quotes:
        print("\n⚠️  No quotes available (market may be closed or data unavailable)")
        await cache.close()
        return
    
    print(f"\n✅ Received quotes for {len(quotes)} stocks\n")
    
    # Display quotes
    for ticker, quote in quotes.items():
        if not quote:
            continue
        
        print(f"📈 {ticker}")
        print(f"   Price: ₹{quote['price']:.2f}")
        print(f"   Change: ₹{quote['change']:.2f} ({quote['change_percent']:.2f}%)")
        print(f"   Day Range: ₹{quote['low']:.2f} - ₹{quote['high']:.2f}")
        print(f"   Volume: {quote['volume']:,}")
        print()
    
    # Simulate a trade with the first stock
    if quotes:
        # Get first available quote
        ticker = next(iter(quotes.keys()))
        quote = quotes[ticker]
        
        if quote:
            print("=" * 80)
            print(f"SIMULATING INTRADAY TRADE: {ticker}")
            print("=" * 80)
            
            entry_price = quote['price']
            stop_loss = entry_price * 0.98  # 2% stop loss
            
            # Calculate position size
            shares, risk_params = risk_model.calculate_position_size(
                entry_price=entry_price,
                stop_loss_price=stop_loss,
                confidence=0.75
            )
            
            print(f"\n💼 Position Sizing:")
            print(f"   Entry Price: ₹{entry_price:.2f}")
            print(f"   Stop Loss: ₹{risk_params.stop_loss_price:.2f}")
            print(f"   Position Size: {shares} shares")
            print(f"   Position Value: ₹{risk_params.position_value:,.2f}")
            print(f"   Portfolio Exposure: {risk_params.portfolio_exposure_pct}%")
            print(f"   Max Risk: ₹{risk_params.max_loss_amount:,.2f}")
            
            # Simulate buy fill
            print(f"\n📤 Simulating BUY order...")
            buy_fill = slippage_sim.simulate_fill(
                order_type="MARKET",
                side="BUY",
                intended_price=entry_price,
                size=shares,
                symbol=ticker
            )
            
            print(f"   Intended: ₹{buy_fill.intended_price:.2f}")
            print(f"   Filled at: ₹{buy_fill.actual_fill_price:.2f}")
            print(f"   Slippage: {buy_fill.slippage_pct:.3f}%")
            print(f"   Slippage Cost: ₹{buy_fill.slippage_cost:.2f}")
            
            # Calculate Indian trading costs
            transaction_value = buy_fill.actual_fill_price * buy_fill.filled_qty
            buy_costs = calculate_indian_trading_costs(
                transaction_value=transaction_value,
                side="BUY",
                segment=TradingSegments.EQUITY_CASH,
                is_intraday=True,
                exchange="NSE"
            )
            
            print(f"\n💰 Indian Trading Costs (BUY):")
            print(f"   STT: ₹{buy_costs['stt']:.2f}")
            print(f"   Exchange Charges: ₹{buy_costs['exchange_charges']:.2f}")
            print(f"   SEBI Charges: ₹{buy_costs['sebi_charges']:.2f}")
            print(f"   GST: ₹{buy_costs['gst']:.2f}")
            print(f"   Total Costs: ₹{buy_costs['total']:.2f}")
            
            # Simulate sell (assume 1% profit)
            exit_price = entry_price * 1.01
            
            print(f"\n📥 Simulating SELL order (Exit: ₹{exit_price:.2f})...")
            sell_fill = slippage_sim.simulate_fill(
                order_type="MARKET",
                side="SELL",
                intended_price=exit_price,
                size=buy_fill.filled_qty,
                symbol=ticker
            )
            
            print(f"   Intended: ₹{sell_fill.intended_price:.2f}")
            print(f"   Filled at: ₹{sell_fill.actual_fill_price:.2f}")
            print(f"   Slippage: {sell_fill.slippage_pct:.3f}%")
            print(f"   Slippage Cost: ₹{sell_fill.slippage_cost:.2f}")
            
            # Calculate sell costs (includes STT on intraday sell)
            sell_value = sell_fill.actual_fill_price * sell_fill.filled_qty
            sell_costs = calculate_indian_trading_costs(
                transaction_value=sell_value,
                side="SELL",
                segment=TradingSegments.EQUITY_CASH,
                is_intraday=True,
                exchange="NSE"
            )
            
            print(f"\n💰 Indian Trading Costs (SELL):")
            print(f"   STT: ₹{sell_costs['stt']:.2f} (0.025% on sell)")
            print(f"   Exchange Charges: ₹{sell_costs['exchange_charges']:.2f}")
            print(f"   SEBI Charges: ₹{sell_costs['sebi_charges']:.2f}")
            print(f"   GST: ₹{sell_costs['gst']:.2f}")
            print(f"   Total Costs: ₹{sell_costs['total']:.2f}")
            
            # Calculate P&L
            gross_pnl = (sell_fill.actual_fill_price - buy_fill.actual_fill_price) * buy_fill.filled_qty
            total_costs = (
                buy_fill.slippage_cost + sell_fill.slippage_cost +
                buy_costs['total'] + sell_costs['total']
            )
            net_pnl = gross_pnl - total_costs
            
            print(f"\n📊 Trade Summary:")
            print(f"   Entry: ₹{buy_fill.actual_fill_price:.2f} x {buy_fill.filled_qty}")
            print(f"   Exit: ₹{sell_fill.actual_fill_price:.2f} x {sell_fill.filled_qty}")
            print(f"   Gross P&L: ₹{gross_pnl:.2f}")
            print(f"   Total Costs: ₹{total_costs:.2f}")
            print(f"   Net P&L: ₹{net_pnl:.2f}")
            
            roi = (net_pnl / transaction_value) * 100
            print(f"   ROI: {roi:.2f}%")
    
    # Fetch index data
    print("\n" + "=" * 80)
    print("INDIAN MARKET INDICES")
    print("=" * 80)
    
    nifty_quote = await price_provider.get_index_quote("NIFTY")
    if nifty_quote:
        print(f"\n📊 NIFTY 50")
        print(f"   Value: {nifty_quote['value']:.2f}")
        print(f"   Change: {nifty_quote['change']:.2f} ({nifty_quote['change_percent']:.2f}%)")
        print(f"   Range: {nifty_quote['low']:.2f} - {nifty_quote['high']:.2f}")
    
    # Get slippage statistics
    stats = slippage_sim.get_statistics()
    print(f"\n" + "=" * 80)
    print("SLIPPAGE SIMULATOR STATISTICS (Indian Market)")
    print("=" * 80)
    print(f"Total Fills: {stats['total_fills']}")
    print(f"Avg Slippage: {stats['avg_slippage_pct']:.3f}%")
    print(f"Total Slippage Cost: ₹{stats['total_slippage_cost']:.2f}")
    print(f"Market Condition: {stats['market_condition']}")
    
    await cache.close()
    
    print("\n" + "=" * 80)
    print("🎉 INDIAN MARKET WORKFLOW COMPLETE!")
    print("=" * 80)
    print("\n✨ This workflow demonstrated:")
    print("   • Real NSE stock prices from Yahoo Finance India")
    print("   • Indian symbol formatting (RELIANCE.NS, TCS.NS)")
    print("   • IST timezone handling")
    print("   • INR currency calculations")
    print("   • STT tax calculations (0.025% on sell)")
    print("   • SEBI-compliant position sizing")
    print("   • Indian market slippage profiles")
    print("   • Market hours checking (9:15 AM - 3:30 PM IST)")
    print("\n💡 To use with real Zerodha broker:")
    print("   1. Get API keys from https://developers.kite.trade/")
    print("   2. Set MARKET_REGION=INDIA in .env")
    print("   3. Add ZERODHA_API_KEY and ZERODHA_API_SECRET")
    print("   4. Run authentication flow to get access_token")


if __name__ == "__main__":
    asyncio.run(main())
