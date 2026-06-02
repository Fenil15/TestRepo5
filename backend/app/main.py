"""FastAPI application exposing the hello endpoint and customer CRUD endpoints."""

import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Fields the customer list may be sorted by.
SORTABLE_FIELDS = frozenset({"name", "email", "company"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# In-memory customer store: id -> customer dict
customers: dict[str, dict] = {}


def _get_or_404(customer_id: str) -> dict:
    """Return customer by id or raise 404."""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers[customer_id]


@app.get("/api/hello")
def hello() -> dict[str, str]:
    """Return the canonical hello-world payload."""
    return {"message": "Hello, World FJ!"}


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
            if term in (c.get("name") or "").lower()
            or term in (c.get("email") or "").lower()
            or term in (c.get("company") or "").lower()
        ]

    # Sort by an allowed field; fall back to name for unknown values.
    field = sort_by if sort_by in SORTABLE_FIELDS else "name"
    reverse = sort_dir == "desc"
    results.sort(key=lambda c: (c.get(field) or "").lower(), reverse=reverse)

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
