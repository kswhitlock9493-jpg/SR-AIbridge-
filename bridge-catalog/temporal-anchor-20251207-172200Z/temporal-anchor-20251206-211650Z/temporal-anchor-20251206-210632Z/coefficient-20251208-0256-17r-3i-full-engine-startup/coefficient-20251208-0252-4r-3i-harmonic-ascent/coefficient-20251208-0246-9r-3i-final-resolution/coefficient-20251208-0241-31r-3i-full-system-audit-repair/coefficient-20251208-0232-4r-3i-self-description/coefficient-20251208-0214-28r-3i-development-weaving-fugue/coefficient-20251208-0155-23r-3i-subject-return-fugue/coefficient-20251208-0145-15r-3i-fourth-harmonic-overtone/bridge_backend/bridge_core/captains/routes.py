from fastapi import APIRouter

router = APIRouter(prefix="/captains", tags=["captains"])

@router.get("/messages")
def get_captain_messages():
    """Return an array of captain messages (stub)."""
    return {"messages": []}

@router.post("/send")
def send_captain_message(message: dict):
    """Send a captain message (stub)."""
    return {"status": "sent", "message": message}
