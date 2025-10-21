"""
Basic health check tests to validate test framework setup
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_endpoint(test_client):
    """Test health check endpoint returns 200"""
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "invoice-parser-api"
    assert "version" in data


@pytest.mark.unit
def test_root_endpoint(test_client):
    """Test root endpoint returns API information"""
    response = test_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["docs"] == "/docs"
