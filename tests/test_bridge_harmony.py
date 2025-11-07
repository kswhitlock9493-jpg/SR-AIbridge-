#!/usr/bin/env python3
"""
Test Bridge Harmony & Communication Unification System
"""

import pytest
from pathlib import Path
import sys


class TestBridgeHarmonyOrchestrator:
    """Test suite for Bridge Harmony Orchestration"""
    
    def test_orchestrator_init(self):
        """Test orchestrator initialization"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        assert orchestrator is not None
        assert orchestrator.engines == {}
        assert orchestrator.communication_paths == []
        
    def test_discover_engines(self):
        """Test engine discovery"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        engines = orchestrator.discover_engines()
        
        # Verify we discovered engines
        assert len(engines) >= 33, "Should discover at least 33 engines"
        
        # Verify core engines are present
        core_engines = ["Blueprint", "HXO_Nexus", "Cascade", "Truth", "Autonomy", "Parser"]
        for engine in core_engines:
            assert engine in engines, f"Core engine {engine} should be discovered"
            assert engines[engine].category == "core"
            
        # Verify super engines are present
        super_engines = ["Leviathan", "CalculusCore", "QHelmSingularity"]
        for engine in super_engines:
            assert engine in engines, f"Super engine {engine} should be discovered"
            assert engines[engine].category == "super"
            
        # Verify utility engines are present
        utility_engines = ["Umbra_Lattice", "Genesis_Bus", "Forge_Dominion", "ARIE"]
        for engine in utility_engines:
            assert engine in engines, f"Utility engine {engine} should be discovered"
            assert engines[engine].category == "utility"
    
    def test_auto_wire_communications(self):
        """Test auto-wiring communication pathways"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        orchestrator.discover_engines()
        paths = orchestrator.auto_wire_communications()
        
        # Verify communication paths were created
        assert len(paths) > 0, "Should create communication pathways"
        
        # Verify Genesis Bus connections
        genesis_paths = [p for p in paths if p.protocol == "genesis_bus"]
        assert len(genesis_paths) > 0, "Should have Genesis Bus connections"
        
        # Verify Umbra Lattice connections
        umbra_paths = [p for p in paths if p.protocol == "umbra_lattice"]
        assert len(umbra_paths) > 0, "Should have Umbra Lattice connections"
        
        # Verify direct connections
        direct_paths = [p for p in paths if p.protocol == "direct"]
        assert len(direct_paths) > 0, "Should have direct connections"
        
        # All paths should be verified
        for path in paths:
            assert path.status == "verified", f"Path {path.source} -> {path.target} should be verified"
    
    def test_verify_documentation_links(self):
        """Test documentation link verification"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        broken_count = orchestrator.verify_documentation_links()
        
        # All documentation links should be valid
        assert broken_count == 0, "All documentation links should be functional"
    
    def test_establish_bridge_resonance(self):
        """Test bridge resonance establishment"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        orchestrator.discover_engines()
        orchestrator.auto_wire_communications()
        
        metrics = orchestrator.establish_bridge_resonance()
        
        # Verify metrics structure
        assert "total_engines" in metrics
        assert "engines_by_category" in metrics
        assert "communication_paths" in metrics
        assert "resonance_percentage" in metrics
        assert "communication_health" in metrics
        assert "harmony_status" in metrics
        
        # Verify metric values
        assert metrics["total_engines"] >= 33
        assert metrics["resonance_percentage"] > 0
        assert metrics["communication_health"] > 0
        assert metrics["harmony_status"] in ["PERFECT", "GOOD", "NEEDS_TUNING"]
    
    def test_full_orchestration(self):
        """Test complete harmony orchestration"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        result = orchestrator.orchestrate_full_harmony()
        
        # Should return success (0)
        assert result == 0, "Full orchestration should succeed"
        
        # Verify engines were discovered
        assert len(orchestrator.engines) >= 33
        
        # Verify communication paths were established
        assert len(orchestrator.communication_paths) > 0
        
        # Verify report was generated
        report_path = orchestrator.repo_root / "BRIDGE_HARMONY_REPORT.md"
        assert report_path.exists(), "Harmony report should be generated"
    
    def test_engine_dependencies(self):
        """Test engine dependency mapping"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        orchestrator.discover_engines()
        
        # HXO Nexus should depend on Umbra Lattice and Genesis Bus
        hxo = orchestrator.engines.get("HXO_Nexus")
        assert hxo is not None
        assert "Genesis_Bus" in hxo.dependencies
        assert "Umbra_Lattice" in hxo.dependencies
        
        # Super engines should depend on Leviathan (except Leviathan itself)
        calculus = orchestrator.engines.get("CalculusCore")
        if calculus:
            assert "Leviathan" in calculus.dependencies
            assert "HXO_Nexus" in calculus.dependencies
        
        # Autonomy should depend on Truth and HXO
        autonomy = orchestrator.engines.get("Autonomy")
        assert autonomy is not None
        assert "Truth" in autonomy.dependencies
        assert "HXO_Nexus" in autonomy.dependencies
    
    def test_communication_protocols(self):
        """Test different communication protocols are used correctly"""
        from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
        orchestrator = BridgeHarmonyOrchestrator()
        orchestrator.discover_engines()
        orchestrator.auto_wire_communications()
        
        # Verify protocol distribution
        protocols = set(p.protocol for p in orchestrator.communication_paths)
        assert "genesis_bus" in protocols, "Should use Genesis Bus protocol"
        assert "umbra_lattice" in protocols, "Should use Umbra Lattice protocol"
        assert "direct" in protocols, "Should use direct protocol"
        
        # All engines should connect to Genesis Bus
        engine_count = len(orchestrator.engines)
        genesis_connections = len([
            p for p in orchestrator.communication_paths 
            if p.target == "Genesis_Bus" and p.protocol == "genesis_bus"
        ])
        # All engines except Genesis_Bus should connect to it
        assert genesis_connections >= engine_count - 1


class TestEngineNode:
    """Test EngineNode data structure"""
    
    def test_engine_node_creation(self):
        """Test creating an EngineNode"""
        from bridge_core.lattice.bridge_harmony import EngineNode
        node = EngineNode(
            name="TestEngine",
            path="bridge_backend/engines/test",
            category="utility",
            status="discovered",
            dependencies=["Genesis_Bus"],
            communication_endpoints=["test.health"]
        )
        
        assert node.name == "TestEngine"
        assert node.path == "bridge_backend/engines/test"
        assert node.category == "utility"
        assert node.status == "discovered"
        assert len(node.dependencies) == 1
        assert len(node.communication_endpoints) == 1


class TestCommunicationPath:
    """Test CommunicationPath data structure"""
    
    def test_communication_path_creation(self):
        """Test creating a CommunicationPath"""
        from bridge_core.lattice.bridge_harmony import CommunicationPath
        path = CommunicationPath(
            source="EngineA",
            target="EngineB",
            protocol="genesis_bus",
            status="verified"
        )
        
        assert path.source == "EngineA"
        assert path.target == "EngineB"
        assert path.protocol == "genesis_bus"
        assert path.status == "verified"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
