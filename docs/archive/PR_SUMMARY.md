# PR: Mission Blueprint Engine + Mission Log v2

## Why

Turn free-form mission requests into operational, auditable plans your agents can execute with minimal captain input.

---

## What's in this PR

### Backend ✅

**New BlueprintEngine** that breaks mission briefs into:
- Objectives (high-level goals)
- Tasks (executable steps with dependencies)
- Artifacts (deliverables)
- Success criteria (acceptance tests)
- Agent job plans (task assignments)

**New Database Tables:**
- `blueprints` - Stores mission plans with JSON structure
- `agent_jobs` - Tracks individual agent tasks with FK to missions/blueprints

**API Endpoints:**
- `POST /blueprint/draft` - Generate plan from brief
- `POST /blueprint/{id}/commit?mission_id={id}` - Lock plan and create jobs
- `DELETE /blueprint/{id}` - Archive and delete (Admiral only)
- `GET /blueprint` - List all blueprints
- `GET /missions/{id}/jobs` - Get agent jobs for mission

**Features:**
- Autonomy engine integration for job dispatching
- Relay-Mailer guard on deletions (archives to email before delete)
- RBAC: Captains manage own blueprints, Admiral can delete
- PostgreSQL monthly partitioning for agent_jobs (optional)

### Frontend ✅

**BlueprintWizard** (`BlueprintWizard.jsx`)
- Draft → Preview → Refine → Commit workflow
- JSON plan visualization
- Mission selection for commit

**Mission Log v2** (`MissionLogV2.jsx`)
- Hierarchical task tree with status colors
- Task dependency visualization
- Status summary dashboard
- Detailed task cards with acceptance criteria

**AgentDeliberationPanel** (`AgentDeliberationPanel.jsx`)
- WebSocket streaming of agent decisions
- Real-time job status updates
- Connection status indicator

**Tree Component** (`ui/Tree.tsx`)
- Reusable hierarchical visualization
- Expandable/collapsible nodes
- Color-coded status (queued/running/done/failed/skipped)

**Armada Unchanged:**
- Toggle Captains/Agents still works as before
- No breaking changes to existing functionality

### Tests ✅

**Backend (14 tests passing):**
- `test_blueprint_engine.py` - 7 unit tests for planning logic
- `test_blueprint_api.py` - 7 API integration tests for endpoints and RBAC

**Test Coverage:**
- Blueprint drafting from various brief types
- Task explosion with dependency chains
- Agent job generation
- RBAC permission enforcement
- API request/response validation

---

## File Tree (New/Changed)

```
bridge_backend/
  bridge_core/
    engines/blueprint/
      __init__.py              [NEW]
      blueprint_engine.py      [NEW]
      planner_rules.py         [NEW]
      routes.py                [NEW]
    middleware/
      permissions.py           [MODIFIED] + RBAC entries
    missions/
      routes.py                [MODIFIED] + /jobs endpoint
    db/
      db_manager.py            [MODIFIED] + get_db_session
  models.py                    [MODIFIED] + Blueprint, AgentJob
  schemas.py                   [MODIFIED] + Pydantic schemas
  main.py                      [MODIFIED] + blueprint router
  
tests/
  test_blueprint_engine.py     [NEW]
  test_blueprint_api.py        [NEW]

bridge-frontend/
  src/
    components/
      BlueprintWizard.jsx      [NEW]
      AgentDeliberationPanel.jsx [NEW]
      MissionLogV2.jsx         [NEW]
      ui/
        Tree.tsx               [NEW]
    config.js                  [MODIFIED] + WebSocket config
  .env.example                 [MODIFIED] + VITE_WS_BASE

blueprint_partition_patch.sql  [NEW] - PostgreSQL partitioning
maintenance.sql                [MODIFIED] + agent_jobs partitions
BLUEPRINT_ENGINE_GUIDE.md      [NEW] - Complete usage guide
```

---

## Backend - Models (Additions)

```python
# bridge_backend/models.py
class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"
    skipped = "skipped"

class Blueprint(Base):
    __tablename__ = "blueprints"
    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int | None] = mapped_column(ForeignKey("missions.id"))
    captain: Mapped[str] = mapped_column(index=True)
    title: Mapped[str]
    brief: Mapped[str]
    plan: Mapped[dict] = mapped_column(JSON)  # objectives/tasks/deps/artifacts
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]

class AgentJob(Base):
    __tablename__ = "agent_jobs"
    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"))
    blueprint_id: Mapped[int] = mapped_column(ForeignKey("blueprints.id"))
    captain: Mapped[str] = mapped_column(index=True)
    agent_name: Mapped[str | None]
    role: Mapped[str] = mapped_column(default="agent")
    task_key: Mapped[str] = mapped_column(index=True)  # "T2.1"
    task_desc: Mapped[str]
    status: Mapped[str] = mapped_column(default="queued")
    inputs: Mapped[dict] = mapped_column(JSON)
    outputs: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

---

## How This Shifts the Product

**Before:** Captains manually create step-by-step mission plans
**After:** Captains submit briefs → Bridge generates structured plans → Agents execute

**Armada** = "who" (captains + agents) - unchanged
**Mission Log v2** = "how" with first-class Blueprint (plan-of-record)
**Autonomy Engine** = consumes agent_jobs directly
**Deliberation UI** = shows agent reasoning and decisions in real-time

---

## Rollout Instructions

### 1. Database Migration

**SQLite (automatic):**
```bash
cd bridge_backend
python -c "import asyncio; from db import init_database; asyncio.run(init_database())"
```

**PostgreSQL:**
```bash
# Base tables (if not already applied)
psql "$DATABASE_URL" -f init.sql

# Blueprint + agent_jobs tables
psql "$DATABASE_URL" -f blueprint_partition_patch.sql
```

### 2. Backend Startup

Add to `main.py` (already done in this PR):
```python
from bridge_core.engines.blueprint.routes import router as blueprint_router
app.include_router(blueprint_router)
```

### 3. Frontend Build

```bash
cd bridge-frontend
npm install  # If new dependencies
npm run build
```

Set environment variables:
```bash
VITE_API_BASE=https://sr-aibridge.onrender.com
VITE_WS_BASE=wss://sr-aibridge.onrender.com
```

### 4. Try It

**Draft Blueprint:**
```bash
curl -X POST http://localhost:8000/blueprint/draft \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q4 Launch",
    "brief": "Launch marketing site with social media assets",
    "captain": "Captain-Alpha"
  }'
```

**Commit to Mission:**
```bash
curl -X POST "http://localhost:8000/blueprint/1/commit?mission_id=1"
```

**View Jobs:**
```bash
curl http://localhost:8000/missions/1/jobs
```

---

## Acceptance Criteria

- [x] Draft blueprint from brief; returns structured plan
- [x] Commit blueprint to existing mission; emits agent_jobs
- [x] Mission Log shows task tree + statuses
- [x] Deliberation panel streams decisions/updates
- [x] RBAC enforced; deletes require email archival
- [x] Works on SQLite and Postgres
- [x] 14 tests passing (7 engine + 7 API)
- [x] End-to-end workflow validated
- [x] Complete documentation (BLUEPRINT_ENGINE_GUIDE.md)
- [x] PostgreSQL partition patch for high-volume deployments

---

## Testing

**Run Tests:**
```bash
cd bridge_backend
PYTHONPATH=. pytest ../tests/test_blueprint_engine.py -v  # 7 passed
PYTHONPATH=. pytest ../tests/test_blueprint_api.py -v     # 7 passed
```

**End-to-End:**
```bash
cd bridge_backend
python -c "
import asyncio
from bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine

async def test():
    engine = BlueprintEngine()
    plan = engine.draft('Marketing launch Q4')
    jobs = engine.agent_jobs_from_plan(1, 1, 'Captain-Alpha', plan)
    print(f'✅ Generated {len(jobs)} jobs from {len(plan[\"objectives\"])} objectives')

asyncio.run(test())
"
```

---

## What's Next

**Immediate:**
- Deploy to Render with new environment variables
- Run database migrations (SQLite auto, Postgres manual)
- Test UI in production

**Future Enhancements:**
- Replace planner_rules.py with LLM for smarter planning
- Add blueprint refinement endpoint (edit before commit)
- Agent-to-agent task handoff visualization
- Timeline view for mission progress
- Export blueprints to PDF/Markdown

---

## Support & Documentation

- **Usage Guide:** [BLUEPRINT_ENGINE_GUIDE.md](./BLUEPRINT_ENGINE_GUIDE.md)
- **PostgreSQL Setup:** [POSTGRES_MIGRATION.md](./POSTGRES_MIGRATION.md)
- **Main Docs:** [README.md](./README.md)

**All tests passing. Ready to merge! 🚀**
