import pytest
from fastapi.testclient import TestClient


class TestForecastsAPI:
    """Test forecasts API endpoints."""

    def test_create_forecast_admin(self, client: TestClient, admin_token, test_sales):
        """Test creating a forecast as admin."""
        forecast_data = {
            "alpha": 0.5,
            "product_name": "Test Product 1",
            "project_name": "Test Project",
            "next_period_date": "2025-05-04"
        }
        response = client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "overall_mape" in data

    def test_create_forecast_owner_forbidden(self, client: TestClient, owner_token, test_sales):
        """Test that owner cannot create forecasts."""
        forecast_data = {
            "alpha": 0.5,
            "product_name": "Test Product 1"
        }
        response = client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {owner_token}"}
        )

        assert response.status_code == 403

    def test_get_latest_forecast(self, client: TestClient, admin_token, test_sales):
        """Test getting the latest forecast."""
        # First create a forecast
        forecast_data = {"alpha": 0.5, "product_name": "Test Product 1"}
        client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Get latest forecast
        response = client.get(
            "/forecast/latest",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "product_name" in data
        assert "alpha" in data
        assert data["product_name"] == "Test Product 1"

    def test_get_forecast_history(self, client: TestClient, admin_token, test_sales):
        """Test getting forecast history."""
        # First create a forecast
        forecast_data = {"alpha": 0.5, "product_name": "Test Product 1"}
        client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Get history
        response = client.get(
            "/forecasts/history",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_forecast_projects(self, client: TestClient, admin_token, test_sales):
        """Test getting forecast projects."""
        # First create a forecast with a project name
        forecast_data = {
            "alpha": 0.5,
            "product_name": "Test Product 1",
            "project_name": "Test Project"
        }
        client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Get projects
        response = client.get(
            "/forecast/projects",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["project_name"] == "Test Project"

    def test_get_forecast_project_by_name(self, client: TestClient, admin_token, test_sales):
        """Test getting a specific forecast project."""
        # First create a forecast with a project name
        forecast_data = {
            "alpha": 0.5,
            "product_name": "Test Product 1",
            "project_name": "Test Project"
        }
        client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Get project by name
        response = client.get(
            "/forecast/project/Test Project",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["project_name"] == "Test Project"
        assert "results" in data

    def test_delete_forecast_project(self, client: TestClient, admin_token, test_sales):
        """Test deleting a forecast project."""
        # First create a forecast with a project name
        forecast_data = {
            "alpha": 0.5,
            "product_name": "Test Product 1",
            "project_name": "Project to Delete"
        }
        client.post(
            "/forecast",
            json=forecast_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        # Delete the project
        response = client.delete(
            "/forecast/project/Project to Delete",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_reset_data(self, client: TestClient, admin_token, test_sales):
        """Test resetting sales and forecasts data."""
        response = client.post(
            "/forecast/reset-data",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
