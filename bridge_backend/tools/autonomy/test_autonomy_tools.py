"""
Tests for Workflow Failure Resolution Framework

Tests the failure analyzer and PR generator tools.
"""

import pytest
import json
import tempfile
from pathlib import Path

# Import from autonomy package
from bridge_backend.tools.autonomy.failure_analyzer import FailurePatternAnalyzer
from bridge_backend.tools.autonomy.pr_generator import PRGenerator
from bridge_backend.tools.autonomy.failure_patterns import (
    get_pattern, 
    get_all_patterns, 
    is_auto_fixable,
    get_priority
)


class TestFailurePatterns:
    """Test failure pattern definitions."""
    
    def test_get_all_patterns(self):
        """Test getting all patterns."""
        patterns = get_all_patterns()
        assert isinstance(patterns, dict)
        assert len(patterns) > 0
        assert "browser_download_blocked" in patterns
        assert "deprecated_actions" in patterns
    
    def test_get_pattern(self):
        """Test getting a specific pattern."""
        pattern = get_pattern("browser_download_blocked")
        assert pattern is not None
        assert pattern["priority"] == "CRITICAL"
        assert pattern["auto_fixable"] is True
    
    def test_is_auto_fixable(self):
        """Test checking if pattern is auto-fixable."""
        assert is_auto_fixable("browser_download_blocked") is True
        assert is_auto_fixable("forge_auth_failure") is False
    
    def test_get_priority(self):
        """Test getting pattern priority."""
        assert get_priority("browser_download_blocked") == "CRITICAL"
        assert get_priority("deprecated_actions") == "LOW"
        assert get_priority("nonexistent") == "UNKNOWN"


class TestFailurePatternAnalyzer:
    """Test the failure pattern analyzer."""
    
    @pytest.fixture
    def temp_workflow_dir(self):
        """Create a temporary directory with test workflow files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create test workflow with deprecated actions
            workflow1 = tmpdir / "test_workflow1.yml"
            workflow1.write_text("""
name: Test Workflow 1
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-artifact@v3
      - run: npm test
""")
            
            # Create test workflow with browser issues
            workflow2 = tmpdir / "test_workflow2.yml"
            workflow2.write_text("""
name: Test Workflow 2
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright install
      - run: npm test
""")
            
            # Create test workflow with container timeout
            workflow3 = tmpdir / "test_workflow3.yml"
            workflow3.write_text("""
name: Test Workflow 3
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Wait for health check
        run: |
          timeout waiting for container to be healthy
""")
            
            yield tmpdir
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = FailurePatternAnalyzer()
        assert analyzer.stats["total_workflows"] == 0
        assert analyzer.stats["total_issues"] == 0
    
    def test_analyze_workflows(self, temp_workflow_dir):
        """Test analyzing workflows."""
        analyzer = FailurePatternAnalyzer(workflows_dir=str(temp_workflow_dir))
        report = analyzer.analyze_workflows()
        
        assert report["stats"]["total_workflows"] == 3
        assert report["stats"]["total_issues"] > 0
        assert len(report["issues"]) > 0
    
    def test_detect_deprecated_actions(self, temp_workflow_dir):
        """Test detection of deprecated actions."""
        analyzer = FailurePatternAnalyzer(workflows_dir=str(temp_workflow_dir))
        analyzer.analyze_workflows()
        
        # Should detect deprecated upload-artifact@v3
        deprecated_issues = [
            issue for issue in analyzer.issues 
            if issue["pattern"] == "deprecated_actions"
        ]
        assert len(deprecated_issues) > 0
    
    def test_detect_container_timeout(self, temp_workflow_dir):
        """Test detection of container timeout issues."""
        analyzer = FailurePatternAnalyzer(workflows_dir=str(temp_workflow_dir))
        analyzer.analyze_workflows()
        
        # Should detect timeout in workflow3
        timeout_issues = [
            issue for issue in analyzer.issues 
            if issue["pattern"] == "container_health_timeout"
        ]
        assert len(timeout_issues) > 0
    
    def test_save_report(self, temp_workflow_dir):
        """Test saving analysis report."""
        analyzer = FailurePatternAnalyzer(workflows_dir=str(temp_workflow_dir))
        analyzer.analyze_workflows()
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_file = f.name
        
        try:
            analyzer.save_report(output_file=output_file)
            
            # Verify file was created
            assert Path(output_file).exists()
            
            # Verify content
            with open(output_file) as f:
                report = json.load(f)
            
            assert "stats" in report
            assert "issues" in report
            assert "recommendations" in report
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()
    
    def test_recommendations_generation(self, temp_workflow_dir):
        """Test recommendation generation."""
        analyzer = FailurePatternAnalyzer(workflows_dir=str(temp_workflow_dir))
        report = analyzer.analyze_workflows()
        
        recommendations = report["recommendations"]
        assert len(recommendations) > 0
        
        # Recommendations should be sorted by severity
        if len(recommendations) > 1:
            severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
            for i in range(len(recommendations) - 1):
                curr_sev = severity_order.get(recommendations[i]["severity"], 99)
                next_sev = severity_order.get(recommendations[i + 1]["severity"], 99)
                assert curr_sev <= next_sev


class TestPRGenerator:
    """Test the PR generator."""
    
    @pytest.fixture
    def temp_fix_plan(self):
        """Create a temporary fix plan."""
        plan = {
            "timestamp": "2025-11-04T00:00:00Z",
            "total_issues": 2,
            "issues": [
                {
                    "file": ".github/workflows/test.yml",
                    "issue_type": "deprecated_actions",
                    "severity": "LOW",
                    "auto_fixable": True,
                    "description": "Uses deprecated actions"
                },
                {
                    "file": ".github/workflows/test2.yml",
                    "issue_type": "browser_config",
                    "severity": "MEDIUM",
                    "auto_fixable": True,
                    "description": "Missing browser config"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(plan, f)
            plan_file = f.name
        
        yield plan_file
        
        if Path(plan_file).exists():
            Path(plan_file).unlink()
    
    def test_generator_initialization(self, temp_fix_plan):
        """Test PR generator initialization."""
        generator = PRGenerator(plan_file=temp_fix_plan)
        assert generator.plan_file.exists()
        assert len(generator.fixes_applied) == 0
        assert len(generator.fixes_failed) == 0
    
    def test_load_plan(self, temp_fix_plan):
        """Test loading fix plan."""
        generator = PRGenerator(plan_file=temp_fix_plan)
        plan = generator.load_plan()
        
        assert plan["total_issues"] == 2
        assert len(plan["issues"]) == 2
    
    def test_generate_fixes_dry_run(self, temp_fix_plan):
        """Test generating fixes in dry-run mode."""
        generator = PRGenerator(plan_file=temp_fix_plan)
        summary = generator.generate_fixes(dry_run=True)
        
        assert "fixes_applied" in summary
        assert "fixes_failed" in summary
    
    def test_fix_deprecated_actions(self):
        """Test fixing deprecated actions."""
        generator = PRGenerator(plan_file="dummy.json")
        
        content = """
        steps:
          - uses: actions/upload-artifact@v3
          - uses: actions/download-artifact@v3
        """
        
        modified, changed = generator._fix_deprecated_actions(content)
        
        assert changed is True
        assert "actions/upload-artifact@v4" in modified
        assert "actions/download-artifact@v4" in modified
        assert "actions/upload-artifact@v3" not in modified
    
    def test_generate_recommendations(self, temp_fix_plan):
        """Test generating recommendations."""
        generator = PRGenerator(plan_file=temp_fix_plan)
        generator.generate_fixes(dry_run=True)
        
        recommendations = generator.generate_recommendations()
        
        assert "Workflow Fix Recommendations" in recommendations
        assert "GitHub Secrets" in recommendations
    
    def test_save_summary(self, temp_fix_plan):
        """Test saving fix summary."""
        generator = PRGenerator(plan_file=temp_fix_plan)
        generator.generate_fixes(dry_run=True)
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            output_file = f.name
        
        try:
            generator.save_summary(output_file=output_file)
            
            # Verify file was created
            assert Path(output_file).exists()
            
            # Verify content
            with open(output_file) as f:
                summary = json.load(f)
            
            assert "fixes_applied" in summary
            assert "fixes_failed" in summary
        finally:
            if Path(output_file).exists():
                Path(output_file).unlink()


def test_integration():
    """Integration test: run analyzer and generate fixes."""
    # This is a lightweight integration test
    # In production, you'd want more comprehensive testing
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create a test workflow
        workflow_dir = tmpdir / "workflows"
        workflow_dir.mkdir()
        
        workflow = workflow_dir / "test.yml"
        workflow.write_text("""
name: Test
on: [push]
jobs:
  test:
    steps:
      - uses: actions/upload-artifact@v3
""")
        
        # Run analyzer
        analyzer = FailurePatternAnalyzer(workflows_dir=str(workflow_dir))
        report = analyzer.analyze_workflows()
        
        # Verify issues found
        assert report["stats"]["total_issues"] > 0
        
        # Create fix plan
        fix_plan_file = tmpdir / "fix_plan.json"
        with open(fix_plan_file, "w") as f:
            json.dump({
                "timestamp": report["timestamp"],
                "total_issues": report["stats"]["total_issues"],
                "issues": report["issues"]
            }, f)
        
        # Run PR generator
        generator = PRGenerator(plan_file=str(fix_plan_file))
        summary = generator.generate_fixes(dry_run=True)
        
        # Verify summary
        assert "fixes_applied" in summary
        assert "fixes_failed" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
