"""
SR-AIbridge Protocol Vaulting System

Provides auditable sealing primitives for protocol invocations.
Creates sealed artifacts in vault/protocols/<name>/ directory structure.
"""

import os
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional


def get_vault_dir() -> Path:
    """Get the vault directory, with environment variable override for testing."""
    vault_dir = os.environ.get('VAULT_DIR', 'vault')
    return Path(vault_dir)


def seal(protocol_name: str, status: str = 'invoked', details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Seal a protocol invocation with auditable artifacts.
    
    Args:
        protocol_name: Name of the protocol being sealed
        status: Status of the protocol (default: 'invoked')
        details: Optional additional details to include in the seal
    
    Returns:
        Dict containing the seal object with protocol, status, timestamp, and details
    
    Creates:
        vault/protocols/<ProtocolName>/lore_applied.txt
        vault/protocols/<ProtocolName>/seal.json
    """
    if details is None:
        details = {}
    
    # Create timestamp
    timestamp = datetime.now(timezone.utc).isoformat() + 'Z'
    
    # Create seal object
    seal_obj = {
        "protocol": protocol_name,
        "status": status,
        "timestamp": timestamp,
        "details": details
    }
    
    # Create protocol directory
    vault_dir = get_vault_dir()
    protocol_dir = vault_dir / "protocols" / protocol_name
    protocol_dir.mkdir(parents=True, exist_ok=True)
    
    # Write lore_applied.txt
    lore_file = protocol_dir / "lore_applied.txt"
    lore_content = f"Protocol: {protocol_name}\nStatus: {status}\nTimestamp: {timestamp}\n"
    if details:
        lore_content += f"Details: {json.dumps(details, indent=2)}\n"
    
    with open(lore_file, 'w') as f:
        f.write(lore_content)
    
    # Write seal.json
    seal_file = protocol_dir / "seal.json"
    with open(seal_file, 'w') as f:
        json.dump(seal_obj, f, indent=2)
    
    return seal_obj