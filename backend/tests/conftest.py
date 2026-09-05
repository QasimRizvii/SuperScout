"""
SuperScout Backend — Test Configuration

Provides shared fixtures for all backend tests.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture(scope="session")
def app():
    """Create a fresh FastAPI app instance for the test session."""
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    """
    Provide a synchronous test client for route-level tests.

    Using scope='session' means one client is shared across all tests
    in the session, which is efficient for read-only endpoint tests.
    """
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
