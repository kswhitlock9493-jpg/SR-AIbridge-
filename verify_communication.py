#!/usr/bin/env python3
"""
Bridge Communication Verification Script
Displays the current status of frontend-backend communication parity
"""

import json
import pathlib
import sys

# Paths
ROOT = pathlib.Path(__file__).resolve().parent
PARITY_REPORT = ROOT / "bridge_backend/diagnostics/bridge_parity_report.json"
AUTOFIX_REPORT = ROOT / "bridge_backend/diagnostics/parity_autofix_report.json"
AUTO_GEN_DIR = ROOT / "bridge-frontend/src/api/auto_generated"

def load_json(filepath):
    """Load JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def print_header(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_status_badge(status):
    """Print colored status badge"""
    if status == "Parity achieved":
        return "✅ HEALTHY"
    elif "Partial" in status:
        return "⚠️  DEGRADED"
    else:
        return "❌ CRITICAL"

def verify_communication():
    """Verify frontend-backend communication status"""
    
    print_header("SR-AIbridge Communication Parity Status")
    
    # Load reports
    parity = load_json(PARITY_REPORT)
    autofix = load_json(AUTOFIX_REPORT)
    
    if not parity:
        print("❌ ERROR: Parity report not found. Run parity_engine.py first.")
        return 1
    
    if not autofix:
        print("❌ ERROR: Autofix report not found. Run parity_autofix.py first.")
        return 1
    
    # Display summary
    summary = autofix.get("summary", {})
    print(f"\n📊 Overall Status: {print_status_badge(summary.get('status', 'Unknown'))}")
    print(f"   Timestamp: {summary.get('timestamp', 'N/A')}")
    print(f"   Version: {summary.get('version', 'N/A')}")
    
    # Backend-Frontend Stats
    print_header("Backend ↔ Frontend Statistics")
    print(f"   Backend Routes:         {summary.get('backend_routes', 0)}")
    print(f"   Frontend API Calls:     {summary.get('frontend_calls', 0)}")
    print(f"   Repaired Endpoints:     {summary.get('repaired_endpoints', 0)}")
    print(f"   Pending Manual Review:  {summary.get('pending_manual_review', 0)}")
    
    # Critical Routes
    critical_routes = autofix.get("auto_repaired", [])
    if critical_routes:
        print_header("Critical Routes Auto-Repaired")
        for route in critical_routes:
            print(f"   ✅ {route}")
    
    # Manual Review Required
    manual_review = autofix.get("manual_review", [])
    if manual_review:
        print_header("Endpoints Requiring Manual Review")
        for route in manual_review:
            print(f"   ⚠️  {route}")
    
    # Generated Stubs
    print_header("Generated Frontend Stubs")
    if AUTO_GEN_DIR.exists():
        stub_files = list(AUTO_GEN_DIR.glob("*.js"))
        stub_files = [f for f in stub_files if f.name not in ['index.js', 'README.md']]
        print(f"   Total Stubs Generated: {len(stub_files)}")
        print(f"   Location: {AUTO_GEN_DIR}")
        
        # Show first 5 as examples
        if stub_files:
            print(f"\n   Sample Stubs:")
            for stub in sorted(stub_files)[:5]:
                print(f"      📄 {stub.name}")
            if len(stub_files) > 5:
                print(f"      ... and {len(stub_files) - 5} more")
    else:
        print("   ⚠️  Auto-generated directory not found")
    
    # Missing Endpoints Analysis
    parity_summary = parity.get("summary", {})
    missing_frontend = parity_summary.get("missing_from_frontend", 0)
    missing_backend = parity_summary.get("missing_from_backend", 0)
    
    print_header("Parity Analysis")
    print(f"   Missing from Frontend: {missing_frontend}")
    print(f"   Missing from Backend:  {missing_backend}")
    
    # Severity Breakdown
    missing_from_frontend = parity.get("missing_from_frontend", [])
    critical_count = sum(1 for x in missing_from_frontend if x.get("severity") == "critical")
    moderate_count = sum(1 for x in missing_from_frontend if x.get("severity") == "moderate")
    info_count = sum(1 for x in missing_from_frontend if x.get("severity") == "informational")
    
    print(f"\n   Severity Breakdown (Frontend):")
    print(f"      🔴 Critical:       {critical_count}")
    print(f"      🟡 Moderate:       {moderate_count}")
    print(f"      🔵 Informational:  {info_count}")
    
    # Final Status
    print_header("Communication Status")
    
    status = summary.get('status', 'Unknown')
    if status == "Parity achieved":
        print("""
   ✅ COMMUNICATION HEALTHY
   
   The frontend and backend are properly communicating. All critical
   endpoints have been analyzed and repaired. Frontend stubs have been
   auto-generated for missing routes.
   
   Next Steps:
   1. Review auto-generated stubs in bridge-frontend/src/api/auto_generated/
   2. Integrate critical endpoint stubs into your application
   3. Implement missing backend endpoints as needed
   
   For details, see PARITY_ENGINE_RUN_SUMMARY.md
        """)
        return 0
    else:
        print(f"""
   ⚠️  STATUS: {status}
   
   Some issues remain. Review the parity reports for details.
        """)
        return 1

if __name__ == "__main__":
    try:
        exit_code = verify_communication()
        print("=" * 70)
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(2)
