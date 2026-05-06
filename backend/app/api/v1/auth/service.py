from typing import Optional, Dict
from app.db.supabase import get_supabase_client
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.exceptions import AuthException, ValidationException
from app.api.v1.auth.schemas import SignupRequest, LoginRequest
import structlog
import uuid

logger = structlog.get_logger()


class AuthService:
    def __init__(self):
        self.db = get_supabase_client()

    async def signup(self, data: SignupRequest) -> Dict:
        # Check existing user
        existing = self.db.table("users").select("id").eq("email", data.email).execute()
        if existing.data:
            raise ValidationException("Email already registered")

        user_id = str(uuid.uuid4())
        password_hash = hash_password(data.password)

        user_record = {
            "id": user_id,
            "email": data.email,
            "name": data.name,
            "password_hash": password_hash,
            "personality": data.personality,
            "streak": 0,
            "total_entries": 0,
        }

        result = self.db.table("users").insert(user_record).execute()
        if not result.data:
            raise ValidationException("Failed to create account")

        user = result.data[0]
        tokens = self._generate_tokens(user_id, data.email)

        logger.info("user_signup", user_id=user_id, email=data.email)
        return {"user": self._sanitize_user(user), **tokens}

    async def login(self, data: LoginRequest) -> Dict:
        result = self.db.table("users").select("*").eq("email", data.email).execute()
        if not result.data:
            raise AuthException("Invalid email or password")

        user = result.data[0]
        if not verify_password(data.password, user["password_hash"]):
            raise AuthException("Invalid email or password")

        tokens = self._generate_tokens(user["id"], user["email"])
        logger.info("user_login", user_id=user["id"])
        return {"user": self._sanitize_user(user), **tokens}

    async def refresh_token(self, refresh_token: str) -> Dict:
        payload = verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise AuthException("Invalid or expired refresh token")

        user_id = payload.get("sub")
        result = self.db.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            raise AuthException("User not found")

        user = result.data[0]
        tokens = self._generate_tokens(user["id"], user["email"])
        return {"user": self._sanitize_user(user), **tokens}

    async def get_user(self, user_id: str) -> Optional[Dict]:
        result = self.db.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            return None
        return self._sanitize_user(result.data[0])

    def _generate_tokens(self, user_id: str, email: str) -> Dict:
        payload = {"sub": user_id, "email": email}
        return {
            "access_token": create_access_token(payload),
            "refresh_token": create_refresh_token(payload),
            "token_type": "bearer",
        }

    def _sanitize_user(self, user: Dict) -> Dict:
        return {k: v for k, v in user.items() if k != "password_hash"}
