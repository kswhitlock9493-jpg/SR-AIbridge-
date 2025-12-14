"""
GitHub Forge Core
Local repository configuration forge without external webhooks
"""

from pathlib import Path
import json
import os


FORGE_DIR = Path(".github/bridge")


class GitHubForge:
    """
    Local GitHub repository configuration forge
    Reads and writes bridge configuration files without external API calls
    """
    
    def __init__(self):
        FORGE_DIR.mkdir(parents=True, exist_ok=True)
    
    def put_json(self, name: str, data: dict) -> str:
        """
        Write JSON data to forge directory
        
        Args:
            name: File name (without extension)
            data: JSON-serializable data
            
        Returns:
            Path to written file
        """
        p = FORGE_DIR / f"{name}.json"
        p.write_text(json.dumps(data, indent=2))
        return str(p)
    
    def get_json(self, name: str) -> dict:
        """
        Read JSON data from forge directory
        
        Args:
            name: File name (without extension)
            
        Returns:
            Parsed JSON data or empty dict if not found
        """
        p = FORGE_DIR / f"{name}.json"
        return json.loads(p.read_text()) if p.exists() else {}
    
    def put_env(self, name: str, kv: dict) -> str:
        """
        Write environment variables to forge directory
        
        Args:
            name: File name (without extension)
            kv: Key-value pairs
            
        Returns:
            Path to written file
        """
        p = FORGE_DIR / f"{name}.env"
        lines = [f'{k}="{v}"' for k, v in kv.items()]
        p.write_text("\n".join(lines) + "\n")
        return str(p)
