from fastapi import APIRouter, Depends, HTTPException, Request
from agents.agent_service import get_agent_service
from backend.deps import get_current_user, limiter

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.post("/start")
@limiter.limit("10/minute")
async def start_autonomous_trading(request: Request, current_user: str = Depends(get_current_user)):
    """Start the autonomous trading agent."""
    try:
        agent_service = get_agent_service()
        await agent_service.start_autonomous_mode()
        return {"status": "success", "message": "Autonomous trading started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop")
@limiter.limit("10/minute")
async def stop_autonomous_trading(request: Request, current_user: str = Depends(get_current_user)):
    """Stop the autonomous trading agent."""
    try:
        agent_service = get_agent_service()
        await agent_service.stop_autonomous_mode()
        return {"status": "success", "message": "Autonomous trading stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
@limiter.limit("30/minute")
async def get_agent_status(request: Request):
    """Get current status of the autonomous agent."""
    try:
        agent_service = get_agent_service()
        return agent_service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/portfolio")
@limiter.limit("20/minute")
async def get_agent_portfolio(request: Request):
    """Get current portfolio managed by the agent."""
    try:
        agent_service = get_agent_service()
        return agent_service.get_portfolio()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/thoughts")
@limiter.limit("20/minute")
async def get_agent_thoughts(request: Request, limit: int = 50):
    """Get recent agent thoughts/logs."""
    try:
        agent_service = get_agent_service()
        return {"thoughts": agent_service.get_thoughts(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
@limiter.limit("20/minute")
async def get_agent_trades(request: Request, limit: int = 50):
    """Get trade history."""
    try:
        agent_service = get_agent_service()
        return {"trades": agent_service.get_trade_history(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
