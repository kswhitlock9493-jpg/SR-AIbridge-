#!/usr/bin/env python3
"""
Heartbeat Ping System for SR-AIbridge v1.9.6e
Intelligent method detection with GET/POST/HEAD auto-switching
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
HEARTBEAT_METHOD = os.getenv("HEARTBEAT_METHOD")
INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "30"))
TIMEOUT = int(os.getenv("HEARTBEAT_TIMEOUT_SECONDS", "5"))
ALLOWED_FALLBACK_ORDER = ("GET", "HEAD", "POST")

# Auto-detect HEARTBEAT_URL from Render
_render_external = os.getenv("RENDER_EXTERNAL_URL")
if not HEARTBEAT_URL and _render_external:
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(_render_external)
    HEARTBEAT_URL = urlunparse(parsed._replace(path="/health"))

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
    if not HEARTBEAT_ENABLED:
        _info("disabled via env")
        return
    if not HEARTBEAT_URL:
        _info("no HEARTBEAT_URL set; skipping external ping")
        return
    if httpx is None:
        _warn("httpx not available; skipping")
        return

    _info("initialized ✅")
    backoff = 1
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        while True:
            try:
                resp, method = await _auto_method(client, HEARTBEAT_URL, HEARTBEAT_METHOD)
                if resp.status_code == 200:
                    _info(f"{method} {HEARTBEAT_URL} → 200 OK")
                    backoff = 1
                else:
                    _warn(f"{method} {HEARTBEAT_URL} → {resp.status_code}")
                    backoff = min(backoff * 2, 60)
            except Exception as e:
                _warn(f"ping failed: {e}")
                backoff = min(backoff * 2, 60)
            await asyncio.sleep(INTERVAL + random.uniform(0, 0.5 * backoff))

# Backward compatibility alias
async def run():
    await heartbeat_loop()
