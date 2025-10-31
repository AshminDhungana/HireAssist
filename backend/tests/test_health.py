import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_response_structure():
    """Test API response has correct structure"""
    response = client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert "message" in data
