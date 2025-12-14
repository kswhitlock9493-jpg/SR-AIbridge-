"""
Quantum Authority - Token Forge Dominion v1.9.7s-SOVEREIGN

Military-grade cryptographic token minting with HKDF-SHA384 derivation.
Implements quantum-resistant token authority for zero-trust environment sovereignty.
"""
import os
import hmac
import hashlib
import secrets
import base64
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from .secret_forge import retrieve_environment


class QuantumAuthority:
    """
    Quantum-resistant token authority using HKDF-SHA384 key derivation.
    Issues ephemeral, auto-refreshing tokens with cryptographic signatures.
    """
    
    def __init__(self, root_key: Optional[str] = None):
        """
        Initialize Quantum Authority with root key.
        
        Args:
            root_key: Base64-encoded root key. If None, generates from environment.
        """
        self.root_key = self._get_or_generate_root_key(root_key)
        self.version = "1.9.7s"
        # Use forge to retrieve environment variable
        self.mode = retrieve_environment("FORGE_DOMINION_MODE", "sovereign")
        
    def _get_or_generate_root_key(self, root_key: Optional[str]) -> bytes:
        """
        Get root key from parameter, environment, or generate new one.
        
        Args:
            root_key: Optional root key string
            
        Returns:
            bytes: Raw root key material
        """
        if root_key:
            return base64.urlsafe_b64decode(root_key + "==")
        
        # Use forge to retrieve environment variable
        env_key = retrieve_environment("FORGE_DOMINION_ROOT")
        if env_key:
            return base64.urlsafe_b64decode(env_key + "==")
        
        # Generate new root key (32 bytes for 256-bit security)
        new_key = secrets.token_bytes(32)
        return new_key
    
    def derive_key(self, context: str, salt: Optional[bytes] = None) -> bytes:
        """
        Derive a context-specific key using HKDF-SHA384.
        
        Args:
            context: Context string for key derivation
            salt: Optional salt bytes, generated if not provided
            
        Returns:
            bytes: Derived key material (48 bytes)
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        hkdf = HKDF(
            algorithm=hashes.SHA384(),
            length=48,  # 384 bits
            salt=salt,
            info=context.encode('utf-8'),
            backend=default_backend()
        )
        
        return hkdf.derive(self.root_key)
    
    def mint_quantum_token(
        self,
        provider: str,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Mint a quantum-resistant ephemeral token for a specific provider.
        
        Args:
            provider: Provider name (e.g., 'render', 'netlify', 'github')
            ttl_seconds: Time-to-live in seconds (default: 300)
            metadata: Optional metadata to include in token
            
        Returns:
            dict: Token envelope with signature
        """
        if ttl_seconds is None:
            ttl_seconds = 300  # 5 minutes default
        
        # Generate token ID and nonce
        token_id = secrets.token_urlsafe(16)
        nonce = secrets.token_bytes(16)
        
        # Derive provider-specific key
        context = f"forge-dominion-{provider}-{self.version}"
        derived_key = self.derive_key(context, nonce)
        
        # Create token payload
        issued_at = datetime.utcnow()
        expires_at = issued_at + timedelta(seconds=ttl_seconds)
        
        payload = {
            "token_id": token_id,
            "provider": provider,
            "version": self.version,
            "mode": self.mode,
            "issued_at": issued_at.isoformat() + "Z",
            "expires_at": expires_at.isoformat() + "Z",
            "ttl_seconds": ttl_seconds,
            "metadata": metadata or {}
        }
        
        # Sign the payload with HMAC-SHA384
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            derived_key,
            payload_json.encode('utf-8'),
            hashlib.sha384
        ).hexdigest()
        
        # Create token envelope
        token_envelope = {
            "token": base64.urlsafe_b64encode(payload_json.encode('utf-8')).decode('utf-8'),
            "signature": signature,
            "nonce": base64.urlsafe_b64encode(nonce).decode('utf-8'),
            "algorithm": "HMAC-SHA384",
            "key_derivation": "HKDF-SHA384"
        }
        
        return token_envelope
    
    def verify_token(self, token_envelope: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify a quantum token signature and validity.
        
        Args:
            token_envelope: Token envelope with signature
            
        Returns:
            tuple: (is_valid, payload_dict or None)
        """
        try:
            # Extract components
            token_b64 = token_envelope.get("token")
            signature = token_envelope.get("signature")
            nonce_b64 = token_envelope.get("nonce")
            
            if not all([token_b64, signature, nonce_b64]):
                return False, None
            
            # Decode token payload
            payload_json = base64.urlsafe_b64decode(token_b64).decode('utf-8')
            payload = json.loads(payload_json)
            
            # Derive the same key
            provider = payload.get("provider")
            version = payload.get("version", self.version)
            nonce = base64.urlsafe_b64decode(nonce_b64)
            
            context = f"forge-dominion-{provider}-{version}"
            derived_key = self.derive_key(context, nonce)
            
            # Verify signature
            expected_signature = hmac.new(
                derived_key,
                payload_json.encode('utf-8'),
                hashlib.sha384
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                return False, None
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload["expires_at"].rstrip('Z'))
            if datetime.utcnow() > expires_at:
                return False, None
            
            return True, payload
            
        except Exception as e:
            return False, None
    
    def rotate_root_key(self) -> str:
        """
        Generate a new root key for key rotation.
        
        Returns:
            str: Base64-encoded new root key
        """
        new_key = secrets.token_bytes(32)
        self.root_key = new_key
        return base64.urlsafe_b64encode(new_key).decode('utf-8').rstrip('=')
    
    def get_key_fingerprint(self) -> str:
        """
        Get fingerprint of current root key for auditing.
        
        Returns:
            str: SHA384 fingerprint of root key
        """
        fingerprint = hashlib.sha384(self.root_key).hexdigest()
        return fingerprint[:16]  # First 16 chars for display


def generate_root_key() -> str:
    """
    Generate a new FORGE_DOMINION_ROOT key.
    
    Returns:
        str: Base64-encoded root key suitable for environment variable
    """
    root_key = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(root_key).decode('utf-8').rstrip('=')
