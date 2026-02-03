"""
Stock name to symbol mapping for NSE stocks
Makes it easier to search by company name instead of symbol
"""

# Popular NSE stocks with their names
STOCK_NAME_MAP = {
    # Major indices components
    "Reliance": "RELIANCE.NS",
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Tata Consultancy Services": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "HDFC": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "ICICI": "ICICIBANK.NS",
    "Infosys": "INFY.NS",
    "Infy": "INFY.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Airtel": "BHARTIARTL.NS",
    "State Bank": "SBIN.NS",
    "SBI": "SBIN.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "HUL": "HINDUNILVR.NS",
    "ITC": "ITC.NS",
    "Kotak Bank": "KOTAKBANK.NS",
    "Kotak Mahindra": "KOTAKBANK.NS",
    "Larsen": "LT.NS",
    "L&T": "LT.NS",
    "Axis Bank": "AXISBANK.NS",
    "Axis": "AXISBANK.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "Maruti": "MARUTI.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Bajaj Finance": "BAJFINANCE.NS",
    "Bajaj": "BAJFINANCE.NS",
    "Wipro": "WIPRO.NS",
    "HCL Tech": "HCLTECH.NS",
    "HCL": "HCLTECH.NS",
    "Sun Pharma": "SUNPHARMA.NS",
    "Sun Pharmaceutical": "SUNPHARMA.NS",
    "Titan": "TITAN.NS",
    "Nestle": "NESTLEIND.NS",
    "Power Grid": "POWERGRID.NS",
    "NTPC": "NTPC.NS",
    "Tech Mahindra": "TECHM.NS",
    "Mahindra": "M&M.NS",
    "M&M": "M&M.NS",
    "Coal India": "COALINDIA.NS",
    "Tata Steel": "TATASTEEL.NS",
    "Tata Motors": "TATAMOTORS.NS",
    "Adani Ports": "ADANIPORTS.NS",
    "Adani": "ADANIPORTS.NS",
    "UltraTech": "ULTRACEMCO.NS",
    "UltraTech Cement": "ULTRACEMCO.NS",
    "JSW Steel": "JSWSTEEL.NS",
    "JSW": "JSWSTEEL.NS",
    "IndusInd Bank": "INDUSINDBK.NS",
    "IndusInd": "INDUSINDBK.NS",
    "Bajaj Auto": "BAJAJ-AUTO.NS",
    "Eicher Motors": "EICHERMOT.NS",
    "Eicher": "EICHERMOT.NS",
    "Britannia": "BRITANNIA.NS",
    "Grasim": "GRASIM.NS",
    "Cipla": "CIPLA.NS",
    "Dr Reddy": "DRREDDY.NS",
    "Divis Lab": "DIVISLAB.NS",
    "Shree Cement": "SHREECEM.NS",
    "Tata Consumer": "TATACONSUM.NS",
    "Hero MotoCorp": "HEROMOTOCO.NS",
    "Hero": "HEROMOTOCO.NS",
    "Apollo Hospital": "APOLLOHOSP.NS",
    "Apollo": "APOLLOHOSP.NS",
    "ONGC": "ONGC.NS",
    "IOC": "IOC.NS",
    "Indian Oil": "IOC.NS",
    "BPCL": "BPCL.NS",
    "Bharat Petroleum": "BPCL.NS",
    "GAIL": "GAIL.NS",
    "Adani Green": "ADANIGREEN.NS",
    "Adani Enterprises": "ADANIENT.NS",
    "Adani Total Gas": "ATGL.NS",
    "Pidilite": "PIDILITIND.NS",
    "Divi's Lab": "DIVISLAB.NS",
    "SBI Life": "SBILIFE.NS",
    "ICICI Lombard": "ICICIGI.NS",
    "HDFC Life": "HDFCLIFE.NS",
    "Bajaj Finserv": "BAJAJFINSV.NS",
    "UPL": "UPL.NS",
    "Berger Paints": "BERGEPAINT.NS",
    "Dabur": "DABUR.NS",
    "Godrej Consumer": "GODREJCP.NS",
    "Marico": "MARICO.NS",
    "Avenue Supermarts": "DMART.NS",
    "DMart": "DMART.NS",
    "Zomato": "ZOMATO.NS",
    "Paytm": "PAYTM.NS",
    "Nykaa": "NYKAA.NS",
    "Policy Bazaar": "POLICYBZR.NS",
    "LIC": "LICI.NS",
    "Vedanta": "VEDL.NS",
    "Hindalco": "HINDALCO.NS",
    "Tata Power": "TATAPOWER.NS",
    "Adani Power": "ADANIPOWER.NS",
}

def search_stock(query):
    """
    Search for stock by name or symbol
    Returns list of matching (name, symbol) tuples
    """
    if not query:
        return []
    
    query = query.upper().strip()
    matches = []
    
    # Direct symbol match
    if query.endswith('.NS'):
        symbol = query
        name = query.replace('.NS', '')
        return [(name, symbol)]
    
    # Check if adding .NS would be a direct match
    potential_symbol = f"{query}.NS"
    for name, symbol in STOCK_NAME_MAP.items():
        if symbol == potential_symbol:
            return [(name, symbol)]
    
    # Partial name match
    for name, symbol in STOCK_NAME_MAP.items():
        if query in name.upper():
            matches.append((name, symbol))
    
    # If no matches, try treating input as symbol
    if not matches:
        if not query.endswith('.NS'):
            symbol = f"{query}.NS"
        else:
            symbol = query
        matches.append((query, symbol))
    
    return matches

def get_all_stock_options():
    """Get all stock names for autocomplete"""
    options = []
    for name, symbol in STOCK_NAME_MAP.items():
        options.append(f"{name} ({symbol.replace('.NS', '')})")
    return sorted(options)
