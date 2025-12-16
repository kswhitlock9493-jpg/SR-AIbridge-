"""
Test suite for v1.9.6c features:
- Port resolution and binding
- Health endpoints (/health/ports, /health/runtime)
- Blueprint engine gating (BLUEPRINTS_ENABLED)
- Import-safe blueprint routes
"""
import pytest
import os
from pathlib import Path


class TestPortResolution:
    """Test dynamic port resolution"""
    
    def test_ports_module_exists(self):
        """Verify runtime/ports.py module exists"""
        ports_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "ports.py"
        assert ports_path.exists(), "runtime/ports.py should exist"
    
    def test_resolve_port_function(self):
        """Verify resolve_port function works correctly"""
        from bridge_backend.runtime.ports import resolve_port
        
        # Test with no PORT env var
        old_port = os.environ.get("PORT")
        if "PORT" in os.environ:
            del os.environ["PORT"]
        
        assert resolve_port() == 8000, "Should default to 8000 when PORT not set"
        
        # Test with valid PORT
        os.environ["PORT"] = "10000"
        assert resolve_port() == 10000, "Should use PORT when valid"
        
        # Test with invalid PORT
        os.environ["PORT"] = "not_a_number"
        assert resolve_port() == 8000, "Should fallback to 8000 on invalid PORT"
        
        # Test with out-of-range PORT
        os.environ["PORT"] = "99999"
        assert resolve_port() == 8000, "Should fallback to 8000 on out-of-range PORT"
        
        # Restore
        if old_port:
            os.environ["PORT"] = old_port
        elif "PORT" in os.environ:
            del os.environ["PORT"]
    
    def test_check_listen_function(self):
        """Verify check_listen function exists and returns tuple"""
        from bridge_backend.runtime.ports import check_listen
        
        occupied, note = check_listen("127.0.0.1", 8000)
        assert isinstance(occupied, bool), "First element should be bool"
        assert isinstance(note, str), "Second element should be string"


class TestHealthEndpoints:
    """Test new health check endpoints"""
    
    def test_health_routes_module_exists(self):
        """Verify routes/health.py module exists"""
        health_path = Path(__file__).parent.parent / "bridge_backend" / "routes" / "health.py"
        assert health_path.exists(), "routes/health.py should exist"
    
    def test_health_router_created(self):
        """Verify health router is created with correct prefix"""
        from bridge_backend.routes.health import router
        assert router.prefix == "/health", "Router should have /health prefix"
        assert "health" in router.tags, "Router should have 'health' tag"
    
    def test_health_ports_endpoint_exists(self):
        """Verify /health/ports endpoint exists"""
        from bridge_backend.routes.health import router
        
        # Check that the route exists
        route_paths = [route.path for route in router.routes]
        assert "/ports" in route_paths or "/health/ports" in [r.path for r in router.routes], \
            "Should have /ports endpoint"
    
    def test_health_runtime_endpoint_exists(self):
        """Verify /health/runtime endpoint exists"""
        from bridge_backend.routes.health import router
        
        # Check that the route exists
        route_paths = [route.path for route in router.routes]
        assert "/runtime" in route_paths or "/health/runtime" in [r.path for r in router.routes], \
            "Should have /runtime endpoint"


class TestMainAppIntegration:
    """Test main.py integrations"""
    
    def test_main_uses_resolve_port(self):
        """Verify main.py imports and uses resolve_port"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        assert "from bridge_backend.runtime.ports import resolve_port" in content, \
            "main.py should import resolve_port"
        assert "resolve_port()" in content, \
            "main.py should call resolve_port()"
    
    def test_main_includes_health_router(self):
        """Verify main.py includes health router"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        assert 'bridge_backend.routes.health' in content, \
            "main.py should reference health routes"
    
    def test_app_version_updated(self):
        """Verify app version is updated to v1.9.6c"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        assert "v1.9.6c" in content, \
            "App version should be v1.9.6c"


class TestBlueprintEngineGating:
    """Test blueprint engine gating with BLUEPRINTS_ENABLED flag"""
    
    def test_blueprints_disabled_by_default(self):
        """Verify blueprints are disabled by default"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        assert 'BLUEPRINTS_ENABLED' in content, \
            "main.py should check BLUEPRINTS_ENABLED flag"
        assert 'Disabled by default' in content or 'disabled by default' in content, \
            "Should log that blueprints are disabled by default"
    
    def test_blueprint_routes_import_safe(self):
        """Verify blueprint routes can be imported without crashing"""
        # This should not raise an ImportError even if models are missing
        try:
            from bridge_backend.bridge_core.engines.blueprint.routes import router
            assert router.prefix == "/blueprint", "Blueprint router should have /blueprint prefix"
        except ImportError as e:
            # If it fails, it should be due to missing dependencies, not import-time crashes
            assert "blueprint_engine" in str(e).lower() or "models" in str(e).lower(), \
                f"Import error should be about dependencies, not structure: {e}"
    
    def test_blueprint_status_endpoint(self):
        """Verify blueprint status endpoint exists"""
        try:
            from bridge_backend.bridge_core.engines.blueprint.routes import router
            
            # Check that status endpoint exists
            route_paths = [route.path for route in router.routes]
            assert "/status" in route_paths or "/blueprint/status" in [r.path for r in router.routes], \
                "Blueprint router should have /status endpoint"
        except ImportError:
            pytest.skip("Blueprint routes not importable in this environment")


class TestRenderYamlConfiguration:
    """Test render.yaml configuration"""
    
    def test_render_yaml_port_fallback(self):
        """Verify render.yaml uses ${PORT:-8000} fallback"""
        render_path = Path(__file__).parent.parent / "render.yaml"
        content = render_path.read_text()
        
        assert "${PORT:-8000}" in content or "${PORT:-10000}" in content, \
            "render.yaml should use PORT with fallback"


class TestDiagnosticsStructure:
    """Test diagnostics directory structure"""
    
    def test_diagnostics_directory_exists(self):
        """Verify diagnostics directory exists"""
        diagnostics_path = Path(__file__).parent.parent / "bridge_backend" / "diagnostics"
        assert diagnostics_path.exists(), "diagnostics directory should exist"
    
    def test_stabilization_tickets_directory_exists(self):
        """Verify stabilization_tickets subdirectory exists"""
        tickets_path = Path(__file__).parent.parent / "bridge_backend" / "diagnostics" / "stabilization_tickets"
        assert tickets_path.exists(), "stabilization_tickets directory should exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
