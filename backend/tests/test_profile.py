import pytest
from app.api.v1.profile.schemas import ProfileUpdateRequest


class TestProfileSchemas:
    def test_name_too_short(self):
        with pytest.raises(Exception):
            ProfileUpdateRequest(name="X")

    def test_invalid_personality(self):
        with pytest.raises(Exception):
            ProfileUpdateRequest(personality="unknown")

    def test_invalid_theme(self):
        with pytest.raises(Exception):
            ProfileUpdateRequest(theme="neon")

    def test_bio_too_long(self):
        with pytest.raises(Exception):
            ProfileUpdateRequest(bio="x" * 301)

    def test_all_none_is_valid(self):
        req = ProfileUpdateRequest()
        assert req.name is None

    def test_valid_update(self):
        req = ProfileUpdateRequest(name="Alice", personality="motivator", theme="dark")
        assert req.name == "Alice"
        assert req.personality == "motivator"


class TestProfileEndpoints:
    def test_get_profile_requires_auth(self, client):
        resp = client.get("/api/v1/profile")
        assert resp.status_code == 401

    def test_update_profile_requires_auth(self, client):
        resp = client.put("/api/v1/profile", json={"name": "New Name"})
        assert resp.status_code == 401

    def test_get_profile_with_auth(self, client, auth_headers, mock_supabase, test_user):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user]
        # Mock stats sub-queries
        count_mock = MagicMock()
        count_mock.count = 5
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = count_mock
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user]

        resp = client.get("/api/v1/profile", headers=auth_headers)
        assert resp.status_code == 200

    def test_streak_requires_auth(self, client):
        resp = client.get("/api/v1/profile/streak")
        assert resp.status_code == 401
