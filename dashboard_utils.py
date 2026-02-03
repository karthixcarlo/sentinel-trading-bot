"""
Dashboard Utilities

Helper functions for the Streamlit dashboard including:
- Async operation wrappers
- Data formatting
- Color coding
- Session state management
"""

import asyncio
import streamlit as st
from typing import Any, Callable, Optional
from datetime import datetime
from sentinel.indian_market_config import IST
import pytz


def run_async(coro):
    """
    Run async coroutine in Streamlit synchronous context.
    
    Args:
        coro: Async coroutine to run
        
    Returns:
        Result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def format_currency(amount: float, currency: str = "INR", decimals: int = 2) -> str:
    """
    Format currency with proper symbol and decimals.
    
    Args:
        amount: Amount to format
        currency: Currency code (INR or USD)
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    symbol = "₹" if currency == "INR" else "$"
    
    # Format with Indian numbering system for INR
    if currency == "INR" and abs(amount) >= 1000:
        # Convert to lakhs/crores
        if abs(amount) >= 10000000:  # 1 crore
            return f"{symbol}{amount/10000000:.{decimals}f}Cr"
        elif abs(amount) >= 100000:  # 1 lakh
            return f"{symbol}{amount/100000:.{decimals}f}L"
    
    return f"{symbol}{amount:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2, show_sign: bool = True) -> str:
    """
    Format percentage with optional sign.
    
    Args:
        value: Percentage value (e.g., 0.05 for 5%)
        decimals: Number of decimal places
        show_sign: Whether to show + sign for positive values
        
    Returns:
        Formatted percentage string
    """
    pct = value * 100 if abs(value) < 1 else value
    sign = "+" if pct > 0 and show_sign else ""
    return f"{sign}{pct:.{decimals}f}%"


def get_color_for_value(value: float, reverse: bool = False) -> str:
    """
    Get color for a numeric value (green for positive, red for negative).
    
    Args:
        value: Numeric value
        reverse: If True, reverse the color scheme
        
    Returns:
        Color name (green, red, or gray)
    """
    if value > 0:
        return "red" if reverse else "green"
    elif value < 0:
        return "green" if reverse else "red"
    else:
        return "gray"


def display_metric_card(label: str, value: str, delta: Optional[str] = None, 
                       delta_color: str = "normal"):
    """
    Display a metric card with optional delta.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional change/delta value
        delta_color: Color scheme for delta (normal, inverse, off)
    """
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def show_success(message: str):
    """Show success notification."""
    st.success(f"✅ {message}")


def show_error(message: str):
    """Show error notification."""
    st.error(f"❌ {message}")


def show_warning(message: str):
    """Show warning notification."""
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    """Show info notification."""
    st.info(f"ℹ️ {message}")


def init_session_state(key: str, default_value: Any):
    """
    Initialize session state variable if not exists.
    
    Args:
        key: Session state key
        default_value: Default value if key doesn't exist
    """
    if key not in st.session_state:
        st.session_state[key] = default_value


def get_market_status_color(is_open: bool) -> str:
    """
    Get color for market status.
    
    Args:
        is_open: Whether market is open
        
    Returns:
        Color name
    """
    return "green" if is_open else "red"


def format_time_ist(dt: datetime = None) -> str:
    """
    Format datetime in IST timezone.
    
    Args:
        dt: Datetime object (defaults to now)
        
    Returns:
        Formatted time string
    """
    if dt is None:
        dt = datetime.now(IST)
    elif dt.tzinfo is None:
        dt = IST.localize(dt)
    else:
        dt = dt.astimezone(IST)
    
    return dt.strftime("%I:%M %p IST")


def format_datetime_ist(dt: datetime = None) -> str:
    """
    Format datetime with date in IST timezone.
    
    Args:
        dt: Datetime object (defaults to now)
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        dt = datetime.now(IST)
    elif dt.tzinfo is None:
        dt = IST.localize(dt)
    else:
        dt = dt.astimezone(IST)
    
    return dt.strftime("%d %b %Y, %I:%M %p IST")


def create_download_button(data: str, filename: str, label: str = "Download"):
    """
    Create a download button for data.
    
    Args:
        data: Data to download
        filename: Filename for download
        label: Button label
    """
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime="text/csv"
    )


def display_loading(message: str = "Loading..."):
    """
    Display loading spinner.
    
    Args:
        message: Loading message
    """
    return st.spinner(message)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails
        
    Returns:
        Division result or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except:
        return default


def truncate_text(text: str, max_length: int = 50) -> str:
    """
    Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
