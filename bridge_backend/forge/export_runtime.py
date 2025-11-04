#!/usr/bin/env python3
"""
🌉 Forge Runtime Exporter
=========================
Exports runtime context and environment state for Forge Dominion handshake.

This script is called during the build process to generate runtime metadata
that synchronizes the deployment state with the Sovereign Bridge.

Usage:
    python3 bridge_backend/forge/export_runtime.py

Environment Variables:
    FORGE_DOMINION_ROOT: Root dominion endpoint
    DOMINION_SEAL: Sovereign signature token
    GITHUB_REF_NAME: Git branch name
    GITHUB_RUN_ID: GitHub Actions run ID
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import hashlib


def get_env_var(name: str, default: str = "") -> str:
    """Get environment variable with fallback."""
    return os.environ.get(name, default)


def generate_runtime_signature() -> str:
    """Generate a runtime signature based on current state."""
    timestamp = datetime.now(timezone.utc).isoformat()
    run_id = get_env_var("GITHUB_RUN_ID", "local")
    ref = get_env_var("GITHUB_REF_NAME", "main")
    
    # Create signature payload
    payload = f"{timestamp}:{run_id}:{ref}"
    signature = hashlib.sha256(payload.encode()).hexdigest()
    
    return signature


def export_runtime() -> dict:
    """Export runtime context for Forge Dominion."""
    
    # Get environment context
    runtime_context = {
        "forge_id": "Σ–AIBR–FJ–553–COD–EX",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "branch": get_env_var("GITHUB_REF_NAME", "main"),
            "run_id": get_env_var("GITHUB_RUN_ID", "local"),
            "dominion_root": get_env_var("FORGE_DOMINION_ROOT", "dominion://sovereign.bridge"),
        },
        "signature": generate_runtime_signature(),
        "status": "exported",
        "version": "5.5.3",
        "deployment": {
            "type": "sovereign",
            "platform": "netlify",
            "mode": "production"
        }
    }
    
    return runtime_context


def save_runtime_manifest(context: dict) -> None:
    """Save runtime manifest to file."""
    # Determine output directory
    output_dir = Path(__file__).parent / "runtime_exports"
    output_dir.mkdir(exist_ok=True)
    
    # Create manifest file
    manifest_path = output_dir / "runtime_manifest.json"
    
    with open(manifest_path, "w") as f:
        json.dump(context, f, indent=2)
    
    print(f"✅ Runtime manifest exported to: {manifest_path}")


def main():
    """Main execution."""
    print("🌉 Forge Runtime Exporter")
    print("=" * 50)
    
    try:
        # Export runtime context
        context = export_runtime()
        
        # Display context
        print(f"\n🔐 Forge ID: {context['forge_id']}")
        print(f"🕐 Timestamp: {context['timestamp']}")
        print(f"🌿 Branch: {context['environment']['branch']}")
        print(f"🔢 Run ID: {context['environment']['run_id']}")
        print(f"🔏 Signature: {context['signature'][:16]}...")
        
        # Save manifest
        save_runtime_manifest(context)
        
        print(f"\n✅ Runtime export completed successfully")
        print(f"📊 Status: {context['status']}")
        print(f"🚀 Version: {context['version']}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error exporting runtime: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
