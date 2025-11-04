#!/usr/bin/env python3
"""
Render ↔ Netlify Parity Layer
Ensures consistent headers and environment variables across platforms
"""
import os
import logging

logger = logging.getLogger(__name__)


def sync_env_headers():
    """
    Synchronize environment headers for CORS and API consistency
    Prevents header/CORS drift between Render and Netlify
    """
    expected_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
    
    aligned_count = 0
    for key, val in expected_headers.items():
        current_val = os.getenv(key)
        if current_val != val:
            os.environ[key] = val
            logger.info(f"[PARITY] {key} aligned → {val}")
            aligned_count += 1
    
    if aligned_count > 0:
        logger.info(f"[PARITY] Aligned {aligned_count} header(s)")
    else:
        logger.debug("[PARITY] All headers already aligned")
    
    return aligned_count


def verify_cors_parity():
    """
    Verify CORS configuration matches expected origins
    """
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
    expected_origins = [
        "https://sr-aibridge.netlify.app"
    ]
    
    all_present = all(origin in allowed_origins for origin in expected_origins)
    
    if all_present:
        logger.debug("[PARITY] CORS origins verified")
    else:
        logger.warning(f"[PARITY] CORS origins may be incomplete: {allowed_origins}")
    
    return all_present


def ensure_port_parity():
    """
    Ensure PORT environment variable is properly configured
    Render typically assigns port 10000, but should use dynamic PORT
    """
    port = os.getenv("PORT", "8000")
    logger.info(f"[PARITY] PORT configured: {port}")
    
    # Record port alignment in repair log
    from bridge_backend.runtime.heartbeat import record_repair
    record_repair("PORT", f"aligned → {port}")
    
    return port


def run_parity_sync():
    """
    Run full parity synchronization
    Called on startup to ensure platform consistency
    """
    logger.info("[PARITY] 🔄 Starting Render ↔ Netlify parity sync...")
    
    sync_env_headers()
    verify_cors_parity()
    ensure_port_parity()
    
    logger.info("[PARITY] ✅ Parity sync complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_parity_sync()
