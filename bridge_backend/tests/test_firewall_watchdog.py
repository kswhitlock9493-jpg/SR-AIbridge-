#!/usr/bin/env python3
"""
Tests for firewall_watchdog.py
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import firewall_watchdog


def test_load_allowlist_empty():
    """Test loading allowlist when file doesn't exist"""
    with patch.object(os.path, 'exists', return_value=False):
        result = firewall_watchdog.load_allowlist()
        assert result == []


def test_load_allowlist_with_hosts():
    """Test loading allowlist with valid hosts"""
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("example.com\n")
        f.write("test.org\n")
        f.write("\n")  # Empty line should be ignored
        f.write("# comment\n")  # This will be included as-is
        temp_file = f.name
    
    try:
        with patch.object(firewall_watchdog, 'ALLOWLIST_PATH', temp_file):
            result = firewall_watchdog.load_allowlist()
            assert "example.com" in result
            assert "test.org" in result
            # Empty lines should be filtered out
            assert "" not in result
    finally:
        os.unlink(temp_file)


def test_log_event():
    """Test event logging"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "logs", "test.log")
        
        with patch.object(firewall_watchdog, 'LOG_PATH', log_path):
            event = {
                "timestamp": "2025-01-15T12:00:00+00:00",
                "host": "example.com",
                "resolved": True,
                "allowed": True,
                "trigger": "test"
            }
            
            firewall_watchdog.log_event(event)
            
            # Verify log file exists and contains the event
            assert os.path.exists(log_path)
            with open(log_path, 'r') as f:
                logged = json.loads(f.read().strip())
                assert logged["host"] == "example.com"
                assert logged["resolved"] is True


def test_report_to_bridge():
    """Test Bridge API reporting (mocked)"""
    with patch('firewall_watchdog.requests.post') as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        
        event = {
            "timestamp": "2025-01-15T12:00:00+00:00",
            "host": "example.com",
            "resolved": True,
            "allowed": True,
            "trigger": "test"
        }
        
        firewall_watchdog.report_to_bridge(event)
        
        # Verify the API was called
        assert mock_post.called
        call_args = mock_post.call_args
        assert "api/diagnostics" in call_args[0][0]
        assert call_args[1]["json"]["type"] == "FIREWALL_EVENT"


def test_report_to_bridge_failure():
    """Test Bridge API reporting handles failures gracefully"""
    with patch('firewall_watchdog.requests.post', side_effect=Exception("Network error")):
        event = {
            "timestamp": "2025-01-15T12:00:00+00:00",
            "host": "example.com",
            "resolved": True,
            "allowed": True,
            "trigger": "test"
        }
        
        # Should not raise an exception
        try:
            firewall_watchdog.report_to_bridge(event)
        except Exception:
            assert False, "report_to_bridge should handle exceptions gracefully"


def test_test_connection():
    """Test DNS connection testing"""
    # Test with a known good host
    with patch('firewall_watchdog.socket.gethostbyname', return_value='1.2.3.4'):
        result = firewall_watchdog.test_connection("example.com")
        assert result is True
    
    # Test with a host that fails
    with patch('firewall_watchdog.socket.gethostbyname', side_effect=Exception("DNS failed")):
        result = firewall_watchdog.test_connection("invalid.host")
        assert result is False


def test_watchdog_integration():
    """Test the full watchdog integration"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "logs", "firewall.log")
        allowlist_path = os.path.join(tmpdir, "allowlist.txt")
        
        # Create test allowlist
        with open(allowlist_path, 'w') as f:
            f.write("example.com\n")
            f.write("test.org\n")
        
        with patch.object(firewall_watchdog, 'LOG_PATH', log_path), \
             patch.object(firewall_watchdog, 'ALLOWLIST_PATH', allowlist_path), \
             patch('firewall_watchdog.requests.post') as mock_post, \
             patch('firewall_watchdog.test_connection') as mock_test:
            
            # Mock DNS resolution
            mock_test.return_value = True
            mock_post.return_value = MagicMock(status_code=200)
            
            firewall_watchdog.watchdog()
            
            # Verify log file was created
            assert os.path.exists(log_path)
            
            # Verify events were logged
            with open(log_path, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 0
                
                # Verify first event
                first_event = json.loads(lines[0])
                assert "timestamp" in first_event
                assert "host" in first_event
                assert "resolved" in first_event
                assert "allowed" in first_event


if __name__ == "__main__":
    print("Running firewall_watchdog tests...")
    
    test_load_allowlist_empty()
    print("✅ test_load_allowlist_empty")
    
    test_load_allowlist_with_hosts()
    print("✅ test_load_allowlist_with_hosts")
    
    test_log_event()
    print("✅ test_log_event")
    
    test_report_to_bridge()
    print("✅ test_report_to_bridge")
    
    test_report_to_bridge_failure()
    print("✅ test_report_to_bridge_failure")
    
    test_test_connection()
    print("✅ test_test_connection")
    
    test_watchdog_integration()
    print("✅ test_watchdog_integration")
    
    print("\n🎉 All tests passed!")
