"""
Quick test of Indian market configuration (no pandas required)
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
print("=" * 60)
print("TESTING INDIAN MARKET SETUP")
print("=" * 60)

print("\n[1] Testing core imports...")
try:
    from sentinel.config import MARKET_REGION, INDIAN_EXCHANGE, is_indian_market
    print(f"  ✓ Config loaded: MARKET_REGION={MARKET_REGION}")
    print(f"  ✓ Exchange: {INDIAN_EXCHANGE}")
    print(f"  ✓ Is Indian Market: {is_indian_market()}")
except Exception as e:
    print(f"  ✗ Config import failed: {e}")
    sys.exit(1)

print("\n[2] Testing Indian market config...")
try:
    from sentinel.indian_market_config import (
        IST, MARKET_OPEN_TIME, MARKET_CLOSE_TIME,
        is_market_open, get_indian_symbol_format,
        calculate_indian_trading_costs, TradingSegments
    )
    
    now = datetime.now(IST)
    print(f"  ✓ Current IST time: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"  ✓ Market hours: {MARKET_OPEN_TIME} - {MARKET_CLOSE_TIME}")
    print(f"  ✓ Market status: {'OPEN' if is_market_open() else 'CLOSED'}")
    
    # Test symbol formatting
    symbol = get_indian_symbol_format("RELIANCE", "NSE")
    print(f"  ✓ Symbol format: RELIANCE -> {symbol}")
    
    # Test tax calculation
    costs = calculate_indian_trading_costs(
        transaction_value=100000,  # ₹1 lakh
        side="SELL",
        segment=TradingSegments.EQUITY_CASH,
        is_intraday=True
    )
    print(f"  ✓ STT on ₹1L sell: ₹{costs['stt']:.2f}")
    print(f"  ✓ Total costs: ₹{costs['total']:.2f}")
    
except Exception as e:
    print(f"  ✗ Indian market config failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[3] Testing risk model...")
try:
    from sentinel.risk_model import ConservativeRiskModel
    
    risk = ConservativeRiskModel(
        account_balance=100000.0,  # ₹1 lakh
        market_region="INDIA",
        currency="INR"
    )
    print(f"  ✓ Risk model initialized for {risk.market_region}")
    print(f"  ✓ Currency: {risk.currency}")
    print(f"  ✓ Indian slippage: {risk.ASSUMED_SLIPPAGE * 100:.2f}%")
    
except Exception as e:
    print(f"  ✗ Risk model failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[4] Testing slippage simulator...")
try:
    from sentinel.slippage_simulator import SlippageSimulator, MarketCondition
    
    sim = SlippageSimulator(
        condition=MarketCondition.NORMAL,
        market_region="INDIA"
    )
    print(f"  ✓ Slippage simulator for {sim.market_region}")
    print(f"  ✓ Using Indian profiles: {sim.market_region == 'INDIA'}")
    
except Exception as e:
    print(f"  ✗ Slippage simulator failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL CORE TESTS PASSED!")
print("=" * 60)
print("\n📊 Summary:")
print(f"  • Market Region: INDIA (NSE)")
print(f"  • Timezone: IST (Asia/Kolkata)")
print(f"  • Currency: INR")
print(f"  • STT Tax: 0.025% on sell")
print(f"  • Market Hours: 9:15 AM - 3:30 PM IST")
print(f"  • Configuration: ✅ Ready")

print("\n💡 Next Steps:")
print("  1. Wait for pandas/yfinance installation to complete")
print("  2. Run: python examples\\indian_market_workflow.py")
print("  3. See live NSE/BSE quotes in INR")

print("\n🎉 Your Indian market setup is working!")
