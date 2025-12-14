# Leviathan Solver - Meta-Engine Orchestrator

## Overview

The Leviathan Solver is a meta-engine that orchestrates the Six Super Engines to provide comprehensive, cited, and actionable solutions to complex queries. It classifies intents, routes work to specialized engines, grounds answers in existing knowledge, and optionally dispatches autonomous tasks.

## Features

### 🎯 Intent Classification
Automatically classifies queries into:
- **Research**: Literature surveys, comparisons, state-of-the-art analysis
- **Design**: Architecture sketches, specifications, prototypes
- **Plan**: Roadmaps, phases, milestones

### 🔌 Six Super Engines Integration
The solver includes adapters for all Six Super Engines:

1. **CalculusCore** (Math Engine)
   - Advanced mathematical computations
   - Symbolic operations and theorem proving
   - Keywords: projection, rotation, transform, 4D, R4

2. **QHelmSingularity** (Quantum/Science Engine)
   - Quantum state modeling
   - Spacetime navigation
   - Keywords: quantum, singularity, physics

3. **AuroraForge** (Creativity/Visual Engine)
   - Visual content generation
   - UX/UI design
   - Keywords: demo, UX, interface, visualization, graphics

4. **ChronicleLoom** (History Engine)
   - Temporal narrative weaving
   - Chronicle analysis
   - Keywords: history, previous, prior, evolution

5. **ScrollTongue** (Language Engine)
   - Natural language synthesis
   - Linguistic analysis
   - Used for: Summary generation, text synthesis

6. **CommerceForge** (Business Engine)
   - Market analysis
   - Resource planning
   - Keywords: cost, budget, vendor, team, BOM

### 📚 Knowledge Grounding
- Scans Parser ledger for relevant chunks
- Retrieves bound truths from Truth Engine
- Provides citations for all claims

### 🤖 Optional Autonomy
When `dispatch=true`:
- Spawns paper roundup tasks
- Creates prototype scaffold tasks
- All tasks are permission-bound and contract-sealed

### 🔒 Proof Artifacts
Every solve operation generates a proof artifact at `vault/leviathan/solver/proof_*.json` with:
- Timestamp
- Query and intents
- Sub-tasks decomposition
- Engines used
- Citation counts
- SHA256 seal for verification

## API Endpoint

### POST `/engines/leviathan/solve`

**Request Body:**
```json
{
  "q": "What would it take to build a 4D projection demo?",
  "captain": "Kyle",
  "project": "nova",
  "modes": ["research", "plan", "design"],  // optional
  "dispatch": false,  // optional, spawn autonomy tasks
  "allow_web": false  // optional, reserved for future
}
```

**Response:**
```json
{
  "summary": "We can approximate 4D→3D→2D via projection + hyperslicing...",
  "plan": [
    {
      "phase": 1,
      "name": "Modeling & Math",
      "deliverables": ["ℝ⁴ rotations", "projection operators"],
      "estimate_weeks": "2-3"
    },
    // ... more phases
  ],
  "requirements": {
    "math": ["ℝ⁴ rotations", "projection operators"],
    "science": ["optics/display tradeoffs"],
    "quantum": [],
    "software": ["WebGPU/Vulkan/OpenGL renderer", "shader stack"],
    "hardware_optional": ["light-field dev kit", "VR HMD"],
    "team": ["graphics eng", "applied math", "UX"],
    "risks": ["display brightness/resolution", "user comprehension"]
  },
  "citations": {
    "truths": [...],
    "parser_hits": [...]
  },
  "tasks": [],  // autonomy tasks if dispatch=true
  "proof": {
    "ts": "2025-10-01T02:44:49Z",
    "q": "...",
    "intents": ["research"],
    "subs": [...],
    "engines_used": {
      "math_science": true,
      "creativity": true,
      "business": true,
      "history": false,
      "engines_available": true
    },
    "citations_counts": {
      "truths": 1,
      "parser_hits": 2
    },
    "tasks_spawned": 0,
    "seal": "ab5e8c0e85edcfa47b91b379bec41df2..."
  }
}
```

## Usage Examples

### Basic Query
```bash
curl -X POST http://localhost:8000/engines/leviathan/solve \
  -H 'Content-Type: application/json' \
  -d '{
    "q": "Build a quantum navigation system"
  }'
```

### With Project Context
```bash
curl -X POST http://localhost:8000/engines/leviathan/solve \
  -H 'Content-Type: application/json' \
  -d '{
    "q": "What would it take to build a 4D projection demo for Nova?",
    "captain": "Kyle",
    "project": "nova"
  }'
```

### With Specific Modes
```bash
curl -X POST http://localhost:8000/engines/leviathan/solve \
  -H 'Content-Type: application/json' \
  -d '{
    "q": "Design a visualization system",
    "modes": ["design", "research"]
  }'
```

### With Autonomy Dispatch
```bash
curl -X POST http://localhost:8000/engines/leviathan/solve \
  -H 'Content-Type: application/json' \
  -d '{
    "q": "Survey 4D rendering literature",
    "captain": "Kyle",
    "project": "nova",
    "dispatch": true
  }'
```

## Testing

### Run Minimal Tests
```bash
cd bridge_backend
python tests/test_solver_minimal.py
```

### Run Smoke Tests
```bash
cd bridge_backend
python tests/smoke_test_solver.py
```

### Run Full Test Suite (requires dependencies)
```bash
cd bridge_backend
pytest tests/test_leviathan_solver.py -v
```

## Architecture

### Flow Diagram
```
Query → Intent Classifier → Decomposer
                                ↓
        ┌───────────────────────┴────────────────────────┐
        ↓                       ↓                        ↓
   Math/Science         Creativity/Visual        Business/Economic
   (CalculusCore)        (AuroraForge)          (CommerceForge)
   (QHelmSingularity)                                    
        ↓                       ↓                        ↓
        └───────────────────────┬────────────────────────┘
                                ↓
                          Language Synthesis
                          (ScrollTongue)
                                ↓
                          Truth Grounding
                          (Parser + Truth)
                                ↓
                          Optional Autonomy
                          (Task Dispatch)
                                ↓
                          Proof Generation
                          (SHA256 Seal)
```

### Adapter Pattern
Each Super Engine has a thin adapter that:
1. Extracts relevant keywords from the query
2. Calls the engine's methods (or uses deterministic logic)
3. Formats the output for the solver
4. Falls back to safe defaults if engine unavailable

## Files

- `bridge_core/engines/leviathan/solver.py` - Core solver logic and adapters
- `bridge_core/engines/leviathan/routes_solver.py` - FastAPI endpoint
- `tests/test_leviathan_solver.py` - Comprehensive tests
- `tests/test_solver_minimal.py` - Minimal dependency tests
- `tests/smoke_test_solver.py` - Manual verification tests
- `vault/leviathan/solver/` - Proof artifacts directory

## Future Enhancements

- [ ] Web plane integration (`allow_web=true`)
- [ ] Real-time engine hooks (replace stubs with live calls)
- [ ] Multi-language support via ScrollTongue
- [ ] Visual artifact generation via AuroraForge
- [ ] Market analysis via CommerceForge
- [ ] Quantum simulation via QHelmSingularity
- [ ] Historical pattern detection via ChronicleLoom

## License

Part of the SR-AIbridge Sovereign Bridge Architecture.
