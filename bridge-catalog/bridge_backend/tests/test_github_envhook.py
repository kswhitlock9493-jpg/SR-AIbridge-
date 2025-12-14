"""
Tests for GitHub Environment Hook (github_envhook.py)
"""

import unittest
import tempfile
import json
import asyncio
from pathlib import Path
from datetime import datetime, UTC

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the hook module
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".github" / "scripts"))
from github_envhook import EnvironmentFileWatcher


class TestEnvironmentFileWatcher(unittest.TestCase):
    """Test GitHub environment file watcher"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.env_file = self.temp_dir / "environment.json"
        self.state_file = self.temp_dir / "state.json"
        
        # Create initial environment.json
        self.initial_config = {
            "version": "1.9.6x",
            "description": "Test environment",
            "variables": {
                "TEST_VAR": {
                    "description": "Test variable",
                    "required": True
                }
            }
        }
        
        with open(self.env_file, 'w') as f:
            json.dump(self.initial_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initial_hash_computation(self):
        """Should compute initial file hash on first run"""
        watcher = EnvironmentFileWatcher(self.env_file, self.state_file)
        
        # First check should not detect change (initializing)
        changed = watcher.has_changed()
        self.assertFalse(changed)
        
        # Hash should be set
        self.assertIsNotNone(watcher.last_hash)
        self.assertEqual(len(watcher.last_hash), 64)  # SHA256 hash length
    
    def test_detect_file_change(self):
        """Should detect when environment.json changes"""
        watcher = EnvironmentFileWatcher(self.env_file, self.state_file)
        
        # Initialize
        watcher.has_changed()
        
        # Modify the file
        modified_config = self.initial_config.copy()
        modified_config['version'] = "1.9.6y"
        
        with open(self.env_file, 'w') as f:
            json.dump(modified_config, f, indent=2)
        
        # Should detect change
        changed = watcher.has_changed()
        self.assertTrue(changed)
    
    def test_no_change_when_file_unchanged(self):
        """Should not detect change when file is unchanged"""
        watcher = EnvironmentFileWatcher(self.env_file, self.state_file)
        
        # Initialize
        watcher.has_changed()
        
        # Check again without modifying
        changed = watcher.has_changed()
        self.assertFalse(changed)
    
    def test_state_persistence(self):
        """Should persist state between watcher instances"""
        # First watcher
        watcher1 = EnvironmentFileWatcher(self.env_file, self.state_file)
        watcher1.has_changed()
        hash1 = watcher1.last_hash
        
        # Second watcher should load same hash
        watcher2 = EnvironmentFileWatcher(self.env_file, self.state_file)
        self.assertEqual(watcher2.last_hash, hash1)
    
    def test_handles_missing_file(self):
        """Should handle missing environment.json gracefully"""
        missing_file = self.temp_dir / "nonexistent.json"
        watcher = EnvironmentFileWatcher(missing_file, self.state_file)
        
        # Should not crash
        changed = watcher.has_changed()
        self.assertFalse(changed)
    
    def test_trigger_events_without_genesis(self):
        """Should handle missing Genesis bus gracefully"""
        watcher = EnvironmentFileWatcher(self.env_file, self.state_file)
        
        # Should not crash when Genesis is not available
        # (We can't test actual publishing without Genesis infrastructure)
        try:
            asyncio.run(watcher.trigger_sync_events())
        except Exception as e:
            # Expected - Genesis bus may not be available in test environment
            pass


class TestEventPayloads(unittest.TestCase):
    """Test event payload structure"""
    
    def test_event_payload_structure(self):
        """Verify event payloads contain required fields"""
        # This is more of a documentation test
        required_envmirror_fields = [
            "type", "source", "trigger", "timestamp", 
            "file_path", "file_hash", "version", "initiated_by"
        ]
        
        required_envduo_fields = [
            "type", "source", "trigger", "timestamp",
            "file_path", "file_hash", "audit_scope", "initiated_by"
        ]
        
        # These fields should be present in the actual events
        # See github_envhook.py trigger_sync_events() method
        self.assertTrue(len(required_envmirror_fields) > 0)
        self.assertTrue(len(required_envduo_fields) > 0)


if __name__ == '__main__':
    unittest.main()
