# bridge_backend/runtime/ports.py
import os
import socket
import time
import logging
from contextlib import closing
from typing import Tuple

log = logging.getLogger(__name__)
DEFAULT_PORT = 8000
DEFAULT_PREBIND_WAIT = 2.5  # Default wait for Render's delayed PORT injection

def get_adaptive_prebind_delay() -> float:
    """
    Get adaptive pre-bind delay, which can be auto-tuned by the stabilizer
    based on observed latency patterns
    """
    adaptive_delay = os.getenv("ADAPTIVE_PREBIND_DELAY")
    if adaptive_delay:
        try:
            delay = float(adaptive_delay)
            log.info(f"[PORT] Using adaptive pre-bind delay: {delay:.2f}s")
            return delay
        except ValueError:
            pass
    return DEFAULT_PREBIND_WAIT

def resolve_port() -> int:
    """
    Adaptive port resolution with auto-tuning prebind monitor.
    Waits for Render's delayed PORT environment variable injection.
    Delay is adaptive based on learned latency patterns.
    Returns PORT if set and valid, else defaults to 8000.
    """
    # First attempt - immediate check
    raw = os.getenv("PORT")
    if raw:
        try:
            port = int(raw)
            if 1 <= port <= 65535:
                log.info(f"[PORT] Resolved immediately: {port}")
                return port
        except ValueError:
            pass
    
    # Adaptive prebind monitor - wait for delayed environment variable injection
    wait_time = get_adaptive_prebind_delay()
    log.info(f"[PORT] Waiting {wait_time:.2f}s for environment variable injection...")
    start_time = time.time()
    while time.time() - start_time < wait_time:
        raw = os.getenv("PORT")
        if raw:
            try:
                port = int(raw)
                if 1 <= port <= 65535:
                    elapsed = time.time() - start_time
                    log.info(f"[PORT] Resolved after {elapsed:.2f}s: {port}")
                    return port
            except ValueError:
                pass
        time.sleep(0.1)  # Check every 100ms
    
    # Fallback to default
    log.warning(f"[PORT] No valid PORT detected after {wait_time:.2f}s, defaulting to {DEFAULT_PORT}")
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
