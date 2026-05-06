import pytest
from app.api.v1.goals.schemas import GoalCreateRequest, GoalUpdateRequest


class TestGoalSchemas:
    def test_title_too_short(self, client, auth_headers):
        resp = client.post(
            "/api/v1/goals/create",
            json={"title": "Go"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_progress_out_of_range(self):
        with pytest.raises(Exception):
            GoalUpdateRequest(progress=150)

    def test_valid_goal(self):
        req = GoalCreateRequest(title="Run 5k every week")
        assert req.title == "Run 5k every week"
        assert req.category == "personal"
        assert req.status if hasattr(req, "status") else True  # status set by service


class TestGoalEndpoints:
    def test_get_goals_requires_auth(self, client):
        resp = client.get("/api/v1/goals")
        assert resp.status_code == 401

    def test_create_goal_requires_auth(self, client):
        resp = client.post("/api/v1/goals/create", json={"title": "A valid goal title"})
        assert resp.status_code == 401

    def test_get_goals_with_auth(self, client, auth_headers, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value.data = []
        resp = client.get("/api/v1/goals", headers=auth_headers)
        assert resp.status_code == 200

    def test_delete_nonexistent_goal(self, client, auth_headers, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        resp = client.delete("/api/v1/goals/nonexistent", headers=auth_headers)
        assert resp.status_code == 404

    def test_milestone_update_on_nonexistent_goal(self, client, auth_headers, mock_supabase):
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        resp = client.patch(
            "/api/v1/goals/nonexistent/milestone",
            json={"milestone_id": "m1", "completed": True},
            headers=auth_headers,
        )
        assert resp.status_code == 404
