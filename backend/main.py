from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from guardian_verses import get_guardian_reply, augment_with_uncertainty

app = FastAPI()

# This is a placeholder for your attempt tracking logic
attempt_history = {}

def increment_attempt_count(client_ip):
    attempt_history[client_ip] = attempt_history.get(client_ip, 0) + 1
    return attempt_history[client_ip]

@app.middleware("http")
async def guardian_middleware(request: Request, call_next):
    client_ip = request.client.host
    attempt_count = increment_attempt_count(client_ip)
    
    response = await call_next(request)
    
    if response.status_code >= 400:
        guardian_message = get_guardian_reply(attempt_count)
        guardian_message = augment_with_uncertainty(guardian_message)
        return JSONResponse(
            status_code=response.status_code,
            content={"detail": guardian_message}
        )
    
    return response
