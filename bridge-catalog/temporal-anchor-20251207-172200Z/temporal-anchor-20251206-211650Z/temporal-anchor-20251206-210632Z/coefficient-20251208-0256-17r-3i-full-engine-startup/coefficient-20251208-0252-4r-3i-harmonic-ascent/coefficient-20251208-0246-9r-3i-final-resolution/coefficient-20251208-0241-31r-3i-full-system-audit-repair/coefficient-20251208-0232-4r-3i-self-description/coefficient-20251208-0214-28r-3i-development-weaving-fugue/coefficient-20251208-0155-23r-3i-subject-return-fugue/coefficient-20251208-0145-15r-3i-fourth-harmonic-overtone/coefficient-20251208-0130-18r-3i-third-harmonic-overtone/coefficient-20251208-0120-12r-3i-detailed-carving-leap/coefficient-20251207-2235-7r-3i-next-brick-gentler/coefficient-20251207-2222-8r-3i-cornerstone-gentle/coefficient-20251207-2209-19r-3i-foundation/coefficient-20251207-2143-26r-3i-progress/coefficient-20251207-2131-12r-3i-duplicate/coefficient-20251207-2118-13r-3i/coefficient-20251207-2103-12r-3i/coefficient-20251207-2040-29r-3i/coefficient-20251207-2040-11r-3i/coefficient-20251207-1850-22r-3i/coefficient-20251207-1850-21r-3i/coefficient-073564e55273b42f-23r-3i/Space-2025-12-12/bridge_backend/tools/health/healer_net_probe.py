#!/usr/bin/env python3
import os
import json
import glob
import platform
from datetime import datetime, timezone

def load_json(path):
    try:
        with open(path) as f: return json.load(f)
    except: return {}

def aggregate_health():
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runner": platform.node(),
        "systems": {},
        "summary": {"healthy": True, "issues": 0},
    }

    # Collect from existing subsystems
    probes = glob.glob("**/*probe*.json", recursive=True)
    for path in probes:
        data = load_json(path)
        name = os.path.basename(path).replace(".json","")
        report["systems"][name] = data
        if "strategy" in str(data) and "downloads-disabled" in str(data):
            report["summary"]["issues"] += 1
        if "status" in data and data["status"] != "ok":
            report["summary"]["issues"] += 1

    if report["summary"]["issues"] > 0:
        report["summary"]["healthy"] = False

    with open("healer_net_report.json","w") as f:
        json.dump(report,f,indent=2)
    print(json.dumps(report,indent=2))

if __name__ == "__main__":
    aggregate_health()
