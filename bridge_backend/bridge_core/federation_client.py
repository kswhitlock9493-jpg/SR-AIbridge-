"""
Federation Client - Cross-bridge task forwarding and heartbeat signaling
Enables communication and coordination between multiple SR-AIbridge instances
"""

import asyncio
import logging
import json
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


class BridgeStatus(Enum):
    """Status of bridge nodes in federation"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class TaskPriority(Enum):
    """Priority levels for federated tasks"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BridgeNode:
    """Represents a bridge node in the federation"""
    node_id: str
    name: str
    endpoint: str
    status: BridgeStatus
    last_heartbeat: datetime
    capabilities: List[str]
    load_score: float  # 0.0 to 1.0, lower is better
    version: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['status'] = self.status.value
        result['last_heartbeat'] = self.last_heartbeat.isoformat()
        return result


@dataclass
class FederatedTask:
    """Task that can be forwarded between bridges"""
    task_id: str
    task_type: str
    priority: TaskPriority
    payload: Dict[str, Any]
    source_bridge: str
    target_bridge: Optional[str]
    created_at: datetime
    deadline: Optional[datetime]
    attempts: int
    max_attempts: int
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['priority'] = self.priority.value
        result['created_at'] = self.created_at.isoformat()
        result['deadline'] = self.deadline.isoformat() if self.deadline else None
        return result


@dataclass
class HeartbeatSignal:
    """Heartbeat signal between bridge nodes"""
    node_id: str
    timestamp: datetime
    status: BridgeStatus
    load_score: float
    active_tasks: int
    capabilities: List[str]
    metadata: Dict[str, Any]


class FederationClient:
    """
    Federation client for cross-bridge communication
    Handles task forwarding, heartbeat signaling, and node discovery
    """
    
    def __init__(self, node_id: str, node_name: str, endpoint: str):
        """
        Initialize Federation Client
        
        Args:
            node_id: Unique identifier for this bridge node
            node_name: Human-readable name for this node
            endpoint: HTTP endpoint for this node
        """
        self.node_id = node_id
        self.node_name = node_name
        self.endpoint = endpoint
        self.bridge_nodes: Dict[str, BridgeNode] = {}
        self.pending_tasks: Dict[str, FederatedTask] = {}
        self.completed_tasks: Dict[str, FederatedTask] = {}
        self.task_handlers: Dict[str, Callable] = {}
        
        # Federation settings
        self.heartbeat_interval = 30  # seconds
        self.node_timeout = 120  # seconds
        self.max_task_attempts = 3
        self.federation_enabled = False
        
        # Statistics
        self.stats = {
            'heartbeats_sent': 0,
            'heartbeats_received': 0,
            'tasks_forwarded': 0,
            'tasks_received': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'federation_uptime': datetime.utcnow(),
            'last_discovery': None
        }
        
        # HTTP session for federation communication
        self.session: Optional[aiohttp.ClientSession] = None
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        logger.info(f"🌐 FederationClient initialized for node {node_id} ({node_name})")
    
    async def start_federation(self, known_bridges: List[str] = None):
        """
        Start federation services
        
        Args:
            known_bridges: List of known bridge endpoints to connect to
        """
        if self.federation_enabled:
            logger.warning("⚠️ Federation already running")
            return
        
        self.federation_enabled = True
        
        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
        # Start heartbeat task
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        # Discover known bridges
        if known_bridges:
            await self._discover_bridges(known_bridges)
        
        logger.info("🚀 Federation services started")
    
    async def stop_federation(self):
        """Stop federation services"""
        if not self.federation_enabled:
            return
        
        self.federation_enabled = False
        
        # Cancel heartbeat task
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        # Close HTTP session
        if self.session:
            await self.session.close()
            self.session = None
        
        logger.info("🛑 Federation services stopped")
    
    async def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for specific task types"""
        self.task_handlers[task_type] = handler
        logger.info(f"📝 Registered handler for task type: {task_type}")
    
    async def forward_task(self, task_type: str, payload: Dict[str, Any],
                          priority: TaskPriority = TaskPriority.NORMAL,
                          target_bridge: Optional[str] = None,
                          deadline: Optional[datetime] = None) -> str:
        """
        Forward a task to another bridge in the federation
        
        Args:
            task_type: Type of task to forward
            payload: Task payload data
            priority: Task priority level
            target_bridge: Specific bridge to target (None for auto-selection)
            deadline: Optional deadline for task completion
            
        Returns:
            str: Task ID of the forwarded task
        """
        if not self.federation_enabled:
            raise RuntimeError("Federation not enabled")
        
        task_id = self._generate_task_id(task_type, payload)
        
        # Select target bridge if not specified
        if target_bridge is None:
            target_bridge = await self._select_target_bridge(task_type, priority)
        
        if target_bridge is None:
            raise RuntimeError("No suitable bridge found for task forwarding")
        
        task = FederatedTask(
            task_id=task_id,
            task_type=task_type,
            priority=priority,
            payload=payload,
            source_bridge=self.node_id,
            target_bridge=target_bridge,
            created_at=datetime.utcnow(),
            deadline=deadline,
            attempts=0,
            max_attempts=self.max_task_attempts,
            metadata={}
        )
        
        self.pending_tasks[task_id] = task
        
        # Send task to target bridge
        success = await self._send_task(task)
        
        if success:
            self.stats['tasks_forwarded'] += 1
            logger.info(f"📤 Task {task_id} forwarded to {target_bridge}")
        else:
            logger.error(f"❌ Failed to forward task {task_id} to {target_bridge}")
            task.attempts += 1
        
        return task_id
    
    async def handle_incoming_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming task from another bridge"""
        try:
            task = FederatedTask(**task_data)
            self.stats['tasks_received'] += 1
            
            logger.info(f"📥 Received task {task.task_id} from {task.source_bridge}")
            
            # Check if we have a handler for this task type
            if task.task_type not in self.task_handlers:
                logger.warning(f"⚠️ No handler for task type: {task.task_type}")
                return {
                    'status': 'error',
                    'error': f'No handler for task type: {task.task_type}',
                    'task_id': task.task_id
                }
            
            # Execute task handler
            handler = self.task_handlers[task.task_type]
            result = await handler(task.payload)
            
            self.stats['tasks_completed'] += 1
            self.completed_tasks[task.task_id] = task
            
            logger.info(f"✅ Completed task {task.task_id}")
            
            return {
                'status': 'completed',
                'result': result,
                'task_id': task.task_id,
                'completed_by': self.node_id,
                'completed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.stats['tasks_failed'] += 1
            logger.error(f"❌ Task execution failed: {e}")
            
            return {
                'status': 'error',
                'error': str(e),
                'task_id': task_data.get('task_id', 'unknown')
            }
    
    async def send_heartbeat(self, bridge_endpoint: str) -> bool:
        """Send heartbeat to a specific bridge"""
        if not self.session:
            return False
        
        heartbeat = HeartbeatSignal(
            node_id=self.node_id,
            timestamp=datetime.utcnow(),
            status=BridgeStatus.ONLINE,
            load_score=await self._calculate_load_score(),
            active_tasks=len(self.pending_tasks),
            capabilities=await self._get_capabilities(),
            metadata={
                'name': self.node_name,
                'endpoint': self.endpoint,
                'version': '2.0.0'
            }
        )
        
        try:
            async with self.session.post(
                f"{bridge_endpoint}/federation/heartbeat",
                json=asdict(heartbeat),
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status == 200:
                    self.stats['heartbeats_sent'] += 1
                    return True
                else:
                    logger.warning(f"⚠️ Heartbeat failed to {bridge_endpoint}: {response.status}")
                    return False
                    
        except Exception as e:
            logger.warning(f"⚠️ Heartbeat error to {bridge_endpoint}: {e}")
            return False
    
    async def handle_heartbeat(self, heartbeat_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming heartbeat from another bridge"""
        try:
            heartbeat = HeartbeatSignal(**heartbeat_data)
            self.stats['heartbeats_received'] += 1
            
            # Update or create bridge node record
            node = BridgeNode(
                node_id=heartbeat.node_id,
                name=heartbeat.metadata.get('name', heartbeat.node_id),
                endpoint=heartbeat.metadata.get('endpoint', ''),
                status=heartbeat.status,
                last_heartbeat=heartbeat.timestamp,
                capabilities=heartbeat.capabilities,
                load_score=heartbeat.load_score,
                version=heartbeat.metadata.get('version', 'unknown'),
                metadata=heartbeat.metadata
            )
            
            self.bridge_nodes[heartbeat.node_id] = node
            
            logger.debug(f"💓 Heartbeat from {heartbeat.node_id}")
            
            # Send our heartbeat back
            our_heartbeat = HeartbeatSignal(
                node_id=self.node_id,
                timestamp=datetime.utcnow(),
                status=BridgeStatus.ONLINE,
                load_score=await self._calculate_load_score(),
                active_tasks=len(self.pending_tasks),
                capabilities=await self._get_capabilities(),
                metadata={
                    'name': self.node_name,
                    'endpoint': self.endpoint,
                    'version': '2.0.0'
                }
            )
            
            return {
                'status': 'ok',
                'heartbeat': asdict(our_heartbeat)
            }
            
        except Exception as e:
            logger.error(f"❌ Heartbeat handling error: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_federation_status(self) -> Dict[str, Any]:
        """Get comprehensive federation status"""
        online_nodes = [n for n in self.bridge_nodes.values() if n.status == BridgeStatus.ONLINE]
        
        return {
            'federation_enabled': self.federation_enabled,
            'node_id': self.node_id,
            'node_name': self.node_name,
            'endpoint': self.endpoint,
            'connected_bridges': len(online_nodes),
            'total_known_bridges': len(self.bridge_nodes),
            'pending_tasks': len(self.pending_tasks),
            'completed_tasks': len(self.completed_tasks),
            'statistics': self.stats,
            'bridge_nodes': [node.to_dict() for node in online_nodes],
            'last_update': datetime.utcnow().isoformat()
        }
    
    async def _heartbeat_loop(self):
        """Main heartbeat loop"""
        while self.federation_enabled:
            try:
                # Send heartbeats to all known bridges
                for node in list(self.bridge_nodes.values()):
                    if node.endpoint and node.node_id != self.node_id:
                        await self.send_heartbeat(node.endpoint)
                
                # Check for offline nodes
                await self._check_node_timeouts()
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Heartbeat loop error: {e}")
                await asyncio.sleep(5)  # Brief pause before retry
    
    async def _discover_bridges(self, bridge_endpoints: List[str]):
        """Discover and connect to known bridges"""
        logger.info(f"🔍 Discovering {len(bridge_endpoints)} bridges...")
        
        for endpoint in bridge_endpoints:
            try:
                # Send initial heartbeat to discover the bridge
                await self.send_heartbeat(endpoint)
            except Exception as e:
                logger.warning(f"⚠️ Failed to discover bridge at {endpoint}: {e}")
        
        self.stats['last_discovery'] = datetime.utcnow()
    
    async def _select_target_bridge(self, task_type: str, priority: TaskPriority) -> Optional[str]:
        """Select the best bridge for forwarding a task"""
        online_nodes = [
            node for node in self.bridge_nodes.values()
            if node.status == BridgeStatus.ONLINE and node.node_id != self.node_id
        ]
        
        if not online_nodes:
            return None
        
        # Simple load-based selection (lowest load score)
        best_node = min(online_nodes, key=lambda n: n.load_score)
        return best_node.node_id
    
    async def _send_task(self, task: FederatedTask) -> bool:
        """Send task to target bridge"""
        if not self.session:
            return False
        
        target_node = self.bridge_nodes.get(task.target_bridge)
        if not target_node or not target_node.endpoint:
            return False
        
        try:
            async with self.session.post(
                f"{target_node.endpoint}/federation/task",
                json=task.to_dict(),
                headers={'Content-Type': 'application/json'}
            ) as response:
                return response.status == 200
                
        except Exception as e:
            logger.error(f"❌ Task send error: {e}")
            return False
    
    async def _calculate_load_score(self) -> float:
        """Calculate current load score (0.0 to 1.0)"""
        # Simple load calculation based on pending tasks
        base_load = len(self.pending_tasks) / 10.0  # Normalize to 10 max tasks
        return min(1.0, base_load)
    
    async def _get_capabilities(self) -> List[str]:
        """Get list of capabilities this bridge supports"""
        return [
            'task_forwarding',
            'heartbeat_signaling',
            'load_balancing',
            'agent_management',
            'mission_coordination'
        ]
    
    async def _check_node_timeouts(self):
        """Check for offline nodes and update their status"""
        timeout_threshold = datetime.utcnow() - timedelta(seconds=self.node_timeout)
        
        for node in self.bridge_nodes.values():
            if node.last_heartbeat < timeout_threshold and node.status == BridgeStatus.ONLINE:
                node.status = BridgeStatus.OFFLINE
                logger.warning(f"⚠️ Node {node.node_id} marked as offline")
    
    def _generate_task_id(self, task_type: str, payload: Dict[str, Any]) -> str:
        """Generate unique task ID"""
        content = f"{task_type}_{json.dumps(payload, sort_keys=True)}_{datetime.utcnow().timestamp()}"
        return hashlib.md5(content.encode()).hexdigest()[:16]