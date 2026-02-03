# Indian Market Setup Guide

Complete guide to setting up Project Sentinel for trading on Indian stock markets (NSE/BSE) using Zerodha Kite Connect API.

## Table of Contents

1. [Quick Start (Mock Mode)](#quick-start-mock-mode)
2. [Zerodha Account Setup](#zerodha-account-setup)
3. [Kite Connect API Setup](#kite-connect-api-setup)
4. [Configuration](#configuration)
5. [Authentication Flow](#authentication-flow)
6. [Running Examples](#running-examples)
7. [Indian Market Specifics](#indian-market-specifics)

---

## Quick Start (Mock Mode)

Test the Indian market features **without broker credentials**:

```bash
# 1. Set market region to INDIA in .env
echo "MARKET_REGION=INDIA" >> .env

# 2. Run Indian market workflow example
python examples/indian_market_workflow.py
```

This uses real NSE/BSE data from Yahoo Finance with simulated trading.

---

## Zerodha Account Setup

### Step 1: Create Zerodha Trading Account

1. Visit [https://zerodha.com/](https://zerodha.com/)
2. Click "Open Account"
3. Complete KYC process (requires Aadhar, PAN, bank details)
4. Account opening fees: ₹200 (one-time)
5. Trading charges: ₹0 for equity delivery, ₹20 per intraday/F&O trade

### Step 2: Funding Your Account

- Minimum: ₹0 (no minimum balance requirement)
- Recommended for testing: ₹10,000 - ₹50,000
- Fund via UPI, net banking, or NEFT

---

## Kite Connect API Setup

### Step 1: Subscribe to Kite Connect

1. Login to [https://kite.zerodha.com/](https://kite.zerodha.com/)
2. Navigate to [https://developers.kite.trade/](https://developers.kite.trade/)
3. Click "Get Started" or "Subscribe"
4. **Cost: ₹2,000/month** (includes live market data)

> **Note**: This is separate from your trading account balance.

### Step 2: Create a Kite Connect App

1. Go to [https://developers.kite.trade/apps](https://developers.kite.trade/apps)
2. Click "Create new app"
3. Fill in details:
   - **App name**: Project Sentinel (or your choice)
   - **App type**: Connect
   - **Redirect URL**: `http://127.0.0.1:5000/callback` (for local testing)
   - **Description**: Algorithmic trading system
   - **Webhook URL**: Leave blank

4. Submit and wait for approval (usually instant for Connect apps)

### Step 3: Get API Credentials

Once approved:

1. Go to your app dashboard
2. Note down:
   - **API Key** (visible on app page)
   - **API Secret** (click "Show API secret")

⚠️ **Keep these credentials secure!** Never commit to GitHub.

---

## Configuration

### Update .env File

```bash
# Market Selection
MARKET_REGION=INDIA

# Zerodha Kite Connect
ZERODHA_API_KEY=your_api_key_here
ZERODHA_API_SECRET=your_api_secret_here

# These will be generated during authentication
ZERODHA_REQUEST_TOKEN=
ZERODHA_ACCESS_TOKEN=

# Exchange Selection
INDIAN_EXCHANGE=NSE  # or BSE
```

### Install Dependencies

```bash
# Install Indian market dependencies
pip install -r requirements.txt

# Key packages:
# - kiteconnect>=4.2.0  (Zerodha API)
# - pytz>=2023.3        (IST timezone)
```

---

## Authentication Flow

Zerodha uses OAuth 2.0 authentication. Follow these steps:

### Step 1: Generate Login URL

```python
from sentinel.execution import ZerodhaClient

# Initialize client
client = ZerodhaClient(
    api_key="your_api_key",
    api_secret="your_api_secret"
)

# Get login URL
login_url = client.get_login_url()
print(f"Visit this URL: {login_url}")
```

### Step 2: Complete Login

1. Open the login URL in browser
2. Login with your Zerodha credentials
3. Authorize the app
4. You'll be redirected to: `http://127.0.0.1:5000/callback?request_token=XXXXX&action=login&status=success`
5. **Copy the `request_token` from URL**

### Step 3: Generate Session

```python
# Use request_token to generate session
session = await client.generate_session(request_token="XXXXX")

# session contains access_token
access_token = session["access_token"]
print(f"Access Token: {access_token}")

# Save this to .env for future use
```

### Step 4: Update .env

```bash
ZERODHA_ACCESS_TOKEN=your_generated_access_token
```

> **Note**: Access tokens are valid until 6 AM next day. You'll need to regenerate daily.

---

## Running Examples

### Example 1: Indian Market Workflow (Mock Mode)

```bash
python examples/indian_market_workflow.py
```

**Features:**
- Real NSE/BSE prices from Yahoo Finance
- IST timezone handling
- INR calculations
- STT tax calculations
- Simulated order execution

### Example 2: Live Trading with Zerodha (Future)

```bash
# Create a new example file
python examples/zerodha_live_trading.py
```

---

## Indian Market Specifics

### Trading Hours (IST)

```python
from sentinel.indian_market_config import *

# Regular Session
MARKET_OPEN_TIME = time(9, 15)   # 9:15 AM IST
MARKET_CLOSE_TIME = time(15, 30)  # 3:30 PM IST

# Pre-market
PRE_MARKET = time(9, 0) - time(9, 15)

# Post-market
POST_MARKET = time(15, 30) - time(16, 0)

# Auto square-off
AUTO_SQUAREOFF_TIME = time(15, 20)  # 3:20 PM IST
```

### Stock Symbols

Indian stocks use exchange-specific formats:

**For Yahoo Finance:**
- NSE stocks: Add `.NS` suffix (e.g., `RELIANCE.NS`, `TCS.NS`)
- BSE stocks: Add `.BO` suffix (e.g., `RELIANCE.BO`, `TCS.BO`)

**For Zerodha Kite:**
- No suffix needed (e.g., `RELIANCE`, `TCS`)
- Specify exchange separately: `NSE` or `BSE`

### Tax & Charges

**Securities Transaction Tax (STT):**
- **Intraday Equity**: 0.025% on **sell side only**
- **Delivery Equity**: 0.1% on **both sides**
- **Futures**: 0.01% on sell side
- **Options**: 0.0625% on sell side (on premium)

**Other Charges:**
- Exchange charges: ~0.00345% (NSE), ~0.00375% (BSE)
- SEBI charges: ₹10 per crore (negligible)
- GST: 18% on (exchange charges + SEBI charges)
- Stamp duty: 0.003% on buy side (₹1,500 max per day)

**Example Cost Calculation:**

```python
from sentinel.indian_market_config import calculate_indian_trading_costs

# ₹1 lakh intraday buy
costs = calculate_indian_trading_costs(
    transaction_value=100000,
    side="BUY",
    is_intraday=True,
    exchange="NSE"
)

print(costs)
# {
#   'stt': 0.0,              # No STT on buy
#   'exchange_charges': 3.45,
#   'sebi_charges': 0.001,
#   'gst': 0.62,
#   'total': 4.07
# }

# ₹1 lakh intraday sell
costs = calculate_indian_trading_costs(
    transaction_value=100000,
    side="SELL",
    is_intraday=True,
    exchange="NSE"
)

print(costs)
# {
#   'stt': 25.0,             # 0.025% STT on sell
#   'exchange_charges': 3.45,
#   'sebi_charges': 0.001,
#   'gst': 0.62,
#   'total': 29.07
# }
```

### SEBI Regulations

**Intraday Trading:**
- **Minimum margin**: 20% (max 5x leverage)
- **Mandatory square-off**: All positions must close by 3:30 PM
- **Broker auto-square-off**: Typically 3:20 PM (10 mins before close)

**Position Limits (Index Options):**
- Net limit: ₹5,000 crore per entity
- Gross limit: ₹10,000 crore per entity

**Circuit Breakers:**
- Individual stocks: 5%, 10%, or 20% bands
- Market-wide: 10%, 15%, 20% (triggers trading halts)

### Popular Indian Stocks

```python
from sentinel.indian_market_config import POPULAR_INDIAN_STOCKS

# Nifty 50 stocks  
nifty_50 = POPULAR_INDIAN_STOCKS["NIFTY_50"]
# ['RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', ...]

# Bank Nifty
bank_nifty = POPULAR_INDIAN_STOCKS["BANK_NIFTY"]
# ['HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', ...]

# IT Sector
it_stocks = POPULAR_INDIAN_STOCKS["IT_SECTOR"]
# ['TCS', 'INFY', 'HCLTECH', 'WIPRO', ...]
```

### Market Holidays

Indian markets are closed on:
- Republic Day (Jan 26)
- Holi
- Good Friday
- Independence Day (Aug 15)
- Diwali
- Christmas
- And other national/religious holidays

Check `MarketHolidays.HOLIDAYS_2026` in `indian_market_config.py` for full list.

---

## Troubleshooting

### Issue: "kiteconnect not installed"

```bash
pip install kiteconnect --upgrade
```

### Issue: "Access token invalid"

Access tokens expire daily at 6 AM IST. Regenerate using the authentication flow.

### Issue: "Market closed" errors

Indian markets trade only 9:15 AM - 3:30 PM IST, Mon-Fri (excluding holidays).

### Issue: "Insufficient funds"

Ensure your Zerodha account has adequate balance:
- Check margin requirements
- Indian markets require 20% minimum margin for intraday

### Issue: "Symbol not found"

Verify symbol format:
- Yahoo Finance: Use `.NS` or `.BO` suffix
- Kite Connect: No suffix, specify exchange separately

---

## Next Steps

1. ✅ Complete Zerodha KYC and fund account
2. ✅ Subscribe to Kite Connect (₹2,000/month)
3. ✅ Create Kite Connect app and get API keys
4. ✅ Update `.env` with credentials
5. ✅ Run authentication flow to get access_token
6. ✅ Test with `indian_market_workflow.py`
7. 🚀 Start paper trading!

---

## Useful Links

- **Zerodha**: [https://zerodha.com/](https://zerodha.com/)
- **Kite Connect Docs**: [https://kite.trade/docs/connect/v3/](https://kite.trade/docs/connect/v3/)
- **Python Client**: [https://github.com/zerodha/pykiteconnect](https://github.com/zerodha/pykiteconnect)
- **NSE**: [https://www.nseindia.com/](https://www.nseindia.com/)
- **BSE**: [https://www.bseindia.com/](https://www.bseindia.com/)
- **SEBI**: [https://www.sebi.gov.in/](https://www.sebi.gov.in/)

---

## Support

For issues specific to:
- **Project Sentinel**: Open a GitHub issue
- **Kite Connect API**: Email [kiteconnect@zerodha.com](mailto:kiteconnect@zerodha.com)
- **Zerodha Account**: Use [Zerodha Support](https://support.zerodha.com/)

---

**Happy Trading! 🇮🇳 🚀**
