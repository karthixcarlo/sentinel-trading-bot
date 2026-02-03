"""
Portfolio Manager

Tracks and manages portfolio state via Alpaca API.
"""

import logging
from typing import Dict, List

from .alpaca_client import AlpacaClient

logger = logging.getLogger(__name__)


class PortfolioManager:
    """
    Portfolio manager using Alpaca API.
    
    Tracks positions, cash, and P&L.
    """
    
    def __init__(self, alpaca_client: AlpacaClient):
        """
        Initialize portfolio manager.
        
        Args:
            alpaca_client: AlpacaClient instance
        """
        self.client = alpaca_client
    
    async def get_summary(self) -> Dict:
        """
        Get portfolio summary.
        
        Returns:
            Dictionary with portfolio metrics
        """
        account = await self.client.get_account()
        
        return {
            "equity": account["equity"],
            "cash": account["cash"],
            "buying_power": account["buying_power"],
            "portfolio_value": account["portfolio_value"],
            "positions_value": account["equity"] - account["cash"],
            "day_pnl": 0.0,  # Would need historical data
            "total_pnl": account["equity"] - 100000.0,  # Assuming $100k starting
            "status": account["status"]
        }
    
    async def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        return await self.client.get_all_positions()
    
    async def get_position(self, symbol: str) -> Dict:
        """Get position for a specific symbol"""
        return await self.client.get_position(symbol)
    
    async def get_cash_balance(self) -> float:
        """Get available cash"""
        account = await self.client.get_account()
        return account["cash"]
    
    async def get_buying_power(self) -> float:
        """Get buying power"""
        account = await self.client.get_account()
        return account["buying_power"]
