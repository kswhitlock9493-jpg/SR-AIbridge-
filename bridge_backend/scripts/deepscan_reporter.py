#!/usr/bin/env python3
"""
DeepScan Reporter for SR-AIbridge Backend
Reports DeepScan diagnostics to the Bridge diagnostics endpoint
"""

import os
import json
from datetime import datetime, timezone
import requests
from typing import Dict, Any, Optional


def report_deepscan(status: str, diagnostics: Dict[str, Any]) -> None:
    """
    Report DeepScan results to Bridge diagnostics endpoint
    
    Args:
        status: Status of the DeepScan (e.g., "complete", "failed")
        diagnostics: Dictionary containing diagnostic information
    """
    payload = {
        "type": "ENDPOINT_DEEPSCAN",
        "status": status,
        "source": "BridgeBackend",
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "diagnostics": diagnostics,
        },
    }
    
    try:
        bridge_url = os.getenv("BRIDGE_URL")
        if not bridge_url:
            print("⚠️ BRIDGE_URL not set, cannot send DeepScan report")
            return
            
        url = f"{bridge_url}/api/diagnostics"
        r = requests.post(url, json=payload, timeout=10)
        
        if r.status_code == 200:
            print(f"📡 DeepScan report sent successfully: {r.status_code}")
        else:
            print(f"⚠️ DeepScan report sent with status: {r.status_code}")
            
    except Exception as e:
        print(f"⚠️ Failed to send DeepScan report: {str(e)}")


def main():
    """Main entry point for manual execution"""
    # Example usage
    sample_diagnostics = {
        "endpoints_checked": 3,
        "environment": "backend",
        "manual_run": True
    }
    
    report_deepscan("complete", sample_diagnostics)
    print("✅ DeepScan report completed")


if __name__ == "__main__":
    main()
