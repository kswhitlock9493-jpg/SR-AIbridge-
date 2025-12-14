#!/usr/bin/env python3
import os, sys, json, hmac, hashlib, urllib.request

secret = os.getenv("TELEMETRY_SIGNING_SECRET", "")
webhook = os.getenv("TELEMETRY_ENDPOINT",
                    "https://sr-aibridge.netlify.app/.netlify/functions/telemetry")

payload = {
  "type": os.getenv("BRIDGE_EVENT_TYPE", "DIAGNOSTIC"),
  "status": os.getenv("BRIDGE_EVENT_STATUS", "UNKNOWN"),
  "details": os.getenv("BRIDGE_EVENT_DETAILS", ""),
}

raw = json.dumps(payload).encode("utf-8")
sig = "sha256=" + hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()

req = urllib.request.Request(webhook, data=raw, method="POST",
    headers={"content-type": "application/json", "X-Bridge-Signature": sig})

try:
    with urllib.request.urlopen(req, timeout=8) as r:
        print("Telemetry delivered:", r.status)
        sys.exit(0)
except Exception as e:
    print("Telemetry failed:", e)
    sys.exit(1)
