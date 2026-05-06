import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.core.security import create_access_token, hash_password


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def test_user():
    return {
        "id": "test-user-uuid-1234",
        "email": "test@example.com",
        "name": "Test User",
        "password_hash": hash_password("TestPass1"),
        "personality": "sera",
        "streak": 0,
        "total_entries": 0,
    }


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": test_user["id"], "email": test_user["email"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_supabase():
    with patch("app.db.supabase.get_supabase_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_openai():
    with patch("app.services.openai_service.client.get_openai_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client
