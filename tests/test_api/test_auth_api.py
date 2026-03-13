import pytest
from fastapi.testclient import TestClient


class TestAuthAPI:
    """Test authentication API endpoints."""

    def test_login_success(self, client: TestClient, test_users):
        """Test successful login."""
        response = client.post(
            "/token",
            data={"username": "test_admin", "password": "admin123"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, test_users):
        """Test login with wrong password."""
        response = client.post(
            "/token",
            data={"username": "test_admin", "password": "wrongpassword"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with non-existent user."""
        response = client.post(
            "/token",
            data={"username": "nonexistent", "password": "password"}
        )

        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, admin_token):
        """Test getting current user info."""
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "test_admin"
        assert data["role"] == "admin"

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/users/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
