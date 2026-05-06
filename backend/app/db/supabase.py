from supabase import create_client, Client
from app.core.config import settings
import structlog

logger = structlog.get_logger()

_client: Client = None


def get_supabase_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        logger.info("supabase_client_initialized")
    return _client


def get_anon_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
