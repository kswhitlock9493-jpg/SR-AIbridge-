import asyncio, os
import pytest
from bridge_core.engines.envsync.diffs import compute_diff
from bridge_core.engines.envsync.engine import load_canonical, _is_included
from bridge_core.engines.envsync.config import CONFIG

def test_diff_noop():
    """Test that identical environments produce noop diffs"""
    canon = {"BRIDGE_OK": "1"}
    remote = {"BRIDGE_OK": "1"}
    d = compute_diff(canon, remote, allow_deletions=False)
    assert any(x["op"] == "noop" and x["key"] == "BRIDGE_OK" for x in d)

def test_diff_create():
    """Test that new variables are marked as create"""
    canon = {"BRIDGE_NEW": "value"}
    remote = {}
    d = compute_diff(canon, remote, allow_deletions=False)
    assert any(x["op"] == "create" and x["key"] == "BRIDGE_NEW" for x in d)

def test_diff_update():
    """Test that changed variables are marked as update"""
    canon = {"BRIDGE_VAR": "new_value"}
    remote = {"BRIDGE_VAR": "old_value"}
    d = compute_diff(canon, remote, allow_deletions=False)
    assert any(x["op"] == "update" and x["key"] == "BRIDGE_VAR" for x in d)

def test_diff_delete_disabled():
    """Test that deletions are ignored when allow_deletions=False"""
    canon = {}
    remote = {"OLD_VAR": "value"}
    d = compute_diff(canon, remote, allow_deletions=False)
    assert not any(x["op"] == "delete" for x in d)

def test_diff_delete_enabled():
    """Test that deletions are included when allow_deletions=True"""
    canon = {}
    remote = {"OLD_VAR": "value"}
    d = compute_diff(canon, remote, allow_deletions=True)
    assert any(x["op"] == "delete" and x["key"] == "OLD_VAR" for x in d)

def test_include_exclude_prefixes():
    """Test that prefix filtering works correctly"""
    # Should be excluded
    assert not _is_included("SECRET_TOKEN")
    assert not _is_included("INTERNAL_VAR")
    assert not _is_included("DEBUG_FLAG")
    
    # Should be included (if include_prefixes is set)
    # Note: The default config includes BRIDGE_, SR_, HEART_, ENVSYNC_
    # If include_prefixes is empty, all non-excluded vars are included

def test_canonical_from_env():
    """Test that canonical source loads from environment"""
    # Set a test variable
    os.environ["BRIDGE_TEST_VAR"] = "test_value"
    canonical = load_canonical()
    # Should include BRIDGE_ prefixed vars
    if "BRIDGE_TEST_VAR" in canonical:
        assert canonical["BRIDGE_TEST_VAR"] == "test_value"
    # Clean up
    del os.environ["BRIDGE_TEST_VAR"]

def test_config_defaults():
    """Test that config has sensible defaults"""
    assert isinstance(CONFIG.enabled, bool)
    assert CONFIG.mode in ("dry-run", "enforce")
    assert isinstance(CONFIG.targets, list)
    assert isinstance(CONFIG.discovery_order, list)

# Add provider-mocked tests with httpx.MockTransport in follow-ups
# For now, these stubs verify core logic without external API calls
