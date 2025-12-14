#!/usr/bin/env python3
import os, re, json, pathlib, requests
ROOT = pathlib.Path(__file__).resolve().parents[2]
FRONT = ROOT/"bridge-frontend"
BACK  = ROOT/"bridge_backend"
OUT   = ROOT/"bridge_backend/diagnostics/endpoint_api_sweep.json"

def routes_backend():
    rx = re.compile(r'@(?:router|app)\.(?:get|post|put|delete)\([\'"](/api[^\'"]+)')
    found=set()
    for p,_,fs in os.walk(BACK):
        for f in fs:
            if f.endswith(".py"):
                t=open(os.path.join(p,f),"r",encoding="utf-8",errors="ignore").read()
                found.update(rx.findall(t))
    return sorted(found)

def calls_frontend():
    patt = [
      re.compile(r'fetch\([\'"](/api[^\'"]+)'),
      re.compile(r'axios\.(?:get|post|put|delete)\([\'"](/api[^\'"]+)')
    ]
    found=set()
    for p,_,fs in os.walk(FRONT):
        for f in fs:
            if f.endswith((".js",".jsx",".ts",".tsx")):
                t=open(os.path.join(p,f),"r",encoding="utf-8",errors="ignore").read()
                for rx in patt: found.update(rx.findall(t))
    return sorted(found)

back = routes_backend()
front= calls_frontend()

missing_from_frontend = [r for r in back if not any(c.startswith(r) for c in front)]
missing_from_backend  = [c for c in front if not any(c.startswith(r) for r in back)]

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({
  "backend_routes": back,
  "frontend_calls": front,
  "missing_from_frontend": missing_from_frontend,
  "missing_from_backend": missing_from_backend
}, indent=2))
print("✅ endpoint sweep complete →", OUT)
