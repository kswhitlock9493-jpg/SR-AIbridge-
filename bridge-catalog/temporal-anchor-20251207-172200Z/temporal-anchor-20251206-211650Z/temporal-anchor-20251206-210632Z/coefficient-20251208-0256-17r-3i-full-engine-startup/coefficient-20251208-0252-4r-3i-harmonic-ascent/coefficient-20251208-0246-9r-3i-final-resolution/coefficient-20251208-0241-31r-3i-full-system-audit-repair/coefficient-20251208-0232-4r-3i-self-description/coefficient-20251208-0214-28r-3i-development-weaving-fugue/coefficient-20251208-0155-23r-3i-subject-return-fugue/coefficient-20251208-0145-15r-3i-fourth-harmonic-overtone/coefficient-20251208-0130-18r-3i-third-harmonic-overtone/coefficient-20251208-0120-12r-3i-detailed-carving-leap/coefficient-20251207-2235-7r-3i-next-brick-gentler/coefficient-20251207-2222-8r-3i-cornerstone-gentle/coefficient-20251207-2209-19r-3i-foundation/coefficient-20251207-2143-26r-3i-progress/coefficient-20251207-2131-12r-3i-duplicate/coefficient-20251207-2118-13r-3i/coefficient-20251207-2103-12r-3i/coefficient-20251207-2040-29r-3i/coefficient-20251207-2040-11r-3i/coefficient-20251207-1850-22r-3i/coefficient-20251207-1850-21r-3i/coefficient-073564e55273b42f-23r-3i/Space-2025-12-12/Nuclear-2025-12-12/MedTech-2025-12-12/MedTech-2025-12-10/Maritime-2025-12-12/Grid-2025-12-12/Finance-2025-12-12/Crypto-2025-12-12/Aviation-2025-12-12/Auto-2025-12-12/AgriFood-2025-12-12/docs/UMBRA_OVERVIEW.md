# Umbra Unified Triage Mesh - Overview

## What is Umbra Triage Mesh?

Umbra Triage Mesh (v1.9.7k) is a unified, real-time triage system that consolidates all error surfaces—build, deploy, runtime, API, endpoints, and webhooks—into a single intelligent brain with automated healing capabilities.

## Why Umbra Triage Mesh?

Previously, triage was fragmented across:
- **Build triage**: GitHub Actions failures
- **Deploy triage**: Netlify/Render deployment issues  
- **Runtime triage**: Health endpoint failures
- **API triage**: Endpoint errors
- **Webhook triage**: Webhook processing failures

Each had its own detection, alerting, and healing logic. Umbra unifies these into one cohesive system.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Signal Sources                            │
├─────────────┬──────────────┬───────────────┬────────────────┤
│ GitHub      │ Netlify      │ Render        │ HealthNet      │
│ Webhooks    │ Webhooks     │ Webhooks      │ Probes         │
└──────┬──────┴──────┬───────┴───────┬───────┴────────┬───────┘
       │             │               │                │
       ▼             ▼               ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                    Umbra Triage Core                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Collect  │→ │Correlate │→ │ Classify │→ │  Decide  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│         ↓                                         ↓          │
│  ┌──────────────────────────────────────────────────┐       │
│  │        Correlation Graph & Decision Engine       │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────┬───────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Umbra Healers                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Parity  │→ │  Truth   │→ │  Heal    │→ │  Report  │    │
│  │  Check   │  │  Certify │  │  Execute │  │          │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│         ↓                          ↓              ↓          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Autonomy │  │ Cascade  │  │ Chimera  │  │  Parity  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Core Concepts

### Signals
External events from various sources (webhooks, probes, APIs). Each signal has:
- **Kind**: build, deploy, runtime, api, endpoint, webhook
- **Source**: netlify, render, github, healthnet, etc.
- **Severity**: critical, high, warning, info
- **Metadata**: Additional context

### Incidents
Normalized internal representation of signals. Created when a signal is ingested.

### Tickets
Correlated collection of related incidents. Umbra automatically groups incidents that are:
- Same kind and source
- Within time window (5 minutes)
- Logically related

### Heal Plans
Automated remediation strategies generated for tickets. Each plan includes:
- **Actions**: Specific healing steps
- **Parity Prechecks**: Environment convergence checks
- **Truth Policy**: Certification requirements
- **Rollback Plan**: Safe fallback if healing fails

### Reports
Summary of each triage sweep with metrics:
- Tickets opened/healed/failed
- Critical/warning counts
- Heal plans generated/applied
- Duration and summary

## Pipeline Flow

### 1. Collect
Signals arrive from:
- **Webhooks**: `/webhooks/render`, `/webhooks/netlify`, `/webhooks/github`
- **Genesis Bus**: `triage.signal.*` topics
- **Direct API**: `/api/umbra/signal`

### 2. Correlate
Similar incidents are grouped into tickets based on:
- Matching kind and source
- Time proximity
- Signal patterns

### 3. Classify
Tickets are analyzed to determine:
- Root cause
- Severity level
- Required heal actions

### 4. Decide
Generate heal plan with:
- Appropriate actions for the issue type
- Parity checks to ensure environment consistency
- Truth certification requirements

### 5. Heal
Execute heal plan through:
- **Parity prechecks**: Verify environment state
- **Truth certification**: Get approval from Truth Engine
- **Action execution**: Delegate to Autonomy, Cascade, Chimera
- **Parity postchecks**: Verify successful convergence

### 6. Certify
Truth Engine validates:
- Heal plan before execution
- Results after execution
- Generates cryptographic signature

### 7. Report
Generate comprehensive report with:
- All tickets and their status
- Heal actions taken
- Success/failure metrics
- Stored as JSON for PR annotations

## Genesis Integration

Umbra integrates with Genesis event bus for:

**Subscribe Topics**:
- `triage.signal.build`
- `triage.signal.deploy`
- `triage.signal.runtime`
- `triage.signal.api`
- `triage.signal.webhook`
- `genesis.heal`

**Publish Topics**:
- `triage.ticket.open`
- `triage.ticket.update`
- `triage.ticket.closed`
- `triage.heal.intent`
- `triage.heal.applied`
- `triage.heal.rollback`
- `triage.alert`
- `triage.report`

## Engine Integrations

### Autonomy Engine
- Executes service restart and recovery actions
- Provides autonomous decision-making

### Cascade Engine
- Applies configuration patches
- Manages tier-based permissions

### Chimera Engine
- Handles deploy preflight checks
- Regenerates deploy configuration

### Parity Engine
- Verifies environment convergence
- Ensures consistency across platforms

### Truth Engine
- Certifies heal plans before execution
- Validates results after execution
- Provides audit trail

## Key Features

### 1. Unified Triage
All error surfaces in one place - no more hunting across systems.

### 2. Automatic Correlation
Related incidents automatically grouped into coherent tickets.

### 3. Intelligent Healing
Context-aware heal plans based on issue type and severity.

### 4. Safety Gates
- RBAC enforcement (Admiral-only by default)
- Truth certification required
- Parity checks before/after healing
- Automatic rollback on failure

### 5. PR Health Annotations
Every PR gets a health score and summary comment showing:
- Overall health percentage
- Critical/warning counts
- Heal actions taken
- Truth certification status

### 6. Observable & Auditable
- All actions logged to Genesis
- JSON reports for every run
- Artifacts uploaded to GitHub Actions

## Configuration

See `.env.example` for all configuration options:

```bash
# Enable Umbra
UMBRA_ENABLED=true

# Allow autonomous healing (intent-only by default)
UMBRA_ALLOW_HEAL=false

# Webhook security
UMBRA_ALLOW_UNVERIFIED_WEBHOOKS=false

# Health thresholds
UMBRA_HEALTH_ERROR_THRESHOLD=5
UMBRA_HEALTH_WARN_THRESHOLD=2

# Parity enforcement
UMBRA_PARITY_STRICT=true

# RBAC minimum role
UMBRA_RBAC_MIN_ROLE=captain

# Webhook secrets (optional)
RENDER_WEBHOOK_SECRET=
NETLIFY_DEPLOY_WEBHOOK_SECRET=
GITHUB_WEBHOOK_SECRET=
```

## Next Steps

- See [UMBRA_OPERATIONS.md](./UMBRA_OPERATIONS.md) for operational guide
- See [TRIAGE_MESH_MIGRATION.md](./TRIAGE_MESH_MIGRATION.md) for migration details
- See [PR_HEALTH_SUMMARY.md](./PR_HEALTH_SUMMARY.md) for PR annotation format
