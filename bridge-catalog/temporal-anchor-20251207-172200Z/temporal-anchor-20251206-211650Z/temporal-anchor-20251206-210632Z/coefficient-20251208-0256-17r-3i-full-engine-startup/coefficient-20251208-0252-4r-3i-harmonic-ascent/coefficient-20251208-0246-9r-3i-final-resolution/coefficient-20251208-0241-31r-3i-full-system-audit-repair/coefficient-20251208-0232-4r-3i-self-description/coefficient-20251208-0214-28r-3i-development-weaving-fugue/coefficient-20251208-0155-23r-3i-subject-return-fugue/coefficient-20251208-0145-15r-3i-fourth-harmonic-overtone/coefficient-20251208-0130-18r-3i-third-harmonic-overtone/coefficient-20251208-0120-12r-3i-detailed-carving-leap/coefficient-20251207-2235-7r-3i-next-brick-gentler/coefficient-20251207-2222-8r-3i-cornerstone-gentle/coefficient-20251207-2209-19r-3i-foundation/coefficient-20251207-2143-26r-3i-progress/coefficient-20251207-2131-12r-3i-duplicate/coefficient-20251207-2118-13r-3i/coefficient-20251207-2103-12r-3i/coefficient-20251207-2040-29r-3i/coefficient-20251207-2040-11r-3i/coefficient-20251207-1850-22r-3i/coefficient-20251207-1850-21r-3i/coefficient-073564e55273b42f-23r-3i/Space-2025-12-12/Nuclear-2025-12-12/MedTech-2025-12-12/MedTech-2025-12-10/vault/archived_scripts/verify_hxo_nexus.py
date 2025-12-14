#!/usr/bin/env python3
"""
HXO Nexus Connectivity Verification Script
Validates the "1+1=∞" connectivity paradigm implementation
"""

import sys
import os
import asyncio
from pathlib import Path

# Add bridge_backend to path
sys.path.insert(0, str(Path(__file__).parent / "bridge_backend"))

# Disable Genesis to avoid dependencies in verification
os.environ['GENESIS_MODE'] = 'disabled'
os.environ['HXO_NEXUS_ENABLED'] = 'true'


async def verify_hxo_nexus():
    """Verify HXO Nexus connectivity implementation"""
    
    print("=" * 70)
    print("HXO Nexus v1.9.6p 'Ascendant' Verification")
    print("=" * 70)
    print()
    
    # 1. Import verification
    print("1. Verifying module imports...")
    try:
        from bridge_backend.bridge_core.engines.hxo import (
            HXONexus, get_nexus_instance, HypShardV3Manager,
            QuantumEntropyHasher, HarmonicConsensusProtocol
        )
        print("   ✅ All modules imported successfully")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # 2. Nexus instantiation
    print("\n2. Verifying HXO Nexus core...")
    try:
        nexus = HXONexus()
        assert nexus.id == "HXO_CORE"
        assert nexus.version == "1.9.6p"
        assert nexus.codename == "HXO Ascendant"
        assert nexus.type == "central_harmonic_conductor"
        print(f"   ✅ Nexus: {nexus.id} v{nexus.version}")
    except Exception as e:
        print(f"   ❌ Nexus verification failed: {e}")
        return False
    
    # 3. Engine connectivity
    print("\n3. Verifying engine connectivity...")
    try:
        # Check all 10 engines are defined
        assert len(nexus._engine_specs) == 10
        
        # Check HXO_CORE connects to all engines
        hxo_connections = nexus.get_engine_connections("HXO_CORE")
        assert len(hxo_connections) == 10
        
        # Verify specific connections from spec
        assert nexus.is_connected("GENESIS_BUS", "TRUTH_ENGINE")
        assert nexus.is_connected("TRUTH_ENGINE", "BLUEPRINT_ENGINE")
        assert nexus.is_connected("CASCADE_ENGINE", "AUTONOMY_ENGINE")
        assert nexus.is_connected("FEDERATION_ENGINE", "LEVIATHAN_ENGINE")
        assert nexus.is_connected("ARIE_ENGINE", "TRUTH_ENGINE")
        
        # Get connection graph stats
        graph = nexus.get_connection_graph()
        total_connections = sum(len(conns) for conns in graph.values())
        
        print(f"   ✅ 10 engines registered")
        print(f"   ✅ {total_connections} total connections")
        print(f"   ✅ Connection topology verified")
    except Exception as e:
        print(f"   ❌ Connectivity verification failed: {e}")
        return False
    
    # 4. HypShard v3
    print("\n4. Verifying HypShard v3...")
    try:
        manager = HypShardV3Manager()
        assert manager.max_capacity == 1_000_000
        assert manager.policies["expand_on_load"] == True
        assert manager.policies["collapse_post_execute"] == True
        assert manager.policies["auto_balance"] == True
        assert len(manager.control_channels) == 4
        
        print(f"   ✅ Capacity: {manager.max_capacity:,} shards")
        print(f"   ✅ Policies: {manager.policies}")
        print(f"   ✅ Control channels: {len(manager.control_channels)}")
    except Exception as e:
        print(f"   ❌ HypShard verification failed: {e}")
        return False
    
    # 5. Security layers
    print("\n5. Verifying security layers...")
    try:
        # Quantum Entropy Hasher
        hasher = QuantumEntropyHasher()
        assert hasher.version == "v3"
        test_hash = hasher.hash("test_data")
        assert len(test_hash) == 64  # SHA-256 hex
        
        # Harmonic Consensus Protocol
        hcp = HarmonicConsensusProtocol()
        assert hcp.mode == "HARMONIC"
        assert hcp.recursion_limit == 5
        
        print(f"   ✅ QEH-{hasher.version} operational")
        print(f"   ✅ HCP mode: {hcp.mode}")
    except Exception as e:
        print(f"   ❌ Security verification failed: {e}")
        return False
    
    # 6. Async operations
    print("\n6. Verifying async operations...")
    try:
        # Health check
        health = await nexus.health_check()
        assert health["nexus_id"] == "HXO_CORE"
        assert health["version"] == "1.9.6p"
        
        # Coordinate engines
        intent = {
            "type": "test_coordination",
            "engines": ["TRUTH_ENGINE", "BLUEPRINT_ENGINE"]
        }
        result = await nexus.coordinate_engines(intent)
        assert result["status"] == "coordinated"
        
        print(f"   ✅ Health check: OK")
        print(f"   ✅ Engine coordination: OK")
    except Exception as e:
        print(f"   ❌ Async operations failed: {e}")
        return False
    
    # 7. API Routes
    print("\n7. Verifying API routes...")
    try:
        from bridge_backend.bridge_core.engines.hxo.routes import router
        assert router.prefix == "/hxo"
        assert len(router.routes) >= 7
        
        print(f"   ✅ Routes prefix: {router.prefix}")
        print(f"   ✅ {len(router.routes)} endpoints available")
    except Exception as e:
        print(f"   ❌ Routes verification failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    print()
    print("✅ HXO Nexus Core: OPERATIONAL")
    print("✅ Engine Connectivity (1+1=∞): VERIFIED")
    print("✅ HypShard v3: READY")
    print("✅ Security Layers: ACTIVE")
    print("✅ API Routes: AVAILABLE")
    print()
    print(f"🌟 HXO Nexus v1.9.6p 'Ascendant' is fully operational!")
    print(f"   Central Harmonic Conductor: {nexus.properties['signature']}")
    print(f"   Protocol: {nexus.properties['core_protocol']}")
    print(f"   Entropy: {nexus.properties['entropy_channel']}")
    print()
    print("The '1+1=∞' connectivity paradigm is now active.")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(verify_hxo_nexus())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
