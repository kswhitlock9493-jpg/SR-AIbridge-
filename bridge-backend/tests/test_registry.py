"""
Tests for the protocol registry module.
"""

import pytest
from bridge_core.protocols.registry import ProtocolEntry


class TestProtocolEntry:
    """Test the ProtocolEntry class"""
    
    def test_protocol_entry_default_state(self):
        """Test ProtocolEntry with default state"""
        entry = ProtocolEntry("TestProtocol")
        assert entry.name == "TestProtocol"
        assert entry.state == "vaulted"
    
    def test_protocol_entry_custom_state(self):
        """Test ProtocolEntry with custom state"""
        entry = ProtocolEntry("CustomProtocol", "active")
        assert entry.name == "CustomProtocol"
        assert entry.state == "active"
    
    def test_protocol_entry_empty_name(self):
        """Test ProtocolEntry with empty name"""
        entry = ProtocolEntry("", "testing")
        assert entry.name == ""
        assert entry.state == "testing"
    
    def test_protocol_entry_special_characters(self):
        """Test ProtocolEntry with special characters in name"""
        entry = ProtocolEntry("Protocol-With_Special.Chars", "sealed")
        assert entry.name == "Protocol-With_Special.Chars"
        assert entry.state == "sealed"