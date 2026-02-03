"""
Unit tests for CircuitBreaker module

Tests state transitions, persistence, exponential backoff, and health checks.
"""

import pytest
import asyncio
import json
from pathlib import Path
from sentinel.circuit_breaker import CircuitBreaker, BreakerState, HealthCheck


@pytest.fixture
def temp_state_file(tmp_path):
    """Create temporary state file"""
    return str(tmp_path / "circuit_breaker_test.json")


@pytest.mark.asyncio
async def test_circuit_breaker_initialization(temp_state_file):
    """Test circuit breaker initialization"""
    breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=10.0,
        state_file=temp_state_file
    )
    
    assert breaker.state == BreakerState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_closed_state_allows_execution(temp_state_file):
    """Test that CLOSED state allows execution"""
    breaker = CircuitBreaker(state_file=temp_state_file)
    
    can_execute, reason = await breaker.can_execute()
    
    assert can_execute is True
    assert "closed" in reason.lower()


@pytest.mark.asyncio
async def test_transition_to_open_on_failures(temp_state_file):
    """Test transition to OPEN after threshold failures"""
    breaker = CircuitBreaker(
        failure_threshold=3,
        state_file=temp_state_file
    )
    
    # Record 3 failures
    for i in range(3):
        await breaker.record_failure(f"Failure {i+1}")
    
    # Should be OPEN now
    assert breaker.state == BreakerState.OPEN
    
    # Should block execution
    can_execute, reason = await breaker.can_execute()
    assert can_execute is False
    assert "open" in reason.lower()


@pytest.mark.asyncio
async def test_transition_to_half_open_after_timeout(temp_state_file):
    """Test transition to HALF_OPEN after recovery timeout"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=0.5,  # Short timeout for testing
        state_file=temp_state_file
    )
    
    # Open the circuit
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    assert breaker.state == BreakerState.OPEN
    
    # Wait for recovery timeout
    await asyncio.sleep(0.6)
    
    # Should transition to HALF_OPEN
    can_execute, reason = await breaker.can_execute()
    assert can_execute is True
    assert breaker.state == BreakerState.HALF_OPEN


@pytest.mark.asyncio
async def test_recovery_success_closes_circuit(temp_state_file):
    """Test successful recovery closes circuit"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=0.5,
        state_file=temp_state_file
    )
    
    # Open circuit
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    
    # Wait for recovery
    await asyncio.sleep(0.6)
    
    # Transition to HALF_OPEN
    await breaker.can_execute()
    assert breaker.state == BreakerState.HALF_OPEN
    
    # Record success
    await breaker.record_success()
    
    # Should be CLOSED
    assert breaker.state == BreakerState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_recovery_failure_reopens_with_backoff(temp_state_file):
    """Test failed recovery reopens with exponential backoff"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=1.0,
        state_file=temp_state_file
    )
    
    # Open circuit
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    initial_timeout = breaker.recovery_timeout
    
    # Wait for recovery
    await asyncio.sleep(1.1)
    
    # Transition to HALF_OPEN
    await breaker.can_execute()
    
    # Fail recovery
    await breaker.record_failure("Recovery failed")
    
    # Should be OPEN with doubled timeout
    assert breaker.state == BreakerState.OPEN
    assert breaker.recovery_timeout == initial_timeout * 2


@pytest.mark.asyncio
async def test_state_persistence(temp_state_file):
    """Test state persists across restarts"""
    # Create breaker and open circuit
    breaker1 = CircuitBreaker(
        failure_threshold=2,
        state_file=temp_state_file
    )
    
    await breaker1.record_failure("Failure 1")
    await breaker1.record_failure("Failure 2")
    assert breaker1.state == BreakerState.OPEN
    
    # Create new breaker (simulating restart)
    breaker2 = CircuitBreaker(
        failure_threshold=2,
        state_file=temp_state_file
    )
    
    # Should load OPEN state
    assert breaker2.state == BreakerState.OPEN
    assert breaker2.failure_count == 2


@pytest.mark.asyncio
async def test_success_resets_failure_count(temp_state_file):
    """Test success resets failure count in CLOSED state"""
    breaker = CircuitBreaker(
        failure_threshold=3,
        state_file=temp_state_file
    )
    
    # Record some failures
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    assert breaker.failure_count == 2
    
    # Record success
    await breaker.record_success()
    
    # Failure count should reset
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_half_open_limits_calls(temp_state_file):
    """Test HALF_OPEN limits number of test calls"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        recovery_timeout=0.5,
        half_open_max_calls=1,
        state_file=temp_state_file
    )
    
    # Open circuit
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    
    # Wait for recovery
    await asyncio.sleep(0.6)
    
    # First call should be allowed
    can_execute1, _ = await breaker.can_execute()
    assert can_execute1 is True
    
    # Second call should be blocked
    can_execute2, reason2 = await breaker.can_execute()
    assert can_execute2 is False
    assert "awaiting" in reason2.lower()


@pytest.mark.asyncio
async def test_get_metrics(temp_state_file):
    """Test metrics retrieval"""
    breaker = CircuitBreaker(state_file=temp_state_file)
    
    await breaker.record_failure("Test failure")
    await breaker.record_success()
    
    metrics = breaker.get_metrics()
    
    assert metrics.failure_count >= 1
    assert metrics.success_count >= 1
    assert metrics.state == breaker.state.name


@pytest.mark.asyncio
async def test_get_status(temp_state_file):
    """Test status retrieval"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        state_file=temp_state_file
    )
    
    # Open circuit
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    
    status = breaker.get_status()
    
    assert status["state"] == "OPEN"
    assert "recovery_in" in status
    assert "last_failure" in status


@pytest.mark.asyncio
async def test_manual_reset(temp_state_file):
    """Test manual circuit reset"""
    breaker = CircuitBreaker(
        failure_threshold=2,
        state_file=temp_state_file
    )
    
    # Open circuit
    await breaker.record_failure("Failure 1")
    await breaker.record_failure("Failure 2")
    assert breaker.state == BreakerState.OPEN
    
    # Manual reset
    await breaker.reset_manually()
    
    # Should be CLOSED
    assert breaker.state == BreakerState.CLOSED
    assert breaker.failure_count == 0


@pytest.mark.asyncio
async def test_health_check_error_rate():
    """Test health check error rate tracking"""
    health = HealthCheck(error_budget_per_minute=5)
    
    # Add some errors
    for i in range(3):
        health.recent_errors.append((asyncio.get_event_loop().time(), f"Error {i}"))
    
    error_rate = health.get_error_rate()
    assert error_rate == 3
    
    is_exceeded = health.is_error_budget_exceeded()
    assert is_exceeded is False  # 3 < 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
