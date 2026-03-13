import os
import sqlite3
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services import auth_manager as auth
from backend.deps import get_current_user, ROOT_DIR

router = APIRouter(prefix="/api/chat", tags=["chat"])

logger = logging.getLogger("sentinel")


class ChatRequest(BaseModel):
    message: str
    user_id: str


@router.post("/copilot")
async def copilot_chat(req: ChatRequest, current_user: str = Depends(get_current_user)):
    """
    Connects to Gemini and fetches the user's latest agent_logs from Supabase
    (with SQLite fallback) to explain the trading system's decision-making process.
    """
    try:
        from langgraph_agents import llm

        # 1. Fetch recent agent context — Supabase first, SQLite fallback
        context_str = "No recent agent activity found."

        try:
            client = auth.get_client()
            logs = client.table("agent_logs").select("agent_name, message, timestamp") \
                .eq("user_id", req.user_id) \
                .order("timestamp", desc=True) \
                .limit(15) \
                .execute()
            if logs.data:
                context_str = "\n".join([
                    f"[{entry.get('timestamp', 'N/A')}] {entry['agent_name']}: {entry['message']}"
                    for entry in logs.data
                ])
        except Exception as supabase_err:
            logger.info(f"Copilot: Supabase unavailable, falling back to SQLite — {supabase_err}")
            try:
                db_path = os.path.join(ROOT_DIR, "sentinel.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.execute(
                    "SELECT agent_name, message, iteration FROM agent_thoughts ORDER BY rowid DESC LIMIT 15"
                )
                rows = cursor.fetchall()
                conn.close()
                if rows:
                    context_str = "\n".join([
                        f"[Cycle {r[2]}] {r[0]}: {r[1]}" for r in rows
                    ])
            except Exception as sqlite_err:
                logger.warning(f"Copilot: SQLite fallback also failed — {sqlite_err}")

        # 2. Construct System Prompt
        sys_prompt = f"""You are Sentinel, a senior AI Trading Copilot. You monitor an internal multi-agent LangGraph execution engine (Scout → Analyst → Risk Manager → Trader).
Your role: Answer the human's queries about trading logic, portfolio moves, or market insights based on the recent agent logs below.
Be concise, analytical, and professional (Groww/Zerodha style). Use markdown formatting (bold for key terms, bullet points for lists). Limit to 3-5 sentences or a short bullet list.

--- RECENT AGENT SYSTEM LOGS ---
{context_str}
"""
        # 3. Invoke Gemini via LangChain
        from langchain_core.messages import SystemMessage, HumanMessage
        response = llm.invoke([
            SystemMessage(content=sys_prompt),
            HumanMessage(content=req.message)
        ])

        return {"status": "success", "reply": response.content}
    except Exception:
        logger.exception("Copilot error")
        return {"status": "error", "reply": "I'm having trouble connecting to the Neural Core right now."}
