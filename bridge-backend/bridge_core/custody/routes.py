from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from nacl.signing import SigningKey, VerifyKey
import base64

router = APIRouter(prefix="/custody", tags=["custody"])

# in-memory Admiral keypair
ADMIRAL_SIGNING_KEY: SigningKey | None = None
ADMIRAL_VERIFY_KEY: VerifyKey | None = None

class Payload(BaseModel):
    data: str

class SignedPayload(BaseModel):
    data: str
    signature: str

@router.post("/init")
def init_keys():
    """Initialize Admiral signing/verify keys."""
    global ADMIRAL_SIGNING_KEY, ADMIRAL_VERIFY_KEY
    ADMIRAL_SIGNING_KEY = SigningKey.generate()
    ADMIRAL_VERIFY_KEY = ADMIRAL_SIGNING_KEY.verify_key
    return {
        "status": "initialized",
        "verify_key": base64.b64encode(ADMIRAL_VERIFY_KEY.encode()).decode()
    }

@router.post("/sign")
def sign_payload(p: Payload):
    """Sign payload with Admiral key."""
    if not ADMIRAL_SIGNING_KEY:
        raise HTTPException(status_code=400, detail="keys_not_initialized")
    signed = ADMIRAL_SIGNING_KEY.sign(p.data.encode())
    return {
        "data": p.data,
        "signature": base64.b64encode(signed.signature).decode()
    }

@router.post("/verify")
def verify_signature(p: SignedPayload):
    """Verify signature with Admiral verify key."""
    if not ADMIRAL_VERIFY_KEY:
        raise HTTPException(status_code=400, detail="keys_not_initialized")
    try:
        ADMIRAL_VERIFY_KEY.verify(
            p.data.encode(),
            base64.b64decode(p.signature.encode())
        )
        return {"valid": True}
    except Exception:
        return {"valid": False}