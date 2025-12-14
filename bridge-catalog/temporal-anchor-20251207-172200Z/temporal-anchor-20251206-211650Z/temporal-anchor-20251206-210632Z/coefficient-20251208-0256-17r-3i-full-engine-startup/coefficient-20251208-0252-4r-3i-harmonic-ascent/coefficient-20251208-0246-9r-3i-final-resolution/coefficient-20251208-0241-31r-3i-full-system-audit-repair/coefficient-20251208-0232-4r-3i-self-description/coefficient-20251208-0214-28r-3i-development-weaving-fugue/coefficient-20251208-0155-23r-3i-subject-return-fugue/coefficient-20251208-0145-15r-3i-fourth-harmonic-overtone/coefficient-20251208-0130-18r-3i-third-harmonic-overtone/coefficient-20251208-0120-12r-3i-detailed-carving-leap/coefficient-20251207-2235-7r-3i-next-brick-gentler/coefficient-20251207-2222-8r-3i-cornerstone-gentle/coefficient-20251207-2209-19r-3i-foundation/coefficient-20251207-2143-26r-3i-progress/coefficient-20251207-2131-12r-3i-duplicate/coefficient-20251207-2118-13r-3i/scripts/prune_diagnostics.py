#!/usr/bin/env python3
import os
import requests
import json
from datetime import datetime, timedelta, timezone

def prune_old_diagnostics():
    bridge_url = os.getenv("BRIDGE_URL")
    if not bridge_url:
        print("⚠️ BRIDGE_URL missing.")
        return
    endpoint = f"{bridge_url.rstrip('/')}/api/diagnostics"

    try:
        r = requests.get(endpoint, timeout=10)
        r.raise_for_status()
        data = r.json()
        data.sort(key=lambda d: d.get("meta", {}).get("timestamp",""), reverse=True)

        cutoff = datetime.now(timezone.utc) - timedelta(days=30)
        to_delete = [d["id"] for i,d in enumerate(data)
                     if (i >= 50) or (datetime.fromisoformat(d["meta"]["timestamp"].replace("Z","")) < cutoff)]

        if not to_delete:
            print("✅ No diagnostics to prune.")
            return

        for did in to_delete:
            del_r = requests.delete(f"{endpoint}/{did}", timeout=10)
            print("🧹", "Deleted" if del_r.ok else "Failed", did)

        # report cleanup event
        payload = {
            "type": "DIAGNOSTIC_CLEANUP",
            "status": "success",
            "source": "GitHubAction",
            "meta": {
                "environment": "CI/CD",
                "timestamp": datetime.now(timezone.utc).isoformat()+"Z",
                "diagnostics": {"deleted_count": len(to_delete)}
            }
        }
        requests.post(endpoint, json=payload, timeout=10)
        
        # External Slack notifications removed in v1.9.6k - Genesis handles all telemetry internally
        
        print(f"✅ Pruned {len(to_delete)} diagnostics; cleanup logged to Bridge.")

    except Exception as e:
        print("❌ Prune failed:", e)

if __name__ == "__main__":
    prune_old_diagnostics()
