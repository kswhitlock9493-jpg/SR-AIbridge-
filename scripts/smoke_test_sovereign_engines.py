#!/usr/bin/env python3
"""
Sovereign Engines API Smoke Test

Quick smoke test to verify API endpoints are working.
"""

import asyncio
import httpx
import io


async def test_sovereign_engines_api():
    """Test Sovereign Engines API endpoints"""
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        print("🧪 Testing Sovereign Engines API...")
        
        # Test 1: Health endpoint
        print("\n1️⃣ Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/bridge/engines/health")
            assert response.status_code == 200
            data = response.json()
            print(f"   ✅ Health: {data}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
        
        # Test 2: Status endpoint
        print("\n2️⃣ Testing status endpoint...")
        try:
            response = await client.get(f"{base_url}/bridge/engines/status")
            assert response.status_code == 200
            data = response.json()
            print(f"   ✅ Status: {data['status']}")
            print(f"   📊 Engines: {', '.join(data['engines'].keys())}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
        
        # Test 3: Compliance check
        print("\n3️⃣ Testing compliance check...")
        try:
            response = await client.get(
                f"{base_url}/bridge/engines/compliance/check",
                params={"operation": "test_operation"}
            )
            assert response.status_code == 200
            data = response.json()
            print(f"   ✅ Compliance: {data['compliant']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
        
        # Test 4: Diff analysis
        print("\n4️⃣ Testing diff analysis...")
        try:
            test_diff = """diff --git a/test.py b/test.py
+# Test change
"""
            files = {"diff_file": ("test.diff", io.BytesIO(test_diff.encode()), "text/plain")}
            
            response = await client.post(
                f"{base_url}/bridge/engines/microscribe/analyze",
                files=files
            )
            assert response.status_code == 200
            data = response.json()
            print(f"   ✅ Diff Analysis: {data['files_changed']} file(s), {data['lines_added']} line(s) added")
            print(f"   🔒 Risk Level: {data['risk_level']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
        
        # Test 5: Log analysis
        print("\n5️⃣ Testing log analysis...")
        try:
            test_logs = """2025-11-05 12:00:00 INFO Application started
2025-11-05 12:01:00 INFO Processing request
"""
            files = {"log_file": ("test.log", io.BytesIO(test_logs.encode()), "text/plain")}
            
            response = await client.post(
                f"{base_url}/bridge/engines/micrologician/analyze",
                files=files
            )
            assert response.status_code == 200
            data = response.json()
            print(f"   ✅ Log Analysis: {data['total_lines']} lines, {data['mode']} mode")
            print(f"   📊 Confidence: {data['confidence']}")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            return False
        
        print("\n✅ All API smoke tests passed!")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 SOVEREIGN ENGINES API SMOKE TEST")
    print("=" * 60)
    print("\n⚠️ Make sure the server is running:")
    print("   uvicorn bridge_backend.main:app --reload\n")
    
    try:
        result = asyncio.run(test_sovereign_engines_api())
        exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        print("\n💡 Is the server running?")
        exit(1)
