# brh/test_chaos_recovery.py
"""
Tests for Chaos Injector and Recovery Watchtower modules
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from brh import chaos, recovery


class TestChaosModule:
    """Test cases for chaos.py module"""
    
    def test_chaos_disabled_by_default(self):
        """Test that chaos is disabled by default"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('threading.Thread') as mock_thread:
                chaos.start()
                mock_thread.assert_not_called()
    
    def test_chaos_enabled_starts_thread(self):
        """Test that chaos starts when enabled"""
        with patch.dict(os.environ, {'BRH_CHAOS_ENABLED': 'true'}):
            with patch('threading.Thread') as mock_thread:
                chaos.start()
                mock_thread.assert_called_once()
    
    def test_chaos_interval_configuration(self):
        """Test chaos interval can be configured"""
        # Module constants are set at import, so we need to reload
        import importlib
        with patch.dict(os.environ, {'BRH_CHAOS_INTERVAL': '300'}):
            importlib.reload(chaos)
            assert chaos.INTERVAL == 300
        # Restore original value
        importlib.reload(chaos)
    
    def test_chaos_probability_configuration(self):
        """Test chaos probability can be configured"""
        with patch.dict(os.environ, {'BRH_KILL_PROB': '0.25'}):
            # Need to reload the module to pick up env var
            import importlib
            importlib.reload(chaos)
            assert chaos.KILL_PROB == 0.25


class TestRecoveryModule:
    """Test cases for recovery.py module"""
    
    def test_recovery_enabled_by_default(self):
        """Test that recovery is enabled by default"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('brh.recovery.DOCKER_AVAILABLE', True):
                with patch('threading.Thread') as mock_thread:
                    recovery.start()
                    mock_thread.assert_called_once()
    
    def test_recovery_disabled_when_configured(self):
        """Test that recovery can be disabled"""
        with patch.dict(os.environ, {'BRH_RECOVERY_ENABLED': 'false'}):
            with patch('threading.Thread') as mock_thread:
                recovery.start()
                mock_thread.assert_not_called()
    
    def test_recovery_disabled_without_docker(self):
        """Test that recovery is disabled when Docker SDK unavailable"""
        with patch('brh.recovery.DOCKER_AVAILABLE', False):
            with patch('threading.Thread') as mock_thread:
                recovery.start()
                mock_thread.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
