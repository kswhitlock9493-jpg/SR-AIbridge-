"""
Smoke test for Umbra Cognitive Stack routes
Tests that routes are accessible and respond correctly
"""

import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)


def test_umbra_status():
    """Test Umbra status endpoint"""
    response = client.get("/umbra/status")
    print(f"Status response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "version" in data
    assert data["version"] == "1.9.7d"
    print(f"✅ Umbra status: {data}")


def test_umbra_metrics():
    """Test Umbra metrics endpoint"""
    response = client.get("/umbra/metrics")
    print(f"Metrics response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "umbra_core" in data
    assert "umbra_memory" in data
    assert "umbra_predictive" in data
    assert "umbra_echo" in data
    print(f"✅ Umbra metrics retrieved successfully")


def test_umbra_detect():
    """Test Umbra detect endpoint"""
    response = client.post("/umbra/detect", json={
        "error_rate": 0.05,
        "response_time": 100,
        "memory_usage": 0.5
    })
    print(f"Detect response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print(f"✅ Umbra detect: {data['status']}")


def test_umbra_memory_recall():
    """Test Umbra memory recall endpoint"""
    response = client.get("/umbra/memory?limit=5")
    print(f"Memory response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "experiences" in data
    assert "count" in data
    print(f"✅ Umbra memory: {data['count']} experiences")


def test_umbra_predict():
    """Test Umbra predict endpoint"""
    response = client.post("/umbra/predict", json={
        "error_rate": 0.05,
        "response_time": 100
    })
    print(f"Predict response: {response.status_code}")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    print(f"✅ Umbra predict: {data['status']}")


if __name__ == "__main__":
    print("\n🧪 Running Umbra Cognitive Stack smoke tests...\n")
    
    try:
        test_umbra_status()
        test_umbra_metrics()
        test_umbra_detect()
        test_umbra_memory_recall()
        test_umbra_predict()
        
        print("\n✅ All Umbra smoke tests passed!\n")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        sys.exit(1)
