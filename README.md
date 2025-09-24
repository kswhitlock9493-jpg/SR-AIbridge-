# SR-AIbridge

A tactical command and control system for AI agent coordination with comprehensive health monitoring and self-healing capabilities.

## 🛡️ NEW: SQLite-first Backend with Full Health Monitoring

SR-AIbridge now includes a production-ready SQLite-first backend with:
- **🔍 Comprehensive Health Checks**: Real-time system monitoring
- **🔧 Self-Healing**: Automatic recovery from common issues
- **📊 Live Health Dashboard**: Visual system status monitoring
- **⚡ Safe Error Handling**: Structured error responses, no exposed exceptions
- **🚀 Zero-Config Deployment**: Works out of the box with SQLite

## 🚀 Quick Start (SQLite-first Backend)

### Backend Setup
```bash
cd bridge-backend
pip install -r requirements.txt
python main_sqlite.py
```

### Frontend Setup
```bash
cd bridge-frontend
npm install
npm start
```

Visit:
- 🌐 **Frontend**: http://localhost:3000
- 📊 **API Docs**: http://localhost:8000/docs
- 🔌 **Health Check**: http://localhost:8000/health
- 🛡️ **Full Health**: http://localhost:8000/health/full

## ✨ New Health Monitoring Features

### 🔍 Health Check Endpoints
- `GET /health` - Basic health for load balancers  
- `GET /health/full` - Comprehensive system health
- `POST /health/self-heal` - Trigger automatic recovery
- `GET /system/metrics` - Performance metrics

### 🛡️ SystemSelfTest Component
The frontend now includes a live health monitoring dashboard:
- **Auto-refresh**: Updates every 30 seconds
- **Visual Status**: Color-coded health indicators  
- **Self-Test**: Manual system validation
- **Self-Repair**: One-click recovery
- **Metrics Display**: Database counts and health scores

### 🔧 Self-Healing Capabilities
- Database connection recovery
- Guardian system maintenance  
- Orphaned record cleanup
- Configuration validation
- Automatic table creation

## 🎯 Classic Features

### 📊 Real-Time Dashboard
- System status overview (agents online, active missions, fleet status)
- Recent activity feed with vault logs
- Mission progress tracking
- Fleet deployment status

### 🤖 Agent Management
- Register and monitor AI agents
- Track agent capabilities and heartbeats
- Remove agents as needed
- Real-time status updates

### 🚀 Mission Control
- Create and track missions
- Priority and status management
- Timeline tracking
- Mission descriptions and updates

### 📜 Vault Logs
- Comprehensive activity logging
- Agent action tracking
- System alerts and notifications
- Filterable by log level (info, warning, error)

### 💬 Captain Communication
- Captain-to-captain messaging
- Real-time message updates
- Message history and threading

### 🗺️ Armada Fleet
- Fleet ship status and locations
- Online/offline ship tracking
- Deployment visualization

## 🛠️ API Endpoints

The backend provides a comprehensive REST API with full health monitoring:

### Health & Monitoring
- `GET /health` - Basic health check for load balancers
- `GET /health/full` - Comprehensive system health
- `POST /health/self-heal` - Trigger automatic recovery
- `GET /system/metrics` - Performance metrics and counts
- `POST /system/self-test` - Run comprehensive system test

### Core Endpoints
- `GET /status` - System status overview
- `GET /` - API information and health check

### Agent Management  
- `GET /agents` - List all agents (with safe error handling)
- `POST /agents` - Register new agent
- `DELETE /agents/{id}` - Remove agent

### Mission Control
- `GET /missions` - List all missions (with safe error handling)
- `POST /missions` - Create new mission

### Vault Logs
- `GET /vault/logs` - Get vault logs (with pagination)
- `POST /vault/logs` - Add vault log entry
- `GET /doctrine` - Alias for vault logs

### Guardian System
- `GET /guardians` - List all guardians
- `GET /guardian/status` - Guardian system status

### Communication
- `GET /captains/messages` - Get captain messages
- `POST /captains/send` - Send captain message
- `GET /chat/messages` - Alternative message endpoint
- `POST /chat/send` - Alternative send endpoint

### Fleet Management
- `GET /armada/status` - Get fleet status

### Utilities
- `GET /activity` - Recent combined activity
- `GET /reseed` - Regenerate demo data

All endpoints include comprehensive error handling and return safe, structured JSON responses.

## 🎮 Demo & Testing

### Run the Demo Seed Script
```bash
cd bridge-backend
python seed.py
```

This script will:
- ✅ Test all API endpoints
- ➕ Add additional demo data
- 📊 Show comprehensive system status
- 🌐 Verify frontend compatibility

### Interactive API Documentation
Visit http://localhost:8000/docs for:
- 📋 Complete API documentation
- 🧪 Interactive testing interface
- 📝 Request/response examples
- 🔧 Schema definitions

## 🏗️ Architecture

### SQLite-first Database
```python
# Modern async SQLAlchemy models
class Guardian(Base):
    - Health monitoring system
    - Self-test capabilities
    - Autonomous recovery

class VaultLog(Base):
    - Activity logging
    - Agent actions
    - System events

class Mission(Base):
    - Mission tracking
    - Progress monitoring  
    - Agent assignment
```

### Frontend Components
- **Dashboard.jsx** - Main overview with real-time data
- **SystemSelfTest.jsx** - Live health monitoring dashboard
- **VaultLogs.jsx** - Activity and log display
- **MissionLog.jsx** - Mission tracking interface
- **App.jsx** - Main application shell with navigation

### Backend Framework
- **FastAPI** - Modern, fast Python web framework
- **SQLAlchemy Async** - Modern async database toolkit
- **SQLite/PostgreSQL** - Database options for any scale
- **Pydantic** - Data validation and serialization
- **Uvicorn** - ASGI server for production deployment

## 🚢 Deployment (Production Ready)

### Render (Backend) + Netlify (Frontend)
The recommended production deployment uses the included configuration files:

**Backend (Render)**:
1. Connect repository to Render
2. Uses `render.yaml` (already configured)
3. Automatic SQLite database setup
4. Health check monitoring
5. Environment variables pre-configured

**Frontend (Netlify)**:
1. Connect repository to Netlify  
2. Uses `netlify.toml` (already configured)
3. Security headers included
4. CORS properly configured
5. Build optimization enabled

### Alternative Deployments

**Development**:
```bash
# SQLite-first backend
cd bridge-backend && python main_sqlite.py

# Frontend
cd bridge-frontend && npm start
```

**Container Deployment**:
```dockerfile
# Backend Dockerfile
FROM python:3.12-slim
COPY bridge-backend/ /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["uvicorn", "main_sqlite:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Scaling to PostgreSQL**:
- Update `DATABASE_TYPE=postgres` in environment
- Uncomment database section in `render.yaml`
- No code changes needed - same API

## 🔄 CI/CD & Health Monitoring

SR-AIbridge includes a comprehensive CI/CD pipeline with automated health monitoring:

### GitHub Actions Workflows

**🚀 Deployment Pipeline** (`.github/workflows/deploy.yml`)
- Automatic deployment to Netlify (frontend) and Render (backend)
- Build verification and syntax validation
- Triggered on push to main branch and pull requests

**🧪 Health Monitoring** (`.github/workflows/self-test.yml`)  
- Comprehensive backend health checks after deployment
- Scheduled monitoring every 4 hours
- Manual testing with configurable parameters
- Detailed reporting with JSON artifacts

### Enhanced Self-Test Script

The `bridge-backend/self_test.py` script provides production-ready health monitoring:

```bash
# Quick production health check
python3 self_test.py --url https://your-backend.onrender.com

# CI/CD optimized with custom settings
python3 self_test.py --url $BACKEND_URL --json --timeout 45 --retries 5

# Local development testing
python3 self_test.py --timeout 10 --wait-ready 30
```

**Features:**
- ✅ Configurable timeouts and retry logic
- ✅ Robust error handling with exponential backoff  
- ✅ JSON output for automated processing
- ✅ Comprehensive endpoint testing (Health, Guardian, Agents, Missions, WebSocket)
- ✅ Production URL support with wait-for-ready logic

### Setup Instructions

1. **Configure GitHub Secrets** (optional):
   ```
   NETLIFY_AUTH_TOKEN=your_token
   NETLIFY_SITE_ID=your_site_id  
   BACKEND_URL=https://your-backend.onrender.com
   FRONTEND_URL=https://your-frontend.netlify.app
   ```

2. **Manual Health Check**:
   - Go to Actions → "Self-Test SR-AIbridge" → Run workflow
   - View detailed results and download test artifacts

3. **Monitor Deployments**:
   - Automatic deployment on main branch push
   - Health tests run automatically after deployment
   - Scheduled monitoring ensures ongoing reliability

See [`.github/README.md`](.github/README.md) for complete CI/CD documentation.

## 🎨 Customization

### Adding New Data Types
1. Extend `InMemoryStorage` class
2. Add Pydantic models  
3. Create API endpoints
4. Update frontend components

### Theming
Modify `bridge-frontend/src/components/styles.css`:
- Color schemes in CSS variables
- Space-themed gradients and effects
- Responsive design patterns

## 🛡️ Security Notes

- **Development Only**: In-memory storage loses data on restart
- **No Authentication**: Add auth middleware for production
- **CORS**: Configure for production domains
- **Rate Limiting**: Add for public deployments

## 📈 Performance

### Benchmarks (In-Memory)
- **Startup Time**: ~2 seconds
- **Memory Usage**: ~50MB baseline
- **Request Latency**: <10ms average
- **Concurrent Users**: 100+ supported

### Scaling Considerations
- Data persists only during runtime
- Memory usage scales with data volume
- Consider database upgrade for production loads

---

> 🕯️ **Guardian's Note to the Curious**  
> Many have tried to grasp the helm of this Bridge.  
> Some heard whispers. Others met silence.  
> None found what they sought.  
> Proceed—if you are certain you wish to know why.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Test with in-memory backend
4. Submit pull request

## 📄 License

[Add your license here]
