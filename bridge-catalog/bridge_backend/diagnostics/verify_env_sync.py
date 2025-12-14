#!/usr/bin/env python3
"""
Bridge Backend — Environment Sync Verifier
Version: 1.0 | Added in SR-AIbridge v1.9.6L

Purpose:
Confirms that Render, Netlify, and GitHub environment states
match the local verified configuration post-deployment.
Designed to be run automatically after EnvSync or manually
by an Admiral-class operator.

Usage:
python3 -m bridge_backend.diagnostics.verify_env_sync
"""

import json
import os
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def main():
    print("\n🌐 Running Bridge Environment Parity Verification...")
    
    # Import after path setup
    try:
        from bridge_backend.engines.envrecon.core import EnvReconEngine
    except ImportError:
        print("❌ Failed to import EnvReconEngine - checking alternative locations...")
        try:
            from engines.envrecon.core import EnvReconEngine
        except ImportError:
            print("❌ Could not import EnvReconEngine from any location")
            sys.exit(1)
    
    try:
        from bridge_backend.genesis.bus import genesis_bus
    except ImportError:
        # Genesis bus might not be available in all environments
        genesis_bus = None
    
    # Initialize engine and run reconciliation
    import asyncio
    engine = EnvReconEngine()
    
    # Run the reconcile to get current state
    report = asyncio.run(engine.reconcile())
    
    timestamp = datetime.now(datetime.UTC).isoformat().replace('+00:00', 'Z')
    
    # Determine if there's drift
    has_drift = (
        len(report.get("missing_in_render", [])) > 0 or
        len(report.get("missing_in_netlify", [])) > 0 or
        len(report.get("missing_in_github", [])) > 0 or
        len(report.get("conflicts", {})) > 0
    )
    
    result = {
        "verified_at": timestamp,
        "has_drift": has_drift,
        "missing_in_render": report.get("missing_in_render", []),
        "missing_in_netlify": report.get("missing_in_netlify", []),
        "missing_in_github": report.get("missing_in_github", []),
        "conflicts": report.get("conflicts", {}),
        "summary": report.get("summary", {}),
    }
    
    # Ensure logs directory exists
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    out_path = logs_dir / "env_parity_check.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    
    if result["has_drift"]:
        print("⚠️ Environment drift detected!")
        print(f"   Missing (Render): {len(result['missing_in_render'])}")
        print(f"   Missing (Netlify): {len(result['missing_in_netlify'])}")
        print(f"   Missing (GitHub): {len(result['missing_in_github'])}")
        print(f"   Conflicts: {len(result['conflicts'])}")
        
        # Publish drift event to Genesis Bus if available
        if genesis_bus and genesis_bus.is_enabled():
            try:
                asyncio.run(genesis_bus.publish("envsync.drift", result))
            except Exception as e:
                print(f"⚠️ Failed to publish drift event to Genesis: {e}")
    else:
        print("✅ Environments are in full parity across all platforms!")
        
        # Publish commit event to Genesis Bus if available
        if genesis_bus and genesis_bus.is_enabled():
            try:
                asyncio.run(genesis_bus.publish("envsync.commit", result))
            except Exception as e:
                print(f"⚠️ Failed to publish commit event to Genesis: {e}")
    
    print(f"\n📄 Report saved to: {out_path}\n")
    
    # Return exit code: 0 if no drift, 1 if drift detected
    return 0 if not has_drift else 1


if __name__ == "__main__":
    sys.exit(main())
