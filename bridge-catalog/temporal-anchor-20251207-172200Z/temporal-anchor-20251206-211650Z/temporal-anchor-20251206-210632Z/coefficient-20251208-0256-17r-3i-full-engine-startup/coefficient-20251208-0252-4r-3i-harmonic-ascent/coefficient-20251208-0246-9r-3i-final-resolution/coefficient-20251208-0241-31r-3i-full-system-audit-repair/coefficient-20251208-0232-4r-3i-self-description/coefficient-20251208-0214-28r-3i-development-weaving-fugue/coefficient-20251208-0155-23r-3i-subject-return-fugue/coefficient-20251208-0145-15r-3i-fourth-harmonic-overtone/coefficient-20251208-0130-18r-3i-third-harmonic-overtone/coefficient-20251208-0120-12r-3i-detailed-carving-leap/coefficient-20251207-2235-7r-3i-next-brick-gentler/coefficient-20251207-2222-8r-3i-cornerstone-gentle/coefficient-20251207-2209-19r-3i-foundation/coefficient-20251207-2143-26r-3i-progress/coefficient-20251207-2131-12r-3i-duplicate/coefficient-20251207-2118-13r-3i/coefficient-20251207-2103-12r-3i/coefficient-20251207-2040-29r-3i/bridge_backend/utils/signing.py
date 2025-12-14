import json, hmac, hashlib, os
from typing import Dict, Any

SECRET = os.environ.get("SCAN_SIGNING_KEY", "dev-scan-key")  # prod: KMS/Vault

def sign_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(SECRET.encode(), blob, hashlib.sha256).hexdigest()
    return {"payload": payload, "signature": sig}

def verify_signed(signed: Dict[str, Any]) -> bool:
    payload = signed.get("payload")
    signature = signed.get("signature")
    if not payload or not signature: return False
    calc = sign_payload(payload)["signature"]
    return hmac.compare_digest(calc, signature)
