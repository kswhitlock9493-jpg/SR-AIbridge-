#!/usr/bin/env python3
"""
Bridge Event Reporter
Reports deployment and health events to the diagnostics system
"""

import argparse
import requests
import json
import sys
from datetime import datetime, timezone

def report_event(status, details=None):
    """Report a bridge event to the diagnostics system"""
    
    event_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source": "bridge_autodeploy",
        "details": details or f"Auto-deploy event: {status}"
    }
    
    print(f"📡 Reporting bridge event: {status}")
    
    # Try to report to diagnostics endpoint
    diagnostics_url = "https://sr-aibridge.onrender.com/api/diagnostics/events"
    
    try:
        response = requests.post(
            diagnostics_url,
            json=event_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Event reported successfully")
            return 0
        else:
            print(f"⚠️ Diagnostics returned HTTP {response.status_code}")
            return 0  # Don't fail the workflow for this
            
    except Exception as e:
        print(f"⚠️ Could not report to diagnostics: {e}")
        print("   (This is non-critical, continuing...)")
        return 0  # Don't fail the workflow for diagnostics issues

def main():
    parser = argparse.ArgumentParser(
        description="Report Bridge deployment events"
    )
    parser.add_argument(
        "--status",
        required=True,
        help="Event status (e.g., AUTODEPLOY_OK, AUTODEPLOY_FAILED)"
    )
    parser.add_argument(
        "--details",
        help="Optional event details"
    )
    
    args = parser.parse_args()
    
    return report_event(args.status, args.details)

if __name__ == "__main__":
    sys.exit(main())
