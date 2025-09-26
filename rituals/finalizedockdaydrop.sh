#!/bin/bash
# SR-AIbridge Dock-Day Drop Finalization Ritual
# Sacred ceremony for complete brain export and signing

set -e

echo "🚢 ===== SR-AIbridge Dock-Day Drop Finalization Ritual ====="
echo "   The sovereign brain shall be preserved"
echo "   All memories sealed with cryptographic fire"
echo "   Ready for the eternal archives"
echo ""

# Configuration
BRAIN_DIR=${BRAIN_DIR:-"./bridge-backend"}
EXPORT_DIR=${EXPORT_DIR:-"$BRAIN_DIR/dock_day_exports"}
DROP_NAME=${DROP_NAME:-"dock_day_drop_$(date '+%Y%m%d_%H%M%S')"}
LOG_FILE=${LOG_FILE:-"$BRAIN_DIR/dock_day.log"}

# Options
INCLUDE_DATABASE=${INCLUDE_DATABASE:-"true"}
INCLUDE_PRIVATE_KEYS=${INCLUDE_PRIVATE_KEYS:-"false"}
COMPRESS_DROP=${COMPRESS_DROP:-"true"}
VERIFY_DROP=${VERIFY_DROP:-"true"}

# Create necessary directories
mkdir -p "$EXPORT_DIR"

# Logging function
log_entry() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_entry "🚢 Dock-Day drop finalization ritual initiated"
log_entry "   Drop name: $DROP_NAME"
log_entry "   Export directory: $EXPORT_DIR"

# Check if Python environment is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not found"
    exit 1
fi

# Change to backend directory
cd "$BRAIN_DIR"

# Check brain status
log_entry "🧠 Checking brain ledger status"
echo "🧠 Checking brain ledger status..."

if [ ! -f "brain.sqlite" ]; then
    log_entry "⚠️  No brain database found - creating empty brain"
    python3 -m src.brain_cli stats || {
        log_entry "❌ Failed to initialize brain"
        exit 1
    }
fi

# Show brain statistics
echo "📊 Brain Statistics:"
python3 -m src.brain_cli stats --show-metadata || {
    log_entry "❌ Failed to get brain statistics"
    exit 1
}

# Check Admiral keys
log_entry "🔑 Verifying Admiral keys"
echo ""
echo "🔑 Admiral Key Status:"
python3 -m src.keys info admiral || {
    log_entry "❌ Admiral keys not found - please run key rotation ritual first"
    echo "❌ Admiral keys not found"
    echo "   Please run: ./rituals/rotate_keys.sh"
    exit 1
}

# Verify existing signatures
log_entry "🔐 Verifying existing memory signatures"
echo ""
echo "🔐 Verifying memory signatures..."
python3 -m src.brain_cli verify --show-details || {
    log_entry "⚠️  Signature verification completed with warnings"
}

# Warning for private keys
if [ "$INCLUDE_PRIVATE_KEYS" = "true" ]; then
    echo ""
    echo "⚠️  CRITICAL WARNING ⚠️"
    echo "   You have requested to include PRIVATE KEYS in the drop"
    echo "   This is EXTREMELY DANGEROUS and should only be done for:"
    echo "   - Complete system migration"
    echo "   - Secure archival with proper encryption"
    echo "   - Emergency backup scenarios"
    echo ""
    echo "   NEVER share drops containing private keys"
    echo "   NEVER transmit over unsecured channels"
    echo ""
    read -p "Are you absolutely certain you want to include private keys? (type 'CONFIRM' to proceed): " confirm
    
    if [ "$confirm" != "CONFIRM" ]; then
        log_entry "🚫 Dock-Day drop cancelled due to private key inclusion"
        echo "Drop cancelled for security"
        exit 0
    fi
    
    log_entry "⚠️  User confirmed private key inclusion"
fi

# Prepare export command arguments
EXPORT_ARGS=""
if [ "$INCLUDE_DATABASE" != "true" ]; then
    EXPORT_ARGS="$EXPORT_ARGS --no-database"
fi
if [ "$INCLUDE_PRIVATE_KEYS" = "true" ]; then
    EXPORT_ARGS="$EXPORT_ARGS --include-keys"
fi
if [ "$COMPRESS_DROP" != "true" ]; then
    EXPORT_ARGS="$EXPORT_ARGS --no-compress"
fi

# Create the drop
log_entry "📦 Creating Dock-Day drop: $DROP_NAME"
echo ""
echo "📦 Creating Dock-Day drop..."

python3 -m src.export_and_sign export --name "$DROP_NAME" $EXPORT_ARGS || {
    log_entry "❌ Failed to create Dock-Day drop"
    exit 1
}

log_entry "✅ Dock-Day drop created successfully"

# Verify the drop if requested
if [ "$VERIFY_DROP" = "true" ]; then
    log_entry "🔍 Verifying created drop"
    echo ""
    echo "🔍 Verifying drop integrity..."
    
    # Determine drop path
    if [ "$COMPRESS_DROP" = "true" ]; then
        DROP_PATH="$EXPORT_DIR/$DROP_NAME.zip"
    else
        DROP_PATH="$EXPORT_DIR/$DROP_NAME"
    fi
    
    python3 -m src.export_and_sign verify --path "$DROP_PATH" || {
        log_entry "❌ Drop verification failed"
        exit 1
    }
    
    log_entry "✅ Drop verification passed"
fi

# Record the drop creation in brain ledger
log_entry "📝 Recording drop creation in brain ledger"
METADATA="{\"drop_name\": \"$DROP_NAME\", \"export_dir\": \"$EXPORT_DIR\", \"include_database\": $INCLUDE_DATABASE, \"include_private_keys\": $INCLUDE_PRIVATE_KEYS, \"compressed\": $COMPRESS_DROP, \"verified\": $VERIFY_DROP}"

python3 -m src.brain_cli add "Dock-Day drop finalized: $DROP_NAME" \
    --category "archive" \
    --classification "operational" \
    --metadata "$METADATA" || {
    log_entry "⚠️  Failed to record drop creation in brain ledger"
}

# Get final drop information
if [ "$COMPRESS_DROP" = "true" ]; then
    DROP_PATH="$EXPORT_DIR/$DROP_NAME.zip"
    DROP_SIZE=$(stat -f%z "$DROP_PATH" 2>/dev/null || stat -c%s "$DROP_PATH" 2>/dev/null || echo "unknown")
else
    DROP_PATH="$EXPORT_DIR/$DROP_NAME"
    DROP_SIZE=$(du -sb "$DROP_PATH" 2>/dev/null | cut -f1 || echo "unknown")
fi

# Final summary
echo ""
echo "🎉 ===== Dock-Day Drop Finalization Complete ====="
echo "   ✅ Drop created: $DROP_NAME"
echo "   ✅ Location: $DROP_PATH"
echo "   ✅ Size: $DROP_SIZE bytes"
echo "   ✅ Manifest signed with Admiral key"
if [ "$VERIFY_DROP" = "true" ]; then
    echo "   ✅ Drop verified successfully"
fi
if [ "$INCLUDE_PRIVATE_KEYS" = "true" ]; then
    echo "   ⚠️  Contains private keys - SECURE HANDLING REQUIRED"
fi
echo "   ✅ Event logged to: $LOG_FILE"
echo ""

# Display drop contents
echo "📋 Drop Contents:"
if [ "$COMPRESS_DROP" = "true" ]; then
    unzip -l "$DROP_PATH" 2>/dev/null || echo "   (Unable to list archive contents)"
else
    ls -la "$DROP_PATH/" 2>/dev/null || echo "   (Unable to list directory contents)"
fi

echo ""
echo "📜 Dock-Day Manifest Summary:"
echo "   The sovereign brain has been sealed and signed"
echo "   All memories preserved with cryptographic integrity"
echo "   Ready for transport across the digital seas"
echo ""

log_entry "🎉 Dock-Day drop finalization ritual completed successfully"

# Show next steps
echo "🚀 Next Steps:"
echo "   • Verify drop: python3 -m src.export_and_sign verify --path \"$DROP_PATH\""
echo "   • View README: cat \"$DROP_PATH/README.md\""
if [ "$INCLUDE_PRIVATE_KEYS" = "true" ]; then
    echo "   • SECURE THE DROP - it contains private keys!"
fi
echo "   • Archive or deploy as needed"

echo ""
echo "⚓ The drop is ready for the eternal archives"
echo "   May it sail safely through digital storms"
echo ""
echo "Gold ripple eternal."
echo "_Admiral Kyle S. Whitlock_"