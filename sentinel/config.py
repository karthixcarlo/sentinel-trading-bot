"""
Configuration Management

Loads configuration from environment variables and .env file.
Supports both US markets (Alpaca) and Indian markets (Zerodha/others).
"""

import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Market Selection
MARKET_REGION = os.getenv("MARKET_REGION", "USA").upper()  # "USA" or "INDIA"

# Alpaca API Configuration (US Markets)
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Zerodha Kite Connect Configuration (Indian Markets)
ZERODHA_API_KEY = os.getenv("ZERODHA_API_KEY")
ZERODHA_API_SECRET = os.getenv("ZERODHA_API_SECRET")
ZERODHA_REQUEST_TOKEN = os.getenv("ZERODHA_REQUEST_TOKEN")  # Generated during login flow
ZERODHA_ACCESS_TOKEN = os.getenv("ZERODHA_ACCESS_TOKEN")  # Generated from request_token

# Indian Market Settings
INDIAN_EXCHANGE = os.getenv("INDIAN_EXCHANGE", "NSE")  # "NSE" or "BSE"

def has_alpaca_credentials() -> bool:
    """Check if Alpaca credentials are configured"""
    return bool(ALPACA_API_KEY and ALPACA_SECRET_KEY)

def has_zerodha_credentials() -> bool:
    """Check if Zerodha credentials are configured"""
    return bool(ZERODHA_API_KEY and ZERODHA_API_SECRET)

def is_indian_market() -> bool:
    """Check if configured for Indian market"""
    return MARKET_REGION == "INDIA"

def is_us_market() -> bool:
    """Check if configured for US market"""
    return MARKET_REGION == "USA"
