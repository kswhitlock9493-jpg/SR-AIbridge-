#!/usr/bin/env python3
"""
API Triage System for SR-AIbridge Service Health Monitoring
Validates API integrations, schema responses, and detects regressions
Runs on startup, hourly, or by manual trigger
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# API checks with schema validation
CHECKS = [
    {
        "name": "Bridge Diagnostics Feed",
        "url": "/api/diagnostics",
        "schema": {"status": "str"}
    },
    {
        "name": "Agents Registry",
        "url": "/agents",
        "schema": {"agents": "list"}
    },
    {
        "name": "System Status",
        "url": "/api/status",
        "schema": {"status": "str"}
    }
]

BASE_URL = os.getenv("BRIDGE_BASE_URL", "https://sr-aibridge.onrender.com")
BRIDGE_NOTIFY = os.getenv("BRIDGE_URL", "https://sr-aibridge.netlify.app/api/diagnostics")


def validate_schema(obj: Any, schema: Dict[str, str]) -> Optional[str]:
    """
    Validate object against expected schema
    Returns error message if validation fails, None if successful
    """
    if not isinstance(obj, dict):
        return f"Response is not an object (got {type(obj).__name__})"
    
    for key, expected_type in schema.items():
        if key not in obj:
            return f"Missing field '{key}'"
        
        value = obj[key]
        
        # Type checking
        if expected_type == "str" and not isinstance(value, str):
            return f"Invalid field '{key}' (expected string, got {type(value).__name__})"
        elif expected_type == "object" and not isinstance(value, dict):
            return f"Invalid field '{key}' (expected object, got {type(value).__name__})"
        elif expected_type == "list" and not isinstance(value, list):
            return f"Invalid field '{key}' (expected list, got {type(value).__name__})"
        elif expected_type == "number" and not isinstance(value, (int, float)):
            return f"Invalid field '{key}' (expected number, got {type(value).__name__})"
        elif expected_type == "boolean" and not isinstance(value, bool):
            return f"Invalid field '{key}' (expected boolean, got {type(value).__name__})"
    
    return None


def check_api(check: Dict[str, Any]) -> Dict[str, Any]:
    """Check a single API endpoint with schema validation"""
    name = check["name"]
    url = check["url"]
    schema = check["schema"]
    full_url = f"{BASE_URL}{url}"
    
    try:
        response = requests.get(full_url, timeout=8)
        if not response.ok:
            raise Exception(f"HTTP {response.status_code}")
        
        # Parse JSON response
        try:
            data = response.json()
        except Exception as e:
            raise Exception(f"Invalid JSON response: {str(e)}")
        
        # Validate schema
        schema_error = validate_schema(data, schema)
        if schema_error:
            raise Exception(schema_error)
        
        return {
            "name": name,
            "url": url,
            "status": "OK"
        }
    except Exception as err:
        return {
            "name": name,
            "url": url,
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


def run_api_triage(manual: bool = False) -> Dict[str, Any]:
    """
    Run API triage checks with schema validation
    Returns triage summary
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    results = []
    
    print("🧬 Starting API triage...")
    
    # Check each API
    for check in CHECKS:
        result = check_api(check)
        results.append(result)
        status_icon = "✅" if result["status"] == "OK" else "❌"
        print(f"  {status_icon} {result['name']}: {result['status']}")
    
    # Calculate overall status
    failed = [r for r in results if r["status"] == "FAILED"]
    if len(failed) == 0:
        state = "HEALTHY"
    elif len(failed) <= 1:
        state = "DEGRADED"
    else:
        state = "CRITICAL"
    
    # Build report
    report = {
        "type": "API_TRIAGE",
        "status": state,
        "source": "api_triage.py",
        "meta": {
            "timestamp": timestamp,
            "manual": manual,
            "failedChecks": failed,
            "results": results,
            "environment": "backend"
        }
    }
    
    # Save to file
    report_path = "api_triage_report.json"
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to {report_path}")
    except Exception as err:
        print(f"⚠️ Failed to save report: {err}")
    
    # Notify Bridge
    notify_bridge(report)
    
    # Print summary
    print(f"\n📡 API Triage: {state}")
    if failed:
        print("\n❌ Failed Checks:")
        for f in failed:
            print(f"  - {f['name']}: {f.get('error', 'Unknown error')}")
    
    return report


if __name__ == "__main__":
    # Check for manual flag
    manual = "--manual" in sys.argv
    
    # Run triage
    report = run_api_triage(manual)
    
    # Exit with appropriate code
    if report["status"] == "CRITICAL":
        sys.exit(2)
    elif report["status"] == "DEGRADED":
        sys.exit(1)
    else:
        sys.exit(0)
