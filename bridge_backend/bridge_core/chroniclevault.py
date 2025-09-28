"""
ChronicleVault - History Engine
Advanced historical data management and temporal analysis engine
Provides comprehensive historical tracking and replay capabilities for the SR-AIbridge system
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class RecordType(Enum):
    """Types of historical records"""
    EVENT = "event"
    STATE_CHANGE = "state_change"
    TRANSACTION = "transaction"
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    DATA_SNAPSHOT = "data_snapshot"


class RecordStatus(Enum):
    """Status of historical records"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted" 
    CORRUPTED = "corrupted"


@dataclass
class HistoricalRecord:
    """Historical record data structure"""
    record_id: str
    record_type: RecordType
    timestamp: datetime
    source: str
    title: str
    description: str
    data: Dict[str, Any]
    status: RecordStatus
    tags: List[str]
    checksum: str
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for serialization"""
        return {
            "record_id": self.record_id,
            "record_type": self.record_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "title": self.title,
            "description": self.description,
            "data": self.data,
            "status": self.status.value,
            "tags": self.tags,
            "checksum": self.checksum,
            "metadata": self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalRecord':
        """Create record from dictionary"""
        return cls(
            record_id=data["record_id"],
            record_type=RecordType(data["record_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            source=data["source"],
            title=data["title"],
            description=data["description"],
            data=data["data"],
            status=RecordStatus(data["status"]),
            tags=data["tags"],
            checksum=data["checksum"],
            metadata=data.get("metadata", {})
        )


@dataclass
class ReplayResult:
    """Result of historical replay operation"""
    replay_id: str
    records_processed: int
    success: bool
    start_time: datetime
    end_time: datetime
    duration_ms: float
    state_changes: List[Dict[str, Any]]
    errors: List[str]


class ChronicleVault:
    """
    History Engine for comprehensive temporal data management
    
    The ChronicleVault provides advanced historical tracking capabilities,
    allowing the system to record events, retrieve historical data,
    and replay past states for analysis and debugging.
    
    Key Rituals:
    - record: Capture and store historical events and state changes
    - retrieve: Query and access historical records with filtering
    - replay: Reconstruct and replay past system states
    """
    
    def __init__(self, retention_days: int = 365, max_records: int = 100000):
        """
        Initialize the ChronicleVault History Engine
        
        Args:
            retention_days: How long to keep historical records
            max_records: Maximum number of records to store
        """
        self.retention_days = retention_days
        self.max_records = max_records
        self.records: Dict[str, HistoricalRecord] = {}
        self.record_index: Dict[str, List[str]] = {
            "by_type": {},
            "by_source": {},
            "by_tags": {},
            "by_date": {}
        }
        self.metrics = {
            "total_records": 0,
            "records_by_type": {},
            "oldest_record": None,
            "newest_record": None,
            "last_cleanup": None,
            "replay_count": 0
        }
        logger.info("📚 ChronicleVault History Engine initialized")

    def record(self, record_type: RecordType, source: str, title: str, 
               description: str, data: Dict[str, Any], 
               tags: List[str] = None) -> HistoricalRecord:
        """
        Record a new historical event or state change
        
        Args:
            record_type: Type of record being created
            source: Source system or component that generated the record
            title: Brief title or summary of the record
            description: Detailed description of the event or change
            data: Associated data and context for the record
            tags: Optional tags for categorization and searching
            
        Returns:
            HistoricalRecord: The created historical record
        """
        timestamp = datetime.utcnow()
        record_id = self._generate_record_id(source, timestamp)
        
        # Calculate data checksum for integrity
        data_str = json.dumps(data, sort_keys=True, default=str)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()[:16]
        
        record = HistoricalRecord(
            record_id=record_id,
            record_type=record_type,
            timestamp=timestamp,
            source=source,
            title=title,
            description=description,
            data=data.copy(),
            status=RecordStatus.ACTIVE,
            tags=tags or [],
            checksum=checksum,
            metadata={
                "created_by": "ChronicleVault",
                "version": "1.0",
                "size_bytes": len(data_str)
            }
        )
        
        # Store record
        self.records[record_id] = record
        
        # Update indexes
        self._update_indexes(record)
        
        # Update metrics
        self._update_metrics(record)
        
        # Cleanup old records if needed
        if len(self.records) > self.max_records:
            self._cleanup_old_records()
        
        logger.info(f"📝 Recorded: {title} [{record_id}] from {source}")
        return record

    def retrieve(self, record_id: str = None, 
                 record_type: RecordType = None,
                 source: str = None,
                 tags: List[str] = None,
                 start_time: datetime = None,
                 end_time: datetime = None,
                 limit: int = 100) -> List[HistoricalRecord]:
        """
        Retrieve historical records with filtering options
        
        Args:
            record_id: Specific record ID to retrieve
            record_type: Filter by record type
            source: Filter by source system
            tags: Filter by tags (records must have all specified tags)
            start_time: Filter records after this time
            end_time: Filter records before this time
            limit: Maximum number of records to return
            
        Returns:
            List[HistoricalRecord]: Matching historical records
        """
        if record_id:
            # Direct record lookup
            record = self.records.get(record_id)
            return [record] if record else []
        
        # Build candidate set based on most selective filter
        candidates = set(self.records.keys())
        
        # Apply filters to narrow down candidates
        if record_type:
            type_records = self.record_index["by_type"].get(record_type.value, [])
            candidates = candidates.intersection(type_records)
        
        if source:
            source_records = self.record_index["by_source"].get(source, [])
            candidates = candidates.intersection(source_records)
        
        if tags:
            for tag in tags:
                tag_records = self.record_index["by_tags"].get(tag, [])
                candidates = candidates.intersection(tag_records)
        
        # Filter by time range and collect results
        results = []
        for record_id in candidates:
            record = self.records[record_id]
            
            # Apply time filters
            if start_time and record.timestamp < start_time:
                continue
            if end_time and record.timestamp > end_time:
                continue
            
            # Only include active records by default
            if record.status == RecordStatus.ACTIVE:
                results.append(record)
            
            if len(results) >= limit:
                break
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda r: r.timestamp, reverse=True)
        
        logger.info(f"🔍 Retrieved {len(results)} records with filters")
        return results

    def replay(self, start_time: datetime, end_time: datetime = None,
               record_types: List[RecordType] = None,
               sources: List[str] = None) -> ReplayResult:
        """
        Replay historical events within a time range
        
        Args:
            start_time: Starting time for replay
            end_time: Ending time for replay (defaults to now)
            record_types: Limit replay to specific record types
            sources: Limit replay to specific sources
            
        Returns:
            ReplayResult: Results of the replay operation
        """
        replay_start = datetime.utcnow()
        replay_id = f"replay_{int(replay_start.timestamp() * 1000)}"
        
        if end_time is None:
            end_time = datetime.utcnow()
        
        logger.info(f"🔄 Starting replay {replay_id} from {start_time} to {end_time}")
        
        try:
            # Retrieve records for replay period
            records = self.retrieve(
                start_time=start_time,
                end_time=end_time,
                limit=10000  # High limit for replay
            )
            
            # Filter by record types and sources if specified
            if record_types:
                records = [r for r in records if r.record_type in record_types]
            
            if sources:
                records = [r for r in records if r.source in sources]
            
            # Sort records chronologically for proper replay
            records.sort(key=lambda r: r.timestamp)
            
            # Process records and track state changes
            state_changes = []
            errors = []
            
            for record in records:
                try:
                    # Simulate state reconstruction
                    state_change = self._process_replay_record(record)
                    state_changes.append(state_change)
                    
                except Exception as e:
                    error_msg = f"Error processing record {record.record_id}: {str(e)}"
                    errors.append(error_msg)
                    logger.warning(f"⚠️ {error_msg}")
            
            replay_end = datetime.utcnow()
            duration_ms = (replay_end - replay_start).total_seconds() * 1000
            
            result = ReplayResult(
                replay_id=replay_id,
                records_processed=len(records),
                success=len(errors) == 0,
                start_time=replay_start,
                end_time=replay_end,
                duration_ms=duration_ms,
                state_changes=state_changes,
                errors=errors
            )
            
            # Update metrics
            self.metrics["replay_count"] += 1
            
            logger.info(f"✅ Replay completed: {len(records)} records, {len(errors)} errors")
            return result
            
        except Exception as e:
            logger.error(f"❌ Replay failed: {str(e)}")
            replay_end = datetime.utcnow()
            duration_ms = (replay_end - replay_start).total_seconds() * 1000
            
            return ReplayResult(
                replay_id=replay_id,
                records_processed=0,
                success=False,
                start_time=replay_start,
                end_time=replay_end,
                duration_ms=duration_ms,
                state_changes=[],
                errors=[str(e)]
            )

    def get_record_count(self, record_type: RecordType = None, 
                        source: str = None) -> int:
        """Get count of records with optional filtering"""
        if record_type is None and source is None:
            return len(self.records)
        
        records = self.retrieve(record_type=record_type, source=source, limit=10000)
        return len(records)

    def export_records(self, start_time: datetime = None, 
                      end_time: datetime = None,
                      format: str = "json") -> str:
        """Export historical records to a specified format"""
        records = self.retrieve(start_time=start_time, end_time=end_time, limit=10000)
        
        if format.lower() == "json":
            return json.dumps([record.to_dict() for record in records], 
                            indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_metrics(self) -> Dict[str, Any]:
        """Get current engine metrics and statistics"""
        return {
            **self.metrics,
            "current_record_count": len(self.records),
            "index_sizes": {k: len(v) for k, v in self.record_index["by_type"].items()},
            "retention_cutoff": datetime.utcnow() - timedelta(days=self.retention_days)
        }

    def _generate_record_id(self, source: str, timestamp: datetime) -> str:
        """Generate unique record ID"""
        content = f"{source}_{timestamp.isoformat()}_{hash(str(timestamp))}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _update_indexes(self, record: HistoricalRecord):
        """Update search indexes for the new record"""
        # Index by type
        record_type = record.record_type.value
        if record_type not in self.record_index["by_type"]:
            self.record_index["by_type"][record_type] = []
        self.record_index["by_type"][record_type].append(record.record_id)
        
        # Index by source
        if record.source not in self.record_index["by_source"]:
            self.record_index["by_source"][record.source] = []
        self.record_index["by_source"][record.source].append(record.record_id)
        
        # Index by tags
        for tag in record.tags:
            if tag not in self.record_index["by_tags"]:
                self.record_index["by_tags"][tag] = []
            self.record_index["by_tags"][tag].append(record.record_id)
        
        # Index by date
        date_key = record.timestamp.date().isoformat()
        if date_key not in self.record_index["by_date"]:
            self.record_index["by_date"][date_key] = []
        self.record_index["by_date"][date_key].append(record.record_id)

    def _update_metrics(self, record: HistoricalRecord):
        """Update engine metrics with new record"""
        self.metrics["total_records"] += 1
        
        # Update record type counts
        record_type = record.record_type.value
        if record_type not in self.metrics["records_by_type"]:
            self.metrics["records_by_type"][record_type] = 0
        self.metrics["records_by_type"][record_type] += 1
        
        # Update timestamp bounds
        if (self.metrics["oldest_record"] is None or 
            record.timestamp < self.metrics["oldest_record"]):
            self.metrics["oldest_record"] = record.timestamp
        
        if (self.metrics["newest_record"] is None or 
            record.timestamp > self.metrics["newest_record"]):
            self.metrics["newest_record"] = record.timestamp

    def _cleanup_old_records(self):
        """Remove old records based on retention policy"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
        old_records = []
        
        for record_id, record in self.records.items():
            if record.timestamp < cutoff_date:
                old_records.append(record_id)
        
        # Remove old records
        for record_id in old_records:
            record = self.records[record_id]
            record.status = RecordStatus.ARCHIVED
            del self.records[record_id]
            
            # Clean up indexes
            self._remove_from_indexes(record)
        
        if old_records:
            logger.info(f"🧹 Cleaned up {len(old_records)} old records")
            self.metrics["last_cleanup"] = datetime.utcnow()

    def _remove_from_indexes(self, record: HistoricalRecord):
        """Remove record from all indexes"""
        record_id = record.record_id
        
        # Remove from type index
        type_records = self.record_index["by_type"].get(record.record_type.value, [])
        if record_id in type_records:
            type_records.remove(record_id)
        
        # Remove from source index
        source_records = self.record_index["by_source"].get(record.source, [])
        if record_id in source_records:
            source_records.remove(record_id)
        
        # Remove from tag indexes
        for tag in record.tags:
            tag_records = self.record_index["by_tags"].get(tag, [])
            if record_id in tag_records:
                tag_records.remove(record_id)

    def _process_replay_record(self, record: HistoricalRecord) -> Dict[str, Any]:
        """Process a single record during replay"""
        # Simulate state change based on record type
        state_change = {
            "record_id": record.record_id,
            "timestamp": record.timestamp.isoformat(),
            "type": record.record_type.value,
            "source": record.source,
            "title": record.title,
            "changes": {}
        }
        
        # Extract state changes based on record type
        if record.record_type == RecordType.STATE_CHANGE:
            state_change["changes"] = record.data.get("state_changes", {})
        elif record.record_type == RecordType.TRANSACTION:
            state_change["changes"] = {
                "transaction_id": record.data.get("transaction_id"),
                "amount": record.data.get("amount"),
                "status": record.data.get("status")
            }  
        elif record.record_type == RecordType.USER_ACTION:
            state_change["changes"] = {
                "user_id": record.data.get("user_id"),
                "action": record.data.get("action"),
                "target": record.data.get("target")
            }
        else:
            # Generic event processing
            state_change["changes"] = {"event_data": record.data}
        
        return state_change