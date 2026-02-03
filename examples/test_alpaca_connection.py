"""
Simple Alpaca Connection Test

Tests connection to Alpaca without yfinance dependency.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.config import ALPACA_API_KEY, ALPACA_SECRET_KEY, has_alpaca_credentials


async def test_alpaca_connection():
    """Test Alpaca connection"""
    print("=" * 70)
    print("ALPACA CONNECTION TEST")
    print("=" * 70)
    
    # Check credentials
    if not has_alpaca_credentials():
        print("\n❌ Alpaca credentials not found in .env file")
        return
    
    print("\n✅ Credentials found!")
    print(f"   API Key: {ALPACA_API_KEY[:10]}...")
    
    # Test connection
    print("\n[1] Connecting to Alpaca paper trading...")
    try:
        from sentinel.execution import AlpacaClient
        
        client = AlpacaClient(
            api_key=ALPACA_API_KEY,
            secret_key=ALPACA_SECRET_KEY,
            paper=True
        )
        print("   ✅ Connected successfully!")
        
        # Get account info
        print("\n[2] Fetching account information...")
        account = await client.get_account()
        
        print(f"\n   📊 Account Status: {account['status']}")
        print(f"   💰 Equity: ${account['equity']:,.2f}")
        print(f"   💵 Cash: ${account['cash']:,.2f}")
        print(f"   📈 Buying Power: ${account['buying_power']:,.2f}")
        
        # Check positions
        print("\n[3] Checking positions...")
        positions = await client.get_all_positions()
        
        if positions:
            print(f"   Found {len(positions)} positions:")
            for pos in positions:
                print(f"   • {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
                print(f"     P&L: ${pos['unrealized_pl']:.2f} ({pos['unrealized_plpc']:.2%})")
        else:
            print("   No open positions")
        
        print("\n" + "=" * 70)
        print("✅ ALPACA PAPER TRADING READY!")
        print("=" * 70)
        print("\n🎉 You can now execute real paper trades!")
        print("   • $100,000 virtual cash")
        print("   • Real market execution")
        print("   • Zero risk")
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API keys are correct")
        print("2. Make sure you're using PAPER trading keys")
        print("3. Verify internet connection")


if __name__ == "__main__":
    asyncio.run(test_alpaca_connection())
