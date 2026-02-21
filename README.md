# Sentinel Trading Bot

**Autonomous AI Trading System for Indian Stock Markets (NSE/BSE)**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.0-4285F4.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

Sentinel is a **production-grade autonomous paper trading platform** built on a **LangGraph multi-agent system** powered by **Google Gemini 2.0 Flash**. Five specialized AI agents work together 24/7 to discover stocks, analyze them with AI + technical indicators, assess risk, and execute paper trades on the NSE/BSE.

---

## Beta Wokring Portfolio

Link : https://sentinel-dashboard-production.up.railway.app

Note: This is sample of this project,still the web app part is under development.The engine ( Lang graph Agent is Production ready and scalable)

---

## Architecture

```
Supervisor Agent
    ├── Scout Agent        → Discovers tradeable NSE/BSE stocks
    ├── Analyst Agent      → AI analysis (Gemini 2.0 + RSI/MACD/Bollinger Bands)
    ├── Risk Manager       → Validates position sizing & risk limits
    └── Trader Agent       → Executes paper trades & updates portfolio
```

All agents share a typed **LangGraph StateGraph** and route through the Supervisor using conditional edges. The system runs 24/7 via `run_autonomous.py`, respecting NSE market hours (9:15 AM – 3:30 PM IST).

---

## Key Features

### AI & Multi-Agent
- **5 LangGraph Agents** — Supervisor, Scout, Analyst, Risk Manager, Trader
- **Google Gemini 2.0 Flash** — Powers AI stock analysis with structured JSON outputs
- **RAG Pipeline** — Combines real-time news (GNews API) with technical indicators as LLM context
- **Pydantic Validation** — Type-safe structured outputs (`BUY / WAIT / AVOID` signals with confidence scores)
- **Fallback Mode** — Rule-based analysis (RSI + MACD) when AI is unavailable

### Dashboard (8 Pages)
| Page | Description |
|------|-------------|
| Home | Portfolio overview, market status, watchlist |
| Market Overview | Live NIFTY 50, SENSEX, BANKNIFTY indices |
| Stock Discovery | Top gainers, losers, most active NSE stocks |
| Stock Analyzer | AI signals, charts, technical indicators |
| Portfolio | Holdings, P&L, order history |
| Trade Executor | Manual buy/sell with market hours validation |
| Settings | Capital, watchlist, API configuration |
| God Mode | Live agent activity monitor with state inspector |

### Autonomous System
- **24/7 Operation** — Auto-restarts, error recovery, rate limiting
- **Database Logging** — SQLite tracks every agent thought and workflow
- **Autonomous Control UI** — Start/stop agents from the dashboard

---

## Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key → [Get free key](https://aistudio.google.com/apikey)
- GNews API key → [Get free key](https://gnews.io) *(100 requests/day free)*

### Installation

```bash
git clone https://github.com/karthixcarlo/sentinel-trading-bot.git
cd sentinel-trading-bot

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt

copy .env.example .env
# Edit .env — add GEMINI_API_KEY, GNEWS_API_KEY
```

### Run Dashboard

```bash
streamlit run dashboard_v3/Home.py --server.port 8501
```
Open → **http://localhost:8501**

### Run Autonomous System (Optional)

```bash
python run_autonomous.py
```

Runs agents 24/7. Pauses automatically when market is closed.

---

## Environment Variables

```env
GEMINI_API_KEY=your_gemini_key_here
GNEWS_API_KEY=your_gnews_key_here
```

---

## Project Structure

```
sentinel-trading-bot/
├── agents/                        # LangGraph agent nodes
│   ├── supervisor.py              # Orchestrates routing
│   ├── scout_agent.py             # Stock discovery
│   ├── analyst_agent.py           # LangGraph analyst wrapper
│   ├── risk_manager.py            # Trade validation
│   └── trader_agent.py            # Order execution
├── dashboard_v3/                  # Streamlit dashboard
│   ├── Home.py                    # Entry point
│   ├── layout.py                  # Global CSS/theme
│   ├── navigation.py              # Top nav bar
│   ├── market_hours.py            # NSE/BSE hours logic
│   ├── premium_theme.py           # Design tokens
│   └── pages/                     # 8 dashboard pages
├── .github/workflows/deploy.yml   # CI/CD pipeline
├── analyst_agent_gemini.py        # Core Gemini AI integration
├── sentinel_hive.py               # LangGraph StateGraph
├── sentinel_state.py              # Shared agent state (TypedDict)
├── run_autonomous.py              # 24/7 autonomous runner
├── database_manager.py            # SQLite logging
├── market_loader.py               # Live market data (yfinance)
├── paper_trading_portfolio.py     # Virtual portfolio management
├── nse_stock_universe.py          # NSE/BSE stock universe
├── stock_signal_indicator.py      # Signal display helper
├── init_schema.sql                # Supabase PostgreSQL schema
├── render.yaml                    # Render deployment blueprint
├── requirements.txt               # Pinned dependencies
└── .env.example                   # Environment template
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Orchestration** | LangGraph 0.2, LangChain Core |
| **AI / LLM** | Google Gemini 2.0 Flash |
| **Frontend** | Streamlit 1.41, Custom CSS |
| **Market Data** | yfinance (NSE/BSE live prices) |
| **News / RAG** | GNews API |
| **Database** | SQLite (local), Supabase PostgreSQL (cloud) |
| **Deployment** | Render (Web + Worker), GitHub Actions CI/CD |
| **Validation** | Pydantic 2.x |

---

## Deployment

The project includes production deployment configuration:
- **`render.yaml`** — Deploys Streamlit dashboard + background worker on Render
- **`init_schema.sql`** — Supabase PostgreSQL schema with Row Level Security
- **`.github/workflows/deploy.yml`** — CI/CD: test → deploy on push to `main`

See the [deployment guide](https://github.com/karthixcarlo/sentinel-trading-bot#readme) for step-by-step instructions.

---

## Disclaimer

This is a **paper trading platform for educational purposes only**. No real money is involved. This is NOT financial advice. Always do your own research before investing.

---

<div align="center">

**Built by [Karthi](https://github.com/karthixcarlo)**

⭐ Star this repo if you find it useful!

</div>
