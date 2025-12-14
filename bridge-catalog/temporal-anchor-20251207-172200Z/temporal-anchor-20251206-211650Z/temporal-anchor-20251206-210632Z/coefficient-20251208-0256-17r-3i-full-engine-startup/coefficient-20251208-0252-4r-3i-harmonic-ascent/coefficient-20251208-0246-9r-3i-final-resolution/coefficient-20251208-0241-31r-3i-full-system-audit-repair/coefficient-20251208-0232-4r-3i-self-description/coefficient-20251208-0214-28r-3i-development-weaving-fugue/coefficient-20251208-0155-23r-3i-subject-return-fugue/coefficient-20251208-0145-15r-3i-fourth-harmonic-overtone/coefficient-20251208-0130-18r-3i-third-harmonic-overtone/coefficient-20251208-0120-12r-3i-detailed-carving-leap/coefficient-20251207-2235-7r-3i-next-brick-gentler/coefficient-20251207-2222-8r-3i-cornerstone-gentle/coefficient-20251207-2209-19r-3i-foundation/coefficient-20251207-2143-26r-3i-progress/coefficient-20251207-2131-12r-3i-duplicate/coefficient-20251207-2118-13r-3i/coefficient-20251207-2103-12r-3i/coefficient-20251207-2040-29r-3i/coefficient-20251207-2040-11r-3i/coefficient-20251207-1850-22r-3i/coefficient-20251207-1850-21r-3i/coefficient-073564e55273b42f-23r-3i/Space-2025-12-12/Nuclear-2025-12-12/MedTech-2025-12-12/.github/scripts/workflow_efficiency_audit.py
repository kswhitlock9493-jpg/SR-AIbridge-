#!/usr/bin/env python3
"""
Workflow Efficiency Audit Tool

Analyzes GitHub Actions workflows to identify optimization opportunities:
- Duplicate workflow triggers
- Missing caching strategies
- Inefficient dependency installations
- Long-running jobs
- High artifact retention periods
"""

import os
import yaml
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

def load_workflow(workflow_path: Path) -> Dict[str, Any]:
    """Load and parse a workflow YAML file."""
    try:
        with open(workflow_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Could not parse {workflow_path}: {e}")
        return {}

def analyze_workflows(workflows_dir: Path) -> Dict[str, Any]:
    """Analyze all workflows in the directory."""
    
    workflows = []
    trigger_map = defaultdict(list)
    optimization_opportunities = []
    
    # Load all workflows
    for workflow_file in workflows_dir.glob("*.yml"):
        workflow = load_workflow(workflow_file)
        if not workflow:
            continue
            
        workflow_name = workflow.get('name', workflow_file.stem)
        workflows.append({
            'file': workflow_file.name,
            'name': workflow_name,
            'config': workflow
        })
        
        # Analyze triggers
        on_config = workflow.get('on', {})
        if isinstance(on_config, dict):
            for trigger in on_config.keys():
                trigger_map[trigger].append(workflow_name)
    
    # Identify optimization opportunities
    for wf in workflows:
        config = wf['config']
        jobs = config.get('jobs', {})
        
        for job_name, job_config in jobs.items():
            steps = job_config.get('steps', [])
            
            # Check for missing caching
            has_python_install = any('pip install' in str(step.get('run', '')) for step in steps)
            has_npm_install = any('npm install' in str(step.get('run', '')) or 'npm ci' in str(step.get('run', '')) for step in steps)
            has_cache = any(step.get('uses', '').startswith('actions/cache') for step in steps)
            has_setup_cache = any(
                'cache' in str(step.get('with', {})) 
                for step in steps 
                if step.get('uses', '').startswith('actions/setup-')
            )
            
            if (has_python_install or has_npm_install) and not (has_cache or has_setup_cache):
                optimization_opportunities.append({
                    'workflow': wf['name'],
                    'job': job_name,
                    'type': 'missing_cache',
                    'severity': 'high',
                    'description': 'Dependencies installed without caching',
                    'savings_estimate': '30-60 seconds per run'
                })
            
            # Check for artifact retention
            for step in steps:
                if step.get('uses', '').startswith('actions/upload-artifact'):
                    retention_days = step.get('with', {}).get('retention-days', 90)
                    if retention_days > 7:
                        optimization_opportunities.append({
                            'workflow': wf['name'],
                            'job': job_name,
                            'type': 'high_artifact_retention',
                            'severity': 'medium',
                            'description': f'Artifact retention set to {retention_days} days (recommend 7)',
                            'savings_estimate': 'Storage cost reduction'
                        })
            
            # Check for redundant pip upgrades
            pip_upgrade_count = sum(1 for step in steps if 'pip install --upgrade pip' in str(step.get('run', '')))
            if pip_upgrade_count > 1:
                optimization_opportunities.append({
                    'workflow': wf['name'],
                    'job': job_name,
                    'type': 'redundant_pip_upgrade',
                    'severity': 'low',
                    'description': f'Pip upgraded {pip_upgrade_count} times in same job',
                    'savings_estimate': '5-10 seconds per run'
                })
            
            # Check for missing timeout
            if 'timeout-minutes' not in job_config:
                optimization_opportunities.append({
                    'workflow': wf['name'],
                    'job': job_name,
                    'type': 'missing_timeout',
                    'severity': 'medium',
                    'description': 'No timeout set (default 360 minutes)',
                    'savings_estimate': 'Prevent runaway jobs'
                })
    
    # Identify duplicate triggers
    duplicate_triggers = {
        trigger: workflows_list 
        for trigger, workflows_list in trigger_map.items() 
        if len(workflows_list) > 3 and trigger in ['push', 'pull_request']
    }
    
    return {
        'total_workflows': len(workflows),
        'trigger_summary': dict(trigger_map),
        'duplicate_triggers': duplicate_triggers,
        'optimization_opportunities': optimization_opportunities,
        'workflows': workflows
    }

def generate_report(analysis: Dict[str, Any]) -> str:
    """Generate a human-readable report."""
    
    report = []
    report.append("=" * 80)
    report.append("GitHub Actions Workflow Efficiency Audit Report")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append(f"📊 SUMMARY")
    report.append(f"Total workflows: {analysis['total_workflows']}")
    report.append(f"Optimization opportunities found: {len(analysis['optimization_opportunities'])}")
    report.append("")
    
    # Trigger analysis
    report.append("🎯 WORKFLOW TRIGGERS")
    for trigger, workflows in sorted(analysis['trigger_summary'].items()):
        report.append(f"  {trigger}: {len(workflows)} workflows")
    report.append("")
    
    # Duplicate triggers (potential consolidation opportunities)
    if analysis['duplicate_triggers']:
        report.append("⚠️  DUPLICATE TRIGGERS (Consider consolidation)")
        for trigger, workflows in analysis['duplicate_triggers'].items():
            report.append(f"  {trigger}:")
            for wf in workflows[:5]:  # Show first 5
                report.append(f"    - {wf}")
            if len(workflows) > 5:
                report.append(f"    ... and {len(workflows) - 5} more")
        report.append("")
    
    # Optimization opportunities by severity
    report.append("🔧 OPTIMIZATION OPPORTUNITIES")
    
    for severity in ['high', 'medium', 'low']:
        opps = [o for o in analysis['optimization_opportunities'] if o['severity'] == severity]
        if opps:
            report.append(f"  {severity.upper()} Priority: {len(opps)} issues")
            
            # Group by type
            by_type = defaultdict(list)
            for opp in opps:
                by_type[opp['type']].append(opp)
            
            for opp_type, items in sorted(by_type.items()):
                report.append(f"    {opp_type.replace('_', ' ').title()}: {len(items)} workflows")
                for item in items[:3]:  # Show first 3
                    report.append(f"      - {item['workflow']} ({item['job']})")
                    report.append(f"        {item['description']}")
                    report.append(f"        Savings: {item['savings_estimate']}")
                if len(items) > 3:
                    report.append(f"      ... and {len(items) - 3} more")
            report.append("")
    
    # Recommendations
    report.append("💡 RECOMMENDATIONS")
    report.append("  1. Add caching to workflows with dependency installation")
    report.append("  2. Reduce artifact retention from 90 days to 7 days")
    report.append("  3. Consolidate workflows with duplicate triggers")
    report.append("  4. Add timeout-minutes to all jobs (recommend 10-15 minutes)")
    report.append("  5. Consider moving heavy compute to self-hosted runners")
    report.append("")
    
    # Expected savings
    high_priority = len([o for o in analysis['optimization_opportunities'] if o['severity'] == 'high'])
    report.append("📈 ESTIMATED IMPACT")
    report.append(f"  High-priority fixes: {high_priority}")
    report.append(f"  Potential time savings: {high_priority * 45} seconds per workflow run")
    report.append(f"  With 43 pushes/month: ~{(high_priority * 45 * 43) / 60:.1f} minutes saved")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)

def main():
    """Main entry point."""
    
    # Find workflows directory
    repo_root = Path(__file__).parent.parent.parent
    workflows_dir = repo_root / '.github' / 'workflows'
    
    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found at {workflows_dir}")
        return 1
    
    print(f"Analyzing workflows in {workflows_dir}...")
    print()
    
    # Analyze workflows
    analysis = analyze_workflows(workflows_dir)
    
    # Generate and print report
    report = generate_report(analysis)
    print(report)
    
    # Save detailed JSON report
    output_dir = repo_root / 'bridge_backend' / 'diagnostics'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'workflow_efficiency_audit.json'
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"Detailed report saved to: {output_file}")
    
    return 0

if __name__ == '__main__':
    exit(main())
