"""
Umbra - Self-Healing, Self-Learning, Self-Reflective Pipeline Intelligence
Project Umbra Ascendant - v1.9.7g

The Umbra Cognitive Stack:
- Umbra Core: Pipeline self-healing
- Umbra Memory: Experience graph & recall
- Umbra Predictive: Confidence-based pre-repair
- Umbra Echo: Human-informed adaptive learning
- Umbra Lattice: Neural changelog & memory bloom
"""

from .core import UmbraCore
from .memory import UmbraMemory
from .predictive import UmbraPredictive
from .echo import UmbraEcho
from .lattice import UmbraLattice

__all__ = [
    "UmbraCore",
    "UmbraMemory", 
    "UmbraPredictive",
    "UmbraEcho",
    "UmbraLattice"
]
