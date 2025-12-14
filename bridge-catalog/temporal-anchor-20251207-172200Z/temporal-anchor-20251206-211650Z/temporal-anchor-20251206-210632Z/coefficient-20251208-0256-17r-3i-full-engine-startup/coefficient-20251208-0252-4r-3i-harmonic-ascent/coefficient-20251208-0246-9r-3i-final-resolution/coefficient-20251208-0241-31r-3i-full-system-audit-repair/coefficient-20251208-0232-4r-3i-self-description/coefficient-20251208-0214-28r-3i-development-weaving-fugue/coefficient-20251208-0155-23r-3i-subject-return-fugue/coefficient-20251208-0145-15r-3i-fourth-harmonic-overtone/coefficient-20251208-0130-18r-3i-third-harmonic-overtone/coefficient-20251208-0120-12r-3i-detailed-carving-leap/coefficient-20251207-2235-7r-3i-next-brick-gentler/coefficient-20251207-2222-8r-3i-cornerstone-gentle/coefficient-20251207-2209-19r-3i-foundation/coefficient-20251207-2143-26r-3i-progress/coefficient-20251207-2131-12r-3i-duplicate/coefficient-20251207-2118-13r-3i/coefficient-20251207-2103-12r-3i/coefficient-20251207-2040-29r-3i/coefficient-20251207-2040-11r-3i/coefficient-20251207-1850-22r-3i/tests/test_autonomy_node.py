"""
Test suite for Embedded Autonomy Node (EAN)
v1.9.7n

Tests the core functionality of the GitHub Internal Mini-Bridge Engine.
"""
import unittest
import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# Add the autonomy_node directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../.github/autonomy_node'))

import truth
import parser
import cascade
import blueprint
from core import AutonomyNode


class TestTruthMicroCertifier(unittest.TestCase):
    """Test the Truth Micro-Certifier component"""
    
    def test_verify_all_ok(self):
        """Test verification with all OK results"""
        results = {
            "file1.py": {"status": "ok", "action": "cleaned"},
            "file2.py": {"status": "ok", "action": "refactored"}
        }
        # Should not raise exception
        truth.verify(results)
    
    def test_verify_with_warnings(self):
        """Test verification with warning results"""
        results = {
            "file1.py": {"status": "ok", "action": "cleaned"},
            "file2.py": {"status": "warn", "action": "needs_review"}
        }
        # Should not raise exception, just print warnings
        truth.verify(results)


class TestParserSentinel(unittest.TestCase):
    """Test the Parser Sentinel component"""
    
    def setUp(self):
        """Set up temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up temporary directory"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_scan_empty_repo(self):
        """Test scanning an empty repository"""
        findings = parser.scan_repo()
        self.assertEqual(len(findings), 0)
    
    def test_scan_with_print_statements(self):
        """Test scanning finds print statements"""
        # Create test file with print statement
        test_file = os.path.join(self.test_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write('print("Hello, world!")\n')
        
        findings = parser.scan_repo()
        self.assertIn("test.py", findings)
        self.assertEqual(findings["test.py"]["status"], "warn")
        self.assertEqual(findings["test.py"]["reason"], "debug print")
    
    def test_scan_without_print_statements(self):
        """Test scanning file without print statements"""
        # Create test file without print statement
        test_file = os.path.join(self.test_dir, "clean.py")
        with open(test_file, 'w') as f:
            f.write('x = 42\ny = x * 2\n')
        
        findings = parser.scan_repo()
        self.assertNotIn("clean.py", findings)
    
    def test_scan_ignores_hidden_dirs(self):
        """Test scanning ignores .git and other hidden directories"""
        # Create .git directory with file
        git_dir = os.path.join(self.test_dir, ".git")
        os.makedirs(git_dir)
        test_file = os.path.join(git_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write('print("Should be ignored")\n')
        
        findings = parser.scan_repo()
        self.assertEqual(len(findings), 0)


class TestBlueprintMicroForge(unittest.TestCase):
    """Test the Blueprint Micro-Forge component"""
    
    def test_repair_warnings(self):
        """Test repairing warning issues"""
        findings = {
            "file1.py": {"status": "warn", "reason": "debug print"},
            "file2.py": {"status": "warn", "reason": "unused import"}
        }
        
        fixes = blueprint.repair(findings)
        
        self.assertEqual(len(fixes), 2)
        self.assertEqual(fixes["file1.py"]["status"], "ok")
        self.assertEqual(fixes["file1.py"]["action"], "log_cleaned")
        self.assertEqual(fixes["file2.py"]["status"], "ok")
    
    def test_repair_empty_findings(self):
        """Test repairing with no findings"""
        findings = {}
        fixes = blueprint.repair(findings)
        self.assertEqual(len(fixes), 0)


class TestCascadeMiniOrchestrator(unittest.TestCase):
    """Test the Cascade Mini-Orchestrator component"""
    
    def test_sync_state(self):
        """Test state synchronization"""
        # Should not raise exception
        cascade.sync_state()


class TestAutonomyNodeCore(unittest.TestCase):
    """Test the core AutonomyNode orchestrator"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create node_config.json
        config = {
            "autonomy_interval_hours": 6,
            "max_report_backups": 10,
            "truth_certification": True,
            "self_heal_enabled": True,
            "genesis_registration": False  # Disable for testing
        }
        
        self.config_path = os.path.join(self.test_dir, "node_config.json")
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        # Create reports directory
        self.reports_dir = os.path.join(self.test_dir, "reports")
        os.makedirs(self.reports_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_node_initialization(self):
        """Test AutonomyNode initialization"""
        # Temporarily change the config path
        original_dirname = os.path.dirname
        
        def mock_dirname(path):
            return self.test_dir
        
        os.path.dirname = mock_dirname
        
        try:
            node = AutonomyNode()
            self.assertIsNotNone(node.config)
            self.assertEqual(node.config["autonomy_interval_hours"], 6)
        finally:
            os.path.dirname = original_dirname
    
    def test_config_parsing(self):
        """Test configuration file parsing"""
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        self.assertEqual(config["autonomy_interval_hours"], 6)
        self.assertEqual(config["max_report_backups"], 10)
        self.assertTrue(config["truth_certification"])
        self.assertTrue(config["self_heal_enabled"])


class TestGenesisRegistration(unittest.TestCase):
    """Test Genesis registration functionality"""
    
    def test_registration_payload_structure(self):
        """Test registration payload has correct structure"""
        from bridge_backend.genesis.registration import register_embedded_nodes
        
        result = register_embedded_nodes()
        
        # Should have registered flag and node info
        self.assertIn("registered", result)
        self.assertIn("node", result)
        
        # Node should have required fields
        node = result["node"]
        self.assertEqual(node["engine"], "autonomy_node")
        self.assertEqual(node["location"], ".github/autonomy_node")
        self.assertEqual(node["type"], "micro_bridge")
        self.assertTrue(node["certified"])
        self.assertEqual(node["version"], "1.9.7n")


class TestIntegration(unittest.TestCase):
    """Integration tests for the full autonomy cycle"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test Python files
        with open("test1.py", 'w') as f:
            f.write('print("Test 1")\n')
        
        with open("test2.py", 'w') as f:
            f.write('x = 42\n')
    
    def tearDown(self):
        """Clean up integration test environment"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def test_full_cycle(self):
        """Test the complete autonomy cycle: scan -> repair -> verify -> sync"""
        # Step 1: Scan
        findings = parser.scan_repo()
        self.assertGreater(len(findings), 0)
        self.assertIn("test1.py", findings)
        
        # Step 2: Repair
        fixes = blueprint.repair(findings)
        self.assertEqual(len(fixes), len(findings))
        
        # Step 3: Verify
        truth.verify(fixes)
        
        # Step 4: Sync
        cascade.sync_state()
        
        # All steps completed without exception


if __name__ == '__main__':
    unittest.main()
