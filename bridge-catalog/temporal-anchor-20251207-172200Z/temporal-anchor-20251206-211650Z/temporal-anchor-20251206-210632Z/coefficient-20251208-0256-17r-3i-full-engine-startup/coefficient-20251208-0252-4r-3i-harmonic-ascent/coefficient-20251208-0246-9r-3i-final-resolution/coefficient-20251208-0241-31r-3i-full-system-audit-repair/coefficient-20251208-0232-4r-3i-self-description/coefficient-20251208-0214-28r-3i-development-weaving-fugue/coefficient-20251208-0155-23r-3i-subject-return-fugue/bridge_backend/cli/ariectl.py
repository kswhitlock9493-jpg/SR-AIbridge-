#!/usr/bin/env python3
"""
ariectl - ARIE Command Line Interface
Autonomous Repository Integrity Engine control tool
"""

import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.arie.core import ARIEEngine
from engines.arie.models import PolicyType


def cmd_scan(args):
    """Run ARIE scan"""
    engine = ARIEEngine()
    
    policy = PolicyType(args.policy) if args.policy else PolicyType.SAFE_EDIT
    
    print(f"🔍 Running ARIE scan (policy: {policy.value}, dry_run: {args.dry_run})")
    
    summary = engine.run(
        policy=policy,
        dry_run=args.dry_run,
        apply=False,
        paths=args.paths
    )
    
    print(f"\n📊 Scan Results:")
    print(f"  Run ID: {summary.run_id}")
    print(f"  Findings: {summary.findings_count}")
    print(f"  Duration: {summary.duration_seconds:.2f}s")
    
    if summary.findings_by_severity:
        print(f"\n  By Severity:")
        for severity, count in summary.findings_by_severity.items():
            print(f"    {severity}: {count}")
    
    if summary.findings_by_category:
        print(f"\n  By Category:")
        for category, count in summary.findings_by_category.items():
            print(f"    {category}: {count}")
    
    if args.verbose and summary.findings:
        print(f"\n📋 Findings (top 10):")
        for i, finding in enumerate(summary.findings[:10], 1):
            print(f"\n  [{i}] {finding.severity.value.upper()} - {finding.category}")
            print(f"      File: {finding.file_path}")
            if finding.line_number:
                print(f"      Line: {finding.line_number}")
            print(f"      {finding.description}")
            if finding.suggested_fix:
                print(f"      Fix: {finding.suggested_fix}")
    
    if args.json:
        print(f"\n{json.dumps(summary.dict(), indent=2)}")
    
    return 0


def cmd_apply(args):
    """Apply ARIE fixes"""
    engine = ARIEEngine()
    
    policy = PolicyType(args.policy) if args.policy else PolicyType.SAFE_EDIT
    
    print(f"🔧 Applying ARIE fixes (policy: {policy.value})")
    
    if not args.yes:
        response = input("This will modify files. Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    
    summary = engine.run(
        policy=policy,
        dry_run=False,
        apply=True,
        paths=args.paths
    )
    
    print(f"\n✅ Apply Results:")
    print(f"  Run ID: {summary.run_id}")
    print(f"  Findings: {summary.findings_count}")
    print(f"  Fixes Applied: {summary.fixes_applied}")
    print(f"  Fixes Failed: {summary.fixes_failed}")
    print(f"  Duration: {summary.duration_seconds:.2f}s")
    
    if summary.patches:
        print(f"\n📦 Patches Created:")
        for patch in summary.patches:
            print(f"  - {patch.id}")
            print(f"    Files modified: {len(patch.files_modified)}")
            print(f"    Certified: {patch.certified}")
    
    if args.json:
        print(f"\n{json.dumps(summary.dict(), indent=2)}")
    
    return 0


def cmd_rollback(args):
    """Rollback a patch"""
    engine = ARIEEngine()
    
    print(f"⏪ Rolling back patch: {args.patch_id}")
    
    if not args.yes and not args.force:
        response = input("This will restore previous file versions. Continue? [y/N]: ")
        if response.lower() != 'y':
            print("Aborted.")
            return 1
    
    rollback = engine.rollback(args.patch_id, force=args.force)
    
    if rollback.success:
        print(f"\n✅ Rollback successful")
        print(f"  Rollback ID: {rollback.id}")
        print(f"  Files restored: {len(rollback.restored_files)}")
        if rollback.restored_files:
            for file_path in rollback.restored_files:
                print(f"    - {file_path}")
    else:
        print(f"\n❌ Rollback failed: {rollback.error}")
        return 1
    
    if args.json:
        print(f"\n{json.dumps(rollback.dict(), indent=2)}")
    
    return 0


def cmd_report(args):
    """Show last ARIE report"""
    engine = ARIEEngine()
    
    summary = engine.get_last_report()
    
    if not summary:
        print("No reports available")
        return 1
    
    print(f"📊 Last ARIE Report")
    print(f"  Run ID: {summary.run_id}")
    print(f"  Timestamp: {summary.timestamp}")
    print(f"  Policy: {summary.policy.value}")
    print(f"  Dry Run: {summary.dry_run}")
    print(f"  Findings: {summary.findings_count}")
    print(f"  Fixes Applied: {summary.fixes_applied}")
    print(f"  Duration: {summary.duration_seconds:.2f}s")
    
    if summary.findings_by_severity:
        print(f"\n  By Severity:")
        for severity, count in summary.findings_by_severity.items():
            print(f"    {severity}: {count}")
    
    if summary.findings_by_category:
        print(f"\n  By Category:")
        for category, count in summary.findings_by_category.items():
            print(f"    {category}: {count}")
    
    if args.json:
        print(f"\n{json.dumps(summary.dict(), indent=2)}")
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="ariectl - ARIE Command Line Interface"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Run integrity scan')
    scan_parser.add_argument('--policy', choices=['LINT_ONLY', 'SAFE_EDIT', 'REFACTOR', 'ARCHIVE'],
                            help='Policy to use')
    scan_parser.add_argument('--dry-run', action='store_true', default=True,
                            help='Dry run mode (default)')
    scan_parser.add_argument('--paths', nargs='+', help='Specific paths to scan')
    scan_parser.add_argument('--verbose', '-v', action='store_true',
                            help='Verbose output')
    scan_parser.add_argument('--json', action='store_true',
                            help='Output JSON')
    
    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply fixes')
    apply_parser.add_argument('--policy', choices=['SAFE_EDIT', 'REFACTOR', 'ARCHIVE'],
                             default='SAFE_EDIT', help='Policy to use')
    apply_parser.add_argument('--paths', nargs='+', help='Specific paths to fix')
    apply_parser.add_argument('--yes', '-y', action='store_true',
                             help='Skip confirmation')
    apply_parser.add_argument('--json', action='store_true',
                             help='Output JSON')
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback a patch')
    rollback_parser.add_argument('--patch', dest='patch_id', required=True,
                                help='Patch ID to rollback')
    rollback_parser.add_argument('--force', action='store_true',
                                help='Force rollback')
    rollback_parser.add_argument('--yes', '-y', action='store_true',
                                help='Skip confirmation')
    rollback_parser.add_argument('--json', action='store_true',
                                help='Output JSON')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Show last report')
    report_parser.add_argument('--json', action='store_true',
                              help='Output JSON')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'scan':
            return cmd_scan(args)
        elif args.command == 'apply':
            return cmd_apply(args)
        elif args.command == 'rollback':
            return cmd_rollback(args)
        elif args.command == 'report':
            return cmd_report(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
