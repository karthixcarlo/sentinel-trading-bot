from fastapi import APIRouter, Depends
from services import auth_manager as auth
from backend.deps import get_current_user, resolve_user_id
import yfinance as yf

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/{user_id}")
async def get_portfolio(user_id: str, current_user: str = Depends(get_current_user)):
    """Retrieves the user's cash and holdings."""
    resolved_id = resolve_user_id(current_user, user_id)
    portfolio = auth.get_user_portfolio(resolved_id)
    if not portfolio.get("success"):
        return {
            "success": True,
            "cash": portfolio.get("cash", 100000.0),
            "positions": portfolio.get("positions", []),
            "orders": portfolio.get("orders", [])
        }
    return portfolio


@router.get("/{user_id}/detail")
async def get_portfolio_detail(user_id: str):
    """Returns portfolio with per-position P&L breakdown. Always returns 200."""
    from backend.routers.trade import _demo_get_cash, _demo_get_positions

    DEMO = {
        "cash": 100000.0,
        "positions": [],
        "portfolio_value": 100000.0,
        "total_holdings_value": 0.0,
        "total_returns": 0.0,
        "returns_pct": 0.0,
        "orders": [],
    }
    try:
        portfolio = auth.get_user_portfolio(user_id)
    except Exception:
        return DEMO

    if not portfolio.get("success"):
        portfolio = {
            "success": True,
            "cash": _demo_get_cash(user_id),
            "positions": _demo_get_positions(user_id),
            "orders": [],
        }

    try:
        cash = float(portfolio.get("cash") or 0.0)
        positions = portfolio.get("positions") or []
        orders = portfolio.get("orders") or []

        enriched_positions = []
        total_holdings_value = 0.0

        for pos in positions:
            symbol = pos.get("symbol", "")
            qty = float(pos.get("quantity") or 0)
            avg_price = float(pos.get("average_price") or 0.0)

            current_price = float(pos.get("current_price") or avg_price)
            try:
                fetch_sym = symbol if symbol.endswith(".NS") else symbol + ".NS"
                hist = yf.Ticker(fetch_sym).history(period="1d")
                if not hist.empty:
                    current_price = round(float(hist["Close"].iloc[-1]), 2)
            except Exception:
                pass

            position_value = qty * current_price
            cost_basis = qty * avg_price
            pnl = round(position_value - cost_basis, 2)
            pnl_pct = round((pnl / cost_basis * 100) if cost_basis > 0 else 0.0, 2)
            total_holdings_value += position_value

            enriched_positions.append({
                "symbol": symbol.replace(".NS", ""),
                "quantity": qty,
                "average_price": round(avg_price, 2),
                "current_price": current_price,
                "position_value": round(position_value, 2),
                "pnl": pnl,
                "pnl_pct": pnl_pct,
            })

        portfolio_value = cash + total_holdings_value
        initial_capital = 100000.0
        total_returns = round(portfolio_value - initial_capital, 2)
        returns_pct = round((total_returns / initial_capital) * 100, 2)

        return {
            "cash": cash,
            "positions": enriched_positions,
            "portfolio_value": round(portfolio_value, 2),
            "total_holdings_value": round(total_holdings_value, 2),
            "total_returns": total_returns,
            "returns_pct": returns_pct,
            "orders": orders,
        }
    except Exception as e:
        print(f"Portfolio Detail Error (inner): {e}")
        return DEMO
