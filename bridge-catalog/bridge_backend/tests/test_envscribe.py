#!/usr/bin/env python3
"""
Test suite for EnvScribe - Unified Environment Intelligence System
Version: 1.0 | Added in SR-AIbridge v1.9.6u

Tests:
1. EnvScribe engine imports and initialization
2. Environment scanning functionality
3. Report generation and persistence
4. Emitter functionality (copy blocks and documentation)
5. CLI tool availability
6. API routes
"""

import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_envscribe_import():
    """Test that EnvScribe engine can be imported"""
    print("🧪 Test: EnvScribe engine import...")
    try:
        from bridge_backend.engines.envscribe.core import EnvScribeEngine
        print("   ✅ EnvScribe engine imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_envscribe_models():
    """Test that EnvScribe models can be imported"""
    print("🧪 Test: EnvScribe models import...")
    try:
        from bridge_backend.engines.envscribe.models import (
            EnvVariable, WebhookDefinition, EnvScribeSummary, EnvScribeReport
        )
        
        # Test model instantiation
        var = EnvVariable(
            name="TEST_VAR",
            scope=["Render"],
            var_type="String",
            description="Test variable"
        )
        assert var.name == "TEST_VAR"
        
        print("   ✅ EnvScribe models imported and instantiated successfully")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def test_envscribe_emitters():
    """Test that EnvScribe emitters can be imported"""
    print("🧪 Test: EnvScribe emitters import...")
    try:
        from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter
        emitter = EnvScribeEmitter()
        assert emitter is not None
        print("   ✅ EnvScribe emitters imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_envscribe_routes():
    """Test that EnvScribe routes can be imported"""
    print("🧪 Test: EnvScribe routes import...")
    try:
        from bridge_backend.engines.envscribe.routes import router
        assert router is not None
        print("   ✅ EnvScribe routes imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_envscribectl_import():
    """Test that envscribectl CLI can be imported"""
    print("🧪 Test: envscribectl import...")
    try:
        from bridge_backend.cli import envscribectl
        print("   ✅ envscribectl imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False


def test_envscribectl_help():
    """Test that envscribectl CLI help works"""
    print("🧪 Test: envscribectl help command...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bridge_backend.cli.envscribectl", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "EnvScribe" in result.stdout:
            print("   ✅ Help command works")
            return True
        else:
            print(f"   ❌ Help command failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def test_envscribe_commands():
    """Test that envscribe CLI commands are available"""
    print("🧪 Test: envscribe subcommands...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bridge_backend.cli.envscribectl", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            required = ["scan", "emit", "audit", "copy", "report"]
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


def test_documentation_exists():
    """Test that documentation files exist"""
    print("🧪 Test: Documentation files...")
    root = Path(__file__).resolve().parents[2]
    
    required_docs = [
        root / "docs" / "SCRIBE_README.md",
    ]
    
    missing = []
    for doc in required_docs:
        if not doc.exists():
            missing.append(doc.name)
    
    if not missing:
        print(f"   ✅ All documentation files present")
        return True
    else:
        print(f"   ❌ Missing documentation: {', '.join(missing)}")
        return False


def test_engine_initialization():
    """Test that EnvScribe engine can be initialized"""
    print("🧪 Test: Engine initialization...")
    try:
        from bridge_backend.engines.envscribe.core import EnvScribeEngine
        engine = EnvScribeEngine()
        
        # Verify directories exist
        assert engine.repo_root.exists()
        assert engine.report_path.parent.exists()
        
        # Verify known variables are loaded
        assert len(engine.known_variables) > 0
        
        print(f"   ✅ Engine initialized with {len(engine.known_variables)} known variables")
        return True
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False


def test_copy_block_generation():
    """Test that copy blocks can be generated"""
    print("🧪 Test: Copy block generation...")
    try:
        from bridge_backend.engines.envscribe.core import EnvScribeEngine
        from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter
        from bridge_backend.engines.envscribe.models import EnvScribeReport, EnvScribeSummary, EnvVariable
        
        # Create a sample report
        summary = EnvScribeSummary(total_keys=3, verified=3)
        variables = [
            EnvVariable(name="VAR1", scope=["Render"], var_type="String", default="value1"),
            EnvVariable(name="VAR2", scope=["Netlify"], var_type="String", default="value2"),
            EnvVariable(name="VAR3", scope=["GitHub"], var_type="Secret"),
        ]
        report = EnvScribeReport(summary=summary, variables=variables)
        
        # Generate copy blocks
        emitter = EnvScribeEmitter()
        blocks = emitter.generate_copy_blocks(report)
        
        # Verify blocks were generated
        assert "render" in blocks
        assert "netlify" in blocks
        assert "github_vars" in blocks
        assert "github_secrets" in blocks
        
        # Verify content
        assert "VAR1" in blocks["render"]
        assert "VAR2" in blocks["netlify"]
        assert "VAR3" in blocks["github_secrets"]
        
        print("   ✅ Copy blocks generated successfully")
        return True
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False


def run_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("EnvScribe - Unified Environment Intelligence - Test Suite v1.0")
    print("=" * 60)
    print()
    
    tests = [
        ("EnvScribe Import", test_envscribe_import),
        ("EnvScribe Models", test_envscribe_models),
        ("EnvScribe Emitters", test_envscribe_emitters),
        ("EnvScribe Routes", test_envscribe_routes),
        ("envscribectl Import", test_envscribectl_import),
        ("envscribectl Help", test_envscribectl_help),
        ("EnvScribe Commands", test_envscribe_commands),
        ("Documentation Files", test_documentation_exists),
        ("Engine Initialization", test_engine_initialization),
        ("Copy Block Generation", test_copy_block_generation),
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
    
    return passed == total


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
