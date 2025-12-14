# Healer-Net Diagnostic Network

Healer-Net fuses the Bridge's self-repair subsystems:
- **Firewall Harmony** (connectivity & security)
- **Parity Engine** (backend/frontend route sync)
- **Triage Suite** (API, Build, Deploy, Env)
- **Auto-Repair Mode**

All outputs are merged into `healer_net_report.json` and displayed in the UI via the BridgeHealthBadge.

## Health States

| State | Meaning |
|--------|----------|
| 🟢 Healthy | All systems online, parity aligned |
| 🟡 Issues | Minor misalignments or pending retries |
| 🔴 Offline | One or more critical systems failed |
| ⚫ Loading | Initializing or collecting telemetry |

---

## Auto-Repair Integration

If a subsystem fails, Healer-Net queues a self-repair job:
- Warm caches (Firewall)
- Retry missed hooks (Endpoint/API)
- Redeploy (Build/Deploy)
- Realign environment vars

## Artifact

Every cycle produces:

```json
healer_net_report.json
```

which aggregates all subsystem probe data.

---

## Architecture

### Components

1. **GitHub Actions Workflow** (`.github/workflows/healer_net.yml`)
   - Runs every 6 hours via cron schedule (`0 */6 * * *`)
   - Manual trigger via workflow_dispatch
   - Executes on push to main branch
   - Coordinates all triage systems:
     - Firewall Harmony check
     - Endpoint Triage
     - API Triage
   - Uploads aggregated health report as artifact

2. **Health Probe Script** (`bridge_backend/tools/health/healer_net_probe.py`)
   - Aggregates triage reports from all subsystems
   - Collects firewall probe data
   - Generates unified health status
   - Outputs `healer_net_report.json`

3. **Frontend Component** (`bridge-frontend/src/components/BridgeHealthBadge.jsx`)
   - Displays current Healer-Net status
   - Color-coded status indicators (healthy/issues/offline/loading)
   - Auto-refreshes via API polling

---

## Usage

### Automated Execution

The Healer-Net runs automatically:

1. **Every 6 Hours**: Via GitHub Actions cron schedule
2. **On Main Branch Push**: Automatically after deployment
3. **Manual Workflow Trigger**: Via GitHub Actions UI

### Frontend Integration

Add the BridgeHealthBadge component to your dashboard:

```jsx
import BridgeHealthBadge from './components/BridgeHealthBadge';

function Dashboard() {
  return (
    <div>
      <BridgeHealthBadge />
      {/* other components */}
    </div>
  );
}
```

---

## Health Report Format

The `healer_net_report.json` contains:

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "runner": "github-runner-hostname",
  "systems": {
    "chromium_probe": { ... },
    "endpoint_report": { ... },
    "api_triage_report": { ... }
  },
  "summary": {
    "healthy": true,
    "issues": 0
  }
}
```

---

## Integration with Existing Systems

Healer-Net builds upon and unifies:

- **Firewall Harmony** (v1.7.6) - Auto-recovering browser automation
- **Endpoint Triage** - Core API endpoint monitoring
- **API Triage** - Response validation and schema checking
- **Parity Engine** - Backend/frontend route synchronization
- **Auto-Repair Core** - Self-healing capabilities

All these systems continue to function independently while feeding data into Healer-Net for unified visibility.

---

## Troubleshooting

### Healer-Net Not Running

Check workflow logs in GitHub Actions for:
```
🌐 Starting unified triage and harmony sync...
```

If missing, verify:
- Workflow file exists at `.github/workflows/healer_net.yml`
- Workflow has proper permissions
- Cron schedule is configured correctly

### Health Badge Not Showing Data

1. Verify `/api/bridge/health` endpoint is working
2. Check browser console for fetch errors
3. Confirm Healer-Net has run at least once

### Report Not Generated

1. Check workflow logs for Python script execution
2. Verify probe scripts exist and are executable
3. Confirm all triage systems have run and generated reports

---

## Related Documentation

- [Firewall Harmony](FIREWALL_HARMONY.md)
- [Endpoint Triage](ENDPOINT_TRIAGE.md)
- [API Triage](API_TRIAGE.md)
- [Bridge Parity Engine](BRIDGE_PARITY_ENGINE.md)
- [Unified Health Timeline](UNIFIED_HEALTH_TIMELINE.md)

---

## Future Enhancements

- Real-time WebSocket updates for health status
- Historical health trend analysis
- Predictive failure detection
- Automated recovery workflows
- Integration with alerting systems
