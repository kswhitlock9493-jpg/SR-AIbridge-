# brh/test_api_endpoints.py
"""
Tests for new API endpoints (federation state and events)
"""
import pytest
from fastapi.testclient import TestClient
from brh.api import app, log_event, EVENT_LOG


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_events():
    """Clear event log before each test"""
    EVENT_LOG.clear()
    yield
    EVENT_LOG.clear()


class TestEventLogging:
    """Test cases for event logging"""
    
    def test_log_event_adds_to_log(self):
        """Test that log_event adds events to the log"""
        log_event("Test event 1")
        log_event("Test event 2")
        assert len(EVENT_LOG) == 2
        assert EVENT_LOG[0]["message"] == "Test event 1"
        assert EVENT_LOG[1]["message"] == "Test event 2"
    
    def test_log_event_has_timestamp(self):
        """Test that log_event adds timestamps"""
        log_event("Test event")
        assert "time" in EVENT_LOG[0]
        assert "message" in EVENT_LOG[0]
    
    def test_log_event_limits_size(self):
        """Test that event log is limited to 1000 entries"""
        for i in range(1100):
            log_event(f"Event {i}")
        assert len(EVENT_LOG) == 1000
        # First 100 should be removed
        assert EVENT_LOG[0]["message"] == "Event 100"


class TestFederationStateEndpoint:
    """Test cases for /federation/state endpoint"""
    
    def test_federation_state_returns_structure(self, client):
        """Test that federation state endpoint returns expected structure"""
        response = client.get("/federation/state")
        assert response.status_code == 200
        data = response.json()
        assert "leader" in data
        assert "peers" in data
        assert isinstance(data["peers"], list)
    
    def test_federation_state_peer_structure(self, client):
        """Test that peer objects have expected structure"""
        from brh import consensus
        # Add a mock peer
        consensus.peers["test-node"] = {
            "epoch": 123456,
            "status": "alive",
            "sig": "test-sig"
        }
        
        response = client.get("/federation/state")
        assert response.status_code == 200
        data = response.json()
        
        if len(data["peers"]) > 0:
            peer = data["peers"][0]
            assert "node" in peer
            assert "epoch" in peer
            assert "status" in peer
            assert "uptime" in peer


class TestEventsEndpoint:
    """Test cases for /events endpoint"""
    
    def test_events_endpoint_returns_events(self, client):
        """Test that events endpoint returns logged events"""
        log_event("Event 1")
        log_event("Event 2")
        
        response = client.get("/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_events_endpoint_limits_to_50(self, client):
        """Test that events endpoint returns at most 50 events"""
        for i in range(100):
            log_event(f"Event {i}")
        
        response = client.get("/events")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 50
        # Should return last 50
        assert data[0]["message"] == "Event 50"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
