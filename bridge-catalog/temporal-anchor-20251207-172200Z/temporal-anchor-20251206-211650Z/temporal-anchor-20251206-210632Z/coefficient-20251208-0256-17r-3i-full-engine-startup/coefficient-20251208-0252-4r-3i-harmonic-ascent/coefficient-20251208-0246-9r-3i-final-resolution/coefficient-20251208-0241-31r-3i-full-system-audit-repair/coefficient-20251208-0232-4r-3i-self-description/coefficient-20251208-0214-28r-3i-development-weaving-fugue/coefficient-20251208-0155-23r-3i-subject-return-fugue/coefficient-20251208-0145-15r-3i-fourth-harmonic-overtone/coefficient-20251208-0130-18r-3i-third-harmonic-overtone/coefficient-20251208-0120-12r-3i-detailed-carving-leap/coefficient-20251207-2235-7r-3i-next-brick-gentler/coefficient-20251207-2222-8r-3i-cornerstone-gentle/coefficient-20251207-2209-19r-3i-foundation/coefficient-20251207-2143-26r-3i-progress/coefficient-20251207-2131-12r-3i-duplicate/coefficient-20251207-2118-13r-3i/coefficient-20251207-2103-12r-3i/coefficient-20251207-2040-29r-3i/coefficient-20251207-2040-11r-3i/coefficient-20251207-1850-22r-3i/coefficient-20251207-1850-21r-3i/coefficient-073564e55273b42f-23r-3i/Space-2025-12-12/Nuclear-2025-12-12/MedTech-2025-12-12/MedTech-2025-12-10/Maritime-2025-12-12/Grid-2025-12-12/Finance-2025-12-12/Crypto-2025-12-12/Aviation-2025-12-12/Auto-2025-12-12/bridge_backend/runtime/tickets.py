"""
Simple ticket creation for TDE-X StabilizationDomain
Uses existing predictive_stabilizer ticket directory
"""
import os
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

TICKET_DIR = Path("bridge_backend/diagnostics/stabilization_tickets")
TICKET_DIR.mkdir(parents=True, exist_ok=True)


def create(message: str) -> str:
    """
    Create a stabilization ticket
    
    Args:
        message: Ticket message (format: [TDE-X:shard_name] ErrorType: error_message)
    
    Returns:
        Ticket file path
    """
    try:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        ticket_name = f"{ts}_tde_x.md"
        ticket_path = TICKET_DIR / ticket_name
        
        with open(ticket_path, "w") as f:
            f.write(f"# TDE-X Stabilization Ticket\n")
            f.write(f"- Generated: {ts}\n")
            f.write(f"- Message: {message}\n")
            f.write(f"\n## Action Required\n")
            f.write(f"Review and resolve the issue reported above.\n")
        
        logger.warning(f"[TDE-X Ticket] Created: {ticket_path}")
        return str(ticket_path)
    except Exception as e:
        logger.error(f"[TDE-X Ticket] Failed to create ticket: {e}")
        return ""
