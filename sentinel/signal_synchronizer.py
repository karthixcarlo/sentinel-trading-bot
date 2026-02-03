"""
Signal Synchronization Module

Handles temporal alignment of signals from different sources (price data, news, etc.)
to ensure all signals are synchronized to common time windows before decision-making.

This solves the "Data Consistency Gap" problem where yfinance (1min delayed) and
web scraping (real-time) have temporal mismatches.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Literal
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimestampedSignal:
    """
    A signal with temporal metadata for synchronization.
    
    Every signal carries its own event time to enable proper temporal alignment
    across different data sources with varying latencies.
    
    Attributes:
        signal_type: Type of signal (e.g., "PRICE", "NEWS", "TECHNICAL")
        value: Numerical value or score of the signal
        event_time: When the event actually happened (source timestamp)
        processing_time: When we received/processed it (system timestamp)
        staleness_budget: Maximum acceptable delay before signal is considered stale
        metadata: Additional context (e.g., source, confidence, raw data)
    """
    signal_type: str
    value: float
    event_time: datetime
    processing_time: datetime = field(default_factory=datetime.utcnow)
    staleness_budget: timedelta = field(default=timedelta(minutes=5))
    metadata: Dict = field(default_factory=dict)
    
    @property
    def is_stale(self) -> bool:
        """Check if signal has exceeded its staleness budget"""
        age = datetime.utcnow() - self.event_time
        return age > self.staleness_budget
    
    @property
    def age_seconds(self) -> float:
        """Get signal age in seconds"""
        return (datetime.utcnow() - self.event_time).total_seconds()
    
    def __repr__(self) -> str:
        return (
            f"TimestampedSignal(type={self.signal_type}, "
            f"value={self.value:.4f}, "
            f"age={self.age_seconds:.1f}s, "
            f"stale={self.is_stale})"
        )


class SignalSynchronizer:
    """
    Aligns signals from different sources to common time windows.
    
    This class buffers incoming signals and only releases them when all required
    signal types are present within the same temporal window, ensuring synchronized
    decision-making.
    
    Example:
        >>> sync = SignalSynchronizer(window_size=timedelta(minutes=5))
        >>> sync.add_signal(TimestampedSignal("PRICE", 150.5, datetime.utcnow()))
        >>> sync.add_signal(TimestampedSignal("NEWS", 75.0, datetime.utcnow()))
        >>> window = sync.get_synchronized_window(required_types=["PRICE", "NEWS"])
        >>> if window["status"] == "READY":
        ...     signals = window["signals"]
    """
    
    def __init__(
        self,
        window_size: timedelta = timedelta(minutes=5),
        max_buffer_size: int = 1000,
        cleanup_interval: int = 10
    ):
        """
        Initialize the signal synchronizer.
        
        Args:
            window_size: Size of temporal windows for alignment
            max_buffer_size: Maximum signals to buffer (prevents memory bloat)
            cleanup_interval: Clean stale signals every N additions
        """
        self.window_size = window_size
        self.max_buffer_size = max_buffer_size
        self.cleanup_interval = cleanup_interval
        
        # Buffer: {window_key: [signals]}
        self.signal_buffer: Dict[str, List[TimestampedSignal]] = defaultdict(list)
        
        # Metrics
        self.signals_received = 0
        self.signals_dropped = 0
        self.windows_completed = 0
        
    def _window_key(self, timestamp: datetime) -> str:
        """
        Generate a window key for a given timestamp.
        
        Windows are aligned to fixed intervals (e.g., :00, :05, :10 for 5-min windows)
        to ensure consistent bucketing across different signal sources.
        """
        # Align to window boundaries
        epoch = datetime(1970, 1, 1)
        seconds_since_epoch = (timestamp - epoch).total_seconds()
        window_seconds = self.window_size.total_seconds()
        
        # Round down to nearest window boundary
        window_start = int(seconds_since_epoch // window_seconds) * window_seconds
        
        return f"window_{int(window_start)}"
    
    def add_signal(self, signal: TimestampedSignal) -> bool:
        """
        Add a signal to the buffer.
        
        Args:
            signal: The timestamped signal to add
            
        Returns:
            True if signal was added, False if rejected (stale or buffer full)
        """
        # Reject stale signals immediately
        if signal.is_stale:
            logger.warning(f"Rejected stale signal: {signal}")
            self.signals_dropped += 1
            return False
        
        # Check buffer size
        total_buffered = sum(len(signals) for signals in self.signal_buffer.values())
        if total_buffered >= self.max_buffer_size:
            logger.warning(f"Signal buffer full ({total_buffered} signals), dropping oldest window")
            self._cleanup_oldest_window()
        
        # Add to appropriate window
        window_key = self._window_key(signal.event_time)
        self.signal_buffer[window_key].append(signal)
        self.signals_received += 1
        
        # Periodic cleanup
        if self.signals_received % self.cleanup_interval == 0:
            self._cleanup_stale_signals()
        
        logger.debug(f"Added signal to {window_key}: {signal}")
        return True
    
    def get_synchronized_window(
        self,
        required_types: Optional[List[str]] = None,
        window_offset: int = 0
    ) -> Dict:
        """
        Get a synchronized window of signals.
        
        Args:
            required_types: List of signal types that must be present (e.g., ["PRICE", "NEWS"])
                          If None, returns all signals in current window
            window_offset: Offset from current window (0=current, -1=previous, etc.)
            
        Returns:
            Dictionary with:
                - status: "READY" | "WAIT" | "STALE"
                - signals: List of signals (if READY)
                - window: Window key
                - reason: Explanation (if not READY)
                - completeness: Dict of signal type presence
        """
        # Determine target window
        target_time = datetime.utcnow() + (window_offset * self.window_size)
        current_window = self._window_key(target_time)
        
        aligned_signals = self.signal_buffer.get(current_window, [])
        
        # Check for stale signals
        fresh_signals = [s for s in aligned_signals if not s.is_stale]
        if len(fresh_signals) < len(aligned_signals):
            logger.warning(f"Removed {len(aligned_signals) - len(fresh_signals)} stale signals from window")
        
        # Analyze signal completeness
        signal_types_present = set(s.signal_type for s in fresh_signals)
        completeness = {
            sig_type: sig_type in signal_types_present
            for sig_type in (required_types or [])
        }
        
        # Check if all required types are present
        if required_types:
            missing_types = [t for t in required_types if t not in signal_types_present]
            
            if missing_types:
                return {
                    "status": "WAIT",
                    "signals": [],
                    "window": current_window,
                    "reason": f"Missing signal types: {missing_types}",
                    "completeness": completeness,
                    "available_types": list(signal_types_present)
                }
        
        # Check if window has any signals
        if not fresh_signals:
            return {
                "status": "WAIT",
                "signals": [],
                "window": current_window,
                "reason": "No signals in current window",
                "completeness": completeness,
                "available_types": []
            }
        
        # Success - window is ready
        self.windows_completed += 1
        return {
            "status": "READY",
            "signals": fresh_signals,
            "window": current_window,
            "completeness": completeness,
            "signal_count": len(fresh_signals),
            "window_start": target_time - self.window_size,
            "window_end": target_time
        }
    
    def get_latest_signal(self, signal_type: str) -> Optional[TimestampedSignal]:
        """
        Get the most recent signal of a specific type across all windows.
        
        Args:
            signal_type: Type of signal to retrieve
            
        Returns:
            Most recent signal of that type, or None if not found
        """
        all_signals = [
            signal
            for signals in self.signal_buffer.values()
            for signal in signals
            if signal.signal_type == signal_type and not signal.is_stale
        ]
        
        if not all_signals:
            return None
        
        # Return most recent by event_time
        return max(all_signals, key=lambda s: s.event_time)
    
    def _cleanup_stale_signals(self):
        """Remove stale signals from all windows"""
        removed_count = 0
        
        for window_key in list(self.signal_buffer.keys()):
            original_count = len(self.signal_buffer[window_key])
            self.signal_buffer[window_key] = [
                s for s in self.signal_buffer[window_key]
                if not s.is_stale
            ]
            removed_count += original_count - len(self.signal_buffer[window_key])
            
            # Remove empty windows
            if not self.signal_buffer[window_key]:
                del self.signal_buffer[window_key]
        
        if removed_count > 0:
            logger.debug(f"Cleaned up {removed_count} stale signals")
    
    def _cleanup_oldest_window(self):
        """Remove the oldest window to free up buffer space"""
        if not self.signal_buffer:
            return
        
        oldest_window = min(self.signal_buffer.keys())
        removed_count = len(self.signal_buffer[oldest_window])
        del self.signal_buffer[oldest_window]
        
        logger.debug(f"Removed oldest window {oldest_window} ({removed_count} signals)")
    
    def get_metrics(self) -> Dict:
        """Get synchronizer performance metrics"""
        total_buffered = sum(len(signals) for signals in self.signal_buffer.values())
        
        return {
            "signals_received": self.signals_received,
            "signals_dropped": self.signals_dropped,
            "windows_completed": self.windows_completed,
            "current_buffer_size": total_buffered,
            "active_windows": len(self.signal_buffer),
            "drop_rate": self.signals_dropped / max(self.signals_received, 1)
        }
    
    def clear(self):
        """Clear all buffered signals"""
        self.signal_buffer.clear()
        logger.info("Signal buffer cleared")
