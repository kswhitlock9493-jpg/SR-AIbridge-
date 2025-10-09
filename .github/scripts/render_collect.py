#!/usr/bin/env python3
"""
Render diagnostics collector
Collects logs, build info, and service status from Render API
"""
import os
import sys
import argparse
import json
import pathlib
from datetime import datetime

def collect_diagnostics(service_id, token):
    """Collect diagnostics from Render"""
    try:
        import requests
    except ImportError:
        print("requests module required")
        return 1
    
    if not token or not service_id:
        print("RENDER_API_TOKEN and RENDER_SERVICE_ID required")
        return 1
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    diagnostics = {
        "timestamp": datetime.utcnow().isoformat(),
        "service_id": service_id
    }
    
    # Get service info
    try:
        resp = requests.get(
            f"https://api.render.com/v1/services/{service_id}",
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            diagnostics["service"] = {
                "name": data.get("service", {}).get("name"),
                "type": data.get("service", {}).get("type"),
                "env": data.get("service", {}).get("env"),
                "status": "retrieved"
            }
            print("✓ Service info retrieved")
        else:
            diagnostics["service"] = {"status": "error", "code": resp.status_code}
            print(f"✗ Service info: {resp.status_code}")
    except Exception as e:
        diagnostics["service"] = {"status": "error", "error": str(e)}
        print(f"✗ Service info: {e}")
    
    # Get recent logs (last 100 lines)
    try:
        resp = requests.get(
            f"https://api.render.com/v1/services/{service_id}/logs?limit=100",
            headers=headers,
            timeout=10
        )
        if resp.status_code == 200:
            logs = resp.text
            diagnostics["logs"] = {
                "status": "retrieved",
                "lines": len(logs.splitlines()),
                "preview": logs[:500]  # First 500 chars
            }
            print(f"✓ Logs retrieved ({len(logs.splitlines())} lines)")
        else:
            diagnostics["logs"] = {"status": "error", "code": resp.status_code}
            print(f"✗ Logs: {resp.status_code}")
    except Exception as e:
        diagnostics["logs"] = {"status": "error", "error": str(e)}
        print(f"✗ Logs: {e}")
    
    # Save diagnostics
    out_dir = pathlib.Path("bridge_backend/diagnostics/render")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # JSON report
    json_file = out_dir / "render_diagnostics.json"
    json_file.write_text(json.dumps(diagnostics, indent=2))
    
    # Text report
    txt_file = out_dir / "render_diagnostics.txt"
    txt_content = f"""Render Diagnostics Report
Generated: {diagnostics['timestamp']}
Service ID: {service_id}

Service Info:
{json.dumps(diagnostics.get('service', {}), indent=2)}

Logs:
{json.dumps(diagnostics.get('logs', {}), indent=2)}
"""
    txt_file.write_text(txt_content)
    
    print(f"\nDiagnostics saved to {out_dir}/")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--service", help="Render service ID")
    parser.add_argument("--token", help="Render API token")
    args = parser.parse_args()
    
    service_id = args.service or os.getenv("RENDER_SERVICE_ID")
    token = args.token or os.getenv("RENDER_API_TOKEN")
    
    sys.exit(collect_diagnostics(service_id, token))
