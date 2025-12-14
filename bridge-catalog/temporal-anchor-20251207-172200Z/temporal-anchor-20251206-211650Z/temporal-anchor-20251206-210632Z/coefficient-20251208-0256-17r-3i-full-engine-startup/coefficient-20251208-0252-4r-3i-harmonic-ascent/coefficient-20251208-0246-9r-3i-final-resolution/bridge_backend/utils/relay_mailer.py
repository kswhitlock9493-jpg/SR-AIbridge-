"""
SR-AIbridge Secure Data Relay Protocol
Email relay module with SMTP/Gmail integration and checksum validation

This module implements the Secure Data Relay Protocol to prevent data loss
by automatically archiving data to sraibridge@gmail.com before deletion.
"""
import os
import json
import hashlib
import smtplib
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path


class RelayMailer:
    """
    Secure Data Relay Mailer
    
    Handles email relay to sraibridge@gmail.com with:
    - Automatic pre-deletion archival
    - Cryptographic checksums for verification
    - Role-aware retention policies (Admiral/Captain/Agent)
    - Queue-based retry mechanism for network failures
    """
    
    def __init__(self):
        self.enabled = os.getenv("RELAY_ENABLED", "false").lower() == "true"
        self.relay_email = os.getenv("RELAY_EMAIL", "sraibridge@gmail.com")
        self.relay_mode = os.getenv("RELAY_MODE", "pre_delete")
        self.backup_path = Path(os.getenv("RELAY_BACKUP_PATH", "./vault/relay_queue"))
        
        # SMTP Configuration
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
        
        # Ensure backup path exists
        try:
            self.backup_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fallback to /tmp if we don't have permission
            self.backup_path = Path("/tmp/relay_queue")
            self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # Role-based retention durations (in hours)
        self.retention_policies = {
            "admiral": -1,  # Permanent (-1 means no expiration)
            "captain": 14,  # 14 hours
            "agent": 7      # 7 hours
        }
    
    def calculate_checksum(self, data: Any) -> str:
        """
        Calculate SHA256 checksum for data verification
        
        Args:
            data: Data to hash (will be JSON-serialized if not string)
        
        Returns:
            Hexadecimal SHA256 hash
        """
        if isinstance(data, str):
            content = data.encode('utf-8')
        else:
            content = json.dumps(data, sort_keys=True).encode('utf-8')
        
        return hashlib.sha256(content).hexdigest()
    
    def format_relay_metadata(
        self,
        component: str,
        action: str,
        user_id: str,
        role: str,
        data: Any
    ) -> Dict[str, Any]:
        """
        Format metadata envelope for relay email
        
        Args:
            component: System component (vault, brain, missions, etc.)
            action: Action type (DELETE, PURGE, EXPIRE)
            user_id: User/Captain/Agent ID
            role: Role (admiral, captain, agent)
            data: Data being archived
        
        Returns:
            Metadata dictionary with checksum
        """
        payload_hash = self.calculate_checksum(data)
        
        metadata = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "role": role,
            "component": component,
            "action": action,
            "payload_hash": payload_hash,
            "retention_hours": self.retention_policies.get(role, 7),
            "notes": "Archived automatically before deletion via Secure Data Relay Protocol"
        }
        
        return metadata
    
    def queue_for_retry(self, metadata: Dict[str, Any], data: Any) -> str:
        """
        Queue email for retry if network fails
        
        Args:
            metadata: Email metadata
            data: Data payload
        
        Returns:
            Queue file path
        """
        queue_entry = {
            "metadata": metadata,
            "data": data,
            "queued_at": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0
        }
        
        filename = f"relay_{metadata['timestamp'].replace(':', '-')}_{metadata['payload_hash'][:8]}.json"
        queue_file = self.backup_path / filename
        
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(queue_entry, f, indent=2)
        
        return str(queue_file)
    
    async def send_relay_email(
        self,
        component: str,
        action: str,
        user_id: str,
        role: str,
        data: Any,
        subject_prefix: str = "[SR-AIbridge] Data Relay Event"
    ) -> bool:
        """
        Send relay email with data archive
        
        Args:
            component: System component
            action: Action type
            user_id: User ID
            role: User role
            data: Data to archive
            subject_prefix: Email subject prefix
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            print(f"[RelayMailer] Relay disabled, skipping archive for {component}/{action}")
            return True
        
        if not self.smtp_user or not self.smtp_password:
            print("[RelayMailer] SMTP credentials not configured, queuing for later")
            metadata = self.format_relay_metadata(component, action, user_id, role, data)
            self.queue_for_retry(metadata, data)
            return False
        
        try:
            # Format metadata
            metadata = self.format_relay_metadata(component, action, user_id, role, data)
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.smtp_user
            msg['To'] = self.relay_email
            msg['Subject'] = f"{subject_prefix} – {component}"
            
            # Email body with metadata
            body = f"""SR-AIbridge Secure Data Relay
            
Component: {component}
Action: {action}
User ID: {user_id}
Role: {role}
Timestamp: {metadata['timestamp']}
Checksum: {metadata['payload_hash']}
Retention: {metadata['retention_hours']} hours

This is an automated data archive generated before deletion.
Data payload is attached as JSON.

---
SR-AIbridge Secure Data Relay Protocol v1.0
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach data as JSON
            data_json = json.dumps({"metadata": metadata, "data": data}, indent=2)
            attachment = MIMEBase('application', 'json')
            attachment.set_payload(data_json.encode('utf-8'))
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename="relay_{component}_{metadata["timestamp"][:10]}.json"'
            )
            msg.attach(attachment)
            
            # Send via SMTP
            async with aiosmtplib.SMTP(hostname=self.smtp_host, port=self.smtp_port) as smtp:
                if self.smtp_use_tls:
                    await smtp.starttls()
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(msg)
            
            print(f"[RelayMailer] Successfully sent relay email for {component}/{action}")
            return True
            
        except Exception as e:
            print(f"[RelayMailer] Failed to send relay email: {e}")
            # Queue for retry
            metadata = self.format_relay_metadata(component, action, user_id, role, data)
            queue_file = self.queue_for_retry(metadata, data)
            print(f"[RelayMailer] Queued for retry: {queue_file}")
            return False
    
    def get_queued_items(self) -> List[Path]:
        """
        Get list of queued relay items
        
        Returns:
            List of queued file paths
        """
        return list(self.backup_path.glob("relay_*.json"))
    
    async def retry_queued_items(self, max_retries: int = 3) -> Dict[str, int]:
        """
        Retry sending queued relay emails
        
        Args:
            max_retries: Maximum retry attempts per item
        
        Returns:
            Dictionary with success/failure counts
        """
        queued = self.get_queued_items()
        results = {"success": 0, "failed": 0, "skipped": 0}
        
        for queue_file in queued:
            try:
                with open(queue_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                
                if entry.get("retry_count", 0) >= max_retries:
                    results["skipped"] += 1
                    continue
                
                metadata = entry["metadata"]
                data = entry["data"]
                
                success = await self.send_relay_email(
                    component=metadata["component"],
                    action=metadata["action"],
                    user_id=metadata["user_id"],
                    role=metadata["role"],
                    data=data
                )
                
                if success:
                    queue_file.unlink()  # Remove from queue
                    results["success"] += 1
                else:
                    # Increment retry count
                    entry["retry_count"] = entry.get("retry_count", 0) + 1
                    with open(queue_file, 'w', encoding='utf-8') as f:
                        json.dump(entry, f, indent=2)
                    results["failed"] += 1
                    
            except Exception as e:
                print(f"[RelayMailer] Error processing queue file {queue_file}: {e}")
                results["failed"] += 1
        
        return results
    
    async def archive_before_delete(
        self,
        component: str,
        user_id: str,
        role: str,
        record: Any
    ) -> bool:
        """
        Archive data before deletion (main entry point)
        
        Args:
            component: System component
            user_id: User ID
            role: User role
            record: Record to archive
        
        Returns:
            True if archive succeeded or not required, False if failed
        """
        return await self.send_relay_email(
            component=component,
            action="DELETE",
            user_id=user_id,
            role=role,
            data=record
        )
    
    def verify_archive(self, metadata: Dict[str, Any], data: Any) -> bool:
        """
        Verify archive integrity using checksum
        
        Args:
            metadata: Archive metadata
            data: Archived data
        
        Returns:
            True if checksum matches, False otherwise
        """
        expected_hash = metadata.get("payload_hash", "")
        actual_hash = self.calculate_checksum(data)
        
        return expected_hash == actual_hash


# Global relay mailer instance
relay_mailer = RelayMailer()
