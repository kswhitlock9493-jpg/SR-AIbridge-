"""
SDTF (Sovereign Dominion Token Forge) Integration for Git

Provides Git with full token minting, validation, and lifecycle management
capabilities for ephemeral sovereign credentials.
"""

import os
import base64
import secrets
import hmac
import hashlib
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class SDTFGitIntegration:
    """
    SDTF integration providing Git with sovereign token capabilities.
    
    Git has authority to:
    - Mint ephemeral tokens with cosmic TTL
    - Validate sovereign signatures
    - Manage token lifecycle
    - Generate credentials for all providers (GitHub, Netlify, Render)
    """
    
    def __init__(self):
        """Initialize SDTF Git integration."""
        self.forge_root = os.getenv("FORGE_DOMINION_ROOT", "")
        self.mode = "sovereign"
        self.version = "1.9.7s-git-cosmic"
        
    def mint_ephemeral_token(
        self,
        provider: str,
        ttl_seconds: int = 3600,
        scope: str = "cosmic",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Mint an ephemeral token with Git's sovereign signature.
        
        Args:
            provider: Token provider (github, netlify, render, cosmic)
            ttl_seconds: Time-to-live in seconds (default: 3600, cosmic: unlimited)
            scope: Token scope (default: cosmic)
            **kwargs: Additional token metadata
            
        Returns:
            Token envelope with signature and metadata
        """
        # Generate token payload
        token_id = secrets.token_urlsafe(32)
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(seconds=ttl_seconds) if ttl_seconds > 0 else None
        
        # Create token payload
        payload = {
            "token_id": token_id,
            "provider": provider,
            "scope": scope,
            "issued_by": "git_sovereign_agent",
            "issued_at": issued_at.isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else "COSMIC_INFINITY",
            "ttl": ttl_seconds,
            "authority": "COSMIC_SOVEREIGNTY",
            **kwargs
        }
        
        # Sign token with Git's sovereign signature
        signature = self._sign_token(payload)
        
        # Create sealed envelope
        envelope = {
            "payload": payload,
            "signature": signature,
            "seal": "GIT_SOVEREIGN_SIGNATURE",
            "dominion_version": self.version,
        }
        
        return envelope
    
    def validate_token(self, envelope: Dict[str, Any]) -> bool:
        """
        Validate a token's sovereign signature.
        
        Args:
            envelope: Token envelope to validate
            
        Returns:
            True if signature is valid and token not expired
        """
        payload = envelope.get("payload", {})
        signature = envelope.get("signature", "")
        
        # Verify signature
        expected_signature = self._sign_token(payload)
        if not hmac.compare_digest(signature, expected_signature):
            return False
        
        # Check expiration (cosmic tokens never expire)
        expires_at = payload.get("expires_at")
        if expires_at and expires_at != "COSMIC_INFINITY":
            expiry = datetime.fromisoformat(expires_at)
            if datetime.utcnow() > expiry:
                return False
        
        return True
    
    def renew_token(self, envelope: Dict[str, Any], extend_seconds: int = 3600) -> Dict[str, Any]:
        """
        Renew an existing token with extended TTL.
        
        Args:
            envelope: Existing token envelope
            extend_seconds: Seconds to extend TTL
            
        Returns:
            New token envelope with extended expiration
        """
        if not self.validate_token(envelope):
            raise ValueError("Cannot renew invalid token")
        
        old_payload = envelope["payload"]
        
        # Create renewed token
        return self.mint_ephemeral_token(
            provider=old_payload["provider"],
            ttl_seconds=extend_seconds,
            scope=old_payload.get("scope", "cosmic"),
            renewed_from=old_payload["token_id"],
        )
    
    def _sign_token(self, payload: Dict[str, Any]) -> str:
        """
        Sign token payload with HMAC-SHA384.
        
        Args:
            payload: Token payload to sign
            
        Returns:
            Base64-encoded signature
        """
        # Use FORGE_DOMINION_ROOT as signing key, or generate ephemeral key
        signing_key = self.forge_root.encode() if self.forge_root else secrets.token_bytes(32)
        
        # Convert payload to canonical string
        canonical = self._canonicalize_payload(payload)
        
        # Generate HMAC-SHA384 signature
        signature = hmac.new(
            signing_key,
            canonical.encode(),
            hashlib.sha384
        ).digest()
        
        return base64.b64encode(signature).decode()
    
    def _canonicalize_payload(self, payload: Dict[str, Any]) -> str:
        """
        Create canonical string representation of payload.
        
        Args:
            payload: Payload to canonicalize
            
        Returns:
            Canonical string representation
        """
        # Sort keys for consistent signing
        sorted_items = sorted(payload.items())
        return "|".join(f"{k}:{v}" for k, v in sorted_items)
    
    def get_forge_status(self) -> Dict[str, Any]:
        """
        Get current SDTF integration status.
        
        Returns:
            Status information
        """
        return {
            "mode": self.mode,
            "version": self.version,
            "authority": "COSMIC_SOVEREIGNTY",
            "forge_root_configured": bool(self.forge_root),
            "capabilities": [
                "TOKEN_MINTING",
                "TOKEN_VALIDATION",
                "TOKEN_RENEWAL",
                "SOVEREIGN_SIGNING",
            ],
        }
    
    def mint_provider_credentials(self, providers: list = None) -> Dict[str, Dict[str, Any]]:
        """
        Mint credentials for all providers.
        
        Args:
            providers: List of providers (default: all)
            
        Returns:
            Dictionary of provider credentials
        """
        if providers is None:
            providers = ["github", "netlify", "render"]
        
        credentials = {}
        for provider in providers:
            credentials[provider] = self.mint_ephemeral_token(
                provider=provider,
                ttl_seconds=7200,  # 2 hours
                scope="full_access",
                auto_renew=True,
            )
        
        return credentials
