#!/usr/bin/env python3
"""
Test suite for Bridge Self-Test Engine v1.9.7j
"""

import os
import sys
import json
import asyncio
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSelfTestEngine:
    """Test Self-Test Engine core functionality"""
    
    def test_selftest_import(self):
        """Test that selftest modules can be imported"""
        try:
            from bridge_backend.engines.selftest import SelfTestController, AutoHealTrigger
            assert SelfTestController is not None
            assert AutoHealTrigger is not None
        except ImportError as e:
            pytest.fail(f"Failed to import selftest modules: {e}")
    
    def test_selftest_controller_init(self):
        """Test SelfTestController initialization"""
        from bridge_backend.engines.selftest.core import SelfTestController
        
        controller = SelfTestController()
        assert controller is not None
        assert len(controller.engines) == 31
        assert "Truth" in controller.engines
        assert "Chimera" in controller.engines
        assert "EnvRecon" in controller.engines
    
    def test_autoheal_trigger_init(self):
        """Test AutoHealTrigger initialization"""
        from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger
        
        autoheal = AutoHealTrigger()
        assert autoheal is not None
        assert autoheal.max_retry_count == 3
        assert autoheal.retry_delay == 1.0
    
    def test_strategy_selection(self):
        """Test healing strategy selection"""
        from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger
        
        autoheal = AutoHealTrigger()
        
        # Test ARIE strategy
        assert autoheal._select_strategy("EnvRecon") == "arie"
        assert autoheal._select_strategy("EnvScribe") == "arie"
        assert autoheal._select_strategy("Firewall") == "arie"
        
        # Test Chimera strategy
        assert autoheal._select_strategy("Chimera") == "chimera"
        assert autoheal._select_strategy("Leviathan") == "chimera"
        assert autoheal._select_strategy("Federation") == "chimera"
        
        # Test Cascade strategy
        assert autoheal._select_strategy("Truth") == "cascade"
        assert autoheal._select_strategy("Cascade") == "cascade"
        assert autoheal._select_strategy("Genesis") == "cascade"
        assert autoheal._select_strategy("HXO") == "cascade"
        
        # Test generic strategy
        assert autoheal._select_strategy("Parser") == "generic"
    
    @pytest.mark.asyncio
    async def test_run_full_test(self):
        """Test running full self-test"""
        from bridge_backend.engines.selftest.core import SelfTestController
        
        controller = SelfTestController()
        report = await controller.run_full_test(heal=False)
        
        assert report is not None
        assert "test_id" in report
        assert "summary" in report
        assert "events" in report
        assert "timestamp" in report
        
        summary = report["summary"]
        assert summary["engines_total"] == 31
        assert "engines_verified" in summary
        assert "autoheal_invocations" in summary
        assert "status" in summary
        assert summary["status"] in ["Stable", "Degraded", "Failed"]
        assert "runtime_ms" in summary
    
    @pytest.mark.asyncio
    async def test_autoheal_engine(self):
        """Test auto-healing an engine"""
        from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger
        
        autoheal = AutoHealTrigger()
        test_result = {
            "engine": "EnvRecon",
            "action": "health_check",
            "result": "⚠️ auto-heal launched",
            "error": "Configuration drift detected"
        }
        
        heal_result = await autoheal.heal_engine("EnvRecon", test_result)
        
        assert heal_result is not None
        assert "engine" in heal_result
        assert "action" in heal_result
        assert "result" in heal_result
        assert heal_result["engine"] == "EnvRecon"


class TestGenesisIntegration:
    """Test Genesis bus integration"""
    
    def test_selftest_topics_registered(self):
        """Test that selftest topics are registered in Genesis bus"""
        from bridge_backend.genesis.bus import GenesisEventBus
        
        bus = GenesisEventBus()
        
        # Check that selftest topics are in valid topics
        assert "selftest.run.start" in bus._valid_topics
        assert "selftest.run.complete" in bus._valid_topics
        assert "selftest.autoheal.trigger" in bus._valid_topics
        assert "selftest.autoheal.complete" in bus._valid_topics


class TestReportSchema:
    """Test report schema and structure"""
    
    @pytest.mark.asyncio
    async def test_report_structure(self):
        """Test that report has correct structure"""
        from bridge_backend.engines.selftest.core import SelfTestController
        
        controller = SelfTestController()
        report = await controller.run_full_test(heal=False)
        
        # Check required fields
        required_fields = ["test_id", "summary", "events", "timestamp"]
        for field in required_fields:
            assert field in report, f"Missing required field: {field}"
        
        # Check summary structure
        summary_fields = ["engines_total", "engines_verified", "autoheal_invocations", "status", "runtime_ms"]
        for field in summary_fields:
            assert field in report["summary"], f"Missing summary field: {field}"
        
        # Check events structure
        assert isinstance(report["events"], list)
        if len(report["events"]) > 0:
            event = report["events"][0]
            assert "engine" in event
            assert "action" in event
            assert "result" in event
    
    def test_report_logs_directory(self):
        """Test that report logs directory exists"""
        logs_dir = Path(__file__).parent.parent / "bridge_backend" / "logs" / "selftest_reports"
        assert logs_dir.exists(), "Self-test reports directory does not exist"


class TestCLIIntegration:
    """Test CLI integration"""
    
    def test_genesisctl_import(self):
        """Test that genesisctl can be imported"""
        try:
            from bridge_backend.cli import genesisctl
            assert genesisctl is not None
        except ImportError as e:
            pytest.fail(f"Failed to import genesisctl: {e}")
    
    def test_self_test_command_exists(self):
        """Test that self_test_full command exists"""
        from bridge_backend.cli import genesisctl
        
        # Check that the function exists
        assert hasattr(genesisctl, 'cmd_self_test_full')
        assert callable(genesisctl.cmd_self_test_full)


class TestDocumentation:
    """Test documentation completeness"""
    
    def test_selftest_overview_exists(self):
        """Test that SELFTEST_OVERVIEW.md exists"""
        doc_path = Path(__file__).parent.parent / "docs" / "SELFTEST_OVERVIEW.md"
        assert doc_path.exists(), "SELFTEST_OVERVIEW.md does not exist"
    
    def test_selftest_healing_doc_exists(self):
        """Test that SELFTEST_HEALING_AUTOTRIGGER.md exists"""
        doc_path = Path(__file__).parent.parent / "docs" / "SELFTEST_HEALING_AUTOTRIGGER.md"
        assert doc_path.exists(), "SELFTEST_HEALING_AUTOTRIGGER.md does not exist"
    
    def test_selftest_schema_doc_exists(self):
        """Test that SELFTEST_REPORT_SCHEMA.md exists"""
        doc_path = Path(__file__).parent.parent / "docs" / "SELFTEST_REPORT_SCHEMA.md"
        assert doc_path.exists(), "SELFTEST_REPORT_SCHEMA.md does not exist"


class TestWorkflow:
    """Test GitHub Actions workflow"""
    
    def test_workflow_file_exists(self):
        """Test that bridge_selftest.yml workflow exists"""
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "bridge_selftest.yml"
        assert workflow_path.exists(), "bridge_selftest.yml workflow does not exist"
    
    def test_workflow_structure(self):
        """Test that workflow has correct structure"""
        import yaml
        
        workflow_path = Path(__file__).parent.parent / ".github" / "workflows" / "bridge_selftest.yml"
        
        with open(workflow_path) as f:
            workflow = yaml.safe_load(f)
        
        assert "name" in workflow
        assert workflow["name"] == "Bridge Autonomy Diagnostic Pulse (Autonomous Mode)"
        # YAML parses 'on' as True (boolean), so check for True key
        assert True in workflow or "on" in workflow
        assert "jobs" in workflow
        assert "run-bridge-selftest" in workflow["jobs"]


def run_tests():
    """Run all tests"""
    pytest_args = [__file__, "-v", "--tb=short"]
    
    # Add asyncio mode
    pytest_args.extend(["--asyncio-mode=auto"])
    
    exit_code = pytest.main(pytest_args)
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
