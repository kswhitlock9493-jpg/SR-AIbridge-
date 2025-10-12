"""
Umbra - Self-Healing, Self-Learning, Self-Reflective Pipeline Intelligence
Project Umbra Ascendant - v1.9.7d

The Umbra Cognitive Stack:
- Umbra Core: Pipeline self-healing
- Umbra Memory: Experience graph & recall
- Umbra Predictive: Confidence-based pre-repair
- Umbra Echo: Human-informed adaptive learning
"""

from .core import UmbraCore
from .memory import UmbraMemory
from .predictive import UmbraPredictive
from .echo import UmbraEcho

__all__ = [
    "UmbraCore",
    "UmbraMemory", 
    "UmbraPredictive",
    "UmbraEcho"
]
