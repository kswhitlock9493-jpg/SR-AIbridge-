#!/usr/bin/env python3
"""
Build Triage Sentinel v1.7.9
- Enforces Node 20
- Ensures devDependencies install (even if NODE_ENV=production)
- Suppresses secret scan false-positives (without turning it off)
- Detects inline env leaks in dist and warns
- Falls back to npm mirror if registry hiccups detected
- Writes diagnostics to bridge_backend/diagnostics/build_triage_report.json
"""

import json, os, re, subprocess, sys, pathlib, shutil

ROOT = pathlib.Path(__file__).resolve().parents[2]
FRONT = ROOT / "bridge-frontend"
DIAG_DIR = ROOT / "bridge_backend" / "diagnostics"
REPORT = DIAG_DIR / "build_triage_report.json"

def run(cmd, cwd=None, check=True):
    print(f"» {' '.join(cmd)}")
    p = subprocess.run(cmd, cwd=cwd or FRONT, text=True, capture_output=True)
    if check and p.returncode != 0:
        print(p.stdout)
        print(p.stderr, file=sys.stderr)
        raise SystemExit(p.returncode)
    return p

def ensure_node20():
    # Netlify uses NODE_VERSION or .nvmrc; we enforce both
    enforced = False
    os.environ["NODE_VERSION"] = "20"
    nvmrc = ROOT / ".nvmrc"
    if not nvmrc.exists() or nvmrc.read_text().strip() != "20":
        nvmrc.write_text("20\n")
        enforced = True
    return enforced

def force_devdeps():
    # Netlify sometimes sets NODE_ENV=production at install time
    os.environ["NPM_CONFIG_PRODUCTION"] = "false"
    # Skip puppeteer downloads to avoid build failures
    os.environ["PUPPETEER_SKIP_DOWNLOAD"] = "true"
    os.environ["PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD"] = "true"
    return True

SECRET_PATTERNS = [
    r"(?i)api[_-]?key\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]",
    r"(?i)secret\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]",
    r"(?i)token\s*[:=]\s*['\"][A-Za-z0-9_\-]{12,}['\"]"
]

def scan_inline_secrets():
    leaks = []
    dist = FRONT / "dist"
    for base in [FRONT, dist]:
        if not base.exists(): 
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in {".js", ".map", ".html"}:
                try:
                    text = p.read_text(errors="ignore")
                except Exception:
                    continue
                for pat in SECRET_PATTERNS:
                    if re.search(pat, text):
                        leaks.append(str(p.relative_to(ROOT)))
                        break
    return leaks

def safe_install_with_mirror():
    # first attempt
    p = run(["npm", "ci", "--no-audit", "--prefer-offline"], check=False)
    if p.returncode == 0:
        return {"attempts": 1, "mirror": False, "status": "ok"}

    # common npm errors indicating registry issues
    if any(sig in (p.stdout + p.stderr) for sig in ["E404", "ENOTFOUND", "ECONNRESET"]):
        # fallback to GitHub mirror for @netlify/*, etc.
        run(["bash", "bridge-frontend/scripts/repair_npm_registry.sh"])
        run(["npm", "ci", "--no-audit", "--prefer-offline"])
        return {"attempts": 2, "mirror": True, "status": "ok"}

    # if it's another error, fail fast (keeps signal)
    print(p.stdout)
    print(p.stderr, file=sys.stderr)
    raise SystemExit(p.returncode)

def main():
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    node_pinned = ensure_node20()
    devdeps_forced = force_devdeps()
    install = safe_install_with_mirror()
    # run vite in the actual build command; we only triage here

    leaks = scan_inline_secrets()

    report = {
        "node_enforced_20": node_pinned,
        "devDependencies_forced": devdeps_forced,
        "install": install,
        "inline_secret_leaks_detected": len(leaks),
        "leak_paths": leaks
    }
    REPORT.write_text(json.dumps(report, indent=2))
    print(f"✅ Build triage report → {REPORT}")

    # Do not hard-fail on leaks, but warn loudly. The Netlify secret scan remains on (log level=error).
    if leaks:
        print("⚠️  Inline-looking secrets detected in build or src. Review leak_paths in report.", file=sys.stderr)

if __name__ == "__main__":
    main()
