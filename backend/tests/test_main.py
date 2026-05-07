"""Tests for the FastAPI hello endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello_returns_hello_world_fj():
    """GET /api/hello returns 200 and the FJ-flavored hello payload."""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World FJ!"}
