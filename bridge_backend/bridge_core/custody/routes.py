from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from nacl.signing import SigningKey, VerifyKey
import base64
from datetime import datetime

router = APIRouter(prefix="/custody", tags=["custody"])

# in-memory Admiral keypair
ADMIRAL_SIGNING_KEY: SigningKey | None = None
ADMIRAL_VERIFY_KEY: VerifyKey | None = None
KEY_CREATION_TIME: str | None = None

class Payload(BaseModel):
    data: str

class SignedPayload(BaseModel):
    data: str
    signature: str

@router.get("/status")
def get_custody_status():
    """Get custody system status - returns JSON"""
    return {
        "status": "operational",
        "admiral_keys_initialized": ADMIRAL_SIGNING_KEY is not None,
        "key_creation_time": KEY_CREATION_TIME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/keys")
def list_keys():
    """List available keys - returns JSON"""
    keys = []
    if ADMIRAL_SIGNING_KEY:
        keys.append({
            "id": "admiral_key_1",
            "type": "signing",
            "created_at": KEY_CREATION_TIME,
            "status": "active"
        })
    return {
        "keys": keys,
        "total": len(keys)
    }

@router.get("/admiral")
def get_admiral_info():
    """Get Admiral key information - returns JSON"""
    if not ADMIRAL_VERIFY_KEY:
        return {
            "admiral_info": None,
            "message": "Admiral keys not initialized"
        }
    
    return {
        "admiral_info": {
            "verify_key": base64.b64encode(ADMIRAL_VERIFY_KEY.encode()).decode(),
            "created_at": KEY_CREATION_TIME,
            "status": "active"
        }
    }

@router.post("/admiral/rotate")
def rotate_admiral_keys():
    """Rotate Admiral keys - returns JSON"""
    global ADMIRAL_SIGNING_KEY, ADMIRAL_VERIFY_KEY, KEY_CREATION_TIME
    ADMIRAL_SIGNING_KEY = SigningKey.generate()
    ADMIRAL_VERIFY_KEY = ADMIRAL_SIGNING_KEY.verify_key
    KEY_CREATION_TIME = datetime.now(timezone.utc).isoformat()
    
    return {
        "status": "rotated",
        "verify_key": base64.b64encode(ADMIRAL_VERIFY_KEY.encode()).decode(),
        "created_at": KEY_CREATION_TIME
    }

@router.post("/init")
def init_keys():
    """Initialize Admiral signing/verify keys - returns JSON"""
    global ADMIRAL_SIGNING_KEY, ADMIRAL_VERIFY_KEY, KEY_CREATION_TIME
    ADMIRAL_SIGNING_KEY = SigningKey.generate()
    ADMIRAL_VERIFY_KEY = ADMIRAL_SIGNING_KEY.verify_key
    KEY_CREATION_TIME = datetime.now(timezone.utc).isoformat()
    
    return {
        "status": "initialized",
        "verify_key": base64.b64encode(ADMIRAL_VERIFY_KEY.encode()).decode(),
        "created_at": KEY_CREATION_TIME
    }

@router.post("/sign")
def sign_payload(p: Payload):
    """Sign payload with Admiral key - returns JSON"""
    if not ADMIRAL_SIGNING_KEY:
        raise HTTPException(status_code=400, detail="keys_not_initialized")
    signed = ADMIRAL_SIGNING_KEY.sign(p.data.encode())
    return {
        "data": p.data,
        "signature": base64.b64encode(signed.signature).decode(),
        "signed_at": datetime.now(timezone.utc).isoformat()
    }

@router.post("/verify")
def verify_signature(p: SignedPayload):
    """Verify signature with Admiral verify key - returns JSON"""
    if not ADMIRAL_VERIFY_KEY:
        raise HTTPException(status_code=400, detail="keys_not_initialized")
    try:
        ADMIRAL_VERIFY_KEY.verify(
            p.data.encode(),
            base64.b64decode(p.signature.encode())
        )
        return {
            "valid": True,
            "verified_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "verified_at": datetime.now(timezone.utc).isoformat()
        }