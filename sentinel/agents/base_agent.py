"""
Base Agent Classes

Provides base functionality for all trading agents including state management,
circuit breaker integration, and standardized result formats.
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class AgentState:
    """
    Shared state passed between agents in the workflow.
    
    This state object flows through the agent pipeline, with each agent
    adding its results and passing to the next agent.
    """
    # Input
    tickers: List[str] = field(default_factory=list)
    
    # Scout results
    scout_candidates: List[Dict] = field(default_factory=list)
    scout_latency_ms: float = 0.0
    
    # Analyst results
    analyst_recommendations: List[Dict] = field(default_factory=list)
    analyst_latency_ms: float = 0.0
    
    # Executioner results
    execution_results: List[Dict] = field(default_factory=list)
    executioner_latency_ms: float = 0.0
    
    # Overall metrics
    total_latency_ms: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class AgentResult:
    """
    Standardized result format from agent execution.
    
    Attributes:
        success: Whether agent execution succeeded
        data: Agent-specific result data
        latency_ms: Execution time in milliseconds
        error: Error message if failed
        metadata: Additional metadata
    """
    success: bool
    data: Any
    latency_ms: float
    error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class BaseAgent(ABC):
    """
    Abstract base class for all trading agents.
    
    Provides common functionality:
    - Circuit breaker integration
    - Execution timing
    - Error handling
    - Logging
    """
    
    def __init__(
        self,
        name: str,
        circuit_breaker: Optional[Any] = None
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent name for logging
            circuit_breaker: Optional circuit breaker instance
        """
        self.name = name
        self.circuit_breaker = circuit_breaker
        self.execution_count = 0
        self.total_latency_ms = 0.0
        self.error_count = 0
    
    async def execute(self, state: AgentState) -> AgentResult:
        """
        Execute agent with circuit breaker check and timing.
        
        Args:
            state: Current agent state
            
        Returns:
            AgentResult with execution outcome
        """
        start_time = time.time()
        
        try:
            # Check circuit breaker
            if self.circuit_breaker:
                can_execute, reason = await self.circuit_breaker.can_execute()
                if not can_execute:
                    logger.warning(f"{self.name} blocked by circuit breaker: {reason}")
                    return AgentResult(
                        success=False,
                        data=None,
                        latency_ms=0.0,
                        error=f"Circuit breaker: {reason}"
                    )
            
            # Execute agent logic
            logger.info(f"{self.name} starting execution")
            result = await self._execute_impl(state)
            
            # Record success
            if self.circuit_breaker:
                await self.circuit_breaker.record_success()
            
            # Update metrics
            latency_ms = (time.time() - start_time) * 1000
            self.execution_count += 1
            self.total_latency_ms += latency_ms
            
            logger.info(f"{self.name} completed in {latency_ms:.0f}ms")
            
            return AgentResult(
                success=True,
                data=result,
                latency_ms=latency_ms,
                metadata={
                    "agent": self.name,
                    "execution_count": self.execution_count
                }
            )
        
        except Exception as e:
            # Record failure
            if self.circuit_breaker:
                await self.circuit_breaker.record_failure(str(e))
            
            self.error_count += 1
            latency_ms = (time.time() - start_time) * 1000
            
            logger.error(f"{self.name} failed after {latency_ms:.0f}ms: {e}")
            
            return AgentResult(
                success=False,
                data=None,
                latency_ms=latency_ms,
                error=str(e),
                metadata={
                    "agent": self.name,
                    "error_count": self.error_count
                }
            )
    
    @abstractmethod
    async def _execute_impl(self, state: AgentState) -> Any:
        """
        Agent-specific execution logic (to be implemented by subclasses).
        
        Args:
            state: Current agent state
            
        Returns:
            Agent-specific result data
        """
        pass
    
    def get_metrics(self) -> Dict:
        """Get agent performance metrics"""
        avg_latency = (
            self.total_latency_ms / self.execution_count
            if self.execution_count > 0
            else 0.0
        )
        
        return {
            "name": self.name,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "avg_latency_ms": round(avg_latency, 2),
            "total_latency_ms": round(self.total_latency_ms, 2),
            "error_rate": (
                self.error_count / self.execution_count
                if self.execution_count > 0
                else 0.0
            )
        }
