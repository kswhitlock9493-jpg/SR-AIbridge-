#!/usr/bin/env python3
"""
Comprehensive triage matrix - validates backend endpoints and API surface
"""
import os
import sys
import argparse
import json
import pathlib

def triage_matrix(base_url, token=None):
    """Run comprehensive triage on backend"""
    try:
        import requests
    except ImportError:
        print("requests module required")
        return 1
    
    results = {}
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Define endpoints to test
    endpoints = [
        {"path": "/api/health", "method": "GET", "required": True},
        {"path": "/health", "method": "GET", "required": True},
        {"path": "/api/version", "method": "GET", "required": False},
        {"path": "/api/routes", "method": "GET", "required": False},
        {"path": "/", "method": "GET", "required": True},
    ]
    
    passed = 0
    failed = 0
    
    for endpoint in endpoints:
        path = endpoint["path"]
        method = endpoint["method"]
        required = endpoint["required"]
        
        try:
            url = f"{base_url}{path}"
            resp = requests.request(method, url, headers=headers, timeout=10)
            
            ok = resp.status_code in [200, 201]
            results[path] = {
                "method": method,
                "status": resp.status_code,
                "ok": ok,
                "required": required
            }
            
            if ok:
                passed += 1
                print(f"✓ {method} {path}: {resp.status_code}")
            elif required:
                failed += 1
                print(f"✗ {method} {path}: {resp.status_code} (REQUIRED)")
            else:
                print(f"⚠ {method} {path}: {resp.status_code} (optional)")
                
        except Exception as e:
            results[path] = {
                "method": method,
                "status": "error",
                "ok": False,
                "required": required,
                "error": str(e)
            }
            if required:
                failed += 1
                print(f"✗ {method} {path}: {e} (REQUIRED)")
            else:
                print(f"⚠ {method} {path}: {e} (optional)")
    
    # Save results
    out_dir = pathlib.Path("bridge_backend/diagnostics")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "triage_matrix_report.json"
    
    summary = {
        "passed": passed,
        "failed": failed,
        "total": len(endpoints),
        "endpoints": results
    }
    
    out_file.write_text(json.dumps(summary, indent=2))
    
    print(f"\nSummary: {passed} passed, {failed} failed, {len(endpoints)} total")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Base URL for backend")
    parser.add_argument("--token", help="Optional authentication token")
    args = parser.parse_args()
    
    sys.exit(triage_matrix(args.base, args.token))
