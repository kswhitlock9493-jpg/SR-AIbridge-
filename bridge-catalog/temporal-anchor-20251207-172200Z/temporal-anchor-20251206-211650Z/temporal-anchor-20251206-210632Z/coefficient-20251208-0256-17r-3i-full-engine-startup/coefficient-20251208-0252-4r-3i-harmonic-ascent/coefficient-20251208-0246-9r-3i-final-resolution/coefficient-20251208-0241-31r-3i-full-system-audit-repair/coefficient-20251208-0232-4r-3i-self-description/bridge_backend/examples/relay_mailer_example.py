"""
Example: Using the Secure Data Relay Protocol

This example demonstrates how to integrate the relay_mailer
into your deletion workflows to ensure zero data loss.

Run from bridge_backend directory:
    python examples/relay_mailer_example.py
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.relay_mailer import relay_mailer


async def example_vault_deletion():
    """
    Example: Archive vault data before deletion
    """
    print("\n=== Example: Vault Data Deletion ===")
    
    # Data to be deleted
    vault_record = {
        "id": 12345,
        "mission_name": "Operation Phoenix",
        "logs": ["Log entry 1", "Log entry 2"],
        "timestamp": "2024-10-04T12:00:00Z"
    }
    
    # Archive before deletion
    print("📧 Archiving data before deletion...")
    success = await relay_mailer.archive_before_delete(
        component="vault",
        user_id="captain_alpha",
        role="captain",
        record=vault_record
    )
    
    if success:
        print("✅ Data archived successfully (or relay disabled)")
        # Now safe to delete
        print("🗑️  Proceeding with deletion...")
        # delete_vault_record(12345)
    else:
        print("❌ Archive failed - deletion postponed")
        # DO NOT delete - data would be lost
        return False
    
    return True


async def example_brain_memory_expiration():
    """
    Example: Archive brain memories before TTL expiration
    """
    print("\n=== Example: Brain Memory Expiration ===")
    
    # Memory about to expire
    memory_record = {
        "id": "mem_67890",
        "category": "mission_context",
        "content": "Strategic analysis of mission objectives...",
        "created_at": "2024-10-03T00:00:00Z",
        "expires_at": "2024-10-04T14:00:00Z"
    }
    
    print("📧 Archiving memory before expiration...")
    success = await relay_mailer.archive_before_delete(
        component="brain",
        user_id="agent_omega",
        role="agent",
        record=memory_record
    )
    
    if success:
        print("✅ Memory archived (7-hour agent retention)")
        # Allow expiration
        print("⏱️  Memory can now expire safely")
    
    return success


async def example_mission_deletion():
    """
    Example: Archive mission before deletion with Admiral oversight
    """
    print("\n=== Example: Mission Deletion (Admiral) ===")
    
    mission_record = {
        "id": "mission_001",
        "title": "Critical Infrastructure Assessment",
        "captain": "captain_beta",
        "agents": ["agent_001", "agent_002"],
        "status": "completed",
        "completion_date": "2024-10-04T10:30:00Z",
        "results": "Mission successful - all objectives met"
    }
    
    print("📧 Archiving mission (permanent Admiral retention)...")
    success = await relay_mailer.archive_before_delete(
        component="missions",
        user_id="admiral_prime",
        role="admiral",
        record=mission_record
    )
    
    if success:
        print("✅ Mission archived permanently")
        print("🗑️  Safe to delete from active database")
    
    return success


async def example_verify_archive():
    """
    Example: Verify archive integrity
    """
    print("\n=== Example: Archive Verification ===")
    
    test_data = {"test": "verification"}
    
    # Create metadata
    metadata = relay_mailer.format_relay_metadata(
        component="test",
        action="DELETE",
        user_id="test_user",
        role="captain",
        data=test_data
    )
    
    print(f"📋 Generated metadata with checksum: {metadata['payload_hash'][:16]}...")
    
    # Verify
    is_valid = relay_mailer.verify_archive(metadata, test_data)
    
    if is_valid:
        print("✅ Archive integrity verified")
    else:
        print("❌ Archive integrity check failed")
    
    return is_valid


async def example_queue_retry():
    """
    Example: Handle network failures with queue retry
    """
    print("\n=== Example: Queue Retry Mechanism ===")
    
    # Check for queued items (from previous failed sends)
    queued = relay_mailer.get_queued_items()
    print(f"📋 Found {len(queued)} queued items")
    
    if len(queued) > 0:
        print("♻️  Retrying queued items...")
        results = await relay_mailer.retry_queued_items(max_retries=3)
        
        print(f"✅ Success: {results['success']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⏭️  Skipped (max retries): {results['skipped']}")
    else:
        print("✅ No queued items to retry")
    
    return True


async def example_role_based_retention():
    """
    Example: Demonstrate role-based retention policies
    """
    print("\n=== Example: Role-Based Retention Policies ===")
    
    test_data = {"example": "data"}
    
    # Admiral - Permanent
    meta_admiral = relay_mailer.format_relay_metadata(
        "test", "DELETE", "admiral_1", "admiral", test_data
    )
    print(f"👑 Admiral retention: {meta_admiral['retention_hours']} hours (permanent)")
    
    # Captain - 14 hours
    meta_captain = relay_mailer.format_relay_metadata(
        "test", "DELETE", "captain_1", "captain", test_data
    )
    print(f"👨‍✈️ Captain retention: {meta_captain['retention_hours']} hours")
    
    # Agent - 7 hours
    meta_agent = relay_mailer.format_relay_metadata(
        "test", "DELETE", "agent_1", "agent", test_data
    )
    print(f"🤖 Agent retention: {meta_agent['retention_hours']} hours")
    
    return True


async def main():
    """
    Run all examples
    """
    print("=" * 60)
    print("🚀 SR-AIbridge Secure Data Relay Protocol Examples")
    print("=" * 60)
    
    print(f"\n⚙️  Relay Status: {'✅ ENABLED' if relay_mailer.enabled else '❌ DISABLED'}")
    print(f"📧 Relay Email: {relay_mailer.relay_email}")
    print(f"📂 Backup Path: {relay_mailer.backup_path}")
    
    if not relay_mailer.enabled:
        print("\n⚠️  Note: Relay is disabled. Set RELAY_ENABLED=true in .env to activate.")
        print("    When disabled, archive operations succeed without sending email.")
    
    # Run examples
    await example_vault_deletion()
    await example_brain_memory_expiration()
    await example_mission_deletion()
    await example_verify_archive()
    await example_queue_retry()
    await example_role_based_retention()
    
    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Note: To actually send emails, you need to:
    # 1. Set RELAY_ENABLED=true in .env
    # 2. Configure SMTP credentials (Gmail App Password recommended)
    # 3. Ensure network connectivity to SMTP server
    
    asyncio.run(main())
