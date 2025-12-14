#!/usr/bin/env python3
"""
chimeractl - Chimera Deployment Engine Command Line Interface
Autonomous deployment control tool
Version: 1.9.7c
"""

import sys
import argparse
import asyncio
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_core.engines.chimera import ChimeraDeploymentEngine, ChimeraConfig


def cmd_simulate(args):
    """Run deployment simulation"""
    print(f"🔮 Running Chimera simulation for {args.platform}...")
    
    config = ChimeraConfig()
    engine = ChimeraDeploymentEngine(config)
    
    project_path = Path(args.path) if args.path else Path.cwd()
    
    # Run simulation
    result = asyncio.run(engine.simulate(args.platform, project_path))
    
    print(f"\n📊 Simulation Results:")
    print(f"  Platform: {args.platform}")
    print(f"  Status: {result.get('status')}")
    print(f"  Duration: {result.get('duration_seconds', 0):.2f}s")
    print(f"  Issues: {result.get('issues_count', 0)}")
    print(f"  Warnings: {result.get('warnings_count', 0)}")
    
    if result.get('issues'):
        print(f"\n⚠️  Issues Detected:")
        for issue in result['issues'][:10]:  # Show first 10
            severity = issue.get('severity', 'unknown')
            issue_type = issue.get('type', 'unknown')
            message = issue.get('message', 'No message')
            print(f"    [{severity.upper()}] {issue_type}: {message}")
    
    if result.get('warnings'):
        print(f"\n📝 Warnings:")
        for warning in result['warnings'][:5]:  # Show first 5
            print(f"    {warning.get('message', 'No message')}")
    
    if args.auto_heal and result.get('issues_count', 0) > 0:
        print(f"\n🩹 Auto-heal mode detected issues. Run with --deploy to apply fixes.")
    
    if args.json:
        print(f"\n--- JSON Output ---")
        print(json.dumps(result, indent=2))
    
    # Exit with error code if issues found
    sys.exit(1 if result.get('issues_count', 0) > 0 else 0)


def cmd_deploy(args):
    """Execute autonomous deployment"""
    print(f"🚀 Starting Chimera deployment to {args.platform}...")
    
    config = ChimeraConfig()
    engine = ChimeraDeploymentEngine(config)
    
    project_path = Path(args.path) if args.path else Path.cwd()
    
    # Run deployment
    result = asyncio.run(engine.deploy(
        args.platform,
        project_path,
        auto_heal=not args.no_heal,
        certify=args.certify
    ))
    
    print(f"\n📊 Deployment Results:")
    print(f"  Platform: {args.platform}")
    print(f"  Status: {result.get('status')}")
    print(f"  Duration: {result.get('duration_seconds', 0):.2f}s")
    
    # Show simulation results
    if 'simulation' in result:
        sim = result['simulation']
        print(f"\n  Simulation:")
        print(f"    Status: {sim.get('status')}")
        print(f"    Issues: {sim.get('issues_count', 0)}")
    
    # Show healing results
    if 'healing' in result and result['healing']:
        heal = result['healing']
        print(f"\n  Healing:")
        print(f"    Status: {heal.get('status')}")
        print(f"    Fixes Applied: {heal.get('fixes_applied', 0)}")
    
    # Show certification results
    if 'certification' in result and result['certification']:
        cert = result['certification']
        print(f"\n  Certification:")
        print(f"    Certified: {'✅' if cert.get('certified') else '❌'}")
        print(f"    Protocol: {cert.get('protocol')}")
        if cert.get('signature'):
            print(f"    Signature: {cert['signature'][:16]}...")
    
    # Show deployment status
    if 'deployment' in result:
        deploy = result['deployment']
        print(f"\n  Deployment:")
        print(f"    Status: {deploy.get('status')}")
    
    if args.json:
        print(f"\n--- JSON Output ---")
        print(json.dumps(result, indent=2))
    
    # Exit with error code if deployment failed
    sys.exit(0 if result.get('status') == 'success' else 1)


def cmd_monitor(args):
    """Monitor Chimera deployment status"""
    print("📡 Chimera Deployment Monitor\n")
    
    config = ChimeraConfig()
    engine = ChimeraDeploymentEngine(config)
    
    status = asyncio.run(engine.monitor())
    
    print(f"🎛️  Engine Status:")
    print(f"  Enabled: {'✅' if status.get('enabled') else '❌'}")
    print(f"  Codename: {status.get('config', {}).get('codename', 'Unknown')}")
    print(f"  Autonomy Level: {status.get('config', {}).get('autonomy_level', 'Unknown')}")
    
    print(f"\n📈 Statistics:")
    print(f"  Total Deployments: {status.get('deployments_count', 0)}")
    print(f"  Total Certifications: {status.get('certifications_count', 0)}")
    
    recent = status.get('recent_deployments', [])
    if recent:
        print(f"\n🕐 Recent Deployments:")
        for i, deploy in enumerate(recent[-5:], 1):
            platform = deploy.get('platform', 'unknown')
            deploy_status = deploy.get('status', 'unknown')
            timestamp = deploy.get('timestamp', 'unknown')
            print(f"  {i}. {platform} - {deploy_status} ({timestamp})")
    
    if args.json:
        print(f"\n--- JSON Output ---")
        print(json.dumps(status, indent=2))


def cmd_verify(args):
    """Verify deployment with Truth Engine"""
    print("🔍 Running Truth Engine verification...\n")
    
    config = ChimeraConfig()
    engine = ChimeraDeploymentEngine(config)
    
    project_path = Path(args.path) if args.path else Path.cwd()
    
    # Run simulation to get results for verification
    print("Step 1: Running simulation...")
    simulation = asyncio.run(engine.simulate(args.platform, project_path))
    
    # Run certification
    print("Step 2: Running certification...")
    certification = asyncio.run(engine.certifier.certify_build(simulation))
    
    print(f"\n📋 Verification Results:")
    print(f"  Certified: {'✅' if certification.get('certified') else '❌'}")
    print(f"  Protocol: {certification.get('protocol')}")
    
    if certification.get('checks'):
        print(f"\n  Checks:")
        for check_name, passed in certification['checks'].items():
            status_icon = '✅' if passed else '❌'
            print(f"    {status_icon} {check_name}")
    
    if certification.get('signature'):
        print(f"\n  Signature: {certification['signature']}")
    
    if certification.get('verification_chain'):
        print(f"\n  Verification Chain:")
        for step in certification['verification_chain']:
            print(f"    → {step}")
    
    if args.json:
        print(f"\n--- JSON Output ---")
        print(json.dumps(certification, indent=2))
    
    sys.exit(0 if certification.get('certified') else 1)


def cmd_preflight(args):
    """Run preflight validation and generate deploy artifacts"""
    print("🚀 Running Chimera preflight validation...\n")
    
    # Use the preflight engine from engines.chimera
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from engines.chimera.core import ChimeraEngine
    
    project_path = Path(args.path) if args.path else Path.cwd()
    engine = ChimeraEngine(project_path)
    
    result = asyncio.run(engine.preflight())
    
    print(f"✅ Preflight validation complete!")
    print(f"  Publish directory: {result.get('publish')}")
    print(f"  Generated files:")
    print(f"    - _headers")
    print(f"    - _redirects")
    print(f"    - netlify.toml")
    
    if args.json:
        print(f"\n--- JSON Output ---")
        print(json.dumps(result, indent=2))
    
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Chimera Deployment Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simulate Netlify deployment
  chimeractl simulate --platform netlify
  
  # Deploy to Render with certification
  chimeractl deploy --platform render --certify
  
  # Monitor deployment status
  chimeractl monitor
  
  # Verify with Truth Engine
  chimeractl verify --platform netlify
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Simulate command
    parser_simulate = subparsers.add_parser('simulate', help='Run deployment simulation')
    parser_simulate.add_argument('--platform', required=True, 
                                 choices=['netlify', 'render', 'github_pages'],
                                 help='Target deployment platform')
    parser_simulate.add_argument('--path', help='Project path (default: current directory)')
    parser_simulate.add_argument('--auto-heal', action='store_true', 
                                help='Show auto-heal recommendations')
    parser_simulate.add_argument('--json', action='store_true', help='Output as JSON')
    parser_simulate.set_defaults(func=cmd_simulate)
    
    # Deploy command
    parser_deploy = subparsers.add_parser('deploy', help='Execute autonomous deployment')
    parser_deploy.add_argument('--platform', required=True,
                               choices=['netlify', 'render', 'github_pages'],
                               help='Target deployment platform')
    parser_deploy.add_argument('--path', help='Project path (default: current directory)')
    parser_deploy.add_argument('--no-heal', action='store_true',
                              help='Disable automatic healing')
    parser_deploy.add_argument('--certify', action='store_true', default=True,
                              help='Require Truth Engine certification')
    parser_deploy.add_argument('--json', action='store_true', help='Output as JSON')
    parser_deploy.set_defaults(func=cmd_deploy)
    
    # Monitor command
    parser_monitor = subparsers.add_parser('monitor', help='Monitor deployment status')
    parser_monitor.add_argument('--json', action='store_true', help='Output as JSON')
    parser_monitor.set_defaults(func=cmd_monitor)
    
    # Verify command
    parser_verify = subparsers.add_parser('verify', help='Verify with Truth Engine')
    parser_verify.add_argument('--platform', required=True,
                               choices=['netlify', 'render', 'github_pages'],
                               help='Target deployment platform')
    parser_verify.add_argument('--path', help='Project path (default: current directory)')
    parser_verify.add_argument('--json', action='store_true', help='Output as JSON')
    parser_verify.set_defaults(func=cmd_verify)
    
    # Preflight command (v1.9.6r)
    parser_preflight = subparsers.add_parser('preflight', help='Run preflight validation')
    parser_preflight.add_argument('--path', help='Project path (default: current directory)')
    parser_preflight.add_argument('--json', action='store_true', help='Output as JSON')
    parser_preflight.set_defaults(func=cmd_preflight)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
