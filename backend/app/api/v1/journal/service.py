from typing import Dict, List, Optional
from datetime import datetime, timezone, date
import uuid
from app.db.supabase import get_supabase_client
from app.services.emotion.detector import emotion_detector
from app.services.openai_service.client import json_completion
from app.services.openai_service.prompt_builder import build_journal_insight_prompt
from app.core.exceptions import NotFoundException, ForbiddenException
import structlog

logger = structlog.get_logger()


class JournalService:
    def __init__(self):
        self.db = get_supabase_client()

    async def create_entry(self, user_id: str, text: str, title: Optional[str] = None) -> Dict:
        is_voice_memo = text.startswith("VOICE_MEMO::")
        emotion = {"dominant_emotion": "neutral", "confidence": 0.0} if is_voice_memo else emotion_detector.detect(text)
        entry_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        auto_title = title or (text[:40] + "..." if len(text) > 40 else text)

        entry = {
            "id": entry_id,
            "user_id": user_id,
            "title": auto_title,
            "text": text,
            "emotion": emotion,
            "created_at": now,
            "updated_at": now,
        }

        result = self.db.table("journal_entries").insert(entry).execute()
        if not result.data:
            raise Exception("Failed to save journal entry")

        # Update user stats (best-effort — don't fail the whole request if missing)
        try:
            self.db.rpc("increment_journal_count", {"p_user_id": user_id}).execute()
        except Exception:
            pass

        logger.info("journal_entry_created", user_id=user_id, emotion=emotion["dominant_emotion"])
        return result.data[0]

    async def get_entries(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        result = (
            self.db.table("journal_entries")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return result.data or []

    async def get_entry(self, user_id: str, entry_id: str) -> Dict:
        result = self.db.table("journal_entries").select("*").eq("id", entry_id).execute()
        if not result.data:
            raise NotFoundException("Journal entry")
        entry = result.data[0]
        if entry["user_id"] != user_id:
            raise ForbiddenException()
        return entry

    async def update_entry(self, user_id: str, entry_id: str, text: Optional[str], title: Optional[str]) -> Dict:
        entry = await self.get_entry(user_id, entry_id)
        updates = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if text:
            updates["text"] = text
            updates["emotion"] = emotion_detector.detect(text)
        if title:
            updates["title"] = title

        result = self.db.table("journal_entries").update(updates).eq("id", entry_id).execute()
        return result.data[0]

    async def delete_entry(self, user_id: str, entry_id: str) -> None:
        await self.get_entry(user_id, entry_id)
        self.db.table("journal_entries").delete().eq("id", entry_id).execute()

    async def get_calendar_data(self, user_id: str, year: int, month: int) -> Dict:
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-31"
        result = (
            self.db.table("journal_entries")
            .select("id,title,emotion,created_at")
            .eq("user_id", user_id)
            .gte("created_at", start)
            .lte("created_at", end)
            .order("created_at")
            .execute()
        )
        entries = result.data or []
        # Return keyed by day-of-month (string) so frontend can do data[day]
        day_map: Dict[str, Dict] = {}
        for e in entries:
            try:
                day = str(int(e["created_at"][8:10]))
            except (ValueError, IndexError):
                continue
            dominant_emotion = (
                e["emotion"].get("dominant_emotion", "neutral")
                if e.get("emotion") else "neutral"
            )
            title = e.get("title", "")
            day_map[day] = {
                "id": e["id"],
                "dominant_emotion": dominant_emotion,
                "color": "#94a3b8",
                "title": title,
                "is_voice_memo": title.startswith("Voice Memo") or "\U0001f3d9" in title,
            }
        return day_map

    async def get_entry_insights(self, user_id: str, entry_id: str) -> Dict:
        entry = await self.get_entry(user_id, entry_id)
        emotion = entry.get("emotion") or {}
        dominant = emotion.get("dominant_emotion", "neutral")
        text = entry.get("text", "")
        title = entry.get("title", "Voice Memo")

        from app.services.custom_ai.engine import custom_ai
        from app.services.emotion.detector import emotion_detector

        # ── Voice memos: transcribe with Whisper, then AI-analyze the transcript ──
        if text.startswith("VOICE_MEMO::"):
            audio_data_url = text[len("VOICE_MEMO::"):]
            from app.services.openai_service.transcription import transcribe_voice_memo
            transcript = await transcribe_voice_memo(audio_data_url)

            if transcript and len(transcript.strip()) > 5:
                # Detect emotion from what the user actually said
                detected = emotion_detector.detect(transcript)
                transcript_emotion = detected.get("dominant_emotion", "neutral")
                logger.info("voice_memo_transcribed", emotion=transcript_emotion, length=len(transcript))

                # Also update the stored emotion in the DB so it reflects reality
                try:
                    self.db.table("journal_entries").update({"emotion": detected}).eq("id", entry_id).execute()
                except Exception:
                    pass

                result = custom_ai.analyze_journal(transcript, transcript_emotion)
                result["transcript"] = transcript
                result["source"] = "whisper"
                return result

            # Whisper unavailable — tell the user honestly
            return {
                "insight": (
                    f"I wasn't able to transcribe your voice memo '{title}' automatically — "
                    "audio transcription requires an active OpenAI subscription. "
                    "To get personalized insights, you can either upgrade the API plan "
                    "or create a text journal entry describing how you felt."
                ),
                "suggestions": [
                    "Write a new text entry on the Calendar page describing what you said in this memo",
                    "Open Chat and tell Sera directly — she can provide real-time therapeutic support",
                    "Try the 'Create Today's Goals' button above to still get emotion-tailored goals",
                ],
                "affirmation": "The fact that you recorded your thoughts is already an act of self-awareness. That matters.",
                "source": "fallback",
            }

        # ── Text entries: AI-analyze the actual content ──
        if len(text.strip()) > 10:
            try:
                return custom_ai.analyze_journal(text, dominant)
            except Exception:
                pass

        # ── Last-resort: short or empty text ──
        return {
            "insight": f"Your entry '{title}' was saved. Write a bit more to unlock deeper AI insights tailored to exactly what you're feeling.",
            "suggestions": [
                "Try writing at least 2–3 sentences about what's on your mind",
                "Open Chat and speak with Sera directly for immediate support",
            ],
            "affirmation": "Every small step toward self-reflection is worth taking.",
            "source": "fallback",
        }

    async def get_insights(self, user_id: str) -> Dict:
        result = (
            self.db.table("journal_entries")
            .select("text,emotion,created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(7)
            .execute()
        )
        entries = result.data or []
        if not entries:
            return {"insight": "Start journaling to get personalized insights.", "mood_trend": "stable", "dominant_themes": [], "suggestion": "Write your first entry today!"}

        formatted = [{"date": e["created_at"][:10], "emotion": e.get("emotion", {}).get("dominant_emotion", "neutral"), "text": e["text"]} for e in entries]
        prompt = build_journal_insight_prompt(formatted)
        raw = await json_completion(prompt)
        import json
        return json.loads(raw)
