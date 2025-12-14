#!/usr/bin/env python3
"""
Bridge Parity Engine v1.6.9 — with Triage
Analyzes backend↔frontend parity for SR-AIbridge and classifies issues by severity.
"""

import os, re, json, pathlib, hashlib, time, asyncio

ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND = ROOT / "bridge_backend"
FRONTEND = ROOT / "bridge-frontend"
REPORT = ROOT / "bridge_backend/diagnostics/bridge_parity_report.json"

def _read(path):
    try:
        return open(path, "r", encoding="utf-8", errors="ignore").read()
    except Exception:
        return ""

def collect_backend_routes():
    routes=set()
    prefixes={}
    for path,_,files in os.walk(BACKEND):
        for f in files:
            if f.endswith(".py"):
                filepath=os.path.join(path,f)
                text=_read(filepath)
                # Extract router prefix
                prefix_match=re.search(r'router\s*=\s*APIRouter\([^)]*prefix=["\'](.*?)["\']',text)
                file_prefix=prefix_match.group(1) if prefix_match else ""
                # Find route decorators
                for match in re.finditer(r'@router\.(get|post|put|delete|patch)\(["\'](.*?)["\']',text):
                    route_path=match.group(2)
                    full_path=file_prefix+route_path if route_path.startswith("/") else file_prefix+"/"+route_path
                    routes.add(full_path)
                # Also catch Flask-style routes
                routes.update(re.findall(r'@app\.route\(["\'](.*?)["\']',text))
                routes.update(re.findall(r'Blueprint\(["\'](.*?)["\']',text))
    return sorted(routes)

def collect_frontend_calls():
    calls=set()
    for path,_,files in os.walk(FRONTEND):
        for f in files:
            if f.endswith((".js",".jsx",".ts",".tsx")):
                text=_read(os.path.join(path,f))
                # Extract full URLs
                calls.update(re.findall(r'https?://[^\s"\']+',text))
                # Extract fetch calls
                calls.update(re.findall(r'fetch\(["\']([^"\']+)["\']',text))
                # Extract axios calls
                for match in re.finditer(r'axios\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',text):
                    calls.add(match.group(2))
                # Extract apiClient calls
                for match in re.finditer(r'apiClient\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',text):
                    calls.add(match.group(2))
    return sorted(calls)

def triage_issue(route:str,missing_side:str)->dict:
    sev="critical" if "/api/" in route else "moderate"
    if "diagnostics" in route or "health" in route:
        sev="informational"
    hint={
        "critical":"Verify endpoint implementation and client hook.",
        "moderate":"Check for deprecated route or unused API.",
        "informational":"Confirm monitoring is enabled."
    }[sev]
    return {"route":route,"missing":missing_side,"severity":sev,"hint":hint}

async def publish_parity_event(report):
    """Publish parity event to genesis bus for autonomy engine integration"""
    try:
        import sys
        sys.path.insert(0, str(ROOT / "bridge_backend"))
        from genesis.bus import genesis_bus
        
        if genesis_bus.is_enabled():
            await genesis_bus.publish("parity.check", {
                "type": "parity_check",
                "source": "parity",
                "report": report,
            })
    except Exception as e:
        # Silently fail if genesis bus not available (e.g., during CI)
        pass

def analyze():
    backend=collect_backend_routes()
    frontend=collect_frontend_calls()
    prefix=os.getenv("BACKEND_URL", "https://bridge.sr-aibridge.com")
    # Normalize frontend calls - extract paths and remove query strings
    normalized=[]
    for c in frontend:
        # Remove base URL if present
        path = c.replace(prefix,"")
        # Remove query strings
        path = path.split("?")[0]
        # Only keep paths that look like API endpoints
        if path.startswith("/") and not path.startswith("http"):
            normalized.append(path)
    normalized = sorted(set(normalized))

    miss_front=[triage_issue(r,"frontend") for r in backend if not any(r in f or f in r for f in normalized)]
    miss_back=[triage_issue(f,"backend") for f in normalized if not any(f.startswith(r.split("{")[0]) or r.startswith(f) for r in backend)]

    summary={
        "timestamp":time.strftime("%Y-%m-%d %H:%M:%S UTC",time.gmtime()),
        "backend_routes":len(backend),
        "frontend_calls":len(frontend),
        "missing_from_frontend":len(miss_front),
        "missing_from_backend":len(miss_back),
        "hash":hashlib.md5(("".join(backend)+ "".join(frontend)).encode()).hexdigest()
    }

    report={
        "summary":summary,
        "missing_from_frontend":miss_front,
        "missing_from_backend":miss_back,
        "backend_routes":backend,
        "frontend_calls":frontend
    }

    REPORT.parent.mkdir(parents=True,exist_ok=True)
    with open(REPORT,"w") as f: json.dump(report,f,indent=2)
    print("✅ Bridge Parity & Triage Report →",REPORT)
    
    # Publish event to genesis bus for autonomy integration
    try:
        asyncio.run(publish_parity_event(report))
    except Exception:
        pass  # Ignore errors in event publishing
    
    return report

if __name__=="__main__": analyze()
