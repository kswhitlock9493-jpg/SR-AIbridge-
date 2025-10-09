#!/usr/bin/env python3
import json, time, pathlib, os
from _net import http, dns_warmup
BASE = os.getenv("RENDER_BASE","https://sr-aibridge.onrender.com")
HEALTH = f"{BASE}/api/health"
DB     = f"{BASE}/api/db/ping"
MIGR   = f"{BASE}/api/db/migrate?dryrun=1"
REPORT = pathlib.Path("bridge_backend/diagnostics/runtime_triage_report.json")
def main():
    host = BASE.split("/")[2]
    dns = dns_warmup(host)
    h = http("GET", HEALTH, timeout=8)
    db = http("GET", DB,     timeout=8)
    mg = http("POST", MIGR,  timeout=12)
    out = {
      "dns_ok": dns, "health": h.status_code,
      "db_ping": db.status_code, "migrate_dryrun": mg.status_code
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(out, indent=2))
    print(out)
    if not(dns and h.status_code==200 and db.status_code==200):
        raise SystemExit(2)
if __name__=="__main__": main()
