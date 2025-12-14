from fastapi.testclient import TestClient
from bridge_backend.main import app
from pathlib import Path
import json

client = TestClient(app)

def test_unified_search_with_tags(tmp_path):
    """Test unified search across creativity, parser, and truth planes with tag filtering"""
    # Setup vault directories directly (no monkeypatching needed)
    vault_dir = Path("vault")
    vault_dir.mkdir(exist_ok=True)
    
    # --- Creativity asset ---
    creat_dir = vault_dir / "creativity"
    creat_dir.mkdir(parents=True, exist_ok=True)
    
    # Clean up any existing test files
    for f in creat_dir.glob("test_unified_*.json"):
        f.unlink()
    
    (creat_dir / "test_unified_a.json").write_text(json.dumps({
        "sha": "aaa",
        "title": "Dragon Sketch",
        "text": "A concept art piece of a dragon.",
        "tags": ["art", "fantasy"],
        "source": "creativity-test",
        "created_at": "2025-10-01T10:00:00Z",
        "path": "vault/creativity/assets/a.json"
    }), encoding="utf-8")

    # --- Parser ledger + chunk ---
    parser_dir = vault_dir / "parser"
    parser_dir.mkdir(parents=True, exist_ok=True)
    ledger = parser_dir / "ledger.jsonl"
    
    # Append to ledger (don't overwrite existing entries)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "sha": "psha1_unified_test",
            "source": "docs/dragon_notes.txt",
            "ts": "2025-10-01T09:00:00Z",
            "tags": ["notes","fantasy"]
        }) + "\n")
    
    (parser_dir / "psha1_unified_test.txt").write_text("The dragon sleeps beneath the ruins.", encoding="utf-8")

    # --- Truths file ---
    truth_dir = vault_dir / "truth"
    truth_dir.mkdir(parents=True, exist_ok=True)
    truths_file = truth_dir / "truths.jsonl"
    
    # Append to truths file
    with truths_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "truth": "Dragons prefer caves.",
            "created_at": "2025-10-01T11:00:00Z",
            "prov": [{"sha":"psha1_unified_test","source":"docs/dragon_notes.txt","ts":"2025-10-01T09:00:00Z"}],
            "tags": ["lore","fantasy"]
        }) + "\n")

    try:
        # 1) Plain search (should hit all three planes)
        r = client.post("/engines/leviathan/search", json={"query": "dragon"})
        assert r.status_code == 200
        results = r.json()["results"]
        assert len(results) >= 3, f"Expected at least 3 results, got {len(results)}: {results}"
        
        planes = set(row["plane"] for row in results)
        assert {"creativity","parser","truth"} & planes, f"Expected at least one of creativity/parser/truth planes, got: {planes}"

        # 2) Tag filter that should still match (fantasy)
        r = client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["fantasy"]})
        assert r.status_code == 200
        data = r.json()["results"]
        assert len(data) > 0, "Should find results with fantasy tag"
        assert all("fantasy" in (row.get("tags") or []) for row in data if row.get("tags")), f"All results should have fantasy tag: {data}"

        # 3) Tag filter that should exclude results
        r = client.post("/engines/leviathan/search", json={"query": "dragon", "tags": ["sci-fi"]})
        assert r.status_code == 200
        assert r.json()["results"] == [], "Should find no results with sci-fi tag"
        
    finally:
        # Cleanup
        (creat_dir / "test_unified_a.json").unlink(missing_ok=True)
        (parser_dir / "psha1_unified_test.txt").unlink(missing_ok=True)
        
        # Remove the test entries from ledger and truths
        if ledger.exists():
            lines = ledger.read_text(encoding="utf-8").strip().split("\n")
            filtered = [l for l in lines if "psha1_unified_test" not in l]
            ledger.write_text("\n".join(filtered) + ("\n" if filtered else ""), encoding="utf-8")
        
        if truths_file.exists():
            lines = truths_file.read_text(encoding="utf-8").strip().split("\n")
            filtered = [l for l in lines if "psha1_unified_test" not in l]
            truths_file.write_text("\n".join(filtered) + ("\n" if filtered else ""), encoding="utf-8")
