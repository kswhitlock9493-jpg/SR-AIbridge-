"""
Tests for ARIE Scheduler
"""

import unittest
import asyncio
import tempfile
import shutil
import json
import os
from pathlib import Path
from datetime import datetime, UTC
from unittest.mock import Mock, patch, AsyncMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.arie.scheduler import ARIEScheduler
from engines.arie.core import ARIEEngine
from engines.arie.models import PolicyType, Summary


class TestARIEScheduler(unittest.TestCase):
    """Test ARIE scheduler functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.logs_dir = self.temp_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Mock engine
        self.mock_engine = Mock(spec=ARIEEngine)
        
        # Mock bus
        self.mock_bus = Mock()
        self.mock_bus.publish = AsyncMock()
        
        # Create summary mock
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
            patches=[]
        )
        
        self.mock_engine.run.return_value = self.mock_summary
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_SCHEDULE_INTERVAL_HOURS": "12"
    })
    def test_scheduler_initialization(self):
        """Test scheduler initializes with correct configuration"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        self.assertTrue(scheduler.enabled)
        self.assertEqual(scheduler.interval_hours, 12)
        self.assertTrue(scheduler.run_on_deploy)
        self.assertTrue(scheduler.admiral_only_apply)
        self.assertTrue(scheduler.truth_mandatory)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "false"
    })
    def test_scheduler_disabled(self):
        """Test scheduler respects disabled flag"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        self.assertFalse(scheduler.enabled)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_SCHEDULE_INTERVAL_HOURS": "6"
    })
    def test_custom_interval(self):
        """Test custom schedule interval"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        self.assertEqual(scheduler.interval_hours, 6)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true"
    })
    def test_run_scan(self):
        """Test scheduled scan execution"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        # Run scan
        loop = asyncio.get_event_loop()
        summary = loop.run_until_complete(scheduler._run_scan())
        
        # Verify engine was called
        self.mock_engine.run.assert_called_once_with(
            policy=PolicyType.SAFE_EDIT,
            dry_run=False,
            apply=True
        )
        
        # Verify summary returned
        self.assertEqual(summary.run_id, "test_run_123")
        self.assertEqual(summary.findings_count, 5)
        self.assertEqual(summary.fixes_applied, 3)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true"
    })
    def test_publish_tick(self):
        """Test tick event publication"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        # Publish tick
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scheduler._publish_tick())
        
        # Verify bus publish was called
        self.mock_bus.publish.assert_called_once()
        call_args = self.mock_bus.publish.call_args
        self.assertEqual(call_args[0][0], "arie.schedule.tick")
        self.assertIn("timestamp", call_args[0][1])
        self.assertEqual(call_args[0][1]["interval_hours"], 12)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true"
    })
    def test_publish_summary(self):
        """Test summary event publication"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        # Publish summary
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scheduler._publish_summary(self.mock_summary))
        
        # Verify bus publish was called
        self.mock_bus.publish.assert_called_once()
        call_args = self.mock_bus.publish.call_args
        self.assertEqual(call_args[0][0], "arie.schedule.summary")
        self.assertEqual(call_args[0][1]["run_id"], "test_run_123")
        self.assertEqual(call_args[0][1]["findings_count"], 5)
        self.assertEqual(call_args[0][1]["fixes_applied"], 3)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true"
    })
    def test_log_run(self):
        """Test run logging to JSON files"""
        # Override logs_dir for this test
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        scheduler.logs_dir = self.logs_dir
        
        # Log run
        scheduler._log_run(self.mock_summary)
        
        # Verify autorun log was created
        autorun_log = self.logs_dir / "arie_autorun.json"
        self.assertTrue(autorun_log.exists())
        
        # Verify log contents
        with open(autorun_log, 'r') as f:
            log_data = json.load(f)
        
        self.assertEqual(len(log_data), 1)
        self.assertEqual(log_data[0]["run_id"], "test_run_123")
        self.assertEqual(log_data[0]["findings_count"], 5)
        self.assertEqual(log_data[0]["fixes_applied"], 3)
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_ADMIRAL_ONLY_APPLY": "true",
        "STEWARD_OWNER_HANDLE": "test_admiral"
    })
    def test_manual_trigger_admiral_only(self):
        """Test manual trigger with Admiral permission"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        loop = asyncio.get_event_loop()
        
        # Should succeed with correct Admiral
        result = loop.run_until_complete(scheduler.trigger_manual_run("test_admiral"))
        self.assertEqual(result["run_id"], "test_run_123")
        
        # Should fail with non-Admiral
        with self.assertRaises(PermissionError):
            loop.run_until_complete(scheduler.trigger_manual_run("random_user"))
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true",
        "ARIE_ADMIRAL_ONLY_APPLY": "false"
    })
    def test_manual_trigger_no_admiral_check(self):
        """Test manual trigger without Admiral restriction"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        loop = asyncio.get_event_loop()
        
        # Should succeed with any user
        result = loop.run_until_complete(scheduler.trigger_manual_run("any_user"))
        self.assertEqual(result["run_id"], "test_run_123")
    
    @patch.dict(os.environ, {
        "ARIE_SCHEDULE_ENABLED": "true"
    })
    def test_start_stop_scheduler(self):
        """Test starting and stopping scheduler"""
        with patch.object(Path, 'mkdir'):
            scheduler = ARIEScheduler(engine=self.mock_engine, bus=self.mock_bus)
        
        loop = asyncio.get_event_loop()
        
        # Start scheduler
        loop.run_until_complete(scheduler.start())
        self.assertTrue(scheduler._running)
        self.assertIsNotNone(scheduler._task)
        
        # Stop scheduler
        loop.run_until_complete(scheduler.stop())
        self.assertFalse(scheduler._running)


if __name__ == '__main__':
    unittest.main()
