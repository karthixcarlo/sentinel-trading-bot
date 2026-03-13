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
- **Backend JWT Verification** — PyJWT validates Supabase tokens on all mutating endpoints; graceful demo fallback
- **WebSocket Auth** — Optional `?token=` query param verified server-side
- **CORS Lockdown** — Explicit origin allowlist (no wildcard + credentials violation)
- **Auth-aware API Client** — Centralized `api.js` attaches Bearer tokens automatically
- **Row Level Security** — PostgreSQL RLS policies on all user data
- **Error Boundaries** — React class-component error boundaries on every route prevent full-app crashes

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
| `GET` | `/api/market/ohlcv/{ticker}` | OHLCV candlestick data via yfinance |
| `GET` | `/api/market/discover` | Discovery grid with live NSE prices |
| `GET` | `/api/market/analyze/{ticker}` | AI-powered stock analysis (Gemini) |
| `GET` | `/api/market/indices` | Nifty 50, Bank Nifty, Sensex |

### Trading (JWT-protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/trade/manual` | Trigger manual trade execution |
| `POST` | `/api/trade/execute` | Execute BUY/SELL with live pricing |

### User Data (JWT-protected)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/portfolio/{user_id}` | User portfolio |
| `GET` | `/api/portfolio/{user_id}/detail` | Portfolio with per-position P&L |
| `GET/PUT` | `/api/settings/{user_id}` | User settings (risk appetite, sectors) |
| `GET` | `/api/watchlist` | User watchlist |
| `POST` | `/api/watchlist` | Add ticker to watchlist |
| `DELETE` | `/api/watchlist/{ticker}` | Remove ticker from watchlist |

### Chat

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/copilot` | AI trading copilot (Gemini + agent logs) |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `ws://host/ws/neural-feed` | Real-time agent thought stream |

---

## Project Structure

```
sentinel-trading-bot/
├── backend/
│   ├── main.py                    # Thin FastAPI aggregator (~80 lines) — CORS, health, router registration
│   ├── deps.py                    # Shared dependencies: JWT auth, ticker validation, resolve_user_id
│   ├── routers/
│   │   ├── auth.py                # POST /api/auth/login
│   │   ├── chat.py                # POST /api/chat/copilot (Gemini + agent logs)
│   │   ├── market.py              # OHLCV, discover, analyze, indices
│   │   ├── portfolio.py           # Portfolio + per-position P&L detail
│   │   ├── trade.py               # Trade execution + demo SQLite helpers
│   │   ├── agent.py               # Agent start/stop/status/portfolio/thoughts/trades
│   │   ├── settings.py            # User settings CRUD (risk appetite, sectors)
│   │   ├── watchlist.py           # Watchlist CRUD (Supabase + SQLite fallback)
│   │   └── ws.py                  # WebSocket /ws/neural-feed + autonomous status
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api.js                 # BASE_URL, WS_BASE, auth-aware fetch client
│   │   ├── main.jsx               # Routes + ProtectedRoute + ErrorBoundary wrappers
│   │   ├── Auth.jsx               # Login / signup page
│   │   ├── AuthContext.jsx         # Supabase auth provider + useAuth hook
│   │   ├── ThemeContext.jsx        # Light/dark mode theme provider
│   │   ├── supabaseClient.js      # Supabase client (null in demo mode)
│   │   ├── Layout.jsx             # Sidebar + Outlet layout wrapper
│   │   ├── Dashboard.jsx          # Portfolio overview
│   │   ├── AutonomousControl.jsx  # Agent start/stop + server-synced state
│   │   ├── GodMode.jsx            # Real-time neural feed terminal
│   │   ├── Portfolio.jsx          # Holdings + P&L
│   │   ├── Settings.jsx           # User preferences
│   │   ├── TradeExecutor.jsx      # Manual trade entry
│   │   ├── Analyze.jsx            # AI analysis view
│   │   ├── Market.jsx             # Market overview
│   │   ├── Discover.jsx           # Sector browsing
│   │   ├── hooks/
│   │   │   ├── useNeuralFeed.js   # Shared WebSocket hook (replaces 3× copy-paste)
│   │   │   └── useAgentStatus.js  # Shared agent status polling hook
│   │   └── components/
│   │       ├── TradingChart.jsx   # lightweight-charts v5 candlestick
│   │       ├── ReasoningEngine.jsx # Slide-out AI reasoning panel
│   │       ├── ErrorBoundary.jsx  # React error boundary with retry UI
│   │       └── CopilotSidebar.jsx # AI chat assistant
│   ├── vite.config.js             # Dev proxy + resolve.conditions
│   ├── vercel.json                # Vercel deployment config
│   ├── package.json               # Dependencies
│   └── tailwind.config.js         # Tailwind theme (dark + light palettes)
├── services/
│   ├── auth_manager.py            # Supabase auth + portfolio DB operations
│   └── news_loader.py             # News scraping for AI analyst context
├── agents/
│   ├── supervisor.py              # LangGraph routing agent
│   ├── scout_agent.py             # Stock discovery (yfinance)
│   ├── analyst_agent.py           # Gemini AI analysis
│   ├── risk_manager.py            # Dynamic risk thresholds
│   └── trader_agent.py            # Order execution
├── agent_service.py               # AgentService singleton (runs LangGraph)
├── sentinel_hive.py               # LangGraph StateGraph definition
├── sentinel_state.py              # Shared typed state (TypedDict)
├── langgraph_agents.py            # Shared Gemini LLM instance
├── broker_engine.py               # Trade execution engine
├── database_manager.py            # SQLite thought + trade logging
├── market_loader.py               # yfinance market data loader
├── analyst_agent_gemini.py        # Core Gemini AI analyst integration
├── supabase_setup.sql             # Idempotent DB schema + RLS + triggers
├── .env.example                   # Environment variable template
├── Procfile                       # Render deployment entry point
├── .github/workflows/
│   ├── ci.yml                     # Legacy CI (compile + build)
│   ├── backend-ci.yml             # Backend CI: Ruff lint + compile + pytest
│   └── frontend-ci.yml            # Frontend CI: ESLint + Vite build
└── .gitignore                     # node_modules, dist, .env, *.db excluded
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

### Backend → Render (Primary)

1. Create a **Web Service** on [render.com](https://render.com)
2. Connect the GitHub repo — `render.yaml` auto-configures the service
3. Or manually set **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
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

## DevOps & CI/CD

### GitHub Actions Pipelines

Sentinel uses two dedicated CI pipelines that run automatically on every push and pull request to `main`:

| Workflow | File | Trigger Paths | Jobs |
|----------|------|---------------|------|
| **Backend CI** | `.github/workflows/backend-ci.yml` | `backend/`, `agents/`, `services/`, `*.py` | Ruff lint, compile check, pytest |
| **Frontend CI** | `.github/workflows/frontend-ci.yml` | `frontend/` | ESLint, Vite build |

**Backend CI** runs three jobs:
1. **Lint (Ruff)** — Fast Python linter checking for syntax errors, undefined names, and unused imports.
2. **Compile Check** — Verifies all Python files compile without syntax errors with full dependencies installed.
3. **Tests (pytest)** — Runs the `tests/` suite covering state management, agent configuration, portfolio logic, and broker input validation.

**Frontend CI** runs two jobs:
1. **Lint (ESLint)** — Catches React errors, hook violations, and unused variables.
2. **Build (Vite)** — Ensures the production build compiles without errors.

### Branch Protection Rules

To prevent broken code from reaching production, configure **GitHub Branch Protection** on `main`:

1. Go to **Settings → Branches → Add branch protection rule**
2. Set **Branch name pattern** to `main`
3. Enable **Require status checks to pass before merging**
4. Search and add these required checks:
   - `Lint (Ruff)`
   - `Compile Check`
   - `Tests (pytest)`
   - `Lint (ESLint)`
   - `Build (Vite)`
5. Enable **Require branches to be up to date before merging**
6. Optionally enable **Require a pull request before merging** with at least 1 approval

This ensures every PR must pass all CI checks before it can be merged to `main`. Vercel and Render deploy automatically from `main`, so these gates protect production.

---

## Disclaimer

This is a **paper trading platform for educational purposes only**. No real money is involved. This is NOT financial advice. Always do your own research before investing.

---

<div align="center">

**Built by [Karthi](https://github.com/karthixcarlo)**

Star this repo if you find it useful!

</div>
