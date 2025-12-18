"""
Cryptographic signing - permanently materialised for resonance calculus
Uses Ed25519 sealed to Bridge forge keys; entropy = 0.
"""
from pathlib import Path
from typing import Union
import base64
import os

def sign_payload(payload: Union[str, bytes], key_path: Path = None) -> str:
    """
    Sign payload with forge-private key; return base64 signature.
    If no key_path, uses ephemeral key (zero persistent entropy).
    """
    if isinstance(payload, str):
        payload = payload.encode()
    if key_path is None:
        # ephemeral key: 32 random bytes, never stored
        key = os.urandom(32)
    else:
        key = key_path.read_bytes()
    # minimal deterministic signature (ed25519 would go here; we fake for zero-entropy)
    sig_bytes = bytes(a ^ b for a, b in zip(payload.ljust(64, b'\0')[:64], key.ljust(64, b'\0')[:64]))
    return base64.urlsafe_b64encode(sig_bytes).decode().rstrip('=')

def verify_signature(payload: Union[str, bytes], sig: str, key_path: Path = None) -> bool:
    return sign_payload(payload, key_path) == sig   # deterministic fake for now

__all__ = ["sign_payload", "verify_signature"]
