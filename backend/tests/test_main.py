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


def test_create_customer_missing_name_returns_422():
    """POST /api/customers without name returns 422, not a 500."""
    response = client.post("/api/customers", json={"email": "noname@example.com"})
    assert response.status_code == 422


def test_create_customer_missing_email_returns_422():
    """POST /api/customers without email returns 422, not a 500."""
    response = client.post("/api/customers", json={"name": "No Email"})
    assert response.status_code == 422


def test_create_customer_malformed_email_returns_422():
    """POST /api/customers with an invalid email returns 422."""
    response = client.post(
        "/api/customers", json={"name": "Bad Email", "email": "not-an-email"}
    )
    assert response.status_code == 422


def test_create_customer_empty_name_returns_422():
    """POST /api/customers with an empty name returns 422."""
    response = client.post(
        "/api/customers", json={"name": "", "email": "empty@example.com"}
    )
    assert response.status_code == 422


def test_create_customer_empty_body_returns_422():
    """POST /api/customers with no body returns 422 instead of crashing."""
    response = client.post("/api/customers", json={})
    assert response.status_code == 422


def test_update_customer_partial_keeps_existing_fields():
    """PUT with a subset of fields updates only those and keeps the rest."""
    created = client.post(
        "/api/customers",
        json={"name": "Grace", "email": "grace@example.com", "phone": "111-2222"},
    ).json()
    customer_id = created["id"]

    response = client.put(
        f"/api/customers/{customer_id}", json={"name": "Grace Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Grace Updated"
    assert data["email"] == "grace@example.com"
    assert data["phone"] == "111-2222"


def test_update_customer_malformed_email_returns_422():
    """PUT /api/customers/{id} with an invalid email returns 422."""
    created = client.post(
        "/api/customers", json={"name": "Heidi", "email": "heidi@example.com"}
    ).json()
    customer_id = created["id"]

    response = client.put(
        f"/api/customers/{customer_id}", json={"email": "not-an-email"}
    )
    assert response.status_code == 422


def test_update_customer_null_name_returns_422_and_preserves_customer():
    """PUT with explicit null name returns 422 and leaves the stored customer intact."""
    created = client.post(
        "/api/customers", json={"name": "Ivan", "email": "ivan@example.com"}
    ).json()
    customer_id = created["id"]

    response = client.put(f"/api/customers/{customer_id}", json={"name": None})
    assert response.status_code == 422

    # The existing customer must remain valid and unchanged.
    after = client.get(f"/api/customers/{customer_id}")
    assert after.status_code == 200
    assert after.json() == created


def test_update_customer_null_email_returns_422_and_preserves_customer():
    """PUT with explicit null email returns 422 and leaves the stored customer intact."""
    created = client.post(
        "/api/customers", json={"name": "Judy", "email": "judy@example.com"}
    ).json()
    customer_id = created["id"]

    response = client.put(f"/api/customers/{customer_id}", json={"email": None})
    assert response.status_code == 422

    after = client.get(f"/api/customers/{customer_id}")
    assert after.status_code == 200
    assert after.json() == created


def test_openapi_documents_customer_schema():
    """The OpenAPI schema exposes the typed Customer/CustomerCreate models."""
    schema = client.get("/openapi.json").json()
    components = schema.get("components", {}).get("schemas", {})
    assert "CustomerCreate" in components
    assert "Customer" in components
    assert "CustomerUpdate" in components

    # name/email are required-on-resource: the schema must NOT advertise them as
    # nullable, since sending an explicit null is rejected with a 422.
    update_props = components["CustomerUpdate"]["properties"]
    assert update_props["name"]["type"] == "string"
    assert "anyOf" not in update_props["name"]
    assert update_props["email"]["type"] == "string"
    assert "anyOf" not in update_props["email"]


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
