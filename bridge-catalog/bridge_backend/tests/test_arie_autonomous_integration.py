"""
Integration test for ARIE v1.9.6o autonomous scheduling
Tests the complete autonomous flow including scheduler, Genesis integration, and rollback
"""

import unittest
import asyncio
import tempfile
import shutil
import os
import importlib.util
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, UTC

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.arie.scheduler import ARIEScheduler
from engines.arie.core import ARIEEngine
from engines.arie.models import PolicyType, Summary, Patch

# Import ARIEGenesisLink directly to avoid bridge_core __init__ dependencies
spec = importlib.util.spec_from_file_location(
    "arie_genesis_link",
    Path(__file__).parent.parent / "bridge_core" / "engines" / "adapters" / "arie_genesis_link.py"
)
arie_genesis_link_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arie_genesis_link_module)
ARIEGenesisLink = arie_genesis_link_module.ARIEGenesisLink

# Import ARIEScheduleLink directly
spec = importlib.util.spec_from_file_location(
    "arie_schedule_link",
    Path(__file__).parent.parent / "bridge_core" / "engines" / "adapters" / "arie_schedule_link.py"
)
arie_schedule_link_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arie_schedule_link_module)
ARIEScheduleLink = arie_schedule_link_module.ARIEScheduleLink


class TestARIEAutonomousIntegration(unittest.TestCase):
    """Integration tests for ARIE autonomous mode"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock bus
        self.mock_bus = Mock()
        self.mock_bus.publish = AsyncMock()
        self.mock_bus.subscribe = Mock()
        
        # Mock engine with summary
        self.mock_engine = Mock(spec=ARIEEngine)
        self.mock_summary = Summary(
            run_id="test_run_123",
            timestamp=datetime.now(UTC).isoformat() + "Z",
            policy=PolicyType.SAFE_EDIT,
            dry_run=False,
            findings_count=5,
            findings_by_severity={"medium": 3, "low": 2},
            findings_by_category={"deprecated": 3, "stub": 2},
            fixes_applied=3,
            fixes_failed=0,
            duration_seconds=1.5,
            findings=[],
            patches=[
                Patch(
                    id="patch_001",
                    plan_id="plan_001",
                    timestamp=datetime.now(UTC).isoformat() + "Z",
                    files_modified=["test.py"],
                    diff="- old\n+ new",
                    certified=False,
                    certificate_id=None,
                    rollback_available=True
                )
            ]
        )
        self.mock_engine.run.return_value = self.mock_summary
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_RUN_ON_DEPLOY": "true",
        "ARIE_TRUTH_MANDATORY": "true"
    })
    def test_full_autonomous_flow(self):
        """Test complete autonomous flow: deploy → scan → certify → commit"""
        loop = asyncio.get_event_loop()
        
        # Create Genesis link
        with patch.object(Path, 'mkdir'):
            genesis_link = ARIEGenesisLink(bus=self.mock_bus, engine=self.mock_engine)
        
        # Simulate deploy success event
        deploy_event = {
            "platform": "render",
            "deployment_id": "dep_123",
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "status": "success"
        }
        
        # Trigger deploy success
        loop.run_until_complete(genesis_link._on_deploy_success(deploy_event))
        
        # Verify engine was called with SAFE_EDIT policy
        self.mock_engine.run.assert_called_once()
        call_kwargs = self.mock_engine.run.call_args[1]
        self.assertEqual(call_kwargs["policy"], PolicyType.SAFE_EDIT)
        self.assertFalse(call_kwargs["dry_run"])
        self.assertTrue(call_kwargs["apply"])
        
        # Verify events were published
        publish_calls = [call[0][0] for call in self.mock_bus.publish.call_args_list]
        self.assertIn("arie.audit", publish_calls)
        self.assertIn("arie.fix.applied", publish_calls)
        self.assertIn("cascade.notify", publish_calls)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_TRUTH_MANDATORY": "true"
    })
    def test_certification_flow(self):
        """Test Truth certification request and success"""
        from unittest.mock import patch as mock_patch
        loop = asyncio.get_event_loop()
        
        # Create Genesis link
        with mock_patch.object(Path, 'mkdir'):
            genesis_link = ARIEGenesisLink(bus=self.mock_bus, engine=self.mock_engine)
        
        # Request certification
        cert_result = loop.run_until_complete(
            genesis_link._request_certification(self.mock_summary)
        )
        
        # Verify certification succeeded
        self.assertTrue(cert_result["success"])
        self.assertIn("certificate_id", cert_result)
        
        # Verify patches were marked as certified
        for patch in self.mock_summary.patches:
            self.assertTrue(patch.certified)
            self.assertIsNotNone(patch.certificate_id)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_TRUTH_MANDATORY": "true"
    })
    def test_failed_certification_rollback(self):
        """Test rollback on failed certification"""
        loop = asyncio.get_event_loop()
        
        # Mock rollback
        from engines.arie.models import Rollback
        mock_rollback = Rollback(
            id="rb_001",
            patch_id="patch_001",
            timestamp=datetime.now(UTC).isoformat() + "Z",
            success=True,
            error=None,
            restored_files=["test.py"]
        )
        self.mock_engine.rollback.return_value = mock_rollback
        
        # Create Genesis link
        with patch.object(Path, 'mkdir'):
            genesis_link = ARIEGenesisLink(bus=self.mock_bus, engine=self.mock_engine)
        
        # Simulate failed certification
        loop.run_until_complete(
            genesis_link._handle_failed_certification(self.mock_summary)
        )
        
        # Verify rollback was called
        self.mock_engine.rollback.assert_called_once_with("patch_001", force=False)
        
        # Verify rollback event was published
        publish_calls = [call[0][0] for call in self.mock_bus.publish.call_args_list]
        self.assertIn("arie.fix.rollback", publish_calls)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_SCHEDULE_INTERVAL_HOURS": "12"
    })
    def test_scheduler_integration(self):
        """Test scheduler integration with Genesis"""
        loop = asyncio.get_event_loop()
        
        # Create scheduler
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        # Create schedule link
        schedule_link = ARIEScheduleLink(bus=self.mock_bus, scheduler=scheduler)
        
        # Verify scheduler is enabled
        self.assertTrue(scheduler.enabled)
        self.assertEqual(scheduler.interval_hours, 12)
        
        # Test tick publication
        loop.run_until_complete(scheduler._publish_tick())
        
        # Verify tick event was published
        publish_calls = [call[0][0] for call in self.mock_bus.publish.call_args_list]
        self.assertIn("arie.schedule.tick", publish_calls)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_ADMIRAL_ONLY_APPLY": "true",
        "STEWARD_OWNER_HANDLE": "test_admiral"
    })
    def test_admiral_guard(self):
        """Test Admiral-only manual trigger guard"""
        loop = asyncio.get_event_loop()
        
        # Create scheduler
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        # Should succeed with Admiral
        result = loop.run_until_complete(
            scheduler.trigger_manual_run("test_admiral")
        )
        self.assertEqual(result["run_id"], "test_run_123")
        
        # Should fail with non-Admiral
        with self.assertRaises(PermissionError) as context:
            loop.run_until_complete(
                scheduler.trigger_manual_run("random_user")
            )
        
        self.assertIn("Admiral", str(context.exception))
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_RUN_ON_DEPLOY": "false"
    })
    def test_run_on_deploy_disabled(self):
        """Test that ARIE respects RUN_ON_DEPLOY=false"""
        loop = asyncio.get_event_loop()
        
        # Create Genesis link
        with patch.object(Path, 'mkdir'):
            genesis_link = ARIEGenesisLink(bus=self.mock_bus, engine=self.mock_engine)
        
        # Simulate deploy success event
        deploy_event = {
            "platform": "render",
            "deployment_id": "dep_123",
            "timestamp": datetime.now(UTC).isoformat() + "Z",
            "status": "success"
        }
        
        # Trigger deploy success
        loop.run_until_complete(genesis_link._on_deploy_success(deploy_event))
        
        # Verify engine was NOT called
        self.mock_engine.run.assert_not_called()


if __name__ == '__main__':
    unittest.main()
