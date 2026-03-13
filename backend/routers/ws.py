import os
import asyncio
import logging
from datetime import datetime
from fastapi import APIRouter, WebSocket, HTTPException
import jwt as _jwt
from agent_service import get_agent_service

router = APIRouter(tags=["websocket"])

logger = logging.getLogger("sentinel")
_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET", "")

# Store active WebSocket connections (use a set for O(1) removal)
active_connections: set = set()


async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients, pruning dead ones."""
    dead = []
    for connection in list(active_connections):
        try:
            await connection.send_json(message)
        except Exception:
            dead.append(connection)
    for conn in dead:
        active_connections.discard(conn)


@router.websocket("/ws/neural-feed")
async def websocket_neural_feed(websocket: WebSocket):
    """
    Streams the live 'thoughts' from the Sentinel Agent
    directly to the client for the 'God Mode' dashboard.
    Accepts an optional ?token= query param for authentication.
    """
    # Authenticate WebSocket: check optional token query param
    token = websocket.query_params.get("token")
    if token and _JWT_SECRET:
        try:
            _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"], audience="authenticated")
        except _jwt.InvalidTokenError:
            await websocket.close(code=4001, reason="Invalid token")
            return
    # Accept connection (allow unauthenticated in demo mode when no JWT secret is configured)
    await websocket.accept()
    active_connections.add(websocket)

    # Set the WebSocket callback on the agent service
    agent_service = get_agent_service()
    original_callback = agent_service.websocket_callback

    async def ws_callback(thought: dict):
        try:
            await websocket.send_json(thought)
        except Exception:
            pass  # connection may have died between heartbeats

    agent_service.set_websocket_callback(ws_callback)

    try:
        # Send initial connection message
        await websocket.send_json({
            "agent": "System",
            "thought": "Neural feed connected - receiving live agent thoughts",
            "timestamp": datetime.now().isoformat()
        })

        # Keep connection alive and send periodic heartbeats
        while True:
            await asyncio.sleep(3)
            await websocket.send_json({
                "agent": "Heartbeat",
                "thought": "...",
                "timestamp": datetime.now().isoformat()
            })
    except Exception as e:
        logger.info(f"WebSocket connection closed: {e}")
    finally:
        active_connections.discard(websocket)
        agent_service.set_websocket_callback(original_callback)


@router.get("/api/autonomous/status")
async def get_autonomous_status():
    """
    Lightweight endpoint: returns only the fields the UI needs to reflect
    server-side autonomous state (running flag + start_time).
    """
    try:
        svc = get_agent_service()
        return {
            "running": svc.status.value == "running",
            "status": svc.status.value,
            "start_time": svc.start_time.isoformat() + "Z" if svc.start_time else None,
            "workflow_id": svc.workflow_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
