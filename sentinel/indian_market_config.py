"""
Indian Market Configuration

Market-specific parameters for NSE/BSE trading including:
- Trading hours and sessions (IST timezone)
- Regulatory parameters (SEBI rules)
- Tax rates (STT, CTT, GST)
- Circuit breaker limits
- Auto square-off timings
"""

from datetime import time, datetime, timedelta
from typing import Dict, List, Tuple
import pytz

# Timezone
IST = pytz.timezone('Asia/Kolkata')

# Market Hours (IST)
MARKET_OPEN_TIME = time(9, 15)  # 9:15 AM
MARKET_CLOSE_TIME = time(15, 30)  # 3:30 PM

# Pre-market session
PRE_MARKET_START = time(9, 0)  # 9:00 AM
PRE_MARKET_END = time(9, 15)  # 9:15 AM

# Post-market session
POST_MARKET_START = time(15, 30)  # 3:30 PM
POST_MARKET_END = time(16, 0)  # 4:00 PM

# Auto square-off time (brokers typically square-off before market close)
AUTO_SQUAREOFF_TIME = time(15, 20)  # 3:20 PM (10 mins before close)

# Tax Rates (as decimals)
class TaxRates:
    """Indian tax rates for trading"""
    
    # STT (Securities Transaction Tax)
    STT_EQUITY_INTRADAY_SELL = 0.00025  # 0.025% on sell side only
    STT_EQUITY_DELIVERY_BUY = 0.001     # 0.1% on buy
    STT_EQUITY_DELIVERY_SELL = 0.001    # 0.1% on sell
    STT_FUTURES_SELL = 0.0001            # 0.01% on sell
    STT_OPTIONS_SELL = 0.000625          # 0.0625% on sell (premium)
    
    # CTT (Commodity Transaction Tax)
    CTT_COMMODITIES = 0.0001             # 0.01% on sell
    
    # Exchange Transaction Charges (approximate, varies by exchange)
    NSE_EQUITY_TRANSACTION = 0.0000345   # 0.00345% (NSE equity)
    BSE_EQUITY_TRANSACTION = 0.0000375   # 0.00375% (BSE equity)
    NSE_FNO_TRANSACTION = 0.000019       # 0.0019% (NSE F&O)
    
    # GST on brokerage and charges
    GST_RATE = 0.18  # 18% GST
    
    # SEBI Turnover Charges
    SEBI_CHARGES = 0.0000001  # ₹10 per crore (negligible)


class CircuitLimits:
    """Circuit breaker limits for Indian markets"""
    
    # Individual stock circuit limits (percentage from previous close)
    # These can vary based on stock category
    LOWER_CIRCUIT_20 = -0.20  # 20% lower circuit
    UPPER_CIRCUIT_20 = 0.20   # 20% upper circuit
    
    LOWER_CIRCUIT_10 = -0.10  # 10% lower circuit
    UPPER_CIRCUIT_10 = 0.10   # 10% upper circuit
    
    LOWER_CIRCUIT_5 = -0.05   # 5% lower circuit
    UPPER_CIRCUIT_5 = 0.05    # 5% upper circuit
    
    # Index-level circuit breakers (market-wide halts)
    INDEX_10_PERCENT = 0.10   # 15-min halt
    INDEX_15_PERCENT = 0.15   # 45-min to 1-hour halt
    INDEX_20_PERCENT = 0.20   # Market closed for the day


class TradingSegments:
    """NSE/BSE trading segments"""
    EQUITY_CASH = "EQ"           # Equity cash segment
    EQUITY_DELIVERY = "EQ_D"     # Equity delivery
    FUTURES = "FUT"              # Futures
    OPTIONS = "OPT"              # Options
    CURRENCY = "CUR"             # Currency derivatives
    COMMODITY = "COM"            # Commodity derivatives


class MarketHolidays:
    """
    Indian stock market holidays for 2026
    Note: This should be updated annually or fetched from exchange APIs
    """
    
    # 2026 NSE/BSE holidays (sample - update as needed)
    HOLIDAYS_2026 = [
        "2026-01-26",  # Republic Day
        "2026-03-14",  # Holi
        "2026-03-30",  # Ram Navami
        "2026-04-02",  # Mahavir Jayanti
        "2026-04-10",  # Good Friday
        "2026-04-21",  # Id-Ul-Fitr
        "2026-05-01",  # Maharashtra Day
        "2026-06-28",  # Id-Ul-Zuha (Bakrid)
        "2026-07-17",  # Muharram
        "2026-08-15",  # Independence Day
        "2026-08-26",  # Janmashtami
        "2026-09-16",  # Ganesh Chaturthi
        "2026-10-02",  # Gandhi Jayanti / Dussehra
        "2026-10-21",  # Diwali Laxmi Pujan
        "2026-10-22",  # Diwali Balipratipada
        "2026-11-16",  # Gurunanak Jayanti
        "2026-12-25",  # Christmas
    ]


class SEBIRegulations:
    """SEBI regulatory parameters"""
    
    # Margin requirements
    MIN_INTRADAY_MARGIN = 0.20  # 20% minimum margin for intraday
    MAX_INTRADAY_LEVERAGE = 5   # Max 5x leverage (1/MIN_MARGIN)
    
    # Position limits for index options (per entity)
    INDEX_OPTIONS_NET_LIMIT = 50_00_00_00_000  # ₹5,000 crore
    INDEX_OPTIONS_GROSS_LIMIT = 100_00_00_00_000  # ₹10,000 crore
    
    # Day trading requirements
    INTRADAY_SQUAREOFF_MANDATORY = True  # Must close positions same day
    
    # Pattern Day Trader rules (less strict than US)
    MIN_EQUITY_FOR_DAY_TRADING = 0  # No minimum (unlike US $25k rule)


def is_market_open(dt: datetime = None) -> bool:
    """
    Check if market is currently open.
    
    Args:
        dt: Datetime to check (defaults to current IST time)
        
    Returns:
        True if market is open, False otherwise
    """
    if dt is None:
        dt = datetime.now(IST)
    
    # Convert to IST if not already
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    else:
        dt = dt.astimezone(IST)
    
    # Check if weekend
    if dt.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    
    # Check if holiday
    date_str = dt.strftime("%Y-%m-%d")
    if date_str in MarketHolidays.HOLIDAYS_2026:
        return False
    
    # Check if within trading hours
    current_time = dt.time()
    return MARKET_OPEN_TIME <= current_time <= MARKET_CLOSE_TIME


def time_until_market_open() -> timedelta:
    """
    Calculate time until next market open.
    
    Returns:
        Timedelta until market opens
    """
    now = datetime.now(IST)
    
    if is_market_open(now):
        return timedelta(0)
    
    # If after market close today, check tomorrow
    if now.time() > MARKET_CLOSE_TIME:
        next_open = now + timedelta(days=1)
    else:
        next_open = now
    
    # Find next trading day
    while next_open.weekday() >= 5 or next_open.strftime("%Y-%m-%d") in MarketHolidays.HOLIDAYS_2026:
        next_open += timedelta(days=1)
    
    # Set to market open time
    next_open = next_open.replace(
        hour=MARKET_OPEN_TIME.hour,
        minute=MARKET_OPEN_TIME.minute,
        second=0,
        microsecond=0
    )
    
    return next_open - now


def should_auto_squareoff(dt: datetime = None) -> bool:
    """
    Check if it's time for auto square-off of intraday positions.
    
    Args:
        dt: Datetime to check (defaults to current IST time)
        
    Returns:
        True if should square-off, False otherwise
    """
    if dt is None:
        dt = datetime.now(IST)
    
    # Convert to IST
    if dt.tzinfo is None:
        dt = IST.localize(dt)
    else:
        dt = dt.astimezone(IST)
    
    # Check if past auto-squareoff time
    return dt.time() >= AUTO_SQUAREOFF_TIME


def calculate_indian_trading_costs(
    transaction_value: float,
    side: str,
    segment: str = TradingSegments.EQUITY_CASH,
    is_intraday: bool = True,
    exchange: str = "NSE"
) -> Dict[str, float]:
    """
    Calculate all trading costs for Indian markets.
    
    Args:
        transaction_value: Total transaction value in INR
        side: "BUY" or "SELL"
        segment: Trading segment (equity, futures, options)
        is_intraday: True for intraday, False for delivery
        exchange: "NSE" or "BSE"
        
    Returns:
        Dictionary with breakdown of all costs
    """
    costs = {
        "stt": 0.0,
        "exchange_charges": 0.0,
        "sebi_charges": 0.0,
        "gst": 0.0,
        "total": 0.0
    }
    
    # STT calculation
    if segment == TradingSegments.EQUITY_CASH:
        if is_intraday:
            # STT only on sell side for intraday
            if side == "SELL":
                costs["stt"] = transaction_value * TaxRates.STT_EQUITY_INTRADAY_SELL
        else:
            # STT on both buy and sell for delivery
            if side == "BUY":
                costs["stt"] = transaction_value * TaxRates.STT_EQUITY_DELIVERY_BUY
            else:
                costs["stt"] = transaction_value * TaxRates.STT_EQUITY_DELIVERY_SELL
    elif segment == TradingSegments.FUTURES:
        if side == "SELL":
            costs["stt"] = transaction_value * TaxRates.STT_FUTURES_SELL
    elif segment == TradingSegments.OPTIONS:
        if side == "SELL":
            costs["stt"] = transaction_value * TaxRates.STT_OPTIONS_SELL
    
    # Exchange transaction charges
    if exchange == "NSE":
        if segment in [TradingSegments.EQUITY_CASH, TradingSegments.EQUITY_DELIVERY]:
            costs["exchange_charges"] = transaction_value * TaxRates.NSE_EQUITY_TRANSACTION
        else:
            costs["exchange_charges"] = transaction_value * TaxRates.NSE_FNO_TRANSACTION
    else:  # BSE
        costs["exchange_charges"] = transaction_value * TaxRates.BSE_EQUITY_TRANSACTION
    
    # SEBI charges
    costs["sebi_charges"] = transaction_value * TaxRates.SEBI_CHARGES
    
    # GST (on exchange charges + SEBI charges)
    taxable_amount = costs["exchange_charges"] + costs["sebi_charges"]
    costs["gst"] = taxable_amount * TaxRates.GST_RATE
    
    # Total costs
    costs["total"] = sum(costs.values())
    
    return costs


def get_indian_symbol_format(symbol: str, exchange: str = "NSE") -> str:
    """
    Convert symbol to Yahoo Finance format for Indian stocks.
    
    Args:
        symbol: Stock symbol (e.g., "RELIANCE", "TCS")
        exchange: "NSE" or "BSE"
        
    Returns:
        Yahoo Finance formatted symbol (e.g., "RELIANCE.NS", "TCS.BO")
    """
    suffix = ".NS" if exchange == "NSE" else ".BO"
    
    # Remove suffix if already present
    if symbol.endswith(".NS") or symbol.endswith(".BO"):
        symbol = symbol.split(".")[0]
    
    return f"{symbol}{suffix}"


# Popular Indian stock symbols
POPULAR_INDIAN_STOCKS = {
    "NIFTY_50": [
        "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
        "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
        "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "BAJFINANCE",
        "HCLTECH", "WIPRO", "SUNPHARMA", "TITAN", "ULTRACEMCO"
    ],
    "BANK_NIFTY": [
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK",
        "INDUSINDBK", "BANDHANBNK", "FEDERALBNK", "IDFCFIRSTB", "PNB"
    ],
    "IT_SECTOR": [
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM", "LTIM", "PERSISTENT"
    ]
}


# Index symbols
INDIAN_INDICES = {
    "NIFTY": "^NSEI",      # Nifty 50
    "BANKNIFTY": "^NSEBANK",  # Bank Nifty
    "SENSEX": "^BSESN",    # BSE Sensex
    "NIFTY_IT": "^CNXIT",  # Nifty IT
    "NIFTY_MIDCAP": "^NSEMDCP50"  # Nifty Midcap 50
}
