"""Tests for the FastAPI hello endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_hello_returns_hello_world_f_jain():
    """GET /api/hello returns 200 and the F Jain hello payload."""
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World F Jain!"}
