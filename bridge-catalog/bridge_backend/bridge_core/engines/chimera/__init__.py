"""
Chimera Deployment Engine (CDE)
Project Chimera: Autonomous Deployment Sovereignty
Version: 1.9.7c "HXO-Echelon-03"

The Chimera Deployment Engine transforms the Bridge's deployment framework
into a self-sustaining, self-healing, and self-certifying system.
"""

from .engine import ChimeraDeploymentEngine, get_chimera_instance
from .config import ChimeraConfig

__all__ = [
    "ChimeraDeploymentEngine",
    "get_chimera_instance",
    "ChimeraConfig",
]
