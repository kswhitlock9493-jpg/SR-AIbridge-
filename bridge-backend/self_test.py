#!/usr/bin/env python3
"""
SR-AIbridge Self-Test Script

Comprehensive testing script for the SR-AIbridge backend.
Tests all endpoints, services, and system components.
"""
import asyncio
import sys
import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any

class SRAIBridgeSelfTest:
    """Comprehensive self-test suite for SR-AIbridge"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.results = {
            "start_time": datetime.utcnow().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0
            }
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp"""
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_result(self, name: str, passed: bool, details: Dict = None, error: str = None):
        """Record test result"""
        result = {
            "name": name,
            "passed": passed,
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
            "error": error
        }
        self.results["tests"].append(result)
        self.results["summary"]["total"] += 1
        
        if passed:
            self.results["summary"]["passed"] += 1
            self.log(f"✅ {name}", "PASS")
        else:
            if error:
                self.results["summary"]["errors"] += 1
                self.log(f"❌ {name}: {error}", "ERROR")
            else:
                self.results["summary"]["failed"] += 1
                self.log(f"❌ {name}", "FAIL")
                
    async def test_health_endpoints(self):
        """Test health and status endpoints"""
        self.log("Testing health endpoints...")
        
        # Test /health
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("health_endpoint", True, {"status": data.get("status")})
            else:
                self.test_result("health_endpoint", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("health_endpoint", False, error=str(e))
            
        # Test /status
        try:
            response = requests.get(f"{self.base_url}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("status_endpoint", True, {
                    "agents": data.get("agents", {}),
                    "missions": data.get("missions", {})
                })
            else:
                self.test_result("status_endpoint", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("status_endpoint", False, error=str(e))
            
        # Test root endpoint
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("root_endpoint", True, {
                    "name": data.get("name"),
                    "version": data.get("version")
                })
            else:
                self.test_result("root_endpoint", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("root_endpoint", False, error=str(e))
            
    async def test_guardian_endpoints(self):
        """Test Guardian daemon endpoints"""
        self.log("Testing Guardian endpoints...")
        
        # Test guardian status
        try:
            response = requests.get(f"{self.base_url}/guardian/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("guardian_status", True, {
                    "active": data.get("active"),
                    "status": data.get("status")
                })
            else:
                self.test_result("guardian_status", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("guardian_status", False, error=str(e))
            
        # Test guardian selftest
        try:
            response = requests.post(f"{self.base_url}/guardian/selftest", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.test_result("guardian_selftest", True, {
                    "success": data.get("success"),
                    "message": data.get("message")
                })
            else:
                self.test_result("guardian_selftest", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("guardian_selftest", False, error=str(e))
            
        # Test guardian activate
        try:
            response = requests.post(f"{self.base_url}/guardian/activate", timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.test_result("guardian_activate", True, {
                    "success": data.get("success"),
                    "message": data.get("message")
                })
            else:
                self.test_result("guardian_activate", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("guardian_activate", False, error=str(e))
            
    async def test_agent_endpoints(self):
        """Test Agent management endpoints"""
        self.log("Testing Agent endpoints...")
        
        # Test list agents
        try:
            response = requests.get(f"{self.base_url}/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("list_agents", True, {"count": len(data)})
            else:
                self.test_result("list_agents", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("list_agents", False, error=str(e))
            
        # Test create agent
        try:
            agent_data = {
                "name": "TestAgent",
                "endpoint": "http://localhost:8001/test",
                "capabilities": ["test", "monitoring"]
            }
            response = requests.post(f"{self.base_url}/agents", json=agent_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                agent_id = data.get("id")
                self.test_result("create_agent", True, {"agent_id": agent_id})
                
                # Test delete agent
                if agent_id:
                    delete_response = requests.delete(f"{self.base_url}/agents/{agent_id}", timeout=10)
                    self.test_result("delete_agent", delete_response.status_code == 200)
            else:
                self.test_result("create_agent", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("create_agent", False, error=str(e))
            
    async def test_mission_endpoints(self):
        """Test Mission management endpoints"""
        self.log("Testing Mission endpoints...")
        
        # Test list missions
        try:
            response = requests.get(f"{self.base_url}/missions", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("list_missions", True, {"count": len(data)})
            else:
                self.test_result("list_missions", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("list_missions", False, error=str(e))
            
        # Test create mission
        try:
            mission_data = {
                "title": "Test Mission",
                "description": "Self-test mission",
                "status": "active",
                "priority": "high"
            }
            response = requests.post(f"{self.base_url}/missions", json=mission_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("create_mission", True, {"mission_id": data.get("id")})
            else:
                self.test_result("create_mission", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("create_mission", False, error=str(e))
            
        # Test tasks endpoints (aliases)
        try:
            response = requests.get(f"{self.base_url}/tasks", timeout=10)
            if response.status_code == 200:
                self.test_result("list_tasks", True)
            else:
                self.test_result("list_tasks", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("list_tasks", False, error=str(e))
            
    async def test_log_endpoints(self):
        """Test Vault/Doctrine log endpoints"""
        self.log("Testing Log endpoints...")
        
        # Test get vault logs
        try:
            response = requests.get(f"{self.base_url}/vault/logs", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("get_vault_logs", True, {"count": len(data)})
            else:
                self.test_result("get_vault_logs", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("get_vault_logs", False, error=str(e))
            
        # Test add vault log
        try:
            log_data = {
                "agent_name": "SelfTest",
                "action": "test_log",
                "details": "Self-test log entry",
                "log_level": "info"
            }
            response = requests.post(f"{self.base_url}/vault/logs", json=log_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("add_vault_log", True, {"log_id": data.get("id")})
            else:
                self.test_result("add_vault_log", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("add_vault_log", False, error=str(e))
            
        # Test doctrine endpoints (aliases)
        try:
            response = requests.get(f"{self.base_url}/doctrine", timeout=10)
            if response.status_code == 200:
                self.test_result("get_doctrine", True)
            else:
                self.test_result("get_doctrine", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("get_doctrine", False, error=str(e))
            
    async def test_websocket_endpoints(self):
        """Test WebSocket related endpoints"""
        self.log("Testing WebSocket endpoints...")
        
        # Test WebSocket stats (HTTP endpoint)
        try:
            response = requests.get(f"{self.base_url}/ws/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("websocket_stats", True, {
                    "current_connections": data.get("current_connections", 0)
                })
            else:
                self.test_result("websocket_stats", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("websocket_stats", False, error=str(e))
            
    async def test_utility_endpoints(self):
        """Test utility endpoints"""
        self.log("Testing utility endpoints...")
        
        # Test activity endpoint
        try:
            response = requests.get(f"{self.base_url}/activity", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_result("activity_endpoint", True, {"count": len(data)})
            else:
                self.test_result("activity_endpoint", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("activity_endpoint", False, error=str(e))
            
        # Test reseed endpoint
        try:
            response = requests.get(f"{self.base_url}/reseed", timeout=15)
            if response.status_code == 200:
                data = response.json()
                self.test_result("reseed_endpoint", True, {
                    "message": data.get("message")
                })
            else:
                self.test_result("reseed_endpoint", False, {"status_code": response.status_code})
        except Exception as e:
            self.test_result("reseed_endpoint", False, error=str(e))
            
    async def run_all_tests(self):
        """Run all test suites"""
        self.log("🚀 Starting SR-AIbridge comprehensive self-test...")
        
        # Wait for server to be ready
        self.log("⏳ Checking server availability...")
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    self.log("✅ Server is ready")
                    break
            except Exception:
                if i == max_retries - 1:
                    self.log("❌ Server not available after retries")
                    return
                time.sleep(2)
                
        # Run test suites
        await self.test_health_endpoints()
        await self.test_guardian_endpoints()
        await self.test_agent_endpoints()
        await self.test_mission_endpoints()
        await self.test_log_endpoints()
        await self.test_websocket_endpoints()
        await self.test_utility_endpoints()
        
    def generate_report(self):
        """Generate and display test report"""
        self.results["end_time"] = datetime.utcnow().isoformat()
        
        print("\n" + "="*80)
        print("🧪 SR-AIBRIDGE SELF-TEST REPORT")
        print("="*80)
        
        summary = self.results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        errors = summary["errors"]
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"📊 SUMMARY:")
        print(f"   Total Tests: {total}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   🚨 Errors: {errors}")
        print(f"   📈 Success Rate: {success_rate:.1f}%")
        
        if failed > 0 or errors > 0:
            print(f"\n🔍 FAILURES:")
            for test in self.results["tests"]:
                if not test["passed"]:
                    print(f"   • {test['name']}: {test.get('error', 'Failed')}")
                    
        print(f"\n⏱️  Duration: {self.results['start_time']} - {self.results['end_time']}")
        print("="*80)
        
        # Return overall success
        return success_rate >= 80.0

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SR-AIbridge Self-Test")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--json", action="store_true", 
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    # Run tests
    test_runner = SRAIBridgeSelfTest(args.url)
    await test_runner.run_all_tests()
    
    # Generate report
    if args.json:
        print(json.dumps(test_runner.results, indent=2))
    else:
        success = test_runner.generate_report()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())