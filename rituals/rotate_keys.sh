#!/bin/bash
# SR-AIbridge Key Rotation Ritual
# Sacred ceremony for Admiral key rotation

set -e

echo "🔑 ===== SR-AIbridge Key Rotation Ritual ====="
echo "   Admiral's sovereign keys shall be renewed"
echo "   The old shall be archived, the new shall reign"
echo ""

# Configuration
BRAIN_DIR=${BRAIN_DIR:-"./bridge-backend"}
KEY_DIR=${KEY_DIR:-"$BRAIN_DIR/keys"}
BACKUP_DIR=${BACKUP_DIR:-"$BRAIN_DIR/key_backups"}
LOG_FILE=${LOG_FILE:-"$BRAIN_DIR/key_rotation.log"}

# Create necessary directories
mkdir -p "$KEY_DIR"
mkdir -p "$BACKUP_DIR"

# Logging function
log_entry() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_entry "🔑 Key rotation ritual initiated"
log_entry "   Key directory: $KEY_DIR"
log_entry "   Backup directory: $BACKUP_DIR"

# Check if Python environment is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not found"
    exit 1
fi

# Change to backend directory
cd "$BRAIN_DIR"

# Check if current keys exist
if [ -f "$KEY_DIR/admiral_keypair.json" ]; then
    log_entry "🔍 Current Admiral keys found"
    
    # Show current key info
    echo "📋 Current Admiral Key Information:"
    python3 -m src.keys info admiral || {
        log_entry "❌ Failed to read current key info"
        exit 1
    }
    
    # Create timestamped backup
    TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
    BACKUP_NAME="admiral_backup_$TIMESTAMP"
    
    log_entry "💾 Creating backup: $BACKUP_NAME"
    
    # Copy current keypair to backup
    cp "$KEY_DIR/admiral_keypair.json" "$BACKUP_DIR/${BACKUP_NAME}_keypair.json"
    if [ -f "$KEY_DIR/admiral_public.key" ]; then
        cp "$KEY_DIR/admiral_public.key" "$BACKUP_DIR/${BACKUP_NAME}_public.key"
    fi
    
    log_entry "✅ Backup created successfully"
    
    # Prompt for confirmation
    echo ""
    echo "⚠️  WARNING: This will replace the current Admiral keys"
    echo "   Current keys have been backed up to: $BACKUP_DIR/$BACKUP_NAME*"
    echo ""
    read -p "Proceed with key rotation? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        log_entry "🚫 Key rotation cancelled by user"
        echo "Key rotation cancelled"
        exit 0
    fi
    
else
    log_entry "ℹ️  No existing Admiral keys found - generating initial keypair"
fi

# Generate new keys using the keys module
log_entry "🔧 Generating new Admiral keypair"
echo "🔧 Generating new Admiral keypair..."

python3 -m src.keys generate admiral || {
    log_entry "❌ Failed to generate new keypair"
    exit 1
}

log_entry "✅ New Admiral keypair generated"

# Show new key information
echo ""
echo "🔑 New Admiral Key Information:"
python3 -m src.keys info admiral || {
    log_entry "❌ Failed to read new key info"
    exit 1
}

# Verify the new keys work by testing signing
log_entry "🔐 Testing new keys with signature verification"
echo "🔐 Testing new keys..."

# Create a test payload
TEST_FILE="/tmp/test_payload_$$.json"
cat > "$TEST_FILE" << EOF
{
    "test": true,
    "message": "Key rotation test",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.%03NZ)"
}
EOF

# Test signing
python3 -m src.signer sign "$TEST_FILE" admiral || {
    log_entry "❌ Failed to test new keys"
    rm -f "$TEST_FILE"
    exit 1
}

# Test verification
SIGNED_FILE="${TEST_FILE%.json}_signed.json"
python3 -m src.signer verify "$SIGNED_FILE" || {
    log_entry "❌ Failed to verify signature with new keys"
    rm -f "$TEST_FILE" "$SIGNED_FILE"
    exit 1
}

# Clean up test files
rm -f "$TEST_FILE" "$SIGNED_FILE"

log_entry "✅ New keys verified successfully"

# Update brain database with key rotation event
if [ -f "brain.sqlite" ]; then
    log_entry "📝 Recording key rotation in brain ledger"
    python3 -m src.brain_cli add "Admiral keys rotated - new sovereign keypair generated" \
        --category "security" \
        --classification "operational" \
        --metadata "{\"event_type\": \"key_rotation\", \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%S.%03NZ)\", \"backup_created\": true}" || {
        log_entry "⚠️  Failed to record key rotation in brain ledger"
    }
fi

# Final summary
echo ""
echo "🎉 ===== Key Rotation Ritual Complete ====="
echo "   ✅ New Admiral keypair generated"
echo "   ✅ Keys tested and verified"
if [ -f "$BACKUP_DIR/${BACKUP_NAME}_keypair.json" ]; then
    echo "   ✅ Old keys backed up to: $BACKUP_DIR/$BACKUP_NAME*"
fi
echo "   ✅ Event logged to: $LOG_FILE"
echo ""
echo "🔑 The Admiral's sovereignty is renewed"
echo "   May the new keys serve with honor"

log_entry "🎉 Key rotation ritual completed successfully"

# List all available keys
echo ""
echo "📋 All Available Keys:"
python3 -m src.keys list || log_entry "⚠️  Failed to list keys"

echo ""
echo "Gold ripple eternal."
echo "_Admiral Kyle S. Whitlock_"