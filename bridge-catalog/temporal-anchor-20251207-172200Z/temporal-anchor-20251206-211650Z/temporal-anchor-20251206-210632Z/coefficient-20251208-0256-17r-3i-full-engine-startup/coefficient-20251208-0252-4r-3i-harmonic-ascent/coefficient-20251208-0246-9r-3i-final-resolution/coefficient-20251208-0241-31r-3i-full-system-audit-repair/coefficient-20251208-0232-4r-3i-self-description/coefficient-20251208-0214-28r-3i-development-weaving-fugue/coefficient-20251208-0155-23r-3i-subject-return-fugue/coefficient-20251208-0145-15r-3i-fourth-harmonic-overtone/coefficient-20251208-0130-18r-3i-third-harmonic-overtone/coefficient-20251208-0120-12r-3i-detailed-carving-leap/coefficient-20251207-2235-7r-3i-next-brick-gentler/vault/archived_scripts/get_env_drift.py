#!/usr/bin/env python3
"""
Quick script to get environment drift report from Steward
Outputs JSON report to stdout and saves to file
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def main():
    # Check if Steward is enabled
    if os.getenv("STEWARD_ENABLED", "false").lower() != "true":
        print("❌ Error: STEWARD_ENABLED is not set to 'true'", file=sys.stderr)
        print("Set STEWARD_ENABLED=true to use this script", file=sys.stderr)
        sys.exit(1)
    
    from bridge_backend.engines.steward.core import steward
    
    print("🔍 Running Steward environment drift analysis...", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Run diff
    try:
        diff_report = await steward.diff(["render", "netlify", "github"], dry_run=True)
    except RuntimeError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Convert to dict
    report = diff_report.model_dump()
    
    # Save to file
    output_file = project_root / "logs" / "steward_drift_report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary to stderr
    print("=" * 80, file=sys.stderr)
    print("📋 Environment Drift Summary", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    summary = report.get("summary", {})
    print(f"Total variables: {summary.get('total_keys', 0)}", file=sys.stderr)
    print(f"Local: {summary.get('local_count', 0)}", file=sys.stderr)
    print(f"Render: {summary.get('render_count', 0)}", file=sys.stderr)
    print(f"Netlify: {summary.get('netlify_count', 0)}", file=sys.stderr)
    print(f"GitHub: {summary.get('github_count', 0)}", file=sys.stderr)
    print("", file=sys.stderr)
    
    missing_render = len(report.get("missing_in_render", []))
    missing_netlify = len(report.get("missing_in_netlify", []))
    missing_github = len(report.get("missing_in_github", []))
    
    if missing_render > 0:
        print(f"❌ {missing_render} variables missing in Render", file=sys.stderr)
    else:
        print("✅ Render is in sync", file=sys.stderr)
    
    if missing_netlify > 0:
        print(f"❌ {missing_netlify} variables missing in Netlify", file=sys.stderr)
    else:
        print("✅ Netlify is in sync", file=sys.stderr)
    
    if missing_github > 0:
        print(f"❌ {missing_github} variables missing in GitHub", file=sys.stderr)
    else:
        print("✅ GitHub is in sync", file=sys.stderr)
    
    print("", file=sys.stderr)
    print(f"📄 Full report saved to: {output_file}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    
    # Output JSON to stdout for piping
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
