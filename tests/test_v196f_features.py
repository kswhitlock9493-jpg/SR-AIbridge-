#!/usr/bin/env python3
"""
Test Suite for SR-AIbridge v1.9.6f — Render Bind & Startup Stability Patch
Validates: adaptive port binding, deferred heartbeat, predictive watchdog, self-healing diagnostics
"""
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestV196fPortBinding:
    """Test adaptive port binding features"""
    
    def test_resolve_port_immediate(self):
        """Test immediate PORT resolution"""
        with patch.dict(os.environ, {"PORT": "10000"}):
            from bridge_backend.runtime.ports import resolve_port
            port = resolve_port()
            assert port == 10000
    
    def test_resolve_port_fallback(self):
        """Test fallback to 8000 when PORT not set"""
        with patch.dict(os.environ, {}, clear=True):
            from bridge_backend.runtime.ports import resolve_port
            port = resolve_port()
            assert port == 8000
    
    def test_resolve_port_invalid(self):
        """Test fallback when PORT is invalid"""
        with patch.dict(os.environ, {"PORT": "invalid"}):
            from bridge_backend.runtime.ports import resolve_port
            port = resolve_port()
            assert port == 8000
    
    def test_resolve_port_out_of_range(self):
        """Test fallback when PORT is out of valid range"""
        with patch.dict(os.environ, {"PORT": "99999"}):
            from bridge_backend.runtime.ports import resolve_port
            port = resolve_port()
            assert port == 8000
    
    def test_adaptive_bind_check_exists(self):
        """Test that adaptive_bind_check function exists"""
        from bridge_backend.runtime.ports import adaptive_bind_check
        assert callable(adaptive_bind_check)
    
    def test_check_listen_exists(self):
        """Test that check_listen function exists"""
        from bridge_backend.runtime.ports import check_listen
        assert callable(check_listen)


class TestV196fWatchdog:
    """Test startup watchdog features"""
    
    def test_watchdog_module_exists(self):
        """Test that startup_watchdog module exists"""
        watchdog_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "startup_watchdog.py"
        assert watchdog_path.exists()
    
    def test_watchdog_import(self):
        """Test that StartupWatchdog can be imported"""
        from bridge_backend.runtime.startup_watchdog import StartupWatchdog, watchdog
        assert StartupWatchdog is not None
        assert watchdog is not None
    
    def test_watchdog_mark_port_resolved(self):
        """Test watchdog port resolution tracking"""
        from bridge_backend.runtime.startup_watchdog import StartupWatchdog
        wd = StartupWatchdog()
        wd.mark_port_resolved(10000)
        assert wd.port_resolved_at is not None
    
    def test_watchdog_mark_bind_confirmed(self):
        """Test watchdog bind confirmation tracking"""
        from bridge_backend.runtime.startup_watchdog import StartupWatchdog
        wd = StartupWatchdog()
        wd.mark_bind_confirmed()
        assert wd.bind_confirmed_at is not None
    
    def test_watchdog_mark_heartbeat(self):
        """Test watchdog heartbeat tracking"""
        from bridge_backend.runtime.startup_watchdog import StartupWatchdog
        wd = StartupWatchdog()
        wd.mark_heartbeat_initialized()
        assert wd.heartbeat_initialized_at is not None
    
    def test_watchdog_get_metrics(self):
        """Test watchdog metrics retrieval"""
        from bridge_backend.runtime.startup_watchdog import StartupWatchdog
        wd = StartupWatchdog()
        wd.mark_port_resolved(8000)
        time.sleep(0.1)
        wd.mark_bind_confirmed()
        
        metrics = wd.get_metrics()
        assert "total_startup_time" in metrics
        assert "port_resolution_time" in metrics
        assert "bind_time" in metrics
        assert metrics["port_resolution_time"] is not None


class TestV196fStabilizer:
    """Test predictive stabilizer enhancements"""
    
    def test_stabilizer_module_exists(self):
        """Test that predictive_stabilizer module exists"""
        stabilizer_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "predictive_stabilizer.py"
        assert stabilizer_path.exists()
    
    def test_stabilizer_resolves_startup_tickets(self):
        """Test that stabilizer can resolve startup latency tickets"""
        from bridge_backend.runtime.predictive_stabilizer import _is_resolved
        
        ticket_text = "# Startup Latency Stabilization Ticket\n**Bind Latency:** 8.5s"
        assert _is_resolved(ticket_text) == True
    
    def test_stabilizer_ticket_directory(self):
        """Test that stabilization_tickets directory exists"""
        ticket_dir = Path(__file__).parent.parent / "bridge_backend" / "diagnostics" / "stabilization_tickets"
        assert ticket_dir.exists()


class TestV196fMainIntegration:
    """Test main.py integration"""
    
    def test_version_is_196f(self):
        """Verify version is set to 1.9.6f"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        assert '1.9.6f' in content
    
    def test_startup_imports_watchdog(self):
        """Verify main.py imports startup_watchdog"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        assert "from bridge_backend.runtime.startup_watchdog import watchdog" in content
    
    def test_startup_uses_adaptive_bind(self):
        """Verify main.py uses adaptive_bind_check"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        assert "adaptive_bind_check" in content
    
    def test_startup_defers_heartbeat(self):
        """Verify heartbeat is initialized after bind confirmation"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        
        # Find startup_event function
        startup_idx = content.find("async def startup_event")
        assert startup_idx > 0
        
        # Extract the function
        startup_func = content[startup_idx:startup_idx + 2000]
        
        # Check order: bind confirmation before heartbeat
        bind_idx = startup_func.find("mark_bind_confirmed")
        heartbeat_idx = startup_func.find("heartbeat_loop")
        
        assert bind_idx > 0
        assert heartbeat_idx > 0
        assert bind_idx < heartbeat_idx, "Heartbeat should be initialized after bind confirmation"
    
    def test_stabilizer_logging(self):
        """Verify STABILIZER logging is present"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        assert "[STABILIZER]" in content


class TestV196fHeartbeat:
    """Test heartbeat deferred initialization"""
    
    def test_heartbeat_module_exists(self):
        """Test heartbeat module exists"""
        heartbeat_path = Path(__file__).parent.parent / "bridge_backend" / "runtime" / "heartbeat.py"
        assert heartbeat_path.exists()
    
    def test_heartbeat_has_loop_function(self):
        """Test heartbeat has heartbeat_loop function"""
        from bridge_backend.runtime.heartbeat import heartbeat_loop
        assert callable(heartbeat_loop)


class TestV196fDocumentation:
    """Test documentation updates"""
    
    def test_version_description(self):
        """Test that version description mentions stability patch"""
        main_path = Path(__file__).parent.parent / "bridge_backend" / "main.py"
        content = main_path.read_text()
        assert "Stability" in content or "stability" in content


if __name__ == "__main__":
    # Run tests manually without pytest
    import traceback
    
    test_classes = [
        TestV196fPortBinding,
        TestV196fWatchdog,
        TestV196fStabilizer,
        TestV196fMainIntegration,
        TestV196fHeartbeat,
        TestV196fDocumentation,
    ]
    
    total = 0
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n{'='*60}")
        print(f"Running {test_class.__name__}")
        print('='*60)
        
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total += 1
                try:
                    method = getattr(instance, method_name)
                    method()
                    print(f"✓ {method_name}")
                    passed += 1
                except Exception as e:
                    print(f"✗ {method_name}")
                    print(f"  Error: {e}")
                    traceback.print_exc()
                    failed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print('='*60)
    
    sys.exit(0 if failed == 0 else 1)
