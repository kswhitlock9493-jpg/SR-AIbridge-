"""
Tests for Umbra Echo - Human-Informed Adaptive Learning Engine
"""

import pytest
import asyncio
from datetime import datetime, timezone
from bridge_backend.bridge_core.engines.umbra.echo import UmbraEcho


@pytest.mark.asyncio
async def test_umbra_echo_initialization():
    """Test Umbra Echo initialization"""
    echo = UmbraEcho()
    
    assert echo is not None
    assert echo.enabled is True
    assert echo.reflect_on_commit is True
    assert len(echo.watched_paths) > 0


@pytest.mark.asyncio
async def test_capture_edit():
    """Test capturing a manual edit"""
    echo = UmbraEcho()
    
    change = {
        "actor": "Admiral",
        "file": ".github/workflows/deploy.yml",
        "diff": "fix: Update deployment timeout",
        "commit_hash": "abc123",
        "lines_added": 2,
        "lines_removed": 1
    }
    
    entry = await echo.capture_edit(change)
    
    assert entry is not None
    assert entry["actor"] == "Admiral"
    assert entry["file"] == ".github/workflows/deploy.yml"
    assert "intent" in entry
    assert "metadata" in entry


@pytest.mark.asyncio
async def test_classify_intent_fix():
    """Test intent classification for fix"""
    echo = UmbraEcho()
    
    change = {
        "file": "test.py",
        "diff": "fix: Resolve bug in authentication"
    }
    
    intent = echo._classify_intent(change)
    
    assert intent == "intent:fix"


@pytest.mark.asyncio
async def test_classify_intent_optimize():
    """Test intent classification for optimization"""
    echo = UmbraEcho()
    
    change = {
        "file": "test.py",
        "diff": "optimize: Improve query performance"
    }
    
    intent = echo._classify_intent(change)
    
    assert intent == "intent:optimize"


@pytest.mark.asyncio
async def test_classify_intent_feature():
    """Test intent classification for feature"""
    echo = UmbraEcho()
    
    change = {
        "file": "test.py",
        "diff": "feat: Add new authentication method"
    }
    
    intent = echo._classify_intent(change)
    
    assert intent == "intent:feature"


@pytest.mark.asyncio
async def test_detect_subsystems_ci_cd():
    """Test subsystem detection for CI/CD files"""
    echo = UmbraEcho()
    
    subsystems = echo._detect_subsystems(".github/workflows/test.yml")
    
    assert "ci_cd" in subsystems


@pytest.mark.asyncio
async def test_detect_subsystems_config():
    """Test subsystem detection for config files"""
    echo = UmbraEcho()
    
    subsystems = echo._detect_subsystems(".env")
    
    assert "configuration" in subsystems


@pytest.mark.asyncio
async def test_detect_subsystems_engines():
    """Test subsystem detection for engine files"""
    echo = UmbraEcho()
    
    subsystems = echo._detect_subsystems("bridge_backend/bridge_core/engines/umbra/core.py")
    
    assert "engines" in subsystems
    assert "umbra" in subsystems


@pytest.mark.asyncio
async def test_observe_commit():
    """Test observing a git commit"""
    echo = UmbraEcho()
    
    commit_data = {
        "hash": "abc123def456",
        "author": "Admiral",
        "message": "fix: Update deployment config",
        "files": [
            {
                "path": ".github/workflows/deploy.yml",
                "diff": "fix: Update timeout values",
                "additions": 3,
                "deletions": 1
            },
            {
                "path": ".env",
                "diff": "Update database URL",
                "additions": 1,
                "deletions": 1
            }
        ]
    }
    
    entries = await echo.observe_commit(commit_data)
    
    assert len(entries) == 2  # Both files are in watched paths
    assert all(e["commit_hash"] == "abc123def456" for e in entries)


@pytest.mark.asyncio
async def test_observe_commit_unwatched_files():
    """Test that unwatched files are ignored"""
    echo = UmbraEcho()
    
    commit_data = {
        "hash": "abc123",
        "author": "Admiral",
        "message": "Update README",
        "files": [
            {
                "path": "README.md",
                "diff": "Update documentation",
                "additions": 10,
                "deletions": 5
            }
        ]
    }
    
    entries = await echo.observe_commit(commit_data)
    
    assert len(entries) == 0  # README.md is not in watched paths


@pytest.mark.asyncio
async def test_get_metrics():
    """Test metrics retrieval"""
    echo = UmbraEcho()
    
    # Capture an edit
    change = {
        "file": ".env",
        "diff": "fix: Update config"
    }
    await echo.capture_edit(change)
    
    metrics = echo.get_metrics()
    
    assert metrics is not None
    assert "enabled" in metrics
    assert "echo_events" in metrics
    assert "intents" in metrics
    assert metrics["echo_events"] >= 1


@pytest.mark.asyncio
async def test_multiple_intents():
    """Test capturing multiple edits with different intents"""
    echo = UmbraEcho()
    
    changes = [
        {"file": "test1.py", "diff": "fix: bug fix"},
        {"file": "test2.py", "diff": "feat: new feature"},
        {"file": "test3.py", "diff": "optimize: performance"},
    ]
    
    for change in changes:
        await echo.capture_edit(change)
    
    metrics = echo.get_metrics()
    
    assert "intents" in metrics
    assert len(metrics["intents"]) >= 3
