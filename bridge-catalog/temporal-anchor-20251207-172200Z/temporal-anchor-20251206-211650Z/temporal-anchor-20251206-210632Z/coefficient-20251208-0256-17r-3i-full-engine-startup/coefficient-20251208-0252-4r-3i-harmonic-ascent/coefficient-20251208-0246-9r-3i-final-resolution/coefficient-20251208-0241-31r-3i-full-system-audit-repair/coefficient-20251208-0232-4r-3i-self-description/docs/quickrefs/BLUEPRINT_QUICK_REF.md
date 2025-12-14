# Blueprint Engine - Quick Reference

## API Endpoints

```bash
# Draft blueprint from brief
POST /blueprint/draft
{
  "title": "Mission Title",
  "brief": "Free-form description",
  "captain": "Captain-Alpha"
}

# Commit blueprint to mission (creates agent jobs)
POST /blueprint/{bp_id}/commit?mission_id={mission_id}

# Get blueprint by ID
GET /blueprint/{bp_id}

# List all blueprints (filter by captain)
GET /blueprint?captain={captain}

# Delete blueprint (Admiral only, with relay archival)
DELETE /blueprint/{bp_id}

# Get agent jobs for mission
GET /missions/{mission_id}/jobs
```

## Frontend Components

```jsx
// Create blueprint wizard
<BlueprintWizard 
  captain="Captain-Alpha"
  onComplete={(bp, missionId) => { ... }}
/>

// Mission task tree + deliberation
<MissionLogV2 
  missionId={1}
  captain="Captain-Alpha"
/>

// Agent deliberation panel only
<AgentDeliberationPanel missionId={1} />

// Reusable tree component
<Tree nodes={taskTree} onNodeClick={handleClick} />
```

## Database Models

```python
# Blueprint (plan storage)
Blueprint(
    title="...",
    brief="...",
    captain="...",
    plan={
        "objectives": [...],
        "tasks": [...],
        "artifacts": [...],
        "success_criteria": [...]
    }
)

# Agent Job (task execution)
AgentJob(
    mission_id=1,
    blueprint_id=1,
    task_key="T1",
    task_desc="...",
    status="queued",  # queued|running|done|failed|skipped
    inputs={"depends_on": [...]},
    outputs={}
)
```

## PostgreSQL Setup

```bash
# Initial setup (one-time)
psql "$DATABASE_URL" -f init.sql
psql "$DATABASE_URL" -f blueprint_partition_patch.sql

# Monthly maintenance (automated)
psql "$DATABASE_URL" -f maintenance.sql
```

## Environment Variables

```bash
# Backend
DATABASE_TYPE=postgres
DATABASE_URL=postgresql+asyncpg://...
RELAY_ENABLED=true
RELAY_EMAIL=sraibridge@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...

# Frontend
VITE_API_BASE=https://bridge.sr-aibridge.com
VITE_WS_BASE=wss://bridge.sr-aibridge.com
```

## RBAC Matrix

| Role    | Create | Commit | Delete |
|---------|--------|--------|--------|
| Admiral | ✓      | ✓      | ✓      |
| Captain | ✓      | ✓      | ✗      |
| Agent   | ✗      | ✗      | ✗      |

## Test Commands

```bash
# Run unit tests
PYTHONPATH=bridge_backend pytest tests/test_blueprint_engine.py -v

# Run API tests
PYTHONPATH=bridge_backend pytest tests/test_blueprint_api.py -v

# All tests
PYTHONPATH=bridge_backend pytest tests/test_blueprint*.py -v
```

## Example Workflow

```bash
# 1. Draft blueprint
curl -X POST http://localhost:8000/blueprint/draft \
  -H "Content-Type: application/json" \
  -d '{"title":"Q4 Launch","brief":"Marketing campaign","captain":"Alpha"}'
# → Returns blueprint with ID 1

# 2. Commit to mission
curl -X POST "http://localhost:8000/blueprint/1/commit?mission_id=1"
# → Creates agent jobs

# 3. View jobs
curl http://localhost:8000/missions/1/jobs
# → Returns list of agent jobs with status

# 4. Monitor via WebSocket
# ws://localhost:8000/ws/mission/1
# → Real-time job status updates
```

## Customization

```python
# Extend planner rules
# bridge_backend/bridge_core/engines/blueprint/planner_rules.py

def derive_objectives(brief: str) -> List[str]:
    if "security" in brief.lower():
        base.append("Conduct security audit")
    return base

# Plug in LLM
# bridge_backend/bridge_core/engines/blueprint/blueprint_engine.py

async def draft(self, brief: str):
    llm_response = await call_openai(brief)
    return parse_plan(llm_response)
```

## Common Issues

**Backend:**
- `ModuleNotFoundError` → Use `PYTHONPATH=bridge_backend`
- `Blueprint not found` → Check ID exists with `GET /blueprint`
- `Mission not found` → Ensure mission exists before commit

**Frontend:**
- WebSocket not connecting → Check `VITE_WS_BASE` in `.env`
- Tree not rendering → Verify jobs fetched successfully

**Database:**
- SQLite: Run `init_database()` to create tables
- Postgres: Run `blueprint_partition_patch.sql` if missing

---

**Full docs:** [BLUEPRINT_ENGINE_GUIDE.md](./BLUEPRINT_ENGINE_GUIDE.md)
