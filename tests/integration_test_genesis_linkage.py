#!/usr/bin/env python3
"""
Integration test for v1.9.7c Genesis Linkage
Validates end-to-end functionality of all linkages
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
from bridge_backend.bridge_core.engines.blueprint.adapters import tde_link, cascade_link, truth_link, autonomy_link


async def test_integration():
    """Run full integration test of Genesis Linkage"""
    print("🚀 Genesis Linkage Integration Test")
    print("=" * 50)
    
    # Step 1: Load Blueprint Registry
    print("\n1. Loading Blueprint Registry...")
    manifest = BlueprintRegistry.load_all()
    print(f"   ✅ Loaded {len(manifest)} engine blueprints")
    
    # Step 2: Validate manifest integrity
    print("\n2. Validating manifest integrity...")
    validation = BlueprintRegistry.validate_manifest_integrity()
    if validation["valid"]:
        print(f"   ✅ Manifest valid ({validation['engine_count']} engines)")
    else:
        print(f"   ❌ Validation errors: {validation['errors']}")
        return False
    
    # Step 3: TDE-X Link - Preload manifest
    print("\n3. Testing TDE-X Link...")
    tde_manifest = await tde_link.preload_manifest()
    print(f"   ✅ Manifest preloaded: {len(tde_manifest)} engines")
    
    # Validate TDE-X shards
    shards_valid = all(
        tde_link.validate_shard(shard, tde_manifest)
        for shard in ["bootstrap", "runtime", "diagnostics"]
    )
    if shards_valid:
        print("   ✅ All TDE-X shards validated")
    else:
        print("   ❌ Shard validation failed")
        return False
    
    # Step 4: Cascade Link - Get configuration
    print("\n4. Testing Cascade Link...")
    cascade_config = cascade_link.get_cascade_config(manifest)
    print(f"   ✅ Cascade config loaded: {cascade_config['name']}")
    print(f"   📋 Dependencies: {cascade_config['dependencies']}")
    
    # Step 5: Truth Link - Validate sync
    print("\n5. Testing Truth Link...")
    sync_result = await truth_link.validate_blueprint_sync(manifest, manifest)
    if sync_result["synced"]:
        print(f"   ✅ Blueprint sync validated")
        print(f"   🔒 Hash: {sync_result['manifest_hash']}")
    else:
        print("   ❌ Sync validation failed")
        return False
    
    # Test fact certification
    test_fact = {
        "type": "test.fact",
        "data": {"status": "healthy"}
    }
    cert = await truth_link.certify_fact(test_fact, manifest)
    if cert["valid"]:
        print(f"   ✅ Fact certification passed")
    else:
        print("   ❌ Fact certification failed")
        return False
    
    # Step 6: Autonomy Link - Get rules and test action
    print("\n6. Testing Autonomy Link...")
    autonomy_rules = autonomy_link.get_autonomy_rules(manifest)
    print(f"   ✅ Autonomy rules loaded")
    print(f"   🛡️  Guardrails mode: {autonomy_rules['guardrails']['mode']}")
    
    # Test safe action
    safe_action = {"type": "read", "target": "config"}
    facts = {"test": "facts"}
    action_result = await autonomy_link.execute_action_with_guardrails(
        safe_action, autonomy_rules, facts
    )
    if action_result["success"]:
        print(f"   ✅ Safe action executed")
    else:
        print(f"   ❌ Action failed: {action_result.get('reason')}")
        return False
    
    # Test restricted action
    restricted_action = {"type": "delete", "target": "data"}
    restricted_result = await autonomy_link.execute_action_with_guardrails(
        restricted_action, autonomy_rules, facts
    )
    if not restricted_result["success"] and restricted_result["reason"] == "blocked_by_guardrails":
        print(f"   ✅ Restricted action properly blocked")
    else:
        print(f"   ❌ Guardrails failed to block restricted action")
        return False
    
    # Step 7: Verify dependencies
    print("\n7. Verifying engine dependencies...")
    for engine_name in ["cascade", "truth", "autonomy"]:
        deps = BlueprintRegistry.get_dependencies(engine_name)
        topics = BlueprintRegistry.get_topics(engine_name)
        print(f"   {engine_name}:")
        print(f"     - Dependencies: {deps}")
        print(f"     - Topics: {topics}")
    
    print("\n" + "=" * 50)
    print("✅ All integration tests passed!")
    print("=" * 50)
    return True


if __name__ == "__main__":
    result = asyncio.run(test_integration())
    sys.exit(0 if result else 1)
