"""
Tests for Bridge Runtime Handler (BRH)
"""

import pytest
import os
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
import sys

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge_backend"))

from bridge_core.runtime_handler import (
    RuntimeManifest,
    ForgeRuntimeAuthority,
    SovereignRuntimeCore
)


@pytest.fixture
def sample_manifest_path(tmp_path):
    """Create a sample runtime manifest for testing"""
    manifest = {
        "version": "1.0",
        "runtime": {
            "name": "test-runtime",
            "type": "sovereign",
            "auth": {
                "provider": "forge_dominion",
                "token_mode": "ephemeral",
                "token_ttl": 3600,
                "auto_renew": True
            },
            "containers": [
                {
                    "name": "test-container",
                    "image": "python:3.12-slim",
                    "command": ["python", "-m", "http.server"],
                    "ports": ["8000:8000"],
                    "health_check": {
                        "path": "/health",
                        "interval": 30,
                        "timeout": 5,
                        "retries": 3
                    }
                }
            ],
            "federation": {
                "enabled": False
            }
        },
        "security": {
            "attestation": {
                "enabled": True,
                "seal_algorithm": "HMAC-SHA256"
            }
        }
    }
    
    manifest_file = tmp_path / "bridge.runtime.yaml"
    with open(manifest_file, 'w') as f:
        yaml.dump(manifest, f)
    
    return str(manifest_file)


@pytest.fixture
def forge_root_key():
    """Set up a test Forge Dominion root key"""
    import base64
    import secrets
    key = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode().rstrip('=')
    os.environ['FORGE_DOMINION_ROOT'] = key
    yield key
    # Cleanup
    if 'FORGE_DOMINION_ROOT' in os.environ:
        del os.environ['FORGE_DOMINION_ROOT']


class TestRuntimeManifest:
    """Test RuntimeManifest class"""
    
    def test_load_manifest(self, sample_manifest_path):
        """Test loading manifest from file"""
        manifest = RuntimeManifest(sample_manifest_path)
        config = manifest.load()
        
        assert config['version'] == '1.0'
        assert config['runtime']['name'] == 'test-runtime'
        assert config['runtime']['type'] == 'sovereign'
    
    def test_validate_manifest(self, sample_manifest_path):
        """Test manifest validation"""
        manifest = RuntimeManifest(sample_manifest_path)
        manifest.load()
        
        assert manifest.validate() is True
    
    def test_get_auth_config(self, sample_manifest_path):
        """Test getting auth configuration"""
        manifest = RuntimeManifest(sample_manifest_path)
        manifest.load()
        
        auth_config = manifest.get_auth_config()
        assert auth_config['provider'] == 'forge_dominion'
        assert auth_config['token_mode'] == 'ephemeral'
        assert auth_config['token_ttl'] == 3600
    
    def test_get_containers(self, sample_manifest_path):
        """Test getting container configurations"""
        manifest = RuntimeManifest(sample_manifest_path)
        manifest.load()
        
        containers = manifest.get_containers()
        assert len(containers) == 1
        assert containers[0]['name'] == 'test-container'
        assert containers[0]['image'] == 'python:3.12-slim'
    
    def test_missing_manifest(self, tmp_path):
        """Test error handling for missing manifest"""
        manifest = RuntimeManifest(str(tmp_path / "nonexistent.yaml"))
        
        with pytest.raises(FileNotFoundError):
            manifest.load()


class TestForgeRuntimeAuthority:
    """Test ForgeRuntimeAuthority class"""
    
    def test_generate_token(self, forge_root_key):
        """Test token generation"""
        auth = ForgeRuntimeAuthority()
        token = auth.generate_runtime_token(
            node_id="test-node-001",
            scope="runtime:test",
            ttl_seconds=3600
        )
        
        assert token['node_id'] == 'test-node-001'
        assert token['scope'] == 'runtime:test'
        assert 'signature' in token
        assert 'issued_at' in token
        assert 'expires_at' in token
    
    def test_validate_token(self, forge_root_key):
        """Test token validation"""
        auth = ForgeRuntimeAuthority()
        
        # Generate a valid token
        token = auth.generate_runtime_token("test-node", "runtime:test", 3600)
        
        # Validate it
        assert auth.validate_token(token) is True
    
    def test_validate_expired_token(self, forge_root_key):
        """Test validation of expired token"""
        auth = ForgeRuntimeAuthority()
        
        # Generate a token that's already expired
        token = auth.generate_runtime_token("test-node", "runtime:test", -1)
        
        # Should fail validation
        assert auth.validate_token(token) is False
    
    def test_validate_tampered_token(self, forge_root_key):
        """Test validation of tampered token"""
        auth = ForgeRuntimeAuthority()
        
        # Generate a valid token
        token = auth.generate_runtime_token("test-node", "runtime:test", 3600)
        
        # Tamper with the signature
        token['signature'] = 'invalid_signature'
        
        # Should fail validation
        assert auth.validate_token(token) is False
    
    def test_renew_token(self, forge_root_key):
        """Test token renewal"""
        auth = ForgeRuntimeAuthority()
        
        # Generate initial token
        old_token = auth.generate_runtime_token("test-node", "runtime:test", 3600)
        
        # Renew it
        new_token = auth.renew_token(old_token, 7200)
        
        # Verify new token
        assert new_token['node_id'] == old_token['node_id']
        assert new_token['scope'] == old_token['scope']
        assert new_token['signature'] != old_token['signature']  # Different signature
        assert auth.validate_token(new_token) is True
    
    def test_missing_root_key(self):
        """Test error handling when root key is missing"""
        # Ensure key is not set
        if 'FORGE_DOMINION_ROOT' in os.environ:
            del os.environ['FORGE_DOMINION_ROOT']
        
        with pytest.raises(ValueError, match="FORGE_DOMINION_ROOT"):
            ForgeRuntimeAuthority()


@pytest.mark.asyncio
class TestSovereignRuntimeCore:
    """Test SovereignRuntimeCore class"""
    
    async def test_initialize(self, sample_manifest_path, forge_root_key):
        """Test runtime initialization"""
        runtime = SovereignRuntimeCore(sample_manifest_path)
        
        await runtime.initialize()
        
        assert runtime.node_id is not None
        assert runtime.runtime_token is not None
        assert runtime.auth.validate_token(runtime.runtime_token) is True
    
    async def test_health_check(self, sample_manifest_path, forge_root_key):
        """Test health check"""
        runtime = SovereignRuntimeCore(sample_manifest_path)
        await runtime.initialize()
        
        health = await runtime.health_check()
        
        assert 'node_id' in health
        assert 'timestamp' in health
        assert 'token_valid' in health
        assert health['token_valid'] is True
    
    async def test_token_renewal(self, sample_manifest_path, forge_root_key):
        """Test automatic token renewal"""
        runtime = SovereignRuntimeCore(sample_manifest_path)
        await runtime.initialize()
        
        # Generate a new token that's near expiration (4 minutes remaining)
        # This should trigger auto-renewal
        from datetime import datetime, timedelta
        old_token = runtime.auth.generate_runtime_token(
            runtime.node_id,
            "runtime:execute",
            240  # 4 minutes - less than the 5 minute renewal threshold
        )
        runtime.runtime_token = old_token
        
        # Trigger renewal
        await runtime.renew_token_if_needed()
        
        # Token should be renewed
        assert runtime.runtime_token is not None
        assert runtime.auth.validate_token(runtime.runtime_token) is True
        # Should have different signature after renewal
        assert runtime.runtime_token['signature'] != old_token['signature']


def test_integration_workflow(sample_manifest_path, forge_root_key, tmp_path):
    """Integration test: Load manifest, generate token, validate"""
    # Load manifest
    manifest = RuntimeManifest(sample_manifest_path)
    config = manifest.load()
    assert manifest.validate()
    
    # Get auth config
    auth_config = manifest.get_auth_config()
    assert auth_config['provider'] == 'forge_dominion'
    
    # Generate token
    auth = ForgeRuntimeAuthority()
    token = auth.generate_runtime_token(
        "integration-test-node",
        "runtime:test",
        auth_config['token_ttl']
    )
    
    # Validate token
    assert auth.validate_token(token) is True
    
    # Save token
    token_file = tmp_path / "test_token.json"
    with open(token_file, 'w') as f:
        json.dump(token, f)
    
    # Load and validate saved token
    with open(token_file, 'r') as f:
        loaded_token = json.load(f)
    
    assert auth.validate_token(loaded_token) is True
    
    print("✓ Integration test passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
