"""
Test Deep-Seek Federation Triage script
"""

import pytest
import json
import pathlib
import subprocess
import os


def test_federation_map_exists():
    """Test that federation_map.json exists and is valid"""
    root = pathlib.Path(__file__).resolve().parents[2]
    fedmap_path = root / "bridge_backend" / "federation_map.json"
    
    assert fedmap_path.exists(), "federation_map.json should exist"
    
    fedmap = json.loads(fedmap_path.read_text())
    assert "diagnostics_federation" in fedmap
    assert "bridge_auto_deploy" in fedmap
    assert "triage_federation" in fedmap
    
    # Check structure
    for name, conf in fedmap.items():
        assert "endpoint" in conf
        assert "heartbeat" in conf
        assert "schema_version" in conf
        assert "schema_probe" in conf
        assert "patch_targets" in conf
        assert "backend_env" in conf["patch_targets"]
        assert "cache_files" in conf["patch_targets"]


def test_net_script_exists():
    """Test that _net.py exists and has valid syntax"""
    root = pathlib.Path(__file__).resolve().parents[2]
    net_path = root / ".github" / "scripts" / "_net.py"
    
    assert net_path.exists(), "_net.py should exist"
    
    # Check syntax by compiling
    code = net_path.read_text()
    compile(code, str(net_path), 'exec')
    
    # Check for expected functions
    assert "def dns_warmup" in code
    assert "def http" in code


def test_deep_seek_script_exists():
    """Test that deep_seek_triage.py exists and has valid syntax"""
    root = pathlib.Path(__file__).resolve().parents[2]
    script_path = root / ".github" / "scripts" / "deep_seek_triage.py"
    
    assert script_path.exists(), "deep_seek_triage.py should exist"
    
    # Check syntax by compiling
    code = script_path.read_text()
    compile(code, str(script_path), 'exec')
    
    # Check for expected functions
    assert "def probe_schema" in code
    assert "def touch_cache" in code
    assert "def deepseek_and_repair" in code
    assert "def main" in code


def test_workflow_exists():
    """Test that federation_deepseek.yml workflow exists"""
    root = pathlib.Path(__file__).resolve().parents[2]
    workflow_path = root / ".github" / "workflows" / "federation_deepseek.yml"
    
    assert workflow_path.exists(), "federation_deepseek.yml should exist"
    
    # Parse YAML to ensure it's valid
    import yaml
    workflow = yaml.safe_load(workflow_path.read_text())
    
    assert workflow["name"] == "Federation Deep-Seek"
    assert "jobs" in workflow
    assert "deepseek" in workflow["jobs"]


def test_documentation_exists():
    """Test that FEDERATION_TRIAGE_ENGINE.md exists"""
    root = pathlib.Path(__file__).resolve().parents[2]
    doc_path = root / "docs" / "FEDERATION_TRIAGE_ENGINE.md"
    
    assert doc_path.exists(), "FEDERATION_TRIAGE_ENGINE.md should exist"
    
    content = doc_path.read_text()
    
    # Check for key sections
    assert "Federation Triage Engine" in content
    assert "Deep-Seek" in content
    assert "Auto-Repair" in content
    assert "Signal Taxonomy" in content


def test_deep_seek_script_runs():
    """Test that deep_seek_triage.py can run (even if it fails due to network)"""
    root = pathlib.Path(__file__).resolve().parents[2]
    script_path = root / ".github" / "scripts" / "deep_seek_triage.py"
    
    # Run with very short timeouts to ensure it doesn't hang
    env = os.environ.copy()
    env["DEEPSEEK_TIMEOUT"] = "1"
    env["DEEPSEEK_MAX_RETRIES"] = "1"
    
    result = subprocess.run(
        ["python3", str(script_path)],
        cwd=str(root),
        env=env,
        capture_output=True,
        timeout=30
    )
    
    # Script should exit (with code 0, 1, or 2)
    assert result.returncode in [0, 1, 2]
    
    # Check that report was generated
    report_path = root / "bridge_backend" / "diagnostics" / "federation_repair_report.json"
    assert report_path.exists(), "Report should be generated"
    
    # Validate report structure
    report = json.loads(report_path.read_text())
    assert "generated_at" in report
    assert "health" in report
    assert "details" in report
    
    # Clean up
    report_path.unlink()

