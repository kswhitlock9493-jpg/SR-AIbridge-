"""
Authentication Routes for Keyless Security
Handles ephemeral session establishment and dynamic key generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import os
from datetime import datetime, timezone

# Import keyless auth handler
import sys
from pathlib import Path
# Add bridge_backend to path if not already there
bridge_backend_path = Path(__file__).resolve().parent.parent.parent
if str(bridge_backend_path) not in sys.path:
    sys.path.insert(0, str(bridge_backend_path))

try:
    from src.keyless_auth import get_keyless_handler, KeylessAuthHandler
except ImportError:
    from bridge_backend.src.keyless_auth import get_keyless_handler, KeylessAuthHandler

router = APIRouter(prefix="/auth", tags=["auth"])

# Configuration
SESSION_EXPIRY_SECONDS = int(os.getenv("AUTH_SESSION_EXPIRY_SECONDS", "3600"))  # Default 1 hour

class SessionRequest(BaseModel):
    requestType: str = "ephemeral_session"
    keyGenerationType: str = "dynamic"

class HandshakeRequest(BaseModel):
    """Request for keyless handshake"""
    pass

@router.post("/handshake")
def perform_keyless_handshake(request: Optional[HandshakeRequest] = None):
    """
    Perform cryptographic handshake without static secrets
    Generates all material dynamically
    
    POST /auth/handshake
    
    Returns:
    {
        "handshake_complete": true,
        "handshake_type": "keyless_ephemeral",
        "session_id": "...",
        "static_keys_involved": 0,
        "dynamic_keys_generated": 1
    }
    """
    try:
        handler = get_keyless_handler()
        result = handler.perform_keyless_handshake()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "handshake_complete": False,
                "error": str(e),
                "static_keys_involved": 0
            }
        )

@router.post("/session")
def establish_session(request: SessionRequest):
    """
    Establish ephemeral session with dynamic key generation
    
    POST /auth/session
    Body: {
        "requestType": "ephemeral_session",
        "keyGenerationType": "dynamic"
    }
    
    Returns:
    {
        "authenticated": true,
        "session": {...}
    }
    """
    try:
        handler = get_keyless_handler()
        result = handler.establish_ephemeral_session()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "authenticated": False,
                "error": str(e),
                "static_keys_used": False
            }
        )


@router.get("/capability")
def check_capability():
    """
    Check dynamic key generation capability
    
    GET /auth/capability
    
    Returns:
    {
        "capable": true,
        "authModel": "keyless_ephemeral_sessions",
        "staticKeysExist": false
    }
    """
    try:
        handler = get_keyless_handler()
        capable = handler.verify_dynamic_key_generation()
        
        return {
            "capable": capable,
            "authModel": "keyless_ephemeral_sessions",
            "staticKeysExist": False,
            "sessionExpiry": SESSION_EXPIRY_SECONDS,
            "securityAdvantages": [
                "No static keys to leak",
                "Dynamic session generation",
                "Automatic expiration",
                "Zero-trust security model"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "capable": False,
                "error": str(e),
                "staticKeysExist": False
            }
        )


@router.get("/status")
def auth_status():
    """
    Get authentication system status
    
    GET /auth/status
    
    Returns complete status of keyless auth system including security advantages
    """
    try:
        handler = get_keyless_handler()
        status = handler.get_status()
        status["timestamp"] = datetime.now(timezone.utc).isoformat()
        return status
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "auth_model": "error",
                "static_keys_exist": False,
                "status": "degraded"
            }
        )
