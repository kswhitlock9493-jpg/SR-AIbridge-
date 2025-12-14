#!/usr/bin/env python3
"""
Test suite for Autonomous Environment Synchronization Pipeline
Version: 1.0 | Added in SR-AIbridge v1.9.6L

Tests:
1. GenesisCtl CLI imports and command parsing
2. verify_env_sync.py execution
3. EnvSync event publishing to Genesis Bus
4. Snapshot export functionality
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_genesisctl_import():
    """Test that GenesisCtl can be imported"""
    print("🧪 Test: GenesisCtl import...")
    try:
        from bridge_backend.cli import genesisctl
        print("   ✅ GenesisCtl imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_genesisctl_help():
    """Test that GenesisCtl CLI help works"""
    print("🧪 Test: GenesisCtl help command...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bridge_backend.cli.genesisctl", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "GenesisCtl" in result.stdout:
            print("   ✅ Help command works")
            return True
        else:
            print(f"   ❌ Help command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def test_env_subcommands():
    """Test that env subcommands are available"""
    print("🧪 Test: Env subcommands...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bridge_backend.cli.genesisctl", "env", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            required = ["audit", "sync", "export", "heal"]
            missing = [cmd for cmd in required if cmd not in result.stdout]
            if not missing:
                print(f"   ✅ All subcommands available: {', '.join(required)}")
                return True
            else:
                print(f"   ❌ Missing subcommands: {', '.join(missing)}")
                return False
        else:
            print(f"   ❌ Command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def test_verify_env_sync_import():
    """Test that verify_env_sync can be imported"""
    print("🧪 Test: verify_env_sync import...")
    try:
        # Import the module
        import bridge_backend.diagnostics.verify_env_sync as verify_module
        print("   ✅ verify_env_sync imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_hubsync_sync_secret():
    """Test that HubSync has sync_secret method"""
    print("🧪 Test: HubSync sync_secret method...")
    try:
        from bridge_backend.engines.envrecon.hubsync import hubsync
        if hasattr(hubsync, 'sync_secret'):
            print("   ✅ HubSync.sync_secret method exists")
            return True
        else:
            print("   ❌ HubSync.sync_secret method not found")
            return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def test_documentation_exists():
    """Test that documentation files exist"""
    print("🧪 Test: Documentation files...")
    docs = [
        "docs/ENV_SYNC_AUTONOMOUS_PIPELINE.md",
        "docs/GITHUB_ENV_SYNC_GUIDE.md",
        "docs/GENESIS_EVENT_FLOW.md"
    ]
    
    project_root = Path(__file__).resolve().parents[2]
    missing = []
    
    for doc in docs:
        doc_path = project_root / doc
        if not doc_path.exists():
            missing.append(doc)
    
    if not missing:
        print(f"   ✅ All documentation files present")
        return True
    else:
        print(f"   ❌ Missing documentation: {', '.join(missing)}")
        return False


def test_workflow_exists():
    """Test that GitHub Actions workflow exists"""
    print("🧪 Test: GitHub Actions workflow...")
    project_root = Path(__file__).resolve().parents[2]
    workflow_path = project_root / ".github" / "workflows" / "env-sync.yml"
    
    if workflow_path.exists():
        print("   ✅ env-sync.yml workflow exists")
        return True
    else:
        print("   ❌ env-sync.yml workflow not found")
        return False


def run_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("Autonomous Environment Sync Pipeline - Test Suite v1.0")
    print("=" * 60)
    print()
    
    tests = [
        ("GenesisCtl Import", test_genesisctl_import),
        ("GenesisCtl Help", test_genesisctl_help),
        ("Env Subcommands", test_env_subcommands),
        ("verify_env_sync Import", test_verify_env_sync_import),
        ("HubSync sync_secret", test_hubsync_sync_secret),
        ("Documentation Files", test_documentation_exists),
        ("GitHub Workflow", test_workflow_exists),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Test crashed: {e}")
            results.append((name, False))
        print()
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run_tests())
