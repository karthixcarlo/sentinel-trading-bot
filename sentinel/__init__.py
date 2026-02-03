"""
Project Sentinel - Autonomous Intraday Trading Agent
Phase 1: Core Risk Management Modules
Phase 2: Tiered Caching & Circuit Breaker
Phase 3: Multi-Agent Orchestration
Phase 4: Real Data Integration
Phase 5: Alpaca Paper Trading
"""

__version__ = "0.5.0"
__author__ = "Project Sentinel Team"

# Phase 1 exports
from .signal_synchronizer import TimestampedSignal, SignalSynchronizer
from .slippage_simulator import MarketCondition, SlippageSimulator
from .risk_model import ConservativeRiskModel

# Phase 2 exports
from .cache_manager import CacheManager, CacheTier, CachedData
from .circuit_breaker import CircuitBreaker, BreakerState, HealthCheck
from .async_utils import (
    gather_with_timeout,
    retry_with_backoff,
    rate_limit,
    run_with_semaphore,
    AsyncTimer
)

# Phase 3 exports
from .agents import (
    AgentState,
    BaseAgent,
    AgentResult,
    ScoutAgent,
    AnalystAgent,
    ExecutionerAgent
)
from .orchestrator import TradingOrchestrator

# Phase 4 exports
from .data import (
    YFinanceProvider,
    TechnicalProvider,
    RealNewsProvider,
    ProviderFactory
)

# Phase 5 exports
from .execution import (
    AlpacaClient,
    PaperTradingExecutor,
    PortfolioManager
)
from .config import has_alpaca_credentials

__all__ = [
    # Phase 1
    "TimestampedSignal",
    "SignalSynchronizer",
    "MarketCondition",
    "SlippageSimulator",
    "ConservativeRiskModel",
    # Phase 2
    "CacheManager",
    "CacheTier",
    "CachedData",
    "CircuitBreaker",
    "BreakerState",
    "HealthCheck",
    "gather_with_timeout",
    "retry_with_backoff",
    "rate_limit",
    "run_with_semaphore",
    "AsyncTimer",
    # Phase 3
    "AgentState",
    "BaseAgent",
    "AgentResult",
    "ScoutAgent",
    "AnalystAgent",
    "ExecutionerAgent",
    "TradingOrchestrator",
    # Phase 4
    "YFinanceProvider",
    "TechnicalProvider",
    "RealNewsProvider",
    "ProviderFactory",
    # Phase 5
    "AlpacaClient",
    "PaperTradingExecutor",
    "PortfolioManager",
    "has_alpaca_credentials",
]
