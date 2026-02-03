"""
Unit tests for ConservativeRiskModel module

Tests position sizing, cost adjustments, and trade validation.
"""

import unittest
from sentinel.risk_model import ConservativeRiskModel, RiskParameters


class TestConservativeRiskModel(unittest.TestCase):
    """Test ConservativeRiskModel class"""
    
    def setUp(self):
        """Set up test risk model"""
        self.model = ConservativeRiskModel(account_balance=10000.0)
    
    def test_expected_return_adjustment(self):
        """Test that expected returns are adjusted for costs"""
        raw_return = 0.015  # 1.5% expected
        
        adjusted = self.model.adjust_expected_return(raw_return, num_roundtrips=1)
        
        # Adjusted should be less than raw due to costs
        self.assertLess(adjusted, raw_return)
        self.assertGreater(adjusted, 0)  # Should still be positive
    
    def test_hurdle_rate_filter(self):
        """Test that trades below hurdle rate are rejected"""
        low_return = 0.003  # 0.3% - below 0.5% hurdle
        
        adjusted = self.model.adjust_expected_return(low_return)
        
        # Should return 0 (rejected)
        self.assertEqual(adjusted, 0.0)
    
    def test_position_sizing_by_risk(self):
        """Test position sizing based on risk limits"""
        entry_price = 100.0
        stop_loss = 98.0  # 2% stop
        
        shares, risk_params = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            confidence=1.0
        )
        
        self.assertGreater(shares, 0)
        self.assertIsInstance(risk_params, RiskParameters)
        
        # Max risk should be ~1% of account
        max_risk_pct = risk_params.max_loss_amount / self.model.account_balance
        self.assertLessEqual(max_risk_pct, 0.011)  # Allow small rounding
    
    def test_position_sizing_by_exposure(self):
        """Test that position size respects max exposure limit"""
        entry_price = 100.0
        stop_loss = 99.0  # Very tight stop
        
        shares, risk_params = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            confidence=1.0
        )
        
        # Position value should not exceed 5% of account
        exposure_pct = risk_params.portfolio_exposure_pct
        self.assertLessEqual(exposure_pct, 5.1)  # Allow small rounding
    
    def test_confidence_scaling(self):
        """Test that confidence scales position size"""
        entry_price = 100.0
        stop_loss = 98.0
        
        # High confidence
        shares_high, _ = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            confidence=1.0
        )
        
        # Low confidence
        shares_low, _ = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            confidence=0.5
        )
        
        # Low confidence should result in smaller position
        self.assertLess(shares_low, shares_high)
    
    def test_volatility_adjustment(self):
        """Test that volatility reduces position size"""
        entry_price = 100.0
        stop_loss = 98.0
        
        # Normal volatility
        shares_normal, _ = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            volatility_adjustment=1.0
        )
        
        # High volatility
        shares_volatile, _ = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            volatility_adjustment=2.0
        )
        
        # High volatility should reduce position size
        self.assertLess(shares_volatile, shares_normal)
    
    def test_minimum_position_filter(self):
        """Test that micro positions are rejected"""
        entry_price = 1000.0  # High price
        stop_loss = 998.0
        
        shares, _ = self.model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss,
            confidence=0.01  # Very low confidence
        )
        
        # Should return 0 shares if position too small
        position_value = shares * entry_price
        if position_value > 0:
            self.assertGreater(position_value, self.model.account_balance * 0.001)
    
    def test_trade_validation_pass(self):
        """Test that valid trades pass validation"""
        is_valid, reason = self.model.validate_trade(
            expected_return=0.01,  # 1% expected
            position_size=3,  # Small position (3 shares * $100 = $300, 3% of $10k account)
            entry_price=100.0,
            stop_loss_price=98.0
        )
        
        self.assertTrue(is_valid)
        self.assertIn("validated", reason.lower())
    
    def test_trade_validation_fail_hurdle(self):
        """Test that trades below hurdle rate fail validation"""
        is_valid, reason = self.model.validate_trade(
            expected_return=0.003,  # 0.3% - below hurdle
            position_size=10,
            entry_price=100.0,
            stop_loss_price=98.0
        )
        
        self.assertFalse(is_valid)
        self.assertIn("hurdle", reason.lower())
    
    def test_trade_validation_fail_exposure(self):
        """Test that oversized positions fail validation"""
        is_valid, reason = self.model.validate_trade(
            expected_return=0.01,
            position_size=100,  # Large position
            entry_price=100.0,
            stop_loss_price=98.0
        )
        
        self.assertFalse(is_valid)
        self.assertIn("exposure", reason.lower())
    
    def test_account_balance_update(self):
        """Test updating account balance"""
        new_balance = 15000.0
        self.model.update_account_balance(new_balance)
        
        self.assertEqual(self.model.account_balance, new_balance)
    
    def test_risk_summary(self):
        """Test risk summary generation"""
        summary = self.model.get_risk_summary()
        
        self.assertIn("account_balance", summary)
        self.assertIn("max_position_value", summary)
        self.assertIn("hurdle_rate_pct", summary)
        self.assertEqual(summary["account_balance"], 10000.0)
    
    def test_custom_assumptions(self):
        """Test custom cost assumptions"""
        custom_model = ConservativeRiskModel(
            account_balance=10000.0,
            custom_assumptions={
                "assumed_slippage": 0.005,  # Higher slippage
                "hurdle_rate": 0.01  # Higher hurdle
            }
        )
        
        self.assertEqual(custom_model.ASSUMED_SLIPPAGE, 0.005)
        self.assertEqual(custom_model.HURDLE_RATE, 0.01)


if __name__ == "__main__":
    unittest.main()
