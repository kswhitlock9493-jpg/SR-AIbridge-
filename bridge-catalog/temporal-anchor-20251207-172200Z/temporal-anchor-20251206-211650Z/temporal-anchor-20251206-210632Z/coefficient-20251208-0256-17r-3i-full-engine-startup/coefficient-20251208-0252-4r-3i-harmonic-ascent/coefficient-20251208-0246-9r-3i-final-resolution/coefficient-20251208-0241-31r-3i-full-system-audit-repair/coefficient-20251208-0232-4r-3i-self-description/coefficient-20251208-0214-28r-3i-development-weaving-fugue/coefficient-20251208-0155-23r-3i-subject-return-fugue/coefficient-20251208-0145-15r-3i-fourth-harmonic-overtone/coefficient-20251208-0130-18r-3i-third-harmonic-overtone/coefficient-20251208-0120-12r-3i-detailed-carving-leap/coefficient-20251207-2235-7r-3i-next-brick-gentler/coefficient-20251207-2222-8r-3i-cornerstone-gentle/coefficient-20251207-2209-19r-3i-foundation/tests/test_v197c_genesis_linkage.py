"""
Unit tests for v1.9.7c Genesis Linkage
Tests Blueprint Registry and engine linkages
"""
import pytest
from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry


def test_blueprint_registry_load_all():
    """Test loading all engine blueprints"""
    manifest = BlueprintRegistry.load_all()
    
    # Should have core engines
    assert "tde_x" in manifest
    assert "blueprint" in manifest
    assert "cascade" in manifest
    assert "truth" in manifest
    assert "autonomy" in manifest
    
    # Check TDE-X blueprint structure
    tde_x = manifest["tde_x"]
    assert tde_x["name"] == "TDE-X"
    assert "shards" in tde_x
    assert set(tde_x["shards"]) == {"bootstrap", "runtime", "diagnostics"}
    assert "deploy.signals" in tde_x["topics"]


def test_blueprint_registry_get_engine():
    """Test getting specific engine blueprint"""
    cascade = BlueprintRegistry.get_engine("cascade")
    
    assert cascade["name"] == "Cascade Engine"
    assert "schema" in cascade
    assert "dependencies" in cascade
    assert "blueprint" in cascade["dependencies"]


def test_blueprint_registry_get_dependencies():
    """Test getting engine dependencies"""
    # Cascade depends on Blueprint
    cascade_deps = BlueprintRegistry.get_dependencies("cascade")
    assert "blueprint" in cascade_deps
    
    # Truth depends on Blueprint
    truth_deps = BlueprintRegistry.get_dependencies("truth")
    assert "blueprint" in truth_deps
    
    # Autonomy depends on Blueprint and Truth
    autonomy_deps = BlueprintRegistry.get_dependencies("autonomy")
    assert "blueprint" in autonomy_deps
    assert "truth" in autonomy_deps
    
    # Blueprint has no dependencies
    blueprint_deps = BlueprintRegistry.get_dependencies("blueprint")
    assert len(blueprint_deps) == 0


def test_blueprint_registry_get_topics():
    """Test getting engine topics"""
    # TDE-X publishes to deploy.signals
    tde_topics = BlueprintRegistry.get_topics("tde_x")
    assert "deploy.signals" in tde_topics
    
    # Blueprint publishes to blueprint.events
    blueprint_topics = BlueprintRegistry.get_topics("blueprint")
    assert "blueprint.events" in blueprint_topics
    
    # Cascade subscribes to multiple topics
    cascade_topics = BlueprintRegistry.get_topics("cascade")
    assert "deploy.graph" in cascade_topics


def test_blueprint_registry_validate_integrity():
    """Test manifest integrity validation"""
    validation = BlueprintRegistry.validate_manifest_integrity()
    
    assert validation["valid"] is True
    assert len(validation["errors"]) == 0
    assert validation["engine_count"] > 0


@pytest.mark.anyio
async def test_tde_link_preload_manifest():
    """Test TDE-X link manifest preloading"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.tde_link import preload_manifest
    
    manifest = await preload_manifest()
    
    assert isinstance(manifest, dict)
    assert len(manifest) > 0
    assert "tde_x" in manifest


def test_tde_link_validate_shard():
    """Test TDE-X shard validation"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.tde_link import validate_shard
    
    manifest = BlueprintRegistry.load_all()
    
    # Valid shards
    assert validate_shard("bootstrap", manifest) is True
    assert validate_shard("runtime", manifest) is True
    assert validate_shard("diagnostics", manifest) is True
    
    # Invalid shard
    assert validate_shard("invalid_shard", manifest) is False


def test_cascade_link_get_config():
    """Test Cascade link configuration extraction"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.cascade_link import get_cascade_config
    
    manifest = BlueprintRegistry.load_all()
    config = get_cascade_config(manifest)
    
    assert config["name"] == "Cascade Engine"
    assert "schema" in config
    assert "dependencies" in config
    assert "blueprint" in config["dependencies"]


def test_autonomy_link_get_rules():
    """Test Autonomy link rules extraction"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.autonomy_link import get_autonomy_rules
    
    manifest = BlueprintRegistry.load_all()
    rules = get_autonomy_rules(manifest)
    
    assert "guardrails" in rules
    assert "scaling_policies" in rules
    assert "self_healing" in rules
    
    # Check guardrails
    guardrails = rules["guardrails"]
    assert "mode" in guardrails
    assert "safe_actions" in guardrails
    assert "restricted_actions" in guardrails


def test_autonomy_link_action_allowed():
    """Test Autonomy link action validation"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.autonomy_link import _is_action_allowed
    
    manifest = BlueprintRegistry.load_all()
    rules = {
        "guardrails": {
            "mode": "strict",
            "safe_actions": ["read", "validate"],
            "restricted_actions": ["delete", "drop"]
        }
    }
    
    # Safe actions should be allowed
    assert _is_action_allowed("read", rules) is True
    assert _is_action_allowed("validate", rules) is True
    
    # Restricted actions should be blocked
    assert _is_action_allowed("delete", rules) is False
    assert _is_action_allowed("drop", rules) is False
    
    # Unknown actions in strict mode should be blocked
    assert _is_action_allowed("unknown", rules) is False


@pytest.mark.anyio
async def test_truth_link_validate_sync():
    """Test Truth link blueprint sync validation"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.truth_link import validate_blueprint_sync
    
    manifest = BlueprintRegistry.load_all()
    
    # Same manifest should be synced
    result = await validate_blueprint_sync(manifest, manifest)
    assert result["synced"] is True
    assert result["manifest_hash"] == result["deployed_hash"]
    
    # Different state should show drift
    different_state = {"different": "data"}
    result = await validate_blueprint_sync(manifest, different_state)
    assert result["synced"] is False


@pytest.mark.anyio
async def test_truth_link_certify_fact():
    """Test Truth link fact certification"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.truth_link import certify_fact
    
    manifest = BlueprintRegistry.load_all()
    
    fact = {
        "type": "deploy.status",
        "data": {
            "status": "healthy",
            "timestamp": "2025-10-11T00:00:00Z"
        }
    }
    
    certification = await certify_fact(fact, manifest)
    
    assert certification["fact_type"] == "deploy.status"
    assert "valid" in certification
    assert "certified_at" in certification


@pytest.mark.anyio
async def test_autonomy_link_execute_action():
    """Test Autonomy link action execution with guardrails"""
    from bridge_backend.bridge_core.engines.blueprint.adapters.autonomy_link import (
        execute_action_with_guardrails,
        get_autonomy_rules
    )
    
    manifest = BlueprintRegistry.load_all()
    rules = get_autonomy_rules(manifest)
    facts = {"some": "facts"}
    
    # Safe action should succeed
    safe_action = {"type": "read", "target": "config"}
    result = await execute_action_with_guardrails(safe_action, rules, facts)
    assert result["success"] is True
    
    # Restricted action should be blocked
    restricted_action = {"type": "delete", "target": "data"}
    result = await execute_action_with_guardrails(restricted_action, rules, facts)
    assert result["success"] is False
    assert result["reason"] == "blocked_by_guardrails"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
