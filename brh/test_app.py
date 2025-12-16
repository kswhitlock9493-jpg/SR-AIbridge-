# brh/test_app.py
"""
Tests for BRH FastAPI serverless backend (brh/app.py)
"""
import pytest
from fastapi.testclient import TestClient
from brh.app import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


class TestHealthEndpoint:
    """Test cases for /health endpoint"""
    
    def test_health_returns_ok(self, client):
        """Test that health endpoint returns ok status"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "uptime_s" in data
        assert data["mode"] == "serverless"
    
    def test_health_includes_env_flags(self, client):
        """Test that health endpoint includes environment flags"""
        response = client.get("/health")
        data = response.json()
        assert "env" in data
        assert "FORGE_DOMINION_ROOT" in data["env"]
        assert "DOMINION_SEAL" in data["env"]
        assert isinstance(data["env"]["FORGE_DOMINION_ROOT"], bool)
        assert isinstance(data["env"]["DOMINION_SEAL"], bool)
    
    def test_health_uptime_increases(self, client):
        """Test that uptime increases between calls"""
        import time
        response1 = client.get("/health")
        uptime1 = response1.json()["uptime_s"]
        time.sleep(0.1)
        response2 = client.get("/health")
        uptime2 = response2.json()["uptime_s"]
        assert uptime2 > uptime1


class TestGenesisHeartbeat:
    """Test cases for /genesis/heartbeat endpoint"""
    
    def test_heartbeat_returns_alive(self, client):
        """Test that heartbeat confirms backend is alive"""
        response = client.post("/genesis/heartbeat")
        assert response.status_code == 200
        data = response.json()
        assert data["bridge"] == "alive"
        assert data["brh"] == "ready"


class TestSelfHealEndpoint:
    """Test cases for /triage/self-heal endpoint"""
    
    def test_self_heal_queues_operation(self, client):
        """Test that self-heal endpoint queues the operation"""
        response = client.post("/triage/self-heal")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["op"] == "self_heal"


class TestWorkflowExecution:
    """Test cases for /workflows/execute endpoint"""
    
    def test_execute_accepts_workflow(self, client):
        """Test that workflow execution accepts a workflow"""
        payload = {
            "name": "test_workflow",
            "payload": {"test": "data"}
        }
        response = client.post("/workflows/execute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert data["workflow"] == "test_workflow"
    
    def test_execute_accepts_workflow_without_payload(self, client):
        """Test that workflow execution works without payload"""
        payload = {"name": "simple_workflow"}
        response = client.post("/workflows/execute", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["accepted"] is True
        assert data["workflow"] == "simple_workflow"
    
    def test_execute_requires_name(self, client):
        """Test that workflow execution requires a name"""
        payload = {"payload": {"test": "data"}}
        response = client.post("/workflows/execute", json=payload)
        assert response.status_code == 422  # Validation error


class TestOpenAPIDocumentation:
    """Test cases for API documentation"""
    
    def test_openapi_json_accessible(self, client):
        """Test that OpenAPI JSON is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "BRH"
        assert data["info"]["version"] == "1.0.0"
    
    def test_docs_accessible(self, client):
        """Test that Swagger UI docs are accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_redoc_accessible(self, client):
        """Test that ReDoc docs are accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200
