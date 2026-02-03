"""
Unit tests for SignalSynchronizer module

Tests temporal alignment, staleness detection, and window-based synchronization.
"""

import unittest
from datetime import datetime, timedelta
from sentinel.signal_synchronizer import TimestampedSignal, SignalSynchronizer


class TestTimestampedSignal(unittest.TestCase):
    """Test TimestampedSignal dataclass"""
    
    def test_signal_creation(self):
        """Test basic signal creation"""
        signal = TimestampedSignal(
            signal_type="PRICE",
            value=150.5,
            event_time=datetime.utcnow()
        )
        
        self.assertEqual(signal.signal_type, "PRICE")
        self.assertEqual(signal.value, 150.5)
        self.assertFalse(signal.is_stale)
    
    def test_staleness_detection(self):
        """Test that stale signals are detected"""
        old_time = datetime.utcnow() - timedelta(minutes=10)
        
        signal = TimestampedSignal(
            signal_type="NEWS",
            value=75.0,
            event_time=old_time,
            staleness_budget=timedelta(minutes=5)
        )
        
        self.assertTrue(signal.is_stale)
    
    def test_age_calculation(self):
        """Test signal age calculation"""
        event_time = datetime.utcnow() - timedelta(seconds=30)
        
        signal = TimestampedSignal(
            signal_type="TECHNICAL",
            value=50.0,
            event_time=event_time
        )
        
        # Age should be approximately 30 seconds
        self.assertGreater(signal.age_seconds, 29)
        self.assertLess(signal.age_seconds, 35)


class TestSignalSynchronizer(unittest.TestCase):
    """Test SignalSynchronizer class"""
    
    def setUp(self):
        """Set up test synchronizer"""
        self.sync = SignalSynchronizer(
            window_size=timedelta(minutes=5),
            max_buffer_size=100
        )
    
    def test_add_signal(self):
        """Test adding signals to buffer"""
        signal = TimestampedSignal(
            signal_type="PRICE",
            value=150.0,
            event_time=datetime.utcnow()
        )
        
        result = self.sync.add_signal(signal)
        self.assertTrue(result)
        
        metrics = self.sync.get_metrics()
        self.assertEqual(metrics["signals_received"], 1)
    
    def test_reject_stale_signal(self):
        """Test that stale signals are rejected"""
        old_time = datetime.utcnow() - timedelta(minutes=10)
        
        stale_signal = TimestampedSignal(
            signal_type="NEWS",
            value=80.0,
            event_time=old_time,
            staleness_budget=timedelta(minutes=5)
        )
        
        result = self.sync.add_signal(stale_signal)
        self.assertFalse(result)
        
        metrics = self.sync.get_metrics()
        self.assertEqual(metrics["signals_dropped"], 1)
    
    def test_window_synchronization(self):
        """Test that signals are synchronized to windows"""
        now = datetime.utcnow()
        
        # Add multiple signals in the same window
        price_signal = TimestampedSignal("PRICE", 150.0, now)
        news_signal = TimestampedSignal("NEWS", 75.0, now)
        
        self.sync.add_signal(price_signal)
        self.sync.add_signal(news_signal)
        
        # Get synchronized window
        window = self.sync.get_synchronized_window(
            required_types=["PRICE", "NEWS"]
        )
        
        self.assertEqual(window["status"], "READY")
        self.assertEqual(len(window["signals"]), 2)
        self.assertTrue(window["completeness"]["PRICE"])
        self.assertTrue(window["completeness"]["NEWS"])
    
    def test_incomplete_window(self):
        """Test that incomplete windows return WAIT status"""
        now = datetime.utcnow()
        
        # Only add PRICE signal
        price_signal = TimestampedSignal("PRICE", 150.0, now)
        self.sync.add_signal(price_signal)
        
        # Request window with both PRICE and NEWS
        window = self.sync.get_synchronized_window(
            required_types=["PRICE", "NEWS"]
        )
        
        self.assertEqual(window["status"], "WAIT")
        self.assertIn("NEWS", window["reason"])
    
    def test_get_latest_signal(self):
        """Test retrieving latest signal of a type"""
        now = datetime.utcnow()
        
        # Add multiple PRICE signals
        signal1 = TimestampedSignal("PRICE", 150.0, now - timedelta(seconds=10))
        signal2 = TimestampedSignal("PRICE", 151.0, now)
        
        self.sync.add_signal(signal1)
        self.sync.add_signal(signal2)
        
        latest = self.sync.get_latest_signal("PRICE")
        
        self.assertIsNotNone(latest)
        self.assertEqual(latest.value, 151.0)
    
    def test_buffer_cleanup(self):
        """Test that stale signals are cleaned up"""
        old_time = datetime.utcnow() - timedelta(minutes=10)
        now = datetime.utcnow()
        
        # Add old signal with short staleness budget
        old_signal = TimestampedSignal(
            "PRICE", 
            150.0, 
            old_time,
            staleness_budget=timedelta(minutes=1)
        )
        
        # Add fresh signal
        fresh_signal = TimestampedSignal("NEWS", 75.0, now)
        
        self.sync.add_signal(old_signal)
        self.sync.add_signal(fresh_signal)
        
        # Trigger cleanup
        self.sync._cleanup_stale_signals()
        
        # Only fresh signal should remain
        metrics = self.sync.get_metrics()
        self.assertEqual(metrics["current_buffer_size"], 1)


if __name__ == "__main__":
    unittest.main()
