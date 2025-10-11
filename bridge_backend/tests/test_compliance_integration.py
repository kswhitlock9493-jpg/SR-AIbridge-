"""
Tests for Autonomy Engine with Compliance Validation
Tests integration of copyright, license, and LOC tracking
"""
import sys
import json
from pathlib import Path

# Setup path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_core.engines.autonomy.service import AutonomyEngine
from bridge_core.engines.autonomy.compliance_validator import ComplianceValidator


def test_autonomy_engine_with_compliance():
    """Test that AutonomyEngine creates tasks with compliance validation"""
    engine = AutonomyEngine(enable_compliance=True)
    
    task = engine.create_task(
        project="test_project",
        captain="TestCaptain",
        objective="test_compliance_integration",
        permissions={"read": ["test"]},
        mode="screen",
        validate_compliance=True
    )
    
    assert task is not None
    assert task.id is not None
    assert task.compliance_validation is not None
    
    # Check compliance validation structure
    validation = task.compliance_validation
    assert "timestamp" in validation
    assert "compliance_state" in validation
    
    print("✅ test_autonomy_engine_with_compliance passed")


def test_compliance_validator_basic():
    """Test ComplianceValidator basic functionality"""
    validator = ComplianceValidator()
    
    # Create a test validation
    result = validator.validate_task_compliance(
        task_id="test-task-123",
        project=".",
        files=[]
    )
    
    assert result is not None
    assert "task_id" in result
    assert result["task_id"] == "test-task-123"
    assert "timestamp" in result
    assert "license_scan" in result
    assert "copyright_check" in result
    assert "loc_metrics" in result
    assert "compliance_state" in result
    
    print("✅ test_compliance_validator_basic passed")


def test_compliance_state_evaluation():
    """Test compliance state evaluation logic"""
    validator = ComplianceValidator()
    
    # Test compliant state
    license_result = {"compliant": True, "violations": []}
    copyright_result = {"original": True, "suspicious_matches": [], "flagged_matches": []}
    
    state = validator._evaluate_compliance(license_result, copyright_result)
    assert state["state"] == "compliant"
    assert state["safe_to_proceed"] is True
    
    # Test flagged state
    copyright_result["flagged_matches"] = [{"file": "test.py", "confidence": 0.7}]
    state = validator._evaluate_compliance(license_result, copyright_result)
    assert state["state"] == "flagged"
    assert state["safe_to_proceed"] is True
    
    # Test blocked state (license violation)
    license_result["compliant"] = False
    license_result["violations"] = [{"file": "bad.py", "license": "GPL-3.0"}]
    state = validator._evaluate_compliance(license_result, copyright_result)
    assert state["state"] == "blocked"
    assert state["safe_to_proceed"] is False
    
    print("✅ test_compliance_state_evaluation passed")


def test_loc_counting():
    """Test LOC counting functionality"""
    validator = ComplianceValidator()
    
    # Create a test file
    test_file = Path("test_temp_file.py")
    test_content = "# Test file\nprint('hello')\nprint('world')\n"
    test_file.write_text(test_content)
    
    try:
        result = validator._count_loc(Path("."), [str(test_file)])
        
        assert "total_lines" in result
        assert result["total_lines"] == 3
        assert "files_counted" in result
        assert result["files_counted"] == 1
        assert "by_extension" in result
        assert ".py" in result["by_extension"]
        
        print("✅ test_loc_counting passed")
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_autonomy_without_compliance():
    """Test that AutonomyEngine works without compliance validation"""
    engine = AutonomyEngine(enable_compliance=False)
    
    task = engine.create_task(
        project="test_project",
        captain="TestCaptain",
        objective="test_without_compliance",
        permissions={"read": ["test"]},
        mode="screen"
    )
    
    assert task is not None
    assert task.id is not None
    # Compliance validation should be None when disabled
    assert task.compliance_validation is None
    
    print("✅ test_autonomy_without_compliance passed")


def test_update_task_loc():
    """Test updating LOC metrics for a task"""
    engine = AutonomyEngine(enable_compliance=False)
    
    task = engine.create_task(
        project="test_project",
        captain="TestCaptain",
        objective="test_loc_update",
        permissions={"read": ["test"]},
        mode="screen"
    )
    
    # Update LOC metrics
    loc_metrics = {
        "total_lines": 500,
        "files_counted": 10,
        "by_extension": {".py": 400, ".js": 100}
    }
    
    updated_task = engine.update_task_loc(task.id, loc_metrics)
    
    assert updated_task is not None
    assert updated_task.compliance_validation is not None
    assert "loc_metrics" in updated_task.compliance_validation
    assert updated_task.compliance_validation["loc_metrics"]["total_lines"] == 500
    assert "loc_updated_at" in updated_task.compliance_validation
    
    print("✅ test_update_task_loc passed")


def test_get_compliance_validation():
    """Test retrieving compliance validation"""
    engine = AutonomyEngine(enable_compliance=True)
    
    task = engine.create_task(
        project="test_project",
        captain="TestCaptain",
        objective="test_get_validation",
        permissions={"read": ["test"]},
        mode="screen",
        validate_compliance=True
    )
    
    # Get compliance validation
    validation = engine.get_compliance_validation(task.id)
    
    assert validation is not None
    assert "compliance_state" in validation
    
    print("✅ test_get_compliance_validation passed")


def test_license_scanning():
    """Test license scanning functionality"""
    validator = ComplianceValidator()
    
    # Create test files with different licenses
    test_mit = Path("test_mit.py")
    test_mit.write_text("# SPDX-License-Identifier: MIT\nprint('MIT licensed')")
    
    test_gpl = Path("test_gpl.py")
    test_gpl.write_text("# GNU General Public License, version 3\nprint('GPL licensed')")
    
    try:
        result = validator._scan_licenses(Path("."), [str(test_mit), str(test_gpl)])
        
        assert "compliant" in result
        assert "licenses" in result
        assert "violations" in result
        
        # GPL should be in violations (blocked license)
        assert len(result["violations"]) > 0
        assert any("GPL" in v.get("license", "") for v in result["violations"])
        
        print("✅ test_license_scanning passed")
    finally:
        # Cleanup
        if test_mit.exists():
            test_mit.unlink()
        if test_gpl.exists():
            test_gpl.unlink()


def test_task_persistence():
    """Test that tasks with compliance are persisted correctly"""
    engine = AutonomyEngine(enable_compliance=True)
    
    task = engine.create_task(
        project="test_project",
        captain="TestCaptain",
        objective="test_persistence",
        permissions={"read": ["test"]},
        mode="screen",
        validate_compliance=True
    )
    
    # Check that task was sealed (saved to disk)
    seal_path = task.seal_path()
    assert seal_path.exists()
    
    # Read and verify
    saved_data = json.loads(seal_path.read_text())
    assert saved_data["id"] == task.id
    assert saved_data["project"] == "test_project"
    assert "compliance_validation" in saved_data
    
    print("✅ test_task_persistence passed")


def run_all_tests():
    """Run all tests"""
    print("🧪 Running Compliance Integration Tests...\n")
    
    tests = [
        test_autonomy_engine_with_compliance,
        test_compliance_validator_basic,
        test_compliance_state_evaluation,
        test_loc_counting,
        test_autonomy_without_compliance,
        test_update_task_loc,
        test_get_compliance_validation,
        test_license_scanning,
        test_task_persistence
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Tests Passed: {passed}/{len(tests)}")
    print(f"Tests Failed: {failed}/{len(tests)}")
    print(f"{'='*60}\n")
    
    if failed == 0:
        print("🎉 All Compliance Integration Tests Passed!")
        return 0
    else:
        print(f"⚠️  {failed} tests failed")
        return 1


if __name__ == "__main__":
    exit(run_all_tests())
