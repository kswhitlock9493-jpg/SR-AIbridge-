#!/usr/bin/env python3
"""
Heartbeat Ping System for SR-AIbridge v1.9.7
Environment-aware GET method with intelligent Netlify ↔ Render coordination
Keeps Render dynos alive and verifies active connection
"""
from __future__ import annotations
import asyncio, os, random
from typing import Optional

try:
    import httpx
except Exception:
    httpx = None

HEARTBEAT_ENABLED = os.getenv("HEARTBEAT_ENABLED", "true").lower() not in ("0","false","no")
HEARTBEAT_URL: Optional[str] = os.getenv("HEARTBEAT_URL")
HEARTBEAT_METHOD = os.getenv("HEARTBEAT_METHOD", "GET")  # Default to GET
INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "30"))
TIMEOUT = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "5"))
ALLOWED_FALLBACK_ORDER = ("GET", "HEAD", "POST")

# Environment-aware target selection
def get_target():
    """Determine heartbeat target based on host platform"""
    if os.getenv("HOST_PLATFORM") == "netlify":
        # For Netlify frontend, check localhost BRH or environment-specified backend
        return os.getenv("BRH_BACKEND_URL", "http://localhost:8000/health")
    if HEARTBEAT_URL:
        return HEARTBEAT_URL
    # Default to localhost for BRH deployments
    return os.getenv("BRH_BACKEND_URL", "http://localhost:8000/health")
    return os.getenv("HEARTBEAT_URL", "http://0.0.0.0:8000/health")

def _info(msg: str): print(f"INFO:bridge_backend.runtime.heartbeat: {msg}")
def _warn(msg: str): print(f"WARNING:bridge_backend.runtime.heartbeat: {msg}")

async def _ping_once(client, url, method):
    req = getattr(client, method.lower())
    return await req(url)

async def _auto_method(client, url, preferred):
    tried = set()
    order = [preferred.upper()] if preferred else ["GET"]
    for method in order + list(ALLOWED_FALLBACK_ORDER):
        if method in tried: continue
        tried.add(method)
        resp = await _ping_once(client, url, method)
        if resp.status_code != 405:
            return resp, method
        allow = [m.strip().upper() for m in resp.headers.get("Allow", "").split(",")]
        for alt in allow or []:
            if alt not in tried:
                resp = await _ping_once(client, url, alt)
                return resp, alt
    return resp, order[0]

async def heartbeat_loop():
    """Environment-aware heartbeat loop with GET method priority"""
    if not HEARTBEAT_ENABLED:
        _info("disabled via env")
        return
    
    target = get_target()
    if not target:
        _info("no heartbeat target available; skipping external ping")
        return
    if httpx is None:
        _warn("httpx not available; skipping")
        return

    _info(f"initialized ✅ targeting {target}")
    backoff = 1
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        while True:
            try:
                resp, method = await _auto_method(client, target, HEARTBEAT_METHOD)
                if resp.status_code == 200:
                    _info(f"{method} {target} → 200 OK")
                    backoff = 1
                else:
                    _warn(f"{method} {target} → {resp.status_code}")
                    backoff = min(backoff * 2, 60)
            except Exception as e:
                _warn(f"ping failed: {e}")
                backoff = min(backoff * 2, 60)
            await asyncio.sleep(INTERVAL + random.uniform(0, 0.5 * backoff))

# Standalone heartbeat function for compatibility
async def heartbeat():
    """Simple heartbeat function for external use"""
    target = get_target()
    try:
        async with httpx.AsyncClient(timeout=5.0) as c:
            r = await c.get(target)
            _info(f"[HEARTBEAT] {target} -> {r.status_code}")
    except Exception as e:
        _warn(f"[HEARTBEAT] failed to reach {target}: {e}")

# Backward compatibility alias
async def run():
    await heartbeat_loop()
