from fastapi.testclient import TestClient
from pathlib import Path
import json
import tempfile
import os

try:
    from bridge_backend.main import app
except ImportError:
    from main import app

client = TestClient(app)

def test_dispatch_and_ingest():
    """Test the main dispatch-and-ingest functionality"""
    body = {
        "project": "research",
        "captain": "Kyle",
        "permissions": {"read": ["docs"]},
        "objective": "recover_notes",
        "raw": "First paragraph.\n\nSecond paragraph."
    }
    r = client.post("/engines/recovery/dispatch-and-ingest", json=body)
    assert r.status_code == 200
    data = r.json()
    
    # Check return structure
    assert "task" in data
    assert "manifest" in data
    assert "linkage" in data
    
    # Check task structure
    task = data["task"]
    assert task["project"] == "research"
    assert task["captain"] == "Kyle"
    assert task["objective"] == "recover_notes"
    assert task["mode"] == "hybrid"
    assert "id" in task
    
    # Check manifest structure
    manifest = data["manifest"]
    assert "ok" in manifest
    assert manifest["ok"] is True
    assert "seen" in manifest
    assert "filed" in manifest
    assert "manifest" in manifest
    
    # Check linkage structure
    linkage = data["linkage"]
    assert linkage["task_id"] == task["id"]
    assert "manifest" in linkage

def test_dispatch_and_ingest_vault_creation():
    """Test that vault files are created correctly"""
    # Get current vault contents
    vault_dir = Path("vault/recovery")
    if vault_dir.exists():
        initial_files = set(f.name for f in vault_dir.iterdir())
    else:
        initial_files = set()
    
    body = {
        "project": "vault_test",
        "captain": "TestCaptain", 
        "permissions": {"execute": ["test"]},
        "objective": "test_vault_logging",
        "raw": "Test content for vault logging."
    }
    
    r = client.post("/engines/recovery/dispatch-and-ingest", json=body)
    assert r.status_code == 200
    
    # Check that new files were created
    if vault_dir.exists():
        final_files = set(f.name for f in vault_dir.iterdir())
        new_files = final_files - initial_files
        
        # Should have 3 new files: task_created, parsed_manifest, linkage
        assert len(new_files) >= 3
        
        # Check that files have correct prefixes
        prefixes = set()
        for filename in new_files:
            if "_" in filename:
                prefixes.add(filename.split("_")[0])
        
        expected_prefixes = {"task", "parsed", "linkage"}
        assert expected_prefixes.issubset(prefixes)

def test_error_handling():
    """Test error handling with invalid input"""
    # Test with missing required fields
    body = {
        "project": "test",
        # missing captain, permissions, objective, raw
    }
    r = client.post("/engines/recovery/dispatch-and-ingest", json=body)
    assert r.status_code == 422  # Validation error

def test_different_permissions():
    """Test dispatch with different permission structures"""
    body = {
        "project": "permission_test",
        "captain": "PermissionCaptain",
        "permissions": {"read": ["docs", "email"], "write": ["vault"]},
        "objective": "test_permissions",
        "raw": "Content with different permissions."
    }
    
    r = client.post("/engines/recovery/dispatch-and-ingest", json=body)
    assert r.status_code == 200
    data = r.json()
    
    task = data["task"]
    assert task["permissions"]["read"] == ["docs", "email"]
    assert task["permissions"]["write"] == ["vault"]

def test_large_raw_content():
    """Test with larger raw content that will be chunked"""
    # Create content that will be split into multiple chunks
    paragraphs = ["Paragraph {}.\n\nThis is content for paragraph {}.".format(i, i) for i in range(10)]
    large_raw = "\n\n".join(paragraphs)
    
    body = {
        "project": "large_content_test",
        "captain": "LargeCaptain",
        "permissions": {"read": ["all"]},
        "objective": "test_large_content",
        "raw": large_raw
    }
    
    r = client.post("/engines/recovery/dispatch-and-ingest", json=body)
    assert r.status_code == 200
    data = r.json()
    
    manifest = data["manifest"]
    assert manifest["ok"] is True
    assert manifest["seen"] > 0  # Should have parsed some content
    assert "manifest" in manifest
    assert len(manifest["manifest"]) > 0  # Should have created chunks