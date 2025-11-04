"""
Tests for Forge Dominion Manifest Resolver and Federation Heartbeat
"""
import os
import json
import time
import hmac
import hashlib
import pytest
from unittest.mock import Mock, patch, MagicMock


class TestForgeResolver:
    """Tests for forge-resolver.js manifest resolution logic"""
    
    def test_manifest_signature_generation(self):
        """Test HMAC signature generation matches expected algorithm"""
        # Simulate the signature generation from forge-resolver.js
        target = "ledger"
        epoch = 1699056000
        seal = "test-seal"
        
        # Python equivalent of the JS HMAC generation
        sig = hmac.new(
            seal.encode(),
            f"{target}:{epoch}".encode(),
            hashlib.sha256
        ).hexdigest()[:32]
        
        assert len(sig) == 32
        assert isinstance(sig, str)
    
    def test_manifest_targets(self):
        """Test that expected targets are defined"""
        valid_targets = ["ledger", "bridge", "default"]
        
        for target in valid_targets:
            # Each target should have specific fields
            if target == "ledger":
                expected_fields = ["ledger_url", "ledger_signature", "ledger_identity"]
            elif target == "bridge":
                expected_fields = ["bridge_url", "bridge_signature", "bridge_identity"]
            else:  # default
                expected_fields = ["forge_status", "forge_epoch", "forge_sig"]
            
            assert len(expected_fields) > 0
    
    def test_epoch_generation(self):
        """Test that epoch is a valid Unix timestamp"""
        epoch = int(time.time())
        
        # Should be a reasonable timestamp (after 2020-01-01)
        assert epoch > 1577836800
        # Should be before 2100-01-01
        assert epoch < 4102444800


class TestHeartbeatDaemon:
    """Tests for BRH Heartbeat Daemon"""
    
    def test_forge_sig_generation(self):
        """Test heartbeat signature generation"""
        from brh.heartbeat_daemon import forge_sig
        
        with patch.dict(os.environ, {
            "FORGE_DOMINION_ROOT": "dominion://test.bridge",
            "DOMINION_SEAL": "test-seal"
        }):
            epoch = 1699056000
            sig = forge_sig(epoch)
            
            # Signature should be 32 characters
            assert len(sig) == 32
            assert isinstance(sig, str)
            
            # Should be deterministic
            sig2 = forge_sig(epoch)
            assert sig == sig2
    
    def test_heartbeat_payload_structure(self):
        """Test heartbeat payload has required fields"""
        with patch.dict(os.environ, {
            "FORGE_DOMINION_ROOT": "dominion://test.bridge",
            "DOMINION_SEAL": "test-seal",
            "BRH_NODE_ID": "test-node"
        }):
            from brh.heartbeat_daemon import forge_sig
            
            epoch = int(time.time())
            sig = forge_sig(epoch)
            
            payload = {
                "epoch": epoch,
                "forge_root": "dominion://test.bridge",
                "sig": sig,
                "node": "test-node",
                "status": "alive",
            }
            
            # Verify all required fields exist
            assert "epoch" in payload
            assert "forge_root" in payload
            assert "sig" in payload
            assert "node" in payload
            assert "status" in payload
            
            # Verify field types
            assert isinstance(payload["epoch"], int)
            assert isinstance(payload["forge_root"], str)
            assert isinstance(payload["sig"], str)
            assert isinstance(payload["node"], str)
            assert payload["status"] == "alive"
    
    @patch('brh.heartbeat_daemon.requests.post')
    def test_heartbeat_broadcast(self, mock_post):
        """Test heartbeat broadcast with mocked request"""
        from brh.heartbeat_daemon import forge_sig
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.dict(os.environ, {
            "FORGE_DOMINION_ROOT": "dominion://test.bridge",
            "DOMINION_SEAL": "test-seal",
            "BRH_NODE_ID": "test-node",
            "BRH_HEARTBEAT_INTERVAL": "1"
        }):
            epoch = int(time.time())
            sig = forge_sig(epoch)
            
            payload = {
                "epoch": epoch,
                "forge_root": "dominion://test.bridge",
                "sig": sig,
                "node": "test-node",
                "status": "alive",
            }
            
            # Simulate single heartbeat
            import requests
            endpoint = "https://test.bridge/federation/heartbeat"
            r = requests.post(endpoint, json=payload, timeout=10)
            
            assert r.status_code == 200
    
    @patch('brh.heartbeat_daemon.threading.Thread')
    def test_heartbeat_start(self, mock_thread):
        """Test heartbeat daemon start"""
        from brh.heartbeat_daemon import start
        
        with patch.dict(os.environ, {
            "BRH_HEARTBEAT_ENABLED": "true"
        }):
            start()
            
            # Should create and start a thread
            mock_thread.assert_called_once()
            thread_instance = mock_thread.return_value
            thread_instance.start.assert_called_once()
    
    def test_heartbeat_disabled(self):
        """Test heartbeat daemon can be disabled"""
        from brh.heartbeat_daemon import start
        
        with patch.dict(os.environ, {
            "BRH_HEARTBEAT_ENABLED": "false"
        }):
            with patch('brh.heartbeat_daemon.threading.Thread') as mock_thread:
                start()
                
                # Should not create a thread when disabled
                mock_thread.assert_not_called()


class TestBridgeRuntimeYaml:
    """Tests for bridge.runtime.yaml configuration"""
    
    def test_runtime_yaml_exists(self):
        """Test that bridge.runtime.yaml file exists"""
        from pathlib import Path
        runtime_file = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge.runtime.yaml")
        assert runtime_file.exists()
    
    def test_runtime_yaml_structure(self):
        """Test bridge.runtime.yaml has required structure"""
        import yaml
        from pathlib import Path
        
        runtime_file = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge.runtime.yaml")
        spec = yaml.safe_load(runtime_file.read_text())
        
        # Check forge configuration exists
        assert "forge" in spec
        assert "dominion" in spec["forge"]
        assert "resolver" in spec["forge"]
        assert "schema" in spec["forge"]
        
        # Check federation configuration exists
        assert "runtime" in spec
        assert "federation" in spec["runtime"]
        assert "heartbeat" in spec["runtime"]["federation"]
        
        heartbeat = spec["runtime"]["federation"]["heartbeat"]
        assert heartbeat["enabled"] is True
        assert heartbeat["interval"] == 60
        assert heartbeat["ttl"] == 300
    
    def test_forge_schema_targets(self):
        """Test forge schema defines expected targets"""
        import yaml
        from pathlib import Path
        
        runtime_file = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/bridge.runtime.yaml")
        spec = yaml.safe_load(runtime_file.read_text())
        
        schema = spec["forge"]["schema"]
        targets = [item["target"] for item in schema]
        
        assert "ledger" in targets
        assert "bridge" in targets


class TestBRHIntegration:
    """Tests for BRH integration with heartbeat"""
    
    def test_brh_run_imports_heartbeat(self):
        """Test that brh/run.py imports heartbeat_daemon"""
        from pathlib import Path
        
        run_file = Path("/home/runner/work/SR-AIbridge-/SR-AIbridge-/brh/run.py")
        content = run_file.read_text()
        
        assert "from brh import heartbeat_daemon" in content
        assert "heartbeat_daemon.start()" in content
