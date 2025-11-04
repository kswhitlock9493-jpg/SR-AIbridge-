#!/usr/bin/env python3
"""
Hooks Triage System for SR-AIbridge Webhook and Build Hook Health Monitoring
Validates webhook endpoints, measures latency, and reports to Bridge diagnostics
Runs on startup, hourly, or by manual trigger
"""

import os
import sys
import json
import time
import hmac
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

# Configuration
# Use BRH (Bridge Runtime Handler) as default, not Render
# Priority: BRIDGE_BASE_URL > BRH_BACKEND_URL > localhost:8000
BASE_URL = os.getenv("BRIDGE_BASE_URL") or os.getenv("BRH_BACKEND_URL") or "http://localhost:8000"
BRIDGE_NOTIFY = os.getenv("BRIDGE_URL", "https://sr-aibridge.netlify.app/api/diagnostics")
CONFIG_PATH = Path(__file__).parent.parent / "config" / "hooks.json"

# Skip HTTP calls during CI/build process to avoid blocking
IS_BUILD_ENV = os.getenv("CI") == "true" or os.getenv("NETLIFY") == "true"


def now_iso() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


def sign_body(body: str, secret: str) -> str:
    """Sign request body with HMAC-SHA256"""
    h = hmac.new(secret.encode(), body.encode('utf-8'), hashlib.sha256)
    return h.hexdigest()


def expand_magic_markers(obj: Any) -> Any:
    """Recursively expand magic markers like __NOW__ in payload"""
    if isinstance(obj, dict):
        return {k: expand_magic_markers(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [expand_magic_markers(item) for item in obj]
    elif obj == "__NOW__":
        return now_iso()
    return obj


def ping_hook(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ping a single hook endpoint and measure latency
    Returns status result with latency information
    """
    # Skip HTTP calls in build environments
    if IS_BUILD_ENV:
        return {
            "name": entry["name"],
            "status": "SKIPPED",
            "reason": "Build environment - HTTP checks disabled"
        }
    
    is_absolute = bool(entry.get("absoluteUrl"))
    target = entry["absoluteUrl"] if is_absolute else f"{BASE_URL}{entry['url']}"
    method = entry.get("method", "POST").upper()
    expect = entry.get("expectStatus", 200)
    
    headers = {"Content-Type": "application/json"}
    body_str = None
    
    # Prepare request body for non-GET requests
    if method != "GET":
        payload = entry.get("samplePayload", {})
        # Expand magic markers
        payload = expand_magic_markers(payload)
        body_str = json.dumps(payload)
        
        # Sign the payload if secret is configured
        signing_secret_env = entry.get("signingSecretEnv")
        if signing_secret_env:
            secret = os.getenv(signing_secret_env)
            if secret:
                headers["X-Bridge-Signature"] = sign_body(body_str, secret)
    
    # Attempt to ping with retries
    start_time = time.time()
    last_error = None
    
    for attempt in range(1, 4):  # 3 attempts
        try:
            response = requests.request(
                method=method,
                url=target,
                headers=headers,
                data=body_str,
                timeout=10,
                allow_redirects=False
            )
            
            elapsed_ms = int((time.time() - start_time) * 1000)
            
            # Check if status matches expectation
            status_ok = response.status_code == expect or (expect == 200 and response.ok)
            
            if status_ok:
                return {
                    "name": entry["name"],
                    "url": target,
                    "status": "OK",
                    "latencyMs": elapsed_ms,
                    "code": response.status_code
                }
            else:
                return {
                    "name": entry["name"],
                    "url": target,
                    "status": "FAILED",
                    "latencyMs": elapsed_ms,
                    "code": response.status_code,
                    "error": f"Expected {expect}, got {response.status_code}"
                }
        
        except Exception as e:
            last_error = str(e)
            if attempt < 3:
                time.sleep(attempt)  # Linear backoff: 1s, 2s
    
    # All attempts failed
    elapsed_ms = int((time.time() - start_time) * 1000)
    return {
        "name": entry["name"],
        "url": target,
        "status": "FAILED",
        "latencyMs": elapsed_ms,
        "error": last_error or "Unknown error"
    }


def notify_bridge(payload: Dict[str, Any]) -> None:
    """Send notification to Bridge diagnostics endpoint"""
    # Skip notifications in build environments
    if IS_BUILD_ENV:
        print(f"ℹ️  Skipping bridge notification (build environment)")
        return
        
    try:
        response = requests.post(
            BRIDGE_NOTIFY,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            print(f"✅ Bridge notified successfully")
        else:
            print(f"⚠️ Bridge returned {response.status_code}: {response.text}")
    except Exception as err:
        print(f"⚠️ Bridge notification failed: {err}")


def run_hooks_triage(manual: bool = False) -> Dict[str, Any]:
    """
    Run hooks triage checks
    Returns triage summary
    """
    timestamp = now_iso()
    
    # Load configuration
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load hooks config: {e}")
        return {
            "type": "HOOKS_TRIAGE",
            "status": "CRITICAL",
            "source": "HooksTriage",
            "manual": manual,
            "meta": {
                "timestamp": timestamp,
                "error": f"Config load failed: {str(e)}",
                "results": []
            }
        }
    
    print("🪝 Starting Hooks triage...")
    
    if IS_BUILD_ENV:
        print("ℹ️  Running in build environment - HTTP checks will be skipped")
    
    # Check each hook
    results = []
    for entry in config:
        result = ping_hook(entry)
        results.append(result)
        if result["status"] == "SKIPPED":
            status_icon = "⏭️"
        elif result["status"] == "OK":
            status_icon = "✅"
        else:
            status_icon = "❌"
        print(f"  {status_icon} {result['name']}: {result['status']}")
    
    # Calculate overall status
    skipped = [r for r in results if r["status"] == "SKIPPED"]
    failed = [r for r in results if r["status"] != "OK" and r["status"] != "SKIPPED"]
    
    if len(skipped) == len(results):
        overall = "SKIPPED"
    elif len(failed) == 0:
        overall = "HEALTHY"
    elif len(failed) <= 1:
        overall = "DEGRADED"
    else:
        overall = "CRITICAL"
    
    # Build report
    report = {
        "type": "HOOKS_TRIAGE",
        "status": overall,
        "source": "HooksTriage",
        "manual": manual,
        "meta": {
            "timestamp": timestamp,
            "buildEnvironment": IS_BUILD_ENV,
            "results": results,
            "environment": "backend"
        }
    }
    
    # Save to file
    report_path = Path(__file__).parent.parent / "hooks_triage_report.json"
    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"📄 Report saved to {report_path}")
    except Exception as err:
        print(f"⚠️ Failed to save report: {err}")
    
    # Notify Bridge
    notify_bridge(report)
    
    # Print summary
    print(f"\n📡 HOOKS_TRIAGE: {overall}")
    if failed:
        print("\n❌ Failed Hooks:")
        for f in failed:
            error_msg = f.get('error', f.get('code', 'Unknown error'))
            print(f"  - {f['name']}: {error_msg}")
    
    return report


if __name__ == "__main__":
    # Check for manual flag
    manual = "--manual" in sys.argv
    
    # Run triage
    report = run_hooks_triage(manual)
    
    # Exit with appropriate code (SKIPPED is not an error)
    if report["status"] == "CRITICAL":
        sys.exit(2)
    elif report["status"] == "DEGRADED":
        sys.exit(1)
    else:
        sys.exit(0)
