# bridge_backend/runtime/ports.py
import os
import socket
from contextlib import closing
from typing import Tuple

DEFAULT_PORT = 8000

def resolve_port() -> int:
    """Return the port we should bind to: $PORT if set and valid, else 8000."""
    raw = os.getenv("PORT")
    if not raw:
        return DEFAULT_PORT
    try:
        port = int(raw)
    except ValueError:
        return DEFAULT_PORT
    return port if 1 <= port <= 65535 else DEFAULT_PORT

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
