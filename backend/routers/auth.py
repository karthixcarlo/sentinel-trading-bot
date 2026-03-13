from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import auth_manager as auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/login")
async def login(req: LoginRequest):
    """Interfaces with Supabase Auth to validate users."""
    result = auth.sign_in(req.email, req.password)
    if result.get("success"):
        user = result.get("user")
        return {
            "status": "success",
            "token": result.get("session", {}).get("access_token", "dummy_token"),
            "user_id": user.id if user else "demo_user"
        }
    raise HTTPException(status_code=401, detail=result.get("error", "Invalid credentials"))
