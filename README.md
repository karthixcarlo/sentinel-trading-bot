# Project Sentinel - Autonomous Trading Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Markets](https://img.shields.io/badge/markets-US%20%7C%20India-blue)](.)

## Overview

**Project Sentinel** is an autonomous intraday trading agent built with a focus on robust risk management and realistic execution modeling. Supports both **US markets** (via Alpaca) and **Indian markets** (NSE/BSE via Zerodha).

### 🎯 Core Modules

1. **SignalSynchronizer** - Temporal alignment of signals from different data sources
2. **SlippageSimulator** - Realistic order fill simulation with market-specific profiles
3. **ConservativeRiskModel** - Pessimistic cost modeling and position sizing
4. **Multi-Market Support** - Seamless switching between US and Indian markets

---

## 🚨 Problems Solved

### Failure Point 1: Data Consistency Gap
**Problem:** `yfinance` (1min delayed) vs web scraping (real-time) creates temporal mismatches  
**Solution:** `SignalSynchronizer` aligns all signals to common time windows with staleness detection

### Failure Point 2: Paper Trading Illusion
**Problem:** Paper fills are instant and perfect, unlike real market conditions  
**Solution:** `SlippageSimulator` injects realistic slippage, spread costs, and partial fills

### Failure Point 3: Zero-Capital Trap
**Problem:** Backtests underestimate costs, leading to over-optimistic results  
**Solution:** `ConservativeRiskModel` applies pessimistic assumptions and minimum hurdle rates

---

## 🎨 Interactive Dashboard (NEW!)

**Zero-code interface** for Project Sentinel! Control everything through a beautiful web dashboard.

### Quick Start

```bash
# Launch the dashboard
run_dashboard.bat

# Dashboard opens at: http://localhost:8501
```

### Features

- **🏠 Home** - Market overview, live status, index quotes
- **🔍 Discover** - One-click auto-discovery of trending Indian stocks
- **📊 Analyze** - Deep stock analysis with charts and recommendations *(coming soon)*
- **💼 Portfolio** - Live position tracking and P&L monitoring *(coming soon)*
- **💰 Trade** - Execute trades with simple forms *(coming soon)*
- **⚙️ Settings** - Configure risk parameters, no coding needed
- **📈 Performance** - Analytics and performance tracking *(coming soon)*

**See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md) for complete guide.**

---

## 📦 Installation

```bash
# Clone the repository
cd C:\Users\Karthi\Desktop\Agent

# Install dependencies (Python 3.8+)
pip install -r requirements.txt

# Run tests
python -m pytest tests/ -v
```

---

## 🚀 Quick Start

### Example 1: Signal Synchronization

```python
from datetime import datetime, timedelta
from sentinel import TimestampedSignal, SignalSynchronizer

# Create synchronizer with 5-minute windows
sync = SignalSynchronizer(window_size=timedelta(minutes=5))

# Add signals from different sources
price_signal = TimestampedSignal("PRICE", 150.25, datetime.utcnow())
news_signal = TimestampedSignal("NEWS", 78.5, datetime.utcnow())

sync.add_signal(price_signal)
sync.add_signal(news_signal)

# Get synchronized window
window = sync.get_synchronized_window(required_types=["PRICE", "NEWS"])

if window["status"] == "READY":
    print(f"Signals synchronized: {window['signal_count']} signals")
    # Make trading decision with aligned signals
```

### Example 2: Slippage Simulation

```python
from sentinel import MarketCondition, SlippageSimulator

# Create simulator for normal market conditions
simulator = SlippageSimulator(condition=MarketCondition.NORMAL)

# Simulate a market order
fill = simulator.simulate_fill(
    order_type="MARKET",
    side="BUY",
    intended_price=150.0,
    size=100,
    symbol="AAPL"
)

print(f"Intended: ${fill.intended_price:.2f}")
print(f"Actual Fill: ${fill.actual_fill_price:.4f}")
print(f"Slippage Cost: ${fill.slippage_cost:.2f}")
```

### Example 3: Conservative Position Sizing

```python
from sentinel import ConservativeRiskModel

# Create risk model with $10,000 account
risk_model = ConservativeRiskModel(account_balance=10000.0)

# Calculate safe position size
shares, risk_params = risk_model.calculate_position_size(
    entry_price=150.0,
    stop_loss_price=147.0,  # 2% stop
    confidence=0.8
)

print(f"Position: {shares} shares")
print(f"Max Risk: ${risk_params.max_loss_amount:.2f}")
print(f"Portfolio Exposure: {risk_params.portfolio_exposure_pct:.2f}%")
```

### Example 4: Indian Market Trading (🇮🇳 NEW!)

```python
# Set market to India in .env
# MARKET_REGION=INDIA

from sentinel import ProviderFactory, ConservativeRiskModel
from sentinel.indian_market_config import is_market_open, IST
from datetime import datetime

# Initialize for Indian market
provider = ProviderFactory(market_region="INDIA")
price_provider = provider.get_price_provider()

# Get NSE stock quote
quote = await price_provider.get_quote("RELIANCE", exchange="NSE")
print(f"RELIANCE: ₹{quote['price']:.2f}")

# Risk model with INR
risk_model = ConservativeRiskModel(
    account_balance=100000.0,  # ₹1 lakh
    market_region="INDIA",
    currency="INR"
)

# Check market hours (IST)
if is_market_open():
    print("NSE is OPEN (9:15 AM - 3:30 PM IST)")
```

**See [INDIAN_MARKET_SETUP.md](INDIAN_MARKET_SETUP.md) for complete Indian market guide.**

---

## 📚 Module Documentation

### SignalSynchronizer

**Purpose:** Align signals from different sources to common time windows

**Key Features:**
- Window-based temporal alignment (configurable window size)
- Staleness detection (reject outdated signals)
- Signal completeness validation (ensure all required signals present)
- Automatic cleanup of stale signals

**Configuration:**
```python
SignalSynchronizer(
    window_size=timedelta(minutes=5),  # Time window size
    max_buffer_size=1000,              # Max signals to buffer
    cleanup_interval=10                # Cleanup frequency
)
```

### SlippageSimulator

**Purpose:** Inject realistic execution costs into paper trading

**Key Features:**
- Market condition profiles (NORMAL, VOLATILE, ILLIQUID, OPENING, CLOSING)
- Bid-ask spread modeling
- Market impact calculation (size-dependent)
- Partial fill simulation
- Cumulative cost tracking

**Configuration:**
```python
SlippageSimulator(
    condition=MarketCondition.NORMAL,  # Market regime
    spread_bps=5.0,                    # Bid-ask spread (basis points)
    enable_partial_fills=True          # Simulate partial fills
)
```

**Slippage Profiles:**
| Condition | Avg Slippage | Partial Fill Range |
|-----------|--------------|-------------------|
| NORMAL    | 0.10%        | 95-100%          |
| VOLATILE  | 0.50%        | 85-100%          |
| ILLIQUID  | 1.00%        | 70-95%           |
| OPENING   | 0.80%        | 80-100%          |
| CLOSING   | 0.60%        | 90-100%          |

### ConservativeRiskModel

**Purpose:** Conservative position sizing with pessimistic cost assumptions

**Key Features:**
- Hurdle rate filtering (0.5% minimum expected profit)
- Multi-constraint position sizing (risk + exposure limits)
- Confidence and volatility scaling
- Trade validation against risk limits

**Configuration:**
```python
ConservativeRiskModel(
    account_balance=10000.0,
    custom_assumptions={
        "assumed_slippage": 0.002,     # 0.2% per trade
        "hurdle_rate": 0.005           # 0.5% minimum profit
    }
)
```

**Risk Limits:**
- Max position size: 5% of account
- Max risk per trade: 1% of account
- Hard stop loss: 2% from entry
- Minimum hurdle rate: 0.5% expected profit after costs

---

## 🧪 Testing

Run the complete test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_signal_synchronizer.py -v
python -m pytest tests/test_slippage_simulator.py -v
python -m pytest tests/test_risk_model.py -v

# Run with coverage
python -m pytest tests/ --cov=sentinel --cov-report=html
```

Run example scripts:

```bash
# Run all examples
python examples/phase1_examples.py

# Examples include:
# 1. Signal synchronization demo
# 2. Slippage simulation comparison
# 3. Risk management scenarios
# 4. Integrated trading workflow
```

---

## 📊 Project Structure

```
Agent/
├── sentinel/                    # Core package
│   ├── __init__.py             # Package exports
│   ├── signal_synchronizer.py  # Temporal alignment module
│   ├── slippage_simulator.py   # Fill simulation module
│   └── risk_model.py           # Position sizing module
├── tests/                       # Unit tests
│   ├── test_signal_synchronizer.py
│   ├── test_slippage_simulator.py
│   └── test_risk_model.py
├── examples/                    # Usage examples
│   └── phase1_examples.py
└── README.md                    # This file
```

---

## 🔧 Advanced Usage

### Integrated Trading Workflow

See `examples/phase1_examples.py` for a complete workflow that:
1. Synchronizes price, news, and technical signals
2. Makes trading decisions based on aligned signals
3. Calculates conservative position sizes
4. Validates trades against risk limits
5. Simulates realistic order execution
6. Tracks total costs and slippage

### Custom Cost Assumptions

```python
# Override default assumptions for specific strategies
custom_model = ConservativeRiskModel(
    account_balance=10000.0,
    custom_assumptions={
        "assumed_slippage": 0.005,      # Higher slippage for illiquid stocks
        "assumed_spread": 0.002,        # Wider spreads
        "market_impact": 0.003,         # Higher impact
        "hurdle_rate": 0.01             # Higher hurdle (1%)
    }
)
```

### Dynamic Market Conditions

```python
# Adjust simulator based on time of day
from datetime import datetime

now = datetime.now()
hour = now.hour

if 9 <= hour < 10:  # Market open
    simulator.set_condition(MarketCondition.OPENING)
elif 15 <= hour < 16:  # Market close
    simulator.set_condition(MarketCondition.CLOSING)
else:
    simulator.set_condition(MarketCondition.NORMAL)
```

---

## 📈 Performance Metrics

Track system performance with built-in metrics:

```python
# Signal synchronizer metrics
metrics = sync.get_metrics()
print(f"Drop rate: {metrics['drop_rate']:.2%}")
print(f"Windows completed: {metrics['windows_completed']}")

# Slippage simulator statistics
stats = simulator.get_statistics()
print(f"Avg slippage: {stats['avg_slippage_pct']:.3f}%")
print(f"Total cost: ${stats['total_slippage_cost']:.2f}")

# Risk model summary
summary = risk_model.get_risk_summary()
print(f"Max position: ${summary['max_position_value']:.2f}")
print(f"Total cost per roundtrip: {summary['total_cost_per_roundtrip_pct']:.3f}%")
```

---

## 🛣️ Roadmap

### Phase 1 ✅ (Current)
- [x] Signal synchronization
- [x] Slippage simulation
- [x] Conservative risk model
- [x] Unit tests
- [x] Usage examples

### Phase 2 (Next)
- [ ] Tiered caching for GraphRAG (overnight batch + real-time lite)
- [ ] Circuit breaker with persistence
- [ ] Multi-agent orchestration with LangGraph
- [ ] Integration with Alpaca Paper Trading API

### Phase 3 (Future)
- [ ] Deep perception agent (supply chain analysis)
- [ ] Analyst agent (multi-factor analysis)
- [ ] Executioner agent (risk-managed execution)
- [ ] Full system integration and testing

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

This is a research/educational project. Contributions welcome via pull requests.

---

## ⚠️ Disclaimer

**This software is for educational and research purposes only.** It is not financial advice. Trading involves substantial risk of loss. Always test thoroughly with paper trading before considering live deployment.

---

## 📧 Contact

For questions or feedback, please open an issue on the repository.

---

**Built with a focus on realistic risk management and robust execution modeling.**
