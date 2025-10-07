#!/usr/bin/env python3
"""
Firewall Watchdog - Copilot Firewall Accountability & Audit Logger

Monitors DNS/firewall events and reports blocked/unknown hosts to Bridge diagnostics.
Ensures accountability for all Copilot network access attempts.
"""

import os
import socket
import time
import json
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any

LOG_PATH = "logs/copilot_firewall.log"
ALLOWLIST_PATH = ".github/allowlist/hosts.txt"
BRIDGE_URL = os.getenv("BRIDGE_URL", "https://sr-aibridge.onrender.com")


def load_allowlist() -> List[str]:
    """Load the allowlist from the configuration file."""
    if not os.path.exists(ALLOWLIST_PATH):
        return []
    with open(ALLOWLIST_PATH) as f:
        return [line.strip() for line in f if line.strip()]


def log_event(event: Dict[str, Any]) -> None:
    """Log a firewall event to the local log file."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def report_to_bridge(event: Dict[str, Any]) -> None:
    """Report a firewall event to the Bridge diagnostics API."""
    try:
        requests.post(
            f"{BRIDGE_URL}/api/diagnostics",
            json={
                "type": "FIREWALL_EVENT",
                "status": "blocked" if not event.get("resolved") else "resolved",
                "meta": event
            },
            timeout=5
        )
    except Exception:
        # Silently fail - we don't want to break the workflow if Bridge is down
        pass


def test_connection(host: str) -> bool:
    """Test if a host can be resolved via DNS."""
    try:
        socket.gethostbyname(host)
        return True
    except Exception:
        return False


def watchdog() -> None:
    """Run the firewall watchdog to monitor and audit network access."""
    allowlist = load_allowlist()
    
    # Hosts that Copilot should be able to reach
    monitored_hosts = [
        "bridge.sr-aibridge.com",
        "diagnostics.sr-aibridge.com",
        "render.com",
        "api.netlify.com",
        "pypi.org",
        "registry.npmjs.org"
    ]

    print("🛡️ Running Firewall Watchdog...")
    print(f"📋 Loaded {len(allowlist)} hosts from allowlist")
    print(f"🔍 Monitoring {len(monitored_hosts)} critical hosts\n")
    
    for host in monitored_hosts:
        resolved = test_connection(host)
        allowed = host in allowlist
        
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "host": host,
            "resolved": resolved,
            "allowed": allowed,
            "trigger": "preflight-scan",
        }
        
        log_event(event)
        report_to_bridge(event)
        
        # Status reporting
        status_icon = '✅' if resolved else '❌'
        access_status = 'allowed' if allowed else 'blocked'
        print(f"{status_icon} {host:40s} ({access_status})")


if __name__ == "__main__":
    print("=" * 70)
    watchdog()
    print("=" * 70)
    print(f"📡 Audit complete. Logs saved to: {LOG_PATH}")
