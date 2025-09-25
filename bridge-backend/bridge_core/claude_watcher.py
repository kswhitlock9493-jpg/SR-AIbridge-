"""
Claude Watcher - Event monitoring & system analyst recommendations
Monitors system events and provides intelligent analysis for decision making
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events that can be monitored"""
    SYSTEM_HEALTH = "system_health"
    AGENT_STATUS = "agent_status"
    MISSION_UPDATE = "mission_update"
    ERROR_DETECTED = "error_detected"
    PERFORMANCE_ALERT = "performance_alert"
    SECURITY_EVENT = "security_event"


class Severity(Enum):
    """Event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SystemEvent:
    """System event data structure"""
    event_id: str
    event_type: EventType
    severity: Severity
    timestamp: datetime
    source: str
    description: str
    data: Dict[str, Any]
    recommendations: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['severity'] = self.severity.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


class ClaudeWatcher:
    """
    Event monitoring and system analyst recommendations engine
    Provides intelligent monitoring and analysis for the SR-AIbridge system
    """
    
    def __init__(self, retention_hours: int = 24):
        """
        Initialize ClaudeWatcher
        
        Args:
            retention_hours: How long to retain events in memory
        """
        self.events: List[SystemEvent] = []
        self.retention_hours = retention_hours
        self.event_handlers: Dict[EventType, List[callable]] = {
            event_type: [] for event_type in EventType
        }
        self.metrics = {
            'total_events': 0,
            'events_by_type': {event_type.value: 0 for event_type in EventType},
            'events_by_severity': {severity.value: 0 for severity in Severity},
            'last_cleanup': datetime.utcnow()
        }
        
        logger.info("🔍 ClaudeWatcher initialized - Event monitoring active")
    
    def log_event(self, event_type: EventType, severity: Severity, source: str, 
                  description: str, data: Dict[str, Any] = None) -> SystemEvent:
        """
        Log a new system event with automatic analysis
        
        Args:
            event_type: Type of event
            severity: Severity level
            source: Source component that generated the event
            description: Human-readable description
            data: Additional event data
            
        Returns:
            SystemEvent: The created event with recommendations
        """
        event_id = f"{event_type.value}_{datetime.utcnow().timestamp()}"
        
        event = SystemEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            source=source,
            description=description,
            data=data or {},
            recommendations=self._generate_recommendations(event_type, severity, data or {})
        )
        
        self.events.append(event)
        self._update_metrics(event)
        self._trigger_handlers(event)
        self._cleanup_old_events()
        
        logger.info(f"📊 Event logged: {event_type.value} - {severity.value} from {source}")
        
        return event
    
    def get_recent_events(self, hours: int = 1, event_type: EventType = None, 
                         severity: Severity = None) -> List[SystemEvent]:
        """Get recent events with optional filtering"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        filtered_events = [
            event for event in self.events
            if event.timestamp >= cutoff
        ]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
            
        if severity:
            filtered_events = [e for e in filtered_events if e.severity == severity]
            
        return sorted(filtered_events, key=lambda x: x.timestamp, reverse=True)
    
    def get_system_analysis(self) -> Dict[str, Any]:
        """Get comprehensive system analysis based on recent events"""
        recent_events = self.get_recent_events(hours=1)
        critical_events = [e for e in recent_events if e.severity == Severity.CRITICAL]
        high_events = [e for e in recent_events if e.severity == Severity.HIGH]
        
        # System health score (0-100)
        health_score = self._calculate_health_score(recent_events)
        
        # Top recommendations
        recommendations = self._generate_system_recommendations(recent_events)
        
        return {
            'health_score': health_score,
            'total_events_1h': len(recent_events),
            'critical_events': len(critical_events),
            'high_priority_events': len(high_events),
            'recommendations': recommendations,
            'event_trend': self._calculate_event_trend(),
            'last_analysis': datetime.utcnow().isoformat(),
            'metrics': self.metrics
        }
    
    def register_event_handler(self, event_type: EventType, handler: callable):
        """Register a handler function for specific event types"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"📝 Registered handler for {event_type.value} events")
    
    def _generate_recommendations(self, event_type: EventType, severity: Severity, 
                                data: Dict[str, Any]) -> List[str]:
        """Generate intelligent recommendations based on event characteristics"""
        recommendations = []
        
        if event_type == EventType.SYSTEM_HEALTH:
            if severity in [Severity.HIGH, Severity.CRITICAL]:
                recommendations.extend([
                    "Run system self-heal process",
                    "Check database connectivity",
                    "Verify all critical services are running"
                ])
        
        elif event_type == EventType.AGENT_STATUS:
            if severity == Severity.CRITICAL:
                recommendations.extend([
                    "Restart failed agent services",
                    "Check agent endpoint connectivity",
                    "Review agent health scores"
                ])
        
        elif event_type == EventType.PERFORMANCE_ALERT:
            recommendations.extend([
                "Monitor system resource usage",
                "Consider scaling if needed",
                "Check for memory leaks or blocking operations"
            ])
        
        elif event_type == EventType.ERROR_DETECTED:
            recommendations.extend([
                "Review error logs for patterns",
                "Check for configuration issues",
                "Validate input data integrity"
            ])
        
        return recommendations
    
    def _generate_system_recommendations(self, events: List[SystemEvent]) -> List[str]:
        """Generate system-wide recommendations based on event patterns"""
        recommendations = []
        
        # Count events by type
        type_counts = {}
        for event in events:
            type_counts[event.event_type] = type_counts.get(event.event_type, 0) + 1
        
        # Pattern-based recommendations
        if type_counts.get(EventType.ERROR_DETECTED, 0) > 5:
            recommendations.append("High error rate detected - consider system maintenance")
        
        if type_counts.get(EventType.AGENT_STATUS, 0) > 3:
            recommendations.append("Multiple agent issues - check network connectivity")
        
        if type_counts.get(EventType.PERFORMANCE_ALERT, 0) > 2:
            recommendations.append("Performance degradation - monitor system resources")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_health_score(self, events: List[SystemEvent]) -> int:
        """Calculate overall system health score (0-100)"""
        if not events:
            return 100
        
        # Start with perfect score
        score = 100
        
        # Deduct points based on severity
        for event in events:
            if event.severity == Severity.CRITICAL:
                score -= 15
            elif event.severity == Severity.HIGH:
                score -= 8
            elif event.severity == Severity.MEDIUM:
                score -= 3
            elif event.severity == Severity.LOW:
                score -= 1
        
        return max(0, score)
    
    def _calculate_event_trend(self) -> str:
        """Calculate if events are trending up, down, or stable"""
        recent = len(self.get_recent_events(hours=1))
        previous = len(self.get_recent_events(hours=2)) - recent
        
        if recent > previous * 1.5:
            return "increasing"
        elif recent < previous * 0.5:
            return "decreasing"
        else:
            return "stable"
    
    def _update_metrics(self, event: SystemEvent):
        """Update internal metrics"""
        self.metrics['total_events'] += 1
        self.metrics['events_by_type'][event.event_type.value] += 1
        self.metrics['events_by_severity'][event.severity.value] += 1
    
    def _trigger_handlers(self, event: SystemEvent):
        """Trigger registered event handlers"""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"❌ Event handler error: {e}")
    
    def _cleanup_old_events(self):
        """Remove events older than retention period"""
        cutoff = datetime.utcnow() - timedelta(hours=self.retention_hours)
        original_count = len(self.events)
        
        self.events = [event for event in self.events if event.timestamp >= cutoff]
        
        cleaned_count = original_count - len(self.events)
        if cleaned_count > 0:
            logger.debug(f"🧹 Cleaned up {cleaned_count} old events")
            self.metrics['last_cleanup'] = datetime.utcnow()