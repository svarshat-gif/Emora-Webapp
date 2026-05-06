from fastapi import APIRouter, Depends
from app.api.v1.auth.schemas import SignupRequest, LoginRequest, RefreshRequest, TokenResponse
from app.api.v1.auth.service import AuthService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    return AuthService()


@router.post("/signup", response_model=dict, status_code=201)
async def signup(data: SignupRequest, service: AuthService = Depends(get_auth_service)):
    result = await service.signup(data)
    return {"success": True, "data": result}


@router.post("/login", response_model=dict)
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    result = await service.login(data)
    return {"success": True, "data": result}


@router.post("/refresh", response_model=dict)
async def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    result = await service.refresh_token(data.refresh_token)
    return {"success": True, "data": result}


@router.get("/me", response_model=dict)
async def get_me(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    user = await service.get_user(current_user["user_id"])
    return {"success": True, "data": user}
