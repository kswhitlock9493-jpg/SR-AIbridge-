# bridge_backend/runtime/ports.py
import os
import socket
import logging
from contextlib import closing
from typing import Tuple

log = logging.getLogger(__name__)
DEFAULT_PORT = 8000

def resolve_port() -> int:
    """
    Simple port resolution without loops.
    Respects PORT env var with validation (1-65535 range).
    Falls back to 8000 if PORT is missing, invalid, or out of range.
    
    No port scanning, no loops - just reads the env var once.
    """
    raw = os.getenv("PORT")
    if raw:
        try:
            port = int(raw)
            if 1 <= port <= 65535:
                log.info(f"[PORT] Using PORT={port} from environment")
                return port
            else:
                log.warning(f"[PORT] PORT={port} out of range (1-65535), using default {DEFAULT_PORT}")
        except ValueError:
            log.warning(f"[PORT] PORT={raw!r} invalid, using default {DEFAULT_PORT}")
    
    log.info(f"[PORT] No PORT set, using default {DEFAULT_PORT}")
    return DEFAULT_PORT

def check_listen(host: str, port: int) -> Tuple[bool, str]:
    """
    Best-effort check: can something bind/listen here?
    We don't actually bind; we attempt to connect to see if already in use.
    """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.2)
            result = s.connect_ex((host, port))
            if result == 0:
                return True, "occupied"
            return False, "free"
    except Exception as e:
        return False, f"unknown: {e!r}"

def adaptive_bind_check(host: str, port: int) -> Tuple[int, str]:
    """
    Graceful rebind fallback - checks if port is available.
    If unavailable, falls back to DEFAULT_PORT.
    Returns (final_port, status_message)
    """
    occupied, status = check_listen(host, port)
    if occupied:
        log.warning(f"[PORT] Port {port} is occupied ({status}), falling back to {DEFAULT_PORT}")
        # Check fallback port
        fb_occupied, fb_status = check_listen(host, DEFAULT_PORT)
        if fb_occupied:
            log.error(f"[PORT] Fallback port {DEFAULT_PORT} also occupied ({fb_status})")
            return port, f"both_occupied"
        return DEFAULT_PORT, f"fallback_ok"
    return port, "ok"
