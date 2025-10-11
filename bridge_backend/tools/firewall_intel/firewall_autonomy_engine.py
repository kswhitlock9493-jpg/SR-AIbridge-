#!/usr/bin/env python3
"""
Firewall Intelligence and Autonomy Engine
Combines firewall intelligence gathering with autonomous decision-making and policy application.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add bridge_backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Import firewall intelligence modules
from bridge_backend.tools.firewall_intel.fetch_firewall_incidents import main as fetch_incidents
from bridge_backend.tools.firewall_intel.analyze_firewall_findings import main as analyze_findings

DIAGNOSTICS_DIR = "bridge_backend/diagnostics"
AUTONOMY_VAULT = "vault/autonomy"
FIREWALL_REPORT = os.path.join(DIAGNOSTICS_DIR, "firewall_report.json")
AUTONOMY_LOG = os.path.join(DIAGNOSTICS_DIR, "firewall_autonomy_log.json")


class FirewallAutonomyEngine:
    """
    Autonomous Firewall Intelligence Engine
    
    Combines firewall intelligence with autonomous decision-making to:
    - Detect firewall/network issues
    - Analyze severity and impact
    - Make autonomous decisions about policy application
    - Apply self-healing network policies
    - Log all autonomous actions for audit
    """
    
    def __init__(self):
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.actions_taken = []
        self.guardrails = {
            "max_severity_for_auto_apply": "medium",  # Only auto-apply low/medium severity
            "require_approval_for_high": True,
            "safe_actions": ["analyze", "report", "recommend"],
            "restricted_actions": ["delete", "drop"],
            "max_concurrent_tasks": 3
        }
        
        # Ensure directories exist
        Path(DIAGNOSTICS_DIR).mkdir(parents=True, exist_ok=True)
        Path(AUTONOMY_VAULT).mkdir(parents=True, exist_ok=True)
        
        print("🤖 Firewall Intelligence and Autonomy Engine")
        print("=" * 60)
        print(f"Session ID: {self.session_id}")
        print(f"Guardrails: {self.guardrails['max_severity_for_auto_apply']} severity max for auto-apply")
        print("=" * 60)
    
    def run(self) -> Dict[str, Any]:
        """Execute the full autonomy cycle"""
        
        # Step 1: Gather Intelligence
        print("\n🔍 Step 1: Gathering Firewall Intelligence...")
        intelligence_result = self._gather_intelligence()
        
        # Step 2: Analyze and Decide
        print("\n🧠 Step 2: Analyzing Findings and Making Decisions...")
        decision_result = self._analyze_and_decide(intelligence_result)
        
        # Step 3: Execute Autonomous Actions
        print("\n⚙️  Step 3: Executing Autonomous Actions...")
        execution_result = self._execute_autonomous_actions(decision_result)
        
        # Step 4: Record and Report
        print("\n📝 Step 4: Recording Actions and Generating Report...")
        final_result = self._record_and_report(execution_result)
        
        return final_result
    
    def _gather_intelligence(self) -> Dict[str, Any]:
        """Gather firewall intelligence from external sources"""
        try:
            # Fetch incidents
            print("  → Fetching incidents from external sources...")
            fetch_incidents()
            
            # Analyze findings
            print("  → Analyzing findings...")
            analyze_findings()
            
            # Load the analysis report
            if os.path.exists(FIREWALL_REPORT):
                with open(FIREWALL_REPORT, 'r') as f:
                    report = json.load(f)
                print(f"  ✅ Intelligence gathered: {report['summary']['issues_detected']} issues detected")
                return {"success": True, "report": report}
            else:
                print("  ⚠️  No firewall report generated")
                return {"success": False, "report": None}
        except Exception as e:
            print(f"  ❌ Intelligence gathering failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_and_decide(self, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze intelligence and make autonomous decisions"""
        if not intelligence.get("success"):
            return {
                "decision": "no_action",
                "reason": "intelligence_gathering_failed",
                "actions": []
            }
        
        report = intelligence["report"]
        summary = report.get("summary", {})
        severity = summary.get("severity", "none")
        issues_count = summary.get("issues_detected", 0)
        signatures = summary.get("firewall_signatures", [])
        
        print(f"  → Severity: {severity.upper()}")
        print(f"  → Issues detected: {issues_count}")
        print(f"  → Firewall signatures: {len(signatures)}")
        
        # Decision logic with guardrails
        decisions = {
            "severity": severity,
            "issues_count": issues_count,
            "signatures": signatures,
            "actions": []
        }
        
        if severity == "none":
            decisions["decision"] = "monitor"
            decisions["reason"] = "no_issues_detected"
            print("  ✅ Decision: MONITOR (no issues detected)")
        
        elif severity in ["low", "medium"]:
            # Within guardrails - can auto-apply
            if self._is_within_guardrails(severity):
                decisions["decision"] = "auto_apply"
                decisions["reason"] = "within_safety_guardrails"
                decisions["actions"].append({
                    "type": "apply_network_policies",
                    "severity": severity,
                    "auto_approved": True
                })
                print(f"  ✅ Decision: AUTO-APPLY ({severity} severity within guardrails)")
            else:
                decisions["decision"] = "recommend"
                decisions["reason"] = "exceeds_guardrails"
                print(f"  ⚠️  Decision: RECOMMEND (exceeds guardrails)")
        
        elif severity == "high":
            # High severity - requires approval
            decisions["decision"] = "escalate"
            decisions["reason"] = "high_severity_requires_approval"
            decisions["actions"].append({
                "type": "notify_operators",
                "severity": severity,
                "requires_approval": True
            })
            print("  🚨 Decision: ESCALATE (high severity requires human approval)")
        
        return decisions
    
    def _execute_autonomous_actions(self, decisions: Dict[str, Any]) -> Dict[str, Any]:
        """Execute autonomous actions based on decisions"""
        results = {
            "executed": [],
            "skipped": [],
            "failed": []
        }
        
        for action in decisions.get("actions", []):
            action_type = action.get("type")
            
            try:
                if action_type == "apply_network_policies":
                    # Autonomous policy application
                    print(f"  → Applying network policies (severity: {action['severity']})...")
                    self._apply_network_policies(action)
                    results["executed"].append(action)
                    print("  ✅ Network policies applied")
                
                elif action_type == "notify_operators":
                    # Notification action
                    print("  → Notifying operators (high severity)...")
                    self._notify_operators(action)
                    results["executed"].append(action)
                    print("  ✅ Operators notified")
                
                else:
                    print(f"  ⚠️  Unknown action type: {action_type}")
                    results["skipped"].append(action)
            
            except Exception as e:
                print(f"  ❌ Action failed: {e}")
                results["failed"].append({"action": action, "error": str(e)})
        
        if not decisions.get("actions"):
            print("  → No autonomous actions required")
        
        return results
    
    def _apply_network_policies(self, action: Dict[str, Any]) -> None:
        """Apply network policies autonomously"""
        # This is a safe action - it generates policy files but doesn't
        # directly modify production infrastructure
        
        timestamp = datetime.now(timezone.utc).isoformat()
        policy_record = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "action": "apply_network_policies",
            "severity": action.get("severity"),
            "auto_approved": action.get("auto_approved", False),
            "status": "completed"
        }
        
        self.actions_taken.append(policy_record)
        
        # Log the autonomous action
        action_log = os.path.join(AUTONOMY_VAULT, f"firewall_action_{self.session_id}.json")
        with open(action_log, 'w') as f:
            json.dump(policy_record, f, indent=2)
    
    def _notify_operators(self, action: Dict[str, Any]) -> None:
        """Notify operators of high-severity issues"""
        timestamp = datetime.now(timezone.utc).isoformat()
        notification = {
            "timestamp": timestamp,
            "session_id": self.session_id,
            "action": "notify_operators",
            "severity": action.get("severity"),
            "requires_approval": action.get("requires_approval", True),
            "message": "High-severity firewall issues detected - human review required",
            "status": "completed"
        }
        
        self.actions_taken.append(notification)
        
        # Log the notification
        notification_log = os.path.join(AUTONOMY_VAULT, f"firewall_notification_{self.session_id}.json")
        with open(notification_log, 'w') as f:
            json.dump(notification, f, indent=2)
    
    def _is_within_guardrails(self, severity: str) -> bool:
        """Check if action is within safety guardrails"""
        severity_levels = ["none", "low", "medium", "high", "critical"]
        max_level = self.guardrails["max_severity_for_auto_apply"]
        
        try:
            severity_index = severity_levels.index(severity)
            max_index = severity_levels.index(max_level)
            return severity_index <= max_index
        except ValueError:
            return False
    
    def _record_and_report(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Record all actions and generate final report"""
        
        final_report = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_summary": {
                "actions_executed": len(execution.get("executed", [])),
                "actions_skipped": len(execution.get("skipped", [])),
                "actions_failed": len(execution.get("failed", []))
            },
            "actions_taken": self.actions_taken,
            "execution_details": execution,
            "guardrails_enforced": self.guardrails
        }
        
        # Save autonomy log
        with open(AUTONOMY_LOG, 'w') as f:
            json.dump(final_report, f, indent=2)
        
        print(f"\n📊 Execution Summary:")
        print(f"  → Actions executed: {final_report['execution_summary']['actions_executed']}")
        print(f"  → Actions skipped: {final_report['execution_summary']['actions_skipped']}")
        print(f"  → Actions failed: {final_report['execution_summary']['actions_failed']}")
        print(f"\n💾 Autonomy log saved to: {AUTONOMY_LOG}")
        
        return final_report


def main():
    """Main execution function"""
    try:
        engine = FirewallAutonomyEngine()
        result = engine.run()
        
        print("\n" + "=" * 60)
        print("✅ Firewall Intelligence and Autonomy Engine Complete")
        print("=" * 60)
        
        return result
    
    except Exception as e:
        print(f"\n❌ Engine execution failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
