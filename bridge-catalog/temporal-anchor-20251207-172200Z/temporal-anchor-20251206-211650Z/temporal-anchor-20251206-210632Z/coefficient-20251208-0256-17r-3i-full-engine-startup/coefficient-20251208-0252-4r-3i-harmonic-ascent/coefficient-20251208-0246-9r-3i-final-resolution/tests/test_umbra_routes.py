"""
Test Umbra Lattice REST API Routes
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone


@pytest.fixture
def client():
    """Create test client"""
    from bridge_backend.main import app
    return TestClient(app)


class TestUmbraLatticeRoutes:
    """Test Umbra Lattice API endpoints"""
    
    def test_lattice_summary_endpoint(self, client):
        """Test GET /api/umbra/lattice/summary"""
        response = client.get("/api/umbra/lattice/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_nodes" in data
        assert "total_edges" in data
        assert "window" in data
    
    def test_lattice_summary_with_window(self, client):
        """Test GET /api/umbra/lattice/summary with time window"""
        response = client.get("/api/umbra/lattice/summary?since=7d")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["window"] == "7d"
        assert "total_nodes" in data
    
    def test_lattice_mermaid_endpoint(self, client):
        """Test GET /api/umbra/lattice/mermaid"""
        response = client.get("/api/umbra/lattice/mermaid")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "mermaid" in data
        assert "since" in data
        assert "graph TD" in data["mermaid"]
    
    def test_lattice_mermaid_with_window(self, client):
        """Test GET /api/umbra/lattice/mermaid with time window"""
        response = client.get("/api/umbra/lattice/mermaid?since=24h")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["since"] == "24h"
        assert "mermaid" in data
    
    def test_lattice_export_endpoint(self, client):
        """Test POST /api/umbra/lattice/export"""
        response = client.post("/api/umbra/lattice/export")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "exported"
        assert "snapshot" in data
        assert "path" in data
        assert ".umbra/snapshots/" in data["path"]
    
    def test_lattice_bloom_endpoint(self, client):
        """Test POST /api/umbra/lattice/bloom"""
        response = client.post("/api/umbra/lattice/bloom")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "complete"
        assert "analysis" in data
        
        analysis = data["analysis"]
        assert "nodes_analyzed" in analysis
        assert "causal_chains" in analysis
        assert "top_causes" in analysis
    
    def test_lattice_stats_endpoint(self, client):
        """Test GET /api/umbra/lattice/stats"""
        response = client.get("/api/umbra/lattice/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "nodes" in data
        assert "edges" in data
        assert "db_path" in data
    
    def test_umbra_status_includes_lattice(self, client):
        """Test /api/umbra/status includes lattice"""
        response = client.get("/api/umbra/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "active"
        assert data["version"] == "1.9.7g"
        assert "engines" in data
        assert "lattice" in data["engines"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
