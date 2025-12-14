"""
SR-AIbridge Sovereign Brain Subsystem
Local-first cryptographic memory management with no cloud dependencies
"""

from .keys import SovereignKeys, initialize_admiral_keys
from .signer import AtomicSigner, BatchSigner, create_signer
from .brain import BrainLedger, create_brain_ledger
from .export_and_sign import DockDayExporter, create_dock_day_exporter

__version__ = "1.0.0"
__all__ = [
    "SovereignKeys",
    "initialize_admiral_keys", 
    "AtomicSigner",
    "BatchSigner",
    "create_signer",
    "BrainLedger",
    "create_brain_ledger",
    "DockDayExporter",
    "create_dock_day_exporter"
]