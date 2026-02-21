# -*- coding: utf-8 -*-
"""
Market Hours Utility
Validates if market is open for trading
"""

from datetime import datetime, time
import pytz

def is_market_open():
    """
    Check if NSE/BSE market is currently open
    
    Trading Hours: 9:15 AM - 3:30 PM IST, Monday-Friday
    
    Returns:
        tuple: (is_open: bool, message: str)
    """
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    
    # Check if weekend
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False, "Market is closed (Weekend). Trading hours: Mon-Fri, 9:15 AM - 3:30 PM IST"
    
    # Check if within trading hours (9:15 AM - 3:30 PM)
    market_open = time(9, 15)
    market_close = time(15, 30)
    current_time = now.time()
    
    if current_time < market_open:
        return False, f"Market opens at 9:15 AM IST. Current time: {now.strftime('%I:%M %p IST')}"
    elif current_time > market_close:
        return False, f"Market closed at 3:30 PM IST. Current time: {now.strftime('%I:%M %p IST')}"
    else:
        return True, f"Market is open. Current time: {now.strftime('%I:%M %p IST')}"

def get_market_status():
    """
    Get detailed market status
    
    Returns:
        dict: Market status information
    """
    is_open, message = is_market_open()
    IST = pytz.timezone('Asia/Kolkata')
    now = datetime.now(IST)
    
    # Determine day type
    if now.weekday() >= 5:
        day_type = "Weekend"
    else:
        day_type = "Weekday"
    
    return {
        'is_open': is_open,
        'message': message,
        'current_time': now.strftime('%I:%M %p IST'),
        'trading_hours': '9:15 AM - 3:30 PM IST',
        'trading_days': 'Monday - Friday',
        'day_type': day_type
    }
