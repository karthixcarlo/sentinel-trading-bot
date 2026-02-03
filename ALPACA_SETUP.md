# Alpaca Paper Trading Setup

## Quick Start Guide

### 1️⃣ Sign Up for Alpaca (2 minutes)

1. Go to: https://alpaca.markets
2. Click "Sign Up" 
3. Enter your email and create a password
4. Verify your email
5. Select **"Paper Trading"** (FREE, no verification)

### 2️⃣ Get Your API Keys

1. Log into Alpaca dashboard
2. Navigate to: **Paper Trading → API Keys**
3. Click **"Generate New Keys"** (or view existing)
4. Copy both:
   - **API Key ID** (starts with `PK...`)
   - **Secret Key** (long string)

### 3️⃣ Add Keys to .env File

1. Open the file: `C:\Users\Karthi\Desktop\Agent\.env`
2. Replace the placeholder values:

```bash
ALPACA_API_KEY=YOUR_ACTUAL_KEY_HERE
ALPACA_SECRET_KEY=YOUR_ACTUAL_SECRET_HERE
```

**Example:**
```bash
ALPACA_API_KEY=PKABCDEFGHIJKLMNOP
ALPACA_SECRET_KEY=abc123def456ghi789jkl012mno345pqr678stu901
```

### 4️⃣ Test the Connection

Run this command:
```bash
.venv\Scripts\python.exe examples\phase5_paper_trading.py
```

You should see:
- ✅ Connected to Alpaca
- Your account balance ($100,000 virtual)
- Portfolio information

---

## What You Get

- **$100,000 virtual cash** to trade with
- **Real market data** (15-min delayed)
- **Real order execution** (paper money)
- **Portfolio tracking**
- **Zero risk** - no real money involved

---

## Troubleshooting

**"Credentials not found"**
- Make sure `.env` file exists in `C:\Users\Karthi\Desktop\Agent\`
- Check that keys are on the correct lines
- No quotes needed around the keys

**"Connection failed"**
- Verify keys are correct (copy-paste from Alpaca)
- Make sure you're using **Paper Trading** keys, not live
- Check internet connection

---

## Security Notes

⚠️ **Never share your API keys**
⚠️ **Never commit `.env` to git** (it's already in `.gitignore`)
⚠️ **Paper trading keys are separate from live trading**
⚠️ **You can regenerate keys anytime in Alpaca dashboard**

---

## Next Steps

Once connected, you can:
1. Run the full trading workflow with real Alpaca execution
2. Track positions and P&L in real-time
3. Test strategies risk-free
4. Monitor portfolio performance

**Ready to trade!** 🚀
