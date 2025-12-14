"""
GitHub adapter for Env Steward
"""

import os
import logging

logger = logging.getLogger(__name__)


class GithubAdapter:
    """Adapter for GitHub repository secrets and variables"""
    
    name = "github"
    
    def enabled(self) -> bool:
        """Check if GitHub adapter is enabled"""
        return os.getenv("STEWARD_GITHUB_ENABLED", "false").lower() == "true"
    
    async def apply(self, changes):
        """
        Apply environment variable changes to GitHub
        
        Args:
            changes: List of changes to apply
            
        Returns:
            Result dictionary
        """
        token = os.getenv("GITHUB_TOKEN", "")
        repo_slug = os.getenv("GITHUB_REPO_SLUG", "")
        
        if not token or not repo_slug:
            logger.warning("GitHub adapter: missing token or repo_slug")
            return {
                "ok": False,
                "reason": "GitHub write disabled or token/repo missing",
                "provider": self.name
            }
        
        # In production, this would call the GitHub API
        # For now, return success simulation
        logger.info(f"GitHub adapter: would apply {len(changes)} changes to repo {repo_slug}")
        
        return {
            "ok": True,
            "updated": len(changes),
            "provider": self.name
        }
