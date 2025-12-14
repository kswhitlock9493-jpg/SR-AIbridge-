"""
Fault Injector - Inject/drop/delay/reorder/corrupt messages for resilience testing
Provides controlled chaos engineering capabilities for testing system resilience
"""

import asyncio
import logging
import random
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


class FaultType(Enum):
    """Types of faults that can be injected"""
    DROP = "drop"           # Drop messages completely
    DELAY = "delay"         # Add artificial delays
    REORDER = "reorder"     # Change message order
    CORRUPT = "corrupt"     # Corrupt message content
    DUPLICATE = "duplicate" # Duplicate messages
    SLOW_RESPONSE = "slow_response"  # Slow down responses


@dataclass
class FaultConfig:
    """Configuration for fault injection"""
    fault_type: FaultType
    probability: float  # 0.0 to 1.0
    enabled: bool = True
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class FaultInjectionResult:
    """Result of fault injection attempt"""
    injected: bool
    fault_type: FaultType
    original_message: Any
    modified_message: Any
    delay_ms: int = 0
    metadata: Dict[str, Any] = None


class FaultInjector:
    """
    Fault injection system for resilience testing
    Supports various chaos engineering patterns to test system robustness
    """
    
    def __init__(self, enabled: bool = False):
        """
        Initialize FaultInjector
        
        Args:
            enabled: Whether fault injection is globally enabled
        """
        self.enabled = enabled
        self.fault_configs: Dict[FaultType, FaultConfig] = {}
        self.statistics = {
            'total_messages': 0,
            'faults_injected': 0,
            'faults_by_type': {fault_type.value: 0 for fault_type in FaultType},
            'last_reset': datetime.now(timezone.utc)
        }
        self.message_queue: List[Any] = []  # For reordering
        self.pending_messages: Dict[str, Any] = {}  # For delays
        
        # Default fault configurations
        self._setup_default_configs()
        
        logger.info(f"🔧 FaultInjector initialized - {'ENABLED' if enabled else 'DISABLED'}")
    
    def enable(self):
        """Enable fault injection globally"""
        self.enabled = True
        logger.info("⚠️ Fault injection ENABLED - Chaos mode activated")
    
    def disable(self):
        """Disable fault injection globally"""
        self.enabled = False
        logger.info("✅ Fault injection DISABLED - Normal operation")
    
    def configure_fault(self, fault_type: FaultType, probability: float, 
                       enabled: bool = True, **parameters):
        """
        Configure a specific fault type
        
        Args:
            fault_type: Type of fault to configure
            probability: Probability of fault injection (0.0 to 1.0)
            enabled: Whether this fault type is enabled
            **parameters: Additional parameters for the fault type
        """
        self.fault_configs[fault_type] = FaultConfig(
            fault_type=fault_type,
            probability=max(0.0, min(1.0, probability)),
            enabled=enabled,
            parameters=parameters
        )
        
        logger.info(f"🎛️ Configured {fault_type.value} fault: "
                   f"probability={probability}, enabled={enabled}")
    
    async def process_message(self, message: Any, message_id: str = None) -> FaultInjectionResult:
        """
        Process a message through fault injection
        
        Args:
            message: The message to potentially inject faults into
            message_id: Optional message identifier
            
        Returns:
            FaultInjectionResult: Result of fault injection processing
        """
        self.statistics['total_messages'] += 1
        
        if not self.enabled:
            return FaultInjectionResult(
                injected=False,
                fault_type=None,
                original_message=message,
                modified_message=message
            )
        
        # Generate message ID if not provided
        if message_id is None:
            message_id = self._generate_message_id(message)
        
        # Determine which fault to inject (if any)
        fault_type = self._select_fault_type()
        
        if fault_type is None:
            return FaultInjectionResult(
                injected=False,
                fault_type=None,
                original_message=message,
                modified_message=message
            )
        
        # Inject the selected fault
        return await self._inject_fault(fault_type, message, message_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get fault injection statistics"""
        return {
            **self.statistics,
            'injection_rate': (
                self.statistics['faults_injected'] / max(1, self.statistics['total_messages'])
            ),
            'enabled': self.enabled,
            'active_faults': len([c for c in self.fault_configs.values() if c.enabled]),
            'current_time': datetime.now(timezone.utc).isoformat()
        }
    
    def reset_statistics(self):
        """Reset fault injection statistics"""
        self.statistics = {
            'total_messages': 0,
            'faults_injected': 0,
            'faults_by_type': {fault_type.value: 0 for fault_type in FaultType},
            'last_reset': datetime.now(timezone.utc)
        }
        logger.info("📊 Fault injection statistics reset")
    
    def _setup_default_configs(self):
        """Setup default fault configurations"""
        # Conservative defaults for safety
        self.configure_fault(FaultType.DROP, probability=0.01)  # 1% drop rate
        self.configure_fault(FaultType.DELAY, probability=0.05, 
                           min_delay_ms=100, max_delay_ms=1000)
        self.configure_fault(FaultType.REORDER, probability=0.02)
        self.configure_fault(FaultType.CORRUPT, probability=0.01,
                           corruption_rate=0.1)  # 10% of content
        self.configure_fault(FaultType.DUPLICATE, probability=0.01)
        self.configure_fault(FaultType.SLOW_RESPONSE, probability=0.03,
                           min_delay_ms=500, max_delay_ms=3000)
    
    def _select_fault_type(self) -> Optional[FaultType]:
        """Select a fault type to inject based on probabilities"""
        enabled_faults = [
            (fault_type, config) for fault_type, config in self.fault_configs.items()
            if config.enabled
        ]
        
        if not enabled_faults:
            return None
        
        # Weighted random selection
        for fault_type, config in enabled_faults:
            if random.random() < config.probability:
                return fault_type
        
        return None
    
    async def _inject_fault(self, fault_type: FaultType, message: Any, 
                          message_id: str) -> FaultInjectionResult:
        """Inject a specific fault type"""
        config = self.fault_configs[fault_type]
        self.statistics['faults_injected'] += 1
        self.statistics['faults_by_type'][fault_type.value] += 1
        
        logger.warning(f"💥 Injecting {fault_type.value} fault for message {message_id}")
        
        if fault_type == FaultType.DROP:
            return await self._inject_drop(message, message_id, config)
        elif fault_type == FaultType.DELAY:
            return await self._inject_delay(message, message_id, config)
        elif fault_type == FaultType.REORDER:
            return await self._inject_reorder(message, message_id, config)
        elif fault_type == FaultType.CORRUPT:
            return await self._inject_corrupt(message, message_id, config)
        elif fault_type == FaultType.DUPLICATE:
            return await self._inject_duplicate(message, message_id, config)
        elif fault_type == FaultType.SLOW_RESPONSE:
            return await self._inject_slow_response(message, message_id, config)
        
        # Fallback - no fault injected
        return FaultInjectionResult(
            injected=False,
            fault_type=fault_type,
            original_message=message,
            modified_message=message
        )
    
    async def _inject_drop(self, message: Any, message_id: str, 
                         config: FaultConfig) -> FaultInjectionResult:
        """Drop message completely"""
        return FaultInjectionResult(
            injected=True,
            fault_type=FaultType.DROP,
            original_message=message,
            modified_message=None,
            metadata={'dropped': True, 'message_id': message_id}
        )
    
    async def _inject_delay(self, message: Any, message_id: str,
                          config: FaultConfig) -> FaultInjectionResult:
        """Add artificial delay to message"""
        min_delay = config.parameters.get('min_delay_ms', 100)
        max_delay = config.parameters.get('max_delay_ms', 1000)
        delay_ms = random.randint(min_delay, max_delay)
        
        # Actually delay the processing
        await asyncio.sleep(delay_ms / 1000.0)
        
        return FaultInjectionResult(
            injected=True,
            fault_type=FaultType.DELAY,
            original_message=message,
            modified_message=message,
            delay_ms=delay_ms,
            metadata={'delayed_ms': delay_ms}
        )
    
    async def _inject_reorder(self, message: Any, message_id: str,
                            config: FaultConfig) -> FaultInjectionResult:
        """Reorder messages"""
        # Add to queue and potentially return an older message
        self.message_queue.append((message, message_id))
        
        # Limit queue size
        max_queue_size = config.parameters.get('max_queue_size', 5)
        if len(self.message_queue) > max_queue_size:
            # Return an older message instead
            old_message, old_id = self.message_queue.pop(0)
            return FaultInjectionResult(
                injected=True,
                fault_type=FaultType.REORDER,
                original_message=message,
                modified_message=old_message,
                metadata={'reordered': True, 'original_id': old_id}
            )
        
        # Not enough messages to reorder yet
        return FaultInjectionResult(
            injected=False,
            fault_type=FaultType.REORDER,
            original_message=message,
            modified_message=message,
            metadata={'queued_for_reorder': True}
        )
    
    async def _inject_corrupt(self, message: Any, message_id: str,
                            config: FaultConfig) -> FaultInjectionResult:
        """Corrupt message content"""
        corruption_rate = config.parameters.get('corruption_rate', 0.1)
        
        if isinstance(message, str):
            corrupted = self._corrupt_string(message, corruption_rate)
        elif isinstance(message, dict):
            corrupted = self._corrupt_dict(message, corruption_rate)
        elif isinstance(message, list):
            corrupted = self._corrupt_list(message, corruption_rate)
        else:
            # Convert to string and corrupt
            corrupted = self._corrupt_string(str(message), corruption_rate)
        
        return FaultInjectionResult(
            injected=True,
            fault_type=FaultType.CORRUPT,
            original_message=message,
            modified_message=corrupted,
            metadata={'corruption_rate': corruption_rate}
        )
    
    async def _inject_duplicate(self, message: Any, message_id: str,
                              config: FaultConfig) -> FaultInjectionResult:
        """Duplicate message"""
        # Return the same message multiple times
        duplicate_count = config.parameters.get('duplicate_count', 2)
        
        return FaultInjectionResult(
            injected=True,
            fault_type=FaultType.DUPLICATE,
            original_message=message,
            modified_message=message,
            metadata={'duplicated': True, 'count': duplicate_count}
        )
    
    async def _inject_slow_response(self, message: Any, message_id: str,
                                  config: FaultConfig) -> FaultInjectionResult:
        """Slow down response processing"""
        min_delay = config.parameters.get('min_delay_ms', 500)
        max_delay = config.parameters.get('max_delay_ms', 3000)
        delay_ms = random.randint(min_delay, max_delay)
        
        await asyncio.sleep(delay_ms / 1000.0)
        
        return FaultInjectionResult(
            injected=True,
            fault_type=FaultType.SLOW_RESPONSE,
            original_message=message,
            modified_message=message,
            delay_ms=delay_ms,
            metadata={'slow_response_ms': delay_ms}
        )
    
    def _corrupt_string(self, text: str, corruption_rate: float) -> str:
        """Corrupt a string by randomly changing characters"""
        if not text:
            return text
        
        corrupted = list(text)
        chars_to_corrupt = max(1, int(len(text) * corruption_rate))
        
        for _ in range(chars_to_corrupt):
            if len(corrupted) > 0:
                idx = random.randint(0, len(corrupted) - 1)
                # Replace with random character
                corrupted[idx] = chr(random.randint(33, 126))
        
        return ''.join(corrupted)
    
    def _corrupt_dict(self, data: dict, corruption_rate: float) -> dict:
        """Corrupt dictionary values"""
        corrupted = data.copy()
        keys_to_corrupt = random.sample(
            list(corrupted.keys()),
            max(1, int(len(corrupted) * corruption_rate))
        )
        
        for key in keys_to_corrupt:
            if isinstance(corrupted[key], str):
                corrupted[key] = self._corrupt_string(corrupted[key], 0.3)
            elif isinstance(corrupted[key], (int, float)):
                corrupted[key] = corrupted[key] * random.uniform(0.5, 1.5)
        
        return corrupted
    
    def _corrupt_list(self, data: list, corruption_rate: float) -> list:
        """Corrupt list elements"""
        if not data:
            return data
        
        corrupted = data.copy()
        indices_to_corrupt = random.sample(
            range(len(corrupted)),
            max(1, int(len(corrupted) * corruption_rate))
        )
        
        for idx in indices_to_corrupt:
            if isinstance(corrupted[idx], str):
                corrupted[idx] = self._corrupt_string(corrupted[idx], 0.3)
        
        return corrupted
    
    def _generate_message_id(self, message: Any) -> str:
        """Generate a unique message ID"""
        content = str(message) + str(datetime.now(timezone.utc).timestamp())
        return hashlib.md5(content.encode()).hexdigest()[:8]