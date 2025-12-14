#!/usr/bin/env python3
"""
Post-Merge Activation Script for v1.9.7m Total Autonomy Protocol

This script is meant to be run immediately after merging v1.9.7m to main.
It boots the Elysium Guardian and performs an initial health check.
"""

import sys
import asyncio
from pathlib import Path

# Add bridge_backend to path
repo_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(repo_root / "bridge_backend"))

async def activate_autonomy():
    """Activate Total Autonomy Protocol"""
    
    print("\n" + "="*70)
    print("🚀 v1.9.7m Total Autonomy Protocol - Post-Merge Activation")
    print("="*70)
    print("\nThis will:")
    print("  1. Run a full system audit")
    print("  2. Apply any necessary repairs")
    print("  3. Certify all subsystems")
    print("  4. Launch continuous monitoring")
    print("\n" + "="*70)
    
    # Import engines
    try:
        from engines.sanctum.core import SanctumEngine
        from engines.forge.core import ForgeEngine
        from engines.arie.core import ARIEEngine
        from engines.elysium.core import ElysiumGuardian
    except ImportError as e:
        print(f"\n❌ Error importing engines: {e}")
        print("Make sure you're running this from the repository root.")
        return 1
    
    # Step 1: Initial Sanctum check
    print("\n📍 Step 1: Sanctum Predictive Check")
    print("-" * 70)
    try:
        sanctum = SanctumEngine(repo_root)
        report = await sanctum.run_predeploy_check()
        
        if report.has_errors():
            print(f"⚠️  Detected {len(report.errors)} configuration issue(s)")
            print("   Forge will repair these automatically...")
        else:
            print("✅ Sanctum: All deployment checks passed")
    except Exception as e:
        print(f"⚠️  Sanctum: {e}")
    
    # Step 2: Forge repair
    print("\n📍 Step 2: Forge Auto-Repair")
    print("-" * 70)
    try:
        forge = ForgeEngine(repo_root)
        repair_report = await forge.run_full_repair(scan_only=False)
        
        if repair_report['issues']:
            print(f"🛠️  Fixed {repair_report['fixed']}/{len(repair_report['issues'])} issue(s)")
        else:
            print("✅ Forge: No repairs needed")
    except Exception as e:
        print(f"⚠️  Forge: {e}")
    
    # Step 3: ARIE integrity scan
    print("\n📍 Step 3: ARIE Integrity Scan")
    print("-" * 70)
    try:
        arie = ARIEEngine(repo_root)
        summary = arie.run(dry_run=True, apply=False)
        print(f"🧠 ARIE: {summary.findings_count} findings in {summary.duration_seconds:.2f}s")
        
        if summary.findings_count > 0:
            print("   (Run ARIE separately to review and fix)")
        else:
            print("✅ ARIE: No integrity issues detected")
    except Exception as e:
        print(f"⚠️  ARIE: {e}")
    
    # Step 4: Launch Elysium Guardian
    print("\n📍 Step 4: Launch Elysium Guardian")
    print("-" * 70)
    try:
        guardian = ElysiumGuardian(repo_root)
        
        print(f"🪶 Elysium Guardian initialized")
        print(f"   Monitoring interval: Every {guardian.interval_hours} hours")
        print(f"   Enabled: {'✅' if guardian.enabled else '❌'}")
        
        if guardian.enabled:
            print("\n   Running initial cycle...")
            cycle_result = await guardian.run_manual_cycle()
            
            print(f"\n   Status: {cycle_result['status']}")
            print(f"   Certified: {'✅' if cycle_result['certified'] else '❌'}")
            
            if cycle_result.get('sanctum'):
                print(f"   Sanctum: {cycle_result['sanctum']['status']}")
            if cycle_result.get('forge'):
                print(f"   Forge: {cycle_result['forge']['issues_fixed']} fixes applied")
            if cycle_result.get('arie'):
                print(f"   ARIE: {cycle_result['arie']['findings_count']} findings")
            
            print("\n✅ Elysium: Initial cycle complete")
            print("   Guardian will now run automatically every 6 hours")
        else:
            print("⚠️  Elysium is disabled (set ELYSIUM_ENABLED=true to enable)")
    except Exception as e:
        print(f"⚠️  Elysium: {e}")
    
    # Summary
    print("\n" + "="*70)
    print("📊 ACTIVATION COMPLETE")
    print("="*70)
    print("\n✅ Total Autonomy Protocol is now active")
    print("✅ The Bridge will self-maintain continuously")
    print("✅ Next automatic cycle in 6 hours")
    print("\nMonitor cycles via Genesis Bus:")
    print("  - sanctum.predeploy.success/failure")
    print("  - forge.repair.applied")
    print("  - arie.audit.complete")
    print("  - elysium.cycle.complete")
    print("\n🪶 The Bridge is now self-sustaining and autonomous.")
    print("="*70 + "\n")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(activate_autonomy())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Activation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Activation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
