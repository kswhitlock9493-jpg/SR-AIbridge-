#!/usr/bin/env python3
import os
import requests
import sys
from datetime import datetime

def rollback_netlify():
    token = os.getenv("NETLIFY_AUTH_TOKEN")
    site_id = os.getenv("NETLIFY_SITE_ID")
    bridge_url = os.getenv("BRIDGE_URL")
    webhook = os.getenv("BRIDGE_SLACK_WEBHOOK")

    if not token or not site_id:
        print("❌ Missing Netlify credentials.")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}"}
    list_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys"

    try:
        print("🧭 Fetching last successful deploy...")
        r = requests.get(list_url, headers=headers, timeout=10)
        r.raise_for_status()
        deploys = r.json()

        last_success = next((d for d in deploys if d["state"] == "ready"), None)
        if not last_success:
            print("⚠️ No previous successful deploy found.")
            return

        restore_url = f"https://api.netlify.com/api/v1/sites/{site_id}/deploys/{last_success['id']}/restore"
        print(f"♻️ Rolling back to deploy {last_success['id']} ({last_success['created_at']})...")
        res = requests.post(restore_url, headers=headers, timeout=10)
        if res.status_code == 200:
            print("✅ Rollback successful.")
            if bridge_url:
                requests.post(f"{bridge_url.rstrip('/')}/api/diagnostics", json={
                    "type": "DEPLOYMENT_ROLLBACK",
                    "status": "success",
                    "source": "GitHubAction",
                    "meta": {
                        "environment": "CI/CD",
                        "timestamp": datetime.utcnow().isoformat()+"Z",
                        "diagnostics": {"rollback_id": last_success["id"]}
                    }
                }, timeout=10)
            if webhook:
                requests.post(webhook, json={"text": f"♻️ Rolled back to deploy `{last_success['id']}`"}, timeout=5)
        else:
            print(f"❌ Rollback failed: {res.status_code} {res.text}")
    except Exception as e:
        print("❌ Netlify rollback failed:", e)

if __name__ == "__main__":
    rollback_netlify()
