"""
Unit tests for SlippageSimulator module

Tests realistic fill simulation, slippage calculation, and market impact.
"""

import unittest
from sentinel.slippage_simulator import (
    MarketCondition,
    SlippageSimulator,
    FillResult
)


class TestSlippageSimulator(unittest.TestCase):
    """Test SlippageSimulator class"""
    
    def setUp(self):
        """Set up test simulator with fixed seed for reproducibility"""
        self.simulator = SlippageSimulator(
            condition=MarketCondition.NORMAL,
            seed=42
        )
    
    def test_market_order_fill(self):
        """Test market order simulation"""
        fill = self.simulator.simulate_fill(
            order_type="MARKET",
            side="BUY",
            intended_price=150.0,
            size=100,
            symbol="AAPL"
        )
        
        self.assertIsInstance(fill, FillResult)
        self.assertEqual(fill.symbol, "AAPL")
        self.assertEqual(fill.side, "BUY")
        self.assertGreater(fill.actual_fill_price, fill.intended_price)  # Buys fill higher
        self.assertGreater(fill.filled_qty, 0)
    
    def test_limit_order_fill(self):
        """Test limit order simulation (better execution than market)"""
        fill = self.simulator.simulate_fill(
            order_type="LIMIT",
            side="BUY",
            intended_price=150.0,
            size=100,
            symbol="AAPL"
        )
        
        # Limit orders should have less slippage than market orders
        self.assertIsInstance(fill, FillResult)
        self.assertGreater(fill.slippage_pct, 0)
    
    def test_sell_order_direction(self):
        """Test that sell orders fill lower than intended"""
        fill = self.simulator.simulate_fill(
            order_type="MARKET",
            side="SELL",
            intended_price=150.0,
            size=100,
            symbol="AAPL"
        )
        
        # Sells should fill lower than intended price
        self.assertLess(fill.actual_fill_price, fill.intended_price)
    
    def test_volatile_condition_higher_slippage(self):
        """Test that volatile conditions produce higher slippage"""
        # Normal condition
        normal_sim = SlippageSimulator(condition=MarketCondition.NORMAL, seed=42)
        normal_fill = normal_sim.simulate_fill(
            "MARKET", "BUY", 150.0, 100, "AAPL"
        )
        
        # Volatile condition
        volatile_sim = SlippageSimulator(condition=MarketCondition.VOLATILE, seed=42)
        volatile_fill = volatile_sim.simulate_fill(
            "MARKET", "BUY", 150.0, 100, "AAPL"
        )
        
        # Volatile should have higher slippage on average
        self.assertGreater(volatile_fill.slippage_pct, normal_fill.slippage_pct)
    
    def test_partial_fills(self):
        """Test that partial fills occur in illiquid conditions"""
        illiquid_sim = SlippageSimulator(
            condition=MarketCondition.ILLIQUID,
            enable_partial_fills=True,
            seed=42
        )
        
        # Run multiple fills to test partial fill behavior
        partial_count = 0
        for _ in range(10):
            fill = illiquid_sim.simulate_fill(
                "MARKET", "BUY", 150.0, 100, "AAPL"
            )
            if fill.unfilled_qty > 0:
                partial_count += 1
        
        # At least some fills should be partial in illiquid conditions
        self.assertGreater(partial_count, 0)
    
    def test_size_impact(self):
        """Test that larger orders have more market impact"""
        # Small order
        small_fill = self.simulator.simulate_fill(
            "MARKET", "BUY", 150.0, 100, "AAPL"
        )
        
        # Large order
        large_fill = self.simulator.simulate_fill(
            "MARKET", "BUY", 150.0, 10000, "AAPL"
        )
        
        # Large order should have higher total slippage cost
        self.assertGreater(large_fill.slippage_cost, small_fill.slippage_cost)
    
    def test_cumulative_cost_tracking(self):
        """Test cumulative slippage cost calculation"""
        # Execute multiple fills
        for i in range(5):
            self.simulator.simulate_fill(
                "MARKET", "BUY", 150.0, 100, "AAPL"
            )
        
        cumulative_cost = self.simulator.get_cumulative_slippage_cost()
        
        self.assertGreater(cumulative_cost, 0)
        self.assertEqual(len(self.simulator.fill_log), 5)
    
    def test_statistics(self):
        """Test fill statistics generation"""
        # Create a new simulator without fixed seed for this test
        test_sim = SlippageSimulator(condition=MarketCondition.NORMAL)
        
        # Execute some fills
        for _ in range(10):
            test_sim.simulate_fill(
                "MARKET", "BUY", 150.0, 100, "AAPL"
            )
        
        stats = test_sim.get_statistics()
        
        self.assertEqual(stats["total_fills"], 10)
        self.assertGreater(stats["avg_slippage_pct"], 0)
        self.assertGreater(stats["total_slippage_cost"], 0)
        # In NORMAL conditions, avg fill ratio should be >= 0.95 (95-100% range)
        self.assertGreaterEqual(stats["avg_fill_ratio"], 0.95)
    
    def test_condition_change(self):
        """Test changing market conditions"""
        self.simulator.set_condition(MarketCondition.VOLATILE)
        self.assertEqual(self.simulator.condition, MarketCondition.VOLATILE)
    
    def test_export_fills(self):
        """Test exporting fill log"""
        self.simulator.simulate_fill("MARKET", "BUY", 150.0, 100, "AAPL")
        
        exports = self.simulator.export_fills()
        
        self.assertEqual(len(exports), 1)
        self.assertIn("symbol", exports[0])
        self.assertIn("slippage_pct", exports[0])


if __name__ == "__main__":
    unittest.main()
