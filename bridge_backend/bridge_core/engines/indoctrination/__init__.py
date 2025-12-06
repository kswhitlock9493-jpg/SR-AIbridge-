# ------------------------------------------------------------------
#  SR-AIbridge – Dominion Canonical v5.7
#  Fleet Admiral Kyle S. Whitlock  |  2025-12-01
# ------------------------------------------------------------------
"""
Dominion-canonical resonance stack – zero-cloud, palm-to-ghost, 1297-artifact constellation.

Exports (unchanged signatures for drop-in safety):
- IndoctrinationEngine  →  ResonanceAlignmentEngine
- IndoctrinationRecord  →  ResonanceRecord
"""
from .resonance_alignment_engine import (
    ResonanceAlignmentEngine as IndoctrinationEngine,
    ResonanceRecord as IndoctrinationRecord,
    EntityType,
    AlignmentStage
)

# Optional: expose the sigil & calculus for advanced users
from .symbols import harmony_sigil  # 𝌆 SVG bytes
from .calculus import (
    quantified_harmony,
    codified_harmony,
    harmony_resonance
)

__all__ = ["IndoctrinationEngine", "IndoctrinationRecord"]
