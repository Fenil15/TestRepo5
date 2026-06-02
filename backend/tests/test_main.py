"""Tests for the FastAPI hello endpoint and customer CRUD endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, Customer
from app.main import app, get_db

# Use a shared in-memory SQLite database for tests so each test starts with a
# clean schema while exercising the real ORM/session machinery.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Recreate a clean schema before and after each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_hello_returns_hello_world_fj():
    """GET /api/hello returns 200 and the FJ-flavored hello payload."""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World FJ!"}


def test_list_customers_initially_empty():
    """GET /api/customers returns 200 with an empty list initially."""
    response = client.get("/api/customers")
    assert response.status_code == 200
    assert response.json() == []


def test_create_customer_returns_201():
    """POST /api/customers creates a customer and returns 201 with the created object."""
    payload = {"name": "Alice", "email": "alice@example.com"}
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert data["phone"] is None
    assert data["company"] is None
    assert data["address"] is None


def test_create_customer_with_optional_fields():
    """POST /api/customers creates a customer with all optional fields."""
    payload = {
        "name": "Bob",
        "email": "bob@example.com",
        "phone": "555-1234",
        "company": "Acme",
        "address": "123 Main St",
    }
    response = client.post("/api/customers", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["phone"] == "555-1234"
    assert data["company"] == "Acme"
    assert data["address"] == "123 Main St"


def test_create_customer_appears_in_list():
    """Customer created via POST appears in GET /api/customers list."""
    payload = {"name": "Charlie", "email": "charlie@example.com"}
    post_response = client.post("/api/customers", json=payload)
    customer_id = post_response.json()["id"]

    list_response = client.get("/api/customers")
    assert list_response.status_code == 200
    ids = [c["id"] for c in list_response.json()]
    assert customer_id in ids


def test_get_customer_returns_200():
    """GET /api/customers/{id} returns 200 with the customer data."""
    payload = {"name": "Dana", "email": "dana@example.com"}
    created = client.post("/api/customers", json=payload).json()
    customer_id = created["id"]

    response = client.get(f"/api/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_customer_unknown_returns_404():
    """GET /api/customers/{id} returns 404 for unknown id."""
    response = client.get("/api/customers/nonexistent-id")
    assert response.status_code == 404


def test_update_customer_returns_200():
    """PUT /api/customers/{id} updates a customer and returns updated data."""
    created = client.post(
        "/api/customers", json={"name": "Eve", "email": "eve@example.com"}
    ).json()
    customer_id = created["id"]

    update_payload = {"name": "Eve Updated", "email": "eve-updated@example.com", "phone": "999-0000"}
    response = client.put(f"/api/customers/{customer_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
    assert data["name"] == "Eve Updated"
    assert data["email"] == "eve-updated@example.com"
    assert data["phone"] == "999-0000"


def test_update_customer_unknown_returns_404():
    """PUT /api/customers/{id} returns 404 for unknown id."""
    response = client.put(
        "/api/customers/nonexistent-id",
        json={"name": "Ghost", "email": "ghost@example.com"},
    )
    assert response.status_code == 404


def test_delete_customer_returns_204():
    """DELETE /api/customers/{id} deletes a customer and returns 204."""
    created = client.post(
        "/api/customers", json={"name": "Frank", "email": "frank@example.com"}
    ).json()
    customer_id = created["id"]

    response = client.delete(f"/api/customers/{customer_id}")
    assert response.status_code == 204

    # Confirm it's gone
    get_response = client.get(f"/api/customers/{customer_id}")
    assert get_response.status_code == 404


def test_delete_customer_unknown_returns_404():
    """DELETE /api/customers/{id} returns 404 for unknown id."""
    response = client.delete("/api/customers/nonexistent-id")
    assert response.status_code == 404


def test_create_customer_missing_name_returns_400():
    """POST /api/customers with no name returns a controlled 400, not a 500."""
    response = client.post("/api/customers", json={"email": "x@example.com"})
    assert response.status_code == 400


def test_create_customer_null_email_returns_400():
    """POST /api/customers with a null email returns a controlled 400."""
    response = client.post(
        "/api/customers", json={"name": "Ann", "email": None}
    )
    assert response.status_code == 400


def test_update_customer_invalid_name_returns_400():
    """PUT /api/customers/{id} with an empty name returns 400."""
    created = client.post(
        "/api/customers", json={"name": "Ivy", "email": "ivy@example.com"}
    ).json()
    response = client.put(
        f"/api/customers/{created['id']}", json={"name": "   "}
    )
    assert response.status_code == 400


def test_create_customer_invalid_optional_field_returns_400():
    """POST /api/customers with a non-string optional field returns 400."""
    response = client.post(
        "/api/customers",
        json={"name": "A", "email": "a@example.com", "phone": {"bad": "value"}},
    )
    assert response.status_code == 400


def test_update_customer_invalid_optional_field_returns_400():
    """PUT /api/customers/{id} with a non-string optional field returns 400."""
    created = client.post(
        "/api/customers", json={"name": "Jo", "email": "jo@example.com"}
    ).json()
    response = client.put(
        f"/api/customers/{created['id']}", json={"company": ["not", "a", "string"]}
    )
    assert response.status_code == 400


def test_update_customer_preserves_omitted_optional_fields():
    """PUT without phone/company/address leaves the existing values intact."""
    created = client.post(
        "/api/customers",
        json={
            "name": "Kim",
            "email": "kim@example.com",
            "phone": "555-7777",
            "company": "Globex",
            "address": "1 Loop",
        },
    ).json()
    updated = client.put(
        f"/api/customers/{created['id']}", json={"name": "Kim Updated"}
    ).json()
    assert updated["name"] == "Kim Updated"
    assert updated["phone"] == "555-7777"
    assert updated["company"] == "Globex"
    assert updated["address"] == "1 Loop"


def test_list_customers_preserves_insertion_order():
    """GET /api/customers returns customers in the order they were created."""
    names = ["First", "Second", "Third"]
    for name in names:
        client.post(
            "/api/customers", json={"name": name, "email": f"{name}@example.com"}
        )
    listed = [c["name"] for c in client.get("/api/customers").json()]
    assert listed == names


def test_customer_persisted_in_database():
    """Created customers are written to the database, not just process memory."""
    created = client.post(
        "/api/customers", json={"name": "Grace", "email": "grace@example.com"}
    ).json()

    # Read directly from a fresh DB session to confirm the row was committed,
    # which is what allows records to survive a backend restart.
    session = TestingSessionLocal()
    try:
        row = session.get(Customer, created["id"])
        assert row is not None
        assert row.name == "Grace"
        assert row.email == "grace@example.com"
    finally:
        session.close()


def test_cors_allows_post_method():
    """CORS preflight for POST /api/customers is allowed from localhost:5173."""
    response = client.options(
        "/api/customers",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    allowed_methods = response.headers.get("access-control-allow-methods", "")
    assert "POST" in allowed_methods
