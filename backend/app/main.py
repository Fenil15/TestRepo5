"""FastAPI application exposing the hello endpoint and customer CRUD endpoints."""

import uuid

from fastapi import FastAPI
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
