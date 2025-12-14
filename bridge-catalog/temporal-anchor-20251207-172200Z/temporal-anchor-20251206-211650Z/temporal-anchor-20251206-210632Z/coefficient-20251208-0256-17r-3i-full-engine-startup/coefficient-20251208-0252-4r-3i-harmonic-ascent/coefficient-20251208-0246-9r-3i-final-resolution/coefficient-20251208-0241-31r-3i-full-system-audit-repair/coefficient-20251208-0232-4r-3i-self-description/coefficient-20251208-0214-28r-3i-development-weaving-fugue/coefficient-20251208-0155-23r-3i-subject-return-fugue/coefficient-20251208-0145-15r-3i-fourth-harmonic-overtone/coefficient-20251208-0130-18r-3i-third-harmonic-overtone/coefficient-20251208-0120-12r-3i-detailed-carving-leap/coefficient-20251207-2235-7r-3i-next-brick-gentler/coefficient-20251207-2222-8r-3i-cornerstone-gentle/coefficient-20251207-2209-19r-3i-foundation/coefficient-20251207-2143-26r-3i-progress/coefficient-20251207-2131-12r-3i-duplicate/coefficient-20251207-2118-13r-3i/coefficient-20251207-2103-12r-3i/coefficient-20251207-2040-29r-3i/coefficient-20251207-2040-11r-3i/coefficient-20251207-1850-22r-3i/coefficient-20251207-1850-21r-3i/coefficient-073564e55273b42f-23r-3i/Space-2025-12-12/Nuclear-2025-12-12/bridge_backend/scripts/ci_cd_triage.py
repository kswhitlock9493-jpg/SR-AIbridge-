#!/usr/bin/env python3
"""
CI/CD Triage Report Generator
Generates a snapshot of the latest CI/CD build/deploy status.
"""

import json
import os
import sys
from datetime import datetime, timezone

def generate_ci_cd_report(event_type="CI_CD_TRIAGE", status="HEALTHY", details=None):
    """
    Generate a CI/CD triage report.
    
    Args:
        event_type: Type of CI/CD event (CI_CD_TRIAGE, DEPLOYMENT_SUCCESS, etc.)
        status: Overall status (HEALTHY, DEGRADED, CRITICAL, etc.)
        details: Additional diagnostic details
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    
    report = {
        "type": event_type,
        "status": status,
        "source": "ci_cd_triage.py",
        "meta": {
            "timestamp": timestamp,
            "environment": "CI/CD",
            "trigger": "GitHubAction",
            "details": details or {},
        }
    }
    
    # Save to file
    report_path = "ci_cd_report.json"
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 CI/CD Report saved to {report_path}")
    except Exception as err:
        print(f"⚠️ Failed to save report: {err}")
    
    print(f"\n📡 CI/CD Triage: {status}")
    return report

if __name__ == "__main__":
    # Parse command line arguments
    event_type = sys.argv[1] if len(sys.argv) > 1 else "CI_CD_TRIAGE"
    status = sys.argv[2] if len(sys.argv) > 2 else "HEALTHY"
    
    # Generate report
    generate_ci_cd_report(event_type, status)
