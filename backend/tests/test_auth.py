import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.core.security import verify_password, hash_password, create_access_token, verify_token


class TestPasswordHashing:
    def test_hash_and_verify(self):
        password = "SecurePass1"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("CorrectPass1")
        assert not verify_password("WrongPass1", hashed)

    def test_hash_is_unique(self):
        pw = "SamePassword1"
        assert hash_password(pw) != hash_password(pw)  # bcrypt salts


class TestJWT:
    def test_access_token_creation(self):
        payload = {"sub": "user-123", "email": "test@test.com"}
        token = create_access_token(payload)
        assert isinstance(token, str)
        assert len(token) > 20

    def test_access_token_verify(self):
        payload = {"sub": "user-123", "email": "test@test.com"}
        token = create_access_token(payload)
        decoded = verify_token(token, token_type="access")
        assert decoded is not None
        assert decoded["sub"] == "user-123"

    def test_wrong_type_fails(self):
        from app.core.security import create_refresh_token
        token = create_refresh_token({"sub": "user-123"})
        # Refresh token should not pass access verification
        result = verify_token(token, token_type="access")
        assert result is None

    def test_invalid_token_returns_none(self):
        result = verify_token("not.a.real.token", token_type="access")
        assert result is None


class TestSignupValidation:
    def test_password_too_short(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "test@test.com", "password": "short", "name": "Test"
        })
        assert resp.status_code == 422

    def test_password_no_uppercase(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "test@test.com", "password": "lowercase1", "name": "Test"
        })
        assert resp.status_code == 422

    def test_password_no_digit(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "test@test.com", "password": "NoDigitHere", "name": "Test"
        })
        assert resp.status_code == 422

    def test_invalid_email(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "notanemail", "password": "ValidPass1", "name": "Test"
        })
        assert resp.status_code == 422

    def test_invalid_personality(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "test@test.com", "password": "ValidPass1", "name": "Test", "personality": "invalid"
        })
        assert resp.status_code == 422

    def test_name_too_short(self, client):
        resp = client.post("/api/v1/auth/signup", json={
            "email": "test@test.com", "password": "ValidPass1", "name": "X"
        })
        assert resp.status_code == 422


class TestAuthEndpoints:
    def test_signup_success(self, client, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{
            "id": "uuid-1", "email": "new@test.com", "name": "New User",
            "personality": "sera", "streak": 0, "total_entries": 0,
        }]

        resp = client.post("/api/v1/auth/signup", json={
            "email": "new@test.com", "password": "ValidPass1", "name": "New User"
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "refresh_token" in data["data"]

    def test_login_wrong_password(self, client, mock_supabase, test_user):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user]

        resp = client.post("/api/v1/auth/login", json={
            "email": "test@example.com", "password": "WrongPass1"
        })
        assert resp.status_code == 401

    def test_me_requires_auth(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_with_valid_token(self, client, auth_headers, mock_supabase, test_user):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [test_user]
        resp = client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["success"] is True
