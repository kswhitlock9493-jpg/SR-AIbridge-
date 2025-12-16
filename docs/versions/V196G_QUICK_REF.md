# V196G Quick Reference

## SR-AIbridge v1.9.6g Predictive Stabilizer — Quick Reference

### 🎯 What Changed

The stabilizer now **learns** instead of **reacting**. It observes patterns, builds adaptive thresholds, and only raises tickets when truly necessary.

---

### 🔍 Key Features at a Glance

| Feature | What It Does | Benefit |
|---------|-------------|---------|
| **Dynamic Thresholds** | Calculates mean + 2σ from last 10 boot cycles | No more false latency alerts |
| **Silent Learning** | Waits for 3 consecutive events before logging | Eliminates noise from one-off glitches |
| **Environment Awareness** | Detects Render/Netlify/local context | Suppresses pre-deploy sandbox noise |
| **Daily Reports** | Aggregates metrics to single daily file | Clean diagnostics directory |
| **Auto-Archive** | Moves tickets >5 days to archive/ | Prevents filesystem clutter |
| **Adaptive Healing** | Auto-tunes port bind delays | Self-optimizing startup performance |

---

### 📊 Expected Behavior

#### During Startup (Good)
```
[BOOT] PORT resolved in 0.12s -> 10000
[BOOT] Adaptive port bind: success in 2.98s
[STABILIZER] Startup latency 2.98s (within adaptive tolerance of 3.45s)
[HEARTBEAT] ✅ Live (initialized in 3.20s)
[DB] Schema sync completed in 0.84s
```

**Result:** No ticket created. Latency is within learned baseline.

#### During Startup (Learning)
```
[BOOT] Adaptive port bind: success in 2.51s
[STABILIZER] Startup latency 2.51s (learning baseline)
```

**Result:** No ticket created. Building baseline (need 3+ boot cycles).

#### Pattern Detection (Silent)
```
[STABILIZER] Anomaly queued (silent): startup_latency (1 events)
[STABILIZER] Anomaly queued (silent): startup_latency (2 events)
[STABILIZER] Pattern confirmed: startup_latency (3 events)
```

**Result:** Ticket created only after 3 consecutive events confirm the pattern.

---

### 🗂️ File Locations

| Path | Purpose | Auto-Managed |
|------|---------|--------------|
| `bridge_backend/diagnostics/boot_history.json` | Last 10 boot cycles | Yes, auto-trimmed |
| `bridge_backend/diagnostics/daily_reports/` | Daily aggregated summaries | Yes, one file per day |
| `bridge_backend/diagnostics/stabilization_tickets/` | Active tickets only | Yes, cleaned after 5 days |
| `bridge_backend/diagnostics/archive/diagnostics/` | Archived old tickets | Yes, auto-populated |

**All these files are gitignored** — they're runtime artifacts only.

---

### 🧪 Environment Variables

| Variable | Purpose | Set By | Example |
|----------|---------|--------|---------|
| `HEARTBEAT_INITIALIZED` | Marks bridge as "live" | Startup watchdog | `"1"` |
| `ADAPTIVE_PREBIND_DELAY` | Auto-tuned port wait time | Predictive stabilizer | `"3.2"` |
| `PORT` | Render's assigned port | Render | `"10000"` |
| `RENDER_EXTERNAL_URL` | Render deployment URL | Render | `"https://sr-aibridge.onrender.com"` |

---

### 📈 How Adaptive Thresholds Work

1. **First 3 Boot Cycles:** Learning baseline
   - Records startup latency each boot
   - No tickets created, just observation
   
2. **After 3 Boot Cycles:** Calculates threshold
   - Threshold = Mean + (2 × Standard Deviation)
   - Example: If boots took [2.0s, 2.1s, 2.2s]:
     - Mean = 2.1s
     - Stdev = 0.1s
     - Threshold = 2.1 + (2 × 0.1) = **2.3s**
   
3. **Ongoing:** Adaptive tolerance
   - Boots under 2.3s: ✅ Normal
   - Boots over 2.3s: ⚠️ Queued (need 3 to confirm)
   - Pattern confirmed: 🎫 Ticket created

---

### 🔧 Integration Points

#### In Your Startup Code
```python
from bridge_backend.runtime.startup_watchdog import watchdog

# Mark milestones
watchdog.mark_port_resolved(port)
watchdog.mark_bind_confirmed()
watchdog.mark_heartbeat_initialized()
watchdog.mark_db_synced()

# Finalize boot
watchdog.finalize_boot()
```

#### Manual Cleanup (Optional)
```python
from bridge_backend.runtime.predictive_stabilizer import archive_old_tickets

# Archive tickets older than 5 days
archive_old_tickets()
```

---

### 🎓 Pro Tips

1. **Don't delete boot_history.json** — it's the stabilizer's memory
2. **Check daily_reports/** for trends over time
3. **Adaptive delays improve over ~5 boots** — give it time to learn
4. **Single anomaly = silent queue** — pattern needs confirmation
5. **Pre-deploy logs are suppressed** — less noise in build phase

---

### 🚨 Troubleshooting

**Q: I'm getting too many tickets**  
**A:** Check if you have 3+ boots in `boot_history.json`. If not, stabilizer is still learning.

**Q: Tickets aren't being archived**  
**A:** Ensure tickets follow naming pattern `YYYYMMDDTHHMMSSz_*.md`

**Q: Daily reports aren't generating**  
**A:** Call `watchdog.finalize_boot()` at end of startup sequence

**Q: Adaptive delay not changing**  
**A:** Pattern needs 3 consecutive high-latency boots to trigger auto-tune

---

### 📚 Related Documentation

- Full Implementation: `V196G_IMPLEMENTATION.md`
- Test Suite: `tests/test_v196g_features.py`
- Previous Version: `V196F_IMPLEMENTATION.md`

---

**Built with ❤️ for adaptive silence and smart observability.**
