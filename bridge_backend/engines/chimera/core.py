"""
Chimera Engine Core
Autonomous deploy healing and preflight validation
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, List
import logging

from .preflight.netlify_config import (
    write_headers, write_redirects, write_netlify_toml, 
    RedirectRule, DEFAULT_SECURITY_HEADERS
)

logger = logging.getLogger(__name__)

DIST_GUESS = ["frontend/dist", "frontend/build", "apps/web/out", "dist", "build", "bridge-frontend/dist"]


class ChimeraEngine:
    """Chimera deployment healing engine"""
    
    def __init__(self, repo_root: Path = None):
        self.root = repo_root or Path.cwd()
        
    def detect_publish_dir(self) -> str:
        """Auto-detect publish directory"""
        for p in DIST_GUESS:
            if (self.root / p).exists():
                return p
        return "frontend/build"
    
    async def preflight(self) -> dict:
        """Run preflight validation and generate deploy artifacts"""
        try:
            # Import genesis_bus here to avoid circular imports
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.preflight.start", {})
        except Exception as e:
            logger.warning(f"Failed to publish chimera.preflight.start: {e}")
        
        publish = self.detect_publish_dir()
        headers = DEFAULT_SECURITY_HEADERS
        redirects = [
            RedirectRule(from_path="/api/*", to_path="/.netlify/functions/server", status=200),
            RedirectRule(from_path="/*", to_path="/index.html", status=200)
        ]
        
        # Generate files
        write_headers(self.root, headers)
        write_redirects(self.root, redirects)
        write_netlify_toml(self.root, publish)
        
        # Quick syntax smoke-checks
        assert (self.root / "_headers").stat().st_size > 0, "_headers file is empty"
        assert (self.root / "_redirects").stat().st_size > 0, "_redirects file is empty"
        assert (self.root / "netlify.toml").stat().st_size > 0, "netlify.toml file is empty"
        
        payload = {"publish": publish, "status": "ok"}
        
        try:
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.preflight.ok", payload)
        except Exception as e:
            logger.warning(f"Failed to publish chimera.preflight.ok: {e}")
        
        return payload
    
    async def heal_after_failure(self, reason: str) -> None:
        """Heal after deployment failure"""
        intent = {"reason": reason}
        
        try:
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.deploy.heal.intent", intent)
        except Exception as e:
            logger.warning(f"Failed to publish chimera.deploy.heal.intent: {e}")
        
        # Regenerate with safe defaults
        await self.preflight()
        
        try:
            from ...genesis.bus import genesis_bus
            await genesis_bus.publish("chimera.deploy.heal.applied", intent)
        except Exception as e:
            logger.warning(f"Failed to publish chimera.deploy.heal.applied: {e}")
