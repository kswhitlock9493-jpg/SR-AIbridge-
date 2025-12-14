# Genesis Event Flow - Environment Synchronization

**Integration:** EnvSync → Genesis Event Bus → Autonomy, Truth, Blueprint  
**Version:** v1.9.6L  
**Event Namespace:** `envsync.*`

---

## 🧩 Overview

The Environment Synchronization Pipeline publishes events to the Genesis Event Bus, enabling other engines (Autonomy, Truth, Blueprint, Cascade) to observe, react to, and audit environment changes across all platforms.

---

## 📊 Event Topics

### envsync.init

**Published When:** Sync operation begins  
**Purpose:** Notify observers that a sync is starting  
**Subscribers:** Autonomy Engine (for tracking), Truth Engine (for audit)

**Payload:**
```json
{
  "type": "sync_init",
  "source": "render",
  "target": "github",
  "timestamp": "2025-10-11T22:43:00Z",
  "initiated_by": "github_actions",
  "_genesis_timestamp": "2025-10-11T22:43:00Z",
  "_genesis_topic": "envsync.init",
  "_genesis_seq": 1042
}
```

---

### envsync.commit

**Published When:** Sync completes successfully with no drift  
**Purpose:** Confirm environment parity achieved  
**Subscribers:** Truth Engine (immutable log), Blueprint Engine (schema validation)

**Payload:**
```json
{
  "verified_at": "2025-10-11T22:45:00Z",
  "has_drift": false,
  "missing_in_render": [],
  "missing_in_netlify": [],
  "missing_in_github": [],
  "conflicts": {},
  "summary": {
    "total_keys": 45,
    "local_count": 45,
    "render_count": 45,
    "netlify_count": 43,
    "github_count": 45
  },
  "_genesis_timestamp": "2025-10-11T22:45:00Z",
  "_genesis_topic": "envsync.commit",
  "_genesis_seq": 1043
}
```

---

### envsync.drift

**Published When:** Drift detected between platforms  
**Purpose:** Alert Autonomy Engine to take corrective action  
**Subscribers:** Autonomy Engine (auto-healing), Steward Engine (reporting)

**Payload:**
```json
{
  "verified_at": "2025-10-11T22:43:00Z",
  "has_drift": true,
  "missing_in_render": [],
  "missing_in_netlify": ["VAR_A", "VAR_B"],
  "missing_in_github": ["AUTO_DIAGNOSE", "CORS_ALLOW_ALL"],
  "conflicts": {
    "DEBUG": {
      "render": "false",
      "netlify": "true",
      "github": "<secret>"
    }
  },
  "summary": {
    "total_keys": 45,
    "drift_count": 5
  },
  "_genesis_timestamp": "2025-10-11T22:43:00Z",
  "_genesis_topic": "envsync.drift",
  "_genesis_seq": 1041
}
```

---

## 🔄 Event Flow Diagram

```
┌─────────────────────┐
│  Sync Triggered     │
│  (CLI or Actions)   │
└──────────┬──────────┘
           │
           ▼
    [envsync.init]
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌─────────────┐   ┌──────────────┐
    │  Autonomy   │   │    Truth     │
    │   Engine    │   │   Engine     │
    │ (tracking)  │   │  (logging)   │
    └─────────────┘   └──────────────┘
           │
           ▼
┌──────────────────────┐
│ EnvRecon Reconcile   │
│ (Fetch all platforms)│
└──────────┬───────────┘
           │
           ▼
      ┌─────────┐
      │Has Drift?│
      └────┬────┘
           │
      ┌────┴────┐
      │         │
     Yes       No
      │         │
      ▼         ▼
[envsync.drift]  [envsync.commit]
      │               │
      ├───────┐       ├───────────┐
      │       │       │           │
      ▼       ▼       ▼           ▼
 ┌────────┐ ┌─────┐ ┌───────┐ ┌─────────┐
 │Autonomy│ │Truth│ │ Truth │ │Blueprint│
 │Auto-   │ │Audit│ │ Audit │ │ Schema  │
 │heal    │ │     │ │       │ │  Check  │
 └────────┘ └─────┘ └───────┘ └─────────┘
```

---

## 🎯 Integration Points

### Autonomy Engine

**Subscribes to:** `envsync.drift`  
**Action:** Triggers auto-healing workflow

**Implementation:**
```python
# bridge_backend/bridge_core/engines/autonomy/observers.py
async def on_envsync_drift(event):
    drift_count = len(event.get('missing_in_github', []))
    if drift_count > 0:
        await trigger_github_sync()
```

---

### Truth Engine

**Subscribes to:** `envsync.commit`, `envsync.drift`  
**Action:** Creates immutable audit log entry

**Implementation:**
```python
# bridge_backend/bridge_core/engines/truth/ledger.py
async def on_envsync_event(event):
    ledger_entry = {
        "event_id": event.get('_genesis_seq'),
        "topic": event.get('_genesis_topic'),
        "timestamp": event.get('_genesis_timestamp'),
        "payload": event,
        "signature": sign_event(event)
    }
    await append_to_ledger(ledger_entry)
```

---

### Blueprint Engine

**Subscribes to:** `envsync.commit`  
**Action:** Validates environment schema compliance

**Implementation:**
```python
# bridge_backend/bridge_core/engines/blueprint/validators.py
async def on_envsync_commit(event):
    summary = event.get('summary', {})
    expected_min_vars = 40
    
    if summary.get('total_keys', 0) < expected_min_vars:
        await publish_validation_warning({
            "type": "schema_drift",
            "expected": expected_min_vars,
            "actual": summary.get('total_keys')
        })
```

---

### Cascade Engine

**Subscribes to:** `envsync.commit`  
**Action:** Triggers frontend config rehydration

**Implementation:**
```python
# bridge_backend/bridge_core/engines/cascade/sync.py
async def on_envsync_commit(event):
    # Notify frontend to reload config
    await websocket_broadcast({
        "type": "config_update",
        "timestamp": event.get('_genesis_timestamp')
    })
```

---

## 🔐 Permission Filtering

Genesis Bus applies Guardian permission checks before publishing:

```python
# In genesis/bus.py
async def publish(topic: str, event: Dict):
    # Guardian gate check
    from bridge_backend.bridge_core.guardians.gate import guardian_gate
    
    allowed, reason = await guardian_gate.check_publish_permission(
        topic=topic,
        event=event,
        context={"role": get_current_role()}
    )
    
    if not allowed:
        await self._emit_blocked_event(topic, event, reason)
        return
    
    # Proceed with publish
    ...
```

---

## 📝 Event History & Introspection

### Query Event History

```python
from bridge_backend.genesis.bus import genesis_bus

# Get last 10 envsync events
history = genesis_bus.get_event_history(limit=10)
envsync_events = [e for e in history if e['_genesis_topic'].startswith('envsync.')]
```

### Event Persistence

Events are stored in:
- **Genesis Event Log:** `bridge_backend/logs/genesis_events.json`
- **Truth Ledger:** `bridge_backend/.genesis/truth_ledger.json`

---

## 🧪 Testing Event Flow

### Publish Test Event

```python
import asyncio
from bridge_backend.genesis.bus import genesis_bus

async def test_event():
    await genesis_bus.publish("envsync.drift", {
        "verified_at": "2025-10-11T22:43:00Z",
        "has_drift": True,
        "missing_in_github": ["TEST_VAR"]
    })
    
    print("✅ Test event published")

asyncio.run(test_event())
```

### Subscribe to Events

```python
from bridge_backend.genesis.bus import genesis_bus

def handle_drift(event):
    print(f"🚨 Drift detected: {event.get('missing_in_github')}")

genesis_bus.subscribe("envsync.drift", handle_drift)
```

---

## 📊 Monitoring & Alerts

### Event Metrics

Track event volume via Genesis introspection:

```python
from bridge_backend.genesis.introspection import get_event_stats

stats = get_event_stats()
print(f"Total envsync.drift events: {stats.get('envsync.drift', 0)}")
```

### Alert Thresholds

Configure alerts for excessive drift:

```python
# In bridge_backend/bridge_core/engines/autonomy/thresholds.py
DRIFT_ALERT_THRESHOLD = 10  # Alert if >10 vars drifted
DRIFT_FREQUENCY_LIMIT = 5   # Alert if drift detected >5 times in 1 hour
```

---

## 🔗 Related Documentation

- [Genesis Architecture](../GENESIS_ARCHITECTURE.md)
- [Autonomy Integration](../AUTONOMY_INTEGRATION.md)
- [Truth Engine Guide](../TRUTH_ENGINE_GUIDE.md)
- [Genesis Linkage Guide](../GENESIS_LINKAGE_GUIDE.md)

---

**Last Updated:** October 11, 2025  
**Maintained by:** Genesis Integration Team
