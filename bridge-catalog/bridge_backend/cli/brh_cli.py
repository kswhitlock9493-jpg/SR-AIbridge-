#!/usr/bin/env python3
"""
Bridge Runtime Handler CLI
Command-line interface for managing BRH nodes
"""

import sys
import os
import json
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_core.runtime_handler import (
    RuntimeManifest,
    ForgeRuntimeAuthority,
    SovereignRuntimeCore
)


def cmd_init(args):
    """Initialize BRH in current repository"""
    print("🧠 Initializing Bridge Runtime Handler...")
    
    # Check if manifest exists
    manifest_path = Path("src/bridge.runtime.yaml")
    if manifest_path.exists() and not args.force:
        print(f"❌ Manifest already exists: {manifest_path}")
        print("   Use --force to overwrite")
        return 1
    
    # Copy example manifest
    example_path = Path("src/bridge.runtime.yaml.example")
    if not example_path.exists():
        print(f"❌ Example manifest not found: {example_path}")
        return 1
    
    import shutil
    shutil.copy(example_path, manifest_path)
    print(f"✓ Created manifest: {manifest_path}")
    
    # Check for Forge Dominion root key
    if not os.getenv("FORGE_DOMINION_ROOT"):
        print("\n⚠️  FORGE_DOMINION_ROOT not set")
        print("   Generate and set the root key:")
        print("   gh secret set FORGE_DOMINION_ROOT --body \"$(python -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip(\"=\"))')\"")
    else:
        print("✓ FORGE_DOMINION_ROOT configured")
    
    print("\n✓ BRH initialized successfully")
    print("  Edit src/bridge.runtime.yaml to configure your runtime")
    return 0


def cmd_validate(args):
    """Validate runtime manifest"""
    print("🔍 Validating runtime manifest...")
    
    manifest_path = args.manifest or "src/bridge.runtime.yaml"
    if not Path(manifest_path).exists():
        print(f"❌ Manifest not found: {manifest_path}")
        return 1
    
    try:
        manifest = RuntimeManifest(manifest_path)
        config = manifest.load()
        manifest.validate()
        
        print(f"✓ Manifest valid: {manifest_path}")
        print(f"  Runtime: {config['runtime']['name']}")
        print(f"  Type: {config['runtime']['type']}")
        print(f"  Containers: {len(config['runtime'].get('containers', []))}")
        print(f"  Federation: {'enabled' if config['runtime'].get('federation', {}).get('enabled') else 'disabled'}")
        
        return 0
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return 1


def cmd_token(args):
    """Generate runtime token"""
    print("🔐 Generating runtime token...")
    
    try:
        auth = ForgeRuntimeAuthority()
        
        node_id = args.node_id or f"cli-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        scope = args.scope or "runtime:execute"
        ttl = args.ttl or 3600
        
        token = auth.generate_runtime_token(node_id, scope, ttl)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(token, f, indent=2)
            print(f"✓ Token saved to: {args.output}")
        else:
            print(json.dumps(token, indent=2))
        
        print(f"\n✓ Token generated for node: {node_id}")
        print(f"  Expires: {token['expires_at']}")
        
        return 0
    except Exception as e:
        print(f"❌ Token generation failed: {e}")
        return 1


def cmd_status(args):
    """Show runtime status"""
    print("📊 Runtime Status\n")
    
    # Check manifest
    manifest_path = args.manifest or "src/bridge.runtime.yaml"
    if Path(manifest_path).exists():
        try:
            manifest = RuntimeManifest(manifest_path)
            manifest.load()
            manifest.validate()
            print("✓ Manifest: Valid")
        except Exception as e:
            print(f"❌ Manifest: Invalid - {e}")
    else:
        print("❌ Manifest: Not found")
    
    # Check Forge key
    if os.getenv("FORGE_DOMINION_ROOT"):
        print("✓ Forge Key: Configured")
    else:
        print("❌ Forge Key: Not set")
    
    # Check active nodes
    nodes_path = Path("forge/runtime/active_nodes.json")
    if nodes_path.exists():
        try:
            with open(nodes_path) as f:
                data = json.load(f)
            node_count = len(data.get('nodes', []))
            print(f"✓ Active Nodes: {node_count}")
        except Exception as e:
            print(f"⚠️  Active Nodes: Error reading - {e}")
    else:
        print("⚠️  Active Nodes: Registry not found")
    
    # Check token file
    token_path = Path("/tmp/forge_runtime_token.json")
    if token_path.exists():
        try:
            with open(token_path) as f:
                token = json.load(f)
            auth = ForgeRuntimeAuthority()
            valid = auth.validate_token(token)
            if valid:
                print(f"✓ Runtime Token: Valid (expires {token['expires_at']})")
            else:
                print("❌ Runtime Token: Expired or invalid")
        except Exception as e:
            print(f"⚠️  Runtime Token: Error - {e}")
    else:
        print("⚠️  Runtime Token: Not found")
    
    return 0


async def cmd_run(args):
    """Run the runtime handler"""
    print("🚀 Starting Bridge Runtime Handler...\n")
    
    manifest_path = args.manifest or "src/bridge.runtime.yaml"
    
    try:
        runtime = SovereignRuntimeCore(manifest_path)
        await runtime.run()
        return 0
    except KeyboardInterrupt:
        print("\n✓ Runtime stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Runtime error: {e}")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Bridge Runtime Handler CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  brh init                    Initialize BRH in current repo
  brh validate               Validate runtime manifest
  brh token --node-id test   Generate runtime token
  brh status                 Show runtime status
  brh run                    Start runtime handler
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # init command
    init_parser = subparsers.add_parser('init', help='Initialize BRH')
    init_parser.add_argument('--force', action='store_true', help='Overwrite existing manifest')
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate manifest')
    validate_parser.add_argument('--manifest', '-m', help='Path to manifest file')
    
    # token command
    token_parser = subparsers.add_parser('token', help='Generate runtime token')
    token_parser.add_argument('--node-id', '-n', help='Node ID')
    token_parser.add_argument('--scope', '-s', help='Token scope')
    token_parser.add_argument('--ttl', '-t', type=int, help='Token TTL in seconds')
    token_parser.add_argument('--output', '-o', help='Output file')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Show runtime status')
    status_parser.add_argument('--manifest', '-m', help='Path to manifest file')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Run runtime handler')
    run_parser.add_argument('--manifest', '-m', help='Path to manifest file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'init':
        return cmd_init(args)
    elif args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'token':
        return cmd_token(args)
    elif args.command == 'status':
        return cmd_status(args)
    elif args.command == 'run':
        return asyncio.run(cmd_run(args))
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
