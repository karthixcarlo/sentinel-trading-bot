"""
Circuit Breaker Module

Production-grade circuit breaker with persistent state and exponential backoff recovery.
Prevents cascading failures by blocking operations when error thresholds are exceeded.

State Machine:
- CLOSED (normal): Operations allowed, monitoring for failures
- OPEN (blocking): Operations blocked, waiting for recovery timeout
- HALF_OPEN (testing): Limited operations allowed to test recovery
"""

import asyncio
import json
import time
import logging
from enum import Enum, auto
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Tuple, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class BreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = auto()      # Normal operation, monitoring for failures
    OPEN = auto()        # Blocking all operations due to failures
    HALF_OPEN = auto()   # Testing recovery with limited operations


@dataclass
class BreakerMetrics:
    """Circuit breaker metrics and state"""
    state: str  # BreakerState name
    failure_count: int
    success_count: int
    last_failure_time: float
    last_success_time: float
    recovery_timeout: float
    half_open_calls: int
    state_changes: int
    total_blocked: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BreakerMetrics':
        """Create from dictionary"""
        return cls(**data)


class CircuitBreaker:
    """
    Production-grade circuit breaker with persistence and recovery.
    
    Monitors operation failures and automatically blocks operations when
    failure thresholds are exceeded. Implements exponential backoff for
    recovery attempts.
    
    Example:
        >>> breaker = CircuitBreaker(
        ...     failure_threshold=3,
        ...     recovery_timeout=60.0,
        ...     state_file="./sentinel_state/circuit_breaker.json"
        ... )
        >>> 
        >>> can_execute, reason = await breaker.can_execute()
        >>> if can_execute:
        ...     result = await execute_trade()
        ...     await breaker.record_success()
        ... else:
        ...     logger.warning(f"Blocked: {reason}")
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 1,
        max_recovery_timeout: float = 300.0,
        state_file: str = "./sentinel_state/circuit_breaker.json"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            half_open_max_calls: Max calls allowed in HALF_OPEN state
            max_recovery_timeout: Maximum recovery timeout (caps exponential backoff)
            state_file: Path to persistent state file
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.max_recovery_timeout = max_recovery_timeout
        self.state_file = Path(state_file)
        
        # State
        self.state = BreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = 0.0
        self.half_open_calls = 0
        self.state_changes = 0
        self.total_blocked = 0
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Load persisted state
        self._load_state()
    
    def _load_state(self) -> None:
        """Load persisted state from file"""
        if not self.state_file.exists():
            logger.info("No persisted circuit breaker state found, starting fresh")
            return
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            self.state = BreakerState[data["state"]]
            self.failure_count = data["failure_count"]
            self.success_count = data["success_count"]
            self.last_failure_time = data["last_failure_time"]
            self.last_success_time = data["last_success_time"]
            self.recovery_timeout = data["recovery_timeout"]
            self.half_open_calls = data.get("half_open_calls", 0)
            self.state_changes = data.get("state_changes", 0)
            self.total_blocked = data.get("total_blocked", 0)
            
            logger.info(
                f"Circuit breaker state loaded: {self.state.name} "
                f"(failures={self.failure_count}, timeout={self.recovery_timeout:.0f}s)"
            )
        except Exception as e:
            logger.error(f"Failed to load circuit breaker state: {e}")
    
    def _persist_state(self) -> None:
        """Persist state to file"""
        try:
            # Create directory if needed
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "state": self.state.name,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "last_failure_time": self.last_failure_time,
                "last_success_time": self.last_success_time,
                "recovery_timeout": self.recovery_timeout,
                "half_open_calls": self.half_open_calls,
                "state_changes": self.state_changes,
                "total_blocked": self.total_blocked
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug(f"Circuit breaker state persisted: {self.state.name}")
        except Exception as e:
            logger.error(f"Failed to persist circuit breaker state: {e}")
    
    async def can_execute(self) -> Tuple[bool, str]:
        """
        Check if operation can execute.
        
        Returns:
            Tuple of (can_execute: bool, reason: str)
        """
        async with self._lock:
            current_time = time.time()
            
            if self.state == BreakerState.CLOSED:
                return True, "Circuit closed - normal operation"
            
            elif self.state == BreakerState.OPEN:
                # Check if recovery timeout has elapsed
                time_since_failure = current_time - self.last_failure_time
                
                if time_since_failure >= self.recovery_timeout:
                    # Transition to HALF_OPEN
                    self._transition_to(BreakerState.HALF_OPEN)
                    return True, "Circuit half-open - testing recovery"
                else:
                    # Still in timeout period
                    remaining = self.recovery_timeout - time_since_failure
                    self.total_blocked += 1
                    return False, f"Circuit open - {remaining:.0f}s until retry"
            
            elif self.state == BreakerState.HALF_OPEN:
                # Allow limited calls for testing
                if self.half_open_calls < self.half_open_max_calls:
                    self.half_open_calls += 1
                    self._persist_state()
                    return True, "Circuit half-open - test call allowed"
                else:
                    self.total_blocked += 1
                    return False, "Circuit half-open - awaiting test result"
            
            return False, "Unknown circuit state"
    
    async def record_success(self) -> None:
        """Record successful operation"""
        async with self._lock:
            self.success_count += 1
            self.last_success_time = time.time()
            
            if self.state == BreakerState.HALF_OPEN:
                # Recovery successful - close circuit
                logger.info(
                    f"Circuit breaker recovery successful after "
                    f"{self.failure_count} failures"
                )
                self._reset()
            elif self.state == BreakerState.CLOSED:
                # Reset failure count on success
                if self.failure_count > 0:
                    logger.debug(f"Resetting failure count from {self.failure_count}")
                    self.failure_count = 0
                    self._persist_state()
    
    async def record_failure(self, reason: str = "") -> None:
        """
        Record failed operation.
        
        Args:
            reason: Optional failure reason for logging
        """
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.warning(
                f"Circuit breaker failure #{self.failure_count}: {reason}"
            )
            
            if self.state == BreakerState.HALF_OPEN:
                # Recovery failed - back to OPEN with exponential backoff
                self.recovery_timeout = min(
                    self.recovery_timeout * 2,
                    self.max_recovery_timeout
                )
                self._transition_to(BreakerState.OPEN)
                logger.warning(
                    f"Recovery failed, circuit reopened with "
                    f"{self.recovery_timeout:.0f}s timeout"
                )
            
            elif self.state == BreakerState.CLOSED:
                # Check if threshold exceeded
                if self.failure_count >= self.failure_threshold:
                    self._transition_to(BreakerState.OPEN)
                    logger.error(
                        f"Circuit breaker opened after {self.failure_count} failures"
                    )
                else:
                    self._persist_state()
    
    def _transition_to(self, new_state: BreakerState) -> None:
        """Transition to new state"""
        old_state = self.state
        self.state = new_state
        self.state_changes += 1
        
        if new_state == BreakerState.HALF_OPEN:
            self.half_open_calls = 0
        
        logger.info(f"Circuit breaker: {old_state.name} → {new_state.name}")
        self._persist_state()
    
    def _reset(self) -> None:
        """Reset to CLOSED state"""
        self.state = BreakerState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0
        self.state_changes += 1
        self._persist_state()
    
    def get_metrics(self) -> BreakerMetrics:
        """Get current metrics"""
        return BreakerMetrics(
            state=self.state.name,
            failure_count=self.failure_count,
            success_count=self.success_count,
            last_failure_time=self.last_failure_time,
            last_success_time=self.last_success_time,
            recovery_timeout=self.recovery_timeout,
            half_open_calls=self.half_open_calls,
            state_changes=self.state_changes,
            total_blocked=self.total_blocked
        )
    
    def get_status(self) -> Dict:
        """Get human-readable status"""
        current_time = time.time()
        
        status = {
            "state": self.state.name,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "state_changes": self.state_changes,
            "total_blocked": self.total_blocked
        }
        
        if self.state == BreakerState.OPEN:
            time_since_failure = current_time - self.last_failure_time
            remaining = max(0, self.recovery_timeout - time_since_failure)
            status["recovery_in"] = f"{remaining:.0f}s"
        
        if self.last_failure_time > 0:
            status["last_failure"] = datetime.fromtimestamp(
                self.last_failure_time
            ).isoformat()
        
        if self.last_success_time > 0:
            status["last_success"] = datetime.fromtimestamp(
                self.last_success_time
            ).isoformat()
        
        return status
    
    async def reset_manually(self) -> None:
        """Manually reset circuit breaker (use with caution)"""
        async with self._lock:
            logger.warning("Circuit breaker manually reset")
            self._reset()


class HealthCheck:
    """
    Health check monitor for API latency and errors.
    
    Monitors API response times and error rates to trigger circuit breaker.
    """
    
    def __init__(
        self,
        latency_threshold_ms: float = 500.0,
        error_budget_per_minute: int = 5
    ):
        """
        Initialize health check.
        
        Args:
            latency_threshold_ms: Maximum acceptable latency in milliseconds
            error_budget_per_minute: Maximum errors allowed per minute
        """
        self.latency_threshold_ms = latency_threshold_ms
        self.error_budget_per_minute = error_budget_per_minute
        
        # Recent errors (timestamp, reason)
        self.recent_errors: list = []
        
        # Recent latencies (timestamp, latency_ms)
        self.recent_latencies: list = []
    
    async def check_latency(self, url: str, timeout: float = 1.0) -> Tuple[bool, float]:
        """
        Check API latency.
        
        Args:
            url: API endpoint to check
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (is_healthy: bool, latency_ms: float)
        """
        import aiohttp
        
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    latency_ms = (time.time() - start_time) * 1000
                    
                    # Record latency
                    self.recent_latencies.append((time.time(), latency_ms))
                    self._cleanup_old_records()
                    
                    # Check if healthy
                    is_healthy = latency_ms < self.latency_threshold_ms and resp.status < 500
                    
                    if not is_healthy:
                        self.recent_errors.append((time.time(), f"High latency: {latency_ms:.0f}ms"))
                    
                    return is_healthy, latency_ms
        
        except asyncio.TimeoutError:
            latency_ms = timeout * 1000
            self.recent_errors.append((time.time(), "Timeout"))
            return False, latency_ms
        
        except Exception as e:
            self.recent_errors.append((time.time(), str(e)))
            return False, float('inf')
    
    def get_error_rate(self) -> float:
        """Get errors per minute"""
        self._cleanup_old_records()
        return len(self.recent_errors)
    
    def is_error_budget_exceeded(self) -> bool:
        """Check if error budget is exceeded"""
        return self.get_error_rate() > self.error_budget_per_minute
    
    def get_avg_latency(self) -> float:
        """Get average latency over last minute"""
        self._cleanup_old_records()
        
        if not self.recent_latencies:
            return 0.0
        
        return sum(lat for _, lat in self.recent_latencies) / len(self.recent_latencies)
    
    def _cleanup_old_records(self) -> None:
        """Remove records older than 1 minute"""
        cutoff = time.time() - 60
        
        self.recent_errors = [
            (ts, reason) for ts, reason in self.recent_errors
            if ts > cutoff
        ]
        
        self.recent_latencies = [
            (ts, lat) for ts, lat in self.recent_latencies
            if ts > cutoff
        ]
