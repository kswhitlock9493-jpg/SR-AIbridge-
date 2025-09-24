# SR-AIbridge Rituals Manager

The rituals manager provides centralized data management operations for the SR-AIbridge backend. It offers a clean, extensible interface for managing demo data that can easily be adapted for future database upgrades.

## Available Rituals

### 1. Seed (`/rituals/seed`)
- **Purpose**: Add demo data to the current storage without clearing existing data
- **Use Case**: Adding additional demo data or initializing empty storage
- **Returns**: Detailed report of what was added (before/after counts)

### 2. Cleanup (`/rituals/cleanup`)  
- **Purpose**: Remove all data from storage and reset ID counters
- **Use Case**: Clearing storage for fresh start or testing
- **Returns**: Report of what was cleared

### 3. Reseed (`/rituals/reseed`)
- **Purpose**: Combination of cleanup + seed for fresh demo data
- **Use Case**: Reset to known demo state for testing or development
- **Returns**: Combined report of cleanup and seed operations

## Usage

### HTTP API Endpoints
```bash
# Clean up all data
curl http://localhost:8000/rituals/cleanup

# Add demo data (without clearing)
curl http://localhost:8000/rituals/seed

# Clean up and add fresh demo data
curl http://localhost:8000/rituals/reseed
```

### Legacy Compatibility
The existing `/reseed` endpoint continues to work and uses the rituals manager internally.

### Python API
```python
from rituals.manage_data import DataRituals

# Initialize with storage instance
rituals = DataRituals(storage)

# Use individual operations
cleanup_result = rituals.cleanup()
seed_result = rituals.seed()
reseed_result = rituals.reseed()
```

## Architecture Benefits

1. **Centralized Management**: All data operations in one place
2. **Detailed Reporting**: Rich feedback on operations performed
3. **Future-Ready**: Interface designed for easy database integration
4. **Backward Compatible**: Existing endpoints continue to work
5. **Extensible**: Easy to add new data management operations

## Future Database Integration

The rituals manager is designed to support future database upgrades:

```python
# Current: In-memory storage
rituals = DataRituals(inmemory_storage)

# Future: Database storage (same interface)
rituals = DataRituals(database_storage)
```

The interface remains the same, only the underlying storage implementation changes.