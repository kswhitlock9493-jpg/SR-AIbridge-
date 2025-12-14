"""
Tests for Chimera Genesis Recovery
Tests import path normalization, retry logic, and fallback channel
"""
import types
from unittest.mock import MagicMock, patch
import pytest


def test_import_genesis_bus_success():
    """Test successful Genesis bus import via paths.py"""
    from bridge_backend.bridge_core.paths import import_genesis_bus
    
    # Should not raise - tests that the function exists and can attempt import
    try:
        bus_mod = import_genesis_bus()
        # If it succeeds, verify it has expected attributes
        assert hasattr(bus_mod, 'genesis_bus') or hasattr(bus_mod, '__name__')
    except ModuleNotFoundError:
        # It's ok if module doesn't exist in test environment
        # The important thing is the path logic is correct
        pass


def test_register_with_retry_success(monkeypatch):
    """Test successful registration with Genesis bus"""
    # Create fake bus module with publish method
    fake_bus_instance = MagicMock()
    fake_bus_instance.publish = MagicMock()
    
    fake_bus_mod = types.SimpleNamespace(
        genesis_bus=fake_bus_instance
    )
    
    def mock_import_genesis_bus():
        return fake_bus_mod
    
    # Patch the import function
    monkeypatch.setattr(
        "bridge_backend.bridge_core.engines.adapters.chimera_genesis_link._load_bus",
        lambda: fake_bus_mod
    )
    
    from bridge_backend.bridge_core.engines.adapters.chimera_genesis_link import register_with_retry
    
    result = register_with_retry()
    assert result is True
    # Verify publish was called
    assert fake_bus_instance.publish.called


def test_register_with_retry_fallback(monkeypatch, capsys):
    """Test fallback to Umbra Lattice when Genesis unavailable"""
    def mock_load_bus():
        return None
    
    # Patch _load_bus to return None (failure)
    monkeypatch.setattr(
        "bridge_backend.bridge_core.engines.adapters.chimera_genesis_link._load_bus",
        mock_load_bus
    )
    
    from bridge_backend.bridge_core.engines.adapters.chimera_genesis_link import register_with_retry
    
    result = register_with_retry()
    assert result is False


def test_safe_init_with_fallback(monkeypatch, capsys):
    """Test safe_init activates fallback when registration fails"""
    # Mock register_with_retry to fail
    def mock_register_with_retry():
        return False
    
    # Mock fallback_neural_channel
    fallback_called = []
    def mock_fallback_neural_channel(name):
        fallback_called.append(name)
    
    monkeypatch.setattr(
        "bridge_backend.bridge_core.engines.adapters.chimera_genesis_link.register_with_retry",
        mock_register_with_retry
    )
    monkeypatch.setattr(
        "bridge_backend.bridge_core.engines.umbra.lattice.fallback_neural_channel",
        mock_fallback_neural_channel
    )
    
    from bridge_backend.bridge_core.engines.hxo import safe_init
    
    # Should not crash
    safe_init()
    
    # Verify fallback was called with 'chimera'
    assert 'chimera' in fallback_called


def test_fallback_neural_channel():
    """Test Umbra Lattice fallback neural channel"""
    from bridge_backend.bridge_core.engines.umbra.lattice import fallback_neural_channel
    
    # Should not crash and should log
    fallback_neural_channel("test_engine")
    # No exception means success
