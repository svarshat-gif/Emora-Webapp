from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime


class JournalCreateRequest(BaseModel):
    text: str
    title: Optional[str] = None
    mood_override: Optional[str] = None

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        v = v.strip()
        # Voice memo data URLs can be large — skip length check for them
        if v.startswith("VOICE_MEMO::"):
            return v
        if len(v) < 5:
            raise ValueError("Journal entry must be at least 5 characters")
        if len(v) > 10000:
            raise ValueError("Journal entry too long (max 10,000 characters)")
        return v


class JournalUpdateRequest(BaseModel):
    text: Optional[str] = None
    title: Optional[str] = None


class JournalEntry(BaseModel):
    id: str
    user_id: str
    title: Optional[str]
    text: str
    emotion: dict
    created_at: datetime
    updated_at: datetime


class JournalCalendarResponse(BaseModel):
    entries: List[dict]
    mood_map: dict  # date -> dominant_emotion
