#!/usr/bin/env python3
"""
Infrastructure Integrity Auditor
Verifies environment health, endpoint availability, and cross-service parity.
"""

import os
import requests
import json
import time

LOG_PATH = "bridge_backend/logs/integrity_audit.json"

ENDPOINTS = {
    "Bridge": "https://bridge.sr-aibridge.com",
    "Diagnostics": "https://diagnostics.sr-aibridge.com",
    "Render": "https://sr-aibridge.onrender.com/health",
    "Netlify": "https://api.netlify.com",
}

REQUIRED_ENV = ["BRIDGE_ENV", "NETLIFY_API", "BRIDGE_BACKEND", "BRIDGE_DIAGNOSTICS"]


def check_endpoints():
    """Check health of all endpoints"""
    results = {}
    for name, url in ENDPOINTS.items():
        try:
            res = requests.get(url, timeout=8)
            results[name] = {"status": res.status_code, "ok": res.ok}
        except Exception as e:
            results[name] = {"status": "error", "detail": str(e)}
    return results


def check_env_vars():
    """Check for required environment variables"""
    return {var: os.getenv(var, "MISSING") for var in REQUIRED_ENV}


def run_audit():
    """Run the complete infrastructure audit"""
    data = {
        "timestamp": time.ctime(),
        "env": check_env_vars(),
        "endpoints": check_endpoints()
    }
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print("🛰️ Infrastructure Audit Complete — Results Logged")


if __name__ == "__main__":
    run_audit()
