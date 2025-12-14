"""
Embedded Autonomy Node - Core orchestration engine
v1.9.7n

This is the main entry point for the Embedded Autonomy Node (EAN).
It orchestrates the micro-Bridge operations within GitHub's environment.
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the autonomy_node directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import truth
import parser
import cascade
import blueprint


class AutonomyNode:
    """
    Main orchestrator for the Embedded Autonomy Node
    """
    
    def __init__(self):
        """Initialize the Autonomy Node with configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "node_config.json")
        with open(config_path) as cfg:
            self.config = json.load(cfg)
    
    def run(self):
        """
        Execute the autonomy cycle:
        1. Parse repository
        2. Repair issues
        3. Verify with Truth Micro-Certifier
        4. Sync with Cascade
        5. Generate report
        """
        print("🧠 [EAN] Embedded Autonomy Node active.")
        print(f"🕒 [EAN] Timestamp: {datetime.now().isoformat()}")
        
        # Parse repository for issues
        findings = parser.scan_repo()
        print(f"📊 [EAN] Found {len(findings)} items to review")
        
        # Apply safe repairs
        fixes = blueprint.repair(findings)
        print(f"🔧 [EAN] Applied {len(fixes)} safe fixes")
        
        # Verify integrity
        truth.verify(fixes)
        
        # Sync state with cascade
        cascade.sync_state()
        
        # Generate report
        self._generate_report(findings, fixes)
        
        print("✅ [EAN] Integrity restored and certified.")
    
    def _generate_report(self, findings, fixes):
        """
        Generate and save audit report
        
        Args:
            findings: Dictionary of issues found
            fixes: Dictionary of repairs applied
        """
        report_dir = os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = os.path.join(report_dir, f"summary_{timestamp}.json")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.9.7n",
            "findings_count": len(findings),
            "fixes_count": len(fixes),
            "findings": findings,
            "fixes": fixes,
            "status": "complete"
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📝 [EAN] Report saved to {report_path}")


def main():
    """Main entry point"""
    try:
        node = AutonomyNode()
        node.run()
        return 0
    except Exception as e:
        print(f"❌ [EAN] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
