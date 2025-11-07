#!/usr/bin/env python3
"""
SR-AIbridge Deployment Verification Script
Verifies system has exited placeholder mode and is fully operational
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"
TIMEOUT = 5

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_section(text):
    print(f"\n{Colors.BOLD}{text}{Colors.END}")
    print("-" * 80)

def test_endpoint(name, url, required=True):
    """Test a single system endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{url}", timeout=TIMEOUT)
        status_code = response.status_code
        
        try:
            data = response.json()
        except:
            data = {"error": "non-json response", "text": response.text[:200]}
        
        # Determine if system is operational
        operational = False
        status_msg = ""
        
        if status_code == 200:
            if isinstance(data, dict):
                status_field = data.get('status', '').lower()
                if status_field in ['ok', 'operational', 'active', 'healthy']:
                    operational = True
                    status_msg = f"Status: {status_field}"
                elif status_field and status_field not in ['offline', 'unavailable', 'unhealthy']:
                    operational = True
                    status_msg = f"Status: {status_field}"
                else:
                    status_msg = f"Status indicates offline: {status_field}"
            else:
                status_msg = "Non-dict response"
        elif status_code == 403:
            status_msg = f"403 Forbidden (expected for {name})"
            operational = not required  # For optional systems, 403 doesn't fail the test
        else:
            status_msg = f"HTTP {status_code}"
        
        check = f"{Colors.GREEN}✓{Colors.END}" if operational else f"{Colors.RED}✗{Colors.END}"
        req_label = f"{Colors.RED}REQUIRED{Colors.END}" if required else f"{Colors.YELLOW}optional{Colors.END}"
        
        print(f"{check} {name:25} | {status_msg:50} | {req_label}")
        return operational
        
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗{Colors.END} {name:25} | Connection refused - is backend running?{' ':25} | {'REQUIRED' if required else 'optional'}")
        return False
    except requests.exceptions.Timeout:
        print(f"{Colors.RED}✗{Colors.END} {name:25} | Timeout after {TIMEOUT}s{' ':45} | {'REQUIRED' if required else 'optional'}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} {name:25} | Exception: {str(e)[:40]:50} | {'REQUIRED' if required else 'optional'}")
        return False

def main():
    print_header("SR-AIBRIDGE DEPLOYMENT VERIFICATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Backend URL: {BASE_URL}")
    
    # Test all systems
    print_section("🔴 CORE SYSTEMS (both must pass for deployment)")
    brh = test_endpoint("BRH Connectivity", "/api/health/status", required=True)
    healing_net = test_endpoint("Healing Net", "/api/health/health", required=True)
    
    print_section("🟡 OPTIONAL SYSTEMS (failures don't block deployment)")
    crypto = test_endpoint("Crypto/Custody", "/custody/status", required=False)
    umbra = test_endpoint("Umbra Lattice", "/api/health/health/full", required=False)
    indoctrination = test_endpoint("Indoctrination", "/engines/indoctrination/status", required=False)
    
    # Calculate results
    core_systems_online = brh and healing_net
    systems_online = sum([brh, healing_net, crypto, umbra, indoctrination])
    total_systems = 5
    
    # Display results
    print_section("📊 VALIDATION RESULTS")
    print(f"\nCore Systems:")
    print(f"  BRH Connectivity:        {Colors.GREEN}✅ PASS{Colors.END}" if brh else f"  BRH Connectivity:        {Colors.RED}❌ FAIL{Colors.END}")
    print(f"  Healing Net Operational: {Colors.GREEN}✅ PASS{Colors.END}" if healing_net else f"  Healing Net Operational: {Colors.RED}❌ FAIL{Colors.END}")
    print(f"  Core Systems Online:     {Colors.GREEN}✅ YES{Colors.END}" if core_systems_online else f"  Core Systems Online:     {Colors.RED}❌ NO{Colors.END}")
    
    print(f"\nOptional Systems:")
    print(f"  Crypto/Custody:          {Colors.GREEN}✅ PASS{Colors.END}" if crypto else f"  Crypto/Custody:          {Colors.YELLOW}❌ FAIL (OK - optional){Colors.END}")
    print(f"  Umbra Lattice:           {Colors.GREEN}✅ PASS{Colors.END}" if umbra else f"  Umbra Lattice:           {Colors.YELLOW}❌ FAIL (OK - optional){Colors.END}")
    print(f"  Indoctrination:          {Colors.GREEN}✅ PASS{Colors.END}" if indoctrination else f"  Indoctrination:          {Colors.YELLOW}❌ FAIL (OK - optional){Colors.END}")
    
    print(f"\nOverall Statistics:")
    print(f"  Systems Online: {systems_online}/{total_systems}")
    print(f"  Success Rate: {(systems_online/total_systems)*100:.1f}%")
    
    # Deployment status
    print_section("🚀 DEPLOYMENT STATUS")
    
    if core_systems_online:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 TRUE DEPLOYMENT ACHIEVED!{Colors.END}")
        print(f"   Status: {Colors.GREEN}OPERATIONAL{Colors.END}")
        print(f"   Mode: {Colors.GREEN}PRODUCTION{Colors.END}")
        print(f"   Message: 'Core systems online - True Bridge revealed'")
        print(f"\n   {Colors.GREEN}FRONTEND SHOULD:{Colors.END}")
        print(f"   - Display DeploymentStatusBadge as '{Colors.GREEN}✅ PRODUCTION{Colors.END}'")
        print(f"   - Reveal all SovereignRevealGate wrapped components")
        print(f"   - Show real functionality (NOT placeholders)")
        print(f"\n   {Colors.GREEN}Components that should be revealed:{Colors.END}")
        print(f"   - ✓ AgentFoundry")
        print(f"   - ✓ BrainConsole")
        print(f"   - ✓ VaultLogs")
        print(f"   - ✓ MissionLog")
        print(f"   - ✓ AdmiralKeysPanel")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ SYSTEM HAS EXITED PLACEHOLDER MODE{Colors.END}")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}🕵️ PLACEHOLDER MODE ACTIVE{Colors.END}")
        print(f"   Status: {Colors.RED}DEGRADED{Colors.END}")
        print(f"   Mode: {Colors.YELLOW}DEVELOPMENT/DEGRADED{Colors.END}")
        print(f"   Message: 'Core deployment not yet achieved - {systems_online}/{total_systems} systems online'")
        print(f"\n   {Colors.YELLOW}FRONTEND SHOULD:{Colors.END}")
        print(f"   - Display DeploymentStatusBadge as '{Colors.YELLOW}⚠️ DEGRADED{Colors.END}' or '{Colors.YELLOW}🛠️ DEVELOPMENT{Colors.END}'")
        print(f"   - Show placeholder components")
        print(f"   - Display friendly 'waiting for deployment' messages")
        print(f"\n   {Colors.RED}Failed core systems:{Colors.END}")
        if not brh:
            print(f"   - {Colors.RED}❌ BRH Connectivity{Colors.END}")
        if not healing_net:
            print(f"   - {Colors.RED}❌ Healing Net Operational{Colors.END}")
        
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ SYSTEM REMAINS IN PLACEHOLDER MODE{Colors.END}")
        print(f"\n{Colors.RED}ACTION REQUIRED:{Colors.END}")
        print(f"   1. Ensure backend server is running: python -m uvicorn bridge_backend.main:app --port 8000")
        print(f"   2. Check backend logs for errors")
        print(f"   3. Verify core endpoints are responding")
        print(f"   4. Review DEPLOYMENT_VERIFICATION_GUIDE.md for troubleshooting")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        print()  # Add spacing
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Verification interrupted by user{Colors.END}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error during verification: {e}{Colors.END}")
        sys.exit(1)
