#!/usr/bin/env python3
"""
Bridge Sync Badge Generator
Generates a real-time badge reflecting Backend + Netlify health status
"""

import requests
import json
import os
import sys

def check_endpoint(url, name):
    """Check if an endpoint is healthy"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name}: OK (200)")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def generate_badge():
    """Generate the sync badge JSON"""
    print("🔍 Checking Bridge sync status...")
    
    # Check backend (configurable)
    backend_url = os.getenv("BACKEND_URL", "https://bridge.sr-aibridge.com")
    backend_ok = check_endpoint(
        f"{backend_url}/api/health",
        "Backend"
    )
    
    # Check frontend (Netlify)
    frontend_ok = check_endpoint(
        "https://sr-aibridge.netlify.app",
        "Frontend (Netlify)"
    )
    
    # Determine overall status
    if backend_ok and frontend_ok:
        status = "stable"
        color = "brightgreen"
        message = "STABLE"
    elif backend_ok or frontend_ok:
        status = "partial"
        color = "yellow"
        message = "PARTIAL"
    else:
        status = "drift"
        color = "red"
        message = "DRIFT"
    
    # Create badge JSON (shields.io endpoint format)
    badge = {
        "schemaVersion": 1,
        "label": "Bridge Sync",
        "message": message,
        "color": color
    }
    
    # Ensure output directory exists
    output_dir = "bridge-frontend/public"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write badge JSON
    output_path = os.path.join(output_dir, "bridge_sync_badge.json")
    with open(output_path, "w") as f:
        json.dump(badge, f, indent=2)
    
    print(f"\n✅ Bridge Sync Badge updated → {status.upper()}")
    print(f"   Badge file: {output_path}")
    print(f"   Backend: {'✅' if backend_ok else '❌'}")
    print(f"   Frontend: {'✅' if frontend_ok else '❌'}")
    
    return 0 if (backend_ok and frontend_ok) else 1

if __name__ == "__main__":
    try:
        exit_code = generate_badge()
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Badge generation failed: {e}")
        sys.exit(1)
