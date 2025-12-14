from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from .service import list_scans, read_scan

router = APIRouter(prefix="/scans", tags=["scans"])

@router.get("")
def get_scans():
    return {"items": list_scans()}

@router.get("/{scan_id}")
def get_scan(scan_id: str):
    try:
        return read_scan(scan_id)
    except Exception:
        raise HTTPException(status_code=404, detail="scan not found")
