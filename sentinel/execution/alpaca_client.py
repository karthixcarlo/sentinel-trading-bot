"""
Alpaca API Client for Paper Trading

Provides async interface to Alpaca paper trading API for order execution,
position tracking, and portfolio management.
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class AlpacaClient:
    """
    Alpaca API client for paper trading.
    
    Features:
    - Order submission (market, limit, stop)
    - Position tracking
    - Portfolio monitoring
    - Account information
    """
    
    def __init__(
        self,
        api_key: str,
        secret_key: str,
        base_url: str = "https://paper-api.alpaca.markets",
        paper: bool = True
    ):
        """
        Initialize Alpaca client.
        
        Args:
            api_key: Alpaca API key
            secret_key: Alpaca secret key
            base_url: API base URL (paper or live)
            paper: Whether using paper trading
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.paper = paper
        
        # Initialize Alpaca API
        try:
            from alpaca_trade_api import REST
            self.api = REST(
                key_id=api_key,
                secret_key=secret_key,
                base_url=base_url
            )
            logger.info(f"Alpaca client initialized (paper={paper})")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca client: {e}")
            raise
    
    async def get_account(self) -> Dict:
        """Get account information"""
        loop = asyncio.get_event_loop()
        
        def _get():
            account = self.api.get_account()
            return {
                "equity": float(account.equity),
                "cash": float(account.cash),
                "buying_power": float(account.buying_power),
                "portfolio_value": float(account.portfolio_value),
                "day_trade_count": int(account.daytrade_count),
                "status": account.status
            }
        
        return await loop.run_in_executor(None, _get)
    
    async def submit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        type: str = "market",
        time_in_force: str = "day",
        limit_price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict:
        """
        Submit an order to Alpaca.
        
        Args:
            symbol: Stock symbol
            qty: Quantity to trade
            side: 'buy' or 'sell'
            type: Order type ('market', 'limit', 'stop', 'stop_limit')
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
            limit_price: Limit price (for limit orders)
            stop_price: Stop price (for stop orders)
            
        Returns:
            Order information dictionary
        """
        loop = asyncio.get_event_loop()
        
        def _submit():
            order = self.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type=type,
                time_in_force=time_in_force,
                limit_price=limit_price,
                stop_price=stop_price
            )
            
            return {
                "id": order.id,
                "symbol": order.symbol,
                "qty": int(order.qty),
                "filled_qty": int(order.filled_qty or 0),
                "side": order.side,
                "type": order.type,
                "status": order.status,
                "submitted_at": order.submitted_at,
                "filled_at": order.filled_at,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
            }
        
        return await loop.run_in_executor(None, _submit)
    
    async def get_order(self, order_id: str) -> Dict:
        """Get order status by ID"""
        loop = asyncio.get_event_loop()
        
        def _get():
            order = self.api.get_order(order_id)
            return {
                "id": order.id,
                "symbol": order.symbol,
                "qty": int(order.qty),
                "filled_qty": int(order.filled_qty or 0),
                "side": order.side,
                "type": order.type,
                "status": order.status,
                "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
            }
        
        return await loop.run_in_executor(None, _get)
    
    async def get_position(self, symbol: str) -> Optional[Dict]:
        """Get position for a symbol"""
        loop = asyncio.get_event_loop()
        
        def _get():
            try:
                position = self.api.get_position(symbol)
                return {
                    "symbol": position.symbol,
                    "qty": int(position.qty),
                    "avg_entry_price": float(position.avg_entry_price),
                    "current_price": float(position.current_price),
                    "market_value": float(position.market_value),
                    "cost_basis": float(position.cost_basis),
                    "unrealized_pl": float(position.unrealized_pl),
                    "unrealized_plpc": float(position.unrealized_plpc),
                    "side": position.side
                }
            except Exception as e:
                # Position doesn't exist
                return None
        
        return await loop.run_in_executor(None, _get)
    
    async def get_all_positions(self) -> List[Dict]:
        """Get all open positions"""
        loop = asyncio.get_event_loop()
        
        def _get():
            positions = self.api.list_positions()
            return [
                {
                    "symbol": p.symbol,
                    "qty": int(p.qty),
                    "avg_entry_price": float(p.avg_entry_price),
                    "current_price": float(p.current_price),
                    "market_value": float(p.market_value),
                    "unrealized_pl": float(p.unrealized_pl),
                    "unrealized_plpc": float(p.unrealized_plpc)
                }
                for p in positions
            ]
        
        return await loop.run_in_executor(None, _get)
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        loop = asyncio.get_event_loop()
        
        def _cancel():
            try:
                self.api.cancel_order(order_id)
                return True
            except Exception as e:
                logger.error(f"Failed to cancel order {order_id}: {e}")
                return False
        
        return await loop.run_in_executor(None, _cancel)
    
    async def close_position(self, symbol: str) -> bool:
        """Close a position"""
        loop = asyncio.get_event_loop()
        
        def _close():
            try:
                self.api.close_position(symbol)
                return True
            except Exception as e:
                logger.error(f"Failed to close position {symbol}: {e}")
                return False
        
        return await loop.run_in_executor(None, _close)
