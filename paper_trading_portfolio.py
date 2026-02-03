"""
Paper Trading Portfolio Manager

Simulates a virtual trading portfolio for paper trading:
- Track positions and cash balance
- Execute simulated orders
- Calculate P&L
- Persist state across sessions
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import streamlit as st


@dataclass
class Position:
    """Represents a stock position."""
    symbol: str
    quantity: int
    entry_price: float
    entry_date: str
    current_price: float = 0.0
    
    @property
    def market_value(self) -> float:
        """Current market value of position."""
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> float:
        """Total cost basis."""
        return self.quantity * self.entry_price
    
    @property
    def pnl(self) -> float:
        """Unrealized P&L."""
        return self.market_value - self.cost_basis
    
    @property
    def pnl_pct(self) -> float:
        """Unrealized P&L percentage."""
        return (self.pnl / self.cost_basis * 100) if self.cost_basis > 0 else 0


@dataclass
class Order:
    """Represents a trade order."""
    symbol: str
    side: str  # BUY or SELL
    quantity: int
    price: float
    timestamp: str
    order_type: str = "MARKET"
    status: str = "FILLED"


class PaperTradingPortfolio:
    """Manages paper trading portfolio."""
    
    def __init__(self, starting_cash: float = 100000.0):
        """
        Initialize paper trading portfolio.
        
        Args:
            starting_cash: Starting cash balance in INR
        """
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.closed_trades: List[Dict] = []
        
        # Load from session state if available
        self._load_from_session()
    
    def _load_from_session(self):
        """Load portfolio from Streamlit session state."""
        if 'paper_portfolio' in st.session_state:
            data = st.session_state.paper_portfolio
            self.cash = data.get('cash', self.starting_cash)
            self.starting_cash = data.get('starting_cash', self.starting_cash)
            
            # Load positions
            for symbol, pos_data in data.get('positions', {}).items():
                self.positions[symbol] = Position(**pos_data)
            
            # Load orders
            for order_data in data.get('orders', []):
                self.orders.append(Order(**order_data))
            
            # Load closed trades
            self.closed_trades = data.get('closed_trades', [])
    
    def _save_to_session(self):
        """Save portfolio to Streamlit session state."""
        st.session_state.paper_portfolio = {
            'cash': self.cash,
            'starting_cash': self.starting_cash,
            'positions': {symbol: asdict(pos) for symbol, pos in self.positions.items()},
            'orders': [asdict(order) for order in self.orders],
            'closed_trades': self.closed_trades
        }
    
    def execute_order(self, symbol: str, side: str, quantity: int, price: float) -> bool:
        """
        Execute a simulated order.
        
        Args:
            symbol: Stock symbol
            side: BUY or SELL
            quantity: Number of shares
            price: Execution price
            
        Returns:
            True if order executed successfully
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            if side == "BUY":
                total_cost = quantity * price * 1.001  # Add 0.1% brokerage
                
                if total_cost > self.cash:
                    return False  # Insufficient funds
                
                # Deduct cash
                self.cash -= total_cost
                
                # Add or update position
                if symbol in self.positions:
                    # Average up
                    pos = self.positions[symbol]
                    total_qty = pos.quantity + quantity
                    total_cost_basis = pos.cost_basis + (quantity * price)
                    avg_price = total_cost_basis / total_qty
                    
                    pos.quantity = total_qty
                    pos.entry_price = avg_price
                else:
                    self.positions[symbol] = Position(
                        symbol=symbol,
                        quantity=quantity,
                        entry_price=price,
                        entry_date=timestamp,
                        current_price=price
                    )
            
            elif side == "SELL":
                if symbol not in self.positions:
                    return False  # No position to sell
                
                pos = self.positions[symbol]
                
                if quantity > pos.quantity:
                    return False  # Insufficient shares
                
                # Calculate P&L for this sale
                sale_proceeds = quantity * price * 0.999  # Deduct 0.1% brokerage
                cost_basis = quantity * pos.entry_price
                realized_pnl = sale_proceeds - cost_basis
                
                # Add to cash
                self.cash += sale_proceeds
                
                # Record closed trade
                self.closed_trades.append({
                    'symbol': symbol,
                    'quantity': quantity,
                    'entry_price': pos.entry_price,
                    'exit_price': price,
                    'pnl': realized_pnl,
                    'pnl_pct': (realized_pnl / cost_basis * 100) if cost_basis > 0 else 0,
                    'exit_date': timestamp
                })
                
                # Update or remove position
                if quantity == pos.quantity:
                    del self.positions[symbol]
                else:
                    pos.quantity -= quantity
            
            # Record order
            order = Order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                timestamp=timestamp,
                order_type="MARKET",
                status="FILLED"
            )
            self.orders.append(order)
            
            # Save state
            self._save_to_session()
            
            return True
            
        except Exception as e:
            print(f"Order execution error: {e}")
            return False
    
    def update_prices(self, prices: Dict[str, float]):
        """
        Update current prices for positions.
        
        Args:
            prices: Dict of symbol -> current price
        """
        for symbol, pos in self.positions.items():
            if symbol in prices:
                pos.current_price = prices[symbol]
        
        self._save_to_session()
    
    def get_portfolio_value(self) -> float:
        """Get total portfolio value (cash + positions)."""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value
    
    def get_total_pnl(self) -> float:
        """Get total unrealized P&L."""
        return sum(pos.pnl for pos in self.positions.values())
    
    def get_realized_pnl(self) -> float:
        """Get total realized P&L from closed trades."""
        return sum(trade['pnl'] for trade in self.closed_trades)
    
    def get_daily_pnl(self) -> float:
        """Get today's P&L (simplified - just unrealized for now)."""
        return self.get_total_pnl()
    
    def reset_portfolio(self, starting_cash: float = 100000.0):
        """Reset portfolio to starting state."""
        self.starting_cash = starting_cash
        self.cash = starting_cash
        self.positions = {}
        self.orders = []
        self.closed_trades = []
        self._save_to_session()
    
    def get_stats(self) -> Dict:
        """Get portfolio statistics."""
        total_value = self.get_portfolio_value()
        total_pnl = total_value - self.starting_cash
        total_pnl_pct = (total_pnl / self.starting_cash * 100) if self.starting_cash > 0 else 0
        
        # Win rate from closed trades
        if self.closed_trades:
            winning_trades = len([t for t in self.closed_trades if t['pnl'] > 0])
            win_rate = (winning_trades / len(self.closed_trades) * 100)
        else:
            win_rate = 0.0
        
        return {
            'portfolio_value': total_value,
            'cash': self.cash,
            'positions_value': total_value - self.cash,
            'total_pnl': total_pnl,
            'total_pnl_pct': total_pnl_pct,
            'unrealized_pnl': self.get_total_pnl(),
            'realized_pnl': self.get_realized_pnl(),
            'positions_count': len(self.positions),
            'total_trades': len(self.orders),
            'win_rate': win_rate
        }
