from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json
import shutil

client = TestClient(app)

def setup_creativity_vault():
    """Helper to setup vault/creativity directory"""
    vault_dir = Path("vault/creativity")
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir

def cleanup_creativity_vault():
    """Helper to cleanup test assets from vault"""
    vault_dir = Path("vault/creativity")
    if vault_dir.exists():
        for f in vault_dir.glob("test_*.json"):
            f.unlink()

def test_tag_search():
    """Test Leviathan tag-aware search across creativity bay"""
    # Setup and cleanup
    vault_dir = setup_creativity_vault()
    cleanup_creativity_vault()
    
    try:
        # Create a test asset with tags
        test_asset = {
            "sha": "test_123abc",
            "title": "Dragon Saga",
            "text": "A story about dragons and their hidden worlds.",
            "tags": ["story", "fantasy"],
            "source": "unit-test",
            "created_at": "2025-10-01T12:00:00Z"
        }
        (vault_dir / "test_dragon.json").write_text(json.dumps(test_asset))
        
        # Search without tags - should find the asset
        r = client.post("/engines/leviathan/search", json={"query": "dragon"})
        assert r.status_code == 200
        results = r.json()["results"]
        assert any("Dragon Saga" in res.get("title", "") for res in results), f"Dragon Saga not found in results: {results}"

        # Search with matching tag - should find the asset
        r = client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["story"]})
        assert r.status_code == 200
        results = r.json()["results"]
        assert len(results) > 0, "No results found with story tag"
        assert any("story" in res.get("tags", []) for res in results), f"story tag not found in results: {results}"

        # Search with non-matching tag - should not find the asset
        r = client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["sci-fi"]})
        assert r.status_code == 200
        results = r.json()["results"]
        # Filter out any indexed docs that don't have tags (they come from DB, not creativity)
        creativity_results = [res for res in results if "tags" in res and res["tags"]]
        assert len(creativity_results) == 0, f"Should not find creativity assets with sci-fi tag, but found: {creativity_results}"
        
    finally:
        cleanup_creativity_vault()


def test_tag_search_multiple_assets():
    """Test Leviathan tag-aware search with multiple assets"""
    # Setup and cleanup
    vault_dir = setup_creativity_vault()
    cleanup_creativity_vault()
    
    try:
        # Create multiple test assets with different tags
        assets = [
            {
                "sha": "test_abc123",
                "title": "Dragon Tale",
                "text": "A dragon flies over mountains",
                "tags": ["fantasy", "dragon"],
                "source": "unit-test-1",
                "created_at": "2025-10-01T12:00:00Z"
            },
            {
                "sha": "test_def456",
                "title": "Space Adventure",
                "text": "A spacecraft explores distant galaxies",
                "tags": ["scifi", "space"],
                "source": "unit-test-2",
                "created_at": "2025-10-02T12:00:00Z"
            },
            {
                "sha": "test_ghi789",
                "title": "Dragon Comic",
                "text": "A dragon breathes fire in comic panels",
                "tags": ["comic", "dragon"],
                "source": "unit-test-3",
                "created_at": "2025-10-03T12:00:00Z"
            }
        ]
        
        for i, asset in enumerate(assets):
            (vault_dir / f"test_asset_{i}.json").write_text(json.dumps(asset))

        # Search for "dragon" with "comic" tag - should find only Dragon Comic
        r = client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["comic"]})
        assert r.status_code == 200
        results = r.json()["results"]
        creativity_results = [res for res in results if "tags" in res and res["tags"]]
        assert len(creativity_results) == 1, f"Expected 1 result with comic tag, got {len(creativity_results)}: {creativity_results}"
        assert creativity_results[0]["title"] == "Dragon Comic"
        assert "comic" in creativity_results[0]["tags"]

        # Search for "dragon" without tag filter - should find both dragon entries
        r = client.post("/engines/leviathan/search", json={"query": "dragon"})
        assert r.status_code == 200
        results = r.json()["results"]
        creativity_results = [res for res in results if "tags" in res and res["tags"]]
        assert len(creativity_results) == 2, f"Expected 2 results without tag filter, got {len(creativity_results)}: {creativity_results}"
        titles = [res["title"] for res in creativity_results]
        assert "Dragon Tale" in titles
        assert "Dragon Comic" in titles

        # Search with multiple tags - should match only if asset has all tags
        r = client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["dragon", "comic"]})
        assert r.status_code == 200
        results = r.json()["results"]
        creativity_results = [res for res in results if "tags" in res and res["tags"]]
        assert len(creativity_results) == 1, f"Expected 1 result with both tags, got {len(creativity_results)}: {creativity_results}"
        assert creativity_results[0]["title"] == "Dragon Comic"
        
    finally:
        cleanup_creativity_vault()
