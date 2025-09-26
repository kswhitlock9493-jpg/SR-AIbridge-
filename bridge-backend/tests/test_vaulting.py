from pathlib import Path
import json
from bridge_core.protocols import vaulting

def test_seal_creates_files(tmp_path):
    # Redirect VAULT_DIR to a temp path to avoid polluting real vault dir
    vaulting.VAULT_DIR = tmp_path / "protocols"
    result = vaulting.seal("TestProto", status="invoked", details={"x": 1})
    assert result["protocol"] == "TestProto"
    p = vaulting.VAULT_DIR / "TestProto"
    assert (p / "lore_applied.txt").exists()
    assert (p / "seal.json").exists()
    data = json.loads((p / "seal.json").read_text())
    assert data["status"] == "invoked"