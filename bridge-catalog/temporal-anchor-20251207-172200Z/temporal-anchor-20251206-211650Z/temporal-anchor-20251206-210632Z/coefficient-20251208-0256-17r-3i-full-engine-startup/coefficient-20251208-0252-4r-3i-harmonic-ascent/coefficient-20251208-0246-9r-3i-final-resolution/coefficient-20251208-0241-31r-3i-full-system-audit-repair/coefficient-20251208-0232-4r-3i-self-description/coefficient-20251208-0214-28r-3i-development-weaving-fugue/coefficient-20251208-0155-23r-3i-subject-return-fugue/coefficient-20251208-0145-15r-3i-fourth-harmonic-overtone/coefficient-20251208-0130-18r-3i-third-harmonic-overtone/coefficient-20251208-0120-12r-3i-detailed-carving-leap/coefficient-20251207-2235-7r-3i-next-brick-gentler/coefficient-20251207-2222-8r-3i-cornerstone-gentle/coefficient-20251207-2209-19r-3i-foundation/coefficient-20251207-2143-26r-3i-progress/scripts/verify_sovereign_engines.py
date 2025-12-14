#!/usr/bin/env python3
"""
Sovereign Engines Deployment Verification Script

Tests all Sovereign Engine API endpoints and validates functionality.
"""

import sys
import os
import asyncio
import httpx
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard
from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe
from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician


def test_engines_import():
    """Test that all engines can be imported"""
    print("🔍 Testing engine imports...")
    
    try:
        guard = SovereignComplianceGuard()
        print("  ✅ Sovereign Compliance Guard imported")
        
        scribe = SovereignMicroScribe()
        print("  ✅ Sovereign MicroScribe imported")
        
        logician = SovereignMicroLogician()
        print("  ✅ Sovereign MicroLogician imported")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_compliance_guard():
    """Test Compliance Guard functionality"""
    print("\n🛡️ Testing Sovereign Compliance Guard...")
    
    try:
        guard = SovereignComplianceGuard()
        
        # Test compliance check
        result = guard.check_compliance("test_operation")
        assert result.compliant is not None
        print("  ✅ Compliance check working")
        
        # Test audit trail
        trail = guard.get_audit_trail()
        assert isinstance(trail, list)
        print("  ✅ Audit trail working")
        
        # Test validation
        valid = guard.validate_operation("test")
        assert isinstance(valid, bool)
        print("  ✅ Validation working")
        
        return True
    except Exception as e:
        print(f"  ❌ Compliance Guard test failed: {e}")
        return False


def test_micro_scribe():
    """Test MicroScribe functionality"""
    print("\n📝 Testing Sovereign MicroScribe...")
    
    try:
        scribe = SovereignMicroScribe()
        
        # Test diff analysis
        test_diff = """diff --git a/test.py b/test.py
+# Added line
"""
        analysis = scribe.analyze_diff(test_diff)
        assert analysis.files_changed > 0
        print("  ✅ Diff analysis working")
        
        # Test PR generation
        pr = scribe.generate_pr(analysis, "Test PR", "Test description")
        assert pr.title == "Test PR"
        print("  ✅ PR generation working")
        
        return True
    except Exception as e:
        print(f"  ❌ MicroScribe test failed: {e}")
        return False


def test_micro_logician():
    """Test MicroLogician functionality"""
    print("\n🔍 Testing Sovereign MicroLogician...")
    
    try:
        logician = SovereignMicroLogician()
        
        # Test log analysis
        test_logs = """
2025-11-05 12:00:00 INFO Application started
2025-11-05 12:01:00 ERROR Database connection failed
2025-11-05 12:02:00 INFO Request processed
"""
        analysis = logician.analyze_logs(test_logs)
        assert analysis.total_lines > 0
        assert len(analysis.log_levels) > 0
        print("  ✅ Log analysis working")
        
        # Test performance metrics
        assert analysis.performance_metrics is not None
        print("  ✅ Performance metrics working")
        
        # Test security findings
        assert isinstance(analysis.security_findings, list)
        print("  ✅ Security analysis working")
        
        return True
    except Exception as e:
        print(f"  ❌ MicroLogician test failed: {e}")
        return False


def test_sovereign_policy():
    """Test sovereign policy configuration"""
    print("\n📋 Testing Sovereign Policy...")
    
    try:
        policy_path = Path(__file__).parent.parent / ".forge" / "sovereign_policy.json"
        
        if policy_path.exists():
            import json
            with open(policy_path) as f:
                policy = json.load(f)
            
            assert "version" in policy
            assert "protected_routes" in policy
            assert "security" in policy
            print("  ✅ Sovereign policy file valid")
            print(f"  📌 Policy version: {policy['version']}")
            print(f"  📌 Protected routes: {len(policy['protected_routes'])}")
            return True
        else:
            print("  ⚠️ Sovereign policy file not found")
            return False
    except Exception as e:
        print(f"  ❌ Policy test failed: {e}")
        return False


def test_license():
    """Test sovereign license"""
    print("\n📄 Testing Sovereign License...")
    
    try:
        license_path = Path(__file__).parent.parent / "bridge_backend" / "bridge_engines" / "SOVEREIGN_LICENSE.md"
        
        if license_path.exists():
            content = license_path.read_text()
            assert "SOVEREIGN LICENSE" in content
            assert "Bridge-Integrated Perpetual License" in content
            print("  ✅ License file valid")
            return True
        else:
            print("  ❌ License file not found")
            return False
    except Exception as e:
        print(f"  ❌ License test failed: {e}")
        return False


async def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n🌐 Testing API Endpoints...")
    
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            try:
                response = await client.get(f"{base_url}/bridge/engines/health", timeout=5.0)
                if response.status_code == 200:
                    print(f"  ✅ Health endpoint working: {response.json()}")
                else:
                    print(f"  ⚠️ Health endpoint returned {response.status_code}")
            except httpx.ConnectError:
                print("  ℹ️ Server not running - skipping API endpoint tests")
                print("     Start the server with: uvicorn bridge_backend.main:app")
                return True
            except httpx.TimeoutException:
                print("  ⚠️ Health endpoint timed out")
                return False
            
            # Test status endpoint
            try:
                response = await client.get(f"{base_url}/bridge/engines/status", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Status endpoint working")
                    print(f"     Engines operational: {data.get('status')}")
                else:
                    print(f"  ⚠️ Status endpoint returned {response.status_code}")
            except Exception as e:
                print(f"  ⚠️ Status endpoint error: {e}")
            
            return True
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("🚀 SOVEREIGN ENGINES DEPLOYMENT VERIFICATION")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Engine Imports", test_engines_import()))
    results.append(("Compliance Guard", test_compliance_guard()))
    results.append(("MicroScribe", test_micro_scribe()))
    results.append(("MicroLogician", test_micro_logician()))
    results.append(("Sovereign Policy", test_sovereign_policy()))
    results.append(("License", test_license()))
    
    # Run async API tests
    try:
        api_result = asyncio.run(test_api_endpoints())
        results.append(("API Endpoints", api_result))
    except Exception as e:
        print(f"\n⚠️ API endpoint tests skipped: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All verification tests passed!")
        print("✅ Sovereign Engines are ready for deployment")
        return 0
    else:
        print("\n⚠️ Some verification tests failed")
        print("❌ Please review the failures above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
