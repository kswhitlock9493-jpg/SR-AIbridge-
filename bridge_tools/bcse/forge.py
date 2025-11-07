"""Forge Dominion Integration - Sovereign Policy Fetching"""
import os
import json
import urllib.request
from typing import Dict, Any


def dominion_root() -> str:
    """Get the Forge Dominion root endpoint"""
    root = os.getenv("FORGE_DOMINION_ROOT") or "dominion://local"
    return root


def fetch_policies() -> Dict[str, Any]:
    """
    Sovereign pull: prefer Forge, fallback to local file
    
    Returns:
        Dictionary containing policy configuration from Forge or local file
    """
    # Sovereign pull: prefer Forge, fallback to local file
    url = os.getenv("FORGE_POLICY_URL")
    if url:
        try:
            req = urllib.request.Request(
                url, 
                headers={"Authorization": f"Bearer {os.getenv('DOMINION_SEAL', '')}"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            print(f"⚠️  Failed to fetch policies from Forge: {e}")
            print("   Falling back to local policy file...")
    
    # fallback to repo policy file if present
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
