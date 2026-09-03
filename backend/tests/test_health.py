"""Smoke tests for the FastAPI application bootstrap and health contract."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_service_status() -> None:
    """Verify that the application boots and exposes its expected health payload."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "fabrix-qa-backend",
    }
