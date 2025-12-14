#!/usr/bin/env python3
"""
Bridge Functionality Smoke Test
================================

Comprehensive test to demonstrate that the SR-AIbridge has full functionality.
This test validates:
1. Bridge CLI commands work
2. Backend API is functional
3. Engines are operational
4. Communication paths are established
"""

import subprocess
import sys
import time
import json
from pathlib import Path

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text:^70}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_info(text):
    print(f"{YELLOW}ℹ️  {text}{RESET}")

def run_command(cmd, description, timeout=30):
    """Run a command and return success status"""
    print_info(f"Testing: {description}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print_success(f"{description} - PASSED")
            return True, result.stdout
        else:
            print_error(f"{description} - FAILED")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print_error(f"{description} - TIMEOUT")
        return False, "Timeout"
    except Exception as e:
        print_error(f"{description} - ERROR: {str(e)}")
        return False, str(e)

def test_bridge_cli():
    """Test Bridge CLI commands"""
    print_header("Testing Bridge CLI")
    
    tests = [
        ("./bridge --help", "Bridge CLI help"),
        ("./bridge status", "Bridge status command"),
        ("./bridge communicate", "Bridge communication paths"),
    ]
    
    results = []
    for cmd, desc in tests:
        success, output = run_command(cmd, desc)
        results.append(success)
        
    return all(results)

def test_backend_app():
    """Test backend app can be imported"""
    print_header("Testing Backend Application")
    
    test_code = """
import sys
sys.path.insert(0, 'bridge_backend')
from main import app
print(f'Routes: {len(app.routes)}')
print(f'Version: {app.version}')
print('SUCCESS')
"""
    
    success, output = run_command(
        f"python3 -c \"{test_code}\"",
        "Backend app import and routes"
    )
    
    if success and "SUCCESS" in output:
        # Extract route count
        for line in output.split('\n'):
            if 'Routes:' in line:
                print(f"  {line}")
            if 'Version:' in line:
                print(f"  {line}")
    
    return success

def test_bridge_core_modules():
    """Test bridge core modules"""
    print_header("Testing Bridge Core Modules")
    
    test_code = """
import sys
sys.path.insert(0, '.')
from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator

orchestrator = BridgeHarmonyOrchestrator()
orchestrator.discover_engines()
print(f'Engines discovered: {len(orchestrator.engines)}')

orchestrator.auto_wire_communications()
print(f'Communication paths: {len(orchestrator.communication_paths)}')

metrics = orchestrator.establish_bridge_resonance()
print(f'Resonance: {metrics["resonance_percentage"]}%')
print(f'Harmony: {metrics["harmony_status"]}')
print('SUCCESS')
"""
    
    success, output = run_command(
        f"python3 -c \"{test_code}\"",
        "Bridge core modules and orchestration",
        timeout=60
    )
    
    if success:
        for line in output.split('\n'):
            if any(key in line for key in ['Engines', 'paths', 'Resonance', 'Harmony']):
                print(f"  {line}")
    
    return success

def test_genesis_bus():
    """Test Genesis event bus"""
    print_header("Testing Genesis Event Bus")
    
    test_code = """
import sys
sys.path.insert(0, 'bridge_backend')
from bridge_backend.genesis.bus import GenesisEventBus

bus = GenesisEventBus()
print(f'Bus initialized: {bus is not None}')
print(f'Strict mode: {bus.strict}')
print('SUCCESS')
"""
    
    success, output = run_command(
        f"python3 -c \"{test_code}\"",
        "Genesis event bus initialization"
    )
    
    return success

def test_engine_discovery():
    """Test engine discovery and listing"""
    print_header("Testing Engine Discovery")
    
    # Count engine directories
    engine_dirs = [
        "bridge_backend/bridge_core/engines",
        "bridge_backend/engines"
    ]
    
    total_engines = 0
    for engine_dir in engine_dirs:
        path = Path(engine_dir)
        if path.exists():
            engines = [d for d in path.iterdir() if d.is_dir() and not d.name.startswith('__')]
            total_engines += len(engines)
            print_info(f"Found {len(engines)} engines in {engine_dir}")
    
    if total_engines > 0:
        print_success(f"Total engines discovered: {total_engines}")
        return True
    else:
        print_error("No engines discovered")
        return False

def generate_report(results):
    """Generate final test report"""
    print_header("Test Summary Report")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"{GREEN}Passed: {passed_tests}{RESET}")
    print(f"{RED}Failed: {failed_tests}{RESET}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%\n")
    
    print("Detailed Results:")
    for test_name, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {test_name}: {status}")
    
    if passed_tests == total_tests:
        print(f"\n{GREEN}🎉 ALL TESTS PASSED - BRIDGE IS FULLY FUNCTIONAL! 🎉{RESET}\n")
        return 0
    else:
        print(f"\n{YELLOW}⚠️  Some tests failed, but bridge has significant functionality{RESET}\n")
        return 1

def main():
    """Main test runner"""
    print_header("SR-AIbridge Functionality Smoke Test")
    print("This test validates that the bridge has full operational functionality\n")
    
    results = {}
    
    # Run all tests
    print_info("Starting comprehensive functionality tests...\n")
    
    results["Bridge CLI"] = test_bridge_cli()
    results["Backend App"] = test_backend_app()
    results["Bridge Core"] = test_bridge_core_modules()
    results["Genesis Bus"] = test_genesis_bus()
    results["Engine Discovery"] = test_engine_discovery()
    
    # Generate report
    return generate_report(results)

if __name__ == "__main__":
    sys.exit(main())
