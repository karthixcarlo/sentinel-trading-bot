"""
Conservative Risk Model Module

Implements pessimistic cost assumptions to prevent the "Zero-Capital Trap" where
backtests look better than live trading due to underestimated costs.

This module ensures that only trades with sufficient expected profit (after all costs)
are executed, with built-in safety margins.
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RiskParameters:
    """Risk parameters for a trade"""
    max_position_size: int
    stop_loss_price: float
    take_profit_price: float
    max_loss_amount: float
    expected_profit: float
    risk_reward_ratio: float
    position_value: float
    portfolio_exposure_pct: float


class ConservativeRiskModel:
    """
    Pessimistic risk model that assumes worst-case costs.
    
    This class adjusts expected returns by conservative cost estimates to ensure
    that only genuinely profitable trades (after all friction) are executed.
    
    Philosophy: Better to be surprised by LESS slippage than MORE.
    
    Example:
        >>> model = ConservativeRiskModel()
        >>> adjusted = model.adjust_expected_return(
        ...     raw_expected_return=0.015,  # 1.5% expected
        ...     num_roundtrips=1
        ... )
        >>> if adjusted > 0:
        ...     print("Trade passes hurdle rate")
    """
    
    # Pessimistic cost assumptions (percentages) - US Markets
    ASSUMED_SLIPPAGE_US = 0.002       # 0.2% per trade (conservative)
    ASSUMED_SPREAD_US = 0.001         # 0.1% half-spread
    MARKET_IMPACT_US = 0.001          # 0.1% for small orders
    REGULATORY_FEES_US = 0.00005      # ~$0.005 per share (SEC fees)
    
    # Indian Markets (higher costs)
    ASSUMED_SLIPPAGE_INDIA = 0.003    # 0.3% per trade
    ASSUMED_SPREAD_INDIA = 0.002      # 0.2% half-spread (wider spreads)
    MARKET_IMPACT_INDIA = 0.002       # 0.2% for small orders  
    STT_INTRADAY = 0.00025            # 0.025% STT on sell side (intraday)
    EXCHANGE_CHARGES_INDIA = 0.0000345  # NSE transaction charges
    GST_INDIA = 0.18                  # 18% GST on charges
    
    COMMISSION_PER_SHARE = 0.0        # Broker-dependent, kept 0 for conservative estimate
    
    # Risk limits
    MAX_POSITION_SIZE_PCT = 0.05   # 5% of portfolio max
    MAX_RISK_PER_TRADE_PCT = 0.01  # 1% max risk per trade
    HARD_STOP_LOSS_PCT = 0.02      # 2% hard stop
    
    # Minimum hurdle rate (don't trade for less than this expected profit)
    HURDLE_RATE = 0.005            # 0.5% minimum expected profit after costs
    
    def __init__(
        self,
        account_balance: float = 10000.0,
        custom_assumptions: Optional[Dict[str, float]] = None,
        market_region: str = "USA",  # "USA" or "INDIA"
        currency: str = "USD"  # "USD" or "INR"
    ):
        """
        Initialize the conservative risk model.
        
        Args:
            account_balance: Current account balance for position sizing
            custom_assumptions: Override default cost assumptions
            market_region: "USA" or "INDIA" for market-specific costs
            currency: "USD" or "INR"
        """
        self.account_balance = account_balance
        self.market_region = market_region.upper()
        self.currency = currency.upper()
        
        # Set market-specific defaults
        if self.market_region == "INDIA":
            self.ASSUMED_SLIPPAGE = self.ASSUMED_SLIPPAGE_INDIA
            self.ASSUMED_SPREAD = self.ASSUMED_SPREAD_INDIA
            self.MARKET_IMPACT = self.MARKET_IMPACT_INDIA
            self.REGULATORY_FEES = self.STT_INTRADAY + self.EXCHANGE_CHARGES_INDIA
            logger.info(f"Risk model initialized for Indian market (currency: {self.currency})")
        else:
            self.ASSUMED_SLIPPAGE = self.ASSUMED_SLIPPAGE_US
            self.ASSUMED_SPREAD = self.ASSUMED_SPREAD_US
            self.MARKET_IMPACT = self.MARKET_IMPACT_US
            self.REGULATORY_FEES = self.REGULATORY_FEES_US
            logger.info(f"Risk model initialized for US market (currency: {self.currency})")
        
        # Allow custom cost assumptions
        if custom_assumptions:
            for key, value in custom_assumptions.items():
                if hasattr(self, key.upper()):
                    setattr(self, key.upper(), value)
                    logger.info(f"Custom assumption: {key} = {value}")
    
    def adjust_expected_return(
        self,
        raw_expected_return: float,
        num_roundtrips: int = 1
    ) -> float:
        """
        Discount expected returns by pessimistic cost estimates.
        
        Only take trades that are profitable AFTER all costs.
        
        Args:
            raw_expected_return: Expected return before costs (as decimal, e.g., 0.015 = 1.5%)
            num_roundtrips: Number of round-trip trades (entry + exit = 1 roundtrip)
            
        Returns:
            Adjusted expected return after costs. Returns 0 if below hurdle rate.
        """
        # Calculate total cost per round trip
        total_cost_per_trip = (
            self.ASSUMED_SLIPPAGE * 2 +  # Entry + Exit
            self.ASSUMED_SPREAD * 2 +    # Bid-ask on both sides
            self.MARKET_IMPACT * 2 +     # Impact on entry and exit
            self.REGULATORY_FEES * 2     # Fees on both sides
        )
        
        # Total drag on returns
        cost_drag = total_cost_per_trip * num_roundtrips
        
        # Adjusted return
        adjusted_return = raw_expected_return - cost_drag
        
        # Apply hurdle rate filter
        if adjusted_return < self.HURDLE_RATE:
            logger.debug(
                f"Trade rejected: adjusted return {adjusted_return:.4f} "
                f"below hurdle rate {self.HURDLE_RATE:.4f}"
            )
            return 0.0
        
        logger.debug(
            f"Expected return: {raw_expected_return:.4f} -> "
            f"{adjusted_return:.4f} (after {cost_drag:.4f} cost drag)"
        )
        
        return adjusted_return
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss_price: float,
        confidence: float = 1.0,
        volatility_adjustment: float = 1.0
    ) -> Tuple[int, RiskParameters]:
        """
        Calculate safe position size based on risk limits.
        
        Uses multiple constraints to ensure conservative sizing:
        1. Max risk per trade (1% of account)
        2. Max portfolio exposure (5% of account)
        3. Volatility adjustment (reduce size in volatile conditions)
        4. Confidence scaling (reduce size for low-confidence trades)
        
        Args:
            entry_price: Intended entry price
            stop_loss_price: Stop loss price
            confidence: Confidence score 0-1 (scales position size)
            volatility_adjustment: Volatility multiplier (>1 = reduce size)
            
        Returns:
            Tuple of (position_size_shares, RiskParameters)
        """
        # 1. Calculate stop distance
        stop_distance = abs(entry_price - stop_loss_price)
        stop_distance_pct = stop_distance / entry_price
        
        # Ensure stop is meaningful (at least 0.5%)
        if stop_distance_pct < 0.005:
            logger.warning(
                f"Stop loss too tight ({stop_distance_pct:.4f}), "
                f"adjusting to minimum 0.5%"
            )
            stop_distance = entry_price * 0.005
            stop_loss_price = entry_price - stop_distance
        
        # 2. Position size by max risk (1% account risk)
        max_loss_amount = self.account_balance * self.MAX_RISK_PER_TRADE_PCT
        shares_by_risk = int(max_loss_amount / stop_distance)
        
        # 3. Position size by max portfolio exposure (5% of account)
        max_capital_allocation = self.account_balance * self.MAX_POSITION_SIZE_PCT
        shares_by_capital = int(max_capital_allocation / entry_price)
        
        # 4. Take the more conservative limit
        base_shares = min(shares_by_risk, shares_by_capital)
        
        # 5. Apply confidence scaling
        confidence_scaled_shares = int(base_shares * confidence)
        
        # 6. Apply volatility adjustment (reduce size in volatile markets)
        final_shares = int(confidence_scaled_shares / volatility_adjustment)
        
        # 7. Minimum position check (avoid micro positions <0.1% of account)
        min_position_value = self.account_balance * 0.001
        if final_shares * entry_price < min_position_value:
            logger.warning(
                f"Position too small (${final_shares * entry_price:.2f}), "
                f"setting to 0"
            )
            final_shares = 0
        
        # 8. Calculate risk parameters
        position_value = final_shares * entry_price
        portfolio_exposure = position_value / self.account_balance
        
        # Assume 2:1 risk-reward ratio
        risk_amount = final_shares * stop_distance
        reward_amount = risk_amount * 2
        take_profit_price = entry_price + (stop_distance * 2)
        
        risk_params = RiskParameters(
            max_position_size=final_shares,
            stop_loss_price=round(stop_loss_price, 4),
            take_profit_price=round(take_profit_price, 4),
            max_loss_amount=round(risk_amount, 2),
            expected_profit=round(reward_amount, 2),
            risk_reward_ratio=2.0,
            position_value=round(position_value, 2),
            portfolio_exposure_pct=round(portfolio_exposure * 100, 2)
        )
        
        logger.info(
            f"Position sizing: {final_shares} shares @ ${entry_price:.2f} "
            f"(${position_value:.2f}, {portfolio_exposure*100:.2f}% exposure)"
        )
        
        return final_shares, risk_params
    
    def validate_trade(
        self,
        expected_return: float,
        position_size: int,
        entry_price: float,
        stop_loss_price: float
    ) -> Tuple[bool, str]:
        """
        Validate if a trade meets all risk criteria.
        
        Args:
            expected_return: Expected return after costs
            position_size: Number of shares
            entry_price: Entry price
            stop_loss_price: Stop loss price
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # 1. Check hurdle rate
        if expected_return < self.HURDLE_RATE:
            return False, f"Below hurdle rate ({expected_return:.4f} < {self.HURDLE_RATE:.4f})"
        
        # 2. Check position size
        position_value = position_size * entry_price
        exposure = position_value / self.account_balance
        
        if exposure > self.MAX_POSITION_SIZE_PCT:
            return False, f"Exceeds max exposure ({exposure:.2%} > {self.MAX_POSITION_SIZE_PCT:.2%})"
        
        # 3. Check risk amount
        stop_distance = abs(entry_price - stop_loss_price)
        risk_amount = position_size * stop_distance
        risk_pct = risk_amount / self.account_balance
        
        if risk_pct > self.MAX_RISK_PER_TRADE_PCT:
            return False, f"Exceeds max risk ({risk_pct:.2%} > {self.MAX_RISK_PER_TRADE_PCT:.2%})"
        
        # 4. All checks passed
        return True, "Trade validated"
    
    def update_account_balance(self, new_balance: float):
        """Update account balance for position sizing calculations"""
        logger.info(f"Account balance updated: ${self.account_balance:.2f} -> ${new_balance:.2f}")
        self.account_balance = new_balance
    
    def get_risk_summary(self) -> Dict:
        """Get summary of current risk parameters"""
        return {
            "account_balance": self.account_balance,
            "max_position_value": self.account_balance * self.MAX_POSITION_SIZE_PCT,
            "max_risk_per_trade": self.account_balance * self.MAX_RISK_PER_TRADE_PCT,
            "hurdle_rate_pct": self.HURDLE_RATE * 100,
            "assumed_slippage_pct": self.ASSUMED_SLIPPAGE * 100,
            "assumed_spread_pct": self.ASSUMED_SPREAD * 100,
            "total_cost_per_roundtrip_pct": (
                (self.ASSUMED_SLIPPAGE + self.ASSUMED_SPREAD + 
                 self.MARKET_IMPACT + self.REGULATORY_FEES) * 2 * 100
            )
        }
