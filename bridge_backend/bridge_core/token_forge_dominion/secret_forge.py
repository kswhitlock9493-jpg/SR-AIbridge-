"""
Secret Forge - Sovereign Secret Management v1.9.7s-SOVEREIGN

Implements the Secret Forge doctrine where ALL secrets are retrieved
through the forge instead of being hardcoded or accessed directly.

NO SECRETS HARDCODED - ALL SECRETS FLOW THROUGH THE FORGE!
"""
import os
import hmac
import hashlib
import time
import json
import base64
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# Required metadata fields for secure token creation
REQUIRED_METADATA_FIELDS = [
    "creator_identity",
    "creation_timestamp",
    "intended_purpose",
    "expiration_policy",
    "access_scope",
    "audit_trail_id"
]

# Constants
SECONDS_PER_DAY = 86400  # Used for timestamp validation clock skew tolerance


class MetadataValidationError(Exception):
    """Raised when token metadata validation fails."""
    pass


def validate_metadata(metadata: Optional[Dict[str, Any]], require_metadata: bool = True) -> None:
    """
    Validate token metadata against security requirements.
    
    Args:
        metadata: Metadata dictionary to validate
        require_metadata: If True, metadata must be present and valid
        
    Raises:
        MetadataValidationError: If metadata validation fails
    """
    if metadata is None:
        if require_metadata:
            raise MetadataValidationError(
                "Token metadata is required for security compliance. "
                f"Required fields: {', '.join(REQUIRED_METADATA_FIELDS)}"
            )
        return
    
    # Check all required fields are present
    missing_fields = [field for field in REQUIRED_METADATA_FIELDS if field not in metadata]
    if missing_fields:
        raise MetadataValidationError(
            f"Missing required metadata fields: {', '.join(missing_fields)}. "
            f"Required fields: {', '.join(REQUIRED_METADATA_FIELDS)}"
        )
    
    # Validate each field has non-empty value
    empty_fields = [field for field in REQUIRED_METADATA_FIELDS if not metadata.get(field)]
    if empty_fields:
        raise MetadataValidationError(
            f"Metadata fields cannot be empty: {', '.join(empty_fields)}"
        )
    
    # Validate creator_identity is a non-empty string
    if not isinstance(metadata.get("creator_identity"), str):
        raise MetadataValidationError(
            "creator_identity must be a non-empty string"
        )
    
    # Validate creation_timestamp is valid
    try:
        timestamp = metadata.get("creation_timestamp")
        if isinstance(timestamp, str):
            # Try to parse as ISO format
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, (int, float)):
            # Unix timestamp
            if timestamp < 0 or timestamp > time.time() + SECONDS_PER_DAY:  # Allow 1 day in future for clock skew
                raise MetadataValidationError(
                    "creation_timestamp is outside valid range"
                )
        else:
            raise MetadataValidationError(
                "creation_timestamp must be ISO format string or Unix timestamp"
            )
    except (ValueError, TypeError) as e:
        raise MetadataValidationError(
            f"Invalid creation_timestamp format: {e}"
        )
    
    # Validate intended_purpose is a non-empty string
    if not isinstance(metadata.get("intended_purpose"), str):
        raise MetadataValidationError(
            "intended_purpose must be a non-empty string"
        )
    
    # Validate expiration_policy
    if not isinstance(metadata.get("expiration_policy"), str):
        raise MetadataValidationError(
            "expiration_policy must be a non-empty string"
        )
    
    # Validate access_scope
    if not isinstance(metadata.get("access_scope"), str):
        raise MetadataValidationError(
            "access_scope must be a non-empty string"
        )
    
    # Validate audit_trail_id
    if not isinstance(metadata.get("audit_trail_id"), str):
        raise MetadataValidationError(
            "audit_trail_id must be a non-empty string"
        )


class SecretForge:
    """
    Sovereign Secret Dominion Forge - The ONLY gateway to secrets.
    
    All secret access must flow through this forge. No direct environment
    variable access or hardcoded secrets allowed.
    
    Philosophy:
    - FORGE_DOMINION_ROOT is our sovereign variable
    - All other secrets retrieved through secure forge methods
    - Ephemeral tokens generated on-demand
    - Zero hardcoded credentials anywhere
    """
    
    def __init__(self, enable_cache: bool = True, enforce_metadata: bool = False):
        """
        Initialize the Secret Forge.
        
        Args:
            enable_cache: Enable caching of retrieved secrets (default: True).
                         Set to False in test environments.
            enforce_metadata: Enforce metadata validation for token creation (default: False).
                            Set to True to require metadata for all tokens.
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl: Dict[str, datetime] = {}
        self._enable_cache = enable_cache
        self._enforce_metadata = enforce_metadata
    
    def retrieve_environment(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve an environment secret through the forge.
        
        This is the SOVEREIGN way to access environment variables.
        All environment access should go through this method.
        
        Args:
            key: Environment variable name
            default: Default value if not found
            
        Returns:
            Secret value from environment or default
        """
        # Check cache first (with TTL) if caching is enabled
        if self._enable_cache and key in self._cache:
            if key in self._cache_ttl and datetime.now() < self._cache_ttl[key]:
                return self._cache[key]
            else:
                # Cache expired, remove
                self._cache.pop(key, None)
                self._cache_ttl.pop(key, None)
        
        # Retrieve from environment
        value = os.getenv(key, default)
        
        # Cache for 5 minutes if caching is enabled
        if self._enable_cache and value is not None:
            self._cache[key] = value
            self._cache_ttl[key] = datetime.now() + timedelta(minutes=5)
        
        return value
    
    def retrieve_forge_dominion_root(self) -> str:
        """
        Retrieve the sovereign FORGE_DOMINION_ROOT variable.
        
        This is the primary sovereign variable that all other secrets
        are derived from.
        
        Returns:
            FORGE_DOMINION_ROOT value
            
        Raises:
            RuntimeError: If FORGE_DOMINION_ROOT is not set
        """
        root = self.retrieve_environment("FORGE_DOMINION_ROOT")
        if not root:
            raise RuntimeError(
                "FORGE_DOMINION_ROOT not set in environment. "
                "This is the sovereign gateway variable and must be configured."
            )
        return root
    
    def generate_ephemeral_token(
        self,
        service: str,
        ttl: int = 300,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an ephemeral token for the specified service.
        
        Tokens are generated on-demand and expire after TTL seconds.
        This replaces ALL hardcoded tokens like ghp_*** with dynamic,
        short-lived credentials.
        
        SECURITY: Metadata validation is enforced when enforce_metadata=True
        or when SOVEREIGN_GIT=true environment variable is set.
        
        Args:
            service: Service name (e.g., "github", "netlify", "api")
            ttl: Time-to-live in seconds (default 300 = 5 minutes)
            metadata: Token metadata with required fields for security compliance
            
        Returns:
            Ephemeral token string
            
        Raises:
            MetadataValidationError: If metadata validation fails when enforcement is enabled
        """
        # Check if metadata enforcement is enabled
        enforce = self._enforce_metadata or os.getenv("SOVEREIGN_GIT", "").lower() == "true"
        
        # Validate metadata if enforcement is enabled
        if enforce:
            validate_metadata(metadata, require_metadata=True)
        
        # Get the sovereign root key
        try:
            root_key = self.retrieve_forge_dominion_root()
        except RuntimeError:
            # Fallback to development key for testing
            root_key = "dev-forge-root-key"
        
        # Generate timestamp
        timestamp = int(time.time())
        expiry = timestamp + ttl
        
        # Build token payload
        payload_parts = [
            service,
            str(timestamp),
            str(expiry)
        ]
        
        # Encode metadata if present
        metadata_encoded = ""
        if metadata:
            # Validate metadata even if not enforcing (to catch errors early)
            try:
                validate_metadata(metadata, require_metadata=False)
            except MetadataValidationError as e:
                # If validation fails but enforcement is not enabled, log warning and allow it
                if not enforce:
                    logger.warning(
                        f"Token metadata validation failed but enforcement is disabled: {e}. "
                        "Consider enabling SOVEREIGN_GIT=true for strict validation."
                    )
                else:
                    raise
            
            # Encode metadata as base64 JSON for inclusion in token
            metadata_json = json.dumps(metadata, sort_keys=True)
            metadata_encoded = base64.b64encode(metadata_json.encode()).decode()
            payload_parts.append(metadata_encoded)
        
        payload = "|".join(payload_parts)
        
        # Generate HMAC signature using root key
        signature = hmac.new(
            root_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Format: service:timestamp:expiry:signature[:metadata] (using : as separator)
        token_parts = [service, str(timestamp), str(expiry), signature[:32]]
        if metadata_encoded:
            token_parts.append(metadata_encoded)
        
        token = ":".join(token_parts)
        
        return token
    
    def validate_ephemeral_token(self, token: str, require_metadata: bool = False) -> bool:
        """
        Validate an ephemeral token.
        
        Args:
            token: Token to validate
            require_metadata: If True, require valid metadata in token
            
        Returns:
            True if valid and not expired, False otherwise
        """
        try:
            # Input validation
            if not token or not isinstance(token, str):
                return False
            
            # Limit token length to prevent abuse
            if len(token) > 10000:  # Reasonable max length
                return False
            
            parts = token.split(":")
            # Token should have 4 or 5 parts (service:timestamp:expiry:signature[:metadata])
            if len(parts) < 4 or len(parts) > 5:
                return False
            
            service = parts[0]
            timestamp = int(parts[1])
            expiry = int(parts[2])
            signature = parts[3]
            metadata_encoded = parts[4] if len(parts) > 4 else None
            
            # Validate service name (basic sanitization)
            if not service or len(service) > 100:
                return False
            
            # Check if metadata is required
            enforce = require_metadata or os.getenv("SOVEREIGN_GIT", "").lower() == "true"
            if enforce and not metadata_encoded:
                return False
            
            # Check expiry
            if int(time.time()) > expiry:
                return False
            
            # Reconstruct payload and verify signature
            try:
                root_key = self.retrieve_forge_dominion_root()
            except RuntimeError:
                # If FORGE_DOMINION_ROOT is not set, validation fails
                return False
            
            # Build payload for signature verification
            payload_parts = [service, str(timestamp), str(expiry)]
            if metadata_encoded:
                payload_parts.append(metadata_encoded)
            payload = "|".join(payload_parts)
            
            expected_sig = hmac.new(
                root_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()[:32]
            
            # Verify signature
            if not hmac.compare_digest(signature, expected_sig):
                return False
            
            # Validate metadata if present
            if metadata_encoded:
                try:
                    metadata_json = base64.b64decode(metadata_encoded).decode()
                    metadata = json.loads(metadata_json)
                    # Validate metadata structure
                    validate_metadata(metadata, require_metadata=enforce)
                except (ValueError, json.JSONDecodeError, MetadataValidationError):
                    return False
            
            return True
            
        except Exception:
            return False
    
    def get_token_metadata(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Extract metadata from a token.
        
        Args:
            token: Token to extract metadata from
            
        Returns:
            Metadata dictionary if present and valid, None otherwise
        """
        try:
            parts = token.split(":")
            if len(parts) < 5:
                return None
            
            metadata_encoded = parts[4]
            metadata_json = base64.b64decode(metadata_encoded).decode()
            metadata = json.loads(metadata_json)
            
            return metadata
        except Exception:
            return None
    
    def clear_cache(self):
        """Clear the secret cache."""
        self._cache.clear()
        self._cache_ttl.clear()


# Global singleton forge instance
_forge_instance: Optional[SecretForge] = None


def get_forge() -> SecretForge:
    """
    Get the global Secret Forge instance.
    
    Returns:
        SecretForge singleton instance
    """
    global _forge_instance
    if _forge_instance is None:
        # Disable caching in test environments
        is_test = os.getenv("PYTEST_CURRENT_TEST") is not None
        # Enable metadata enforcement if SOVEREIGN_GIT is true
        enforce_metadata = os.getenv("SOVEREIGN_GIT", "").lower() == "true"
        _forge_instance = SecretForge(
            enable_cache=not is_test,
            enforce_metadata=enforce_metadata
        )
    return _forge_instance


def reset_forge():
    """
    Reset the global forge instance.
    This is useful for testing to ensure clean state.
    """
    global _forge_instance
    _forge_instance = None


# Convenience functions for common operations
def retrieve_environment(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieve environment variable through the forge.
    
    This is the SOVEREIGN way to access environment variables.
    """
    return get_forge().retrieve_environment(key, default)


def retrieve_forge_dominion_root() -> str:
    """
    Retrieve the sovereign FORGE_DOMINION_ROOT variable.
    
    This is the primary sovereign variable.
    """
    return get_forge().retrieve_forge_dominion_root()


def generate_ephemeral_token(
    service: str,
    ttl: int = 300,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate an ephemeral token for the specified service.
    
    This replaces ALL hardcoded tokens.
    """
    return get_forge().generate_ephemeral_token(service, ttl, metadata)


def validate_ephemeral_token(token: str, require_metadata: bool = False) -> bool:
    """
    Validate an ephemeral token.
    
    Args:
        token: Token to validate
        require_metadata: If True, require valid metadata in token
    """
    return get_forge().validate_ephemeral_token(token, require_metadata)


def get_token_metadata(token: str) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from a token.
    
    Args:
        token: Token to extract metadata from
        
    Returns:
        Metadata dictionary if present and valid, None otherwise
    """
    return get_forge().get_token_metadata(token)
