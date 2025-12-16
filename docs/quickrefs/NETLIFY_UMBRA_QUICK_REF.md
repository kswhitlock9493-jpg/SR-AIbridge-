# Umbra + Netlify Integration — Quick Reference v1.9.7e

## 🚀 Quick Start

### 1. Enable Netlify Validation

Add to your `.env`:
```bash
UMBRA_NETLIFY_SYNC=true
NETLIFY_OPTIONAL_PREVIEW_CHECKS=true
```

### 2. Run Validation

**Standalone:**
```bash
python3 scripts/validate_netlify.py
```

**With Umbra Memory:**
```python
from bridge_backend.engines.netlify_validator import NetlifyValidator
from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory

memory = UmbraMemory()
validator = NetlifyValidator(umbra_memory=memory)
result = await validator.validate_with_recall()
```

### 3. Record Netlify Events

```python
from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory

memory = UmbraMemory()
await memory.record_netlify_event(
    event_type="config_edit",
    data={"file": "netlify.toml", "change": "fixed header rules"},
    intent="repair"  # or "optimize" or "bypass"
)
```

---

## 📡 API Endpoints

### Validate Configuration
```bash
POST /api/netlify/validate
# RBAC: Admiral, Captain
# Response: Validation result with status
```

### Validate with Memory Recall
```bash
POST /api/netlify/validate/recall
# RBAC: Admiral, Captain
# Response: Validation result + recall information
```

### Get Metrics
```bash
GET /api/netlify/metrics
# RBAC: Admiral, Captain, Observer
# Response: Validator metrics
```

### Get Status
```bash
GET /api/netlify/status
# RBAC: All roles
# Response: Validator status and version
```

---

## 🧠 Intent Classification

Umbra automatically classifies Netlify events:

| Intent | Description | Examples |
|--------|-------------|----------|
| **repair** | Syntax fixes or patches | Fixing duplicate rules, env patches |
| **optimize** | Performance improvements | New redirect logic, caching rules |
| **bypass** | Skip validation | Emergency deployments, test overrides |

---

## 🔍 Validation Checks

The validator checks:

✅ **netlify.toml**
- Build command present
- Required sections exist
- No duplicate header rules
- No duplicate redirect rules

✅ **_headers** (optional)
- No duplicate path definitions
- Proper syntax

✅ **_redirects** (optional)
- No duplicate redirect rules
- Valid format

✅ **Build Script**
- scripts/netlify_build.sh exists

---

## 🔄 CI/CD Integration

The workflow runs automatically on:
- Pull requests changing Netlify files
- Pushes to main/release branches
- Manual dispatch

**Workflow File:** `.github/workflows/netlify_validation.yml`

---

## 📊 Metrics

### Validator Metrics
```python
validator = NetlifyValidator()
metrics = validator.get_metrics()

# Returns:
{
  "enabled": true,
  "truth_available": true,
  "memory_available": true
}
```

### Umbra Memory Metrics
```python
memory = UmbraMemory()
metrics = memory.get_metrics()

# Categories include:
# - netlify_validation
# - netlify_event
# - repair
# - anomaly
# - echo
```

---

## 🧪 Testing

### Run Tests
```bash
# Netlify validator tests
python3 -m pytest bridge_backend/tests/test_netlify_validator.py -v

# All Umbra tests (including Netlify)
python3 -m pytest bridge_backend/tests/test_umbra_* -v
```

### Manual Testing
```bash
# Test validation script
python3 scripts/validate_netlify.py

# Test with Python
python3 -c "
from bridge_backend.engines.netlify_validator import validate_netlify_rules
result = validate_netlify_rules()
print(result['status'])
"
```

---

## 🔐 RBAC

| Role | Permissions |
|------|-------------|
| **Admiral** | Full control: validate, record, override |
| **Captain** | Validate, recall, read metrics |
| **Observer** | Read-only metrics and logs |

---

## 🐛 Troubleshooting

### Validation Fails
```bash
# Check the output for specific errors
python3 scripts/validate_netlify.py

# Common issues:
# - Duplicate header rules
# - Duplicate redirect rules
# - Missing build command
# - Invalid syntax in netlify.toml
```

### Memory Not Recording
```bash
# Check if Umbra Memory is enabled
echo $UMBRA_MEMORY_ENABLED  # should be "true"

# Check if Netlify sync is enabled
echo $UMBRA_NETLIFY_SYNC    # should be "true"

# Verify vault directory exists
ls -la vault/umbra/
```

### API Endpoints Not Working
```bash
# Check if routes are registered
# The routes should be in: bridge_backend/engines/netlify_routes.py

# Verify RBAC is configured
# Check your authentication middleware
```

---

## 📚 Related Documentation

- [V197E_IMPLEMENTATION.md](V197E_IMPLEMENTATION.md) - Full implementation details
- [UMBRA_README.md](UMBRA_README.md) - Umbra Cognitive Stack documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 🎯 Common Use Cases

### 1. Pre-Deploy Validation
```bash
# In your CI/CD pipeline
python3 scripts/validate_netlify.py
if [ $? -ne 0 ]; then
  echo "Validation failed, blocking deploy"
  exit 1
fi
```

### 2. Learning from Failures
```python
# After fixing a Netlify issue
memory = UmbraMemory()
await memory.record_netlify_event(
    event_type="deploy_fix",
    data={
        "issue": "duplicate header rules",
        "fix": "removed duplicate /*",
        "commit": "abc123"
    },
    intent="repair"
)
```

### 3. Checking Historical Fixes
```python
# Recall past Netlify events
memory = UmbraMemory()
events = await memory.recall(category="netlify_event", limit=10)

for event in events:
    print(f"Intent: {event['data']['intent']}")
    print(f"Event: {event['data']['event_type']}")
```

---

**Version:** v1.9.7e  
**Status:** ✅ Production Ready  
**Engines:** Umbra + Netlify Validator + Truth + ChronicleLoom
