#!/usr/bin/env python3
"""
Check for critical security failures in predeploy report.
"""
import json
import os
import sys

def main():
    report_file = '.alik/predeploy_report.json'
    
    if not os.path.exists(report_file):
        print("❌ No predeploy report found", file=sys.stderr)
        return 1
    
    with open(report_file) as f:
        report = json.load(f)
    
    # Check for critical security findings
    scan = report.get('security_scan', {})
    findings = scan.get('findings_by_severity', {})
    
    if findings.get('critical', 0) > 0:
        print(f"❌ Critical security findings detected: {findings['critical']}")
        return 1
    
    # Check compliance for production
    environment = report.get('environment', 'unknown')
    if environment == 'production':
        compliance = report.get('compliance', {})
        if compliance.get('compliance_status') != 'COMPLIANT':
            print(f"❌ Production deployment requires COMPLIANT status")
            return 1
    
    print("✅ Security checks passed")
    return 0

if __name__ == '__main__':
    sys.exit(main())
