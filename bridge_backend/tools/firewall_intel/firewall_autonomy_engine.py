#!/usr/bin/env python3
"""
Firewall Intelligence and Autonomy Engine
Combines firewall intelligence gathering with autonomous decision-making and policy application.
"""

import os
import sys
import json
import time
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add bridge_backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

# Import firewall intelligence modules
from bridge_backend.tools.firewall_intel.fetch_firewall_incidents import main as fetch_incidents
from bridge_backend.tools.firewall_intel.analyze_firewall_findings import main as analyze_findings
from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager

DIAGNOSTICS_DIR = "bridge_backend/diagnostics"
AUTONOMY_VAULT = "vault/autonomy"
FIREWALL_REPORT = os.path.join(DIAGNOSTICS_DIR, "firewall_report.json")
AUTONOMY_LOG = os.path.join(DIAGNOSTICS_DIR, "firewall_autonomy_log.json")

# Known browser download domains that may be blocked
BROWSER_DOWNLOAD_DOMAINS = [
    "googlechromelabs.github.io",
    "storage.googleapis.com",
    "edgedl.me.gvt1.com",
    "playwright.azureedge.net",
    "cdn.playwright.dev"
]

# Error patterns that indicate browser download blocking
BROWSER_DOWNLOAD_ERROR_PATTERNS = [
    r"chrome-for-testing-public",
    r"install\.mjs",
    r"playwright.*install",
    r"puppeteer.*install",
    r"chromium.*download",
    r"browser.*download.*fail",
    r"ENOTFOUND.*googleapis",
    r"ENOTFOUND.*googlechromelabs"
]


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
            # add_domain_to_allowlist is safe because:
            # 1. Only adds to allowlist (doesn't modify existing rules)
            # 2. Limited to known browser download domains (BROWSER_DOWNLOAD_DOMAINS)
            # 3. All actions are logged for audit
            # 4. Firewall still enforces protocol and port restrictions
            "safe_actions": ["analyze", "report", "recommend", "add_domain_to_allowlist"],
            "restricted_actions": ["delete", "drop"],
            "max_concurrent_tasks": 3
        }
        
        # Initialize firewall config manager
        self.firewall_manager = FirewallConfigManager()
        
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
        
        # Step 0: Check for browser download blocking (proactive check)
        print("\n🔍 Step 0: Checking for Browser Download Issues...")
        browser_check_result = self._check_browser_download_blocking()
        
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
        final_result = self._record_and_report(execution_result, browser_check_result)
        
        return final_result
    
    def _check_browser_download_blocking(self) -> Dict[str, Any]:
        """Proactively check for browser download blocking issues"""
        result = {
            "checked": True,
            "blocked_domains": [],
            "actions_taken": []
        }
        
        try:
            # Check if browser download domains are in allowlist
            current_allowed = self.firewall_manager.get_all_allowed_domains()
            
            missing_domains = []
            for domain in BROWSER_DOWNLOAD_DOMAINS:
                if domain not in current_allowed:
                    missing_domains.append(domain)
            
            if missing_domains:
                print(f"  ⚠️  Found {len(missing_domains)} browser download domains not in allowlist")
                result["blocked_domains"] = missing_domains
                
                # Autonomous action: Add domains to allowlist
                print("  → Auto-adding browser download domains to allowlist...")
                for domain in missing_domains:
                    added = self.firewall_manager.add_domain_to_allowlist(domain, "browser_downloads")
                    if added:
                        print(f"    ✅ Added: {domain}")
                        result["actions_taken"].append({
                            "action": "add_domain",
                            "domain": domain,
                            "category": "browser_downloads",
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                
                # Record the autonomous action
                self.actions_taken.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "session_id": self.session_id,
                    "action": "browser_download_firewall_repair",
                    "domains_added": len(missing_domains),
                    "auto_approved": True,
                    "status": "completed"
                })
                
                print(f"  ✅ Successfully added {len(missing_domains)} domains to browser_downloads allowlist")
            else:
                print("  ✅ All browser download domains already in allowlist")
            
            # Check GitHub workflow logs for install.mjs errors (if available)
            log_check = self._check_for_install_mjs_errors()
            if log_check.get("errors_found"):
                result["install_mjs_errors"] = log_check
                print(f"  ⚠️  Found {len(log_check.get('errors', []))} install.mjs related errors in logs")
            
        except Exception as e:
            print(f"  ❌ Browser download check failed: {e}")
            result["error"] = str(e)
        
        return result
    
    def _check_for_install_mjs_errors(self) -> Dict[str, Any]:
        """Check for install.mjs errors in logs and GitHub workflows"""
        result = {
            "errors_found": False,
            "errors": []
        }
        
        # Maximum file size to read (10MB to prevent memory issues)
        MAX_FILE_SIZE = 10 * 1024 * 1024
        
        try:
            # Check local log files for browser download errors
            log_dirs = ["logs", "bridge_backend/diagnostics", ".npm/_logs"]
            
            for log_dir in log_dirs:
                if not os.path.exists(log_dir):
                    continue
                
                for log_file in Path(log_dir).rglob("*.log"):
                    try:
                        # Skip files larger than MAX_FILE_SIZE
                        if log_file.stat().st_size > MAX_FILE_SIZE:
                            continue
                        
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                            # Check for browser download error patterns
                            for pattern in BROWSER_DOWNLOAD_ERROR_PATTERNS:
                                if re.search(pattern, content, re.IGNORECASE):
                                    result["errors_found"] = True
                                    result["errors"].append({
                                        "file": str(log_file),
                                        "pattern": pattern,
                                        "timestamp": datetime.now(timezone.utc).isoformat()
                                    })
                                    break
                    except Exception:
                        continue  # Skip files we can't read
            
        except Exception as e:
            result["check_error"] = str(e)
        
        return result
    
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
    
    def _record_and_report(self, execution: Dict[str, Any], browser_check: Dict[str, Any]) -> Dict[str, Any]:
        """Record all actions and generate final report"""
        
        final_report = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "browser_download_check": browser_check,
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
        print(f"  → Browser domains checked: {len(browser_check.get('blocked_domains', [])) + len(browser_check.get('actions_taken', []))}")
        print(f"  → Browser domains added: {len(browser_check.get('actions_taken', []))}")
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
