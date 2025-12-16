"""
Pytest configuration for SR-AIbridge tests
"""
import sys
from pathlib import Path

# Add parent directory to Python path for imports
# This must come before bridge_backend to avoid module shadowing
repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Also add bridge_backend for tests that need it
# This comes after repo_root to ensure bridge_core is found from repo root first
bridge_backend_path = repo_root / "bridge_backend"
if str(bridge_backend_path) not in sys.path:
    sys.path.append(str(bridge_backend_path))
