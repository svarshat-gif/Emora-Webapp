from fastapi import APIRouter, Depends, Query
from app.api.v1.journal.schemas import JournalCreateRequest, JournalUpdateRequest
from app.api.v1.journal.service import JournalService
from app.core.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/journal", tags=["journal"])


def get_journal_service() -> JournalService:
    return JournalService()


@router.post("/create", response_model=dict, status_code=201)
async def create_entry(
    data: JournalCreateRequest,
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    entry = await service.create_entry(current_user["user_id"], data.text, data.title)
    return {"success": True, "data": entry}


@router.get("/entries", response_model=dict)
async def get_entries(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    entries = await service.get_entries(current_user["user_id"], limit, offset)
    return {"success": True, "data": entries, "count": len(entries)}


@router.get("/calendar", response_model=dict)
async def get_calendar(
    year: int = Query(default=None),
    month: int = Query(default=None, ge=1, le=12),
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    now = datetime.now()
    calendar_data = await service.get_calendar_data(
        current_user["user_id"], year or now.year, month or now.month
    )
    return {"success": True, "data": calendar_data}


@router.get("/insights", response_model=dict)
async def get_insights(
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    insights = await service.get_insights(current_user["user_id"])
    return {"success": True, "data": insights}


@router.get("/{entry_id}/insights", response_model=dict)
async def get_entry_insights(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    insights = await service.get_entry_insights(current_user["user_id"], entry_id)
    return {"success": True, "data": insights}


@router.get("/{entry_id}", response_model=dict)
async def get_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    entry = await service.get_entry(current_user["user_id"], entry_id)
    return {"success": True, "data": entry}


@router.put("/{entry_id}", response_model=dict)
async def update_entry(
    entry_id: str,
    data: JournalUpdateRequest,
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    entry = await service.update_entry(current_user["user_id"], entry_id, data.text, data.title)
    return {"success": True, "data": entry}


@router.delete("/{entry_id}", response_model=dict)
async def delete_entry(
    entry_id: str,
    current_user: dict = Depends(get_current_user),
    service: JournalService = Depends(get_journal_service),
):
    await service.delete_entry(current_user["user_id"], entry_id)
    return {"success": True, "message": "Entry deleted"}
