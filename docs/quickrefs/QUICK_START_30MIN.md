# Quick Start Guide: SR-AIbridge in 30 Minutes
## Ultra-Fast Setup for Experienced Developers

> **Purpose**: Get SR-AIbridge running in 30 minutes or less. This assumes you're familiar with Python/Node.js and just need the commands.

---

## ⚡ Prerequisites (2 minutes)

```bash
# Verify versions
python --version   # Must be 3.12+
node --version     # Must be 18+
git --version      # Any recent version

# Clone repository
git clone https://github.com/kswhitlock9493-jpg/SR-AIbridge-.git
cd SR-AIbridge-
```

---

## 🐍 Backend Setup (10 minutes)

### 1. Install Dependencies (3 minutes)
```bash
cd bridge_backend
pip install -r requirements.txt
```

### 2. Configure Environment (1 minute)
```bash
# Copy example or create .env
cat > .env << 'EOF'
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///bridge.db
HOST=0.0.0.0
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
ENABLE_ENGINES=true
LOG_LEVEL=INFO
EOF
```

### 3. Start Backend (1 minute)
```bash
python main.py
# Backend running on http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Verify Backend (1 minute)
```bash
# In new terminal
curl http://localhost:8000/health
curl http://localhost:8000/health/full
curl http://localhost:8000/docs  # Interactive API docs
```

---

## ⚛️ Frontend Setup (10 minutes)

### 1. Install Dependencies (4 minutes)
```bash
cd bridge-frontend
npm install
```

### 2. Configure Environment (1 minute)
```bash
# Copy example or create .env
cat > .env << 'EOF'
VITE_API_BASE=http://localhost:8000
VITE_WS_BASE=ws://localhost:8000
EOF
```

### 3. Start Frontend (1 minute)
```bash
npm run dev
# Frontend running on http://localhost:5173
```

### 4. Verify Frontend (1 minute)
- Open http://localhost:5173 in browser
- Should see SR-AIbridge dashboard
- Health status should be green
- System stats should display

---

## 🎮 Load Demo Data (5 minutes)

```bash
cd bridge_backend
python seed.py
```

This creates:
- 5 sample agents
- 10 demo missions  
- Sample vault logs
- Fleet data
- Default guardian

Refresh frontend to see demo data.

---

## 🧪 Smoke Test (3 minutes)

### Test All Endpoints
```bash
cd SR-AIbridge-
python test_endpoints_full.py
```

### Test Engines
```bash
./smoke_test_engines.sh
```

### Manual API Tests
```bash
# Create agent
curl -X POST http://localhost:8000/agents \
  -H "Content-Type: application/json" \
  -d '{"name": "Quick Agent", "role": "agent"}'

# Create mission
curl -X POST http://localhost:8000/missions \
  -H "Content-Type: application/json" \
  -d '{"title": "Quick Mission", "captain": "Admiral", "role": "captain"}'

# List agents
curl http://localhost:8000/agents

# List missions
curl http://localhost:8000/missions
```

---

## 🎯 Key URLs

Once running, access these:

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | Main dashboard |
| Backend | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Interactive API testing |
| Health | http://localhost:8000/health/full | System status |
| WebSocket | ws://localhost:8000/ws/stats | Real-time updates |

---

## 🚀 Production Deploy (Bonus - 10 minutes)

### Deploy Frontend to Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd bridge-frontend
npm run build
netlify deploy --prod --dir=dist
```

### Deploy Backend to Render

1. Go to https://render.com
2. Create new Web Service
3. Connect GitHub repo
4. Render auto-detects `infra/render.yaml`
5. Click "Create Web Service"
6. Wait ~5 minutes for deployment

### Update Frontend Config

```bash
# Update .env with production backend URL
VITE_API_BASE=https://your-backend.onrender.com
```

Rebuild and redeploy frontend.

---

## 🔧 Common Commands Reference

### Backend
```bash
# Start server
python main.py

# Run with auto-reload (development)
uvicorn main:app --reload

# Different port
uvicorn main:app --port 8001

# Check logs
tail -f logs/app.log
```

### Frontend
```bash
# Development server
npm run dev

# Production build
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Database
```bash
# Reset database (SQLite)
rm bridge.db
python main.py  # Auto-creates new database

# PostgreSQL migration (production)
psql $DATABASE_URL -f init.sql
```

### Testing
```bash
# Full endpoint test
python test_endpoints_full.py

# Engine smoke test
./smoke_test_engines.sh

# Backend tests
pytest bridge_backend/tests/

# Frontend tests
cd bridge-frontend && npm test
```

---

## 🎓 Next Steps After Setup

### Explore the System
1. Visit dashboard: http://localhost:5173
2. Check API docs: http://localhost:8000/docs
3. Review system health: `/health/full`
4. Create test agents and missions

### Read Documentation
1. `README.md` - Complete overview
2. `MASTER_ROADMAP.md` - System navigation
3. `SYSTEM_BLUEPRINT.md` - Technical details
4. `DEPLOYMENT.md` - Production deployment

### Customize
1. Add custom engines
2. Configure autonomy rules
3. Set up CI/CD
4. Add authentication
5. Scale to PostgreSQL

---

## 🚨 Quick Troubleshooting

### Backend Issues
```bash
# Port in use
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it

# Module not found
pip install -r requirements.txt --force-reinstall

# Database locked
rm bridge.db
python main.py
```

### Frontend Issues
```bash
# Build fails
rm -rf node_modules package-lock.json
npm install

# Port in use
# Vite will auto-increment (5173 → 5174)

# Can't connect to backend
# Check CORS in backend .env
# Verify backend is running
curl http://localhost:8000/health
```

### CORS Errors
```bash
# Add frontend URL to backend .env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 📊 What You Have Now

After 30 minutes, you should have:

✅ **Backend Running**
- FastAPI server on port 8000
- SQLite database initialized
- Default guardian created
- All core endpoints active
- Interactive API docs available

✅ **Frontend Running**  
- React app on port 5173
- Real-time dashboard
- WebSocket connection active
- Health monitoring working

✅ **Demo Data Loaded**
- 5+ sample agents
- 10+ demo missions
- System logs
- Fleet data

✅ **Core Features Working**
- Agent management
- Mission control
- Health monitoring
- Real-time updates
- API documentation

---

## 🎯 Performance Expectations

With default SQLite setup:

- **Backend startup**: ~2 seconds
- **Frontend build**: ~10 seconds  
- **API response time**: <10ms (local)
- **WebSocket latency**: <5ms (local)
- **Memory usage**: ~150MB total
- **Disk usage**: ~50MB

---

## 🔐 Security Notes

**Development setup** (current):
- No authentication
- CORS allows localhost
- SQLite database (file-based)
- Debug logging enabled

**For production**, you need:
- JWT or OAuth2 authentication
- Restricted CORS origins
- PostgreSQL database
- HTTPS/TLS encryption
- Environment secrets management

See `SECURITY.md` for production security guide.

---

## 📞 Getting Help

If stuck:

1. **Check logs**: Backend terminal output
2. **Test health**: `curl http://localhost:8000/health/full`
3. **Try self-heal**: `curl -X POST http://localhost:8000/health/self-heal`
4. **Review docs**: `README.md`, `TROUBLESHOOTING` section
5. **GitHub Issues**: Search or create issue

---

## 🎉 Success Checklist

- [ ] Backend responds to `/health`
- [ ] Frontend loads in browser
- [ ] Dashboard shows system stats
- [ ] Can create agents via API
- [ ] Can create missions via API
- [ ] WebSocket updates work
- [ ] Interactive API docs accessible
- [ ] Demo data loaded successfully
- [ ] All smoke tests pass

---

## 🚀 You're Ready!

Congratulations! You now have a fully functional SR-AIbridge instance.

**Time taken**: ~30 minutes  
**Status**: Operational ✅  
**Next**: Explore, customize, deploy!

---

## 📖 Quick Reference Links

- **Main README**: `/README.md`
- **Architecture**: `/SYSTEM_BLUEPRINT.md`
- **Full Build Guide**: `/BUILD_DOSSIER.md`
- **Navigation Guide**: `/MASTER_ROADMAP.md`
- **API Docs**: `http://localhost:8000/docs`
- **Deployment**: `/DEPLOYMENT.md`
- **Security**: `/SECURITY.md`

---

**From clone to command in 30 minutes. Welcome to the bridge, Admiral.** 🌉

*Gold ripple eternal.*
