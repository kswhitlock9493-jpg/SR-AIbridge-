#!/usr/bin/env python3
# v1.8.3 Netlify Config Triage — validates & gently repairs redirects/headers/publish
import pathlib, json, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
FRONT = ROOT / "bridge-frontend"
NTL   = ROOT / "netlify.toml"
RDR   = FRONT / "_redirects"
HDR   = FRONT / "_headers"
OUT   = ROOT / "bridge_backend" / "diagnostics" / "netlify_config_report.json"

def _exists(p): return p.exists() and p.is_file()

def validate_toml(text: str):
    issues=[]
    if 'publish = "bridge-frontend/dist"' not in text:
        issues.append("publish path not set to bridge-frontend/dist")
    if "[[redirects]]" not in text:
        issues.append("missing [[redirects]] block for SPA fallback")
    if 'status = 200' not in text and "200!" not in text:
        issues.append("SPA fallback not forcing 200")
    return issues

def normalize_redirects():
    fixed=[]
    if not _exists(RDR):
        return fixed
    lines = [l.rstrip() for l in RDR.read_text(encoding="utf-8", errors="ignore").splitlines()]
    # Ensure every rule has at least "from to status"
    new=[]
    for l in lines:
        if l.strip()=="" or l.strip().startswith("#"):
            new.append(l); continue
        parts = l.split()
        if len(parts) == 1 and parts[0].startswith("/"):
            # turn "/path" into "/path /index.html 200!"
            l = f"{parts[0]} /index.html 200!"
            fixed.append(f"completed rule: {l}")
        new.append(l)
    RDR.write_text("\n".join(new) + "\n", encoding="utf-8")
    return fixed

def ensure_headers():
    created=False
    if not _exists(HDR):
        HDR.write_text(
            "/*\n"
            "  X-Frame-Options: DENY\n"
            "  X-Content-Type-Options: nosniff\n"
            "  Referrer-Policy: strict-origin-when-cross-origin\n"
            "  Permissions-Policy: geolocation=(), camera=(), microphone=()\n",
            encoding="utf-8"
        )
        created=True
    return created

def main():
    report={"toml_issues":[], "redirects_fixes":[], "headers_created": False, "ok": True}
    if _exists(NTL):
        t=NTL.read_text(encoding="utf-8", errors="ignore")
        report["toml_issues"] = validate_toml(t)
    else:
        report["toml_issues"].append("netlify.toml missing")

    report["redirects_fixes"] = normalize_redirects()
    report["headers_created"] = ensure_headers()

    report["ok"] = len(report["toml_issues"])==0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["ok"] else 2)

if __name__ == "__main__":
    main()
