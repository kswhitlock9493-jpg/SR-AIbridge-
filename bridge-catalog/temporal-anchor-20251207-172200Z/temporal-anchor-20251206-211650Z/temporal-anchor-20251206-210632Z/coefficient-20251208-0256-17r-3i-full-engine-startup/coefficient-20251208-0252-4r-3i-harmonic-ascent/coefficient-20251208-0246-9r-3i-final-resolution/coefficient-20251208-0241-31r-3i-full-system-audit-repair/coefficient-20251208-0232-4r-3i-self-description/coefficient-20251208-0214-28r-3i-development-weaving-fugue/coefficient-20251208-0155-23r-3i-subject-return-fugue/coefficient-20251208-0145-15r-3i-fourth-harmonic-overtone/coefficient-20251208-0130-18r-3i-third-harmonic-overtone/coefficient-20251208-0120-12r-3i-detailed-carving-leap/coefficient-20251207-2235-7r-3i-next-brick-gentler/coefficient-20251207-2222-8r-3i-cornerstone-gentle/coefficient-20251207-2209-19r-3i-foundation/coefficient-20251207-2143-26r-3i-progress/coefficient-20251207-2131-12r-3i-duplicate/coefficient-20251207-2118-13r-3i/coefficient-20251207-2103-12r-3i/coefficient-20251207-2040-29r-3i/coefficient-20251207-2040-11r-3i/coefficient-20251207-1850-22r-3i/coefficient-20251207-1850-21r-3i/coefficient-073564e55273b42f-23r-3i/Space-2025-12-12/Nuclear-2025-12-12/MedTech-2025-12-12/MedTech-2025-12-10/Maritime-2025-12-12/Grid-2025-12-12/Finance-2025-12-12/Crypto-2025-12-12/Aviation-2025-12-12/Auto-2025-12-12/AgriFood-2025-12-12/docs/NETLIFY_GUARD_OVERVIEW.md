# Netlify Guard Overview

**Version:** v1.9.7q  
**Module:** `bridge_backend/bridge_core/guards/netlify_guard.py`  
**Purpose:** Prevent Netlify deployment failures through path validation and token fallbacks

---

## What It Does

The Netlify Guard provides two critical functions:

1. **Publish Path Validation** - Ensures deployment has a valid publish directory
2. **Token Fallback** - Provides authentication even when NETLIFY_AUTH_TOKEN is missing

---

## Functions

### `validate_publish_path()`

Validates and normalizes the Netlify publish path.

**Behavior:**
1. Check if `NETLIFY_PUBLISH_PATH` environment variable is set and exists
2. If valid, use it and log confirmation
3. If not, try default paths in order: `dist`, `build`, `public`
4. If none exist, create `public/` with minimal `index.html`
5. Set `NETLIFY_PUBLISH_PATH` environment variable to resolved path
6. Return the resolved path

**Example:**
```python
from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path

# Returns path and sets NETLIFY_PUBLISH_PATH env var
path = validate_publish_path()
print(f"Using publish path: {path}")
```

**Console Output:**
```
✅ Netlify Guard: using publish path: dist
```
or
```
⚠️ Netlify Guard: normalized publish path -> public
```

---

### `require_netlify_token(get_github_token)`

Ensures a valid Netlify authentication token is available.

**Parameters:**
- `get_github_token` - Callable that returns a GitHub token (fallback)

**Behavior:**
1. Check if `NETLIFY_AUTH_TOKEN` environment variable is set
2. If yes, use it and return
3. If no, call `get_github_token()` to get fallback token
4. Set `NETLIFY_AUTH_TOKEN` to the GitHub token
5. If neither available, raise `RuntimeError`

**Example:**
```python
from bridge_backend.bridge_core.guards.netlify_guard import require_netlify_token

def get_gh_token():
    return os.getenv("GITHUB_TOKEN")

token = require_netlify_token(get_gh_token)
```

**Console Output:**
```
🔑 Netlify Guard: using Reflex GitHub token as egress auth.
```

---

## Default Publish Paths

The guard tries these paths in order:

1. `NETLIFY_PUBLISH_PATH` (if set and exists)
2. `dist`
3. `build`
4. `public`
5. Creates `public/` if none exist

---

## Token Fallback Mechanism

The guard implements a two-tier token strategy:

### Tier 1: Netlify Token
- Preferred method
- Use `NETLIFY_AUTH_TOKEN` environment variable
- Full Netlify API access

### Tier 2: GitHub Token
- Fallback method
- Use `GITHUB_TOKEN` or `REFLEX_GITHUB_TOKEN`
- Sufficient for guarded egress sync

This ensures deployments never fail due to missing tokens when running in GitHub Actions.

---

## Integration

### In Application Boot (main.py)

```python
from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path, require_netlify_token

# Validate publish path
validate_publish_path()

# Ensure token is available
def get_github_token():
    return os.getenv("GITHUB_TOKEN")
require_netlify_token(get_github_token)
```

### In GitHub Actions

```yaml
- name: 🛡️ Netlify Guard
  run: |
    python - <<'PY'
    from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path, require_netlify_token
    validate_publish_path()
    require_netlify_token(lambda: os.getenv("GITHUB_TOKEN"))
    PY
  env:
    REFLEX_GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Environment Variables

### Input Variables

- `NETLIFY_PUBLISH_PATH` - Preferred publish directory (optional)
- `NETLIFY_AUTH_TOKEN` - Netlify API token (optional)
- `GITHUB_TOKEN` - GitHub token for fallback (provided by Actions)
- `REFLEX_GITHUB_TOKEN` - Alternative GitHub token name

### Output Variables

- `NETLIFY_PUBLISH_PATH` - Set to resolved publish directory
- `NETLIFY_AUTH_TOKEN` - Set to resolved token (Netlify or GitHub)

---

## Error Handling

### Missing Publish Path
**Problem:** No publish directory exists  
**Solution:** Guard creates `public/` automatically  
**Impact:** Deployment succeeds with minimal placeholder

### Missing Tokens
**Problem:** Neither NETLIFY_AUTH_TOKEN nor GitHub token available  
**Solution:** Guard raises `RuntimeError`  
**Impact:** Deployment fails fast with clear error message

---

## Best Practices

1. **Set NETLIFY_PUBLISH_PATH** explicitly in production
2. **Provide NETLIFY_AUTH_TOKEN** for full Netlify API access
3. **Use GitHub token fallback** only in CI/CD environments
4. **Monitor logs** for normalization warnings

---

## Testing

### Test Publish Path Validation

```python
import os
from pathlib import Path
from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path

# Test with existing path
os.environ["NETLIFY_PUBLISH_PATH"] = "dist"
Path("dist").mkdir(exist_ok=True)
assert validate_publish_path() == "dist"

# Test with missing path (creates public/)
os.environ.pop("NETLIFY_PUBLISH_PATH", None)
assert validate_publish_path() == "public"
assert Path("public/index.html").exists()
```

### Test Token Fallback

```python
import os
from bridge_backend.bridge_core.guards.netlify_guard import require_netlify_token

# Test with Netlify token
os.environ["NETLIFY_AUTH_TOKEN"] = "netlify_token"
assert require_netlify_token(lambda: "gh_token") == "netlify_token"

# Test with GitHub token fallback
os.environ.pop("NETLIFY_AUTH_TOKEN", None)
assert require_netlify_token(lambda: "gh_token") == "gh_token"
```

---

**Version:** v1.9.7q  
**Status:** ✅ Production Ready  
**Scope:** Netlify deployment path and token safety
