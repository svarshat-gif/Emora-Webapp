from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.api.v1.goals.schemas import GoalCreateRequest, GoalUpdateRequest, MilestoneUpdateRequest, EmotionGoalsRequest
from app.api.v1.goals.service import GoalsService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/goals", tags=["goals"])


def get_goals_service() -> GoalsService:
    return GoalsService()


@router.post("/from-emotion", response_model=dict, status_code=201)
async def generate_from_emotion(
    data: EmotionGoalsRequest,
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    goals = await service.generate_emotion_goals(current_user["user_id"], data.emotion, data.memo_title)
    return {"success": True, "data": goals, "count": len(goals)}


@router.post("/create", response_model=dict, status_code=201)
async def create_goal(
    data: GoalCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    goal = await service.create_goal(current_user["user_id"], data.model_dump())
    return {"success": True, "data": goal}


@router.get("", response_model=dict)
async def get_goals(
    status: Optional[str] = Query(default=None),
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    goals = await service.get_goals(current_user["user_id"], status)
    return {"success": True, "data": goals}


@router.get("/{goal_id}", response_model=dict)
async def get_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    goal = await service.get_goal(current_user["user_id"], goal_id)
    return {"success": True, "data": goal}


@router.put("/{goal_id}", response_model=dict)
async def update_goal(
    goal_id: str,
    data: GoalUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    goal = await service.update_goal(current_user["user_id"], goal_id, updates)
    return {"success": True, "data": goal}


@router.patch("/{goal_id}/milestone", response_model=dict)
async def update_milestone(
    goal_id: str,
    data: MilestoneUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    goal = await service.update_milestone(current_user["user_id"], goal_id, data.milestone_id, data.completed)
    return {"success": True, "data": goal}


@router.delete("/{goal_id}", response_model=dict)
async def delete_goal(
    goal_id: str,
    current_user: dict = Depends(get_current_user),
    service: GoalsService = Depends(get_goals_service),
):
    await service.delete_goal(current_user["user_id"], goal_id)
    return {"success": True, "message": "Goal deleted"}
