"""
Test suite for the Thirukkural Educational API.
"""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add the project root to sys.path so we can import from src
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Add the backend directory to sys.path so we can import from app
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from app import app

client = TestClient(app)

def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Thirukkural Scenario-Based Decision-Making API" in data["message"]

def test_health():
    """Test the health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_predict_no_file():
    """Test predict endpoint with no file."""
    response = client.post("/predict/")
    assert response.status_code == 422  # Unprocessable Entity

def test_predict_wrong_file_type():
    """Test predict endpoint with a non-image file."""
    # Create a dummy text file
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    response = client.post("/predict/", files=files)
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert data["error"] == "HTTP 400"
    assert data["message"] == "File must be an image"

def test_explain_no_file():
    """Test explain endpoint with no file."""
    response = client.post("/explain/")
    assert response.status_code == 422

def test_chat_missing_fields():
    """Test chat endpoint with missing fields."""
    # Missing image
    response = client.post("/chat/", json={"question": "test"})
    assert response.status_code == 422
    # Missing question
    response = client.post("/chat/", json={"image": "dummy"})
    assert response.status_code == 422

def test_chat_followup_no_session():
    """Test chat followup without an active session."""
    response = client.post("/chat/followup", json={"question": "test"})
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert "message" in data
    assert data["error"] == "HTTP 400"
    assert "No active chat session" in data["message"]

def test_chat_reset():
    """Test reset chat endpoint."""
    response = client.delete("/chat/reset")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "reset" in data["message"].lower()

# Note: Testing the actual prediction and chat endpoints would require sample images.
# For brevity, we skip those tests here, but in a real scenario, we would:
# 1. Upload a known image (e.g., from the dataset)
# 2. Check that the prediction and explanation are returned
# 3. Test chat with that image and verify the answer

if __name__ == "__main__":
    test_root()
    test_health()
    test_predict_no_file()
    test_predict_wrong_file_type()
    test_explain_no_file()
    test_chat_missing_fields()
    test_chat_followup_no_session()
    test_chat_reset()
    print("All tests passed!")