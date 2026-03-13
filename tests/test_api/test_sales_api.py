import pytest
from fastapi.testclient import TestClient


class TestSalesAPI:
    """Test sales API endpoints."""

    def test_get_sales_empty(self, client: TestClient, admin_token):
        """Test getting sales when none exist."""
        response = client.get(
            "/sales",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_get_sales_with_data(self, client: TestClient, admin_token, test_sales):
        """Test getting sales with data."""
        response = client.get(
            "/sales",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_create_sale_admin(self, client: TestClient, admin_token):
        """Test creating a sale as admin."""
        sale_data = {"date": "2025-05-04", "product_name": "Test Product 1", "qty": 25}
        response = client.post(
            "/sales",
            json=sale_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_create_sale_owner_forbidden(self, client: TestClient, owner_token):
        """Test that owner cannot create sales."""
        sale_data = {"date": "2025-05-04", "product_name": "Test Product 1", "qty": 25}
        response = client.post(
            "/sales",
            json=sale_data,
            headers={"Authorization": f"Bearer {owner_token}"}
        )

        assert response.status_code == 403

    def test_get_sales_by_product(self, client: TestClient, admin_token, test_sales):
        """Test getting sales for a specific product."""
        response = client.get(
            "/sales/product/Test Product 1",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_delete_sale(self, client: TestClient, admin_token, test_sales):
        """Test deleting a sale."""
        # First, get the sale ID
        sales_response = client.get(
            "/sales",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        sale_id = sales_response.json()[0]["id"]

        # Delete the sale
        response = client.delete(
            f"/sales/{sale_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"
