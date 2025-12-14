"""
Tests for ARIE Engine Core
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, UTC

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.arie.core import (
    ARIEEngine, DatetimeDeprecatedAnalyzer, StubMarkerAnalyzer,
    RouteRegistryAnalyzer, ImportHealthAnalyzer, ConfigSmellAnalyzer,
    DuplicateFileAnalyzer, DeadFileAnalyzer, UnusedFileAnalyzer,
    DatetimeFixer, StubCommentFixer
)
from engines.arie.models import PolicyType, Severity


class TestDatetimeDeprecatedAnalyzer(unittest.TestCase):
    """Test datetime.utcnow() detection"""
    
    def setUp(self):
        self.analyzer = DatetimeDeprecatedAnalyzer()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_detects_deprecated_datetime(self):
        """Should detect datetime.utcnow() usage"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("timestamp = datetime.utcnow()")
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].severity, Severity.MEDIUM)
        self.assertEqual(findings[0].category, "deprecated")
        self.assertIn("utcnow", findings[0].description)
    
    def test_ignores_correct_datetime(self):
        """Should not flag datetime.now(UTC)"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("timestamp = datetime.now(UTC)")
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 0)
    
    def test_multiple_occurrences(self):
        """Should detect multiple occurrences"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("""
            t1 = datetime.utcnow()
            t2 = datetime.utcnow()
            t3 = datetime.utcnow()
        """)
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 3)


class TestStubMarkerAnalyzer(unittest.TestCase):
    """Test stub marker detection"""
    
    def setUp(self):
        self.analyzer = StubMarkerAnalyzer()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_detects_stub_markers(self):
        """Should detect TODO stub comments"""
        test_file = self.temp_dir / "auto_generated" / "client.js"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("// TODO stub - implement this")
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "stub")
    
    def test_only_scans_generated_files(self):
        """Should only scan generated client files"""
        test_file = self.temp_dir / "normal.py"
        test_file.write_text("# TODO stub")
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 0)


class TestDuplicateFileAnalyzer(unittest.TestCase):
    """Test duplicate file detection"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.analyzer = DuplicateFileAnalyzer(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_detects_duplicates(self):
        """Should detect files with identical content"""
        # Create two files with same content
        file1 = self.temp_dir / "file1.txt"
        file2 = self.temp_dir / "file2.txt"
        
        file1.write_text("This is test content")
        file2.write_text("This is test content")
        
        findings = self.analyzer.scan_repository()
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "duplicate")
        self.assertEqual(len(findings[0].metadata["duplicates"]), 2)
    
    def test_ignores_different_files(self):
        """Should not flag files with different content"""
        file1 = self.temp_dir / "file1.txt"
        file2 = self.temp_dir / "file2.txt"
        
        file1.write_text("Content A")
        file2.write_text("Content B")
        
        findings = self.analyzer.scan_repository()
        
        self.assertEqual(len(findings), 0)
    
    def test_ignores_init_files(self):
        """Should ignore __init__.py duplicates (intentional)"""
        dir1 = self.temp_dir / "pkg1"
        dir2 = self.temp_dir / "pkg2"
        dir1.mkdir()
        dir2.mkdir()
        
        (dir1 / "__init__.py").write_text("")
        (dir2 / "__init__.py").write_text("")
        
        findings = self.analyzer.scan_repository()
        
        # Should not flag __init__.py files as duplicates
        self.assertEqual(len(findings), 0)


class TestDatetimeFixer(unittest.TestCase):
    """Test datetime fixer"""
    
    def setUp(self):
        self.fixer = DatetimeFixer()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_fixes_deprecated_datetime(self):
        """Should replace datetime.utcnow() with datetime.now(UTC)"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("from datetime import datetime\ntimestamp = datetime.utcnow()")
        
        analyzer = DatetimeDeprecatedAnalyzer()
        findings = analyzer.analyze(test_file, test_file.read_text())
        
        success, error = self.fixer.fix(test_file, findings[0])
        
        self.assertTrue(success)
        self.assertIsNone(error)
        
        content = test_file.read_text()
        self.assertIn("datetime.now(UTC)", content)
        self.assertNotIn("datetime.utcnow()", content)
        self.assertIn("from datetime import datetime, UTC", content)


class TestARIEEngine(unittest.TestCase):
    """Test ARIE Engine orchestration"""
    
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.engine = ARIEEngine(repo_root=self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_discover_files(self):
        """Should discover Python files for scanning"""
        # Create test files
        (self.temp_dir / "test1.py").write_text("# test")
        (self.temp_dir / "test2.py").write_text("# test")
        (self.temp_dir / "readme.md").write_text("# test")
        
        files = self.engine.discover()
        
        py_files = [f for f in files if f.suffix == '.py']
        self.assertGreaterEqual(len(py_files), 2)
    
    def test_analyze_finds_issues(self):
        """Should analyze files and find issues"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("timestamp = datetime.utcnow()")
        
        files = self.engine.discover()
        findings = self.engine.analyze(files)
        
        # Should find the deprecated datetime usage
        deprecated = [f for f in findings if f.category == "deprecated"]
        self.assertGreater(len(deprecated), 0)
    
    def test_plan_respects_policy(self):
        """Should create plan respecting policy"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("timestamp = datetime.utcnow()")
        
        files = self.engine.discover()
        findings = self.engine.analyze(files)
        
        # LINT_ONLY should not include any fixes
        plan_lint = self.engine.plan(findings, PolicyType.LINT_ONLY)
        self.assertEqual(len(plan_lint.actions), 0)
        
        # SAFE_EDIT should include deprecated fixes
        plan_safe = self.engine.plan(findings, PolicyType.SAFE_EDIT)
        self.assertGreater(len(plan_safe.actions), 0)
    
    def test_run_pipeline(self):
        """Should execute full pipeline"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text("from datetime import datetime\ntimestamp = datetime.utcnow()")
        
        summary = self.engine.run(
            policy=PolicyType.LINT_ONLY,
            dry_run=True
        )
        
        self.assertIsNotNone(summary)
        self.assertEqual(summary.policy, PolicyType.LINT_ONLY)
        self.assertTrue(summary.dry_run)
        self.assertGreater(summary.findings_count, 0)
    
    def test_rollback_nonexistent_patch(self):
        """Should handle rollback of nonexistent patch"""
        rollback = self.engine.rollback("nonexistent_patch")
        
        self.assertFalse(rollback.success)
        self.assertIsNotNone(rollback.error)


class TestConfigSmellAnalyzer(unittest.TestCase):
    """Test config smell detection"""
    
    def setUp(self):
        self.analyzer = ConfigSmellAnalyzer()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_detects_env_without_default(self):
        """Should detect os.getenv() without default"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text('value = os.getenv("MY_VAR")')
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].category, "config_smell")
    
    def test_ignores_env_with_default(self):
        """Should not flag os.getenv() with default"""
        test_file = self.temp_dir / "test.py"
        test_file.write_text('value = os.getenv("MY_VAR", "default")')
        
        findings = self.analyzer.analyze(test_file, test_file.read_text())
        
        self.assertEqual(len(findings), 0)


if __name__ == '__main__':
    unittest.main()
