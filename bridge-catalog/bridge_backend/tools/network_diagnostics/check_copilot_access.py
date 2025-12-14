#!/usr/bin/env python3
"""
Bridge Network Diagnostics v1.7.2
Performs real-time verification of allowlisted endpoints for Copilot, Render, Netlify, NPM, and GitHub.
"""

import socket
import ssl
import json
import concurrent.futures
import time
import pathlib
import urllib.parse
import requests

REPORT = pathlib.Path(__file__).resolve().parents[2] / "diagnostics" / "copilot_network_report.json"
TIMEOUT = 4

DOMAINS = [
    "https://api.github.com",
    "https://api.netlify.com",
    "https://bridge.sr-aibridge.com",
    "https://diagnostics.sr-aibridge.com",
    "https://sr-aibridge.netlify.app/api/vault",
    "https://registry.npmjs.org",
    "https://pypi.org",
    "https://nodejs.org",
    "https://github.com",
    "https://codeload.github.com",
    "https://raw.githubusercontent.com",
    "https://objects.githubusercontent.com",
    "https://ghcr.io",
    "https://www.githubstatus.com",
    "https://www.netlifystatus.com"
]

# Optional: Legacy backend provider endpoints (not required for sovereign mode)
OPTIONAL_ENDPOINTS = [
    "https://api.render.com",
]

def check_tls(domain):
    hostname = urllib.parse.urlparse(domain).hostname
    ctx = ssl.create_default_context()
    start = time.time()
    try:
        with socket.create_connection((hostname, 443), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                elapsed = round(time.time() - start, 2)
                return {"domain": domain, "status": "reachable", "latency": elapsed, "subject": cert.get('subject', [])}
    except Exception as e:
        return {"domain": domain, "status": f"unreachable: {type(e).__name__}", "latency": None}

def check_http(domain):
    try:
        r = requests.get(domain, timeout=TIMEOUT)
        return {"domain": domain, "http_status": r.status_code, "ok": r.ok}
    except Exception as e:
        return {"domain": domain, "http_status": None, "ok": False, "error": str(e)}

def run_diagnostics():
    print("\n🌐 Running Bridge Network Diagnostics ...\n")
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(check_tls, d) for d in DOMAINS]
        for f in concurrent.futures.as_completed(futures):
            results.append(f.result())

    http_checks = [check_http(d) for d in DOMAINS]

    summary = {
        "reachable": sum(1 for r in results if r["status"] == "reachable"),
        "total": len(DOMAINS),
        "timestamp": time.time()
    }

    status = (
        "🟢 BRIDGE NETWORK STABLE"
        if summary["reachable"] == len(DOMAINS)
        else "🟡 PARTIAL CONNECTIVITY"
        if summary["reachable"] > len(DOMAINS) * 0.7
        else "🔴 CRITICAL FAILURE"
    )

    report = {"summary": summary, "status": status, "tls": results, "http": http_checks}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=2)
    print(f"{status}\nDiagnostic report → {REPORT}\n")

if __name__ == "__main__":
    run_diagnostics()
