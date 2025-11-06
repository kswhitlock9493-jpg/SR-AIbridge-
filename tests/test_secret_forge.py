"""
Test suite for Secret Forge - Sovereign Secret Management
Validates that forge-based secret retrieval works correctly
"""
import os
import pytest
from bridge_backend.bridge_core.token_forge_dominion import (
    SecretForge,
    get_forge,
    reset_forge,
    retrieve_environment,
    generate_ephemeral_token,
    validate_ephemeral_token
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
        
        metadata = {"user": "test", "scope": "read"}
        token = generate_ephemeral_token("api", ttl=300, metadata=metadata)
        
        assert token.startswith("api:")
    
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
