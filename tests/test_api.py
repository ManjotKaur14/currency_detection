"""
Tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestAPIEndpoints:
    """Test API endpoint functionality."""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns HTML."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Currency Detector" in response.text
    
    def test_upload_endpoint_no_file(self):
        """Test upload endpoint without file."""
        response = client.post("/upload")
        assert response.status_code == 422  # Validation error
    
    def test_analyze_endpoint_no_file(self):
        """Test analyze endpoint without file."""
        response = client.post("/analyze")
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.skip(reason="Requires actual image file for testing")
    def test_upload_with_image(self):
        """Test upload endpoint with actual image."""
        # This would test with a real image file
        # files = {"image": ("test.jpg", open("test_image.jpg", "rb"), "image/jpeg")}
        # response = client.post("/upload", files=files)
        # assert response.status_code == 200
        pass
    
    @pytest.mark.skip(reason="Requires actual image file for testing")
    def test_analyze_with_image(self):
        """Test analyze endpoint with actual image."""
        # This would test with a real image file
        # files = {"image": ("test.jpg", open("test_image.jpg", "rb"), "image/jpeg")}
        # response = client.post("/analyze", files=files)
        # assert response.status_code == 200
        pass