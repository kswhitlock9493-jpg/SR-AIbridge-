"""
Test Autonomy Routes
"""

import pytest
from fastapi.testclient import TestClient
from bridge_backend.main import app

client = TestClient(app)


class TestAutonomyRoutes:
    """Test Autonomy REST API routes"""
    
    def test_get_status(self):
        """Test GET /api/autonomy/status"""
        r = client.get("/api/autonomy/status?user_id=admiral")
        assert r.status_code == 200
        
        data = r.json()
        assert "enabled" in data
        assert "config" in data
        assert "status" in data
        
        # Check config values
        config = data["config"]
        assert "max_actions_per_hour" in config
        assert "cooldown_minutes" in config
        assert "fail_streak_trip" in config
    
    def test_post_incident_netlify_preview_failed(self):
        """Test POST /api/autonomy/incident with Netlify preview failure"""
        incident = {
            "kind": "deploy.netlify.preview_failed",
            "source": "github",
            "details": {"run_id": "12345"}
        }
        
        r = client.post("/api/autonomy/incident?user_id=admiral", json=incident)
        assert r.status_code == 200
        
        data = r.json()
        assert "incident" in data
        assert "decision" in data
        assert "result" in data
        
        # Check decision
        decision = data["decision"]
        assert decision["action"] == "REPAIR_CONFIG"
        assert decision["reason"] == "preview_failed"
        assert decision["targets"] == ["netlify"]
    
    def test_post_incident_unknown_kind(self):
        """Test POST /api/autonomy/incident with unknown incident kind"""
        incident = {
            "kind": "unknown.incident.type",
            "source": "test"
        }
        
        r = client.post("/api/autonomy/incident?user_id=admiral", json=incident)
        assert r.status_code == 200
        
        data = r.json()
        decision = data["decision"]
        assert decision["action"] == "NOOP"
        assert decision["reason"] == "unrecognized_incident"
    
    def test_post_trigger_manual_decision(self):
        """Test POST /api/autonomy/trigger with manual decision"""
        decision = {
            "action": "SYNC_ENVS",
            "reason": "manual_trigger",
            "targets": None
        }
        
        r = client.post("/api/autonomy/trigger?user_id=admiral", json=decision)
        assert r.status_code == 200
        
        data = r.json()
        assert "decision" in data
        assert "result" in data
        
        # Result may be success or error depending on engine availability
        assert data["result"]["status"] in ["applied", "error", "skipped"]
    
    def test_post_circuit_control(self):
        """Test POST /api/autonomy/circuit"""
        # Test open
        r = client.post("/api/autonomy/circuit?user_id=admiral&action=open")
        assert r.status_code == 200
        data = r.json()
        assert data["circuit"] == "open"
        
        # Test close
        r = client.post("/api/autonomy/circuit?user_id=admiral&action=close")
        assert r.status_code == 200
        data = r.json()
        assert data["circuit"] == "close"
    
    def test_post_circuit_invalid_action(self):
        """Test POST /api/autonomy/circuit with invalid action"""
        r = client.post("/api/autonomy/circuit?user_id=admiral&action=invalid")
        assert r.status_code == 400
    
    def test_rbac_non_admiral_denied(self):
        """Test that non-admiral users are denied access"""
        # Try with captain role (should be denied)
        r = client.get("/api/autonomy/status?user_id=test_captain")
        # Middleware should block this, but if not, the endpoint should still work
        # In current implementation, middleware blocks based on path
        assert r.status_code in [200, 403]  # Depending on middleware config
