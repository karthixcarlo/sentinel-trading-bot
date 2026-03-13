import os
import json
import sqlite3
from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from agent_service import get_agent_service
from backend.deps import get_current_user, resolve_user_id, ROOT_DIR

router = APIRouter(prefix="/api/settings", tags=["settings"])

_DEMO_DB = os.path.join(ROOT_DIR, "sentinel.db")

_DEFAULT_SETTINGS = {
    "risk_appetite": "Moderate",
    "max_position_size": 10,
    "allowed_sectors": ["IT", "Banking", "Energy", "Automobile"]
}


class UserSettings(BaseModel):
    risk_appetite: str
    max_position_size: int
    allowed_sectors: List[str]


def _ensure_settings_table():
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS agent_settings (
        user_id TEXT PRIMARY KEY,
        risk_appetite TEXT DEFAULT 'Moderate',
        max_position_size INTEGER DEFAULT 10,
        allowed_sectors TEXT DEFAULT '[]'
    )""")
    conn.commit()
    conn.close()


def _load_settings(user_id: str) -> dict:
    _ensure_settings_table()
    conn = sqlite3.connect(_DEMO_DB)
    row = conn.execute(
        "SELECT risk_appetite, max_position_size, allowed_sectors FROM agent_settings WHERE user_id=?",
        (user_id,)
    ).fetchone()
    conn.close()
    if row:
        return {
            "risk_appetite": row[0],
            "max_position_size": row[1],
            "allowed_sectors": json.loads(row[2] or "[]")
        }
    return dict(_DEFAULT_SETTINGS)


def _save_settings(user_id: str, s: dict):
    _ensure_settings_table()
    conn = sqlite3.connect(_DEMO_DB)
    conn.execute(
        "INSERT OR REPLACE INTO agent_settings (user_id, risk_appetite, max_position_size, allowed_sectors) VALUES (?,?,?,?)",
        (user_id, s["risk_appetite"], s["max_position_size"], json.dumps(s["allowed_sectors"]))
    )
    conn.commit()
    conn.close()


@router.get("/{user_id}")
async def get_settings(user_id: str, current_user: str = Depends(get_current_user)):
    """Load agent constraints for a user."""
    resolved_id = resolve_user_id(current_user, user_id)
    return _load_settings(resolved_id)


@router.put("/{user_id}")
async def update_settings(user_id: str, settings: UserSettings, current_user: str = Depends(get_current_user)):
    """Persist agent constraints and apply them to the live AgentService."""
    resolved_id = resolve_user_id(current_user, user_id)
    s = settings.model_dump()
    _save_settings(resolved_id, s)
    svc = get_agent_service()
    svc.update_config(s)
    return {"status": "success", "message": "Agent constraints updated and applied."}
