"""
Scout Agent

Discovers trading opportunities by collecting and synchronizing signals from
multiple data sources (price, news, technical indicators, supply chain).
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .base_agent import BaseAgent, AgentState
from ..signal_synchronizer import SignalSynchronizer, TimestampedSignal
from ..async_utils import gather_with_timeout
from ..data import (
    get_price_provider,
    get_news_provider,
    get_technical_provider,
    get_supply_chain_provider
)

logger = logging.getLogger(__name__)


class ScoutAgent(BaseAgent):
    """
    Scout Agent - Discovers trading opportunities.
    
    Responsibilities:
    - Collect signals from multiple sources in parallel
    - Synchronize signals using SignalSynchronizer
    - Filter candidates by quality thresholds
    - Output scored candidates for analysis
    """
    
    def __init__(
        self,
        circuit_breaker=None,
        min_score: float = 60.0,
        signal_window_minutes: int = 5
    ):
        """
        Initialize Scout Agent.
        
        Args:
            circuit_breaker: Optional circuit breaker
            min_score: Minimum score threshold for candidates
            signal_window_minutes: Time window for signal synchronization
        """
        super().__init__(name="Scout", circuit_breaker=circuit_breaker)
        self.min_score = min_score
        self.signal_synchronizer = SignalSynchronizer(
            window_size=timedelta(minutes=signal_window_minutes)
        )
        
        # Data providers
        self.price_provider = get_price_provider()
        self.news_provider = get_news_provider()
        self.technical_provider = get_technical_provider()
        self.supply_chain_provider = get_supply_chain_provider()
    
    async def _execute_impl(self, state: AgentState) -> List[Dict]:
        """
        Execute scout logic: collect signals and find candidates.
        
        Args:
            state: Current agent state with tickers to scout
            
        Returns:
            List of candidate dictionaries with scores
        """
        candidates = []
        
        for ticker in state.tickers:
            try:
                # Collect signals in parallel
                signals = await self._collect_signals(ticker)
                
                # Calculate opportunity score
                score = self._calculate_score(signals)
                
                # Filter by minimum score
                if score >= self.min_score:
                    candidate = {
                        "ticker": ticker,
                        "score": round(score, 2),
                        "signals": signals,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    candidates.append(candidate)
                    logger.info(f"Candidate found: {ticker} (score={score:.1f})")
                else:
                    logger.debug(f"Filtered out: {ticker} (score={score:.1f} < {self.min_score})")
            
            except Exception as e:
                logger.error(f"Failed to scout {ticker}: {e}")
                state.errors.append(f"Scout error for {ticker}: {str(e)}")
        
        # Sort by score (highest first)
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"Scout found {len(candidates)} candidates from {len(state.tickers)} tickers")
        
        return candidates
    
    async def _collect_signals(self, ticker: str) -> Dict:
        """
        Collect all signals for a ticker in parallel.
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dictionary of collected signals
        """
        # Parallel signal collection with timeout
        results = await gather_with_timeout(
            self.price_provider.get_price(ticker),
            self.news_provider.get_sentiment(ticker),
            self.technical_provider.get_indicators(ticker),
            self.supply_chain_provider.get_supply_chain(ticker),
            timeout=0.2,  # 200ms max for all signals
            return_exceptions=True
        )
        
        # Unpack results
        price_data, news_data, technical_data, supply_chain_data = results
        
        # Handle exceptions
        if isinstance(price_data, Exception):
            logger.warning(f"Price data failed for {ticker}: {price_data}")
            price_data = {"price": 0.0, "volume": 0}
        
        if isinstance(news_data, Exception):
            logger.warning(f"News data failed for {ticker}: {news_data}")
            news_data = {"sentiment_score": 50.0, "confidence": 0.5}
        
        if isinstance(technical_data, Exception):
            logger.warning(f"Technical data failed for {ticker}: {technical_data}")
            technical_data = {"rsi": 50.0, "signal": "NEUTRAL"}
        
        if isinstance(supply_chain_data, Exception):
            logger.warning(f"Supply chain data failed for {ticker}: {supply_chain_data}")
            supply_chain_data = {"risk_score": 50.0}
        
        return {
            "price": price_data,
            "news": news_data,
            "technical": technical_data,
            "supply_chain": supply_chain_data
        }
    
    def _calculate_score(self, signals: Dict) -> float:
        """
        Calculate opportunity score from signals.
        
        Scoring factors:
        - News sentiment (0-100): 40% weight
        - Technical indicators: 30% weight
        - Supply chain risk (inverted): 20% weight
        - Volume: 10% weight
        
        Args:
            signals: Collected signals
            
        Returns:
            Score from 0-100
        """
        # News sentiment (40% weight)
        news_score = signals["news"].get("sentiment_score", 50.0) * 0.4
        
        # Technical indicators (30% weight)
        rsi = signals["technical"].get("rsi", 50.0)
        technical_signal = signals["technical"].get("signal", "NEUTRAL")
        
        # RSI: prefer 40-60 range (not overbought/oversold)
        rsi_score = 100 - abs(rsi - 50) * 2  # Max 100 at RSI=50
        
        # Signal bonus
        signal_bonus = 20 if technical_signal == "BUY" else 0
        
        technical_score = (rsi_score + signal_bonus) / 2 * 0.3
        
        # Supply chain risk (20% weight, inverted - lower risk is better)
        supply_chain_risk = signals["supply_chain"].get("risk_score", 50.0)
        supply_chain_score = (100 - supply_chain_risk) * 0.2
        
        # Volume (10% weight)
        volume = signals["price"].get("volume", 0)
        volume_score = min(volume / 1000000 * 50, 100) * 0.1  # Normalize to 100
        
        total_score = news_score + technical_score + supply_chain_score + volume_score
        
        return max(0, min(100, total_score))  # Clamp to 0-100
