# EnvScribe Quick Reference

**v1.9.6u** — Unified Environment Intelligence System

---

## 🚀 Quick Commands

```bash
# Full audit (scan + emit + certify)
python -m bridge_backend.cli.envscribectl audit

# Just scan
python -m bridge_backend.cli.envscribectl scan

# View current report
python -m bridge_backend.cli.envscribectl report

# Generate docs and copy blocks
python -m bridge_backend.cli.envscribectl emit

# Get platform-specific copy block
python -m bridge_backend.cli.envscribectl copy render
python -m bridge_backend.cli.envscribectl copy netlify
python -m bridge_backend.cli.envscribectl copy github_vars
python -m bridge_backend.cli.envscribectl copy github_secrets
```

---

## 📡 API Endpoints

```bash
# Health check
GET /api/envscribe/health

# Full audit workflow
POST /api/envscribe/audit

# Scan only
POST /api/envscribe/scan

# Get current report
GET /api/envscribe/report

# Generate artifacts
POST /api/envscribe/emit

# Get copy block
GET /api/envscribe/copy/{platform}
```

---

## 📂 Output Files

| File | Location | Purpose |
|------|----------|---------|
| `ENV_OVERVIEW.md` | `docs/` | Truth-certified variable documentation |
| `envscribe_report.json` | `bridge_backend/diagnostics/` | Complete scan report (JSON) |
| `envscribe_render.env` | `bridge_backend/diagnostics/` | Render copy block |
| `envscribe_netlify.env` | `bridge_backend/diagnostics/` | Netlify copy block |
| `envscribe_github.txt` | `bridge_backend/diagnostics/` | GitHub vars + secrets |

---

## 🏗️ Architecture

```
┌─────────────┐
│ Parser      │ ──► Scans codebase for env references
└─────────────┘
       │
       ▼
┌─────────────┐
│ EnvScribe   │ ──► Compiles comprehensive variable catalog
└─────────────┘
       │
       ▼
┌─────────────┐
│ EnvRecon    │ ──► Verifies against live platforms
└─────────────┘
       │
       ▼
┌─────────────┐
│ Truth       │ ──► Certifies configuration integrity
└─────────────┘
       │
       ▼
┌─────────────┐
│ Emitters    │ ──► Generates docs & copy blocks
└─────────────┘
       │
       ├──► ENV_OVERVIEW.md
       ├──► Platform configs
       └──► Genesis events
```

---

## 🔗 Integration Points

### Genesis Bus
- Publishes to `genesis.echo` with type `ENVSCRIBE_SCAN_COMPLETE`
- Publishes to `genesis.echo` with type `ENVSCRIBE_CERTIFIED`

### EnvRecon
- Uses EnvRecon data for live platform verification
- Detects drift and missing variables

### Truth Engine
- Requests certification for environment configuration
- Includes certificate ID in documentation when certified

### Steward
- Dashboard displays `ENV_OVERVIEW.md`
- Shows environment status and health

### HXO Nexus
- Consumes scan metrics for cognitive analysis
- Pattern recognition for environment optimization

---

## 🧪 Testing

```bash
# Unit tests (10/10)
python bridge_backend/tests/test_envscribe.py

# Integration tests (3/3)
python bridge_backend/tests/test_envscribe_integration.py

# Existing tests (7/7)
python bridge_backend/tests/test_envsync_pipeline.py
```

---

## 📊 Example Output

### Scan Summary
```
Total variables: 181
Verified: 181
Missing in Render: 0
Missing in Netlify: 0
Missing in GitHub: 0
Drifted: 0
```

### Copy Block (Render)
```bash
BRIDGE_API_URL=
DATABASE_URL=<secret>
DATABASE_TYPE=postgres
SECRET_KEY=<secret>
AUTO_DIAGNOSE=true
CASCADE_MODE=genesis
CORS_ALLOW_ALL=true
ALLOWED_ORIGINS=*
DEBUG=false
LOG_LEVEL=info
PORT=8000
```

---

## 🎯 Use Cases

### 1. Deployment Preparation
```bash
# Generate all platform configs before deployment
envscribectl audit
# Copy blocks from diagnostics/ to platform dashboards
```

### 2. Environment Drift Detection
```bash
# Scan and compare against live platforms
envscribectl scan
# Review drifted variables in report
```

### 3. Documentation Generation
```bash
# Keep ENV_OVERVIEW.md up-to-date
envscribectl emit
```

### 4. CI/CD Integration
```bash
# Add to deployment pipeline
envscribectl audit && git add docs/ENV_OVERVIEW.md
```

---

## 🔐 Security

- Secrets are masked as `<secret>` in copy blocks
- Never commits actual secret values
- Truth Engine certification ensures integrity
- Genesis events are sanitized

---

## 🎛️ Configuration

```bash
# Enable/disable EnvScribe
ENVSCRIBE_ENABLED=true  # (default: true)

# Enable/disable Truth Engine
TRUTH_ENABLED=true

# Enable/disable Genesis Bus
GENESIS_MODE=enabled
```

---

## 📚 Related Docs

- [SCRIBE_README.md](SCRIBE_README.md) — Full documentation
- [ENVRECON_AUTONOMY_INTEGRATION.md](../ENVRECON_AUTONOMY_INTEGRATION.md) — EnvRecon integration
- [GENESIS_V2_GUIDE.md](GENESIS_V2_GUIDE.md) — Genesis Bus architecture

---

**EnvScribe v1.9.6u** — Complete environment self-awareness for the Bridge.
