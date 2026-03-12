# Sentinel V4 — Architectural Audit & Development Roadmap

> Generated: 2026-03-13
> Audit scope: Full-stack codebase (React 18 + FastAPI + Supabase + LangGraph)

---

## 1. Executive Summary

**Project Sentinel** is an autonomous AI trading platform for Indian stock markets (NSE/BSE) built with React/Vite on Vercel, FastAPI on Render, Supabase for auth/DB, and a LangGraph multi-agent pipeline powered by Google Gemini.

### Current State (V3)

| Layer | Status | Health |
|-------|--------|--------|
| Frontend (React/Vite/Vercel) | Deployed | Stable — polished Groww-style dark/light theme, 9 pages, command palette, chart grid |
| Backend (FastAPI/Render) | Deployed | Functional but fragile — monolithic, zero auth on API routes |
| Database (Supabase) | Active | RLS policies in place, but backend bypasses them entirely |
| AI Pipeline (LangGraph) | Embedded | AgentService singleton in main.py, in-memory state only |
| CI/CD | None | No tests, no pipelines, no linting |

**Overall Assessment:** The product surface is impressive for a prototype. The UI is production-grade. However, the backend has **critical security gaps** (zero JWT verification on any route), a **monolithic architecture** (1,051-line main.py), and **zero automated tests**. These must be addressed before any feature expansion.

---

## 2. Critical Tech Debt (Priority Order)

### P0 — Security (Must Fix Immediately)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | **No JWT verification on ANY FastAPI route** | `backend/main.py` — all endpoints | Any anonymous user can execute trades, start/stop agents, read portfolios. The `services/auth_manager.py` exists but is never imported by the API. |
| 2 | **WebSocket endpoint has no authentication** | `backend/main.py` `/ws/neural-feed` | Anyone can connect and receive all agent thoughts and trade signals. |
| 3 | **CORS wildcard with credentials** | `backend/main.py:27-46` | `allow_origins=["*"]` + `allow_credentials=True` is spec-invalid. Falls back to wildcard when `ALLOWED_ORIGINS` is empty. |
| 4 | **Trade endpoint trusts client-supplied user_id** | `POST /api/trade/execute` | The `user_id` comes from the request body with no server-side verification. Any caller can trade on behalf of any user. |
| 5 | **Gemini error leaks internals** | `/api/chat/copilot` | Generic `except Exception` returns raw exception message to client. |

### P1 — Architectural Debt

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 6 | **Monolithic 1,051-line main.py** | `backend/main.py` | Contains CORS config, WebSocket manager, AgentService class, 15+ routes, Pydantic models, utility functions — all in one file. Unmaintainable. |
| 7 | **Agent state is in-memory only** | `AgentService` singleton | Server restart loses all portfolio state, running agent status, and trade history. No persistence layer. |
| 8 | **Duplicated WebSocket connections** | `AutonomousControl.jsx`, `GodMode.jsx`, `ReasoningEngine.jsx` | Three components independently connect to the same `/ws/neural-feed` endpoint. Should be a shared React context/hook. |
| 9 | **WebSocket reconnection leaks** | All 3 WS components | `setTimeout(connect, 3000)` in `onclose` is never cleared on component unmount. Causes state updates on unmounted components. |
| 10 | **TradingChart ResizeObserver leak** | `components/TradingChart.jsx:96-105` | The `ResizeObserver.disconnect()` cleanup is returned from the async `fetchChartData()` but never actually called by the `useEffect` cleanup. |
| 11 | **No error boundaries** | Entire React app | Any component crash white-screens the whole application. |
| 12 | **Zero dependency version pinning** | `requirements.txt` | `fastapi`, `supabase`, `langchain` etc. have no version pins. A breaking upstream release will break deploys. |

### P2 — Code Quality

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 13 | **Inconsistent error handling** | Backend routes | Some return `HTTPException`, some return `JSONResponse`, some silently fall back to demo data. No unified pattern. |
| 14 | **Ticker validation not universal** | `backend/main.py` | `_validate_ticker()` is only used on `/ohlcv` and `/analyze`, but not on `/api/trade/execute` which also accepts a symbol. |
| 15 | **N+1 API calls for portfolio pricing** | Portfolio detail endpoint | Fetches current price via yfinance for each position sequentially. Slow with many positions. |
| 16 | **Duplicated fetch patterns** | `Dashboard.jsx`, `Portfolio.jsx`, `TradeExecutor.jsx` | Portfolio fetching logic is copy-pasted across 3 components. |
| 17 | **UI component library unused** | `components/ui/` | Button, Card, Input, Badge components exist but most pages use raw Tailwind classes instead. |
| 18 | **Dead dependencies** | `requirements.txt` | `websockets` package is listed but unused (FastAPI uses Starlette's built-in WS). `langchain`/`langgraph` may be partially dead. |

---

## 3. V4 Feature Blueprint

### Epic 1: Security & Auth Hardening

**Goal:** Every API route validates the caller's identity via Supabase JWT.

- **JWT Middleware:** Create `middleware/auth.py` with a FastAPI dependency that extracts + verifies Supabase JWT from the `Authorization: Bearer <token>` header on every protected route. Extract `user_id` from the token — never trust the client body.
- **WebSocket Auth:** Require a token query parameter on WS connect (`/ws/neural-feed?token=xxx`), verify before accepting.
- **CORS Lockdown:** Whitelist only the production Vercel URL + localhost for development. Remove wildcard fallback.
- **Rate Limiting:** Add `slowapi` or similar rate limiter on auth endpoints and trade execution.

### Epic 2: Backend Decomposition

**Goal:** Break `main.py` into a proper FastAPI project structure.

```
backend/
  main.py              # App factory, middleware, startup
  routers/
    market.py          # /api/market/* routes
    portfolio.py       # /api/portfolio/* routes
    trade.py           # /api/trade/* routes
    agent.py           # /api/agent/* routes
    settings.py        # /api/settings/* routes
    chat.py            # /api/chat/* routes
  services/
    agent_service.py   # AgentService singleton (extracted)
    portfolio_service.py
    market_data.py     # yfinance wrapper with caching
  models/
    schemas.py         # All Pydantic request/response models
  middleware/
    auth.py            # JWT verification dependency
  ws/
    neural_feed.py     # WebSocket manager
```

### Epic 3: State Persistence & Reliability

**Goal:** Agent state survives server restarts.

- **Persist agent status** to Supabase: `agent_runs` table with `status`, `start_time`, `portfolio_snapshot`, `config`.
- **Persist portfolio state** to Supabase on every trade execution, not just in-memory.
- **Background task recovery:** On startup, check if an agent run was interrupted and resume or mark as crashed.
- **Database migrations:** Adopt Alembic or Supabase migrations instead of raw SQL files.

### Epic 4: Advanced Multi-Agent Architecture

**Goal:** Evolve from a monolithic AgentService to specialized, composable agents.

| Agent | Responsibility | Data Sources |
|-------|---------------|-------------|
| **Market Sentiment Agent** | Aggregate news sentiment, social signals, FII/DII flows | NewsAPI, RSS feeds, Twitter/X API |
| **Technical Analysis Agent** | Compute indicators (RSI, MACD, Bollinger, SuperTrend), detect patterns | yfinance OHLCV data, custom indicators |
| **Fundamental Analysis Agent** | Earnings, P/E ratios, sector rotation analysis | Financial APIs, quarterly results |
| **Risk Management Agent** | Position sizing, portfolio heat, drawdown limits, correlation analysis | Portfolio state, VaR calculations |
| **Execution Agent** | Order routing, slippage estimation, timing optimization | Broker APIs (Zerodha Kite, Angel One) |
| **Supervisor** | Orchestrates agents via LangGraph, resolves conflicts, makes final call | All agent outputs |

**Communication:** Agents communicate via LangGraph's state graph with typed messages. Each agent's reasoning is streamed to the frontend via the existing WebSocket.

### Epic 5: Pro-Grade UI/UX

**Goal:** Match professional trading terminal aesthetics.

- **Shared WebSocket Context:** Create a `useNeuralFeed()` hook that manages a single WebSocket connection, shared across all components that need live data.
- **Error Boundaries:** Wrap each page-level route in a React Error Boundary with a fallback UI.
- **Advanced Charts:**
  - Multi-timeframe support (1D, 1W, 1M, 3M, 6M, 1Y)
  - Drawing tools overlay (trendlines, support/resistance)
  - Technical indicator overlays (RSI, MACD, Volume profile)
  - Split-screen chart comparison
- **Portfolio Analytics Dashboard:**
  - Equity curve chart (daily P&L over time)
  - Sector allocation pie chart
  - Risk metrics panel (Sharpe ratio, max drawdown, beta)
  - Trade journal with AI annotations
- **Real-time Watchlist:** Live price updates via WebSocket with sparkline mini-charts
- **Mobile Responsive:** Currently hidden on mobile (`hidden md:flex` sidebar). Add a hamburger menu + bottom tab bar for mobile.

### Epic 6: Testing & CI/CD

**Goal:** Automated quality gates on every push.

- **Backend Tests (pytest + httpx):**
  - Unit tests for AgentService state machine
  - Unit tests for ticker validation, portfolio calculations
  - Integration tests for each API route (with mocked Supabase)
  - WebSocket connection tests
- **Frontend Tests (Vitest + React Testing Library):**
  - Component rendering tests for each page
  - Auth flow tests (login, demo mode, protected routes)
  - Theme toggle tests
- **GitHub Actions Pipeline:**
  - On PR: lint (ruff + eslint), type check, run tests, build check
  - On merge to main: deploy to Render (backend) + Vercel (frontend)
  - Scheduled: dependency audit (`npm audit`, `pip-audit`)
- **Pre-commit Hooks:** ruff, black, eslint, prettier

### Epic 7: Feature Expansion

| Feature | Description | Priority |
|---------|-------------|----------|
| **Paper Trading Simulator** | Full order book simulation with realistic slippage, brokerage fees, and market hours enforcement | High |
| **Portfolio Performance Tracker** | Historical equity curve, XIRR calculations, benchmark comparison (vs Nifty 50) | High |
| **Real-time News Feed** | WebSocket-powered news stream with AI-generated sentiment scores per stock | Medium |
| **Alerts & Notifications** | Price alerts, agent action notifications via email/push | Medium |
| **Broker Integration** | Connect to Zerodha Kite / Angel One for live trading (with explicit user consent) | Low (V5) |
| **Social Features** | Public portfolio leaderboards, strategy sharing | Low (V5) |

---

## 4. Step-by-Step Execution Plan

### Phase 1: Foundation (Week 1-2) — "Make It Safe"

**Do not add any features. Fix what's broken.**

1. **Pin all dependencies** in `requirements.txt` and `package.json` with exact versions.
2. **Create JWT auth middleware** (`middleware/auth.py`):
   - FastAPI dependency that decodes Supabase JWT
   - Apply to all routes except `/health`, `/auth/*`
   - Extract `user_id` from token — remove `user_id` from request bodies
3. **Lock down CORS** to explicit origins only.
4. **Add WebSocket authentication** — verify token on connect.
5. **Fix frontend WebSocket leaks**: Track `setTimeout` IDs and clear on unmount.
6. **Fix TradingChart ResizeObserver leak**.
7. **Add React Error Boundaries** at the route level.
8. **Commit & deploy.** Verify nothing breaks on Vercel + Render.

### Phase 2: Decomposition (Week 3-4) — "Make It Clean"

1. **Extract FastAPI routers** from `main.py` into `routers/` modules.
2. **Extract AgentService** into `services/agent_service.py`.
3. **Extract Pydantic models** into `models/schemas.py`.
4. **Create shared `useNeuralFeed()` hook** — single WebSocket connection shared via React context.
5. **Create shared `usePortfolio()` hook** — deduplicate portfolio fetching.
6. **Standardize error responses** across all backend routes.
7. **Apply ticker validation** to all endpoints that accept symbols.
8. **Write first batch of tests**: auth middleware, ticker validation, agent lifecycle.
9. **Set up GitHub Actions** with lint + test + build checks.

### Phase 3: Persistence (Week 5-6) — "Make It Reliable"

1. **Create `agent_runs` table** in Supabase with proper RLS.
2. **Persist portfolio state** to database on every trade.
3. **Add startup recovery** — check for interrupted agent runs.
4. **Add database migration system** (Alembic or Supabase CLI migrations).
5. **Cache market data** — add Redis or in-memory TTL cache for yfinance calls to prevent N+1 slowness.
6. **Add health check improvements** — include DB connectivity, agent status.

### Phase 4: Multi-Agent Evolution (Week 7-10) — "Make It Smart"

1. **Design agent communication protocol** using LangGraph state graphs.
2. **Implement Technical Analysis Agent** — RSI, MACD, SuperTrend indicators.
3. **Implement Market Sentiment Agent** — news aggregation + Gemini sentiment scoring.
4. **Implement Risk Management Agent** — position sizing, drawdown limits.
5. **Update Supervisor Agent** to orchestrate the new specialist agents.
6. **Stream per-agent reasoning** to the frontend with agent-typed WebSocket messages.

### Phase 5: Pro UI (Week 11-13) — "Make It Beautiful"

1. **Multi-timeframe charts** with indicator overlays.
2. **Portfolio analytics dashboard** — equity curve, sector allocation, risk metrics.
3. **Real-time watchlist** with live price WebSocket.
4. **Mobile responsive layout** — bottom tab bar, hamburger sidebar.
5. **Paper trading simulator** with realistic order execution.

### Phase 6: Production Hardening (Week 14-15) — "Make It Ship"

1. **Load testing** — verify backend handles 100+ concurrent WebSocket connections.
2. **Monitoring** — add Sentry for error tracking, Grafana for metrics.
3. **Staging environment** — deploy a staging branch to a separate Render instance.
4. **Security audit** — run OWASP ZAP against the API.
5. **Documentation** — API docs (FastAPI auto-generates these), deployment guide, architecture diagram.
6. **Beta launch** with a limited user group.

---

## Appendix: File Inventory

### Backend (Python)
| File | Lines | Role |
|------|-------|------|
| `backend/main.py` | 1,051 | Monolithic API — needs decomposition |
| `services/auth_manager.py` | 179 | Supabase auth helpers — unused by API |
| `services/news_loader.py` | 196 | News/market data fetcher |
| `supabase_setup.sql` | 101 | DB schema + RLS policies |

### Frontend (React)
| File | Lines | Role |
|------|-------|------|
| `src/main.jsx` | 56 | App entry + routing + ProtectedRoute |
| `src/AuthContext.jsx` | ~60 | Auth state + demo mode bypass |
| `src/ThemeContext.jsx` | 32 | Light/dark theme toggle |
| `src/Layout.jsx` | ~40 | Sidebar + Outlet wrapper |
| `src/Sidebar.jsx` | 99 | Navigation + theme toggle |
| `src/Dashboard.jsx` | 259 | Portfolio + multi-ticker grid |
| `src/Market.jsx` | 162 | Index cards + top movers table |
| `src/Discover.jsx` | 140 | Stock discovery grid |
| `src/Analyze.jsx` | 128 | AI analysis report renderer |
| `src/Portfolio.jsx` | 172 | Holdings table + metrics |
| `src/TradeExecutor.jsx` | 242 | Order form + execution |
| `src/GodMode.jsx` | 260 | Live agent terminal feed |
| `src/AutonomousControl.jsx` | 304 | Agent control panel |
| `src/Settings.jsx` | 170 | Trading constraints config |
| `src/Auth.jsx` | 174 | Login/signup + demo access |
| `src/components/TradingChart.jsx` | 161 | Candlestick chart (lightweight-charts) |
| `src/components/CopilotSidebar.jsx` | 227 | AI chat drawer |
| `src/components/CommandPalette.jsx` | ~120 | Cmd+K fuzzy search |
| `src/components/ReasoningEngine.jsx` | ~80 | Agent reasoning sidebar |

---

*This document is a living artifact. Update it as items are completed or priorities shift.*
