#!/usr/bin/env python3
"""
Copilot Environment Validator
Ensures Copilot's runtime can reach all approved domains
and verifies preinstalled dependencies.
"""

import requests, subprocess, sys, json, os, time

ALLOWLIST = [
    "https://api.netlify.com",
    "https://bridge.sr-aibridge.com",
    "https://diagnostics.sr-aibridge.com",
    "https://render.com",
    "https://registry.npmjs.org",
    "https://pypi.org",
    "https://nodejs.org",
    "https://cdn.jsdelivr.net",
    "https://raw.githubusercontent.com",
    "https://github.com",
]

LOG_PATH = "bridge_backend/logs/copilot_env_validation.json"

def check_endpoint(url):
    try:
        r = requests.get(url, timeout=8)
        return {"url": url, "status": r.status_code, "ok": r.ok}
    except Exception as e:
        return {"url": url, "status": "error", "detail": str(e)}

def check_versions():
    checks = {}
    try:
        node = subprocess.check_output(["node", "-v"]).decode().strip()
        python = sys.version.split()[0]
        npm = subprocess.check_output(["npm", "-v"]).decode().strip()
        checks.update({"node": node, "python": python, "npm": npm})
    except Exception as e:
        checks["error"] = str(e)
    return checks

def write_log(data):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def main():
    print("🔍 Validating Copilot Environment...")
    results = {"timestamp": time.ctime(), "results": [], "versions": check_versions()}
    for url in ALLOWLIST:
        results["results"].append(check_endpoint(url))
        print(f"  → {url} checked")
    write_log(results)
    print(f"\n✅ Validation complete. Log written to {LOG_PATH}")

if __name__ == "__main__":
    main()
