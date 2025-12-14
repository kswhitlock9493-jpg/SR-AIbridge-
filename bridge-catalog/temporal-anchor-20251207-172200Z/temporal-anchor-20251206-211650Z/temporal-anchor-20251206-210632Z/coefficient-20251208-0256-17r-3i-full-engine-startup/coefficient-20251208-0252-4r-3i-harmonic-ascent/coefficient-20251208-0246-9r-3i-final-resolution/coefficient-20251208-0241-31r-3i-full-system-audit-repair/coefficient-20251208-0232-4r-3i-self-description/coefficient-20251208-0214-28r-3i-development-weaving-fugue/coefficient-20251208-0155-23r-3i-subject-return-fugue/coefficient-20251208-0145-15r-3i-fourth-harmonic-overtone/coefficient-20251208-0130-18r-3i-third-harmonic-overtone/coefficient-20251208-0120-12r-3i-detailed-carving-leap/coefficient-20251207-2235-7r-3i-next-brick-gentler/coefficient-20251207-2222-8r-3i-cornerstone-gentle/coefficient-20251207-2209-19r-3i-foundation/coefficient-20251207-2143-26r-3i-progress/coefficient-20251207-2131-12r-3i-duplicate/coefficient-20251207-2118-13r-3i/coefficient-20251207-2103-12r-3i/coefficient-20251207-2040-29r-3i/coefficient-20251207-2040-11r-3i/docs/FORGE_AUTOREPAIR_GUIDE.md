# Forge Auto-Repair Guide

## 🛠️ Forge - Autonomous Repair System

Forge is the Bridge's autonomous repair engine that automatically fixes configuration drift, missing files, and environment mismatches.

### Purpose

- **Detect** repository configuration issues
- **Repair** automatically without manual intervention
- **Certify** repairs through Truth Engine
- **Report** via Genesis Bus

### What Forge Fixes

#### 1. Missing Netlify Configuration

Forge creates default files when missing:

- `_headers` - Security headers
- `_redirects` - Routing rules
- `netlify.toml` - Build configuration

#### 2. Environment Drift

Fixes:
- Missing `.env` (creates from `.env.example`)
- Environment variable mismatches
- Configuration inconsistencies

#### 3. Build Configuration

Ensures:
- Proper build commands
- Correct publish directories
- Valid serverless function setup

### Architecture

```
┌─────────────────────────────┐
│   Forge Engine              │
│                             │
│  ┌─────────────────────┐   │
│  │ Repository Scanner  │   │
│  └─────────────────────┘   │
│           ↓                 │
│  ┌─────────────────────┐   │
│  │ Issue Detection     │   │
│  └─────────────────────┘   │
│           ↓                 │
│  ┌─────────────────────┐   │
│  │ Repair Tools        │   │
│  └─────────────────────┘   │
│           ↓                 │
│  ┌─────────────────────┐   │
│  │ Truth Certification │   │
│  └─────────────────────┘   │
└─────────────────────────────┘
```

### Usage

#### Programmatic

```python
from bridge_backend.engines.forge.core import ForgeEngine

engine = ForgeEngine()
report = await engine.run_full_repair(scan_only=False)

print(f"Fixed: {report['fixed']}/{len(report['issues'])}")
```

#### CLI

```bash
# Full repair
cd bridge_backend/engines/forge
python3 core.py

# Scan only (no fixes)
python3 core.py --scan-only
```

#### Auto-Triggered

Forge is automatically triggered by:
- Sanctum on predeploy failure
- Elysium during health cycles
- Genesis heal events

### Repair Process

1. **Scan** - Detect all issues in repository
2. **Plan** - Determine which fixes to apply
3. **Execute** - Apply fixes safely
4. **Certify** - Request Truth Engine validation
5. **Publish** - Emit Genesis Bus event

### Default Files Created

#### `_headers`

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  X-XSS-Protection: 1; mode=block
```

#### `_redirects`

```
/api/*  /.netlify/functions/server  200
/*      /index.html                200
```

#### `netlify.toml`

```toml
[build]
  command = "npm run build"
  publish = "frontend/dist"
  functions = "netlify/functions"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/server"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Configuration

Environment variables:

```bash
# Enable/disable Forge
FORGE_ENABLED=true

# Genesis integration
GENESIS_MODE=enabled

# Truth certification
TRUTH_MANDATORY=true
```

### Genesis Bus Events

Forge publishes repair events:

```python
await genesis_bus.publish("forge.repair.applied", {
    "count": 3,
    "total_issues": 5,
    "timestamp": "...",
    "certified": True
})
```

### Integration with ARIE

Forge focuses on **configuration** while ARIE handles **code quality**:

| Engine | Scope |
|--------|-------|
| **Forge** | Config files, env vars, build setup |
| **ARIE** | Deprecated code, unused imports, code smells |

They work together:
1. Sanctum detects config issue
2. Forge repairs configuration
3. ARIE audits code quality
4. Truth certifies both

### Safety Features

1. **Scan-only mode** - Preview changes without applying
2. **Truth certification** - All repairs must be certified
3. **Genesis audit trail** - Every repair is logged
4. **Rollback support** - Can revert if needed

### Example Output

```
🛠️ Forge: Executing autonomous repo repair sequence...
🛠️ Forge: Detected 3 issue(s)
🛠️ Forge: Created default _headers
🛠️ Forge: Created default _redirects
🛠️ Forge: Created default netlify.toml
✅ Forge: Truth certified repair completion
🛠️ Forge: Repair complete - 3/3 fixed
```

### Troubleshooting

**Forge not fixing issues?**
- Check `FORGE_ENABLED=true`
- Verify file permissions
- Review Genesis Bus events

**Repairs not being certified?**
- Ensure Truth Engine is available
- Check `TRUTH_MANDATORY` setting
- Verify Genesis Bus connection

**Want to preview repairs first?**
```bash
python3 core.py --scan-only
```

### Best Practices

1. **Run regularly** - Include in health cycles
2. **Review repairs** - Check Genesis events after auto-repair
3. **Customize defaults** - Modify repair templates as needed
4. **Monitor trends** - Track which repairs are most common

### Related

- [Sanctum Overview](SANCTUM_OVERVIEW.md)
- [ARIE Sanctum Loop](ARIE_SANCTUM_LOOP.md)
- [Total Autonomy Protocol](TOTAL_AUTONOMY_PROTOCOL.md)
