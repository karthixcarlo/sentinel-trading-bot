"""
Paper Trading Executor

Executes trades via Alpaca paper trading API, replacing the slippage simulator
with real order execution.
"""

import logging
from typing import Dict, Optional
from datetime import datetime

from .alpaca_client import AlpacaClient

logger = logging.getLogger(__name__)


class PaperTradingExecutor:
    """
    Paper trading executor using Alpaca API.
    
    Replaces slippage simulation with real paper trading orders.
    """
    
    def __init__(self, alpaca_client: AlpacaClient):
        """
        Initialize paper trading executor.
        
        Args:
            alpaca_client: AlpacaClient instance
        """
        self.client = alpaca_client
        self.execution_count = 0
    
    async def execute_trade(self, recommendation: Dict) -> Dict:
        """
        Execute a trade recommendation via Alpaca.
        
        Args:
            recommendation: Trade recommendation from Analyst
            
        Returns:
            Execution result dictionary
        """
        ticker = recommendation["ticker"]
        action = recommendation["action"]
        entry_price = recommendation["entry_price"]
        position_size = recommendation["position_size"]
        
        try:
            # Submit market order to Alpaca
            logger.info(f"Submitting {action} order for {ticker}: {position_size} shares")
            
            order = await self.client.submit_order(
                symbol=ticker,
                qty=position_size,
                side=action.lower(),  # 'buy' or 'sell'
                type="market",
                time_in_force="day"
            )
            
            # Wait a moment for fill (market orders usually fill instantly)
            import asyncio
            await asyncio.sleep(1)
            
            # Get updated order status
            order_status = await self.client.get_order(order["id"])
            
            # Build execution result
            filled_qty = order_status["filled_qty"]
            avg_fill_price = order_status["filled_avg_price"] or entry_price
            
            # Calculate slippage
            slippage_pct = ((avg_fill_price - entry_price) / entry_price * 100) if entry_price else 0
            slippage_cost = (avg_fill_price - entry_price) * filled_qty
            
            result = {
                "status": "EXECUTED" if order_status["status"] == "filled" else "PARTIAL",
                "ticker": ticker,
                "action": action,
                "intended_price": entry_price,
                "avg_fill_price": avg_fill_price,
                "intended_qty": position_size,
                "filled_qty": filled_qty,
                "unfilled_qty": position_size - filled_qty,
                "slippage_pct": slippage_pct,
                "slippage_cost": slippage_cost,
                "total_cost": avg_fill_price * filled_qty,
                "order_id": order["id"],
                "order_status": order_status["status"],
                "stop_loss": recommendation.get("stop_loss"),
                "take_profit": recommendation.get("take_profit"),
                "confidence": recommendation.get("confidence"),
                "execution_time": datetime.utcnow().isoformat()
            }
            
            self.execution_count += 1
            logger.info(f"Order {order['id']} {order_status['status']}: {filled_qty} shares @ ${avg_fill_price:.2f}")
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to execute trade for {ticker}: {e}")
            
            # Return error result
            return {
                "status": "FAILED",
                "ticker": ticker,
                "action": action,
                "error": str(e),
                "intended_qty": position_size,
                "filled_qty": 0
            }
