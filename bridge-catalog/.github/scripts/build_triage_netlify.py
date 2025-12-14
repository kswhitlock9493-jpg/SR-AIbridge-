#!/usr/bin/env python3
"""
Build Triage (Netlify) - Optional local-use script
Auto-repair behaviors:
- Normalizes netlify.toml publish path → bridge-frontend/dist
- Adds missing [[redirects]] → SPA fallback to /index.html
- Adds @netlify/functions-core only if functions dir exists
"""

import json, pathlib, os, re

ROOT = pathlib.Path(__file__).resolve().parents[2]
NETLIFY_TOML = ROOT / "netlify.toml"
PACKAGE_JSON = ROOT / "bridge-frontend" / "package.json"
FUNCTIONS_DIR = ROOT / "bridge-frontend" / "netlify" / "functions"
REPORT = ROOT / "bridge_backend" / "diagnostics" / "build_triage_report.json"

def normalize_netlify_toml():
    """Ensure netlify.toml has correct publish path and SPA redirects"""
    changes = []
    
    if not NETLIFY_TOML.exists():
        print("⚠️  netlify.toml not found, skipping normalization")
        return changes
    
    content = NETLIFY_TOML.read_text()
    original = content
    
    # Normalize publish path
    if 'publish = "dist"' in content:
        content = content.replace('publish = "dist"', 'publish = "bridge-frontend/dist"')
        changes.append("normalized_publish_path")
    
    # Add SPA redirect if missing
    if "[[redirects]]" not in content:
        redirect_block = '\n\n[[redirects]]\n  from = "/*"\n  to = "/index.html"\n  status = 200\n'
        content += redirect_block
        changes.append("added_spa_redirect")
    
    if content != original:
        NETLIFY_TOML.write_text(content)
        print(f"✅ Updated netlify.toml: {', '.join(changes)}")
    
    return changes

def check_functions_dependency():
    """Add @netlify/functions-core if functions directory exists"""
    changes = []
    
    if not PACKAGE_JSON.exists():
        print("⚠️  package.json not found")
        return changes
    
    pkg = json.loads(PACKAGE_JSON.read_text())
    
    # Check if functions dir exists
    if FUNCTIONS_DIR.exists():
        deps = pkg.get("devDependencies", {})
        if "@netlify/functions" not in deps:
            print("ℹ️  Functions directory exists but @netlify/functions not in devDependencies")
            print("   Add it manually: npm install --save-dev @netlify/functions")
            changes.append("intent:add_netlify_functions_dep")
    
    return changes

def generate_report():
    """Generate build triage report"""
    dist_path = ROOT / "bridge-frontend" / "dist"
    
    out = {
        "has_dist": dist_path.exists(),
        "size_kb": 0,
        "missing_scripts": False,
        "repairs": []
    }
    
    if dist_path.exists():
        total_size = sum(f.stat().st_size for f in dist_path.rglob("*") if f.is_file())
        out["size_kb"] = total_size // 1024
    
    if PACKAGE_JSON.exists():
        pkg_text = PACKAGE_JSON.read_text()
        out["missing_scripts"] = '"build"' not in pkg_text
    
    # Run auto-repair
    netlify_changes = normalize_netlify_toml()
    functions_changes = check_functions_dependency()
    
    out["repairs"] = netlify_changes + functions_changes
    
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(out, indent=2))
    
    print(f"\n📊 Build Triage Report:")
    print(f"   Has dist: {out['has_dist']}")
    print(f"   Size: {out['size_kb']} KB")
    print(f"   Missing build script: {out['missing_scripts']}")
    print(f"   Repairs: {out['repairs']}")
    print(f"\n✅ Report saved to {REPORT}")
    
    return out

def main():
    print("🔧 Build Triage (Netlify) - Local Mode\n")
    report = generate_report()
    
    # Exit with error if critical issues found
    if not report["has_dist"] or report["missing_scripts"]:
        print("\n❌ Critical build issues detected")
        raise SystemExit(1)
    
    print("\n✅ Build triage complete")

if __name__ == "__main__":
    main()
