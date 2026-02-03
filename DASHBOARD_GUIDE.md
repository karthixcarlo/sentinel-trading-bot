# Project Sentinel - Interactive Dashboard Guide

## 🚀 Quick Start

### Launch the Dashboard

**Windows:**
```bash
run_dashboard.bat
```

The dashboard will automatically:
1. Activate the virtual environment
2. Install required dependencies (Streamlit, Plotly)
3. Launch the web interface at `http://localhost:8501`
4. Open your default browser

---

## 📱 Dashboard Pages

### 1. 🏠 Home (Market Overview)

**Features:**
- Real-time market status (OPEN/CLOSED)
- Current time in IST
- Market hours countdown
- Indian indices (Nifty, Bank Nifty, Sensex)
- Quick portfolio statistics

**What you can do:**
- Monitor market status at a glance
- Check index performance
- View portfolio summary

---

### 2. 🔍 Discover (Stock Discovery)

**Features:**
- **One-click auto-discovery** of trending Indian stocks
- Scrapes Moneycontrol for:
  - Top Gainers 🟢
  - Top Losers 🔴
  - Most Active Stocks 🔥
- **Deep analysis** on selected stocks
- AI-powered recommendations (BUY/SELL/HOLD)

**How to use:**
1. Adjust discovery parameters (stocks per category, deep analysis count)
2. Click **"Discover Stocks"** button
3. Wait 1-2 minutes for scraping and analysis
4. View results in three tabs (Gainers, Losers, Active)
5. Review deep analysis with recommendations

**No coding required!** Just click the button and get instant stock recommendations.

---

### 3. 📊 Analyze (Stock Analysis)

*Coming Soon*

Will provide:
- Deep technical analysis for any stock
- Interactive price charts
- Technical indicators (RSI, MACD, SMA)
- News sentiment analysis
- Trade recommendations
- Position sizing suggestions

---

### 4. 💼 Portfolio (Position Tracking)

*Coming Soon*

Will display:
- Current open positions with live P&L
- Holdings (delivery positions)
- Account balance and margin
- Position distribution charts
- Auto-refresh every 30 seconds

---

### 5. 💰 Trade (Order Execution)

*Coming Soon*

Will allow:
- Manual buy/sell order submission
- Order type selection (Market, Limit, Stop-Loss)
- Risk validation before execution
- Order status tracking
- Confirmation dialogs

---

### 6. ⚙️ Settings (Configuration)

**Features:**
- **Risk Management:**
  - Max position size % (default: 5%)
  - Max risk per trade % (default: 1%)
  - Hurdle rate (minimum profit threshold)
  - Account balance configuration

- **Trading Mode:**
  - Paper Trading (simulated, no real money)
  - Live Trading (requires Zerodha subscription)

- **Data Settings:**
  - Cache TTL for market data
  - Auto-refresh intervals

**How to use:**
1. Adjust sliders for risk parameters
2. Set your account balance
3. Select trading mode
4. Click **"Save Settings"**
5. Settings persist across sessions

---

### 7. 📈 Performance (Analytics)

*Coming Soon*

Will show:
- Equity curve chart
- Win rate statistics
- Profit factor
- Maximum drawdown
- Sharpe ratio
- Trade history with filters
- Monthly/weekly breakdown

---

## 🎯 Common Workflows

### Workflow 1: Discover and Review Stocks

1. Go to **Home** page → Check market status
2. Go to **Discover** page
3. Click **"Discover Stocks"**
4. Review top gainers/losers/active stocks
5. Check deep analysis recommendations
6. Note stocks with BUY recommendations

**Time:** 2-3 minutes

---

### Workflow 2: Configure Risk Settings

1. Go to **Settings** page
2. Adjust risk parameters:
   - Set max position size (e.g., 5% of portfolio)
   - Set max risk per trade (e.g., 1% of portfolio)
3. Set account balance
4. Select Paper Trading mode
5. Click **"Save Settings"**

**Time:** 1 minute

---

### Workflow 3: Monitor Portfolio (When Available)

1. Go to **Portfolio** page
2. View current positions
3. Check today's P&L
4. Review position distribution
5. Click **"Refresh"** for updates

**Time:** 30 seconds

---

## 🎨 Dashboard Features

### Visual Indicators

- **🟢 Green:** Positive changes, profits, BUY recommendations
- **🔴 Red:** Negative changes, losses, SELL recommendations  
- **🟡 Yellow:** HOLD recommendations, warnings
- **⚪ Gray:** Neutral, no change

### Real-time Updates

- Market status updates automatically
- Click **"Refresh"** buttons for manual updates
- Some pages auto-refresh (Portfolio will refresh every 30s)

### Responsive Design

- Works on desktop, tablet, and mobile
- Sidebar collapses on smaller screens
- Tables are scrollable

---

## 💡 Tips & Tricks

### Performance Tips

1. **Cache settings:** Use 5-minute cache (300s) for good balance
2. **Discovery frequency:** Run discovery 1-2 times per day max
3. **Browser:** Works best on Chrome, Firefox, or Edge

### Trading Tips

1. **Start with Paper Trading:** Test strategies without risk
2. **Review recommendations:** Don't blindly follow AI suggestions
3. **Set conservative risk limits:** Start with 1-2% risk per trade
4. **Monitor regularly:** Check portfolio during market hours

### Data Tips

1. **Yahoo Finance delay:** ~15 minutes for free data
2. **Best discovery time:** Market hours (9:15 AM - 3:30 PM IST)
3. **Indices update:** Refresh every 5 minutes for latest quotes

---

## 🔒 Security & Safety

### Data Security

- API keys stored in `.env` file (not in dashboard)
- Keys are never displayed in full (masked)
- No sensitive data logged

### Trading Safety

- **Paper trading by default** (no real money risk)
- Risk validation before execution
- Confirmation dialogs for trades
- Emergency stop available (close dashboard)

### Best Practices

1. Never share your `.env` file
2. Use strong API keys
3. Start with paper trading
4. Test thoroughly before live trading
5. Set conservative risk limits

---

## ❓ Troubleshooting

### Dashboard won't start

**Problem:** `streamlit: command not found`

**Solution:**
```bash
.venv\Scripts\pip.exe install streamlit plotly streamlit-option-menu
```

---

### Discovery not working

**Problem:** No results from auto-discovery

**Solution:**
1. Check internet connection
2. Moneycontrol may have changed structure (check logs)
3. Try during market hours for better data

---

### Slow performance

**Problem:** Dashboard is slow

**Solution:**
1. Reduce cache TTL
2. Reduce discovery parameters
3. Close other applications
4. Clear browser cache

---

### Market status wrong

**Problem:** Shows CLOSED when market is open

**Solution:**
1. Check system time is correct
2. Ensure timezone is IST (Asia/Kolkata)
3. Check for market holidays

---

## 📞 Support

### Getting Help

1. **Documentation:** Check README.md, INDIAN_MARKET_SETUP.md
2. **Logs:** Check Streamlit console output for errors
3. **Code:** Review dashboard.py for detailed comments

### Reporting Issues

Include:
- What you were trying to do
- Error message (if any)
- Screenshot
- Steps to reproduce

---

## 🔮 Upcoming Features

### Next Release
- Complete Stock Analyzer with charts
- Portfolio tracker with real-time P&L
- Manual trade execution
- Performance analytics

### Future Enhancements
- WebSocket for real-time updates
- Email/SMS notifications
- Backtesting interface
- Strategy builder
- Dark mode
- Mobile app

---

## 📚 Additional Resources

- **Main Documentation:** [README.md](file:///c:/Users/Karthi/Desktop/Agent/README.md)
- **Indian Market Setup:** [INDIAN_MARKET_SETUP.md](file:///c:/Users/Karthi/Desktop/Agent/INDIAN_MARKET_SETUP.md)
- **Project Completion:** [PROJECT_COMPLETE.md](file:///c:/Users/Karthi/Desktop/Agent/PROJECT_COMPLETE.md)

---

## 🎊 Enjoy Trading!

The dashboard abstracts all the complex code behind a simple, beautiful interface. No coding required - just click, review, and trade!

**Remember:** Start with paper trading, learn the system, then consider live trading when ready.

---

**Built with ❤️ using Streamlit**
