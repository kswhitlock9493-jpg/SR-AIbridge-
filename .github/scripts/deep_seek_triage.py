#!/usr/bin/env python3
# Deep-Seek Federation Triage & Auto-Repair v1.8.1

import json, time, pathlib, os
from urllib.parse import urlparse
import requests

from _net import dns_warmup, http

ROOT    = pathlib.Path(__file__).resolve().parents[2]
FEDMAP  = ROOT / "bridge_backend" / "federation_map.json"
REPORT  = ROOT / "bridge_backend" / "diagnostics" / "federation_repair_report.json"

MAX_RETRIES = int(os.getenv("DEEPSEEK_MAX_RETRIES", "4"))
TIMEOUT     = int(os.getenv("DEEPSEEK_TIMEOUT", "8"))

def probe_schema(base, probe):
    meth, path = probe.split(":", 1)
    url = base.rstrip("/") + path
    r = http(meth, url, timeout=TIMEOUT)
    return r.status_code, r.text

def touch_cache(paths, payload):
    changed = []
    for p in paths:
        fp = ROOT / p
        fp.parent.mkdir(parents=True, exist_ok=True)
        before = fp.read_text() if fp.exists() else None
        data = payload if isinstance(payload, str) else json.dumps(payload, indent=2)
        fp.write_text(data)
        if before != data:
            changed.append(str(p))
    return changed

def attempt_live_call(name, conf):
    # Minimal no-op call that exercises the route safely
    if "deploy" in conf["endpoint"]:
        # dry-run deploy
        url = conf["endpoint"] + "/dryrun"
        return http("POST", url, json={"check": True}, timeout=TIMEOUT)
    elif "relay" in conf["endpoint"]:
        url = conf["endpoint"] + "/echo"
        return http("POST", url, json={"ping":"triage"}, timeout=TIMEOUT)
    else:
        return http("GET", conf["heartbeat"], timeout=TIMEOUT)

def deepseek_and_repair(name, conf):
    host = urlparse(conf["endpoint"]).hostname
    result = {
        "reachable": False,
        "schema_match": False,
        "latency_ms": None,
        "repairs": [],
        "errors": []
    }

    # DNS warm-up
    if not dns_warmup(host):
        result["errors"].append(f"DNS warmup failed for {host}")

    # Heartbeat & latency
    t0 = time.time()
    try:
        hb = http("GET", conf["heartbeat"], timeout=TIMEOUT)
        result["latency_ms"] = round((time.time() - t0)*1000, 2)
        result["reachable"] = hb.status_code == 200
    except Exception as e:
        result["errors"].append(f"HB error: {e}")

    # Schema probe compare
    try:
        sc, body = probe_schema(conf["endpoint"], conf["schema_probe"])
        if sc == 200 and conf["schema_version"] in body:
            result["schema_match"] = True
        else:
            # Try auto-repair: refresh local schema cache and suggest env bump
            cache_changes = touch_cache(conf["patch_targets"]["cache_files"], body)
            if cache_changes:
                result["repairs"] += [f"cache_refreshed:{x}" for x in cache_changes]
            result["errors"].append(
              f"Schema drift (want {conf['schema_version']}, probe {sc}); staged patch intent"
            )
    except Exception as e:
        result["errors"].append(f"Schema probe error: {e}")

    # Live call w/ exponential retry
    for i in range(MAX_RETRIES):
        try:
            resp = attempt_live_call(name, conf)
            if resp.status_code in (200, 201, 204):
                result["repairs"].append(f"live_call_ok@attempt_{i+1}")
                break
            else:
                result["errors"].append(f"live_call_status:{resp.status_code}")
        except Exception as e:
            result["errors"].append(f"live_call_error:{e}")
        if i < MAX_RETRIES - 1:  # Don't sleep after the last retry
            time.sleep(0.4 * (2 ** i))

    # Emit patch intents (non-destructive): federated env bumps
    if not result["schema_match"]:
        envs = conf["patch_targets"].get("backend_env", [])
        if envs:
            result["repairs"].append(
              f"intent:update_env:{envs}=>{conf['schema_version']}"
            )

    return result

def main():
    print("Starting Federation Deep-Seek...")
    
    # Check if running in safe placeholder mode (no external connectivity expected)
    safe_mode = os.getenv("SAFE_PLACEHOLDER_MODE", "false").lower() == "true"
    if safe_mode:
        print("⚠️  Running in SAFE PLACEHOLDER MODE - skipping external federation checks")
        report = {
            "generated_at": int(time.time()),
            "mode": "safe_placeholder",
            "health": {},
            "details": {},
            "message": "Safe placeholder mode active - external federation checks skipped"
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(json.dumps(report, indent=2))
        print("✅ Federation Deep-Seek report (safe mode) →", REPORT)
        return 0
    
    fedmap = json.loads(FEDMAP.read_text())
    print(f"Loaded {len(fedmap)} federation nodes")
    summary = {}
    for name, conf in fedmap.items():
        print(f"Processing {name}...")
        summary[name] = deepseek_and_repair(name, conf)
        print(f"  Result: {summary[name].get('reachable', 'unknown')}")

    # Health classification
    health = {
        k: ("PASS" if v["reachable"] and (v["schema_match"] or "live_call_ok" in "".join(v["repairs"])) else "FAIL")
        for k, v in summary.items()
    }

    report = {
        "generated_at": int(time.time()),
        "mode": "production",
        "health": health,
        "details": summary
    }

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2))
    print("✅ Federation Deep-Seek report →", REPORT)
    for k, v in health.items():
        print(f" - {k}: {v}")

    # Exit code: fail only if ALL fail
    if all(v == "FAIL" for v in health.values()):
        raise SystemExit(2)

if __name__ == "__main__":
    main()
