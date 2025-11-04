# Engine Catalog
## Complete Documentation of All 20 SR-AIbridge Engines

> **Purpose**: Comprehensive reference for all 20 specialized engines in the SR-AIbridge system, organized by category.

---

## 📊 Engine Overview

SR-AIbridge features **20 specialized engines** organized into 4 categories:

```
Total Engines: 20
├── Core Engines: 6 (Infrastructure)
├── Super Engines: 6 (Specialized AI)
├── Utility Engines: 7 (Support Services)
└── Orchestrator: 1 (Coordination)
```

**Communication**: 33 event topics via Genesis Linkage event bus

---

## 🏗️ Category 1: Core Engines (6)

These provide the foundational infrastructure for the system.

### 1. Blueprint Engine

**Purpose**: Transform free-form mission briefs into structured, executable plans

**Location**: `bridge_backend/bridge_core/engines/blueprint/`

**Key Files**:
- `blueprint_engine.py` - Core planning engine
- `planner_rules.py` - Deterministic planning logic
- `routes.py` - API endpoints
- `registry.py` - Engine registry (source of truth)

**API Endpoint**: `POST /blueprint/draft`

**Input**:
```json
{
  "mission_brief": "Analyze Q4 sales data and identify top-performing products"
}
```

**Output**:
```json
{
  "objectives": [
    "Collect Q4 sales data",
    "Perform analysis",
    "Identify patterns"
  ],
  "tasks": [
    {
      "id": "task-1",
      "title": "Data Collection",
      "dependencies": [],
      "success_criteria": "All Q4 sales records retrieved",
      "agent_requirements": ["data_access"]
    },
    {
      "id": "task-2", 
      "title": "Sales Analysis",
      "dependencies": ["task-1"],
      "success_criteria": "Statistical analysis complete",
      "agent_requirements": ["analysis", "python"]
    }
  ],
  "artifacts": [
    "sales_report.pdf",
    "analysis_summary.md"
  ]
}
```

**Features**:
- Derives objectives from natural language
- Explodes objectives into granular tasks
- Identifies task dependencies
- Generates success criteria
- Specifies agent requirements

**Event Topics**:
- Publishes: `blueprint.events`
- Subscribes: -

---

### 2. TDE-X (Tri-Domain Execution)

**Purpose**: Three-shard execution engine for bootstrap, runtime, and diagnostics

**Location**: `bridge_backend/bridge_core/engines/tde_x/`

**Key Files**:
- `tri_domain.py` - Core execution
- `bootstrap.py` - Initialization phase
- `runtime.py` - Active execution phase
- `diagnostics.py` - Health monitoring phase

**Shards**:
1. **Bootstrap Shard**: System initialization and setup
2. **Runtime Shard**: Active task execution
3. **Diagnostics Shard**: Continuous health monitoring

**Workflow**:
```
Bootstrap (Init) → Runtime (Execute) → Diagnostics (Monitor)
     ↓                  ↓                    ↓
  Setup tables      Run tasks          Check health
  Load config       Process jobs        Report metrics
  Verify deps       Execute code        Detect issues
```

**Event Topics**:
- Publishes: `deploy.signals`
- Subscribes: `blueprint.events`

---

### 3. Cascade Engine

**Purpose**: DAG (Directed Acyclic Graph) orchestration with auto-rebuild

**Location**: `bridge_backend/bridge_core/engines/cascade/`

**Key Files**:
- `dag.py` - Graph construction and validation
- `executor.py` - Task execution with dependency resolution

**Features**:
- Builds dependency graph from tasks
- Validates no circular dependencies
- Determines execution order
- Parallel execution where possible
- Auto-rebuilds when blueprint changes

**Example DAG**:
```
task-1 (no deps) ────┐
                     ├──→ task-3 (depends on 1,2) ──→ task-5
task-2 (no deps) ────┘                               ↑
                                                      │
task-4 (no deps) ─────────────────────────────────────┘
```

**Execution Order**: [task-1, task-2, task-4] → [task-3] → [task-5]

**Event Topics**:
- Publishes: `deploy.graph`
- Subscribes: `blueprint.events`

---

### 4. Truth Engine

**Purpose**: Fact certification and state validation with rollback protection

**Location**: `bridge_backend/bridge_core/engines/truth/`

**Key Files**:
- `validator.py` - State validation logic
- `rollback.py` - Rollback protection
- `certification.py` - Fact certification

**Features**:
- Validates system state against blueprint
- Certifies deployment facts
- Provides rollback protection
- Maintains fact history
- QEH-v3 entropy hashing for verification

**Validation Process**:
```
Current State
    ↓
Compare to Blueprint (Expected State)
    ↓
Identify Discrepancies
    ↓
Generate Correction Facts
    ↓
Certify with QEH-v3 Signature
```

**Event Topics**:
- Publishes: `deploy.facts`
- Subscribes: `deploy.signals`, `deploy.graph`

---

### 5. Autonomy Engine

**Purpose**: Self-healing and autonomous recovery with integrated triage

**Location**: `bridge_backend/bridge_core/engines/autonomy/`

**Key Files**:
- `engine.py` - Core autonomy logic
- `rules.py` - Blueprint-defined guardrails
- `integrations.py` - Triage/federation/parity integration
- `recovery.py` - Recovery action execution

**Features**:
- Automatic issue detection
- Blueprint-defined guardrails
- Integrated with Triage (API/endpoint/diagnostics)
- Integrated with Federation (heartbeats/distributed events)
- Integrated with Parity (engine/autofix/deploy checks)
- Event-driven auto-healing
- Self-repair for endpoint mismatches

**Integration Points**:
```
Triage Events ──┐
                ├──→ Autonomy Engine ──→ Recovery Actions
Federation ─────┤         ↓
                └──→ genesis.heal
Parity ─────────────→ genesis.intent
```

**Event Topics**:
- Publishes: `deploy.actions`, `autonomy.heal`, `autonomy.intent`
- Subscribes: `deploy.facts`, `triage.events`, `federation.events`, `parity.events`

---

### 6. Parser Engine

**Purpose**: Content ingestion with lineage tracking and provenance

**Location**: `bridge_backend/bridge_core/engines/parser/`

**Key Files**:
- `parser.py` - Document parsing
- `lineage.py` - Provenance tracking
- `extractors.py` - Metadata extraction

**Features**:
- Multi-format document parsing
- Metadata extraction
- Lineage tracking (who/what/when/where)
- Provenance certification
- Content indexing

**Supported Formats**:
- Markdown (.md)
- JSON (.json)
- YAML (.yaml)
- Plain text (.txt)
- Python (.py)
- JavaScript (.js)

**Event Topics**:
- Publishes: `parser.content`, `parser.lineage`
- Subscribes: `solver.results`, `recovery.tasks`

---

## 🚀 Category 2: Super Engines (6)

Specialized AI capabilities for advanced operations.

### 1. CalculusCore (Math Engine)

**Purpose**: Symbolic mathematics, calculus, and theorem proving

**Location**: `bridge_backend/bridge_core/engines/calculus_core/`

**API Endpoint**: `POST /engines/math/prove`

**Library**: SymPy 1.13.1 (symbolic mathematics)

**Capabilities**:
- **Differentiation**: Compute derivatives of functions
- **Integration**: Solve definite and indefinite integrals
- **Equation Solving**: Solve algebraic and differential equations
- **Expression Simplification**: Simplify mathematical expressions
- **Theorem Proving**: Validate mathematical theorems
- **Matrix Operations**: Linear algebra computations

**Example Request**:
```json
{
  "expression": "diff(sin(x^2), x)",
  "operation": "differentiate"
}
```

**Example Response**:
```json
{
  "result": "2*x*cos(x^2)",
  "steps": [
    "Applied chain rule: d/dx[sin(u)] = cos(u) * du/dx",
    "Where u = x^2, du/dx = 2x",
    "Result: 2*x*cos(x^2)"
  ],
  "confidence": 1.0,
  "metadata": {
    "engine": "CalculusCore",
    "library": "SymPy",
    "complexity": "medium"
  }
}
```

**Advanced Operations**:
```python
# Integration
integrate(x**2, (x, 0, 1))  # Definite integral
# Result: 1/3

# Equation solving
solve(x**2 - 4, x)  # Solve x^2 - 4 = 0
# Result: [-2, 2]

# Limits
limit(sin(x)/x, x, 0)  # Limit as x approaches 0
# Result: 1

# Series expansion
series(exp(x), x, 0, 10)  # Taylor series
# Result: 1 + x + x^2/2 + x^3/6 + ...
```

**Event Topics**:
- Publishes: `math.proofs`, `math.solutions`
- Subscribes: `solver.tasks`

---

### 2. QHelmSingularity (Quantum Engine)

**Purpose**: Quantum state manipulation and spacetime navigation

**Location**: `bridge_backend/bridge_core/engines/qhelm/`

**API Endpoint**: `POST /engines/quantum/collapse`

**Capabilities**:
- Quantum state superposition
- Wave function collapse simulation
- Spacetime navigation algorithms
- Singularity physics modeling
- Quantum entanglement simulation
- Multi-particle quantum systems

**Example Request**:
```json
{
  "state": "superposition",
  "particles": 5,
  "waypoints": 10,
  "operation": "navigate"
}
```

**Example Response**:
```json
{
  "result": {
    "collapsed_states": ["|0⟩", "|1⟩", "|0⟩", "|1⟩", "|1⟩"],
    "navigation_path": [
      {"t": 0, "coords": [0, 0, 0]},
      {"t": 1, "coords": [1.5, 2.3, 0.8]},
      {"t": 2, "coords": [3.2, 4.1, 1.6]}
    ],
    "entanglement_coefficient": 0.87
  },
  "metadata": {
    "engine": "QHelmSingularity",
    "particles_simulated": 5,
    "waypoints_calculated": 10
  }
}
```

**Quantum Operations**:
- Hadamard gates
- CNOT gates
- Measurement operations
- State tomography
- Quantum teleportation

**Event Topics**:
- Publishes: `quantum.states`, `quantum.navigation`
- Subscribes: `solver.tasks`

---

### 3. AuroraForge (Science/Creative Engine)

**Purpose**: Visual content generation and scientific simulation

**Location**: `bridge_backend/bridge_core/engines/aurora/`

**API Endpoint**: `POST /engines/science/experiment`

**Capabilities**:
- Visual content generation
- Creative pattern synthesis
- Scientific simulation
- Experimental design
- Data visualization
- Hypothesis testing

**Example Request**:
```json
{
  "experiment_type": "pattern_synthesis",
  "parameters": {
    "base_pattern": "fractal",
    "iterations": 5,
    "color_scheme": "aurora"
  }
}
```

**Example Response**:
```json
{
  "result": {
    "patterns_generated": 5,
    "visual_data": "base64_encoded_image_data",
    "properties": {
      "fractal_dimension": 1.58,
      "color_palette": ["#5E4FA2", "#3288BD", "#66C2A5"],
      "symmetry": "rotational"
    }
  }
}
```

**Event Topics**:
- Publishes: `creative.assets`, `science.experiments`
- Subscribes: `solver.tasks`

---

### 4. ChronicleLoom (History Engine)

**Purpose**: Temporal narrative weaving and pattern detection

**Location**: `bridge_backend/bridge_core/engines/chronicle/`

**API Endpoint**: `POST /engines/history/weave`

**Capabilities**:
- Temporal narrative construction
- Historical pattern detection
- Event correlation across time
- Timeline generation
- Historical context synthesis
- Trend analysis

**Example Request**:
```json
{
  "events": [
    {"timestamp": "2024-01-01", "type": "deployment", "details": "v1.0 released"},
    {"timestamp": "2024-02-15", "type": "incident", "details": "Database crash"},
    {"timestamp": "2024-03-01", "type": "fix", "details": "Added monitoring"}
  ],
  "operation": "weave_narrative"
}
```

**Example Response**:
```json
{
  "narrative": "The system evolved through three key phases...",
  "patterns": [
    {
      "pattern": "incident_followed_by_fix",
      "occurrences": 1,
      "timespan": "15 days"
    }
  ],
  "timeline": {
    "start": "2024-01-01",
    "end": "2024-03-01",
    "events": 3,
    "critical_moments": [
      {"date": "2024-02-15", "reason": "major_incident"}
    ]
  }
}
```

**Event Topics**:
- Publishes: `chronicle.narratives`, `chronicle.patterns`
- Subscribes: `solver.tasks`

---

### 5. ScrollTongue (Language Engine)

**Purpose**: Advanced linguistic analysis and natural language processing

**Location**: `bridge_backend/bridge_core/engines/scroll/`

**API Endpoint**: `POST /engines/language/interpret`

**Capabilities**:
- Semantic interpretation
- Multi-language processing
- Sentiment analysis
- Entity extraction
- Intent classification
- Language translation

**Example Request**:
```json
{
  "text": "The system deployed successfully at 3pm EST with zero downtime.",
  "operations": ["sentiment", "entities", "intent"]
}
```

**Example Response**:
```json
{
  "sentiment": {
    "polarity": 0.8,
    "classification": "positive"
  },
  "entities": [
    {"text": "3pm EST", "type": "TIME"},
    {"text": "zero downtime", "type": "METRIC"}
  ],
  "intent": "status_report",
  "confidence": 0.92,
  "language": "en"
}
```

**Supported Languages**:
- English, Spanish, French, German, Chinese, Japanese, and 40+ more

**Event Topics**:
- Publishes: `language.analysis`, `language.translation`
- Subscribes: `solver.tasks`

---

### 6. CommerceForge (Business Engine)

**Purpose**: Market simulation, economic modeling, and business intelligence

**Location**: `bridge_backend/bridge_core/engines/commerce/`

**API Endpoint**: `POST /engines/business/forge`

**Capabilities**:
- Market simulation
- Portfolio optimization
- Economic modeling
- Financial forecasting
- Risk analysis
- Business metrics calculation

**Example Request**:
```json
{
  "operation": "portfolio_optimization",
  "portfolio": {
    "assets": ["AAPL", "GOOGL", "MSFT"],
    "weights": [0.33, 0.33, 0.34],
    "capital": 100000
  },
  "constraints": {
    "max_risk": 0.15,
    "target_return": 0.12
  }
}
```

**Example Response**:
```json
{
  "optimized_weights": {
    "AAPL": 0.30,
    "GOOGL": 0.40,
    "MSFT": 0.30
  },
  "expected_return": 0.13,
  "risk_level": 0.14,
  "sharpe_ratio": 0.89,
  "recommendations": [
    "Increase GOOGL allocation",
    "Reduce MSFT allocation slightly"
  ]
}
```

**Event Topics**:
- Publishes: `commerce.markets`, `commerce.analysis`
- Subscribes: `solver.tasks`

---

## 🎯 Category 3: Orchestrator (1)

### Leviathan Solver

**Purpose**: Orchestrate all super engines and solve complex multi-engine tasks

**Location**: `bridge_backend/bridge_core/engines/leviathan/`

**Key Files**:
- `solver.py` - Task orchestration
- `coordinator.py` - Engine coordination
- `decomposer.py` - Problem decomposition

**Workflow**:
```
Complex Task Input
    ↓
Problem Decomposition
    ↓
Route to Appropriate Super Engines
    ├─→ CalculusCore (for math)
    ├─→ ScrollTongue (for language)
    └─→ CommerceForge (for business)
    ↓
Aggregate Results
    ↓
Synthesize Final Solution
```

**Example Multi-Engine Task**:
```
Task: "Analyze sales trends and predict Q1 revenue with 95% confidence"

Leviathan Routing:
1. ScrollTongue → Parse natural language request
2. CommerceForge → Analyze historical sales data
3. CalculusCore → Calculate statistical confidence intervals
4. ChronicleLoom → Identify temporal patterns
5. Leviathan → Synthesize comprehensive prediction
```

**Event Topics**:
- Publishes: `solver.results`, `solver.status`
- Subscribes: `solver.tasks`

---

## 🛠️ Category 4: Utility Engines (7)

Support services for various system functions.

### 1. Creativity Bay

**Purpose**: Creative asset management and storage

**Location**: `bridge_backend/bridge_core/engines/creativity/`

**Capabilities**:
- Asset cataloging
- Creative content storage
- Asset versioning
- Metadata tagging

**Event Topics**:
- Publishes: `creativity.assets`

---

### 2. Indoctrination Engine

**Purpose**: Agent onboarding and certification

**Location**: `bridge_backend/bridge_core/engines/indoctrination/`

**Capabilities**:
- Agent training
- Certification workflows
- Policy enforcement
- Competency validation

**Event Topics**:
- Publishes: `agents.certified`

---

### 3. Screen Engine

**Purpose**: Screen sharing and WebRTC signaling

**Location**: `bridge_backend/bridge_core/engines/screen/`

**Capabilities**:
- WebRTC signaling
- Screen share sessions
- Real-time collaboration

**Event Topics**:
- Publishes: `screen.sessions`, `screen.signals`

---

### 4. Speech Engine

**Purpose**: Text-to-speech and speech-to-text processing

**Location**: `bridge_backend/bridge_core/engines/speech/`

**Capabilities**:
- TTS (Text-to-Speech)
- STT (Speech-to-Text)
- Voice synthesis
- Audio transcription

**Event Topics**:
- Publishes: `speech.tts`, `speech.stt`

---

### 5. Recovery Orchestrator

**Purpose**: Task dispatch and content ingestion for recovery

**Location**: `bridge_backend/bridge_core/engines/recovery/`

**Capabilities**:
- Recovery task dispatch
- Content ingestion
- System restoration
- Backup coordination

**Event Topics**:
- Publishes: `recovery.tasks`, `recovery.status`
- Subscribes: `autonomy.heal`

---

### 6. Agents Foundry

**Purpose**: Agent creation with archetypes

**Location**: `bridge_backend/bridge_core/engines/agents_foundry/`

**Archetypes**:
- Poe (creative/analytical)
- Aeon (temporal/historical)
- Jarvis (assistant/coordinator)

**Capabilities**:
- Agent template creation
- Archetype instantiation
- Capability assignment
- Agent customization

**Event Topics**:
- Publishes: `agents.created`

---

### 7. Filing Engine

**Purpose**: File management and organization

**Location**: `bridge_backend/bridge_core/engines/filing/`

**Capabilities**:
- File storage
- Directory management
- File operations
- Access control

**Event Topics**:
- Publishes: `files.operations`

---

## 🔗 Genesis Linkage

**Event Bus Architecture**:
```
33 Event Topics organized by domain:

Core (5):
- blueprint.events
- deploy.signals
- deploy.facts
- deploy.graph
- deploy.actions

Super Engines (12):
- math.calculus, math.proofs
- quantum.navigation, quantum.singularities
- creative.assets, creative.render
- chronicle.narratives, chronicle.patterns
- language.analysis, language.translation
- commerce.markets, commerce.trades

Orchestration (2):
- solver.tasks
- solver.results

Utility (14):
- creativity.ingest, creativity.assets
- agents.onboard, agents.certify
- screen.sessions, screen.signaling
- speech.tts, speech.stt
- recovery.tasks, recovery.linkage
- agents.create, agents.archetypes
- files.operations
- (+ 1 more)
```

**Dependency Graph**:
```
Blueprint (ROOT)
    ↓
├─→ TDE-X
├─→ Cascade → Truth → Autonomy → Leviathan
└─→ Parser                           ↓
                            6 Super Engines
                                     ↓
                            7 Utility Engines
```

---

## 📊 Engine Summary Statistics

**Total Engines**: 20
- **Core**: 6 (30%)
- **Super**: 6 (30%)
- **Utility**: 7 (35%)
- **Orchestrator**: 1 (5%)

**Event Topics**: 33
**API Endpoints**: 8 (Genesis Linkage) + 6 (Super Engines) = 14
**Code Volume**: ~845 lines (adapters + routes)
**Test Coverage**: 100% validation tests passing

---

## 🎯 Quick Reference

**Find Engine by Purpose**:
- **Planning**: Blueprint Engine
- **Math**: CalculusCore
- **Language**: ScrollTongue
- **Business**: CommerceForge
- **Science**: AuroraForge
- **History**: ChronicleLoom
- **Quantum**: QHelmSingularity
- **Coordination**: Leviathan Solver
- **Self-Healing**: Autonomy Engine
- **Execution**: TDE-X, Cascade
- **Validation**: Truth Engine

**API Endpoints**:
```
GET  /engines/linked/status           # All engine status
GET  /engines/linked/manifest         # Complete registry
POST /engines/math/prove              # CalculusCore
POST /engines/quantum/collapse        # QHelmSingularity
POST /engines/science/experiment      # AuroraForge
POST /engines/history/weave           # ChronicleLoom
POST /engines/language/interpret      # ScrollTongue
POST /engines/business/forge          # CommerceForge
```

---

**Complete catalog of all 20 engines. Every capability documented, every interface specified.**

*20 engines, infinite possibilities.*
