from .core import Base, User  # re-export

# Import from models.py (top-level bridge_backend/models.py, not models/core.py)
try:
    import sys
    import os
    # Add parent directory to path to import from bridge_backend.models
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    
    from models import Blueprint, AgentJob, Mission, Agent, Guardian, VaultLog
    __all__ = ["Base", "User", "Blueprint", "AgentJob", "Mission", "Agent", "Guardian", "VaultLog"]
except ImportError as e:
    # Fallback if models.py is not available
    print(f"WARNING: Could not import models from models.py: {e}")
    __all__ = ["Base", "User"]
