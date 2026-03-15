# Sentinel V4 — Multi-Agent Trading Engine Architecture

> **Status**: Brainstorm & Development Plan
> **Author**: AI Architect
> **Date**: 2026-03-15
> **Scope**: Multi-agent architecture redesign, data pipelines, memory strategy, phased roadmap

---

## Executive Summary

Sentinel V3 runs a functional LangGraph pipeline: **Supervisor → Scout → Analyst → Risk Manager → Trader**. It scans 2,000+ NSE stocks, generates Gemini-powered BUY signals, validates risk, and executes paper trades to Supabase. It works — but it has fundamental limitations that cap its intelligence ceiling:

1. **No exit logic** — the system can BUY but never SELL. Stop-losses are recommended but never enforced. Positions are held forever.
2. **No quantitative depth** — analysis relies on basic RSI/MACD plus a single Gemini call. No multi-timeframe confluence, no Bollinger Bands, no ATR-based volatility modeling.
3. **No sentiment awareness** — a basic news scraper exists but feeds plain text to Gemini. No structured sentiment scoring, no macro data (RBI rates, FII flows), no social signals.
4. **No trade memory** — agents don't learn from past wins or losses. Every cycle starts fresh with zero historical context.
5. **LLM-dependent routing** — the Supervisor makes a Gemini API call every iteration just to decide which agent runs next. This is slow, expensive, and unpredictable.
6. **Single-threaded** — one workflow at a time, 5-minute cycles. Quant analysis and sentiment gathering could run in parallel but don't.

**V4 Vision**: Transform Sentinel from a basic signal-generator into an enterprise-grade autonomous trading engine with:
- **7 specialized agents** operating across 3 workflow modes (Scan, Monitor, Rebalance)
- **Deterministic FSM routing** replacing LLM-based supervision
- **Parallel agent execution** cutting cycle time by 40%
- **Trade memory with pgvector** enabling pattern recognition from past outcomes
- **Full position lifecycle management** — entry, monitoring, exit, rebalancing

The result: a system that not only finds opportunities but manages risk dynamically, learns from its history, and optimizes its portfolio composition over time.

---

## Agent Topology

### V3 (Current) — Hub-and-Spoke

```
                 ┌────────────┐
                 │ Supervisor │ (Gemini-powered router)
                 └─────┬──────┘
           ┌───────┬───┴───┬────────┐
           ▼       ▼       ▼        ▼
        ┌──────┐┌───────┐┌──────┐┌───────┐
        │Scout ││Analyst││ Risk ││Trader │
        └──────┘└───────┘└──────┘└───────┘
                                     │
                                ┌────▼─────┐
                                │ Supabase │
                                └──────────┘
```

**Problems**: Single workflow mode, sequential execution, no exit path, Gemini in the routing hot-path.

### V4 (Proposed) — Three-Mode FSM with Parallel Execution

```
                        ┌──────────────────────────────┐
                        │       SUPERVISOR V2          │
                        │   Deterministic FSM Router   │
                        │                              │
                        │   Modes: SCAN | MONITOR |    │
                        │          REBALANCE           │
                        └──────────┬───────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
 ┌────────▼────────┐    ┌─────────▼─────────┐   ┌─────────▼─────────┐
 │   SCAN MODE     │    │  MONITOR MODE     │   │  REBALANCE MODE   │
 └────────┬────────┘    └─────────┬─────────┘   └─────────┬─────────┘
          │                       │                       │
 ┌────────▼────────┐     ┌───────▼────────┐     ┌────────▼────────┐
 │     Scout       │     │  Exit Monitor  │     │   Portfolio     │
 │  (Market Scan)  │     │  (Stop/TP/Time)│     │   Optimizer     │
 └────────┬────────┘     └───────┬────────┘     └────────┬────────┘
          │                      │                       │
   ┌──────┴──────┐               │              ┌────────▼────────┐
   │  PARALLEL   │               │              │   Risk V2       │
   │  FAN-OUT    │               │              │  (Rebal Check)  │
   ▼             ▼               │              └────────┬────────┘
┌──────┐  ┌──────────┐           │                       │
│Quant │  │Sentiment │           │                       │
│Agent │  │  Agent   │           │                       │
└──┬───┘  └────┬─────┘           │                       │
   └─────┬─────┘                 │                       │
   ┌─────▼──────┐                │                       │
   │ Analyst V2 │                │                       │
   │  (Merger)  │                │                       │
   └─────┬──────┘                │                       │
   ┌─────▼──────┐                │                       │
   │  Risk V2   │                │                       │
   └─────┬──────┘                │                       │
         │                       │                       │
         └───────────┬───────────┴───────────────────────┘
               ┌─────▼──────┐
               │  Trader V2 │
               │ (BUY+SELL) │
               └─────┬──────┘
                     │
               ┌─────▼──────┐          ┌─────────────────┐
               │   Broker   │          │  Memory Layer   │
               │  Engine V2 │◄────────►│  (pgvector +    │
               └─────┬──────┘          │   feedback)     │
                     │                 └─────────────────┘
               ┌─────▼──────┐
               │  Supabase  │
               └────────────┘
```

### Workflow Execution Patterns

| Mode | Trigger | Agent Sequence | Cycle Time |
|------|---------|----------------|------------|
| **SCAN** | Every 5 minutes | Scout → [Quant ∥ Sentiment] → Analyst V2 → Risk V2 → Trader V2 | ~25s |
| **MONITOR** | Every 1 minute (between scans) | Exit Monitor → Trader V2 (SELL if triggered) | ~5s |
| **REBALANCE** | Daily (9:30 AM IST) or manual | Portfolio Optimizer → Risk V2 → Trader V2 | ~10s |

---

## New Agent Specifications

### 1. Quant Agent (`agents/quant_agent.py`)

**Purpose**: Advanced technical analysis with multi-timeframe confluence scoring.

**Inputs from state**: `current_ticker`, `market_data` (raw OHLCV)

**Outputs to state**: `quant_signals`

**Indicators computed**:

| Indicator | Parameters | Signal Logic |
|-----------|-----------|--------------|
| Bollinger Bands | 20-period, 2σ | Squeeze = low volatility breakout pending; price below lower band = oversold |
| ATR (Average True Range) | 14-period | Volatility measure; used for stop-loss sizing (entry - 2×ATR) |
| Fibonacci Retracement | Recent swing high/low | Price at 0.618 retracement = potential support/resistance |
| VWAP | Intraday | Price above VWAP = bullish intraday bias |
| Volume Profile | 20-day | POC (Point of Control) = highest volume price level; breakout above POC is bullish |
| RSI | 14-period | Carried from V3; <30 oversold, >70 overbought |
| MACD | 12/26/9 | Carried from V3; crossover signals |
| ADX | 14-period | Trend strength; ADX > 25 = trending market (signals more reliable) |

**Multi-timeframe confluence**:
```
Timeframes: [15min, 1h, 1d]

For each timeframe:
  compute all indicators
  classify as BULLISH / BEARISH / NEUTRAL

confluence_count = count(timeframes where direction == BULLISH)
composite_score = weighted_average(
  15min_score * 0.2,
  1h_score * 0.3,
  1d_score * 0.5
)
```

A `confluence_count >= 2` boosts confidence. A score where daily and hourly disagree triggers a WAIT signal.

**Output schema**:
```python
quant_signals = {
    "ticker": "RELIANCE.NS",
    "composite_score": 0.73,        # 0.0 to 1.0
    "confluence_count": 2,           # 0 to 3
    "atr_14": 42.5,                  # Used by Risk V2 for stop sizing
    "bollinger_position": "lower",   # upper / middle / lower / squeeze
    "adx": 31.2,                     # Trend strength
    "vwap_bias": "bullish",          # bullish / bearish
    "fib_nearest_level": 0.618,      # Nearest Fibonacci level
    "timeframe_breakdown": {
        "15m": {"direction": "bullish", "score": 0.65},
        "1h":  {"direction": "bullish", "score": 0.71},
        "1d":  {"direction": "neutral", "score": 0.55}
    }
}
```

**Implementation notes**:
- All indicator computations are pure functions taking a pandas DataFrame → easy to unit test and backtest
- Use `numpy` and `pandas` only (no `ta-lib` — avoids C compilation on Render/Railway)
- Reuse `services/data_cache.py` to avoid redundant yfinance downloads

---

### 2. Sentiment Agent (`agents/sentiment_agent.py`)

**Purpose**: Aggregate market sentiment from news, social media, and macroeconomic data.

**Inputs from state**: `current_ticker`

**Outputs to state**: `sentiment_data`

**Data sources (by phase)**:

| Source | Phase | Method | Rate Limit Strategy |
|--------|-------|--------|-------------------|
| RSS feeds (MoneyControl, ET, LiveMint) | Phase 2 | `feedparser` library | Respect feed TTL, cache 30min |
| Google News scraping | Phase 2 | Upgrade existing `news_loader.py` | Rotating User-Agent, 10 req/min max |
| RBI policy announcements | Phase 2 | Scrape rbi.org.in press releases | Daily check only |
| FII/DII daily flows | Phase 2 | Scrape NSE website | Once per morning |
| INR/USD rate | Phase 2 | `yfinance USDINR=X` | Via data_cache |
| Twitter/X cashtags | Phase 3 | `snscrape` or API v2 free tier | 100 tweets/15min window |

**Sentiment scoring pipeline**:
```
For each headline/tweet:
  → Gemini Flash with focused prompt:
    "Rate this headline's impact on {ticker} from -1.0 (very bearish) to +1.0 (very bullish).
     Return only a JSON: {score: float, reasoning: string}"
  → Parse score

Aggregate:
  news_score    = mean(headline_scores)     weight: 0.50
  social_score  = mean(tweet_scores)        weight: 0.30 (0.0 if unavailable)
  macro_score   = composite(rbi + fii + fx) weight: 0.20

  composite_sentiment = weighted_sum
```

**Macro scoring rules**:
- RBI rate cut → +0.3 (bullish for equities)
- RBI rate hike → -0.3
- FII net buyers > ₹1000Cr → +0.2
- FII net sellers > ₹1000Cr → -0.2
- INR weakening > 0.5% in a day → -0.1 (import-heavy sectors hit harder)

**Fallback**: When Gemini is unavailable, use keyword-based scoring (existing `get_sentiment_indicator` in `services/news_loader.py`) — matches positive/negative word lists against headlines.

**Output schema**:
```python
sentiment_data = {
    "ticker": "TCS.NS",
    "news_score": 0.35,
    "social_score": 0.0,        # 0.0 until Twitter integration
    "macro_score": 0.15,
    "composite_sentiment": 0.22,
    "headlines": [
        "TCS wins $500M deal from UK bank",
        "IT sector sees strong Q4 guidance"
    ],
    "macro_summary": "FII net buyers ₹2,100Cr, RBI holds rates steady",
    "data_freshness_minutes": 12
}
```

---

### 3. Exit Monitor Agent (`agents/exit_monitor.py`)

**Purpose**: Check all open positions against exit conditions. This is the critical missing piece in V3 — without it, positions are held indefinitely.

**Inputs from state**: `portfolio_snapshot` (all open positions with entry metadata)

**Outputs to state**: `exit_signals` list

**Exit conditions (checked in priority order)**:

| # | Exit Type | Condition | Priority |
|---|-----------|-----------|----------|
| 1 | Stop-loss | `current_price <= position.stop_loss` | IMMEDIATE |
| 2 | Take-profit | `current_price >= position.take_profit` | IMMEDIATE |
| 3 | Trailing stop | Price moved favorably → adjust stop upward by ATR increments | UPDATE |
| 4 | Time-based | Position held > 10 trading days without hitting TP | EVALUATE |
| 5 | Momentum exit | RSI > 80 (overbought) for long positions | EVALUATE |
| 6 | Drawdown exit | Position PnL < -5% from peak unrealized gain | EVALUATE |

**Trailing stop logic**:
```
If position is in profit:
  new_stop = max(current_stop, current_price - 2 * ATR_14)
  if new_stop > current_stop:
    update stop_loss in database
    broadcast("Exit Monitor", f"Trailing stop for {ticker} raised to ₹{new_stop}")
```

**Output schema**:
```python
exit_signals = [
    {
        "ticker": "INFY.NS",
        "exit_type": "stop_loss",
        "current_price": 1420.50,
        "trigger_price": 1425.00,  # the stop-loss price
        "position_id": "uuid-...",
        "urgency": "immediate"
    },
    {
        "ticker": "HDFC.NS",
        "exit_type": "time_based",
        "days_held": 12,
        "current_pnl_pct": 1.2,
        "urgency": "evaluate"  # Supervisor may override
    }
]
```

**Execution flow in MONITOR mode**:
1. Fetch live prices for all open positions (batch yfinance call)
2. Check each position against all exit conditions
3. Append triggered exits to `exit_signals`
4. Supervisor routes to Trader V2 for SELL execution on `immediate` signals
5. `evaluate` signals are logged and optionally held for human review

---

### 4. Portfolio Optimizer Agent (`agents/portfolio_optimizer.py`) — Phase 3

**Purpose**: Periodic portfolio rebalancing and health assessment.

**Trigger**: Runs in REBALANCE mode — daily at 9:30 AM IST or on-demand.

**Analysis performed**:

| Check | Threshold | Action |
|-------|-----------|--------|
| Sector concentration | Any sector > 30% of portfolio | Recommend trimming overweight sector |
| Cash allocation | Cash > 40% of total value | Flag as underinvested, trigger SCAN |
| Trailing Sharpe | Sharpe < 0 over 30 days | Reduce position sizes by 50% |
| Correlation | Two positions with ρ > 0.8 | Warn, suggest closing one |
| Drawdown | Portfolio down > 10% from peak | Activate defensive mode (higher confidence thresholds) |

**Output**: List of recommended rebalancing orders routed through Risk V2 → Trader V2.

---

### 5. Analyst V2 (`agents/analyst_agent.py` — modified)

**Change from V3**: The Analyst becomes a **signal merger** rather than the sole analysis source.

**V3 flow**: Fetch indicators → call Gemini → return signal
**V4 flow**: Receive quant_signals + sentiment_data → call Gemini as adjudicator → weighted merge → return signal

**Weighted merge formula**:
```
final_confidence = (
    0.50 * quant_signals.composite_score +
    0.30 * gemini_analysis_score +
    0.20 * sentiment_data.composite_sentiment
)
```

Weights are configurable via `user_settings.signal_weights`.

**Gemini's new role**: Instead of being the primary analyst, Gemini receives the quant and sentiment data as context and acts as an **adjudicator** — it can boost or reduce confidence based on qualitative reasoning that pure numbers miss (e.g., "this stock has earnings tomorrow, quant signals are unreliable pre-earnings").

**Output**: Same `TradeSignal` Pydantic model as V3 (backward compatible), with added `signal_source_breakdown` dict.

---

### 6. Risk Manager V2 (`agents/risk_manager.py` — upgraded)

**New capabilities over V3**:

#### Position Sizing — Kelly Criterion
```python
# Compute from last 50 closed trades
win_rate = wins / total_trades
avg_win = mean(winning_pnl_pcts)
avg_loss = mean(losing_pnl_pcts)  # absolute value

kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
position_pct = kelly_fraction * 0.5  # Half-Kelly for safety

# Guardrails
position_pct = max(0.005, min(position_pct, 0.05))  # 0.5% to 5% range
```

**Why Half-Kelly**: Full Kelly maximizes long-term growth but has enormous variance. Half-Kelly sacrifices ~25% growth rate but reduces volatility by ~50%. Critical for a system that may transition to real money.

**Fallback**: If fewer than 10 closed trades exist, use fixed 2% (current V3 behavior).

#### Dynamic Stop-Loss (ATR-Based)
```python
stop_loss = entry_price - (2.0 * quant_signals['atr_14'])
take_profit = entry_price + (3.0 * quant_signals['atr_14'])  # 1.5:1 reward-to-risk
```

#### Portfolio Heat
```python
# Sum of risk across all positions
portfolio_heat = sum(
    (position.value * abs(position.current_price - position.stop_loss) / position.current_price)
    for position in open_positions
)
heat_pct = portfolio_heat / total_portfolio_value

if heat_pct > 0.06:  # 6% total risk
    reject("Portfolio heat exceeds 6% — no new positions until risk decreases")
```

#### Correlation & Sector Checks
- Maintain sector mapping in `services/sector_map.py`
- If adding a position brings any sector above 30% of portfolio → reject
- If two positions have ρ > 0.8 (30-day return correlation) → warn

#### Drawdown Circuit Breaker
- Track peak portfolio value in database
- If current drawdown > 10% from peak → **defensive mode**:
  - Only allow positions with confidence > 0.85
  - Require Kelly fraction > 0
  - Reduce max position size to 1%

**Output schema**:
```python
risk_assessment = {
    "approved": True,
    "position_size_shares": 15,
    "position_size_value": 21375.00,
    "kelly_fraction": 0.034,
    "stop_loss_price": 1340.50,
    "stop_loss_type": "atr_trailing",
    "take_profit_price": 1530.75,
    "portfolio_heat_pct": 0.042,
    "sector_exposure": {"IT": 0.22, "Banking": 0.15},
    "correlation_warning": None,
    "rejection_reason": None
}
```

---

### 7. Supervisor V2 (`agents/supervisor.py` — rewritten)

**Key change**: Replace LLM-based routing with a **deterministic finite state machine**. The existing `fallback_decision()` function (line 138 in current supervisor.py) already implements most of this logic — it becomes the primary router, not the fallback.

**FSM transition table**:

```
SCAN MODE:
  ┌─────────────────────────────────────────────────────────────┐
  │ State              │ Condition              │ Next          │
  ├─────────────────────────────────────────────────────────────┤
  │ START              │ always                 │ scout         │
  │ scout_complete     │ ticker found           │ parallel_analysis │
  │ scout_complete     │ no ticker              │ COMPLETE      │
  │ parallel_analysis  │ always                 │ [quant, sentiment] │
  │ analysis_complete  │ always                 │ analyst       │
  │ analyst_complete   │ signal == BUY          │ risk          │
  │ analyst_complete   │ signal == WAIT/AVOID   │ COMPLETE      │
  │ risk_complete      │ approved               │ trader        │
  │ risk_complete      │ rejected               │ COMPLETE      │
  │ trade_complete     │ always                 │ COMPLETE      │
  │ ANY                │ iteration > 15         │ COMPLETE      │
  │ ANY                │ errors > 5             │ COMPLETE      │
  └─────────────────────────────────────────────────────────────┘

MONITOR MODE:
  ┌─────────────────────────────────────────────────────────────┐
  │ START              │ always                 │ exit_monitor  │
  │ exit_complete      │ exit_signals not empty │ trader (SELL) │
  │ exit_complete      │ no exits               │ COMPLETE      │
  │ trade_complete     │ always                 │ COMPLETE      │
  └─────────────────────────────────────────────────────────────┘

REBALANCE MODE:
  ┌─────────────────────────────────────────────────────────────┐
  │ START              │ always                 │ optimizer     │
  │ optimizer_complete │ rebalance orders exist │ risk          │
  │ optimizer_complete │ no changes needed      │ COMPLETE      │
  │ risk_complete      │ approved               │ trader        │
  │ risk_complete      │ rejected               │ COMPLETE      │
  │ trade_complete     │ always                 │ COMPLETE      │
  └─────────────────────────────────────────────────────────────┘
```

**Benefits of FSM over LLM routing**:
- **Speed**: No API call per hop — instant routing (~0ms vs ~500ms)
- **Cost**: Zero token consumption for routing decisions
- **Predictability**: Deterministic paths, no hallucinated routes
- **Debuggability**: Clear state machine, easy to trace

**LLM retained for**: Edge-case arbitration only (e.g., analyst returns a borderline signal with unusual reasoning — Supervisor can consult Gemini to decide).

---

## State Schema V4

### Current V3 State (flat, 15 fields)
```python
class SentinelState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    current_ticker: str
    market_data: Dict[str, Any]
    analyst_signal: Dict[str, Any]
    risk_approval: bool
    trade_status: str
    next_agent: str
    iteration_count: int
    errors: List[str]
    timestamp: str
    portfolio_snapshot: Dict[str, Any]
    user_id: str
    user_settings: Dict[str, Any]
    broadcast_callback: Optional[Callable]
```

### V4 State (partitioned, scoped)
```python
class SentinelStateV4(TypedDict):
    # ── Control (always present, minimal tokens) ──
    workflow_mode: Literal["scan", "monitor", "rebalance"]
    phase: Literal["scout", "analysis", "risk", "execution",
                    "exit_check", "rebalance", "complete"]
    next_agent: str
    iteration_count: int
    workflow_id: str
    user_id: str
    timestamp: str
    errors: List[str]

    # ── Messages (windowed to last 20) ──
    messages: Annotated[List[BaseMessage], operator.add]
    message_summary: str  # LLM summary of older messages

    # ── Scan Phase ──
    scan_results: Dict[str, Any]   # {candidates, batch_stats}
    current_ticker: str
    market_data: Dict[str, Any]

    # ── Quant Data (NEW) ──
    quant_signals: Dict[str, Any]  # composite_score, atr, confluence

    # ── Sentiment Data (NEW) ──
    sentiment_data: Dict[str, Any] # news_score, social_score, macro_score

    # ── Merged Analysis ──
    analyst_signal: Dict[str, Any] # V3 compatible + source_breakdown

    # ── Risk Assessment (replaces risk_approval: bool) ──
    risk_assessment: Dict[str, Any]  # kelly, stops, heat, sector exposure

    # ── Exit Monitor (NEW) ──
    exit_signals: List[Dict[str, Any]]  # triggered exits

    # ── Execution ──
    trade_status: str
    executed_orders: List[Dict[str, Any]]  # supports batch sells

    # ── Portfolio (enriched) ──
    portfolio_snapshot: Dict[str, Any]  # + sharpe, drawdown, sector_exposure

    # ── Configuration ──
    user_settings: Dict[str, Any]
    broadcast_callback: Optional[Callable]
```

**Key changes**:
- `risk_approval: bool` → `risk_assessment: Dict` (rich context)
- Added `quant_signals`, `sentiment_data`, `exit_signals` for new agents
- Added `message_summary` for context window compression
- Added `workflow_mode` and `phase` for FSM routing
- `executed_orders` is now a list (supports batch sells in rebalance)
- `portfolio_snapshot` includes analytics (Sharpe, drawdown)
- Backward compatible — all V3 fields preserved

---

## Data Pipeline & Memory Strategy

### 1. Trade Memory (pgvector in Supabase)

**Problem**: Agents have zero memory of past trades. A stock that lost money 3 times in similar conditions will be bought a 4th time with the same confidence.

**Solution**: Store trade outcomes as vector embeddings. Before entering a new position, query similar past trades to adjust confidence.

**Schema**:
```sql
-- Requires: CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE trade_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL,
    ticker TEXT NOT NULL,
    entry_date TIMESTAMPTZ NOT NULL,
    exit_date TIMESTAMPTZ,
    entry_price FLOAT NOT NULL,
    exit_price FLOAT,
    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
    pnl FLOAT,
    pnl_pct FLOAT,
    hold_days INT,
    entry_signal JSONB,          -- snapshot of analyst_signal at entry
    quant_snapshot JSONB,        -- snapshot of quant_signals at entry
    sentiment_snapshot JSONB,    -- snapshot of sentiment_data at entry
    outcome TEXT CHECK (outcome IN ('WIN', 'LOSS', 'OPEN')),
    embedding VECTOR(768),       -- Gemini text-embedding-004
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_trade_memory_embedding
    ON trade_memory USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX idx_trade_memory_user
    ON trade_memory (user_id, created_at DESC);
```

**Embedding generation** (on trade closure):
```python
text = f"""
Ticker: {ticker}
Signal: {signal} (confidence: {confidence})
Quant score: {quant_composite} | Sentiment: {sentiment_composite}
Indicators: RSI={rsi}, MACD={macd_signal}, BB={bb_position}, ADX={adx}
Sector: {sector}
Hold period: {hold_days} days
Outcome: {outcome} | PnL: {pnl_pct}%
"""
embedding = gemini.embed_content(model="models/text-embedding-004", content=text)
```

**Retrieval** (before new entry):
```python
similar_trades = supabase.rpc("match_trade_memory", {
    "query_embedding": current_trade_embedding,
    "match_count": 5,
    "match_threshold": 0.75
})

loss_rate = count(t for t in similar_trades if t.outcome == 'LOSS') / len(similar_trades)
if loss_rate > 0.60:
    confidence_adjustment = -0.10  # Reduce confidence
    broadcast("Memory", f"Warning: {loss_rate*100}% of similar past trades were losses")
```

### 2. Context Window Management

**Problem**: `state.messages` uses `operator.add` (append-only), growing unboundedly. After 10+ iterations, the message list dominates the state and wastes tokens.

**Solution**: Message windowing with summarization.

```python
MAX_MESSAGES = 20
SUMMARIZE_BATCH = 10

def manage_context(state):
    if len(state['messages']) > MAX_MESSAGES:
        old_messages = state['messages'][:SUMMARIZE_BATCH]
        summary = gemini_flash.invoke(
            f"Summarize these agent messages in 3 bullet points: {old_messages}"
        )
        state['message_summary'] = summary.content
        state['messages'] = state['messages'][SUMMARIZE_BATCH:]
    return state
```

**Cost**: One cheap Gemini Flash call per ~10 iterations. Saves significant tokens on subsequent agent calls that receive the full state.

### 3. Feedback Loop

After every trade closure (stop-loss, take-profit, or time exit):

```
1. Compute actual PnL and outcome (WIN/LOSS)
2. Generate embedding of the complete trade context
3. Store in trade_memory table
4. Update rolling statistics:
   - win_rate (last 50 trades)
   - avg_win, avg_loss (for Kelly Criterion)
   - sector performance breakdown
5. Risk Manager V2 reads these stats on next cycle
```

**Weekly batch job** (cron or Supabase function):
- Recompute Sharpe ratio, max drawdown, sector attribution
- Flag any strategy drift (e.g., confidence thresholds consistently wrong)
- Generate performance report accessible via API

### 4. Data Cache Service (`services/data_cache.py`)

**Problem**: Scout, Quant Agent, Analyst, and Exit Monitor all call yfinance independently for the same tickers. Redundant network calls slow cycles and risk rate limiting.

**Solution**: In-memory LRU cache with TTL.

```python
from functools import lru_cache
from datetime import datetime, timedelta

_cache = {}  # key: (ticker, interval, period) → (data, timestamp)
CACHE_TTL = {
    "1d": timedelta(hours=1),
    "1h": timedelta(minutes=15),
    "15m": timedelta(minutes=5),
}

def get_ohlcv(ticker: str, interval: str = "1d", period: str = "6mo"):
    key = (ticker, interval, period)
    if key in _cache:
        data, ts = _cache[key]
        if datetime.now() - ts < CACHE_TTL.get(interval, timedelta(minutes=5)):
            return data

    data = yfinance.download(ticker, interval=interval, period=period)
    _cache[key] = (data, datetime.now())
    return data
```

### 5. Real-Time Data Architecture (Phase 3)

For Phase 3, integrate with an Indian broker API that provides WebSocket feeds:

**Option A — Dhan API** (recommended):
- Free tier available
- WebSocket for live tick data
- REST for order placement (if we ever move to real trading)

**Option B — Kite Connect** (Zerodha):
- More established but requires ₹2,000/month subscription
- WebSocket + REST

**Architecture**:
```
Dhan WebSocket ──→ services/ws_feed.py ──→ asyncio.Queue
                                              │
                                    ┌─────────┼──────────┐
                                    ▼         ▼          ▼
                              Exit Monitor  Quant     Trader
                              (stop check) (live TA) (live price)
```

This replaces yfinance for live price checks, reducing latency from ~2s to ~50ms.

---

## Phase 1: Foundation — Exit Logic + Quant Analysis

**Goal**: Solve the two most critical gaps — positions can now be SOLD, and analysis has quantitative depth.

**Duration**: Weeks 1-3

### Week 1: State + Exit Monitor

| # | Task | File | Details |
|---|------|------|---------|
| 1.1 | Create `SentinelStateV4` | `agents/sentinel_state.py` | Extend with new fields (backward-compatible) |
| 1.2 | Create Exit Monitor agent | `agents/exit_monitor.py` | Stop-loss, take-profit, trailing stop, time-based exit |
| 1.3 | Add SELL support to Trader | `agents/trader_agent.py` | Handle `exit_signals` → SELL orders via broker_engine |
| 1.4 | Add MONITOR mode to Supervisor | `agents/supervisor.py` | FSM transitions for exit checking |
| 1.5 | Update graph with exit_monitor node | `agents/sentinel_hive.py` | New node + MONITOR mode edges |

### Week 2: Quant Agent + Data Cache

| # | Task | File | Details |
|---|------|------|---------|
| 2.1 | Create data cache service | `services/data_cache.py` | LRU cache with TTL for yfinance |
| 2.2 | Create Quant Agent | `agents/quant_agent.py` | BB, ATR, Fib, VWAP, Volume Profile, ADX |
| 2.3 | Implement multi-timeframe confluence | `agents/quant_agent.py` | Score across 15m, 1h, 1d |
| 2.4 | Update Analyst to merge quant signals | `agents/analyst_agent.py` | Weighted merge: quant 50% + gemini 30% |
| 2.5 | Add quant node to SCAN graph | `agents/sentinel_hive.py` | Scout → Quant → Analyst → Risk → Trader |

### Week 3: Risk V2 + Integration

| # | Task | File | Details |
|---|------|------|---------|
| 3.1 | Implement Kelly Criterion | `agents/risk_manager.py` | Half-Kelly from rolling 50-trade stats |
| 3.2 | ATR-based stop-loss sizing | `agents/risk_manager.py` | entry - 2×ATR, with guardrails |
| 3.3 | Portfolio heat calculation | `agents/risk_manager.py` | Sum of position risks, 6% cap |
| 3.4 | Create portfolio analytics service | `services/portfolio_analytics.py` | Sharpe, drawdown, sector exposure |
| 3.5 | Alternate SCAN/MONITOR in loop | `agents/agent_service.py` | SCAN every 5min, MONITOR every 1min between |
| 3.6 | Tests for new agents | `tests/` | Unit tests for quant, exit_monitor, risk_v2 |

**Phase 1 deliverable**: System can BUY and SELL, uses advanced TA with multi-timeframe confluence, enforces stop-losses automatically, and sizes positions with Kelly Criterion.

---

## Phase 2: Intelligence — Sentiment + Memory

**Goal**: Agents become contextually aware — they process market sentiment and learn from past trades.

**Duration**: Weeks 4-6

### Week 4: Sentiment Agent

| # | Task | File | Details |
|---|------|------|---------|
| 4.1 | Create sentiment pipeline service | `services/sentiment_pipeline.py` | RSS feeds, upgraded news scraping, macro data |
| 4.2 | Create Sentiment Agent | `agents/sentiment_agent.py` | Aggregate scores from pipeline, Gemini scoring |
| 4.3 | Add `feedparser` to requirements | `requirements.txt` | RSS feed parsing library |
| 4.4 | Integrate sentiment into Analyst V2 | `agents/analyst_agent.py` | Add sentiment_data to weighted merge (20% weight) |
| 4.5 | Add sentiment node to SCAN graph (parallel with quant) | `agents/sentinel_hive.py` | Fan-out after Scout |

### Week 5: Trade Memory

| # | Task | File | Details |
|---|------|------|---------|
| 5.1 | Create `trade_memory` table | `supabase_setup.sql` | pgvector schema with embedding index |
| 5.2 | Create memory service | `services/trade_memory.py` | Embed trades, store, retrieve similar |
| 5.3 | Wire embedding generation on trade close | `agents/trader_agent.py` | After SELL execution, generate + store embedding |
| 5.4 | Wire similarity check before entry | `agents/risk_manager.py` | Query top-5 similar trades, adjust confidence |
| 5.5 | Create feedback stats computation | `services/trade_memory.py` | Rolling win rate, avg win/loss for Kelly |

### Week 6: FSM Supervisor + Parallel Execution

| # | Task | File | Details |
|---|------|------|---------|
| 6.1 | Convert Supervisor to deterministic FSM | `agents/supervisor.py` | Remove Gemini from routing hot-path |
| 6.2 | Implement parallel fan-out | `agents/sentinel_hive.py` | Quant + Sentiment run concurrently (LangGraph Send) |
| 6.3 | Implement context window management | `agents/supervisor.py` | Message windowing + summarization |
| 6.4 | Add macro data scrapers | `services/sentiment_pipeline.py` | RBI policy, FII/DII flows |
| 6.5 | Integration tests | `tests/` | End-to-end SCAN + MONITOR cycle tests |

**Phase 2 deliverable**: System uses sentiment analysis from multiple sources, remembers past trades via vector similarity, routes deterministically without LLM overhead, and runs Quant + Sentiment in parallel.

---

## Phase 3: Optimization — Portfolio Management + Scale

**Goal**: Full portfolio lifecycle management, backtesting capability, and optional real-time data.

**Duration**: Weeks 7-9

### Week 7: Portfolio Optimizer

| # | Task | File | Details |
|---|------|------|---------|
| 7.1 | Create Portfolio Optimizer agent | `agents/portfolio_optimizer.py` | Sector rebalancing, concentration limits |
| 7.2 | Create sector mapping service | `services/sector_map.py` | NSE ticker → GICS sector mapping |
| 7.3 | Add REBALANCE workflow mode | `agents/sentinel_hive.py` | Optimizer → Risk → Trader graph |
| 7.4 | Implement correlation checks | `agents/risk_manager.py` | 30-day return correlation between positions |
| 7.5 | Implement drawdown circuit breaker | `agents/risk_manager.py` | 10% drawdown → defensive mode |

### Week 8: Data Feeds + Social

| # | Task | File | Details |
|---|------|------|---------|
| 8.1 | Investigate broker WebSocket integration | `services/ws_feed.py` | Dhan API or Kite Connect evaluation |
| 8.2 | Implement WebSocket feed client (if available) | `services/ws_feed.py` | Real-time tick data → asyncio queue |
| 8.3 | Wire real-time prices to Exit Monitor | `agents/exit_monitor.py` | Replace yfinance polling with WS ticks |
| 8.4 | Add Twitter/X sentiment (optional) | `services/sentiment_pipeline.py` | Cashtag scraping with rate limiting |

### Week 9: Backtesting + Hardening

| # | Task | File | Details |
|---|------|------|---------|
| 9.1 | Create backtesting engine | `services/backtester.py` | Replay historical data through Quant Agent's pure functions |
| 9.2 | Create signal history logging | `services/trade_memory.py` | Log all signals (not just executed trades) for RL training data |
| 9.3 | Add performance dashboard endpoints | `backend/routers/analytics.py` | Sharpe chart, drawdown chart, sector allocation |
| 9.4 | Load testing + edge case hardening | `tests/` | Stress test with 100+ positions, empty portfolio, API failures |
| 9.5 | Documentation | `README.md` | Update architecture section, agent descriptions |

**Phase 3 deliverable**: Full V4 system with portfolio optimization, potential real-time data feeds, backtesting capability, and production hardening.

---

## Risk Considerations & Failure Modes

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Gemini API outage** | Analyst + Sentiment agents fail | Rule-based fallback in Analyst; keyword scoring in Sentiment |
| **yfinance rate limiting** | Scout + Quant can't fetch data | `data_cache.py` with 5min TTL; spread requests across cycles |
| **pgvector not enabled in Supabase** | Memory features unavailable | Graceful degradation — skip similarity check, log warning |
| **State size explosion** | Token bloat in LangGraph | Message windowing caps at 20; agents read only their relevant fields |
| **SQLite write contention** | SCAN and MONITOR modes conflict | WAL mode for SQLite dev; Supabase handles concurrency in prod |

### Financial Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Kelly Criterion with small sample** | Wild position sizing early on | Fall back to fixed 2% until 30+ trades; Half-Kelly always |
| **Trailing stop whipsaw** | Stopped out on normal volatility | Use 2× ATR (not 1×); require close-basis triggers, not intraday |
| **Correlated mass exit** | All positions stop out in market crash | Drawdown circuit breaker at 10%; portfolio heat cap at 6% |
| **Stale sentiment** | News from 24h ago treated as current | `data_freshness_minutes` field; reject sentiment older than 4 hours |
| **Overfitting to memory** | Past losses prevent valid new trades | Similarity threshold at 0.75; max confidence adjustment of ±0.10 |

### Operational Failure Modes

| Failure Mode | Detection | Recovery |
|---|---|---|
| Gemini API down | Exception in analyst/sentiment | Fallback to rule-based analysis |
| yfinance returns empty data | Empty DataFrame check | Skip ticker, log error, try next batch |
| Supabase unreachable | broker_engine exception | Queue order locally in SQLite, retry next cycle |
| Exit Monitor misses a stop | Position PnL check on next cycle | Time-based exit as backstop (10 days max) |
| Infinite loop in FSM | `iteration_count > 15` guard | Force COMPLETE, log warning, alert via WebSocket |
| WebSocket feed disconnect | Heartbeat timeout (Phase 3) | Fall back to yfinance polling automatically |
| Memory embedding fails | Gemini embed exception | Store trade without embedding, retry in batch job |

### Architecture Decision Records

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| **FSM over LLM for routing** | Current Supervisor wastes ~500ms + tokens per hop on deterministic decisions | Loses ability to handle novel states (mitigated by LLM fallback for edge cases) |
| **No external TA library** | `ta-lib` requires C compilation, breaks on Render/Railway | Must implement indicators manually with numpy/pandas — more code but cleaner deploys |
| **Half-Kelly, not Full Kelly** | Full Kelly has enormous variance unsuitable for a system that may go live | Sacrifices ~25% theoretical growth for ~50% variance reduction |
| **Message windowing over full summarization** | Summarizing every message is expensive | Recent context is verbatim (accurate), old context is compressed (lossy) |
| **pgvector over dedicated vector DB** | Already using Supabase (Postgres); no new infrastructure | Lower performance than Pinecone/Weaviate at scale, but sufficient for <10k trades |
| **feedparser over paid news APIs** | Free, no API keys needed, sufficient for Phase 2 | Less reliable than Bloomberg/Reuters feeds; may miss breaking news |

---

## New Files Summary

| File | Type | Phase | Description |
|------|------|-------|-------------|
| `agents/quant_agent.py` | Agent | 1 | Multi-timeframe technical analysis with confluence scoring |
| `agents/exit_monitor.py` | Agent | 1 | Position exit condition monitoring |
| `agents/sentiment_agent.py` | Agent | 2 | Multi-source sentiment aggregation |
| `agents/portfolio_optimizer.py` | Agent | 3 | Portfolio rebalancing and health assessment |
| `services/data_cache.py` | Service | 1 | LRU cache for yfinance data with TTL |
| `services/portfolio_analytics.py` | Service | 1 | Sharpe ratio, drawdown, sector exposure calculations |
| `services/sentiment_pipeline.py` | Service | 2 | RSS + news + macro data aggregation |
| `services/trade_memory.py` | Service | 2 | pgvector embedding storage and similarity search |
| `services/sector_map.py` | Service | 3 | NSE ticker to sector mapping |
| `services/backtester.py` | Service | 3 | Historical data replay through quant functions |
| `services/ws_feed.py` | Service | 3 | Real-time WebSocket data feed client |
| `backend/routers/analytics.py` | Router | 3 | Performance dashboard API endpoints |

## Modified Files Summary

| File | Phase | Changes |
|------|-------|---------|
| `agents/sentinel_state.py` | 1 | Extend to SentinelStateV4 |
| `agents/sentinel_hive.py` | 1-3 | Add new nodes, modes, parallel edges |
| `agents/supervisor.py` | 1-2 | Add MONITOR mode (P1), convert to FSM (P2) |
| `agents/trader_agent.py` | 1 | Add SELL order execution |
| `agents/risk_manager.py` | 1-3 | Kelly, ATR stops, heat, correlation |
| `agents/analyst_agent.py` | 1-2 | Weighted signal merger |
| `agents/agent_service.py` | 1 | Alternate SCAN/MONITOR cycles |
| `services/news_loader.py` | 2 | Upgraded scraping for sentiment pipeline |
| `requirements.txt` | 2 | Add feedparser |
| `supabase_setup.sql` | 2 | Add trade_memory table with pgvector |
