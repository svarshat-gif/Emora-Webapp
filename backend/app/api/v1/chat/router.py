from fastapi import APIRouter, Depends
from app.api.v1.chat.schemas import ChatMessageRequest
from app.api.v1.chat.service import ChatService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service() -> ChatService:
    return ChatService()


@router.post("/message", response_model=dict)
async def send_message(
    data: ChatMessageRequest,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    result = await service.send_message(
        current_user["user_id"], data.message, data.personality, data.session_id
    )
    return {"success": True, "data": result}


@router.get("/sessions", response_model=dict)
async def get_sessions(
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    sessions = await service.get_sessions(current_user["user_id"])
    return {"success": True, "data": sessions}


@router.get("/sessions/{session_id}/history", response_model=dict)
async def get_session_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    history = await service.get_session_history(current_user["user_id"], session_id)
    return {"success": True, "data": history}


@router.delete("/sessions/{session_id}", response_model=dict)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    service: ChatService = Depends(get_chat_service),
):
    await service.delete_session(current_user["user_id"], session_id)
    return {"success": True, "message": "Session deleted"}
