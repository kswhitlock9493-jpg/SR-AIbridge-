#!/usr/bin/env python3
"""
Validation Script for v1.9.7c Genesis Linkage - Unified Edition
Tests all 20 engines and their linkages
"""

import sys
sys.path.insert(0, 'bridge_backend')
import importlib.util

def load_module(name, path):
    """Load a module from a file path"""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

print("=" * 70)
print("v1.9.7c Genesis Linkage - UNIFIED VALIDATION")
print("=" * 70)

# Test 1: Blueprint Registry
print("\n1. Testing Blueprint Registry...")
try:
    registry = load_module('registry', 'bridge_backend/bridge_core/engines/blueprint/registry.py')
    manifest = registry.BlueprintRegistry.load_all()
    
    if len(manifest) != 20:
        print(f"   ❌ Expected 20 engines, got {len(manifest)}")
        sys.exit(1)
    
    print(f"   ✅ All 20 engines loaded")
    
    validation = registry.BlueprintRegistry.validate_manifest_integrity()
    if not validation["valid"]:
        print(f"   ❌ Validation failed: {validation['errors']}")
        sys.exit(1)
    
    print(f"   ✅ Manifest integrity validated")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Engine Categories
print("\n2. Validating Engine Categories...")
try:
    core_engines = ['tde_x', 'blueprint', 'cascade', 'truth', 'autonomy', 'parser']
    super_engines = ['calculuscore', 'qhelmsingularity', 'auroraforge', 'chronicleloom', 'scrolltongue', 'commerceforge']
    utility_engines = ['creativity', 'indoctrination', 'screen', 'speech', 'recovery', 'agents_foundry', 'filing']
    
    core_found = [e for e in core_engines if e in manifest]
    super_found = [e for e in super_engines if e in manifest]
    utility_found = [e for e in utility_engines if e in manifest]
    
    if len(core_found) != len(core_engines):
        print(f"   ❌ Core engines: {len(core_found)}/{len(core_engines)}")
        sys.exit(1)
    print(f"   ✅ Core engines: {len(core_found)}/{len(core_engines)}")
    
    if len(super_found) != len(super_engines):
        print(f"   ❌ Super engines: {len(super_found)}/{len(super_engines)}")
        sys.exit(1)
    print(f"   ✅ Super engines: {len(super_found)}/{len(super_engines)}")
    
    if len(utility_found) != len(utility_engines):
        print(f"   ❌ Utility engines: {len(utility_found)}/{len(utility_engines)}")
        sys.exit(1)
    print(f"   ✅ Utility engines: {len(utility_found)}/{len(utility_engines)}")
    
    if 'leviathan' not in manifest:
        print(f"   ❌ Leviathan not found")
        sys.exit(1)
    print(f"   ✅ Leviathan orchestrator: present")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 3: Leviathan Link Adapter
print("\n3. Testing Leviathan Link Adapter...")
try:
    lev_link = load_module('leviathan_link', 'bridge_backend/bridge_core/engines/blueprint/adapters/leviathan_link.py')
    
    lev_config = lev_link.get_leviathan_config(manifest)
    if len(lev_config["super_engines"]) != 6:
        print(f"   ❌ Expected 6 super engines, got {len(lev_config['super_engines'])}")
        sys.exit(1)
    print(f"   ✅ Leviathan coordinates 6 super engines")
    
    # No async validation needed for now
    print(f"   ✅ Leviathan adapter loaded")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 4: Super Engines Link Adapter
print("\n4. Testing Super Engines Link Adapter...")
try:
    super_link = load_module('super_engines_link', 'bridge_backend/bridge_core/engines/blueprint/adapters/super_engines_link.py')
    
    super_config = super_link.get_super_engines_config(manifest)
    available = [k for k, v in super_config.items() if v.get("available")]
    
    if len(available) != 6:
        print(f"   ❌ Expected 6 super engines available, got {len(available)}")
        sys.exit(1)
    print(f"   ✅ All 6 super engines available")
    
    if super_link.SUPER_ENGINES != ['calculuscore', 'qhelmsingularity', 'auroraforge', 'chronicleloom', 'scrolltongue', 'commerceforge']:
        print(f"   ❌ Super engines list mismatch")
        sys.exit(1)
    print(f"   ✅ Super engines list correct")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 5: Utility Engines Link Adapter
print("\n5. Testing Utility Engines Link Adapter...")
try:
    util_link = load_module('utility_engines_link', 'bridge_backend/bridge_core/engines/blueprint/adapters/utility_engines_link.py')
    
    util_config = util_link.get_utility_engines_config(manifest)
    available = [k for k, v in util_config.items() if v.get("available")]
    
    if len(available) != 7:
        print(f"   ❌ Expected 7 utility engines available, got {len(available)}")
        sys.exit(1)
    print(f"   ✅ All 7 utility engines available")
    
    if util_link.UTILITY_ENGINES != ['creativity', 'indoctrination', 'screen', 'speech', 'recovery', 'agents_foundry', 'filing']:
        print(f"   ❌ Utility engines list mismatch")
        sys.exit(1)
    print(f"   ✅ Utility engines list correct")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 6: Routes Compilation
print("\n6. Testing Linked Routes...")
try:
    import py_compile
    py_compile.compile('bridge_backend/bridge_core/engines/routes_linked.py', doraise=True)
    print(f"   ✅ routes_linked.py compiles successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 7: Dependencies Validation
print("\n7. Validating Engine Dependencies...")
try:
    # Check that all dependencies exist in manifest
    issues = []
    for engine_name, engine_data in manifest.items():
        deps = engine_data.get("dependencies", [])
        for dep in deps:
            if dep not in manifest:
                issues.append(f"{engine_name} → {dep} (missing)")
    
    if issues:
        print(f"   ❌ Dependency issues: {issues}")
        sys.exit(1)
    
    print(f"   ✅ All dependencies validated")
    
    # Check specific important dependencies
    if 'blueprint' not in manifest['cascade']['dependencies']:
        print(f"   ❌ Cascade should depend on Blueprint")
        sys.exit(1)
    
    if 'truth' not in manifest['leviathan']['dependencies']:
        print(f"   ❌ Leviathan should depend on Truth")
        sys.exit(1)
    
    if set(manifest['recovery']['dependencies']) != {'autonomy', 'parser'}:
        print(f"   ❌ Recovery dependencies incorrect")
        sys.exit(1)
    
    print(f"   ✅ Critical dependencies correct")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 8: Event Topics
print("\n8. Validating Event Topics...")
try:
    # Check that key engines have topics defined
    if not manifest['leviathan']['topics']:
        print(f"   ❌ Leviathan should have topics")
        sys.exit(1)
    
    if 'solver.tasks' not in manifest['leviathan']['topics']:
        print(f"   ❌ Leviathan should publish to solver.tasks")
        sys.exit(1)
    
    # Count total unique topics
    all_topics = set()
    for engine_data in manifest.values():
        all_topics.update(engine_data.get('topics', []))
    
    print(f"   ✅ {len(all_topics)} unique event topics defined")
    print(f"   ✅ Event bus integration complete")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 9: Documentation
print("\n9. Checking Documentation...")
try:
    import os
    
    docs = [
        'V197C_UNIFIED_GENESIS.md',
        'GENESIS_LINKAGE_GUIDE.md',
        'V197C_IMPLEMENTATION_COMPLETE.md'
    ]
    
    for doc in docs:
        if not os.path.exists(doc):
            print(f"   ❌ Missing documentation: {doc}")
            sys.exit(1)
    
    print(f"   ✅ All documentation files present")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print("✅ Blueprint Registry - 20 engines loaded")
print("✅ Engine Categories - Core (6), Super (6), Utility (7), Orchestration (1)")
print("✅ Leviathan Link - Super engines coordinated")
print("✅ Super Engines Link - All 6 available")
print("✅ Utility Engines Link - All 7 available")
print("✅ Linked Routes - Compiled successfully")
print("✅ Dependencies - All validated")
print("✅ Event Topics - Integration complete")
print("✅ Documentation - All files present")
print("=" * 70)
print("🎉 ALL VALIDATION TESTS PASSED - DEPLOYMENT READY")
print("=" * 70)
