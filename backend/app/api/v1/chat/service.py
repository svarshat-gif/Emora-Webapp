from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid
from app.db.supabase import get_supabase_client
from app.services.emotion.detector import emotion_detector
from app.services.openai_service.client import chat_completion
from app.services.openai_service.prompt_builder import build_chat_prompt
from app.core.exceptions import NotFoundException
import structlog

logger = structlog.get_logger()


class ChatService:
    def __init__(self):
        self.db = get_supabase_client()

    async def send_message(self, user_id: str, message: str, personality: str, session_id: Optional[str]) -> Dict:
        # Detect emotion
        emotion = emotion_detector.detect(message)

        # Get or create session
        if not session_id:
            session_id = await self._create_session(user_id, personality, message)
        else:
            session = self.db.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
            if not session.data:
                raise NotFoundException("Chat session")

        # Get conversation history
        history = await self._get_history(session_id, limit=6)

        # Get user name for personalization
        user_result = self.db.table("users").select("name").eq("id", user_id).execute()
        user_name = user_result.data[0]["name"] if user_result.data else None

        # Build prompt and get AI response
        messages = build_chat_prompt(message, emotion, personality, history, user_name)
        response_text = await chat_completion(messages, temperature=0.75, personality=personality)

        # Store messages
        user_msg_id = str(uuid.uuid4())
        ai_msg_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        self.db.table("chat_messages").insert([
            {
                "id": user_msg_id, "session_id": session_id, "user_id": user_id,
                "role": "user", "content": message, "emotion": emotion, "created_at": now,
            },
            {
                "id": ai_msg_id, "session_id": session_id, "user_id": user_id,
                "role": "assistant", "content": response_text, "created_at": now,
            },
        ]).execute()

        # Update session
        title = message[:50] + "..." if len(message) > 50 else message
        self.db.table("chat_sessions").update({
            "last_message": response_text[:100], "updated_at": now, "title": title,
        }).eq("id", session_id).execute()

        logger.info("chat_message_sent", user_id=user_id, session_id=session_id, emotion=emotion["dominant_emotion"])

        return {
            "session_id": session_id,
            "message_id": ai_msg_id,
            "response": response_text,
            "emotion": emotion,
            "personality": personality,
            "timestamp": now,
        }

    async def get_sessions(self, user_id: str) -> List[Dict]:
        result = self.db.table("chat_sessions").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(20).execute()
        return result.data or []

    async def get_session_history(self, user_id: str, session_id: str) -> List[Dict]:
        session = self.db.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        if not session.data:
            raise NotFoundException("Chat session")
        result = self.db.table("chat_messages").select("*").eq("session_id", session_id).order("created_at").execute()
        return result.data or []

    async def delete_session(self, user_id: str, session_id: str) -> None:
        session = self.db.table("chat_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        if not session.data:
            raise NotFoundException("Chat session")
        self.db.table("chat_messages").delete().eq("session_id", session_id).execute()
        self.db.table("chat_sessions").delete().eq("id", session_id).execute()

    async def _create_session(self, user_id: str, personality: str, first_message: str) -> str:
        session_id = str(uuid.uuid4())
        title = first_message[:50] + "..." if len(first_message) > 50 else first_message
        now = datetime.now(timezone.utc).isoformat()
        self.db.table("chat_sessions").insert({
            "id": session_id, "user_id": user_id, "personality": personality,
            "title": title, "created_at": now, "updated_at": now,
        }).execute()
        return session_id

    async def _get_history(self, session_id: str, limit: int = 6) -> List[Dict]:
        result = self.db.table("chat_messages").select("role,content").eq("session_id", session_id).order("created_at", desc=True).limit(limit).execute()
        return list(reversed(result.data or []))
