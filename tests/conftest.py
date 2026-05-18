import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from services.auth_service import get_password_hash
import models

# Test database URL (in-memory SQLite)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a test database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_users(client, db_session):
    """Create test users in the database."""
    admin = models.User(
        username="test_admin",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    owner = models.User(
        username="test_owner",
        hashed_password=get_password_hash("owner123"),
        role="owner"
    )
    db_session.add(admin)
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(admin)
    db_session.refresh(owner)
    return {"admin": admin, "owner": owner}


@pytest.fixture
def admin_token(client, test_users):
    """Get an admin authentication token."""
    response = client.post(
        "/token",
        data={"username": "test_admin", "password": "admin123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def owner_token(client, test_users):
    """Get an owner authentication token."""
    response = client.post(
        "/token",
        data={"username": "test_owner", "password": "owner123"}
    )
    assert response.status_code == 200, f"Login failed: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    """Get authentication headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_products(client, db_session):
    """Create test products in the database."""
    from datetime import datetime
    products = [
        models.Product(name="Test Product 1", created_at=datetime.utcnow()),
        models.Product(name="Test Product 2", created_at=datetime.utcnow()),
    ]
    for p in products:
        db_session.add(p)
    db_session.commit()
    return products


@pytest.fixture
def test_sales(client, db_session, test_products):
    """Create test sales in the database."""
    from datetime import date
    sales = [
        models.Sale(date=date(2025, 5, 1), product_name="Test Product 1", qty=10),
        models.Sale(date=date(2025, 5, 2), product_name="Test Product 1", qty=15),
        models.Sale(date=date(2025, 5, 3), product_name="Test Product 1", qty=20),
    ]
    for s in sales:
        db_session.add(s)
    db_session.commit()
    return sales
