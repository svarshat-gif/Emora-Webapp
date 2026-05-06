from typing import Dict, List, Optional
from datetime import datetime, timezone, date
import uuid
import json
from app.db.supabase import get_supabase_client
from app.services.openai_service.client import json_completion
from app.services.openai_service.prompt_builder import build_routine_prompt
from app.core.exceptions import NotFoundException
import structlog

logger = structlog.get_logger()


class RoutineService:
    def __init__(self):
        self.db = get_supabase_client()

    async def generate_routine(self, user_id: str, goals: Optional[List[str]], current_mood: str) -> Dict:
        # Get user's active goals if not provided
        if not goals:
            result = self.db.table("goals").select("title").eq("user_id", user_id).eq("status", "active").limit(5).execute()
            goals = [g["title"] for g in (result.data or [])]

        # Get user name
        user_result = self.db.table("users").select("name").eq("id", user_id).execute()
        user_name = user_result.data[0]["name"] if user_result.data else None

        prompt = build_routine_prompt(goals, current_mood, user_name)
        raw = await json_completion(prompt, temperature=0.4)
        routine_data = json.loads(raw)

        # Add IDs to tasks
        for block in ["morning", "afternoon", "evening"]:
            for task in routine_data.get(block, []):
                task["id"] = str(uuid.uuid4())
                task["completed"] = False

        routine_id = str(uuid.uuid4())
        today = str(date.today())
        now = datetime.now(timezone.utc).isoformat()

        record = {
            "id": routine_id,
            "user_id": user_id,
            "date": today,
            "mood": current_mood,
            "tasks": routine_data,
            "completion_rate": 0.0,
            "created_at": now,
            "updated_at": now,
        }

        # Upsert (replace today's routine if exists)
        existing = self.db.table("routines").select("id").eq("user_id", user_id).eq("date", today).execute()
        if existing.data:
            self.db.table("routines").update(record).eq("id", existing.data[0]["id"]).execute()
            record["id"] = existing.data[0]["id"]
        else:
            self.db.table("routines").insert(record).execute()

        logger.info("routine_generated", user_id=user_id, mood=current_mood)
        return record

    async def get_today_routine(self, user_id: str) -> Optional[Dict]:
        today = str(date.today())
        result = self.db.table("routines").select("*").eq("user_id", user_id).eq("date", today).execute()
        return result.data[0] if result.data else None

    async def get_routine_history(self, user_id: str, limit: int = 7) -> List[Dict]:
        result = (
            self.db.table("routines")
            .select("id,date,mood,completion_rate,created_at")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def update_task(self, user_id: str, routine_id: str, task_id: str, completed: bool) -> Dict:
        result = self.db.table("routines").select("*").eq("id", routine_id).eq("user_id", user_id).execute()
        if not result.data:
            raise NotFoundException("Routine")

        routine = result.data[0]
        tasks = routine["tasks"]
        total = 0
        done = 0

        for block in ["morning", "afternoon", "evening"]:
            for task in tasks.get(block, []):
                total += 1
                if task["id"] == task_id:
                    task["completed"] = completed
                if task["completed"]:
                    done += 1

        completion_rate = round((done / total) * 100, 1) if total > 0 else 0.0
        now = datetime.now(timezone.utc).isoformat()

        self.db.table("routines").update({
            "tasks": tasks,
            "completion_rate": completion_rate,
            "updated_at": now,
        }).eq("id", routine_id).execute()

        return {**routine, "tasks": tasks, "completion_rate": completion_rate}
