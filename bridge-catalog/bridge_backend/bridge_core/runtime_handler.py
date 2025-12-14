"""
Bridge Runtime Handler - Sovereign Runtime Core (SRC)
Integration with Forge Dominion for ephemeral token management
"""

import os
import yaml
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import hashlib
import hmac
import base64

# Import secret forge for sovereign secret retrieval
try:
    from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
except ImportError:
    # Fallback if module not available
    def retrieve_environment(key: str, default=None):
        return os.getenv(key, default)

logger = logging.getLogger(__name__)


class RuntimeManifest:
    """Parses and validates bridge.runtime.yaml"""
    
    def __init__(self, manifest_path: str):
        self.manifest_path = Path(manifest_path)
        self.config: Dict[str, Any] = {}
        self.schema_path = Path(__file__).parent.parent.parent / "src" / "manifest.json"
        
    def load(self) -> Dict[str, Any]:
        """Load and parse the runtime manifest"""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Runtime manifest not found: {self.manifest_path}")
        
        with open(self.manifest_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        logger.info(f"Loaded runtime manifest: {self.manifest_path}")
        return self.config
    
    def validate(self) -> bool:
        """Validate manifest against schema"""
        if not self.schema_path.exists():
            logger.warning(f"Schema not found: {self.schema_path}, skipping validation")
            return True
        
        # TODO: Implement jsonschema validation
        # For now, basic validation
        required_keys = ['version', 'runtime', 'security']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required key: {key}")
        
        logger.info("Runtime manifest validation passed")
        return True
    
    def get_auth_config(self) -> Dict[str, Any]:
        """Get authentication configuration"""
        return self.config.get('runtime', {}).get('auth', {})
    
    def get_containers(self) -> List[Dict[str, Any]]:
        """Get container configurations"""
        return self.config.get('runtime', {}).get('containers', [])
    
    def get_federation_config(self) -> Dict[str, Any]:
        """Get federation configuration"""
        return self.config.get('runtime', {}).get('federation', {})


class ForgeRuntimeAuthority:
    """Forge Dominion integration for runtime authentication"""
    
    def __init__(self):
        self.root_key = self._get_root_key()
        
    def _get_root_key(self) -> bytes:
        """Get the Forge Dominion root key"""
        # Use forge to retrieve environment variable
        root_key_str = retrieve_environment("FORGE_DOMINION_ROOT")
        if not root_key_str:
            raise ValueError("FORGE_DOMINION_ROOT environment variable not set")
        
        # Decode base64url encoded key
        try:
            return base64.urlsafe_b64decode(root_key_str + '==')
        except Exception as e:
            raise ValueError(f"Invalid FORGE_DOMINION_ROOT format: {e}")
    
    def generate_runtime_token(
        self, 
        node_id: str, 
        scope: str = "runtime:execute",
        ttl_seconds: int = 3600
    ) -> Dict[str, Any]:
        """Generate an ephemeral runtime token"""
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=ttl_seconds)
        
        token_data = {
            "node_id": node_id,
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "scope": scope
        }
        
        # Create HMAC signature
        payload = f"{node_id}:{scope}:{int(now.timestamp())}:{int(expires_at.timestamp())}"
        signature = hmac.new(
            self.root_key,
            payload.encode(),
            hashlib.sha256
        ).digest()
        
        token_data["signature"] = base64.urlsafe_b64encode(signature).decode().rstrip('=')
        
        logger.info(f"Generated runtime token for node: {node_id}")
        return token_data
    
    def validate_token(self, token: Dict[str, Any]) -> bool:
        """Validate a runtime token"""
        # Check expiration
        expires_at = datetime.fromisoformat(token["expires_at"])
        if datetime.utcnow() > expires_at:
            logger.warning(f"Token expired at {expires_at}")
            return False
        
        # Verify signature
        issued_at = datetime.fromisoformat(token["issued_at"])
        payload = (
            f"{token['node_id']}:{token['scope']}:"
            f"{int(issued_at.timestamp())}:{int(expires_at.timestamp())}"
        )
        
        expected_sig = hmac.new(
            self.root_key,
            payload.encode(),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode().rstrip('=')
        
        if token["signature"] != expected_sig_b64:
            logger.error("Token signature validation failed")
            return False
        
        logger.info(f"Token validated for node: {token['node_id']}")
        return True
    
    def renew_token(self, old_token: Dict[str, Any], ttl_seconds: int = 3600) -> Dict[str, Any]:
        """Renew an existing token"""
        if not self.validate_token(old_token):
            raise ValueError("Cannot renew invalid token")
        
        return self.generate_runtime_token(
            old_token["node_id"],
            old_token["scope"],
            ttl_seconds
        )


class SovereignRuntimeCore:
    """Main runtime handler - manages container lifecycle and federation"""
    
    def __init__(self, manifest_path: str):
        self.manifest = RuntimeManifest(manifest_path)
        self.auth = ForgeRuntimeAuthority()
        self.running_containers: Dict[str, Any] = {}
        self.node_id = self._generate_node_id()
        self.runtime_token: Optional[Dict[str, Any]] = None
        
    def _generate_node_id(self) -> str:
        """Generate unique node ID"""
        import socket
        hostname = socket.gethostname()
        timestamp = datetime.utcnow().isoformat()
        node_hash = hashlib.sha256(f"{hostname}:{timestamp}".encode()).hexdigest()[:12]
        return f"bridge-runtime-{node_hash}"
    
    async def initialize(self):
        """Initialize the runtime core"""
        logger.info(f"Initializing Sovereign Runtime Core: {self.node_id}")
        
        # Load and validate manifest
        self.manifest.load()
        self.manifest.validate()
        
        # Get runtime token
        auth_config = self.manifest.get_auth_config()
        ttl = auth_config.get('token_ttl', 3600)
        self.runtime_token = self.auth.generate_runtime_token(self.node_id, ttl_seconds=ttl)
        
        # Save token for runtime use
        token_path = Path("/tmp/forge_runtime_token.json")
        with open(token_path, 'w') as f:
            json.dump(self.runtime_token, f, indent=2)
        
        logger.info(f"Runtime initialized with token (expires: {self.runtime_token['expires_at']})")
    
    async def start_containers(self):
        """Start all containers defined in manifest"""
        containers = self.manifest.get_containers()
        
        for container_config in containers:
            container_name = container_config['name']
            logger.info(f"Starting container: {container_name}")
            
            # TODO: Implement actual container spawning
            # This would use Docker SDK, Firecracker, or similar
            self.running_containers[container_name] = {
                'config': container_config,
                'status': 'running',
                'started_at': datetime.utcnow().isoformat()
            }
        
        logger.info(f"Started {len(containers)} containers")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all containers"""
        health_status = {
            'node_id': self.node_id,
            'timestamp': datetime.utcnow().isoformat(),
            'token_valid': self.auth.validate_token(self.runtime_token) if self.runtime_token else False,
            'containers': {}
        }
        
        for name, container in self.running_containers.items():
            # TODO: Implement actual health checks
            health_status['containers'][name] = {
                'status': container['status'],
                'uptime': container['started_at']
            }
        
        return health_status
    
    async def renew_token_if_needed(self):
        """Auto-renew token if nearing expiration"""
        if not self.runtime_token:
            return
        
        expires_at = datetime.fromisoformat(self.runtime_token['expires_at'])
        time_remaining = (expires_at - datetime.utcnow()).total_seconds()
        
        # Renew if less than 5 minutes remaining
        if time_remaining < 300:
            logger.info("Token nearing expiration, renewing...")
            auth_config = self.manifest.get_auth_config()
            ttl = auth_config.get('token_ttl', 3600)
            self.runtime_token = self.auth.renew_token(self.runtime_token, ttl)
            
            # Save renewed token
            token_path = Path("/tmp/forge_runtime_token.json")
            with open(token_path, 'w') as f:
                json.dump(self.runtime_token, f, indent=2)
            
            logger.info("Token renewed successfully")
    
    async def shutdown(self):
        """Graceful shutdown of all containers"""
        logger.info("Shutting down runtime...")
        
        for name in list(self.running_containers.keys()):
            logger.info(f"Stopping container: {name}")
            # TODO: Implement actual container shutdown
            del self.running_containers[name]
        
        logger.info("Runtime shutdown complete")
    
    async def run(self):
        """Main runtime loop"""
        await self.initialize()
        await self.start_containers()
        
        try:
            while True:
                # Periodic tasks
                await self.renew_token_if_needed()
                health = await self.health_check()
                logger.debug(f"Health check: {health}")
                
                # Wait before next iteration
                await asyncio.sleep(30)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            await self.shutdown()


async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    manifest_path = os.getenv('BRIDGE_RUNTIME_MANIFEST', 'src/bridge.runtime.yaml')
    runtime = SovereignRuntimeCore(manifest_path)
    
    await runtime.run()


if __name__ == "__main__":
    asyncio.run(main())
