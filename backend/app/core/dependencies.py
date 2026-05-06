from fastapi import Depends, Header
from typing import Optional
from app.core.security import verify_token
from app.core.exceptions import AuthException
from app.db.supabase import get_supabase_client
import structlog

logger = structlog.get_logger()


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthException("Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    payload = verify_token(token, token_type="access")

    if not payload:
        raise AuthException("Invalid or expired token")

    user_id = payload.get("sub")
    if not user_id:
        raise AuthException("Invalid token payload")

    return {"user_id": user_id, "email": payload.get("email"), "payload": payload}


async def get_optional_user(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    try:
        return await get_current_user(authorization)
    except AuthException:
        return None
