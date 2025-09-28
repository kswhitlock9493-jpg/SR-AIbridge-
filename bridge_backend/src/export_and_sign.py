"""
Dock-Day Export with Manifest Signing for SR-AIbridge Sovereign Brain
Complete system export with cryptographic attestation
"""
import os
import json
import shutil
import zipfile
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from .brain import create_brain_ledger
from .signer import create_signer
from .keys import initialize_admiral_keys


class DockDayExporter:
    """Dock-Day export manager with manifest signing"""
    
    def __init__(self, brain_db: str = "./brain.sqlite", key_dir: str = "./keys", 
                 export_dir: str = "./dock_day_exports"):
        self.brain = create_brain_ledger(brain_db)
        self.keys = initialize_admiral_keys(key_dir)
        self.signer = create_signer(key_dir)
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
    
    def create_dock_day_drop(self, drop_name: str = None, include_database: bool = True,
                           include_keys: bool = False, compress: bool = True) -> Dict[str, Any]:
        """Create a complete Dock-Day drop with manifest"""
        if drop_name is None:
            drop_name = f"dock_day_drop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        drop_dir = self.export_dir / drop_name
        drop_dir.mkdir(exist_ok=True)
        
        manifest_items = []
        
        try:
            # 1. Export brain memories
            brain_export = self.brain.export_memories(include_signatures=True)
            brain_file = drop_dir / "brain_memories.json"
            with open(brain_file, 'w') as f:
                json.dump(brain_export, f, indent=2)
            
            manifest_items.append({
                "type": "brain_memories",
                "filename": "brain_memories.json",
                "size": brain_file.stat().st_size,
                "memory_count": brain_export['memory_count'],
                "checksum": self._calculate_file_checksum(brain_file)
            })
            
            # 2. Copy brain database if requested
            if include_database and os.path.exists(self.brain.db_path):
                db_dest = drop_dir / "brain.sqlite"
                shutil.copy2(self.brain.db_path, db_dest)
                
                manifest_items.append({
                    "type": "brain_database",
                    "filename": "brain.sqlite",
                    "size": db_dest.stat().st_size,
                    "checksum": self._calculate_file_checksum(db_dest)
                })
            
            # 3. Export brain statistics
            stats = self.brain.get_statistics()
            stats_file = drop_dir / "brain_statistics.json"
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            manifest_items.append({
                "type": "brain_statistics",
                "filename": "brain_statistics.json",
                "size": stats_file.stat().st_size,
                "checksum": self._calculate_file_checksum(stats_file)
            })
            
            # 4. Export public keys (always safe to include)
            public_keys = []
            for key_info in self.keys.list_keys():
                public_keys.append({
                    "name": key_info['name'],
                    "created_at": key_info['created_at'],
                    "public_key": key_info['public_key'],
                    "public_key_hex": key_info['public_key_hex']
                })
            
            if public_keys:
                keys_file = drop_dir / "public_keys.json"
                with open(keys_file, 'w') as f:
                    json.dump(public_keys, f, indent=2)
                
                manifest_items.append({
                    "type": "public_keys",
                    "filename": "public_keys.json",
                    "size": keys_file.stat().st_size,
                    "key_count": len(public_keys),
                    "checksum": self._calculate_file_checksum(keys_file)
                })
            
            # 5. Include private keys if explicitly requested (dangerous!)
            if include_keys:
                keys_dir_dest = drop_dir / "keys"
                if os.path.exists(self.keys.key_dir):
                    shutil.copytree(self.keys.key_dir, keys_dir_dest)
                    
                    manifest_items.append({
                        "type": "private_keys",
                        "filename": "keys/",
                        "size": sum(f.stat().st_size for f in keys_dir_dest.rglob('*') if f.is_file()),
                        "warning": "CONTAINS PRIVATE KEYS - SECURE HANDLING REQUIRED",
                        "checksum": "directory"
                    })
            
            # 6. Export system information
            system_info = self._gather_system_info()
            system_file = drop_dir / "system_info.json"
            with open(system_file, 'w') as f:
                json.dump(system_info, f, indent=2)
            
            manifest_items.append({
                "type": "system_info",
                "filename": "system_info.json",
                "size": system_file.stat().st_size,
                "checksum": self._calculate_file_checksum(system_file)
            })
            
            # 7. Create and sign manifest
            manifest = self._create_manifest(drop_name, manifest_items, include_keys)
            signed_manifest = self.signer.sign_manifest(manifest)
            
            manifest_file = drop_dir / "dock_day_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(signed_manifest, f, indent=2)
            
            # 8. Create README
            readme_content = self._create_readme(drop_name, manifest, include_keys)
            readme_file = drop_dir / "README.md"
            with open(readme_file, 'w') as f:
                f.write(readme_content)
            
            # 9. Compress if requested
            archive_path = None
            if compress:
                archive_path = self._create_archive(drop_dir, drop_name)
            
            # Create result summary
            result = {
                "drop_name": drop_name,
                "drop_directory": str(drop_dir),
                "archive_path": str(archive_path) if archive_path else None,
                "manifest_signed": True,
                "items_count": len(manifest_items),
                "total_size": sum(item.get('size', 0) for item in manifest_items),
                "created_at": datetime.now().isoformat(),
                "manifest": signed_manifest,
                "warnings": ["CONTAINS PRIVATE KEYS - SECURE HANDLING REQUIRED"] if include_keys else []
            }
            
            return result
        
        except Exception as e:
            # Clean up on error
            if drop_dir.exists():
                shutil.rmtree(drop_dir)
            raise e
    
    def verify_dock_day_drop(self, drop_path: str) -> Dict[str, Any]:
        """Verify a Dock-Day drop manifest and contents"""
        drop_path = Path(drop_path)
        
        # Handle both directory and archive
        if drop_path.is_file() and drop_path.suffix == '.zip':
            # Extract to temporary directory for verification
            temp_dir = drop_path.parent / f"temp_verify_{drop_path.stem}"
            with zipfile.ZipFile(drop_path, 'r') as zip_file:
                zip_file.extractall(temp_dir)
            
            try:
                return self._verify_drop_directory(temp_dir)
            finally:
                shutil.rmtree(temp_dir)
        
        elif drop_path.is_dir():
            return self._verify_drop_directory(drop_path)
        
        else:
            return {
                "valid": False,
                "message": "Drop path is neither a directory nor a zip file",
                "details": {}
            }
    
    def _verify_drop_directory(self, drop_dir: Path) -> Dict[str, Any]:
        """Verify a drop directory"""
        manifest_file = drop_dir / "dock_day_manifest.json"
        
        if not manifest_file.exists():
            return {
                "valid": False,
                "message": "Manifest file not found",
                "details": {}
            }
        
        try:
            # Load and verify manifest signature
            with open(manifest_file, 'r') as f:
                signed_manifest = json.load(f)
            
            is_valid, message, details = self.signer.verify_manifest(signed_manifest)
            
            if not is_valid:
                return {
                    "valid": False,
                    "message": f"Manifest signature invalid: {message}",
                    "details": details
                }
            
            # Verify individual files
            manifest_payload = signed_manifest.get("payload", {})
            items = manifest_payload.get("items", [])
            
            file_verifications = []
            for item in items:
                filename = item.get("filename")
                expected_checksum = item.get("checksum")
                
                if filename == "keys/" or expected_checksum == "directory":
                    # Skip directory verification for now
                    file_verifications.append({
                        "filename": filename,
                        "status": "skipped",
                        "message": "Directory verification not implemented"
                    })
                    continue
                
                file_path = drop_dir / filename
                if not file_path.exists():
                    file_verifications.append({
                        "filename": filename,
                        "status": "missing",
                        "message": "File not found"
                    })
                    continue
                
                actual_checksum = self._calculate_file_checksum(file_path)
                if actual_checksum == expected_checksum:
                    file_verifications.append({
                        "filename": filename,
                        "status": "valid",
                        "message": "Checksum matches"
                    })
                else:
                    file_verifications.append({
                        "filename": filename,
                        "status": "invalid",
                        "message": f"Checksum mismatch: expected {expected_checksum}, got {actual_checksum}"
                    })
            
            # Summary
            valid_files = sum(1 for v in file_verifications if v["status"] == "valid")
            invalid_files = sum(1 for v in file_verifications if v["status"] == "invalid")
            missing_files = sum(1 for v in file_verifications if v["status"] == "missing")
            
            overall_valid = invalid_files == 0 and missing_files == 0
            
            return {
                "valid": overall_valid,
                "message": "Drop verification complete",
                "details": {
                    "manifest_valid": True,
                    "manifest_signer": details.get("signer"),
                    "manifest_signed_at": details.get("signed_at"),
                    "total_files": len(file_verifications),
                    "valid_files": valid_files,
                    "invalid_files": invalid_files,
                    "missing_files": missing_files,
                    "file_verifications": file_verifications
                }
            }
        
        except Exception as e:
            return {
                "valid": False,
                "message": f"Verification error: {str(e)}",
                "details": {}
            }
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        import hashlib
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def _create_manifest(self, drop_name: str, items: List[Dict[str, Any]], 
                        includes_private_keys: bool) -> Dict[str, Any]:
        """Create a manifest for the drop"""
        manifest = {
            "type": "dock_day_drop",
            "drop_name": drop_name,
            "created_at": datetime.now().isoformat(),
            "sovereign_brain_version": "1.0",
            "items": items,
            "item_count": len(items),
            "total_size": sum(item.get('size', 0) for item in items),
            "security_level": "CLASSIFIED" if includes_private_keys else "PUBLIC",
            "warnings": ["CONTAINS PRIVATE KEYS - SECURE HANDLING REQUIRED"] if includes_private_keys else [],
            "export_metadata": {
                "exporter": "SR-AIbridge Sovereign Brain",
                "export_version": "1.0",
                "export_purpose": "dock_day_drop"
            }
        }
        
        return manifest
    
    def _create_readme(self, drop_name: str, manifest: Dict[str, Any], 
                      includes_private_keys: bool) -> str:
        """Create a README for the drop"""
        warnings = ""
        if includes_private_keys:
            warnings = """
⚠️  SECURITY WARNING ⚠️
This drop contains PRIVATE KEYS. Handle with extreme care:
- Store in a secure location
- Limit access to authorized personnel only
- Consider encryption for transport/storage
- Never share or transmit over unsecured channels

"""
        
        readme = f"""# SR-AIbridge Dock-Day Drop: {drop_name}

{warnings}## Overview

This is a complete export of the SR-AIbridge Sovereign Brain system, created on {manifest['created_at']}.

## Contents

- **brain_memories.json**: Complete export of brain memory entries with signatures
- **brain.sqlite**: SQLite database file (if included)
- **brain_statistics.json**: System statistics and metadata
- **public_keys.json**: Public key information for verification
- **system_info.json**: System information at time of export
- **dock_day_manifest.json**: Signed manifest of all contents
- **keys/**: Private key directory (if included - SECURE HANDLING REQUIRED)

## Manifest Information

- **Items**: {manifest['item_count']} files/directories
- **Total Size**: {manifest['total_size']} bytes
- **Security Level**: {manifest['security_level']}
- **Manifest Hash**: {manifest.get('manifest_hash', 'N/A')}

## Verification

To verify this drop:

```bash
python export_and_sign.py verify {drop_name}
```

Or use the CLI:

```bash
python -m src.export_and_sign verify {drop_name}
```

## Usage

This drop can be used to:
1. Restore the Sovereign Brain system
2. Audit brain contents and signatures
3. Migrate to a new system
4. Archive brain state for compliance

## Admiral's Note

> "The scrolls are sealed with sovereign fire.  
> What was written in light, travels in shadow.  
> The Bridge remembers all."

---

Generated by SR-AIbridge Sovereign Brain v1.0
"""
        
        return readme
    
    def _gather_system_info(self) -> Dict[str, Any]:
        """Gather system information for the export"""
        import platform
        import sys
        
        return {
            "export_timestamp": datetime.now().isoformat(),
            "system": {
                "platform": platform.platform(),
                "python_version": sys.version,
                "architecture": platform.architecture(),
                "hostname": platform.node()
            },
            "brain_info": {
                "database_path": self.brain.db_path,
                "database_exists": os.path.exists(self.brain.db_path),
                "key_directory": self.keys.key_dir,
                "available_keys": len(self.keys.list_keys())
            },
            "export_info": {
                "exporter_version": "1.0",
                "export_format": "dock_day_drop",
                "signed": True
            }
        }
    
    def _create_archive(self, drop_dir: Path, drop_name: str) -> Path:
        """Create a ZIP archive of the drop"""
        archive_path = drop_dir.parent / f"{drop_name}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in drop_dir.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path for archive
                    relative_path = file_path.relative_to(drop_dir)
                    zipf.write(file_path, relative_path)
        
        return archive_path


def create_dock_day_exporter(brain_db: str = "./brain.sqlite", key_dir: str = "./keys") -> DockDayExporter:
    """Create a Dock-Day exporter with initialized components"""
    return DockDayExporter(brain_db, key_dir)


if __name__ == "__main__":
    # CLI for export operations
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Dock-Day Export with Manifest Signing")
    parser.add_argument("action", choices=["export", "verify"], help="Action to perform")
    parser.add_argument("--name", help="Drop name for export")
    parser.add_argument("--path", help="Path for verification")
    parser.add_argument("--no-database", action="store_true", help="Don't include database file")
    parser.add_argument("--include-keys", action="store_true", help="Include private keys (DANGEROUS)")
    parser.add_argument("--no-compress", action="store_true", help="Don't create ZIP archive")
    parser.add_argument("--brain-db", default="./brain.sqlite", help="Brain database path")
    parser.add_argument("--key-dir", default="./keys", help="Keys directory")
    
    args = parser.parse_args()
    
    exporter = create_dock_day_exporter(args.brain_db, args.key_dir)
    
    if args.action == "export":
        result = exporter.create_dock_day_drop(
            drop_name=args.name,
            include_database=not args.no_database,
            include_keys=args.include_keys,
            compress=not args.no_compress
        )
        
        print(f"✅ Created Dock-Day drop: {result['drop_name']}")
        print(f"   Directory: {result['drop_directory']}")
        if result['archive_path']:
            print(f"   Archive: {result['archive_path']}")
        print(f"   Items: {result['items_count']}")
        print(f"   Size: {result['total_size']} bytes")
        print(f"   Manifest signed: {'Yes' if result['manifest_signed'] else 'No'}")
        
        for warning in result['warnings']:
            print(f"   ⚠️  {warning}")
    
    elif args.action == "verify":
        if not args.path:
            print("--path required for verification")
            sys.exit(1)
        
        result = exporter.verify_dock_day_drop(args.path)
        
        if result['valid']:
            print(f"✅ Drop verification passed")
        else:
            print(f"❌ Drop verification failed: {result['message']}")
        
        details = result.get('details', {})
        if details:
            print(f"   Manifest valid: {details.get('manifest_valid', False)}")
            print(f"   Total files: {details.get('total_files', 0)}")
            print(f"   Valid files: {details.get('valid_files', 0)}")
            print(f"   Invalid files: {details.get('invalid_files', 0)}")
            print(f"   Missing files: {details.get('missing_files', 0)}")
    
    else:
        parser.print_help()
        sys.exit(1)