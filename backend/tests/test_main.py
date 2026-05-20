"""Tests for the FastAPI hello endpoint and customer CRUD endpoints."""

import pytest
from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_customers():
    """Clear the in-memory customers store before each test."""
    main_module.customers.clear()
    yield
    main_module.customers.clear()


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
