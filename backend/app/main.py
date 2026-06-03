"""FastAPI application exposing the hello endpoint and customer CRUD endpoints."""

import uuid
from collections import Counter

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Fields the customer list may be sorted by.
SORTABLE_FIELDS = frozenset({"name", "email", "company"})


def _field_text(customer: dict, field: str) -> str:
    """Return a customer field as lowercase text for search/sort.

    Treats only ``None`` as empty; other non-string values (the API accepts raw
    dicts) are stringified so they remain searchable and sortable without crashing.
    """
    value = customer.get(field)
    return "" if value is None else str(value).lower()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# In-memory customer store: id -> customer dict
customers: dict[str, dict] = {}

# Static sample product orders used by the transparent rule-based risk detector.
product_orders: list[dict] = [
    {
        "id": "ORD-1001",
        "customer": "Avery Stone",
        "customerEmail": "avery@example.com",
        "date": "2024-05-01",
        "status": "Processing",
        "products": [
            {
                "name": "Laptop Pro 15",
                "category": "Electronics",
                "quantity": 1,
                "unitPrice": 1299.0,
            },
            {
                "name": "USB-C Dock",
                "category": "Accessories",
                "quantity": 1,
                "unitPrice": 179.99,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "CA",
        "paymentMethod": "Gift Card",
    },
    {
        "id": "ORD-1002",
        "customer": "Mia Chen",
        "customerEmail": "mia@example.com",
        "date": "2024-05-01",
        "status": "Shipped",
        "products": [
            {
                "name": "Cotton T-Shirt",
                "category": "Apparel",
                "quantity": 10,
                "unitPrice": 24.5,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Debit Card",
    },
    {
        "id": "ORD-1003",
        "customer": "Noah Patel",
        "customerEmail": "noah@example.com",
        "date": "2024-05-02",
        "status": "Cancelled",
        "products": [
            {
                "name": "Smart Watch",
                "category": "Electronics",
                "quantity": 1,
                "unitPrice": 299.99,
            },
        ],
        "shippingCountry": "GB",
        "billingCountry": "GB",
        "paymentMethod": "PayPal",
    },
    {
        "id": "ORD-1004",
        "customer": "Sofia Rivera",
        "customerEmail": "sofia@example.com",
        "date": "2024-05-03",
        "status": "Processing",
        "products": [
            {
                "name": "Gaming Console",
                "category": "Electronics",
                "quantity": 1,
                "unitPrice": 399.99,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Gift Card",
    },
    {
        "id": "ORD-1005",
        "customer": "Lucas Martin",
        "customerEmail": "lucas@example.com",
        "date": "2024-05-04",
        "status": "Delivered",
        "products": [
            {
                "name": "Notebook",
                "category": "Office",
                "quantity": 2,
                "unitPrice": 8.5,
            },
            {
                "name": "Pen Set",
                "category": "Office",
                "quantity": 1,
                "unitPrice": 12.0,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Credit Card",
    },
    {
        "id": "ORD-1006",
        "customer": "Repeat Buyer",
        "customerEmail": "repeat@example.com",
        "date": "2024-05-05",
        "status": "Processing",
        "products": [
            {
                "name": "Wireless Mouse",
                "category": "Accessories",
                "quantity": 1,
                "unitPrice": 45.0,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Credit Card",
    },
    {
        "id": "ORD-1007",
        "customer": "Repeat Buyer",
        "customerEmail": "repeat@example.com",
        "date": "2024-05-05",
        "status": "Processing",
        "products": [
            {
                "name": "Keyboard",
                "category": "Accessories",
                "quantity": 1,
                "unitPrice": 85.0,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Credit Card",
    },
    {
        "id": "ORD-1008",
        "customer": "Repeat Buyer",
        "customerEmail": "repeat@example.com",
        "date": "2024-05-05",
        "status": "Processing",
        "products": [
            {
                "name": "Monitor",
                "category": "Electronics",
                "quantity": 1,
                "unitPrice": 219.0,
            },
        ],
        "shippingCountry": "US",
        "billingCountry": "US",
        "paymentMethod": "Gift Card",
    },
]


def calculate_order_total(order: dict) -> float:
    """Return an order total rounded to cents."""
    total = sum(
        product["quantity"] * product["unitPrice"]
        for product in order.get("products", [])
    )
    return round(total, 2)


def count_orders_by_customer_date(orders: list[dict]) -> dict[tuple[str, str], int]:
    """Count orders per customer email and order date."""
    counts: dict[tuple[str, str], int] = {}
    for order in orders:
        key = (order["customerEmail"], order["date"])
        counts[key] = counts.get(key, 0) + 1
    return counts


def score_order_risk(
    order: dict, customer_date_count: int, total: float | None = None
) -> dict:
    """Score one order using transparent fraud-risk rules."""
    score = 0
    reasons: list[str] = []
    if total is None:
        total = calculate_order_total(order)
    total_quantity = sum(product["quantity"] for product in order.get("products", []))

    if total >= 500:
        score += 30
        reasons.append("High order value")
    if total_quantity >= 8:
        score += 20
        reasons.append("Bulk quantity order")
    if customer_date_count >= 3:
        score += 25
        reasons.append("Multiple same-day orders by customer")
    if order.get("billingCountry") != order.get("shippingCountry"):
        score += 20
        reasons.append("Billing and shipping country mismatch")
    if order.get("status") == "Cancelled" and total >= 250:
        score += 15
        reasons.append("Cancelled high-value order")
    if order.get("paymentMethod") == "Gift Card" and total >= 200:
        score += 10
        reasons.append("Gift card payment on elevated order value")

    score = min(score, 100)
    if score >= 60:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {"score": score, "level": level, "reasons": reasons}


def build_order_risk_report(orders: list[dict]) -> dict:
    """Build a sorted risk report and summary for product orders."""
    customer_date_counts = count_orders_by_customer_date(orders)
    scored_orders = []

    for order in orders:
        key = (order["customerEmail"], order["date"])
        total = calculate_order_total(order)
        risk = score_order_risk(order, customer_date_counts[key], total)
        scored_orders.append(
            {
                **order,
                "total": total,
                "riskScore": risk["score"],
                "riskLevel": risk["level"],
                "riskReasons": risk["reasons"],
            }
        )

    scored_orders.sort(key=lambda order: order["riskScore"], reverse=True)

    risk_level_counts = Counter(order["riskLevel"] for order in scored_orders)
    average_risk_score = round(
        sum(order["riskScore"] for order in scored_orders) / len(scored_orders), 2
    ) if scored_orders else 0.0

    return {
        "summary": {
            "totalOrders": len(scored_orders),
            "highRisk": risk_level_counts["High"],
            "mediumRisk": risk_level_counts["Medium"],
            "lowRisk": risk_level_counts["Low"],
            "averageRiskScore": average_risk_score,
        },
        "orders": scored_orders,
    }


def _get_or_404(customer_id: str) -> dict:
    """Return customer by id or raise 404."""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers[customer_id]


@app.get("/api/hello")
def hello() -> dict[str, str]:
    """Return the canonical hello-world payload."""
    return {"message": "Hello, World FJ!"}


@app.get("/api/order-risk")
def get_order_risk() -> dict:
    """Return the product-order risk report."""
    return build_order_risk_report(product_orders)


@app.get("/api/customers")
def list_customers(
    search: str = "",
    sort_by: str = "name",
    sort_dir: str = "asc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> dict:
    """Return a paginated, optionally filtered and sorted list of customers.

    Query params:
    - ``search``: case-insensitive substring matched against name, email and company.
    - ``sort_by``: one of ``name``, ``email`` or ``company`` (defaults to ``name``).
    - ``sort_dir``: ``asc`` or ``desc`` (defaults to ``asc``).
    - ``page``: 1-based page number.
    - ``page_size``: number of records per page (1-100).

    Returns an envelope with ``items`` (the current page), ``total`` (count of all
    matching records), ``page`` and ``page_size`` so the client can build pagination.
    """
    results = list(customers.values())

    # Filter by case-insensitive substring across name, email and company.
    term = search.strip().lower()
    if term:
        results = [
            c
            for c in results
            if term in _field_text(c, "name")
            or term in _field_text(c, "email")
            or term in _field_text(c, "company")
        ]

    # Sort by an allowed field; fall back to name for unknown values.
    field = sort_by if sort_by in SORTABLE_FIELDS else "name"
    reverse = sort_dir == "desc"
    results.sort(key=lambda c: _field_text(c, field), reverse=reverse)

    total = len(results)
    start = (page - 1) * page_size
    items = results[start : start + page_size]

    return {"items": items, "total": total, "page": page, "page_size": page_size}


@app.post("/api/customers", status_code=201)
def create_customer(body: dict) -> dict:
    """Create a new customer; name and email are required."""
    customer_id = str(uuid.uuid4())
    customer = {
        "id": customer_id,
        "name": body["name"],
        "email": body["email"],
        "phone": body.get("phone"),
        "company": body.get("company"),
        "address": body.get("address"),
    }
    customers[customer_id] = customer
    return customer


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str) -> dict:
    """Return a single customer by id, or 404 if not found."""
    return _get_or_404(customer_id)


@app.put("/api/customers/{customer_id}")
def update_customer(customer_id: str, body: dict) -> dict:
    """Update an existing customer by id, or 404 if not found."""
    existing = _get_or_404(customer_id)
    updated = {
        "id": customer_id,
        "name": body.get("name", existing["name"]),
        "email": body.get("email", existing["email"]),
        "phone": body.get("phone", existing["phone"]),
        "company": body.get("company", existing["company"]),
        "address": body.get("address", existing["address"]),
    }
    customers[customer_id] = updated
    return updated


@app.delete("/api/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: str) -> None:
    """Delete a customer by id, or 404 if not found."""
    _get_or_404(customer_id)
    del customers[customer_id]
