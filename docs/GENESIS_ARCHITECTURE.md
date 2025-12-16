# Genesis Linkage - Unified Engine Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Blueprint Registry (Source of Truth)          │
│                          20 Engines Unified                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
    ┌───────▼──────┐  ┌────▼────┐  ┌──────▼──────┐
    │ Core Engines │  │  Super  │  │   Utility   │
    │    (6)       │  │ Engines │  │  Engines    │
    │              │  │   (6)   │  │    (7)      │
    └──────────────┘  └─────────┘  └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  Leviathan  │
                    │ Orchestrator│
                    └─────────────┘
```

## Detailed Architecture

### Core Infrastructure Layer (6 Engines)

```
Blueprint Engine (Source of Truth)
    │
    ├──► TDE-X (Tri-Domain Execution)
    │     └─ Shards: bootstrap, runtime, diagnostics
    │
    ├──► Cascade (DAG Orchestration)
    │     └─ Auto-rebuild on blueprint changes
    │
    ├──► Truth (Fact Certification)
    │     └─ Validates state against blueprint
    │
    ├──► Autonomy (Self-Healing)
    │     └─ Blueprint-defined guardrails
    │
    └──► Parser (Content Ingestion)
          └─ Lineage tracking
```

### Super Engines Layer (6 Engines)

```
Leviathan Solver (Orchestrator)
    │
    ├──► CalculusCore
    │     └─ Differentiation, Integration, Analysis
    │
    ├──► QHelmSingularity
    │     └─ Quantum Navigation, Spacetime Physics
    │
    ├──► AuroraForge
    │     └─ Visual Generation, Creative Content
    │
    ├──► ChronicleLoom
    │     └─ Temporal Narratives, Pattern Detection
    │
    ├──► ScrollTongue
    │     └─ NLP, Linguistic Analysis, Translation
    │
    └──► CommerceForge
          └─ Market Simulation, Economic Modeling
```

### Utility Engines Layer (7 Engines)

```
Utility Engines (Support Services)
    │
    ├──► Creativity Bay
    │     └─ Creative asset management
    │
    ├──► Indoctrination
    │     └─ Agent onboarding & certification
    │
    ├──► Screen Engine
    │     └─ Screen sharing, WebRTC signaling
    │
    ├──► Speech Engine
    │     └─ TTS & STT processing
    │
    ├──► Recovery Orchestrator
    │     └─ Task dispatch + content ingestion
    │
    ├──► Agents Foundry
    │     └─ Agent creation, archetypes
    │
    └──► Filing Engine
          └─ File management
```

## Event Bus Integration

### Event Flow Diagram

```
Blueprint Registry
    │
    ├─[blueprint.events]──────► Cascade, Super Engines, Utility Engines
    │
TDE-X
    │
    ├─[deploy.signals]────────► Truth, Autonomy
    │
Truth Engine
    │
    ├─[deploy.facts]──────────► Autonomy, Leviathan
    │
Cascade Engine
    │
    ├─[deploy.graph]──────────► TDE-X, Autonomy
    │
Autonomy Engine
    │
    ├─[deploy.actions]────────► Recovery, Truth
    │
Leviathan Solver
    │
    ├─[solver.tasks]──────────► Super Engines
    │
    └─[solver.results]────────► Truth, Parser
```

### Event Topics (33 Total)

**Core Topics (5)**
- blueprint.events
- deploy.signals
- deploy.facts
- deploy.graph
- deploy.actions

**Super Engine Topics (12)**
- math.calculus, math.proofs
- quantum.navigation, quantum.singularities
- creative.assets, creative.render
- chronicle.narratives, chronicle.patterns
- language.analysis, language.translation
- commerce.markets, commerce.trades

**Orchestration Topics (2)**
- solver.tasks
- solver.results

**Utility Topics (14)**
- creativity.ingest, creativity.assets
- agents.onboard, agents.certify
- screen.sessions, screen.signaling
- speech.tts, speech.stt
- recovery.tasks, recovery.linkage
- agents.create, agents.archetypes
- files.operations
- (+ 1 more)

## Dependency Graph

```
                    Blueprint (ROOT)
                         │
        ┌────────────────┼────────────────┐
        │                │                │
    TDE-X           Cascade           Parser
                       │
                  ┌────┴────┐
                  │         │
              Truth     Autonomy
                  │         │
                  └────┬────┘
                       │
                  Leviathan ──┐
                       │      │
        ┌──────────────┼──────┼──────────┐
        │              │      │          │
   CalculusCore   QHelmSing  Aurora  Chronicle
                       │      │          │
                  ScrollTongue  Commerce  ...
                       
Recovery ──► Autonomy + Parser
Indoctrination (standalone)
Creativity (standalone)
Screen (standalone)
Speech (standalone)
AgentsFoundry (standalone)
Filing (standalone)
```

## API Endpoints (8 Total)

### Status & Information
- `GET /engines/linked/status` - All engine linkages
- `GET /engines/linked/manifest` - Complete blueprint
- `GET /engines/linked/manifest/{name}` - Specific engine

### Initialization
- `POST /engines/linked/initialize` - Initialize all linkages

### Dependencies
- `GET /engines/linked/dependencies/{name}` - Engine dependencies

### Category Status
- `GET /engines/linked/super-engines/status` - Super engines (6)
- `GET /engines/linked/utility-engines/status` - Utility engines (7)
- `GET /engines/linked/leviathan/status` - Leviathan coordination

## File Structure

```
bridge_backend/bridge_core/engines/
├── blueprint/
│   ├── registry.py (20 engine manifests)
│   └── adapters/
│       ├── __init__.py
│       ├── tde_link.py
│       ├── cascade_link.py
│       ├── truth_link.py
│       ├── autonomy_link.py
│       ├── leviathan_link.py      [NEW]
│       ├── super_engines_link.py  [NEW]
│       └── utility_engines_link.py [NEW]
└── routes_linked.py (8 API endpoints)
```

## Key Metrics

- **Total Engines**: 20
- **Event Topics**: 33
- **API Endpoints**: 8
- **Adapter Modules**: 7
- **Lines of Code Added**: ~845 production + documentation
- **Dependencies Validated**: 100%
- **Test Coverage**: All validation tests passing

## Benefits

✅ Complete unification - All engines in one registry
✅ Event-driven - 33 topics for inter-engine communication
✅ Dependency aware - Full graph tracking
✅ Hierarchical - Organized by function (Core, Super, Utility)
✅ Coordinated - Leviathan orchestrates super engines
✅ Validated - All schemas and dependencies checked
✅ Documented - Comprehensive guides and references
✅ Backward compatible - No breaking changes
