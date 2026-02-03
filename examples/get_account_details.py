"""
Get Alpaca Account Details
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.execution import AlpacaClient
from sentinel.config import ALPACA_API_KEY, ALPACA_SECRET_KEY


async def main():
    """Get detailed account information"""
    client = AlpacaClient(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=True
    )
    
    # Get account details
    account = await client.get_account()
    
    print("=" * 60)
    print("ALPACA ACCOUNT DETAILS")
    print("=" * 60)
    print(f"\nAccount Status: {account['status']}")
    print(f"Account Type: Paper Trading")
    print(f"\nBalance Information:")
    print(f"  Equity: ${account['equity']:,.2f}")
    print(f"  Cash: ${account['cash']:,.2f}")
    print(f"  Buying Power: ${account['buying_power']:,.2f}")
    print(f"\nDay Trade Count: {account['day_trade_count']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
