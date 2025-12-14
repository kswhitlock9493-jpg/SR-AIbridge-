"""
Tests for GitHub Forge
"""

import pytest
from pathlib import Path
from bridge_backend.engines.github_forge.core import GitHubForge


def test_github_forge_initialization():
    """Test GitHub Forge initialization"""
    forge = GitHubForge()
    
    assert forge is not None
    # Forge directory should be created
    assert Path(".github/bridge").exists()


def test_github_forge_put_get_json():
    """Test GitHub Forge JSON read/write"""
    forge = GitHubForge()
    
    test_data = {"test": "data", "value": 123}
    path = forge.put_json("test_config", test_data)
    
    assert path is not None
    assert Path(path).exists()
    
    retrieved = forge.get_json("test_config")
    assert retrieved == test_data
    
    # Cleanup
    Path(path).unlink()


def test_github_forge_put_env():
    """Test GitHub Forge env file writing"""
    forge = GitHubForge()
    
    env_data = {"VAR1": "value1", "VAR2": "value2"}
    path = forge.put_env("test_env", env_data)
    
    assert path is not None
    assert Path(path).exists()
    
    content = Path(path).read_text()
    assert 'VAR1="value1"' in content
    assert 'VAR2="value2"' in content
    
    # Cleanup
    Path(path).unlink()
