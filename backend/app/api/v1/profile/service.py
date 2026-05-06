from typing import Dict, Optional
from datetime import datetime, timezone
from app.db.supabase import get_supabase_client
from app.core.exceptions import NotFoundException
import structlog

logger = structlog.get_logger()


class ProfileService:
    def __init__(self):
        self.db = get_supabase_client()

    async def get_profile(self, user_id: str) -> Dict:
        result = self.db.table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            raise NotFoundException("User")

        user = {k: v for k, v in result.data[0].items() if k != "password_hash"}

        # Fetch stats
        journal_count = self.db.table("journal_entries").select("id", count="exact").eq("user_id", user_id).execute()
        goal_count = self.db.table("goals").select("id", count="exact").eq("user_id", user_id).eq("status", "completed").execute()
        chat_count = self.db.table("chat_sessions").select("id", count="exact").eq("user_id", user_id).execute()

        user["stats"] = {
            "journal_entries": journal_count.count or 0,
            "goals_completed": goal_count.count or 0,
            "chat_sessions": chat_count.count or 0,
            "streak": user.get("streak", 0),
        }
        return user

    async def update_profile(self, user_id: str, updates: dict) -> Dict:
        # Remove None values
        clean = {k: v for k, v in updates.items() if v is not None}
        if not clean:
            return await self.get_profile(user_id)

        clean["updated_at"] = datetime.now(timezone.utc).isoformat()
        result = self.db.table("users").update(clean).eq("id", user_id).execute()
        if not result.data:
            raise NotFoundException("User")

        logger.info("profile_updated", user_id=user_id, fields=list(clean.keys()))
        return {k: v for k, v in result.data[0].items() if k != "password_hash"}

    async def get_streak(self, user_id: str) -> Dict:
        # Get last 30 days of journal entries
        result = (
            self.db.table("journal_entries")
            .select("created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(60)
            .execute()
        )
        entries = result.data or []

        # Calculate streak
        from datetime import date, timedelta
        dates_with_entries = set(e["created_at"][:10] for e in entries)
        streak = 0
        check_date = date.today()

        while str(check_date) in dates_with_entries:
            streak += 1
            check_date -= timedelta(days=1)

        # Update streak in DB
        self.db.table("users").update({"streak": streak}).eq("id", user_id).execute()
        return {"streak": streak, "total_entries": len(entries)}
