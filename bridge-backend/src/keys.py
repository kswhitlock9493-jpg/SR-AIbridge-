"""
Ed25519 Key Utilities for SR-AIbridge Sovereign Brain
Local-first cryptographic operations with no cloud dependencies
"""
import os
import base64
from typing import Tuple, Optional
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder, RawEncoder
from nacl.exceptions import BadSignatureError
import json
from datetime import datetime


class SovereignKeys:
    """Ed25519 key management for the Sovereign Brain"""
    
    def __init__(self, key_dir: str = "./keys"):
        self.key_dir = key_dir
        os.makedirs(key_dir, exist_ok=True)
    
    def generate_keypair(self) -> Tuple[SigningKey, VerifyKey]:
        """Generate a new Ed25519 keypair"""
        signing_key = SigningKey.generate()
        verify_key = signing_key.verify_key
        return signing_key, verify_key
    
    def save_keypair(self, signing_key: SigningKey, name: str = "admiral") -> str:
        """Save a keypair to disk with metadata"""
        verify_key = signing_key.verify_key
        
        # Create keypair metadata
        keypair_data = {
            "name": name,
            "created_at": datetime.utcnow().isoformat(),
            "signing_key": signing_key.encode(encoder=Base64Encoder).decode('utf-8'),
            "verify_key": verify_key.encode(encoder=Base64Encoder).decode('utf-8'),
            "public_key_hex": verify_key.encode(encoder=RawEncoder).hex()
        }
        
        # Save to file
        key_file = os.path.join(self.key_dir, f"{name}_keypair.json")
        with open(key_file, 'w') as f:
            json.dump(keypair_data, f, indent=2)
        
        # Also save public key separately for easy access
        pub_file = os.path.join(self.key_dir, f"{name}_public.key")
        with open(pub_file, 'w') as f:
            f.write(verify_key.encode(encoder=Base64Encoder).decode('utf-8'))
        
        return key_file
    
    def load_signing_key(self, name: str = "admiral") -> Optional[SigningKey]:
        """Load signing key from disk"""
        key_file = os.path.join(self.key_dir, f"{name}_keypair.json")
        if not os.path.exists(key_file):
            return None
        
        try:
            with open(key_file, 'r') as f:
                data = json.load(f)
            
            signing_key_bytes = base64.b64decode(data["signing_key"])
            return SigningKey(signing_key_bytes)
        except Exception:
            return None
    
    def load_verify_key(self, name: str = "admiral") -> Optional[VerifyKey]:
        """Load verify key from disk"""
        key_file = os.path.join(self.key_dir, f"{name}_keypair.json")
        if not os.path.exists(key_file):
            return None
        
        try:
            with open(key_file, 'r') as f:
                data = json.load(f)
            
            verify_key_bytes = base64.b64decode(data["verify_key"])
            return VerifyKey(verify_key_bytes)
        except Exception:
            return None
    
    def get_public_key_info(self, name: str = "admiral") -> Optional[dict]:
        """Get public key information"""
        key_file = os.path.join(self.key_dir, f"{name}_keypair.json")
        if not os.path.exists(key_file):
            return None
        
        try:
            with open(key_file, 'r') as f:
                data = json.load(f)
            
            return {
                "name": data["name"],
                "created_at": data["created_at"],
                "public_key": data["verify_key"],
                "public_key_hex": data["public_key_hex"]
            }
        except Exception:
            return None
    
    def list_keys(self) -> list:
        """List all available keypairs"""
        keys = []
        if not os.path.exists(self.key_dir):
            return keys
        
        for filename in os.listdir(self.key_dir):
            if filename.endswith('_keypair.json'):
                name = filename.replace('_keypair.json', '')
                info = self.get_public_key_info(name)
                if info:
                    keys.append(info)
        
        return keys
    
    def rotate_keys(self, old_name: str = "admiral", new_name: str = None) -> Tuple[str, str]:
        """Rotate keys by generating new ones and archiving old ones"""
        if new_name is None:
            new_name = f"{old_name}_new"
        
        # Generate new keypair
        signing_key, verify_key = self.generate_keypair()
        new_key_file = self.save_keypair(signing_key, new_name)
        
        # Archive old keypair if it exists
        old_key_file = os.path.join(self.key_dir, f"{old_name}_keypair.json")
        archived_file = None
        if os.path.exists(old_key_file):
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            archived_file = os.path.join(self.key_dir, f"{old_name}_archived_{timestamp}.json")
            os.rename(old_key_file, archived_file)
        
        return new_key_file, archived_file


def initialize_admiral_keys(key_dir: str = "./keys") -> SovereignKeys:
    """Initialize admiral keys if they don't exist"""
    keys = SovereignKeys(key_dir)
    
    # Check if admiral keys exist
    if keys.load_signing_key("admiral") is None:
        # Generate new admiral keypair
        signing_key, verify_key = keys.generate_keypair()
        keys.save_keypair(signing_key, "admiral")
        print(f"🔑 Generated new Admiral keypair")
    
    return keys


if __name__ == "__main__":
    # CLI for key management
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python keys.py [generate|list|info] [name]")
        sys.exit(1)
    
    action = sys.argv[1]
    keys = SovereignKeys()
    
    if action == "generate":
        name = sys.argv[2] if len(sys.argv) > 2 else "admiral"
        signing_key, verify_key = keys.generate_keypair()
        key_file = keys.save_keypair(signing_key, name)
        print(f"Generated keypair: {key_file}")
    
    elif action == "list":
        key_list = keys.list_keys()
        print("Available keypairs:")
        for key_info in key_list:
            print(f"  {key_info['name']}: {key_info['public_key_hex'][:16]}...")
    
    elif action == "info":
        name = sys.argv[2] if len(sys.argv) > 2 else "admiral"
        info = keys.get_public_key_info(name)
        if info:
            print(f"Key: {info['name']}")
            print(f"Created: {info['created_at']}")
            print(f"Public Key: {info['public_key']}")
            print(f"Hex: {info['public_key_hex']}")
        else:
            print(f"Key '{name}' not found")