# SR-AIbridge Deployment Guide

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

## Support

For issues and questions:
1. Check health endpoints first
2. Try self-heal functionality
3. Review application logs
4. Check deployment configurations
5. Verify environment variables

The system is designed to be self-healing and should automatically recover from most common issues.