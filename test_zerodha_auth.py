"""
Zerodha Authentication - Simple Version (No Heavy Dependencies)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")

print("=" * 80)
print("🔐 ZERODHA KITE CONNECT AUTHENTICATION")
print("=" * 80)

# Check credentials
print("\n[1] Checking credentials from .env...")
if not ZERODHA_API_KEY or not ZERODHA_API_SECRET:
    print("  ❌ API credentials not found in .env")
    print("\n  Please add to .env:")
    print("  ZERODHA_API_KEY=your_api_key")
    print("  ZERODHA_API_SECRET=your_api_secret")
    exit(1)

print(f"  ✓ API Key: {ZERODHA_API_KEY}")
print(f"  ✓ API Secret: {ZERODHA_API_SECRET[:10]}...")

# Initialize Kite Connect
print("\n[2] Initializing Kite Connect...")
try:
    from kiteconnect import KiteConnect
    kite = KiteConnect(api_key=ZERODHA_API_KEY)
    print("  ✓ KiteConnect initialized")
except ImportError:
    print("  ❌ kiteconnect not installed")
    print("\n  Install with: pip install kiteconnect")
    exit(1)
except Exception as e:
    print(f"  ❌ Error: {e}")
    exit(1)

# Generate login URL
print("\n[3] Generating login URL...")
login_url = kite.login_url()

print("\n" + "=" * 80)
print("📋 AUTHENTICATION STEPS:")
print("=" * 80)

print("\n✅ STEP 1: Open this URL in your browser:\n")
print(f"  {login_url}\n")

print("✅ STEP 2: Login with your Zerodha credentials")
print("   • User ID: Your Zerodha trading account ID")
print("   • Password: Your Zerodha password")
print("   • 2FA: Your PIN/TOTP")

print("\n✅ STEP 3: After successful login, you'll be redirected to:")
print("   http://127.0.0.1:5000/callback?request_token=XXXXX&action=login&status=success")

print("\n✅ STEP 4: The page will NOT load (that's normal!)")
print("   Just COPY the entire URL from your browser's address bar")

print("\n✅ STEP 5: Look for 'request_token=XXXXX' in the URL")
print("   Copy ONLY the token part (after 'request_token=' and before '&')")

print("\n" + "=" * 80)

# Get request token from user
request_token = input("\n📋 Paste the request_token here: ").strip()

if not request_token:
    print("\n❌ No token provided. Exiting.")
    exit(1)

print(f"\n  ✓ Token received: {request_token[:15]}...")

# Generate session
print("\n[4] Generating access token...")
try:
    session_data = kite.generate_session(
        request_token=request_token,
        api_secret=ZERODHA_API_SECRET
    )
    
    access_token = session_data["access_token"]
    user_id = session_data["user_id"]
    
    print("  ✓ Session generated successfully!")
    print(f"  ✓ User ID: {user_id}")
    print(f"  ✓ Access Token: {access_token[:15]}...{access_token[-10:]}")
    
except Exception as e:
    print(f"\n❌ Failed to generate session: {e}")
    print("\nCommon issues:")
    print("  • Token expired (only valid for 5 minutes)")
    print("  • Token already used")
    print("  • Wrong API secret")
    print("\nTry again: Re-run this script and get a fresh token")
    exit(1)

# Test the connection
print("\n[5] Testing API connection...")
try:
    kite.set_access_token(access_token)
    profile = kite.profile()
    
    print("  ✓ Connected successfully!")
    print(f"  ✓ Name: {profile['user_name']}")
    print(f"  ✓ Email: {profile['email']}")
    print(f"  ✓ Broker: {profile['broker']}")
    
    # Get margins
    margins = kite.margins()
    equity = margins.get("equity", {})
    available = equity.get("available", {})
    
    print(f"\n  💰 Account Balance:")
    print(f"     Available Cash: ₹{available.get('cash', 0):,.2f}")
    print(f"     Available Margin: ₹{available.get('live_balance', 0):,.2f}")
    
except Exception as e:
    print(f"  ⚠️  Connection test failed: {e}")

# Save instructions
print("\n" + "=" * 80)
print("💾 SAVE TO .ENV FILE:")
print("=" * 80)

print(f"\nAdd this line to your .env file:\n")
print(f"ZERODHA_ACCESS_TOKEN={access_token}\n")

print("⚠️  IMPORTANT:")
print("  • Access tokens expire at 6:00 AM IST every day")
print("  • You'll need to run this script daily to get a new token")
print("  • Or use the token until it expires, then regenerate")

print("\n" + "=" * 80)
print("✅ AUTHENTICATION COMPLETE!")
print("=" * 80)

print("\n📋 Next Steps:")
print("  1. Copy the access token to .env file")
print("  2. Test with: python examples\\indian_market_workflow.py")
print("  3. Start trading with live Zerodha data!")

print("\n🎉 You're all set to trade on NSE/BSE!")
