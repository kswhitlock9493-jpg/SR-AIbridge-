#!/usr/bin/env python3
"""
Deep Diagnostics CLI - diagctl
Runs all engines and shows their status in a compact JSON report
"""
import asyncio
import json
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

async def run_all():
    results = {}

    # HXO Nexus
    try:
        from bridge_backend.bridge_core.engines.hxo import initialize_nexus
        from bridge_backend.genesis.bus import genesis_bus
        
        ok = await initialize_nexus(genesis_bus)
        results["hxo_initialized"] = bool(ok) if ok is not None else True
        results["hxo_status"] = "ok" if ok else "failed"
    except Exception as e:
        results["hxo_error"] = str(e)
        results["hxo_initialized"] = False

    # EnvRecon
    try:
        from bridge_backend.engines.envrecon.core import EnvReconEngine
        
        recon = EnvReconEngine()
        report = await recon.reconcile()
        results["envrecon"] = {
            "has_drift": report.get("has_drift", False),
            "summary": report.get("summary", {}),
        }
    except Exception as e:
        results["envrecon_error"] = str(e)

    # ARIE (config scan)
    try:
        from bridge_backend.engines.arie.core import ARIEngine
        
        ar = ARIEngine()
        cfg = await ar.scan_environment_config()
        results["arie_config_scan"] = cfg.summary if hasattr(cfg, "summary") else str(cfg)
    except Exception as e:
        results["arie_error"] = str(e)

    # Steward diff view materialization
    try:
        from bridge_backend.engines.steward.core import StewardEngine
        
        ste = StewardEngine()
        await ste.render_env_diff_snapshot()
        results["steward_env_viz"] = "ok"
    except Exception as e:
        results["steward_error"] = str(e)

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(run_all())
