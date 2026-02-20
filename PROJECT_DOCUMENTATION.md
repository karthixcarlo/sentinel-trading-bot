# Sentinel Trading Bot - Complete Project Documentation

**AI-Powered Trading Dashboard for Indian Markets (NSE/BSE)**

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Features & Capabilities](#features--capabilities)
4. [Technology Stack](#technology-stack)
5. [Installation & Setup](#installation--setup)
6. [Components Deep Dive](#components-deep-dive)
7. [UI/UX Design](#uiux-design)
8. [API Integrations](#api-integrations)
9. [Usage Guide](#usage-guide)
10. [Development Journey](#development-journey)

---

## 1. Project Overview

### What is Sentinel Trading Bot?

Sentinel is a **production-grade paper trading dashboard** that simulates real stock trading in Indian markets (NSE/BSE). It combines **Google Gemini AI** for intelligent trade signals with real-time market data, technical indicators, and news analysis.

### Key Objectives

- ✅ **Learn Trading** - Practice without risking real money
- ✅ **AI-Powered Decisions** - Get BUY/WAIT/AVOID signals from Gemini AI
- ✅ **Real Market Data** - Live prices, charts, and news
- ✅ **Portfolio Tracking** - Monitor P&L, holdings, and order history
- ✅ **Professional UI** - Clean, Groww-inspired design

### Target Users

- **Beginner Traders** - Learn market dynamics
- **Strategy Testers** - Validate trading strategies
- **Students** - Understand financial markets
- **Anyone** - Practice trading risk-free

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                       │
│  (Multi-page Dashboard with Premium UI)                    │
└──────────────────┬──────────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼────────┐
│  DATA LAYER    │   │   AI LAYER      │
│  - yfinance    │   │  - Gemini 2.5   │
│  - Web Scraper │   │  - Analyst      │
│  - NSE Data    │   │  - Signals      │
└───────┬────────┘   └────────┬────────┘
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────▼──────────┐
        │  BACKEND LOGIC      │
        │  - Portfolio Mgmt   │
        │  - Order Execution  │
        │  - Technical Calc   │
        └─────────────────────┘
```

### Directory Structure

```
Agent/
├── dashboard_v3/               # Main Application
│   ├── Home.py                # Landing page
│   ├── pages/
│   │   ├── 1_Market_Overview.py
│   │   ├── 2_Stock_Discovery.py
│   │   ├── 3_Stock_Analyzer.py
│   │   ├── 4_Portfolio.py
│   │   ├── 5_Trade_Executor.py
│   │   └── 6_Settings.py
│   ├── premium_theme.py       # Groww-inspired styling
│   ├── market_hours.py        # Trading hours validation
│   ├── navigation.py          # Top nav component
│   └── news_loader.py         # Web scraper for news
├── analyst_agent_gemini.py    # AI trading analyst
├── .env                       # API keys (GOOGLE_API_KEY)
└── requirements.txt           # Dependencies
```

---

## 3. Features & Capabilities

### 3.1 Core Features

#### Home Dashboard
- **Portfolio Snapshot** - Real-time portfolio value, P&L, positions
- **Market Status** - Live NSE/BSE market hours indicator
- **Watchlist** - Track favorite stocks
- **Recent Orders** - Quick view of trade history
- **Quick Actions** - One-click navigation to key features

#### Market Overview
- **Live Indices** - NIFTY 50, SENSEX, BANKNIFTY with real-time prices
- **Market Status** - Open/Closed indicator with IST time
- **Portfolio Summary** - Holdings, cash, total value at a glance

#### Stock Discovery
- **Top Gainers** - 24 best performing stocks
- **Top Losers** - 24 worst performing stocks
- **Most Active** - High volume stocks
- **Real-time Refresh** - 3-minute cached data with manual refresh

#### Stock Analyzer (★ Main Feature)
- **AI-Powered Signals** - Gemini analyzes and provides BUY/WAIT/AVOID recommendations
- **Technical Analysis**
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Bollinger Bands
  - Volume Analysis
  - Trend Detection
- **Interactive Charts** - Candlestick, line, and volume charts
- **News Integration** - Recent news from multiple sources
- **Quick Trade Widget** - Place orders directly from analysis
- **Stop Loss & Target** - AI-suggested risk management levels

#### Portfolio Tracker
- **Current Holdings** - All positions with live prices
- **Profit & Loss** - Real-time P&L calculation
- **Order History** - Complete trade log
- **Portfolio Value** - Total holdings + cash

#### Trade Executor
- **Order Placement** - BUY/SELL with quantity selection
- **Market & Limit Orders** - Flexible order types
- **Order Validation** - Checks cash availability, share ownership
- **Live Price Fetching** - Real-time market prices
- **Trade Confirmation** - Success/error feedback with animations

#### Settings
- **Portfolio Configuration** - Initial capital, refresh intervals
- **Watchlist Management** - Add/remove stocks
- **CSV Import** - Bulk import watchlist
- **Portfolio Reset** - Fresh start option

### 3.2 Advanced Features

#### AI Trading Analyst (Gemini Integration)
```python
# Signal Generation Process
1. Fetch technical indicators (RSI, MACD, Volume, Trend)
2. Scrape recent news
3. Send to Gemini 2.5 Flash
4. AI analyzes holistically
5. Returns BUY/WAIT/AVOID with confidence score
6. Provides reasoning (max 200 chars)
7. Suggests stop loss & take profit levels
```

**Signal Framework:**
- **BUY (Green)** - 2+ bullish signals, confidence ≥ 60%
- **WAIT (Gray)** - Mixed/unclear signals, 40-60% confidence
- **AVOID (Red)** - 2+ bearish signals, negative confidence ≥ 60%

#### Market Hours Validation
- **Trading Hours:** Monday-Friday, 9:15 AM - 3:30 PM IST
- **Order Blocking:** Prevents trades outside market hours
- **Realistic Simulation:** Mimics real broker behavior

#### Technical Indicators Calculation
```python
RSI = Relative Strength Index (14-period)
MACD = 12-26-9 configuration
Bollinger Bands = 20-period SMA ± 2 std dev
Volume = 20-day moving average comparison
Trend = Price vs 50-day SMA
```

---

## 4. Technology Stack

### Frontend
- **Streamlit** (v1.32+) - Web framework
- **Custom CSS** - Groww-inspired premium theme
- **Material Symbols** - Professional iconography
- **Chart.js** (via Streamlit) - Interactive charts

### Backend
- **Python 3.10+** - Core language
- **Pandas** - Data manipulation
- **NumPy** - Numerical computation
- **TA-Lib** - Technical analysis

### Data Sources
- **yfinance** - Yahoo Finance API for stock data
- **Web Scraping** - BeautifulSoup4 + Requests for news
- **NSE/BSE APIs** - Market indices

### AI/ML
- **Google Gemini 2.5 Flash** - LLM for trading analysis
- **google-genai SDK** - Official Gemini Python client
- **Pydantic** - Data validation for AI responses

### Infrastructure
- **python-dotenv** - Environment variable management
- **pytz** - Timezone handling (IST)
- **Logging** - Built-in Python logging

---

## 5. Installation & Setup

### Prerequisites
```bash
- Python 3.10 or higher
- pip package manager
- Google API Key (for Gemini)
```

### Step 1: Clone/Download Project
```bash
cd C:\Users\Karthi\Desktop\Agent
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Key Dependencies:**
```
streamlit>=1.32.0
google-genai>=1.0.0
yfinance>=0.2.30
pandas>=2.0.0
numpy>=1.24.0
beautifulsoup4>=4.12.0
requests>=2.31.0
python-dotenv>=1.0.0
pytz>=2023.3
pydantic>=2.0.0
```

### Step 4: Configure Environment Variables
Create `.env` file:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

**How to get Gemini API Key:**
1. Visit: https://aistudio.google.com/apikey
2. Create new API key
3. Copy and paste in `.env`

### Step 5: Run Dashboard
```bash
cd dashboard_v3
streamlit run Home.py --server.port 8509
```

### Step 6: Access Dashboard
```
Local: http://localhost:8509
Network: http://[your-ip]:8509
```

---

## 6. Components Deep Dive

### 6.1 Home.py - Landing Page

**Purpose:** Central hub for navigation and overview

**Key Features:**
- Session state initialization
- Portfolio snapshot (cash, holdings, P&L)
- Market status indicator
- Watchlist preview
- Recent orders
- Quick action buttons

**Session State Variables:**
```python
st.session_state.paper_portfolio = {
    'cash': 100000.0,
    'positions': [],
    'orders': []
}
st.session_state.watchlist = ['RELIANCE.NS', 'TCS.NS', ...]
st.session_state.settings = {
    'initial_capital': 100000.0,
    'refresh_interval': 60
}
```

### 6.2 Market Overview

**Purpose:** Live market indices and portfolio summary

**Data Sources:**
- NIFTY 50: ^NSEI
- SENSEX: ^BSESN
- BANKNIFTY: ^NSEBANK

**Caching Strategy:**
```python
@st.cache_data(ttl=60)  # 1-minute cache
def fetch_market_data():
    # Fetch from yfinance
    return data
```

### 6.3 Stock Discovery

**Purpose:** Find trading opportunities

**Categories:**
1. **Top Gainers** - Highest % increase
2. **Top Losers** - Highest % decrease
3. **Most Active** - Highest trading volume

**Discovery Sources:**
- NSE 100 stocks (100+ tickers)
- Live data via yfinance
- 3-minute cache for performance

**UI Elements:**
- Card-based layout (4 columns)
- Price, % change metrics
- Direct "Analyze" button

### 6.4 Stock Analyzer (★ Core Component)

**Workflow:**

```
1. Stock Selection
   ↓
2. Data Fetching (yfinance)
   ↓
3. Technical Calculation
   - RSI, MACD, Bollinger Bands
   - Volume, Trend
   ↓
4. News Scraping
   - Web scraping from multiple sources
   ↓
5. AI Analysis (Gemini)
   - Holistic evaluation
   - Signal generation
   ↓
6. Display Results
   - Signal badge (BUY/WAIT/AVOID)
   - Charts (candlestick, indicators)
   - News cards
   - Quick Trade widget
```

**Technical Indicators Module:**
```python
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data):
    exp1 = data['Close'].ewm(span=12).mean()
    exp2 = data['Close'].ewm(span=26).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9).mean()
    return macd, signal
```

**AI Analyst Integration:**
```python
from analyst_agent_gemini import AgenticAnalyst

analyst = AgenticAnalyst(model_name="gemini-2.5-flash")
signal = analyst.analyze_ticker(
    ticker=symbol,
    current_price=price,
    technical_data={
        'RSI': rsi_value,
        'MACD': macd_value,
        'Trend': trend,
        'Volume': volume_ratio
    },
    news_summary=news_text
)

# Returns: TradeSignal(signal, confidence, reasoning, stop_loss, take_profit)
```

**Chart Types:**
1. **Candlestick Chart** - OHLC prices
2. **Volume Bars** - Trading volume
3. **RSI Line** - Momentum indicator
4. **MACD Histogram** - Trend strength

### 6.5 Portfolio Tracker

**Purpose:** Monitor holdings and P&L

**Calculations:**
```python
# For each position
current_value = quantity * current_price
cost_basis = quantity * average_price
unrealized_pnl = current_value - cost_basis
pnl_percentage = (unrealized_pnl / cost_basis) * 100

# Portfolio totals
total_holdings = sum(all position values)
total_portfolio = cash + total_holdings
total_pnl = total_portfolio - initial_capital
```

**Display:**
- Expandable cards per stock
- Real-time price updates
- Color-coded P&L (green/red)
- "Sell" button for each position

### 6.6 Trade Executor

**Purpose:** Place buy/sell orders

**Order Types:**
1. **MARKET** - Execute at current price
2. **LIMIT** - Execute at specified price

**Validation Logic:**
```python
# BUY validation
if side == "BUY":
    total_cost = (quantity * price) + brokerage
    if cash < total_cost:
        error("Insufficient funds")
    else:
        execute_buy()

# SELL validation
if side == "SELL":
    if position_exists and position.quantity >= quantity:
        execute_sell()
    else:
        error("Insufficient shares")
```

**Market Hours Check:**
```python
from market_hours import is_market_open

market_open, message = is_market_open()
if not market_open:
    st.error(message)
    # Block order placement
```

**Brokerage:** 0.03% (₹0.03 per ₹100)

### 6.7 Settings

**Purpose:** Configure dashboard preferences

**Configurable Options:**
- Initial capital (default: ₹100,000)
- Refresh interval
- Watchlist management
- Portfolio reset

**Watchlist Import:**
- CSV upload support
- Format: One ticker per line (e.g., RELIANCE.NS)

---

## 7. UI/UX Design

### Design Philosophy

**Inspired by Groww App:**
- Clean, minimal interface
- Professional typography
- Subtle animations
- Card-based layouts
- Ample white space

### Color Palette

```css
/* Primary Colors */
--primary-green: #00D09C    /* Success, BUY signals */
--primary-red: #EB5B3C      /* Error, AVOID signals */
--neutral-gray: #8B92A0     /* WAIT signals */

/* Background */
--bg-primary: #FFFFFF
--bg-secondary: #F8F9FA

/* Text */
--text-primary: #1A1D29
--text-secondary: #7C7E8C

/* Borders */
--border-color: #E8EAED
```

### Typography

```css
/* Fonts */
--font-ui: 'DM Sans', sans-serif
--font-data: 'JetBrains Mono', monospace

/* Sizes */
--text-xs: 12px
--text-sm: 14px
--text-base: 16px
--text-lg: 18px
--text-xl: 20px
--text-2xl: 24px
```

### Components

#### Navigation Bar
```css
position: sticky
top: 0
background: white
shadow: 0 1px 3px rgba(0,0,0,0.1)
z-index: 1000
```

#### Cards
```css
background: white
border-radius: 8px
padding: 16px-24px
box-shadow: 0 1px 2px rgba(0,0,0,0.05)
border: 1px solid #E8EAED
transition: all 0.2s ease
```

#### Buttons
```css
/* Primary */
background: linear-gradient(135deg, #00D09C 0%, #00B386 100%)
color: white
border-radius: 6px
padding: 10px 20px
font-weight: 600

/* Hover */
transform: translateY(-1px)
box-shadow: 0 4px 12px rgba(0, 208, 156, 0.3)
```

### Iconography

**Material Symbols Used:**
- `trending_up` - Stock growth, BUY signals
- `trending_down` - Stock decline, AVOID signals
- `bar_chart` - Market overview, analytics
- `search` - Stock discovery
- `account_balance_wallet` - Portfolio
- `bolt` - Quick actions, trade executor
- `settings` - Configuration
- `refresh` - Data refresh
- `check_circle` - Success states
- `error` - Error states
- `schedule` - Market hours
- `info` - Information

### Animations

```css
/* Micro-interactions */
transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1)

/* Page transitions */
fade-in: 0.3s ease-in

/* Hover effects */
scale(1.02) on hover
```

### Responsive Design

- **Desktop** - Full 3-4 column layouts
- **Tablet** - 2 column layouts
- **Mobile** - Single column, stacked

---

## 8. API Integrations

### 8.1 Google Gemini API

**Model:** gemini-2.5-flash

**Configuration:**
```python
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
```

**Prompt Engineering:**
```
System Prompt:
- Role: Balanced Quantitative Analyst
- Task: Analyze technicals + news → Generate signal
- Output: JSON with signal, confidence, reasoning

User Prompt:
- Ticker: RELIANCE.NS
- Price: ₹2,450
- RSI: 42 (Neutral)
- MACD: Bullish crossover
- News: Positive earnings report
```

**Response Structure:**
```json
{
  "signal": "BUY",
  "confidence": 0.75,
  "reasoning": "Bullish MACD + positive earnings, RSI neutral allows entry",
  "stop_loss": 2400.0,
  "take_profit": 2550.0
}
```

**Error Handling:**
- Fallback to rule-based logic if API fails
- Retry mechanism (3 attempts)
- Timeout: 10 seconds
- Rate limiting: Handled by SDK

### 8.2 Yahoo Finance (yfinance)

**Use Cases:**
1. Stock price data
2. Historical OHLCV data
3. Market indices
4. Volume data

**Example:**
```python
import yfinance as yf

ticker = yf.Ticker("RELIANCE.NS")
hist = ticker.history(period="1mo")
current_price = hist['Close'].iloc[-1]
```

**Caching:**
```python
@st.cache_data(ttl=60)
def get_stock_data(symbol):
    return yf.Ticker(symbol).history(period="3mo")
```

### 8.3 News Scraping

**Method:** Web scraping (BeautifulSoup4)

**Sources:**
- Google News
- MoneyControl
- Economic Times
- Financial news aggregators

**Implementation:**
```python
def scrape_news(ticker):
    query = ticker.replace('.NS', '')
    url = f"https://www.google.com/search?q={query}+stock+news"
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract headlines
    headlines = soup.find_all('h3')
    return [h.text for h in headlines[:5]]
```

**Fallback:** "No recent news available"

---

## 9. Usage Guide

### Getting Started

1. **Launch Dashboard**
   ```bash
   cd dashboard_v3
   streamlit run Home.py --server.port 8509
   ```

2. **Access in Browser**
   - Open http://localhost:8509
   - Check market status on home page

3. **Configure Watchlist**
   - Go to Settings
   - Add stocks to watchlist (e.g., RELIANCE, TCS, INFY)
   - Save

### Trading Workflow

#### Step 1: Discover Stocks
- Navigate to **Stock Discovery**
- Browse Top Gainers/Losers/Active
- Click "Analyze" on interesting stock

#### Step 2: Analyze Stock
- **Stock Analyzer** page loads
- View AI signal (BUY/WAIT/AVOID)
- Check technical indicators
- Read news
- Review charts

#### Step 3: Make Decision
- If **BUY signal** + confident:
  - Use Quick Trade widget
  - Enter quantity
  - Click "BUY Shares"
  
- If **AVOID signal**:
  - Skip or wait for better entry
  
- If **WAIT signal**:
  - Monitor, comeback later

#### Step 4: Track Portfolio
- Navigate to **Portfolio**
- View all holdings
- Monitor P&L
- Sell when target reached

#### Step 5: Execute Trades
- Go to **Trade Executor** for detailed orders
- Place BUY/SELL orders
- Market hours validation ensures realistic trading

### Best Practices

1. **Start Small** - Begin with ₹10,000 virtual capital
2. **Follow AI Signals** - Trust the Gemini analysis
3. **Set Stop Losses** - Use AI-suggested levels
4. **Monitor News** - Stay updated on company developments
5. **Check Market Hours** - Trade only during 9:15 AM - 3:30 PM IST
6. **Diversify** - Don't put all capital in one stock
7. **Review Regularly** - Check portfolio daily

### Advanced Features

#### Custom Watchlist
```csv
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
ITC.NS
```
Upload in Settings → Watchlist Management

#### Portfolio Analytics
- Total P&L percentage
- Best performing stock
- Worst performing stock
- Cash utilization rate

---

## 10. Development Journey

### Phase 1: Foundation (Days 1-2)
- ✅ Setup Streamlit multi-page structure
- ✅ Integrate yfinance for stock data
- ✅ Basic portfolio tracking
- ✅ Session state management

### Phase 2: Technical Analysis (Days 3-4)
- ✅ Implement RSI calculation
- ✅ MACD indicator
- ✅ Bollinger Bands
- ✅ Volume analysis
- ✅ Trend detection

### Phase 3: AI Integration (Days 5-6)
- ✅ Google Gemini API setup
- ✅ AgenticAnalyst class
- ✅ Prompt engineering
- ✅ Signal generation (BUY/SELL/WAIT)
- ✅ Fallback logic

### Phase 4: News Integration (Day 7)
- ✅ Web scraping implementation
- ✅ News summarization
- ✅ Display in UI

### Phase 5: UI/UX Enhancement (Days 8-10)
- ✅ Groww-inspired theme
- ✅ Material Symbols icons
- ✅ Premium typography (DM Sans, JetBrains Mono)
- ✅ Custom CSS styling
- ✅ Responsive design

### Phase 6: Feature Refinement (Days 11-12)
- ✅ Market hours validation
- ✅ Quick Trade widget
- ✅ Stock Discovery page
- ✅ Settings page
- ✅ CSV import

### Phase 7: Bug Fixes & Polish (Days 13-14)
- ✅ Session state crash fixes
- ✅ Navigation consistency
- ✅ Emoji removal (replaced with icons)
- ✅ Market hours enforcement
- ✅ AI signal rebalancing (BUY/WAIT/AVOID)

### Key Challenges & Solutions

#### Challenge 1: Gemini API Errors
**Problem:** Model not found, deprecated SDK
**Solution:** Switched to `google-genai` SDK, stable model (gemini-2.5-flash)

#### Challenge 2: Too Many "WAIT" Signals
**Problem:** AI was overly conservative
**Solution:** Rewrote system prompt, lowered confidence threshold (70% → 60%)

#### Challenge 3: Unicode Errors
**Problem:** Emojis in code causing crashes
**Solution:** Added UTF-8 encoding, replaced all emojis with Material Symbols

#### Challenge 4: Session State Crashes
**Problem:** Missing portfolio initialization
**Solution:** Added initialization checks in all pages

#### Challenge 5: Trading Outside Market Hours
**Problem:** Unrealistic 24/7 trading
**Solution:** Implemented `market_hours.py` validation module

### Lessons Learned

1. **Start with Planning** - Clear architecture saves time
2. **Incremental Development** - Build feature by feature
3. **Error Handling is Critical** - Especially with external APIs
4. **UI Matters** - Clean design improves user experience
5. **Testing is Essential** - Test edge cases (market closed, no funds, etc.)
6. **Documentation** - Good docs help future you

---

## 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Total Files** | 12+ Python files |
| **Lines of Code** | 3,500+ |
| **Pages** | 6 main pages |
| **Features** | 20+ features |
| **API Integrations** | 3 (Gemini, yfinance, Web Scraping) |
| **Development Time** | 14 days |
| **Supported Stocks** | 100+ NSE stocks |

---

## 🎯 Future Enhancements

### Planned Features
- [ ] **Historical Backtesting** - Test strategies on past data
- [ ] **Advanced Charts** - More technical indicators
- [ ] **Alerts System** - Price/signal notifications
- [ ] **Multiple Portfolios** - Manage different strategies
- [ ] **Export Reports** - PDF/CSV portfolio reports
- [ ] **Leaderboard** - Compare with other users
- [ ] **Options Trading** - F&O simulation
- [ ] **Mobile App** - React Native version

---

## 📝 Conclusion

Sentinel Trading Bot is a **comprehensive paper trading platform** that combines:
- 🤖 **AI-powered analysis** (Google Gemini)
- 📈 **Real market data** (yfinance)
- 📰 **News integration** (Web scraping)
- 🎨 **Professional UI** (Groww-inspired)
- 💼 **Complete portfolio management**

Perfect for **learning**, **practicing**, and **mastering** stock trading without financial risk!

---

## 📞 Support & Contact

**Created by:** Karthi  
**Project Location:** `C:\Users\Karthi\Desktop\Agent`  
**Documentation:** This file  

---

*Last Updated: February 3, 2026*  
*Version: 1.0.0*  
*Status: Production Ready ✅*
