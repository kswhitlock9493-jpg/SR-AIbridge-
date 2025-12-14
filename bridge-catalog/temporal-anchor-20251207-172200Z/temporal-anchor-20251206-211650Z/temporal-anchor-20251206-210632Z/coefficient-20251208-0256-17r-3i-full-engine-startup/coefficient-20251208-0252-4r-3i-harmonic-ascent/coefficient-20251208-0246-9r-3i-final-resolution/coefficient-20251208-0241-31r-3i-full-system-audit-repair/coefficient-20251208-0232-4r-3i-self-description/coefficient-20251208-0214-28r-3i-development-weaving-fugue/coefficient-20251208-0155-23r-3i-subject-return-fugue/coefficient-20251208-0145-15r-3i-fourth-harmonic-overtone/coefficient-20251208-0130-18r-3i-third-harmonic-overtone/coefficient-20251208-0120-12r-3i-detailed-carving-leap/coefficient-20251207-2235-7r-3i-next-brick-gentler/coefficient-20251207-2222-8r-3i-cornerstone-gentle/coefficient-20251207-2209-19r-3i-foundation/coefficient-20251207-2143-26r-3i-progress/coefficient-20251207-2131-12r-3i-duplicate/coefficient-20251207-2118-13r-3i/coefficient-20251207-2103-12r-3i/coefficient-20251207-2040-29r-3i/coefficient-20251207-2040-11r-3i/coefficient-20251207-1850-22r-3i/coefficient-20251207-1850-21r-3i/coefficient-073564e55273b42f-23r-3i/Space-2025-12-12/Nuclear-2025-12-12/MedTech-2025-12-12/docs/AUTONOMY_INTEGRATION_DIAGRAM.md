# Autonomy Engine Integration - System Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                      SR-AIbridge System Architecture                    │
│                   with Autonomy Engine Integration                      │
└────────────────────────────────────────────────────────────────────────┘

                               GENESIS BUS
                        (Central Event Multiplexer)
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
    ┌───────┐                  ┌──────────┐              ┌──────────┐
    │TRIAGE │                  │FEDERATION│              │ PARITY   │
    │SYSTEM │                  │ SYSTEM   │              │ SYSTEM   │
    └───┬───┘                  └────┬─────┘              └────┬─────┘
        │                           │                         │
        │ Events Published:         │ Events Published:       │ Events Published:
        │ • triage.api             │ • federation.events     │ • parity.check
        │ • triage.endpoint        │ • federation.heartbeat  │ • parity.autofix
        │ • triage.diagnostics     │                         │
        │                           │                         │
        └───────────────────────────┼─────────────────────────┘
                                    │
                                    ▼
                        ┌────────────────────┐
                        │  AUTONOMY ENGINE   │
                        │  Event Handlers:   │
                        │  ▸ Triage → Heal   │
                        │  ▸ Federation → Sync│
                        │  ▸ Parity → Fix    │
                        └──────────┬─────────┘
                                   │
                                   ▼
                        ┌────────────────────┐
                        │  AUTO-HEAL ACTIONS │
                        │  • genesis.heal    │
                        │  • genesis.intent  │
                        └────────────────────┘

═══════════════════════════════════════════════════════════════════════

                          EVENT FLOW EXAMPLES

1. TRIAGE EVENT FLOW:
   
   api_triage.py → triage.api → Autonomy Engine → genesis.heal
                    (Genesis Bus)                   (Auto-healing)

2. FEDERATION EVENT FLOW:

   FederationClient.send_heartbeat() → federation.heartbeat → 
   Autonomy Engine → genesis.intent (Distributed coordination)

3. PARITY EVENT FLOW:

   parity_engine.py → parity.check → Autonomy Engine → genesis.heal
                      (Genesis Bus)                     (Auto-fix)

═══════════════════════════════════════════════════════════════════════

                        COMPONENT INTERACTIONS

┌─────────────────┐     publishes to      ┌─────────────────┐
│ Triage Scripts  │────────────────────────▶│  Genesis Bus    │
│  • api_triage   │                        │  (Event Broker) │
│  • endpoint     │                        │                 │
│  • diagnostics  │                        │  Valid Topics:  │
└─────────────────┘                        │  • triage.*     │
                                           │  • federation.* │
┌─────────────────┐     publishes to      │  • parity.*     │
│ Federation      │────────────────────────▶│                 │
│  Client         │                        │                 │
└─────────────────┘                        └────────┬────────┘
                                                    │ notifies
┌─────────────────┐     publishes to               │
│ Parity Tools    │────────────────────────────────┘
│  • parity_engine│                                 │
│  • parity_autofix│                                ▼
│  • deploy_parity│                        ┌─────────────────┐
└─────────────────┘                        │ Autonomy Engine │
                                           │  Subscriptions: │
                                           │  ▸ triage.*     │
                                           │  ▸ federation.* │
                                           │  ▸ parity.*     │
                                           │                 │
                                           │  Publishes:     │
                                           │  ▸ genesis.heal │
                                           │  ▸ genesis.intent│
                                           └─────────────────┘

═══════════════════════════════════════════════════════════════════════

                            KEY FEATURES

✅ Unified Event Bus: All systems communicate through Genesis Bus
✅ Automatic Healing: Autonomy responds to triage failures  
✅ Distributed Coordination: Federation events trigger sync
✅ Self-Repair: Parity issues automatically trigger fixes
✅ Error Resilience: Event publishing gracefully fails in CI/CD
✅ Topic Validation: Strict mode ensures event integrity

═══════════════════════════════════════════════════════════════════════

                         FILES MODIFIED

Core Integration:
  • bridge_backend/bridge_core/engines/adapters/genesis_link.py
  • bridge_backend/genesis/bus.py

Triage Integration:  
  • bridge_backend/tools/triage/api_triage.py
  • bridge_backend/tools/triage/endpoint_triage.py
  • bridge_backend/tools/triage/diagnostics_federate.py

Federation Integration:
  • bridge_backend/bridge_core/heritage/federation/federation_client.py

Parity Integration:
  • bridge_backend/tools/parity_engine.py
  • bridge_backend/tools/parity_autofix.py
  • bridge_backend/runtime/deploy_parity.py

Testing:
  • bridge_backend/tests/test_autonomy_integration.py

Documentation:
  • docs/AUTONOMY_INTEGRATION.md

═══════════════════════════════════════════════════════════════════════
```
