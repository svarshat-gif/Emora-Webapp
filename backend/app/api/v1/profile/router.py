from fastapi import APIRouter, Depends
from app.api.v1.profile.schemas import ProfileUpdateRequest
from app.api.v1.profile.service import ProfileService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


def get_profile_service() -> ProfileService:
    return ProfileService()


@router.get("", response_model=dict)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    profile = await service.get_profile(current_user["user_id"])
    return {"success": True, "data": profile}


@router.put("", response_model=dict)
async def update_profile(
    data: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    profile = await service.update_profile(current_user["user_id"], data.model_dump())
    return {"success": True, "data": profile}


@router.get("/streak", response_model=dict)
async def get_streak(
    current_user: dict = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    streak_data = await service.get_streak(current_user["user_id"])
    return {"success": True, "data": streak_data}
