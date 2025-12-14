"""
Brain CLI - Operator CLI for SR-AIbridge Sovereign Brain
Command-line interface for brain ledger management
"""
import sys
import json
import argparse
from typing import Dict, Any
from tabulate import tabulate
from datetime import datetime

from .brain import create_brain_ledger, BrainLedger
from .keys import SovereignKeys, initialize_admiral_keys
from .signer import create_signer


class BrainCLI:
    """Command-line interface for brain operations"""
    
    def __init__(self, db_path: str = "./brain.sqlite", key_dir: str = "./keys"):
        self.brain = create_brain_ledger(db_path)
        self.keys = initialize_admiral_keys(key_dir)
        self.signer = create_signer(key_dir)
    
    def cmd_add(self, args):
        """Add a new memory entry"""
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("❌ Invalid JSON metadata")
                return 1
        
        entry_id = self.brain.add_memory(
            content=args.content,
            category=args.category,
            classification=args.classification,
            metadata=metadata,
            sign=not args.no_sign
        )
        
        print(f"✅ Added memory entry {entry_id}")
        if not args.no_sign:
            print("🔒 Entry signed with Admiral key")
        
        return 0
    
    def cmd_search(self, args):
        """Search memory entries"""
        memories = self.brain.search_memories(
            query=args.query,
            category=args.category,
            classification=args.classification,
            limit=args.limit,
            offset=args.offset
        )
        
        if not memories:
            print("No memories found")
            return 0
        
        if args.format == "table":
            headers = ["ID", "Category", "Classification", "Content", "Created"]
            rows = []
            for memory in memories:
                content = memory.content[:50] + "..." if len(memory.content) > 50 else memory.content
                created = memory.created_at.strftime("%Y-%m-%d %H:%M") if isinstance(memory.created_at, datetime) else memory.created_at
                rows.append([memory.id, memory.category, memory.classification, content, created])
            
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        
        elif args.format == "json":
            output = []
            for memory in memories:
                output.append({
                    "id": memory.id,
                    "content": memory.content,
                    "category": memory.category,
                    "classification": memory.classification,
                    "created_at": memory.created_at.isoformat() if isinstance(memory.created_at, datetime) else memory.created_at,
                    "signed": bool(memory.signed_hash)
                })
            print(json.dumps(output, indent=2))
        
        else:  # detailed format
            for memory in memories:
                print(f"\n🧠 Memory Entry {memory.id}")
                print(f"   Category: {memory.category}")
                print(f"   Classification: {memory.classification}")
                print(f"   Created: {memory.created_at}")
                print(f"   Signed: {'Yes' if memory.signed_hash else 'No'}")
                print(f"   Content: {memory.content}")
                if args.show_metadata:
                    metadata = json.loads(memory.metadata) if isinstance(memory.metadata, str) else memory.metadata
                    print(f"   Metadata: {json.dumps(metadata, indent=4)}")
        
        return 0
    
    def cmd_get(self, args):
        """Get a specific memory entry"""
        memory = self.brain.get_memory(args.id)
        if not memory:
            print(f"❌ Memory entry {args.id} not found")
            return 1
        
        print(f"🧠 Memory Entry {memory.id}")
        print(f"   Category: {memory.category}")
        print(f"   Classification: {memory.classification}")
        print(f"   Created: {memory.created_at}")
        print(f"   Updated: {memory.updated_at}")
        print(f"   Signed: {'Yes' if memory.signed_hash else 'No'}")
        print(f"   Content: {memory.content}")
        
        if args.show_metadata:
            metadata = json.loads(memory.metadata) if isinstance(memory.metadata, str) else memory.metadata
            print(f"   Metadata: {json.dumps(metadata, indent=4)}")
        
        if args.show_signature and memory.signed_hash:
            print(f"   Hash: {memory.signed_hash}")
            if memory.signature_data:
                sig_data = json.loads(memory.signature_data)
                print(f"   Signature: {sig_data.get('data', 'N/A')[:32]}...")
        
        return 0
    
    def cmd_update(self, args):
        """Update a memory entry"""
        metadata = None
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("❌ Invalid JSON metadata")
                return 1
        
        success = self.brain.update_memory(
            entry_id=args.id,
            content=args.content,
            category=args.category,
            classification=args.classification,
            metadata=metadata,
            resign=not args.no_resign
        )
        
        if success:
            print(f"✅ Updated memory entry {args.id}")
            if not args.no_resign:
                print("🔒 Entry re-signed with Admiral key")
        else:
            print(f"❌ Failed to update memory entry {args.id}")
            return 1
        
        return 0
    
    def cmd_delete(self, args):
        """Delete a memory entry"""
        if not args.force:
            memory = self.brain.get_memory(args.id)
            if not memory:
                print(f"❌ Memory entry {args.id} not found")
                return 1
            
            print(f"🧠 Memory Entry {args.id}")
            print(f"   Content: {memory.content[:100]}...")
            
            confirm = input("Are you sure you want to delete this entry? (y/N): ")
            if confirm.lower() != 'y':
                print("Deletion cancelled")
                return 0
        
        success = self.brain.delete_memory(args.id)
        if success:
            print(f"✅ Deleted memory entry {args.id}")
        else:
            print(f"❌ Failed to delete memory entry {args.id}")
            return 1
        
        return 0
    
    def cmd_stats(self, args):
        """Show brain statistics"""
        stats = self.brain.get_statistics()
        
        print("🧠 Sovereign Brain Statistics")
        print(f"   Total memories: {stats['total_memories']}")
        print(f"   Signed memories: {stats['signed_memories']}")
        print(f"   Unsigned memories: {stats['unsigned_memories']}")
        print(f"   Recent activity (7 days): {stats['recent_activity']}")
        print(f"   Database size: {stats['database_size']} bytes")
        
        if stats['categories']:
            print("\n📂 Categories:")
            for category, count in stats['categories'].items():
                print(f"   {category}: {count}")
        
        if stats['classifications']:
            print("\n🔒 Classifications:")
            for classification, count in stats['classifications'].items():
                print(f"   {classification}: {count}")
        
        if args.show_metadata and stats['brain_metadata']:
            print("\n⚙️ Brain Metadata:")
            for key, value in stats['brain_metadata'].items():
                print(f"   {key}: {value}")
        
        return 0
    
    def cmd_export(self, args):
        """Export brain data"""
        export_data = self.brain.export_memories(
            category=args.category,
            classification=args.classification,
            include_signatures=not args.no_signatures
        )
        
        # Sign the export if requested
        if not args.no_sign:
            signed_export = self.signer.sign_payload(export_data)
            export_data = signed_export
        
        output_file = args.output or f"brain_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Exported {export_data.get('payload', export_data)['memory_count']} memories to {output_file}")
        if not args.no_sign:
            print("🔒 Export signed with Admiral key")
        
        return 0
    
    def cmd_verify(self, args):
        """Verify memory signatures"""
        results = self.brain.verify_memory_signatures()
        
        print("🔒 Signature Verification Results")
        print(f"   Total checked: {results['total_checked']}")
        print(f"   Valid signatures: {results['valid_signatures']}")
        print(f"   Invalid signatures: {results['invalid_signatures']}")
        print(f"   Unsigned memories: {results['unsigned_memories']}")
        
        if results['invalid_signatures'] > 0 and args.show_details:
            print("\n❌ Invalid Signatures:")
            for detail in results['verification_details']:
                if not detail['valid']:
                    print(f"   Entry {detail['entry_id']}: {detail['message']}")
        
        return 0
    
    def cmd_keys(self, args):
        """Key management operations"""
        if args.key_action == "list":
            keys = self.keys.list_keys()
            if not keys:
                print("No keys found")
                return 0
            
            headers = ["Name", "Created", "Public Key"]
            rows = []
            for key_info in keys:
                rows.append([
                    key_info['name'],
                    key_info['created_at'][:19],  # Truncate timestamp
                    key_info['public_key_hex'][:32] + "..."
                ])
            
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        
        elif args.key_action == "info":
            name = args.key_name or "admiral"
            info = self.keys.get_public_key_info(name)
            if not info:
                print(f"❌ Key '{name}' not found")
                return 1
            
            print(f"🔑 Key Information: {info['name']}")
            print(f"   Created: {info['created_at']}")
            print(f"   Public Key: {info['public_key']}")
            print(f"   Hex: {info['public_key_hex']}")
        
        elif args.key_action == "generate":
            name = args.key_name or "admiral"
            signing_key, verify_key = self.keys.generate_keypair()
            key_file = self.keys.save_keypair(signing_key, name)
            print(f"✅ Generated new keypair: {name}")
            print(f"   Saved to: {key_file}")
            print(f"   Public key: {verify_key.encode().hex()[:32]}...")
        
        elif args.key_action == "rotate":
            old_name = args.key_name or "admiral"
            new_file, archived_file = self.keys.rotate_keys(old_name)
            print(f"✅ Rotated keys for: {old_name}")
            print(f"   New key: {new_file}")
            if archived_file:
                print(f"   Archived: {archived_file}")
        
        return 0


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="SR-AIbridge Sovereign Brain CLI")
    parser.add_argument("--db", default="./brain.sqlite", help="Brain database path")
    parser.add_argument("--keys", default="./keys", help="Keys directory path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new memory entry")
    add_parser.add_argument("content", help="Memory content")
    add_parser.add_argument("--category", default="general", help="Memory category")
    add_parser.add_argument("--classification", default="public", help="Memory classification")
    add_parser.add_argument("--metadata", help="JSON metadata")
    add_parser.add_argument("--no-sign", action="store_true", help="Don't sign the entry")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search memory entries")
    search_parser.add_argument("--query", help="Search query")
    search_parser.add_argument("--category", help="Filter by category")
    search_parser.add_argument("--classification", help="Filter by classification")
    search_parser.add_argument("--limit", type=int, default=20, help="Limit results")
    search_parser.add_argument("--offset", type=int, default=0, help="Offset results")
    search_parser.add_argument("--format", choices=["table", "json", "detailed"], default="table", help="Output format")
    search_parser.add_argument("--show-metadata", action="store_true", help="Show metadata")
    
    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific memory entry")
    get_parser.add_argument("id", type=int, help="Memory entry ID")
    get_parser.add_argument("--show-metadata", action="store_true", help="Show metadata")
    get_parser.add_argument("--show-signature", action="store_true", help="Show signature info")
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update a memory entry")
    update_parser.add_argument("id", type=int, help="Memory entry ID")
    update_parser.add_argument("--content", help="New content")
    update_parser.add_argument("--category", help="New category")
    update_parser.add_argument("--classification", help="New classification")
    update_parser.add_argument("--metadata", help="JSON metadata to merge")
    update_parser.add_argument("--no-resign", action="store_true", help="Don't re-sign the entry")
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a memory entry")
    delete_parser.add_argument("id", type=int, help="Memory entry ID")
    delete_parser.add_argument("--force", action="store_true", help="Skip confirmation")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show brain statistics")
    stats_parser.add_argument("--show-metadata", action="store_true", help="Show brain metadata")
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export brain data")
    export_parser.add_argument("--output", help="Output file path")
    export_parser.add_argument("--category", help="Filter by category")
    export_parser.add_argument("--classification", help="Filter by classification")
    export_parser.add_argument("--no-signatures", action="store_true", help="Exclude signatures")
    export_parser.add_argument("--no-sign", action="store_true", help="Don't sign the export")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify memory signatures")
    verify_parser.add_argument("--show-details", action="store_true", help="Show verification details")
    
    # Keys command
    keys_parser = subparsers.add_parser("keys", help="Key management")
    keys_parser.add_argument("key_action", choices=["list", "info", "generate", "rotate"], help="Key action")
    keys_parser.add_argument("--key-name", help="Key name (default: admiral)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        cli = BrainCLI(args.db, args.keys)
        
        if args.command == "add":
            return cli.cmd_add(args)
        elif args.command == "search":
            return cli.cmd_search(args)
        elif args.command == "get":
            return cli.cmd_get(args)
        elif args.command == "update":
            return cli.cmd_update(args)
        elif args.command == "delete":
            return cli.cmd_delete(args)
        elif args.command == "stats":
            return cli.cmd_stats(args)
        elif args.command == "export":
            return cli.cmd_export(args)
        elif args.command == "verify":
            return cli.cmd_verify(args)
        elif args.command == "keys":
            return cli.cmd_keys(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())