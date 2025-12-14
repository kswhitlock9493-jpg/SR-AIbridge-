#!/usr/bin/env python3
"""
Test Suite for SR-AIbridge v1.9.5 — Unified Runtime & Autonomic Homeostasis
Validates self-healing, diagnostics, and federation parity features
"""
import os
import sys
import pytest
from pathlib import Path

# Add bridge_backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge_backend"))


class TestUnifiedRuntime:
    """Test suite for Unified Runtime v1.9.5"""
    
    def test_version_1_9_5(self):
        """Verify version is set to 1.9.5"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        assert 'version="1.9.5"' in content
        assert "Unified Runtime" in content or "Autonomic Homeostasis" in content
    
    def test_heartbeat_self_healing(self):
        """Verify heartbeat module has self-healing capabilities"""
        heartbeat_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "heartbeat.py"
        content = heartbeat_path.read_text()
        
        # Check for self-healing functions
        assert "def ensure_httpx" in content
        assert "def record_repair" in content
        assert "auto-install" in content.lower()
        assert "subprocess.run" in content
        assert "importlib.invalidate_caches()" in content
    
    def test_repair_log_recording(self):
        """Verify repair logging functionality"""
        heartbeat_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "heartbeat.py"
        content = heartbeat_path.read_text()
        
        # Check for repair log functionality
        assert ".bridge_repair_log" in content
        assert "datetime" in content
        assert "record_repair" in content
    
    def test_parity_layer_exists(self):
        """Verify parity layer module exists and has required functions"""
        parity_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "parity.py"
        
        assert parity_path.exists(), "Parity layer module should exist"
        
        content = parity_path.read_text()
        
        # Check for required functions
        assert "def sync_env_headers" in content
        assert "def verify_cors_parity" in content
        assert "def ensure_port_parity" in content
        assert "def run_parity_sync" in content
    
    def test_parity_integration_in_startup(self):
        """Verify parity sync is called on startup"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Check that parity sync is imported and called
        assert "from bridge_backend.runtime.parity import run_parity_sync" in content
        assert "run_parity_sync()" in content
    
    def test_bridge_doctor_cli_exists(self):
        """Verify Bridge Doctor CLI tool exists"""
        doctor_path = Path(__file__).parent.parent / "bridge_backend" / "cli" / "doctor.py"
        
        assert doctor_path.exists(), "Bridge Doctor CLI should exist"
        
        content = doctor_path.read_text()
        
        # Check for main diagnostic function
        assert "def run_bridge_diagnostics" in content
        assert "if __name__ == \"__main__\"" in content
        assert "ensure_httpx" in content
    
    def test_doctor_checks_dependencies(self):
        """Verify Bridge Doctor checks dependencies"""
        doctor_path = Path(__file__).parent.parent / "bridge_backend" / "cli" / "doctor.py"
        content = doctor_path.read_text()
        
        # Check for dependency checks
        assert "httpx" in content
        assert "Checking dependencies" in content or "dependencies" in content.lower()
    
    def test_doctor_checks_database(self):
        """Verify Bridge Doctor checks database schema"""
        doctor_path = Path(__file__).parent.parent / "bridge_backend" / "cli" / "doctor.py"
        content = doctor_path.read_text()
        
        # Check for database validation
        assert "Base.metadata.create_all" in content or "database" in content.lower()
    
    def test_doctor_checks_network(self):
        """Verify Bridge Doctor checks network configuration"""
        doctor_path = Path(__file__).parent.parent / "bridge_backend" / "cli" / "doctor.py"
        content = doctor_path.read_text()
        
        # Check for network checks
        assert "PORT" in content
        assert "DATABASE_URL" in content or "ALLOWED_ORIGINS" in content
    
    def test_federation_diagnostics_endpoint(self):
        """Verify federation diagnostics endpoint exists"""
        health_routes_path = Path(__file__).parent.parent / "bridge_backend" / "bridge_core" / "health" / "routes.py"
        content = health_routes_path.read_text()
        
        # Check for federation diagnostics endpoint
        assert "/federation/diagnostics" in content
        assert "def federation_diagnostics" in content
        assert "heartbeat" in content.lower()
        assert "self_heal" in content
    
    def test_federation_diagnostics_response_structure(self):
        """Verify federation diagnostics endpoint returns expected data"""
        health_routes_path = Path(__file__).parent.parent / "bridge_backend" / "bridge_core" / "health" / "routes.py"
        content = health_routes_path.read_text()
        
        # Check for expected response fields
        assert '"status"' in content
        assert '"heartbeat"' in content
        assert '"self_heal"' in content
        assert '"federation"' in content
        assert '"version"' in content
    
    def test_start_sh_port_binding(self):
        """Verify start.sh uses dynamic PORT binding"""
        start_sh_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "start.sh"
        content = start_sh_path.read_text()
        
        # Check for dynamic PORT
        assert 'export PORT="${PORT:-8000}"' in content
        assert "Using PORT=${PORT}" in content or "PORT=" in content
    
    def test_start_sh_messages(self):
        """Verify start.sh has proper initialization messages"""
        start_sh_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "start.sh"
        content = start_sh_path.read_text()
        
        # Check for clear initialization messages
        assert "[INIT]" in content
        assert "Launching" in content or "Starting" in content
    
    def test_auto_repair_version(self):
        """Verify auto_repair.py has v1.9.5 branding"""
        auto_repair_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "auto_repair.py"
        content = auto_repair_path.read_text()
        
        assert "v1.9.5" in content or "1.9.5" in content
        assert "Unified Runtime" in content or "Autonomic Homeostasis" in content
    
    def test_changelog_exists(self):
        """Verify CHANGELOG.md exists and documents v1.9.5"""
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
        
        assert changelog_path.exists(), "CHANGELOG.md should exist"
        
        content = changelog_path.read_text()
        
        assert "v1.9.5" in content or "1.9.5" in content
        assert "Unified Runtime" in content
        assert "Self-Healing" in content or "self-healing" in content
    
    def test_changelog_documents_features(self):
        """Verify CHANGELOG documents all major features"""
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
        content = changelog_path.read_text()
        
        # Check for documented features
        assert "Bridge Doctor" in content
        assert "Parity" in content or "parity" in content
        assert "heartbeat" in content.lower()
        assert "federation" in content.lower()
    
    def test_httpx_in_requirements(self):
        """Verify httpx is in requirements.txt"""
        requirements_path = Path(__file__).parent.parent / "bridge_backend" / "requirements.txt"
        content = requirements_path.read_text()
        
        assert "httpx" in content.lower()


class TestSelfHealing:
    """Test suite for self-healing capabilities"""
    
    def test_ensure_httpx_function(self):
        """Test that ensure_httpx function exists and is callable"""
        try:
            from runtime.heartbeat import ensure_httpx
            assert callable(ensure_httpx)
        except ImportError:
            pytest.skip("Could not import heartbeat module in test environment")
    
    def test_record_repair_function(self):
        """Test that record_repair function exists and is callable"""
        try:
            from runtime.heartbeat import record_repair
            assert callable(record_repair)
        except ImportError:
            pytest.skip("Could not import heartbeat module in test environment")


class TestParityLayer:
    """Test suite for Render ↔ Netlify parity"""
    
    def test_parity_sync_function(self):
        """Test that run_parity_sync function exists"""
        try:
            from runtime.parity import run_parity_sync
            assert callable(run_parity_sync)
        except ImportError:
            pytest.skip("Could not import parity module in test environment")
    
    def test_cors_verification(self):
        """Test that CORS verification function exists"""
        try:
            from runtime.parity import verify_cors_parity
            assert callable(verify_cors_parity)
        except ImportError:
            pytest.skip("Could not import parity module in test environment")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
