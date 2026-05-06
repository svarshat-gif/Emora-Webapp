from pydantic import BaseModel, field_validator
from typing import Optional
import re


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    notification_enabled: Optional[bool] = None
    theme: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 2 or len(v) > 50:
            raise ValueError("Name must be 2-50 characters")
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Name contains invalid characters")
        return v

    @field_validator("personality")
    @classmethod
    def validate_personality(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = {"sera", "motivator", "rational", "luna"}
        if v not in allowed:
            raise ValueError(f"Personality must be one of: {', '.join(allowed)}")
        return v

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        allowed = {"dark", "light", "system"}
        if v not in allowed:
            raise ValueError(f"Theme must be one of: {', '.join(allowed)}")
        return v

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and len(v) > 300:
            raise ValueError("Bio must be under 300 characters")
        return v
