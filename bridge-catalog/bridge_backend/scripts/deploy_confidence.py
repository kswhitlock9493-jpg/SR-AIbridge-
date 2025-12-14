#!/usr/bin/env python3
"""
Deployment Confidence Reporter
Pulls audit and watchdog logs, summarizes stability, posts result to Bridge DB.
"""

import json, os, requests, time

LOG_DIR = "bridge_backend/logs"
TARGET = "https://bridge.sr-aibridge.com/api/system/healthreport"

def load_logs():
    combined = {}
    if not os.path.exists(LOG_DIR):
        return combined
    for f in os.listdir(LOG_DIR):
        if f.endswith(".log") or f.endswith(".json"):
            filepath = os.path.join(LOG_DIR, f)
            try:
                with open(filepath) as file:
                    if f.endswith(".json"):
                        combined[f] = json.load(file)
                    else:
                        combined[f] = file.read()
            except Exception as e:
                combined[f] = f"Error reading file: {e}"
    return combined

def summarize_health(data):
    stable = all("error" not in str(v).lower() for v in data.values())
    summary = {
        "timestamp": time.ctime(),
        "status": "STABLE" if stable else "DEGRADED",
        "details": list(data.keys())
    }
    return summary

def post_to_bridge(report):
    try:
        r = requests.post(TARGET, json=report, timeout=10)
        print("Bridge Response:", r.status_code, r.text)
    except Exception as e:
        print("Post failed:", e)

if __name__ == "__main__":
    logs = load_logs()
    report = summarize_health(logs)
    post_to_bridge(report)
    print("🛰️ Deployment Confidence Report Sent.")
