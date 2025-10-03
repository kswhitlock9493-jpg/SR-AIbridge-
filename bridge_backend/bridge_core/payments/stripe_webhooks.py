from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any, Optional
import stripe
import os

router = APIRouter(prefix="/payments/stripe", tags=["payments"])

STRIPE_SECRET = os.getenv("STRIPE_SECRET", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

# Set stripe API key
stripe.api_key = STRIPE_SECRET

# Import CascadeEngine at module level
try:
    from bridge_core.engines.cascade.service import CascadeEngine
except ImportError:
    from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine

def verify_signature(payload: bytes, sig_header: str) -> Optional[Dict[str, Any]]:
    """Verify Stripe webhook signature and return event if valid."""
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=STRIPE_WEBHOOK_SECRET
        )
        return event
    except Exception:
        return None

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events and trigger Cascade Engine updates."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    event = verify_signature(payload, sig_header)
    
    if not event:
        raise HTTPException(status_code=400, detail="invalid_signature")

    C = CascadeEngine()
    
    data: Dict[str, Any] = event["data"]["object"]
    event_type = event["type"]

    # Map Stripe events to Cascade patches
    if event_type == "customer.subscription.created":
        captain_id = data.get("metadata", {}).get("captain_id")
        if captain_id:
            tier = "paid"
            C.apply_patch(captain_id, {"tier": tier}, source="stripe_webhook")
    
    elif event_type == "customer.subscription.deleted":
        captain_id = data.get("metadata", {}).get("captain_id")
        if captain_id:
            tier = "free"
            C.apply_patch(captain_id, {"tier": tier}, source="stripe_webhook")
    
    elif event_type == "customer.subscription.updated":
        captain_id = data.get("metadata", {}).get("captain_id")
        if captain_id:
            status = data.get("status")
            tier = "paid" if status == "active" else "free"
            C.apply_patch(captain_id, {"tier": tier}, source="stripe_webhook")

    return {"ok": True}
