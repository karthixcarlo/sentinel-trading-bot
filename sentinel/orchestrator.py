"""
Trading Workflow Orchestrator

Coordinates the multi-agent trading workflow: Scout → Analyst → Executioner
"""

import logging
import time
from typing import List, Optional

from .agents import ScoutAgent, AnalystAgent, ExecutionerAgent, AgentState
from .circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class TradingOrchestrator:
    """
    Orchestrates the complete trading workflow.
    
    Workflow:
    1. Scout: Discover opportunities from signals
    2. Analyst: Analyze and generate recommendations
    3. Executioner: Validate and execute trades
    """
    
    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        account_balance: float = 10000.0
    ):
        """
        Initialize trading orchestrator.
        
        Args:
            circuit_breaker: Optional circuit breaker for all agents
            account_balance: Account balance for position sizing
        """
        self.circuit_breaker = circuit_breaker
        
        # Initialize agents
        self.scout = ScoutAgent(circuit_breaker=circuit_breaker)
        self.analyst = AnalystAgent(
            circuit_breaker=circuit_breaker,
            account_balance=account_balance
        )
        self.executioner = ExecutionerAgent(circuit_breaker=circuit_breaker)
    
    async def execute_workflow(self, tickers: List[str]) -> AgentState:
        """
        Execute complete trading workflow.
        
        Args:
            tickers: List of tickers to analyze
            
        Returns:
            Final agent state with all results
        """
        start_time = time.time()
        
        # Initialize state
        state = AgentState(tickers=tickers)
        
        logger.info(f"Starting trading workflow for {len(tickers)} tickers")
        
        # Phase 1: Scout - Discover opportunities
        logger.info("=" * 60)
        logger.info("PHASE 1: SCOUT - Discovering opportunities")
        logger.info("=" * 60)
        
        scout_result = await self.scout.execute(state)
        
        if scout_result.success:
            state.scout_candidates = scout_result.data
            state.scout_latency_ms = scout_result.latency_ms
            logger.info(f"Scout found {len(state.scout_candidates)} candidates")
        else:
            logger.error(f"Scout failed: {scout_result.error}")
            state.errors.append(f"Scout: {scout_result.error}")
            state.total_latency_ms = (time.time() - start_time) * 1000
            return state
        
        # Skip if no candidates
        if not state.scout_candidates:
            logger.info("No candidates found, skipping analysis")
            state.total_latency_ms = (time.time() - start_time) * 1000
            return state
        
        # Phase 2: Analyst - Analyze and recommend
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 2: ANALYST - Analyzing candidates")
        logger.info("=" * 60)
        
        analyst_result = await self.analyst.execute(state)
        
        if analyst_result.success:
            state.analyst_recommendations = analyst_result.data
            state.analyst_latency_ms = analyst_result.latency_ms
            logger.info(f"Analyst generated {len(state.analyst_recommendations)} recommendations")
        else:
            logger.error(f"Analyst failed: {analyst_result.error}")
            state.errors.append(f"Analyst: {analyst_result.error}")
            state.total_latency_ms = (time.time() - start_time) * 1000
            return state
        
        # Skip if no recommendations
        if not state.analyst_recommendations:
            logger.info("No recommendations generated, skipping execution")
            state.total_latency_ms = (time.time() - start_time) * 1000
            return state
        
        # Phase 3: Executioner - Execute trades
        logger.info("\n" + "=" * 60)
        logger.info("PHASE 3: EXECUTIONER - Executing trades")
        logger.info("=" * 60)
        
        executioner_result = await self.executioner.execute(state)
        
        if executioner_result.success:
            state.execution_results = executioner_result.data
            state.executioner_latency_ms = executioner_result.latency_ms
            logger.info(f"Executioner completed {len(state.execution_results)} trades")
        else:
            logger.error(f"Executioner failed: {executioner_result.error}")
            state.errors.append(f"Executioner: {executioner_result.error}")
        
        # Calculate total latency
        state.total_latency_ms = (time.time() - start_time) * 1000
        
        logger.info("\n" + "=" * 60)
        logger.info(f"WORKFLOW COMPLETE - Total latency: {state.total_latency_ms:.0f}ms")
        logger.info("=" * 60)
        
        return state
    
    def get_metrics(self) -> dict:
        """Get metrics from all agents"""
        return {
            "scout": self.scout.get_metrics(),
            "analyst": self.analyst.get_metrics(),
            "executioner": self.executioner.get_metrics()
        }
