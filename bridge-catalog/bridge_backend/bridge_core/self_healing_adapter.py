"""
Self-Healing MAS Adapter - Retry + auto-heal adapter for corrupted/incomplete messages
Provides intelligent recovery and adaptation capabilities for multi-agent systems
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass
import hashlib
from functools import wraps

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Status of message processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CORRUPTED = "corrupted"
    RETRYING = "retrying"
    ABANDONED = "abandoned"


class HealingStrategy(Enum):
    """Self-healing strategies"""
    RETRY = "retry"
    FALLBACK = "fallback"
    RECONSTRUCTION = "reconstruction"
    BYPASS = "bypass"
    ESCALATION = "escalation"


@dataclass
class MessageRecord:
    """Record of message processing attempt"""
    message_id: str
    original_message: Any
    current_message: Any
    status: MessageStatus
    attempts: int
    created_at: datetime
    last_attempt: datetime
    errors: List[str]
    healing_attempts: List[str]
    metadata: Dict[str, Any]


@dataclass
class HealingResult:
    """Result of self-healing attempt"""
    success: bool
    strategy_used: HealingStrategy
    healed_message: Any
    confidence: float  # 0.0 to 1.0
    healing_time_ms: int
    metadata: Dict[str, Any]


class SelfHealingMASAdapter:
    """
    Self-healing Multi-Agent System adapter
    Provides intelligent retry, recovery, and adaptation for corrupted/incomplete messages
    """
    
    def __init__(self, max_retries: int = 3, healing_timeout: int = 300):
        """
        Initialize the self-healing adapter
        
        Args:
            max_retries: Maximum number of retry attempts
            healing_timeout: Timeout in seconds for healing operations
        """
        self.max_retries = max_retries
        self.healing_timeout = healing_timeout
        self.message_records: Dict[str, MessageRecord] = {}
        self.healing_strategies: Dict[HealingStrategy, Callable] = {}
        self.fallback_handlers: Dict[str, Callable] = {}
        
        # Statistics tracking
        self.stats = {
            'total_messages': 0,
            'successful_heals': 0,
            'failed_heals': 0,
            'healing_by_strategy': {strategy.value: 0 for strategy in HealingStrategy},
            'average_healing_time': 0.0,
            'last_reset': datetime.now(timezone.utc)
        }
        
        # Initialize default healing strategies
        self._setup_default_strategies()
        
        logger.info("🔧 SelfHealingMASAdapter initialized")
    
    async def process_message(self, message: Any, message_type: str = "default",
                            validator: Optional[Callable] = None) -> Any:
        """
        Process a message with self-healing capabilities
        
        Args:
            message: The message to process
            message_type: Type/category of the message
            validator: Optional function to validate message integrity
            
        Returns:
            Processed message or raises exception if healing fails
        """
        message_id = self._generate_message_id(message)
        self.stats['total_messages'] += 1
        
        # Create or update message record
        if message_id not in self.message_records:
            self.message_records[message_id] = MessageRecord(
                message_id=message_id,
                original_message=message,
                current_message=message,
                status=MessageStatus.PENDING,
                attempts=0,
                created_at=datetime.now(timezone.utc),
                last_attempt=datetime.now(timezone.utc),
                errors=[],
                healing_attempts=[],
                metadata={'message_type': message_type}
            )
        
        record = self.message_records[message_id]
        record.status = MessageStatus.PROCESSING
        record.attempts += 1
        record.last_attempt = datetime.now(timezone.utc)
        
        try:
            # Validate message if validator provided
            if validator and not await self._safe_validate(message, validator):
                logger.warning(f"📋 Message {message_id} failed validation")
                record.status = MessageStatus.CORRUPTED
                return await self._attempt_healing(record, validator)
            
            # Message is valid, process normally
            record.status = MessageStatus.COMPLETED
            logger.debug(f"✅ Message {message_id} processed successfully")
            return message
            
        except Exception as e:
            logger.error(f"❌ Error processing message {message_id}: {e}")
            record.errors.append(str(e))
            record.status = MessageStatus.FAILED
            
            # Attempt self-healing
            return await self._attempt_healing(record, validator)
    
    async def register_healing_strategy(self, strategy: HealingStrategy, 
                                      handler: Callable):
        """Register a custom healing strategy"""
        self.healing_strategies[strategy] = handler
        logger.info(f"🔧 Registered healing strategy: {strategy.value}")
    
    async def register_fallback_handler(self, message_type: str, 
                                      handler: Callable):
        """Register a fallback handler for specific message types"""
        self.fallback_handlers[message_type] = handler
        logger.info(f"🛡️ Registered fallback handler for: {message_type}")
    
    def get_healing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive healing statistics"""
        total_healing_attempts = self.stats['successful_heals'] + self.stats['failed_heals']
        
        return {
            **self.stats,
            'healing_success_rate': (
                self.stats['successful_heals'] / max(1, total_healing_attempts)
            ),
            'active_message_records': len(self.message_records),
            'pending_messages': len([r for r in self.message_records.values() 
                                   if r.status == MessageStatus.PENDING]),
            'failed_messages': len([r for r in self.message_records.values() 
                                  if r.status == MessageStatus.FAILED]),
            'current_time': datetime.now(timezone.utc).isoformat()
        }
    
    def cleanup_old_records(self, hours: int = 24):
        """Clean up old message records"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        old_records = [
            msg_id for msg_id, record in self.message_records.items()
            if record.created_at < cutoff and record.status in [
                MessageStatus.COMPLETED, MessageStatus.ABANDONED
            ]
        ]
        
        for msg_id in old_records:
            del self.message_records[msg_id]
        
        if old_records:
            logger.info(f"🧹 Cleaned up {len(old_records)} old message records")
    
    async def _attempt_healing(self, record: MessageRecord, 
                             validator: Optional[Callable] = None) -> Any:
        """Attempt to heal a corrupted or failed message"""
        if record.attempts > self.max_retries:
            record.status = MessageStatus.ABANDONED
            logger.error(f"🚫 Message {record.message_id} abandoned after {record.attempts} attempts")
            raise Exception(f"Message healing failed after {record.attempts} attempts")
        
        logger.info(f"🔄 Attempting to heal message {record.message_id} (attempt {record.attempts})")
        
        # Try different healing strategies
        strategies = [
            HealingStrategy.RETRY,
            HealingStrategy.RECONSTRUCTION,
            HealingStrategy.FALLBACK,
            HealingStrategy.BYPASS
        ]
        
        for strategy in strategies:
            try:
                start_time = datetime.now(timezone.utc)
                result = await self._apply_healing_strategy(strategy, record, validator)
                healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                if result.success:
                    record.status = MessageStatus.COMPLETED
                    record.healing_attempts.append(f"{strategy.value}:success")
                    self.stats['successful_heals'] += 1
                    self.stats['healing_by_strategy'][strategy.value] += 1
                    self._update_average_healing_time(healing_time)
                    
                    logger.info(f"✅ Message {record.message_id} healed using {strategy.value}")
                    return result.healed_message
                else:
                    record.healing_attempts.append(f"{strategy.value}:failed")
                    
            except Exception as e:
                logger.warning(f"⚠️ Healing strategy {strategy.value} failed: {e}")
                record.healing_attempts.append(f"{strategy.value}:error")
        
        # All strategies failed
        record.status = MessageStatus.FAILED
        self.stats['failed_heals'] += 1
        logger.error(f"💔 All healing strategies failed for message {record.message_id}")
        
        # Try fallback handler as last resort
        message_type = record.metadata.get('message_type', 'default')
        if message_type in self.fallback_handlers:
            try:
                fallback_result = await self.fallback_handlers[message_type](record)
                logger.info(f"🛡️ Fallback handler succeeded for {record.message_id}")
                return fallback_result
            except Exception as e:
                logger.error(f"🚫 Fallback handler failed: {e}")
        
        raise Exception(f"Message healing completely failed for {record.message_id}")
    
    async def _apply_healing_strategy(self, strategy: HealingStrategy, 
                                    record: MessageRecord,
                                    validator: Optional[Callable] = None) -> HealingResult:
        """Apply a specific healing strategy"""
        if strategy in self.healing_strategies:
            # Use custom registered strategy
            return await self.healing_strategies[strategy](record, validator)
        
        # Use built-in strategies
        if strategy == HealingStrategy.RETRY:
            return await self._retry_strategy(record, validator)
        elif strategy == HealingStrategy.RECONSTRUCTION:
            return await self._reconstruction_strategy(record, validator)
        elif strategy == HealingStrategy.FALLBACK:
            return await self._fallback_strategy(record, validator)
        elif strategy == HealingStrategy.BYPASS:
            return await self._bypass_strategy(record, validator)
        
        return HealingResult(
            success=False,
            strategy_used=strategy,
            healed_message=None,
            confidence=0.0,
            healing_time_ms=0,
            metadata={'error': 'Strategy not implemented'}
        )
    
    async def _retry_strategy(self, record: MessageRecord, 
                            validator: Optional[Callable] = None) -> HealingResult:
        """Simple retry strategy - try processing the original message again"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Add small delay to avoid immediate retry
            await asyncio.sleep(0.1 * record.attempts)
            
            # Validate the original message again
            if validator:
                if await self._safe_validate(record.original_message, validator):
                    healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                    return HealingResult(
                        success=True,
                        strategy_used=HealingStrategy.RETRY,
                        healed_message=record.original_message,
                        confidence=0.8,
                        healing_time_ms=int(healing_time),
                        metadata={'retries': record.attempts}
                    )
            else:
                # No validator, assume retry succeeded
                healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                return HealingResult(
                    success=True,
                    strategy_used=HealingStrategy.RETRY,
                    healed_message=record.original_message,
                    confidence=0.6,
                    healing_time_ms=int(healing_time),
                    metadata={'retries': record.attempts}
                )
                
        except Exception as e:
            logger.warning(f"⚠️ Retry strategy failed: {e}")
        
        return HealingResult(
            success=False,
            strategy_used=HealingStrategy.RETRY,
            healed_message=None,
            confidence=0.0,
            healing_time_ms=0,
            metadata={'error': 'Retry failed'}
        )
    
    async def _reconstruction_strategy(self, record: MessageRecord,
                                     validator: Optional[Callable] = None) -> HealingResult:
        """Attempt to reconstruct corrupted message"""
        start_time = datetime.now(timezone.utc)
        
        try:
            # Basic reconstruction strategies
            message = record.current_message
            
            # Strategy 1: Try to parse as JSON if it's a string
            if isinstance(message, str):
                try:
                    reconstructed = json.loads(message)
                    if validator and await self._safe_validate(reconstructed, validator):
                        healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                        return HealingResult(
                            success=True,
                            strategy_used=HealingStrategy.RECONSTRUCTION,
                            healed_message=reconstructed,
                            confidence=0.7,
                            healing_time_ms=int(healing_time),
                            metadata={'method': 'json_parse'}
                        )
                except json.JSONDecodeError:
                    pass
            
            # Strategy 2: Remove common corruption patterns
            if isinstance(message, str):
                # Remove null bytes, control characters
                cleaned = ''.join(char for char in message if ord(char) >= 32)
                if cleaned != message and validator:
                    if await self._safe_validate(cleaned, validator):
                        healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                        return HealingResult(
                            success=True,
                            strategy_used=HealingStrategy.RECONSTRUCTION,
                            healed_message=cleaned,
                            confidence=0.6,
                            healing_time_ms=int(healing_time),
                            metadata={'method': 'cleanup'}
                        )
            
            # Strategy 3: Try to recover dictionary structure
            if isinstance(message, dict):
                reconstructed = {}
                for key, value in message.items():
                    # Skip obviously corrupted keys/values
                    if isinstance(key, str) and len(key) > 0 and len(key) < 100:
                        reconstructed[key] = value
                
                if reconstructed and validator:
                    if await self._safe_validate(reconstructed, validator):
                        healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                        return HealingResult(
                            success=True,
                            strategy_used=HealingStrategy.RECONSTRUCTION,
                            healed_message=reconstructed,
                            confidence=0.5,
                            healing_time_ms=int(healing_time),
                            metadata={'method': 'dict_filter'}
                        )
            
        except Exception as e:
            logger.warning(f"⚠️ Reconstruction strategy failed: {e}")
        
        return HealingResult(
            success=False,
            strategy_used=HealingStrategy.RECONSTRUCTION,
            healed_message=None,
            confidence=0.0,
            healing_time_ms=0,
            metadata={'error': 'Reconstruction failed'}
        )
    
    async def _fallback_strategy(self, record: MessageRecord,
                               validator: Optional[Callable] = None) -> HealingResult:
        """Fallback to a default/safe message"""
        start_time = datetime.now(timezone.utc)
        
        # Create a minimal safe message based on message type
        message_type = record.metadata.get('message_type', 'default')
        
        fallback_messages = {
            'default': {'status': 'ok', 'message': 'fallback_response'},
            'agent_status': {'agent_id': 'unknown', 'status': 'unknown', 'health': 0.5},
            'mission_update': {'mission_id': 'unknown', 'status': 'pending', 'progress': 0},
            'system_event': {'event': 'fallback', 'timestamp': datetime.now(timezone.utc).isoformat()}
        }
        
        fallback_message = fallback_messages.get(message_type, fallback_messages['default'])
        
        healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return HealingResult(
            success=True,
            strategy_used=HealingStrategy.FALLBACK,
            healed_message=fallback_message,
            confidence=0.3,  # Low confidence since it's a fallback
            healing_time_ms=int(healing_time),
            metadata={'fallback_type': message_type}
        )
    
    async def _bypass_strategy(self, record: MessageRecord,
                             validator: Optional[Callable] = None) -> HealingResult:
        """Bypass validation and return the message as-is"""
        start_time = datetime.now(timezone.utc)
        
        # Return the message without validation
        healing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        
        return HealingResult(
            success=True,
            strategy_used=HealingStrategy.BYPASS,
            healed_message=record.current_message,
            confidence=0.2,  # Very low confidence
            healing_time_ms=int(healing_time),
            metadata={'warning': 'validation_bypassed'}
        )
    
    async def _safe_validate(self, message: Any, validator: Callable) -> bool:
        """Safely validate a message without throwing exceptions"""
        try:
            if asyncio.iscoroutinefunction(validator):
                return await validator(message)
            else:
                return validator(message)
        except Exception as e:
            logger.debug(f"🔍 Validation failed: {e}")
            return False
    
    def _generate_message_id(self, message: Any) -> str:
        """Generate a unique message ID"""
        content = str(message) + str(datetime.now(timezone.utc).timestamp())
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _update_average_healing_time(self, healing_time_ms: float):
        """Update the running average of healing times"""
        current_avg = self.stats['average_healing_time']
        total_heals = self.stats['successful_heals']
        
        if total_heals == 1:
            self.stats['average_healing_time'] = healing_time_ms
        else:
            # Running average calculation
            self.stats['average_healing_time'] = (
                (current_avg * (total_heals - 1) + healing_time_ms) / total_heals
            )
    
    def _setup_default_strategies(self):
        """Setup default healing strategies"""
        # Default strategies are implemented as methods
        # Custom strategies can be registered using register_healing_strategy
        pass