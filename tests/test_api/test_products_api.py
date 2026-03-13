import pytest
from fastapi.testclient import TestClient


class TestProductsAPI:
    """Test products API endpoints."""

    def test_get_products_empty(self, client: TestClient, admin_token):
        """Test getting products when none exist."""
        response = client.get(
            "/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json() == []

    def test_get_products_with_data(self, client: TestClient, admin_token, test_products):
        """Test getting products with data."""
        response = client.get(
            "/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_create_product_admin(self, client: TestClient, admin_token):
        """Test creating a product as admin."""
        product_data = {"name": "New Product"}
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_create_duplicate_product(self, client: TestClient, admin_token, test_products):
        """Test creating a duplicate product."""
        product_data = {"name": "Test Product 1"}
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 400

    def test_create_product_owner_forbidden(self, client: TestClient, owner_token):
        """Test that owner cannot create products."""
        product_data = {"name": "New Product"}
        response = client.post(
            "/products",
            json=product_data,
            headers={"Authorization": f"Bearer {owner_token}"}
        )

        assert response.status_code == 403

    def test_delete_product_without_sales(self, client: TestClient, admin_token, test_products):
        """Test deleting a product that has no sales."""
        # Get product ID
        products_response = client.get(
            "/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = products_response.json()[0]["id"]

        response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 200

    def test_delete_product_with_sales_fails(self, client: TestClient, admin_token, test_sales):
        """Test that deleting a product with sales fails."""
        # Get product ID (Test Product 1 has sales)
        products_response = client.get(
            "/products",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        product_id = next(p["id"] for p in products_response.json() if p["name"] == "Test Product 1")

        response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

        assert response.status_code == 400
