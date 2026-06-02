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
    """GET /api/customers returns 200 with an empty paginated envelope initially."""
    response = client.get("/api/customers")
    assert response.status_code == 200
    assert response.json() == {"items": [], "total": 0, "page": 1, "page_size": 10}


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
    ids = [c["id"] for c in list_response.json()["items"]]
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


def _seed(*customers_data: dict) -> None:
    """Create the given customers via the API."""
    for data in customers_data:
        client.post("/api/customers", json=data)


def test_list_returns_paginated_envelope():
    """GET /api/customers wraps results in items/total/page/page_size."""
    _seed({"name": "Alice", "email": "alice@example.com"})
    body = client.get("/api/customers").json()
    assert set(body.keys()) == {"items", "total", "page", "page_size"}
    assert body["total"] == 1
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert len(body["items"]) == 1


def test_search_matches_name_email_company_case_insensitive():
    """search filters across name, email and company, ignoring case."""
    _seed(
        {"name": "Alice Wong", "email": "alice@acme.com", "company": "Acme"},
        {"name": "Bob Stone", "email": "bob@globex.com", "company": "Globex"},
        {"name": "Carol Reed", "email": "carol@initech.com", "company": "Initech"},
    )

    # Match by name fragment.
    names = [c["name"] for c in client.get("/api/customers?search=ali").json()["items"]]
    assert names == ["Alice Wong"]

    # Match by email fragment.
    names = [c["name"] for c in client.get("/api/customers?search=GLOBEX").json()["items"]]
    assert names == ["Bob Stone"]

    # Match by company fragment.
    names = [c["name"] for c in client.get("/api/customers?search=initech").json()["items"]]
    assert names == ["Carol Reed"]


def test_search_no_match_returns_empty():
    """search with no matches returns an empty page with total 0."""
    _seed({"name": "Alice", "email": "alice@example.com"})
    body = client.get("/api/customers?search=zzz").json()
    assert body["items"] == []
    assert body["total"] == 0


def test_sort_by_name_asc_and_desc():
    """sort_by=name orders results ascending or descending."""
    _seed(
        {"name": "Charlie", "email": "c@example.com"},
        {"name": "alice", "email": "a@example.com"},
        {"name": "Bob", "email": "b@example.com"},
    )

    asc = [c["name"] for c in client.get("/api/customers?sort_by=name&sort_dir=asc").json()["items"]]
    assert asc == ["alice", "Bob", "Charlie"]

    desc = [c["name"] for c in client.get("/api/customers?sort_by=name&sort_dir=desc").json()["items"]]
    assert desc == ["Charlie", "Bob", "alice"]


def test_sort_by_email():
    """sort_by=email orders results by email."""
    _seed(
        {"name": "X", "email": "zed@example.com"},
        {"name": "Y", "email": "amy@example.com"},
    )
    emails = [c["email"] for c in client.get("/api/customers?sort_by=email").json()["items"]]
    assert emails == ["amy@example.com", "zed@example.com"]


def test_sort_unknown_field_falls_back_to_name():
    """An unknown sort_by value falls back to sorting by name."""
    _seed(
        {"name": "Bob", "email": "b@example.com"},
        {"name": "Alice", "email": "a@example.com"},
    )
    names = [c["name"] for c in client.get("/api/customers?sort_by=bogus").json()["items"]]
    assert names == ["Alice", "Bob"]


def test_pagination_splits_results():
    """page and page_size control the slice of results returned."""
    _seed(*[{"name": f"User{i:02d}", "email": f"user{i:02d}@example.com"} for i in range(25)])

    page1 = client.get("/api/customers?page=1&page_size=10").json()
    assert page1["total"] == 25
    assert len(page1["items"]) == 10
    assert page1["items"][0]["name"] == "User00"

    page3 = client.get("/api/customers?page=3&page_size=10").json()
    assert len(page3["items"]) == 5
    assert page3["items"][0]["name"] == "User20"


def test_pagination_out_of_range_returns_empty_items():
    """A page beyond the available results returns empty items but correct total."""
    _seed({"name": "Alice", "email": "alice@example.com"})
    body = client.get("/api/customers?page=5&page_size=10").json()
    assert body["items"] == []
    assert body["total"] == 1
    assert body["page"] == 5


def test_invalid_pagination_params_rejected():
    """page < 1 and page_size out of bounds are rejected with 422."""
    assert client.get("/api/customers?page=0").status_code == 422
    assert client.get("/api/customers?page_size=0").status_code == 422
    assert client.get("/api/customers?page_size=101").status_code == 422


def test_search_sort_and_pagination_combined():
    """search, sort and pagination work together."""
    _seed(
        {"name": "Acme Alice", "email": "alice@acme.com", "company": "Acme"},
        {"name": "Acme Bob", "email": "bob@acme.com", "company": "Acme"},
        {"name": "Acme Carol", "email": "carol@acme.com", "company": "Acme"},
        {"name": "Other Dave", "email": "dave@other.com", "company": "Other"},
    )
    body = client.get(
        "/api/customers?search=acme&sort_by=name&sort_dir=desc&page=1&page_size=2"
    ).json()
    assert body["total"] == 3
    assert [c["name"] for c in body["items"]] == ["Acme Carol", "Acme Bob"]


def test_list_handles_non_string_field_values():
    """Non-string stored field values do not crash search/sort (regression)."""
    # The API accepts raw dicts, so a numeric name can be stored.
    client.post("/api/customers", json={"name": 123, "email": "num@example.com"})
    client.post("/api/customers", json={"name": "Alice", "email": "alice@example.com"})

    # Listing with sort + search must not 500 on the non-string value.
    resp = client.get("/api/customers?sort_by=name&search=alice")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()["items"]]
    assert names == ["Alice"]


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
