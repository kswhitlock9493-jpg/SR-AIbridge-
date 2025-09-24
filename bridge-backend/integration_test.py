#!/usr/bin/env python3
"""
Integration test script for SR-AIbridge backend
Tests Guardian endpoints and CORS functionality
"""

import asyncio
import aiohttp
import json
from datetime import datetime

API_BASE = "http://localhost:8000"

async def test_cors_integration():
    """Test CORS configuration with various origins"""
    print("🌐 Testing CORS Configuration...")
    
    test_origins = [
        "https://bridge.netlify.app",
        "https://sr-aibridge.netlify.app", 
        "https://test.netlify.app",
        "https://localhost:3000"
    ]
    
    async with aiohttp.ClientSession() as session:
        for origin in test_origins:
            headers = {"Origin": origin}
            try:
                async with session.get(f"{API_BASE}/", headers=headers) as resp:
                    cors_header = resp.headers.get('Access-Control-Allow-Origin')
                    print(f"  ✅ Origin: {origin} -> CORS: {cors_header}")
            except Exception as e:
                print(f"  ❌ Origin: {origin} -> Error: {e}")

async def test_guardian_endpoints():
    """Test all Guardian endpoints for functionality"""
    print("\n🛡️ Testing Guardian Endpoints...")
    
    async with aiohttp.ClientSession() as session:
        # Test status endpoint
        try:
            async with session.get(f"{API_BASE}/guardian/status") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  ✅ /guardian/status -> Status: {data.get('status')}, Active: {data.get('active')}")
                else:
                    print(f"  ❌ /guardian/status -> Status: {resp.status}")
        except Exception as e:
            print(f"  ❌ /guardian/status -> Error: {e}")
        
        # Test selftest endpoint
        try:
            async with session.post(f"{API_BASE}/guardian/selftest") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  ✅ /guardian/selftest -> Success: {data.get('success')}, Status: {data.get('status')}")
                else:
                    print(f"  ❌ /guardian/selftest -> Status: {resp.status}")
        except Exception as e:
            print(f"  ❌ /guardian/selftest -> Error: {e}")
        
        # Test activate endpoint
        try:
            async with session.post(f"{API_BASE}/guardian/activate") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  ✅ /guardian/activate -> Success: {data.get('success')}, Active: {data.get('active')}")
                else:
                    print(f"  ❌ /guardian/activate -> Status: {resp.status}")
        except Exception as e:
            print(f"  ❌ /guardian/activate -> Error: {e}")

async def test_connectivity():
    """Test basic backend connectivity"""
    print("\n📊 Testing Backend Connectivity...")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{API_BASE}/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"  ✅ Backend online -> Version: {data.get('version')}")
                    print(f"  ✅ Guardian endpoint available: {'/guardian/status' in str(data.get('endpoints', {}))}")
                else:
                    print(f"  ❌ Backend status: {resp.status}")
        except Exception as e:
            print(f"  ❌ Backend connection error: {e}")

async def main():
    """Run all integration tests"""
    print(f"🚀 SR-AIbridge Integration Test - {datetime.now().isoformat()}")
    print("=" * 60)
    
    await test_connectivity()
    await test_cors_integration()
    await test_guardian_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Integration test complete!")
    print("\nNext steps:")
    print("1. Frontend should connect to backend without CORS errors")
    print("2. Guardian Banner should show PASS status instead of Unknown")
    print("3. Backend logs available at startup show Guardian activation")

if __name__ == "__main__":
    asyncio.run(main())