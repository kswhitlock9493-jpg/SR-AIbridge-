#!/usr/bin/env python3
"""
Endpoint Triage Automation for SR-AIbridge Backend
Autonomous triage process for core API routes
Runs on startup, on interval, or by manual trigger
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any

# Core endpoints to monitor
ENDPOINTS = [
    {"name": "status", "url": "/api/status"},
    {"name": "diagnostics", "url": "/api/diagnostics"},
    {"name": "agents", "url": "/agents"},
]

BASE_URL = os.getenv("BRIDGE_BASE_URL", "https://sr-aibridge.onrender.com")
BRIDGE_NOTIFY = os.getenv("BRIDGE_URL", "https://sr-aibridge.netlify.app/api/diagnostics")


def check_endpoint(endpoint: Dict[str, str]) -> Dict[str, Any]:
    """Check a single endpoint and return status"""
    name = endpoint["name"]
    url = endpoint["url"]
    full_url = f"{BASE_URL}{url}"
    
    try:
        response = requests.get(full_url, timeout=7)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}")
        
        # Try to parse JSON response
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text[:100]}
        
        return {
            "name": name,
            "status": "OK",
            "data": data
        }
    except Exception as err:
        return {
            "name": name,
            "status": "FAILED",
            "error": str(err)
        }


def notify_bridge(payload: Dict[str, Any]) -> None:
    """Send notification to Bridge diagnostics endpoint"""
    try:
        response = requests.post(
            BRIDGE_NOTIFY,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Bridge notified successfully")
        else:
            print(f"⚠️ Bridge returned {response.status_code}: {response.text}")
    except Exception as err:
        print(f"⚠️ Bridge notification failed: {err}")


def run_endpoint_triage(manual: bool = False) -> Dict[str, Any]:
    """
    Run endpoint triage checks
    Returns triage summary
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    results = []
    
    print("🩺 Starting endpoint triage...")
    
    # Check each endpoint
    for endpoint in ENDPOINTS:
        result = check_endpoint(endpoint)
        results.append(result)
        status_icon = "✅" if result["status"] == "OK" else "❌"
        print(f"  {status_icon} {result['name']}: {result['status']}")
    
    # Calculate overall status
    failed = [r for r in results if r["status"] == "FAILED"]
    if len(failed) == 0:
        overall = "HEALTHY"
    elif len(failed) < 2:
        overall = "DEGRADED"
    else:
        overall = "CRITICAL"
    
    # Build summary
    summary = {
        "type": "ENDPOINT_TRIAGE",
        "status": overall,
        "source": "endpoint_triage.py",
        "meta": {
            "timestamp": timestamp,
            "manual": manual,
            "failedEndpoints": [f["name"] for f in failed],
            "results": results,
            "environment": "backend"
        }
    }
    
    # Save to file
    report_path = "endpoint_report.json"
    try:
        with open(report_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"📄 Report saved to {report_path}")
    except Exception as err:
        print(f"⚠️ Failed to save report: {err}")
    
    # Notify Bridge
    notify_bridge(summary)
    
    # Print summary
    print(f"\n📡 Endpoint Triage: {overall}")
    if overall != "HEALTHY":
        print("\n❌ Failed Endpoints:")
        for f in failed:
            print(f"  - {f['name']}: {f.get('error', 'Unknown error')}")
    
    return summary


if __name__ == "__main__":
    # Check for manual flag
    manual = "--manual" in sys.argv
    
    # Run triage
    summary = run_endpoint_triage(manual)
    
    # Exit with appropriate code
    if summary["status"] == "CRITICAL":
        sys.exit(2)
    elif summary["status"] == "DEGRADED":
        sys.exit(1)
    else:
        sys.exit(0)
