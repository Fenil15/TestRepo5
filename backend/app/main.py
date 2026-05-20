"""FastAPI application exposing the hello endpoint and customer CRUD endpoints."""

import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# In-memory customer store: id -> customer dict
customers: dict[str, dict] = {}


@app.get("/api/hello")
def hello() -> dict[str, str]:
    """Return the canonical hello-world payload."""
    return {"message": "Hello, World FJ!"}


@app.get("/api/customers")
def list_customers() -> list[dict]:
    """Return list of all customers."""
    return list(customers.values())


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
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customers[customer_id]


@app.put("/api/customers/{customer_id}")
def update_customer(customer_id: str, body: dict) -> dict:
    """Update an existing customer by id, or 404 if not found."""
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing = customers[customer_id]
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
