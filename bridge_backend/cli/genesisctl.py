#!/usr/bin/env python3
"""
GenesisCtl - Genesis Framework CLI Commands
Command-line interface for Genesis orchestration, engine activation, and environment reconciliation
"""

import sys
import os
import asyncio
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.envrecon.core import EnvReconEngine
from engines.envrecon.hubsync import hubsync
from engines.envrecon.autoheal import autoheal


async def cmd_env_audit():
    """Run environment audit across all platforms"""
    print("🔍 Running environment audit...")
    engine = EnvReconEngine()
    report = await engine.reconcile()
    
    print("\n📊 Audit Results:")
    print(f"  Total variables: {report['summary']['total_keys']}")
    print(f"  Missing in Render: {len(report['missing_in_render'])}")
    print(f"  Missing in Netlify: {len(report['missing_in_netlify'])}")
    print(f"  Missing in GitHub: {len(report['missing_in_github'])}")
    print(f"  Conflicts: {len(report['conflicts'])}")
    
    print(f"\n📄 Report saved to: {engine.report_path}")
    return 0


async def cmd_env_sync(target=None, from_platform=None):
    """Sync environment variables to specified target"""
    engine = EnvReconEngine()
    
    if target == "github" and from_platform == "render":
        print("🔄 Syncing to GitHub from Render...")
        if not hubsync.is_configured():
            print("❌ GitHub sync not configured. Set GITHUB_TOKEN and GITHUB_REPO.")
            return 1
        
        # Fetch verified Render variables
        render_vars = await engine.fetch_render_env()
        if not render_vars:
            print("❌ Failed to fetch Render environment variables")
            return 1
        
        print(f"✅ Fetched {len(render_vars)} variables from Render")
        
        # Get current GitHub secrets
        github_vars = await engine.fetch_github_secrets()
        
        # Determine what needs to be synced
        missing_in_github = [k for k in render_vars if k not in github_vars]
        
        print(f"📊 Sync Analysis:")
        print(f"  Variables to sync: {len(missing_in_github)}")
        
        if missing_in_github:
            print(f"\n  Missing in GitHub:")
            for var in missing_in_github[:10]:
                print(f"    - {var}")
            if len(missing_in_github) > 10:
                print(f"    ... and {len(missing_in_github) - 10} more")
        
        # Perform the sync using hubsync
        synced_count = 0
        for var in missing_in_github:
            try:
                success = await hubsync.sync_secret(var, render_vars[var])
                if success:
                    synced_count += 1
            except Exception as e:
                print(f"⚠️ Failed to sync {var}: {e}")
        
        print(f"\n✅ Synced {synced_count}/{len(missing_in_github)} variables to GitHub")
        
        # Generate sync report
        await cmd_env_export(target="github", source="render")
        
        return 0
    elif target == "render":
        print("🔄 Syncing to Render...")
        print("⚠️  Direct sync not yet implemented - use audit + manual review")
        return 1
    elif target == "netlify":
        print("🔄 Syncing to Netlify...")
        print("⚠️  Direct sync not yet implemented - use audit + manual review")
        return 1
    elif target == "github":
        print("🔄 Syncing to GitHub...")
        if not hubsync.is_configured():
            print("❌ GitHub sync not configured. Set GITHUB_TOKEN and GITHUB_REPO.")
            return 1
        
        # Load report to get missing secrets
        report = engine.load_report()
        if not report:
            print("⚠️  No report available. Run 'genesisctl env audit' first.")
            return 1
        
        # Show what would be synced
        missing = report.get('missing_in_github', [])
        print(f"  Would sync {len(missing)} secrets to GitHub")
        print("💡 Tip: Use --from render to sync from Render to GitHub")
        return 0
    else:
        print("🔄 Syncing all platforms...")
        await cmd_env_audit()
        print("\n✅ Audit complete. Review report and use --target for specific sync.")
        return 0


async def cmd_env_export(target=None, source=None):
    """Export environment sync snapshot to .env.sync.json"""
    print(f"📤 Exporting environment sync snapshot...")
    engine = EnvReconEngine()
    
    # Determine source and target
    if not source:
        source = "render"  # Default to Render as canonical source
    if not target:
        target = "github"  # Default to GitHub as sync target
    
    # Fetch source environment
    if source == "render":
        source_vars = await engine.fetch_render_env()
    elif source == "netlify":
        source_vars = await engine.fetch_netlify_env()
    elif source == "local":
        source_vars = engine.load_local_env()
    else:
        print(f"❌ Unknown source: {source}")
        return 1
    
    if not source_vars:
        print(f"❌ Failed to fetch variables from {source}")
        return 1
    
    timestamp = datetime.now().isoformat().replace('+00:00', 'Z')
    
    sync_snapshot = {
        "provider": target,
        "source": source,
        "synced_at": timestamp,
        "variables": source_vars
    }
    
    # Save to config directory
    config_dir = Path(__file__).parent.parent / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    snapshot_path = config_dir / ".env.sync.json"
    with open(snapshot_path, 'w') as f:
        json.dump(sync_snapshot, f, indent=2)
    
    print(f"✅ Exported {len(source_vars)} variables from {source}")
    print(f"📄 Snapshot saved to: {snapshot_path}")
    
    # Also save to logs for audit trail
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    log_snapshot_path = logs_dir / "env_sync_report.json"
    with open(log_snapshot_path, 'w') as f:
        json.dump(sync_snapshot, f, indent=2)
    
    return 0


async def cmd_env_heal():
    """Trigger auto-healing for environment drift"""
    print("🩹 Running auto-heal...")
    engine = EnvReconEngine()
    
    report = engine.load_report()
    if not report:
        print("⚠️  No report available. Running audit first...")
        report = await engine.reconcile()
    
    heal_result = await autoheal.heal_environment(report)
    
    if heal_result.get('enabled'):
        healed = heal_result.get('healed', [])
        print(f"\n✅ Auto-heal complete")
        print(f"  Healed variables: {len(healed)}")
        if healed:
            for var in healed[:10]:
                print(f"    - {var}")
            if len(healed) > 10:
                print(f"    ... and {len(healed) - 10} more")
    else:
        print("❌ Auto-heal is disabled")
    
    return 0


def cmd_engines_enable_true():
    """Activate all engines with RBAC + Truth Certification"""
    print("🚀 Activating all Bridge engines...")
    print("=" * 80)
    
    try:
        from genesis.activation import activate_all_engines
        
        # Run activation
        report = activate_all_engines()
        
        # Print report
        print(report.report())
        
        # Save report to logs
        logs_dir = Path(__file__).parent.parent / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = logs_dir / "engine_activation_report.json"
        with open(report_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return 0
    except Exception as e:
        print(f"❌ Failed to activate engines: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_engines_status():
    """Get current activation status of all engines"""
    print("📊 Engine Activation Status")
    print("=" * 80)
    
    try:
        from genesis.activation import get_activation_status
        
        status = get_activation_status()
        
        print(f"\n📈 Summary:")
        print(f"  Total Engines: {status['summary']['total']}")
        print(f"  Active: {status['summary']['active']}")
        print(f"  Inactive: {status['summary']['inactive']}")
        print("")
        
        # Group by category
        categories = {}
        for engine in status['engines']:
            cat = engine['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(engine)
        
        # Print by category
        for category, engines in sorted(categories.items()):
            print(f"🔧 {category.upper()} Engines:")
            for engine in engines:
                status_icon = "✅" if engine['enabled'] else "⏹️"
                print(f"  {status_icon} {engine['name']} ({engine['role']})")
            print("")
        
        return 0
    except Exception as e:
        print(f"❌ Failed to get engine status: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GenesisCtl - Genesis Framework CLI"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # engines_enable_true command
    subparsers.add_parser('engines_enable_true', 
                         help='Activate all engines with RBAC + Truth Certification')
    
    # engines_status command
    subparsers.add_parser('engines_status',
                         help='Get current activation status of all engines')
    
    # env command
    env_parser = subparsers.add_parser('env', help='Environment management commands')
    env_subparsers = env_parser.add_subparsers(dest='env_command', help='Environment subcommands')
    
    # env audit
    env_subparsers.add_parser('audit', help='Run environment audit')
    
    # env sync
    sync_parser = env_subparsers.add_parser('sync', help='Sync environment variables')
    sync_parser.add_argument('--target', choices=['render', 'netlify', 'github'], 
                            help='Target platform to sync')
    sync_parser.add_argument('--from', dest='from_platform', choices=['render', 'netlify', 'local'],
                            help='Source platform to sync from')
    
    # env export
    export_parser = env_subparsers.add_parser('export', help='Export environment sync snapshot')
    export_parser.add_argument('--target', choices=['render', 'netlify', 'github'],
                              help='Target platform for export')
    export_parser.add_argument('--source', choices=['render', 'netlify', 'local'],
                              help='Source platform to export from')
    
    # env heal
    env_subparsers.add_parser('heal', help='Trigger auto-healing')
    
    args = parser.parse_args()
    
    if args.command == 'engines_enable_true':
        return cmd_engines_enable_true()
    elif args.command == 'engines_status':
        return cmd_engines_status()
    elif args.command == 'env':
        if args.env_command == 'audit':
            return asyncio.run(cmd_env_audit())
        elif args.env_command == 'sync':
            return asyncio.run(cmd_env_sync(args.target, args.from_platform))
        elif args.env_command == 'export':
            return asyncio.run(cmd_env_export(args.target, args.source))
        elif args.env_command == 'heal':
            return asyncio.run(cmd_env_heal())
        else:
            env_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
