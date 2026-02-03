"""
Force Execute Test Order

Manually submits a small test order to Alpaca to verify execution works.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.execution import AlpacaClient
from sentinel.config import ALPACA_API_KEY, ALPACA_SECRET_KEY


async def main():
    """Submit a test order to verify Alpaca execution"""
    print("=" * 70)
    print("🧪 TEST: Manual Order Submission to Alpaca")
    print("=" * 70)
    
    # Connect to Alpaca
    print("\n[1] Connecting to Alpaca...")
    client = AlpacaClient(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=True
    )
    
    account = await client.get_account()
    print(f"  ✓ Connected! Cash: ${account['cash']:,.2f}")
    
    # Check market status
    print("\n[2] Checking market status...")
    print("  ⚠️  Note: US markets are closed on weekends")
    print("  ⚠️  Orders will be queued until market opens")
    
    # Submit a small test order
    print("\n[3] Submitting test order...")
    print("  Symbol: AAPL")
    print("  Quantity: 1 share")
    print("  Type: Market order")
    
    try:
        order = await client.submit_order(
            symbol="AAPL",
            qty=1,
            side="buy",
            type="market",
            time_in_force="day"
        )
        
        print(f"\n  ✅ Order submitted!")
        print(f"  Order ID: {order['id']}")
        print(f"  Status: {order['status']}")
        print(f"  Symbol: {order['symbol']}")
        print(f"  Quantity: {order['qty']}")
        
        # Wait a moment
        await asyncio.sleep(2)
        
        # Check order status
        print("\n[4] Checking order status...")
        updated_order = await client.get_order(order['id'])
        print(f"  Status: {updated_order['status']}")
        
        if updated_order['status'] == 'filled':
            print(f"  ✅ FILLED!")
            print(f"  Fill Price: ${updated_order['filled_avg_price']:.2f}")
            print(f"  Filled Qty: {updated_order['filled_qty']}")
        elif updated_order['status'] == 'pending_new':
            print(f"  ⏳ Order pending (market closed)")
        else:
            print(f"  Status: {updated_order['status']}")
        
        # Check positions
        print("\n[5] Checking positions...")
        positions = await client.get_all_positions()
        
        if positions:
            print(f"  Found {len(positions)} positions:")
            for pos in positions:
                print(f"  • {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
        else:
            print("  No positions yet (order may be pending)")
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE")
        print("=" * 70)
        print("\nCheck your Alpaca dashboard:")
        print("https://app.alpaca.markets/paper/dashboard/orders")
        
    except Exception as e:
        print(f"\n❌ Order failed: {e}")
        print("\nPossible reasons:")
        print("1. Market is closed (orders queue until open)")
        print("2. Invalid symbol or quantity")
        print("3. Insufficient buying power")


if __name__ == "__main__":
    asyncio.run(main())
