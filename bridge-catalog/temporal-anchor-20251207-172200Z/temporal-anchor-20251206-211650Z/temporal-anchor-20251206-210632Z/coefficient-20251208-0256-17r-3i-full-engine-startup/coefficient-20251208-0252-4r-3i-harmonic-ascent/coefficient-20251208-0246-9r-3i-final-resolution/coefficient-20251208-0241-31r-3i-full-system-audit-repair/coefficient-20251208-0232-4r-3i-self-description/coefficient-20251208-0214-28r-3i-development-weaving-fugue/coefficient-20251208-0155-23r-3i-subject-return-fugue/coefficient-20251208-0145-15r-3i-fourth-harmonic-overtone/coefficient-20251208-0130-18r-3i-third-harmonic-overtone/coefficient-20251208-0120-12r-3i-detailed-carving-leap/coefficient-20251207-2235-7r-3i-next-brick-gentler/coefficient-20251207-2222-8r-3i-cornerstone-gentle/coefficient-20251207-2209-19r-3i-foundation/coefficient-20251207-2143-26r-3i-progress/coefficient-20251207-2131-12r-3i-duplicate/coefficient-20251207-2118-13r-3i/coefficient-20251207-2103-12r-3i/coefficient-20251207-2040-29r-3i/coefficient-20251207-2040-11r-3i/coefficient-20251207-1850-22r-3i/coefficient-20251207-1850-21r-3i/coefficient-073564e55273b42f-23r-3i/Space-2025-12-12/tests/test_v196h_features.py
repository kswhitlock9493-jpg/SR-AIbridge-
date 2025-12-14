#!/usr/bin/env python3
"""
Test Suite for SR-AIbridge v1.9.6h — Port Parity & Deploy Integrity
Validates: PORT binding, deploy parity checks, incident replay, seed bootstrap
"""
import os
import sys
import json
import asyncio
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestV196hPortHandling:
    """Test PORT environment variable handling"""
    
    def test_port_guard_with_port_set(self):
        """Test port_guard correctly logs PORT when set"""
        with patch.dict(os.environ, {"PORT": "10000"}):
            from bridge_backend.runtime.port_guard import describe_port_env
            # Should not raise any exceptions
            describe_port_env()
    
    def test_port_guard_without_port(self):
        """Test port_guard handles missing PORT"""
        with patch.dict(os.environ, {}, clear=True):
            from bridge_backend.runtime.port_guard import describe_port_env
            # Should not raise any exceptions
            describe_port_env()
    
    def test_run_module_requires_port(self):
        """Test that run.py exits when PORT is not set"""
        with patch.dict(os.environ, {}, clear=True):
            from bridge_backend import run
            try:
                run.main()
                assert False, "Should have exited without PORT"
            except SystemExit as e:
                assert e.code == 1
    
    def test_run_module_validates_port(self):
        """Test that run.py validates PORT is an integer"""
        with patch.dict(os.environ, {"PORT": "invalid"}):
            from bridge_backend import run
            try:
                run.main()
                assert False, "Should have exited with invalid PORT"
            except SystemExit as e:
                assert e.code == 1


class TestV196hDeployParity:
    """Test deploy parity engine"""
    
    def test_deploy_parity_check_with_valid_env(self):
        """Test deploy parity check passes with valid environment"""
        async def run_test():
            with patch.dict(os.environ, {
                "PORT": "10000",
                "DATABASE_URL": "sqlite:///test.db",
                "SECRET_KEY": "test-secret"
            }):
                from fastapi import FastAPI
                from bridge_backend.runtime.deploy_parity import deploy_parity_check
                
                app = FastAPI()
                # Add a /health/live route
                @app.get("/health/live")
                def health_live():
                    return {"status": "ok"}
                
                # Should not raise exceptions
                await deploy_parity_check(app)
        
        asyncio.run(run_test())
    
    def test_deploy_parity_creates_ticket_on_issues(self):
        """Test deploy parity creates ticket when issues detected"""
        async def run_test():
            with patch.dict(os.environ, {}, clear=True):
                from fastapi import FastAPI
                from bridge_backend.runtime.deploy_parity import deploy_parity_check
                from pathlib import Path
                
                app = FastAPI()
                
                # Clear existing tickets
                tickets_dir = Path("bridge_backend/diagnostics/stabilization_tickets")
                if tickets_dir.exists():
                    for f in tickets_dir.glob("*_deploy_parity.json"):
                        f.unlink()
                
                await deploy_parity_check(app)
                
                # Check that a ticket was created
                tickets = list(tickets_dir.glob("*_deploy_parity.json"))
                assert len(tickets) > 0, "Should have created a parity ticket"
        
        asyncio.run(run_test())


class TestV196hHealthEndpoints:
    """Test new health endpoints"""
    
    def test_health_live_endpoint_exists(self):
        """Test /health/live endpoint is registered"""
        with patch.dict(os.environ, {
            "PORT": "10000",
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "test"
        }):
            from bridge_backend.main import app
            routes = [r.path for r in app.router.routes if hasattr(r, 'path')]
            assert "/health/live" in routes
    
    def test_diagnostics_deploy_parity_endpoint_exists(self):
        """Test /api/diagnostics/deploy-parity endpoint is registered"""
        with patch.dict(os.environ, {
            "PORT": "10000",
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "test"
        }):
            from bridge_backend.main import app
            routes = [r.path for r in app.router.routes if hasattr(r, 'path')]
            assert "/api/diagnostics/deploy-parity" in routes


class TestV196hIncidentReplay:
    """Test incident replay functionality"""
    
    def test_incident_replay_endpoint_exists(self):
        """Test incident replay endpoint is registered"""
        with patch.dict(os.environ, {
            "PORT": "10000",
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "test"
        }):
            from bridge_backend.main import app
            routes = [r.path for r in app.router.routes if hasattr(r, 'path')]
            # Check for replay endpoint pattern
            has_replay = any("/incidents/replay" in r for r in routes)
            assert has_replay, "Should have incident replay endpoint"


class TestV196hSeedBootstrap:
    """Test seed bootstrap functionality"""
    
    def test_seed_bootstrap_endpoint_exists(self):
        """Test seed bootstrap endpoint is registered"""
        with patch.dict(os.environ, {
            "PORT": "10000",
            "DATABASE_URL": "sqlite:///test.db",
            "SECRET_KEY": "test"
        }):
            from bridge_backend.main import app
            routes = [r.path for r in app.router.routes if hasattr(r, 'path')]
            assert "/api/system/seed/bootstrap" in routes


class TestV196hModelExports:
    """Test model exports from models/__init__.py"""
    
    def test_blueprint_model_export(self):
        """Test Blueprint model can be imported from models package"""
        from bridge_backend.models import Blueprint
        assert Blueprint is not None
        assert hasattr(Blueprint, "__tablename__")
        assert Blueprint.__tablename__ == "blueprints"
    
    def test_agent_job_model_export(self):
        """Test AgentJob model can be imported from models package"""
        from bridge_backend.models import AgentJob
        assert AgentJob is not None
        assert hasattr(AgentJob, "__tablename__")
        assert AgentJob.__tablename__ == "agent_jobs"
    
    def test_mission_model_export(self):
        """Test Mission model can be imported from models package"""
        from bridge_backend.models import Mission
        assert Mission is not None
        assert hasattr(Mission, "__tablename__")
        assert Mission.__tablename__ == "missions"


def run_all_tests():
    """Run all test classes"""
    test_classes = [
        TestV196hPortHandling,
        TestV196hDeployParity,
        TestV196hHealthEndpoints,
        TestV196hIncidentReplay,
        TestV196hSeedBootstrap,
        TestV196hModelExports,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    print("=" * 70)
    print("SR-AIbridge v1.9.6h Test Suite")
    print("=" * 70)
    
    for test_class in test_classes:
        class_name = test_class.__name__
        print(f"\n{class_name}")
        print("-" * 70)
        
        instance = test_class()
        test_methods = [m for m in dir(instance) if m.startswith("test_")]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                method = getattr(instance, method_name)
                method()
                print(f"  ✅ {method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"  ❌ {method_name}: {e}")
                failed_tests.append((class_name, method_name, str(e)))
    
    print("\n" + "=" * 70)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if failed_tests:
        print("\nFailed Tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  ❌ {class_name}.{method_name}: {error}")
        return False
    else:
        print("\n✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
