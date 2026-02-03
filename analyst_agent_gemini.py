"""
Agentic Analyst powered by Google Gemini
Production-grade module for autonomous trading decisions using LLM reasoning
"""

import os
import logging
import json
from typing import Optional, Literal
from pydantic import BaseModel, Field
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURE (Pydantic)
# ============================================================================

class TradeSignal(BaseModel):
    """Structured trade signal with strict validation"""
    signal: Literal["BUY", "WAIT", "AVOID"] = Field(
        description="Trading action: BUY (bullish), WAIT (neutral), AVOID (bearish)"
    )
    confidence: float = Field(
        description="Confidence score from 0.0 to 1.0",
        ge=0.0,
        le=1.0
    )
    reasoning: str = Field(
        description="Concise explanation of the decision (max 200 chars)",
        max_length=200
    )
    stop_loss: Optional[float] = Field(
        default=None,
        description="Recommended stop loss price"
    )
    take_profit: Optional[float] = Field(
        default=None,
        description="Recommended target price"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "signal": "BUY",
                "confidence": 0.85,
                "reasoning": "Strong oversold RSI (25) + bullish MACD crossover + positive news momentum",
                "stop_loss": 2400.0,
                "take_profit": 2650.0
            }
        }


# ============================================================================
# THE AGENTIC ANALYST
# ============================================================================

class AgenticAnalyst:
    """
    AI-powered trading analyst using Google Gemini
    Replaces rigid if/else logic with LLM reasoning
    """
    
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the Gemini-powered analyst
        
        Args:
            model_name: Gemini model to use (default: gemini-2.5-flash for stability)
        """
        # Validate API key
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found in environment. Fallback mode will be used.")
            self.client = None
            self.model = None
        else:
            try:
                # Initialize Google GenAI client
                self.client = genai.Client(api_key=api_key)
                self.model = model_name
                logger.info(f"AgenticAnalyst initialized with {model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini: {e}")
                self.client = None
                self.model = None
        
        # Define the system prompt
        self.system_prompt = """You are a BALANCED Quantitative Trading Analyst with experience in Indian markets (NSE/BSE).
Your job is to analyze technical indicators and news to make ACTIONABLE trading decisions.

SIGNAL FRAMEWORK (Use all 3 signals equally):
- **BUY** (Green): Strong bullish signals, positive momentum, good risk/reward
- **WAIT** (Neutral): Mixed signals, unclear direction, need more data
- **AVOID** (Red): Strong bearish signals, negative momentum, high risk

CRITICAL RULES:
1. BE DECISIVE - Don't default to WAIT unless truly unclear
2. ANALYZE HOLISTICALLY - Consider ALL indicators together
3. CONFIDENCE THRESHOLD: 
   - BUY if confidence ≥ 60% (not too high!)
   - AVOID if negative confidence ≥ 60%
   - WAIT only if truly mixed (40-60% range)
4. NEWS WEIGHT: Recent news can override technicals
5. TREND MATTERS: Respect the dominant trend

INDICATORS INTERPRETATION:
- RSI < 30 = Oversold (BULLISH signal)
- RSI > 70 = Overbought (BEARISH signal)
- MACD > Signal = Bullish momentum → favor BUY
- MACD < Signal = Bearish momentum → favor AVOID
- Volume spike + price up = Strong buying → BUY
- Volume spike + price down = Strong selling → AVOID
- Trend: Bullish → bias BUY | Bearish → bias AVOID | Neutral → WAIT

DECISION LOGIC:
- If 2+ bullish signals → BUY
- If 2+ bearish signals → AVOID  
- If mixed/contradictory → WAIT

You MUST respond with valid JSON in this EXACT format:
{
  "signal": "BUY" or "WAIT" or "AVOID",
  "confidence": 0.75,
  "reasoning": "Brief explanation max 200 chars",
  "stop_loss": 2400.0 or null,
  "take_profit": 2650.0 or null
}"""
    
    def analyze_ticker(
        self,
        ticker: str,
        current_price: float,
        technical_data: dict,
        news_summary: str = "No recent news"
    ) -> TradeSignal:
        """
        Analyze a ticker and generate a trade signal
        
        Args:
            ticker: Stock symbol (e.g., "RELIANCE.NS")
            current_price: Current stock price
            technical_data: Dict with RSI, MACD, volume, trend, etc.
            news_summary: Recent news context
            
        Returns:
            TradeSignal with BUY/SELL/WAIT recommendation
        """
        
        # Format technical data
        tech_str = "\n".join([f"- {k}: {v}" for k, v in technical_data.items()])
        
        # ====================================================================
        # CIRCUIT BREAKER: Try Gemini, fallback to rule-based
        # ====================================================================
        
        if self.client is None:
            logger.warning("Gemini not available. Using fallback logic.")
            return self._fallback_analysis(ticker, current_price, technical_data)
        
        try:
            # Create the full prompt
            prompt = f"""{self.system_prompt}

Now analyze this trade opportunity:

TICKER: {ticker}
CURRENT PRICE: ${current_price}

TECHNICAL DATA:
{tech_str}

NEWS SUMMARY:
{news_summary}

Provide your expert analysis and trading recommendation in JSON format."""
            
            # Call Gemini
            logger.info(f"Analyzing {ticker} with Gemini...")
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Create TradeSignal
            signal = TradeSignal(**data)
            
            logger.info(f"Gemini analysis complete: {signal.signal} (confidence: {signal.confidence})")
            return signal
            
        except Exception as e:
            # Log error but don't crash
            logger.error(f"Gemini API failed: {e}. Falling back to rule-based analysis.")
            return self._fallback_analysis(ticker, current_price, technical_data)
    
    def _fallback_analysis(
        self,
        ticker: str,
        current_price: float,
        technical_data: dict
    ) -> TradeSignal:
        """
        Simple rule-based fallback when Gemini is unavailable
        
        Args:
            ticker: Stock symbol
            current_price: Current price
            technical_data: Technical indicators
            
        Returns:
            TradeSignal based on simple rules
        """
        rsi = technical_data.get('rsi', 50)
        macd_signal = technical_data.get('macd_signal', 'neutral')
        
        # Simple oversold/overbought logic
        if rsi < 30 and macd_signal.lower() == 'bullish':
            return TradeSignal(
                signal="BUY",
                confidence=0.6,
                reasoning="Fallback: Oversold RSI + bullish MACD",
                stop_loss=current_price * 0.95,
                take_profit=current_price * 1.10
            )
        elif rsi > 70 and macd_signal.lower() == 'bearish':
            return TradeSignal(
                signal="SELL",
                confidence=0.6,
                reasoning="Fallback: Overbought RSI + bearish MACD",
                stop_loss=None,
                take_profit=None
            )
        elif rsi < 30:
            return TradeSignal(
                signal="BUY",
                confidence=0.5,
                reasoning="Fallback: Oversold RSI",
                stop_loss=current_price * 0.95,
                take_profit=current_price * 1.08
            )
        elif rsi > 70:
            return TradeSignal(
                signal="SELL",
                confidence=0.5,
                reasoning="Fallback: Overbought RSI",
                stop_loss=None,
                take_profit=None
            )
        else:
            return TradeSignal(
                signal="WAIT",
                confidence=0.7,
                reasoning="Fallback: Neutral indicators, no clear signal",
                stop_loss=None,
                take_profit=None
            )


# ============================================================================
# TEST / DEMO
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 AGENTIC ANALYST DEMO - Gemini-Powered Trading Bot")
    print("=" * 60)
    
    # Initialize analyst
    analyst = AgenticAnalyst(model_name="gemini-2.5-flash")
    
    # Mock test case: TSLA with concerning indicators
    print("\n📊 Test Case: TSLA with Mixed Signals")
    print("-" * 60)
    
    test_data = {
        "ticker": "TSLA",
        "current_price": 242.50,
        "technical_data": {
            "rsi": 75.2,
            "macd": 3.45,
            "macd_signal": "Bullish",
            "sma_20": 235.00,
            "sma_50": 228.00,
            "sma_200": 220.00,
            "volume": "High (2.5x avg)",
            "trend": "Bullish"
        },
        "news_summary": "Tesla reports battery fire in new Model Y. NHTSA investigating. Stock up 15% this week on AI hype."
    }
    
    # Get analysis
    signal = analyst.analyze_ticker(
        ticker=test_data["ticker"],
        current_price=test_data["current_price"],
        technical_data=test_data["technical_data"],
        news_summary=test_data["news_summary"]
    )
    
    # Display results
    print(f"\n{'🟢 BUY' if signal.signal == 'BUY' else '🔴 SELL' if signal.signal == 'SELL' else '🔵 WAIT'} Signal")
    print(f"Confidence: {signal.confidence * 100:.1f}%")
    print(f"\nReasoning:\n{signal.reasoning}")
    
    if signal.stop_loss:
        print(f"\nStop Loss: ${signal.stop_loss:.2f}")
    if signal.take_profit:
        print(f"Take Profit: ${signal.take_profit:.2f}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis Complete!")
    print("=" * 60)
    
    # Test case 2: Strong buy signal
    print("\n\n📊 Test Case 2: RELIANCE.NS - Strong Buy Setup")
    print("-" * 60)
    
    signal2 = analyst.analyze_ticker(
        ticker="RELIANCE.NS",
        current_price=2450.00,
        technical_data={
            "rsi": 28.5,
            "macd": -2.1,
            "macd_signal": "Bullish crossover",
            "sma_20": 2480.00,
            "sma_50": 2520.00,
            "sma_200": 2400.00,
            "volume": "High",
            "trend": "Recovering from oversold"
        },
        news_summary="Reliance announces major expansion in renewable energy. Govt approves new refinery."
    )
    
    print(f"\n{'🟢 BUY' if signal2.signal == 'BUY' else '🔴 SELL' if signal2.signal == 'SELL' else '🔵 WAIT'} Signal")
    print(f"Confidence: {signal2.confidence * 100:.1f}%")
    print(f"\nReasoning:\n{signal2.reasoning}")
    
    if signal2.stop_loss:
        print(f"\nStop Loss: ₹{signal2.stop_loss:.2f}")
    if signal2.take_profit:
        print(f"Take Profit: ₹{signal2.take_profit:.2f}")
    
    print("\n" + "=" * 60)
