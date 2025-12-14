# GitHub Environment Hook - Integration Guide

This guide shows how to integrate the GitHub Environment Hook into your workflow for autonomous environment synchronization.

---

## 🎯 Quick Start

### 1. Verify Installation

Check that the hook script is installed:

```bash
ls -l .github/scripts/github_envhook.py
```

### 2. Test Manual Trigger

Trigger a sync manually to verify Genesis integration:

```bash
python3 .github/scripts/github_envhook.py --trigger
```

Expected output:
```
🔧 Manual trigger mode
🚀 Triggering environment sync events...
✅ Published: envmirror.sync.start
✅ Published: envduo.audit
🎯 Environment sync triggered successfully
✅ Manual trigger complete
```

### 3. Start Watching (Development)

For development, run the watcher in a terminal:

```bash
python3 .github/scripts/github_envhook.py --watch
```

---

## 🔄 Integration Patterns

### Pattern 1: GitHub Actions Workflow

Create `.github/workflows/env-watcher.yml`:

```yaml
name: Environment Watcher

on:
  push:
    branches:
      - main
    paths:
      - '.github/environment.json'
  
  workflow_dispatch:

jobs:
  trigger-sync:
    runs-on: ubuntu-latest
    name: Trigger Environment Sync
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Trigger Environment Sync
        env:
          GENESIS_MODE: enabled
          GENESIS_TRACE_LEVEL: 2
        run: |
          python3 .github/scripts/github_envhook.py --trigger
      
      - name: Upload Logs
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: envhook-logs
          path: logs/github_envhook_triggers.log
```

### Pattern 2: Background Service (Production)

Run as a systemd service on your deployment server:

**File:** `/etc/systemd/system/github-envhook.service`

```ini
[Unit]
Description=GitHub Environment Hook Watcher
After=network.target

[Service]
Type=simple
User=bridge
WorkingDirectory=/opt/sr-aibridge
Environment="GENESIS_MODE=enabled"
Environment="GENESIS_TRACE_LEVEL=1"
ExecStart=/usr/bin/python3 .github/scripts/github_envhook.py --watch
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable github-envhook
sudo systemctl start github-envhook
sudo systemctl status github-envhook
```

### Pattern 3: Docker Container

**File:** `Dockerfile.envhook`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY .github/scripts/github_envhook.py .github/scripts/
COPY .github/environment.json .github/
COPY bridge_backend bridge_backend/

# Create logs directory
RUN mkdir -p logs

# Set environment
ENV GENESIS_MODE=enabled
ENV GENESIS_TRACE_LEVEL=1

# Run watcher
CMD ["python3", ".github/scripts/github_envhook.py", "--watch"]
```

Build and run:
```bash
docker build -f Dockerfile.envhook -t sr-aibridge-envhook .
docker run -d --name envhook --restart always sr-aibridge-envhook
```

---

## 🔌 Subscribing to Events

### Example: EnvMirror Engine Subscriber

```python
# bridge_backend/engines/envmirror/core.py

import asyncio
from genesis.bus import genesis_bus

class EnvMirrorEngine:
    def __init__(self):
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        """Subscribe to environment hook events"""
        genesis_bus.subscribe("envmirror.sync.start", self.on_sync_triggered)
    
    async def on_sync_triggered(self, event: dict):
        """Handle sync trigger from environment hook"""
        print(f"🔄 EnvMirror sync triggered by: {event['source']}")
        
        file_hash = event.get('file_hash')
        version = event.get('version')
        
        # Load environment.json
        env_config = self.load_environment_config()
        
        # Perform cross-platform sync
        await self.sync_github_to_render(env_config)
        await self.sync_github_to_netlify(env_config)
        
        # Publish completion event
        await genesis_bus.publish("envmirror.sync.complete", {
            "type": "sync_completed",
            "source": "envmirror",
            "triggered_by": event['source'],
            "file_hash": file_hash,
            "status": "success",
            "platforms_synced": ["github", "render", "netlify"]
        })
```

### Example: EnvDuo Audit Subscriber

```python
# bridge_backend/engines/envduo/core.py

from genesis.bus import genesis_bus
from engines.arie.core import ARIEEngine
from engines.envrecon.engine import EnvReconEngine

class EnvDuoEngine:
    def __init__(self):
        self.arie = ARIEEngine()
        self.envrecon = EnvReconEngine()
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        """Subscribe to environment hook events"""
        genesis_bus.subscribe("envduo.audit", self.on_audit_triggered)
    
    async def on_audit_triggered(self, event: dict):
        """Handle audit trigger from environment hook"""
        print(f"🔍 EnvDuo audit triggered by: {event['source']}")
        
        # Phase 1: ARIE integrity scan
        arie_results = await self.arie.scan_environment_json()
        
        # Phase 2: EnvRecon parity check
        recon_results = await self.envrecon.audit_cycle()
        
        # Combine results
        has_drift = arie_results['issues_found'] or recon_results['has_drift']
        
        if has_drift:
            # Trigger healing
            await genesis_bus.publish("envduo.heal", {
                "type": "heal_triggered",
                "source": "envduo",
                "arie_issues": arie_results['issues'],
                "recon_drift": recon_results['drift'],
                "auto_heal": True
            })
            
            # Apply fixes
            await self.apply_healing(arie_results, recon_results)
```

### Example: Truth Engine Audit Logger

```python
# bridge_backend/engines/truth/ledger.py

from genesis.bus import genesis_bus
import json
from datetime import datetime, UTC

class TruthLedger:
    def __init__(self):
        self.ledger_path = "logs/truth_certified_actions.log"
        self.setup_subscriptions()
    
    def setup_subscriptions(self):
        """Subscribe to all environment events for audit trail"""
        genesis_bus.subscribe("envmirror.sync.start", self.log_event)
        genesis_bus.subscribe("envmirror.sync.complete", self.log_event)
        genesis_bus.subscribe("envduo.audit", self.log_event)
        genesis_bus.subscribe("envduo.heal", self.log_event)
    
    async def log_event(self, event: dict):
        """Create immutable audit log entry"""
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_id": event.get('_genesis_seq'),
            "topic": event.get('_genesis_topic'),
            "payload": event,
            "signature": self.sign_event(event),
            "certified": True
        }
        
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        print(f"✅ Truth-certified: {event.get('_genesis_topic')}")
```

---

## 📊 Monitoring & Observability

### View Event History

Check Genesis event history:

```bash
curl http://localhost:8000/api/genesis/events?topic=envmirror.sync.start&limit=10
```

Response:
```json
{
  "events": [
    {
      "topic": "envmirror.sync.start",
      "timestamp": "2025-10-12T18:25:15.700113Z",
      "seq": 1042,
      "type": "sync_triggered"
    }
  ],
  "total": 1,
  "limit": 10
}
```

### View Trigger Logs

```bash
tail -f logs/github_envhook_triggers.log | jq .
```

### View State

```bash
cat logs/github_envhook_state.json | jq .
```

Output:
```json
{
  "last_hash": "c6accf48a1d9e8f2b3d4c5e6f7a8b9c0...",
  "last_modified": "2025-10-12T18:25:15.700113Z",
  "file_path": ".github/environment.json"
}
```

---

## 🧪 Testing Integration

### Test 1: Modify environment.json

```bash
# Start watcher in background
python3 .github/scripts/github_envhook.py --watch &
WATCHER_PID=$!

# Wait for initialization
sleep 2

# Modify environment.json
jq '.version = "1.9.6y"' .github/environment.json > /tmp/env.json
mv /tmp/env.json .github/environment.json

# Wait for detection
sleep 6

# Check logs
grep "sync_triggered" logs/github_envhook_triggers.log

# Cleanup
kill $WATCHER_PID
```

### Test 2: Subscribe to Events (Python)

```python
import asyncio
from genesis.bus import genesis_bus

async def test_subscription():
    received_events = []
    
    def handler(event):
        received_events.append(event)
        print(f"Received: {event['type']}")
    
    genesis_bus.subscribe("envmirror.sync.start", handler)
    genesis_bus.subscribe("envduo.audit", handler)
    
    # Trigger manually
    import subprocess
    subprocess.run([
        "python3", 
        ".github/scripts/github_envhook.py", 
        "--trigger"
    ])
    
    await asyncio.sleep(2)
    
    assert len(received_events) == 2
    print(f"✅ Received {len(received_events)} events")

asyncio.run(test_subscription())
```

### Test 3: Load Testing

Generate multiple changes rapidly:

```bash
for i in {1..10}; do
  jq ".version = \"1.9.6x-test-$i\"" .github/environment.json > /tmp/env.json
  mv /tmp/env.json .github/environment.json
  sleep 1
done

# Verify all triggers logged
wc -l logs/github_envhook_triggers.log
```

---

## 🔧 Troubleshooting

### Debug Mode

Enable verbose logging:

```bash
export GENESIS_TRACE_LEVEL=3
python3 .github/scripts/github_envhook.py --watch
```

### Check Genesis Bus Status

```python
from genesis.bus import genesis_bus

print(f"Genesis enabled: {genesis_bus.is_enabled()}")
print(f"Valid topics: {len(genesis_bus._valid_topics)}")
print(f"Subscribers: {len(genesis_bus._subs)}")
```

### Verify Topic Registration

```python
from genesis.bus import genesis_bus

required_topics = [
    "envmirror.sync.start",
    "envmirror.sync.complete", 
    "envmirror.audit",
    "envduo.audit",
    "envduo.heal"
]

for topic in required_topics:
    if topic in genesis_bus._valid_topics:
        print(f"✅ {topic}")
    else:
        print(f"❌ {topic} - MISSING")
```

---

## 🎨 Example: Complete Workflow

```python
#!/usr/bin/env python3
"""
Complete example: Modify environment.json and observe sync
"""

import json
import asyncio
from pathlib import Path
from genesis.bus import genesis_bus

ENV_FILE = Path(".github/environment.json")

async def observe_sync():
    events_received = []
    
    def log_event(event):
        events_received.append(event)
        print(f"📡 Event: {event['_genesis_topic']}")
        print(f"   Type: {event['type']}")
        print(f"   Source: {event['source']}")
    
    # Subscribe to all environment events
    genesis_bus.subscribe("envmirror.sync.start", log_event)
    genesis_bus.subscribe("envmirror.sync.complete", log_event)
    genesis_bus.subscribe("envduo.audit", log_event)
    genesis_bus.subscribe("envduo.heal", log_event)
    
    print("👁️ Watching for environment changes...")
    print("   Modify .github/environment.json to trigger sync")
    
    # Wait for events
    await asyncio.sleep(30)
    
    print(f"\n📊 Summary: {len(events_received)} events received")
    for event in events_received:
        print(f"   - {event['_genesis_topic']}: {event['type']}")

if __name__ == "__main__":
    asyncio.run(observe_sync())
```

---

## 📚 Best Practices

1. **Always use manual trigger for testing** - Don't rely on file watching during development

2. **Monitor Genesis event history** - Use `/api/genesis/events` to track sync operations

3. **Review audit logs regularly** - Check `logs/github_envhook_triggers.log` for anomalies

4. **Use RBAC controls** - Restrict write access to `.github/environment.json` to Admirals only

5. **Enable Truth certification** - Ensure all events are logged to Truth Engine ledger

6. **Set up alerting** - Monitor for repeated sync failures or drift

7. **Version environment.json** - Always increment version field when making changes

---

## 🔗 Next Steps

1. Implement `EnvMirror` engine to consume `envmirror.sync.start` events
2. Implement `EnvDuo` engine to consume `envduo.audit` events
3. Add Steward visual diff layer for timeline visualization
4. Configure GitHub Actions workflow for automated triggering
5. Set up monitoring dashboards for sync health

---

**Component:** GitHub Environment Hook  
**Version:** v1.9.6x  
**Integration:** Genesis Event Bus  
**Documentation:** See `docs/GITHUB_ENVHOOK.md`
