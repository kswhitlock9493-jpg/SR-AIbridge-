#!/usr/bin/env python3
"""
Extract security metrics from predeploy report for GitHub Actions summary.
"""
import json
import os
import sys

def main():
    report_file = '.alik/predeploy_report.json'
    
    if not os.path.exists(report_file):
        print("No predeploy report found", file=sys.stderr)
        return 1
    
    with open(report_file) as f:
        report = json.load(f)
    
    summary = []
    summary.append("| Component | Status |")
    summary.append("|-----------|--------|")
    
    # Health check
    health = report.get('health_check', {})
    overall = health.get('overall_status', 'unknown')
    summary.append(f"| Overall Health | {overall} |")
    
    # Pre-deployment checks
    checks = report.get('pre_deployment_checks', {})
    overall_checks = checks.get('overall', 'UNKNOWN')
    summary.append(f"| Pre-deployment Checks | {overall_checks} |")
    
    # Security scan
    scan = report.get('security_scan', {})
    scan_status = scan.get('status', 'UNKNOWN')
    total_findings = scan.get('total_findings', 0)
    risk_score = scan.get('risk_score', 0)
    summary.append(f"| Security Scan | {scan_status} |")
    summary.append(f"| Total Findings | {total_findings} |")
    summary.append(f"| Risk Score | {risk_score} |")
    
    # Compliance
    compliance = report.get('compliance', {})
    compliance_status = compliance.get('compliance_status', 'UNKNOWN')
    summary.append(f"| Compliance | {compliance_status} |")
    
    github_summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if github_summary:
        with open(github_summary, 'a') as f:
            f.write('\n'.join(summary))
            f.write('\n\n')
            
            # Findings by severity
            if scan.get('findings_by_severity'):
                f.write("#### Security Findings\n\n")
                findings = scan['findings_by_severity']
                if findings.get('critical', 0) > 0:
                    f.write(f"- ❌ **Critical**: {findings['critical']}\n")
                if findings.get('high', 0) > 0:
                    f.write(f"- ⚠️ **High**: {findings['high']}\n")
                if findings.get('medium', 0) > 0:
                    f.write(f"- ℹ️ **Medium**: {findings['medium']}\n")
                if findings.get('low', 0) > 0:
                    f.write(f"- ℹ️ **Low**: {findings['low']}\n")
    else:
        # Print to stdout for local testing
        print('\n'.join(summary))
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
