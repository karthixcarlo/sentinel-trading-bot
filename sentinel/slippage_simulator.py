"""
Slippage Simulation Module

Injects realistic fill behavior into paper trading to prevent the "Paper Trading Illusion"
where paper fills are instant and perfect, unlike real market conditions.

This module simulates:
- Bid-ask spread costs
- Market impact from order size
- Partial fills
- Volatility-dependent slippage
- Market condition effects
"""

import random
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class MarketCondition(Enum):
    """Market liquidity and volatility regimes"""
    NORMAL = auto()      # Standard market hours, normal volume
    VOLATILE = auto()    # High volatility, wider spreads
    ILLIQUID = auto()    # Low volume, poor liquidity
    OPENING = auto()     # Market open (9:30-10:00 ET)
    CLOSING = auto()     # Market close (15:30-16:00 ET)


@dataclass
class FillResult:
    """Result of a simulated order fill"""
    order_id: str
    symbol: str
    order_type: Literal["MARKET", "LIMIT"]
    side: Literal["BUY", "SELL"]
    
    # Order details
    intended_price: float
    intended_qty: int
    
    # Fill details
    actual_fill_price: float
    filled_qty: int
    unfilled_qty: int
    
    # Cost analysis
    slippage_pct: float
    slippage_cost: float  # Total dollar cost of slippage
    spread_cost: float
    market_impact_cost: float
    total_cost: float
    
    # Context
    market_condition: MarketCondition
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def fill_ratio(self) -> float:
        """Percentage of order that was filled"""
        return self.filled_qty / max(self.intended_qty, 1)
    
    @property
    def is_complete(self) -> bool:
        """Whether order was completely filled"""
        return self.unfilled_qty == 0
    
    def __repr__(self) -> str:
        return (
            f"FillResult({self.side} {self.filled_qty}/{self.intended_qty} "
            f"{self.symbol} @ ${self.actual_fill_price:.4f}, "
            f"slippage={self.slippage_pct:.3f}%, cost=${self.total_cost:.2f})"
        )


class SlippageSimulator:
    """
    Simulates realistic order fills with slippage, spread, and market impact.
    
    This class helps calibrate risk models by injecting real-world execution costs
    into paper trading, preventing over-optimistic backtests.
    
    Example:
        >>> simulator = SlippageSimulator(condition=MarketCondition.NORMAL)
        >>> fill = simulator.simulate_fill(
        ...     order_type="MARKET",
        ...     side="BUY",
        ...     intended_price=150.0,
        ...     size=100,
        ...     symbol="AAPL"
        ... )
        >>> print(f"Slippage cost: ${fill.slippage_cost:.2f}")
    """
    
    # Slippage profiles by market condition (mean, std in percentage)
    # US Markets (default)
    SLIPPAGE_PROFILES_US = {
        MarketCondition.NORMAL: {"mean": 0.001, "std": 0.0005},      # 0.1% avg
        MarketCondition.VOLATILE: {"mean": 0.005, "std": 0.003},     # 0.5% avg
        MarketCondition.ILLIQUID: {"mean": 0.01, "std": 0.008},      # 1.0% avg
        MarketCondition.OPENING: {"mean": 0.008, "std": 0.005},      # 0.8% avg
        MarketCondition.CLOSING: {"mean": 0.006, "std": 0.004},      # 0.6% avg
    }
    
    # Indian Markets (higher slippage due to wider spreads)
    SLIPPAGE_PROFILES_INDIA = {
        MarketCondition.NORMAL: {"mean": 0.0015, "std": 0.0008},     # 0.15% avg
        MarketCondition.VOLATILE: {"mean": 0.0075, "std": 0.004},    # 0.75% avg
        MarketCondition.ILLIQUID: {"mean": 0.015, "std": 0.012},     # 1.5% avg
        MarketCondition.OPENING: {"mean": 0.012, "std": 0.007},      # 1.2% avg
        MarketCondition.CLOSING: {"mean": 0.009, "std": 0.006},      # 0.9% avg
    }
    
    # Partial fill probabilities by condition
    PARTIAL_FILL_PROFILES = {
        MarketCondition.NORMAL: {"min": 0.95, "max": 1.0},
        MarketCondition.VOLATILE: {"min": 0.85, "max": 1.0},
        MarketCondition.ILLIQUID: {"min": 0.70, "max": 0.95},
        MarketCondition.OPENING: {"min": 0.80, "max": 1.0},
        MarketCondition.CLOSING: {"min": 0.90, "max": 1.0},
    }
    
    def __init__(
        self,
        condition: MarketCondition = MarketCondition.NORMAL,
        spread_bps: float = 5.0,  # Typical bid-ask spread in basis points
        enable_partial_fills: bool = True,
        seed: Optional[int] = None,
        market_region: str = "USA"  # "USA" or "INDIA"
    ):
        """
        Initialize the slippage simulator.
        
        Args:
            condition: Current market condition
            spread_bps: Bid-ask spread in basis points (1 bp = 0.01%)
            enable_partial_fills: Whether to simulate partial fills
            seed: Random seed for reproducibility in testing
            market_region: "USA" or "INDIA" for region-specific slippage profiles
        """
        self.condition = condition
        self.spread_bps = spread_bps
        self.enable_partial_fills = enable_partial_fills
        self.market_region = market_region.upper()
        
        # Select appropriate slippage profile based on market region
        if self.market_region == "INDIA":
            self.slippage_profiles = self.SLIPPAGE_PROFILES_INDIA
            logger.info("Using Indian market slippage profiles (higher slippage)")
        else:
            self.slippage_profiles = self.SLIPPAGE_PROFILES_US
            logger.info("Using US market slippage profiles")
        
        if seed is not None:
            random.seed(seed)
        
        # Track all fills for analysis
        self.fill_log: List[FillResult] = []
        
    def simulate_fill(
        self,
        order_type: Literal["MARKET", "LIMIT"],
        side: Literal["BUY", "SELL"],
        intended_price: float,
        size: int,
        symbol: str,
        order_id: Optional[str] = None
    ) -> FillResult:
        """
        Simulate a realistic order fill with slippage and costs.
        
        Args:
            order_type: "MARKET" or "LIMIT"
            side: "BUY" or "SELL"
            intended_price: Expected execution price
            size: Number of shares to trade
            symbol: Ticker symbol
            order_id: Optional order identifier
            
        Returns:
            FillResult with actual fill details and cost breakdown
        """
        if order_id is None:
            order_id = f"{symbol}_{datetime.utcnow().timestamp()}"
        
        # 1. Calculate base slippage from market condition
        profile = self.slippage_profiles[self.condition]
        base_slippage_pct = abs(random.gauss(profile["mean"], profile["std"]))
        
        # 2. Market orders get worse execution than limit orders
        if order_type == "MARKET":
            base_slippage_pct *= 1.5
        
        # 3. Calculate spread cost (half-spread for market orders)
        spread_pct = (self.spread_bps / 10000) / 2  # Convert bps to percentage, take half
        
        # 4. Calculate market impact based on size
        # Larger orders move the market more
        size_impact_pct = self._calculate_market_impact(size, intended_price)
        
        # 5. Total slippage
        total_slippage_pct = base_slippage_pct + spread_pct + size_impact_pct
        
        # 6. Direction: buys get filled higher, sells get filled lower
        direction_multiplier = 1 if side == "BUY" else -1
        
        # 7. Calculate actual fill price
        actual_fill_price = intended_price * (1 + (total_slippage_pct * direction_multiplier))
        
        # 8. Simulate partial fills
        filled_qty = size
        if self.enable_partial_fills:
            fill_profile = self.PARTIAL_FILL_PROFILES[self.condition]
            fill_ratio = random.uniform(fill_profile["min"], fill_profile["max"])
            filled_qty = int(size * fill_ratio)
            
            # Ensure at least some fill for market orders
            if order_type == "MARKET" and filled_qty == 0 and size > 0:
                filled_qty = max(1, size // 10)
        
        unfilled_qty = size - filled_qty
        
        # 9. Calculate costs
        slippage_cost = abs(actual_fill_price - intended_price) * filled_qty
        spread_cost = intended_price * spread_pct * filled_qty
        market_impact_cost = intended_price * size_impact_pct * filled_qty
        total_cost = slippage_cost
        
        # 10. Create fill result
        fill_result = FillResult(
            order_id=order_id,
            symbol=symbol,
            order_type=order_type,
            side=side,
            intended_price=intended_price,
            intended_qty=size,
            actual_fill_price=round(actual_fill_price, 4),
            filled_qty=filled_qty,
            unfilled_qty=unfilled_qty,
            slippage_pct=round(total_slippage_pct * 100, 4),
            slippage_cost=round(slippage_cost, 2),
            spread_cost=round(spread_cost, 2),
            market_impact_cost=round(market_impact_cost, 2),
            total_cost=round(total_cost, 2),
            market_condition=self.condition
        )
        
        # Log the fill
        self.fill_log.append(fill_result)
        
        logger.info(f"Simulated fill: {fill_result}")
        
        return fill_result
    
    def _calculate_market_impact(self, size: int, price: float) -> float:
        """
        Calculate market impact based on order size.
        
        Larger orders have more market impact. This uses a simplified square-root
        model where impact scales with sqrt(size).
        
        Args:
            size: Number of shares
            price: Current price
            
        Returns:
            Market impact as a percentage
        """
        # Base impact: 0.01% per 1000 shares
        base_impact_per_1k = 0.0001
        
        # Square root scaling (larger orders have diminishing marginal impact)
        impact_pct = base_impact_per_1k * (size / 1000) ** 0.5
        
        # Condition multipliers
        condition_multipliers = {
            MarketCondition.NORMAL: 1.0,
            MarketCondition.VOLATILE: 1.5,
            MarketCondition.ILLIQUID: 2.5,
            MarketCondition.OPENING: 1.8,
            MarketCondition.CLOSING: 1.3,
        }
        
        multiplier = condition_multipliers.get(self.condition, 1.0)
        
        return impact_pct * multiplier
    
    def get_cumulative_slippage_cost(self) -> float:
        """
        Calculate total slippage cost across all fills.
        
        Returns:
            Total dollar cost of slippage
        """
        return sum(fill.slippage_cost for fill in self.fill_log)
    
    def get_statistics(self) -> Dict:
        """
        Get statistical summary of all simulated fills.
        
        Returns:
            Dictionary with fill statistics
        """
        if not self.fill_log:
            return {
                "total_fills": 0,
                "avg_slippage_pct": 0.0,
                "total_slippage_cost": 0.0,
                "complete_fill_rate": 0.0
            }
        
        total_fills = len(self.fill_log)
        avg_slippage = sum(f.slippage_pct for f in self.fill_log) / total_fills
        total_cost = self.get_cumulative_slippage_cost()
        complete_fills = sum(1 for f in self.fill_log if f.is_complete)
        
        return {
            "total_fills": total_fills,
            "avg_slippage_pct": round(avg_slippage, 4),
            "total_slippage_cost": round(total_cost, 2),
            "complete_fill_rate": round(complete_fills / total_fills, 4),
            "total_shares_traded": sum(f.filled_qty for f in self.fill_log),
            "avg_fill_ratio": round(
                sum(f.fill_ratio for f in self.fill_log) / total_fills, 4
            ),
            "market_condition": self.condition.name
        }
    
    def set_condition(self, condition: MarketCondition):
        """Update the current market condition"""
        logger.info(f"Market condition changed: {self.condition.name} -> {condition.name}")
        self.condition = condition
    
    def reset_log(self):
        """Clear the fill log"""
        self.fill_log.clear()
        logger.info("Fill log reset")
    
    def export_fills(self) -> List[Dict]:
        """
        Export fill log as list of dictionaries for analysis.
        
        Returns:
            List of fill results as dictionaries
        """
        return [
            {
                "order_id": f.order_id,
                "symbol": f.symbol,
                "side": f.side,
                "order_type": f.order_type,
                "intended_price": f.intended_price,
                "actual_fill_price": f.actual_fill_price,
                "filled_qty": f.filled_qty,
                "slippage_pct": f.slippage_pct,
                "slippage_cost": f.slippage_cost,
                "total_cost": f.total_cost,
                "market_condition": f.market_condition.name,
                "timestamp": f.timestamp.isoformat()
            }
            for f in self.fill_log
        ]
