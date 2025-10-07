#!/usr/bin/env python3
import os
import requests
import json

def notify_bridge(event_type: str, status: str, source: str):
    bridge_url = os.getenv("BRIDGE_URL")
    if not bridge_url:
        print("⚠️ BRIDGE_URL not set, skipping webhook notification.")
        return

    endpoint = f"{bridge_url.rstrip('/')}/api/diagnostics"
    payload = {
        "type": event_type,
        "status": status,
        "source": source,
        "meta": {
            "environment": "CI/CD",
            "trigger": "GitHubAction",
        }
    }

    try:
        resp = requests.post(endpoint, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ Bridge successfully notified of deployment repair.")
        else:
            print(f"⚠️ Bridge notification returned {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"❌ Failed to notify Bridge: {e}")

if __name__ == "__main__":
    notify_bridge("DEPLOYMENT_REPAIR", "auto-healed", "GitHubAction")
