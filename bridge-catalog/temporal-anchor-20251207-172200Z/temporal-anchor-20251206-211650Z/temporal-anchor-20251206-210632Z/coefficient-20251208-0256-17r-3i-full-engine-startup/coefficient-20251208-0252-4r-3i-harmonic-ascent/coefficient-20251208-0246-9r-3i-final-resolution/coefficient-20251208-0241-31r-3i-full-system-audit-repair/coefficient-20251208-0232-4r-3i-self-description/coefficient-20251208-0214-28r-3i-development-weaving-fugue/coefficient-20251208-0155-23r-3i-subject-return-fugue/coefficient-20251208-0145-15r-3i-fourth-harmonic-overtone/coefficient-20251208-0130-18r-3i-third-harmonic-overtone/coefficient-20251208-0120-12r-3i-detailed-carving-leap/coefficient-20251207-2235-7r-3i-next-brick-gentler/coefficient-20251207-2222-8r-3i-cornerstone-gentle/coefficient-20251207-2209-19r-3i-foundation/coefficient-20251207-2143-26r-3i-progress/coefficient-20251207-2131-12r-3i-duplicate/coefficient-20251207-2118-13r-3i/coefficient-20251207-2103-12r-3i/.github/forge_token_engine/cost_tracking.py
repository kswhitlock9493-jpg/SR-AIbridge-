#!/usr/bin/env python3
"""
Cost Tracking and Reporting Script
Tracks GitHub Actions usage and reports on cost savings from sovereign infrastructure.

This script can be run:
1. Locally to check current costs
2. As a GitHub Action to track over time
3. As a cron job for regular monitoring
"""

import os
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional


class CostTracker:
    """Track and report on GitHub Actions costs and savings"""
    
    def __init__(self, tracking_file: str = ".github/forge_token_engine/cost_tracking.json"):
        self.tracking_file = Path(tracking_file)
        self.data = self._load_tracking_data()
    
    def _load_tracking_data(self) -> Dict:
        """Load historical tracking data"""
        if self.tracking_file.exists():
            try:
                with open(self.tracking_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "start_date": datetime.now().isoformat(),
            "baseline_monthly_cost": 75.0,  # User's reported cost
            "baseline_monthly_minutes": 3010,  # User's reported usage
            "monthly_records": []
        }
    
    def _save_tracking_data(self):
        """Save tracking data to file"""
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_month(
        self,
        github_minutes: int = 0,
        self_hosted_minutes: int = 0,
        render_minutes: int = 0,
        netlify_minutes: int = 0,
        vercel_minutes: int = 0
    ):
        """Record costs for a month"""
        # Calculate costs
        github_cost = github_minutes * 0.008  # Standard rate
        
        total_minutes = (
            github_minutes + 
            self_hosted_minutes + 
            render_minutes + 
            netlify_minutes + 
            vercel_minutes
        )
        
        # What it would have cost on GitHub Actions
        hypothetical_github_cost = total_minutes * 0.008
        
        # Actual savings
        savings = hypothetical_github_cost - github_cost
        
        record = {
            "date": datetime.now().isoformat(),
            "month": datetime.now().strftime("%Y-%m"),
            "minutes": {
                "github_actions": github_minutes,
                "self_hosted": self_hosted_minutes,
                "render_free": render_minutes,
                "netlify_free": netlify_minutes,
                "vercel_free": vercel_minutes,
                "total": total_minutes
            },
            "costs": {
                "actual_github_cost": round(github_cost, 2),
                "hypothetical_github_cost": round(hypothetical_github_cost, 2),
                "savings": round(savings, 2),
                "savings_percentage": round((savings / hypothetical_github_cost * 100) if hypothetical_github_cost > 0 else 0, 1)
            }
        }
        
        self.data["monthly_records"].append(record)
        self._save_tracking_data()
        
        return record
    
    def get_current_month_record(self) -> Optional[Dict]:
        """Get the record for the current month"""
        current_month = datetime.now().strftime("%Y-%m")
        
        for record in reversed(self.data["monthly_records"]):
            if record["month"] == current_month:
                return record
        
        return None
    
    def get_total_savings(self) -> Dict:
        """Calculate total savings since tracking started"""
        if not self.data["monthly_records"]:
            return {
                "total_months": 0,
                "total_savings": 0,
                "average_monthly_savings": 0
            }
        
        total_savings = sum(
            record["costs"]["savings"] 
            for record in self.data["monthly_records"]
        )
        
        months = len(self.data["monthly_records"])
        
        return {
            "total_months": months,
            "total_savings": round(total_savings, 2),
            "average_monthly_savings": round(total_savings / months if months > 0 else 0, 2),
            "start_date": self.data["start_date"],
            "baseline_monthly_cost": self.data["baseline_monthly_cost"]
        }
    
    def generate_report(self) -> str:
        """Generate a comprehensive cost report"""
        current = self.get_current_month_record()
        total = self.get_total_savings()
        
        report = []
        report.append("=" * 70)
        report.append("💰 SOVEREIGN FINANCIAL INDEPENDENCE REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Baseline
        report.append("📊 BASELINE (Before Sovereign Infrastructure)")
        report.append(f"   Monthly Cost: ${self.data['baseline_monthly_cost']}")
        report.append(f"   Monthly Minutes: {self.data['baseline_monthly_minutes']}")
        report.append("")
        
        # Current month
        if current:
            report.append(f"📅 CURRENT MONTH ({current['month']})")
            report.append("   Minutes Used:")
            for provider, minutes in current["minutes"].items():
                if minutes > 0 and provider != "total":
                    report.append(f"     - {provider}: {minutes} min")
            report.append(f"     Total: {current['minutes']['total']} min")
            report.append("")
            report.append("   Costs:")
            report.append(f"     Actual GitHub Cost: ${current['costs']['actual_github_cost']}")
            report.append(f"     Would Have Cost: ${current['costs']['hypothetical_github_cost']}")
            report.append(f"     💰 Savings: ${current['costs']['savings']} ({current['costs']['savings_percentage']}%)")
            report.append("")
        else:
            report.append("📅 CURRENT MONTH: No data recorded yet")
            report.append("")
        
        # Total savings
        if total["total_months"] > 0:
            report.append(f"🎯 TOTAL SAVINGS (Over {total['total_months']} months)")
            report.append(f"   Total Saved: ${total['total_savings']}")
            report.append(f"   Average/Month: ${total['average_monthly_savings']}")
            report.append(f"   Tracking Since: {total['start_date'][:10]}")
            
            # Calculate ROI if self-hosted was set up
            if current and current['minutes']['self_hosted'] > 0:
                report.append("")
                report.append("   💡 Self-Hosted ROI:")
                report.append(f"      Setup Cost: ~$0 (using existing infrastructure)")
                report.append(f"      Monthly Savings: ${total['average_monthly_savings']}")
                report.append(f"      Payback Period: Immediate")
            report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS")
        if current:
            github_minutes = current['minutes']['github_actions']
            if github_minutes > 100:
                report.append("   ⚠️  Still using significant GitHub Actions minutes")
                report.append("   → Consider setting up self-hosted runner")
            
            if current['minutes']['self_hosted'] == 0:
                report.append("   💰 Not using self-hosted runners yet")
                report.append("   → Potential additional savings: $" + 
                            str(round(github_minutes * 0.008, 2)))
        else:
            report.append("   → Record your first month's usage to track savings")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def main():
    """Main CLI interface"""
    tracker = CostTracker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--record":
        # Record usage from command line
        # Usage: --record [github_min] [self_hosted_min] [render_min] [netlify_min] [vercel_min]
        args = sys.argv[2:]
        
        github_min = int(args[0]) if len(args) > 0 else 0
        self_hosted_min = int(args[1]) if len(args) > 1 else 0
        render_min = int(args[2]) if len(args) > 2 else 0
        netlify_min = int(args[3]) if len(args) > 3 else 0
        vercel_min = int(args[4]) if len(args) > 4 else 0
        
        record = tracker.record_month(
            github_minutes=github_min,
            self_hosted_minutes=self_hosted_min,
            render_minutes=render_min,
            netlify_minutes=netlify_min,
            vercel_minutes=vercel_min
        )
        
        print(f"✅ Recorded usage for {record['month']}")
        print(f"💰 Savings this month: ${record['costs']['savings']}")
    
    # Always show report
    print(tracker.generate_report())
    
    # Show usage tracking file location
    print(f"\n📁 Tracking data: {tracker.tracking_file}")


if __name__ == "__main__":
    main()
