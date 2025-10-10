#!/usr/bin/env python3
"""
Test Suite for SR-AIbridge v1.9.4 — Anchorhold Protocol
Validates all core improvements and infrastructure updates
"""
import os
import sys
import pytest
from pathlib import Path

# Add bridge_backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge_backend"))


class TestAnchorholdProtocol:
    """Test suite for Anchorhold Protocol v1.9.4"""
    
    def test_version_1_9_4(self):
        """Verify version is set to 1.9.4"""
        # Check source code directly to avoid database initialization
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        assert 'version="1.9.4"' in content
        assert "Anchorhold" in content
    
    def test_dynamic_port_binding(self):
        """Verify dynamic port binding implementation"""
        # Test that main.py has the correct port binding code
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Check for dynamic port binding
        assert 'port = int(os.environ.get("PORT", 8000))' in content
        assert 'uvicorn.run("bridge_backend.main:app", host="0.0.0.0", port=port)' in content
    
    def test_schema_sync_on_startup(self):
        """Verify automatic schema sync on startup"""
        # Check source code directly to avoid database initialization
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Verify startup_event exists and has schema sync
        assert "async def startup_event()" in content
        assert "Base.metadata.create_all" in content
        assert "Database schema synchronized successfully" in content
    
    def test_heartbeat_module_exists(self):
        """Verify heartbeat module exists and has required functions"""
        try:
            from runtime.heartbeat import start_heartbeat, bridge_heartbeat
            import inspect
            
            # Verify both functions are async
            assert inspect.iscoroutinefunction(start_heartbeat)
            assert inspect.iscoroutinefunction(bridge_heartbeat)
            
        except ImportError:
            pytest.fail("Heartbeat module not found")
    
    def test_heartbeat_interval(self):
        """Verify heartbeat interval is set to 300 seconds (5 minutes)"""
        from runtime.heartbeat import HEARTBEAT_INTERVAL
        assert HEARTBEAT_INTERVAL == 300
    
    def test_cors_configuration(self):
        """Verify CORS configuration with ALLOWED_ORIGINS"""
        # Check source code directly to avoid database initialization
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Should have CORS_ALLOW_ORIGINS from environment
        assert 'CORS_ALLOW_ORIGINS = os.getenv' in content
        assert 'ALLOWED_ORIGINS' in content
        
        # Should contain required origins in default
        assert "https://sr-aibridge.netlify.app" in content
        assert "https://sr-aibridge.onrender.com" in content
    
    def test_httpx_dependency(self):
        """Verify httpx is in requirements.txt"""
        req_path = Path(__file__).parent.parent / "bridge_backend" / "requirements.txt"
        content = req_path.read_text()
        
        assert "httpx" in content
        # Verify version requirement
        httpx_lines = [line for line in content.split('\n') if 'httpx' in line.lower()]
        assert len(httpx_lines) > 0
        assert any(">=0.24.0" in line for line in httpx_lines)
    
    def test_auto_repair_branding(self):
        """Verify auto_repair.py has Anchorhold Protocol branding"""
        auto_repair_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "auto_repair.py"
        content = auto_repair_path.read_text()
        
        assert "SR-AIbridge v1.9.4" in content
        assert "Anchorhold Protocol" in content
        assert "Auto-Repair + Schema Sync + Heartbeat Init" in content
    
    def test_cors_validation_in_auto_repair(self):
        """Verify CORS validation in auto_repair.py"""
        auto_repair_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "auto_repair.py"
        content = auto_repair_path.read_text()
        
        assert "ALLOWED_ORIGINS" in content
        assert "CORS" in content


class TestInfrastructureConfiguration:
    """Test infrastructure configuration files"""
    
    def test_render_yaml_port_config(self):
        """Verify render.yaml has PORT sync: false"""
        render_path = Path(__file__).parent.parent / "render.yaml"
        content = render_path.read_text()
        
        # Check for PORT configuration
        assert "PORT" in content
        assert "sync: false" in content
    
    def test_render_yaml_allowed_origins(self):
        """Verify render.yaml has expanded ALLOWED_ORIGINS"""
        render_path = Path(__file__).parent.parent / "render.yaml"
        content = render_path.read_text()
        
        assert "ALLOWED_ORIGINS" in content
        # Should have multiple origins
        assert "sr-aibridge.netlify.app" in content or "bridge.netlify.app" in content
    
    def test_render_yaml_direct_python_execution(self):
        """Verify render.yaml uses direct Python execution"""
        render_path = Path(__file__).parent.parent / "render.yaml"
        content = render_path.read_text()
        
        # Check for direct Python module execution
        assert "python -m bridge_backend.main" in content
    
    def test_netlify_toml_api_proxy(self):
        """Verify netlify.toml has API proxy configuration"""
        netlify_path = Path(__file__).parent.parent / "netlify.toml"
        content = netlify_path.read_text()
        
        # Check for API proxy redirects
        assert "/api/*" in content
        assert "https://sr-aibridge.onrender.com" in content
        assert "status = 200" in content
    
    def test_netlify_toml_build_environment(self):
        """Verify netlify.toml has federation environment variables"""
        netlify_path = Path(__file__).parent.parent / "netlify.toml"
        content = netlify_path.read_text()
        
        assert "VITE_BRIDGE_BASE" in content
        assert "VITE_PUBLIC_API_BASE" in content
    
    def test_netlify_toml_spa_fallback(self):
        """Verify netlify.toml has SPA fallback with correct precedence"""
        netlify_path = Path(__file__).parent.parent / "netlify.toml"
        content = netlify_path.read_text()
        
        # Check for SPA fallback
        assert "to = \"/index.html\"" in content or "to   = \"/index.html\"" in content
        # force = false means API proxy takes priority
        assert "force  = false" in content or "force = false" in content


class TestDocumentation:
    """Test documentation completeness"""
    
    def test_anchorhold_protocol_doc_exists(self):
        """Verify ANCHORHOLD_PROTOCOL.md exists"""
        doc_path = Path(__file__).parent.parent / "docs" / "ANCHORHOLD_PROTOCOL.md"
        assert doc_path.exists()
    
    def test_anchorhold_quick_ref_exists(self):
        """Verify ANCHORHOLD_QUICK_REF.md exists"""
        doc_path = Path(__file__).parent.parent / "docs" / "ANCHORHOLD_QUICK_REF.md"
        assert doc_path.exists()
    
    def test_protocol_doc_completeness(self):
        """Verify ANCHORHOLD_PROTOCOL.md has all sections"""
        doc_path = Path(__file__).parent.parent / "docs" / "ANCHORHOLD_PROTOCOL.md"
        content = doc_path.read_text()
        
        required_sections = [
            "Dynamic Port Binding",
            "Automatic Table Creation",
            "Heartbeat Ping System",
            "Netlify ↔ Render Header Alignment",
            "Extended Runtime Guard",
            "render.yaml",
            "netlify.toml"
        ]
        
        for section in required_sections:
            assert section in content, f"Missing section: {section}"


class TestEndpoints:
    """Test API endpoint responses"""
    
    def test_root_endpoint_protocol(self):
        """Verify root endpoint returns Anchorhold protocol"""
        # Check source code directly to avoid database initialization
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Check root endpoint definition
        assert 'return {"status": "active", "version": "1.9.4", "environment": "production", "protocol": "Anchorhold"}' in content
    
    def test_version_endpoint_protocol(self):
        """Verify /api/version endpoint includes protocol info"""
        # Check source code directly to avoid database initialization
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Check version endpoint includes protocol
        assert '"protocol": "Anchorhold"' in content
        assert '"service": "SR-AIbridge Backend"' in content


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
