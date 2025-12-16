# Hydra Guard v2

## Overview

Hydra Guard v2 is a Netlify configuration synthesis and validation engine that automatically generates and validates security headers, redirects, and configuration files.

## Features

### 1. Security Headers Synthesis

Automatically generates security headers:

- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: same-origin`
- `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`
- `Access-Control-Allow-Origin: *`

### 2. Redirect Rules

Creates redirect rules for:

- API proxy to backend: `/api/* → https://sr-aibridge.onrender.com/:splat`
- Health check: `/health → /index.html`

### 3. Configuration Files

Manages:

- `public/_headers` - Security headers
- `public/_redirects` - Redirect rules
- `netlify.toml` - Build configuration

## Usage

### Python

```python
from bridge_backend.engines.hydra import HydraGuard

guard = HydraGuard()
result = await guard.synthesize_and_validate()
```

### API

```bash
curl -X POST http://localhost:8000/api/hydra/synthesize
```

## Idempotence

All synthesis operations are idempotent - running multiple times produces the same result without duplication.

## Integration with Chimera

Hydra Guard v2 is integrated into the Chimera Oracle pipeline via the `NetlifyGuard` adapter.

## File Structure

```
public/
  _headers      # Security headers
  _redirects    # Redirect rules
netlify.toml    # Build configuration
```
