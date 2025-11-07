"""
Forge Dominion Policy API
Serves BCSE quality policies with Dominion Seal authentication
"""
from fastapi import APIRouter, Header, HTTPException, Query
import os
import yaml
from typing import Dict, Any, Optional

router = APIRouter(prefix="/forge/policy", tags=["forge-policy"])


def _load_yaml(path: str) -> dict:
    """Load YAML file safely"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Failed to load policy file {path}: {e}")
        return {}


def _merge_policies(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two policy dictionaries"""
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_policies(result[key], value)
        else:
            result[key] = value
    
    return result


def _apply_federation_modifiers(
    policy: Dict[str, Any], 
    role: str, 
    federation_config: Dict[str, Any]
) -> Dict[str, Any]:
    """Apply federation role modifiers to policy"""
    if role not in federation_config:
        return policy
    
    modifiers = federation_config[role]
    result = policy.copy()
    
    for key, value in modifiers.items():
        if isinstance(value, str) and value.startswith(("+", "-")):
            # Relative modifier
            if key in result:
                try:
                    base_value = result[key]
                    modifier_value = float(value)
                    
                    if isinstance(base_value, (int, float)):
                        result[key] = base_value + modifier_value
                except (ValueError, TypeError):
                    pass
        else:
            # Absolute override
            result[key] = value
    
    return result


@router.get("/quality")
def get_quality_policy(
    branch: str = Query(default="main", description="Git branch name"),
    environment: Optional[str] = Query(default=None, description="Environment (development/staging/production)"),
    federation_role: Optional[str] = Query(default=None, description="BRH federation role (leader/witness)"),
    authorization: str = Header(default="")
):
    """
    Get quality policy for a specific branch, environment, and federation role
    
    Args:
        branch: Git branch name (e.g., 'main', 'feature/add-bcse')
        environment: Environment tier (development, staging, production)
        federation_role: BRH federation role (leader, witness)
        authorization: Bearer token with Dominion Seal
        
    Returns:
        Merged policy configuration for the specified context
    """
    # Validate Dominion Seal
    seal = os.getenv("DOMINION_SEAL", "")
    if seal and authorization != f"Bearer {seal}":
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Dominion Seal")
    
    # Load base policy
    policy_path = "bridge_tools/bcse/policies.yaml"
    base = _load_yaml(policy_path)
    
    if not base:
        raise HTTPException(status_code=500, detail="Policy file not found or invalid")
    
    # Start with defaults
    defaults = base.get("defaults", {})
    result = defaults.copy()
    
    # Apply environment overrides if specified
    if environment:
        env_config = base.get("env", {})
        if environment in env_config:
            result = _merge_policies(result, env_config[environment])
    else:
        # Infer environment from branch if not specified
        if branch.startswith("feature/") or branch == "develop":
            environment = "development"
        elif branch.startswith("staging/"):
            environment = "staging"
        elif branch in ("main", "master") or branch.startswith("release/"):
            environment = "production"
        else:
            environment = "development"
        
        env_config = base.get("env", {})
        if environment in env_config:
            result = _merge_policies(result, env_config[environment])
    
    # Apply branch-specific overrides
    branches = base.get("branches", {})
    
    # Check for exact match first
    if branch in branches:
        result = _merge_policies(result, branches[branch])
    else:
        # Check for pattern matches (e.g., "feature/*")
        for pattern, branch_policy in branches.items():
            if pattern.endswith("/*"):
                prefix = pattern[:-2]
                if branch.startswith(prefix + "/"):
                    result = _merge_policies(result, branch_policy)
                    break
    
    # Apply federation role modifiers if specified
    if federation_role and federation_role in ("leader", "witness"):
        federation_config = base.get("federation", {})
        if federation_config:
            result = _apply_federation_modifiers(result, federation_role, federation_config)
    
    # Include metadata
    result["_context"] = {
        "branch": branch,
        "environment": environment,
        "federation_role": federation_role,
        "version": base.get("version", "unknown")
    }
    
    # Optionally include the full raw policy for advanced clients
    result["_raw"] = base
    
    return result


@router.get("/version")
def get_policy_version():
    """Get the current policy version"""
    policy_path = "bridge_tools/bcse/policies.yaml"
    base = _load_yaml(policy_path)
    
    return {
        "version": base.get("version", "unknown"),
        "seal_required": bool(os.getenv("DOMINION_SEAL"))
    }


@router.get("/branches")
def list_branch_policies():
    """List all available branch-specific policies"""
    policy_path = "bridge_tools/bcse/policies.yaml"
    base = _load_yaml(policy_path)
    
    branches = base.get("branches", {})
    
    return {
        "count": len(branches),
        "branches": list(branches.keys())
    }


@router.get("/environments")
def list_environment_policies():
    """List all available environment-specific policies"""
    policy_path = "bridge_tools/bcse/policies.yaml"
    base = _load_yaml(policy_path)
    
    environments = base.get("env", {})
    
    return {
        "count": len(environments),
        "environments": list(environments.keys())
    }
