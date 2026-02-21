# -*- coding: utf-8 -*-
"""
Stock Discovery - Find top gainers, losers, and most active NSE stocks
"""

import streamlit as st
import sys
import os

PAGES_DIR = os.path.dirname(os.path.abspath(__file__))
DASH_DIR  = os.path.dirname(PAGES_DIR)
ROOT_DIR  = os.path.dirname(DASH_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, DASH_DIR)

from layout import setup_page_config, render_navigation, apply_groww_theme

setup_page_config("Stock Discovery", "🔍")
apply_groww_theme()
render_navigation()

# ── NSE stock universe for discovery ──────────────────────────
NSE_STOCKS = [
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","INFY.NS","ICICIBANK.NS",
    "HINDUNILVR.NS","SBIN.NS","BHARTIARTL.NS","KOTAKBANK.NS","BAJFINANCE.NS",
    "AXISBANK.NS","MARUTI.NS","ASIANPAINT.NS","LTIM.NS","SUNPHARMA.NS",
    "TITAN.NS","ONGC.NS","WIPRO.NS","ULTRACEMCO.NS","NESTLEIND.NS",
    "POWERGRID.NS","NTPC.NS","HCLTECH.NS","TECHM.NS","SHREECEM.NS",
    "DIVISLAB.NS","DRREDDY.NS","CIPLA.NS","BPCL.NS","COALINDIA.NS",
]

@st.cache_data(ttl=180)
def fetch_stock_data(symbols):
    """Fetch price data for a list of symbols via yfinance."""
    try:
        import yfinance as yf
        results = []
        for sym in symbols:
            try:
                t = yf.Ticker(sym)
                hist = t.history(period="2d")
                if len(hist) >= 2:
                    current = float(hist["Close"].iloc[-1])
                    prev    = float(hist["Close"].iloc[-2])
                    chg_pct = ((current - prev) / prev) * 100
                    vol     = int(hist["Volume"].iloc[-1])
                    results.append({
                        "symbol": sym,
                        "name": sym.replace(".NS", ""),
                        "price": current,
                        "change_pct": chg_pct,
                        "volume": vol,
                    })
            except Exception:
                pass
        return results
    except Exception:
        return []

# ── Page ──────────────────────────────────────────────────────
st.title("Stock Discovery")
st.caption("Live NSE/BSE data — 3-minute cache")

with st.spinner("Fetching live market data..."):
    all_stocks = fetch_stock_data(NSE_STOCKS)

if not all_stocks:
    st.error("Could not fetch market data. Please try again in a moment.")
    st.stop()

gainers = sorted([s for s in all_stocks if s["change_pct"] > 0], key=lambda x: x["change_pct"], reverse=True)
losers  = sorted([s for s in all_stocks if s["change_pct"] < 0], key=lambda x: x["change_pct"])
active  = sorted(all_stocks, key=lambda x: x["volume"], reverse=True)

def render_stock_cards(stocks, max_cards=12):
    if not stocks:
        st.info("No stocks found.")
        return
    for i in range(0, min(len(stocks), max_cards), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = i + j
            if idx < len(stocks):
                s = stocks[idx]
                color = "#00D09C" if s["change_pct"] >= 0 else "#EB5B3C"
                with col:
                    with st.container(border=True):
                        st.markdown(f"**{s['name']}**")
                        st.markdown(
                            f"₹{s['price']:,.2f} &nbsp; "
                            f"<span style='color:{color};font-weight:700;'>{s['change_pct']:+.2f}%</span>",
                            unsafe_allow_html=True
                        )
                        if st.button("Analyze", key=f"disc_{s['symbol']}_{i}_{j}", use_container_width=True):
                            st.session_state["selected_stock"] = s["symbol"]
                            st.switch_page("pages/3_Stock_Analyzer.py")

tab1, tab2, tab3 = st.tabs(["Top Gainers", "Top Losers", "Most Active"])

with tab1:
    st.subheader(f"Top Gainers ({len(gainers)})")
    render_stock_cards(gainers)

with tab2:
    st.subheader(f"Top Losers ({len(losers)})")
    render_stock_cards(losers)

with tab3:
    st.subheader(f"Most Active ({len(active)})")
    render_stock_cards(active)

st.markdown("---")
if st.button("Refresh Data"):
    fetch_stock_data.clear()
    st.rerun()
