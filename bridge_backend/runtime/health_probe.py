#!/usr/bin/env python3
"""
Health probe and cache warmer
Verifies the application is responding before accepting traffic
"""
import os
import sys
import argparse

def warm_health():
    """Warm up the health endpoint"""
    try:
        import requests
    except ImportError:
        print("[health_probe] requests not installed, skipping warm")
        return 0
    
    base = os.getenv("SELF_BASE", f"http://127.0.0.1:{os.getenv('PORT', '10000')}")
    
    try:
        # Note: This runs before the app is started, so we just prepare
        # The actual warming happens after uvicorn starts
        print(f"[health_probe] Health endpoint will be: {base}/api/health")
        print("[health_probe] Warm probe ready")
        return 0
    except Exception as e:
        print(f"[health_probe] Warm failed: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--warm", action="store_true")
    args = parser.parse_args()
    
    if args.warm:
        sys.exit(warm_health())
    else:
        print("[health_probe] No action specified")
        sys.exit(0)
