"""
Provider Factory - Easy Switching Between Mock and Real Data

Provides a simple interface to switch between mock and real data providers.
Supports both US markets (Alpaca/YFinance) and Indian markets (Zerodha/Yahoo India).
"""

import logging
from typing import Optional

from .mock_sources import (
    MockPriceProvider,
    MockNewsProvider,
    MockTechnicalProvider,
    MockSupplyChainProvider
)

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating data providers.
    
    Enables easy switching between mock and real providers for testing
    and production use. Supports both US and Indian markets.
    """
    
    def __init__(
        self,
        use_mock: bool = False,
        cache_manager=None,
        market_region: Optional[str] = None
    ):
        """
        Initialize provider factory.
        
        Args:
            use_mock: If True, use mock providers. If False, use real providers.
            cache_manager: Optional CacheManager for real providers
            market_region: "USA" or "INDIA" (auto-detected from config if None)
        """
        self.use_mock = use_mock
        self.cache_manager = cache_manager
        
        # Auto-detect market region from config
        if market_region is None:
            from sentinel.config import MARKET_REGION
            market_region = MARKET_REGION
        
        self.market_region = market_region.upper()
        
        # Initialize providers lazily
        self._price_provider = None
        self._news_provider = None
        self._technical_provider = None
        self._supply_chain_provider = None
        
        logger.info(
            f"ProviderFactory initialized (use_mock={use_mock}, "
            f"market_region={self.market_region})"
        )
    
    def get_price_provider(self):
        """Get price provider (mock or real, market-aware)"""
        if self._price_provider is None:
            if self.use_mock:
                self._price_provider = MockPriceProvider()
                logger.debug("Using MockPriceProvider")
            else:
                # Route to appropriate provider based on market region
                if self.market_region == "INDIA":
                    from .indian_price_provider import IndianPriceProvider
                    from sentinel.config import INDIAN_EXCHANGE
                    self._price_provider = IndianPriceProvider(
                        cache_manager=self.cache_manager,
                        cache_ttl=300,  # 5 minutes
                        exchange=INDIAN_EXCHANGE
                    )
                    logger.debug(f"Using IndianPriceProvider (exchange={INDIAN_EXCHANGE})")
                else:
                    # Default to US markets
                    from .yfinance_provider import YFinanceProvider
                    self._price_provider = YFinanceProvider(
                        cache_manager=self.cache_manager,
                        cache_ttl=300  # 5 minutes
                    )
                    logger.debug("Using YFinanceProvider (US markets)")
        
        return self._price_provider
    
    def get_news_provider(self):
        """Get news provider (mock or real)"""
        if self._news_provider is None:
            if self.use_mock:
                self._news_provider = MockNewsProvider()
                logger.debug("Using MockNewsProvider")
            else:
                from .real_news_provider import RealNewsProvider
                self._news_provider = RealNewsProvider(
                    cache_manager=self.cache_manager,
                    cache_ttl=21600  # 6 hours
                )
                logger.debug("Using RealNewsProvider")
        
        return self._news_provider
    
    def get_technical_provider(self):
        """Get technical provider (mock or real)"""
        if self._technical_provider is None:
            if self.use_mock:
                self._technical_provider = MockTechnicalProvider()
                logger.debug("Using MockTechnicalProvider")
            else:
                from .technical_provider import TechnicalProvider
                price_provider = self.get_price_provider()
                self._technical_provider = TechnicalProvider(
                    price_provider=price_provider,
                    cache_manager=self.cache_manager,
                    cache_ttl=3600  # 1 hour
                )
                logger.debug("Using TechnicalProvider")
        
        return self._technical_provider
    
    def get_supply_chain_provider(self):
        """Get supply chain provider (always mock for now)"""
        if self._supply_chain_provider is None:
            # Always use mock for supply chain (no real implementation yet)
            self._supply_chain_provider = MockSupplyChainProvider()
            logger.debug("Using MockSupplyChainProvider")
        
        return self._supply_chain_provider
