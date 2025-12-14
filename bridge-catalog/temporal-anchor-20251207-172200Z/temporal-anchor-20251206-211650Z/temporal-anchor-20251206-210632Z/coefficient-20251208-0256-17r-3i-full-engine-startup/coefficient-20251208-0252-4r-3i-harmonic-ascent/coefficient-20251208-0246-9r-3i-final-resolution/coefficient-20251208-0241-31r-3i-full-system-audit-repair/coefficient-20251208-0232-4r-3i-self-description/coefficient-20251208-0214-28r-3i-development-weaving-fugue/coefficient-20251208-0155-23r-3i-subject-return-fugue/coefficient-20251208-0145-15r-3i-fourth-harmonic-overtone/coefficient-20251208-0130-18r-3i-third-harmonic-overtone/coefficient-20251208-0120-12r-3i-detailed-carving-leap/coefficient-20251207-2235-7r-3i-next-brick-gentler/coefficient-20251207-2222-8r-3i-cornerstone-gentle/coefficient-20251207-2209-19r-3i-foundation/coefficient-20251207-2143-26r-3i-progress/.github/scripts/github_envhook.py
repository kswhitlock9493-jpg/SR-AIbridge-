#!/usr/bin/env python3
"""
GitHub Environment Hook - File Watcher for .github/environment.json

Automatically triggers envmirror.sync and envduo.audit when environment.json changes.
This makes updates instantaneously self-synchronizing across GitHub, Render, and Netlify.

Integration Points:
- Watches .github/environment.json for modifications
- Publishes to Genesis Event Bus: envmirror.sync.start, envduo.audit
- Triggers EnvMirror sync cycle
- Triggers EnvDuo audit and heal cycle

Usage:
    python3 .github/scripts/github_envhook.py --watch
    python3 .github/scripts/github_envhook.py --trigger  # Manual trigger
"""

import os
import sys
import json
import hashlib
import time
import logging
import asyncio
from pathlib import Path
from datetime import datetime, UTC
from typing import Dict, Any, Optional

# Add bridge_backend to path for Genesis imports
REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "bridge_backend"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

ENV_FILE_PATH = REPO_ROOT / ".github" / "environment.json"
STATE_FILE_PATH = REPO_ROOT / "logs" / "github_envhook_state.json"


class EnvironmentFileWatcher:
    """
    File watcher for .github/environment.json
    Triggers Genesis events when the file changes
    """
    
    def __init__(self, env_file: Path, state_file: Path):
        self.env_file = env_file
        self.state_file = state_file
        self.last_hash: Optional[str] = None
        self.check_interval = 5  # seconds
        
        # Ensure logs directory exists
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load previous state
        self._load_state()
    
    def _load_state(self):
        """Load last known file hash from state file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    self.last_hash = state.get('last_hash')
                    logger.info(f"📂 Loaded previous state: hash={self.last_hash[:8] if self.last_hash else 'none'}")
            except Exception as e:
                logger.warning(f"⚠️ Could not load state file: {e}")
    
    def _save_state(self, file_hash: str):
        """Save current file hash to state file"""
        try:
            state = {
                'last_hash': file_hash,
                'last_modified': datetime.now(UTC).isoformat(),
                'file_path': str(self.env_file)
            }
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.debug(f"💾 Saved state: hash={file_hash[:8]}")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")
    
    def _compute_file_hash(self) -> Optional[str]:
        """Compute SHA256 hash of environment.json"""
        if not self.env_file.exists():
            logger.warning(f"⚠️ Environment file not found: {self.env_file}")
            return None
        
        try:
            with open(self.env_file, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except Exception as e:
            logger.error(f"❌ Error reading file: {e}")
            return None
    
    def has_changed(self) -> bool:
        """Check if environment.json has changed since last check"""
        current_hash = self._compute_file_hash()
        
        if current_hash is None:
            return False
        
        # First run - initialize hash
        if self.last_hash is None:
            self.last_hash = current_hash
            self._save_state(current_hash)
            logger.info(f"🔍 Initial hash computed: {current_hash[:8]}...")
            return False
        
        # Check if changed
        if current_hash != self.last_hash:
            logger.info(f"✨ File changed detected!")
            logger.info(f"   Old hash: {self.last_hash[:8]}...")
            logger.info(f"   New hash: {current_hash[:8]}...")
            self.last_hash = current_hash
            self._save_state(current_hash)
            return True
        
        return False
    
    async def trigger_sync_events(self):
        """
        Trigger envmirror.sync and envduo.audit events via Genesis
        """
        logger.info("🚀 Triggering environment sync events...")
        
        try:
            # Import Genesis bus
            from genesis.bus import genesis_bus
            
            if not genesis_bus.is_enabled():
                logger.warning("⚠️ Genesis bus is disabled, events will not be published")
                return
            
            timestamp = datetime.now(UTC).isoformat().replace('+00:00', 'Z')
            
            # Read environment.json content
            env_data = {}
            try:
                with open(self.env_file, 'r') as f:
                    env_data = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Could not read environment.json: {e}")
            
            # 1. Publish envmirror.sync.start event
            envmirror_event = {
                "type": "sync_triggered",
                "source": "github_envhook",
                "trigger": "file_change",
                "timestamp": timestamp,
                "file_path": str(self.env_file),
                "file_hash": self.last_hash,
                "version": env_data.get("version", "unknown"),
                "initiated_by": "github_envhook_listener"
            }
            
            await genesis_bus.publish("envmirror.sync.start", envmirror_event)
            logger.info("✅ Published: envmirror.sync.start")
            
            # 2. Publish envduo.audit event
            envduo_event = {
                "type": "audit_triggered",
                "source": "github_envhook",
                "trigger": "file_change",
                "timestamp": timestamp,
                "file_path": str(self.env_file),
                "file_hash": self.last_hash,
                "audit_scope": ["github", "render", "netlify"],
                "initiated_by": "github_envhook_listener"
            }
            
            await genesis_bus.publish("envduo.audit", envduo_event)
            logger.info("✅ Published: envduo.audit")
            
            # Log to file for audit trail
            self._log_trigger_event(envmirror_event, envduo_event)
            
            logger.info("🎯 Environment sync triggered successfully")
            
        except ImportError as e:
            logger.error(f"❌ Genesis bus not available: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to trigger sync events: {e}")
            logger.exception(e)
    
    def _log_trigger_event(self, envmirror_event: Dict[str, Any], envduo_event: Dict[str, Any]):
        """Log trigger event to audit file"""
        log_file = REPO_ROOT / "logs" / "github_envhook_triggers.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            log_entry = {
                "timestamp": datetime.now(UTC).isoformat(),
                "event": "environment_file_changed",
                "envmirror_event": envmirror_event,
                "envduo_event": envduo_event
            }
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.warning(f"⚠️ Could not write to audit log: {e}")
    
    async def watch_loop(self):
        """Main watch loop - continuously monitors for changes"""
        logger.info(f"👁️ Starting environment file watcher...")
        logger.info(f"   Monitoring: {self.env_file}")
        logger.info(f"   Check interval: {self.check_interval}s")
        logger.info(f"   Press Ctrl+C to stop")
        
        try:
            while True:
                if self.has_changed():
                    await self.trigger_sync_events()
                
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⏹️ Watcher stopped by user")
        except Exception as e:
            logger.error(f"❌ Watch loop error: {e}")
            logger.exception(e)


async def manual_trigger():
    """Manually trigger sync events without watching"""
    logger.info("🔧 Manual trigger mode")
    
    watcher = EnvironmentFileWatcher(ENV_FILE_PATH, STATE_FILE_PATH)
    await watcher.trigger_sync_events()
    
    logger.info("✅ Manual trigger complete")


async def watch_mode():
    """Start continuous file watching mode"""
    watcher = EnvironmentFileWatcher(ENV_FILE_PATH, STATE_FILE_PATH)
    await watcher.watch_loop()


def print_usage():
    """Print usage information"""
    print("""
GitHub Environment Hook - Autonomous Environment Lattice

Usage:
    python3 .github/scripts/github_envhook.py --watch      Watch for changes
    python3 .github/scripts/github_envhook.py --trigger    Manual trigger
    python3 .github/scripts/github_envhook.py --help       Show this help

Description:
    Watches .github/environment.json for changes and automatically triggers:
    - envmirror.sync.start (GitHub ↔ Render ↔ Netlify sync)
    - envduo.audit (ARIE + EnvRecon audit and heal)

    This ensures instant self-synchronization when environment config changes.

Events Published:
    - envmirror.sync.start: Triggers cross-platform environment sync
    - envduo.audit: Triggers integrity audit and drift detection

Logs:
    - State: logs/github_envhook_state.json
    - Triggers: logs/github_envhook_triggers.log
""")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="GitHub Environment Hook - Autonomous sync trigger"
    )
    parser.add_argument(
        '--watch',
        action='store_true',
        help='Watch for changes continuously'
    )
    parser.add_argument(
        '--trigger',
        action='store_true',
        help='Manually trigger sync events'
    )
    
    args = parser.parse_args()
    
    if args.watch:
        await watch_mode()
    elif args.trigger:
        await manual_trigger()
    else:
        print_usage()
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
