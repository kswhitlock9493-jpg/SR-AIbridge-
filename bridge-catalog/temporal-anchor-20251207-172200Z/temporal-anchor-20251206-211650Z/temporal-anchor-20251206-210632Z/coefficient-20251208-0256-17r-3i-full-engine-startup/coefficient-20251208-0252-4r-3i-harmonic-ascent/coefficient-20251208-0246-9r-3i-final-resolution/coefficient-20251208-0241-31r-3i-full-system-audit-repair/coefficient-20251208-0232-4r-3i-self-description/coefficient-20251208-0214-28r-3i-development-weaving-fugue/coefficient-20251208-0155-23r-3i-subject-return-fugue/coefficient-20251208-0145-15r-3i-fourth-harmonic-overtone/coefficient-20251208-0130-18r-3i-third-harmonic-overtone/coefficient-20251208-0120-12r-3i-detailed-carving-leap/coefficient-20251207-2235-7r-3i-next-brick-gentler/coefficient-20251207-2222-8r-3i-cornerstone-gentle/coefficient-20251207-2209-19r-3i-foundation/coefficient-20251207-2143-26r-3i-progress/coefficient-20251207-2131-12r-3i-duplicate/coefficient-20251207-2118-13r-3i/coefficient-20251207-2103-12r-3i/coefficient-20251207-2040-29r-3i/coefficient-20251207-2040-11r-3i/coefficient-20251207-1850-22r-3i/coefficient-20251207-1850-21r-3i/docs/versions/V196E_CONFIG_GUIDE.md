# v1.9.6e Environment Configuration Guide

## Heartbeat Configuration

The v1.9.6e heartbeat system supports several environment variables for fine-tuning:

### Basic Configuration

```bash
# Enable/disable heartbeat (default: true)
HEARTBEAT_ENABLED=true

# Heartbeat target URL (auto-detects from RENDER_EXTERNAL_URL if not set)
HEARTBEAT_URL=https://sr-aibridge.onrender.com/health

# Preferred HTTP method (default: auto-detect)
# Options: GET, POST, HEAD
HEARTBEAT_METHOD=GET

# Interval between heartbeats in seconds (default: 30)
HEARTBEAT_INTERVAL_SECONDS=30

# Timeout for each heartbeat request in seconds (default: 5)
HEARTBEAT_TIMEOUT_SECONDS=5
```

### Example Configurations

#### Render Deployment (Default)
```bash
# No configuration needed! 
# Heartbeat auto-detects RENDER_EXTERNAL_URL and uses GET method
```

#### Custom Heartbeat Target
```bash
HEARTBEAT_ENABLED=true
HEARTBEAT_URL=https://custom-health-check.example.com/ping
HEARTBEAT_METHOD=POST
HEARTBEAT_INTERVAL_SECONDS=60
```

#### Disable Heartbeat
```bash
HEARTBEAT_ENABLED=false
# or
HEARTBEAT_ENABLED=0
# or
HEARTBEAT_ENABLED=no
```

#### High-Frequency Monitoring
```bash
HEARTBEAT_ENABLED=true
HEARTBEAT_INTERVAL_SECONDS=15  # Check every 15 seconds
HEARTBEAT_TIMEOUT_SECONDS=3     # 3-second timeout
```

## How It Works

### Method Auto-Detection

1. **Default**: Tries GET first (FastAPI best practice)
2. **On 405**: Reads `Allow` header and tries suggested methods
3. **Fallback Order**: GET → HEAD → POST
4. **Smart Caching**: Once a working method is found, it's used for all subsequent requests

### Backoff Strategy

- **Initial**: 1 second backoff
- **On Failure**: Doubles backoff (2s, 4s, 8s, 16s, 32s...)
- **Maximum**: Caps at 60 seconds
- **Jitter**: Adds random 0-50% of current backoff to prevent thundering herd
- **On Success**: Resets to 1 second

### Example Retry Pattern

```
Attempt 1: Fails → Sleep 30s + 0.5s jitter
Attempt 2: Fails → Sleep 30s + 1.0s jitter  (backoff=2s)
Attempt 3: Fails → Sleep 30s + 2.0s jitter  (backoff=4s)
Attempt 4: Fails → Sleep 30s + 4.0s jitter  (backoff=8s)
Attempt 5: Success → Sleep 30s + 0.5s jitter (backoff reset to 1s)
```

## Health Endpoint

The `/api/control/health` endpoint now accepts both GET and POST:

```bash
# Both work!
curl https://sr-aibridge.onrender.com/api/control/health
curl -X POST https://sr-aibridge.onrender.com/api/control/health
```

Response:
```json
{"status": "ok"}
```

## Render Deployment

### Option 1: Using start.sh (Recommended)
```bash
bash start.sh
```

### Option 2: Using Python module
```bash
python -m bridge_backend
```

### Option 3: Direct uvicorn
```bash
uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
```

All methods automatically respect the `PORT` environment variable set by Render.

## Troubleshooting

### Heartbeat Not Running
Check logs for:
```
INFO:bridge_backend.runtime.heartbeat: initialized ✅
```

If missing, verify:
- `httpx>=0.28.1` is in requirements.txt
- No import errors at startup
- `HEARTBEAT_ENABLED` is not set to false

### 405 Errors Persisting
The v1.9.6e heartbeat should automatically detect and fix these. Check logs for:
```
INFO:bridge_backend.runtime.heartbeat: GET https://... → 200 OK
```

If you see:
```
WARNING:bridge_backend.runtime.heartbeat: POST https://... → 405
```

The next attempt should try a different method automatically.

### Predictive Stabilizer
Tickets mentioning "405" or "Method Not Allowed" are automatically resolved in v1.9.6e since the heartbeat now handles method detection.

Check:
```
bridge_backend/diagnostics/stabilization_tickets/resolved/
```
