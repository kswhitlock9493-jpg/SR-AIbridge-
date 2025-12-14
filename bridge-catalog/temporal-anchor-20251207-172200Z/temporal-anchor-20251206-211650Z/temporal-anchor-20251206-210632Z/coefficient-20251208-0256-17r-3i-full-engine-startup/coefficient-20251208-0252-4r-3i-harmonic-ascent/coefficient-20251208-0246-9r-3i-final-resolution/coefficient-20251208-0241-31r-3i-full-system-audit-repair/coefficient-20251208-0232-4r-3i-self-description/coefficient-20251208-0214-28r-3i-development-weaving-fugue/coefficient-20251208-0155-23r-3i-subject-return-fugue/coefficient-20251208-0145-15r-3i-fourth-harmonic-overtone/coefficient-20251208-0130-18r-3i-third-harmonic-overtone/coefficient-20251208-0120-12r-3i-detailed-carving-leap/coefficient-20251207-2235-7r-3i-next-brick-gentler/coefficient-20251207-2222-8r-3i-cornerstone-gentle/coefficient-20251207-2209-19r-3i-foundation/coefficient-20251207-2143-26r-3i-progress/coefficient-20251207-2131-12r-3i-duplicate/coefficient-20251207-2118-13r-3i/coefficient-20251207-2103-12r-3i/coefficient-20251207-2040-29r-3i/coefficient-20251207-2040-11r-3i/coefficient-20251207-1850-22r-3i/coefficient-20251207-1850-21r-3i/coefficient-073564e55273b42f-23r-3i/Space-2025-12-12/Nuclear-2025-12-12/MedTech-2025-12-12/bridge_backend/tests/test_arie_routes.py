"""
Tests for ARIE Routes and API Endpoints
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from fastapi import FastAPI

from engines.arie.routes import router, get_engine
from engines.arie.models import PolicyType, ScanRequest, RollbackRequest


class TestARIERoutes(unittest.TestCase):
    """Test ARIE API routes"""
    
    def setUp(self):
        """Set up test client"""
        self.app = FastAPI()
        self.app.include_router(router)
        self.client = TestClient(self.app)
        
        # Create temp directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_run_scan_dry_run(self):
        """Test POST /api/arie/run with dry_run"""
        response = self.client.post(
            "/api/arie/run",
            json={
                "policy": "SAFE_EDIT",
                "dry_run": True,
                "apply": False
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("run_id", data)
        self.assertIn("findings_count", data)
        self.assertTrue(data["dry_run"])
        self.assertEqual(data["fixes_applied"], 0)
    
    def test_run_scan_lint_only(self):
        """Test scan with LINT_ONLY policy"""
        response = self.client.post(
            "/api/arie/run",
            json={
                "policy": "LINT_ONLY",
                "dry_run": True,
                "apply": False
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data["policy"], "LINT_ONLY")
    
    def test_get_report_without_run(self):
        """Test GET /api/arie/report when no reports exist"""
        # Reset engine
        from engines.arie.routes import _engine
        if _engine:
            _engine.last_summary = None
        
        response = self.client.get("/api/arie/report")
        
        # Should return 404 when no reports available
        self.assertEqual(response.status_code, 404)
    
    def test_get_report_after_run(self):
        """Test GET /api/arie/report after running scan"""
        # First run a scan
        self.client.post(
            "/api/arie/run",
            json={
                "policy": "LINT_ONLY",
                "dry_run": True,
                "apply": False
            }
        )
        
        # Then get report
        response = self.client.get("/api/arie/report")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("run_id", data)
        self.assertIn("findings_count", data)
    
    def test_rollback_nonexistent_patch(self):
        """Test POST /api/arie/rollback with nonexistent patch"""
        response = self.client.post(
            "/api/arie/rollback",
            json={
                "patch_id": "nonexistent_patch",
                "force": False
            }
        )
        
        # Should return 400 for failed rollback
        self.assertEqual(response.status_code, 400)
    
    def test_get_config(self):
        """Test GET /api/arie/config"""
        response = self.client.get("/api/arie/config")
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("enabled", data)
        self.assertIn("policy", data)
        self.assertIn("auto_fix_on_deploy", data)
    
    def test_update_config(self):
        """Test POST /api/arie/config"""
        response = self.client.post(
            "/api/arie/config",
            json={
                "enabled": True,
                "policy": "SAFE_EDIT",
                "auto_fix_on_deploy": False,
                "max_patch_backlog": 100,
                "strict_rollback": True,
                "excluded_paths": [],
                "enabled_analyzers": []
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data["enabled"])
        self.assertEqual(data["policy"], "SAFE_EDIT")
        self.assertEqual(data["max_patch_backlog"], 100)


class TestARIEModels(unittest.TestCase):
    """Test ARIE Pydantic models"""
    
    def test_scan_request_model(self):
        """Test ScanRequest model"""
        request = ScanRequest(
            policy=PolicyType.SAFE_EDIT,
            dry_run=True,
            apply=False
        )
        
        self.assertEqual(request.policy, PolicyType.SAFE_EDIT)
        self.assertTrue(request.dry_run)
        self.assertFalse(request.apply)
    
    def test_rollback_request_model(self):
        """Test RollbackRequest model"""
        request = RollbackRequest(
            patch_id="test_patch",
            force=False
        )
        
        self.assertEqual(request.patch_id, "test_patch")
        self.assertFalse(request.force)
    
    def test_policy_type_enum(self):
        """Test PolicyType enum values"""
        self.assertEqual(PolicyType.LINT_ONLY.value, "LINT_ONLY")
        self.assertEqual(PolicyType.SAFE_EDIT.value, "SAFE_EDIT")
        self.assertEqual(PolicyType.REFACTOR.value, "REFACTOR")
        self.assertEqual(PolicyType.ARCHIVE.value, "ARCHIVE")


if __name__ == '__main__':
    unittest.main()
