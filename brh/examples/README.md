# BRH Examples

This directory contains example scripts and tests for the Bridge Runtime Handler.

## Scripts

### generate_forge_root.sh

Generates a valid FORGE_DOMINION_ROOT environment variable with HMAC signature.

**Usage:**
```bash
./brh/examples/generate_forge_root.sh [env] [seal]
```

**Examples:**
```bash
# Development with default seal
./brh/examples/generate_forge_root.sh dev dev-seal

# Production with custom seal
./brh/examples/generate_forge_root.sh prod "my-secret-seal-key"
```

The script will output the export commands you need to run.

### test_forge_auth.py

Tests the forge authentication flow including parsing, verification, and token minting.

**Usage:**
```bash
# First, set the environment variables
export FORGE_DOMINION_ROOT="dominion://sovereign.bridge?env=dev&epoch=1234567890&sig=abc123..."
export DOMINION_SEAL="dev-seal"

# Then run the test
python brh/examples/test_forge_auth.py
```

**What it tests:**
- FORGE_DOMINION_ROOT parsing
- Signature verification
- Time skew validation
- Ephemeral token minting

## Quick Start

1. Generate a Forge root:
   ```bash
   ./brh/examples/generate_forge_root.sh
   ```

2. Copy and run the export commands from the output

3. Test the authentication:
   ```bash
   python brh/examples/test_forge_auth.py
   ```

4. If all tests pass, you can run the full BRH:
   ```bash
   python -m brh.run
   ```
