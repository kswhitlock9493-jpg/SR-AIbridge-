# SR-AIbridge Deployment Guide

> 📋 **New:** For detailed environment variable setup and Render/Netlify synchronization, see [ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md)

## SQLite-first Backend with Full Health Monitoring

This deployment guide covers the new SQLite-first backend implementation with comprehensive health checks and self-healing capabilities.

## Architecture Overview

- **Backend**: FastAPI with SQLite-first async database (can scale to PostgreSQL)
- **Frontend**: React with live health monitoring component
- **Database**: SQLite for development/simple deployments, PostgreSQL for production
- **Deployment**: Render (backend) + Netlify (frontend)

## Quick Start (Development)

### Backend
```bash
cd bridge_backend
pip install -r requirements.txt
python main_sqlite.py
```

The backend will start on `http://localhost:8000` with:
- SQLite database automatically initialized
- Default guardian created
- Health endpoints available

### Frontend  
```bash
cd bridge-frontend
npm install
npm start
```

Frontend starts on `http://localhost:3000` and connects to the backend.

## Health Monitoring Endpoints

### Basic Health Check
```
GET /health
```
Returns basic system status for load balancers.

### Full Health Check
```
GET /health/full
```
Returns comprehensive system health with component details.

### Self-Heal
```
POST /health/self-heal
```
Triggers automatic system repair and recovery.

### System Metrics
```
GET /system/metrics
```
Returns system performance metrics and record counts.

## Production Deployment

### Render (Backend)

1. **Connect Repository** to Render
2. **Use provided `render.yaml`** - already configured for SQLite-first deployment
3. **Environment Variables** (automatically set from render.yaml):
   - `DATABASE_TYPE=sqlite`
   - `DATABASE_URL=sqlite:///bridge.db` 
   - `CORS_ALLOW_ALL=false`
   - `ALLOWED_ORIGINS=https://bridge.netlify.app,https://sr-aibridge.netlify.app`

4. **Health Check**: Render will automatically monitor `/health` endpoint

#### Scaling to PostgreSQL (Optional)
To use PostgreSQL instead of SQLite:

1. Uncomment database section in `render.yaml`
2. Update environment variables:
   ```yaml
   - key: DATABASE_TYPE
     value: postgres
   - key: DATABASE_URL
     fromDatabase:
       name: sr-aibridge-db
       property: connectionString
   ```

### Netlify (Frontend)

1. **Connect Repository** to Netlify
2. **Build Settings** (automatically configured in `netlify.toml`):
   - Build directory: `bridge-frontend`
   - Build command: `npm run build`
   - Publish directory: `build`

3. **Environment Variables**:
   - `REACT_APP_API_URL=https://your-render-backend-url.onrender.com`
   - `NODE_VERSION=18`

4. **Security Headers**: Automatically applied via `netlify.toml`

## Health Monitoring Features

### SystemSelfTest Component

The frontend includes a comprehensive health monitoring component:

```jsx
import SystemSelfTest from './components/SystemSelfTest';

// Use in your main dashboard
<SystemSelfTest />
```

Features:
- **Live Health Status**: Auto-refreshes every 30 seconds
- **Visual Indicators**: Color-coded status indicators
- **Self-Test**: Manual system testing
- **Self-Repair**: One-click system recovery
- **Metrics Display**: Database counts and health scores

### Database Health Scoring

The system calculates health scores based on:
- Database connectivity (required)
- Guardian presence (20 points deducted if missing)
- Agent registration (10 points deducted if none)
- Response times and error rates

Health levels:
- **Healthy**: 80-100 points
- **Degraded**: 60-79 points  
- **Unhealthy**: <60 points

## Self-Healing Capabilities

The system can automatically recover from:

1. **Database Connection Issues**
   - Reinitializes database connection
   - Recreates tables if needed
   - Restores default guardian

2. **Missing System Components**
   - Creates default guardian if missing
   - Validates table structure
   - Cleans up orphaned records

3. **Configuration Problems**
   - Resets environment variables
   - Validates CORS settings
   - Checks endpoint availability

## Environment Configuration

### Development (.env)
```bash
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///bridge.db
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_ALL=false
DEBUG=true
PORT=8000
```

### Production (Render)
Environment variables are set automatically via `render.yaml`. Key settings:

```yaml
- key: DATABASE_TYPE
  value: sqlite
- key: CORS_ALLOW_ALL  
  value: false
- key: ALLOWED_ORIGINS
  value: https://bridge.netlify.app,https://sr-aibridge.netlify.app
```

## API Error Handling

All endpoints return safe, structured error responses:
```json
{
  "status": "error",
  "error": "Safe error message",
  "timestamp": "2024-01-01T00:00:00.000000",
  "self_heal_available": true
}
```

No internal exceptions or stack traces are exposed to clients.

## Monitoring and Observability

### Health Check Endpoints
- Use `/health` for load balancer health checks
- Use `/health/full` for detailed monitoring dashboards
- Use `/system/metrics` for performance monitoring

### Logging
- Structured JSON logging for production
- Comprehensive error tracking
- Health check and self-heal action logging

### Alerts
Set up monitoring alerts for:
- Health endpoint failures
- Self-heal activations
- Database connection issues
- API error rate increases

## Security

### CORS Configuration
- Whitelist specific origins for production
- Support for development localhost
- Netlify and Render subdomain support

### Headers
- Security headers automatically applied
- Content Security Policy configured
- XSS and clickjacking protection

### Database
- SQLite file permissions secured
- No direct database access exposed
- Prepared statements prevent injection

## Troubleshooting

### Backend Won't Start
1. Check Python version (3.12+ required)
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Check database permissions
4. Review startup logs for specific errors

### Health Checks Failing
1. Try manual self-heal: `POST /health/self-heal`
2. Check database file permissions
3. Verify environment variables
4. Review application logs

### Frontend Can't Connect
1. Verify backend is running and accessible
2. Check CORS configuration
3. Confirm API URL in frontend config
4. Test health endpoints directly

### Database Issues
1. SQLite file corruption: Delete `bridge.db` and restart
2. Permission issues: Check file system permissions
3. Connection timeouts: Increase timeout in db.py
4. Migration needed: Self-heal will recreate tables

## Performance Tuning

### SQLite Optimization
- Connection pooling enabled
- WAL mode for better concurrency
- Prepared statements for queries
- Automatic vacuum maintenance

### API Performance
- Async operations throughout
- Connection reuse
- Error response caching
- Health check result caching

### Frontend Optimization
- Component-level error boundaries
- Efficient re-rendering with state management
- Auto-refresh with backoff on errors
- Responsive design for mobile

## Auto-Deploy & Continuous Monitoring (v1.6.7)

### Bridge Auto-Deploy Workflow

SR-AIbridge v1.6.7 introduces autonomous deployment management:

**Workflow File:** `.github/workflows/bridge_autodeploy.yml`

**Features:**
- 🔄 **Automatic Redeploys**: Every 6 hours
- 🏥 **Health Checks**: Backend verification before deployment
- 📊 **Live Status Badge**: Real-time Render↔Netlify sync monitoring
- 🔧 **Self-Healing**: Automatic recovery from drift

**Workflow Steps:**

1. **Setup** - Checkout code, install Node 22, install dependencies
2. **Build** - Compile frontend with Vite
3. **Verify Backend** - Check Render health endpoint
4. **Generate Badge** - Create sync status badge
5. **Deploy** - Push to Netlify production
6. **Report** - Log event to diagnostics system

**Trigger Methods:**

```bash
# Automatic triggers:
- Push to main branch
- Cron schedule: 0 */6 * * * (every 6 hours)

# Manual trigger:
- GitHub Actions UI → Bridge Auto-Deploy Mode → Run workflow
```

### Live Sync Badge

Monitor system health in real-time via the Bridge Sync Badge:

**Badge Display:**
- 🟢 **STABLE**: Both platforms healthy
- 🟡 **PARTIAL**: One platform down
- 🔴 **DRIFT**: Both platforms experiencing issues

**Badge is automatically updated:**
- Every 6 hours via auto-deploy workflow
- On each push to main
- When manually triggered

**View badge at:** `https://sr-aibridge.netlify.app/bridge_sync_badge.json`

### Package & Registry Configuration (v1.6.7)

**Updated Dependencies:**

```json
{
  "devDependencies": {
    "@netlify/functions": "^2.8.2",
    "@netlify/plugin-lighthouse": "^4.1.0"
  }
}
```

**Registry Fallback (`.npmrc`):**

```ini
registry=https://registry.npmjs.org/
@netlify:registry=https://registry.npmjs.org/
always-auth=false
legacy-peer-deps=true
```

This configuration:
- Prevents 404 errors from deprecated packages
- Ensures build stability across environments
- Supports Node 22+ with legacy peer dependency handling

### Deployment Secrets Required

Ensure these secrets are configured in GitHub repository settings:

| Secret | Purpose |
|--------|---------|
| `NETLIFY_AUTH_TOKEN` | Netlify deployment authentication |
| `NETLIFY_SITE_ID` | Target Netlify site identifier |

**To configure:**
1. Go to repository Settings → Secrets and variables → Actions
2. Add `NETLIFY_AUTH_TOKEN` (from Netlify Personal Access Tokens)
3. Add `NETLIFY_SITE_ID` (from Netlify Site Settings)

## Support

For issues and questions:
1. Check health endpoints first
2. Try self-heal functionality
3. Review application logs
4. Check deployment configurations
5. Verify environment variables
6. **NEW:** Check Bridge Sync Badge status
7. **NEW:** Review auto-deploy workflow runs

The system is designed to be self-healing and should automatically recover from most common issues.