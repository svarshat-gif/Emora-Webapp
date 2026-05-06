from fastapi import APIRouter, Depends
from app.api.v1.routine.schemas import RoutineGenerateRequest, RoutineTaskUpdateRequest
from app.api.v1.routine.service import RoutineService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/routine", tags=["routine"])


def get_routine_service() -> RoutineService:
    return RoutineService()


@router.post("/generate", response_model=dict)
async def generate_routine(
    data: RoutineGenerateRequest,
    current_user: dict = Depends(get_current_user),
    service: RoutineService = Depends(get_routine_service),
):
    routine = await service.generate_routine(current_user["user_id"], data.goals, data.current_mood)
    return {"success": True, "data": routine}


@router.get("/today", response_model=dict)
async def get_today_routine(
    current_user: dict = Depends(get_current_user),
    service: RoutineService = Depends(get_routine_service),
):
    routine = await service.get_today_routine(current_user["user_id"])
    return {"success": True, "data": routine}


@router.get("/history", response_model=dict)
async def get_history(
    current_user: dict = Depends(get_current_user),
    service: RoutineService = Depends(get_routine_service),
):
    history = await service.get_routine_history(current_user["user_id"])
    return {"success": True, "data": history}


@router.patch("/{routine_id}/task", response_model=dict)
async def update_task(
    routine_id: str,
    data: RoutineTaskUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: RoutineService = Depends(get_routine_service),
):
    routine = await service.update_task(current_user["user_id"], routine_id, data.task_id, data.completed)
    return {"success": True, "data": routine}
