#!/usr/bin/env python3
"""
Sovereign Engines Integration Example

Demonstrates the complete workflow of analyzing code changes and logs
using all Sovereign Engines together.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard
from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe
from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician


def example_workflow():
    """Complete workflow example"""
    
    print("=" * 70)
    print("🚀 SOVEREIGN ENGINES - COMPLETE WORKFLOW EXAMPLE")
    print("=" * 70)
    
    # Initialize all engines
    print("\n📦 Initializing Sovereign Engines...")
    guard = SovereignComplianceGuard()
    scribe = SovereignMicroScribe()
    logician = SovereignMicroLogician()
    print("✅ All engines initialized\n")
    
    # Step 1: Check compliance
    print("=" * 70)
    print("STEP 1: COMPLIANCE CHECK")
    print("=" * 70)
    
    compliance = guard.check_compliance("code_analysis", "/bridge/engines/microscribe/analyze")
    print(f"\n🛡️ Compliance Status: {'✅ COMPLIANT' if compliance.compliant else '❌ VIOLATION'}")
    print(f"   License Valid: {compliance.license_valid}")
    print(f"   Resonance Sufficient: {compliance.resonance_sufficient}")
    print(f"   Policy Enforced: {compliance.policy_enforced}")
    
    if not compliance.compliant:
        print(f"   Violations: {', '.join(compliance.violations)}")
        return
    
    # Step 2: Analyze code changes
    print("\n" + "=" * 70)
    print("STEP 2: CODE CHANGE ANALYSIS")
    print("=" * 70)
    
    sample_diff = """diff --git a/backend/api.py b/backend/api.py
index 1234567..abcdefg 100644
--- a/backend/api.py
+++ b/backend/api.py
@@ -10,7 +10,8 @@ def authenticate_user(username, password):
     # Authenticate user
-    db_password = get_password_from_db(username)
+    # Security fix: Use constant-time comparison
+    db_password = get_password_hash(username)
-    if password == db_password:
+    if constant_time_compare(password, db_password):
         return create_session(username)
     return None
 
diff --git a/backend/config.py b/backend/config.py
index 7890abc..defghij 100644
--- a/backend/config.py
+++ b/backend/config.py
@@ -5,4 +5,5 @@
 DEBUG = False
 DATABASE_URL = "postgresql://localhost/mydb"
+LOG_LEVEL = "INFO"
+CACHE_TTL = 3600
"""
    
    print("\n📝 Analyzing diff with MicroScribe...")
    analysis = scribe.analyze_diff(sample_diff)
    
    print(f"\n📊 Analysis Results:")
    print(f"   Mode: {analysis.mode.value}")
    print(f"   Files Changed: {analysis.files_changed}")
    print(f"   Lines Added: {analysis.lines_added}")
    print(f"   Lines Removed: {analysis.lines_removed}")
    print(f"   Risk Level: {analysis.risk_level.value}")
    print(f"   Security Findings: {len(analysis.security_findings)}")
    
    if analysis.security_findings:
        print("\n🔒 Security Findings:")
        for finding in analysis.security_findings:
            print(f"   - {finding}")
    
    print("\n💡 Recommendations:")
    for rec in analysis.recommendations:
        print(f"   - {rec}")
    
    # Step 3: Generate PR
    print("\n" + "=" * 70)
    print("STEP 3: PR TEMPLATE GENERATION")
    print("=" * 70)
    
    pr = scribe.generate_pr(
        analysis,
        "Security: Implement constant-time password comparison",
        "This PR fixes a timing attack vulnerability in password comparison."
    )
    
    print(f"\n📄 Generated PR:")
    print(f"   Title: {pr.title}")
    print(f"   Labels: {', '.join(pr.labels)}")
    print(f"\nDescription Preview:")
    print("   " + pr.description.replace("\n", "\n   ")[:500] + "...")
    
    # Step 4: Analyze deployment logs
    print("\n" + "=" * 70)
    print("STEP 4: DEPLOYMENT LOG ANALYSIS")
    print("=" * 70)
    
    sample_logs = """2025-11-05 12:00:00 INFO [Deploy] Starting deployment of backend v2.1.0
2025-11-05 12:00:05 INFO [Build] Building Docker image
2025-11-05 12:00:30 INFO [Build] Image built successfully
2025-11-05 12:00:35 INFO [Deploy] Pushing to registry
2025-11-05 12:01:00 INFO [Deploy] Image pushed
2025-11-05 12:01:05 INFO [Deploy] Updating service
2025-11-05 12:01:10 INFO [Health] Running health checks
2025-11-05 12:01:15 INFO [Health] Health check passed
2025-11-05 12:01:20 INFO [Deploy] Deployment successful
2025-11-05 12:01:25 INFO [App] Application started on port 8000
2025-11-05 12:01:30 INFO [App] Database connection established
2025-11-05 12:01:35 INFO [App] Cache initialized
2025-11-05 12:02:00 INFO [API] GET /api/health 200 OK
2025-11-05 12:02:05 INFO [API] GET /api/status 200 OK
"""
    
    print("\n🔍 Analyzing logs with MicroLogician...")
    log_analysis = logician.analyze_logs(sample_logs)
    
    print(f"\n📊 Log Analysis Results:")
    print(f"   Mode: {log_analysis.mode}")
    print(f"   Confidence: {log_analysis.confidence}")
    print(f"   Total Events: {log_analysis.total_lines}")
    print(f"   Error Rate: {log_analysis.performance_metrics.error_rate:.2%}")
    print(f"   Warning Rate: {log_analysis.performance_metrics.warning_rate:.2%}")
    
    if log_analysis.security_findings:
        print(f"\n🔒 Security Findings: {len(log_analysis.security_findings)}")
        for finding in log_analysis.security_findings:
            print(f"   [{finding.threat_level.value}] {finding.description}")
    
    if log_analysis.patterns:
        print(f"\n🔍 Patterns Detected:")
        for pattern, count in log_analysis.patterns.items():
            print(f"   - {pattern}: {count}")
    
    print(f"\n💡 Recommendations:")
    for rec in log_analysis.recommendations:
        print(f"   - {rec}")
    
    # Step 5: Audit trail
    print("\n" + "=" * 70)
    print("STEP 5: AUDIT TRAIL")
    print("=" * 70)
    
    audit_trail = guard.get_audit_trail(limit=5)
    print(f"\n📋 Recent Audit Entries: {len(audit_trail)}")
    
    for i, entry in enumerate(audit_trail[-3:], 1):
        print(f"\n   Entry {i}:")
        print(f"      Operation: {entry['operation']}")
        print(f"      Result: {entry['result']}")
        print(f"      Timestamp: {entry['timestamp']}")
        print(f"      Signature: {entry['signature'][:32]}...")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ WORKFLOW COMPLETE")
    print("=" * 70)
    print("""
Summary:
✅ Compliance validated
✅ Code changes analyzed with security checks
✅ PR template generated with recommendations
✅ Deployment logs analyzed for performance and security
✅ Complete audit trail maintained

The Sovereign Engines provide end-to-end visibility and security
for your development and deployment workflow!
    """)


if __name__ == "__main__":
    try:
        example_workflow()
    except Exception as e:
        print(f"\n❌ Error running example: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
