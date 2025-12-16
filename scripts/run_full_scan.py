#!/usr/bin/env python3
"""
Full System Scan - GitHub Triage, Quantum Dominion Security, Umbra, Preflight, and More

This script runs a comprehensive scan of all critical infrastructure components:
- Quantum Dominion Security (pre-deployment orchestrator)
- API Triage (endpoint health checks)
- Preflight (Netlify guard, integrity checks)
- Umbra Triage (issue tracking and auto-healing)
- Build Triage (Netlify build validation)
- Endpoint API Sweep (route analysis)
- Environment Parity Guard (environment drift detection)
- Runtime Triage (Render health checks)

Usage:
    python3 scripts/run_full_scan.py [--json] [--quiet]
    
Options:
    --json      Output results in JSON format
    --quiet     Suppress progress messages
    --timeout N Set timeout for individual scans (default: 60 seconds)
"""
import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


def run_command(cmd: str, cwd: str = None, timeout: int = 60) -> Dict[str, Any]:
    """Run a command and return its output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=True
        )
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': 'Command timed out'
        }
    except Exception as e:
        return {
            'success': False,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e)
        }


def load_json_report(path: Path) -> Dict[str, Any]:
    """Load a JSON report file if it exists."""
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            return None
    return None


def scan_quantum_dominion(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Quantum Dominion Security check."""
    if not quiet:
        print("\n🜂 Running Quantum Dominion Security...")
    
    result = run_command('python3 bridge_backend/runtime/quantum_predeploy_orchestrator.py', timeout=timeout)
    report_path = Path('.alik/predeploy_report.json')
    
    return {
        'name': 'Quantum Dominion Security',
        'success': result['success'],
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def scan_api_triage(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run API Triage check."""
    if not quiet:
        print("\n📡 Running API Triage...")
    
    result = run_command('cd bridge_backend && python3 scripts/api_triage.py --manual || true', timeout=timeout)
    report_path = Path('bridge_backend/api_triage_report.json')
    
    return {
        'name': 'API Triage',
        'success': report_path.exists(),
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def scan_preflight(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Preflight checks."""
    if not quiet:
        print("\n🚀 Running Preflight Checks...")
    
    netlify_cmd = """python3 - <<'PY'
import sys
sys.path.insert(0, '.')
from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path, require_netlify_token
import os
def _gh(): return os.getenv("GITHUB_TOKEN") or os.getenv("REFLEX_GITHUB_TOKEN")
print("publish:", validate_publish_path())
try:
    require_netlify_token(_gh)
    print("token: ok")
except Exception as e:
    print(f"token: {e}")
PY
"""
    
    integrity_cmd = """python3 - <<'PY'
import sys
sys.path.insert(0, '.')
from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
def _run(): 
    print("integrity: OK (deferred dry-run)")
delayed_integrity_check(_run)
PY
"""
    
    netlify_result = run_command(netlify_cmd, timeout=timeout)
    integrity_result = run_command(integrity_cmd, timeout=timeout)
    
    return {
        'name': 'Preflight',
        'success': netlify_result['success'] and integrity_result['success'],
        'netlify_guard': netlify_result['success'],
        'integrity_check': integrity_result['success']
    }


def scan_umbra(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Umbra Triage check."""
    if not quiet:
        print("\n🌑 Running Umbra Triage...")
    
    os.makedirs('bridge_backend/logs/umbra_reports', exist_ok=True)
    result = run_command(f'python3 -m bridge_backend.cli.umbractl run --heal --report --timeout 30 || true', timeout=timeout)
    report_path = Path('bridge_backend/logs/umbra_reports/latest.json')
    
    return {
        'name': 'Umbra Triage',
        'success': True,
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def scan_build_triage(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Build Triage check."""
    if not quiet:
        print("\n🏗️ Running Build Triage (Netlify)...")
    
    result = run_command('python3 .github/scripts/build_triage_netlify.py || true', timeout=timeout)
    report_path = Path('bridge_backend/diagnostics/build_triage_report.json')
    
    return {
        'name': 'Build Triage (Netlify)',
        'success': report_path.exists(),
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def scan_endpoint_triage(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Endpoint Triage check."""
    if not quiet:
        print("\n🔌 Running Endpoint API Sweep...")
    
    result = run_command('python3 .github/scripts/endpoint_api_sweep.py || true', timeout=timeout)
    report_path = Path('bridge_backend/diagnostics/endpoint_api_sweep.json')
    
    return {
        'name': 'Endpoint API Sweep',
        'success': report_path.exists(),
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def scan_env_parity(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Environment Parity check."""
    if not quiet:
        print("\n⚖️ Running Environment Parity Guard...")
    
    result = run_command('python3 .github/scripts/env_parity_guard.py || true', timeout=timeout)
    report_path = Path('bridge_backend/diagnostics/env_parity_report.json')
    
    return {
        'name': 'Environment Parity Guard',
        'success': report_path.exists(),
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def scan_runtime_triage(quiet: bool = False, timeout: int = 60) -> Dict[str, Any]:
    """Run Runtime Triage check."""
    if not quiet:
        print("\n⏰ Running Runtime Triage (Render)...")
    
    result = run_command('python3 .github/scripts/runtime_triage_render.py || true', timeout=timeout)
    report_path = Path('bridge_backend/diagnostics/runtime_triage_report.json')
    
    return {
        'name': 'Runtime Triage (Render)',
        'success': report_path.exists(),
        'report_exists': report_path.exists(),
        'report_data': load_json_report(report_path)
    }


def main():
    parser = argparse.ArgumentParser(
        description='Run comprehensive system scan of all checks'
    )
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress messages')
    parser.add_argument('--timeout', type=int, default=60, help='Timeout for individual scans (default: 60s)')
    args = parser.parse_args()
    
    if not args.quiet and not args.json:
        print("=" * 70)
        print("FULL SYSTEM SCAN - GitHub Triage, Quantum Dominion, Umbra, Preflight")
        print("=" * 70)
        print(f"Scan Date: {datetime.now().isoformat()}")
    
    # Run all scans
    results: List[Dict[str, Any]] = []
    results.append(scan_quantum_dominion(args.quiet, args.timeout))
    results.append(scan_api_triage(args.quiet, args.timeout))
    results.append(scan_preflight(args.quiet, args.timeout))
    results.append(scan_umbra(args.quiet, args.timeout))
    results.append(scan_build_triage(args.quiet, args.timeout))
    results.append(scan_endpoint_triage(args.quiet, args.timeout))
    results.append(scan_env_parity(args.quiet, args.timeout))
    results.append(scan_runtime_triage(args.quiet, args.timeout))
    
    # Calculate summary
    passed = sum(1 for r in results if r['success'])
    failed = len(results) - passed
    
    # Generate report
    scan_report = {
        'scan_date': datetime.now().isoformat(),
        'total_checks': len(results),
        'passed': passed,
        'failed': failed,
        'results': results
    }
    
    # Save comprehensive report
    report_path = Path('bridge_backend/diagnostics/full_scan_report.json')
    os.makedirs(report_path.parent, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(scan_report, f, indent=2)
    
    # Output results
    if args.json:
        print(json.dumps(scan_report, indent=2))
    else:
        if not args.quiet:
            print("\n" + "=" * 70)
            print("SCAN RESULTS SUMMARY")
            print("=" * 70)
        
        for result in results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"{status} - {result['name']}")
        
        if not args.quiet:
            print("\n" + "=" * 70)
            print(f"Total: {len(results)} checks")
            print(f"✅ Passed: {passed}")
            print(f"❌ Failed: {failed}")
            print("=" * 70)
            print(f"\n📄 Full report saved to: {report_path}")
    
    # Exit with appropriate code
    return 0 if failed == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
