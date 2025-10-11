#!/usr/bin/env python3
"""
Demo: Compliance Integration with Autonomy Engine
Shows how copyright, license, and LOC engines work together
"""
import sys
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent / "bridge_backend"))

from bridge_core.engines.autonomy import AutonomyEngine, ComplianceValidator
import json


def print_section(title):
    """Print a section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_basic_compliance():
    """Demo 1: Basic compliance validation"""
    print_section("Demo 1: Basic Compliance Validation")
    
    engine = AutonomyEngine(enable_compliance=True)
    
    print("Creating task with automatic compliance validation...")
    task = engine.create_task(
        project="demo_project",
        captain="DemoCaptain",
        objective="demonstrate_compliance_integration",
        permissions={"read": ["src"], "write": ["docs"]},
        mode="screen"
    )
    
    print(f"✅ Task created: {task.id}")
    print(f"   Project: {task.project}")
    print(f"   Captain: {task.captain}")
    print(f"   Objective: {task.objective}")
    
    if task.compliance_validation:
        state = task.compliance_validation.get("compliance_state", {})
        print(f"\n📋 Compliance State: {state.get('state', 'unknown').upper()}")
        print(f"   License Compliant: {state.get('license_compliant', False)}")
        print(f"   Copyright Original: {state.get('copyright_original', False)}")
        print(f"   Safe to Proceed: {state.get('safe_to_proceed', False)}")
        
        # Show LOC metrics
        loc = task.compliance_validation.get("loc_metrics", {})
        print(f"\n📊 LOC Metrics:")
        print(f"   Total Lines: {loc.get('total_lines', 0):,}")
        print(f"   Files Counted: {loc.get('files_counted', 0)}")
        
        by_ext = loc.get("by_extension", {})
        if by_ext:
            print(f"   By Extension:")
            for ext, lines in sorted(by_ext.items(), key=lambda x: x[1], reverse=True):
                print(f"     {ext}: {lines:,} lines")
    
    return task


def demo_loc_update():
    """Demo 2: Updating LOC metrics"""
    print_section("Demo 2: Updating LOC Metrics")
    
    engine = AutonomyEngine(enable_compliance=False)
    
    print("Creating task without initial compliance...")
    task = engine.create_task(
        project="demo_project_2",
        captain="DemoCaptain",
        objective="track_loc_growth",
        permissions={"write": ["src"]},
        mode="screen",
        validate_compliance=False
    )
    
    print(f"✅ Task created: {task.id}")
    
    print("\nUpdating LOC metrics as work progresses...")
    
    # Simulate LOC growth over time
    updates = [
        {"total_lines": 100, "files_counted": 2, "by_extension": {".py": 100}},
        {"total_lines": 350, "files_counted": 5, "by_extension": {".py": 280, ".js": 70}},
        {"total_lines": 750, "files_counted": 10, "by_extension": {".py": 600, ".js": 150}},
    ]
    
    for i, update in enumerate(updates, 1):
        updated_task = engine.update_task_loc(task.id, update)
        print(f"\n  Update {i}: {update['total_lines']:,} lines across {update['files_counted']} files")
        for ext, lines in update["by_extension"].items():
            print(f"    {ext}: {lines:,} lines")
    
    return task


def demo_compliance_states():
    """Demo 3: Different compliance states"""
    print_section("Demo 3: Compliance State Examples")
    
    validator = ComplianceValidator()
    
    # Example 1: Compliant state
    print("Example 1: Compliant (all checks passed)")
    license_ok = {"compliant": True, "violations": []}
    copyright_ok = {"original": True, "suspicious_matches": [], "flagged_matches": []}
    state = validator._evaluate_compliance(license_ok, copyright_ok)
    print(f"  State: {state['state'].upper()}")
    print(f"  Safe to Proceed: {state['safe_to_proceed']}")
    print(f"  Reason: {state['reason']}")
    
    # Example 2: Flagged state
    print("\nExample 2: Flagged (potential issues)")
    copyright_flagged = {
        "original": True, 
        "suspicious_matches": [],
        "flagged_matches": [{"file": "utils.py", "confidence": 0.7}]
    }
    state = validator._evaluate_compliance(license_ok, copyright_flagged)
    print(f"  State: {state['state'].upper()}")
    print(f"  Safe to Proceed: {state['safe_to_proceed']}")
    print(f"  Reason: {state['reason']}")
    
    # Example 3: Blocked state
    print("\nExample 3: Blocked (critical violations)")
    license_blocked = {
        "compliant": False,
        "violations": [{"file": "main.py", "license": "GPL-3.0"}]
    }
    state = validator._evaluate_compliance(license_blocked, copyright_ok)
    print(f"  State: {state['state'].upper()}")
    print(f"  Safe to Proceed: {state['safe_to_proceed']}")
    print(f"  Reason: {state['reason']}")


def demo_license_detection():
    """Demo 4: License detection"""
    print_section("Demo 4: License Detection")
    
    # Create test files with different licenses
    test_files = [
        ("test_mit.py", "# SPDX-License-Identifier: MIT\nprint('hello')"),
        ("test_apache.py", "# Licensed under the Apache License, Version 2.0\nprint('world')"),
        ("test_unknown.py", "# No license\nprint('test')"),
    ]
    
    print("Creating test files with different licenses...")
    for filename, content in test_files:
        path = Path(filename)
        path.write_text(content)
        print(f"  ✓ {filename}")
    
    validator = ComplianceValidator()
    
    try:
        print("\nScanning licenses...")
        result = validator._scan_licenses(Path("."), [f[0] for f in test_files])
        
        print(f"\n📋 Scan Results:")
        print(f"  Compliant: {result['compliant']}")
        print(f"  Files Scanned: {result['files_scanned']}")
        print(f"\n  Licenses Detected:")
        for lic, count in result['licenses'].items():
            print(f"    {lic}: {count} file(s)")
        
        if result['violations']:
            print(f"\n  ⚠️  Violations: {len(result['violations'])}")
            for v in result['violations']:
                print(f"    {v['file']}: {v['license']} ({v['reason']})")
    
    finally:
        # Cleanup
        print("\nCleaning up test files...")
        for filename, _ in test_files:
            path = Path(filename)
            if path.exists():
                path.unlink()
                print(f"  ✓ Removed {filename}")


def demo_vault_storage():
    """Demo 5: Vault storage"""
    print_section("Demo 5: Vault Storage and Retrieval")
    
    engine = AutonomyEngine(enable_compliance=True)
    
    print("Creating task with compliance validation...")
    task = engine.create_task(
        project="vault_demo",
        captain="VaultCaptain",
        objective="demonstrate_vault_storage",
        permissions={"read": ["vault"]},
        mode="screen"
    )
    
    print(f"✅ Task created: {task.id}")
    
    # Check vault storage
    seal_path = task.seal_path()
    print(f"\n📁 Task sealed to: {seal_path}")
    print(f"   File exists: {seal_path.exists()}")
    
    if seal_path.exists():
        print("\n   Task contract preview:")
        with open(seal_path, 'r') as f:
            data = json.load(f)
            print(f"   - ID: {data.get('id', 'N/A')[:20]}...")
            print(f"   - Project: {data.get('project', 'N/A')}")
            print(f"   - Status: {data.get('status', 'N/A')}")
            print(f"   - Has Compliance: {'compliance_validation' in data}")
    
    # Retrieve compliance validation
    print("\n🔍 Retrieving compliance validation...")
    validation = engine.get_compliance_validation(task.id)
    if validation:
        print(f"   ✓ Validation retrieved")
        print(f"   State: {validation.get('compliance_state', {}).get('state', 'unknown')}")
    
    return task


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("  SR-AIbridge Compliance Integration Demo")
    print("  Copyright + License + LOC + Autonomy Engine")
    print("="*70)
    
    try:
        # Run demos
        demo_basic_compliance()
        demo_loc_update()
        demo_compliance_states()
        demo_license_detection()
        demo_vault_storage()
        
        # Summary
        print_section("Summary")
        print("✅ Anti-Copyright Engine: Integrated (counterfeit detection)")
        print("✅ Compliance Engine: Integrated (license scanning)")
        print("✅ LOC Engine: Integrated (line counting)")
        print("✅ Autonomy Engine: Enhanced with compliance validation")
        print("\n🎉 All engines working together!")
        print("\nResult: Autonomous tasks start original and open-source compliant!")
        print("        Nothing accidentally stolen! 🛡️\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
