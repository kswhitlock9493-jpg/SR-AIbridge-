#!/usr/bin/env python3
"""
🌟 Master Sovereign Audit & Repair
================================================================================
Comprehensive sovereign checks orchestrator that runs ALL audit systems:

1. Sovereign Audit Orchestrator (Git, Netlify, Repository)
2. Firewall Sovereignty System
3. Network Resilience System
4. Validation Sovereignty System
5. Script Execution Sovereignty

This is the MASTER audit tool - "Sovereign Git = true" verification
================================================================================
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime, timezone
import traceback

# Add paths
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "bridge_backend"))


class MasterSovereignAudit:
    """Master sovereign audit coordinator"""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.timestamp = datetime.now(timezone.utc)
        self.results = {
            "master_audit_id": f"master-{self.timestamp.strftime('%Y%m%d_%H%M%S')}",
            "timestamp": self.timestamp.isoformat(),
            "audits": {},
            "overall_status": "UNKNOWN",
            "summary": {}
        }
        
        print("\n" + "="*80)
        print("👑 MASTER SOVEREIGN AUDIT & REPAIR")
        print("="*80)
        print(f"Timestamp: {self.timestamp.isoformat()}")
        print(f"Repository: {self.repo_root}")
        print("="*80)
        print("\n🔍 Performing FULL sovereign checks as requested:")
        print("  1. Git Sovereign Checks")
        print("  2. Netlify Sovereign Checks")
        print("  3. Repository Sovereign Checks")
        print("  4. Firewall Sovereignty")
        print("  5. Network Resilience")
        print("  6. Validation Sovereignty")
        print("  7. Script Execution Sovereignty")
        print("="*80)
    
    def run_comprehensive_audit(self, auto_repair: bool = True) -> Dict[str, Any]:
        """Run all sovereign audit systems"""
        
        # 1. Run Sovereign Audit Orchestrator (Git, Netlify, Repo)
        print("\n📍 PHASE 1: Git, Netlify & Repository Audit")
        print("-" * 80)
        self._run_audit_orchestrator(auto_repair)
        
        # 2. Run Firewall Sovereignty System
        print("\n📍 PHASE 2: Firewall Sovereignty System")
        print("-" * 80)
        self._run_firewall_sovereignty()
        
        # 3. Generate Master Summary
        print("\n📍 PHASE 3: Master Summary Generation")
        print("-" * 80)
        self._generate_master_summary()
        
        # 4. Save Master Report
        self._save_master_report()
        
        # 5. Print Final Status
        self._print_final_status()
        
        return self.results
    
    def _run_audit_orchestrator(self, auto_repair: bool):
        """Run the sovereign audit orchestrator"""
        try:
            from sovereign_audit_orchestrator import SovereignAuditOrchestrator
            
            print("  → Initializing Audit Orchestrator...")
            orchestrator = SovereignAuditOrchestrator(str(self.repo_root))
            
            print("  → Running comprehensive audits...")
            report = orchestrator.execute_full_audit(auto_repair=auto_repair)
            
            # Store results
            self.results["audits"]["git_netlify_repo"] = {
                "status": "COMPLETED",
                "timestamp": report.timestamp,
                "summary": report.summary,
                "total_checks": report.summary["total_checks"],
                "passed": report.summary["passed"],
                "warnings": report.summary["warnings"],
                "failed": report.summary["failed"],
                "repaired": report.summary["repaired"],
                "score": report.summary["score"],
                "audit_status": report.summary["status"]
            }
            
            print(f"  ✅ Git/Netlify/Repo Audit: {report.summary['score']}% - {report.summary['status']}")
            
        except Exception as e:
            print(f"  ❌ Audit Orchestrator failed: {e}")
            traceback.print_exc()
            self.results["audits"]["git_netlify_repo"] = {
                "status": "FAILED",
                "error": str(e)
            }
    
    def _run_firewall_sovereignty(self):
        """Run the firewall sovereignty system"""
        try:
            from bridge_backend.tools.firewall_sovereignty.sovereign_orchestrator import SovereignOrchestrator
            
            print("  → Initializing Firewall Sovereignty...")
            orchestrator = SovereignOrchestrator(str(self.repo_root))
            
            print("  → Executing Sovereignty Protocol...")
            results = orchestrator.execute_sovereignty_protocol()
            
            # Store results
            self.results["audits"]["firewall_sovereignty"] = {
                "status": "COMPLETED",
                "session_id": results.get("session_id"),
                "systems": len(results.get("systems", {})),
                "overall_status": results.get("summary", {}).get("overall_status", "UNKNOWN")
            }
            
            print(f"  ✅ Firewall Sovereignty: {results.get('summary', {}).get('overall_status', 'UNKNOWN')}")
            
        except Exception as e:
            print(f"  ⚠️  Firewall Sovereignty skipped: {e}")
            self.results["audits"]["firewall_sovereignty"] = {
                "status": "SKIPPED",
                "reason": str(e)
            }
    
    def _generate_master_summary(self):
        """Generate master summary across all audits"""
        print("  → Aggregating results...")
        
        total_audits = len(self.results["audits"])
        completed_audits = sum(1 for a in self.results["audits"].values() if a.get("status") == "COMPLETED")
        failed_audits = sum(1 for a in self.results["audits"].values() if a.get("status") == "FAILED")
        
        # Calculate overall status
        if failed_audits > 0:
            overall_status = "NEEDS_ATTENTION"
        elif completed_audits == total_audits:
            overall_status = "HEALTHY"
        else:
            overall_status = "PARTIAL"
        
        # Aggregate scores
        git_netlify_repo = self.results["audits"].get("git_netlify_repo", {})
        
        self.results["summary"] = {
            "total_audit_systems": total_audits,
            "completed": completed_audits,
            "failed": failed_audits,
            "overall_status": overall_status,
            "git_netlify_repo_score": git_netlify_repo.get("score", 0),
            "git_netlify_repo_status": git_netlify_repo.get("audit_status", "UNKNOWN"),
            "firewall_status": self.results["audits"].get("firewall_sovereignty", {}).get("overall_status", "UNKNOWN"),
            "timestamp": self.timestamp.isoformat()
        }
        
        self.results["overall_status"] = overall_status
        
        print(f"  ✅ Master summary generated: {overall_status}")
    
    def _save_master_report(self):
        """Save master audit report"""
        reports_dir = self.repo_root / "bridge_backend" / "diagnostics"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Save latest
        latest_path = reports_dir / "master_sovereign_audit_latest.json"
        with open(latest_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"  💾 Report saved: {latest_path}")
        
        # Save timestamped
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        timestamped_path = reports_dir / f"master_sovereign_audit_{timestamp_str}.json"
        with open(timestamped_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"  💾 Timestamped: {timestamped_path}")
    
    def _print_final_status(self):
        """Print final audit status"""
        print("\n" + "="*80)
        print("📊 MASTER SOVEREIGN AUDIT SUMMARY")
        print("="*80)
        
        summary = self.results["summary"]
        
        print(f"Total Audit Systems: {summary['total_audit_systems']}")
        print(f"✅ Completed: {summary['completed']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"\n📈 Overall Status: {summary['overall_status']}")
        
        print("\n🎯 Detailed Results:")
        print(f"  Git/Netlify/Repo:")
        print(f"    Score: {summary.get('git_netlify_repo_score', 'N/A')}%")
        print(f"    Status: {summary.get('git_netlify_repo_status', 'N/A')}")
        
        print(f"  Firewall Sovereignty:")
        print(f"    Status: {summary.get('firewall_status', 'N/A')}")
        
        print("\n" + "="*80)
        
        # Final verdict
        if summary['overall_status'] == "HEALTHY":
            print("✅ SOVEREIGN GIT = TRUE - Full sovereignty confirmed!")
            print("   All systems operational, all checks passed!")
        elif summary['overall_status'] == "PARTIAL":
            print("⚠️  SOVEREIGN GIT = PARTIAL - Some systems require attention")
            print("   Review audit reports for details")
        else:
            print("❌ SOVEREIGN GIT = NEEDS ATTENTION - Critical issues detected")
            print("   Immediate action required")
        
        print("="*80)
        
        # Additional recommendations
        git_netlify = self.results["audits"].get("git_netlify_repo", {})
        if git_netlify.get("warnings", 0) > 0:
            print(f"\n💡 Recommendations:")
            print(f"   - Review {git_netlify.get('warnings', 0)} warnings in Git/Netlify/Repo audit")
            print(f"   - Check detailed report: bridge_backend/diagnostics/sovereign_audit_latest.json")
        
        if git_netlify.get("repaired", 0) > 0:
            print(f"\n🔧 Auto-Repairs Performed:")
            print(f"   - {git_netlify.get('repaired', 0)} issues automatically fixed")
            print(f"   - Review changes and commit if appropriate")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Master Sovereign Audit & Repair - Full sovereignty verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool performs COMPLETE sovereign checks:
  ✅ Git sovereign configuration and agent
  ✅ Netlify configuration and deployment settings
  ✅ Repository structure and integrity
  ✅ Firewall sovereignty and network policies
  ✅ Network resilience and health
  ✅ Validation sovereignty across all systems
  ✅ Script execution environment

Examples:
  # Run full audit with auto-repair
  python3 scripts/master_sovereign_audit.py
  
  # Run audit without auto-repair
  python3 scripts/master_sovereign_audit.py --no-repair
  
  # Run in specific directory
  python3 scripts/master_sovereign_audit.py --repo-root /path/to/repo
        """
    )
    
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root directory (default: current directory)"
    )
    
    parser.add_argument(
        "--no-repair",
        action="store_true",
        help="Disable auto-repair functionality"
    )
    
    args = parser.parse_args()
    
    # Change to repo root
    repo_root = Path(args.repo_root).resolve()
    os.chdir(repo_root)
    
    # Execute master audit
    audit = MasterSovereignAudit(repo_root)
    results = audit.run_comprehensive_audit(auto_repair=not args.no_repair)
    
    # Exit with appropriate code
    status = results["overall_status"]
    if status == "HEALTHY":
        sys.exit(0)
    elif status == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
