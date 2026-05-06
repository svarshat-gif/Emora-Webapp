from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class GoalStatus(str, Enum):
    active = "active"
    completed = "completed"
    paused = "paused"


class GoalCategory(str, Enum):
    mental_health = "mental_health"
    physical = "physical"
    social = "social"
    career = "career"
    personal = "personal"
    spiritual = "spiritual"


class GoalCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    category: GoalCategory = GoalCategory.personal
    target_date: Optional[date] = None
    milestones: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3 or len(v) > 200:
            raise ValueError("Goal title must be 3-200 characters")
        return v


class GoalUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    progress: Optional[int] = None

    @field_validator("progress")
    @classmethod
    def validate_progress(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and not (0 <= v <= 100):
            raise ValueError("Progress must be 0-100")
        return v


class MilestoneUpdateRequest(BaseModel):
    milestone_id: str
    completed: bool


class EmotionGoalsRequest(BaseModel):
    emotion: str
    memo_title: str = "Voice Memo"
