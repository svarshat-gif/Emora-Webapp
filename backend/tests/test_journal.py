import pytest
from unittest.mock import MagicMock, patch
from app.api.v1.journal.schemas import JournalCreateRequest


class TestJournalSchemas:
    def test_text_too_short(self, client, auth_headers):
        resp = client.post(
            "/api/v1/journal/create",
            json={"text": "Hi"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_text_too_long(self, client, auth_headers):
        resp = client.post(
            "/api/v1/journal/create",
            json={"text": "x" * 10001},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_valid_entry_schema(self):
        req = JournalCreateRequest(text="Today was a really meaningful day for me.")
        assert req.text == "Today was a really meaningful day for me."

    def test_auto_strips_whitespace(self):
        req = JournalCreateRequest(text="  spaced text  ")
        assert req.text == "spaced text"


class TestJournalEndpoints:
    def test_get_entries_requires_auth(self, client):
        resp = client.get("/api/v1/journal/entries")
        assert resp.status_code == 401

    def test_calendar_requires_auth(self, client):
        resp = client.get("/api/v1/journal/calendar")
        assert resp.status_code == 401

    def test_create_requires_auth(self, client):
        resp = client.post("/api/v1/journal/create", json={"text": "Hello world this is a test entry."})
        assert resp.status_code == 401

    def test_get_entries_with_auth(self, client, auth_headers, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = []
        resp = client.get("/api/v1/journal/entries", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_calendar_returns_mood_map(self, client, auth_headers, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.gte.return_value.lte.return_value.order.return_value.execute.return_value.data = [
            {"id": "entry-1", "title": "Test", "emotion": {"dominant_emotion": "joy"}, "created_at": "2026-05-01T10:00:00Z"}
        ]
        resp = client.get("/api/v1/journal/calendar?year=2026&month=5", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "mood_map" in data
        assert "entries" in data

    def test_get_nonexistent_entry(self, client, auth_headers, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        resp = client.get("/api/v1/journal/nonexistent-id", headers=auth_headers)
        assert resp.status_code == 404
