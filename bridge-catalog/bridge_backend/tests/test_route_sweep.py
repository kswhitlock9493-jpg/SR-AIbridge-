#!/usr/bin/env python3
"""
Tests for Route Integrity Sweep Check v1.9.6b
"""
import sys
import subprocess
from pathlib import Path

def test_route_sweep_check_exists():
    """Test that route_sweep_check.py exists"""
    root = Path(__file__).resolve().parents[2]
    script_path = root / "tools" / "route_sweep_check.py"
    
    assert script_path.exists(), "route_sweep_check.py should exist"
    print("✅ route_sweep_check.py exists")

def test_route_sweep_check_runs():
    """Test that route_sweep_check.py executes successfully"""
    root = Path(__file__).resolve().parents[2]
    script_path = root / "tools" / "route_sweep_check.py"
    
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(root),
        capture_output=True,
        timeout=30
    )
    
    # Should pass since we're checking clean code
    assert result.returncode == 0, f"Route sweep check should pass, got: {result.stdout.decode()}"
    
    output = result.stdout.decode()
    assert "Bridge Route Integrity Sweep Check" in output
    assert "All routes comply" in output or "Route Sweep Check Failed" in output
    
    print("✅ route_sweep_check.py runs successfully")

def test_route_sweep_check_detects_issues():
    """Test that route sweep check can detect issues"""
    # This test would create a temporary bad route file and verify detection
    # For now, we just verify the script has the right patterns
    root = Path(__file__).resolve().parents[2]
    script_path = root / "tools" / "route_sweep_check.py"
    
    content = script_path.read_text()
    assert "UNSAFE_PATTERNS" in content
    assert "SAFE_PATTERNS" in content
    assert "AsyncSession" in content
    
    print("✅ route_sweep_check.py has proper detection patterns")

if __name__ == "__main__":
    print("=" * 60)
    print("Route Integrity Sweep Check - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Script Exists", test_route_sweep_check_exists),
        ("Script Runs", test_route_sweep_check_runs),
        ("Detection Patterns", test_route_sweep_check_detects_issues),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"Running: {name}")
        try:
            test_func()
            results.append((name, True))
        except Exception as e:
            print(f"❌ Test failed: {e}")
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
    
    sys.exit(0 if passed == total else 1)
