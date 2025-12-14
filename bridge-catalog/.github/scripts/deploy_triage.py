#!/usr/bin/env python3
import json, pathlib, glob
OUT = pathlib.Path("bridge_backend/diagnostics/total_stack_report.json")
def readj(p): 
    try: return json.loads(pathlib.Path(p).read_text())
    except: return {}
fed = readj("bridge_backend/diagnostics/federation_repair_report.json")
bld = readj("bridge_backend/diagnostics/build_triage_report.json")
run = readj("bridge_backend/diagnostics/runtime_triage_report.json")
eps = readj("bridge_backend/diagnostics/endpoint_api_sweep.json")
env = readj("bridge_backend/diagnostics/env_parity_report.json")

rollup = {
  "federation": fed, "build": bld, "runtime": run,
  "endpoints": eps, "env": env
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rollup, indent=2))
print("📦 total_stack_report.json written")
