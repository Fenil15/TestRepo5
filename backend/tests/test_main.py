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


def make_order(**overrides):
    """Build a product order for risk-scoring tests."""
    order = {
        "id": "ORD-TEST",
        "customer": "Test Customer",
        "customerEmail": "test@example.com",
        "date": "2024-05-10",
        "status": "Processing",
        "products": [
            {
                "name": "Sticker Pack",
                "category": "Accessories",
                "quantity": 1,
                "unitPrice": 10.0,
            }
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Credit Card",
    }
    order.update(overrides)
    return order


def test_calculate_order_total_with_multiple_products():
    """Order totals include all product lines and are rounded to cents."""
    order = make_order(
        products=[
            {
                "name": "Widget",
                "category": "Tools",
                "quantity": 2,
                "unitPrice": 12.345,
            },
            {"name": "Gadget", "category": "Tools", "quantity": 3, "unitPrice": 5.5},
        ]
    )

    assert main_module.calculate_order_total(order) == 41.19


def test_count_orders_by_customer_date_groups_email_and_date():
    """Order counts are grouped by customer email and order date."""
    orders = [
        make_order(id="ORD-1", customerEmail="a@example.com", date="2024-05-10"),
        make_order(id="ORD-2", customerEmail="a@example.com", date="2024-05-10"),
        make_order(id="ORD-3", customerEmail="a@example.com", date="2024-05-11"),
        make_order(id="ORD-4", customerEmail="b@example.com", date="2024-05-10"),
    ]

    assert main_module.count_orders_by_customer_date(orders) == {
        ("a@example.com", "2024-05-10"): 2,
        ("a@example.com", "2024-05-11"): 1,
        ("b@example.com", "2024-05-10"): 1,
    }


def test_score_order_risk_high_value_and_country_mismatch():
    """High value plus billing/shipping mismatch scores as medium risk."""
    order = make_order(
        products=[
            {
                "name": "Premium Tablet",
                "category": "Electronics",
                "quantity": 1,
                "unitPrice": 650.0,
            }
        ],
        shippingCountry="US",
        billingCountry="CA",
    )

    risk = main_module.score_order_risk(order, customer_date_count=1)

    assert risk == {
        "score": 50,
        "level": "Medium",
        "reasons": [
            "High order value",
            "Billing and shipping country mismatch",
        ],
    }


def test_score_order_risk_same_day_repeat_customer_count_of_three():
    """Customers with three same-day orders receive the repeat-order signal."""
    risk = main_module.score_order_risk(make_order(), customer_date_count=3)

    assert risk["score"] == 25
    assert risk["level"] == "Low"
    assert risk["reasons"] == ["Multiple same-day orders by customer"]


def test_score_order_risk_low_risk_order():
    """A normal low-value order has no signals and remains low risk."""
    risk = main_module.score_order_risk(make_order(), customer_date_count=1)

    assert risk["score"] < 30
    assert risk["level"] == "Low"
    assert risk["reasons"] == []


def test_score_order_risk_caps_at_100():
    """Risk scores are capped at 100 when all scoring rules match."""
    order = make_order(
        status="Cancelled",
        products=[
            {
                "name": "Camera Bundle",
                "category": "Electronics",
                "quantity": 8,
                "unitPrice": 100.0,
            }
        ],
        shippingCountry="US",
        billingCountry="CA",
        paymentMethod="Gift Card",
    )

    risk = main_module.score_order_risk(order, customer_date_count=3)

    assert risk["score"] == 100
    assert risk["level"] == "High"
    assert risk["reasons"] == [
        "High order value",
        "Bulk quantity order",
        "Multiple same-day orders by customer",
        "Billing and shipping country mismatch",
        "Cancelled high-value order",
        "Gift card payment on elevated order value",
    ]


def test_build_order_risk_report_empty_orders():
    """Empty reports return zeroed summary values and no orders."""
    report = main_module.build_order_risk_report([])

    assert report == {
        "summary": {
            "totalOrders": 0,
            "highRisk": 0,
            "mediumRisk": 0,
            "lowRisk": 0,
            "averageRiskScore": 0.0,
        },
        "orders": [],
    }


def test_build_order_risk_report_rounds_average_risk_score():
    """Average risk score is rounded to two decimal places."""
    orders = [
        make_order(id="ORD-LOW", customerEmail="low@example.com", products=[]),
        make_order(
            id="ORD-MEDIUM",
            customerEmail="medium@example.com",
            products=[
                {
                    "name": "Bulk Socks",
                    "category": "Apparel",
                    "quantity": 8,
                    "unitPrice": 5.0,
                }
            ],
        ),
        make_order(
            id="ORD-HIGH",
            customerEmail="high@example.com",
            products=[
                {
                    "name": "Laptop",
                    "category": "Electronics",
                    "quantity": 1,
                    "unitPrice": 600.0,
                }
            ],
            shippingCountry="US",
            billingCountry="CA",
        ),
    ]

    report = main_module.build_order_risk_report(orders)

    assert report["summary"]["averageRiskScore"] == 23.33


def test_build_order_risk_report_summary_counts_are_correct():
    """Report summary counts each risk level correctly."""
    orders = [
        make_order(
            id="ORD-HIGH",
            customerEmail="high@example.com",
            products=[
                {
                    "name": "Laptop",
                    "category": "Electronics",
                    "quantity": 1,
                    "unitPrice": 600.0,
                }
            ],
            shippingCountry="US",
            billingCountry="CA",
            paymentMethod="Gift Card",
        ),
        make_order(
            id="ORD-MEDIUM",
            customerEmail="medium@example.com",
            products=[
                {
                    "name": "Console",
                    "category": "Electronics",
                    "quantity": 1,
                    "unitPrice": 500.0,
                }
            ],
        ),
        make_order(id="ORD-LOW", customerEmail="low@example.com"),
    ]

    summary = main_module.build_order_risk_report(orders)["summary"]

    assert summary["totalOrders"] == 3
    assert summary["highRisk"] == 1
    assert summary["mediumRisk"] == 1
    assert summary["lowRisk"] == 1


def test_get_order_risk_returns_summary_and_sorted_orders():
    """GET /api/order-risk returns the scored sample-order report."""
    response = client.get("/api/order-risk")

    assert response.status_code == 200
    data = response.json()
    assert set(data["summary"]) == {
        "totalOrders",
        "highRisk",
        "mediumRisk",
        "lowRisk",
        "averageRiskScore",
    }
    assert data["summary"]["totalOrders"] == len(main_module.product_orders)
    assert data["summary"]["highRisk"] >= 1

    risk_scores = [order["riskScore"] for order in data["orders"]]
    assert risk_scores == sorted(risk_scores, reverse=True)
    assert any(order["riskLevel"] == "High" for order in data["orders"])
    for order in data["orders"]:
        assert {
            "id",
            "customer",
            "customerEmail",
            "date",
            "status",
            "products",
            "shippingCountry",
            "billingCountry",
            "paymentMethod",
            "total",
            "riskScore",
            "riskLevel",
            "riskReasons",
        }.issubset(order)
