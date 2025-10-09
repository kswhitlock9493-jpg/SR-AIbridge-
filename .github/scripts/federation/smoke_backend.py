#!/usr/bin/env python3
"""
Backend smoke test - validates core backend health endpoints
"""
import os
import sys
import argparse
import json
import pathlib

def smoke_backend(base_url):
    """Run smoke tests on backend"""
    try:
        import requests
    except ImportError:
        print("requests module required")
        return 1
    
    results = {}
    
    # Test 1: Health endpoint
    try:
        resp = requests.get(f"{base_url}/api/health", timeout=10)
        results["health"] = {
            "status": resp.status_code,
            "ok": resp.status_code == 200
        }
        print(f"✓ /api/health: {resp.status_code}")
    except Exception as e:
        results["health"] = {"status": "error", "ok": False, "error": str(e)}
        print(f"✗ /api/health: {e}")
    
    # Test 2: Version endpoint (if exists)
    try:
        resp = requests.get(f"{base_url}/api/version", timeout=10)
        results["version"] = {
            "status": resp.status_code,
            "ok": resp.status_code == 200
        }
        if resp.status_code == 200:
            print(f"✓ /api/version: {resp.status_code}")
        else:
            print(f"⚠ /api/version: {resp.status_code} (endpoint may not exist yet)")
    except Exception as e:
        results["version"] = {"status": "error", "ok": False, "error": str(e)}
        print(f"⚠ /api/version: {e} (endpoint may not exist yet)")
    
    # Test 3: Routes endpoint (if exists)
    try:
        resp = requests.get(f"{base_url}/api/routes", timeout=10)
        results["routes"] = {
            "status": resp.status_code,
            "ok": resp.status_code == 200
        }
        if resp.status_code == 200:
            data = resp.json()
            print(f"✓ /api/routes: {resp.status_code} ({data.get('count', 0)} routes)")
        else:
            print(f"⚠ /api/routes: {resp.status_code} (endpoint may not exist yet)")
    except Exception as e:
        results["routes"] = {"status": "error", "ok": False, "error": str(e)}
        print(f"⚠ /api/routes: {e} (endpoint may not exist yet)")
    
    # Save results
    out_dir = pathlib.Path("bridge_backend/diagnostics")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "smoke_backend_report.json"
    out_file.write_text(json.dumps(results, indent=2))
    
    # Return success if health check passed (version and routes are optional)
    return 0 if results.get("health", {}).get("ok") else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Base URL for backend")
    args = parser.parse_args()
    
    sys.exit(smoke_backend(args.base))
