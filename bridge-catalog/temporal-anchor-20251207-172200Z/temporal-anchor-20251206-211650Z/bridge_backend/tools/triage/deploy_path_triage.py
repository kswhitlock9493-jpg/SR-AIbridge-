#!/usr/bin/env python3
"""
Bridge Deploy Path Triage Engine v1.7.4
Validates Netlify publish paths, auto-repairs builds, and updates health badges.
"""

import os
import json
import subprocess
import pathlib
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parents[3]
FRONTEND = ROOT / "bridge-frontend"
DIST = FRONTEND / "dist"
DIAG_DIR = ROOT / "bridge_backend" / "diagnostics"
REPORT = DIAG_DIR / "deploy_path_triage_report.json"
BADGE_FILE = ROOT / "docs" / "BADGE_DEPLOY_STATUS.md"

def run_build():
    print("⚙️  Missing dist/ — running npm build...")
    try:
        subprocess.run(["npm", "install"], cwd=FRONTEND, check=True)
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND, check=True)
        return DIST.exists()
    except subprocess.CalledProcessError:
        return False

def generate_badge(status: str):
    color = "brightgreen" if status == "verified" else "yellow" if status == "rebuilt" else "red"
    badge = f"![Netlify Deploy Status](https://img.shields.io/badge/Netlify_{status}-{color}?style=for-the-badge)"
    BADGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(BADGE_FILE, "w") as f:
        f.write(f"# Netlify Health Badge\n\n{badge}\n\nUpdated: {datetime.now(timezone.utc).isoformat()} UTC\n")
    return badge

def verify_and_heal():
    exists = DIST.exists()
    status = "verified" if exists else "rebuilt" if run_build() else "failed"

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "frontend": str(FRONTEND),
        "dist": str(DIST),
        "status": status,
        "message": (
            "✅ Verified deploy directory."
            if status == "verified"
            else "🩹 Auto-repair succeeded."
            if status == "rebuilt"
            else "❌ Build failed — manual intervention required."
        ),
    }

    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT, "w") as f:
        json.dump(report, f, indent=2)

    badge = generate_badge(status)
    print(report["message"])
    print(f"Badge generated: {badge}")
    return report

if __name__ == "__main__":
    verify_and_heal()
