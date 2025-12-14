#!/usr/bin/env python3
"""
Tests for the Firewall Intelligence and Autonomy Engine
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_backend.tools.firewall_intel.firewall_autonomy_engine import FirewallAutonomyEngine


def test_engine_initialization():
    """Test that the engine initializes with proper guardrails"""
    engine = FirewallAutonomyEngine()
    
    assert engine.session_id is not None
    assert engine.guardrails is not None
    assert engine.guardrails["max_severity_for_auto_apply"] == "medium"
    assert engine.guardrails["require_approval_for_high"] is True
    assert len(engine.actions_taken) == 0


def test_is_within_guardrails():
    """Test guardrail checking logic"""
    engine = FirewallAutonomyEngine()
    
    # None and low should be within guardrails (max is medium)
    assert engine._is_within_guardrails("none") is True
    assert engine._is_within_guardrails("low") is True
    assert engine._is_within_guardrails("medium") is True
    
    # High should exceed guardrails
    assert engine._is_within_guardrails("high") is False
    assert engine._is_within_guardrails("critical") is False


def test_analyze_and_decide_no_issues():
    """Test decision making when no issues are detected"""
    engine = FirewallAutonomyEngine()
    
    intelligence = {
        "success": True,
        "report": {
            "summary": {
                "severity": "none",
                "issues_detected": 0,
                "firewall_signatures": []
            }
        }
    }
    
    decision = engine._analyze_and_decide(intelligence)
    
    assert decision["decision"] == "monitor"
    assert decision["reason"] == "no_issues_detected"
    assert len(decision["actions"]) == 0


def test_analyze_and_decide_low_severity():
    """Test decision making for low severity issues (within guardrails)"""
    engine = FirewallAutonomyEngine()
    
    intelligence = {
        "success": True,
        "report": {
            "summary": {
                "severity": "low",
                "issues_detected": 2,
                "firewall_signatures": ["ETIMEDOUT"]
            }
        }
    }
    
    decision = engine._analyze_and_decide(intelligence)
    
    assert decision["decision"] == "auto_apply"
    assert decision["reason"] == "within_safety_guardrails"
    assert len(decision["actions"]) == 1
    assert decision["actions"][0]["type"] == "apply_network_policies"
    assert decision["actions"][0]["auto_approved"] is True


def test_analyze_and_decide_high_severity():
    """Test decision making for high severity issues (requires approval)"""
    engine = FirewallAutonomyEngine()
    
    intelligence = {
        "success": True,
        "report": {
            "summary": {
                "severity": "high",
                "issues_detected": 5,
                "firewall_signatures": ["ENOTFOUND", "E404", "ECONNRESET"]
            }
        }
    }
    
    decision = engine._analyze_and_decide(intelligence)
    
    assert decision["decision"] == "escalate"
    assert decision["reason"] == "high_severity_requires_approval"
    assert len(decision["actions"]) == 1
    assert decision["actions"][0]["type"] == "notify_operators"
    assert decision["actions"][0]["requires_approval"] is True


def test_execute_autonomous_actions_apply_policies():
    """Test executing autonomous policy application"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Patch the vault directory
        vault_dir = os.path.join(tmpdir, "vault", "autonomy")
        os.makedirs(vault_dir, exist_ok=True)
        
        with patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.AUTONOMY_VAULT', vault_dir):
            engine = FirewallAutonomyEngine()
            
            decisions = {
                "actions": [
                    {
                        "type": "apply_network_policies",
                        "severity": "low",
                        "auto_approved": True
                    }
                ]
            }
            
            result = engine._execute_autonomous_actions(decisions)
            
            assert len(result["executed"]) == 1
            assert len(result["failed"]) == 0
            assert len(engine.actions_taken) == 1
            
            # Verify action was logged to vault
            vault_files = os.listdir(vault_dir)
            assert len(vault_files) == 1
            assert vault_files[0].startswith("firewall_action_")


def test_execute_autonomous_actions_notify():
    """Test executing notification action"""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_dir = os.path.join(tmpdir, "vault", "autonomy")
        os.makedirs(vault_dir, exist_ok=True)
        
        with patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.AUTONOMY_VAULT', vault_dir):
            engine = FirewallAutonomyEngine()
            
            decisions = {
                "actions": [
                    {
                        "type": "notify_operators",
                        "severity": "high",
                        "requires_approval": True
                    }
                ]
            }
            
            result = engine._execute_autonomous_actions(decisions)
            
            assert len(result["executed"]) == 1
            assert len(result["failed"]) == 0
            assert len(engine.actions_taken) == 1
            
            # Verify notification was logged to vault
            vault_files = os.listdir(vault_dir)
            assert len(vault_files) == 1
            assert vault_files[0].startswith("firewall_notification_")


def test_record_and_report():
    """Test final reporting and logging"""
    with tempfile.TemporaryDirectory() as tmpdir:
        diagnostics_dir = os.path.join(tmpdir, "diagnostics")
        os.makedirs(diagnostics_dir, exist_ok=True)
        autonomy_log = os.path.join(diagnostics_dir, "firewall_autonomy_log.json")
        
        with patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.AUTONOMY_LOG', autonomy_log):
            engine = FirewallAutonomyEngine()
            
            execution = {
                "executed": [{"type": "apply_network_policies"}],
                "skipped": [],
                "failed": []
            }
            
            browser_check = {
                "checked": True,
                "blocked_domains": [],
                "actions_taken": []
            }
            
            report = engine._record_and_report(execution, browser_check)
            
            assert report["session_id"] == engine.session_id
            assert report["execution_summary"]["actions_executed"] == 1
            assert report["execution_summary"]["actions_skipped"] == 0
            assert report["execution_summary"]["actions_failed"] == 0
            assert "guardrails_enforced" in report
            assert "browser_download_check" in report
            
            # Verify log file was created
            assert os.path.exists(autonomy_log)
            
            # Verify log contents
            with open(autonomy_log, 'r') as f:
                logged_report = json.load(f)
                assert logged_report["session_id"] == engine.session_id



def test_full_integration_no_issues():
    """Test full engine run with no issues detected"""
    with tempfile.TemporaryDirectory() as tmpdir:
        diagnostics_dir = os.path.join(tmpdir, "diagnostics")
        vault_dir = os.path.join(tmpdir, "vault", "autonomy")
        os.makedirs(diagnostics_dir, exist_ok=True)
        os.makedirs(vault_dir, exist_ok=True)
        
        # Create a mock firewall report
        firewall_report = os.path.join(diagnostics_dir, "firewall_report.json")
        with open(firewall_report, 'w') as f:
            json.dump({
                "summary": {
                    "severity": "none",
                    "issues_detected": 0,
                    "firewall_signatures": []
                }
            }, f)
        
        autonomy_log = os.path.join(diagnostics_dir, "firewall_autonomy_log.json")
        
        with patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.DIAGNOSTICS_DIR', diagnostics_dir), \
             patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.AUTONOMY_VAULT', vault_dir), \
             patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.FIREWALL_REPORT', firewall_report), \
             patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.AUTONOMY_LOG', autonomy_log), \
             patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.fetch_incidents'), \
             patch('bridge_backend.tools.firewall_intel.firewall_autonomy_engine.analyze_findings'):
            
            engine = FirewallAutonomyEngine()
            result = engine.run()
            
            assert result is not None
            assert result["execution_summary"]["actions_executed"] == 0
            assert os.path.exists(autonomy_log)


if __name__ == "__main__":
    print("Running Firewall Autonomy Engine tests...")
    
    test_engine_initialization()
    print("✅ test_engine_initialization")
    
    test_is_within_guardrails()
    print("✅ test_is_within_guardrails")
    
    test_analyze_and_decide_no_issues()
    print("✅ test_analyze_and_decide_no_issues")
    
    test_analyze_and_decide_low_severity()
    print("✅ test_analyze_and_decide_low_severity")
    
    test_analyze_and_decide_high_severity()
    print("✅ test_analyze_and_decide_high_severity")
    
    test_execute_autonomous_actions_apply_policies()
    print("✅ test_execute_autonomous_actions_apply_policies")
    
    test_execute_autonomous_actions_notify()
    print("✅ test_execute_autonomous_actions_notify")
    
    test_record_and_report()
    print("✅ test_record_and_report")
    
    test_full_integration_no_issues()
    print("✅ test_full_integration_no_issues")
    
    print("\n🎉 All Firewall Autonomy Engine tests passed!")
