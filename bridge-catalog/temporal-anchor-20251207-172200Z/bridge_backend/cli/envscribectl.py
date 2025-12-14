#!/usr/bin/env python3
"""
EnvScribe CLI Tool
Command-line interface for environment intelligence system

Usage:
    python -m bridge_backend.cli.envscribectl scan
    python -m bridge_backend.cli.envscribectl emit
    python -m bridge_backend.cli.envscribectl audit
    python -m bridge_backend.cli.envscribectl copy render
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bridge_backend.engines.envscribe.core import EnvScribeEngine
from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter


def main():
    parser = argparse.ArgumentParser(
        description="EnvScribe CLI - Unified Environment Intelligence System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scan              Scan repository and verify environment
  %(prog)s emit              Generate documentation and copy blocks
  %(prog)s audit             Full audit: scan + emit + certify
  %(prog)s copy render       Show copy-ready block for Render
  %(prog)s copy netlify      Show copy-ready block for Netlify
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Scan command
    subparsers.add_parser("scan", help="Scan repository and verify environment")
    
    # Emit command
    subparsers.add_parser("emit", help="Generate documentation and copy blocks")
    
    # Audit command
    subparsers.add_parser("audit", help="Full audit: scan + emit + certify")
    
    # Copy command
    copy_parser = subparsers.add_parser("copy", help="Show copy-ready environment block")
    copy_parser.add_argument(
        "platform",
        choices=["render", "netlify", "github_vars", "github_secrets"],
        help="Platform to generate copy block for"
    )
    
    # Report command
    subparsers.add_parser("report", help="Show current scan report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == "scan":
            asyncio.run(cmd_scan())
        elif args.command == "emit":
            asyncio.run(cmd_emit())
        elif args.command == "audit":
            asyncio.run(cmd_audit())
        elif args.command == "copy":
            asyncio.run(cmd_copy(args.platform))
        elif args.command == "report":
            cmd_report()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def cmd_scan():
    """Execute scan command"""
    print("🔍 EnvScribe: Starting environment scan...")
    print()
    
    engine = EnvScribeEngine()
    report = await engine.scan()
    
    print("✅ Scan complete!")
    print()
    print(f"📊 Summary:")
    print(f"   Total variables: {report.summary.total_keys}")
    print(f"   Verified: {report.summary.verified}")
    print(f"   Missing in Render: {report.summary.missing_in_render}")
    print(f"   Missing in Netlify: {report.summary.missing_in_netlify}")
    print(f"   Missing in GitHub: {report.summary.missing_in_github}")
    print(f"   Drifted: {report.summary.drifted}")
    print()
    
    if report.missing_in_render:
        print(f"🟥 Missing in Render: {', '.join(report.missing_in_render)}")
    if report.missing_in_netlify:
        print(f"🟥 Missing in Netlify: {', '.join(report.missing_in_netlify)}")
    if report.missing_in_github:
        print(f"🟥 Missing in GitHub: {', '.join(report.missing_in_github)}")
    
    if report.drifted:
        print()
        print(f"⚠️ Drifted variables: {', '.join(report.drifted.keys())}")


async def cmd_emit():
    """Execute emit command"""
    print("📝 EnvScribe: Generating documentation and copy blocks...")
    print()
    
    engine = EnvScribeEngine()
    report = engine.load_report()
    
    if not report:
        print("❌ No report found. Run 'scan' first.")
        sys.exit(1)
    
    emitter = EnvScribeEmitter()
    outputs = emitter.emit_all(report)
    
    print("✅ Artifacts generated!")
    print()
    print("📄 Generated files:")
    for name, path in outputs.items():
        if name != "copy_blocks":
            print(f"   {name}: {path}")
    
    print()
    print("📋 Copy blocks available for: render, netlify, github_vars, github_secrets")
    print("   Use 'envscribectl copy <platform>' to view")


async def cmd_audit():
    """Execute full audit command"""
    print("🔬 EnvScribe: Running full audit...")
    print()
    
    # Scan
    print("1️⃣ Scanning repository...")
    engine = EnvScribeEngine()
    report = await engine.scan()
    print(f"   ✅ Found {report.summary.total_keys} variables")
    print()
    
    # Emit
    print("2️⃣ Generating artifacts...")
    emitter = EnvScribeEmitter()
    outputs = emitter.emit_all(report)
    print(f"   ✅ Generated {len([k for k in outputs.keys() if k != 'copy_blocks'])} files")
    print()
    
    # Summary
    print("✅ Audit complete!")
    print()
    print(f"📊 Summary:")
    print(f"   Total variables: {report.summary.total_keys}")
    print(f"   Verified: {report.summary.verified}")
    print(f"   Missing: {report.summary.missing_in_render + report.summary.missing_in_netlify + report.summary.missing_in_github}")
    print(f"   Drifted: {report.summary.drifted}")
    print()
    
    if report.certified:
        print(f"🏆 Truth-Certified: {report.certificate_id}")
    else:
        print("⚠️ Not yet certified by Truth Engine")
    
    print()
    print(f"📄 Documentation: docs/ENV_OVERVIEW.md")
    print(f"📁 Diagnostics: bridge_backend/diagnostics/envscribe_report.json")


async def cmd_copy(platform: str):
    """Execute copy command"""
    engine = EnvScribeEngine()
    report = engine.load_report()
    
    if not report:
        print("❌ No report found. Run 'scan' first.")
        sys.exit(1)
    
    emitter = EnvScribeEmitter()
    blocks = emitter.generate_copy_blocks(report)
    
    print(f"📋 Copy-ready block for {platform.upper()}:")
    print()
    print("=" * 60)
    print(blocks[platform])
    print("=" * 60)


def cmd_report():
    """Show current scan report"""
    engine = EnvScribeEngine()
    report = engine.load_report()
    
    if not report:
        print("❌ No report found. Run 'scan' first.")
        sys.exit(1)
    
    print("📊 EnvScribe Report")
    print("=" * 60)
    print()
    print(f"Timestamp: {report.summary.timestamp}")
    print(f"Total variables: {report.summary.total_keys}")
    print(f"Verified: {report.summary.verified}")
    print()
    
    if report.certified:
        print(f"✅ Truth-Certified: {report.certificate_id}")
        print()
    
    print("Variables by platform:")
    print()
    
    render_vars = [v for v in report.variables if "Render" in v.scope]
    netlify_vars = [v for v in report.variables if "Netlify" in v.scope]
    github_vars = [v for v in report.variables if "GitHub" in v.scope]
    
    print(f"  Render: {len(render_vars)} variables")
    print(f"  Netlify: {len(netlify_vars)} variables")
    print(f"  GitHub: {len(github_vars)} variables")
    print()
    
    if report.missing_in_render or report.missing_in_netlify or report.missing_in_github:
        print("Missing variables:")
        if report.missing_in_render:
            print(f"  Render ({len(report.missing_in_render)}): {', '.join(report.missing_in_render[:5])}")
            if len(report.missing_in_render) > 5:
                print(f"          ... and {len(report.missing_in_render) - 5} more")
        if report.missing_in_netlify:
            print(f"  Netlify ({len(report.missing_in_netlify)}): {', '.join(report.missing_in_netlify[:5])}")
            if len(report.missing_in_netlify) > 5:
                print(f"           ... and {len(report.missing_in_netlify) - 5} more")
        if report.missing_in_github:
            print(f"  GitHub ({len(report.missing_in_github)}): {', '.join(report.missing_in_github[:5])}")
            if len(report.missing_in_github) > 5:
                print(f"          ... and {len(report.missing_in_github) - 5} more")
    
    print()
    print("For full report: bridge_backend/diagnostics/envscribe_report.json")
    print("For documentation: docs/ENV_OVERVIEW.md")


if __name__ == "__main__":
    main()
