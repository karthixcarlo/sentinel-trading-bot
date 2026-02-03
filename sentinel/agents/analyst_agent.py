"""
Analyst Agent

Performs deep analysis and risk assessment on scout candidates to generate
trade recommendations with position sizing.
"""

import logging
from typing import Dict, List, Optional

from .base_agent import BaseAgent, AgentState
from ..risk_model import ConservativeRiskModel

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """
    Analyst Agent - Deep analysis and risk assessment.
    
    Responsibilities:
    - Multi-factor analysis of candidates
    - Risk/reward calculation
    - Position sizing using ConservativeRiskModel
    - Generate trade recommendations with confidence scores
    """
    
    def __init__(
        self,
        circuit_breaker=None,
        account_balance: float = 10000.0,
        min_confidence: float = 0.65
    ):
        """
        Initialize Analyst Agent.
        
        Args:
            circuit_breaker: Optional circuit breaker
            account_balance: Account balance for position sizing
            min_confidence: Minimum confidence threshold for recommendations
        """
        super().__init__(name="Analyst", circuit_breaker=circuit_breaker)
        self.risk_model = ConservativeRiskModel(account_balance=account_balance)
        self.min_confidence = min_confidence
    
    async def _execute_impl(self, state: AgentState) -> List[Dict]:
        """
        Execute analyst logic: analyze candidates and generate recommendations.
        
        Args:
            state: Current agent state with scout candidates
            
        Returns:
            List of trade recommendations
        """
        recommendations = []
        
        for candidate in state.scout_candidates:
            try:
                # Analyze candidate
                recommendation = await self._analyze_candidate(candidate)
                
                # Filter by confidence
                if recommendation and recommendation["confidence"] >= self.min_confidence:
                    recommendations.append(recommendation)
                    logger.info(
                        f"Recommendation: {recommendation['action']} {recommendation['ticker']} "
                        f"(confidence={recommendation['confidence']:.2f})"
                    )
                else:
                    logger.debug(
                        f"Filtered out: {candidate['ticker']} "
                        f"(confidence={recommendation['confidence']:.2f} < {self.min_confidence})"
                    )
            
            except Exception as e:
                logger.error(f"Failed to analyze {candidate['ticker']}: {e}")
                state.errors.append(f"Analyst error for {candidate['ticker']}: {str(e)}")
        
        logger.info(f"Analyst generated {len(recommendations)} recommendations")
        
        return recommendations
    
    async def _analyze_candidate(self, candidate: Dict) -> Optional[Dict]:
        """
        Analyze a candidate and generate trade recommendation.
        
        Args:
            candidate: Candidate from scout
            
        Returns:
            Trade recommendation dictionary or None
        """
        ticker = candidate["ticker"]
        signals = candidate["signals"]
        score = candidate["score"]
        
        # Get current price
        current_price = signals["price"]["price"]
        
        # Determine action based on signals
        action = self._determine_action(signals)
        
        if action == "HOLD":
            return None
        
        # Calculate entry, stop loss, and take profit
        entry_price = current_price
        
        # Stop loss: 2% below entry for BUY
        stop_loss_price = entry_price * 0.98 if action == "BUY" else entry_price * 1.02
        
        # Take profit: 4% above entry for BUY (2:1 reward/risk)
        take_profit_price = entry_price * 1.04 if action == "BUY" else entry_price * 0.96
        
        # Calculate confidence from score and signals
        confidence = self._calculate_confidence(signals, score)
        
        # Calculate expected return (before costs)
        expected_return_pct = 0.04 if action == "BUY" else 0.04  # 4% target
        
        # Adjust for costs (Phase 1 risk model does this)
        adjusted_return = self.risk_model.adjust_expected_return(expected_return_pct)
        
        # Calculate position size
        position_size, risk_params = self.risk_model.calculate_position_size(
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            confidence=confidence
        )
        
        # Validate trade
        is_valid, validation_reason = self.risk_model.validate_trade(
            expected_return=adjusted_return,
            position_size=position_size,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price
        )
        
        if not is_valid:
            logger.debug(f"Trade validation failed for {ticker}: {validation_reason}")
            return None
        
        # Generate recommendation
        recommendation = {
            "ticker": ticker,
            "action": action,
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss_price, 2),
            "take_profit": round(take_profit_price, 2),
            "position_size": position_size,
            "confidence": round(confidence, 3),
            "expected_return": round(adjusted_return, 4),
            "risk_params": {
                "max_loss_amount": round(risk_params.max_loss_amount, 2),
                "portfolio_exposure_pct": round(risk_params.portfolio_exposure_pct, 2),
                "risk_reward_ratio": round(risk_params.risk_reward_ratio, 2)
            },
            "reasoning": self._generate_reasoning(signals, score, confidence)
        }
        
        return recommendation
    
    def _determine_action(self, signals: Dict) -> str:
        """Determine trading action from signals"""
        technical_signal = signals["technical"].get("signal", "NEUTRAL")
        sentiment = signals["news"].get("sentiment_score", 50.0)
        rsi = signals["technical"].get("rsi", 50.0)
        
        # Simple rule-based decision
        if technical_signal == "BUY" and sentiment > 60 and rsi < 60:
            return "BUY"
        elif technical_signal == "SELL" or sentiment < 40 or rsi > 70:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_confidence(self, signals: Dict, score: float) -> float:
        """Calculate confidence score from signals"""
        # Base confidence from scout score
        base_confidence = score / 100
        
        # Adjust for news confidence
        news_confidence = signals["news"].get("confidence", 0.7)
        
        # Combine (weighted average)
        confidence = base_confidence * 0.7 + news_confidence * 0.3
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_reasoning(self, signals: Dict, score: float, confidence: float) -> str:
        """Generate human-readable reasoning"""
        sentiment = signals["news"].get("sentiment_score", 50.0)
        rsi = signals["technical"].get("rsi", 50.0)
        technical_signal = signals["technical"].get("signal", "NEUTRAL")
        
        reasoning = f"Scout score: {score:.1f}/100. "
        reasoning += f"Sentiment: {sentiment:.1f}/100. "
        reasoning += f"RSI: {rsi:.1f}. "
        reasoning += f"Technical signal: {technical_signal}. "
        reasoning += f"Confidence: {confidence:.2f}."
        
        return reasoning
