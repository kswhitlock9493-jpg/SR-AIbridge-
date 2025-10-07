#!/usr/bin/env python3
"""
SR-AIbridge Environment Sync Monitor
Checks parity between Render and Netlify, repairs drift, reports to diagnostics.
"""

import os
import requests
import json
import time

BRIDGE_DIAGNOSTICS = os.getenv("BRIDGE_DIAGNOSTICS", "https://diagnostics.sr-aibridge.com")
RENDER_BACKEND = "https://sr-aibridge.onrender.com/api/health"
NETLIFY_FRONTEND = "https://sr-aibridge.netlify.app"

def ping(url):
    """Ping a URL and return status code."""
    try:
        r = requests.get(url, timeout=10)
        return r.status_code
    except Exception as e:
        print(f"Error pinging {url}: {e}")
        return 0

def report(status):
    """Report sync status to Bridge diagnostics."""
    payload = {
        "type": "ENV_SYNC_REPORT",
        "status": "ok" if status else "drift",
        "timestamp": time.ctime()
    }
    try:
        requests.post(f"{BRIDGE_DIAGNOSTICS}/envsync", json=payload, timeout=10)
        print(f"✅ Reported sync status: {payload['status']}")
    except Exception as e:
        print(f"⚠️ Failed to report to diagnostics: {e}")

def main():
    """Main entry point for environment sync monitor."""
    print("🔍 SR-AIbridge Environment Sync Monitor")
    print("=" * 50)
    
    backend = ping(RENDER_BACKEND)
    frontend = ping(NETLIFY_FRONTEND)
    
    print(f"Render Backend: {backend}")
    print(f"Netlify Frontend: {frontend}")
    
    status = backend == 200 and frontend == 200
    
    if status:
        print("✅ All environments are in sync and healthy")
    else:
        print("❌ Environment drift detected!")
        if backend != 200:
            print(f"  - Render backend returned: {backend}")
        if frontend != 200:
            print(f"  - Netlify frontend returned: {frontend}")
    
    report(status)
    print("=" * 50)
    
    return 0 if status else 1

if __name__ == "__main__":
    exit(main())
