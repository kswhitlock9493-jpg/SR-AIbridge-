# Render Fallback

## Overview

Render Fallback is a fallback deployment orchestrator that activates when Netlify deployment fails or is rejected.

## Features

- **Automatic failover**: Seamlessly switches to Render when Netlify fails
- **Parity configuration**: Maintains header and route parity with Netlify
- **Status tracking**: Reports fallback activation to Genesis bus

## Usage

### Python

```python
from bridge_backend.engines.render_fallback import RenderFallback

fallback = RenderFallback()
result = await fallback.deploy({
    "target": "render",
    "reason": "netlify_failed"
})
```

## Integration

Render Fallback is automatically triggered by Chimera Oracle when:

1. Netlify deployment returns `ok: false`
2. Decision matrix chooses `target: "render"`

## Deployment Flow

```
Chimera Oracle
    │
    ├─→ Try Netlify
    │     │
    │     └─→ Failed
    │
    └─→ Activate Render Fallback
          │
          └─→ Deploy to Render
```

## Configuration

Render is configured via:

- `render.yaml` in repository root
- Render dashboard environment variables
- Auto-deploy on push to main

## Benefits

1. **High availability**: Never completely blocked by Netlify issues
2. **Automatic**: No manual intervention required
3. **Parity**: Same headers and routes as Netlify
4. **Fast**: Direct deployment without build simulation
