#!/usr/bin/env python3
"""
Budget Monitor - Real-time monitoring and alerting for GitHub Actions costs

This script:
1. Monitors current month's GitHub Actions spending
2. Calculates projected end-of-month cost
3. Sends alerts at threshold crossings
4. Triggers automatic cost reduction measures

Run this regularly (e.g., via cron or GitHub Actions) to maintain budget compliance.
"""

import os
import json
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# Import our financial modules
try:
    from financial_rescue import FinancialRescueEngine, BudgetThreshold
except ImportError:
    # If running from repo root, adjust path
    sys.path.insert(0, str(Path(__file__).parent))
    from financial_rescue import FinancialRescueEngine, BudgetThreshold

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BudgetMonitor:
    """Real-time budget monitoring and alerting"""
    
    def __init__(self):
        self.rescue_engine = FinancialRescueEngine()
        self.monitor_log = Path('.github/forge_token_engine/monitor_log.json')
        self.alerts = self._load_alerts()
        
    def _load_alerts(self) -> Dict:
        """Load alert history"""
        if self.monitor_log.exists():
            with open(self.monitor_log, 'r') as f:
                return json.load(f)
        return {
            'alerts_sent': [],
            'last_check': None
        }
    
    def _save_alerts(self):
        """Save alert history"""
        self.monitor_log.parent.mkdir(parents=True, exist_ok=True)
        with open(self.monitor_log, 'w') as f:
            json.dump(self.alerts, f, indent=2)
    
    def check_budget_status(self) -> Dict:
        """Check current budget status and return analysis"""
        status = self.rescue_engine.get_financial_status()
        
        # Calculate days remaining in month
        now = datetime.now()
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)
        
        days_remaining = (next_month - now).days
        days_elapsed = now.day
        
        # Calculate burn rate and projection
        if days_elapsed > 0:
            burn_rate = status['current_spend'] / days_elapsed
            projected_total = status['current_spend'] + (burn_rate * days_remaining)
        else:
            burn_rate = 0
            projected_total = status['current_spend']
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'current_spend': status['current_spend'],
            'budget_limit': status['budget_limit'],
            'budget_remaining': status['budget_remaining'],
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'burn_rate_per_day': round(burn_rate, 2),
            'projected_month_end': round(projected_total, 2),
            'projected_overage': round(max(0, projected_total - status['budget_limit']), 2),
            'protection_level': status['protection_level'],
            'health_status': self._calculate_health_status(status, projected_total)
        }
        
        return analysis
    
    def _calculate_health_status(self, status: Dict, projected_total: float) -> str:
        """Calculate overall budget health status"""
        if status['emergency_mode']:
            return "CRITICAL - Emergency Bypass Active"
        elif status['sovereign_mode']:
            return "WARNING - Sovereign Mode Active"
        elif projected_total > status['budget_limit']:
            return "CAUTION - Projected to Exceed Budget"
        elif status['utilization_percentage'] > 80:
            return "ATTENTION - High Budget Utilization"
        else:
            return "HEALTHY - On Track"
    
    def send_alert(self, alert_type: str, details: Dict):
        """Send budget alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'type': alert_type,
            'details': details
        }
        
        self.alerts['alerts_sent'].append(alert)
        self._save_alerts()
        
        # In production, this would integrate with notification systems
        # (email, Slack, Discord, GitHub Issues, etc.)
        logger.warning(f"🚨 ALERT: {alert_type}")
        logger.warning(f"   Details: {json.dumps(details, indent=2)}")
    
    def monitor_and_alert(self) -> Dict:
        """Main monitoring function - check status and send alerts if needed"""
        analysis = self.check_budget_status()
        
        # Check for alert conditions
        if analysis['health_status'].startswith('CRITICAL'):
            self.send_alert('CRITICAL_BUDGET_EMERGENCY', {
                'current_spend': analysis['current_spend'],
                'protection_level': analysis['protection_level'],
                'message': 'Emergency bypass activated - all workflows using sovereign infrastructure'
            })
        
        elif analysis['health_status'].startswith('WARNING'):
            self.send_alert('WARNING_SOVEREIGN_ACTIVE', {
                'current_spend': analysis['current_spend'],
                'projected_total': analysis['projected_month_end'],
                'message': 'Sovereign mode activated - workflows routing to free providers'
            })
        
        elif analysis['projected_overage'] > 0:
            self.send_alert('CAUTION_PROJECTED_OVERAGE', {
                'current_spend': analysis['current_spend'],
                'projected_total': analysis['projected_month_end'],
                'projected_overage': analysis['projected_overage'],
                'burn_rate': analysis['burn_rate_per_day'],
                'message': f'Projected to exceed budget by ${analysis["projected_overage"]:.2f}'
            })
        
        elif analysis['budget_remaining'] < 10:
            self.send_alert('ATTENTION_LOW_BUDGET', {
                'budget_remaining': analysis['budget_remaining'],
                'days_remaining': analysis['days_remaining'],
                'message': f'Only ${analysis["budget_remaining"]:.2f} remaining in budget'
            })
        
        # Update last check time
        self.alerts['last_check'] = datetime.now().isoformat()
        self._save_alerts()
        
        return analysis
    
    def generate_monitoring_report(self) -> str:
        """Generate comprehensive monitoring report"""
        analysis = self.check_budget_status()
        
        report = []
        report.append("=" * 80)
        report.append("📊 BUDGET MONITORING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Current status
        report.append("💰 CURRENT STATUS")
        report.append(f"   Current Spend: ${analysis['current_spend']}")
        report.append(f"   Budget Limit: ${analysis['budget_limit']}")
        report.append(f"   Remaining: ${analysis['budget_remaining']}")
        report.append("")
        
        # Time tracking
        report.append("📅 TIME TRACKING")
        report.append(f"   Days Elapsed: {analysis['days_elapsed']}")
        report.append(f"   Days Remaining: {analysis['days_remaining']}")
        report.append("")
        
        # Spend rate analysis
        report.append("📈 SPEND RATE ANALYSIS")
        report.append(f"   Burn Rate: ${analysis['burn_rate_per_day']:.2f}/day")
        report.append(f"   Projected Month-End: ${analysis['projected_month_end']:.2f}")
        
        if analysis['projected_overage'] > 0:
            report.append(f"   ⚠️  Projected Overage: ${analysis['projected_overage']:.2f}")
        else:
            savings = analysis['budget_limit'] - analysis['projected_month_end']
            report.append(f"   ✅ Projected Under Budget: ${savings:.2f}")
        
        report.append("")
        
        # Health status
        report.append("🏥 HEALTH STATUS")
        report.append(f"   {analysis['health_status']}")
        report.append(f"   Protection Level: {analysis['protection_level']}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        
        if analysis['health_status'].startswith('CRITICAL'):
            report.append("   🚨 Emergency measures in effect")
            report.append("      → All GitHub Actions blocked")
            report.append("      → Use sovereign infrastructure only")
        
        elif analysis['health_status'].startswith('WARNING'):
            report.append("   ⚠️  Cost reduction measures active")
            report.append("      → New workflows use sovereign providers")
            report.append("      → Monitor daily for improvement")
        
        elif analysis['projected_overage'] > 0:
            report.append("   ⚠️  Immediate optimization needed")
            report.append("      → Run emergency cost containment")
            report.append("      → Enable workflow caching")
            report.append("      → Consider sovereign provider activation")
        
        else:
            report.append("   ✅ Continue current practices")
            report.append("      → Budget on track")
            report.append("      → No immediate action needed")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main monitoring execution"""
    monitor = BudgetMonitor()
    
    # Generate and display report
    report = monitor.generate_monitoring_report()
    print(report)
    
    # Run monitoring and alerting
    print("\n🔍 Running budget monitoring...")
    analysis = monitor.monitor_and_alert()
    
    print(f"\n✅ Monitoring complete")
    print(f"💰 Current spend: ${analysis['current_spend']:.2f}")
    print(f"📊 Projected total: ${analysis['projected_month_end']:.2f}")
    print(f"🏥 Health: {analysis['health_status']}")
    
    # Return exit code based on health
    if analysis['health_status'].startswith('CRITICAL'):
        sys.exit(2)
    elif analysis['health_status'].startswith('WARNING'):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
