#!/usr/bin/env python3
import os, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT/"bridge_backend/diagnostics/env_parity_report.json"

# canonical list from docs/ENVIRONMENT_SETUP.md (or hard-coded fallback)
CANON = [
  "BRIDGE_API_URL","CASCADE_MODE","VAULT_URL",
  "REACT_APP_API_URL","VITE_API_BASE",
  "FEDERATION_SCHEMA_VERSION_DIAGNOSTICS",
  "FEDERATION_SCHEMA_VERSION_DEPLOY",
  "FEDERATION_SCHEMA_VERSION_TRIAGE"
]

def load_env_files():
    maps = {}
    for name in [".env",".env.production","bridge-frontend/.env.production",".env.netlify",".env.render"]:
        p = ROOT/name
        if p.exists():
            data={}
            for line in p.read_text().splitlines():
                m = re.match(r'\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$', line)
                if m: data[m.group(1)] = m.group(2)
            maps[name]=data
    return maps

envmaps = load_env_files()
report = { "canonical": CANON, "files": envmaps, "missing": {} }
for f, m in envmaps.items():
    miss = [k for k in CANON if k not in m]
    if miss: report["missing"][f]=miss

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(report, indent=2))
print("✅ env parity report →", OUT)
# Non-fatal; the Deploy Gate will enforce if needed
