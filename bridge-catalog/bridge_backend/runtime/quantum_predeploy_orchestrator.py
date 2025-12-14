#!/usr/bin/env python3
"""
Quantum Predeploy Orchestrator - Token Forge Dominion v1.9.7s-SOVEREIGN

Pre-deployment orchestration for quantum environment sovereignty.
Runs compliance checks, security scans, and token validation before deployment.
"""
import os
import sys
import json
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bridge_backend.bridge_core.token_forge_dominion import (
    EnterpriseOrchestrator,
    QuantumScanner,
    generate_root_key
)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Main orchestrator function for pre-deployment validation.
    """
    logger.info("🜂 Quantum Predeploy Orchestrator v1.9.7s-SOVEREIGN")
    logger.info("=" * 60)
    
    # Get environment from environment variable
    environment = os.getenv("DEPLOY_ENVIRONMENT", os.getenv("ENVIRONMENT", "development"))
    logger.info(f"Target Environment: {environment}")
    
    # Check for root key
    root_key = os.getenv("FORGE_DOMINION_ROOT")
    if not root_key:
        logger.warning("⚠️  FORGE_DOMINION_ROOT not set")
        logger.info("Generating temporary root key for this deployment...")
        temp_key = generate_root_key()
        os.environ["FORGE_DOMINION_ROOT"] = temp_key
        logger.warning("⚠️  Set FORGE_DOMINION_ROOT in production environment!")
    else:
        logger.info("✅ FORGE_DOMINION_ROOT configured")
    
    # Initialize orchestrator
    logger.info("Initializing Enterprise Orchestrator...")
    orchestrator = EnterpriseOrchestrator(environment=environment)
    
    # Run health check
    logger.info("\n" + "=" * 60)
    logger.info("🏥 Health Check")
    logger.info("=" * 60)
    health = orchestrator.health_check()
    logger.info(f"Overall Status: {health['overall_status']}")
    
    for component, status in health['components'].items():
        status_icon = "✅" if status['status'] == 'healthy' else "⚠️"
        logger.info(f"{status_icon} {component}: {status['status']}")
    
    if health['overall_status'] == 'unhealthy':
        logger.error("❌ Health check failed - deployment aborted")
        return 1
    
    # Run pre-deployment checks
    logger.info("\n" + "=" * 60)
    logger.info("🔍 Pre-Deployment Checks")
    logger.info("=" * 60)
    
    checks_passed, checks_report = orchestrator.pre_deployment_checks()
    
    for check_name, check_result in checks_report.get('checks', {}).items():
        if check_result.get('passed'):
            logger.info(f"✅ {check_name}: PASSED")
            if 'fingerprint' in check_result:
                logger.info(f"   Key fingerprint: {check_result['fingerprint']}")
            if 'score' in check_result:
                logger.info(f"   Resonance score: {check_result['score']}")
        else:
            logger.error(f"❌ {check_name}: FAILED")
            logger.error(f"   Reason: {check_result.get('reason', 'Unknown')}")
    
    if not checks_passed:
        logger.error("\n❌ Pre-deployment checks failed")
        logger.info("\nChecks Report:")
        print(json.dumps(checks_report, indent=2))
        return 1
    
    logger.info(f"\n✅ All pre-deployment checks passed")
    
    # Run quantum scanner
    logger.info("\n" + "=" * 60)
    logger.info("🔬 Quantum Security Scan")
    logger.info("=" * 60)
    
    scanner = QuantumScanner(root_path=".")
    scan_report = scanner.quantum_scan()
    
    logger.info(f"Files scanned: {scan_report['files_scanned']}")
    logger.info(f"Files with findings: {scan_report['files_with_findings']}")
    logger.info(f"Total findings: {scan_report['total_findings']}")
    logger.info(f"Status: {scan_report['status']}")
    logger.info(f"Risk score: {scan_report['risk_score']}")
    
    # Show findings by severity
    findings = scan_report['findings_by_severity']
    if findings['critical'] > 0:
        logger.error(f"❌ Critical: {findings['critical']}")
    if findings['high'] > 0:
        logger.warning(f"⚠️  High: {findings['high']}")
    if findings['medium'] > 0:
        logger.info(f"ℹ️  Medium: {findings['medium']}")
    if findings['low'] > 0:
        logger.info(f"ℹ️  Low: {findings['low']}")
    
    # Production requires clean or low risk
    if environment == "production" and scan_report['status'] not in ['CLEAN', 'LOW_RISK']:
        logger.error(f"❌ Security scan status '{scan_report['status']}' not acceptable for production")
        return 1
    
    # Generate compliance report
    logger.info("\n" + "=" * 60)
    logger.info("📋 Compliance Report")
    logger.info("=" * 60)
    
    compliance = orchestrator.generate_compliance_report()
    logger.info(f"Compliance Status: {compliance['compliance_status']}")
    logger.info(f"Validation Success Rate: {compliance['validation_metrics']['success_rate']:.1f}%")
    
    # Save reports
    logger.info("\n" + "=" * 60)
    logger.info("💾 Saving Reports")
    logger.info("=" * 60)
    
    reports_dir = Path(".alik")
    reports_dir.mkdir(exist_ok=True)
    
    # Save pre-deployment report
    predeploy_report = {
        "timestamp": checks_report['timestamp'],
        "environment": environment,
        "health_check": health,
        "pre_deployment_checks": checks_report,
        "security_scan": scan_report,
        "compliance": compliance
    }
    
    report_file = reports_dir / "predeploy_report.json"
    with open(report_file, 'w') as f:
        json.dump(predeploy_report, f, indent=2)
    
    logger.info(f"✅ Pre-deployment report saved to {report_file}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 Deployment Readiness Summary")
    logger.info("=" * 60)
    
    if checks_passed and health['overall_status'] != 'unhealthy':
        logger.info("✅ System is ready for deployment")
        logger.info(f"   Environment: {environment}")
        logger.info(f"   Security Status: {scan_report['status']}")
        logger.info(f"   Compliance: {compliance['compliance_status']}")
        return 0
    else:
        logger.error("❌ System is NOT ready for deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())
