# Sentinel Trading Bot 🤖📈

**AI-Powered Paper Trading Dashboard for Indian Stock Markets (NSE/BSE)**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red.svg)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-4285F4.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

![Sentinel Trading Bot](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 🎯 Overview

Sentinel is a **production-grade paper trading platform** that combines **Google Gemini AI** with real-time market data to help you learn stock trading without risking real money. Perfect for beginners, students, and anyone wanting to master the Indian stock market!

### ✨ Key Features

- 🤖 **AI-Powered Signals** - Gemini analyzes stocks and gives BUY/WAIT/AVOID recommendations
- 📊 **Real-Time Data** - Live prices, charts, and news from NSE/BSE
- 💼 **Portfolio Tracking** - Monitor your virtual holdings and P&L
- 📈 **Technical Analysis** - RSI, MACD, Bollinger Bands, Volume analysis
- 📰 **News Integration** - Stay updated with latest market news
- 🎨 **Premium UI** - Clean, Groww-inspired design
- ⏰ **Market Hours** - Realistic trading hours (9:15 AM - 3:30 PM IST)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Google Gemini API key ([Get it free](https://aistudio.google.com/apikey))

### Installation

```bash
# Clone the repository
git clone https://github.com/karthixcarlo/sentinel-trading-bot.git
cd sentinel-trading-bot

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Running the Dashboard

```bash
cd dashboard_v3
streamlit run Home.py --server.port 8509
```

Open your browser to **http://localhost:8509**

---

## 📚 Features Walkthrough

### 🏠 Home Dashboard
- Portfolio snapshot with real-time P&L
- Market status indicator
- Watchlist preview
- Recent orders history
- Quick action buttons

### 📊 Market Overview
- Live NIFTY 50, SENSEX, BANKNIFTY indices
- Market open/closed status
- Portfolio summary

### 🔍 Stock Discovery
- **Top Gainers** - Best performing stocks
- **Top Losers** - Worst performing stocks  
- **Most Active** - High volume stocks
- One-click analysis

### 📈 Stock Analyzer (★ Main Feature)
- **AI Signals** - BUY (🟢), WAIT (⚪), AVOID (🔴)
- **Technical Indicators** - RSI, MACD, Bollinger Bands
- **Interactive Charts** - Candlestick, volume, indicators
- **News Feed** - Latest company news
- **Quick Trade** - Place orders instantly
- **Risk Management** - AI-suggested stop loss & targets

### 💼 Portfolio Tracker
- Current holdings with live prices
- Unrealized P&L calculation
- Order history
- Performance metrics

### ⚡ Trade Executor
- Buy/Sell orders with quantity selection
- Market hours validation
- Real-time price fetching
- Order confirmation feedback

### ⚙️ Settings
- Initial capital configuration
- Watchlist management
- CSV import support
- Portfolio reset

---

## 🛠️ Technology Stack

| Category | Technology |
|----------|-----------|
| **Frontend** | Streamlit, Custom CSS, Material Symbols |
| **Backend** | Python 3.10+ |
| **AI/ML** | Google Gemini 2.5 Flash |
| **Data** | yfinance, BeautifulSoup4 |
| **Libraries** | Pandas, NumPy, Pydantic |

---

## 🎨 UI Design

Inspired by **Groww** app with:
- Clean, minimal interface
- Professional typography (DM Sans, JetBrains Mono)
- Subtle animations
- Card-based layouts
- Material Symbols icons

### Color Palette
- 🟢 **Primary Green** (#00D09C) - BUY signals, success
- 🔴 **Primary Red** (#EB5B3C) - AVOID signals, errors
- ⚪ **Neutral Gray** (#8B92A0) - WAIT signals
- ⚫ **Text** (#1A1D29) - Primary text

---

## 🧠 AI Trading Analyst

### How It Works

1. **Fetch Data** - Get technical indicators (RSI, MACD, Volume, Trend)
2. **Scrape News** - Latest company news from web sources
3. **AI Analysis** - Gemini evaluates all data holistically
4. **Generate Signal** - Returns BUY/WAIT/AVOID with confidence score
5. **Provide Reasoning** - Explains the decision
6. **Risk Levels** - Suggests stop loss & take profit

### Signal Framework

| Signal | Color | Meaning | Criteria |
|--------|-------|---------|----------|
| **BUY** | 🟢 Green | Strong bullish opportunity | 2+ bullish signals, confidence ≥ 60% |
| **WAIT** | ⚪ Gray | Mixed/unclear signals | Contradictory indicators, 40-60% confidence |
| **AVOID** | 🔴 Red | Strong bearish signals | 2+ bearish signals, negative confidence ≥ 60% |

---

## 📖 Usage Guide

### Basic Workflow

1. **Discover** → Go to Stock Discovery, browse gainers/losers
2. **Analyze** → Click "Analyze" to see AI signal & charts
3. **Trade** → Use Quick Trade widget to place orders
4. **Track** → Monitor portfolio in Portfolio page
5. **Learn** → Review what works, refine your strategy

### Best Practices

- ✅ Start with ₹10,000 virtual capital
- ✅ Follow AI signals and reasoning
- ✅ Set stop losses (use AI suggestions)
- ✅ Trade only during market hours (9:15 AM - 3:30 PM IST)
- ✅ Diversify - don't put all capital in one stock
- ✅ Review portfolio daily

---

## 📁 Project Structure

```
sentinel-trading-bot/
├── dashboard_v3/              # Main Streamlit app
│   ├── Home.py               # Landing page
│   ├── pages/                # Multi-page app
│   │   ├── 1_Market_Overview.py
│   │   ├── 2_Stock_Discovery.py
│   │   ├── 3_Stock_Analyzer.py
│   │   ├── 4_Portfolio.py
│   │   ├── 5_Trade_Executor.py
│   │   └── 6_Settings.py
│   ├── premium_theme.py      # Groww-inspired styling
│   ├── market_hours.py       # Trading hours validation
│   ├── navigation.py         # Top nav component
│   └── news_loader.py        # Web scraper
├── analyst_agent_gemini.py   # AI analyst (Gemini)
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── README.md                # This file
└── PROJECT_DOCUMENTATION.md # Comprehensive docs (60+ pages)
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Get your Gemini API key:**
1. Visit https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy and paste in `.env`

### Initial Settings

Default configuration:
- **Initial Capital**: ₹100,000
- **Brokerage**: 0.03% per trade
- **Market Hours**: Mon-Fri, 9:15 AM - 3:30 PM IST
- **Watchlist**: Top NSE stocks (RELIANCE, TCS, INFY, etc.)

---

## 🎓 Learning Resources

- 📄 [Complete Documentation](PROJECT_DOCUMENTATION.md) - 60+ page comprehensive guide
- 🎬 Demo walkthrough (coming soon)
- 📝 Trading tutorials (coming soon)

---

## 🚧 Roadmap

- [ ] Historical backtesting
- [ ] Advanced charting (more indicators)
- [ ] Price alerts & notifications  
- [ ] Multiple portfolio strategies
- [ ] Export reports (PDF/CSV)
- [ ] Options trading (F&O)
- [ ] Mobile app (React Native)

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Gemini** - AI-powered trading analysis
- **yfinance** - Real-time stock data
- **Streamlit** - Beautiful web framework
- **Groww** - UI/UX inspiration
- **NSE/BSE** - Indian stock market data

---

## 📞 Contact & Support

**Created by:** Karthi ([@karthixcarlo](https://github.com/karthixcarlo))

**Issues & Questions:**
- Open an [issue](https://github.com/karthixcarlo/sentinel-trading-bot/issues)
- Discussions tab for Q&A

---

## ⚠️ Disclaimer

This is a **paper trading platform** for **educational purposes only**. No real money is involved. This is NOT financial advice. Always do your own research before investing real money. Past performance does not guarantee future results.

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/karthixcarlo/sentinel-trading-bot?style=social)
![GitHub forks](https://img.shields.io/github/forks/karthixcarlo/sentinel-trading-bot?style=social)
![GitHub issues](https://img.shields.io/github/issues/karthixcarlo/sentinel-trading-bot)

---

<div align="center">

**Made with ❤️ for aspiring traders**

**⭐ Star this repo if you find it helpful!**

[Report Bug](https://github.com/karthixcarlo/sentinel-trading-bot/issues) · [Request Feature](https://github.com/karthixcarlo/sentinel-trading-bot/issues) · [Documentation](PROJECT_DOCUMENTATION.md)

</div>
