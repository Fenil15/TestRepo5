"""FastAPI application exposing the hello endpoint and customer CRUD endpoints.

Customer records are persisted in a relational database (SQLite for local dev,
Postgres for production) so they survive backend restarts and deployments.
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import Customer, SessionLocal, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on application startup."""
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


def get_db():
    """Yield a database session, ensuring it is closed after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_or_404(db: Session, customer_id: str) -> Customer:
    """Return customer by id or raise 404."""
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.get("/api/hello")
def hello() -> dict[str, str]:
    """Return the canonical hello-world payload."""
    return {"message": "Hello, World FJ!"}


def _require_str(body: dict, field: str) -> str:
    """Return a required non-empty string field or raise 400."""
    value = body.get(field)
    if not isinstance(value, str) or not value.strip():
        raise HTTPException(
            status_code=400, detail=f"'{field}' is required and must be a non-empty string"
        )
    return value


def _optional_str(body: dict, field: str, current=None):
    """Return an optional string field (or None), raising 400 for wrong types.

    If the field is absent, ``current`` is returned unchanged so PUT can leave
    existing values in place.
    """
    if field not in body:
        return current
    value = body[field]
    if value is not None and not isinstance(value, str):
        raise HTTPException(
            status_code=400, detail=f"'{field}' must be a string or null"
        )
    return value


@app.get("/api/customers")
def list_customers(db: Session = Depends(get_db)) -> list[dict]:
    """Return list of all customers in insertion order."""
    customers = (
        db.query(Customer).order_by(Customer.created_at, Customer.id).all()
    )
    return [c.to_dict() for c in customers]


@app.post("/api/customers", status_code=201)
def create_customer(body: dict, db: Session = Depends(get_db)) -> dict:
    """Create a new customer; name and email are required."""
    customer = Customer(
        id=str(uuid.uuid4()),
        name=_require_str(body, "name"),
        email=_require_str(body, "email"),
        phone=_optional_str(body, "phone"),
        company=_optional_str(body, "company"),
        address=_optional_str(body, "address"),
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer.to_dict()


@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str, db: Session = Depends(get_db)) -> dict:
    """Return a single customer by id, or 404 if not found."""
    return _get_or_404(db, customer_id).to_dict()


@app.put("/api/customers/{customer_id}")
def update_customer(
    customer_id: str, body: dict, db: Session = Depends(get_db)
) -> dict:
    """Update an existing customer by id, or 404 if not found."""
    customer = _get_or_404(db, customer_id)
    if "name" in body:
        customer.name = _require_str(body, "name")
    if "email" in body:
        customer.email = _require_str(body, "email")
    customer.phone = _optional_str(body, "phone", customer.phone)
    customer.company = _optional_str(body, "company", customer.company)
    customer.address = _optional_str(body, "address", customer.address)
    db.commit()
    db.refresh(customer)
    return customer.to_dict()


@app.delete("/api/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: str, db: Session = Depends(get_db)) -> None:
    """Delete a customer by id, or 404 if not found."""
    customer = _get_or_404(db, customer_id)
    db.delete(customer)
    db.commit()
