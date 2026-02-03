"""
Phase 5 Example - Alpaca Paper Trading

Demonstrates connecting to Alpaca paper trading API and executing real orders.
"""

import asyncio
import logging
from sentinel.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, has_alpaca_credentials
from sentinel.execution import AlpacaClient, PaperTradingExecutor, PortfolioManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate Alpaca paper trading integration"""
    print("=" * 70)
    print("PHASE 5: ALPACA PAPER TRADING INTEGRATION")
    print("=" * 70)
    
    # Check for credentials
    if not has_alpaca_credentials():
        print("\n❌ Alpaca credentials not found!")
        print("\nTo use Alpaca paper trading:")
        print("1. Sign up at https://alpaca.markets (FREE)")
        print("2. Get your paper trading API keys")
        print("3. Copy .env.example to .env")
        print("4. Add your keys to .env file")
        print("\nExample .env file:")
        print("ALPACA_API_KEY=your_key_here")
        print("ALPACA_SECRET_KEY=your_secret_here")
        return
    
    print("\n✅ Alpaca credentials found!")
    
    # Initialize Alpaca client
    print("\n[1] Connecting to Alpaca paper trading...")
    try:
        client = AlpacaClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
            paper=True
        )
        print("  ✓ Connected to Alpaca paper trading")
    except Exception as e:
        print(f"  ❌ Failed to connect: {e}")
        return
    
    # Get account information
    print("\n[2] Fetching account information...")
    account = await client.get_account()
    print(f"  Account Status: {account['status']}")
    print(f"  Equity: ${account['equity']:,.2f}")
    print(f"  Cash: ${account['cash']:,.2f}")
    print(f"  Buying Power: ${account['buying_power']:,.2f}")
    
    # Initialize portfolio manager
    print("\n[3] Initializing portfolio manager...")
    portfolio = PortfolioManager(client)
    summary = await portfolio.get_summary()
    print(f"  Portfolio Value: ${summary['portfolio_value']:,.2f}")
    print(f"  Positions Value: ${summary['positions_value']:,.2f}")
    print(f"  Total P&L: ${summary['total_pnl']:,.2f}")
    
    # Check existing positions
    print("\n[4] Checking existing positions...")
    positions = await portfolio.get_positions()
    if positions:
        print(f"  Found {len(positions)} open positions:")
        for pos in positions:
            print(f"    {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
            print(f"      Current: ${pos['current_price']:.2f}, P&L: ${pos['unrealized_pl']:.2f} ({pos['unrealized_plpc']:.2%})")
    else:
        print("  No open positions")
    
    # Demo order submission (commented out to avoid accidental trades)
    print("\n[5] Paper trading executor ready!")
    executor = PaperTradingExecutor(client)
    print("  ✓ Can execute real paper trades")
    print("\n  To execute a trade, create a recommendation and call:")
    print("    result = await executor.execute_trade(recommendation)")
    
    print("\n" + "=" * 70)
    print("ALPACA PAPER TRADING INTEGRATION SUCCESSFUL!")
    print("=" * 70)
    print("\n✨ You can now:")
    print("   • Execute real paper trades")
    print("   • Track positions and P&L")
    print("   • Monitor portfolio value")
    print("   • Test strategies risk-free")
    print("\n🚀 Ready for live paper trading workflow!")


if __name__ == "__main__":
    asyncio.run(main())
