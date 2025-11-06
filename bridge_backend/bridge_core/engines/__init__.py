"""
SR-AIbridge 34 Engines System
The complete engine ecosystem that powers the Sovereign Bridge architecture
"""

# Super Engines (7)
from .scrolltongue import ScrollTongue
from .commerceforge import CommerceForge
from .auroraforge import AuroraForge
from .chronicleloom import ChronicleLoom
from .calculuscore import CalculusCore
from .qhelmsingularity import QHelmSingularity
from .leviathan import LeviathanEngine

# Core Infrastructure Engines (6)
from .blueprint.blueprint_engine import BlueprintEngine
from .cascade.service import CascadeEngine
from .autonomy import AutonomyEngine
from .parser import ParserEngine
from .hxo import HXONexus

# Utility & Support Engines (14+)
from .chimera.engine import ChimeraDeploymentEngine
from .envsync import EnvSyncEngine
from .filing import FilingEngine
from .screen.service import ScreenEngine
from .speech.tts import TTSEngine
from .speech.stt import STTEngine
from .recovery import RecoveryOrchestrator
from .creativity import CreativityBay
from .indoctrination.service import IndoctrinationEngine
from .umbra import UmbraLattice

__all__ = [
    # Super Engines
    "ScrollTongue",
    "CommerceForge", 
    "AuroraForge",
    "ChronicleLoom",
    "CalculusCore",
    "QHelmSingularity",
    "LeviathanEngine",
    # Core Infrastructure
    "BlueprintEngine",
    "CascadeEngine",
    "AutonomyEngine",
    "ParserEngine",
    "HXONexus",
    # Utility & Support
    "ChimeraDeploymentEngine",
    "EnvSyncEngine",
    "FilingEngine",
    "ScreenEngine",
    "TTSEngine",
    "STTEngine",
    "RecoveryOrchestrator",
    "CreativityBay",
    "IndoctrinationEngine",
    "UmbraLattice",
]