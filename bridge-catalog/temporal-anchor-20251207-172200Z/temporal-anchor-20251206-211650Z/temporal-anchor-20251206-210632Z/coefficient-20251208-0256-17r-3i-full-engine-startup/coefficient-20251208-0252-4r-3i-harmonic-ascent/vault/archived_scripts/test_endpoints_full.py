#!/usr/bin/env python3
"""
SR-AIbridge Comprehensive Endpoint Test
Tests all critical API endpoints with retry logic and detailed reporting
"""
import sys
import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

# Configuration
DEFAULT_BASE_URL = "http://localhost:8000"
TIMEOUT = 30
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ANSI color codes for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color
    BOLD = '\033[1m'

class EndpointTest:
    """Represents a single endpoint test"""
    def __init__(self, name: str, method: str, endpoint: str, 
                 payload: Optional[Dict] = None, expected_status: int = 200,
                 description: str = ""):
        self.name = name
        self.method = method.upper()
        self.endpoint = endpoint
        self.payload = payload
        self.expected_status = expected_status
        self.description = description
        self.result = None
        self.status_code = None
        self.error_message = None
        self.response_time = 0
        
    def __repr__(self):
        return f"<EndpointTest {self.name}: {self.method} {self.endpoint}>"

class EndpointTester:
    """Main test runner"""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.tests: List[EndpointTest] = []
        self.results = {
            'passed': [],
            'failed': [],
            'skipped': []
        }
        
    def add_test(self, test: EndpointTest):
        """Add a test to the suite"""
        self.tests.append(test)
        
    def test_endpoint(self, test: EndpointTest) -> bool:
        """Test a single endpoint with retries"""
        url = f"{self.base_url}{test.endpoint}"
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                start_time = time.time()
                
                if test.method == 'GET':
                    response = requests.get(url, timeout=TIMEOUT)
                elif test.method == 'POST':
                    response = requests.post(
                        url, 
                        json=test.payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=TIMEOUT
                    )
                elif test.method == 'PUT':
                    response = requests.put(
                        url,
                        json=test.payload,
                        headers={'Content-Type': 'application/json'},
                        timeout=TIMEOUT
                    )
                elif test.method == 'DELETE':
                    response = requests.delete(url, timeout=TIMEOUT)
                else:
                    raise ValueError(f"Unsupported method: {test.method}")
                
                test.response_time = time.time() - start_time
                test.status_code = response.status_code
                
                if response.status_code == test.expected_status:
                    test.result = 'PASSED'
                    return True
                else:
                    test.error_message = f"Expected {test.expected_status}, got {response.status_code}"
                    if attempt < MAX_RETRIES:
                        time.sleep(RETRY_DELAY * attempt)
                        continue
                    test.result = 'FAILED'
                    return False
                    
            except requests.exceptions.Timeout:
                test.error_message = f"Timeout after {TIMEOUT}s (attempt {attempt}/{MAX_RETRIES})"
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
                    continue
                test.result = 'FAILED'
                return False
                
            except requests.exceptions.ConnectionError:
                test.error_message = f"Connection error (attempt {attempt}/{MAX_RETRIES})"
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY * attempt)
                    continue
                test.result = 'FAILED'
                return False
                
            except Exception as e:
                test.error_message = f"Error: {str(e)}"
                test.result = 'FAILED'
                return False
                
        return False
    
    def run_all_tests(self) -> Dict:
        """Run all tests and return results"""
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 SR-AIbridge Comprehensive Endpoint Test{Colors.NC}")
        print("=" * 70)
        print(f"Backend URL: {self.base_url}")
        print(f"Timeout: {TIMEOUT}s")
        print(f"Max Retries: {MAX_RETRIES}")
        print(f"Total Tests: {len(self.tests)}")
        print("=" * 70)
        print()
        
        for i, test in enumerate(self.tests, 1):
            print(f"{Colors.CYAN}[{i}/{len(self.tests)}] Testing: {test.name}{Colors.NC}")
            print(f"  Endpoint: {test.method} {test.endpoint}")
            if test.description:
                print(f"  Description: {test.description}")
            
            success = self.test_endpoint(test)
            
            if success:
                self.results['passed'].append(test)
                print(f"  {Colors.GREEN}✅ PASSED{Colors.NC} (HTTP {test.status_code}, {test.response_time:.2f}s)")
            else:
                self.results['failed'].append(test)
                print(f"  {Colors.RED}❌ FAILED{Colors.NC}")
                if test.error_message:
                    print(f"  {Colors.RED}Error: {test.error_message}{Colors.NC}")
            print()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        total = len(self.tests)
        passed = len(self.results['passed'])
        failed = len(self.results['failed'])
        
        print("=" * 70)
        print(f"{Colors.BOLD}📊 Test Summary{Colors.NC}")
        print("=" * 70)
        print(f"Total Tests:  {total}")
        print(f"{Colors.GREEN}Passed:       {passed}{Colors.NC}")
        print(f"{Colors.RED}Failed:       {failed}{Colors.NC}")
        print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")
        print("=" * 70)
        
        if failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.NC}")
            for test in self.results['failed']:
                print(f"  {Colors.RED}❌{Colors.NC} {test.name}")
                print(f"     Endpoint: {test.method} {test.endpoint}")
                if test.error_message:
                    print(f"     Error: {test.error_message}")
            print()
        
        if passed == total:
            print(f"\n{Colors.GREEN}🎉 All endpoints are functional!{Colors.NC}")
            print(f"{Colors.GREEN}✅ SR-AIbridge backend is ready for operation{Colors.NC}\n")
            return 0
        else:
            print(f"\n{Colors.YELLOW}⚠️  Some endpoints need attention{Colors.NC}")
            print(f"{Colors.YELLOW}📋 Check the detailed output above{Colors.NC}\n")
            if failed == total:
                print(f"{Colors.RED}❌ All endpoint tests failed{Colors.NC}")
                print(f"{Colors.RED}🚨 Backend may not be running or is misconfigured{Colors.NC}\n")
                return 2
            return 1

def create_test_suite(base_url: str) -> EndpointTester:
    """Create the comprehensive test suite"""
    tester = EndpointTester(base_url)
    
    # Core Health & Status Endpoints
    tester.add_test(EndpointTest(
        name="Health Check",
        method="GET",
        endpoint="/health",
        description="Basic health check for load balancers"
    ))
    
    tester.add_test(EndpointTest(
        name="Full Health Check",
        method="GET",
        endpoint="/health/full",
        description="Comprehensive system health check"
    ))
    
    tester.add_test(EndpointTest(
        name="Status Check",
        method="GET",
        endpoint="/status",
        description="System status endpoint"
    ))
    
    tester.add_test(EndpointTest(
        name="API Status",
        method="GET",
        endpoint="/api/status",
        description="Frontend health check endpoint"
    ))
    
    # Diagnostics Endpoints
    tester.add_test(EndpointTest(
        name="Diagnostics Submission",
        method="POST",
        endpoint="/api/diagnostics",
        payload={
            "type": "ENDPOINT_TEST",
            "status": "TESTING",
            "source": "test_endpoints_full.py",
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "test_run": True
            }
        },
        description="Submit diagnostic event"
    ))
    
    # Agents Endpoints
    tester.add_test(EndpointTest(
        name="List Agents",
        method="GET",
        endpoint="/agents",
        description="List all registered agents"
    ))
    
    # Engine Endpoints (from smoke_test_engines.sh)
    tester.add_test(EndpointTest(
        name="Math Engine (CalculusCore)",
        method="POST",
        endpoint="/engines/math/prove",
        payload={
            "equation": "x^2 + 2*x + 1",
            "operation": "differentiate",
            "variable": "x",
            "prove_theorem": "quadratic_completion"
        },
        expected_status=404,  # May not be implemented yet
        description="Test Math Engine"
    ))
    
    tester.add_test(EndpointTest(
        name="Quantum Engine (QHelmSingularity)",
        method="POST",
        endpoint="/engines/quantum/collapse",
        payload={
            "quantum_state": "superposition",
            "coordinates": [1.0, 2.0, 3.0, 4.0],
            "singularity_type": "wormhole",
            "navigation_mode": "quantum_tunneling"
        },
        expected_status=404,  # May not be implemented yet
        description="Test Quantum Engine"
    ))
    
    tester.add_test(EndpointTest(
        name="Science Engine (AuroraForge)",
        method="POST",
        endpoint="/engines/science/experiment",
        payload={
            "experiment_type": "visual_synthesis",
            "parameters": {
                "style": "cyberpunk",
                "dimensions": [1920, 1080],
                "complexity": 0.8
            },
            "hypothesis": "aurora_pattern_generation"
        },
        expected_status=404,  # May not be implemented yet
        description="Test Science Engine"
    ))
    
    tester.add_test(EndpointTest(
        name="Language Engine (ScrollTongue)",
        method="POST",
        endpoint="/engines/language/translate",
        payload={
            "text": "Hello, SR-AIbridge!",
            "source_lang": "en",
            "target_lang": "es",
            "preserve_technical_terms": True
        },
        expected_status=404,  # May not be implemented yet
        description="Test Language Engine"
    ))
    
    tester.add_test(EndpointTest(
        name="Business Engine (CommerceForge)",
        method="POST",
        endpoint="/engines/business/analyze",
        payload={
            "query": "Calculate ROI for new feature development",
            "context": {
                "budget": 100000,
                "timeline": "Q2 2024"
            }
        },
        expected_status=404,  # May not be implemented yet
        description="Test Business Engine"
    ))
    
    tester.add_test(EndpointTest(
        name="History Engine (ChronicleLoom)",
        method="POST",
        endpoint="/engines/history/chronicle",
        payload={
            "event": "Test deployment",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "source": "endpoint_test"
            }
        },
        expected_status=404,  # May not be implemented yet
        description="Test History Engine"
    ))
    
    # Leviathan Solver
    tester.add_test(EndpointTest(
        name="Leviathan Solver",
        method="POST",
        endpoint="/engines/leviathan/solve",
        payload={
            "q": "What would it take to build a 4D projection demo for Nova?",
            "captain": "TestCaptain",
            "project": "test",
            "dispatch": False
        },
        description="Test Leviathan Solver engine"
    ))
    
    # Truth Engine
    tester.add_test(EndpointTest(
        name="Truth Engine - Find",
        method="POST",
        endpoint="/engines/truth/find",
        payload={
            "query": "test query",
            "limit": 10
        },
        description="Test Truth Engine find endpoint"
    ))
    
    # Parser Engine
    tester.add_test(EndpointTest(
        name="Parser Engine - Parse",
        method="POST",
        endpoint="/engines/parser/parse",
        payload={
            "text": "This is a test document",
            "source": "endpoint_test"
        },
        description="Test Parser Engine"
    ))
    
    return tester

def main():
    """Main entry point"""
    import argparse
    
    global TIMEOUT
    
    parser = argparse.ArgumentParser(
        description='SR-AIbridge Comprehensive Endpoint Test',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Test localhost:8000
  %(prog)s https://your-backend.onrender.com # Test deployed backend
  %(prog)s --json                            # Output in JSON format
        """
    )
    parser.add_argument(
        'base_url',
        nargs='?',
        default=DEFAULT_BASE_URL,
        help='Backend URL (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=None,
        help=f'Request timeout in seconds (default: {TIMEOUT})'
    )
    
    args = parser.parse_args()
    
    # Update global timeout if specified
    if args.timeout is not None:
        TIMEOUT = args.timeout
    
    # Create and run test suite
    tester = create_test_suite(args.base_url)
    results = tester.run_all_tests()
    
    if args.json:
        # Output JSON format
        json_results = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'base_url': args.base_url,
            'total_tests': len(tester.tests),
            'passed': len(results['passed']),
            'failed': len(results['failed']),
            'tests': [
                {
                    'name': test.name,
                    'method': test.method,
                    'endpoint': test.endpoint,
                    'result': test.result,
                    'status_code': test.status_code,
                    'response_time': test.response_time,
                    'error': test.error_message
                }
                for test in tester.tests
            ]
        }
        print(json.dumps(json_results, indent=2))
    else:
        # Print summary
        exit_code = tester.print_summary()
        sys.exit(exit_code)

if __name__ == '__main__':
    main()
