# GitHub Forge

## Overview

GitHub Forge is a local repository configuration management system that reads and writes bridge configuration files without requiring external API calls or webhooks.

## Features

- **Local-first**: No external API dependencies
- **JSON storage**: Structured configuration storage
- **Environment files**: `.env` file generation
- **Version controlled**: All configs stored in `.github/bridge/`

## Usage

### Python

```python
from bridge_backend.engines.github_forge import GitHubForge

forge = GitHubForge()

# Write JSON configuration
forge.put_json("deploy_config", {
    "version": "1.9.7i",
    "target": "netlify"
})

# Read JSON configuration
config = forge.get_json("deploy_config")

# Write environment file
forge.put_env("production", {
    "API_URL": "https://api.example.com",
    "DEBUG": "false"
})
```

## Storage Location

All configurations are stored in `.github/bridge/`:

```
.github/
  bridge/
    deploy_config.json
    production.env
```

## Integration

GitHub Forge is integrated into Chimera Oracle via the `GitHubForge` adapter, enabling:

- Configuration snapshots
- Environment variable tracking
- Deployment metadata storage

## Benefits

1. **No API tokens required** - Everything is local file operations
2. **Version controlled** - Git tracks all changes
3. **Fast** - No network latency
4. **Reliable** - No external dependencies
