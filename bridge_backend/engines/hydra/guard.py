"""
Hydra Guard v2
Netlify configuration synthesis and validation engine
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, Any


NETLIFY_TOML = Path("netlify.toml")
HEADERS_FILE = Path("public/_headers")
REDIRECTS_FILE = Path("public/_redirects")


class HydraGuard:
    """
    Hydra Netlify Guard v2
    Synthesizes and validates Netlify configuration files
    """
    
    def _desired_headers(self) -> str:
        """
        Generate desired security and CORS headers
        
        Returns:
            Headers configuration string
        """
        # Synthesized security & CORS headers (idempotent)
        return """/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: same-origin
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  Access-Control-Allow-Origin: *
"""
    
    def _desired_redirects(self) -> str:
        """
        Generate desired redirect rules
        
        Returns:
            Redirects configuration string
        """
        return """/api/*   https://sr-aibridge.onrender.com/:splat   200
/health    /index.html   200
"""
    
    def _merge_text(self, path: Path, wanted: str) -> Dict[str, Any]:
        """
        Merge desired text into existing file (idempotent)
        
        Args:
            path: File path to update
            wanted: Desired content to ensure is present
            
        Returns:
            Result dict with ok, changed, and path
        """
        existing = path.read_text() if path.exists() else ""
        if wanted.strip() in existing:
            return {"ok": True, "changed": False, "path": str(path)}
        
        path.parent.mkdir(parents=True, exist_ok=True)
        merged = (existing.rstrip() + "\n\n" + wanted.strip() + "\n").strip() if existing else wanted.strip() + "\n"
        path.write_text(merged)
        return {"ok": True, "changed": True, "path": str(path)}
    
    async def synthesize_and_validate(self) -> Dict[str, Any]:
        """
        Synthesize and validate all Netlify configuration files
        
        Returns:
            Result dict with synthesis results for headers, redirects, and toml
        """
        h = self._merge_text(HEADERS_FILE, self._desired_headers())
        r = self._merge_text(REDIRECTS_FILE, self._desired_redirects())
        
        # Minimal toml idempotence
        if not NETLIFY_TOML.exists():
            NETLIFY_TOML.write_text('[build]\ncommand = "npm run build"\npublish = "dist"\n')
            t = {"ok": True, "changed": True, "path": str(NETLIFY_TOML)}
        else:
            t = {"ok": True, "changed": False, "path": str(NETLIFY_TOML)}
        
        return {"ok": True, "headers": h, "redirects": r, "toml": t}
    
    async def deploy(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute deployment (CI triggers actual Netlify build)
        
        Args:
            plan: Deployment plan from Chimera
            
        Returns:
            Deployment result
        """
        # CI triggers actual Netlify build; here we surface plan for logs.
        return {"ok": True, "provider": "netlify", "plan": plan}
