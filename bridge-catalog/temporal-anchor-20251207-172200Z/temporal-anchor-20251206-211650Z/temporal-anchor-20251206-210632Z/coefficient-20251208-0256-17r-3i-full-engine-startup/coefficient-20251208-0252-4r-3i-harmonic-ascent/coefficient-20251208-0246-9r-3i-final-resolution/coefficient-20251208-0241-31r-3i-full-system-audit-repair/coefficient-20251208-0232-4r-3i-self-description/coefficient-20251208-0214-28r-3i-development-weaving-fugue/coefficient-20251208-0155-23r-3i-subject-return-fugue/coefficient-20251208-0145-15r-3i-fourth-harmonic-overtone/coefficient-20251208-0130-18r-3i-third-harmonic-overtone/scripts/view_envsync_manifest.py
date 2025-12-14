#!/usr/bin/env python3
"""
EnvSync Seed Manifest Viewer

Quick utility to display the current manifest contents and statistics.

Usage:
    python3 scripts/view_envsync_manifest.py
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def parse_manifest(manifest_path: Path) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Parse manifest and extract variables and metadata"""
    variables = {}
    metadata = {}
    
    with open(manifest_path, 'r') as f:
        for line in f:
            line_stripped = line.strip()
            
            # Extract metadata from comments
            if line_stripped.startswith('#') and ':' in line_stripped:
                parts = line_stripped.lstrip('#').split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key in ['Version', 'Purpose', 'AutoPropagate', 'SyncTarget', 'Canonical', 'ManagedBy', 'LastUpdated']:
                        metadata[key] = value
            
            # Extract variables
            if not line_stripped or line_stripped.startswith('#'):
                continue
            if '=' in line_stripped:
                key, value = line_stripped.split('=', 1)
                variables[key.strip()] = value.strip()
    
    return variables, metadata

def categorize_variables(variables: Dict[str, str]) -> Dict[str, List[str]]:
    """Categorize variables by prefix"""
    categories = defaultdict(list)
    
    for var_name in sorted(variables.keys()):
        # Determine category based on prefix
        if var_name.startswith('LINK_'):
            categories['Link Engines'].append(var_name)
        elif var_name.startswith('BLUEPRINT'):
            categories['Blueprints'].append(var_name)
        elif var_name.startswith('DB_'):
            categories['Database'].append(var_name)
        elif var_name.startswith('HEALTH_'):
            categories['Health Checks'].append(var_name)
        elif var_name.startswith('FEDERATION_'):
            categories['Federation'].append(var_name)
        elif var_name.startswith('WATCHDOG_'):
            categories['Watchdog'].append(var_name)
        elif var_name.startswith('GENESIS_'):
            categories['Genesis'].append(var_name)
        elif var_name.startswith('PREDICTIVE_'):
            categories['Predictive Systems'].append(var_name)
        elif var_name == 'HOST':
            categories['Runtime'].append(var_name)
        else:
            categories['Other'].append(var_name)
    
    return dict(categories)

def main():
    """Main entry point"""
    # Determine manifest path
    if len(sys.argv) > 1:
        manifest_path = Path(sys.argv[1])
    else:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        manifest_path = project_root / "bridge_backend" / ".genesis" / "envsync_seed_manifest.env"
    
    if not manifest_path.exists():
        print(f"{BOLD}❌ Error:{RESET} Manifest not found at {manifest_path}")
        sys.exit(1)
    
    # Parse manifest
    variables, metadata = parse_manifest(manifest_path)
    categories = categorize_variables(variables)
    
    # Display header
    print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}")
    print(f"{BOLD}{BLUE}EnvSync Seed Manifest Viewer{RESET}")
    print(f"{BOLD}{BLUE}{'=' * 80}{RESET}\n")
    
    # Display metadata
    print(f"{BOLD}{CYAN}📋 Metadata{RESET}")
    print(f"{'-' * 80}")
    for key, value in metadata.items():
        print(f"  {BOLD}{key}:{RESET} {value}")
    
    # Display statistics
    print(f"\n{BOLD}{CYAN}📊 Statistics{RESET}")
    print(f"{'-' * 80}")
    print(f"  {BOLD}Total Variables:{RESET} {len(variables)}")
    print(f"  {BOLD}Categories:{RESET} {len(categories)}")
    print(f"  {BOLD}Manifest Path:{RESET} {manifest_path}")
    
    # Display variables by category
    print(f"\n{BOLD}{CYAN}🗂️  Variables by Category{RESET}")
    print(f"{'-' * 80}")
    
    for category, var_list in sorted(categories.items()):
        print(f"\n  {BOLD}{GREEN}{category}{RESET} ({len(var_list)} variables)")
        for var_name in var_list:
            value = variables[var_name]
            # Truncate long values
            display_value = value if len(value) <= 50 else value[:47] + "..."
            print(f"    {YELLOW}{var_name}{RESET} = {display_value}")
    
    # Display footer
    print(f"\n{BOLD}{BLUE}{'=' * 80}{RESET}")
    print(f"{BOLD}To edit:{RESET} {manifest_path}")
    print(f"{BOLD}To validate:{RESET} python3 scripts/validate_envsync_manifest.py")
    print(f"{BOLD}{BLUE}{'=' * 80}{RESET}\n")

if __name__ == "__main__":
    main()
