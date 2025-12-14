"""
Tests for Bridge Health Record System
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from bridge_backend.metrics.health_record import (
    load_json_report,
    calculate_health_score,
    aggregate_health_record,
    generate_markdown_record,
    write_health_history,
    compress_old_records
)


class TestLoadJsonReport:
    """Test JSON report loading"""
    
    def test_load_valid_report(self):
        """Test loading valid JSON report"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "data"}, f)
            temp_path = f.name
        
        try:
            result = load_json_report(temp_path)
            assert result == {"test": "data"}
        finally:
            os.unlink(temp_path)
    
    def test_load_missing_report(self):
        """Test loading non-existent report"""
        result = load_json_report("/nonexistent/file.json")
        assert result == {}
    
    def test_load_invalid_json(self):
        """Test loading invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = f.name
        
        try:
            result = load_json_report(temp_path)
            assert result == {}
        finally:
            os.unlink(temp_path)


class TestCalculateHealthScore:
    """Test health score calculation"""
    
    def test_perfect_score(self):
        """Test perfect health score (100%)"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 10
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        assert score == 70  # 50 (tests) + 20 (no heal attempts)
    
    def test_failing_tests(self):
        """Test with failing tests"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 5
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        assert score == 45  # 50% pass rate = 25 points, + 20 heal points
    
    def test_critical_issues(self):
        """Test with critical issues"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 10
        }
        umbra = {
            "critical_count": 2,
            "warning_count": 0,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        assert score == 50  # 50 (tests) - 20 (2 criticals * 10) + 20 (heals) = 50
    
    def test_heal_failures(self):
        """Test with heal failures"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 10
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 1,
            "tickets_failed": 1
        }
        
        score = calculate_health_score(selftest, umbra)
        assert score == 60  # 50 (tests) + 10 (50% heal rate)
    
    def test_no_tests(self):
        """Test with no tests"""
        selftest = {
            "total_tests": 0,
            "passed_tests": 0
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        score = calculate_health_score(selftest, umbra)
        assert score == 70  # 50 (neutral) + 20 (no heals)


class TestAggregateHealthRecord:
    """Test health record aggregation"""
    
    def test_aggregate_basic_record(self):
        """Test basic health record aggregation"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 10,
            "failed_tests": 0,
            "engines_total": 31,
            "engines_active": 31
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_opened": 0,
            "tickets_healed": 0,
            "tickets_failed": 0,
            "heal_plans_generated": 0,
            "heal_plans_applied": 0,
            "rollbacks": 0
        }
        
        record = aggregate_health_record(selftest, umbra)
        
        assert record["bridge_health_score"] == 70  # 50 (tests) + 20 (no heals)
        assert record["status"] == "critical"  # < 80
        assert record["truth_certified"] is True
        assert record["auto_heals"] == 0
        assert "timestamp" in record
        assert record["selftest"]["total_tests"] == 10
        assert record["umbra"]["critical_count"] == 0
    
    def test_aggregate_warning_status(self):
        """Test warning status aggregation"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 9,
            "failed_tests": 1,
            "engines_total": 31,
            "engines_active": 31
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 1,
            "tickets_healed": 0,
            "tickets_failed": 0
        }
        
        record = aggregate_health_record(selftest, umbra)
        
        # 90% pass rate = 45 points, -3 for warning, +20 for no heal attempts = 62
        assert record["bridge_health_score"] == 62
        assert record["status"] == "critical"  # < 80
    
    def test_aggregate_with_heals(self):
        """Test aggregation with auto-heals"""
        selftest = {
            "total_tests": 10,
            "passed_tests": 10
        }
        umbra = {
            "critical_count": 0,
            "warning_count": 0,
            "tickets_healed": 5,
            "tickets_failed": 0
        }
        
        record = aggregate_health_record(selftest, umbra)
        
        assert record["auto_heals"] == 5
        assert record["umbra"]["tickets_healed"] == 5


class TestGenerateMarkdownRecord:
    """Test Markdown record generation"""
    
    def test_generate_passing_markdown(self):
        """Test Markdown for passing status"""
        record = {
            "bridge_health_score": 100,
            "status": "passing",
            "truth_certified": True,
            "auto_heals": 0,
            "timestamp": "2025-10-13T00:00:00Z",
            "selftest": {
                "total_tests": 10,
                "passed_tests": 10,
                "failed_tests": 0,
                "engines_total": 31,
                "engines_active": 31
            },
            "umbra": {
                "critical_count": 0,
                "warning_count": 0,
                "tickets_opened": 0,
                "tickets_healed": 0,
                "heal_plans_generated": 0,
                "rollbacks": 0
            }
        }
        
        md = generate_markdown_record(record)
        
        assert "🟢" in md
        assert "100%" in md
        assert "Passing" in md
        assert "✅ Yes" in md
        assert "Self-Test Results" in md
        assert "Umbra Triage" in md
    
    def test_generate_critical_markdown(self):
        """Test Markdown for critical status"""
        record = {
            "bridge_health_score": 50,
            "status": "critical",
            "truth_certified": False,
            "auto_heals": 3,
            "timestamp": "2025-10-13T00:00:00Z",
            "selftest": {
                "total_tests": 10,
                "passed_tests": 5,
                "failed_tests": 5,
                "engines_total": 31,
                "engines_active": 28
            },
            "umbra": {
                "critical_count": 2,
                "warning_count": 5,
                "tickets_opened": 7,
                "tickets_healed": 3,
                "heal_plans_generated": 5,
                "rollbacks": 1
            }
        }
        
        md = generate_markdown_record(record)
        
        assert "🔴" in md
        assert "50%" in md
        assert "Critical" in md
        assert "❌ No" in md
        assert "3" in md  # auto-heals


class TestWriteHealthHistory:
    """Test health history writing"""
    
    def test_write_history(self):
        """Test writing health history"""
        with tempfile.TemporaryDirectory() as tmpdir:
            record = {
                "bridge_health_score": 100,
                "status": "passing",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            history_file, latest_file = write_health_history(record, tmpdir)
            
            # Check files exist
            assert history_file.exists()
            assert latest_file.exists()
            
            # Check latest.json content
            with open(latest_file) as f:
                loaded = json.load(f)
                assert loaded["bridge_health_score"] == 100
            
            # Check timestamped file content
            with open(history_file) as f:
                loaded = json.load(f)
                assert loaded["bridge_health_score"] == 100


class TestCompressOldRecords:
    """Test old record compression"""
    
    def test_no_compression_new_files(self):
        """Test that new files are not compressed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a recent file
            recent_file = Path(tmpdir) / "health_20251013_000000.json"
            with open(recent_file, 'w') as f:
                json.dump({"test": "data"}, f)
            
            compress_old_records(tmpdir)
            
            # File should still exist and not be compressed
            assert recent_file.exists()
            assert not Path(f"{recent_file}.gz").exists()
    
    def test_compress_old_files(self):
        """Test that old files are compressed"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an old file (8 days old)
            old_file = Path(tmpdir) / "health_20251001_000000.json"
            with open(old_file, 'w') as f:
                json.dump({"test": "data"}, f)
            
            # Set modification time to 8 days ago
            old_time = (datetime.now(timezone.utc) - timedelta(days=8)).timestamp()
            os.utime(old_file, (old_time, old_time))
            
            compress_old_records(tmpdir)
            
            # Original file should be deleted, compressed version should exist
            assert not old_file.exists()
            assert Path(f"{old_file}.gz").exists()
    
    def test_delete_very_old_files(self):
        """Test that very old files are deleted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a very old file (100 days old)
            very_old_file = Path(tmpdir) / "health_20250701_000000.json"
            with open(very_old_file, 'w') as f:
                json.dump({"test": "data"}, f)
            
            # Set modification time to 100 days ago
            very_old_time = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
            os.utime(very_old_file, (very_old_time, very_old_time))
            
            compress_old_records(tmpdir)
            
            # File should be deleted
            assert not very_old_file.exists()
            assert not Path(f"{very_old_file}.gz").exists()
