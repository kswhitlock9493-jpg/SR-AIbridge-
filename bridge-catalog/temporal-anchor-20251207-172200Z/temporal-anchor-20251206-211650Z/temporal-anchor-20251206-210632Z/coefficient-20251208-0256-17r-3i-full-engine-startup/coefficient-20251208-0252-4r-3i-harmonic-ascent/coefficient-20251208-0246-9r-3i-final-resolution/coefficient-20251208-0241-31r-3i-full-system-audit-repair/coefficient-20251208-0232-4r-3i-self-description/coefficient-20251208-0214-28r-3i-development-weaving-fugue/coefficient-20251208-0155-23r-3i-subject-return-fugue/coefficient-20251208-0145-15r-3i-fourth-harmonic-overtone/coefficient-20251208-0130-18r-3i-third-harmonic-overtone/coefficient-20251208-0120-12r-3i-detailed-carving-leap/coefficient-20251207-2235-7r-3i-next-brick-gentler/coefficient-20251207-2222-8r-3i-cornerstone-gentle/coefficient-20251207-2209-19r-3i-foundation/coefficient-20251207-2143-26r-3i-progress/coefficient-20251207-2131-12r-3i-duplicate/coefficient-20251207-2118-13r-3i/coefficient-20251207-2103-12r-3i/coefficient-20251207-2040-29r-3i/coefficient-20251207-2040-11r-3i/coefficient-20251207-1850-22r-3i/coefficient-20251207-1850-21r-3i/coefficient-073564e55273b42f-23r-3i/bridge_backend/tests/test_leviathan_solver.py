from fastapi.testclient import TestClient
from pathlib import Path
import json, shutil

# Import the app
try:
    from bridge_backend.main import app
except ImportError:
    from main import app

client = TestClient(app)

def test_leviathan_solve_grounding_and_proof(tmp_path, monkeypatch):
    # Prep temp vault dirs
    vault = tmp_path / "vault"
    (vault / "parser").mkdir(parents=True)
    (vault / "truth").mkdir(parents=True)

    # Monkeypatch paths used by solver & truth utils
    import bridge_core.engines.leviathan.solver as solver_module
    monkeypatch.setattr(solver_module, "SOLVER_DIR", vault / "leviathan" / "solver", raising=False)
    monkeypatch.setattr(solver_module, "TRUTH_DIR", vault / "truth", raising=False)
    monkeypatch.setattr(solver_module, "PARSER_LEDGER", vault / "parser" / "ledger.jsonl", raising=False)

    # Also patch load_chunk_text to read from our temp parser chunks
    chunks_dir = vault / "parser"
    def _fake_load_chunk_text(sha: str):
        f = chunks_dir / f"{sha}.txt"
        return f.read_text(encoding="utf-8") if f.exists() else None
    monkeypatch.setattr(solver_module, "load_chunk_text", _fake_load_chunk_text, raising=False)

    # Seed parser ledger + chunks
    ledger = [
        {"sha": "abc123", "source": "docs/nova.txt", "ts": "2025-09-20T00:00:00Z"},
        {"sha": "def456", "source": "notes/4d.txt",  "ts": "2025-09-21T00:00:00Z"},
    ]
    (vault / "parser" / "ledger.jsonl").write_text("\n".join(json.dumps(x) for x in ledger), encoding="utf-8")
    (vault / "parser" / "abc123.txt").write_text("Project Nova uses 4D projections and hyperslicing.", encoding="utf-8")
    (vault / "parser" / "def456.txt").write_text("Hyperslicing requires rotation in R4 and projection operators.", encoding="utf-8")

    # Seed a truth
    truths = [
        {"canon": "Nova phase two explores 4D rendering demos.", "sources": [{"sha":"abc123","source":"docs/nova.txt"}]}
    ]
    (vault / "truth" / "truths.jsonl").write_text("\n".join(json.dumps(x) for x in truths), encoding="utf-8")

    # Call endpoint (no dispatch to keep test simple)
    r = client.post("/engines/leviathan/solve", json={
        "q": "What would it take to build a 4D projection demo for Nova?",
        "captain": "Kyle", "project": "nova", "dispatch": False
    })
    assert r.status_code == 200
    body = r.json()
    assert "summary" in body and "plan" in body and "requirements" in body
    assert body["citations"]["truths"] or body["citations"]["parser_hits"]

    # Proof dropped
    proof_dir = vault / "leviathan" / "solver"
    proofs = list(proof_dir.glob("proof_*.json"))
    assert len(proofs) >= 1
    p = json.loads(proofs[0].read_text(encoding="utf-8"))
    assert p.get("seal")


def test_leviathan_solve_basic():
    """Test basic solve without grounding data"""
    r = client.post("/engines/leviathan/solve", json={
        "q": "Build a quantum navigation system",
        "captain": "TestCaptain",
        "project": "test_project"
    })
    assert r.status_code == 200
    body = r.json()
    
    # Verify structure
    assert "summary" in body
    assert "plan" in body
    assert "requirements" in body
    assert "citations" in body
    assert "tasks" in body
    assert "proof" in body
    
    # Verify plan has phases
    assert len(body["plan"]) > 0
    for phase in body["plan"]:
        assert "phase" in phase
        assert "name" in phase
        assert "deliverables" in phase
        assert "estimate_weeks" in phase
    
    # Verify requirements structure
    assert "math" in body["requirements"]
    assert "science" in body["requirements"]
    assert "software" in body["requirements"]
    assert "team" in body["requirements"]
    
    # Verify proof has seal
    assert body["proof"]["seal"]
    assert "engines_used" in body["proof"]


def test_leviathan_solve_with_modes():
    """Test solve with specific modes"""
    r = client.post("/engines/leviathan/solve", json={
        "q": "Design a visualization for 4D data",
        "modes": ["design", "research"]
    })
    assert r.status_code == 200
    body = r.json()
    
    # Should have intents matching modes
    assert body["proof"]["intents"] == ["design", "research"]


def test_leviathan_solve_short_query_fails():
    """Test that short queries are rejected"""
    r = client.post("/engines/leviathan/solve", json={
        "q": "abc"  # Too short
    })
    assert r.status_code == 422  # Validation error


def test_leviathan_solve_engines_adapter():
    """Test that engines adapter layer is working"""
    r = client.post("/engines/leviathan/solve", json={
        "q": "Build a 4D projection demo with quantum rendering and business plan"
    })
    assert r.status_code == 200
    body = r.json()
    
    # Check that proof shows engines were used
    assert "engines_used" in body["proof"]
    engines_used = body["proof"]["engines_used"]
    
    # At minimum, we should have used the stub adapters
    assert "math_science" in engines_used
    assert "creativity" in engines_used
    assert "business" in engines_used
