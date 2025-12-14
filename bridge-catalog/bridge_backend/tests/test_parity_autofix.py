#!/usr/bin/env python3
"""
Test suite for Bridge Parity Auto-Fix Engine v1.7.0
"""

import os
import sys
import json
import pathlib
import shutil

# Add parent directory to path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

def test_parity_autofix_import():
    """Test that parity_autofix.py can be imported"""
    try:
        from tools import parity_autofix
        print("✅ parity_autofix module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import parity_autofix: {e}")
        return False

def test_parity_report_exists():
    """Test that parity report exists"""
    report_path = pathlib.Path(__file__).resolve().parents[1] / "diagnostics/bridge_parity_report.json"
    if report_path.exists():
        print("✅ Bridge parity report exists")
        return True
    else:
        print("⚠️  Bridge parity report not found - run parity_engine.py first")
        return False

def test_autofix_report_schema():
    """Test that autofix report has correct schema"""
    report_path = pathlib.Path(__file__).resolve().parents[1] / "diagnostics/parity_autofix_report.json"
    
    if not report_path.exists():
        print("⚠️  Autofix report not found - run parity_autofix.py first")
        return False
    
    with open(report_path) as f:
        report = json.load(f)
    
    # Check required fields
    required_fields = ["summary", "auto_repaired", "manual_review", "frontend_stubs_created", "backend_stubs_documentation"]
    for field in required_fields:
        if field not in report:
            print(f"❌ Missing required field: {field}")
            return False
    
    # Check summary fields
    summary_fields = ["timestamp", "version", "backend_routes", "frontend_calls", "repaired_endpoints", "pending_manual_review", "status"]
    for field in summary_fields:
        if field not in report["summary"]:
            print(f"❌ Missing summary field: {field}")
            return False
    
    # Check version
    if report["summary"]["version"] != "v1.7.0":
        print(f"❌ Incorrect version: {report['summary']['version']}")
        return False
    
    print("✅ Autofix report schema is valid")
    print(f"   Status: {report['summary']['status']}")
    print(f"   Repaired: {report['summary']['repaired_endpoints']} endpoints")
    print(f"   Pending review: {report['summary']['pending_manual_review']} endpoints")
    return True

def test_frontend_stubs_generated():
    """Test that frontend stubs were generated"""
    auto_gen_dir = pathlib.Path(__file__).resolve().parents[2] / "bridge-frontend/src/api/auto_generated"
    
    if not auto_gen_dir.exists():
        print("❌ Auto-generated directory not found")
        return False
    
    # Check for index.js
    index_path = auto_gen_dir / "index.js"
    if not index_path.exists():
        print("❌ index.js not found in auto_generated directory")
        return False
    
    # Count generated files
    js_files = list(auto_gen_dir.glob("*.js"))
    if len(js_files) < 2:  # Should have at least index.js and one stub
        print(f"❌ Too few files generated: {len(js_files)}")
        return False
    
    print(f"✅ Frontend stubs generated: {len(js_files)} files")
    
    # Check critical routes
    critical_stubs = [
        "api_control_hooks_triage.js",
        "api_control_rollback.js"
    ]
    
    for stub in critical_stubs:
        stub_path = auto_gen_dir / stub
        if not stub_path.exists():
            print(f"⚠️  Critical stub not found: {stub}")
        else:
            print(f"   ✓ {stub}")
    
    return True

def test_stub_content():
    """Test that generated stubs have correct content"""
    auto_gen_dir = pathlib.Path(__file__).resolve().parents[2] / "bridge-frontend/src/api/auto_generated"
    
    # Check a critical stub
    stub_path = auto_gen_dir / "api_control_hooks_triage.js"
    if not stub_path.exists():
        print("⚠️  Critical stub not found for content test")
        return False
    
    with open(stub_path) as f:
        content = f.read()
    
    # Check for required elements
    required_elements = [
        "// AUTO-GEN-BRIDGE v1.7.0",
        "// TODO:",
        "import apiClient from",
        "export async function",
        "try {",
        "const url =",
        "await apiClient.",
        "catch (error) {"
    ]
    
    for element in required_elements:
        if element not in content:
            print(f"❌ Missing element in stub: {element}")
            return False
    
    print("✅ Stub content is valid")
    return True

def test_path_parameter_interpolation():
    """Test that path parameters are correctly interpolated"""
    auto_gen_dir = pathlib.Path(__file__).resolve().parents[2] / "bridge-frontend/src/api/auto_generated"
    
    # Check a stub with path parameter
    stub_path = auto_gen_dir / "engines_parser_chunk_sha.js"
    if not stub_path.exists():
        print("⚠️  Path parameter stub not found")
        return False
    
    with open(stub_path) as f:
        content = f.read()
    
    # Check that parameter is in function signature
    if "engines_parser_chunk_sha(sha)" not in content:
        print("❌ Path parameter not in function signature")
        return False
    
    # Check that parameter is interpolated in URL
    if "${sha}" not in content:
        print("❌ Path parameter not interpolated in URL")
        return False
    
    print("✅ Path parameter interpolation is correct")
    return True

def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("Bridge Parity Auto-Fix Engine - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Module Import", test_parity_autofix_import),
        ("Parity Report Exists", test_parity_report_exists),
        ("Autofix Report Schema", test_autofix_report_schema),
        ("Frontend Stubs Generated", test_frontend_stubs_generated),
        ("Stub Content Validation", test_stub_content),
        ("Path Parameter Interpolation", test_path_parameter_interpolation),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Running: {name}")
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
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
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
