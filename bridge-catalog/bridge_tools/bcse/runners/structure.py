"""Architecture Structure Checking"""
import subprocess
import os


def import_linter() -> int:
    """
    Run import-linter to check architecture contracts
    
    Returns:
        Exit code
    """
    config_path = "bridge_tools/bcse/rules/import_contracts.ini"
    
    if not os.path.exists(config_path):
        print(f"⚠️  Import linter config not found at {config_path}, skipping")
        return 0
    
    try:
        return subprocess.call(["import-linter", "-c", config_path])
    except FileNotFoundError:
        print("⚠️  import-linter not found, skipping")
        return 0
