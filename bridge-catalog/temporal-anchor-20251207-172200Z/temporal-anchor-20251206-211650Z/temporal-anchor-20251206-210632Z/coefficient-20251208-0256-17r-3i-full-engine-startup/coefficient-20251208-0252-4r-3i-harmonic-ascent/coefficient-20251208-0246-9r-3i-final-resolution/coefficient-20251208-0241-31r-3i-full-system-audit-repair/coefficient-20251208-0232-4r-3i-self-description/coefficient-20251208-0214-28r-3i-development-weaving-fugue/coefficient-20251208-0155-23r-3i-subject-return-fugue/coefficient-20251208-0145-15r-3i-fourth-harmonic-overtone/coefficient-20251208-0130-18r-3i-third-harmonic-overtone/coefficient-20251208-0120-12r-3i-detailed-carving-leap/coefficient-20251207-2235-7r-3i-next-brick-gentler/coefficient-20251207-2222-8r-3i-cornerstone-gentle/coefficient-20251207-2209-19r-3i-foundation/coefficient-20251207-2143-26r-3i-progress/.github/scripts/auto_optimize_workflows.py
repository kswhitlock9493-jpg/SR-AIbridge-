#!/usr/bin/env python3
"""
Workflow Auto-Optimizer

Automatically applies common optimizations to GitHub Actions workflows:
- Adds pip caching to Python setup
- Adds npm caching to Node setup  
- Reduces artifact retention to 7 days
- Adds timeouts to jobs
"""

import os
import sys
import yaml
import re
from pathlib import Path
from typing import Dict, Any, List

def add_pip_cache_to_workflow(workflow: Dict[str, Any]) -> bool:
    """Add pip caching to workflows using actions/setup-python."""
    modified = False
    jobs = workflow.get('jobs', {})
    
    for job_name, job_config in jobs.items():
        steps = job_config.get('steps', [])
        
        for i, step in enumerate(steps):
            # Check if this is a setup-python step
            uses = step.get('uses', '')
            if 'actions/setup-python' in uses:
                with_config = step.get('with', {})
                
                # Add cache if not present
                if 'cache' not in with_config:
                    with_config['cache'] = 'pip'
                    step['with'] = with_config
                    modified = True
                    
                    # Try to find requirements.txt path
                    for j in range(i, min(i+10, len(steps))):
                        run_cmd = steps[j].get('run', '')
                        if 'pip install -r' in run_cmd:
                            # Extract requirements path
                            match = re.search(r'pip install -r\s+(\S+)', run_cmd)
                            if match:
                                req_path = match.group(1)
                                with_config['cache-dependency-path'] = req_path
                                step['with'] = with_config
                            break
    
    return modified

def add_npm_cache_to_workflow(workflow: Dict[str, Any]) -> bool:
    """Add npm caching to workflows using actions/setup-node."""
    modified = False
    jobs = workflow.get('jobs', {})
    
    for job_name, job_config in jobs.items():
        steps = job_config.get('steps', [])
        
        for i, step in enumerate(steps):
            uses = step.get('uses', '')
            if 'actions/setup-node' in uses:
                with_config = step.get('with', {})
                
                # Add cache if not present
                if 'cache' not in with_config:
                    with_config['cache'] = 'npm'
                    step['with'] = with_config
                    modified = True
    
    return modified

def reduce_artifact_retention(workflow: Dict[str, Any]) -> bool:
    """Reduce artifact retention to 7 days."""
    modified = False
    jobs = workflow.get('jobs', {})
    
    for job_name, job_config in jobs.items():
        steps = job_config.get('steps', [])
        
        for step in steps:
            uses = step.get('uses', '')
            if 'actions/upload-artifact' in uses:
                with_config = step.get('with', {})
                current_retention = with_config.get('retention-days', 90)
                
                if current_retention > 7:
                    with_config['retention-days'] = 7
                    step['with'] = with_config
                    modified = True
    
    return modified

def add_job_timeouts(workflow: Dict[str, Any]) -> bool:
    """Add timeout-minutes to jobs that don't have one."""
    modified = False
    jobs = workflow.get('jobs', {})
    
    for job_name, job_config in jobs.items():
        if 'timeout-minutes' not in job_config:
            # Default timeout: 15 minutes for most jobs
            job_config['timeout-minutes'] = 15
            modified = True
    
    return modified

def optimize_workflow_file(workflow_path: Path, dry_run: bool = False) -> bool:
    """Optimize a single workflow file."""
    try:
        # Read original content to preserve formatting
        with open(workflow_path, 'r') as f:
            original_content = f.read()
        
        # Parse YAML
        workflow = yaml.safe_load(original_content)
        if not workflow or not isinstance(workflow, dict):
            return False
        
        # Apply optimizations
        modified = False
        modified |= add_pip_cache_to_workflow(workflow)
        modified |= add_npm_cache_to_workflow(workflow)
        modified |= reduce_artifact_retention(workflow)
        modified |= add_job_timeouts(workflow)
        
        if modified and not dry_run:
            # Write back
            with open(workflow_path, 'w') as f:
                yaml.dump(workflow, f, default_flow_style=False, sort_keys=False, width=120)
            
            print(f"✅ Optimized: {workflow_path.name}")
            return True
        elif modified and dry_run:
            print(f"🔍 Would optimize: {workflow_path.name}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"⚠️  Error processing {workflow_path.name}: {e}")
        return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimize GitHub Actions workflows')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    parser.add_argument('--workflow', help='Optimize specific workflow file')
    args = parser.parse_args()
    
    # Find workflows directory
    repo_root = Path(__file__).parent.parent.parent
    workflows_dir = repo_root / '.github' / 'workflows'
    
    if not workflows_dir.exists():
        print(f"Error: Workflows directory not found at {workflows_dir}")
        return 1
    
    # Process workflows
    if args.workflow:
        workflow_path = workflows_dir / args.workflow
        if not workflow_path.exists():
            print(f"Error: Workflow not found: {workflow_path}")
            return 1
        workflows = [workflow_path]
    else:
        workflows = list(workflows_dir.glob("*.yml"))
    
    print(f"{'Analyzing' if args.dry_run else 'Optimizing'} {len(workflows)} workflows...")
    print()
    
    optimized_count = 0
    for workflow_path in workflows:
        if optimize_workflow_file(workflow_path, dry_run=args.dry_run):
            optimized_count += 1
    
    print()
    print(f"{'Would optimize' if args.dry_run else 'Optimized'} {optimized_count}/{len(workflows)} workflows")
    
    if args.dry_run:
        print("\nRun without --dry-run to apply changes")
    
    return 0

if __name__ == '__main__':
    exit(main())
