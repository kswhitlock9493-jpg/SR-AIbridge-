#!/usr/bin/env python3
"""
Chromium Probe - Build Environment Diagnostics
Part of Firewall Harmony v1.7.6

Generates structured diagnostic report for Chromium-dependent builds
"""

import json
import os
import sys
import platform
import subprocess
from pathlib import Path

def get_runner_info():
    """Get runner/environment information"""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }

def get_environment_variables():
    """Get relevant environment variables"""
    env_vars = {}
    relevant_vars = [
        "PUPPETEER_SKIP_DOWNLOAD",
        "PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD",
        "CHROMIUM_DOWNLOAD_ALLOWED",
        "CHROMIUM_CHANNEL",
        "PUPPETEER_CACHE_DIR",
        "PLAYWRIGHT_BROWSERS_PATH",
        "PUPPETEER_EXECUTABLE_PATH",
        "CI",
        "GITHUB_ACTIONS",
        "NETLIFY",
        "RENDER"
    ]
    
    for var in relevant_vars:
        env_vars[var] = os.getenv(var, "not set")
    
    return env_vars

def check_paths():
    """Check for browser cache and executable paths"""
    paths = {}
    
    # Puppeteer cache
    puppeteer_cache = os.getenv("PUPPETEER_CACHE_DIR", os.path.expanduser("~/.cache/puppeteer"))
    paths["puppeteer_cache"] = {
        "path": puppeteer_cache,
        "exists": os.path.exists(puppeteer_cache)
    }
    
    # Playwright cache
    playwright_cache = os.getenv("PLAYWRIGHT_BROWSERS_PATH", os.path.expanduser("~/.cache/ms-playwright"))
    paths["playwright_cache"] = {
        "path": playwright_cache,
        "exists": os.path.exists(playwright_cache)
    }
    
    # System Chrome locations
    chrome_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/snap/bin/chromium"
    ]
    
    paths["system_chrome"] = []
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            paths["system_chrome"].append({
                "path": chrome_path,
                "exists": True
            })
    
    return paths

def determine_strategy():
    """Determine which browser strategy is being used"""
    paths = check_paths()
    
    # Check cache first
    if paths["puppeteer_cache"]["exists"] or paths["playwright_cache"]["exists"]:
        return "cache"
    
    # Check system Chrome
    if paths["system_chrome"]:
        return "system-chrome"
    
    # Check if downloads are allowed
    if os.getenv("CHROMIUM_DOWNLOAD_ALLOWED") == "true":
        return "controlled-download"
    
    return "downloads-disabled"

def check_node_modules():
    """Check if browser automation packages are installed"""
    packages = {}
    
    try:
        result = subprocess.run(
            ["npm", "list", "puppeteer", "--depth=0"],
            capture_output=True,
            text=True,
            cwd="/home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge-frontend"
        )
        packages["puppeteer"] = "installed" if result.returncode == 0 else "not installed"
    except Exception as e:
        packages["puppeteer"] = f"error: {str(e)}"
    
    try:
        result = subprocess.run(
            ["npm", "list", "@playwright/test", "--depth=0"],
            capture_output=True,
            text=True,
            cwd="/home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge-frontend"
        )
        packages["playwright"] = "installed" if result.returncode == 0 else "not installed"
    except Exception as e:
        packages["playwright"] = f"error: {str(e)}"
    
    return packages

def main():
    """Generate diagnostic report"""
    report = {
        "version": "1.7.6",
        "timestamp": subprocess.check_output(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"]).decode().strip(),
        "runner": get_runner_info(),
        "env": get_environment_variables(),
        "paths": check_paths(),
        "strategy": determine_strategy(),
        "packages": check_node_modules()
    }
    
    # Output JSON
    print(json.dumps(report, indent=2))
    
    # Summary
    print("\n" + "=" * 60, file=sys.stderr)
    print("🔍 Chromium Probe Summary", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"Strategy: {report['strategy']}", file=sys.stderr)
    print(f"Runner: {report['runner']['platform']}", file=sys.stderr)
    print(f"Puppeteer Cache: {'✅' if report['paths']['puppeteer_cache']['exists'] else '❌'}", file=sys.stderr)
    print(f"Playwright Cache: {'✅' if report['paths']['playwright_cache']['exists'] else '❌'}", file=sys.stderr)
    print(f"System Chrome: {'✅' if report['paths']['system_chrome'] else '❌'}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

if __name__ == "__main__":
    main()
