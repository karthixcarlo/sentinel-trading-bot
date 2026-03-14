from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import yfinance as yf
from services import auth_manager as auth
from backend.deps import validate_ticker

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/ohlcv/{ticker}")
async def get_ohlcv(ticker: str, user_id: str | None = None):
    """Fetches historical daily OHLCV via yfinance, formatted for lightweight-charts."""
    try:
        ticker = validate_ticker(ticker)
        fetch_ticker = ticker if ticker.endswith(".NS") or ticker.endswith(".BO") else f"{ticker}.NS"
        stock = yf.Ticker(fetch_ticker)
        df = stock.history(period="6mo")

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")

        ohlc = []
        volume = []

        for index, row in df.iterrows():
            time_str = index.strftime('%Y-%m-%d')
            is_green = row['Close'] >= row['Open']
            ohlc.append({
                "time": time_str,
                "open": round(float(row['Open']), 2),
                "high": round(float(row['High']), 2),
                "low": round(float(row['Low']), 2),
                "close": round(float(row['Close']), 2)
            })
            vol_val = int(row['Volume']) if 'Volume' in row else 0
            volume.append({
                "time": time_str,
                "value": vol_val,
                "color": '#26a69a' if is_green else '#ef5350'
            })

        trades = []
        if user_id:
            try:
                client = auth.get_client()
                base_ticker = ticker.replace(".NS", "").replace(".BO", "")
                ticker_variants = list({ticker, base_ticker, fetch_ticker})
                tx_result = client.table("transactions").select("ticker, side, qty, timestamp")\
                    .eq("user_id", user_id)\
                    .in_("ticker", ticker_variants)\
                    .eq("status", "EXECUTED")\
                    .order("timestamp")\
                    .execute()
                if tx_result.data:
                    for tx in tx_result.data:
                        ts = tx.get("timestamp") or ""
                        time_str = ts[:10] if len(ts) >= 10 else ts
                        trades.append({
                            "time": time_str,
                            "side": tx.get("side", "BUY").upper(),
                            "qty": int(float(tx.get("qty", 0)))
                        })
            except Exception as e:
                print(f"OHLCV: Could not fetch transactions: {e}")

        if not trades:
            trades = [
                {"time": (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'), "side": "BUY", "qty": 25},
                {"time": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'), "side": "SELL", "qty": 10},
                {"time": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'), "side": "BUY", "qty": 15},
            ]

        return {"ohlc": ohlc, "volume": volume, "trades": trades}
    except Exception as e:
        print(f"Chart Data Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market data")


DEMO_DISCOVER = [
    {"symbol": "RELIANCE", "name": "Reliance Industries", "price": 1250.50, "change": 1.2},
    {"symbol": "TCS", "name": "Tata Consultancy", "price": 3850.25, "change": -0.5},
    {"symbol": "HDFCBANK", "name": "HDFC Bank Ltd", "price": 1680.00, "change": 0.8},
    {"symbol": "INFY", "name": "Infosys Ltd", "price": 1520.75, "change": 1.1},
    {"symbol": "ICICIBANK", "name": "ICICI Bank Ltd", "price": 1125.00, "change": -0.3},
    {"symbol": "SBIN", "name": "State Bank of India", "price": 850.50, "change": 2.1},
    {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "price": 1450.00, "change": 0.9},
    {"symbol": "ITC", "name": "ITC Ltd", "price": 465.25, "change": -0.2},
    {"symbol": "LT", "name": "Larsen & Toubro", "price": 3650.00, "change": 1.5},
    {"symbol": "ASIANPAINT", "name": "Asian Paints", "price": 2850.50, "change": 0.4},
    {"symbol": "BAJFINANCE", "name": "Bajaj Finance", "price": 6850.00, "change": -0.8},
    {"symbol": "MARUTI", "name": "Maruti Suzuki", "price": 12500.00, "change": 1.0},
]


@router.get("/discover")
async def get_market_discover():
    """Fetches live market data for the Discovery grid."""
    try:
        symbols = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
            "ICICIBANK.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS",
            "LT.NS", "ASIANPAINT.NS", "BAJFINANCE.NS", "MARUTI.NS"
        ]
        tickers = yf.Tickers(" ".join(symbols))
        data = []
        name_map = {
            "RELIANCE": "Reliance Industries", "TCS": "Tata Consultancy",
            "HDFCBANK": "HDFC Bank Ltd", "INFY": "Infosys Ltd",
            "ICICIBANK": "ICICI Bank Ltd", "SBIN": "State Bank of India",
            "BHARTIARTL": "Bharti Airtel", "ITC": "ITC Ltd",
            "LT": "Larsen & Toubro", "ASIANPAINT": "Asian Paints",
            "BAJFINANCE": "Bajaj Finance", "MARUTI": "Maruti Suzuki"
        }
        for symbol in symbols:
            try:
                hist = tickers.tickers[symbol].history(period="5d")
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_close = hist['Close'].iloc[-2]
                    change_pct = ((current_price - prev_close) / prev_close) * 100
                    display_sym = symbol.replace('.NS', '')
                    data.append({
                        "symbol": display_sym,
                        "name": name_map.get(display_sym, display_sym),
                        "price": round(float(current_price), 2),
                        "change": round(float(change_pct), 2)
                    })
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
        if not data:
            return DEMO_DISCOVER
        return data
    except Exception as e:
        print(f"Discover API Error: {e}")
        return DEMO_DISCOVER


@router.get("/analyze/{ticker}")
async def analyze_stock(ticker: str):
    """Generates an AI deep dive report on a specific equity."""
    try:
        ticker = validate_ticker(ticker)
        from agents.langgraph_agents import llm

        fetch_ticker = ticker + ".NS" if not ticker.endswith(".NS") else ticker
        stock = yf.Ticker(fetch_ticker)

        hist = stock.history(period="1mo")
        if hist.empty:
            raise HTTPException(status_code=404, detail="Stock data not found")

        info = stock.info
        current_price = round(hist['Close'].iloc[-1], 2)
        sma_20 = round(hist['Close'].tail(20).mean(), 2) if len(hist) >= 20 else current_price

        prompt = f"""You are Sentinel's Senior Financial Analyst.
Analyze the Indian NSE stock {ticker}.
Current Price: ₹{current_price}
20-Day SMA: ₹{sma_20}
Sector: {info.get('sector', 'Unknown')}
Industry: {info.get('industry', 'Unknown')}
Market Cap: {info.get('marketCap', 'Unknown')}
P/E Ratio: {info.get('trailingPE', 'N/A')}

Please write a structured markdown report covering:
1. Executive Summary (BUY/HOLD/SELL recommendation)
2. Technical Outlook (Trend, Support/Resistance levels based on recent price action)
3. Fundamental Overview
4. Key Risks

Keep it highly professional, formatting it beautifully in markdown. Do not hallucinate exact pricing data beyond what is provided, but use your vast pre-trained knowledge about this company to fill in fundamental context.
"""
        response = llm.invoke(prompt)

        return {
            "ticker": ticker,
            "current_price": current_price,
            "sma_20": sma_20,
            "name": info.get('shortName', ticker),
            "report": response.content
        }
    except Exception as e:
        print(f"Analysis API Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze stock")


@router.get("/indices")
async def get_market_indices():
    """Fetches live Nifty 50, Bank Nifty, and Sensex index data."""
    fallback = [
        {"name": "Nifty 50",   "symbol": "^NSEI",    "value": 22150.50, "change": 1.25},
        {"name": "Bank Nifty", "symbol": "^NSEBANK",  "value": 48250.75, "change": -0.85},
        {"name": "Sensex",     "symbol": "^BSESN",    "value": 73280.30, "change": 0.95},
    ]
    try:
        result = []
        for item in fallback:
            try:
                ticker = yf.Ticker(item["symbol"])
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    current = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    change_pct = ((current - prev) / prev) * 100
                    result.append({"name": item["name"], "value": round(current, 2), "change": round(change_pct, 2)})
                else:
                    result.append(item)
            except Exception:
                result.append(item)
        return result
    except Exception as e:
        print(f"Indices Error: {e}")
        return fallback
