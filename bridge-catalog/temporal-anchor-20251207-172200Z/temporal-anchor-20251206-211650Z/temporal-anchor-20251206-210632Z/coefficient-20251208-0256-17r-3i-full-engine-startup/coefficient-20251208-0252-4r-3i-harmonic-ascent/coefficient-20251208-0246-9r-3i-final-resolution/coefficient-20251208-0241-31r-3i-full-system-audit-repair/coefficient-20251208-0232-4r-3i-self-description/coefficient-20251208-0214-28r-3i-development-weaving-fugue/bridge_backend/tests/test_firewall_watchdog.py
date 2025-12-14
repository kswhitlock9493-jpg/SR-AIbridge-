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


def test_resolve_dns():
    """Test DNS resolution function"""
    with patch('firewall_watchdog.socket.gethostbyname', return_value='1.2.3.4'):
        result = firewall_watchdog.resolve_dns("example.com")
        assert result["host"] == "example.com"
        assert result["ip"] == "1.2.3.4"
        assert result["status"] == "resolved"
    
    # Test error case
    with patch('firewall_watchdog.socket.gethostbyname', side_effect=Exception("DNS failed")):
        result = firewall_watchdog.resolve_dns("invalid.host")
        assert result["host"] == "invalid.host"
        assert result["status"] == "error"
        assert "DNS failed" in result["detail"]


def test_ping_host():
    """Test HTTP ping functionality"""
    # Test successful ping
    with patch('firewall_watchdog.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = firewall_watchdog.ping_host("example.com")
        assert result["host"] == "example.com"
        assert result["status"] == 200
    
    # Test blocked host
    with patch('firewall_watchdog.requests.get', side_effect=Exception("Connection refused")):
        result = firewall_watchdog.ping_host("blocked.host")
        assert result["host"] == "blocked.host"
        assert result["status"] == "blocked"
        assert "Connection refused" in result["detail"]


def test_self_heal_dns():
    """Test self-healing DNS functionality"""
    with tempfile.TemporaryDirectory() as tmpdir:
        watchdog_log_path = os.path.join(tmpdir, "logs", "watchdog.log")
        
        with patch.object(firewall_watchdog, 'WATCHDOG_LOG_PATH', watchdog_log_path), \
             patch.object(firewall_watchdog, 'TARGETS', ["test1.com", "test2.com"]), \
             patch('firewall_watchdog.ping_host') as mock_ping, \
             patch('firewall_watchdog.resolve_dns') as mock_resolve:
            
            # Mock ping_host to return blocked for first host, success for second
            mock_ping.side_effect = [
                {"host": "test1.com", "status": "blocked", "detail": "timeout"},
                {"host": "test2.com", "status": 200}
            ]
            
            # Mock resolve_dns
            mock_resolve.return_value = {
                "host": "test1.com",
                "ip": "1.2.3.4",
                "status": "resolved"
            }
            
            firewall_watchdog.self_heal_dns()
            
            # Verify log was created
            assert os.path.exists(watchdog_log_path)
            
            # Verify log contents
            with open(watchdog_log_path, 'r') as f:
                log_data = json.loads(f.read().strip())
                assert "timestamp" in log_data
                assert "entries" in log_data
                assert len(log_data["entries"]) == 2


def test_write_log():
    """Test write_log functionality for self-healing DNS"""
    with tempfile.TemporaryDirectory() as tmpdir:
        watchdog_log_path = os.path.join(tmpdir, "logs", "watchdog.log")
        
        with patch.object(firewall_watchdog, 'WATCHDOG_LOG_PATH', watchdog_log_path):
            test_data = [
                {"host": "test.com", "status": "resolved"},
                {"host": "test2.com", "status": "blocked"}
            ]
            
            firewall_watchdog.write_log(test_data)
            
            # Verify file was created
            assert os.path.exists(watchdog_log_path)
            
            # Verify contents
            with open(watchdog_log_path, 'r') as f:
                log_entry = json.loads(f.read().strip())
                assert "timestamp" in log_entry
                assert "entries" in log_entry
                assert log_entry["entries"] == test_data


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
    
    test_resolve_dns()
    print("✅ test_resolve_dns")
    
    test_ping_host()
    print("✅ test_ping_host")
    
    test_self_heal_dns()
    print("✅ test_self_heal_dns")
    
    test_write_log()
    print("✅ test_write_log")
    
    print("\n🎉 All tests passed!")

