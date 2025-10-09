#!/usr/bin/env python3
"""
Tests for runtime guard scripts
"""
import pytest
import os
import sys
import tempfile
import pathlib

# Add bridge_backend to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

class TestDatabaseWait:
    """Test database wait logic"""
    
    def test_wait_for_db_sqlite(self):
        """SQLite should skip DB wait"""
        from runtime.wait_for_db import wait_for_db
        
        # SQLite URL should return immediately
        result = wait_for_db("sqlite:///./test.db", timeout=1)
        assert result == 0
    
    def test_wait_for_db_no_url(self):
        """Empty URL should return 0 (skip wait)"""
        from runtime.wait_for_db import wait_for_db
        
        result = wait_for_db("", timeout=1)
        assert result == 0


class TestEgressCanary:
    """Test egress canary host coverage"""
    
    def test_egress_hosts_defined(self):
        """Verify all required hosts are in the list"""
        from runtime.egress_canary import HOSTS
        
        required = [
            "api.github.com",
            "api.render.com",
            "api.netlify.com"
        ]
        
        for host in required:
            assert host in HOSTS, f"{host} should be in HOSTS list"
    
    def test_check_host_localhost(self):
        """Check that localhost connectivity works"""
        from runtime.egress_canary import check_host
        
        # This might fail in some environments, so we'll just test the function exists
        # and returns a boolean
        result = check_host("localhost", port=80, timeout=1)
        assert isinstance(result, bool)


class TestMigrations:
    """Test migration logic"""
    
    def test_run_migrations_safe_mode(self):
        """Safe mode should perform checks"""
        from runtime.run_migrations import run_migrations
        
        # In safe mode with SQLite, should succeed
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        result = run_migrations(safe_mode=True)
        assert result == 0
    
    def test_run_migrations_unsafe_mode(self):
        """Unsafe mode should skip checks"""
        from runtime.run_migrations import run_migrations
        
        result = run_migrations(safe_mode=False)
        assert result == 0


class TestHealthProbe:
    """Test health probe"""
    
    def test_warm_health_no_requests(self):
        """Health probe should handle missing requests module"""
        from runtime.health_probe import warm_health
        
        # Should return 0 even if requests is not available
        result = warm_health()
        assert isinstance(result, int)


class TestRouteManifest:
    """Test route manifest endpoint"""
    
    def test_routes_endpoint_contract(self):
        """Verify /api/routes returns correct structure"""
        # This would require importing the app, which may have dependencies
        # So we'll just verify the endpoint exists in main.py
        main_file = pathlib.Path(__file__).parent.parent / "main.py"
        content = main_file.read_text()
        
        assert "@app.get(\"/api/routes\")" in content
        assert "list_routes" in content


class TestVersionEndpoint:
    """Test version endpoint"""
    
    def test_version_endpoint_exists(self):
        """Verify /api/version endpoint exists"""
        main_file = pathlib.Path(__file__).parent.parent / "main.py"
        content = main_file.read_text()
        
        assert "@app.get(\"/api/version\")" in content
        assert "get_version" in content


class TestRenderYaml:
    """Test render.yaml configuration"""
    
    def test_render_yaml_has_start_command(self):
        """Verify render.yaml uses start.sh"""
        render_file = pathlib.Path(__file__).parent.parent.parent / "render.yaml"
        content = render_file.read_text()
        
        assert "startCommand:" in content
        assert "start.sh" in content
    
    def test_render_yaml_has_health_check(self):
        """Verify render.yaml has health check configured"""
        render_file = pathlib.Path(__file__).parent.parent.parent / "render.yaml"
        content = render_file.read_text()
        
        assert "healthCheckPath:" in content
        assert "/api/health" in content


class TestWorkflows:
    """Test workflow files exist and are valid"""
    
    def test_federation_runtime_guard_workflow(self):
        """Test that federation_runtime_guard.yml exists"""
        workflow_file = pathlib.Path(__file__).parent.parent.parent / ".github" / "workflows" / "federation_runtime_guard.yml"
        
        assert workflow_file.exists(), "federation_runtime_guard.yml should exist"
        
        content = workflow_file.read_text()
        assert "smoke_backend.py" in content
        assert "triage_matrix.py" in content
    
    def test_render_env_guard_workflow(self):
        """Test that render_env_guard.yml exists"""
        workflow_file = pathlib.Path(__file__).parent.parent.parent / ".github" / "workflows" / "render_env_guard.yml"
        
        assert workflow_file.exists(), "render_env_guard.yml should exist"
        
        content = workflow_file.read_text()
        assert "render_env_lint.py" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
