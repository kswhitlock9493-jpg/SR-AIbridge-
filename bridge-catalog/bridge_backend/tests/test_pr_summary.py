"""
Tests for PR Summary Generator
v1.9.7k - Umbra Unified Triage Mesh
"""

import pytest
import json
import tempfile
from pathlib import Path

from bridge_backend.cli.selftest_summary import (
    load_json_report,
    calculate_health_score,
    generate_markdown_summary,
    generate_json_summary
)


class TestPRSummaryGenerator:
    """Test PR health summary generation"""
    
    def test_load_json_report_valid(self):
        """Test loading a valid JSON report"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
        
        try:
            report = load_json_report(temp_path)
            assert report == {"test": "data"}
        finally:
            Path(temp_path).unlink()
    
    def test_load_json_report_missing(self):
        """Test loading a missing file"""
        report = load_json_report("/nonexistent/file.json")
        assert report == {}
    
    def test_calculate_health_score_perfect(self):
        """Test health score calculation for perfect health"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 100,
            "failed_tests": 0,
            "engines_total": 31,
            "engines_active": 31
        }
        
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        assert score == 100
    
    def test_calculate_health_score_with_criticals(self):
        """Test health score with critical issues"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 100,
            "engines_total": 31,
            "engines_active": 31
        }
        
        umbra = {
            "critical_count": 2,
            "warning_count": 1,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        # Should have deductions for criticals and warnings
        assert score < 100
        assert score >= 0
    
    def test_calculate_health_score_with_failed_tests(self):
        """Test health score with failed tests"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 80,
            "failed_tests": 20,
            "engines_total": 31,
            "engines_active": 31
        }
        
        umbra = {
            "critical_count": 0,
            "warning_count": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        # Should be around 80% due to test failures
        assert 70 <= score <= 90
    
    def test_calculate_health_score_with_heal_failures(self):
        """Test health score with heal failures"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 100,
            "engines_total": 31,
            "engines_active": 31
        }
        
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 5,
            "tickets_failed": 5
        }
        
        score = calculate_health_score(selftest, umbra)
        # Should have some deduction for heal failures
        assert score < 100
        assert score >= 70
    
    def test_generate_markdown_summary_excellent(self):
        """Test markdown generation for excellent health"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 100,
            "engines_total": 31,
            "engines_active": 31
        }
        
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_opened": 0
        }
        
        md = generate_markdown_summary(selftest, umbra, 100)
        
        assert "### 🤖 Bridge Health: 100%" in md
        assert "✅ **Excellent**" in md
        assert "Passed: 100" in md
        assert "No incidents detected" in md
    
    def test_generate_markdown_summary_with_issues(self):
        """Test markdown generation with issues"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 90,
            "failed_tests": 10,
            "engines_total": 31,
            "engines_active": 30
        }
        
        umbra = {
            "critical_count": 2,
            "warning_count": 3,
            "tickets_opened": 5,
            "heal_plans_generated": 5,
            "tickets_healed": 3
        }
        
        md = generate_markdown_summary(selftest, umbra, 75)
        
        assert "### 🤖 Bridge Health: 75%" in md
        assert "Failed: 10" in md
        assert "Critical incidents: 2" in md
        assert "Warnings: 3" in md
        assert "Auto-heals applied: 3" in md
    
    def test_generate_json_summary(self):
        """Test JSON summary generation"""
        selftest = {
            "total_tests": 100,
            "passed_tests": 95,
            "failed_tests": 5,
            "engines_total": 31,
            "engines_active": 30
        }
        
        umbra = {
            "critical_count": 1,
            "warning_count": 2,
            "tickets_opened": 3,
            "tickets_healed": 2,
            "tickets_failed": 1,
            "heal_plans_generated": 3,
            "heal_plans_applied": 2,
            "rollbacks": 0
        }
        
        json_summary = generate_json_summary(selftest, umbra, 85)
        
        assert json_summary["health_score"] == 85
        assert json_summary["selftest"]["total_tests"] == 100
        assert json_summary["selftest"]["passed_tests"] == 95
        assert json_summary["umbra"]["critical_count"] == 1
        assert json_summary["umbra"]["tickets_healed"] == 2
        assert "timestamp" in json_summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
