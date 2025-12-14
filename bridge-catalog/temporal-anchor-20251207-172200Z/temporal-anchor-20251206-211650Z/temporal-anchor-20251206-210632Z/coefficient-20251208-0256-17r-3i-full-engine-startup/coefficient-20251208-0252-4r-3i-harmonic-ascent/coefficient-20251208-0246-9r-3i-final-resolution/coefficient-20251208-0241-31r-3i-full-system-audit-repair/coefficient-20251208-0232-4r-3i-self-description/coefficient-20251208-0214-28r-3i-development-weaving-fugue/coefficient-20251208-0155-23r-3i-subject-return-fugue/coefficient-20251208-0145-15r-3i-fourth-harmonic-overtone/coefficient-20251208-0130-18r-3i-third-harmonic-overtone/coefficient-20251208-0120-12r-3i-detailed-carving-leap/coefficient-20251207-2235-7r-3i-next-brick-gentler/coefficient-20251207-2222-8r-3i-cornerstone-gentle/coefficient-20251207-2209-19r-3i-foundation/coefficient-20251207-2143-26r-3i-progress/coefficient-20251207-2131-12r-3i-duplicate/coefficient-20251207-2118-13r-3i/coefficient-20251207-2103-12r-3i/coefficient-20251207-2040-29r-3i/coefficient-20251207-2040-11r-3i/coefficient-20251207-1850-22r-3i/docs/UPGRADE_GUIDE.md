# SR-AIbridge Upgrade Guide

This guide provides instructions for upgrading your SR-AIbridge deployment from the basic in-memory demo to a fully autonomous, production-ready system with database persistence.

## Current Architecture (v1.1.0-autonomous)

SR-AIbridge now operates in **fully autonomous mode** with the following capabilities:

### 🤖 Autonomous Backend Features
- **Self-Managing Missions**: Agents automatically assign themselves to missions and progress through statuses
- **Real-Time Reports**: System generates agent reports, vault logs, and fleet updates continuously
- **Live Fleet Command**: Enhanced armada management with ship movement and status tracking
- **NPC Interactions**: Autonomous captain-to-captain communications with simulated responses
- **WebSocket Integration**: Real-time updates pushed to all connected clients

### 🌐 Enhanced Frontend Features
- **Live Data Streaming**: All panels update in real-time via WebSocket connections
- **Connection Status**: Visual indicators for backend and WebSocket connectivity
- **Auto-Refresh Panels**: No manual toggles required - everything updates automatically
- **Enhanced Visualizations**: Improved fleet maps, mission logs, and chat interfaces

## Deployment Options

> **🚀 New in v1.1.0**: Automated CI/CD pipeline with health monitoring available for all deployment options! See [CI/CD & Monitoring](#cicd--monitoring) section below.

### Option 1: Quick Start (In-Memory Demo)

**Perfect for**: Development, testing, demonstrations, proof-of-concept

**Advantages**:
- ✅ Zero configuration required
- ✅ No database setup needed
- ✅ Instant deployment
- ✅ Full feature set available
- ✅ Perfect for Render free tier

**Limitations**:
- ⚠️ Data resets on restart
- ⚠️ Single instance only
- ⚠️ Memory usage scales with data

**Deployment Steps**:

1. **Backend (Render)**:
   ```bash
   # Deploy from GitHub
   Repository: https://github.com/kswhitlock9493-jpg/SR-AIbridge-
   Build Command: cd bridge_backend && pip install -r requirements.txt
   Start Command: cd bridge_backend && uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Frontend (Netlify)**:
   ```bash
   # Deploy from GitHub
   Repository: https://github.com/kswhitlock9493-jpg/SR-AIbridge-
   Build Command: cd bridge-frontend && npm install && npm run build
   Publish Directory: bridge-frontend/build
   ```

3. **Configuration**:
   - Update `bridge-frontend/src/config.js` with your Render backend URL
   - Ensure CORS settings in backend allow your Netlify domain

### Option 2: Production Database Backend

**Perfect for**: Production deployments, enterprise use, persistent data requirements

**Advantages**:
- ✅ Persistent data storage
- ✅ Multi-instance scaling
- ✅ Production performance
- ✅ Data backup and recovery
- ✅ Advanced querying capabilities

**Prerequisites**:
- PostgreSQL database (Render PostgreSQL, AWS RDS, or similar)
- Environment variable management
- Database migration tools

**Upgrade Steps**:

#### Step 1: Database Setup

1. **Create PostgreSQL Database**:
   ```bash
   # On Render
   Create New PostgreSQL Database
   Note the Internal Database URL
   ```

2. **Update Requirements**:
   ```txt
   # Add to bridge_backend/requirements.txt
   sqlalchemy>=2.0.0
   asyncpg>=0.28.0
   alembic>=1.12.0
   databases[postgresql]>=0.8.0
   ```

#### Step 2: Database Models

1. **Create Database Models** (`bridge_backend/models.py`):
   ```python
   from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
   from sqlalchemy.ext.declarative import declarative_base
   from sqlalchemy.sql import func
   
   Base = declarative_base()
   
   class Agent(Base):
       __tablename__ = "agents"
       id = Column(Integer, primary_key=True)
       name = Column(String(255), nullable=False)
       endpoint = Column(String(255), nullable=False)
       status = Column(String(50), default="online")
       capabilities = Column(Text)  # JSON stored as text
       last_heartbeat = Column(DateTime, server_default=func.now())
       created_at = Column(DateTime, server_default=func.now())
   
   class Mission(Base):
       __tablename__ = "missions"
       id = Column(Integer, primary_key=True)
       title = Column(String(255), nullable=False)
       description = Column(Text)
       status = Column(String(50), default="active")
       priority = Column(String(50), default="normal")
       assigned_agent_id = Column(Integer)
       created_at = Column(DateTime, server_default=func.now())
       updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
   
   class VaultLog(Base):
       __tablename__ = "vault_logs"
       id = Column(Integer, primary_key=True)
       agent_name = Column(String(255), nullable=False)
       action = Column(String(255), nullable=False)
       details = Column(Text, nullable=False)
       log_level = Column(String(50), default="info")
       timestamp = Column(DateTime, server_default=func.now())
   
   class CaptainMessage(Base):
       __tablename__ = "captain_messages"
       id = Column(Integer, primary_key=True)
       from_ = Column("from_user", String(255), nullable=False)
       to = Column(String(255), nullable=False)
       message = Column(Text, nullable=False)
       timestamp = Column(DateTime, server_default=func.now())
   
   class ArmadaShip(Base):
       __tablename__ = "armada_ships"
       id = Column(Integer, primary_key=True)
       name = Column(String(255), nullable=False)
       status = Column(String(50), default="online")
       location = Column(String(255), nullable=False)
       patrol_sectors = Column(Text)  # JSON array as text
       updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
   ```

2. **Create Database Service** (`bridge_backend/database.py`):
   ```python
   import os
   from sqlalchemy import create_engine
   from sqlalchemy.orm import sessionmaker
   from databases import Database
   from models import Base
   
   DATABASE_URL = os.getenv("DATABASE_URL")
   
   if DATABASE_URL.startswith("postgres://"):
       DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
   
   # For SQLAlchemy
   engine = create_engine(DATABASE_URL)
   SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
   
   # For async operations
   database = Database(DATABASE_URL)
   
   def create_tables():
       Base.metadata.create_all(bind=engine)
   ```

#### Step 3: Update Main Application

1. **Update Storage Backend** (`bridge_backend/database_storage.py`):
   ```python
   from database import database, SessionLocal
   from models import Agent, Mission, VaultLog, CaptainMessage, ArmadaShip
   import json
   from datetime import datetime
   
   class DatabaseStorage:
       async def connect(self):
           await database.connect()
       
       async def disconnect(self):
           await database.disconnect()
       
       async def get_agents(self):
           query = "SELECT * FROM agents ORDER BY created_at DESC"
           return await database.fetch_all(query)
       
       async def create_agent(self, agent_data):
           query = """
           INSERT INTO agents (name, endpoint, capabilities, status)
           VALUES (:name, :endpoint, :capabilities, :status)
           RETURNING *
           """
           return await database.fetch_one(query, agent_data)
       
       # Add similar methods for other entities...
   ```

2. **Update Main Application**:
   ```python
   # In main.py, replace InMemoryStorage with DatabaseStorage
   from database_storage import DatabaseStorage
   from database import create_tables
   
   # Replace storage initialization
   storage = DatabaseStorage()
   
   @app.on_event("startup")
   async def startup():
       create_tables()
       await storage.connect()
       # ... rest of startup code
   
   @app.on_event("shutdown") 
   async def shutdown():
       await storage.disconnect()
   ```

#### Step 4: Environment Configuration

1. **Set Environment Variables**:
   ```bash
   # In Render Dashboard
   DATABASE_URL=postgresql://user:password@host:port/database
   ENVIRONMENT=production
   ```

2. **Update CORS for Production**:
   ```python
   # In main.py
   origins = [
       "https://your-app.netlify.app",
       "https://your-custom-domain.com"
   ]
   ```

#### Step 5: Deploy Database Version

1. **Deploy Backend**:
   ```bash
   # Render will automatically detect changes and redeploy
   # Database migrations will run on startup
   ```

2. **Verify Database Connection**:
   ```bash
   # Check logs in Render dashboard
   # Look for "✅ Database connected" message
   ```

## Feature Comparison

| Feature | In-Memory Demo | Database Production |
|---------|---------------|-------------------|
| Data Persistence | ❌ Lost on restart | ✅ Permanent storage |
| Scalability | ⚠️ Single instance | ✅ Multi-instance |
| Setup Complexity | ✅ Zero config | ⚠️ Database required |
| Development Speed | ✅ Instant | ⚠️ Setup time |
| Production Ready | ⚠️ Demo only | ✅ Enterprise ready |
| Cost | ✅ Free tier friendly | ⚠️ Database costs |
| Backup/Recovery | ❌ Not available | ✅ Database backups |

## Migration Strategy

### Zero-Downtime Migration

1. **Deploy Database Backend** alongside existing in-memory version
2. **Test Database Version** with separate endpoints
3. **Update Frontend** to point to database backend
4. **Verify Functionality** across all components
5. **Switch DNS/Routing** to database backend
6. **Monitor Performance** and rollback if needed

### Data Migration (Optional)

If you have critical demo data to preserve:

```python
# migration_script.py
import asyncio
import aiohttp
import asyncpg

async def migrate_data():
    # Fetch from in-memory backend
    async with aiohttp.ClientSession() as session:
        async with session.get("https://old-backend.onrender.com/agents") as resp:
            agents = await resp.json()
    
    # Insert into database backend
    conn = await asyncpg.connect("postgresql://...")
    for agent in agents:
        await conn.execute("""
            INSERT INTO agents (name, endpoint, status, capabilities)
            VALUES ($1, $2, $3, $4)
        """, agent['name'], agent['endpoint'], agent['status'], json.dumps(agent['capabilities']))
    
    await conn.close()

asyncio.run(migrate_data())
```

## Troubleshooting

### Common Issues

**Issue**: WebSocket connections failing
**Solution**: Check CORS settings and ensure WebSocket URL is correct

**Issue**: Database connection errors
**Solution**: Verify DATABASE_URL format and database accessibility

**Issue**: Memory usage high in in-memory mode
**Solution**: Consider database upgrade or implement data rotation

**Issue**: Slow performance with large datasets
**Solution**: Add database indexes and implement pagination

### Performance Optimization

1. **Database Indexes**:
   ```sql
   CREATE INDEX idx_missions_status ON missions(status);
   CREATE INDEX idx_vault_logs_timestamp ON vault_logs(timestamp DESC);
   CREATE INDEX idx_agents_status ON agents(status);
   ```

2. **Connection Pooling**:
   ```python
   # In database.py
   engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0)
   ```

3. **Caching Strategy**:
   ```python
   # Add Redis for frequently accessed data
   import redis
   redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
   ```

## Support and Maintenance

### Monitoring

- **Health Checks**: `/status` endpoint for uptime monitoring
- **WebSocket Stats**: `/ws/stats` for connection monitoring  
- **Database Performance**: Monitor query times and connection counts

### Backup Strategy

- **Automated Backups**: Configure daily database backups
- **Point-in-time Recovery**: Enable for critical data protection
- **Disaster Recovery**: Document recovery procedures

### Updates and Scaling

- **Rolling Updates**: Deploy new versions without downtime
- **Horizontal Scaling**: Add multiple backend instances
- **Load Balancing**: Distribute traffic across instances

## CI/CD & Monitoring

### Automated Deployment Pipeline

SR-AIbridge includes a comprehensive CI/CD infrastructure with GitHub Actions:

#### 🚀 Deployment Workflow (`.github/workflows/deploy.yml`)

**Automatic Features:**
- **Frontend Build & Deploy**: Automatically builds React app and deploys to Netlify
- **Backend Validation**: Validates Python code and triggers Render deployment  
- **Build Verification**: Tests complete build process before deployment
- **Pull Request Testing**: Validates changes before merging

**Setup Requirements:**
```bash
# Required GitHub Secrets (optional but recommended)
NETLIFY_AUTH_TOKEN=your_netlify_token
NETLIFY_SITE_ID=your_netlify_site_id

# Optional: Custom deployment URLs
BACKEND_URL=https://your-backend.onrender.com
FRONTEND_URL=https://your-frontend.netlify.app
RENDER_DEPLOY_HOOK=https://api.render.com/deploy/your-hook
```

#### 🧪 Health Monitoring Workflow (`.github/workflows/self-test.yml`)

**Comprehensive Testing:**
- **Post-Deployment Health Checks**: Runs automatically after successful deployments
- **Scheduled Monitoring**: Health checks every 4 hours to ensure ongoing reliability
- **Manual Testing**: Trigger health checks anytime with custom parameters
- **Detailed Reporting**: JSON artifacts with test results and performance metrics

**Monitoring Coverage:**
- ✅ API endpoint health (`/health`, `/status`, `/`)
- ✅ Guardian daemon functionality  
- ✅ Agent management operations
- ✅ Mission/task system
- ✅ WebSocket connectivity
- ✅ Vault logs and doctrine endpoints
- ✅ System utility functions

#### Enhanced Self-Test Script

The `bridge_backend/self_test.py` script has been enhanced for production monitoring:

```bash
# Production health check
python3 self_test.py --url https://your-backend.onrender.com --json

# Advanced CI/CD usage
python3 self_test.py \
  --url $BACKEND_URL \
  --timeout 45 \
  --retries 5 \
  --wait-ready 120 \
  --json > health_report.json

# Local development testing  
python3 self_test.py --timeout 10 --wait-ready 30
```

**New Features:**
- **Configurable Timeouts**: Adjust for slow networks or cold starts
- **Retry Logic**: Exponential backoff for transient failures
- **Production URLs**: Built-in support for HTTPS endpoints
- **JSON Output**: Machine-readable results for automation
- **Wait-for-Ready**: Intelligent backend readiness detection

#### Manual Health Monitoring

**Using GitHub Actions UI:**

1. Navigate to your repository's **Actions** tab
2. Select **"Self-Test SR-AIbridge"** workflow
3. Click **"Run workflow"** 
4. Optionally specify custom backend URL
5. Review detailed results in workflow summary

**Direct Script Usage:**

```bash
# Clone repository locally
git clone https://github.com/your-username/SR-AIbridge.git
cd SR-AIbridge/bridge_backend

# Install dependencies
pip install -r requirements.txt

# Run health check against your deployment
python3 self_test.py --url https://your-backend.onrender.com
```

#### Monitoring Dashboard

**GitHub Actions provides:**
- ✅ Workflow success/failure history
- ✅ Detailed step-by-step logs
- ✅ Performance metrics and trends
- ✅ Downloadable test artifacts (JSON reports)
- ✅ Email notifications for failures

**Available Metrics:**
- Response times for all endpoints
- Success rates over time
- Error patterns and frequencies  
- WebSocket connection statistics
- Guardian daemon health status

#### Troubleshooting CI/CD

**Common Issues:**

**Issue**: Deployment workflow fails on Netlify
**Solution**: Check `NETLIFY_AUTH_TOKEN` and `NETLIFY_SITE_ID` secrets

**Issue**: Backend health tests timeout
**Solution**: Increase `--wait-ready` parameter or check backend startup time

**Issue**: Self-test script fails locally
**Solution**: Verify backend URL and network connectivity

**Integration with Deployment Options:**

- **In-Memory Demo**: Full CI/CD support with zero additional configuration
- **Database Production**: Enhanced monitoring for database connectivity and performance
- **Container Deployment**: Docker-compatible health checks and deployment validation

---

**Need Help?** 

- Check the [README.md](./README.md) for basic setup instructions
- Review backend logs in Render dashboard
- Test WebSocket connections at `/ws/stats`
- Verify database connectivity with health checks

**Ready to Deploy?**

Choose your deployment strategy based on your requirements:
- **Quick Demo**: Use in-memory version for immediate results
- **Production**: Follow database upgrade path for scalable solution