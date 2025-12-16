"""
Test Umbra Lattice Core Functionality
"""

import pytest
from datetime import datetime, timezone, timedelta

from bridge_backend.bridge_core.engines.umbra.models import (
    LatticeNode, LatticeEdge, LatticeSnapshot, NodeKind, EdgeKind
)
from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
from bridge_backend.bridge_core.engines.umbra.storage import LatticeStorage


class TestLatticeModels:
    """Test Lattice data models"""
    
    def test_lattice_node_creation(self):
        """Test creating a lattice node"""
        node = LatticeNode(
            id="test:node:1",
            kind="deploy",
            attrs={"service": "render", "status": "success"}
        )
        
        assert node.id == "test:node:1"
        assert node.kind == "deploy"
        assert node.attrs["service"] == "render"
        assert isinstance(node.ts, datetime)
    
    def test_lattice_edge_creation(self):
        """Test creating a lattice edge"""
        edge = LatticeEdge(
            src="commit:abc123",
            dst="deploy:render:1",
            kind="caused_by",
            attrs={"confidence": "high"}
        )
        
        assert edge.src == "commit:abc123"
        assert edge.dst == "deploy:render:1"
        assert edge.kind == "caused_by"
        assert isinstance(edge.ts, datetime)
    
    def test_lattice_snapshot_creation(self):
        """Test creating a lattice snapshot"""
        nodes = [
            LatticeNode(id="n1", kind="commit"),
            LatticeNode(id="n2", kind="deploy")
        ]
        edges = [
            LatticeEdge(src="n1", dst="n2", kind="caused_by")
        ]
        
        snapshot = LatticeSnapshot(
            nodes=nodes,
            edges=edges,
            summary={"nodes": 2, "edges": 1}
        )
        
        assert len(snapshot.nodes) == 2
        assert len(snapshot.edges) == 1
        assert snapshot.summary["nodes"] == 2


@pytest.mark.asyncio
class TestLatticeStorage:
    """Test Lattice storage operations"""
    
    async def test_storage_initialization(self, tmp_path):
        """Test storage initialization"""
        storage = LatticeStorage()
        await storage.initialize()
        
        stats = await storage.get_stats()
        assert "nodes" in stats
        assert "edges" in stats
    
    async def test_add_node(self):
        """Test adding a node to storage"""
        storage = LatticeStorage()
        await storage.initialize()
        
        node = LatticeNode(
            id="test:node:1",
            kind="commit",
            attrs={"sha": "abc123"}
        )
        
        result = await storage.add_node(node, certified=True)
        assert result is True
        
        # Verify it was stored
        nodes = await storage.get_nodes(limit=10)
        assert len(nodes) > 0
        assert any(n.id == "test:node:1" for n in nodes)
    
    async def test_add_edge(self):
        """Test adding an edge to storage"""
        storage = LatticeStorage()
        await storage.initialize()
        
        # Add nodes first
        node1 = LatticeNode(id="n1", kind="commit")
        node2 = LatticeNode(id="n2", kind="deploy")
        await storage.add_node(node1)
        await storage.add_node(node2)
        
        # Add edge
        edge = LatticeEdge(src="n1", dst="n2", kind="caused_by")
        result = await storage.add_edge(edge, certified=True)
        assert result is True
        
        # Verify it was stored
        edges = await storage.get_edges(limit=10)
        assert len(edges) > 0
    
    async def test_query_nodes_by_kind(self):
        """Test querying nodes by kind"""
        storage = LatticeStorage()
        await storage.initialize()
        
        # Add different node types
        await storage.add_node(LatticeNode(id="c1", kind="commit"))
        await storage.add_node(LatticeNode(id="d1", kind="deploy"))
        await storage.add_node(LatticeNode(id="c2", kind="commit"))
        
        # Query commits only
        commits = await storage.get_nodes(kind="commit", limit=10)
        assert len(commits) >= 2
        assert all(n.kind == "commit" for n in commits)
    
    async def test_query_nodes_by_time(self):
        """Test querying nodes by time window"""
        storage = LatticeStorage()
        await storage.initialize()
        
        # Add a node
        node = LatticeNode(id="recent", kind="commit")
        await storage.add_node(node)
        
        # Query recent nodes (last hour)
        since = datetime.now(timezone.utc) - timedelta(hours=1)
        recent = await storage.get_nodes(since=since, limit=10)
        
        assert len(recent) > 0
    
    async def test_create_snapshot(self):
        """Test creating a snapshot"""
        storage = LatticeStorage()
        await storage.initialize()
        
        # Add some data
        await storage.add_node(LatticeNode(id="n1", kind="commit"))
        await storage.add_node(LatticeNode(id="n2", kind="deploy"))
        
        # Create snapshot
        snapshot = await storage.create_snapshot()
        
        assert isinstance(snapshot, LatticeSnapshot)
        assert "nodes" in snapshot.summary
        assert snapshot.summary["nodes"] >= 2


@pytest.mark.asyncio
class TestUmbraLattice:
    """Test Umbra Lattice core functionality"""
    
    async def test_lattice_initialization(self):
        """Test lattice initialization"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        assert lattice.enabled is True
        assert lattice.storage is not None
    
    async def test_record_deploy_event(self):
        """Test recording a deploy event"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        event = {
            "type": "deploy_success",
            "service": "render",
            "status": "success",
            "commit": "abc123",
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
        await lattice.record_event(event)
        
        # Verify it was recorded
        summary = await lattice.get_summary(since="1h")
        assert summary["total_nodes"] > 0
    
    async def test_record_drift_event(self):
        """Test recording a drift event"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        event = {
            "type": "envrecon_drift",
            "context": "env",
            "missing": ["KEY1", "KEY2"],
            "drifted": ["KEY3"],
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
        await lattice.record_event(event)
        
        summary = await lattice.get_summary(since="1h")
        assert summary["total_nodes"] > 0
    
    async def test_record_heal_event(self):
        """Test recording a heal event"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        event = {
            "type": "arie_heal",
            "action": "fix_env",
            "target": "render",
            "status": "applied",
            "ts": datetime.now(timezone.utc).isoformat()
        }
        
        await lattice.record_event(event)
        
        summary = await lattice.get_summary(since="1h")
        assert summary["total_nodes"] > 0
    
    async def test_get_summary(self):
        """Test getting lattice summary"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Add some events
        await lattice.record_event({
            "type": "deploy_success",
            "service": "render",
            "ts": datetime.now(timezone.utc).isoformat()
        })
        
        summary = await lattice.get_summary(since="24h")
        
        assert "total_nodes" in summary
        assert "total_edges" in summary
        assert "node_types" in summary
    
    async def test_mermaid_generation(self):
        """Test mermaid graph generation"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Add some events
        await lattice.record_event({
            "type": "deploy_success",
            "service": "render",
            "commit": "abc123",
            "ts": datetime.now(timezone.utc).isoformat()
        })
        
        mermaid = await lattice.mermaid(since="24h")
        
        assert isinstance(mermaid, str)
        assert "graph TD" in mermaid
    
    async def test_bloom_analysis(self):
        """Test bloom causal analysis"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Add some events with causal relationships
        ts = datetime.now(timezone.utc).isoformat()
        
        await lattice.record_event({
            "type": "deploy_success",
            "service": "render",
            "commit": "abc123",
            "ts": ts
        })
        
        await lattice.record_event({
            "type": "arie_heal",
            "action": "fix_env",
            "target": "render",
            "ts": ts
        })
        
        results = await lattice.bloom()
        
        assert "nodes_analyzed" in results
        assert "causal_chains" in results
        assert "top_causes" in results
    
    async def test_export_snapshot(self):
        """Test exporting a snapshot"""
        lattice = UmbraLattice()
        await lattice.initialize()
        
        # Add some data
        await lattice.record_event({
            "type": "deploy_success",
            "service": "render",
            "ts": datetime.now(timezone.utc).isoformat()
        })
        
        snapshot = await lattice.export_snapshot(since="24h")
        
        assert isinstance(snapshot, LatticeSnapshot)
        assert len(snapshot.nodes) > 0
        assert "nodes" in snapshot.summary
    
    async def test_time_window_parsing(self):
        """Test time window parsing"""
        lattice = UmbraLattice()
        
        # Test various formats
        dt_7d = lattice._parse_time_window("7d")
        dt_24h = lattice._parse_time_window("24h")
        dt_1w = lattice._parse_time_window("1w")
        
        assert dt_7d is not None
        assert dt_24h is not None
        assert dt_1w is not None
        
        # Check they're in the past
        now = datetime.now(timezone.utc)
        assert dt_7d < now
        assert dt_24h < now
        assert dt_1w < now


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
