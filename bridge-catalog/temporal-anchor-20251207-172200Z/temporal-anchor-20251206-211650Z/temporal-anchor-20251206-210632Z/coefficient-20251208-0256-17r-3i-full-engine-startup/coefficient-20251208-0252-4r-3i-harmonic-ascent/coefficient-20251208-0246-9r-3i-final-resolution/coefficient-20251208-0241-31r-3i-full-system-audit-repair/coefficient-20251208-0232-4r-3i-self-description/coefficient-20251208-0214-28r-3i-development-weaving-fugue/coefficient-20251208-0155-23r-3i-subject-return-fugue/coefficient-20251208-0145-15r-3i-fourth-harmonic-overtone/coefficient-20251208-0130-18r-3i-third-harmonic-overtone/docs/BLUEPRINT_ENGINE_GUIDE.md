# Blueprint Engine + Mission Log v2 - Usage Guide

## Overview

The Blueprint Engine transforms free-form mission briefs into structured, executable plans with task dependencies, success criteria, and agent job assignments. Mission Log v2 provides real-time visualization of task execution with agent deliberation streaming.

---

## Architecture

### Backend Components

**Blueprint Engine** (`bridge_backend/bridge_core/engines/blueprint/`)
- `planner_rules.py` - Deterministic planning logic (derive objectives, explode tasks)
- `blueprint_engine.py` - Core engine (draft blueprints, generate agent jobs)
- `routes.py` - FastAPI endpoints (draft, commit, delete, list)

**Database Models** (`bridge_backend/models.py`)
- `Blueprint` - Stores mission blueprints with plan structure (JSON)
- `AgentJob` - Tracks individual agent tasks with status, dependencies, outputs

**Schemas** (`bridge_backend/schemas.py`)
- `BlueprintPlan`, `TaskItem` - Structured plan representation
- `BlueprintCreate`, `BlueprintOut` - API request/response models
- `AgentJobOut` - Job status and details

### Frontend Components

**BlueprintWizard** (`bridge-frontend/src/components/BlueprintWizard.jsx`)
- Draft blueprints from mission briefs
- Preview generated plan with objectives, tasks, artifacts
- Commit blueprints to missions

**MissionLogV2** (`bridge-frontend/src/components/MissionLogV2.jsx`)
- Hierarchical task tree visualization
- Status summary dashboard
- Detailed task cards with dependencies

**AgentDeliberationPanel** (`bridge-frontend/src/components/AgentDeliberationPanel.jsx`)
- Real-time WebSocket connection to agent activity
- Streaming decision logs and job updates
- Visual connection status indicator

**Tree** (`bridge-frontend/src/components/ui/Tree.tsx`)
- Reusable hierarchical tree component
- Color-coded status visualization
- Expandable/collapsible nodes

---

## Quick Start

### Backend Setup

1. **Database Migration** (SQLite auto-creates, Postgres requires init)

SQLite (automatic):
```bash
cd bridge_backend
python -c "import asyncio; from db import init_database; asyncio.run(init_database())"
```

PostgreSQL (run init.sql + optional partition patch):
```bash
psql "$DATABASE_URL" -f init.sql
psql "$DATABASE_URL" -f blueprint_partition_patch.sql  # Optional: monthly partitions for agent_jobs
```

2. **Start Backend**

```bash
cd bridge_backend
uvicorn main:app --reload --port 8000
```

3. **Verify Endpoints**

```bash
# Health check
curl http://localhost:8000/health

# List blueprints (empty initially)
curl http://localhost:8000/blueprint
```

### Frontend Setup

1. **Configure Environment**

```bash
cd bridge-frontend
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_BASE=http://localhost:8000
VITE_WS_BASE=ws://localhost:8000
```

2. **Install & Run**

```bash
npm install
npm run dev
```

3. **Access UI**

Open http://localhost:5173 (or Vite's port)

---

## API Usage

### 1. Draft a Blueprint

**POST** `/blueprint/draft`

Creates a structured plan from a free-form brief.

```bash
curl -X POST http://localhost:8000/blueprint/draft \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Q4 Marketing Launch",
    "brief": "Launch marketing campaign for Q4 with social media and email",
    "captain": "Captain-Alpha"
  }'
```

**Response:**
```json
{
  "id": 1,
  "mission_id": null,
  "captain": "Captain-Alpha",
  "title": "Q4 Marketing Launch",
  "brief": "Launch marketing campaign...",
  "plan": {
    "objectives": [
      "Clarify requirements",
      "Collect sources/data",
      "Produce deliverable",
      "Create distribution plan"
    ],
    "tasks": [
      {
        "key": "T1",
        "title": "Clarify requirements",
        "detail": "Execute objective: Clarify requirements — context: Launch marketing campaign...",
        "depends_on": [],
        "role_hint": "agent",
        "acceptance": ["Document steps taken", "Record logs and outputs", "Attach relevant artifacts"]
      },
      ...
    ],
    "artifacts": ["report.md", "logs.json"],
    "success_criteria": [
      "All acceptance criteria satisfied",
      "No task failing; critical tasks done"
    ]
  },
  "created_at": "2024-10-05T00:00:00",
  "updated_at": "2024-10-05T00:00:00"
}
```

### 2. Commit Blueprint to Mission

**POST** `/blueprint/{bp_id}/commit?mission_id={mission_id}`

Locks in the blueprint and generates agent jobs.

```bash
curl -X POST "http://localhost:8000/blueprint/1/commit?mission_id=1"
```

**Response:**
```json
{
  "ok": true,
  "created_jobs": 4,
  "blueprint_id": 1,
  "mission_id": 1
}
```

### 3. Get Mission Jobs

**GET** `/missions/{mission_id}/jobs`

Retrieves all agent jobs for a mission.

```bash
curl http://localhost:8000/missions/1/jobs
```

**Response:**
```json
[
  {
    "id": 1,
    "mission_id": 1,
    "blueprint_id": 1,
    "task_key": "T1",
    "task_desc": "Clarify requirements: Execute objective...",
    "status": "queued",
    "agent_name": null,
    "inputs": {"depends_on": []},
    "outputs": {},
    "created_at": "2024-10-05T00:00:00",
    "updated_at": "2024-10-05T00:00:00"
  },
  ...
]
```

### 4. Delete Blueprint (Admiral Only)

**DELETE** `/blueprint/{bp_id}`

Archives to relay mailer before deletion (if enabled).

```bash
curl -X DELETE http://localhost:8000/blueprint/1
```

---

## Frontend Usage

### Using BlueprintWizard

```jsx
import BlueprintWizard from './components/BlueprintWizard';

function MyPage() {
  return (
    <BlueprintWizard
      captain="Captain-Alpha"
      onComplete={(blueprint, missionId) => {
        console.log('Blueprint committed!', blueprint, missionId);
        // Navigate to mission view or refresh
      }}
    />
  );
}
```

### Using MissionLogV2

```jsx
import MissionLogV2 from './components/MissionLogV2';

function MissionView({ missionId }) {
  return (
    <MissionLogV2
      missionId={missionId}
      captain="Captain-Alpha"
    />
  );
}
```

---

## PostgreSQL Partitioning

For high-volume deployments, use monthly partitioned `agent_jobs` table.

### Initial Setup

```bash
psql "$DATABASE_URL" -f blueprint_partition_patch.sql
```

This creates:
- Monthly partitions for current + next 12 months
- Indexes on each partition (mission_id, captain_id, task_key, status)
- `blueprints` table (non-partitioned)

### Monthly Maintenance

Run automatically via cron or GitHub Actions:

```bash
psql "$DATABASE_URL" -f maintenance.sql
```

This:
- Creates next month's partition
- Applies indexes
- Drops partitions older than 18 months

**GitHub Actions Example:**

```yaml
name: PostgreSQL Monthly Maintenance
on:
  schedule:
    - cron: '0 2 1 * *'  # 2 AM on the 1st of each month
  workflow_dispatch:

jobs:
  maintenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run maintenance
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f maintenance.sql
```

---

## RBAC Permissions

Defined in `bridge_backend/bridge_core/middleware/permissions.py`:

| Role    | blueprint:create | blueprint:commit | blueprint:delete |
|---------|------------------|------------------|------------------|
| Admiral | ✓                | ✓                | ✓                |
| Captain | ✓                | ✓                | ✗                |
| Agent   | ✗                | ✗                | ✗                |

- **Captains** can draft and commit blueprints for their own missions
- **Admiral** can delete blueprints (with relay archival)
- **Agents** have no blueprint management access

---

## Customization

### Extending Planner Rules

Edit `bridge_backend/bridge_core/engines/blueprint/planner_rules.py`:

```python
def derive_objectives(brief: str) -> List[str]:
    # Add custom logic based on keywords, entities, or LLM
    if "security" in brief.lower():
        base.append("Conduct security audit")
    
    # Integrate with external services
    if "customer" in brief.lower():
        base.append("Review customer feedback")
    
    return base
```

### Plugging in an LLM

Replace deterministic rules with LLM calls in `blueprint_engine.py`:

```python
async def draft(self, brief: str) -> Dict[str, Any]:
    # Call OpenAI, Claude, or local LLM
    llm_response = await call_llm_api(
        prompt=f"Generate mission objectives and tasks for: {brief}"
    )
    
    # Parse LLM output into plan structure
    plan = parse_llm_response(llm_response)
    return plan
```

---

## Testing

### Run Backend Tests

```bash
cd bridge_backend
PYTHONPATH=. pytest ../tests/test_blueprint_engine.py -v
PYTHONPATH=. pytest ../tests/test_blueprint_api.py -v
```

**Expected Output:**
```
7 passed in test_blueprint_engine.py
7 passed in test_blueprint_api.py
```

### Manual Testing

1. **Draft Blueprint:**
   ```bash
   curl -X POST http://localhost:8000/blueprint/draft \
     -H "Content-Type: application/json" \
     -d '{"title":"Test","brief":"Test brief","captain":"Test"}'
   ```

2. **Create Mission:**
   ```bash
   # Create a test mission first (or use existing ID)
   ```

3. **Commit Blueprint:**
   ```bash
   curl -X POST "http://localhost:8000/blueprint/1/commit?mission_id=1"
   ```

4. **View Jobs:**
   ```bash
   curl http://localhost:8000/missions/1/jobs
   ```

---

## Troubleshooting

### Backend Issues

**Error: `ModuleNotFoundError: No module named 'bridge_backend'`**
- Run with `PYTHONPATH=/path/to/bridge_backend`

**Error: `Blueprint not found`**
- Check blueprint ID exists: `curl http://localhost:8000/blueprint`

**Error: `Mission not found`**
- Ensure mission exists before committing blueprint

### Frontend Issues

**WebSocket not connecting**
- Verify `VITE_WS_BASE` in `.env`
- Check backend WebSocket endpoint availability
- Inspect browser console for connection errors

**Tree component not rendering**
- Ensure jobs are fetched successfully
- Check browser console for errors
- Verify Tree.tsx is properly imported

### Database Issues

**SQLite: `no such table: blueprints`**
- Run `init_database()` to create tables

**Postgres: `relation "sra.agent_jobs" does not exist`**
- Run `blueprint_partition_patch.sql`

---

## Production Deployment

### Environment Variables

**Backend (.env):**
```bash
DATABASE_TYPE=postgres
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
RELAY_ENABLED=true
RELAY_EMAIL=sraibridge@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Frontend (.env):**
```bash
VITE_API_BASE=https://sr-aibridge.onrender.com
VITE_WS_BASE=wss://sr-aibridge.onrender.com
```

### Render Deployment

1. **Backend:**
   - Build: `cd bridge_backend && pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`

2. **Frontend:**
   - Build: `cd bridge-frontend && npm run build`
   - Serve: Static site from `dist/`

3. **Database:**
   - Provision PostgreSQL instance
   - Run `init.sql` + `blueprint_partition_patch.sql`

---

## Support

- **Issues:** https://github.com/kswhitlock9493-jpg/SR-AIbridge-/issues
- **Docs:** See POSTGRES_MIGRATION.md, README.md
- **Tests:** Run pytest suite for validation
