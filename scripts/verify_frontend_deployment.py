#!/usr/bin/env python3
"""
Deployment Verification Script for SR-AIbridge Frontend
Validates that the frontend is properly configured and ready for Netlify deployment
"""
import os
import sys
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_dist_directory():
    """Verify dist directory has required files"""
    dist_path = Path("bridge-frontend/dist")
    if not dist_path.exists():
        print("❌ Dist directory not found. Run 'npm run build' first.")
        return False
    
    required_files = [
        "index.html",
        "_headers",
        "_redirects"
    ]
    
    all_exist = True
    for file in required_files:
        filepath = dist_path / file
        if filepath.exists():
            print(f"✅ Dist file exists: {file}")
        else:
            print(f"❌ Dist file MISSING: {file}")
            all_exist = False
    
    # Check for JavaScript assets
    assets_path = dist_path / "assets"
    if assets_path.exists():
        js_files = list(assets_path.glob("*.js"))
        css_files = list(assets_path.glob("*.css"))
        print(f"✅ Assets: {len(js_files)} JS files, {len(css_files)} CSS files")
    else:
        print("❌ Assets directory missing")
        all_exist = False
    
    return all_exist

def check_netlify_config():
    """Verify netlify.toml configuration"""
    netlify_toml = Path("netlify.toml")
    if not netlify_toml.exists():
        print("❌ netlify.toml not found")
        return False
    
    content = netlify_toml.read_text()
    
    checks = {
        "publish directory": 'publish = "bridge-frontend/dist"',
        "functions directory": 'directory = "netlify/functions"',
        "SPA redirect": 'to = "/index.html"',
        "security headers": 'X-Frame-Options = "SAMEORIGIN"'
    }
    
    all_passed = True
    for name, pattern in checks.items():
        if pattern in content:
            print(f"✅ Netlify config has {name}")
        else:
            print(f"⚠️  Netlify config missing {name}")
            all_passed = False
    
    return all_passed

def check_environment_config():
    """Check environment configuration files"""
    checks = [
        ("bridge-frontend/.env.production", "Production environment"),
        ("bridge-frontend/.env.example", "Environment template"),
    ]
    
    all_exist = True
    for filepath, description in checks:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    # Check production env has required variables
    prod_env = Path("bridge-frontend/.env.production")
    if prod_env.exists():
        content = prod_env.read_text()
        required_vars = ["VITE_API_BASE", "REACT_APP_API_URL"]
        for var in required_vars:
            if var in content:
                print(f"  ✅ Has {var}")
            else:
                print(f"  ⚠️  Missing {var}")
    
    return all_exist

def check_frontend_config():
    """Verify frontend config.js is properly set up"""
    config_path = Path("bridge-frontend/src/config.js")
    if not config_path.exists():
        print("❌ Frontend config.js not found")
        return False
    
    content = config_path.read_text()
    
    # Check for production-aware configuration
    checks = [
        ("VITE_API_BASE", "Vite API base variable"),
        ("REACT_APP_API_URL", "React API URL variable"),
        ("bridge.sr-aibridge.com", "Production backend URL"),
        ("getApiBase", "Smart API detection function")
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ Config has {description}")
        else:
            print(f"⚠️  Config missing {description}")
            all_passed = False
    
    return all_passed

def check_github_workflow():
    """Verify GitHub Actions deployment workflow"""
    workflow_path = Path(".github/workflows/deploy.yml")
    if not workflow_path.exists():
        print("❌ Deployment workflow not found")
        return False
    
    content = workflow_path.read_text()
    
    checks = [
        ("deploy-frontend", "Frontend deployment job"),
        ("VITE_API_BASE", "Vite API base env var"),
        ("REACT_APP_API_URL", "React API URL env var"),
        ("bridge-frontend/dist", "Correct publish directory"),
        ("NETLIFY_AUTH_TOKEN", "Netlify authentication")
    ]
    
    all_passed = True
    for pattern, description in checks:
        if pattern in content:
            print(f"✅ Workflow has {description}")
        else:
            print(f"⚠️  Workflow missing {description}")
            all_passed = False
    
    return all_passed

def main():
    """Run all verification checks"""
    print("=" * 70)
    print("SR-AIbridge Frontend Deployment Verification")
    print("=" * 70)
    print()
    
    checks = [
        ("Frontend Configuration", check_frontend_config),
        ("Environment Configuration", check_environment_config),
        ("Dist Directory", check_dist_directory),
        ("Netlify Configuration", check_netlify_config),
        ("GitHub Workflow", check_github_workflow)
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        print("-" * 70)
        results[name] = check_func()
        print()
    
    print("=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! Frontend is ready for deployment.")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
