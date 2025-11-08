"""Forge Dominion Integration - Sovereign Policy Fetching"""
import os
import json
import urllib.request
from typing import Dict, Any, Optional


def dominion_root() -> str:
    """Get the Forge Dominion root endpoint"""
    root = os.getenv("FORGE_DOMINION_ROOT") or "dominion://local"
    return root


def get_current_branch() -> str:
    """
    Get the current git branch name
    
    Returns:
        Branch name (e.g., 'main', 'feature/add-bcse', etc.)
    """
    # Try GitHub Actions environment first
    github_ref = os.getenv("GITHUB_REF_NAME")
    if github_ref:
        return github_ref
    
    # Try to get from git
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    
    # Default fallback
    return "main"


def get_environment() -> str:
    """
    Get the current environment (development, staging, production)
    
    Returns:
        Environment name
    """
    env = os.getenv("ENVIRONMENT", "").lower()
    if env in ("development", "staging", "production"):
        return env
    
    # Infer from branch name if not explicitly set
    branch = get_current_branch()
    if branch.startswith("feature/") or branch == "develop":
        return "development"
    elif branch.startswith("staging/"):
        return "staging"
    elif branch in ("main", "master") or branch.startswith("release/"):
        return "production"
    
    return "development"


def get_federation_role() -> Optional[str]:
    """
    Get the BRH federation role (leader or witness)
    
    Returns:
        'leader', 'witness', or None if not in federation mode
    """
    role = os.getenv("BRH_FEDERATION_ROLE", "").lower()
    if role in ("leader", "witness"):
        return role
    return None


def merge_policies(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two policy dictionaries
    
    Args:
        base: Base policy configuration
        override: Override values to apply
        
    Returns:
        Merged policy dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_policies(result[key], value)
        else:
            result[key] = value
    
    return result


def apply_federation_modifiers(policy: Dict[str, Any], role: str, federation_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply federation role modifiers to policy
    
    Args:
        policy: Base policy configuration
        role: Federation role ('leader' or 'witness')
        federation_config: Federation configuration with modifiers
        
    Returns:
        Modified policy
    """
    if role not in federation_config:
        return policy
    
    modifiers = federation_config[role]
    result = policy.copy()
    
    # Apply modifiers
    for key, value in modifiers.items():
        if isinstance(value, str) and value.startswith(("+", "-")):
            # Relative modifier
            if key in result:
                try:
                    base_value = result[key]
                    modifier_value = float(value)
                    
                    if isinstance(base_value, (int, float)):
                        result[key] = base_value + modifier_value
                    elif isinstance(base_value, int):
                        result[key] = int(base_value + modifier_value)
                except (ValueError, TypeError):
                    pass  # Skip invalid modifiers
        else:
            # Absolute override
            result[key] = value
    
    return result


def load_local_policy() -> Dict[str, Any]:
    """
    Load policy from local YAML file
    
    Returns:
        Policy dictionary from local file
    """
    policy_path = "bridge_tools/bcse/policies.yaml"
    if os.path.exists(policy_path):
        try:
            import yaml
            with open(policy_path, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            print("⚠️  PyYAML not installed, cannot load local policy file")
        except Exception as e:
            print(f"⚠️  Failed to load local policy file: {e}")
    
    return {}


def fetch_policies() -> Dict[str, Any]:
    """
    Sovereign pull: prefer Forge, fallback to local file
    Supports branch-aware, environment-aware, and federation-aware policies
    
    Returns:
        Dictionary containing policy configuration from Forge or local file
    """
    branch = get_current_branch()
    environment = get_environment()
    federation_role = get_federation_role()
    
    print(f"🔍 Policy context: branch={branch}, env={environment}, role={federation_role or 'standalone'}")
    
    # Try to fetch from Forge first
    url = os.getenv("FORGE_POLICY_URL")
    if url:
        try:
            req = urllib.request.Request(
                url, 
                headers={"Authorization": f"Bearer {os.getenv('DOMINION_SEAL', '')}"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                raw_data = json.loads(r.read().decode("utf-8"))
                print("✅ Loaded policy from Forge Dominion")
                return raw_data
        except Exception as e:
            print(f"⚠️  Failed to fetch policies from Forge: {e}")
            print("   Falling back to local policy file...")
    
    # Fallback to local policy file
    raw_policy = load_local_policy()
    if not raw_policy:
        return {}
    
    # Extract defaults
    defaults = raw_policy.get("defaults", {})
    result = defaults.copy()
    
    # Apply environment overrides
    env_config = raw_policy.get("env", {})
    if environment in env_config:
        result = merge_policies(result, env_config[environment])
        print(f"📊 Applied environment override: {environment}")
    
    # Apply branch-specific overrides
    branches = raw_policy.get("branches", {})
    
    # Check for exact match first
    if branch in branches:
        result = merge_policies(result, branches[branch])
        print(f"🌿 Applied branch policy: {branch}")
    else:
        # Check for pattern matches (e.g., "feature/*")
        for pattern, branch_policy in branches.items():
            if pattern.endswith("/*"):
                prefix = pattern[:-2]
                if branch.startswith(prefix + "/"):
                    result = merge_policies(result, branch_policy)
                    print(f"🌿 Applied branch pattern: {pattern}")
                    break
    
    # Apply federation role modifiers
    if federation_role:
        federation_config = raw_policy.get("federation", {})
        if federation_config:
            result = apply_federation_modifiers(result, federation_role, federation_config)
            print(f"🔱 Applied federation role: {federation_role}")
    
    # Store raw policy for reference
    result["_raw"] = raw_policy
    result["_context"] = {
        "branch": branch,
        "environment": environment,
        "federation_role": federation_role
    }
    
    return result
