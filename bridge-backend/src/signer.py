"""
Atomic Signing Helpers for SR-AIbridge Sovereign Brain
Secure transaction signing with verification and attestation
"""
import json
import hashlib
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError

from .keys import SovereignKeys


class AtomicSigner:
    """Atomic signing operations for the Sovereign Brain"""
    
    def __init__(self, keys: SovereignKeys):
        self.keys = keys
    
    def create_payload_hash(self, payload: Dict[str, Any]) -> str:
        """Create a deterministic hash of a payload"""
        # Sort keys to ensure consistent hashing
        normalized = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    def sign_payload(self, payload: Dict[str, Any], signer_name: str = "admiral") -> Dict[str, Any]:
        """Sign a payload atomically with metadata"""
        signing_key = self.keys.load_signing_key(signer_name)
        if not signing_key:
            raise ValueError(f"Signing key '{signer_name}' not found")
        
        # Create payload hash
        payload_hash = self.create_payload_hash(payload)
        
        # Create signing envelope
        signing_envelope = {
            "payload": payload,
            "metadata": {
                "signer": signer_name,
                "signed_at": datetime.utcnow().isoformat(),
                "payload_hash": payload_hash,
                "signature_version": "1.0"
            }
        }
        
        # Create signature data (hash of the envelope)
        envelope_hash = self.create_payload_hash(signing_envelope)
        signature_bytes = signing_key.sign(envelope_hash.encode('utf-8'))
        
        # Add signature to envelope
        signed_envelope = {
            **signing_envelope,
            "signature": {
                "data": signature_bytes.signature.hex(),
                "envelope_hash": envelope_hash,
                "public_key": signing_key.verify_key.encode(encoder=Base64Encoder).decode('utf-8')
            }
        }
        
        return signed_envelope
    
    def verify_signature(self, signed_envelope: Dict[str, Any]) -> Tuple[bool, str]:
        """Verify a signed payload"""
        try:
            # Extract components
            signature_data = signed_envelope.get("signature", {})
            signature_hex = signature_data.get("data")
            envelope_hash = signature_data.get("envelope_hash")
            public_key_b64 = signature_data.get("public_key")
            
            if not all([signature_hex, envelope_hash, public_key_b64]):
                return False, "Missing signature components"
            
            # Reconstruct envelope without signature for verification
            verification_envelope = {
                "payload": signed_envelope["payload"],
                "metadata": signed_envelope["metadata"]
            }
            
            # Verify envelope hash
            computed_hash = self.create_payload_hash(verification_envelope)
            if computed_hash != envelope_hash:
                return False, "Envelope hash mismatch"
            
            # Verify signature
            verify_key = VerifyKey(public_key_b64, encoder=Base64Encoder)
            signature_bytes = bytes.fromhex(signature_hex)
            
            verify_key.verify(envelope_hash.encode('utf-8'), signature_bytes)
            
            return True, "Signature valid"
            
        except BadSignatureError:
            return False, "Invalid signature"
        except Exception as e:
            return False, f"Verification error: {str(e)}"
    
    def create_manifest(self, items: list, manifest_type: str = "dock_day_drop") -> Dict[str, Any]:
        """Create a manifest for multiple items"""
        manifest = {
            "type": manifest_type,
            "created_at": datetime.utcnow().isoformat(),
            "items": items,
            "item_count": len(items),
            "manifest_hash": None
        }
        
        # Calculate manifest hash
        manifest["manifest_hash"] = self.create_payload_hash(manifest)
        
        return manifest
    
    def sign_manifest(self, manifest: Dict[str, Any], signer_name: str = "admiral") -> Dict[str, Any]:
        """Sign a manifest with all its items"""
        return self.sign_payload(manifest, signer_name)
    
    def verify_manifest(self, signed_manifest: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Verify a signed manifest and return verification details"""
        is_valid, message = self.verify_signature(signed_manifest)
        
        verification_details = {
            "is_valid": is_valid,
            "message": message,
            "signer": signed_manifest.get("metadata", {}).get("signer"),
            "signed_at": signed_manifest.get("metadata", {}).get("signed_at"),
            "item_count": signed_manifest.get("payload", {}).get("item_count", 0)
        }
        
        return is_valid, message, verification_details


class BatchSigner:
    """Batch signing operations for multiple payloads"""
    
    def __init__(self, signer: AtomicSigner):
        self.signer = signer
    
    def sign_batch(self, payloads: list, signer_name: str = "admiral") -> Dict[str, Any]:
        """Sign multiple payloads as a batch"""
        batch_id = hashlib.sha256(
            f"{datetime.utcnow().isoformat()}{len(payloads)}".encode('utf-8')
        ).hexdigest()[:16]
        
        signed_items = []
        for i, payload in enumerate(payloads):
            # Add batch metadata to each payload
            payload_with_batch = {
                **payload,
                "_batch_meta": {
                    "batch_id": batch_id,
                    "item_index": i,
                    "batch_size": len(payloads)
                }
            }
            
            signed_item = self.signer.sign_payload(payload_with_batch, signer_name)
            signed_items.append(signed_item)
        
        # Create batch manifest
        batch_manifest = {
            "batch_id": batch_id,
            "created_at": datetime.utcnow().isoformat(),
            "items": signed_items,
            "item_count": len(signed_items),
            "signer": signer_name
        }
        
        return self.signer.sign_manifest(batch_manifest, signer_name)
    
    def verify_batch(self, signed_batch: Dict[str, Any]) -> Dict[str, Any]:
        """Verify a signed batch and all its items"""
        # Verify batch manifest
        batch_valid, batch_message, batch_details = self.signer.verify_manifest(signed_batch)
        
        results = {
            "batch_valid": batch_valid,
            "batch_message": batch_message,
            "batch_details": batch_details,
            "item_results": []
        }
        
        if batch_valid:
            # Verify each item in the batch
            items = signed_batch.get("payload", {}).get("items", [])
            for i, item in enumerate(items):
                item_valid, item_message = self.signer.verify_signature(item)
                results["item_results"].append({
                    "index": i,
                    "valid": item_valid,
                    "message": item_message
                })
        
        return results


def create_signer(key_dir: str = "./keys") -> AtomicSigner:
    """Create a signer with initialized keys"""
    from .keys import initialize_admiral_keys
    keys = initialize_admiral_keys(key_dir)
    return AtomicSigner(keys)


if __name__ == "__main__":
    # CLI for signing operations
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python signer.py [sign|verify] [payload_file] [signer_name]")
        sys.exit(1)
    
    action = sys.argv[1]
    signer = create_signer()
    
    if action == "sign" and len(sys.argv) >= 3:
        payload_file = sys.argv[2]
        signer_name = sys.argv[3] if len(sys.argv) > 3 else "admiral"
        
        with open(payload_file, 'r') as f:
            payload = json.load(f)
        
        signed = signer.sign_payload(payload, signer_name)
        
        output_file = payload_file.replace('.json', '_signed.json')
        with open(output_file, 'w') as f:
            json.dump(signed, f, indent=2)
        
        print(f"Signed payload saved to: {output_file}")
    
    elif action == "verify" and len(sys.argv) >= 3:
        signed_file = sys.argv[2]
        
        with open(signed_file, 'r') as f:
            signed_envelope = json.load(f)
        
        is_valid, message = signer.verify_signature(signed_envelope)
        print(f"Verification: {message}")
        if is_valid:
            print("✅ Signature is valid")
        else:
            print("❌ Signature is invalid")
    
    else:
        print("Invalid arguments")
        sys.exit(1)