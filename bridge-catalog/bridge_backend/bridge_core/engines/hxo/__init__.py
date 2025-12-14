"""
HXO Nexus - Harmonic Orchestration Engine
Central harmonic conductor for all engine connectivity
Version: 1.9.6p "HXO Ascendant"
"""
from __future__ import annotations
import logging

from .nexus import HXONexus, get_nexus_instance, initialize_nexus
from .hypshard import HypShardV3Manager
from .security import QuantumEntropyHasher, HarmonicConsensusProtocol

logger = logging.getLogger(__name__)

__all__ = [
    "HXONexus",
    "get_nexus_instance",
    "initialize_nexus",
    "HypShardV3Manager",
    "QuantumEntropyHasher",
    "HarmonicConsensusProtocol",
    "safe_init",
]


def safe_init():
    """
    Safe initialization for HXO/Chimera with Genesis registration and fallback.
    
    Attempts to register Chimera with Genesis bus using retry logic.
    If all attempts fail, activates Umbra Lattice fallback channel to keep
    Chimera online and observable.
    """
    from ..adapters.chimera_genesis_link import register_with_retry
    
    ok = register_with_retry()
    if not ok:
        # Fallback to Umbra lattice channel so Chimera remains online
        try:
            from ..umbra.lattice import fallback_neural_channel
            fallback_neural_channel("chimera")
            logger.warning("⚠️ Chimera fallback mode via Umbra Lattice activated")
        except Exception as e:
            logger.error(f"❌ Chimera fallback failed: {e}")
