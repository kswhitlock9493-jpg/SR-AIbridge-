"""
Integration tests for Forge v1.9.7f - Cascade Synchrony
Tests the core Forge integration and synchrony healing protocol
"""

import os
import pytest
from pathlib import Path


class TestForgeCore:
    """Tests for forge_core.py"""
    
    def test_forge_imports(self):
        """Test that forge module imports successfully"""
        from bridge_backend.forge import forge_integrate_engines, get_forge_status
        assert forge_integrate_engines is not None
        assert get_forge_status is not None
    
    def test_get_forge_status_default(self):
        """Test forge status with default settings"""
        from bridge_backend.forge import get_forge_status
        
        status = get_forge_status()
        
        assert "forge_mode" in status
        assert "forge_self_heal" in status
        assert "cascade_sync" in status
        assert "arie_propagation" in status
        assert "umbra_memory_sync" in status
        assert "truth_certification" in status
        assert "registry_exists" in status
    
    def test_load_forge_registry(self):
        """Test loading the bridge_forge.json registry"""
        from bridge_backend.forge.forge_core import load_forge_registry
        
        registry = load_forge_registry()
        
        # Registry should exist and have entries
        assert isinstance(registry, dict)
        assert len(registry) > 0
        
        # Check for some expected engines
        expected_engines = ["cascade", "arie", "truth", "umbra"]
        for engine in expected_engines:
            assert engine in registry or "umbrella" in registry  # umbrella is the correct name for umbra
    
    def test_discover_engine_paths(self):
        """Test engine path discovery"""
        from bridge_backend.forge.forge_core import discover_engine_paths
        
        discovered = discover_engine_paths()
        
        assert isinstance(discovered, dict)
        # Should discover at least some engines
        assert len(discovered) > 0
    
    def test_forge_integrate_disabled(self):
        """Test forge integration when disabled"""
        from bridge_backend.forge import forge_integrate_engines
        
        # Ensure FORGE_MODE is not enabled
        old_val = os.environ.get("FORGE_MODE")
        os.environ["FORGE_MODE"] = "disabled"
        
        try:
            result = forge_integrate_engines()
            
            assert result["forge_mode"] == "disabled"
            assert result["engines_integrated"] == []
            assert "message" in result
        finally:
            if old_val:
                os.environ["FORGE_MODE"] = old_val
            else:
                os.environ.pop("FORGE_MODE", None)
    
    def test_forge_integrate_enabled(self):
        """Test forge integration when enabled"""
        from bridge_backend.forge import forge_integrate_engines
        
        # Enable FORGE_MODE for this test
        old_val = os.environ.get("FORGE_MODE")
        os.environ["FORGE_MODE"] = "enabled"
        
        try:
            result = forge_integrate_engines()
            
            assert result["forge_mode"] == "enabled"
            assert "engines_discovered" in result
            assert "engines_integrated" in result
            assert "engines_failed" in result
            assert "integration_count" in result
            assert "failure_count" in result
            
            # Should discover some engines
            assert result["engines_discovered"] > 0
        finally:
            if old_val:
                os.environ["FORGE_MODE"] = old_val
            else:
                os.environ.pop("FORGE_MODE", None)


class TestSynchrony:
    """Tests for synchrony.py"""
    
    def test_synchrony_imports(self):
        """Test that synchrony module imports successfully"""
        from bridge_backend.forge.synchrony import get_synchrony_status, synchrony
        assert get_synchrony_status is not None
        assert synchrony is not None
    
    def test_get_synchrony_status(self):
        """Test synchrony status"""
        from bridge_backend.forge.synchrony import get_synchrony_status
        
        status = get_synchrony_status()
        
        assert "enabled" in status
        assert "arie_propagation" in status
        assert "umbra_memory_sync" in status
        assert "cascade_sync" in status
        assert "protocol" in status
        assert "version" in status
        assert status["protocol"] == "cascade_synchrony"
        assert status["version"] == "v1.9.7f"
    
    def test_synchrony_disabled_by_default(self):
        """Test that synchrony is disabled by default"""
        from bridge_backend.forge.synchrony import CascadeSynchrony
        
        sync = CascadeSynchrony()
        
        assert sync.enabled == False
        assert sync.arie_propagation == False
        assert sync.umbra_memory_sync == False
    
    def test_synchrony_detect_error_disabled(self):
        """Test error detection when synchrony is disabled"""
        from bridge_backend.forge.synchrony import CascadeSynchrony
        
        sync = CascadeSynchrony()
        
        error = {"message": "Test error", "subsystem": "test"}
        event_id = sync.detect_error("test_subsystem", error)
        
        # Should return None when disabled
        assert event_id is None
    
    def test_synchrony_detect_error_enabled(self):
        """Test error detection when synchrony is enabled"""
        from bridge_backend.forge.synchrony import CascadeSynchrony
        
        # Enable CASCADE_SYNC
        old_val = os.environ.get("CASCADE_SYNC")
        os.environ["CASCADE_SYNC"] = "true"
        
        try:
            sync = CascadeSynchrony()
            
            error = {"message": "Test error"}
            event_id = sync.detect_error("test_subsystem", error)
            
            # Should return an event ID when enabled
            assert event_id is not None
            assert "heal_test_subsystem" in event_id
        finally:
            if old_val:
                os.environ["CASCADE_SYNC"] = old_val
            else:
                os.environ.pop("CASCADE_SYNC", None)
    
    def test_auto_recovery_disabled(self):
        """Test auto-recovery when disabled"""
        from bridge_backend.forge.synchrony import CascadeSynchrony
        
        sync = CascadeSynchrony()
        
        error = {"message": "Test error"}
        result = sync.auto_recover("render", error)
        
        # Should return False when disabled
        assert result == False
    
    def test_auto_recovery_platforms(self):
        """Test auto-recovery for different platforms"""
        from bridge_backend.forge.synchrony import CascadeSynchrony
        
        # Enable CASCADE_SYNC
        old_val = os.environ.get("CASCADE_SYNC")
        os.environ["CASCADE_SYNC"] = "true"
        
        try:
            sync = CascadeSynchrony()
            
            platforms = ["render", "netlify", "github", "bridge"]
            error = {"message": "Test error"}
            
            for platform in platforms:
                result = sync.auto_recover(platform, error)
                # Should return True for recognized platforms
                assert result == True
        finally:
            if old_val:
                os.environ["CASCADE_SYNC"] = old_val
            else:
                os.environ.pop("CASCADE_SYNC", None)


class TestForgeRegistry:
    """Tests for .github/bridge_forge.json"""
    
    def test_registry_file_exists(self):
        """Test that the registry file exists"""
        registry_path = Path(".github/bridge_forge.json")
        assert registry_path.exists()
    
    def test_registry_is_valid_json(self):
        """Test that the registry is valid JSON"""
        import json
        
        registry_path = Path(".github/bridge_forge.json")
        
        with open(registry_path, "r") as f:
            registry = json.load(f)
        
        assert isinstance(registry, dict)
        assert len(registry) > 0
    
    def test_registry_paths_format(self):
        """Test that registry paths are properly formatted"""
        import json
        
        registry_path = Path(".github/bridge_forge.json")
        
        with open(registry_path, "r") as f:
            registry = json.load(f)
        
        for engine_name, path in registry.items():
            # Paths should start with bridge_backend
            assert path.startswith("bridge_backend/")
            # Paths should end with .py or __init__.py
            assert path.endswith(".py")


class TestForgeTopology:
    """Tests for .github/forge_topology.json"""
    
    def test_topology_file_exists(self):
        """Test that the topology file exists"""
        topology_path = Path(".github/forge_topology.json")
        assert topology_path.exists()
    
    def test_topology_is_valid_json(self):
        """Test that the topology is valid JSON"""
        import json
        
        topology_path = Path(".github/forge_topology.json")
        
        with open(topology_path, "r") as f:
            topology = json.load(f)
        
        assert isinstance(topology, dict)
        assert "forge_topology" in topology
    
    def test_topology_structure(self):
        """Test that the topology has the expected structure"""
        import json
        
        topology_path = Path(".github/forge_topology.json")
        
        with open(topology_path, "r") as f:
            data = json.load(f)
        
        topology = data["forge_topology"]
        
        # Check required fields
        assert "version" in topology
        assert topology["version"] == "v1.9.7f"
        assert "healing_protocol" in topology
        assert topology["healing_protocol"] == "cascade_synchrony"
        
        # Check clusters
        assert "clusters" in topology
        clusters = topology["clusters"]
        assert "core_engines" in clusters
        assert "healing_engines" in clusters
        assert "forge_engines" in clusters
        assert "utility_engines" in clusters
        
        # Check integration matrix
        assert "integration_matrix" in topology
        matrix = topology["integration_matrix"]
        assert "render" in matrix
        assert "netlify" in matrix
        assert "github" in matrix
        assert "bridge" in matrix
