#!/usr/bin/env python3
import os, time, json, random, urllib.request, urllib.error

DEFAULT_TIMEOUT = int(os.getenv("TRIAGE_TIMEOUT_MS", "8000")) / 1000.0
MAX_RETRIES = int(os.getenv("TRIAGE_MAX_RETRIES", "4"))
BACKOFF_BASE = float(os.getenv("TRIAGE_BACKOFF_BASE", "0.8"))  # seconds
BACKOFF_FACTOR = float(os.getenv("TRIAGE_BACKOFF_FACTOR", "2.0"))
JITTER_MAX = float(os.getenv("TRIAGE_JITTER_MAX", "0.35"))
CIRCUIT_FAILS = int(os.getenv("TRIAGE_CIRCUIT_BREAKER_FAILS", "6"))

def http_get(url: str, timeout: float = DEFAULT_TIMEOUT):
    req = urllib.request.Request(url, headers={"User-Agent": "SR-AIbridge-Triage/1.7.5"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.getcode(), resp.read()

def retrying_check(url: str, expect=200):
    failures = 0
    last_err = "unknown"
    last_code = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            code, _ = http_get(url)
            last_code = code
            if code == expect:
                return {"ok": True, "attempts": attempt, "code": code}
            failures += 1
            last_err = f"unexpected status code {code}"
        except Exception as e:
            failures += 1
            last_err = str(e)
        if failures >= CIRCUIT_FAILS:
            break
        # backoff + jitter
        sleep_s = BACKOFF_BASE * (BACKOFF_FACTOR ** (attempt - 1))
        sleep_s += random.uniform(0, JITTER_MAX)
        time.sleep(sleep_s)
    return {"ok": False, "attempts": attempt, "code": last_code, "error": last_err}
