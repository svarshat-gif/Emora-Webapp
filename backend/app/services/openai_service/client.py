"""
AI client — custom engine primary, OpenAI optional fallback.
The custom AI engine generates personalized, contextual responses
with no external API dependencies (no quota, no billing, always on).
OpenAI is used only if OPENAI_API_KEY has active credits.
"""
from app.core.config import settings
from app.services.custom_ai.engine import custom_ai
import structlog

logger = structlog.get_logger()

# Lazy OpenAI client — only initialized if key is present
_openai_client = None


def get_openai_client():
    global _openai_client
    if _openai_client is None and settings.OPENAI_API_KEY:
        from openai import AsyncOpenAI
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


async def chat_completion(
    messages: list,
    temperature: float = 0.7,
    max_tokens: int = 500,
    personality: str = "sera",
) -> str:
    # 1. Try OpenAI if key is configured (may have credits)
    client = get_openai_client()
    if client:
        try:
            from openai import RateLimitError, APIError
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            logger.info("openai_completion_success", tokens=response.usage.total_tokens)
            return response.choices[0].message.content
        except Exception as e:
            logger.warning("openai_unavailable_falling_back_to_custom_ai", error=str(e)[:100])

    # 2. Custom AI engine — always available, no external calls
    try:
        response_text = custom_ai.generate(messages, personality=personality)
        logger.info("custom_ai_response_generated", personality=personality)
        return response_text
    except Exception as e:
        logger.error("custom_ai_error", error=str(e))
        return (
            "I'm here with you. Something went wrong on my end — could you try sending that again?"
        )


async def json_completion(prompt: str, temperature: float = 0.3) -> str:
    client = get_openai_client()
    if client:
        try:
            response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.warning("openai_json_failed", error=str(e)[:100])

    # Fallback: ask custom AI to produce JSON-like text
    # (used by routine/insight features — best effort)
    raise RuntimeError("json_completion requires an OpenAI key with active credits")
