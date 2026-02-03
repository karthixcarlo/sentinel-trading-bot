"""
Data package initialization
"""

# Mock providers (Phase 3)
from .mock_sources import (
    MockPriceProvider,
    MockNewsProvider,
    MockTechnicalProvider,
    MockSupplyChainProvider,
    get_price_provider,
    get_news_provider,
    get_technical_provider,
    get_supply_chain_provider,
)

# Real providers (Phase 4)
from .yfinance_provider import YFinanceProvider
from .technical_provider import TechnicalProvider
from .real_news_provider import RealNewsProvider
from .provider_factory import ProviderFactory

__all__ = [
    # Mock providers
    "MockPriceProvider",
    "MockNewsProvider",
    "MockTechnicalProvider",
    "MockSupplyChainProvider",
    "get_price_provider",
    "get_news_provider",
    "get_technical_provider",
    "get_supply_chain_provider",
    # Real providers
    "YFinanceProvider",
    "TechnicalProvider",
    "RealNewsProvider",
    "ProviderFactory",
]
