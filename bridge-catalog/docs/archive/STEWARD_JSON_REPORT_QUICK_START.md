# 🎯 Quick Answer: Environment Drift JSON Report

## What You Asked For

> "run the envelope steward engine ideally in with mode but being you probably can't do that yet lol read is fine that way I have a json for all the environments of what's missing and I'll fix it lol"

## ✅ Done!

Steward now runs in **read-only mode** and gives you a **complete JSON report** of what environment variables are missing in each platform (Render, Netlify, GitHub).

## 🚀 How to Use It

### Method 1: Quick Script (Easiest)

```bash
# Enable Steward
export STEWARD_ENABLED=true
export STEWARD_OWNER_HANDLE=kswhitlock9493-jpg

# Get the JSON report
python3 get_env_drift.py > my_drift_report.json
```

That's it! You now have a JSON file showing:
- What's missing in Render
- What's missing in Netlify  
- What's missing in GitHub

### Method 2: Via API

If you're running the server:

```bash
curl -X POST "http://localhost:8000/api/steward/diff?providers=render,netlify,github&dry_run=true" \
  > drift_report.json
```

## 📄 What You Get

Example JSON output:

```json
{
  "has_drift": true,
  "providers": ["render", "netlify", "github"],
  "missing_in_render": [
    "SECRET_KEY",
    "DATABASE_URL",
    "API_KEY",
    "BRIDGE_API_URL",
    "..."
  ],
  "missing_in_netlify": [
    "SECRET_KEY",
    "DATABASE_URL",
    "..."
  ],
  "missing_in_github": [
    "API_KEY",
    "..."
  ],
  "summary": {
    "total_keys": 16,
    "local_count": 16,
    "render_count": 13,
    "netlify_count": 14,
    "github_count": 15
  }
}
```

## 🔍 What It Does

1. **Reads your local .env files** to see what variables you have
2. **Checks Render, Netlify, and GitHub** to see what they have (if API credentials are configured)
3. **Compares everything** and shows you exactly what's missing where
4. **Outputs JSON** so you can parse it, pipe it, or use it however you want

## 📝 Note About API Credentials

- **Without credentials**: The report will show 0 variables for that platform and list all local variables as missing
- **With credentials**: The report will show actual drift by comparing live data

To add credentials (optional):

```bash
# For Render
export RENDER_API_KEY=your_key
export RENDER_SERVICE_ID=your_service_id

# For Netlify
export NETLIFY_AUTH_TOKEN=your_token
export NETLIFY_SITE_ID=your_site_id

# For GitHub
export GITHUB_TOKEN=your_token
export GITHUB_REPO=owner/repo
```

## 🛡️ Safety

- **Read-only mode**: Nothing is changed, just reported
- **Admiral-only**: Only you (the owner) can run this
- **No secrets exposed**: Secret values are masked in the output
- **Genesis events**: All operations are logged to the audit trail

## 📚 More Info

- [STEWARD_ENVRECON_INTEGRATION.md](STEWARD_ENVRECON_INTEGRATION.md) - Full integration details
- [STEWARD_QUICK_REF.md](STEWARD_QUICK_REF.md) - Complete API reference
- [V196L_STEWARD_SUMMARY.md](V196L_STEWARD_SUMMARY.md) - Implementation summary

## 🎉 You're All Set!

You can now get a JSON report of your environment drift whenever you want. Use it to:
- See what's missing across platforms
- Fix things manually through dashboards
- Track changes over time
- Eventually: Use Steward's write mode to auto-sync (when you're ready)

**Built with ❤️ by GitHub Copilot for kswhitlock9493-jpg 🚀**
