"""
Tests for SR-AIbridge Protocol Vaulting System
"""

import os
import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from bridge_backend.bridge_core.protocols.vaulting import seal, get_vault_dir


class TestVaulting:
    """Test the protocol vaulting functionality"""
    
    @pytest.fixture
    def temp_vault(self):
        """Create a temporary vault directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set environment variable to redirect vault to temp directory
            original_vault_dir = os.environ.get('VAULT_DIR')
            os.environ['VAULT_DIR'] = temp_dir
            
            try:
                yield Path(temp_dir)
            finally:
                # Restore original vault directory
                if original_vault_dir is not None:
                    os.environ['VAULT_DIR'] = original_vault_dir
                elif 'VAULT_DIR' in os.environ:
                    del os.environ['VAULT_DIR']
    
    def test_get_vault_dir_default(self):
        """Test default vault directory"""
        # Clean environment
        original_vault_dir = os.environ.get('VAULT_DIR')
        if 'VAULT_DIR' in os.environ:
            del os.environ['VAULT_DIR']
        
        try:
            vault_dir = get_vault_dir()
            assert vault_dir == Path('vault')
        finally:
            # Restore original
            if original_vault_dir is not None:
                os.environ['VAULT_DIR'] = original_vault_dir
    
    def test_get_vault_dir_environment_override(self):
        """Test vault directory environment variable override"""
        test_dir = '/tmp/test_vault'
        original_vault_dir = os.environ.get('VAULT_DIR')
        os.environ['VAULT_DIR'] = test_dir
        
        try:
            vault_dir = get_vault_dir()
            assert vault_dir == Path(test_dir)
        finally:
            # Restore original
            if original_vault_dir is not None:
                os.environ['VAULT_DIR'] = original_vault_dir
            else:
                del os.environ['VAULT_DIR']
    
    def test_seal_basic(self, temp_vault):
        """Test basic seal functionality"""
        protocol_name = "TestProtocol"
        result = seal(protocol_name)
        
        # Check return value
        assert result["protocol"] == protocol_name
        assert result["status"] == "invoked"  # default status
        assert "timestamp" in result
        assert "details" in result
        assert result["details"] == {}
        
        # Validate timestamp format (ISO 8601 with Z suffix)
        timestamp = result["timestamp"]
        assert timestamp.endswith('Z')
        # Should be parseable as datetime
        datetime.fromisoformat(timestamp.rstrip('Z'))
    
    def test_seal_with_custom_status_and_details(self, temp_vault):
        """Test seal with custom status and details"""
        protocol_name = "CustomProtocol"
        status = "completed"
        details = {"step": 1, "message": "Test execution"}
        
        result = seal(protocol_name, status=status, details=details)
        
        assert result["protocol"] == protocol_name
        assert result["status"] == status
        assert result["details"] == details
    
    def test_seal_file_creation(self, temp_vault):
        """Test that seal creates the correct files"""
        protocol_name = "FileTestProtocol"
        details = {"test": "data"}
        
        seal(protocol_name, status="tested", details=details)
        
        # Check directory structure
        protocol_dir = temp_vault / "protocols" / protocol_name
        assert protocol_dir.exists()
        assert protocol_dir.is_dir()
        
        # Check lore_applied.txt
        lore_file = protocol_dir / "lore_applied.txt"
        assert lore_file.exists()
        lore_content = lore_file.read_text()
        assert f"Protocol: {protocol_name}" in lore_content
        assert "Status: tested" in lore_content
        assert "Timestamp:" in lore_content
        assert "Details:" in lore_content
        
        # Check seal.json
        seal_file = protocol_dir / "seal.json"
        assert seal_file.exists()
        
        with open(seal_file) as f:
            seal_data = json.load(f)
        
        assert seal_data["protocol"] == protocol_name
        assert seal_data["status"] == "tested"
        assert seal_data["details"] == details
        assert "timestamp" in seal_data
    
    def test_seal_json_integrity(self, temp_vault):
        """Test JSON integrity of seal file"""
        protocol_name = "JsonIntegrityTest"
        details = {
            "complex": {"nested": "data"},
            "list": [1, 2, 3],
            "unicode": "🔒 sealed",
            "number": 42,
            "boolean": True
        }
        
        result = seal(protocol_name, details=details)
        
        # Read back the JSON file
        seal_file = temp_vault / "protocols" / protocol_name / "seal.json"
        with open(seal_file) as f:
            loaded_data = json.load(f)
        
        # Verify complete integrity
        assert loaded_data == result
        assert loaded_data["details"] == details
        
        # Verify JSON is well-formed (can be loaded without errors)
        json_str = seal_file.read_text()
        json.loads(json_str)  # Should not raise exception
    
    def test_seal_multiple_protocols(self, temp_vault):
        """Test sealing multiple different protocols"""
        protocols = ["Protocol1", "Protocol2", "Protocol3"]
        
        for i, protocol_name in enumerate(protocols):
            seal(protocol_name, status=f"step_{i}", details={"order": i})
        
        # Verify all protocols were created
        for i, protocol_name in enumerate(protocols):
            protocol_dir = temp_vault / "protocols" / protocol_name
            assert protocol_dir.exists()
            
            seal_file = protocol_dir / "seal.json"
            with open(seal_file) as f:
                seal_data = json.load(f)
            
            assert seal_data["protocol"] == protocol_name
            assert seal_data["status"] == f"step_{i}"
            assert seal_data["details"]["order"] == i
    
    def test_seal_directory_creation(self, temp_vault):
        """Test that seal creates nested directories as needed"""
        protocol_name = "DeepProtocol"
        
        # Ensure vault doesn't exist initially
        assert not (temp_vault / "protocols").exists()
        
        seal(protocol_name)
        
        # Verify full directory structure was created
        assert (temp_vault / "protocols").exists()
        assert (temp_vault / "protocols" / protocol_name).exists()
        assert (temp_vault / "protocols" / protocol_name / "seal.json").exists()
        assert (temp_vault / "protocols" / protocol_name / "lore_applied.txt").exists()
    
    def test_seal_overwrites_existing(self, temp_vault):
        """Test that seal overwrites existing files for the same protocol"""
        protocol_name = "OverwriteTest"
        
        # First seal
        result1 = seal(protocol_name, status="first", details={"run": 1})
        
        # Second seal (should overwrite)
        result2 = seal(protocol_name, status="second", details={"run": 2})
        
        # Verify the files contain the second seal data
        seal_file = temp_vault / "protocols" / protocol_name / "seal.json"
        with open(seal_file) as f:
            seal_data = json.load(f)
        
        assert seal_data["status"] == "second"
        assert seal_data["details"]["run"] == 2
        assert seal_data["timestamp"] == result2["timestamp"]
        # Timestamps should be different
        assert result1["timestamp"] != result2["timestamp"]