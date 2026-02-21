"""
Stock Signal Indicator - BUY/SELL/HOLDDisplay
Based on enhanced_deep_search technical analysis
"""

import streamlit as st
from enhanced_deep_search import enhanced_deep_search
import asyncio


def display_stock_signal(symbol: str):
    """
    Display BUY/SELL/HOLD signal for a stock
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')
    
    Returns:
        HTML badge with signal and confidence
    """
    
    try:
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(enhanced_deep_search(symbol))
        loop.close()
        
        recommendation = analysis.get('recommendation', 'HOLD')
        confidence = analysis.get('confidence', 0.5)
        technical = analysis.get('technical_analysis', {})
        
        # Groww-style color coding
        if recommendation == 'BUY':
            color = "#00D09C"  # Groww Green
            icon = "🟢" # Green circle
            bg_color = "#E6FAF5"  # Light mint
        elif recommendation == 'SELL':
            color = "#EB5B3C"  # Groww Red
            icon = "🔴" # Red circle
            bg_color = "#FFECEA"  # Light red
        else:  # HOLD
            color = "#4A90E2"  # Blue
            icon = "🔵" # Blue circle
            bg_color = "#E3F2FD"  # Light blue
        
        # Display badge
        st.markdown(f"""
        <div style="
            background-color: {bg_color};
            border-left: 4px solid {color};
            padding: 12px 16px;
            border-radius: 8px;
            margin: 8px 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="color: {color}; font-weight: 700; font-size: 16px;">
                        {icon} {recommendation}
                    </span>
                    <span style="color: #7C7E8C; font-size: 14px; margin-left: 12px;">
                        Confidence: {confidence*100:.0f}%
                    </span>
                </div>
                <div style="text-align: right; font-size: 12px; color: #7C7E8C;">
                    RSI: {technical.get('rsi', 'N/A')} | {technical.get('rsi_signal', 'N/A')}<br/>
                    Trend: {technical.get('sma_trend', 'N/A')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        return recommendation, confidence
        
    except Exception as e:
        st.warning(f"Could not load signal: {str(e)}", icon="⚠️")
        return 'HOLD', 0.5


def display_compact_signal(symbol: str) -> str:
    """
    Display compact signal badge (for cards)
    
    Returns:
        HTML badge string
    """
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(enhanced_deep_search(symbol))
        loop.close()
        
        recommendation = analysis.get('recommendation', 'HOLD')
        confidence = analysis.get('confidence', 0.5)
        
        # Color coding
        if recommendation == 'BUY':
            badge_class = "green-badge"
            icon = "↑"
        elif recommendation == 'SELL':
            badge_class = "red-badge"
            icon = "↓"
        else:
            badge_class = "blue-badge"
            icon = "—"
        
        return f":{badge_class}[{icon} {recommendation} {confidence*100:.0f}%]"
        
    except:
        return ":gray-badge[— HOLD 50%]"


def get_signal_only(symbol: str) -> tuple:
    """
    Get signal without displaying
    
    Returns:
        (recommendation, confidence) tuple
    """
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        analysis = loop.run_until_complete(enhanced_deep_search(symbol))
        loop.close()
        
        return analysis.get('recommendation', 'HOLD'), analysis.get('confidence', 0.5)
    except:
        return 'HOLD', 0.5
