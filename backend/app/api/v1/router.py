from fastapi import APIRouter
from app.api.v1.auth.router import router as auth_router
from app.api.v1.chat.router import router as chat_router
from app.api.v1.journal.router import router as journal_router
from app.api.v1.goals.router import router as goals_router
from app.api.v1.routine.router import router as routine_router
from app.api.v1.profile.router import router as profile_router

api_router = APIRouter(prefix="")

api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(journal_router)
api_router.include_router(goals_router)
api_router.include_router(routine_router)
api_router.include_router(profile_router)
