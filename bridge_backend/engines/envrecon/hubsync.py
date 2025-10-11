"""
HubSync Layer - GitHub Secrets Integration
Detects GitHub secret drift and auto-creates or syncs missing secrets
"""

import os
import logging
import base64
from typing import List, Dict, Any, Optional
import httpx
from nacl import encoding, public

logger = logging.getLogger(__name__)


class HubSync:
    """GitHub Secrets synchronization layer"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO")
        self.dry_run = os.getenv("HUBSYNC_DRYRUN", "false").lower() == "true"
    
    def is_configured(self) -> bool:
        """Check if HubSync is properly configured"""
        return bool(self.github_token and self.github_repo)
    
    async def get_public_key(self) -> Optional[Dict[str, str]]:
        """Get repository public key for encrypting secrets"""
        if not self.is_configured():
            return None
        
        url = f"https://api.github.com/repos/{self.github_repo}/actions/secrets/public-key"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception as e:
            logger.error(f"❌ Failed to get GitHub public key: {e}")
            return None
    
    def encrypt_secret(self, public_key: str, secret_value: str) -> str:
        """Encrypt a secret using the repository's public key"""
        public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
        sealed_box = public.SealedBox(public_key_obj)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")
    
    async def create_or_update_secret(self, secret_name: str, secret_value: str) -> bool:
        """
        Create or update a GitHub secret.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to set
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_configured():
            logger.warning("⚠️ HubSync not configured")
            return False
        
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would create/update secret: {secret_name}")
            return True
        
        # Get public key
        key_data = await self.get_public_key()
        if not key_data:
            return False
        
        # Encrypt the secret
        encrypted_value = self.encrypt_secret(key_data["key"], secret_value)
        
        # Create or update the secret
        url = f"https://api.github.com/repos/{self.github_repo}/actions/secrets/{secret_name}"
        headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Accept": "application/vnd.github+json"
        }
        
        payload = {
            "encrypted_value": encrypted_value,
            "key_id": key_data["key_id"]
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.put(url, headers=headers, json=payload)
                resp.raise_for_status()
                logger.info(f"✅ Created/updated GitHub secret: {secret_name}")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to create/update secret {secret_name}: {e}")
            return False
    
    async def autofix_github_secrets(self, secrets: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Auto-fix missing GitHub secrets.
        
        Args:
            secrets: List of dicts with 'name' and 'value' keys
            
        Returns:
            Summary of operations
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "HubSync not configured (missing GITHUB_TOKEN or GITHUB_REPO)"
            }
        
        results = {
            "dry_run": self.dry_run,
            "created": [],
            "failed": [],
            "skipped": []
        }
        
        for secret in secrets:
            name = secret.get("name")
            value = secret.get("value")
            
            if not name or not value:
                results["skipped"].append(name or "unnamed")
                continue
            
            success = await self.create_or_update_secret(name, value)
            if success:
                results["created"].append(name)
            else:
                results["failed"].append(name)
        
        logger.info(f"🤝 HubSync complete - {len(results['created'])} secrets synced")
        
        return results


# Singleton instance
hubsync = HubSync()
