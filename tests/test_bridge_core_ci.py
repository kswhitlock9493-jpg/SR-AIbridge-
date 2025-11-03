#!/usr/bin/env python3
"""
Tests for Bridge Core CI/CD Modules (v1.9.7s)
Tests the modules used by bridge_federation_build.yml workflow
"""
import pytest
import sys
import os
from pathlib import Path

# Add bridge_core to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSelfHealGuard:
    """Test self_heal.guard module"""

    def test_guard_import(self):
        """Test that guard module can be imported"""
        from bridge_core.self_heal import guard
        assert guard is not None

    def test_check_core_validation(self):
        """Test core validation function"""
        from bridge_core.self_heal.guard import check_core_validation
        result = check_core_validation()
        assert result == 0, "Core validation should pass"


class TestLatticeHeartbeat:
    """Test lattice.heartbeat module"""

    def test_heartbeat_import(self):
        """Test that heartbeat module can be imported"""
        from bridge_core.lattice import heartbeat
        assert heartbeat is not None

    def test_run_federation_heartbeat(self):
        """Test federation heartbeat function"""
        from bridge_core.lattice.heartbeat import run_federation_heartbeat
        result = run_federation_heartbeat(mode="federation", timeout=5)
        assert result == 0, "Federation heartbeat should succeed"


class TestLatticePathcheck:
    """Test lattice.pathcheck module"""

    def test_pathcheck_import(self):
        """Test that pathcheck module can be imported"""
        from bridge_core.lattice import pathcheck
        assert pathcheck is not None

    def test_verify_deployment_paths(self):
        """Test deployment path verification"""
        from bridge_core.lattice.pathcheck import verify_deployment_paths
        result = verify_deployment_paths()
        assert result == 0, "Deployment path verification should pass"


class TestSecurityValidateToken:
    """Test security.validate_token module"""

    def test_validate_token_import(self):
        """Test that validate_token module can be imported"""
        from bridge_core.security import validate_token
        assert validate_token is not None

    def test_validate_dominion_token_success(self):
        """Test token validation with valid token"""
        from bridge_core.security.validate_token import validate_dominion_token
        result = validate_dominion_token("valid_token_12345")
        assert result == 0, "Valid token should pass validation"

    def test_validate_dominion_token_failure(self):
        """Test token validation with invalid token"""
        from bridge_core.security.validate_token import validate_dominion_token
        result = validate_dominion_token("")
        assert result == 1, "Empty token should fail validation"

        result = validate_dominion_token("short")
        assert result == 1, "Short token should fail validation"


class TestModuleStructure:
    """Test overall module structure"""

    def test_bridge_core_package(self):
        """Test that bridge_core is a valid package"""
        import bridge_core
        assert hasattr(bridge_core, '__version__')
        assert bridge_core.__version__ == "1.9.7s"

    def test_all_modules_importable(self):
        """Test that all core modules can be imported"""
        from bridge_core.self_heal import guard
        from bridge_core.lattice import heartbeat, pathcheck
        from bridge_core.security import validate_token

        assert guard is not None
        assert heartbeat is not None
        assert pathcheck is not None
        assert validate_token is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
