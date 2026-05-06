from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class ChatMessageRequest(BaseModel):
    message: str
    personality: str = "sera"
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 2000:
            raise ValueError("Message too long (max 2000 characters)")
        return v

    @field_validator("personality")
    @classmethod
    def validate_personality(cls, v: str) -> str:
        allowed = {"sera", "motivator", "rational", "luna"}
        if v not in allowed:
            raise ValueError(f"Personality must be one of: {', '.join(allowed)}")
        return v


class ChatMessageResponse(BaseModel):
    session_id: str
    message_id: str
    response: str
    emotion: dict
    personality: str
    timestamp: datetime


class ChatSession(BaseModel):
    session_id: str
    personality: str
    title: str
    last_message: Optional[str]
    created_at: datetime
    updated_at: datetime


class ChatHistoryItem(BaseModel):
    message_id: str
    role: str
    content: str
    emotion: Optional[dict]
    timestamp: datetime
