# Sentinel Trading Bot

**Autonomous AI Trading System for Indian Stock Markets (NSE/BSE)**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini%202.5%20Flash-4285F4.svg)](https://ai.google.dev/)
[![Supabase](https://img.shields.io/badge/Auth-Supabase-3FCF8E.svg)](https://supabase.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

Sentinel is a **production-grade autonomous paper trading platform** built on a **LangGraph multi-agent system** powered by **Google Gemini 2.5 Flash**. Five specialized AI agents work together to discover stocks, analyze them with AI + technical indicators, assess risk with configurable thresholds, and execute paper trades on the NSE.

**Live Demo:** [sentinel-trading-bot.vercel.app](https://sentinel-trading-bot.vercel.app)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Vercel (Frontend)           │  Render (Backend)                 │
│  React + Vite + TailwindCSS  │  FastAPI + LangGraph + SQLite     │
│  Port 5173 (dev)             │  Port 8001 (dev)                  │
│                              │                                   │
│  VITE_API_URL ──────────────▶│  REST API + WebSocket              │
│  VITE_SUPABASE_URL ─────────▶│  JWT verification                  │
└──────────────────────────────┴───────────────────────────────────┘
                                        │
                                        ▼
                               ┌────────────────┐
                               │   Supabase      │
                               │   PostgreSQL    │
                               │   + Auth + RLS  │
                               └────────────────┘
```

### LangGraph Multi-Agent Pipeline

```
Supervisor Agent (Gemini — routing decisions)
    ├── Scout Agent        → Discovers tradeable NSE stocks via yfinance
    ├── Analyst Agent      → Gemini 2.5 Flash AI analysis + RSI/MACD/Bollinger
    ├── Risk Manager       → Dynamic confidence thresholds from user settings
    └── Trade Executor     → Paper trades → SQLite/Supabase logging
```

All agents share a typed **LangGraph StateGraph** (`sentinel_state.py`) and route through the Supervisor using conditional edges. The system runs in 5-minute cycles, respecting NSE market hours (9:15 AM – 3:30 PM IST).

---

## Key Features

### AI & Multi-Agent System
- **5 LangGraph Agents** — Supervisor, Scout, Analyst, Risk Manager, Trader
- **Google Gemini 2.5 Flash** — Powers AI stock analysis with structured JSON outputs
- **Configurable Risk Thresholds** — Conservative (85%), Moderate (70%), Aggressive (55%) confidence gates
- **Sector Filtering** — IT, Banking, Energy, Automobile, FMCG, Pharma, Metals
- **Real-time WebSocket Feed** — Live agent thoughts streamed to the UI

### Frontend (React + Vite)

| Page | Description |
|------|-------------|
| **Dashboard** | Portfolio overview, market stats, quick actions |
| **Trading Chart** | Interactive candlestick + volume chart (lightweight-charts v5) |
| **Autonomous Control** | Start/stop agent, live thought feed, server-synced state |
| **God Mode** | Real-time WebSocket neural feed from all agents |
| **Portfolio** | Holdings, P&L, trade history |
| **Market / Discover** | Sector browsing, top movers |
| **Analyze** | AI-powered stock analysis view |
| **Trade Executor** | Manual buy/sell with market hours validation |
| **Settings** | Risk appetite, max position %, allowed sectors |

### Authentication & Security
- **Supabase Auth** — Email/password signup with JWT sessions
- **Demo Mode** — Full access without signup when Supabase is not configured
- **Protected Routes** — React `ProtectedRoute` wrapper with auth redirect
- **Backend JWT Verification** — PyJWT validates Supabase tokens; graceful demo fallback
- **Row Level Security** — PostgreSQL RLS policies on all user data

### Autonomous System
- **Server-Side State** — Running status persists across page navigation and tab hibernation
- **Lightweight Polling** — `/api/autonomous/status` endpoint for cheap 30-second heartbeats
- **Auto Error Recovery** — Max 5 consecutive errors before pause, 1-minute backoff
- **Uptime Tracking** — `start_time` shown in the UI as "Running since HH:MM:SS"

---

## Quick Start

### Prerequisites

- **Python 3.10+**
- **Node.js 20+**
- **Google Gemini API key** — [Get free key](https://aistudio.google.com/apikey)

### Installation

```bash
git clone https://github.com/karthixcarlo/sentinel-trading-bot.git
cd sentinel-trading-bot
```

#### Backend

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r backend/requirements.txt

# Create .env in project root
echo "GEMINI_API_KEY=your_key_here" > .env
```

#### Frontend

```bash
cd frontend
npm ci
```

### Run Locally

Start both servers (in separate terminals):

```bash
# Terminal 1 — Backend (port 8001)
cd backend
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 2 — Frontend (port 5173)
cd frontend
npm run dev
```

Open **http://localhost:5173** — The Vite dev server proxies `/api` and `/ws` requests to the backend automatically.

---

## Environment Variables

### Backend (.env)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI agents |
| `SUPABASE_URL` | No | Supabase project URL (demo mode if omitted) |
| `SUPABASE_KEY` | No | Supabase service role key |
| `SUPABASE_JWT_SECRET` | No | Supabase JWT secret for token verification |
| `ALLOWED_ORIGINS` | No | Comma-separated CORS origins (defaults include localhost + Vercel) |

### Frontend (Vercel Environment Variables)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Yes (prod) | Backend URL (e.g., `https://your-app.onrender.com`) |
| `VITE_SUPABASE_URL` | No | Supabase project URL (demo mode if omitted) |
| `VITE_SUPABASE_ANON_KEY` | No | Supabase anon/public key |

---

## API Reference

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check with uptime and version |
| `GET` | `/api/agent/status` | Full agent status (running, portfolio, thoughts) |
| `GET` | `/api/autonomous/status` | Lightweight: running flag + start_time only |

### Agent Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agent/start` | Start autonomous trading loop |
| `POST` | `/api/agent/stop` | Stop autonomous trading loop |
| `GET` | `/api/agent/thoughts?limit=50` | Recent agent thought log |
| `GET` | `/api/agent/trades?limit=50` | Trade history |
| `GET` | `/api/agent/portfolio` | Current portfolio state |

### Market Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/market-data/{symbol}` | OHLCV candlestick data via yfinance |
| `GET` | `/api/analyze/{symbol}` | AI analysis for a stock |

### User Data (JWT-protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/portfolio/{user_id}` | User portfolio |
| `GET/POST` | `/api/settings/{user_id}` | User settings (risk appetite, sectors) |
| `GET` | `/api/watchlist` | User watchlist |
| `POST` | `/api/watchlist` | Add ticker to watchlist |
| `DELETE` | `/api/watchlist/{ticker}` | Remove ticker from watchlist |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host/ws/neural-feed` | Real-time agent thought stream |

---

## Project Structure

```
sentinel-trading-bot/
├── backend/
│   ├── main.py                    # FastAPI app — all REST + WebSocket endpoints
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api.js                 # BASE_URL + WS_BASE (env-driven)
│   │   ├── main.jsx               # Routes + ProtectedRoute
│   │   ├── Auth.jsx               # Login / signup page
│   │   ├── AuthContext.jsx        # Supabase auth provider + useAuth hook
│   │   ├── supabaseClient.js      # Supabase client (null in demo mode)
│   │   ├── Sidebar.jsx            # Navigation + user profile
│   │   ├── Dashboard.jsx          # Portfolio overview
│   │   ├── AutonomousControl.jsx  # Agent start/stop + server-synced state
│   │   ├── GodMode.jsx            # WebSocket neural feed
│   │   ├── Portfolio.jsx          # Holdings + P&L
│   │   ├── Settings.jsx           # User preferences
│   │   ├── TradeExecutor.jsx      # Manual trade entry
│   │   ├── Analyze.jsx            # AI analysis view
│   │   ├── Market.jsx             # Market overview
│   │   ├── Discover.jsx           # Sector browsing
│   │   └── components/
│   │       ├── TradingChart.jsx   # lightweight-charts v5 candlestick
│   │       └── CopilotSidebar.jsx # AI chat assistant
│   ├── vite.config.js             # Dev proxy + resolve.conditions
│   ├── vercel.json                # Forces npm ci on Vercel
│   ├── package.json               # Dependencies (supabase@2.39.3 pinned)
│   └── tailwind.config.js         # Tailwind theme
├── agents/
│   ├── supervisor.py              # LangGraph routing agent
│   ├── scout_agent.py             # Stock discovery (yfinance)
│   ├── analyst_agent.py           # Gemini AI analysis
│   ├── risk_manager.py            # Dynamic risk thresholds
│   └── trader_agent.py            # Order execution
├── agent_service.py               # AgentService singleton (runs LangGraph)
├── sentinel_hive.py               # LangGraph StateGraph definition
├── sentinel_state.py              # Shared typed state (TypedDict)
├── broker_engine.py               # Trade execution engine
├── supabase_setup.sql             # Idempotent DB schema + RLS + triggers
├── dev_sync_watcher.py            # Auto git push on file changes
├── Procfile                       # Render/Heroku deployment
├── .github/workflows/ci.yml       # CI: Python compile + Node build
└── .gitignore                     # node_modules, dist, .env excluded
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI / LLM** | Google Gemini 2.5 Flash |
| **Agent Orchestration** | LangGraph 0.2, LangChain Core |
| **Frontend** | React 18, Vite 5, TailwindCSS 3, lightweight-charts v5 |
| **Backend** | FastAPI, Uvicorn, WebSocket |
| **Auth** | Supabase Auth, PyJWT |
| **Market Data** | yfinance (NSE live prices) |
| **Database** | SQLite (local), Supabase PostgreSQL (cloud) |
| **Frontend Hosting** | Vercel |
| **Backend Hosting** | Render |
| **CI/CD** | GitHub Actions |

---

## Deployment

### Frontend → Vercel

1. Import repo on [vercel.com](https://vercel.com)
2. Set **Root Directory** to `frontend`
3. Set **Framework Preset** to `Vite`
4. Add environment variables: `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`
5. Deploy — Vercel runs `npm ci && npm run build` automatically

### Backend → Render

1. Create a **Web Service** on [render.com](https://render.com)
2. Connect the GitHub repo
3. Set **Build Command**: `pip install -r backend/requirements.txt`
4. Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `GEMINI_API_KEY`, `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_JWT_SECRET`, `ALLOWED_ORIGINS`

### Database → Supabase

1. Create a project on [supabase.com](https://supabase.com)
2. Open **SQL Editor** and run `supabase_setup.sql` (idempotent — safe to re-run)
3. Copy your project URL, anon key, and JWT secret to the environment variables above

---

## Risk Thresholds

The Risk Manager agent uses configurable confidence thresholds set from the Settings page:

| Risk Appetite | Min Confidence | Description |
|---------------|----------------|-------------|
| **Conservative** | 85% | Only high-conviction trades pass through |
| **Moderate** | 70% | Balanced risk/reward (default) |
| **Aggressive** | 55% | More trades, higher risk tolerance |

---

## Disclaimer

This is a **paper trading platform for educational purposes only**. No real money is involved. This is NOT financial advice. Always do your own research before investing.

---

<div align="center">

**Built by [Karthi](https://github.com/karthixcarlo)**

Star this repo if you find it useful!

</div>
