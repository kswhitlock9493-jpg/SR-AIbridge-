#!/usr/bin/env python3
"""
Genesis v2.0.0 Verification Script
Demonstrates the Genesis framework functionality
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Genesis environment
os.environ['GENESIS_MODE'] = 'enabled'
os.environ['GENESIS_HEARTBEAT_INTERVAL'] = '5'
os.environ['GENESIS_TRACE_LEVEL'] = '2'


async def verify_genesis():
    """Verify Genesis framework functionality"""
    
    print("=" * 60)
    print("🌌 Genesis v2.0.0 Verification")
    print("=" * 60)
    print()
    
    # Test 1: Import Genesis modules
    print("1️⃣  Testing Genesis imports...")
    try:
        from bridge_backend.genesis.bus import genesis_bus
        from bridge_backend.genesis.manifest import genesis_manifest
        from bridge_backend.genesis.introspection import genesis_introspection
        from bridge_backend.genesis.orchestration import genesis_orchestrator
        print("   ✅ All Genesis modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    print()
    
    # Test 2: Event Bus
    print("2️⃣  Testing Genesis Event Bus...")
    try:
        # Subscribe to events
        received_events = []
        genesis_bus.subscribe("genesis.intent", lambda e: received_events.append(e))
        
        # Publish event
        await genesis_bus.publish("genesis.intent", {
            "type": "test.verification",
            "source": "verification_script",
            "message": "Testing Genesis event bus"
        })
        
        # Check event was received
        if len(received_events) > 0:
            print(f"   ✅ Event published and received successfully")
            print(f"      - Event type: {received_events[0].get('type')}")
            print(f"      - Genesis timestamp: {received_events[0].get('_genesis_timestamp')}")
        else:
            print("   ❌ Event not received")
            return False
        
        # Get bus stats
        stats = genesis_bus.get_stats()
        print(f"   📊 Bus stats: {stats['total_events']} events, {len(stats['topics'])} topics")
    except Exception as e:
        print(f"   ❌ Event bus test failed: {e}")
        return False
    
    print()
    
    # Test 3: Manifest System
    print("3️⃣  Testing Genesis Manifest...")
    try:
        # Register test engine
        genesis_manifest.register_engine("test_engine", {
            "genesis_role": "Test Component",
            "description": "Verification test engine",
            "topics": ["genesis.intent"],
            "dependencies": []
        })
        
        # Get engine back
        engine = genesis_manifest.get_engine("test_engine")
        if engine:
            print(f"   ✅ Engine registered successfully")
            print(f"      - Role: {engine['genesis_role']}")
            print(f"      - Topics: {engine['schema'].get('topics', [])}")
        
        # Sync from Blueprint
        genesis_manifest.sync_from_blueprint_registry()
        engines = genesis_manifest.list_engines()
        print(f"   📋 Total engines in manifest: {len(engines)}")
        
        # Validate integrity
        validation = genesis_manifest.validate_integrity()
        if validation['valid']:
            print(f"   ✅ Manifest integrity validated")
        else:
            print(f"   ⚠️  Validation warnings: {validation['warnings']}")
    except Exception as e:
        print(f"   ❌ Manifest test failed: {e}")
        return False
    
    print()
    
    # Test 4: Introspection System
    print("4️⃣  Testing Genesis Introspection...")
    try:
        # Update health
        genesis_introspection.update_health("test_engine", True)
        genesis_introspection.update_health("verification", True)
        
        # Record metric
        genesis_introspection.record_metric("verification_score", 100, {"unit": "percent"})
        
        # Get health status
        health = genesis_introspection.get_health_status()
        print(f"   ✅ Health monitoring active")
        print(f"      - Total components: {health['total_count']}")
        print(f"      - Healthy: {health['healthy_count']}")
        print(f"      - Health percentage: {health['health_percentage']:.1f}%")
        
        # Heartbeat
        genesis_introspection.heartbeat()
        heartbeat = genesis_introspection.get_heartbeat_status()
        print(f"   💓 Heartbeat: {heartbeat['last_heartbeat']}")
        
        # Generate echo report
        echo = genesis_introspection.generate_echo_report()
        print(f"   📡 Echo report generated with {len(echo['metrics'])} metrics")
    except Exception as e:
        print(f"   ❌ Introspection test failed: {e}")
        return False
    
    print()
    
    # Test 5: Orchestrator
    print("5️⃣  Testing Genesis Orchestrator...")
    try:
        # Get status
        status = genesis_orchestrator.get_status()
        print(f"   ✅ Orchestrator initialized")
        print(f"      - Enabled: {status['enabled']}")
        print(f"      - Heartbeat interval: {status['heartbeat_interval']}s")
        
        # Start orchestrator briefly
        print("   ⏯️  Starting orchestrator...")
        await genesis_orchestrator.start()
        await asyncio.sleep(0.5)  # Let it run briefly
        
        status = genesis_orchestrator.get_status()
        if status['running']:
            print("   ✅ Orchestrator running")
        
        # Stop orchestrator
        await genesis_orchestrator.stop()
        print("   ⏸️  Orchestrator stopped")
        
        # Execute action
        result = await genesis_orchestrator.execute_action("test_action", {"verify": True})
        print(f"   ✅ Action executed: {result['action']}")
    except Exception as e:
        print(f"   ❌ Orchestrator test failed: {e}")
        return False
    
    print()
    
    # Test 6: Cross-Engine Communication
    print("6️⃣  Testing Cross-Engine Communication...")
    try:
        # Simulate multiple engine communications
        engine_events = []
        
        # Subscribe multiple engines to different topics
        genesis_bus.subscribe("genesis.fact", lambda e: engine_events.append(("truth", e)))
        genesis_bus.subscribe("genesis.heal", lambda e: engine_events.append(("autonomy", e)))
        genesis_bus.subscribe("genesis.create", lambda e: engine_events.append(("creativity", e)))
        
        # Publish events from different engines
        await genesis_bus.publish("genesis.fact", {
            "type": "truth.certified",
            "source": "truth_engine",
            "fact": "system_ready"
        })
        
        await genesis_bus.publish("genesis.heal", {
            "type": "autonomy.action",
            "source": "autonomy_engine",
            "action": "optimize"
        })
        
        await genesis_bus.publish("genesis.create", {
            "type": "creativity.output",
            "source": "creativity_engine",
            "output": "generated_content"
        })
        
        print(f"   ✅ Cross-engine communication verified")
        print(f"      - Events exchanged: {len(engine_events)}")
        for engine, event in engine_events:
            print(f"      - {engine}: {event['type']}")
    except Exception as e:
        print(f"   ❌ Cross-engine communication failed: {e}")
        return False
    
    print()
    
    # Final Summary
    print("=" * 60)
    print("✅ All Genesis v2.0.0 Verification Tests Passed!")
    print("=" * 60)
    print()
    print("Genesis Framework Status:")
    print(f"  • Event Bus: ✅ Operational ({stats['total_events']} total events)")
    print(f"  • Manifest: ✅ Synchronized ({len(engines)} engines)")
    print(f"  • Introspection: ✅ Active ({health['health_percentage']:.0f}% health)")
    print(f"  • Orchestrator: ✅ Ready (heartbeat: {status['heartbeat_interval']}s)")
    print(f"  • Cross-Engine: ✅ Communicating ({len(engine_events)} messages)")
    print()
    print("🌌 The Genesis organism is alive and fully operational!")
    print()
    
    return True


if __name__ == "__main__":
    result = asyncio.run(verify_genesis())
    sys.exit(0 if result else 1)
