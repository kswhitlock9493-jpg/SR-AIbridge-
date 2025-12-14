"""
Tests for ARIE Truth and Cascade Integration
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, UTC
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.arie.core import ARIEEngine
from engines.arie.models import PolicyType, Patch, Summary, Finding


class MockTruthLink:
    """Mock Truth Link for testing without bridge_core dependencies"""
    
    def __init__(self, truth_engine=None, arie_engine=None):
        self.truth_engine = truth_engine
        self.arie_engine = arie_engine
    
    async def certify_patch(self, patch):
        """Mock certification"""
        if self.truth_engine:
            result = await self.truth_engine.verify()
            if not result.get("certified"):
                # Trigger rollback on failure
                if self.arie_engine:
                    self.arie_engine.rollback(patch.id, force=False)
            return result
        return {"certified": True, "certificate_id": "mock_cert"}


class MockCascadeLink:
    """Mock Cascade Link for testing"""
    
    def __init__(self, cascade_engine=None, bus=None):
        self.cascade_engine = cascade_engine
        self.bus = bus
    
    async def trigger_post_fix_cascade(self, summary):
        """Mock cascade trigger"""
        if summary.fixes_applied == 0:
            return
        
        # Check for config fixes
        config_fixes = sum(1 for f in summary.findings if f.category == "config_smell")
        
        if config_fixes > 0 and self.bus:
            await self.bus.publish("envrecon.scan", {
                "trigger": "arie_config_fix",
                "run_id": summary.run_id,
                "config_fixes": config_fixes
            })


class TestTruthCascadeIntegration(unittest.TestCase):
    """Test integrated Truth and Cascade flows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = ARIEEngine(repo_root=self.temp_dir)
        self.truth_engine = MagicMock()
        self.cascade_engine = MagicMock()
        self.bus = MagicMock()
        
        self.truth_link = MockTruthLink(
            truth_engine=self.truth_engine,
            arie_engine=self.engine
        )
        
        self.cascade_link = MockCascadeLink(
            cascade_engine=self.cascade_engine,
            bus=self.bus
        )
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    async def test_successful_fix_flow(self):
        """
        Test complete flow: scan → fix → certify → cascade
        """
        # Step 1: Create test file with issue
        test_file = self.temp_dir / "test.py"
        test_file.write_text("from datetime import datetime\ntimestamp = datetime.utcnow()")
        
        # Step 2: Run scan and apply fixes
        summary = self.engine.run(
            policy=PolicyType.SAFE_EDIT,
            dry_run=False,
            apply=True
        )
        
        # Should have found and potentially fixed the issue
        self.assertGreater(summary.findings_count, 0)
        
        # Step 3: Mock Truth certification
        if summary.patches:
            patch = summary.patches[0]
            
            self.truth_engine.verify = AsyncMock(return_value={
                "certified": True,
                "certificate_id": "cert_test_123"
            })
            
            cert_result = await self.truth_link.certify_patch(patch)
            
            self.assertTrue(cert_result["certified"])
            self.assertTrue(patch.certified)
            
            # Step 4: Trigger cascade
            self.bus.publish = AsyncMock()
            await self.cascade_link.trigger_post_fix_cascade(summary)
            
            # Should have published events
            self.assertTrue(self.bus.publish.called)
    
    async def test_failed_certification_rollback(self):
        """
        Test rollback flow when certification fails
        """
        # Create a patch
        patch = Patch(
            id="test_patch",
            plan_id="test_plan",
            timestamp=datetime.now(UTC).isoformat() + "Z",
            files_modified=["test.py"],
            diff="test diff",
            certified=False
        )
        
        # Mock failed certification
        self.truth_engine.verify = AsyncMock(return_value={
            "certified": False,
            "reason": "Tests failed"
        })
        
        # Mock rollback
        rollback_result = MagicMock()
        rollback_result.success = True
        rollback_result.restored_files = ["test.py"]
        self.engine.rollback = MagicMock(return_value=rollback_result)
        
        # Certify patch (should fail and trigger rollback)
        result = await self.truth_link.certify_patch(patch)
        
        self.assertFalse(result["certified"])
        self.assertTrue(self.engine.rollback.called)
        
        # Verify rollback was called with correct patch ID
        self.engine.rollback.assert_called_once_with(patch.id, force=False)
    
    async def test_cascade_notifies_envrecon(self):
        """
        Test that Cascade notifies EnvRecon for config fixes
        """
        # Create summary with config smell fixes
        summary = Summary(
            run_id="test_run",
            timestamp=datetime.now(UTC).isoformat() + "Z",
            policy=PolicyType.SAFE_EDIT,
            dry_run=False,
            findings_count=5,
            findings_by_severity={},
            findings_by_category={},
            fixes_applied=3,
            duration_seconds=1.0,
            findings=[
                Finding(
                    id="config_1",
                    analyzer="config_smell",
                    severity="low",
                    category="config_smell",
                    file_path="config.py",
                    description="ENV access without default"
                ),
                Finding(
                    id="config_2",
                    analyzer="config_smell",
                    severity="low",
                    category="config_smell",
                    file_path="settings.py",
                    description="ENV access without default"
                )
            ],
            patches=[]
        )
        
        self.bus.publish = AsyncMock()
        
        await self.cascade_link.trigger_post_fix_cascade(summary)
        
        # Should publish envrecon.scan event
        self.assertTrue(self.bus.publish.called)
    
    async def test_no_cascade_for_dry_run(self):
        """
        Test that cascade is not triggered for dry runs
        """
        summary = Summary(
            run_id="test_run",
            timestamp=datetime.now(UTC).isoformat() + "Z",
            policy=PolicyType.LINT_ONLY,
            dry_run=True,  # Dry run
            findings_count=10,
            findings_by_severity={},
            findings_by_category={},
            fixes_applied=0,  # No fixes applied in dry run
            duration_seconds=1.0,
            findings=[],
            patches=[]
        )
        
        self.bus.publish = AsyncMock()
        
        await self.cascade_link.trigger_post_fix_cascade(summary)
        
        # Should not publish anything
        self.assertFalse(self.bus.publish.called)
    
    async def test_multiple_patches_certification(self):
        """
        Test certification of multiple patches
        """
        patches = [
            Patch(
                id=f"patch_{i}",
                plan_id=f"plan_{i}",
                timestamp=datetime.now(UTC).isoformat() + "Z",
                files_modified=[f"file_{i}.py"],
                diff=f"diff {i}",
                certified=False
            )
            for i in range(3)
        ]
        
        # Mock Truth Engine to certify all
        self.truth_engine.verify = AsyncMock(return_value={
            "certified": True,
            "certificate_id": "cert_batch"
        })
        
        # Certify all patches
        results = []
        for patch in patches:
            result = await self.truth_link.certify_patch(patch)
            results.append(result)
        
        # All should be certified
        for result, patch in zip(results, patches):
            self.assertTrue(result["certified"])
            self.assertTrue(patch.certified)


class TestARIEEndToEnd(unittest.TestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = ARIEEngine(repo_root=self.temp_dir)
    
    def tearDown(self):
        """Clean up"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_scan_fix_cycle(self):
        """
        Test complete cycle: create file → scan → plan → fix
        """
        # Create test file with multiple issues
        test_file = self.temp_dir / "example.py"
        test_file.write_text("""
from datetime import datetime
import os

# Get config without default
DEBUG = os.getenv("DEBUG")

# Deprecated datetime
timestamp = datetime.utcnow()
created_at = datetime.utcnow()
        """)
        
        # Run LINT_ONLY first
        summary_lint = self.engine.run(
            policy=PolicyType.LINT_ONLY,
            dry_run=True
        )
        
        # Should find issues
        self.assertGreater(summary_lint.findings_count, 0)
        
        # Check for expected findings
        deprecated_findings = [
            f for f in summary_lint.findings 
            if f.category == "deprecated"
        ]
        config_findings = [
            f for f in summary_lint.findings 
            if f.category == "config_smell"
        ]
        
        # Should find deprecated datetime usage
        self.assertGreater(len(deprecated_findings), 0)
        
        # Should find config smell
        self.assertGreater(len(config_findings), 0)
        
        # Now apply fixes
        summary_fix = self.engine.run(
            policy=PolicyType.SAFE_EDIT,
            dry_run=False,
            apply=True
        )
        
        # Should have applied some fixes
        self.assertGreater(summary_fix.fixes_applied, 0)
    
    def test_duplicate_detection(self):
        """
        Test duplicate file detection
        """
        # Create duplicate files
        file1 = self.temp_dir / "dup1.txt"
        file2 = self.temp_dir / "dup2.txt"
        
        content = "This is duplicate content"
        file1.write_text(content)
        file2.write_text(content)
        
        # Run scan
        summary = self.engine.run(policy=PolicyType.LINT_ONLY, dry_run=True)
        
        # Should detect duplicate
        dup_findings = [
            f for f in summary.findings 
            if f.category == "duplicate"
        ]
        
        self.assertGreater(len(dup_findings), 0)


if __name__ == '__main__':
    # Run async tests
    import asyncio
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Monkey-patch to handle async tests
    original_call = unittest.TestCase.__call__
    
    def async_aware_call(self, *args, **kwargs):
        test_method = getattr(self, self._testMethodName)
        if asyncio.iscoroutinefunction(test_method):
            # Replace with sync version
            setattr(self, self._testMethodName, 
                   lambda: asyncio.run(test_method()))
        return original_call(self, *args, **kwargs)
    
    unittest.TestCase.__call__ = async_aware_call
    
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
