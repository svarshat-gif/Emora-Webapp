from typing import Dict, List, Optional
from datetime import datetime, timezone
import uuid
from app.db.supabase import get_supabase_client
from app.core.exceptions import NotFoundException, ForbiddenException
import structlog

logger = structlog.get_logger()

EMOTION_GOAL_TEMPLATES: Dict[str, List[Dict]] = {
    "sadness": [
        {"title": "Daily Mood Check-In", "description": "Take 5 minutes each morning to check in with your emotional state and name what you're feeling.", "milestones": ["Write 3 feelings you're experiencing", "Identify what may have triggered them", "Note one thing you can appreciate right now"], "category": "mental_health"},
        {"title": "Gentle Self-Care Ritual", "description": "Build one compassionate, nourishing practice for hard days.", "milestones": ["Drink water and eat something warm", "Get 10+ minutes of fresh air or sunlight", "Rest without guilt for at least 30 minutes"], "category": "personal"},
    ],
    "anxiety": [
        {"title": "Daily Calm Practice", "description": "Build a consistent breathing or grounding routine to reduce anxiety over time.", "milestones": ["Practice box breathing (4-4-4-4) for 5 minutes", "Do a 5-4-3-2-1 sensory grounding exercise", "Limit news/social media to 30 minutes per day"], "category": "mental_health"},
        {"title": "Worry Management System", "description": "Create a structured way to process worries so they don't spiral.", "milestones": ["Write your worries down every morning", "For each worry, write one realistic counter-thought", "Set a 15-min 'worry window' and contain it to that time"], "category": "personal"},
    ],
    "anger": [
        {"title": "Emotional Regulation Practice", "description": "Build healthy tools to process and channel anger constructively.", "milestones": ["Take 5 deep breaths before reacting to triggers", "Exercise for 20 minutes to release physical tension", "Journal frustrations uncensored, then reflect on the root need"], "category": "mental_health"},
        {"title": "Clear Communication Goal", "description": "Develop the skill of expressing difficult emotions without escalation.", "milestones": ["Practice 'I feel...' statements instead of blame language", "Pause 10 seconds before responding when triggered", "Identify one boundary you need to set this week"], "category": "social"},
    ],
    "fear": [
        {"title": "Courage Building Practice", "description": "Take one small brave action each day to gradually expand what feels possible.", "milestones": ["Name your specific fear in writing today", "Identify the smallest possible next step", "Take that step and journal how it felt"], "category": "personal"},
        {"title": "Support Network Strengthening", "description": "Create reliable emotional support for moments of fear or overwhelm.", "milestones": ["List 3 people you can call when you're scared", "Reach out to one of them this week", "Create a calming playlist or comfort activity list"], "category": "social"},
    ],
    "joy": [
        {"title": "Sustain Your Positive Energy", "description": "Capture what's working and use this momentum to build toward something meaningful.", "milestones": ["Write down exactly what made you feel this joy", "Share your happiness with one person today", "Set one new goal while your motivation is high"], "category": "personal"},
        {"title": "Daily Gratitude Practice", "description": "Anchor this positive state with a daily gratitude habit.", "milestones": ["Write 3 specific gratitudes every morning", "Express genuine appreciation to someone today", "Notice and name one beautiful thing each evening"], "category": "mental_health"},
    ],
    "surprise": [
        {"title": "Mindful Processing Practice", "description": "Build the habit of pausing and processing unexpected events before reacting.", "milestones": ["Journal what surprised you and what it means", "Sleep on any big decisions that emerged", "Talk it through with a trusted person"], "category": "mental_health"},
        {"title": "Adaptability Practice", "description": "Strengthen your ability to handle unexpected change with grace.", "milestones": ["Identify one assumption that needs updating", "List 3 things that are still stable and in your control", "Do one flexible, unplanned activity this week"], "category": "personal"},
    ],
    "disgust": [
        {"title": "Boundary Setting Practice", "description": "Use this feeling as a signal to identify and protect what matters most to you.", "milestones": ["Write down specifically what feels wrong and why", "Identify the value or boundary being violated", "Take one clear action to create distance or protection"], "category": "personal"},
        {"title": "Values Clarification", "description": "Reconnect with your core values to build a life more aligned with who you are.", "milestones": ["List your top 5 personal values", "Identify where your life currently conflicts with them", "Make one small change to better honor a value"], "category": "mental_health"},
    ],
    "neutral": [
        {"title": "Intentional Living Practice", "description": "Use moments of calm clarity to set meaningful direction for your days.", "milestones": ["Define your top priority for this week", "Break it into 3 small, specific steps", "Complete the first step today"], "category": "personal"},
        {"title": "Mindful Awareness Habit", "description": "Deepen your connection to your inner life through regular reflection.", "milestones": ["Do a 10-minute morning meditation or journaling session", "Check in with your feelings 3 times throughout the day", "Reflect on one thing you want more of in your life"], "category": "mental_health"},
    ],
}


class GoalsService:
    def __init__(self):
        self.db = get_supabase_client()

    async def create_goal(self, user_id: str, data: dict) -> Dict:
        goal_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        milestones = []
        for i, text in enumerate(data.get("milestones") or []):
            milestones.append({"id": str(uuid.uuid4()), "text": text, "completed": False, "order": i})

        goal = {
            "id": goal_id,
            "user_id": user_id,
            "title": data["title"],
            "description": data.get("description"),
            "category": data.get("category", "personal"),
            "status": "active",
            "progress": 0,
            "target_date": str(data["target_date"]) if data.get("target_date") else None,
            "milestones": milestones,
            "created_at": now,
            "updated_at": now,
        }

        result = self.db.table("goals").insert(goal).execute()
        logger.info("goal_created", user_id=user_id, goal_id=goal_id)
        return result.data[0]

    async def get_goals(self, user_id: str, status: Optional[str] = None) -> List[Dict]:
        query = self.db.table("goals").select("*").eq("user_id", user_id)
        if status:
            query = query.eq("status", status)
        result = query.order("created_at", desc=True).execute()
        return result.data or []

    async def get_goal(self, user_id: str, goal_id: str) -> Dict:
        result = self.db.table("goals").select("*").eq("id", goal_id).execute()
        if not result.data:
            raise NotFoundException("Goal")
        goal = result.data[0]
        if goal["user_id"] != user_id:
            raise ForbiddenException()
        return goal

    async def update_goal(self, user_id: str, goal_id: str, updates: dict) -> Dict:
        await self.get_goal(user_id, goal_id)
        updates["updated_at"] = datetime.now(timezone.utc).isoformat()
        # Auto-complete goal at 100%
        if updates.get("progress") == 100:
            updates["status"] = "completed"
        result = self.db.table("goals").update(updates).eq("id", goal_id).execute()
        return result.data[0]

    async def update_milestone(self, user_id: str, goal_id: str, milestone_id: str, completed: bool) -> Dict:
        goal = await self.get_goal(user_id, goal_id)
        milestones = goal.get("milestones", [])

        updated = False
        for m in milestones:
            if m["id"] == milestone_id:
                m["completed"] = completed
                updated = True
                break

        if not updated:
            raise NotFoundException("Milestone")

        # Recalculate progress
        total = len(milestones)
        done = sum(1 for m in milestones if m["completed"])
        progress = int((done / total) * 100) if total > 0 else 0

        now = datetime.now(timezone.utc).isoformat()
        updates = {"milestones": milestones, "progress": progress, "updated_at": now}
        if progress == 100:
            updates["status"] = "completed"

        result = self.db.table("goals").update(updates).eq("id", goal_id).execute()
        return result.data[0]

    async def delete_goal(self, user_id: str, goal_id: str) -> None:
        await self.get_goal(user_id, goal_id)
        self.db.table("goals").delete().eq("id", goal_id).execute()

    async def generate_emotion_goals(self, user_id: str, emotion: str, memo_title: str) -> List[Dict]:
        templates = EMOTION_GOAL_TEMPLATES.get(emotion, EMOTION_GOAL_TEMPLATES["neutral"])
        created = []
        for tmpl in templates:
            goal_data = {
                "title": tmpl["title"],
                "description": f"{tmpl['description']} (Created from voice memo: '{memo_title}')",
                "milestones": tmpl["milestones"],
                "category": tmpl["category"],
            }
            goal = await self.create_goal(user_id, goal_data)
            created.append(goal)
        logger.info("emotion_goals_generated", user_id=user_id, emotion=emotion, count=len(created))
        return created
