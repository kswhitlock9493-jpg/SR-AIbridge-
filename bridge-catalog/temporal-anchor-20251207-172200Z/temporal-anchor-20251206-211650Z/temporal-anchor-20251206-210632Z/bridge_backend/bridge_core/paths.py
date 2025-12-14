"""
Bridge Core Paths - Import Path Normalization
Single source of truth for internal imports to prevent path drift
"""
from __future__ import annotations
import importlib
import logging

logger = logging.getLogger(__name__)


def import_genesis_bus():
    """
    Import Genesis bus with automatic fallback for different layouts.
    
    Attempts the preferred modern path first, then falls back to legacy paths.
    
    Returns:
        Module: The genesis.bus module
        
    Raises:
        ModuleNotFoundError: If genesis bus cannot be found in any location
    """
    # Preferred modern path
    try:
        return importlib.import_module("bridge_backend.genesis.bus")
    except ModuleNotFoundError:
        pass
    
    # Back-compat path (older layouts)
    try:
        return importlib.import_module("bridge_backend.bridge_core.genesis.bus")
    except ModuleNotFoundError:
        pass
    
    # Last resort - try relative to bridge_core
    try:
        return importlib.import_module("genesis.bus")
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "Cannot locate genesis.bus module in any known path. "
            "Tried: bridge_backend.genesis.bus, bridge_backend.bridge_core.genesis.bus, genesis.bus"
        )
