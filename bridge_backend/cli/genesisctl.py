#!/usr/bin/env python3
"""
GenesisCtl - EnvRecon CLI Commands
Command-line interface for environment reconciliation and synchronization
"""

import sys
import os
import asyncio
import argparse
import json
from pathlib import Path

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


async def cmd_env_sync(target=None):
    """Sync environment variables to specified target"""
    engine = EnvReconEngine()
    
    if target == "render":
        print("🔄 Syncing to Render...")
        # This would use the existing sync provider
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
        print("⚠️  Auto-sync requires API implementation")
        return 0
    else:
        print("🔄 Syncing all platforms...")
        await cmd_env_audit()
        print("\n✅ Audit complete. Review report and use --target for specific sync.")
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


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GenesisCtl - Environment Reconciliation CLI"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # env command
    env_parser = subparsers.add_parser('env', help='Environment management commands')
    env_subparsers = env_parser.add_subparsers(dest='env_command', help='Environment subcommands')
    
    # env audit
    env_subparsers.add_parser('audit', help='Run environment audit')
    
    # env sync
    sync_parser = env_subparsers.add_parser('sync', help='Sync environment variables')
    sync_parser.add_argument('--target', choices=['render', 'netlify', 'github'], 
                            help='Target platform to sync')
    
    # env heal
    env_subparsers.add_parser('heal', help='Trigger auto-healing')
    
    args = parser.parse_args()
    
    if args.command == 'env':
        if args.env_command == 'audit':
            return asyncio.run(cmd_env_audit())
        elif args.env_command == 'sync':
            return asyncio.run(cmd_env_sync(args.target))
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
