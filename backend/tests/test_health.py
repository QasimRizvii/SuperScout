"""
SuperScout Backend — Health Endpoint Tests

Tests for GET /api/v1/health

These tests verify:
  1. The application starts successfully.
  2. The health endpoint returns HTTP 200.
  3. The response body matches the expected schema.
  4. Database status is reported (healthy or unavailable) — never missing.
"""


def test_app_starts(client):
    """Verify the application starts and the test client can connect."""
    # If the app failed to start, the TestClient fixture itself would have raised.
    # This test makes the startup check explicit.
    assert client is not None


def test_health_endpoint_returns_200(client):
    """GET /api/v1/health must return HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_schema(client):
    """Health response must match the expected JSON schema."""
    response = client.get("/api/v1/health")
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "SuperScout API"
    assert "version" in data
    assert "database" in data


def test_health_database_field_present(client):
    """
    Database field must always be present in the health response.

    The database may be 'healthy' or 'unavailable' depending on the
    test environment — but it must never be absent.
    """
    response = client.get("/api/v1/health")
    data = response.json()

    db = data["database"]
    assert "status" in db
    assert db["status"] in ("healthy", "unavailable")


def test_health_response_content_type(client):
    """Health endpoint must return JSON."""
    response = client.get("/api/v1/health")
    assert "application/json" in response.headers.get("content-type", "")


def test_unknown_route_returns_404(client):
    """Non-existent routes must return 404."""
    response = client.get("/api/v1/nonexistent")
    assert response.status_code == 404
