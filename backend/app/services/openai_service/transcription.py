"""
Voice memo transcription using OpenAI Whisper.
Converts base64 audio data URLs to text transcripts.
"""
import base64
import io
import structlog
from app.core.config import settings

logger = structlog.get_logger()


async def transcribe_voice_memo(audio_data_url: str) -> str | None:
    """
    Transcribe a voice memo stored as a base64 data URL.
    Returns the transcript string, or None if transcription is unavailable/failed.
    """
    if not settings.OPENAI_API_KEY:
        logger.warning("whisper_unavailable", reason="no_api_key")
        return None

    if "," not in audio_data_url:
        return None

    try:
        from openai import AsyncOpenAI, AuthenticationError, RateLimitError

        header, b64_data = audio_data_url.split(",", 1)

        # Determine MIME type and file extension
        mime_type = "audio/webm"
        if "audio/" in header:
            mime_type = header.split("data:")[1].split(";")[0]

        ext_map = {
            "audio/webm": "webm",
            "audio/ogg":  "ogg",
            "audio/mp4":  "mp4",
            "audio/mpeg": "mp3",
            "audio/wav":  "wav",
        }
        ext = ext_map.get(mime_type, "webm")

        audio_bytes = base64.b64decode(b64_data)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = f"voice_memo.{ext}"

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio_file.name, audio_file, mime_type),
            language="en",
            response_format="text",
        )

        transcript = response if isinstance(response, str) else getattr(response, "text", str(response))
        logger.info("whisper_transcription_success", length=len(transcript))
        return transcript.strip()

    except Exception as e:
        logger.warning("whisper_transcription_failed", error=str(e)[:120])
        return None
