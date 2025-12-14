"""GitHub Forge Adapter for Chimera Oracle"""

from typing import Dict, Any
from ...github_forge.core import GitHubForge as GitHubForgeCore


class GitHubForge:
    """GitHub Forge adapter for Chimera"""
    
    def __init__(self):
        self.forge = GitHubForgeCore()
    
    def put_json(self, name: str, data: dict) -> str:
        """Write JSON to forge"""
        return self.forge.put_json(name, data)
    
    def get_json(self, name: str) -> dict:
        """Read JSON from forge"""
        return self.forge.get_json(name)
    
    def put_env(self, name: str, kv: dict) -> str:
        """Write env file to forge"""
        return self.forge.put_env(name, kv)
