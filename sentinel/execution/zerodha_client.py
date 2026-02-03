"""
Zerodha Kite Connect Client for Paper Trading

Provides async interface to Zerodha Kite Connect API for order execution,
position tracking, and portfolio management on Indian markets (NSE/BSE).
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

from sentinel.indian_market_config import IST

logger = logging.getLogger(__name__)


class ZerodhaClient:
    """
    Zerodha Kite Connect API client for trading Indian stocks.
    
    Features:
    - Order submission (market, limit, SL, SL-M)
    - Position tracking
    - Portfolio monitoring
    - Account information
    - Support for NSE/BSE equity and F&O
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        access_token: Optional[str] = None
    ):
        """
        Initialize Zerodha client.
        
        Args:
            api_key: Zerodha API key
            api_secret: Zerodha API secret
            access_token: Access token (generated from request_token)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        
        # Initialize Kite Connect API
        try:
            from kiteconnect import KiteConnect
            self.kite = KiteConnect(api_key=api_key)
            
            # Set access token if provided
            if access_token:
                self.kite.set_access_token(access_token)
                logger.info("Zerodha client initialized with access token")
            else:
                logger.warning("Zerodha client initialized without access token")
            
        except ImportError:
            logger.error(
                "kiteconnect not installed. Install with: pip install kiteconnect"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Zerodha client: {e}")
            raise
    
    def get_login_url(self) -> str:
        """
        Get login URL for Zerodha authentication.
        
        User must visit this URL, login, and copy the request_token from redirect.
        
        Returns:
            Login URL string
        """
        login_url = self.kite.login_url()
        logger.info(f"Zerodha login URL generated: {login_url}")
        return login_url
    
    async def generate_session(self, request_token: str) -> Dict:
        """
        Generate session and access token from request_token.
        
        Args:
            request_token: Request token from login redirect
            
        Returns:
            Session data including access_token
        """
        loop = asyncio.get_event_loop()
        
        def _generate():
            data = self.kite.generate_session(
                request_token=request_token,
                api_secret=self.api_secret
            )
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            return data
        
        return await loop.run_in_executor(None, _generate)
    
    async def get_profile(self) -> Dict:
        """Get user profile information"""
        loop = asyncio.get_event_loop()
        
        def _get():
            profile = self.kite.profile()
            return {
                "user_id": profile["user_id"],
                "user_name": profile["user_name"],
                "email": profile["email"],
                "broker": profile["broker"],
                "exchanges": profile["exchanges"],
                "products": profile["products"],
                "order_types": profile["order_types"]
            }
        
        return await loop.run_in_executor(None, _get)
    
    async def get_margins(self) -> Dict:
        """Get account margins"""
        loop = asyncio.get_event_loop()
        
        def _get():
            margins = self.kite.margins()
            
            # Extract equity segment margins
            equity = margins.get("equity", {})
            
            return {
                "available_cash": float(equity.get("available", {}).get("cash", 0)),
                "available_margin": float(equity.get("available", {}).get("live_balance", 0)),
                "used_margin": float(equity.get("utilised", {}).get("debits", 0)),
                "net": float(equity.get("net", 0)),
                "currency": "INR"
            }
        
        return await loop.run_in_executor(None, _get)
    
    async def submit_order(
        self,
        symbol: str,
        exchange: str,
        transaction_type: str,
        quantity: int,
        order_type: str = "MARKET",
        product: str = "MIS",  # MIS for intraday, CNC for delivery
        price: Optional[float] = None,
        trigger_price: Optional[float] = None,
        validity: str = "DAY"
    ) -> Dict:
        """
        Submit an order to Zerodha.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            exchange: Exchange ("NSE" or "BSE")
            transaction_type: "BUY" or "SELL"
            quantity: Quantity to trade
            order_type: "MARKET", "LIMIT", "SL", "SL-M"
            product: "MIS" (intraday), "CNC" (delivery), "NRML" (normal F&O)
            price: Limit price (for LIMIT/SL orders)
            trigger_price: Trigger price (for SL/SL-M orders)
            validity: "DAY" or "IOC"
            
        Returns:
            Order information dictionary
        """
        loop = asyncio.get_event_loop()
        
        def _submit():
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=exchange,
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=product,
                order_type=order_type,
                price=price,
                trigger_price=trigger_price,
                validity=validity
            )
            
            logger.info(
                f"Order submitted: {transaction_type} {quantity} {symbol} @ "
                f"{order_type} (Order ID: {order_id})"
            )
            
            return {
                "order_id": order_id,
                "symbol": symbol,
                "exchange": exchange,
                "transaction_type": transaction_type,
                "quantity": quantity,
                "order_type": order_type,
                "product": product,
                "status": "SUBMITTED",
                "timestamp": datetime.now(IST)
            }
        
        return await loop.run_in_executor(None, _submit)
    
    async def get_order(self, order_id: str) -> Dict:
        """Get order status by ID"""
        loop = asyncio.get_event_loop()
        
        def _get():
            orders = self.kite.orders()
            
            # Find order by ID
            for order in orders:
                if order["order_id"] == order_id:
                    return {
                        "order_id": order["order_id"],
                        "symbol": order["tradingsymbol"],
                        "exchange": order["exchange"],
                        "transaction_type": order["transaction_type"],
                        "quantity": order["quantity"],
                        "filled_quantity": order["filled_quantity"],
                        "pending_quantity": order["pending_quantity"],
                        "order_type": order["order_type"],
                        "product": order["product"],
                        "status": order["status"],
                        "average_price": float(order["average_price"]) if order["average_price"] else None,
                        "order_timestamp": order["order_timestamp"],
                        "exchange_timestamp": order["exchange_timestamp"]
                    }
            
            return None
        
        return await loop.run_in_executor(None, _get)
    
    async def get_orders(self) -> List[Dict]:
        """Get all orders for the day"""
        loop = asyncio.get_event_loop()
        
        def _get():
            orders = self.kite.orders()
            return [
                {
                    "order_id": o["order_id"],
                    "symbol": o["tradingsymbol"],
                    "exchange": o["exchange"],
                    "transaction_type": o["transaction_type"],
                    "quantity": o["quantity"],
                    "filled_quantity": o["filled_quantity"],
                    "status": o["status"],
                    "order_type": o["order_type"],
                    "average_price": float(o["average_price"]) if o["average_price"] else None
                }
                for o in orders
            ]
        
        return await loop.run_in_executor(None, _get)
    
    async def get_positions(self) -> Dict[str, List[Dict]]:
        """Get all positions (day and net)"""
        loop = asyncio.get_event_loop()
        
        def _get():
            positions = self.kite.positions()
            
            # Separate day and net positions
            day_positions = [
                {
                    "symbol": p["tradingsymbol"],
                    "exchange": p["exchange"],
                    "quantity": p["quantity"],
                    "buy_quantity": p["buy_quantity"],
                    "sell_quantity": p["sell_quantity"],
                    "average_price": float(p["average_price"]),
                    "last_price": float(p["last_price"]),
                    "pnl": float(p["pnl"]),
                    "product": p["product"]
                }
                for p in positions.get("day", [])
                if p["quantity"] != 0
            ]
            
            net_positions = [
                {
                    "symbol": p["tradingsymbol"],
                    "exchange": p["exchange"],
                    "quantity": p["quantity"],
                    "average_price": float(p["average_price"]),
                    "last_price": float(p["last_price"]),
                    "pnl": float(p["pnl"]),
                    "product": p["product"]
                }
                for p in positions.get("net", [])
                if p["quantity"] != 0
            ]
            
            return {
                "day": day_positions,
                "net": net_positions
            }
        
        return await loop.run_in_executor(None, _get)
    
    async def get_holdings(self) -> List[Dict]:
        """Get all holdings (delivery positions)"""
        loop = asyncio.get_event_loop()
        
        def _get():
            holdings = self.kite.holdings()
            return [
                {
                    "symbol": h["tradingsymbol"],
                    "exchange": h["exchange"],
                    "quantity": h["quantity"],
                    "average_price": float(h["average_price"]),
                    "last_price": float(h["last_price"]),
                    "pnl": float(h["pnl"]),
                    "day_change": float(h["day_change"]),
                    "day_change_percent": float(h["day_change_percentage"])
                }
                for h in holdings
            ]
        
        return await loop.run_in_executor(None, _get)
    
    async def cancel_order(self, order_id: str, variety: str = "regular") -> bool:
        """Cancel an order"""
        loop = asyncio.get_event_loop()
        
        def _cancel():
            try:
                self.kite.cancel_order(
                    variety=variety,
                    order_id=order_id
                )
                logger.info(f"Order {order_id} cancelled")
                return True
            except Exception as e:
                logger.error(f"Failed to cancel order {order_id}: {e}")
                return False
        
        return await loop.run_in_executor(None, _cancel)
    
    async def modify_order(
        self,
        order_id: str,
        quantity: Optional[int] = None,
        price: Optional[float] = None,
        order_type: Optional[str] = None,
        trigger_price: Optional[float] = None,
        variety: str = "regular"
    ) -> bool:
        """Modify an existing order"""
        loop = asyncio.get_event_loop()
        
        def _modify():
            try:
                self.kite.modify_order(
                    variety=variety,
                    order_id=order_id,
                    quantity=quantity,
                    price=price,
                    order_type=order_type,
                    trigger_price=trigger_price
                )
                logger.info(f"Order {order_id} modified")
                return True
            except Exception as e:
                logger.error(f"Failed to modify order {order_id}: {e}")
                return False
        
        return await loop.run_in_executor(None, _modify)
    
    async def get_quote(self, symbol: str, exchange: str) -> Dict:
        """Get live quote for a symbol"""
        loop = asyncio.get_event_loop()
        
        def _get():
            instrument_key = f"{exchange}:{symbol}"
            quotes = self.kite.quote([instrument_key])
            
            if instrument_key in quotes:
                q = quotes[instrument_key]
                return {
                    "symbol": symbol,
                    "exchange": exchange,
                    "last_price": float(q["last_price"]),
                    "open": float(q["ohlc"]["open"]),
                    "high": float(q["ohlc"]["high"]),
                    "low": float(q["ohlc"]["low"]),
                    "close": float(q["ohlc"]["close"]),
                    "volume": int(q["volume"]),
                    "last_traded_time": q["last_trade_time"],
                    "oi": int(q.get("oi", 0)),  # Open interest for F&O
                    "currency": "INR"
                }
            
            return {}
        
        return await loop.run_in_executor(None, _get)
