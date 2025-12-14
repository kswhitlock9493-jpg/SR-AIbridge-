"""
Test suite for Secure Data Relay Protocol (relay_mailer)
"""
import pytest
import os
import json
from pathlib import Path
from utils.relay_mailer import RelayMailer, relay_mailer


class TestRelayMailer:
    """Test cases for RelayMailer functionality"""
    
    def test_relay_mailer_initialization(self):
        """Test that RelayMailer can be initialized"""
        mailer = RelayMailer()
        assert mailer is not None
        assert mailer.relay_email == "sraibridge@gmail.com"
        assert mailer.relay_mode == "pre_delete"
    
    def test_global_relay_mailer_instance(self):
        """Test that global relay_mailer instance exists"""
        assert relay_mailer is not None
        assert isinstance(relay_mailer, RelayMailer)
    
    def test_checksum_calculation(self):
        """Test checksum calculation for data verification"""
        mailer = RelayMailer()
        
        # Test with string data
        data1 = "test data"
        checksum1 = mailer.calculate_checksum(data1)
        assert isinstance(checksum1, str)
        assert len(checksum1) == 64  # SHA256 hex is 64 chars
        
        # Test with dict data
        data2 = {"key": "value", "number": 123}
        checksum2 = mailer.calculate_checksum(data2)
        assert isinstance(checksum2, str)
        assert len(checksum2) == 64
        
        # Same data should produce same checksum
        checksum3 = mailer.calculate_checksum(data1)
        assert checksum1 == checksum3
    
    def test_format_relay_metadata(self):
        """Test metadata envelope formatting"""
        mailer = RelayMailer()
        
        test_data = {"mission_id": 123, "status": "deleted"}
        metadata = mailer.format_relay_metadata(
            component="vault",
            action="DELETE",
            user_id="captain_alpha",
            role="captain",
            data=test_data
        )
        
        # Verify all required fields
        assert "timestamp" in metadata
        assert "user_id" in metadata
        assert metadata["user_id"] == "captain_alpha"
        assert metadata["role"] == "captain"
        assert metadata["component"] == "vault"
        assert metadata["action"] == "DELETE"
        assert "payload_hash" in metadata
        assert metadata["retention_hours"] == 14  # Captain retention
        assert "notes" in metadata
    
    def test_role_based_retention(self):
        """Test role-based retention policies"""
        mailer = RelayMailer()
        
        # Admiral - permanent
        metadata_admiral = mailer.format_relay_metadata(
            "vault", "DELETE", "admiral_1", "admiral", {"data": "test"}
        )
        assert metadata_admiral["retention_hours"] == -1
        
        # Captain - 14 hours
        metadata_captain = mailer.format_relay_metadata(
            "vault", "DELETE", "captain_1", "captain", {"data": "test"}
        )
        assert metadata_captain["retention_hours"] == 14
        
        # Agent - 7 hours
        metadata_agent = mailer.format_relay_metadata(
            "vault", "DELETE", "agent_1", "agent", {"data": "test"}
        )
        assert metadata_agent["retention_hours"] == 7
    
    def test_verify_archive(self):
        """Test archive verification with checksum"""
        mailer = RelayMailer()
        
        test_data = {"mission": "test_mission", "id": 456}
        metadata = mailer.format_relay_metadata(
            "missions", "DELETE", "captain_beta", "captain", test_data
        )
        
        # Verification should succeed with correct data
        assert mailer.verify_archive(metadata, test_data) is True
        
        # Verification should fail with modified data
        modified_data = {"mission": "modified_mission", "id": 456}
        assert mailer.verify_archive(metadata, modified_data) is False
    
    def test_queue_for_retry(self, tmp_path):
        """Test queueing mechanism for failed sends"""
        # Create mailer with temporary backup path
        os.environ["RELAY_BACKUP_PATH"] = str(tmp_path)
        mailer = RelayMailer()
        
        test_data = {"test": "data"}
        metadata = mailer.format_relay_metadata(
            "vault", "DELETE", "captain_gamma", "captain", test_data
        )
        
        # Queue the item
        queue_file = mailer.queue_for_retry(metadata, test_data)
        
        # Verify file was created
        assert Path(queue_file).exists()
        
        # Verify content
        with open(queue_file, 'r') as f:
            queued_entry = json.load(f)
        
        assert "metadata" in queued_entry
        assert "data" in queued_entry
        assert "queued_at" in queued_entry
        assert queued_entry["retry_count"] == 0
        assert queued_entry["data"] == test_data
    
    def test_get_queued_items(self, tmp_path):
        """Test retrieval of queued items"""
        os.environ["RELAY_BACKUP_PATH"] = str(tmp_path)
        mailer = RelayMailer()
        
        # Create some queue files
        test_data1 = {"id": 1}
        test_data2 = {"id": 2}
        
        metadata1 = mailer.format_relay_metadata(
            "vault", "DELETE", "user1", "captain", test_data1
        )
        metadata2 = mailer.format_relay_metadata(
            "brain", "EXPIRE", "user2", "agent", test_data2
        )
        
        mailer.queue_for_retry(metadata1, test_data1)
        mailer.queue_for_retry(metadata2, test_data2)
        
        # Get queued items
        queued = mailer.get_queued_items()
        
        assert len(queued) == 2
        assert all(f.suffix == ".json" for f in queued)
        assert all("relay_" in f.name for f in queued)
    
    def test_disabled_relay(self):
        """Test that relay can be disabled"""
        os.environ["RELAY_ENABLED"] = "false"
        mailer = RelayMailer()
        
        assert mailer.enabled is False
    
    def test_enabled_relay(self):
        """Test that relay can be enabled"""
        os.environ["RELAY_ENABLED"] = "true"
        mailer = RelayMailer()
        
        assert mailer.enabled is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
