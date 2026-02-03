"""
Fallback Discovery using Yahoo Finance

When Moneycontrol scraping fails, use yfinance to discover stocks.
"""

import yfinance as yf
from typing import List, Dict
from datetime import datetime
import pytz

IST = pytz.timezone('Asia/Kolkata')

# Comprehensive NSE stocks list - 200+ stocks across all sectors
NSE_STOCKS = [
    # Nifty 50 - Large Cap
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "TITAN.NS", "SUNPHARMA.NS", "ULTRACEMCO.NS", "NESTLEIND.NS", "WIPRO.NS",
    "HCLTECH.NS", "TATASTEEL.NS", "POWERGRID.NS", "NTPC.NS", "ONGC.NS",
    "COALINDIA.NS", "M&M.NS", "BAJAJFINSV.NS", "TECHM.NS", "ADANIPORTS.NS",
    "INDUSINDBK.NS", "JSWSTEEL.NS", "DIVISLAB.NS", "TATAMOTORS.NS", "DRREDDY.NS",
    "BRITANNIA.NS", "CIPLA.NS", "GRASIM.NS", "EICHERMOT.NS", "HEROMOTOCO.NS",
    "APOLLOHOSP.NS", "ADANIENT.NS", "HINDALCO.NS", "SBILIFE.NS", "BPCL.NS",
    "TATACONSUM.NS", "VEDL.NS", "SHREECEM.NS", "BAJAJ-AUTO.NS", "HDFCLIFE.NS",
    
    # Nifty Next 50 - Mid Cap Leaders
    "ADANIGREEN.NS", "ADANITRANS.NS", "AMBUJACEM.NS", "BANKBARODA.NS", "BERGEPAINT.NS",
    "BIOCON.NS", "BOSCHLTD.NS", "CADILAHC.NS", "CHOLAFIN.NS", "COLPAL.NS",
    "CONCOR.NS", "DABUR.NS", "DLF.NS", "DMART.NS", "GAIL.NS",
    "GODREJCP.NS", "GODREJPROP.NS", "HAVELLS.NS", "ICICIGI.NS", "ICICIPRULI.NS",
    "INDIGO.NS", "IOC.NS", "IGL.NS", "LICHSGFIN.NS", "LUPIN.NS",
    "MARICO.NS", "MCDOWELL-N.NS", "MUTHOOTFIN.NS", "NMDC.NS", "NYKAA.NS",
    "PAGEIND.NS", "PERSISTENT.NS", "PETRONET.NS", "PFC.NS", "PIDILITIND.NS",
    "PIIND.NS", "PNB.NS", "RECLTD.NS", "SBICARD.NS", "SIEMENS.NS",
    "SRF.NS", "TATAPOWER.NS", "TORNTPHARM.NS", "TRENT.NS", "UBL.NS",
    "UPL.NS", "VEDL.NS", "VOLTAS.NS", "ZOMATO.NS", "ZYDUSLIFE.NS",
    
    # Banking & Financial Services
    "YESBANK.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS", "BANDHANBNK.NS", "RBLBANK.NS",
    "AUBANK.NS", "BAJAJHLDNG.NS", "CANBK.NS", "HDFCAMC.NS", "INDHOTEL.NS",
    "JUBLFOOD.NS", "LTIM.NS", "MAXHEALTH.NS", "MOTHERSON.NS", "MPHASIS.NS",
    
    # IT & Technology
    "COFORGE.NS", "LTTS.NS", "MINDTREE.NS", "OFSS.NS", "TECHM.NS",
    "LTIM.NS", "HAPPSTMNDS.NS", "ROUTE.NS", "INFY.BO", "TCS.BO",
    
    # Pharma & Healthcare
    "ALKEM.NS", "AUROPHARMA.NS", "DRREDDY.NS", "GRANULES.NS", "IPCALAB.NS",
    "LAURUSLABS.NS", "NATCOPHARM.NS", "TORNTPHARM.NS", "ABBOTINDIA.NS", "APOLLOHOSP.NS",
    "FORTIS.NS", "MAXHEALTH.NS", "METROPOLIS.NS", "LALPATHLAB.NS",
    
    # Auto & Auto Components
    "BAJAJ-AUTO.NS", "ESCORTS.NS", "EXIDEIND.NS", "MRF.NS", "MOTHERSON.NS",
    "BALKRISIND.NS", "APOLLOTYRE.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "BOSCHLTD.NS",
    "CUMMINSIND.NS", "EICHERMOT.NS", "ESCORTS.NS", "HEROMOTOCO.NS", "MAHINDRA.NS",
    "MARUTI.NS", "TATAMOTORS.NS", "TVSMOTOR.NS",
    
    # FMCG & Consumer
    "BATAINDIA.NS", "EMAMILTD.NS", "GODREJCP.NS", "HINDUNILVR.NS", "ITC.NS",
    "MARICO.NS", "NESTLEIND.NS", "PGHH.NS", "TATACONSUM.NS", "BRITANNIA.NS",
    "DABUR.NS", "COLPAL.NS", "GILLETTE.NS", "JYOTHYLAB.NS", "RADICO.NS",
    "TATAELXSI.NS", "TITAN.NS", "VBL.NS", "WHIRLPOOL.NS",
    
    # Cement & Construction
    "ACC.NS", "AMBUJACEM.NS", "DALMIACEM.NS", "GRASIM.NS", "JKCEMENT.NS",
    "RAMCOCEM.NS", "SHREECEM.NS", "ULTRACEMCO.NS", "DLF.NS", "GODREJPROP.NS",
    "LODHA.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "SOBHA.NS",
    
    # Metals & Mining
    "HINDALCO.NS", "HINDZINC.NS", "JINDALSTEL.NS", "JSWSTEEL.NS", "NATIONALUM.NS",
    "NMDC.NS", "SAIL.NS", "TATASTEEL.NS", "VEDL.NS", "COALINDIA.NS",
    
    # Energy & Power
    "ADANIGREEN.NS", "ADANIPOWER.NS", "BPCL.NS", "GAIL.NS", "HINDPETRO.NS",
    "IOC.NS", "NTPC.NS", "ONGC.NS", "POWERGRID.NS", "TATAPOWER.NS",
    "RELIANCE.NS", "TORNTPOWER.NS", "JSPL.NS",
    
    # Telecom & Media
    "BHARTIARTL.NS", "IDEA.NS", "ZEEL.NS", "SUNTV.NS", "TV18BRDCST.NS",
    
    # Retail & E-commerce
    "TRENT.NS", "DMART.NS", "SHOPERSTOP.NS", "V-MART.NS", "ZOMATO.NS",
    "POLICYBZR.NS", "NYKAA.NS", "PAYTM.NS",
    
    # Chemicals & Fertilizers
    "AARTI.NS", "BALRAMCHIN.NS", "DEEPAKNTR.NS", "GNFC.NS", "GUJGASLTD.NS",
    "NAVINFLUOR.NS", "PIIND.NS", "SRF.NS", "TATACHEM.NS", "UPL.NS",
    
    # Infrastructure
    "ADANIPORTS.NS", "ADANITRANS.NS", "CONCOR.NS", "GMRINFRA.NS", "IRB.NS",
    "IRCTC.NS", "L&TFH.NS", "PFC.NS", "RECLTD.NS",
    
    # Hotels & Tourism
    "INDHOTEL.NS", "LEMONTREE.NS", "TAJ.NS", "WESTLIFE.NS",
    
    # Textiles
    "ARVIND.NS", "GRASIM.NS", "PAGEIND.NS", "RAYMOND.NS", "SIYARAM.NS",
    "WELSPUNIND.NS",
    
    # Diversified
    "ADANIENT.NS", "ITC.NS", "GODREJIND.NS", "SIEMENS.NS", "ABB.NS",
    "HAVELLS.NS", "CROMPTON.NS", "VOLTAS.NS", "BLUESTARCO.NS",
    
    # New Age Tech & Startups
    "ZOMATO.NS", "PAYTM.NS", "NYKAA.NS", "POLICYBZR.NS", "CARTRADE.NS",
    
    # PSU Banks
    "SBIN.NS", "PNB.NS", "BANKBARODA.NS", "CANBK.NS", "INDUSINDBK.NS",
    "UNIONBANK.NS", "MAHABANK.NS", "BANKINDIA.NS",
]


def discover_with_yfinance(limit_per_category: int = 10) -> Dict[str, List[Dict]]:
    """
    Discover stocks using yfinance by scanning popular NSE stocks.
    
    Args:
        limit_per_category: Number of stocks per category
        
    Returns:
        Dictionary with gainers, losers, and active stocks
    """
    
    stocks_data = []
    
    # Fetch data for all stocks
    for symbol in NSE_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price and previous close
            current_price = info.get('regularMarketPrice', info.get('currentPrice', 0))
            prev_close = info.get('previousClose', current_price)
            volume = info.get('volume', 0)
            
            if current_price > 0 and prev_close > 0:
                change = current_price - prev_close
                change_pct = (change / prev_close) * 100
                
                stocks_data.append({
                    'symbol': symbol,
                    'price': current_price,
                    'change_percent': change_pct,
                    'volume': volume,
                    'source': 'yfinance',
                    'discovered_at': datetime.now(IST)
                })
        except Exception as e:
            # Skip stocks that fail to load
            continue
    
    # Sort into categories
    gainers = sorted(
        [s for s in stocks_data if s['change_percent'] > 0],
        key=lambda x: x['change_percent'],
        reverse=True
    )[:limit_per_category]
    
    losers = sorted(
        [s for s in stocks_data if s['change_percent'] < 0],
        key=lambda x: x['change_percent']
    )[:limit_per_category]
    
    most_active = sorted(
        stocks_data,
        key=lambda x: x['volume'],
        reverse=True
    )[:limit_per_category]
    
    return {
        'top_gainers': gainers,
        'top_losers': losers,
        'most_active': most_active
    }


async def discover_all_fallback(limit_per_category: int = 10) -> Dict[str, List[Dict]]:
    """
    Async wrapper for discover_with_yfinance.
    
    Args:
        limit_per_category: Number of stocks per category
        
    Returns:
        Dictionary with all discovered stocks
    """
    import asyncio
    
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        discover_with_yfinance,
        limit_per_category
    )
    
    return result
