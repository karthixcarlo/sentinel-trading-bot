"""
Executioner Agent

Performs final validation and executes trades with slippage simulation
and circuit breaker integration.
"""

import logging
from typing import Dict, List, Optional

from .base_agent import BaseAgent, AgentState
from ..slippage_simulator import SlippageSimulator, MarketCondition

logger = logging.getLogger(__name__)


class ExecutionerAgent(BaseAgent):
    """
    Executioner Agent - Risk-managed trade execution.
    
    Responsibilities:
    - Final validation with circuit breaker
    - Slippage simulation for realistic fills
    - Order execution (paper trading)
    - Post-trade monitoring
    """
    
    def __init__(
        self,
        circuit_breaker=None,
        market_condition: MarketCondition = MarketCondition.NORMAL
    ):
        """
        Initialize Executioner Agent.
        
        Args:
            circuit_breaker: Optional circuit breaker
            market_condition: Current market condition for slippage
        """
        super().__init__(name="Executioner", circuit_breaker=circuit_breaker)
        self.slippage_simulator = SlippageSimulator(condition=market_condition)
    
    async def _execute_impl(self, state: AgentState) -> List[Dict]:
        """
        Execute executioner logic: validate and execute trades.
        
        Args:
            state: Current agent state with analyst recommendations
            
        Returns:
            List of execution results
        """
        execution_results = []
        
        for recommendation in state.analyst_recommendations:
            try:
                # Execute trade
                result = await self._execute_trade(recommendation)
                
                if result:
                    execution_results.append(result)
                    logger.info(
                        f"Executed: {result['status']} {result['ticker']} "
                        f"{result['filled_qty']} @ ${result['avg_fill_price']:.2f}"
                    )
            
            except Exception as e:
                logger.error(f"Failed to execute {recommendation['ticker']}: {e}")
                state.errors.append(f"Execution error for {recommendation['ticker']}: {str(e)}")
        
        logger.info(f"Executioner completed {len(execution_results)} trades")
        
        return execution_results
    
    async def _execute_trade(self, recommendation: Dict) -> Optional[Dict]:
        """
        Execute a single trade with slippage simulation.
        
        Args:
            recommendation: Trade recommendation from analyst
            
        Returns:
            Execution result dictionary or None if failed
        """
        ticker = recommendation["ticker"]
        action = recommendation["action"]
        entry_price = recommendation["entry_price"]
        position_size = recommendation["position_size"]
        
        # Simulate order execution with slippage
        fill_result = self.slippage_simulator.simulate_fill(
            order_type="MARKET",
            side=action,
            intended_price=entry_price,
            size=position_size,
            symbol=ticker
        )
        
        # Check if fill was successful
        if fill_result.filled_qty == 0:
            logger.warning(f"No fill for {ticker} - order rejected")
            return None
        
        # Calculate total cost
        total_cost = fill_result.actual_fill_price * fill_result.filled_qty
        
        # Create execution result
        execution_result = {
            "status": "EXECUTED" if fill_result.is_complete else "PARTIAL",
            "ticker": ticker,
            "action": action,
            "intended_price": entry_price,
            "avg_fill_price": fill_result.actual_fill_price,
            "intended_qty": position_size,
            "filled_qty": fill_result.filled_qty,
            "unfilled_qty": fill_result.unfilled_qty,
            "slippage_pct": fill_result.slippage_pct,
            "slippage_cost": fill_result.slippage_cost,
            "total_cost": round(total_cost, 2),
            "stop_loss": recommendation["stop_loss"],
            "take_profit": recommendation["take_profit"],
            "confidence": recommendation["confidence"],
            "market_condition": fill_result.market_condition.name
        }
        
        return execution_result
    
    def set_market_condition(self, condition: MarketCondition):
        """Update market condition for slippage simulation"""
        self.slippage_simulator.set_condition(condition)
        logger.info(f"Market condition updated to {condition.name}")
