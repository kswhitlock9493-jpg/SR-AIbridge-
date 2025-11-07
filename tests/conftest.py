"""
Pytest configuration for SR-AIbridge tests
"""
import sys
from pathlib import Path

# Add parent directory to Python path for imports
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))
