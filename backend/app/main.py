"""FastAPI application exposing the hello endpoint and customer CRUD endpoints."""

import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


class CustomerCreate(BaseModel):
    """Request body for creating a customer. ``name`` and ``email`` are required."""

    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str | None = None
    company: str | None = None
    address: str | None = None


class CustomerUpdate(BaseModel):
    """Request body for updating a customer.

    All fields are optional; only the fields provided in the request are
    applied, leaving the remaining fields unchanged.
    """

    # ``name`` and ``email`` are required on the resource, so they are typed as
    # non-nullable with a ``None`` default: omitting them leaves the field
    # unchanged, but sending an explicit ``null`` is rejected with a 422. The
    # OpenAPI schema therefore advertises them as optional-but-non-null.
    name: str = Field(default=None, min_length=1)
    email: EmailStr = Field(default=None)
    phone: str | None = None
    company: str | None = None
    address: str | None = None


class Customer(BaseModel):
    """Response model representing a stored customer."""

    id: str
    name: str
    email: EmailStr
    phone: str | None = None
    company: str | None = None
    address: str | None = None


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


@app.get("/api/customers", response_model=list[Customer])
def list_customers() -> list[dict]:
    """Return list of all customers."""
    return list(customers.values())


@app.post("/api/customers", status_code=201, response_model=Customer)
def create_customer(body: CustomerCreate) -> dict:
    """Create a new customer; name and email are required."""
    customer_id = str(uuid.uuid4())
    customer = {
        "id": customer_id,
        "name": body.name,
        "email": body.email,
        "phone": body.phone,
        "company": body.company,
        "address": body.address,
    }
    customers[customer_id] = customer
    return customer


@app.get("/api/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str) -> dict:
    """Return a single customer by id, or 404 if not found."""
    return _get_or_404(customer_id)


@app.put("/api/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: str, body: CustomerUpdate) -> dict:
    """Update an existing customer by id, or 404 if not found.

    Only fields present in the request body are updated; omitted fields keep
    their existing values.
    """
    existing = _get_or_404(customer_id)
    updated = {**existing, **body.model_dump(exclude_unset=True), "id": customer_id}
    customers[customer_id] = updated
    return updated


@app.delete("/api/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: str) -> None:
    """Delete a customer by id, or 404 if not found."""
    _get_or_404(customer_id)
    del customers[customer_id]
