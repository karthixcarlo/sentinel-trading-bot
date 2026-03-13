# Sentinel Next-Gen Roadmap — Deep Implementation Guide

> **Generated**: March 13, 2026
> **Audit Scope**: 3,788 lines backend Python + 3,094 lines frontend React + 67 lines SQL + 174 lines tests
> **Total Files Audited**: 28 source files across backend, agents, services, and frontend
> **Relationship to V4 Roadmap**: `SENTINEL_V4_ROADMAP.md` provides high-level epics and timelines. This document drills into exact file paths, line numbers, and implementation prescriptions.

---

## Phase 1: Codebase Cleanup & Security

### 1.1 Backend Monolith Decomposition

`backend/main.py` is **1,031 lines** containing 26 endpoints, 6 Pydantic models, a WebSocket manager, demo DB helpers, and inline SQLite operations. It must be split into focused modules.

**Proposed Router Extraction**:

| New File | Lines from main.py | Endpoints |
|----------|-------------------|-----------|
| `routers/auth.py` | 65-120 | `get_current_user` dependency, `/api/auth/login` |
| `routers/market.py` | 223-414, 724-749 | `/api/market/ohlcv`, `/discover`, `/analyze`, `/indices` |
| `routers/portfolio.py` | 123-137, 755-835 | `/api/portfolio/{user_id}`, `/detail` |
| `routers/trade.py` | 141-144, 905-1031 | `/api/trade/manual`, `/api/trade/execute` |
| `routers/agent.py` | 479-567 | `/api/agent/start`, `/stop`, `/status`, `/thoughts`, `/trades`, `/autonomous/status`, `/agent/portfolio` |
| `routers/settings.py` | 572-636 | `/api/settings/{user_id}` GET/PUT |
| `routers/watchlist.py` | 643-715 | `/api/watchlist` GET/POST/DELETE |
| `routers/chat.py` | 148-212 | `/api/chat/copilot` |
| `ws/neural_feed.py` | 419-474 | `/ws/neural-feed` WebSocket manager + broadcast |

**Model Extraction** — Move to `models/schemas.py`:
- `LoginRequest` (line 97), `TradeRequest` (line 101), `ChatRequest` (line 148)
- `UserSettings` (line 572), `WatchlistAddRequest` (line 655), `TradeExecuteRequest` (line 905)

**Additional Decomposition**:
- **Consolidate 6 separate `sqlite3` imports** (lines 179, 640, 642, 840, aliased as `_sqlite3` and `_wl_sqlite`) into a single `services/local_db.py` module
- **Move demo DB helpers** (`_demo_ensure_tables`, `_demo_get_cash`, `_demo_get_positions`, `_demo_log_tx`, `_demo_update_cash`, lines 844-902) to `services/demo_db.py`
- **Move hardcoded constants** (`DEMO_DISCOVER` list at lines 307-320) to `config/constants.py`

**Target**: `backend/main.py` reduced to ~80 lines (app init, CORS config, router includes)

---

### 1.2 Security Hardening

**1.2.1 JWT Enforcement Gap**

Only **4 of 26 endpoints** use `Depends(get_current_user)`: lines 124, 659, 680, 702 (portfolio GET, watchlist CRUD). All mutating endpoints are unprotected:

| Endpoint | Line | Auth Status | Risk |
|----------|------|-------------|------|
| `POST /api/trade/manual` | 142 | **NONE** | Anyone can execute trades |
| `POST /api/trade/execute` | 914 | **NONE** | Anyone can execute trades |
| `POST /api/chat/copilot` | 153 | **NONE** | Free Gemini API abuse |
| `POST /api/agent/start` | 480 | **NONE** | Anyone can start agent |
| `POST /api/agent/stop` | 492 | **NONE** | Anyone can stop agent |
| `PUT /api/settings/{user_id}` | 629 | **NONE** | Anyone can modify settings |
| `GET /api/market/analyze/{ticker}` | 366 | **NONE** | Free Gemini API abuse |

**Fix**: Add `current_user: str = Depends(get_current_user)` to all mutating endpoints.

**1.2.2 Trade Endpoint Trusts Client-Supplied user_id**

`TradeExecuteRequest` (line 905) includes a `user_id: str` field. The handler at line 914 uses `req.user_id` directly, never verifying it matches the JWT identity. An attacker can trade on behalf of any user.

**Fix**: Remove `user_id` from the request model; derive it from `current_user` via JWT.

**1.2.3 CORS Wildcard + Credentials Violation**

Line 29: When `ALLOWED_ORIGINS` env var is empty, `_CORS_ORIGINS` defaults to `["*"]`.
Line 43: `allow_credentials=True` is set unconditionally.
Per the CORS spec, `credentials: true` + `origin: *` is invalid and browsers will reject it.

**Fix**: Remove wildcard fallback; require explicit origins in production. Default to `["http://localhost:5173"]` for development.

**1.2.4 WebSocket Zero Authentication**

Lines 433-474: `websocket_neural_feed` accepts any connection without token verification. Anyone with the URL can subscribe to real-time agent data.

**Fix**: Require a `token` query parameter, validate with `get_current_user()` before accepting the connection.

**1.2.5 Copilot Leaks Exception Details**

Lines 210-212: The except block returns `detail=str(e)` to the client, exposing internal error messages, stack traces, and potentially API keys.

**Fix**: Return generic `"An internal error occurred"` to the client; log the full exception server-side.

**1.2.6 Missing Ticker Validation on Trade**

`execute_trade` at line 917 does `req.symbol.upper()` but never calls `_validate_ticker()` (defined at line 223). The `/ohlcv` and `/analyze` endpoints validate, but the trade endpoint does not.

**Fix**: Call `_validate_ticker(req.symbol)` before proceeding with trade execution.

---

### 1.3 Race Conditions in `broker_engine.py`

**Non-Atomic Transaction Flow** (lines 177-190 BUY, lines 230-240 SELL):

```
Step 1: INSERT into transactions  → may succeed
Step 2: UPDATE portfolios cash    → may fail
```

If Step 2 fails, the transaction is recorded but cash is not debited. Portfolio accounting diverges from transaction history.

**Additional Race**: `_get_cash_balance()` (lines 42-56) has no locking. Two concurrent threads can read the same cash balance, both execute BUY, and overdraw the account.

**Fix Options** (choose one):
1. **Supabase RPC function**: Wrap INSERT + UPDATE in a server-side PostgreSQL function with `BEGIN/COMMIT`
2. **Optimistic locking**: Add a `version` column to `portfolios`; UPDATE with `WHERE version = ?`; retry on conflict
3. **Application-level lock**: Add `threading.Lock()` around the entire buy/sell flow (simplest for paper trading)

---

### 1.4 Database Schema Gaps

`supabase_setup.sql` (67 lines) only defines the `watchlists` table and a `handle_new_user` trigger. **6 tables** are used throughout the codebase but have no DDL:

| Table | Used In | Missing DDL |
|-------|---------|-------------|
| `portfolios` | `auth_manager.py:118,142,177`, `broker_engine.py:48,188,238` | PK `user_id`, `cash_balance` REAL |
| `transactions` | `auth_manager.py:148,198`, `broker_engine.py:68,178,230` | FK `user_id`, `ticker`, `qty`, `price`, `side`, `timestamp` |
| `agent_logs` | `backend/main.py:166`, `broker_engine.py:91` | `agent_name`, `message`, `action_type`, `timestamp` |
| `agent_thoughts` | `agent_service.py:247-249,473-479` | `agent_name`, `message`, `iteration`, `workflow_id` |
| `trade_history` | `agent_service.py:492-504` | `ticker`, `side`, `qty`, `price`, `status`, `timestamp` |
| `agent_settings` | `backend/main.py:588-593` | PK `user_id`, `risk_appetite`, `max_position_size`, `allowed_sectors` |

**Missing Indices**:
```sql
CREATE INDEX portfolios_user_id_idx ON portfolios(user_id);
CREATE INDEX transactions_user_ticker_idx ON transactions(user_id, ticker);
CREATE INDEX agent_thoughts_workflow_idx ON agent_thoughts(workflow_id);
CREATE INDEX agent_logs_timestamp_idx ON agent_logs(timestamp);
```

**Missing Constraints**:
```sql
ALTER TABLE portfolios ADD CHECK (cash_balance >= 0);
ALTER TABLE transactions ADD CHECK (qty > 0);
```

---

### 1.5 Missing Timeouts

| Location | File:Line | Risk |
|----------|-----------|------|
| `yf.Ticker().history()` | `main.py:241,331,374,737,797,925` | Network hang freezes endpoint |
| `graph.invoke(state)` | `agent_service.py:322` | LangGraph run forever |
| `llm.invoke()` (Gemini) | `main.py:204` | API hang freezes copilot |
| `yfinance.download()` | `scout_agent.py:49-57` | Blocks entire agent cycle |

**Fix**: Wrap all external calls with timeouts:
- yfinance: `yf.Ticker(t).history(period="6mo", timeout=15)`
- LangGraph: `await asyncio.wait_for(asyncio.to_thread(graph.invoke, state), timeout=120)`
- Gemini: Pass `timeout=30` to LangChain LLM constructor

---

### 1.6 Testing Expansion

**Current State**: 174 lines across 3 test files:
- `test_agent_service.py` (86 lines) — Config and portfolio tests
- `test_broker_engine.py` (41 lines) — Input validation only
- `test_sentinel_state.py` (45 lines) — State initialization

**Target**: 500+ lines across 8+ files:

| Test File | Coverage Target |
|-----------|----------------|
| `test_api_routes.py` | All 26 endpoints via `httpx.AsyncClient` |
| `test_auth_middleware.py` | Valid JWT, expired JWT, missing token, demo mode |
| `test_trade_execution.py` | BUY/SELL flows, insufficient cash, invalid ticker |
| `test_websocket.py` | Connection lifecycle, message format, auth |
| `test_broker_engine.py` | Atomic transactions, race condition simulation |
| `test_agent_pipeline.py` | LangGraph routing, state transitions |
| `test_ticker_validation.py` | Edge cases (M&M, special characters, XSS) |
| `test_portfolio_calc.py` | Position aggregation, P&L calculations |

---

## Phase 2: UI/UX Polish

### 2.1 Error Boundaries

**Current State**: Zero React Error Boundary components. Any component crash = white screen.

**Fix**: Create `frontend/src/components/ErrorBoundary.jsx`:
- Class component with `componentDidCatch` and `getDerivedStateFromError`
- Fallback UI: "Something went wrong" + retry button + link to report
- Wrap `<Layout />` in `main.jsx` (line 42) with the ErrorBoundary
- Add per-page boundaries for isolated failure containment (GodMode, AutonomousControl, TradingChart)

---

### 2.2 WebSocket Deduplication

Three components independently connect to `/ws/neural-feed`:

| Component | Lines | Reconnection | Cleanup |
|-----------|-------|-------------|---------|
| `AutonomousControl.jsx` | 74-91 | `setTimeout(connect, 3000)` | Timeout ID NOT tracked — leak |
| `GodMode.jsx` | 44-80 | None (logs disconnect) | Clean |
| `ReasoningEngine.jsx` | 14-35 | `setTimeout(connect, 3000)` | Timeout ID NOT tracked — leak |

**Fix**: Create `frontend/src/hooks/useNeuralFeed.js`:
- Shared `NeuralFeedProvider` wrapping `<Layout />` with single WebSocket connection
- Custom `useNeuralFeed()` hook returns `{ messages, isConnected }`
- Exponential backoff (3s → 6s → 12s → max 30s) with max 10 retry attempts
- Track timeout ID with `useRef` and clear on unmount

All three components consume the hook instead of managing connections.

---

### 2.3 God Component Decomposition

**AutonomousControl.jsx (304 lines)** — Extract:
- `AgentStatusCard` (lines 137-172) — agent state display
- `MarketStatusCard` (lines 174-183) — NSE market hours check
- `PortfolioSummaryCard` (lines 186-216) — cash + positions display
- `RecentTradesCard` (lines 219-240) — trade history list
- `NeuralFeedPanel` (lines 247-265) — WebSocket message log

**GodMode.jsx (253 lines)** — Extract:
- `TerminalWindow` (lines 144-176) — scrollable log with auto-scroll
- `SafetyPanel` (lines 181-191) — risk gate indicators
- `ClusterHealthPanel` (lines 193-213) — agent node status grid
- Share `AgentBadge` component (duplicated with AutonomousControl)

**Dashboard.jsx (259 lines)** — Extract:
- `MetricsGrid` (lines 119-140) — portfolio value cards
- `SectorMonitor` (lines 143-201) — pinned ticker charts
- `HoldingsTable` (lines 204-253) — positions list

**TradeExecutor.jsx (242 lines)** — Extract:
- `OrderSummary` (lines 194-222) — price/brokerage/total calculation display
- `PortfolioSnapshot` (lines 101-114) — current cash/positions sidebar
- `useTradeCalculations` hook — debounced price fetch + order computation

---

### 2.4 API Client Abstraction

`frontend/src/api.js` (7 lines) only exports `BASE_URL` and `WS_BASE`. Every component uses raw `fetch()`.

**Fix**: Expand `api.js` into a proper client:
```
api.get(endpoint)    — GET with auth header
api.post(endpoint, body) — POST with auth header + JSON
api.put(endpoint, body)  — PUT with auth header + JSON
api.delete(endpoint)     — DELETE with auth header
```

- Attach `Authorization: Bearer <token>` from `AuthContext.session?.access_token`
- Centralized error handling: 401 → redirect to `/auth`, 5xx → show toast notification
- Eliminates hardcoded `"demo_user"` from **10 locations**:
  - `Dashboard.jsx` (lines 27, 190)
  - `Discover.jsx` (line 80)
  - `Portfolio.jsx` (line 34)
  - `Settings.jsx` (lines 19, 45)
  - `TradeExecutor.jsx` (lines 21, 57)
  - `CopilotSidebar.jsx` (line 60)

---

### 2.5 Remove Unused Dependencies

`package.json` includes two dependencies with zero imports across the entire frontend:

| Package | Version | Bundle Size | Status |
|---------|---------|-------------|--------|
| `zustand` | ^4.4.7 | ~7KB | Zero imports found |
| `recharts` | ^2.10.3 | ~100KB | Zero imports found (using lightweight-charts instead) |

**Fix**: `npm uninstall zustand recharts` — saves ~107KB from bundle.

---

### 2.6 Memoization Gaps

**Missing `React.memo()`** for pure presentational components:
- `MetricCard` in Portfolio.jsx — rendered 4+ times per mount
- `IndexCard` in Market.jsx — rendered per market index
- `AgentBadge` in GodMode.jsx / AutonomousControl.jsx — rendered per agent

**Missing `useCallback()`** for event handlers passed as props:
- `addTicker`, `removeTicker` in Dashboard.jsx — recreated every render
- `toggleAgent` in AutonomousControl.jsx (line 93) — recreated every render
- `handleSubmit` in TradeExecutor.jsx (line 50) — recreated every render

**Missing `useMemo()`** for derived data:
- `filteredData` in Discover.jsx (lines 29-36) — recalculated every render
- Sorted stock lists in Market.jsx — re-sorted on every tab change
- Holdings aggregation in Portfolio.jsx — recomputed on every render

---

### 2.7 TradingChart Optimization

**Problem 1: Full chart re-creation on theme toggle**

`TradingChart.jsx` line 129: `isDark` is in the `useEffect` dependency array. When the user toggles theme, the entire chart (DOM element, series, data fetch) is destroyed and re-created.

**Fix**: Separate chart creation from theme application. On theme change, call `chart.applyOptions({ layout: { background, textColor }, grid: { ... } })` to update colors without rebuilding.

**Problem 2: ResizeObserver memory leak**

The `ResizeObserver` is created inside the async `fetchChartData()` function (line 112). The cleanup `return () => ro.disconnect()` is a return from the async function, NOT from the `useEffect` cleanup. The `useEffect` cleanup at lines 123-128 only removes the chart, not the observer.

**Fix**: Create the ResizeObserver outside the async function, in the main `useEffect` body, so the cleanup function can properly call `ro.disconnect()`.

---

### 2.8 Hardcoded Hex Colors

Multiple components still use inline hex colors instead of Tailwind theme tokens:

- `TradingChart.jsx`: `'#00D09C'`, `'#EB5B3C'` in chart config (lines 37-40)
- `Market.jsx`: `text-[#00D09C]`, `bg-[#00D09C]/10` (line 20)
- `GodMode.jsx`: Agent color mapping with hardcoded hex values
- `AutonomousControl.jsx`: Status indicator colors

The Tailwind config (`tailwind.config.js` lines 19-23) already defines `accent-green`, `accent-red`, `accent-blue`, `accent-amber`, `accent-purple`. These should be used consistently.

**Note**: For JavaScript chart libraries (lightweight-charts), CSS variables can be read via `getComputedStyle()` to maintain theme consistency.

---

### 2.9 Lazy Loading

`main.jsx` eagerly imports all 9 page components (lines 8-17). Heavy pages should use `React.lazy()` + `Suspense`:

| Page | Lines | Load Priority |
|------|-------|--------------|
| `GodMode` | 253 | Lazy — advanced users only |
| `AutonomousControl` | 304 | Lazy — heavy WebSocket + polling |
| `Discover` | 140 | Lazy — includes TradingChart |
| `Analyze` | 128 | Lazy — triggers Gemini API call |
| `Dashboard` | 259 | **Eager** — landing page |
| `Portfolio` | 172 | **Eager** — core feature |
| `Market` | 162 | **Eager** — core feature |

---

### 2.10 Financial Data Formatting

Inconsistent number formatting across components:

| Component | Line | Format Used |
|-----------|------|-------------|
| `Dashboard.jsx` | 123 | `toLocaleString()` — no locale |
| `Portfolio.jsx` | 85 | `toLocaleString('en-IN')` — locale, no decimals |
| `TradeExecutor.jsx` | 104 | `toLocaleString('en-IN', { maximumFractionDigits: 0 })` |
| `AutonomousControl.jsx` | 194 | `toLocaleString('en-IN')` — no decimal control |

**Fix**: Create `frontend/src/utils/format.js`:
```javascript
export const formatINR = (value, decimals = 2) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value);

export const formatPercent = (value) => `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
export const formatVolume = (value) => value >= 1e7 ? `${(value/1e7).toFixed(1)}Cr` : value >= 1e5 ? `${(value/1e5).toFixed(1)}L` : value.toLocaleString('en-IN');
```

---

## Phase 3: AI & Feature Expansion

### 3.1 Multi-Agent Specialization

Current agent architecture (1,223 lines across 5 agents in `agents/`):

```
Supervisor (240 lines) → Scout (344) → Analyst (226) → Risk (205) → Trader (208)
```

The Analyst agent handles both technical analysis AND Gemini AI signal generation. The Scout only uses momentum. No dedicated sentiment or fundamentals analysis.

**New Agents to Add**:

| Agent | File | Purpose | Data Source |
|-------|------|---------|-------------|
| Sentiment Agent | `agents/sentiment_agent.py` | NLP-based news/social sentiment scoring | `services/news_loader.py` output → Gemini |
| Fundamentals Agent | `agents/fundamentals_agent.py` | P/E, market cap, sector analysis | `yf.Ticker().info` data |

**Implementation**:
- Add `sentiment_data` and `fundamental_data` fields to `SentinelState` in `sentinel_state.py`
- Add new nodes to `sentinel_hive.py` graph with conditional routing from Supervisor
- Update Supervisor prompt in `agents/supervisor.py` (line 29) to include new routing targets
- The existing Analyst agent focuses solely on technical indicators (RSI, MACD, SMA)
- New Sentiment agent replaces keyword matching in `news_loader.py` (lines 198-224) with Gemini NLP
- New Fundamentals agent uses data already fetched in `main.py` lines 380-393 but never passed to the pipeline

**Evolved Pipeline**:
```
Supervisor → Scout → [Sentiment, Fundamentals, Analyst (parallel)] → Risk → Trader
```

---

### 3.2 Market Data Caching

Zero caching exists. Every API call triggers a fresh yfinance download. On a busy day, the same ticker's data is fetched 5-10 times.

**Fix**: In-memory TTL cache using `cachetools`:

| Cache Key | TTL | Applies To |
|-----------|-----|-----------|
| `(ticker, "1d")` | 60 seconds | Intraday OHLCV, current price |
| `(ticker, "6mo")` | 300 seconds | Historical charts, technical indicators |
| `(ticker, "info")` | 600 seconds | Company fundamentals |

Apply to: `main.py` lines 241, 331, 374, 737, 797, 925 and `scout_agent.py` batch downloads.

---

### 3.3 Fix `calculate_daily_pnl()`

`agents/risk_manager.py` lines 36-54: The function iterates `portfolio.get('orders', [])` looking for a `'pnl'` key. But the order dicts from both `auth_manager._aggregate_positions()` and `_demo_get_positions()` never include a `'pnl'` field. The function **always returns 0.0**, making the daily loss limit check at line 132 permanently disabled.

**Fix**:
1. Calculate P&L from transactions: `SUM(sell_price * qty) - SUM(buy_price * qty)` for today's trades
2. Or: Track realized P&L per trade in the `transactions` table with a `pnl` column
3. Update `calculate_daily_pnl()` to query actual transaction data filtered by today's date

---

### 3.4 Position Correlation Checks

`risk_manager.py` approves any trade passing confidence + cash checks. No portfolio concentration analysis.

**Fix**: Before approving, check:
1. **Sector exposure**: If adding INFY (IT) and portfolio already has 40%+ in IT sector, reject
2. **Position count**: Maximum 10 open positions (configurable via settings)
3. **Single-stock exposure**: No single position > 20% of portfolio value

Add `SECTOR_MAP` lookup (already exists in `scout_agent.py` as `SECTOR_STOCKS`) and calculate sector weights from current positions.

---

### 3.5 State Persistence

`agent_service.py` line 154: `self.current_thoughts` is an in-memory list.
Line 157: `self.performance_stats` is an empty dict that is **never populated**.
On server restart (Render free tier spins down after 15 min inactivity), all agent state is lost.

**Fix**:
1. **Persist agent runs**: Create `agent_runs` table in Supabase with `status`, `started_at`, `stopped_at`, `cycles_completed`
2. **Startup recovery**: On FastAPI startup, check for `status=RUNNING` rows → mark as `CRASHED`
3. **Populate performance_stats**: Aggregate from `trade_history` table (win rate, total P&L, Sharpe ratio)
4. **Portfolio persistence**: Call `_save_portfolio()` after every trade execution (currently only called in tests)

---

### 3.6 Backtesting Framework

No backtesting capability exists. Traders cannot evaluate strategy performance on historical data.

**Design**:

**Backend** — `backtesting/engine.py`:
- Accept parameters: `ticker`, `date_range`, `initial_cash`, `risk_settings`
- Replay historical OHLCV data through `create_sentinel_graph()` pipeline
- Mock `broker_engine.execute_order()` with historical prices
- Calculate: Sharpe ratio, max drawdown, win rate, CAGR, total trades

**API** — New endpoint `POST /api/backtest`:
- Request: `{ ticker, start_date, end_date, initial_cash, risk_appetite }`
- Response: `{ trades: [...], metrics: { sharpe, drawdown, win_rate, cagr } }`

**Frontend** — New `Backtest.jsx` page:
- Date range picker + ticker selector + settings
- Results visualization: equity curve chart, trade markers, metrics cards
- Add to Sidebar navigation and router in `main.jsx`

---

### 3.7 Notifications System

No notification mechanism exists. Users have no way to know when the agent executes a trade unless they're watching the Neural Feed.

**Design**:

**Database**: New `notifications` table:
```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users,
  type TEXT NOT NULL,  -- 'trade_executed', 'agent_paused', 'risk_rejected'
  title TEXT NOT NULL,
  body TEXT,
  read BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**Backend**: New endpoints:
- `GET /api/notifications` — List unread notifications
- `PUT /api/notifications/{id}/read` — Mark as read
- Extend WebSocket `/ws/neural-feed` to send notification-type messages

**Frontend**:
- Toast notification component (bottom-right, auto-dismiss after 5s)
- Notification bell icon in Sidebar with unread count badge
- Notification drawer/panel for history

---

### 3.8 SQLite Connection Pooling

Throughout `backend/main.py`, SQLite connections are created fresh per function call (lines 599, 615, 644, 671, 693, 715, 857, 870, 889, 899). Each call to `sqlite3.connect()` opens a new file handle.

**Fix**:
1. Enable WAL (Write-Ahead Logging) mode for concurrent reads: `conn.execute("PRAGMA journal_mode=WAL")`
2. Use a connection pool or singleton pattern for the demo SQLite database
3. Add `timeout=5` to all `sqlite3.connect()` calls to prevent indefinite blocking

---

## Appendix A: File Inventory

### Backend (3,788 lines)

| File | Lines | Role |
|------|-------|------|
| `backend/main.py` | 1,031 | FastAPI REST API (26 endpoints) |
| `agent_service.py` | 520 | Autonomous trading orchestrator |
| `agents/scout_agent.py` | 344 | Market scanning (rolling batch) |
| `broker_engine.py` | 264 | Paper trade accounting |
| `services/news_loader.py` | 254 | News scraping (Google Finance) |
| `services/auth_manager.py` | 250 | Supabase auth + DB operations |
| `agents/supervisor.py` | 240 | LangGraph routing (Gemini) |
| `agents/analyst_agent.py` | 226 | Technical analysis + AI signals |
| `agents/trader_agent.py` | 208 | Trade execution via broker engine |
| `agents/risk_manager.py` | 205 | Rule-based risk gates |
| `sentinel_hive.py` | 170 | LangGraph StateGraph definition |
| `sentinel_state.py` | 74 | SentinelState TypedDict |

### Frontend (3,094 lines)

| File | Lines | Role |
|------|-------|------|
| `AutonomousControl.jsx` | 304 | Agent control panel + neural feed |
| `Dashboard.jsx` | 259 | Portfolio overview + pinned tickers |
| `GodMode.jsx` | 253 | Multi-agent terminal monitor |
| `TradeExecutor.jsx` | 242 | Manual trade form + execution |
| `CopilotSidebar.jsx` | 227 | AI chat sidebar |
| `CommandPalette.jsx` | 211 | Keyboard-driven search + navigation |
| `Auth.jsx` | 174 | Login/signup page |
| `Portfolio.jsx` | 172 | Holdings + metrics display |
| `Settings.jsx` | 170 | Agent configuration |
| `TradingChart.jsx` | 168 | lightweight-charts integration |
| `Market.jsx` | 162 | Market overview + top movers |
| `Discover.jsx` | 140 | Stock discovery + search |
| `ReasoningEngine.jsx` | 136 | Agent reasoning sidebar |
| `Analyze.jsx` | 128 | AI stock analysis report |
| `Sidebar.jsx` | 112 | Navigation + theme toggle |
| `AuthContext.jsx` | 78 | Auth state management |
| `Layout.jsx` | 57 | App shell + sidebar layout |
| `main.jsx` | 58 | Router + providers |
| `ThemeContext.jsx` | 33 | Dark/light mode toggle |
| `api.js` | 7 | API base URL config |

### Tests (174 lines)

| File | Lines | Coverage |
|------|-------|---------|
| `test_agent_service.py` | 86 | Config, Portfolio, Status |
| `test_sentinel_state.py` | 45 | State initialization |
| `test_broker_engine.py` | 41 | Input validation only |

---

## Appendix B: Dependency Audit

### Backend (`requirements.txt` — 34 dependencies)
- All versions pinned (good)
- Core: `fastapi==0.133.0`, `uvicorn==0.41.0`, `langchain==0.3.25`, `langgraph==0.4.1`
- AI: `langchain-google-genai`, `google-generativeai`
- Data: `yfinance`, `pandas`, `numpy`
- Auth: `supabase`, `PyJWT`
- Missing: `cachetools` (for TTL caching), `slowapi` (for rate limiting)

### Frontend (`package.json` — 11 dependencies)
- **Active**: react 18, react-router-dom 6, lightweight-charts 5.1, lucide-react 0.300, framer-motion 11, react-markdown 10, @supabase/supabase-js 2.39
- **UNUSED**: zustand 4.4.7 (zero imports), recharts 2.10.3 (zero imports)
- **Recommendation**: Remove unused deps, saving ~107KB from bundle

---

## Appendix C: CI/CD Enhancement Recommendations

### Current Pipelines

| Workflow | File | Jobs |
|----------|------|------|
| Backend CI | `backend-ci.yml` | Ruff lint → Compile check → pytest |
| Frontend CI | `frontend-ci.yml` | ESLint → Vite build |
| Legacy CI | `ci.yml` | Python compile + npm build (redundant) |

### Recommended Additions

1. **Security scanning**: Add `bandit` (Python SAST) and `npm audit` to CI
2. **Type checking**: Add `mypy --strict` for backend Python files
3. **Coverage enforcement**: Add `pytest --cov --cov-fail-under=70`
4. **Dependency audit**: Add `pip-audit` and `npm audit --audit-level=moderate`
5. **Remove legacy `ci.yml`**: Now redundant with `backend-ci.yml` and `frontend-ci.yml`
6. **Add staging deployment**: Auto-deploy to staging on PR merge; manual promotion to production

---

*This roadmap complements `SENTINEL_V4_ROADMAP.md` with implementation-level detail. Execute Phase 1 first — security and cleanup unblock everything else.*
