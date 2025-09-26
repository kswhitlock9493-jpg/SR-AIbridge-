"""
SQLite Brain Ledger for SR-AIbridge Sovereign Brain
Local-first memory storage with cryptographic attestation
"""
import os
import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from contextlib import contextmanager

from .signer import AtomicSigner, create_signer


@dataclass
class MemoryEntry:
    """A single memory entry in the brain ledger"""
    id: Optional[int]
    content: str
    category: str
    classification: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    signed_hash: Optional[str] = None
    signature_data: Optional[str] = None


class BrainLedger:
    """SQLite-based brain ledger for sovereign memory storage"""
    
    def __init__(self, db_path: str = "./brain.sqlite", signer: Optional[AtomicSigner] = None):
        self.db_path = db_path
        self.signer = signer or create_signer()
        self._init_database()
    
    def _init_database(self):
        """Initialize the brain database schema"""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    classification TEXT NOT NULL DEFAULT 'public',
                    metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    signed_hash TEXT,
                    signature_data TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS brain_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_category ON memory_entries(category)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_classification ON memory_entries(classification)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_memory_created ON memory_entries(created_at)
            """)
            
            # Initialize brain metadata
            conn.execute("""
                INSERT OR IGNORE INTO brain_metadata (key, value) 
                VALUES ('initialized_at', ?)
            """, (datetime.utcnow().isoformat(),))
            
            conn.execute("""
                INSERT OR IGNORE INTO brain_metadata (key, value) 
                VALUES ('version', '1.0')
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_memory(self, content: str, category: str = "general", 
                   classification: str = "public", metadata: Dict[str, Any] = None,
                   sign: bool = True) -> int:
        """Add a new memory entry to the brain"""
        if metadata is None:
            metadata = {}
        
        # Add system metadata (don't overwrite user metadata)
        system_metadata = {
            "source": "sovereign_brain",
            "entry_type": "memory",
            "auto_signed": sign
        }
        
        # Merge system metadata without overwriting user metadata
        if metadata:
            system_metadata.update(metadata)
        metadata = system_metadata
        
        signed_hash = None
        signature_data = None
        
        if sign:
            # Create signable payload
            payload = {
                "content": content,
                "category": category,
                "classification": classification,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            signed_envelope = self.signer.sign_payload(payload)
            signed_hash = signed_envelope["metadata"]["payload_hash"]
            signature_data = json.dumps(signed_envelope["signature"])
        
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO memory_entries 
                (content, category, classification, metadata, signed_hash, signature_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content, category, classification, json.dumps(metadata), 
                  signed_hash, signature_data))
            
            entry_id = cursor.lastrowid
            conn.commit()
            return entry_id
    
    def get_memory(self, entry_id: int) -> Optional[MemoryEntry]:
        """Get a specific memory entry by ID"""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM memory_entries WHERE id = ?
            """, (entry_id,)).fetchone()
            
            if row:
                return self._row_to_memory_entry(row)
            return None
    
    def search_memories(self, query: str = None, category: str = None, 
                       classification: str = None, limit: int = 100,
                       offset: int = 0) -> List[MemoryEntry]:
        """Search memory entries with optional filters"""
        sql = "SELECT * FROM memory_entries WHERE 1=1"
        params = []
        
        if query:
            sql += " AND (content LIKE ? OR metadata LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%"])
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        if classification:
            sql += " AND classification = ?"
            params.append(classification)
        
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self._get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_memory_entry(row) for row in rows]
    
    def update_memory(self, entry_id: int, content: str = None, 
                     category: str = None, classification: str = None,
                     metadata: Dict[str, Any] = None, resign: bool = True) -> bool:
        """Update an existing memory entry"""
        # Get current entry
        current = self.get_memory(entry_id)
        if not current:
            return False
        
        # Prepare updates
        updates = {}
        if content is not None:
            updates["content"] = content
        if category is not None:
            updates["category"] = category
        if classification is not None:
            updates["classification"] = classification
        if metadata is not None:
            # Merge with existing metadata
            current_meta = json.loads(current.metadata) if isinstance(current.metadata, str) else current.metadata
            current_meta.update(metadata)
            current_meta["last_modified"] = datetime.utcnow().isoformat()
            updates["metadata"] = json.dumps(current_meta)
        
        if not updates:
            return False
        
        # Handle re-signing if requested
        if resign and updates:
            payload = {
                "entry_id": entry_id,
                "updates": updates,
                "timestamp": datetime.utcnow().isoformat(),
                "operation": "update"
            }
            
            signed_envelope = self.signer.sign_payload(payload)
            updates["signed_hash"] = signed_envelope["metadata"]["payload_hash"]
            updates["signature_data"] = json.dumps(signed_envelope["signature"])
        
        # Build SQL update
        set_clauses = []
        params = []
        for key, value in updates.items():
            set_clauses.append(f"{key} = ?")
            params.append(value)
        
        params.append(entry_id)
        
        sql = f"""
            UPDATE memory_entries 
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        
        with self._get_connection() as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_memory(self, entry_id: int) -> bool:
        """Delete a memory entry"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM memory_entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_categories(self) -> List[Tuple[str, int]]:
        """Get all categories with counts"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM memory_entries 
                GROUP BY category 
                ORDER BY count DESC
            """).fetchall()
            return [(row["category"], row["count"]) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get brain ledger statistics"""
        with self._get_connection() as conn:
            # Basic counts
            total_memories = conn.execute("SELECT COUNT(*) FROM memory_entries").fetchone()[0]
            signed_memories = conn.execute("SELECT COUNT(*) FROM memory_entries WHERE signed_hash IS NOT NULL").fetchone()[0]
            
            # Category breakdown
            categories = dict(conn.execute("""
                SELECT category, COUNT(*) 
                FROM memory_entries 
                GROUP BY category
            """).fetchall())
            
            # Classification breakdown
            classifications = dict(conn.execute("""
                SELECT classification, COUNT(*) 
                FROM memory_entries 
                GROUP BY classification
            """).fetchall())
            
            # Recent activity
            recent_count = conn.execute("""
                SELECT COUNT(*) FROM memory_entries 
                WHERE created_at > datetime('now', '-7 days')
            """).fetchone()[0]
            
            # Brain metadata
            metadata_rows = conn.execute("SELECT key, value FROM brain_metadata").fetchall()
            brain_metadata = {row["key"]: row["value"] for row in metadata_rows}
            
            return {
                "total_memories": total_memories,
                "signed_memories": signed_memories,
                "unsigned_memories": total_memories - signed_memories,
                "categories": categories,
                "classifications": classifications,
                "recent_activity": recent_count,
                "brain_metadata": brain_metadata,
                "database_size": os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            }
    
    def export_memories(self, category: str = None, classification: str = None,
                       include_signatures: bool = True) -> Dict[str, Any]:
        """Export memories to a portable format"""
        memories = self.search_memories(category=category, classification=classification, limit=10000)
        
        export_data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "export_type": "sovereign_brain_dump",
            "filters": {
                "category": category,
                "classification": classification,
                "include_signatures": include_signatures
            },
            "memory_count": len(memories),
            "memories": []
        }
        
        for memory in memories:
            memory_data = {
                "id": memory.id,
                "content": memory.content,
                "category": memory.category,
                "classification": memory.classification,
                "metadata": json.loads(memory.metadata) if isinstance(memory.metadata, str) else memory.metadata,
                "created_at": memory.created_at.isoformat() if isinstance(memory.created_at, datetime) else memory.created_at,
                "updated_at": memory.updated_at.isoformat() if isinstance(memory.updated_at, datetime) else memory.updated_at
            }
            
            if include_signatures and memory.signed_hash:
                memory_data["signed_hash"] = memory.signed_hash
                memory_data["signature_data"] = json.loads(memory.signature_data) if memory.signature_data else None
            
            export_data["memories"].append(memory_data)
        
        return export_data
    
    def verify_memory_signatures(self) -> Dict[str, Any]:
        """Verify all signed memories in the brain"""
        results = {
            "total_checked": 0,
            "valid_signatures": 0,
            "invalid_signatures": 0,
            "unsigned_memories": 0,
            "verification_details": []
        }
        
        with self._get_connection() as conn:
            rows = conn.execute("SELECT * FROM memory_entries").fetchall()
            
            for row in rows:
                results["total_checked"] += 1
                
                if not row["signed_hash"] or not row["signature_data"]:
                    results["unsigned_memories"] += 1
                    continue
                
                try:
                    # Reconstruct the original payload for verification
                    metadata = json.loads(row["metadata"]) if row["metadata"] else {}
                    payload = {
                        "content": row["content"],
                        "category": row["category"],
                        "classification": row["classification"],
                        "metadata": metadata,
                        "timestamp": row["created_at"]
                    }
                    
                    # Reconstruct signing envelope (without signature)
                    signing_envelope = {
                        "payload": payload,
                        "metadata": {
                            "signer": "admiral",  # Default signer
                            "signed_at": row["created_at"],  # Use created_at as signed_at
                            "payload_hash": row["signed_hash"],
                            "signature_version": "1.0"
                        }
                    }
                    
                    # Add signature data and verify
                    signature_data = json.loads(row["signature_data"])
                    signed_envelope = {
                        **signing_envelope,
                        "signature": signature_data
                    }
                    
                    is_valid, message = self.signer.verify_signature(signed_envelope)
                    
                    if is_valid:
                        results["valid_signatures"] += 1
                    else:
                        results["invalid_signatures"] += 1
                        results["verification_details"].append({
                            "entry_id": row["id"],
                            "valid": False,
                            "message": message
                        })
                
                except Exception as e:
                    results["invalid_signatures"] += 1
                    results["verification_details"].append({
                        "entry_id": row["id"],
                        "valid": False,
                        "message": f"Verification error: {str(e)}"
                    })
        
        return results
    
    def _row_to_memory_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry object"""
        return MemoryEntry(
            id=row["id"],
            content=row["content"],
            category=row["category"],
            classification=row["classification"],
            metadata=row["metadata"],
            created_at=datetime.fromisoformat(row["created_at"].replace('Z', '+00:00')) if isinstance(row["created_at"], str) else row["created_at"],
            updated_at=datetime.fromisoformat(row["updated_at"].replace('Z', '+00:00')) if isinstance(row["updated_at"], str) else row["updated_at"],
            signed_hash=row["signed_hash"],
            signature_data=row["signature_data"]
        )


def create_brain_ledger(db_path: str = "./brain.sqlite") -> BrainLedger:
    """Create a brain ledger with initialized signer"""
    return BrainLedger(db_path)


if __name__ == "__main__":
    # CLI for brain operations
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python brain.py [add|search|stats|export|verify] [args...]")
        sys.exit(1)
    
    action = sys.argv[1]
    brain = create_brain_ledger()
    
    if action == "add":
        if len(sys.argv) < 3:
            print("Usage: python brain.py add <content> [category] [classification]")
            sys.exit(1)
        
        content = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "general"
        classification = sys.argv[4] if len(sys.argv) > 4 else "public"
        
        entry_id = brain.add_memory(content, category, classification)
        print(f"Added memory entry {entry_id}")
    
    elif action == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else None
        memories = brain.search_memories(query=query, limit=10)
        
        print(f"Found {len(memories)} memories:")
        for memory in memories:
            print(f"  [{memory.id}] {memory.category}: {memory.content[:50]}...")
    
    elif action == "stats":
        stats = brain.get_statistics()
        print(f"Brain Statistics:")
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  Signed memories: {stats['signed_memories']}")
        print(f"  Categories: {len(stats['categories'])}")
        print(f"  Recent activity: {stats['recent_activity']}")
    
    elif action == "export":
        export_data = brain.export_memories()
        output_file = "brain_export.json"
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"Exported {export_data['memory_count']} memories to {output_file}")
    
    elif action == "verify":
        results = brain.verify_memory_signatures()
        print(f"Signature Verification Results:")
        print(f"  Total checked: {results['total_checked']}")
        print(f"  Valid signatures: {results['valid_signatures']}")
        print(f"  Invalid signatures: {results['invalid_signatures']}")
        print(f"  Unsigned memories: {results['unsigned_memories']}")
    
    else:
        print("Unknown action")
        sys.exit(1)