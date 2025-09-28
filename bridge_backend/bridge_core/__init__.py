"""
SR-AIbridge Core Modules
Modular separation for critical AI Bridge components
"""

from .claude_watcher import ClaudeWatcher
from .fault_injector import FaultInjector
from .self_healing_adapter import SelfHealingMASAdapter
from .federation_client import FederationClient
from .registry_payloads import current_registry_payloads

# Six Super Engines - Sovereign Bridge Architecture
from .engines.scrolltongue import ScrollTongue
from .engines.commerceforge import CommerceForge
from .engines.auroraforge import AuroraForge
from .engines.chronicleloom import ChronicleLoom
from .engines.calculuscore import CalculusCore
from .engines.qhelmsingularity import QHelmSingularity

# Legacy Super Engines (maintained for backward compatibility)
from .labyrinthforge import LabyrinthForge
from .chroniclevault import ChronicleVault
from .prooffoundry import ProofFoundry
from .entanglecore import EntangleCore

__all__ = [
    "ClaudeWatcher",
    "FaultInjector", 
    "SelfHealingMASAdapter",
    "FederationClient",
    "current_registry_payloads",
    # Six Super Engines - Sovereign Bridge Architecture
    "ScrollTongue",
    "CommerceForge",
    "AuroraForge",
    "ChronicleLoom",
    "CalculusCore",
    "QHelmSingularity",
    # Legacy Super Engines (backward compatibility)
    "LabyrinthForge",
    "ChronicleVault", 
    "ProofFoundry",
    "EntangleCore"
]