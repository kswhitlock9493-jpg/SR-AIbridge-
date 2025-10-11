#!/usr/bin/env python3
import os
import requests
import json
from datetime import datetime

def notify_slack(event_type, status, message=None):
    """DEPRECATED: External Slack notifications removed in v1.9.6k.
    
    All notifications now route through internal Genesis event bus.
    This function is kept for backwards compatibility but does nothing.
    """
    # External Slack/Discord webhooks removed - Genesis handles all telemetry internally
    pass

def collect_repair_diagnostics():
    """Read repair log or return default diagnostics."""
    repair_log_path = "repair_log.json"
    if os.path.exists(repair_log_path):
        try:
            with open(repair_log_path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "summary": "No repair log found. Sending generic diagnostic payload."
    }

def build_payload(event_type, status, source, diagnostics=None):
    """Construct a unified diagnostic payload for Bridge."""
    payload = {
        "type": event_type,
        "status": status,
        "source": source,
        "meta": {
            "environment": "CI/CD",
            "trigger": "GitHubAction",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "diagnostics": diagnostics or {}
        }
    }
    return payload

def notify_bridge(event_type, status, source, diagnostics=None):
    """Send diagnostic event to Bridge."""
    bridge_url = os.getenv("BRIDGE_URL")
    if not bridge_url:
        print("⚠️ BRIDGE_URL not set, skipping Bridge notification.")
        return

    endpoint = f"{bridge_url.rstrip('/')}/api/diagnostics"
    payload = build_payload(event_type, status, source, diagnostics)

    try:
        resp = requests.post(endpoint, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"✅ Bridge notified: {event_type} ({status})")
        else:
            print(f"⚠️ Bridge returned {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"❌ Bridge notification failed: {e}")

# --- Shortcut Event Wrappers ---

def report_repair_success():
    notify_bridge("DEPLOYMENT_REPAIR", "auto-healed", "GitHubAction", collect_repair_diagnostics())
    notify_slack("DEPLOYMENT_REPAIR", "auto-healed", "Environment repaired automatically.")

def report_build_failure():
    notify_bridge("BUILD_FAILURE", "failed", "GitHubAction")
    notify_slack("BUILD_FAILURE", "failed", "Build failed during npm run build.")

def report_deploy_failure():
    notify_bridge("DEPLOYMENT_FAILURE", "failed", "GitHubAction")
    notify_slack("DEPLOYMENT_FAILURE", "failed", "Deploy failed during Netlify publish.")

def report_deploy_success():
    notify_bridge("DEPLOYMENT_SUCCESS", "success", "GitHubAction")
    notify_slack("DEPLOYMENT_SUCCESS", "success", "Deploy completed successfully.")

def report_build_success():
    notify_bridge("BUILD_SUCCESS", "success", "GitHubAction")
    notify_slack("BUILD_SUCCESS", "success", "Vite build completed successfully.")

if __name__ == "__main__":
    # Default behavior for standalone execution
    report_repair_success()
