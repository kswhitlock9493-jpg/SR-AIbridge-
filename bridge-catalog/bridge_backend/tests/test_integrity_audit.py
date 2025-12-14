#!/usr/bin/env python3
"""
Tests for integrity_audit.py
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

import integrity_audit


def test_check_env_vars():
    """Test environment variable checking"""
    # Mock environment variables
    with patch.dict(os.environ, {
        'BRIDGE_ENV': 'production',
        'NETLIFY_API': 'https://api.netlify.com',
        'BRIDGE_BACKEND': 'https://bridge.sr-aibridge.com',
        'BRIDGE_DIAGNOSTICS': 'https://diagnostics.sr-aibridge.com'
    }):
        result = integrity_audit.check_env_vars()
        assert result['BRIDGE_ENV'] == 'production'
        assert result['NETLIFY_API'] == 'https://api.netlify.com'
        assert result['BRIDGE_BACKEND'] == 'https://bridge.sr-aibridge.com'
        assert result['BRIDGE_DIAGNOSTICS'] == 'https://diagnostics.sr-aibridge.com'


def test_check_env_vars_missing():
    """Test environment variable checking with missing vars"""
    # Clear environment
    with patch.dict(os.environ, {}, clear=True):
        result = integrity_audit.check_env_vars()
        assert result['BRIDGE_ENV'] == 'MISSING'
        assert result['NETLIFY_API'] == 'MISSING'
        assert result['BRIDGE_BACKEND'] == 'MISSING'
        assert result['BRIDGE_DIAGNOSTICS'] == 'MISSING'


def test_check_endpoints_success():
    """Test endpoint checking with successful responses"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.ok = True
    
    with patch('integrity_audit.requests.get', return_value=mock_response):
        result = integrity_audit.check_endpoints()
        
        # All endpoints should succeed
        assert result['Bridge']['status'] == 200
        assert result['Bridge']['ok'] is True
        assert result['Diagnostics']['status'] == 200
        assert result['Diagnostics']['ok'] is True
        assert result['Render']['status'] == 200
        assert result['Render']['ok'] is True
        assert result['Netlify']['status'] == 200
        assert result['Netlify']['ok'] is True


def test_check_endpoints_failure():
    """Test endpoint checking with failures"""
    with patch('integrity_audit.requests.get', side_effect=Exception('Connection failed')):
        result = integrity_audit.check_endpoints()
        
        # All endpoints should report errors
        assert result['Bridge']['status'] == 'error'
        assert 'Connection failed' in result['Bridge']['detail']
        assert result['Diagnostics']['status'] == 'error'
        assert result['Render']['status'] == 'error'
        assert result['Netlify']['status'] == 'error'


def test_check_endpoints_mixed():
    """Test endpoint checking with mixed responses"""
    def mock_get(url, timeout=None):
        mock_response = MagicMock()
        if 'netlify' in url:
            mock_response.status_code = 200
            mock_response.ok = True
            return mock_response
        else:
            raise Exception('Connection timeout')
    
    with patch('integrity_audit.requests.get', side_effect=mock_get):
        result = integrity_audit.check_endpoints()
        
        # Netlify should succeed
        assert result['Netlify']['status'] == 200
        assert result['Netlify']['ok'] is True
        
        # Others should fail
        assert result['Bridge']['status'] == 'error'
        assert result['Diagnostics']['status'] == 'error'
        assert result['Render']['status'] == 'error'


def test_run_audit():
    """Test the complete audit run"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = os.path.join(tmpdir, "logs", "audit.json")
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True
        
        with patch.object(integrity_audit, 'LOG_PATH', log_path), \
             patch('integrity_audit.requests.get', return_value=mock_response), \
             patch.dict(os.environ, {'BRIDGE_ENV': 'test'}):
            
            integrity_audit.run_audit()
            
            # Verify log file was created
            assert os.path.exists(log_path)
            
            # Verify log contents
            with open(log_path, 'r') as f:
                data = json.load(f)
                assert 'timestamp' in data
                assert 'env' in data
                assert 'endpoints' in data
                assert data['env']['BRIDGE_ENV'] == 'test'
                assert data['endpoints']['Bridge']['status'] == 200


if __name__ == "__main__":
    print("Running integrity_audit tests...")
    
    test_check_env_vars()
    print("✅ test_check_env_vars")
    
    test_check_env_vars_missing()
    print("✅ test_check_env_vars_missing")
    
    test_check_endpoints_success()
    print("✅ test_check_endpoints_success")
    
    test_check_endpoints_failure()
    print("✅ test_check_endpoints_failure")
    
    test_check_endpoints_mixed()
    print("✅ test_check_endpoints_mixed")
    
    test_run_audit()
    print("✅ test_run_audit")
    
    print("\n🎉 All tests passed!")
