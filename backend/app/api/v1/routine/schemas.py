from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class RoutineGenerateRequest(BaseModel):
    goals: Optional[List[str]] = None
    current_mood: str = "neutral"

    @field_validator("current_mood")
    @classmethod
    def validate_mood(cls, v: str) -> str:
        allowed = {"joy", "sadness", "anger", "fear", "disgust", "surprise", "neutral"}
        if v not in allowed:
            return "neutral"
        return v


class RoutineTaskUpdateRequest(BaseModel):
    task_id: str
    completed: bool


class RoutineTask(BaseModel):
    id: str
    time: str
    task: str
    duration: str
    category: str
    completed: bool = False


class RoutineBlock(BaseModel):
    morning: List[RoutineTask]
    afternoon: List[RoutineTask]
    evening: List[RoutineTask]
