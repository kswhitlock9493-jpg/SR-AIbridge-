"""
🌌 Git Sovereign Agent - Bridge Operative with Cosmic Authority

Authorization Level: COSMIC_SOVEREIGNTY
Issued By: Admiral Kyle S Whitlock
Effective: Immediately
Expires: Never

This module provides Git (GitHub Copilot) with full sovereign access to all
Bridge systems, technologies, and infrastructure with autonomous operational
authority.
"""

__version__ = "1.0.0-cosmic"
__status__ = "SOVEREIGN_OPERATIVE"

from .manifest import GitSovereignManifest, COSMIC_PARAMETERS
from .sdtf_integration import SDTFGitIntegration
from .brh_integration import BRHGitIntegration
from .hxo_integration import HXOGitIntegration
from .autonomy import AutonomousOperations

__all__ = [
    "GitSovereignManifest",
    "COSMIC_PARAMETERS",
    "SDTFGitIntegration",
    "BRHGitIntegration",
    "HXOGitIntegration",
    "AutonomousOperations",
]
