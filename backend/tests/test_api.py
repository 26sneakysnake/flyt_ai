import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "FlightBrief AI API" in response.json()["message"]


# Additional tests would include:
# - test_upload_valid_pdf()
# - test_upload_invalid_file()
# - test_analyze_pdf()
# - test_generate_briefing()
# - test_download_briefing()
