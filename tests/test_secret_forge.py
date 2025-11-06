"""
Test suite for Secret Forge - Sovereign Secret Management
Validates that forge-based secret retrieval works correctly
"""
import os
import time
import pytest
from bridge_backend.bridge_core.token_forge_dominion import (
    SecretForge,
    get_forge,
    reset_forge,
    retrieve_environment,
    generate_ephemeral_token,
    validate_ephemeral_token,
    get_token_metadata,
    MetadataValidationError,
    REQUIRED_METADATA_FIELDS,
    validate_metadata,
)


class TestSecretForge:
    """Test Secret Forge functionality."""
    
    def setup_method(self):
        """Reset forge before each test."""
        reset_forge()
    
    def test_retrieve_environment_basic(self, monkeypatch):
        """Test basic environment variable retrieval."""
        monkeypatch.setenv("TEST_VAR", "test_value")
        
        value = retrieve_environment("TEST_VAR")
        assert value == "test_value"
    
    def test_retrieve_environment_with_default(self):
        """Test retrieval with default value."""
        value = retrieve_environment("NONEXISTENT_VAR", "default_value")
        assert value == "default_value"
    
    def test_retrieve_forge_dominion_root(self, monkeypatch):
        """Test retrieval of FORGE_DOMINION_ROOT."""
        from bridge_backend.bridge_core.token_forge_dominion import retrieve_forge_dominion_root
        
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        # Reset forge to pick up new env var
        reset_forge()
        
        root = retrieve_forge_dominion_root()
        assert root == test_root
    
    def test_retrieve_forge_dominion_root_missing(self):
        """Test retrieval of FORGE_DOMINION_ROOT when not set."""
        from bridge_backend.bridge_core.token_forge_dominion import retrieve_forge_dominion_root
        
        # Ensure it's not set
        if "FORGE_DOMINION_ROOT" in os.environ:
            del os.environ["FORGE_DOMINION_ROOT"]
        
        # Reset forge
        reset_forge()
        
        with pytest.raises(RuntimeError, match="FORGE_DOMINION_ROOT not set"):
            retrieve_forge_dominion_root()
    
    def test_generate_ephemeral_token(self, monkeypatch):
        """Test ephemeral token generation."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        # Reset forge to pick up new env var
        reset_forge()
        
        token = generate_ephemeral_token("github", ttl=60)
        
        # Token should have expected format: service:timestamp:expiry:signature
        parts = token.split(":")
        assert len(parts) == 4
        assert parts[0] == "github"
        assert parts[1].isdigit()  # timestamp
        assert parts[2].isdigit()  # expiry
        assert len(parts[3]) == 32  # signature (32 hex chars)
    
    def test_generate_ephemeral_token_with_metadata(self, monkeypatch):
        """Test ephemeral token generation with metadata."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        # Reset forge
        reset_forge()
        
        # Note: metadata is currently not supported in validation
        # This test only verifies generation works
        metadata = {"user": "test", "scope": "read"}
        token = generate_ephemeral_token("api", ttl=300, metadata=metadata)
        
        assert token.startswith("api:")
        # Note: We don't validate this token as metadata is not yet supported in validation
    
    def test_validate_ephemeral_token_valid(self, monkeypatch):
        """Test validation of valid ephemeral token."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        # Reset forge
        reset_forge()
        
        # Generate a token
        token = generate_ephemeral_token("test_service", ttl=300)
        
        # Validate it
        is_valid = validate_ephemeral_token(token)
        assert is_valid is True
    
    def test_validate_ephemeral_token_invalid(self):
        """Test validation of invalid ephemeral token."""
        is_valid = validate_ephemeral_token("invalid_token_format")
        assert is_valid is False
    
    def test_forge_caching_disabled_in_tests(self, monkeypatch):
        """Test that caching is disabled in test environment."""
        # Set a variable
        monkeypatch.setenv("TEST_CACHE_VAR", "value1")
        
        value1 = retrieve_environment("TEST_CACHE_VAR")
        assert value1 == "value1"
        
        # Change the variable
        monkeypatch.setenv("TEST_CACHE_VAR", "value2")
        
        # Should get new value (no caching in tests)
        value2 = retrieve_environment("TEST_CACHE_VAR")
        assert value2 == "value2"
    
    def test_forge_singleton(self):
        """Test that forge returns singleton instance."""
        forge1 = get_forge()
        forge2 = get_forge()
        
        assert forge1 is forge2
    
    def test_forge_reset(self):
        """Test that reset_forge creates new instance."""
        forge1 = get_forge()
        reset_forge()
        forge2 = get_forge()
        
        assert forge1 is not forge2


class TestForgeIntegration:
    """Test forge integration with existing components."""
    
    def test_bootstrap_uses_forge(self, monkeypatch):
        """Test that bootstrap uses forge for retrieval."""
        from bridge_backend.bridge_core.token_forge_dominion.bootstrap import bootstrap_dominion_root
        
        test_key = "a" * 50  # Long enough to be valid
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_key)
        
        # Reset forge
        reset_forge()
        
        is_valid, message = bootstrap_dominion_root()
        assert is_valid
        assert "Valid root key" in message
    
    def test_quantum_authority_uses_forge(self, monkeypatch):
        """Test that QuantumAuthority uses forge."""
        from bridge_backend.bridge_core.token_forge_dominion import QuantumAuthority, generate_root_key
        
        # Generate a proper base64-encoded key
        test_key = generate_root_key()
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_key)
        monkeypatch.setenv("FORGE_DOMINION_MODE", "sovereign")
        
        # Reset forge
        reset_forge()
        
        qa = QuantumAuthority()
        assert qa.mode == "sovereign"


class TestMetadataValidation:
    """Test metadata validation functionality."""
    
    def setup_method(self):
        """Reset forge before each test."""
        reset_forge()
    
    def test_required_metadata_fields_constant(self):
        """Test that required metadata fields are defined."""
        assert len(REQUIRED_METADATA_FIELDS) == 6
        assert "creator_identity" in REQUIRED_METADATA_FIELDS
        assert "creation_timestamp" in REQUIRED_METADATA_FIELDS
        assert "intended_purpose" in REQUIRED_METADATA_FIELDS
        assert "expiration_policy" in REQUIRED_METADATA_FIELDS
        assert "access_scope" in REQUIRED_METADATA_FIELDS
        assert "audit_trail_id" in REQUIRED_METADATA_FIELDS
    
    def test_validate_metadata_with_all_fields(self):
        """Test metadata validation with all required fields."""
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        # Should not raise exception
        validate_metadata(metadata, require_metadata=True)
    
    def test_validate_metadata_missing_fields(self):
        """Test metadata validation with missing fields."""
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": int(time.time()),
            # Missing other required fields
        }
        
        with pytest.raises(MetadataValidationError, match="Missing required metadata fields"):
            validate_metadata(metadata, require_metadata=True)
    
    def test_validate_metadata_empty_fields(self):
        """Test metadata validation with empty fields."""
        metadata = {
            "creator_identity": "",  # Empty
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        with pytest.raises(MetadataValidationError, match="cannot be empty"):
            validate_metadata(metadata, require_metadata=True)
    
    def test_validate_metadata_invalid_creator_identity(self):
        """Test metadata validation with invalid creator identity."""
        metadata = {
            "creator_identity": 12345,  # Not a string
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        with pytest.raises(MetadataValidationError, match="creator_identity must be"):
            validate_metadata(metadata, require_metadata=True)
    
    def test_validate_metadata_invalid_timestamp(self):
        """Test metadata validation with invalid timestamp."""
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": "invalid",  # Invalid format
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        with pytest.raises(MetadataValidationError, match="Invalid creation_timestamp"):
            validate_metadata(metadata, require_metadata=True)
    
    def test_validate_metadata_none_when_required(self):
        """Test metadata validation when None but required."""
        with pytest.raises(MetadataValidationError, match="metadata is required"):
            validate_metadata(None, require_metadata=True)
    
    def test_validate_metadata_none_when_not_required(self):
        """Test metadata validation when None and not required."""
        # Should not raise exception
        validate_metadata(None, require_metadata=False)
    
    def test_generate_token_with_valid_metadata(self, monkeypatch):
        """Test token generation with valid metadata."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        reset_forge()
        
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        token = generate_ephemeral_token("test_service", ttl=300, metadata=metadata)
        
        # Token should have 5 parts (including metadata)
        parts = token.split(":")
        assert len(parts) == 5
        assert parts[0] == "test_service"
    
    def test_generate_token_with_metadata_enforcement(self, monkeypatch):
        """Test token generation with metadata enforcement enabled."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        monkeypatch.setenv("SOVEREIGN_GIT", "true")
        
        reset_forge()
        
        # Should raise error when metadata is missing
        with pytest.raises(MetadataValidationError, match="metadata is required"):
            generate_ephemeral_token("test_service", ttl=300, metadata=None)
    
    def test_generate_token_with_invalid_metadata_enforcement(self, monkeypatch):
        """Test token generation with invalid metadata when enforcement enabled."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        monkeypatch.setenv("SOVEREIGN_GIT", "true")
        
        reset_forge()
        
        # Invalid metadata (missing fields)
        metadata = {
            "creator_identity": "user@example.com",
        }
        
        with pytest.raises(MetadataValidationError, match="Missing required metadata fields"):
            generate_ephemeral_token("test_service", ttl=300, metadata=metadata)
    
    def test_validate_token_with_metadata(self, monkeypatch):
        """Test token validation with metadata."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        reset_forge()
        
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        token = generate_ephemeral_token("test_service", ttl=300, metadata=metadata)
        
        # Should validate successfully
        assert validate_ephemeral_token(token) is True
    
    def test_validate_token_without_metadata_when_required(self, monkeypatch):
        """Test token validation without metadata when required."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        reset_forge()
        
        # Generate token without metadata
        token = generate_ephemeral_token("test_service", ttl=300, metadata=None)
        
        # Should fail validation when metadata is required
        assert validate_ephemeral_token(token, require_metadata=True) is False
    
    def test_validate_token_with_sovereign_git_enabled(self, monkeypatch):
        """Test token validation with SOVEREIGN_GIT enabled."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        monkeypatch.setenv("SOVEREIGN_GIT", "true")
        
        reset_forge()
        
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        # Generate token with metadata
        token = generate_ephemeral_token("test_service", ttl=300, metadata=metadata)
        
        # Should validate successfully
        assert validate_ephemeral_token(token) is True
    
    def test_get_token_metadata(self, monkeypatch):
        """Test extracting metadata from token."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        reset_forge()
        
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": int(time.time()),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        token = generate_ephemeral_token("test_service", ttl=300, metadata=metadata)
        
        # Extract metadata
        extracted = get_token_metadata(token)
        assert extracted is not None
        assert extracted["creator_identity"] == "user@example.com"
        assert extracted["intended_purpose"] == "api_access"
        assert extracted["access_scope"] == "read_only"
        assert extracted["audit_trail_id"] == "audit_12345"
    
    def test_get_token_metadata_from_token_without_metadata(self, monkeypatch):
        """Test extracting metadata from token without metadata."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        reset_forge()
        
        token = generate_ephemeral_token("test_service", ttl=300, metadata=None)
        
        # Should return None
        extracted = get_token_metadata(token)
        assert extracted is None
    
    def test_backward_compatibility_without_enforcement(self, monkeypatch):
        """Test that tokens without metadata still work when enforcement is disabled."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        # Ensure SOVEREIGN_GIT is not set
        monkeypatch.delenv("SOVEREIGN_GIT", raising=False)
        
        reset_forge()
        
        # Generate token without metadata
        token = generate_ephemeral_token("test_service", ttl=300, metadata=None)
        
        # Should validate successfully
        assert validate_ephemeral_token(token) is True
    
    def test_forge_instance_with_enforcement_flag(self, monkeypatch):
        """Test creating forge instance with enforce_metadata flag."""
        test_root = "test_forge_root_key_12345678901234567890"
        monkeypatch.setenv("FORGE_DOMINION_ROOT", test_root)
        
        forge = SecretForge(enable_cache=False, enforce_metadata=True)
        
        # Should require metadata
        with pytest.raises(MetadataValidationError):
            forge.generate_ephemeral_token("test", ttl=300, metadata=None)
    
    def test_iso_timestamp_format(self):
        """Test metadata validation with ISO format timestamp."""
        from datetime import datetime, timezone
        
        metadata = {
            "creator_identity": "user@example.com",
            "creation_timestamp": datetime.now(timezone.utc).isoformat(),
            "intended_purpose": "api_access",
            "expiration_policy": "5_minutes",
            "access_scope": "read_only",
            "audit_trail_id": "audit_12345"
        }
        
        # Should not raise exception
        validate_metadata(metadata, require_metadata=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
