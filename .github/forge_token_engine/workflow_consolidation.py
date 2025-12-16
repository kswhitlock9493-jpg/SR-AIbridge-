#!/usr/bin/env python3
"""
Workflow Consolidation Analyzer
Identifies redundant workflows and suggests optimizations to reduce GitHub Actions usage.

This tool analyzes all workflows in .github/workflows/ and provides actionable recommendations
for reducing compute minutes through consolidation and optimization.
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class WorkflowAnalysis:
    """Analysis results for a single workflow"""
    name: str
    file_path: str
    triggers: List[str]
    jobs: List[str]
    estimated_minutes: int
    runs_per_month: int
    monthly_minutes: int
    can_consolidate_with: List[str]
    optimization_potential: str


class WorkflowConsolidationAnalyzer:
    """
    Analyzes GitHub Actions workflows to identify:
    1. Duplicate/redundant workflows
    2. Workflows that could be consolidated
    3. Inefficient trigger configurations
    4. Opportunities for caching and optimization
    """
    
    def __init__(self, workflows_dir: str = ".github/workflows"):
        self.workflows_dir = Path(workflows_dir)
        self.workflows = {}
        self.analyses = []
    
    def analyze_all_workflows(self) -> Dict:
        """Analyze all workflows and generate optimization recommendations"""
        if not self.workflows_dir.exists():
            return {"error": "Workflows directory not found"}
        
        # Load all workflow files
        for workflow_file in self.workflows_dir.glob("*.yml"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)
                    if workflow:
                        self.workflows[workflow_file.name] = workflow
            except Exception as e:
                print(f"Warning: Could not parse {workflow_file}: {e}")
        
        # Analyze each workflow
        for filename, workflow in self.workflows.items():
            analysis = self._analyze_workflow(filename, workflow)
            self.analyses.append(analysis)
        
        # Generate consolidation recommendations
        return self._generate_recommendations()
    
    def _analyze_workflow(self, filename: str, workflow: Dict) -> WorkflowAnalysis:
        """Analyze a single workflow"""
        name = workflow.get('name', filename)
        
        # Analyze triggers
        triggers = []
        on_config = workflow.get('on', {})
        if isinstance(on_config, str):
            triggers = [on_config]
        elif isinstance(on_config, list):
            triggers = on_config
        elif isinstance(on_config, dict):
            triggers = list(on_config.keys())
        
        # Count jobs
        jobs = list(workflow.get('jobs', {}).keys())
        
        # Estimate minutes (rough estimate based on typical job durations)
        estimated_minutes = len(jobs) * 5  # Assume 5 min per job average
        
        # Estimate runs per month based on triggers
        runs_per_month = self._estimate_monthly_runs(triggers)
        monthly_minutes = estimated_minutes * runs_per_month
        
        # Find consolidation opportunities
        can_consolidate = self._find_consolidation_opportunities(filename, workflow)
        
        # Determine optimization potential
        if monthly_minutes > 1000:
            opt_potential = "HIGH"
        elif monthly_minutes > 300:
            opt_potential = "MEDIUM"
        else:
            opt_potential = "LOW"
        
        return WorkflowAnalysis(
            name=name,
            file_path=filename,
            triggers=triggers,
            jobs=jobs,
            estimated_minutes=estimated_minutes,
            runs_per_month=runs_per_month,
            monthly_minutes=monthly_minutes,
            can_consolidate_with=can_consolidate,
            optimization_potential=opt_potential
        )
    
    def _estimate_monthly_runs(self, triggers: List[str]) -> int:
        """Estimate how many times a workflow runs per month"""
        if not triggers:
            return 0
        
        runs = 0
        for trigger in triggers:
            if trigger == 'push':
                runs += 43  # User mentioned 43 pushes/month
            elif trigger == 'pull_request':
                runs += 10  # Estimate
            elif trigger == 'schedule':
                # Would need to parse cron, assume daily
                runs += 30
            elif trigger == 'workflow_dispatch':
                runs += 2  # Manual triggers
        
        return runs
    
    def _find_consolidation_opportunities(self, filename: str, workflow: Dict) -> List[str]:
        """Find workflows that could be consolidated with this one"""
        opportunities = []
        
        current_jobs = set(workflow.get('jobs', {}).keys())
        current_triggers = set(self._get_triggers(workflow))
        
        for other_file, other_workflow in self.workflows.items():
            if other_file == filename:
                continue
            
            other_jobs = set(other_workflow.get('jobs', {}).keys())
            other_triggers = set(self._get_triggers(other_workflow))
            
            # Check if workflows have similar triggers
            if len(current_triggers & other_triggers) > 0:
                # Check if jobs don't overlap
                if len(current_jobs & other_jobs) == 0:
                    opportunities.append(other_file)
        
        return opportunities
    
    def _get_triggers(self, workflow: Dict) -> List[str]:
        """Extract trigger list from workflow"""
        on_config = workflow.get('on', {})
        if isinstance(on_config, str):
            return [on_config]
        elif isinstance(on_config, list):
            return on_config
        elif isinstance(on_config, dict):
            return list(on_config.keys())
        return []
    
    def _generate_recommendations(self) -> Dict:
        """Generate actionable recommendations"""
        total_monthly_minutes = sum(a.monthly_minutes for a in self.analyses)
        
        # Sort by monthly minutes (highest first)
        sorted_analyses = sorted(
            self.analyses,
            key=lambda a: a.monthly_minutes,
            reverse=True
        )
        
        # Find top optimization targets
        high_impact = [a for a in sorted_analyses if a.optimization_potential == "HIGH"]
        
        # Generate consolidation groups
        consolidation_groups = self._generate_consolidation_groups()
        
        # Calculate potential savings
        potential_savings = self._calculate_potential_savings(consolidation_groups)
        
        return {
            "summary": {
                "total_workflows": len(self.workflows),
                "total_monthly_minutes": total_monthly_minutes,
                "estimated_monthly_cost": round(total_monthly_minutes * 0.008, 2),
                "high_impact_workflows": len(high_impact),
                "potential_savings_minutes": potential_savings,
                "potential_savings_dollars": round(potential_savings * 0.008, 2)
            },
            "workflows": [
                {
                    "name": a.name,
                    "file": a.file_path,
                    "monthly_minutes": a.monthly_minutes,
                    "optimization_potential": a.optimization_potential,
                    "recommendations": self._get_workflow_recommendations(a)
                }
                for a in sorted_analyses[:10]  # Top 10
            ],
            "consolidation_opportunities": consolidation_groups,
            "quick_wins": self._identify_quick_wins()
        }
    
    def _generate_consolidation_groups(self) -> List[Dict]:
        """Generate groups of workflows that should be consolidated"""
        groups = []
        processed = set()
        
        for analysis in self.analyses:
            if analysis.file_path in processed:
                continue
            
            if analysis.can_consolidate_with:
                group = {
                    "primary": analysis.file_path,
                    "can_merge": analysis.can_consolidate_with,
                    "combined_minutes": analysis.monthly_minutes,
                    "savings_minutes": 0
                }
                
                for other in analysis.can_consolidate_with:
                    processed.add(other)
                    # Find the other analysis
                    other_analysis = next(
                        (a for a in self.analyses if a.file_path == other),
                        None
                    )
                    if other_analysis:
                        group["combined_minutes"] += other_analysis.monthly_minutes
                        # Consolidation saves ~30% due to shared setup
                        group["savings_minutes"] += int(other_analysis.monthly_minutes * 0.3)
                
                groups.append(group)
                processed.add(analysis.file_path)
        
        return sorted(groups, key=lambda g: g["savings_minutes"], reverse=True)
    
    def _calculate_potential_savings(self, consolidation_groups: List[Dict]) -> int:
        """Calculate total potential savings from consolidation"""
        return sum(g["savings_minutes"] for g in consolidation_groups)
    
    def _get_workflow_recommendations(self, analysis: WorkflowAnalysis) -> List[str]:
        """Get specific recommendations for a workflow"""
        recommendations = []
        
        if analysis.monthly_minutes > 500:
            recommendations.append("HIGH USAGE: Consider moving to self-hosted runner")
        
        if 'push' in analysis.triggers and 'pull_request' in analysis.triggers:
            recommendations.append("Duplicate triggers: Use paths filter to avoid running on both")
        
        if len(analysis.can_consolidate_with) > 0:
            recommendations.append(
                f"Can consolidate with: {', '.join(analysis.can_consolidate_with)}"
            )
        
        if analysis.runs_per_month > 40:
            recommendations.append("High frequency: Add path filters or conditional triggers")
        
        return recommendations
    
    def _identify_quick_wins(self) -> List[Dict]:
        """Identify quick optimization wins"""
        quick_wins = []
        
        # Find workflows with duplicate triggers
        for analysis in self.analyses:
            if 'push' in analysis.triggers and 'pull_request' in analysis.triggers:
                quick_wins.append({
                    "workflow": analysis.file_path,
                    "issue": "Duplicate push/PR triggers",
                    "fix": "Add paths filter or remove one trigger",
                    "estimated_savings_minutes": int(analysis.monthly_minutes * 0.4)
                })
        
        # Find workflows that run on schedule but could be on-demand
        for analysis in self.analyses:
            if 'schedule' in analysis.triggers:
                quick_wins.append({
                    "workflow": analysis.file_path,
                    "issue": "Scheduled runs (may be unnecessary)",
                    "fix": "Convert to workflow_dispatch or reduce frequency",
                    "estimated_savings_minutes": int(analysis.monthly_minutes * 0.5)
                })
        
        return sorted(quick_wins, key=lambda w: w["estimated_savings_minutes"], reverse=True)[:5]


def main():
    """Main execution"""
    print("\n" + "="*70)
    print("WORKFLOW CONSOLIDATION ANALYSIS")
    print("="*70)
    
    analyzer = WorkflowConsolidationAnalyzer()
    results = analyzer.analyze_all_workflows()
    
    print(json.dumps(results, indent=2))
    
    # Print summary
    summary = results.get('summary', {})
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total Workflows: {summary.get('total_workflows')}")
    print(f"Monthly Minutes: {summary.get('total_monthly_minutes')}")
    print(f"Estimated Cost: ${summary.get('estimated_monthly_cost')}")
    print(f"\n💰 Potential Savings: {summary.get('potential_savings_minutes')} minutes/month")
    print(f"   = ${summary.get('potential_savings_dollars')}/month")
    
    # Print quick wins
    quick_wins = results.get('quick_wins', [])
    if quick_wins:
        print("\n" + "="*70)
        print("🎯 QUICK WINS")
        print("="*70)
        for i, win in enumerate(quick_wins, 1):
            print(f"\n{i}. {win['workflow']}")
            print(f"   Issue: {win['issue']}")
            print(f"   Fix: {win['fix']}")
            print(f"   Savings: {win['estimated_savings_minutes']} min/month")


if __name__ == "__main__":
    main()
