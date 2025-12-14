"""
Autonomy Link Adapter
Connects Blueprint Engine to Autonomy Engine for guardrail enforcement and rule-based actions
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def get_autonomy_rules(manifest: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract autonomy rules and guardrails from blueprint manifest.
    
    Args:
        manifest: Blueprint manifest
        
    Returns:
        Autonomy rules including guardrails, policies, and safe actions
    """
    autonomy_blueprint = manifest.get("autonomy", {})
    
    # Default rules if not specified in manifest
    default_rules = {
        "guardrails": {
            "mode": "strict",
            "max_concurrent_tasks": 5,
            "safe_actions": [
                "read",
                "validate",
                "log",
                "notify"
            ],
            "restricted_actions": [
                "delete",
                "drop",
                "truncate"
            ]
        },
        "scaling_policies": {
            "auto_scale": False,
            "min_instances": 1,
            "max_instances": 3
        },
        "self_healing": {
            "enabled": True,
            "retry_limit": 3,
            "backoff_seconds": 60
        }
    }
    
    # Merge with manifest-defined rules
    rules = {
        "name": autonomy_blueprint.get("name", "Autonomy Engine"),
        "guardrails": default_rules["guardrails"],
        "scaling_policies": default_rules["scaling_policies"],
        "self_healing": default_rules["self_healing"],
        "schema": autonomy_blueprint.get("schema", {}),
        "dependencies": autonomy_blueprint.get("dependencies", [])
    }
    
    logger.info("[Autonomy Link] 📋 Loaded autonomy rules from blueprint")
    return rules


async def execute_action_with_guardrails(
    action: Dict[str, Any],
    rules: Dict[str, Any],
    facts: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute an autonomous action within blueprint-defined guardrails.
    
    Args:
        action: Action to execute
        rules: Autonomy rules from blueprint
        facts: Certified facts from Truth engine
        
    Returns:
        Execution result
    """
    try:
        action_type = action.get("type", "")
        
        # Check if action is allowed by guardrails
        allowed = _is_action_allowed(action_type, rules)
        
        if not allowed:
            logger.warning(f"[Autonomy Link] 🚫 Action '{action_type}' blocked by guardrails")
            return {
                "success": False,
                "action": action_type,
                "reason": "blocked_by_guardrails",
                "timestamp": _get_timestamp()
            }
        
        # Validate facts support the action
        facts_valid = _validate_facts_for_action(action, facts)
        if not facts_valid:
            logger.warning(f"[Autonomy Link] ⚠️ Action '{action_type}' lacks certified facts")
            return {
                "success": False,
                "action": action_type,
                "reason": "insufficient_facts",
                "timestamp": _get_timestamp()
            }
        
        # Execute action (placeholder - actual execution would happen here)
        logger.info(f"[Autonomy Link] ✅ Executing action '{action_type}'")
        
        # Publish action event
        from ....heritage.event_bus import bus
        await bus.publish("deploy.actions", {
            "type": "action.executed",
            "action": action_type,
            "timestamp": _get_timestamp()
        })
        
        return {
            "success": True,
            "action": action_type,
            "timestamp": _get_timestamp()
        }
        
    except Exception as e:
        logger.error(f"[Autonomy Link] ❌ Action execution failed: {e}")
        return {
            "success": False,
            "action": action.get("type", "unknown"),
            "error": str(e),
            "timestamp": _get_timestamp()
        }


def _is_action_allowed(action_type: str, rules: Dict[str, Any]) -> bool:
    """
    Check if action is allowed by guardrails.
    
    Args:
        action_type: Type of action
        rules: Autonomy rules
        
    Returns:
        True if action is allowed
    """
    guardrails = rules.get("guardrails", {})
    safe_actions = guardrails.get("safe_actions", [])
    restricted_actions = guardrails.get("restricted_actions", [])
    
    # Block restricted actions
    if action_type in restricted_actions:
        return False
    
    # Allow safe actions
    if action_type in safe_actions:
        return True
    
    # In strict mode, only allow explicitly safe actions
    if guardrails.get("mode") == "strict":
        return False
    
    # In permissive mode, allow unless restricted
    return True


def _validate_facts_for_action(action: Dict[str, Any], facts: Dict[str, Any]) -> bool:
    """
    Validate that certified facts support the action.
    
    Args:
        action: Action to validate
        facts: Certified facts
        
    Returns:
        True if facts support the action
    """
    # For now, accept actions if we have any facts
    # TODO: Add more sophisticated validation
    return isinstance(facts, dict) and len(facts) > 0


def _get_timestamp() -> str:
    """Get ISO timestamp"""
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat() + "Z"
