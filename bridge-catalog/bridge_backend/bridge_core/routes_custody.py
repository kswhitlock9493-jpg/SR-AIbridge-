"""
Custody and Key Management Routes for SR-AIbridge Sovereign Brain
FastAPI endpoints for cryptographic key operations and custody management
"""
from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import os

from src.keys import SovereignKeys, initialize_admiral_keys
from src.signer import create_signer
from src.export_and_sign import create_dock_day_exporter

# Create router
router = APIRouter(prefix="/custody", tags=["custody"])

# Global instances (initialized on first use)
_sovereign_keys = None
_signer = None
_exporter = None

def get_sovereign_keys():
    """Get or create sovereign keys instance"""
    global _sovereign_keys
    if _sovereign_keys is None:
        _sovereign_keys = initialize_admiral_keys("./keys")
    return _sovereign_keys

def get_signer():
    """Get or create signer instance"""
    global _signer
    if _signer is None:
        _signer = create_signer("./keys")
    return _signer

def get_exporter():
    """Get or create dock day exporter instance"""
    global _exporter
    if _exporter is None:
        _exporter = create_dock_day_exporter("./brain.sqlite", "./keys")
    return _exporter

# Pydantic models
class KeyInfo(BaseModel):
    name: str
    created_at: str
    public_key: str
    public_key_hex: str

class SignRequest(BaseModel):
    payload: Dict[str, Any]
    signer_name: str = "admiral"

class VerifyRequest(BaseModel):
    signed_envelope: Dict[str, Any]

class DockDayDropRequest(BaseModel):
    drop_name: Optional[str] = None
    include_database: bool = True
    include_keys: bool = False
    compress: bool = True

class VerifyDropRequest(BaseModel):
    drop_path: str


@router.get("/status")
async def get_custody_status():
    """Get custody subsystem status"""
    try:
        keys = get_sovereign_keys()
        available_keys = keys.list_keys()
        
        # Check if admiral keys exist
        admiral_info = keys.get_public_key_info("admiral")
        
        return {
            "status": "operational",
            "key_directory": keys.key_dir,
            "available_keys": len(available_keys),
            "admiral_keys_present": admiral_info is not None,
            "signing_ready": admiral_info is not None,
            "version": "1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custody status error: {str(e)}")


@router.get("/keys", response_model=List[KeyInfo])
async def list_keys():
    """List all available keys"""
    try:
        keys = get_sovereign_keys()
        key_list = keys.list_keys()
        
        return [
            KeyInfo(
                name=key_info["name"],
                created_at=key_info["created_at"],
                public_key=key_info["public_key"],
                public_key_hex=key_info["public_key_hex"]
            )
            for key_info in key_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list keys: {str(e)}")


@router.get("/keys/{key_name}", response_model=KeyInfo)
async def get_key_info(key_name: str):
    """Get information about a specific key"""
    try:
        keys = get_sovereign_keys()
        key_info = keys.get_public_key_info(key_name)
        
        if not key_info:
            raise HTTPException(status_code=404, detail=f"Key '{key_name}' not found")
        
        return KeyInfo(
            name=key_info["name"],
            created_at=key_info["created_at"],
            public_key=key_info["public_key"],
            public_key_hex=key_info["public_key_hex"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get key info: {str(e)}")


@router.post("/keys/{key_name}/generate")
async def generate_key(key_name: str):
    """Generate a new keypair"""
    try:
        keys = get_sovereign_keys()
        
        # Check if key already exists
        existing = keys.get_public_key_info(key_name)
        if existing:
            raise HTTPException(
                status_code=409, 
                detail=f"Key '{key_name}' already exists. Use rotation endpoint to replace."
            )
        
        # Generate new keypair
        signing_key, verify_key = keys.generate_keypair()
        key_file = keys.save_keypair(signing_key, key_name)
        
        # Get the new key info
        key_info = keys.get_public_key_info(key_name)
        
        return {
            "status": "success",
            "message": f"Generated new keypair: {key_name}",
            "key_file": key_file,
            "key_info": KeyInfo(
                name=key_info["name"],
                created_at=key_info["created_at"],
                public_key=key_info["public_key"],
                public_key_hex=key_info["public_key_hex"]
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate key: {str(e)}")


@router.post("/keys/{key_name}/rotate")
async def rotate_key(key_name: str):
    """Rotate an existing key"""
    try:
        keys = get_sovereign_keys()
        
        new_key_file, archived_file = keys.rotate_keys(key_name)
        
        # Get the new key info
        key_info = keys.get_public_key_info(key_name)
        
        return {
            "status": "success",
            "message": f"Rotated keys for: {key_name}",
            "new_key_file": new_key_file,
            "archived_file": archived_file,
            "key_info": KeyInfo(
                name=key_info["name"],
                created_at=key_info["created_at"],
                public_key=key_info["public_key"],
                public_key_hex=key_info["public_key_hex"]
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rotate key: {str(e)}")


@router.post("/sign")
async def sign_payload(sign_request: SignRequest):
    """Sign a payload with the specified key"""
    try:
        signer = get_signer()
        
        signed_envelope = signer.sign_payload(
            sign_request.payload,
            sign_request.signer_name
        )
        
        return {
            "status": "success",
            "message": "Payload signed successfully",
            "signed_envelope": signed_envelope,
            "signer": sign_request.signer_name
        }
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signing failed: {str(e)}")


@router.post("/verify")
async def verify_signature(verify_request: VerifyRequest):
    """Verify a signed payload"""
    try:
        signer = get_signer()
        
        is_valid, message = signer.verify_signature(verify_request.signed_envelope)
        
        # Extract additional details from the envelope
        metadata = verify_request.signed_envelope.get("metadata", {})
        signature = verify_request.signed_envelope.get("signature", {})
        
        return {
            "status": "success",
            "valid": is_valid,
            "message": message,
            "verification_details": {
                "signer": metadata.get("signer"),
                "signed_at": metadata.get("signed_at"),
                "payload_hash": metadata.get("payload_hash"),
                "public_key": signature.get("public_key")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/dock-day-drop")
async def create_dock_day_drop(drop_request: DockDayDropRequest):
    """Create a complete Dock-Day drop with manifest"""
    try:
        exporter = get_exporter()
        
        result = exporter.create_dock_day_drop(
            drop_name=drop_request.drop_name,
            include_database=drop_request.include_database,
            include_keys=drop_request.include_keys,
            compress=drop_request.compress
        )
        
        return {
            "status": "success",
            "message": f"Dock-Day drop created: {result['drop_name']}",
            "drop_info": {
                "drop_name": result["drop_name"],
                "drop_directory": result["drop_directory"],
                "archive_path": result["archive_path"],
                "items_count": result["items_count"],
                "total_size": result["total_size"],
                "manifest_signed": result["manifest_signed"],
                "warnings": result["warnings"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Dock-Day drop: {str(e)}")


@router.post("/verify-drop")
async def verify_dock_day_drop(verify_request: VerifyDropRequest):
    """Verify a Dock-Day drop"""
    try:
        exporter = get_exporter()
        
        if not os.path.exists(verify_request.drop_path):
            raise HTTPException(status_code=404, detail="Drop path not found")
        
        result = exporter.verify_dock_day_drop(verify_request.drop_path)
        
        return {
            "status": "success",
            "verification_result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to verify drop: {str(e)}")


@router.get("/admiral")
async def get_admiral_info():
    """Get Admiral key information"""
    try:
        keys = get_sovereign_keys()
        admiral_info = keys.get_public_key_info("admiral")
        
        if not admiral_info:
            raise HTTPException(status_code=404, detail="Admiral keys not found")
        
        return {
            "status": "success",
            "admiral_info": KeyInfo(
                name=admiral_info["name"],
                created_at=admiral_info["created_at"],
                public_key=admiral_info["public_key"],
                public_key_hex=admiral_info["public_key_hex"]
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get Admiral info: {str(e)}")


@router.post("/admiral/rotate")
async def rotate_admiral_keys():
    """Rotate Admiral keys"""
    try:
        keys = get_sovereign_keys()
        
        new_key_file, archived_file = keys.rotate_keys("admiral")
        
        # Get the new Admiral info
        admiral_info = keys.get_public_key_info("admiral")
        
        return {
            "status": "success",
            "message": "Admiral keys rotated successfully",
            "new_key_file": new_key_file,
            "archived_file": archived_file,
            "admiral_info": KeyInfo(
                name=admiral_info["name"],
                created_at=admiral_info["created_at"],
                public_key=admiral_info["public_key"],
                public_key_hex=admiral_info["public_key_hex"]
            )
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to rotate Admiral keys: {str(e)}")


@router.get("/health")
async def custody_health_check():
    """Custody subsystem health check"""
    try:
        keys = get_sovereign_keys()
        
        # Basic health checks
        healthy = True
        issues = []
        
        # Check key directory exists
        if not os.path.exists(keys.key_dir):
            healthy = False
            issues.append("Key directory not found")
        
        # Check Admiral keys exist
        admiral_info = keys.get_public_key_info("admiral")
        if not admiral_info:
            healthy = False
            issues.append("Admiral keys not found")
        
        # Test signing if Admiral keys exist
        if admiral_info:
            try:
                signer = get_signer()
                test_payload = {"test": True, "timestamp": datetime.now().isoformat()}
                signed = signer.sign_payload(test_payload, "admiral")
                is_valid, _ = signer.verify_signature(signed)
                if not is_valid:
                    healthy = False
                    issues.append("Signature test failed")
            except Exception as e:
                healthy = False
                issues.append(f"Signing test error: {str(e)}")
        
        # Check key directory permissions
        try:
            test_file = os.path.join(keys.key_dir, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except Exception as e:
            healthy = False
            issues.append(f"Key directory not writable: {str(e)}")
        
        available_keys = keys.list_keys()
        
        return {
            "status": "healthy" if healthy else "unhealthy",
            "issues": issues,
            "key_directory": keys.key_dir,
            "available_keys": len(available_keys),
            "admiral_keys_present": admiral_info is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "issues": [f"Health check failed: {str(e)}"],
            "key_directory": "unknown",
            "available_keys": 0,
            "admiral_keys_present": False
        }