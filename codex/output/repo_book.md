# 📘 The Book of the Repo

_Generated automatically on 2025-11-07T03:41:36.489670+00:00 UTC_

---

## 🧠 Truth Engine Summary

- **blocked_licenses** → `['GPL-2.0', 'GPL-3.0', 'AGPL-3.0']`  
  _source: ./scan_policy.yaml_
- **allowed_licenses** → `['MIT', 'Apache-2.0', 'BSD-3-Clause']`  
  _source: ./scan_policy.yaml_
- **thresholds** → `{'counterfeit_confidence_block': 0.94, 'counterfeit_confidence_flag': 0.6}`  
  _source: ./scan_policy.yaml_
- **max_file_size_bytes** → `750000`  
  _source: ./scan_policy.yaml_
- **scan_exclude_paths** → `['node_modules', '.venv', '__pycache__', 'bridge_backend/scan_reports']`  
  _source: ./scan_policy.yaml_
- **version** → `1.0`  
  _source: ./src/bridge.runtime.yaml_
- **dominion** → `{'root_env_var': 'FORGE_DOMINION_ROOT', 'service_ttl_minutes': 180, 'allow_unsigned': False}`  
  _source: ./bridge.runtime.yaml_
- **runtime** → `{'name': 'sr-aibridge', 'forge': {'mode': 'dominion', 'handshake': 'forge://resolve', 'targets': [{'name': 'sovereign-ledger', 'type': 'log', 'scope': 'deploy', 'verify': True}]}, 'federation': {'heartbeat': {'enabled': True, 'interval': 60, 'endpoint': 'forge://federation/heartbeat', 'ledger_forward': True, 'ttl': 300}, 'consensus': {'enabled': True, 'interval': 180, 'election_method': 'highest_epoch', 'ledger_forward': True}}, 'health': {'recovery': True, 'chaos': {'enabled': False, 'interval': 600, 'probability': 0.15}}, 'ledger': {'forward': ['federation/heartbeat', 'federation/consensus', 'recovery']}}`  
  _source: ./bridge.runtime.yaml_
- **forge** → `{'dominion': 'sovereign.bridge', 'resolver': 'forge://resolve', 'schema': [{'target': 'ledger', 'purpose': 'runtime logging', 'return': ['ledger_url', 'ledger_signature', 'ledger_identity']}, {'target': 'bridge', 'purpose': 'deployment bridge sync', 'return': ['bridge_url', 'bridge_signature', 'bridge_identity']}]}`  
  _source: ./bridge.runtime.yaml_
- **provider** → `{'kind': 'docker', 'network': 'brh_net', 'autostart': True}`  
  _source: ./bridge.runtime.yaml_
- **services** → `{'api': {'context': './bridge_backend', 'dockerfile': 'Dockerfile', 'image': 'ghcr.io/kswhitlock9493-jpg/sr-aibridge-backend:latest', 'replicas': 1, 'ports': ['8000:8000'], 'env': ['ENVIRONMENT=production', 'LOG_LEVEL=INFO'], 'health': {'http': 'http://localhost:8000/health/live', 'interval': '10s', 'timeout': '2s', 'retries': 12}, 'volumes': []}, 'ws': {'image': 'ghcr.io/kswhitlock9493-jpg/ws-sidecar:latest', 'replicas': 1, 'depends_on': ['api'], 'env': ['BACKEND_URL=http://api:8000'], 'health': {'tcp': 'localhost:9001', 'interval': '10s', 'timeout': '2s', 'retries': 12}}}`  
  _source: ./bridge.runtime.yaml_
- **version** → `1.0.0`  
  _source: ./network_policies/egress_policies.yaml_
- **last_updated** → `2025-11-06T12:48:19.103259+00:00`  
  _source: ./network_policies/firewall_rules.yaml_
- **rules** → `[{'id': 'allow_critical_domains', 'action': 'allow', 'priority': 100, 'source': 'any', 'destination': 'critical_domains', 'protocol': 'https', 'enabled': True}, {'id': 'allow_infrastructure', 'action': 'allow', 'priority': 90, 'source': 'any', 'destination': 'infrastructure_domains', 'protocol': 'https', 'enabled': True}, {'id': 'allow_browser_downloads', 'action': 'allow', 'priority': 85, 'source': 'any', 'destination': 'browser_download_domains', 'protocol': 'https', 'enabled': True, 'description': 'Allow browser downloads for Playwright/Puppeteer (Chrome, Chromium, etc.)'}, {'id': 'block_unknown', 'action': 'log_and_notify', 'priority': 10, 'source': 'any', 'destination': 'unknown', 'protocol': 'any', 'enabled': True}]`  
  _source: ./network_policies/firewall_rules.yaml_
- **last_updated** → `2025-11-06T12:48:35.243572+00:00`  
  _source: ./network_policies/sovereign_allowlist.yaml_
- **domains** → `{'critical': ['api.netlify.com', 'bridge.sr-aibridge.com', 'diagnostics.sr-aibridge.com'], 'infrastructure': ['github.com', 'api.github.com', 'registry.npmjs.org', 'pypi.org'], 'monitoring': ['sentry.io'], 'browser_downloads': ['googlechromelabs.github.io', 'storage.googleapis.com', 'edgedl.me.gvt1.com', 'playwright.azureedge.net', 'cdn.playwright.dev']}`  
  _source: ./network_policies/sovereign_allowlist.yaml_
- **ip_ranges** → `{'netlify': ['44.211.0.0/16', '52.2.0.0/15'], 'github': ['140.82.112.0/20', '143.55.64.0/20']}`  
  _source: ./network_policies/sovereign_allowlist.yaml_
- **last_updated** → `2025-11-06T12:48:19.102407+00:00`  
  _source: ./network_policies/egress_policies.yaml_
- **policies** → `{'default_action': 'deny', 'allowed_protocols': ['https', 'http'], 'allowed_ports': [80, 443, 8080, 3000], 'dns_resolution': {'primary': ['8.8.8.8', '8.8.4.4'], 'fallback': ['1.1.1.1', '1.0.0.1']}, 'retry_policy': {'max_retries': 3, 'backoff_multiplier': 2, 'initial_delay_ms': 1000}, 'timeout_policy': {'connection_timeout_s': 10, 'read_timeout_s': 30, 'total_timeout_s': 60}}`  
  _source: ./network_policies/egress_policies.yaml_
- **services** → `[{'type': 'web', 'name': 'sr-aibridge-backend', 'env': 'python', 'plan': 'starter', 'buildCommand': 'pip install -r requirements.txt', 'startCommand': 'bash bridge_backend/runtime/start.sh', 'envVars': [{'key': 'PYTHON_VERSION', 'value': '3.11.9'}, {'key': 'PORT', 'value': '10000'}, {'key': 'NODE_ENV', 'value': 'production'}, {'key': 'DATABASE_URL', 'sync': False}, {'key': 'BRIDGE_VERSION', 'value': '2.0.1'}], 'healthCheckPath': '/api/health', 'autoDeploy': True}]`  
  _source: ./.archive/render_legacy/render.yaml_
- **version** → `v1`  
  _source: ./DOCTRINE/indoctrination/policy.yaml_
- **constraints** → `{'certification_required': True}`  
  _source: ./DOCTRINE/indoctrination/policy.yaml_
- **checks** → `[{'id': 'doctrine_alignment', 'description': 'Verify agent training against doctrine scrolls'}]`  
  _source: ./DOCTRINE/indoctrination/policy.yaml_
- **name** → `SR-AIbridge`  
  _source: ./codex/manifest.yaml_
- **version** → `5.5.3`  
  _source: ./codex/manifest.yaml_
- **description** → `Self-documenting repository with automated codex compilation`  
  _source: ./codex/manifest.yaml_
- **engines** → `{'truth': 'Validates facts and metadata from YAML files', 'parser': 'Extracts documentation from markdown files', 'blueprint': 'Maps code dependencies and imports'}`  
  _source: ./codex/manifest.yaml_
- **outputs** → `['codex/output/repo_book.json', 'codex/output/repo_book.md']`  
  _source: ./codex/manifest.yaml_
- **runtime** → `{'name': 'sr-aibridge-runtime', 'type': 'sovereign', 'auth': {'provider': 'forge_dominion', 'token_mode': 'ephemeral', 'token_ttl': 3600, 'auto_renew': True}, 'containers': [{'name': 'backend-api', 'image': 'python:3.12-slim', 'command': ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'], 'environment': ['FORGE_DOMINION_MODE=sovereign', 'DATABASE_TYPE=sqlite'], 'ports': ['8000:8000'], 'health_check': {'path': '/health', 'interval': 30, 'timeout': 5, 'retries': 3}, 'resources': {'memory': '512Mi', 'cpu': '0.5'}}, {'name': 'frontend-static', 'image': 'nginx:alpine', 'command': ['nginx', '-g', 'daemon off;'], 'ports': ['3000:80'], 'health_check': {'path': '/', 'interval': 30, 'timeout': 5, 'retries': 3}, 'resources': {'memory': '256Mi', 'cpu': '0.25'}}], 'routes': [{'path': '/api/*', 'target': 'backend-api:8000', 'strip_prefix': '/api'}, {'path': '/*', 'target': 'frontend-static:80'}], 'lifecycle': {'startup_timeout': 120, 'shutdown_timeout': 30, 'restart_policy': 'on-failure', 'max_restarts': 3}, 'federation': {'enabled': True, 'lattice_mode': 'harmonic', 'heartbeat_interval': 10, 'sync_protocol': 'μ-state-replication'}, 'observability': {'logs': {'destination': 'forge://sovereign-ledger/runtime', 'level': 'info', 'format': 'json'}, 'metrics': {'enabled': True, 'destination': 'forge://metrics/runtime', 'interval': 60}}}`  
  _source: ./src/bridge.runtime.yaml_
- **deploy** → `{'github': {'workflow': 'bridge_deploy.yml', 'trigger': 'push', 'branches': ['main', 'staging']}, 'targets': [{'name': 'production', 'provider': 'bridge_runtime_handler', 'region': 'auto', 'replicas': 2}, {'name': 'staging', 'provider': 'bridge_runtime_handler', 'region': 'auto', 'replicas': 1}]}`  
  _source: ./src/bridge.runtime.yaml_
- **security** → `{'attestation': {'enabled': True, 'seal_algorithm': 'HMAC-SHA256'}, 'network': {'ingress': [{'port': 8000, 'protocol': 'HTTP'}, {'port': 3000, 'protocol': 'HTTP'}], 'egress': [{'destination': 'forge://dominion', 'protocol': 'HTTPS'}, {'destination': '*.github.com', 'protocol': 'HTTPS'}]}}`  
  _source: ./src/bridge.runtime.yaml_

---
## 📄 Documentation Index

### ./FIREWALL_FIX_SUMMARY.md

- # Firewall Blocking Fix - Browser Downloads
- ## Problem Statement
- ## Root Cause
- ## Solution Implemented
- ### 1. Environment Variables Configuration
- ### 2. NPM Configuration Files
- # Skip browser downloads to avoid firewall blocks
- # Skip browser downloads to avoid firewall blocks
- ### 3. GitHub Actions Workflows
- ### 4. Key Changes Summary
- ## Files Modified
- ### GitHub Workflows (12 files)
- ### GitHub Actions (1 file)
- ### Configuration Files (2 files)
- ### Python Tools (1 file)
- ## Browser Strategy
- ## Testing & Validation
- ## Future Maintenance
- ## Related Scripts
- ## Benefits
- ## Monitoring
- ## Rollback Plan
- ## Additional Notes


### ./CHANGELOG.md

- # SR-AIbridge CHANGELOG
- ## v1.9.7e — Umbra + Netlify Integration Healing (Full Synthesis Drop)
- ### Overview
- ### New Layer: Umbra x Netlify Neural Sync
- ### Components Added
- #### ✅ Netlify Validator Engine
- #### ✅ Validation Script
- #### ✅ Umbra Memory Extensions
- #### ✅ API Routes
- #### ✅ CI/CD Workflow
- ### Environment Additions
- # Umbra + Netlify Integration v1.9.7e
- ### RBAC Enforcement
- ### Testing Results
- ### Cognitive Feedback Loop
- ### Impact
- ### Files Changed
- ### Admiral Summary
- ## v1.9.7d — Project Umbra Ascendant: Memory + Echo Finalization
- ### Overview
- ### The Umbra Cognitive Stack
- ### Core Features
- #### ✅ Umbra Core - Pipeline Self-Healing
- #### ✅ Umbra Memory - Experience Graph & Recall
- #### ✅ Umbra Predictive - Confidence-Based Pre-Repair
- #### ✅ Umbra Echo - Human-Informed Adaptive Learning
- #### ✅ Full Cognitive Lifecycle
- ### Genesis Integration
- ### Environment Configuration
- # Umbra Cognitive Stack v1.9.7d
- ### RBAC & Security
- ### API Endpoints
- ### Test Results
- ### Impact
- ### Admiral Summary
- ## v1.9.7c — Project Chimera: Autonomous Deployment Sovereignty
- ### Overview
- ### Core Features
- #### ✅ Chimera Deployment Engine (CDE)
- #### ✅ Predictive Build Simulation (Leviathan)
- #### ✅ Autonomous Configuration Healing (ARIE)
- #### ✅ Truth Engine Certification (v3.0)
- #### ✅ Deterministic Deployment Protocol
- #### ✅ Cascade Post-Verification
- ### New Components
- #### Chimera CLI (`chimeractl`)
- # Simulate deployment
- # Deploy with certification
- # Monitor status
- # Verify with Truth Engine
- #### API Endpoints
- ### Genesis Bus Integration
- ### Configuration
- ### Files Created
- ### Testing Matrix
- ### Security & Governance
- ### Performance Metrics
- ### Impact
- ### Integration Examples
- ### Complementary Updates
- ### Breaking Changes
- ### Upgrade Notes
- ### Known Issues
- ### Future Roadmap
- ### Final Declaration
- ## v1.9.6p — HXO Ascendant (Federation Nexus)
- ### Overview
- ### Core Features
- #### ✅ Federation Nexus — 9 Engine Integration
- #### ✅ Predictive Orchestration Engine
- #### ✅ Temporal Event Replay Cache (TERC)
- #### ✅ Zero-Downtime Upgrade Path (ZDU)
- #### ✅ Quantum-Entropy Hashing (QEH)
- #### ✅ Harmonic Consensus Protocol (HCP)
- #### ✅ Cross-Federation Telemetry Layer
- #### ✅ Adaptive Load Intent Router (ALIR)
- #### ✅ Auto-Heal Cascade Overwatch (ACH)
- ### Genesis Bus Integration
- ### New Capabilities
- ### Configuration
- ### Files Changed
- ### Testing
- ### Security Enhancements
- ### Impact Metrics
- ### Migration from v1.9.6n
- ### Documentation
- ### Closing Statement
- ## v1.9.6f — Render Bind & Startup Stability Patch (Final)
- ### Overview
- ### Core Features
- #### ✅ Adaptive Port Binding
- #### ✅ Deferred Heartbeat Initialization
- #### ✅ Predictive Watchdog
- #### ✅ Self-Healing Diagnostics
- ### Files Changed
- ### Migration from v1.9.6b
- ### Expected Logs
- ### Success Criteria
- ## v1.9.5 – Unified Runtime & Autonomic Homeostasis (Final Merge)
- ### Overview
- ### Core Features
- #### ✅ Dynamic Port Binding
- #### ✅ Self-Healing Heartbeat
- #### ✅ Bridge Doctor CLI
- #### ✅ Automatic Schema Sync
- #### ✅ Render ↔ Netlify Parity Layer
- #### ✅ Autonomous Diagnostics
- #### ✅ Federation Health Endpoint
- #### ✅ Deployment Guard
- ### Files Added
- ### Files Modified
- ### Technical Details
- #### Self-Healing Heartbeat
- #### Parity Layer
- #### Bridge Doctor CLI
- ### Deployment
- #### Startup Sequence
- #### Expected Render Logs
- ### Federation Diagnostics
- ### Validation Matrix
- ### Breaking Changes
- ### Upgrade Notes
- ### Known Issues
- ## Previous Versions
- ### v1.9.4a+ - Anchorhold Protocol
- ### v1.9.3


### ./REPO_MAP.md

- # SR-AIbridge Repository Comprehensive Map
- ## Executive Summary
- ## File Type Distribution
- ## Key Directories
- ### bridge_backend
- ### bridge-frontend
- ### bridge_core
- ### docs
- ### codex
- ### tools
- ### scripts
- ### tests
- ### DOCTRINE
- ## Root Level Files


### ./BRIDGE_HARMONY_SUMMARY.md

- # 🎻 Bridge Harmony Implementation Summary
- ## Mission Statement
- ## Problem Solved
- ### Before
- ### After
- ## Implementation
- ### Core Components
- ## Architecture Integration
- ### HXO Nexus (Harmonic Conductor)
- ### Umbra Lattice (Neural Memory)
- ### Genesis Federation Bus (Event Router)
- ## Discovered Engines (34 Total)
- ### Core Infrastructure (6)
- ### Super Engines (7)
- ### Utility & Support (21)
- ## Communication Pathways (91 Total)
- ## Metrics Achieved
- ## Usage Examples
- ### CLI Commands
- # Complete harmony fix (recommended)
- # Show current status
- # Individual operations
- ### Python API
- # Full orchestration
- # Check metrics
- ## Files Changed
- ### Modified
- ### Created
- ## Testing
- ### Test Results
- ### Test Coverage
- ## Security
- ## Code Quality
- ### Code Review
- ### Best Practices
- ## Impact
- ### Immediate Benefits
- ### Long-term Benefits
- ## Philosophy
- ## Conclusion


### ./SOVEREIGN_AUDIT_SUMMARY.md

- # 🎉 Sovereign Audit & Repair - Implementation Summary
- ## Mission Accomplished ✅
- ## What Was Delivered
- ### 1. Complete Audit System (3 Tools)
- #### Sovereign Audit Orchestrator
- #### Master Sovereign Audit
- ### 2. Comprehensive Test Suite
- ### 3. Complete Documentation
- #### Full Guide
- #### Quick Reference
- ## Audit Results
- ### Current Status
- ### Detailed Breakdown
- ## Security
- ### Security Review ✅
- ## Usage
- ### Quick Start
- # Run full sovereign audit
- # Expected output:
- # ✅ SOVEREIGN GIT = TRUE - Full sovereignty confirmed!
- ### Individual Audits
- # Run Git/Netlify/Repo audit only
- # Run without auto-repair
- ### Testing
- # Run test suite
- # Expected: 29 passed in 0.26s
- ## Reports Generated
- ## Features
- ### ✅ Comprehensive Coverage
- ### ✅ Auto-Repair
- ### ✅ Detailed Reporting
- ### ✅ CI/CD Ready
- ### ✅ Production Ready
- ## Integration Examples
- ### GitHub Actions
- ### Scheduled Audits
- ## Recommendations
- ## Files Modified
- ### Created Files
- ### Generated Files
- ## Metrics
- ### Code Quality
- ### Audit Performance
- ### Coverage
- ## Success Criteria Met ✅
- ## Final Verdict


### ./FIREWALL_ENGINE_AUDIT_SUMMARY.md

- # Firewall Engine Audit & Repair Summary
- ## Executive Summary
- ## Problem Statement
- ## Solution Implemented
- ### 1. Enhanced Firewall Allowlist
- ### 2. New Firewall Rule for Browser Downloads
- ### 3. Autonomous Browser Download Blocking Detection
- #### a. Proactive Browser Download Check (Step 0)
- #### b. Error Pattern Detection
- #### c. Automatic Remediation
- ### 4. Integration with Firewall Config Manager
- ## Files Modified
- ### Core Engine Files (3 files)
- ### Configuration Files (4 files)
- ## Testing & Validation
- ### Test Results
- ### Manual Testing
- ### Configuration Validation
- ## How It Works
- ### Execution Flow
- ### Autonomous Actions
- ## Benefits
- ### Immediate Benefits
- ### Long-term Benefits
- ## Guardrails & Safety
- ### Safety Measures
- ### Operational Limits
- ## Monitoring & Verification
- ### How to Verify the Fix is Working
- ## Future Enhancements
- ### Recommended Improvements
- ### Potential Extensions
- ## Rollback Plan
- ## Related Documentation
- ## Conclusion


### ./DIAGNOSTIC_REPORT.md

- # SR-AIbridge Repository Diagnostic & Incident Report
- ## Executive Summary
- ## 1. Engine Inventory & Status
- ### Core Engines (bridge_core/engines)
- ### Backend Engines (bridge_backend/engines)
- ### Specialized Engines & Technologies
- ## 2. Documentation Health Check
- ### Documentation Categories:
- ### Key Documentation Status:
- ## 3. Repository Structure Analysis
- ### Root Level Organization
- ### Vault Infrastructure Status
- ### Backend Health
- ### Frontend Health
- ## 4. Incidents & Findings
- ### 🟢 Positive Findings
- ### 🟡 Opportunities for Improvement
- ### 🔴 Critical Issues
- ## 5. Recommendations
- ### High Priority
- ### Medium Priority
- ### Low Priority
- ## 6. Proposed Action Plan
- ### Phase 1: Create Vault Structure
- ### Phase 2: Organize Root Level
- ### Phase 3: Update Documentation
- ## 7. Conclusion


### ./DEPLOYMENT_IMPLEMENTATION_SUMMARY.md

- # Deployment Validation & True Reveal Protocol - Implementation Summary
- ## Executive Summary
- ## What Was Built
- ### 1. Core Services (4 new files)
- #### `bridge-frontend/src/services/deployment-validator.js` (310 lines)
- #### `bridge-frontend/src/services/true-data-revealer.js` (271 lines)
- #### `bridge-frontend/src/services/silent-failure-capture.js` (418 lines)
- #### `bridge-frontend/src/components/DeploymentGate.jsx` (336 lines)
- ### 2. Modified Components (6 files)
- #### `bridge-frontend/src/App.jsx`
- #### `bridge-frontend/src/components/AgentFoundry.jsx`
- #### `bridge-frontend/src/components/MissionLog.jsx`
- #### `bridge-frontend/src/components/AdmiralKeysPanel.jsx`
- #### `bridge-frontend/src/components/BrainConsole.jsx`
- #### `bridge-frontend/src/components/VaultLogs.jsx`
- ### 3. Documentation
- #### `bridge-frontend/DEPLOYMENT_VALIDATION.md` (360 lines)
- ## How It Works
- ### Validation Flow
- ### Data Flow
- ### Health Monitoring
- ## Deployment Modes
- ### Production Mode (All Systems Online)
- ### Degraded Mode (Partial Systems)
- ### Development Mode (No Backend)
- ## Security Benefits
- ### Paranoid Security Gates
- ### Validation Checks
- ## Testing Results
- ### Linting
- ### Build
- ### Security Scanning
- ### Code Review
- ## Usage Examples
- ### Basic Component Wrapping
- ### Data Fetching with Deployment Awareness
- ### Health Monitoring
- ## Files Changed
- ## Statistics
- ## Success Indicators (All Achieved ✅)
- ## Next Steps for Users
- ## Maintenance
- ### Adding New Components
- ### Updating System Validators
- ### Customizing Placeholders
- ## Conclusion


### ./NAVIGATION_GUIDE.md

- # SR-AIbridge Complete Navigation Guide
- ## 🎯 Quick Start
- ## 📊 Repository Overview
- ### Key Stats
- ### Repository Health
- ## 🗂️ Repository Structure Map
- ### Root Level (Essential Files Only)
- ## 🏗️ Core Components
- ### 1. Backend (`bridge_backend/`)
- ### 2. Frontend (`bridge-frontend/`)
- ### 3. Documentation (`docs/`)
- ### 4. Vault (`vault/`)
- ## 🔧 Engine Inventory
- ### Core Engines (`bridge_backend/bridge_core/engines/`)
- ### Backend Engines (`bridge_backend/engines/`)
- ### Special Engines (Codex)
- ## 👥 Role-Based Navigation
- ### New Users / Learning
- ### Developers
- ### DevOps / Deployment
- ### Contributors
- ## 🔍 Finding What You Need
- ### By Topic
- ### By File Type
- ## 📋 Common Tasks
- ### Running the Application
- ### Running Tests
- ### Analyzing the Repository
- ### Working with Database
- # Initialize database
- # Apply patches
- # Maintenance
- ### Accessing Vault UI
- ## 🔗 Key Integrations
- ### ARIE (AI Reasoning & Intelligence Engine)
- ### ALIK (AI Logic Integration Kit)
- ### Truth Engine
- ### Parser Engine
- ### HXO Nexus
- ### Forge Dominion
- ## 🛠️ Maintenance & Tools
- ### Development Tools
- ### Configuration Drift
- ### Line Counting
- ### Smoke Testing
- ## 📦 Dependencies
- ### Python (Backend)
- ### JavaScript (Frontend)
- ### System
- ## 🚀 Deployment
- ### Netlify (Frontend)
- ### Runtime (Backend)
- ### Docker
- ## 📝 Documentation Standards
- ### Adding New Documentation
- ### Archiving Files
- ## 🎓 Learning Paths
- ### Path 1: Understanding SR-AIbridge (1 hour)
- ### Path 2: Development Setup (30 min)
- ### Path 3: Engine Mastery (2-4 hours)
- ### Path 4: Contributing (Variable)
- ## ❓ Troubleshooting
- ### Can't find a specific engine?
- ### Missing dependencies?
- ### Configuration issues?
- ### Tests failing?
- ### Documentation unclear?
- ## 🔐 Security Notes
- ## 📊 Repository Statistics
- ## 🎯 Next Steps
- ## 📞 Support & Contact


### ./IMPLEMENTATION_SUMMARY.md

- # 🎉 GitHub Actions Workflow Optimization - Implementation Complete
- ## Executive Summary
- ## 📊 Results Overview
- ### Before Optimization
- ### After Optimization
- ### Impact
- ## 🔧 Optimizations Implemented
- ### 1. Dependency Caching ⚡
- ### 2. Workflow Consolidation 🔄
- ### 3. Artifact Optimization 💾
- ### 4. Native Bridge Runner Support 🏃
- ### 5. Security Improvements 🔒
- ## 🛠️ Tools & Scripts Created
- ### 1. Workflow Efficiency Audit (`workflow_efficiency_audit.py`)
- ### 2. Auto-Optimizer (`auto_optimize_workflows.py`)
- # Preview changes
- # Apply optimizations
- ### 3. Cost Calculator (`cost_calculator.py`)
- ### 4. Render Integration Script (`render_quantum_security.sh`)
- ## 📁 Files Modified/Created
- ### Modified Workflows (3 files)
- ### New Workflows (2 files)
- ### New Scripts (4 files)
- ### New Documentation (2 files)
- ### Generated Reports (1 file)
- ## 🎯 Time Savings Breakdown
- ### Per-Push Optimization
- ### Monthly Impact (43 pushes)
- ## 📚 Documentation
- ### Primary Guides
- ### Quick Reference
- ## ✅ Validation Complete
- ## 🚀 Next Steps
- ### Immediate Actions
- ### Optional Enhancements
- ## 💡 What Makes This Work
- ### Legitimate Optimizations ✅
- ### Not Attempting ❌
- ### Result 🏆
- ## 📈 Monitoring & Maintenance
- ### Monitor GitHub Actions Usage
- ### Run Regular Audits
- ### Verify Optimizations
- ## 🎊 Conclusion
- ## 📞 Support
- ## 🏅 Achievement Unlocked


### ./SECURITY_AUDIT_SUMMARY.md

- # Security and Repository Audit Summary
- ## Render.com Removal - Migration to BRH Sovereign Deployment
- ## Executive Summary
- ### Key Changes
- ## Changes Implemented
- ### 1. Files Archived (`.archive/render_legacy/`)
- ### 2. Environment Configuration Updates
- #### Updated Files:
- #### Key Changes:
- ### 3. GitHub Workflows Updated
- #### Modified Workflows:
- #### Key Changes:
- ### 4. Python Code Modifications
- #### Files Modified:
- ### 5. Scripts Updated
- #### Modified Scripts:
- ### 6. Documentation Updates
- #### Files Updated:
- #### Key Documentation Changes:
- ## Security Scan Results
- ### CodeQL Analysis (2025-11-05)
- #### Alert Fixed:
- #### Python Security:
- ## Migration Path
- ### Old Architecture:
- ### New Architecture (BRH):
- ### Benefits:
- ## Deployment Instructions
- ## Testing & Validation
- ### Code Compilation:
- ### Import Validation:
- ### Workflow Validation:
- ## Breaking Changes
- ### Environment Variables Removed:
- ### Environment Variables Added:
- ### API Changes:
- ## Backward Compatibility
- ### Archived Files:
- ### Legacy Support:
- ## Recommendations
- ### Immediate Actions:
- ### Future Enhancements:
- ## Audit Checklist
- ## Conclusion


### ./HEALING_NET_IMPLEMENTATION.md

- # Healing Net System Implementation
- ## Overview
- ## Architecture
- ### Core Components
- #### 1. API Guardian (`healing-net.js`)
- #### 2. Umbra Lattice
- #### 3. Circuit Breakers
- #### 4. Triage Engine
- ### Frontend Integration
- #### Error Boundaries
- #### Healing Net Dashboard
- ## Backend Enhancements
- ### Custody Routes (Admiral Keys)
- #### New Endpoints
- ### Mission Routes
- #### New/Updated Endpoints
- ## Agent Foundry
- ### Features
- ### Auto-Indoctrination
- ## Mission Progress Tracking
- ### Real-Time Progress
- ## Deployment Checklist
- ### Frontend
- ### Backend
- ## Testing
- ### Frontend Testing
- ### Manual Testing
- ## Monitoring
- ### Health Status
- ### Failure Logs
- ### Circuit Breaker States
- ## Configuration
- ### API Client
- ### Circuit Breaker Tuning
- ## Troubleshooting
- ### "HTML response detected" errors
- ### Circuit breaker keeps opening
- ### Components keep crashing
- ## Future Enhancements
- ### Planned Features
- ### Performance Optimizations
- ## API Reference


### ./KEYLESS_SECURITY_IMPLEMENTATION.md

- # Keyless Security Implementation Summary
- ## 🎯 Mission Accomplished
- ## What Was Changed
- ### Problem Statement
- ### Solution Implemented
- #### 1. Frontend Changes (JavaScript)
- #### 2. Backend Changes (Python)
- #### 3. Testing (Python)
- #### 4. Documentation
- ## Test Results
- ## Validation Output
- ### True Deployment Check
- ### Auth System Status
- ## Security Improvements
- ### Attack Surface Eliminated
- ### Benefits Achieved
- ## Files Changed
- ## Admiral's Insight Validated
- ## Next Steps for Users
- ### For Developers
- # ❌ Old: Loading static keys
- # ✅ New: Generating ephemeral session
- ### For Security Auditors
- ### For Operations
- ## Status


### ./START_HERE.md

- # 🎉 Documentation Enhancement Complete!
- ## Your SR-AIbridge Documentation is Now Comprehensive and Navigable
- ## 🎯 What Just Happened?
- ## 📚 Your New Documentation System
- ### 1. Master Index (START HERE!)
- ### 2. Feature Inventory
- ### 3. Usage Guide
- ### 4. Enhancement Plan
- ### 5. Improvement Summary
- ## 🚀 Quick Start: Finding What You Need
- ### Method 1: Use the Master Index (Recommended)
- ### Method 2: Browse the Feature Inventory
- ### Method 3: Follow a Learning Path
- ## 📊 What You Now Have
- ### Coverage Stats
- ### Navigation Power
- ## 🎓 Your Documentation Journey
- ### If You're New to SR-AIbridge
- ### If You're a Developer
- ### If You're Looking for Something Specific
- ## 💡 Pro Tips
- ## 🔥 Key Features You Can Now Utilize
- ### Engines (20+)
- ### Backend (47 modules)
- ### Frontend (37 components)
- ## 🎯 What's Next?
- ### This PR (COMPLETE ✅)
- ### Next Phase (Weeks 3-4)
- ### Future (Weeks 5-8)
- ## 🤝 How to Contribute
- ## 📖 Remember
- ## 🎉 Start Exploring!


### ./README.md

- # 🚀 SR-AIbridge
- ## 📚 **ENHANCED: Complete Documentation Suite (100,000+ Lines)**
- ### 🎯 Start Here: Documentation Navigator
- ### 📊 Documentation Coverage
- ## ✨ What is SR-AIbridge?
- ## 📋 Table of Contents
- ## 🚀 Quick Start
- ### Prerequisites
- ### Development Setup
- ### Access Points
- ### Health API (v1.6.8)
- ### Demo Data
- ## 🎯 Features
- ### Core Capabilities
- #### 🤖 AI Agent Management
- #### 🎯 Mission Control
- #### 🛡️ Health Monitoring & Self-Healing
- #### 🔐 Security & Attestation
- #### 💬 Communication Systems
- #### 🚢 Fleet & Armada Management
- #### 📜 Vault Logging & Doctrine
- #### 🧠 Advanced Features
- #### 🔍 Autonomy Engine with Originality Verification
- #### 🔗 Unified Autonomy Integration (NEW)
- ## 📦 Installation
- ### System Requirements
- ### Backend Installation
- # Edit .env with your settings
- ### Frontend Installation
- # Create .env.local file
- # or
- ### Verify Installation
- ### Load Demo Data
- ### Troubleshooting Installation
- # If not, install Python 3.12 from python.org
- # If not, install from nodejs.org or use nvm
- # Backend on different port
- # Frontend on different port
- # Delete and recreate database
- # Reinstall dependencies
- ### Deployment Verification & Compliance (v1.6.6)
- # 1. Validate environment configuration
- # 2. Validate scanner compliance
- # 3. Install Netlify plugins (frontend)
- # 4. Run pre-build sanitizer
- # 5. Build and verify
- # 6. Test deployment locally
- # Check backend health
- # Check frontend health
- # Full bridge diagnostics
- # Verify environment sync
- ## 🔌 API Documentation
- ### Interactive Documentation
- ### Core Endpoints
- #### Health & System
- #### Agent Management
- #### Mission Control
- #### Vault Logs
- #### Guardian System
- #### Fleet Management
- #### Communication
- #### Admiral Keys & Custody
- #### Utilities
- ### Six Super Engines
- ### WebSocket Endpoints
- ### Error Responses
- ### Rate Limiting
- ### Authentication
- ## 🎨 Frontend Components
- ### Main Application
- ### Dashboard & Monitoring
- ### Mission & Fleet
- ### Communication
- ### Data & Logging
- ### Administration
- ### UI Components
- ## 🧠 Six Super Engines
- ### 1. CalculusCore (Math Engine)
- ### 2. QHelmSingularity (Quantum Engine)
- ### 3. AuroraForge (Science Engine)
- ### 4. ChronicleLoom (History Engine)
- ### 5. ScrollTongue (Language Engine)
- ### 6. CommerceForge (Business Engine)
- ### Engine Testing
- ### Full Endpoint Testing
- # Custom timeout
- # JSON output for CI/CD
- # Combine options
- ### Health & Monitoring
- ### Core Endpoints
- ### Agent Management  
- ### Mission Control
- ### Vault Logs
- ### Guardian System
- ### Communication
- ### Fleet Management
- ### Utilities
- ## 🎮 Demo & Testing
- ### Run the Demo Seed Script
- ### Interactive API Documentation
- ## 🏗️ Architecture
- ### System Overview
- ### Technology Stack
- #### Backend
- #### Frontend
- ### Database Schema
- #### Core Models
- ### Frontend Architecture
- ### Backend Module Organization
- ## 🚢 Deployment
- ### Development Deployment
- # Terminal 1: Backend
- # Terminal 2: Frontend
- # Build and run with Docker Compose
- # View logs
- # Stop
- ### Production Deployment
- #### BRH (Backend) + Netlify (Frontend)
- #### Alternative: Heroku
- # Install Heroku CLI
- # Build and deploy
- # Deploy dist/ to Heroku or any static host
- #### Alternative: AWS (EC2 + S3)
- # Install dependencies
- # Clone and setup
- # Run with systemd
- # Build
- # Deploy to S3
- # Invalidate CloudFront
- #### Container Deployment (Docker)
- #### Kubernetes Deployment
- # backend-deployment.yaml
- ### Database Scaling
- ### Environment Configuration
- # Database
- # Security
- # Features
- # Monitoring
- ### Health Checks
- ### Scaling Considerations
- ## 🔄 CI/CD & Monitoring
- ### GitHub Actions Workflows
- #### 🚀 Deployment Pipeline
- # Required GitHub Secrets (optional but recommended)
- # BRH deployment managed independently - see docs/BRH_DEPLOYMENT_GUIDE.md
- #### 🧪 Health Monitoring Workflow
- ### Self-Test Script
- # Quick production health check
- # CI/CD optimized with custom settings
- # Local development testing
- # Verbose output with detailed logs
- ### Engine Smoke Test Script
- # Test all engines on local backend
- # Test engines on production deployment
- # Verbose output with detailed logging
- # Custom timeout and retry configuration
- # Save logs to specific directory
- ### Monitoring Dashboard
- # Add to main.py
- # Add prometheus_client
- ### Continuous Deployment
- # Via GitHub
- # Via BRH Dashboard
- # Select previous deployment → "Deploy"
- # Via Netlify Dashboard
- # Deployments → Select previous → "Publish deploy"
- # Clear Netlify cache and redeploy
- # 1. Go to Netlify Dashboard
- # 2. Site settings → Build & deploy → Clear cache
- # 3. Trigger deploy → Deploy site
- # Trigger BRH redeploy
- # 1. Go to BRH Dashboard
- # 2. Select your service
- # 3. Manual Deploy → Deploy latest commit
- # Test backend health endpoint
- # Test diagnostics sync endpoint
- # Verify bridge status
- # Check environment sync status
- # Validate environment setup
- # Auto-repair Netlify environment
- # Check environment parity between platforms
- # Report bridge event to diagnostics
- # Run full environment sync monitor
- ### Performance Monitoring
- ### Alerts and Notifications
- # alerts.yaml
- ## 🔥 Firewall Intelligence Engine
- ### Overview
- ### Capabilities
- ### Error Signatures Detected
- ### Generated Artifacts
- ### Workflows
- ### Usage
- # Run the full firewall intelligence + autonomy engine
- # Review autonomy logs
- # Check vault records
- # Fetch firewall incidents
- # Analyze findings
- # Review reports
- # Trigger unified autonomy engine
- # Or trigger basic intelligence scan
- # Or manually via GitHub Actions UI
- # Actions → Firewall Intelligence and Autonomy Engine → Run workflow
- ### Critical Domains
- ### The Firewall Oath
- ### Documentation
- ## ⚙️ Configuration
- ### Environment Variables
- #### Backend Configuration
- # Database type (sqlite or postgres)
- # Database connection URL
- # For PostgreSQL: postgresql://user:pass@host:5432/dbname
- # Server host and port
- # Environment (development, staging, production)
- # Python version
- # Secret key for cryptographic operations
- # CORS configuration
- # API key for protected endpoints (optional)
- # Enable/disable features
- # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- # Health check interval in seconds
- # Enable detailed request logging
- # Stripe payment integration (optional)
- # Email service (optional)
- #### Frontend Configuration
- # Backend API base URL
- # WebSocket base URL
- # Alternative API URL for fallback
- # Enable debug mode
- # Enable experimental features
- # Auto-refresh intervals (milliseconds)
- # Theme (light, dark, auto)
- # Language (en, es, fr, etc.)
- # Enable animations
- ### Configuration Files
- ### Deployment Configuration
- # BRH sovereign runtime configuration
- ### Advanced Configuration
- # db.py
- ## 🔒 Security
- ### Security Features
- #### 🔐 Cryptographic Security
- #### 🛡️ API Security
- # Configure allowed origins
- # CORS middleware in FastAPI
- #### 🔑 Authentication & Authorization
- # Permission matrix
- #### 🗄️ Database Security
- # Use SSL for PostgreSQL connections
- # Connection encryption
- # Encrypt sensitive fields
- #### 🌐 Network Security
- # Secure WebSocket connections
- # Origin validation
- # Prevent abuse
- #### 🔍 Security Monitoring
- ### Security Best Practices
- #### For Development
- #### For Production
- ### Security Checklist
- ### Reporting Security Issues
- ## 🔧 Troubleshooting
- ### Common Issues and Solutions
- #### Backend Issues
- # Error: ModuleNotFoundError
- # Error: Port already in use
- # Find process using port 8000
- # Kill process or use different port
- # Error: Python version too old
- # Install Python 3.12 from python.org
- # Error: database is locked
- # SQLite doesn't support concurrent writes well
- # Upgrade to PostgreSQL for production
- # Error: table doesn't exist
- # Delete and recreate database
- # Error: connection timeout
- # Check database URL in .env
- # Verify database server is running
- # Increase timeout in connection settings
- # Try manual self-heal
- # Check logs
- # Verify all services
- # Restart backend
- # Ctrl+C to stop, then:
- # Run engine smoke test
- # Check if engines are enabled
- # Verify engine dependencies
- # Check engine logs
- #### Frontend Issues
- # Error: Cannot find module
- # Error: Port 3000 already in use
- # Error: Node version too old
- # Install Node 18+ from nodejs.org or use nvm
- # Check backend is running
- # Check CORS settings
- # In bridge_backend/main.py, verify ALLOWED_ORIGINS includes frontend URL
- # Check API endpoint in frontend
- # Create bridge-frontend/.env.local:
- # Restart frontend
- # Error: Out of memory
- # Increase Node memory limit
- # Error: Module build failed
- # Clear build cache
- # Error: Terser minification failed
- # Disable minification temporarily
- # In vite.config.js:
- #### Deployment Issues
- # Check build logs in BRH runtime management
- # Common issues:
- # 1. Wrong Python version
- # 2. Dependencies not installing
- # 3. Database connection fails
- # 4. Health check timeout
- # Check build logs in Netlify dashboard
- # Common issues:
- # 1. Build command fails
- # 2. Environment variables missing
- # 3. React Router 404 errors
- # 4. Build timeout
- #### Database Issues
- # SQLite limitations:
- # - Single writer at a time
- # - No concurrent writes
- # - Limited connection pooling
- # Update .env:
- # No code changes needed!
- # Error: could not connect to server
- # Verify PostgreSQL is running
- # Check connection string
- # Test connection
- # Check firewall rules
- # Ensure port 5432 is open
- # Backup before migration
- # If migration fails, restore
- # Manual migration
- # Export from SQLite:
- # Import to PostgreSQL:
- #### Performance Issues
- # Check system metrics
- # Enable query logging
- # Common causes:
- # 1. Database not indexed
- # 2. N+1 query problem
- # 3. Large result sets
- # 4. No caching
- # Monitor memory
- # Backend:
- # Frontend:
- # Check browser dev tools → Memory
- # Solutions:
- # 1. Limit result set sizes
- # 2. Implement pagination
- # 3. Add caching
- # 4. Optimize queries
- # 5. Increase server resources
- # Too many connections
- # Messages too frequent
- # Large message payloads
- #### Network Issues
- # Backend not responding
- # 1. Check backend is running
- # 2. Verify health endpoint works
- # 3. Check reverse proxy config
- # 4. Increase timeout settings
- # Error: certificate verify failed
- # 1. Check certificate is valid
- # 2. Verify certificate chain
- # 3. Update CA certificates
- # 4. For development, disable verification (not recommended)
- ### Debugging Tips
- # Backend
- # Frontend
- # Interactive testing
- # Test endpoints directly
- # Backend logs
- # Deployment logs
- # BRH: View in dashboard
- # Netlify: View in dashboard
- # Local logs
- # Terminal output shows real-time logs
- # SQLite
- # PostgreSQL
- # Test connectivity
- # Check WebSocket
- # Monitor network traffic
- # Use browser DevTools → Network tab
- ### Getting Help
- ## 🤝 Contributing
- ### How to Contribute
- # Click "Fork" on GitHub, then clone your fork
- # Create a feature branch
- # Or a bugfix branch
- # Backend changes
- # Make changes to Python files
- # Frontend changes
- # Make changes to React components
- # Documentation changes
- # Edit .md files
- # Backend tests
- # Frontend tests
- # Manual testing
- # Start backend and frontend, verify functionality
- # Stage your changes
- # Commit with descriptive message
- # Push to your fork
- ### Contribution Guidelines
- #### Code Style
- # Follow PEP 8
- # Use type hints
- # Use async/await for async operations
- # Format: type(scope): description
- # Types:
- # Examples:
- #### Testing Requirements
- # tests/test_agents.py
- #### Documentation
- #### Review Process
- ### Development Setup
- # Create virtual environment
- # Install dev dependencies
- # Run tests
- # Format code
- # Lint code
- # Run with auto-reload
- # Install dependencies
- # Run dev server with hot reload
- # Run tests
- # Run tests in watch mode
- # Lint code
- # Build for production
- ### Areas for Contribution
- #### 🐛 Bug Fixes
- #### ✨ Features
- #### 📚 Documentation
- #### 🧪 Testing
- #### 🎨 UI/UX
- #### 🔧 DevOps
- ### Reporting Bugs
- ### Feature Requests
- ### Code of Conduct
- ### Recognition
- ## 📊 Performance
- ### Benchmarks
- ### Optimization Tips
- # 1. Database connection pooling
- # 2. Query optimization
- # Use select_related/joinedload for related data
- # 3. Pagination
- # 4. Caching
- # 5. Async operations
- ### Scaling Strategies
- # Redis caching
- ## 📚 Additional Resources
- ### Documentation Files
- ### Project Documentation
- ### External Resources
- ### Community
- ### Related Projects
- ## 📄 License
- ## 🙏 Acknowledgments
- ### Core Technologies
- ### Inspiration
- ### Contributors
- ### Special Thanks
- ## 🗺️ Roadmap
- ### Current Version (v1.1.0)
- ### Upcoming Features (v1.2.0)
- ### Future Plans (v2.0.0)
- ### Community Requests
- ## 📞 Support
- ### Getting Help
- ### Professional Support
- ## 🌐 Netlify Config & Egress Status
- ## ⭐ Star History
- ## 🧠 Bridge Runtime Handler (BRH)
- ### Sovereign Deployment Without Vendor Lock-In
- # src/bridge.runtime.yaml
- # 1. Configure Forge Dominion
- # 2. Create runtime manifest
- # 3. Deploy


### ./WALKTHROUGH_SUMMARY.md

- # 🎯 Repository Walkthrough Complete - Executive Summary
- ## ✅ Mission Accomplished
- ## 📊 What Was Done
- ### 1. Complete Repository Mapping ✅
- ### 2. Full Diagnostic & Incident Report ✅
- ### 3. Complete Navigation Guide ✅
- ### 4. Vault Organization ✅
- ## 🔍 Key Findings
- ### 🟢 Repository Health: EXCELLENT
- ## 📚 Technology Stack Verified
- ### Engines Catalogued (33+)
- ## 🌉 Bridge UI Integration
- ## 📁 Repository Organization Impact
- ### Before Organization
- ### After Organization
- ## 🎯 Deliverables Summary
- ## 🔐 Sovereign Git Mode
- ## 📖 Using Your New Documentation
- ### Quick Start Navigation
- ## 🏆 Achievement Metrics
- ### Documentation Coverage
- ### Organization Impact
- ### Quality Metrics
- ## 🚀 Next Steps (Optional Future Work)
- ### High Priority
- ### Medium Priority
- ### Low Priority
- ## 📞 How to Use This Work
- ### For Team Members
- ### For New Contributors
- ### For DevOps
- ## ✨ Final Status
- ## 🎓 Summary


### ./SOVEREIGN_ENGINES_DEPLOYMENT.md

- # SOVEREIGN-ENGINES Deployment Summary
- ## Overview
- ## Implementation Summary
- ### ✅ PR #1: MicroScribe & Compliance Guard - COMPLETE
- ### ✅ PR #2: MicroLogician Integration & Analytics - COMPLETE
- ## Technical Specifications
- ### Architecture
- ### API Endpoints (9 Total)
- ### Analysis Modes
- ### Security Levels
- ## Quality Assurance
- ### Test Coverage
- ### Verification
- ### Code Review
- ### Security Scan
- ## Configuration
- ### Environment Variables
- # Enable/disable engines
- # License key (production)
- # Bridge resonance
- # Minimum resonance threshold
- # Policy directory (optional)
- ### Sovereign Policy
- ## Deployment Instructions
- ### Prerequisites
- ### Enable Engines
- ### Start Server
- ### Verify Deployment
- # Run verification
- # Run smoke tests (server must be running)
- ## Usage Examples
- ### 1. Analyze Git Diff
- ### 2. Generate PR Template
- ### 3. Analyze Logs
- ### 4. Check Compliance
- ### 5. Complete Workflow
- ## Integration Points
- ### Genesis Event Bus
- ### Bridge Core
- ### Main Application
- ## Performance Characteristics
- ### Resource Usage
- ### Scalability
- ### Latency
- ## Monitoring & Observability
- ### Health Checks
- ### Status Monitoring
- ### Audit Trail
- ## Security Considerations
- ### Quantum-Resistant
- ### Data Protection
- ### Compliance
- ## Troubleshooting
- ### Issue: Compliance violations
- ### Issue: Routes not loading
- ### Issue: Policy file not found
- ## Support & Maintenance
- ### Documentation
- ### Testing
- ## Changelog
- ### Version 1.0.0 (2025-11-05)
- ## Conclusion


### ./BRIDGE_HARMONY_REPORT.md

- # 🎻 Bridge Harmony & Communication Report
- ## System Overview
- ### Engines by Category
- #### Core Engines (6)
- #### Super Engines (7)
- #### Utility Engines (21)
- ## Communication Pathways
- ### Genesis Bus (33)
- ### Direct (26)
- ### Umbra Lattice (32)


### ./DEPLOYMENT_VISUAL_GUIDE.md

- # Deployment Validation Protocol - Visual Guide
- ## Before & After Comparison
- ### Before Implementation
- ### After Implementation
- ## UI Components
- ### 1. Deployment Status Badge (Header)
- ### 2. Placeholder Component
- ### 3. Real Component (Deployed)
- ## Component Flow Diagrams
- ### Agent Foundry Flow
- ### Data Service Flow
- ## Health Monitoring Flow
- ## Console Output Examples
- ### Development Mode (No Backend)
- ### Production Mode (All Systems Online)
- ### Health Check Recording
- ### Crash Forensics Example
- ## File Structure
- ## Testing Scenarios
- ### Scenario 1: Pure Frontend Development
- # Expected:
- # - All components show placeholders
- # - Status badge shows "DEVELOPMENT"
- # - No crashes or errors
- # - Console shows validation failures (expected)
- ### Scenario 2: Backend Available
- # Terminal 1
- # Terminal 2  
- # Expected:
- # - Components show real data
- # - Status badge shows "PRODUCTION"
- # - Console shows validation success
- # - Health monitoring active
- ### Scenario 3: Partial Backend
- # Start only some backend services
- # Expected:
- # - Status badge shows "DEGRADED"
- # - Some components show real data
- # - Others show placeholders
- # - Clear indication which systems are down
- ## Key Features Demonstrated
- ### 1. Paranoid Security ✅
- ### 2. Health Monitoring ✅
- ### 3. Deployment Awareness ✅
- ### 4. Developer Experience ✅
- ### 5. User Experience ✅
- ## Conclusion


### ./SOVEREIGN_DEPLOYMENT.md

- # Sovereign Deployment Mode
- ## Overview
- ## What Changed
- ### 1. Environment Variable Strategy
- ### 2. Files Modified (33 total)
- #### Network Policies (2 files)
- #### GitHub Workflows (18 files)
- #### Python Scripts (10 files)
- #### Firewall & Network Tools (3 files)
- ## How to Deploy
- ### Option 1: Sovereign Mode (Recommended)
- # Set your backend URL
- # Or use GitHub Secrets for workflows
- # Deploy
- ### Option 2: With Legacy Render Support
- # Set backend URL
- # Optional: Set Render API credentials for advanced features
- # Deploy
- ### Option 3: Custom Backend Provider
- # GitHub Secrets
- # Optional: Custom API credentials
- ## Migration Guide
- ### From Render.com to Sovereign
- ### From Legacy Setup to Environment Variables
- ## Backward Compatibility
- ## Verification
- ### Check Your Configuration
- # List current secrets
- # Expected for sovereign mode:
- # - BACKEND_URL (or uses default)
- # - NETLIFY_AUTH_TOKEN
- # - FORGE_DOMINION_ROOT
- # Not required:
- # - RENDER_API_KEY ✗
- # - RENDER_SERVICE_ID ✗
- ### Test Deployment
- # Trigger deploy workflow
- # Monitor logs
- # Look for:
- # ✅ Backend URL: https://bridge.sr-aibridge.com (or your custom URL)
- # ✅ Health checks passing
- # ✅ No Render API errors
- ### Verify Health Checks
- # Test backend health
- # Test frontend
- # Check sync status
- ## Benefits
- ### 🎯 Vendor Independence
- ### 🔒 Security
- ### 💰 Cost Optimization
- ### 🚀 Flexibility
- ## Troubleshooting
- ### Health Checks Failing
- # Check your BACKEND_URL is set correctly
- # Update if needed
- # Verify endpoint is accessible
- ### Environment Variables Not Working
- # Clear browser/workflow cache
- # Force new run
- ### Render Features Not Working
- # Ensure Render credentials are set
- # Set backend URL to Render
- ## Architecture
- ## References
- ## Support


### ./HEALING_NET_SUMMARY.md

- # SR-AIbridge: Healing Net Implementation - Complete Summary
- ## Mission Accomplished ✅
- ## The Problem (From Oracle's Diagnosis)
- ## The Solution (What We Built)
- ### 1. HEALING NET ACTIVATION 🩹
- ### 2. ERROR BOUNDARIES - Component Isolation 🛡️
- ### 3. AGENT FOUNDRY 🛠️ - Invisible Indoctrination Engine
- ### 4. MISSION PROGRESS TRACKING 🎯
- ### 5. BACKEND API FIXES 🔧
- # New endpoints - All return JSON
- # Enhanced endpoint
- ### 6. HEALTH MONITORING DASHBOARD 🩺
- ## File Structure
- ### New Files Created
- ### Modified Files
- ## Testing Results
- ### Frontend Build
- ### Code Quality
- ## Deployment Guide
- ### 1. Frontend Deployment
- # Deploy dist/ folder
- ### 2. Backend Deployment
- ### 3. Environment Variables
- ## Usage Examples
- ### 1. View System Health
- ### 2. Create Agent with Auto-Indoctrination
- ### 3. Track Mission Progress
- ### 4. Monitor API Failures
- ## Architecture Diagram
- ## Metrics & Impact
- ### Before Implementation
- ### After Implementation
- ### Performance
- ## Future Enhancements
- ### Planned (Not in Scope)
- ### Performance Optimizations
- ## Troubleshooting
- ### "HTML response detected" error
- ### Component crash
- ### Circuit breaker keeps opening
- ### Progress not updating
- ## Support & Documentation
- ## Credits
- ## Status: PRODUCTION READY ✅


### ./FRONTEND_INTEGRATION_COMPLETE.md

- # Frontend Integration Complete - BRH + Netlify Deployment
- ## Executive Summary
- ## What Was Implemented
- ### 1. Production-First Frontend Configuration
- ### 2. Environment Configuration
- ### 3. Deployment Workflow Updates
- ### 4. Code Quality Improvements
- ### 5. Deployment Verification
- ## Architecture Overview
- ## Environment Configuration
- ### Production (Netlify Deployment)
- ### Development (Local)
- ### Override (Via GitHub Secrets)
- ## Build Output
- ## UI Features Verified
- ## Deployment Checklist
- ## How to Deploy
- ## Manual Deployment
- # 1. Build the frontend
- # 2. Verify the deployment
- # 3. Deploy to Netlify (requires Netlify CLI)
- ## Troubleshooting
- ### UI Not Loading
- ### API Connection Failures
- ### Build Failures
- ## Next Steps
- ## Technical Details
- ## Security Considerations
- ## Performance Metrics
- # Phase 2: Vite + React Integration - COMPLETE ✅
- ## 🎯 Mission Update (November 2025)
- ## 🆕 What's New in Phase 2
- ### Services & Infrastructure
- ### New Components
- ### Enhanced Styling
- ### Vite Configuration Enhancements
- ## 📊 Updated Build Metrics
- ## ✅ Quality Assurance Results
- ### Code Review
- ### Security Scan (CodeQL)
- ## 🎨 Component Integration
- ## 🔌 Enhanced API Integration
- ## 📱 Responsive Design Verified
- ## 🚀 Deployment Ready
- # Build with all Phase 2 enhancements
- # Deploy to Netlify (auto-configured)
- ## �� Phase 2 Success Metrics


### ./SECURITY.md

- # SR-AIbridge — Security & Responsible Disclosure
- ## Purpose
- ## Responsible Disclosure
- ## Key Security Principles
- ## Data Protection & Vaulting
- ## Federation Security
- ## Fault Injection & Testing Safety
- ## Secrets & Keys
- ## Incident Response (high-level)
- ## CI/CD & Dependency Management
- ## Contributors & Pre-commit
- ## Contact & Escalation


### ./SOVEREIGNTY_IMPLEMENTATION_SUMMARY.md

- # 👑 SOVEREIGN ARCHITECTURE - IMPLEMENTATION SUMMARY
- ## Mission Accomplished ✅
- ## What Was Built
- ### 🏗️ Core Architecture (5 Components)
- ## Testing & Quality ✅
- ### Test Coverage
- ### Test Results
- ### Security Analysis
- ## Operational Metrics 📊
- ### Firewall Status
- ### Network Health
- ### Validation Status
- ### Script Execution
- ## Generated Artifacts 📁
- ### Configuration Files
- ### Diagnostic Reports
- ### Code Assets
- ### Tests
- ### Documentation
- ### GitHub Actions
- ## Integration 🔄
- ### GitHub Actions Workflow
- ### Command-Line Interface
- # Execute complete sovereignty protocol
- # Expected output: SOVEREIGN AUTHORITY ESTABLISHED
- ## Key Features 🎯
- ### Security First
- ### Observability
- ### Resilience
- ### Maintainability
- ## Design Principles Applied ⚡
- ### Sovereign Mindset
- ### Architectural Excellence
- ## Code Review Results ✅
- ## Performance Benchmarks 🚀
- ### Execution Time
- ### Resource Usage
- ## Documentation Quality 📚
- ### Coverage
- ### Accessibility
- ## Future Extensibility 🔮
- ## Success Criteria Met ✅
- ## Bottom Line 💎
- ## Quick Start Commands
- ### Execute Sovereignty Protocol
- ### Run Tests
- ### View Latest Report
- ### Check Status
- ## References


### ./scripts/README.md

- # Scripts Directory
- ## 🔍 Full System Scan
- ### `run_full_scan.py` - Comprehensive System Check ⭐
- # Run full scan with progress output
- # Run quietly (just show pass/fail results)
- # Output results as JSON
- # Set custom timeout (default: 60s)
- ## 🔐 Validation & Security
- ### `validate_env_setup.py`
- ### `validate_netlify.py`
- ### `validate_envsync_manifest.py`
- ### `integrity_audit.py`
- ### `validate_copilot_env.py`
- ## 🌐 Netlify Operations
- ### `netlify_build.sh`
- ### `netlify_rollback.py`
- ### `repair_netlify_env.py`
- ### `verify_netlify_build.py`
- ### `synthesize_netlify_artifacts.py`
- ## 🧹 Maintenance & Cleanup
- ### `comprehensive_repo_scan.py`
- ### `repo_cleanup.py`
- ### `prune_diagnostics.py`
- ### `clean_stub_todos.py`
- ### `fix_deprecated_datetime.py`
- ## 🔄 Environment & Parity
- ### `check_env_parity.py`
- ### `scan_manual_env_vars.py`
- ## 🛡️ Security & Firewall
- ### `firewall_watchdog.py`
- ## 🧪 Verification Scripts
- ### `verify_autonomy_node.py`
- ### `verify_reflex_loop.py`
- ### `verify_umbra_lattice.py`
- ## 📊 Reporting
- ### `report_bridge_event.py`
- ## 🚀 Deployment & Build
- ### `arie_run_ci.sh`
- ### `migrate_workflows_to_forge.sh`
- ### `start.sh`
- ## 🌱 Bootstrap & Seeding
- ### `seed_bootstrap.py`
- ## 📝 EnvSync
- ### `view_envsync_manifest.py`
- ## 📖 Usage Guidelines
- ### Running Scripts
- ### Common Patterns
- ### Environment Variables
- ## 🆘 Getting Help
- ## 📚 Related Documentation


### ./docs/ETHICS_IMPACT_TEMPLATE.md

- # Ethics Impact Statement (template) — include in PRs for major features
- ## 1) Description
- ## 2) Potential Misuses
- ## 3) Mitigations & Controls
- ## 4) Data Sensitivity
- ## 5) Federation / External Dependencies
- ## 6) Approval


### ./docs/HXO_ENGINE_MATRIX.md

- # HXO Engine Matrix — Detailed Interlinks
- ## Engine Interaction Map
- ### HXO ↔ Autonomy
- ### HXO ↔ Blueprint
- ### HXO ↔ Truth
- ### HXO ↔ Cascade
- ### HXO ↔ Federation
- ### HXO ↔ Parser
- ### HXO ↔ Leviathan
- ### HXO ↔ ARIE
- ### HXO ↔ EnvRecon
- ## Cross-Engine Telemetry Flow
- ## Federation Coordination Matrix
- ## Consensus Protocol Flow
- ## Link Channel Health Monitoring
- ## Emergency Failover Procedures


### ./docs/GITHUB_FORGE.md

- # GitHub Forge
- ## Overview
- ## Features
- ## Usage
- ### Python
- # Write JSON configuration
- # Read JSON configuration
- # Write environment file
- ## Storage Location
- ## Integration
- ## Benefits


### ./docs/DOMINION_DEPLOY_GUIDE.md

- # Forge Dominion Deployment Guide v1.9.7s-SOVEREIGN
- ## Quick Start
- ### 1. Generate Root Key
- # Generate new root key
- ### 2. Set Configuration Variables
- # Set forge mode
- # Set forge version
- ### 3. Verify Installation
- # Run quantum predeploy orchestrator
- ## Deployment Environments
- ### Local Development
- # Bootstrap will auto-generate local key
- ### Staging/Production
- # Mandatory
- # Optional (with defaults)
- ## GitHub Actions Integration
- ### Workflow Setup
- ### Integration with Existing Workflows
- ## Render Deployment
- ### Environment Variables
- ### Build Command
- ## Netlify Deployment
- ### Environment Variables
- ### Build Settings
- ## Token Management
- ### Generate Provider Tokens
- # Initialize authority
- # Mint token for Render
- ### Validate Tokens
- # Verify token
- ## Security Scanning
- ### Manual Scan
- ### Pre-Commit Hook
- ## Key Rotation
- ### Manual Rotation
- # Generate new root key
- ### Automated Rotation (Future)
- ## Monitoring & Compliance
- ### Health Check
- ### Compliance Report
- ### View Audit Trail
- ## Troubleshooting
- ### Root Key Not Found
- # Generate and set root key
- # Or for GitHub Actions
- ### Security Scan Failures
- ### Low Resonance Score
- ### Token Validation Failures
- ## Best Practices
- ### Security
- ### Operational
- ### Development
- ## Support & Resources


### ./docs/DOMINION_SECURITY_SPEC.md

- # 🜂 Dominion Security Specification — v1.9.7s-SOVEREIGN
- ### "Quantum resistance is not a feature; it is survival."
- ## 🧩 Purpose
- ## ⚙️ Core Cryptographic Framework
- ## 🧱 Zero-Trust Validation Matrix
- ## 🔐 Token Anatomy
- ## 🧮 Entropy Audit Procedure
- ## 🧭 Threat Response Hierarchy
- ## 🧬 Audit Trail Schema
- ## 🧰 Verification Commands
- ### Validate Configuration
- ### Issue & Verify Token
- ## 🛡 Governance Notes
- ## 🕊 Lore Appendix


### ./docs/CHIMERA_CERTIFICATION_FLOW.md

- # Chimera Certification Flow
- ## Truth Engine v3.0 Certification Mechanics
- ## Overview
- ## Certification Protocol: TRUTH_CERT_V3
- ### Core Principles
- ## Certification Flow Diagram
- ## Verification Chain Details
- ### 1. ARIE_HEALTH_PASS
- ### 2. TRUTH_CERTIFICATION_PASS
- ### 3. HXO_FINAL_APPROVAL
- ## Cryptographic Signature Generation
- ### Algorithm: SHA3-256
- ### Signature Payload
- ### Signature Computation
- # Example output:
- # "a7f4e2b9c1d3e5f6a8b0c2d4e6f8a0b2c4d6e8f0a2b4c6d8e0f2a4b6c8d0e2f4"
- ### Entropy Nonce
- ### Temporal Binding
- # "2025-10-12T00:00:00.000000+00:00"
- ## Certification Result Format
- ### Success Case
- ### Failure Case
- ## Genesis Ledger Persistence
- ### Event: `deploy.certified`
- ## Signature Verification
- ### Verify Signature
- # Verify by signature
- ### Get Certification History
- ## Rollback Protocol Integration
- ### Trigger Conditions
- ### Rollback Flow
- ### Rollback Authority
- ## Performance Benchmarks
- ## Security Considerations
- ### Replay Attack Prevention
- ### Signature Tampering
- ### Access Control
- ## Troubleshooting
- ### Certification Fails Despite Passing Simulation
- # Run verify with --json to see detailed checks
- ### Signature Mismatch
- ### Rollback Not Triggered
- # Check config
- ## Future Enhancements
- ## Related Documentation


### ./docs/TOTAL_AUTONOMY_PROTOCOL.md

- # Total Autonomy Protocol
- ## 🚀 v1.9.7m - Complete Self-Maintenance Architecture
- ### Overview
- ### The Four Engines
- #### 🧭 Sanctum (Predictive Simulation)
- #### 🛠️ Forge (Autonomous Repair)
- #### 🧠 ARIE (Integrity Certification)
- #### 🪶 Elysium (Continuous Guardian)
- ### Architecture
- ### Genesis Bus Integration
- ### Workflow
- ### Operational States
- #### 🟢 Healthy
- #### 🟡 Self-Healing
- #### 🟠 Degraded
- #### 🔴 Critical
- ### Example Scenario
- # 1. Sanctum predicts issue
- # 2. Forge repairs automatically
- # 3. ARIE audits changes
- # 4. Truth certifies
- # 5. Elysium confirms stability
- ### Configuration
- # Sanctum
- # Forge
- # ARIE
- # Elysium
- # Genesis Bus
- # Truth Engine
- ### Governance & RBAC
- ### Truth Certification
- # Sanctum certification
- # Forge certification  
- # ARIE certification
- # Full cycle certification
- ### Cascade Support
- # Rollback Forge repair
- # Rollback ARIE fix
- ### Monitoring Dashboard
- # Subscribe to all autonomy events
- ### Sample Output
- ### Post-Merge Activation
- # Boot Elysium Guardian
- ### Testing
- # Test Sanctum
- # Test Forge
- # Test Elysium cycle
- # Run full workflow
- ### Troubleshooting
- ### Version History
- ### Success Criteria
- ### Related Documentation


### ./docs/PIPELINE_AUTOMATION_OVERVIEW.md

- # SR-AIbridge Automated Deployment Pipeline
- ## Overview
- ### Components
- ### Workflow
- ### Benefits
- ## Pre-Deploy Validation
- ### Required Environment Variables
- ### Usage
- ## Auto-Repair Script
- ### Prerequisites
- ### Usage
- ### Default Environment Values
- ## Post-Deploy Verification Checklist
- ## Netlify Configuration
- ### Build Settings
- ### Security Headers
- ### Redirects
- ## Troubleshooting
- ### Build Fails with Missing Environment Variables
- ### Validation Script Fails Locally
- ### Repair Script Cannot Connect to Netlify
- ## Security Notes


### ./docs/TRIAGE_OPERATIONS.md

- # SR-AIbridge Triage Operations Handbook
- ## Overview
- ## System Architecture
- ## Environment Triage
- ### Auto-Repair Mode
- ### Bridge Health Reporting
- ## TOML + Function Sanity Checks
- ### Netlify Configuration (v1.6.4)
- ### Functions Directory Implementation
- ## Secret Scanner Compliance (v1.6.4 Update)
- ### The Paradigm Shift
- ### Why the Change?
- ### The Legitimate Solution
- ### Validation
- ## Drift Auto-Repair Lifecycle
- ### GitHub Actions Workflow
- ### Parity Monitor
- ## Health Telemetry
- ### Diagnostic Events
- ### Endpoint Monitoring
- ## Manual Triage Procedures
- ### Emergency Environment Repair
- # 1. Validate current state
- # 2. Check parity across platforms
- # 3. Run repair (requires NETLIFY_API_KEY and NETLIFY_SITE_ID)
- # 4. Verify sync status
- # 5. Report event manually
- ### Configuration Rollback
- # Revert netlify.toml changes
- ### Clearing Build Cache
- ## Command Reference
- ### Validation Commands
- # Validate netlify.toml syntax
- # Validate environment setup
- # Validate scanner compliance (v1.6.4)
- # Validate Copilot environment
- ### Health Check Commands
- # Backend health
- # Frontend health
- # Full bridge diagnostics
- # Environment sync status
- ### Repair Commands
- # Auto-repair Netlify environment
- # Check cross-platform parity
- # Manual Netlify rollback
- ### CI/CD Commands
- # Trigger workflow manually (via GitHub CLI)
- # View workflow status
- # View workflow logs
- ## Troubleshooting
- ### Build Fails with Secret Scanner Warning (Updated for v1.6.4)
- ### Environment Drift Detected
- ### Functions Directory Warning (Updated for v1.6.4)
- ### Auto-Repair Not Working
- ## Best Practices
- ### Configuration Management
- ### Security
- ### Monitoring
- ## Future Enhancements
- ## Conclusion


### ./docs/API_TRIAGE.md

- # API Triage System
- ## Overview
- ## Architecture
- ### Components
- ## API Checks
- ### 1. Bridge Diagnostics Feed
- ### 2. Agents Registry
- ### 3. System Status
- ## Schema Validation
- ### Example Schema Validation
- # Check definition
- # Valid response
- # Invalid response (would fail)
- # or
- ## Health Status Levels
- ## Usage
- ### Manual Execution
- ### View Triage Report
- ### Automated Execution
- #### Startup Integration
- # In bridge_backend/main.py
- #### GitHub Actions
- # Trigger manually
- # View workflow runs
- ### Frontend Integration
- ## Configuration
- ### Environment Variables
- ### GitHub Secrets
- ## Integration with Diagnostics Timeline
- ## Comparison with Endpoint Triage
- ## Troubleshooting
- ### Triage Not Running on Startup
- ### Workflow Failures
- ### Frontend Panel Not Showing Data
- ### Schema Validation Errors
- ## Security Considerations
- ## Extending the System
- ### Adding New API Checks
- ### Custom Schema Types
- ### Adjusting Health Thresholds
- # Current logic
- ## Future Enhancements
- ## Related Documentation


### ./docs/TRIAGE_MESH_MIGRATION.md

- # Umbra Triage Mesh - Migration Guide
- ## Overview
- ## What Changed
- ### Before (v1.9.6 and earlier)
- ### After (v1.9.7k)
- ## Migration Path
- ### Phase 1: Parallel Operation (Recommended)
- ### Phase 2: Gradual Cutover
- ### Phase 3: Enable Autonomous Healing
- ## Data Migration
- ### Triage Hospital → Umbra
- # Migration script (example)
- ### HealthNet → Umbra
- # In your health probe code
- ## API Changes
- ### Deprecated Endpoints
- ### New Endpoints
- ### Webhook Routes
- ## Configuration Changes
- ### Old Configuration
- # Triage Hospital
- # HealthNet
- # Deploy Triage
- ### New Configuration
- # Unified Umbra
- # Webhook secrets
- ## Code Changes
- ### Emitting Triage Signals
- ## Testing Migration
- ### Verify Signal Ingestion
- # Send test signal
- # Check tickets
- ### Verify Webhook Processing
- # Test Netlify webhook
- # Check if incident was created
- ### Verify Heal Plan Generation
- # Run triage sweep
- # Check for heal plans
- ## Rollback Plan
- ## Common Issues
- ### Issue: Duplicate Tickets
- ### Issue: Webhooks Not Working
- ### Issue: No Heal Plans Generated
- ### Issue: Parity Checks Failing
- ## Timeline Summary
- ## Support
- ## Post-Migration Cleanup


### ./docs/ARIE_V196O_QUICK_REF.md

- # ARIE v1.9.6o Quick Reference
- ## Full Autonomous Run Enablement
- ## 🔄 New Autonomous Behavior
- ### On Deploy Success (`deploy.platform.success`)
- ### Scheduled Runs (Every 12 Hours)
- ## ⚙️ Configuration
- # Enable autonomous scheduling (default: false)
- # Scheduled scan interval in hours (default: 12)
- # Run ARIE on successful deployments (default: true)
- # Require Admiral permission to apply fixes (default: true)
- # Require Truth Engine certification (default: true)
- ## 🧠 Genesis Event Flow
- ## ✅ Safeguards
- ### RBAC Guard
- ### Truth Enforcement
- ### Rollback Shield
- ### Genesis Integration
- ## 📊 Output Reports
- ### `arie_autorun.json`
- ### `arie_certified.json`
- ### `arie_rollback.json`
- ## 🚀 Manual Trigger (Admiral Only)
- # Trigger manual run (requires Admiral handle)
- ## 🔬 Testing
- ### Run Scheduler Tests
- ### Simulate 48-Hour Cycle
- # Set short interval for testing
- # Start scheduler
- # Wait and observe
- # Stop scheduler
- ### Verify No Interference
- ## 📝 Genesis Topics
- ### New Topics (v1.9.6o)
- ### Existing Topics
- ## 🎯 Production Readiness
- ## 🔗 Related Documentation


### ./docs/FORGE_DOMINION_DEPLOYMENT_GUIDE.md

- # 🜂 Forge Dominion — Environment Sovereignty Deployment Guide (v1.9.7s)
- ## ⚙️ Objective
- ## 🧩 Architecture: Dominion Token Engine
- ## 🧬 Flow Summary
- ## 🧠 Setup (First-Time Configuration)
- ### 🜂 GitHub Variables
- ## 🚀 Deployment Sequence
- ### 1️⃣ Bootstrap
- ### 2️⃣ Pre-Deploy
- ### 3️⃣ Validate & Scrub
- ### 4️⃣ CI Verification
- ## 🔒 Security Guarantees
- ## 🧾 Test Plan
- ## 🖼 Visual Pulse Integration
- ## 🛡 Governance Addendum (v1.9.7s+)
- ## 🧾 Changelog
- ## 🕊 Lore Summary
- ## ✅ Seal of Dominion: Environment Sovereignty Achieved
- ## 📚 File Structure
- ## 🔧 Troubleshooting
- ### Issue: Bootstrap fails with "No FORGE_DOMINION_ROOT"
- ### Issue: scan_envs.py finds secrets
- ### Issue: Token validation fails
- ## 🎯 Next Steps


### ./docs/GITHUB_ENVHOOK.md

- # GitHub Environment Hook - Autonomous Sync Trigger
- ## 📋 Overview
- ### Purpose
- ### How It Works
- ## 🚀 Usage
- ### Watch Mode (Continuous Monitoring)
- ### Manual Trigger Mode
- ### Help
- ## 📡 Genesis Event Topics
- ### envmirror.sync.start
- ### envduo.audit
- ## 🔍 Implementation Details
- ### File Monitoring
- ### State Persistence
- ### Audit Logging
- ## 🧪 Testing
- ### Run Tests
- ### Test Coverage
- ### Manual Testing
- ## 🔗 Integration Points
- ### EnvMirror Engine
- ### EnvDuo Subsystem
- ### Truth Engine
- ### Steward Dashboard
- ## 📂 Files
- ### Created/Modified
- ## 🔒 Security & RBAC
- ### Access Control
- ### Security Features
- ## 🛠️ Configuration
- ### Environment Variables
- ### Customization
- ## 🔧 Troubleshooting
- ### Watcher Not Detecting Changes
- ### Genesis Events Not Publishing
- ### State File Corruption
- ## 🚦 Operational Use
- ### Deployment Workflow
- ### Monitoring
- ## 📊 Metrics & Analytics
- ## 🎯 Result
- ## 📚 Related Documentation


### ./docs/AUTONOMY_INTEGRATION.md

- # Autonomy Engine Integration Guide
- ## Overview
- ## Architecture
- ### Event Flow
- ### Integration Coverage
- ## Integration Points
- #### 1. Triage Integration
- #### 2. Federation Integration
- #### 3. Parity Integration
- #### 4. Six Super Engines Integration
- #### 5. Specialized Engines Integration
- #### 6. Core Systems Integration
- #### 7. Tools & Runtime Integration
- #### 8. Heritage & MAS Integration
- ## Configuration
- ### Environment Variables
- ### Feature Flags
- ## Usage Examples
- ### Triage Auto-Healing
- # Run API triage (publishes to triage.api)
- # Autonomy engine receives event and initiates healing
- # Check autonomy logs: grep "autonomy.triage_response" logs/
- ### Federation Coordination
- # Autonomy engine receives and coordinates
- ### Parity Auto-Fix
- # Run parity check (publishes to parity.check)
- # Run auto-fix (publishes to parity.autofix)
- # Autonomy engine receives events and coordinates fixes
- ### Super Engines Analysis
- # Initialize engine
- # Perform analysis (can publish to scrolltongue.analysis)
- # Autonomy monitors the analysis
- # Check with: grep "autonomy.scrolltongue_analysis" logs/
- ### Health Monitoring with Auto-Healing
- # Healthy status - publishes to genesis.fact
- # Degraded status - triggers autonomy healing
- ### Firewall Threat Response
- # Low threat - analysis only
- # High threat - triggers autonomy healing
- ### MAS Agent Coordination
- # Normal coordination - publishes to genesis.intent
- # Agent failure - triggers autonomy healing
- ### Guardians Safety Validation
- # Safe action - passes validation
- # Dangerous action - blocked by guardians
- # Results in autonomy.action_blocked event
- ### Doctrine Compliance
- # Compliance check - publishes to genesis.fact
- # Violation - triggers autonomy healing
- ### Network Diagnostics
- # Normal diagnostics - publishes to genesis.fact
- # Network error - triggers autonomy healing
- ### Runtime Deploy Events
- # Successful deploy - publishes to genesis.intent
- # Deploy failure - triggers autonomy healing
- ## Testing
- ### Unit Tests
- ### Integration Validation
- # Original topics
- # Super Engines topics
- # Core Systems topics
- # Tools/Runtime topics
- # Heritage/MAS topics
- ### Event Flow Testing
- ## Monitoring
- ### Event Tracing
- ### Logs
- ## Troubleshooting
- ### Genesis Bus Disabled
- # Check Genesis mode
- # Enable if needed
- ### Missing Topics
- # Check strict policy
- # Disable strict mode for debugging
- ### Event Publishing Errors
- ## Version History
- ## Related Documentation


### ./docs/ENVSYNC_ENGINE.md

- # EnvSync Engine - Render & Netlify Auto-Sync
- ## Overview
- ## Features
- ## Architecture
- ### Genesis Bus Integration
- ### Autonomy Engine Integration
- ## Configuration
- ### Environment Variables
- # === ENVSYNC CORE ===
- # === TOKEN DISCOVERY ===
- # === RENDER SELECTORS ===
- # Legacy RENDER_SERVICE_ID removed=srv-xxxxx
- # === NETLIFY SELECTORS ===
- # === SYNC SHAPING ===
- ## Token Discovery
- ### 1. Environment Variables
- ### 2. Secret Files
- ### 3. Vault API
- ### 4. Dashboard Endpoints
- ## API Endpoints
- ### Health Check
- ### Dry-Run (Preview Changes)
- ### Apply Sync
- ## Usage Examples
- ### Manual Dry-Run
- ### Apply Sync to All Providers
- ## Include/Exclude Filtering
- ## Scheduled Sync
- ## GitHub Actions Integration
- # .github/workflows/envsync.yml
- ## Troubleshooting
- ### Token Not Found
- ### Empty Diff
- ### Provider Errors
- ## Dashboard Token Endpoint (Optional)
- # Your admin dashboard route
- ## Security Notes
- ## Operational Best Practices
- ## Version History


### ./docs/BUILD_DOSSIER.md

- # SR-AIbridge Build Dossier
- ## Step-by-Step Rebuild Guide from Scratch
- ## 📋 Prerequisites Checklist
- ## 🎯 Phase 1: Environment Setup (5 minutes)
- ### Step 1.1: Create Project Directory
- # Create and navigate to project directory
- # Initialize git repository
- ### Step 1.2: Create Directory Structure
- # Create main directories
- ### Step 1.3: Create Environment Files
- # Database Configuration
- # Server Configuration
- # Security
- # Features
- # Logging
- ## 🐍 Phase 2: Backend Foundation (15 minutes)
- ### Step 2.1: Install Python Dependencies
- ### Step 2.2: Create Database Models
- ### Step 2.3: Create Database Connection
- ### Step 2.4: Create Pydantic Schemas
- # Guardian Schemas
- # Agent Schemas
- # Mission Schemas
- # Health Response
- ### Step 2.5: Create Main Application
- # Create FastAPI app
- # CORS Middleware
- # Startup event
- # Health Endpoints
- # Agent Endpoints
- # Mission Endpoints
- # Guardian Endpoints
- # Root endpoint
- ### Step 2.6: Test Backend
- # Start the backend
- # In another terminal, test the API
- ## ⚛️ Phase 3: Frontend Foundation (15 minutes)
- ### Step 3.1: Initialize React Project
- ### Step 3.2: Install Additional Dependencies
- ### Step 3.3: Create API Client
- ### Step 3.4: Create Main Dashboard Component
- ### Step 3.5: Create App Component
- ### Step 3.6: Add Basic Styling
- ### Step 3.7: Test Frontend
- # Start the frontend
- # Open browser to http://localhost:5173
- ## 🔧 Phase 4: Add Core Features (30 minutes)
- ### Step 4.1: Add WebSocket Support (Backend)
- ### Step 4.2: Add WebSocket Support (Frontend)
- ### Step 4.3: Add Agent Creation Form
- ## 🚀 Phase 5: Deployment Setup (20 minutes)
- ### Step 5.1: Create Netlify Configuration
- ### Step 5.2: Create Render Configuration
- ### Step 5.3: Create GitHub Actions Workflow
- ## ✅ Phase 6: Verification & Testing (10 minutes)
- ### Step 6.1: Backend Tests
- # Test all endpoints
- # Create test agent
- # Create test mission
- ### Step 6.2: Frontend Tests
- ### Step 6.3: System Integration Test
- # Run both backend and frontend simultaneously
- # Terminal 1:
- # Terminal 2:
- # Verify:
- # - Frontend connects to backend
- # - Health status displays
- # - WebSocket updates work
- # - Data flows correctly
- ## 📊 Verification Checklist
- ## 🎓 Next Steps
- ## 🚨 Troubleshooting
- ### Backend won't start
- ### Frontend won't build
- ### CORS errors
- ### Database errors
- ## 📖 Reference


### ./docs/UMBRA_LATTICE_QUICK_START.md

- # Umbra Lattice Memory - Quick Reference
- ## Overview
- ## Key Concepts
- ### Graph Structure
- ### Truth Gating
- ## REST API
- ### Get Summary
- ### Get Mermaid Graph
- ### Export Snapshot
- ### Run Bloom Analysis
- ### Get Statistics
- ## CLI Commands
- ### View Report
- # Mermaid graph (default)
- # Summary only
- # Both
- ### Export Snapshot
- ### Run Bloom Analysis
- ### View Statistics
- ## Environment Variables
- # Enable/disable Umbra Lattice (default: true)
- # Strict truth certification (default: true)
- # Snapshot interval (default: 10m)
- ## Genesis Integration
- ## Storage
- ## RBAC
- ## Example Mermaid Output
- ## Neural Changelog Queries
- ## Integration Examples
- ### Record Custom Event
- ### Query Recent Nodes
- ### Generate Visualization
- ## Troubleshooting
- ## Related Documentation


### ./docs/DEPLOYMENT_AUTOMATION.md

- # SR-AIbridge Deployment Automation
- ## Overview
- ## Netlify Environment Structure
- ### Build Configuration
- ### Key Features
- ## Deploy Path Triage Engine
- ### Overview
- ### Lifecycle
- ### Status Types
- ### Generated Artifacts
- ## Badge Synchronization Logic
- ### Integration Points
- ### Badge States
- ## CI/CD Integration
- ### Workflow: Deploy Path Verification
- ### Workflow Benefits
- ## Self-Healing Deployment
- ### Auto-Repair Flow
- ### Failure Handling
- ## Usage
- ### Manual Triage Run
- ### CI/CD Trigger
- # Via GitHub CLI
- # Check status
- ### View Diagnostic Report
- ## Lore Entry V: The Self-Repairing Song of the Bridge
- ## Version History
- ## Related Documentation


### ./docs/ELYSIUM_GUARDIAN.md

- # Elysium Guardian
- ## 🪶 Elysium - Continuous Passive Guardian System
- ### Purpose
- ### Architecture
- ### Features
- #### 1. Scheduled Cycles
- #### 2. Full Autonomy Pipeline
- #### 3. Continuous Monitoring
- #### 4. Genesis Integration
- ### Usage
- #### Automatic (Post-Merge)
- #### Programmatic
- # Start continuous monitoring
- # Or run async
- # Manual cycle trigger
- #### CLI
- #### GitHub Actions
- ### Configuration
- # Enable/disable Elysium
- # Cycle interval (hours)
- # Run immediately on start
- # Genesis bus integration
- ### Cycle Flow
- ### Cycle Results
- ### Example Output
- ### Monitoring
- ### Integration with Other Systems
- #### Cascade Orchestration
- #### Governance
- #### Truth Engine
- ### Scheduling Strategy
- # Every 3 hours (aggressive)
- # Every 12 hours (conservative)
- # Daily
- ### Safety Features
- ### Troubleshooting
- ### Best Practices
- ### Post-Merge Activation
- # SSH into server or run in deployment
- # Or add to startup script
- # This boots Elysium Guardian instantly
- ### Related


### ./docs/BRH_GUIDE.md

- # 🧠 Bridge Runtime Handler (BRH) Guide
- ## 🌟 Overview
- ### Key Principles
- ## 🏗️ Architecture
- ## 🚀 Quick Start
- ### Prerequisites
- ### Step 1: Configure Runtime Manifest
- ### Step 2: Initialize Runtime Locally
- # Set Forge root key
- # Run runtime handler
- ### Step 3: Deploy via GitHub Actions
- ## 📋 Configuration Reference
- ### Runtime Manifest Schema
- #### `runtime.auth`
- #### `runtime.containers`
- #### `runtime.federation`
- #### `security.attestation`
- ## 🔐 Security
- ### Token Lifecycle
- ### Forge Dominion Integration
- ### Attestation
- ## 🌐 Federation
- ### μ-Harmonic Lattice Integration
- # Register node in lattice
- ### Multi-Node Deployment
- ## 📊 Monitoring
- ### Health Endpoint
- ### Logs
- ### Active Nodes Registry
- ## 🔧 Troubleshooting
- ### Token Validation Failures
- ### Container Won't Start
- ### Federation Sync Issues
- ## 🛣️ Roadmap
- ### ✅ Phase 1: Core Runtime (Current)
- ### 🚧 Phase 2: GitHub Integration (Next)
- ### 📅 Phase 3: Federation Linking
- ### 🔮 Phase 4: UI Integration
- ## 📚 Additional Resources
- ## 🤝 Contributing
- ## 📄 License


### ./docs/GITHUB_ENVHOOK_INTEGRATION.md

- # GitHub Environment Hook - Integration Guide
- ## 🎯 Quick Start
- ### 1. Verify Installation
- ### 2. Test Manual Trigger
- ### 3. Start Watching (Development)
- ## 🔄 Integration Patterns
- ### Pattern 1: GitHub Actions Workflow
- ### Pattern 2: Background Service (Production)
- ### Pattern 3: Docker Container
- # Install dependencies
- # Copy application
- # Create logs directory
- # Set environment
- # Run watcher
- ## 🔌 Subscribing to Events
- ### Example: EnvMirror Engine Subscriber
- # bridge_backend/engines/envmirror/core.py
- ### Example: EnvDuo Audit Subscriber
- # bridge_backend/engines/envduo/core.py
- ### Example: Truth Engine Audit Logger
- # bridge_backend/engines/truth/ledger.py
- ## 📊 Monitoring & Observability
- ### View Event History
- ### View Trigger Logs
- ### View State
- ## 🧪 Testing Integration
- ### Test 1: Modify environment.json
- # Start watcher in background
- # Wait for initialization
- # Modify environment.json
- # Wait for detection
- # Check logs
- # Cleanup
- ### Test 2: Subscribe to Events (Python)
- ### Test 3: Load Testing
- # Verify all triggers logged
- ## 🔧 Troubleshooting
- ### Debug Mode
- ### Check Genesis Bus Status
- ### Verify Topic Registration
- ## 🎨 Example: Complete Workflow
- ## 📚 Best Practices
- ## 🔗 Next Steps


### ./docs/ANCHORHOLD_PROTOCOL.md

- # SR-AIbridge v1.9.4 — Anchorhold Protocol
- ## Overview
- ## Core Improvements
- ### 1️⃣ Dynamic Port Binding (Render Timeout Fix)
- ### 2️⃣ Automatic Table Creation & Schema Sync
- ### 3️⃣ Heartbeat Ping System
- # bridge_backend/runtime/heartbeat.py
- ### 4️⃣ Netlify ↔ Render Header Alignment
- # Environment constants
- # FastAPI Middleware
- ### 5️⃣ Extended Runtime Guard
- # SR-AIbridge v1.9.4 — Anchorhold Protocol
- # Auto-Repair + Schema Sync + Heartbeat Init
- ## Infrastructure Updates
- ### render.yaml
- ### netlify.toml
- # API proxy to Render backend
- # SPA fallback for client routing
- ## Outcome Metrics
- ## Technical Details
- ### Dependencies Added
- ### Files Modified
- ### Version Information
- ## Testing & Validation
- ### Automated Tests
- ### Live Testing
- ### API Responses
- ## Deployment Guide
- ### Render Deployment
- ### Netlify Deployment
- ### Environment Variables
- ## Migration Notes
- ### Breaking Changes
- ### Upgrade Path
- ### Rollback Plan
- ## Future Enhancements
- ## Support & Troubleshooting
- ### Common Issues
- ### Debug Commands
- # Test dynamic port
- # Test heartbeat module
- # Test CORS
- # View runtime logs
- ## Acknowledgments


### ./docs/AUTONOMY_DEPLOYMENT_INTEGRATION.md

- # Autonomy Engine Deployment Integration
- ## Overview
- ## Architecture
- ### Event Flow
- ## Integration Points
- ### 1. GitHub Actions Integration
- ### 2. Webhook Endpoints
- ### 3. Autonomy Engine API
- ## Genesis Bus Topics
- ### Platform-Specific Topics
- ### Generic Deployment Topics
- ### Autonomy Response Topics
- ## Event Payload Structure
- ## Configuration
- ### Environment Variables
- ### GitHub Actions Secrets
- ## Setup Instructions
- ### 1. Configure Netlify Webhooks
- ### 2. Configure Render Webhooks
- ### 3. Configure GitHub Webhooks
- ## Usage Examples
- ### Manual Event Publishing (CLI)
- # Publish deployment start event
- # Publish deployment success
- # Publish deployment failure
- ### Programmatic Event Publishing (Python)
- # Publish deployment event
- ### API Event Publishing (cURL)
- # Via autonomy engine API
- ## Monitoring
- ### Check Webhook Status
- ### Check Autonomy Deployment Status
- ### Genesis Bus Introspection
- ## Benefits
- ### 1. Real-Time Deployment Tracking
- ### 2. Automated Failure Response
- ### 3. Distributed Coordination
- ### 4. Deployment Analytics
- ### 5. Integration with Existing Systems
- ## Troubleshooting
- ### Events Not Publishing
- ### Webhook Authentication Failures
- ### Missing Deployment Events
- ## Files Changed
- ### Created (3 files)
- ### Modified (4 files)
- ## Next Steps
- ### Optional Enhancements
- ## Conclusion


### ./docs/RUNTIME_TROUBLESHOOTING.md

- # Runtime Troubleshooting Guide
- ## Quick Diagnostics
- ### Check Runtime Health
- # Run the federation runtime guard locally
- # Run full triage
- ### Collect Render Diagnostics
- # Set your Render credentials
- # Collect diagnostics
- ## Common Issues
- ### 1. Health Check Failing
- ### 2. Database Connection Issues
- ### 3. Egress/Network Issues
- ### 4. Version Mismatch
- ## Runtime Scripts
- ### start.sh
- ### wait_for_db.py
- ### run_migrations.py
- ### egress_canary.py
- ### health_probe.py
- ## Manual Triage
- ### Run Full Diagnostics
- # From GitHub Actions
- # Or manually
- ### Check Specific Endpoints
- ## Environment Variables
- ## Workflow Integration
- ### Federation Runtime Guard
- ### Render Env Guard
- ## Debugging Tips
- ## Getting Help
- ## Related Documentation


### ./docs/TROUBLESHOOTING_LINKS.md

- # Troubleshooting: HXO Genesis Links
- ## Common Issues
- ### "NoneType can't be used in 'await' expression"
- ### "Invalid Genesis topic: deploy.tde.orchestrator.completed"
- ### Import Error: "cannot import name 'notify_autonomy_autotune_signal'"
- ### Registration Fails on Render Startup
- ## Health Checks
- ### Verify HXO Genesis Link is Active
- ### Verify HXO Autonomy Link is Active
- ## Debug Mode
- ## Getting Help


### ./docs/BLUEPRINT_ENGINE_GUIDE.md

- # Blueprint Engine + Mission Log v2 - Usage Guide
- ## Overview
- ## Architecture
- ### Backend Components
- ### Frontend Components
- ## Quick Start
- ### Backend Setup
- # Health check
- # List blueprints (empty initially)
- ### Frontend Setup
- ## API Usage
- ### 1. Draft a Blueprint
- ### 2. Commit Blueprint to Mission
- ### 3. Get Mission Jobs
- ### 4. Delete Blueprint (Admiral Only)
- ## Frontend Usage
- ### Using BlueprintWizard
- ### Using MissionLogV2
- ## PostgreSQL Partitioning
- ### Initial Setup
- ### Monthly Maintenance
- ## RBAC Permissions
- ## Customization
- ### Extending Planner Rules
- ### Plugging in an LLM
- ## Testing
- ### Run Backend Tests
- ### Manual Testing
- ## Troubleshooting
- ### Backend Issues
- ### Frontend Issues
- ### Database Issues
- ## Production Deployment
- ### Environment Variables
- ### Render Deployment
- ## Support


### ./docs/PHOENIX_COMPARISON.md

- # Phoenix vs Current Implementation - Comparison Report
- ## 🔥 Phoenix Protocol Progress
- ### ✅ Implemented Features
- ### 📊 API Endpoint Comparison
- ### 🎯 Testing Results
- ### 📁 Directory Structure Comparison
- ### 🔍 Key Differences Identified
- ### 📝 Documentation Accuracy
- ### 🚀 Next Steps for Phoenix
- ### 💡 Recommendations
- ### 📊 Metrics Summary
- ### 🎯 Conclusion


### ./docs/GITHUB_ENVHOOK_QUICK_REF.md

- # GitHub Environment Hook - Quick Reference
- ## 🚀 Commands
- # Watch for changes (continuous monitoring)
- # Manual trigger (one-time sync)
- # Help
- ## 📡 Genesis Events Published
- ## 📂 Files
- ## 🔍 Monitoring
- # View trigger logs
- # View current state
- # Check Genesis events
- ## 🧪 Testing
- # Run tests
- # Test manual trigger
- # Simulate file change
- ## 🔌 Integration
- ### Subscribe to Events (Python)
- ### GitHub Actions Workflow
- ## 🎯 Use Cases
- ## 🔒 Security
- ## 📚 Documentation
- ## 🛠️ Environment Variables
- ## 🎯 Result


### ./docs/HYDRA_GUARD_V2.md

- # Hydra Guard v2
- ## Overview
- ## Features
- ### 1. Security Headers Synthesis
- ### 2. Redirect Rules
- ### 3. Configuration Files
- ## Usage
- ### Python
- ### API
- ## Idempotence
- ## Integration with Chimera
- ## File Structure


### ./docs/V197M_QUICK_REF.md

- # Total Autonomy Protocol - Quick Reference
- ## v1.9.7m Quick Start
- ### 🚀 What Is It?
- ### ⚡ Quick Commands
- # Test Sanctum (predictive simulation)
- # Test Forge (auto-repair)
- # Run Elysium Guardian (full cycle)
- # Scan only (no fixes)
- ### 🔧 Configuration
- # Enable all engines
- # Elysium monitoring
- # Genesis integration
- ### 🌊 The Autonomy Cycle
- ### 📡 Genesis Events
- # Success/failure predictions
- # Auto-repair events
- # Full cycle completion
- ### 🎯 Post-Merge Activation
- # Boot Elysium Guardian
- ### 🔍 Monitoring
- ### 🛡️ Safety Features
- ### 📚 Documentation
- ### ⚠️ Troubleshooting
- # Run repair in scan-only mode
- ### ✅ Success Criteria
- ### 🎯 Version


### ./docs/BRH_CONSENSUS_ARCHITECTURE.md

- # BRH Consensus System Architecture
- ## System Overview
- ## Component Interactions
- ### 1. Heartbeat Flow (Every 60s)
- ### 2. Consensus Election Flow (Every 180s)
- ### 3. Leader Polling Flow (Every 10s)
- ### 4. Deploy Hook Flow
- ## State Transitions
- ### Node Role States
- ### Container Ownership Transfer
- ## Data Structures
- ### role.py State
- ### consensus.py Peers
- ### Container Labels
- ## Failure Scenarios
- ### Scenario 1: Leader Node Fails
- ### Scenario 2: Network Partition
- ### Scenario 3: Split Brain Prevention
- ## Security Model
- ### Signature Generation
- ### Validation Flow
- ## Performance Characteristics
- ## Extension Points
- ### 1. Custom Election Algorithm
- # consensus.py - modify elect_leader()
- ### 2. Lease Token System
- ### 3. Drain-and-Stop Policy
- # consensus.py - modify apply_leader_change()
- ## Monitoring & Observability
- ### Key Metrics
- # Prometheus-style metrics (future enhancement)
- ### Health Checks
- # Check if consensus is running
- # Verify leader identity
- # List container ownership
- ## Deployment Topology
- ### Development (Single Node)
- ### Production (Multi-Node)
- ### High Availability (Geographic)


### ./docs/HOOKS_TRIAGE.md

- # Hooks Triage System - Operation Reflex
- ## Overview
- ## Architecture
- ### Components
- ## Health Status Levels
- ## Configuration
- ### Hooks Configuration File
- #### Configuration Fields
- #### Magic Markers
- ### Environment Variables
- ### GitHub Secrets (Required for Workflows)
- ## Usage
- ### Manual Execution
- ### View Triage Report
- ### Automated Execution
- ### Frontend Integration
- ## Integration with Diagnostics Timeline
- ## HMAC Signature Authentication
- ### How It Works
- ### Example: Verifying Signatures in Python
- ## Retry Logic
- ## Troubleshooting
- ### Triage Not Running on Startup
- ### Workflow Failures
- ### Frontend Panel Not Showing Data
- ### Hook Always Failing
- ## Security Considerations
- ### HMAC Signing
- ### Control Endpoint
- ### Configuration Security
- ## Future Enhancements
- ## Event Flow
- ## Files Created/Modified
- ### Created Files
- ### Modified Files


### ./docs/TOTAL_STACK_TRIAGE.md

- # Total-Stack Triage Mesh
- ## Overview
- ## Signals
- ## Workflows
- ### 1. Build Triage (Netlify)
- ### 2. Runtime Triage (Render)
- ### 3. Deploy Gate
- ### 4. Endpoints & Hooks Sweep
- ### 5. Environment Parity Guard
- ## Escalation
- ## Reports
- ## Safe Auto-Repair
- ## Running Locally
- # Runtime triage
- # Endpoint sweep
- # Environment parity
- # Unified report
- ## Post-Merge Checklist
- ## Integration
- # Existing workflows upload their artifacts
- # Deploy Gate downloads and evaluates all artifacts
- ## Troubleshooting
- ### Deploy Gate Fails
- ### Schema Mismatch
- ### Missing Endpoints
- ## Architecture
- ## Version History


### ./docs/SECURITY_PATCH_SUMMARY.md

- # Security Patch Summary: Token Metadata Validation
- ## 🎯 Mission Accomplished
- ## 📊 Implementation Statistics
- ### Code Changes
- ### Test Coverage
- ### Security Scans
- ## 🛡️ Security Improvements
- ### Before Patch
- ### After Patch
- ## 🔑 Key Features Implemented
- ### 1. Required Metadata Fields
- ### 2. Validation Rules
- ### 3. Enforcement Modes
- ### 4. Security Hardening
- ## 📈 Migration Path
- ### Phase 1: Development ✅ COMPLETE
- ### Phase 2: Integration (Next Steps)
- ### Phase 3: Production Rollout (Future)
- ## 🧪 Testing & Validation
- ### Unit Tests
- # Result: 33/33 PASSED
- ### Integration Tests
- # Result: 26/26 PASSED
- ### Demonstration
- # Shows all 4 scenarios working correctly
- ### Security Scan
- # Result: 0 alerts - Clean
- ## 📚 Documentation
- ### User Documentation
- ### Developer Documentation
- ### API Reference
- ## 🔍 Code Quality
- ### Code Review Feedback
- ### Best Practices Followed
- ## 🚀 Deployment Instructions
- ### For Development
- # Metadata is optional (backward compatible)
- ### For Production (Recommended)
- # Enable strict validation
- # Metadata is required
- ## 📞 Support & Troubleshooting
- ### Common Issues
- ### Getting Help
- ## ✅ Success Criteria - All Met
- ## 🎖️ Impact
- ### Security Posture
- ### Compliance
- ### Auditability
- ### Developer Experience
- ## 🏆 Conclusion


### ./docs/WORKFLOW_OPTIMIZATION.md

- # GitHub Actions Workflow Optimization Guide
- ## Overview
- ## Problem Statement
- ## Optimization Strategies Implemented
- ### 1. Dependency Caching ✅
- ### 2. Artifact Retention Reduction ✅
- ### 3. Workflow Consolidation ✅
- ### 4. Native Bridge Runner Support ✅
- ### 5. Render.com Integration ✅
- ### 6. Workflow Efficiency Analysis Tools ✅
- # Audit workflows
- # Auto-optimize (dry run)
- # Auto-optimize (apply changes)
- ## Implementation Checklist
- ## Monitoring and Maintenance
- ### Monitor GitHub Actions Usage
- ### Run Regular Audits
- ### Verify Render.com Services
- ## Expected Results
- ### Workflow Runtime Comparison
- ### Cost Projection
- ### Cost Savings
- ## Next Steps
- ### Immediate Actions
- ### Optional Advanced Optimizations
- ### Future Improvements
- ## Troubleshooting
- ### Cache Not Working
- # Verify cache keys are unique per dependency hash
- # Check cache hit in workflow logs
- ### Render Services Not Triggering
- ### Self-Hosted Runner Issues
- ## Technical Details
- ### What We CANNOT Do (GitHub Limits)
- ### What We CAN Do (Legitimate Optimizations)
- ## Conclusion
- ## Support


### ./docs/GENESIS_V2_0_1_QUICK_REF.md

- # Genesis v2.0.1 Quick Reference
- ## Installation
- # Environment variables
- ## Emit Events
- # Intent
- # Heal
- # Fact
- # Convenience
- ## Subscribe to Events
- ## Check Safety
- ## Replay Events
- # From watermark
- # From timestamp
- # With topic filter
- ## TDE-X v2 Status
- ## Topic Patterns
- ## Event Kinds
- ## Configuration
- # Genesis
- # Guardians
- # TDE-X v2
- # Port
- ## Run Tests
- ## Troubleshooting
- ## API Endpoints
- ## Render Deploy


### ./docs/COMPLIANCE_INTEGRATION_GUIDE.md

- # Compliance Integration Guide
- ## Table of Contents
- ## Overview
- ## Architecture
- ### Data Flow
- ### Components
- ## API Reference
- ### POST /engines/autonomy/task
- ### GET /engines/autonomy/task/{task_id}/compliance
- ### POST /engines/autonomy/task/{task_id}/loc
- ## Usage Examples
- ### Basic Task Creation
- # Check if task is safe to proceed
- ### Scan Specific Files
- ### Disable Compliance (if needed)
- ### Retrieve Compliance Later
- # Get compliance validation for a task
- ### Update LOC Metrics
- # Refresh LOC metrics for a task
- ## Compliance States
- ### OK ✅
- ### Flagged ⚠️
- ### Blocked 🚫
- ### Error ❌
- ## Configuration
- ### Policy File: `scan_policy.yaml`
- ### Environment Variables
- ## Testing
- ### Run Tests
- # Run all autonomy engine tests
- ### Test Coverage
- ## Troubleshooting
- ### Issue: Compliance check returns "error" state
- ### Issue: High false-positive rate in counterfeit detection
- ### Issue: Task creation is slow
- ### Issue: LOC metrics show 0 lines
- ## License


### ./docs/PR_HEALTH_SUMMARY.md

- # PR Health Summary Format
- ## Overview
- ## Example Output
- ### Excellent Health (95-100%)
- ### 🤖 Bridge Health: 100%
- ### Good Health (80-94%)
- ### 🤖 Bridge Health: 87%
- ### Fair Health (60-79%)
- ### 🤖 Bridge Health: 72%
- ### Poor Health (<60%)
- ### 🤖 Bridge Health: 45%
- ## Health Score Calculation
- ### 1. Self-Test Pass Rate (50% weight)
- ### 2. Umbra Issue Penalties (30% weight)
- ### 3. Heal Success Rate (20% weight)
- ## Health Indicators
- ## Components Breakdown
- ### Self-Test Results
- ### Umbra Triage
- # OR
- ### Truth Certification
- ### Rollbacks
- ### Artifacts
- ## JSON Summary Format
- ## Interpreting Results
- ### When to Merge
- ### Common Scenarios
- #### Scenario: New Feature PR
- #### Scenario: Dependency Update
- #### Scenario: Configuration Change
- #### Scenario: Autonomous Healing Success
- ## Viewing Detailed Reports
- ## Customization
- ## Troubleshooting
- ### Summary Not Generated
- ### Wrong Health Score
- ### Missing PR Comment
- ## Best Practices


### ./docs/ENV_OVERVIEW.md

- # Environment Overview
- ## Summary
- ## Variables
- ### Legend
- ## Webhooks


### ./docs/ARIE_SANCTUM_LOOP.md

- # ARIE + Sanctum Integration Loop
- ## 🔄 The Predict → Repair → Certify Loop
- ### Overview
- ### Responsibilities
- #### Sanctum: Configuration Layer
- #### Forge: Repair Layer
- #### ARIE: Code Quality Layer
- #### Truth: Certification Layer
- ### Integration Flow
- #### 1. Pre-Deploy (Sanctum)
- # Sanctum runs simulation
- #### 2. Auto-Repair (Forge)
- # Forge scans and repairs
- # Certify repairs
- # Publish to Genesis
- #### 3. Code Audit (ARIE)
- # ARIE runs integrity scan
- # Truth certification happens internally
- # Results published to Genesis
- #### 4. Continuous Monitor (Elysium)
- # Elysium runs full cycle
- # Includes all of: Sanctum → Forge → ARIE → Truth
- ### Event Chain
- ### Use Cases
- #### Case 1: Missing Configuration File
- #### Case 2: Deprecated Code
- #### Case 3: Environment Drift
- ### Policy Hierarchy
- ### Genesis Bus Topics
- # Sanctum topics
- # Forge topics
- # ARIE topics (existing)
- # Elysium topics
- ### Truth Certification
- # Sanctum certification
- # Forge certification
- # ARIE certification
- # Full cycle certification
- ### Monitoring
- # Monitor Sanctum
- # Monitor Forge
- # Monitor ARIE
- # Monitor full cycle
- ### Best Practices
- ### Troubleshooting
- ### Related


### ./docs/BADGES.md

- # Status Badges
- ## Health Status
- ### Rendered:
- ## Workflow Status
- ## Component Status
- ### Rendered:
- ## Security & Compliance
- ### Rendered:
- ## Status Colors
- ## Custom Badge Examples
- ### Build Status with Size
- ### Runtime with Response Time
- ### Environment with Version
- ## Dynamic Badges
- ## Badge Templates
- ### Success Template
- ### Info Template
- ### Warning Template
- ### Error Template
- ## Shield.io Documentation
- ## Suggested README Section
- ## 🏥 System Health


### ./docs/GENESIS_V2_GUIDE.md

- # v2.0.0 — Project Genesis: Universal Engine Integration
- ## Overview
- ## Core Architecture
- ### The Genesis Framework Components
- ## Genesis Organism Roles
- ## Genesis Event Topics
- ### 1. `genesis.intent`
- ### 2. `genesis.fact`
- ### 3. `genesis.heal`
- ### 4. `genesis.create`
- ### 5. `genesis.echo`
- ## Environment Variables
- ### Trace Levels
- ## API Endpoints
- ### `GET /api/genesis/pulse`
- ### `GET /api/genesis/manifest`
- ### `GET /api/genesis/manifest/{engine_name}`
- ### `GET /api/genesis/health`
- ### `GET /api/genesis/echo`
- ### `GET /api/genesis/map`
- ### `GET /api/genesis/events?limit=100`
- ### `GET /api/genesis/stats`
- ## Signal Flow
- ## Initialization Sequence
- ## Usage Examples
- ### Publishing Events
- # Publish an intent event
- # Publish a fact
- ### Subscribing to Events
- # Subscribe to intent events
- ### Registering Engines
- # Register a custom engine
- ### Health Monitoring
- # Update health status
- # Get overall health
- ## Backward Compatibility
- ## Migration from v1.9.7c
- ### For Users
- ### For Developers
- ## Testing
- ## Deployment
- ### Render
- ### Netlify
- ## Troubleshooting
- ### Genesis Not Starting
- ### Missing Engine Links
- ### Event Not Publishing
- ## Future Enhancements
- ## Summary
- ## Related Documentation


### ./docs/DEPLOYMENT_SECURITY_FIX.md

- # Deployment Security Fix - Netlify + Render Synchronization
- ## Overview
- ## Problem Statement
- ## Solution
- ### 1. Environment Configuration
- #### Frontend Configuration (`.env.netlify`)
- # Bridge Frontend Configuration
- # Optional Monitoring
- #### Backend Configuration (`.env.example`)
- # Core Database Connection
- # Bridge Services
- # Optional Monitoring
- ### 2. Backend Configuration Enhancements
- #### `bridge_backend/config.py`
- #### `bridge_backend/__init__.py`
- ### 3. Netlify Configuration (`netlify.toml`)
- ### 4. Safe Handling of Environment Variables
- #### What Gets Scanned?
- #### How We Prevent False Positives
- #### Variables Safe for Frontend
- ### 5. Backend Connection Verification
- #### Startup Sequence
- #### Testing Connection
- # Check database connectivity
- ### 6. Deployment Workflow
- #### Initial Setup
- #### Re-deployment
- # Render auto-deploys on push
- # Check logs for "✅ Database connection verified."
- # Netlify auto-deploys on push
- # Check build logs for successful completion
- #### Rollback Procedure
- ### 7. Monitoring and Verification
- #### Backend Health Check
- #### Frontend Health Check
- #### Log Inspection
- # Look for connection verification
- # Look for successful build
- ### 8. Security Best Practices
- #### Environment Variable Management
- #### Database Security
- ### 9. Troubleshooting
- #### Build Fails on Netlify
- #### Database Connection Failed
- #### Frontend Can't Reach Backend
- ### 10. Testing Checklist
- ### 11. Future Improvements
- #### Automated Secret Rotation
- # Pseudocode for key rotation
- #### Continuous Sync Automation
- ## Conclusion


### ./docs/GITHUB_ENV_SYNC_GUIDE.md

- # GitHub Environment Sync Guide
- ## 🎯 Purpose
- ## 🚀 Quick Sync
- ### Command Line
- # Sync from Render to GitHub
- # Export snapshot for audit
- # Verify sync succeeded
- ### GitHub Actions
- # .github/workflows/env-sync.yml
- ## 🔐 Required Secrets
- ### In GitHub Repository Secrets
- ### In Render Environment
- ## 📊 How It Works
- ### 1. Fetch Phase
- ### 2. Compare Phase
- ### 3. Sync Phase
- ### 4. Verify Phase
- ## 🔍 Understanding the Output
- ### Successful Sync
- ### Drift Detected
- ## 📄 Generated Artifacts
- ### .env.sync.json
- ### env_parity_check.json
- ### GITHUB_ENV_AUDIT.md
- # GitHub Environment Sync Log
- ## Sync Report
- ## Parity Verification
- ## 🔧 Advanced Configuration
- ### Filtering Variables
- ### Dry Run Mode
- ### Custom Canonical Source
- ## 🧪 Testing
- ### Test Connection
- # Test Render API connectivity
- ### Test GitHub Secrets API
- # Test GitHub connectivity
- ## 🆘 Troubleshooting
- ### "GitHub sync not configured"
- ### "Failed to fetch Render env"
- ### Secrets Not Appearing in GitHub
- ### Variables Keep Showing as Drift
- ## 📚 Related Topics


### ./docs/BRIDGE_NOTIFICATIONS_ROLLBACK.md

- # Bridge Notifications, Retention, and Rollback System
- ## Features Overview
- ### 1. Netlify Build Context Fix ✅
- ### 2. Slack/Discord Webhook Notifications 📡
- ### 3. Diagnostic Retention & Cleanup 🧹
- ### 4. Automatic Netlify Rollback ♻️
- ### 5. Bridge Rollback Control API 🎮
- ## Required Secrets
- ## Event Flow
- ### Complete Deployment Lifecycle
- ### Notification Flow
- ## Usage Examples
- ### Manual Rollback
- ### Manual Diagnostic Cleanup
- ### Test Notifications
- ### Trigger Remote Rollback (from Bridge Dashboard)
- ## Testing
- ## Troubleshooting
- ### Slack Notifications Not Appearing
- ### Rollback Not Triggering
- ### Control API Returns 401
- ## File Changes Summary
- ## Benefits
- ## Next Steps


### ./docs/PREDICTIVE_DEPLOY_PIPELINE.md

- # Predictive Deploy Pipeline
- ## Overview
- ## Pipeline Stages
- ### 1. Environment Audit
- ### 2. Simulation (Leviathan)
- ### 3. Guard Synthesis (Hydra v2)
- ### 4. ARIE Repair (if needed)
- ### 5. Truth Certification
- ### 6. Deployment Decision
- ### 7. Outcome Reporting
- ## Flowchart
- ## GitHub Actions Integration
- ## Environment Variables
- ## Troubleshooting
- ### Simulation Failed
- ### Certification Failed
- ### Both Platforms Failed
- ## Monitoring
- ## Success Criteria


### ./docs/NETLIFY_SECRETS_SCANNING_FIX.md

- # Netlify Secrets Scanning Configuration Fix
- ## Problem
- ### Error Details
- ## Solution
- ### 1. Configure Secrets Scanning Exclusions
- #### Configuration Added
- ### 2. Updated Engine Exports
- ## Why This Works
- ## Security Considerations
- ### Why FORGE_DOMINION_ROOT is Safe to Exclude
- ### What Should NOT Be Excluded
- ## Testing
- ## References
- ## Maintenance


### ./docs/AUTONOMY_DEPLOYMENT_README.md

- # 🚀 Autonomy Engine Deployment Integration - README
- ## Overview
- ## What Was Built
- ### 3 Platform Integrations
- ### 6 Genesis Bus Topics
- ### 5 New Endpoints
- ### Event Flow
- ## Files Changed
- ### Created (7 files, ~2,000 lines)
- ### Modified (6 files)
- ## Total Impact
- ## Quick Start
- ### 1. Enable Genesis Mode
- ### 2. Test Integration
- # Test event publishing
- # Check integration status
- # Run verification
- ### 3. Configure Webhooks (Optional)
- ## Key Features
- ### Real-Time Monitoring
- ### Automated Response
- ### Multi-Platform Support
- ### Integration with Existing Systems
- ## Documentation
- ## Testing
- ### Verification Script
- ### Manual Testing
- # Test CLI publisher
- # Test webhook endpoints (after deployment)
- # Test autonomy API
- ## Event Examples
- ### GitHub Actions Event
- ### Webhook Event
- ### API Event
- ## Benefits
- ## Next Steps
- ### For Users (Setup)
- ### For Developers (Enhancements)
- ## Troubleshooting
- ### Genesis Mode Not Enabled
- # Check environment variable
- # Enable if needed
- ### Webhooks Not Working
- ### Events Not Publishing
- ## Support
- ## Conclusion


### ./docs/FORGE_MANIFEST_RESOLVER_GUIDE.md

- # Forge Dominion Manifest Resolver & Federation Heartbeat
- ## Overview
- ## Forge Dominion Manifest Resolver
- ### Purpose
- ### Endpoint
- ### Supported Targets
- ### Response Format
- ### Environment Variables
- ### Security
- ## Federation Heartbeat Extension
- ### Purpose
- ### Endpoint
- ### Request Format
- ### Heartbeat Daemon
- ### Environment Variables
- ### Integration
- # In brh/run.py main():
- ## Configuration
- # Forge configuration schema
- # Federation heartbeat configuration
- ## Testing
- ## Architecture
- ### Flow: Manifest Resolution
- ### Flow: Federation Heartbeat
- ## Benefits
- ## Next Steps


### ./docs/GENESIS_ARCHITECTURE.md

- # Genesis Linkage - Unified Engine Architecture
- ## System Overview
- ## Detailed Architecture
- ### Core Infrastructure Layer (6 Engines)
- ### Super Engines Layer (6 Engines)
- ### Utility Engines Layer (7 Engines)
- ## Event Bus Integration
- ### Event Flow Diagram
- ### Event Topics (33 Total)
- ## Dependency Graph
- ## API Endpoints (8 Total)
- ### Status & Information
- ### Initialization
- ### Dependencies
- ### Category Status
- ## File Structure
- ## Key Metrics
- ## Benefits


### ./docs/UMBRA_OVERVIEW.md

- # Umbra Unified Triage Mesh - Overview
- ## What is Umbra Triage Mesh?
- ## Why Umbra Triage Mesh?
- ## Architecture
- ## Core Concepts
- ### Signals
- ### Incidents
- ### Tickets
- ### Heal Plans
- ### Reports
- ## Pipeline Flow
- ### 1. Collect
- ### 2. Correlate
- ### 3. Classify
- ### 4. Decide
- ### 5. Heal
- ### 6. Certify
- ### 7. Report
- ## Genesis Integration
- ## Engine Integrations
- ### Autonomy Engine
- ### Cascade Engine
- ### Chimera Engine
- ### Parity Engine
- ### Truth Engine
- ## Key Features
- ### 1. Unified Triage
- ### 2. Automatic Correlation
- ### 3. Intelligent Healing
- ### 4. Safety Gates
- ### 5. PR Health Annotations
- ### 6. Observable & Auditable
- ## Configuration
- # Enable Umbra
- # Allow autonomous healing (intent-only by default)
- # Webhook security
- # Health thresholds
- # Parity enforcement
- # RBAC minimum role
- # Webhook secrets (optional)
- ## Next Steps


### ./docs/FIREWALL_HARMONY.md

- # Firewall Harmony - Auto-Repair Integration v1.7.6
- ## Overview
- ## Key Features
- ## Architecture
- ### Browser Strategy Selection
- ## Components
- ### 1. Workflow Integration (`.github/workflows/firewall_harmony.yml`)
- ### 2. Chromium Guard (`bridge-frontend/scripts/chromium-guard.mjs`)
- ### 3. Chrome Location Detector (`bridge-frontend/scripts/which-chrome.mjs`)
- ### 4. Chromium Probe (`bridge_backend/tools/firewall_intel/chromium_probe.py`)
- ## Configuration
- ### Netlify Configuration
- ### Render Configuration
- ### GitHub Actions Secrets/Variables
- ### Package.json Integration
- ## Usage
- ### Triggering the Workflow
- # Via GitHub CLI
- # Check status
- ### Viewing Diagnostic Reports
- # Download artifacts from workflow run
- # View report
- ### Manual Testing
- # Test chromium guard
- # Check Chrome installations
- # Generate diagnostic probe
- ## Auto-Repair Process
- ## Security & Compliance
- ### No Unsanctioned Egress
- ### Cache Integrity
- ### Full Audit Trail
- ### Approved Domains
- ## Troubleshooting
- ### Build Fails with "Browser not found"
- ### Cache Not Warming on Auto-Repair
- ### Netlify Build Fails
- ### Permission Denied on Cache Directory
- # In workflow, before running guard:
- ## Integration with Existing Workflows
- ## Performance Impact
- ## Monitoring
- ### Metrics to Track
- ### Dashboard Queries
- # Get all probe reports
- # Analyze strategies
- ## Lore Entry
- ## Version History
- ## Related Documentation
- ## Support


### ./docs/PHOENIX_PROTOCOL.md

- # Phoenix Protocol
- ## Documented Perfection Rebuild
- ## 🔥 What is the Phoenix Protocol?
- ## 📁 Directory Structure
- ## 🎯 Rebuild Phases
- ### Phase 1: Core Backend (BUILD_DOSSIER Steps 1-3)
- ### Phase 2: Essential Engines (BUILD_DOSSIER Steps 4-5)
- ### Phase 3: Agent & Mission Management
- ### Phase 4: Frontend Foundation
- ### Phase 5: Advanced Engines
- ### Phase 6: Support Systems
- ### Phase 7: Specialized Features
- ### Phase 8: Deployment & Testing
- ## 📊 Comparison Metrics
- ## 🔍 Key Differences to Track
- ## 🚀 Usage
- ### Run Phoenix Backend
- ### Run Phoenix Frontend
- ### Compare with Current
- # Compare file structures
- # Compare LOC
- # Compare endpoints
- ## 📝 Build Log
- ### 2025-11-04 - Phase 1 Complete ✅
- ## 🎓 Lessons Learned
- ## 🔗 References


### ./docs/AUTONOMY_V196T_QUICK_REF.md

- # Autonomy v1.9.6t - Quick Reference
- ## What's New in v1.9.6t?
- ### 🆕 New Features
- ## Quick Start
- ### Enable Autonomy
- ### Trigger Manual Healing
- ### View Certificates
- ## Decision Matrix
- ## Safety Guardrails
- # Rate Limiting: 6 actions/hour
- # Cooldown: 5 minutes between actions
- # Circuit Breaker: trips after 3 failures
- ## Reinforcement Scoring
- # Example:
- # - ARIE success rate: 0.85
- # - Cooldown penalty: 0.10 (2 min since last action)
- # - Final score: 0.75
- ## Leviathan Prediction
- # Returns: 0.0 to 1.0
- # Warning threshold: < 0.3
- ## Certificate Format
- ## GitHub Workflows
- ### bridge_autonomy.yml
- ### env_sync.yml
- ## Environment Config
- ## Integration Flow
- ## Engine Success Rates
- # Initial rates:
- # Updated after each action:
- ## Testing
- # Run all v1.9.6t tests
- # Run original tests (backward compatibility)
- # Run all autonomy tests
- ## API Endpoints
- # Emit incident
- # Get governor status
- # Get recent certificates
- ## Common Tasks
- ### Force Environment Sync
- ### View Predictions
- ### Check Circuit Breaker Status
- ### Reset Governor State
- ## Troubleshooting
- ### Autonomy not triggering?
- ### Circuit breaker tripped?
- # Check fail streak
- ### Low prediction scores?
- ### Certificates not generating?
- ## File Locations
- ## Version Compatibility
- ## Next Steps
- ## Resources


### ./docs/STEWARD_DEPLOYMENT_GUIDE.md

- # Env Steward v1.9.6l — Deployment Guide
- ## Admiral-Tier Environment Orchestration
- ## Overview
- ## Pre-Deployment Checklist
- ## Deployment Steps
- ### 1. Ship to Main
- ### 2. Enable Engine (Read-Only)
- # Provider toggles (keep false for now)
- # Provider identifiers (non-secret, safe to add)
- ### 3. Verify Deployment
- ### 4. Test Diff/Plan (Read-Only)
- ## Optional: Enable Write Mode
- ### 5. Add Provider Tokens
- ### 6. Enable Write Mode
- ### 7. Issue Capability Token
- ### 8. Apply Plan
- ### 9. Monitor Genesis Events
- ## Security Notes
- ### Admiral-Only Access
- ### Capability Tokens
- ### Secret Handling
- ## Rollback
- ## Monitoring
- ### Genesis Events
- ### Health Check
- ## Troubleshooting
- ### Deployment Issues
- ### Write Mode Issues
- ## Ops Playbook
- ### Daily Operations
- ### Emergency Rollback
- ### Capability Management
- ## What's Next?
- ### Phase 1: Read-Only Monitoring (Current)
- ### Phase 2: Write Mode (Optional)
- ### Phase 3: Autonomy Integration (Future)
- ## Support


### ./docs/NOTIFICATION_EXAMPLES.md

- # Example Slack/Discord Notifications
- ## Notification Format
- ## Example Notifications
- ### Deployment Success ✅
- ### Deployment Failure ❌
- ### Build Failure 🧱
- ### Environment Repair 🔧
- ### Automatic Rollback ♻️
- ### Manual Rollback (from Dashboard) 🎮
- ### Diagnostic Cleanup 🧹
- ## Setting Up Webhook
- ### For Slack
- ### For Discord
- ## Testing Notifications
- # Set the webhook URL
- # Test a notification
- ## Disabling Notifications
- ## Notification Schedule
- ## Advanced: Custom Notifications
- # Send a custom notification
- ## Troubleshooting


### ./docs/INCIDENT_CATALOG.md

- # Incident Catalog
- ## Incident Structure
- ## Deployment Incidents
- ### `deploy.netlify.preview_failed`
- ### `deploy.render.failed`
- ### `deploy.render.rollback`
- ## Environment Incidents
- ### `envrecon.drift`
- ### `env.drift.detected`
- ## Code Integrity Incidents
- ### `arie.deprecated.detected`
- ### `code.integrity.deprecated`
- ## Generic Incidents
- ### `*` (Unknown/Unrecognized)
- ## Adding New Incident Kinds
- ### 1. Update Governor Policy Matrix
- ### 2. Update Genesis Topics (if needed)
- ### 3. Create Genesis Subscription (if needed)
- ### 4. Update This Catalog
- ### 5. Add Test Coverage
- ## Action Reference
- ## Event Flow Examples
- ### Example 1: Netlify Preview Failure → Auto-Fix
- ### Example 2: Environment Drift → Auto-Sync
- ### Example 3: Repeated Failures → Circuit Breaker
- ## See Also


### ./docs/HEALER_NET.md

- # Healer-Net Diagnostic Network
- ## Health States
- ## Auto-Repair Integration
- ## Artifact
- ## Architecture
- ### Components
- ## Usage
- ### Automated Execution
- ### Frontend Integration
- ## Health Report Format
- ## Integration with Existing Systems
- ## Troubleshooting
- ### Healer-Net Not Running
- ### Health Badge Not Showing Data
- ### Report Not Generated
- ## Related Documentation
- ## Future Enhancements


### ./docs/SCRIBE_README.md

- # EnvScribe — Unified Environment Intelligence System
- ## 🎯 Purpose
- ## 🏗️ Architecture
- ### Core Components
- ## 🚀 Quick Start
- ### CLI Usage
- # Full audit (recommended)
- # Scan repository only
- # Generate documentation and copy blocks
- # Get copy-ready block for a platform
- # View current report
- ### API Endpoints
- # Health check
- # Run full audit
- # Scan only
- # Get current report
- # Generate artifacts
- # Get copy block for platform
- ## 📊 Output Files
- ### Documentation
- ### Diagnostics
- ## 📋 Example Output
- ### Copy-Ready Block (Render)
- ### ENV_OVERVIEW.md (Sample)
- # Environment Overview
- ## Summary
- ## Variables
- ### Legend
- ## 🔗 Genesis Events
- ### Published Events
- ### Event Integration
- ## 🧪 Testing
- # Run EnvScribe-specific tests
- # Run full environment sync pipeline tests
- ## 🔐 Truth Engine Integration
- ## 🎛️ Configuration
- # Enable/disable EnvScribe
- # Enable/disable Truth Engine certification
- # Enable/disable Genesis Bus integration
- ## 🔄 Integration with Other Engines
- ### Parser Engine
- ### EnvRecon
- ### Steward
- ### HXO
- ### ARIE
- ## 📖 Related Documentation
- ## 🏆 Achievements


### ./docs/CHIMERA_API_REFERENCE.md

- # Chimera API Reference
- ## CLI Commands
- ### `chimeractl`
- #### Global Options
- ### Commands
- #### `simulate`
- # Simulate Netlify deployment
- # Simulate with JSON output
- # Simulate specific path
- #### `deploy`
- # Deploy to Netlify with certification
- # Deploy to Render without healing
- # Deploy with JSON output
- #### `monitor`
- # Monitor status
- # Get JSON output
- #### `verify`
- # Verify Netlify deployment
- # Verify with JSON output
- ## REST API Endpoints
- ### GET `/status`
- ### GET `/config`
- ### POST `/simulate`
- ### POST `/deploy`
- ### GET `/deployments`
- ### GET `/certifications`
- ## Genesis Bus Events
- ### Published Events
- #### `deploy.initiated`
- #### `deploy.heal.intent`
- #### `deploy.heal.complete`
- #### `deploy.certified`
- #### `chimera.simulate.start`
- #### `chimera.simulate.complete`
- #### `chimera.deploy.start`
- #### `chimera.deploy.complete`
- #### `chimera.rollback.triggered`
- ## Python API
- ### ChimeraDeploymentEngine
- # Initialize
- # Or use singleton
- #### Methods
- ##### `deploy(platform, project_path=None, auto_heal=True, certify=True)`
- ##### `simulate(platform, project_path=None)`
- ##### `monitor()`
- ### ChimeraConfig
- # Export as JSON
- # Export as dict
- ## Environment Variables
- ## Error Codes
- ## Rate Limits
- ## Examples
- ### Full Deployment Pipeline
- ### Simulation Only
- ### Monitor Status


### ./docs/HXO_BLUEPRINT_CONTRACT.md

- # HXO Blueprint Contract
- ## Overview
- ## Job Kinds
- ### `deploy.pack`
- ### `deploy.migrate`
- ### `deploy.prime`
- ### `assets.index`
- ### `assets.stage`
- ### `docs.index`
- ## Validation Rules
- ### Stage Validation
- ### Example Validation
- ## Adding New Job Kinds
- # In hxo_blueprint_link.py
- # In partitioners.py
- # In executors.py
- ## Safety Policies
- ### `allow_non_idempotent`
- ### `require_dry_run`
- ## Result Schemas
- ## Evolution Policy
- ## Appendix: Full Job Kind Registry


### ./docs/ENDPOINT_TRIAGE.md

- # Endpoint Triage System
- ## Overview
- ## Architecture
- ### Components
- ## Health Status Levels
- ## Usage
- ### Manual Execution
- ### View Triage Report
- ### Automated Execution
- ### Frontend Integration
- ## Configuration
- ### Environment Variables
- ### Monitored Endpoints
- ## Integration with Diagnostics Timeline
- ## Troubleshooting
- ### Triage Not Running on Startup
- ### Workflow Failures
- ### Frontend Panel Not Showing Data
- ## Security Considerations
- ## Future Enhancements


### ./docs/UPGRADE_GUIDE.md

- # SR-AIbridge Upgrade Guide
- ## Current Architecture (v1.1.0-autonomous)
- ### 🤖 Autonomous Backend Features
- ### 🌐 Enhanced Frontend Features
- ## Deployment Options
- ### Option 1: Quick Start (In-Memory Demo)
- ### Option 2: Production Database Backend
- #### Step 1: Database Setup
- #### Step 2: Database Models
- #### Step 3: Update Main Application
- #### Step 4: Environment Configuration
- #### Step 5: Deploy Database Version
- ## Feature Comparison
- ## Migration Strategy
- ### Zero-Downtime Migration
- ### Data Migration (Optional)
- # migration_script.py
- ## Troubleshooting
- ### Common Issues
- ### Performance Optimization
- ## Support and Maintenance
- ### Monitoring
- ### Backup Strategy
- ### Updates and Scaling
- ## CI/CD & Monitoring
- ### Automated Deployment Pipeline
- #### 🚀 Deployment Workflow (`.github/workflows/deploy.yml`)
- # Required GitHub Secrets (optional but recommended)
- # Optional: Custom deployment URLs
- #### 🧪 Health Monitoring Workflow (`.github/workflows/self-test.yml`)
- #### Enhanced Self-Test Script
- # Production health check
- # Advanced CI/CD usage
- # Local development testing  
- #### Manual Health Monitoring
- # Clone repository locally
- # Install dependencies
- # Run health check against your deployment
- #### Monitoring Dashboard
- #### Troubleshooting CI/CD


### ./docs/UPGRADE_v1.9.6q.md

- # Upgrade Guide: v1.9.6q
- ## What's New
- ### HXO↔Genesis Async-Safe Linkage
- ## Breaking Changes
- ## Migration Steps
- ### If You Use the Default Setup
- ### If You Have Custom HXO Integration
- ## New Topics
- ## Deployment Checklist
- ## Config Changes
- ## Testing


### ./docs/GENESIS_REGISTRATION_OVERVIEW.md

- # Genesis Registration Overview
- ## 🌌 Node Registration & Federation Protocol
- ## Overview
- ## Registration Process
- ### 1. Node Initialization
- ### 2. Genesis Bus Connection
- ### 3. Event Publication
- ### 4. Confirmation
- ## Registration Payload
- ### Standard Fields
- ### Optional Fields
- ### Example Full Registration
- ## Registration States
- ### Active
- ### Inactive
- ### Degraded
- ### Failed
- ## Genesis Bus Topics
- ### Registration Topic
- ### Report Topic
- ### Status Topics
- ## Federation Integration
- ### Discovery
- # Find autonomy node
- ### Coordination
- # Route repair request to autonomy node
- ### Health Monitoring
- # Check node status
- ## Registration Implementation
- ### Module Location
- ### Main Function
- ### Usage in Application
- # During application startup
- # Register node
- ### Usage in Workflow
- # In .github/autonomy_node/core.py
- ## Configuration
- ### Enable/Disable Registration
- ### Environment Variables
- # Enable Genesis mode
- # Enable strict policy
- ### Conditional Registration
- # Only register in production
- ## Offline Mode
- ## Security Considerations
- ### Authentication
- ### Authorization
- ### Validation
- # In GenesisEventBus.publish()
- ### Encryption
- ## Monitoring & Debugging
- ### Check Registration Status
- ### View Registration Events
- # Get recent events
- # Filter registration events
- ### Debug Registration Failures
- # Enable debug logging
- # Attempt registration
- ## Best Practices
- ## Troubleshooting
- ### Registration Not Appearing
- ### Duplicate Registrations
- ### Registration Stale
- ### Cannot Find Registered Node
- ## Future Enhancements
- ## See Also


### ./docs/POSTGRES_RENDER_SETUP.md

- # Render PostgreSQL Setup
- ## 1. Database
- ### Database Details
- ### Creating the Database
- ## 2. Connection
- ### Connection String Format
- ### Important Notes
- ## 3. Render Environment
- ### Required Environment Variables
- # Database Configuration
- # Bridge Services
- # Optional Monitoring
- ### Environment Variable Details
- ## 4. Verification
- ### Troubleshooting Connection Issues
- ## 5. Database Initialization
- ### Option A: Via Render Shell
- ### Option B: From Local Machine
- # Using the External Database URL
- ### What Gets Created
- ## 6. Monthly Maintenance
- ### Automated Maintenance
- ### Manual Maintenance
- ## 7. Security Best Practices
- ## 8. Performance Optimization
- ### Connection Pooling
- # Default settings in bridge_backend/db.py
- ### Monitoring Queries
- ## 9. Backup and Recovery
- ### Creating a Manual Backup
- ### Restoring from Backup
- ## 10. Migration from SQLite
- ## Support


### ./docs/COMPONENT_INDEX.md

- # Component Index
- ## Complete File & Component Reference for SR-AIbridge
- ## 📁 Root Level Files
- ### Documentation
- ### Configuration Files
- ### Database Files
- ### Scripts & Tools
- ## 🐍 Backend (`bridge_backend/`)
- ### Core Files
- ### Bridge Core (`bridge_backend/bridge_core/`)
- #### Agents System
- #### Missions System
- #### Health Monitoring
- #### Guardians System
- #### Vault/Logging
- #### Fleet Management
- #### Captains System
- #### Custody/Keys
- #### Forge Dominion (Token Management)
- #### Runtime Handler (BRH)
- ## 🧠 Engines (`bridge_backend/bridge_core/engines/`)
- ### Blueprint Engine
- ### Leviathan Solver
- ### Autonomy Engine
- ### TDE-X Engine
- ### Cascade Engine
- ### Truth Engine
- ### Super Engines (6)
- ### Utility Engines (7)
- ## ⚛️ Frontend (`bridge-frontend/`)
- ### Root Files
- ### Source Files (`bridge-frontend/src/`)
- ### Components (`bridge-frontend/src/components/`)
- #### Core Components
- #### Mission & Planning
- #### Agent & Fleet
- #### Communication
- #### Data & Logging
- #### Administration
- #### Specialized Panels
- ### UI Components (`bridge-frontend/src/components/ui/`)
- ### API Client (`bridge-frontend/src/api/`)
- ## 🔧 Infrastructure
- ### CI/CD (`.github/workflows/`)
- ### Deployment
- ## 📚 Documentation (`docs/`)
- ### Quick References (26 files)
- ### Key Documentation
- ## 📊 Stats Summary
- ### File Counts
- ### Code Volume
- ### Component Counts
- ## 🔍 Quick Find Guide


### ./docs/ENDPOINT_TRIAGE_QUICK_REF.md

- # Endpoint Triage Quick Reference
- ## 🚀 Quick Start
- ### Manual Check
- ### View Report
- ### Trigger GitHub Workflow
- ### Add to Dashboard
- ## 📊 Status Levels
- ## 🔍 Monitored Endpoints
- ## 🔧 Configuration
- ### Environment Variables
- ### Add New Endpoint
- ## 📅 Automated Execution
- ## 🛠️ Troubleshooting
- ### Script Not Running
- # Check script exists and is executable
- # Make executable if needed
- # Check Python dependencies
- ### Frontend Not Showing Data
- # Check diagnostics timeline API
- # Verify triage has run
- ### Workflow Failures
- ## 📝 Example Report
- ## 🔗 Related Documentation
- ## 💡 Tips


### ./docs/INTEGRITY_DEFERRED_GUIDE.md

- # Integrity Deferred Guide
- ## Problem Statement
- ## Solution: Deferred Integrity
- ### Key Concept
- ## How It Works
- ### Function: `delayed_integrity_check(run_integrity_callable)`
- # This will wait 3 seconds, then run integrity checks
- ## Configuration
- ### Environment Variable
- # Delay before running integrity checks (seconds)
- ### Recommended Values
- ## Integration
- ### In Application Boot (main.py)
- # After all engines initialize...
- ### In CI/CD (GitHub Actions)
- ## Boot Sequence
- ## Timing Tuning
- ### Too Short (< 2 seconds)
- ### Too Long (> 10 seconds)
- ### Just Right (3-5 seconds)
- ## Custom Integrity Checks
- ### Example 1: Simple Check
- ### Example 2: Complex Validation
- ### Example 3: Conditional Checks
- ## Testing
- ### Unit Test
- ### Integration Test
- ## Debugging
- ### Enable Debug Logging
- ### Disable Deferral (Development)
- # Set to 0 to run immediately
- ### Verbose Checks
- ## Best Practices
- ## Troubleshooting
- ### Issue: Checks still fail after deferral
- ### Issue: Slow boot times
- ### Issue: Checks timeout
- ### Issue: No deferral happening


### ./docs/ENVIRONMENT_SETUP.md

- # Environment Integration & Build Stabilization
- ## Overview
- ## Environment Variable Reference
- ## Render Setup
- ### Environment Group: SR_AIBridge_Production
- ### Required Environment Variables
- # Core Database
- # Backend Configuration
- # Security
- # Bridge Services
- # Logging
- # CORS
- # Diagnostics (Internal Genesis telemetry only)
- ### Using .env.render
- ## Netlify Setup
- ### Environment Configuration
- ### Netlify Dashboard Configuration
- # API Configuration
- # Bridge Configuration
- # Federation
- # Diagnostics (Internal Genesis telemetry only)
- ### Using .env.netlify
- ### netlify.toml Configuration (v1.6.6)
- ### Bridge Compliance and Plugin Enforcement (v1.6.6)
- #### Plugin Requirements
- #### Pre-Build Sanitizer
- # Run manually
- # Output example:
- # [SR-AIBridge Sanitizer]
- # Version: 1.6.6
- # ---
- # ✔ Sanitized 3 file(s)
- #   - dist/assets/config.json
- #   - node_modules/.cache/vite/env.json
- #   - .env.local
- # ✔ Updated manifests: dist/assets, node_modules/.cache
- # ✔ Compliance ready for build
- # ✔ Manifest: sanitized_manifest.log
- #### Local Compliance Checks
- # Validate environment setup
- # Validate scanner compliance
- # Run sanitizer
- # Build and test
- #### GitHub Actions Workflow
- ## Deployment Workflow
- ### Initial Setup
- #### Render (Backend)
- #### Netlify (Frontend)
- ### Environment Synchronization
- ## Security Best Practices
- ### Secret Management
- ### Frontend Safety
- ## Troubleshooting
- ### Netlify Scanner Compliance & Security Policy (v1.6.4)
- #### Safe Omit Paths vs Sensitive Paths
- #### How to Read Scanner Logs
- #### Configuration Validation
- # Run scanner compliance validation
- ### Build Fails with Missing Environment Variables
- ### Secret Scan Warnings (Updated for v1.6.4)
- ### Database Connection Errors on Render
- ### CORS Errors
- ## File Reference
- ## Validation Scripts
- ### Pre-Deploy Validation (`validate_netlify_env.py`)
- # or directly:
- ### Post-Deploy Verification (`verify_netlify_build.py`)
- ### Environment Repair (`repair_netlify_env.py`)
- ### Environment Parity Check (`check_env_parity.py`)
- ### Environment Sync Monitor (`env_sync_monitor.py`)
- ## Auto-Repair & CI/CD Integration
- ### GitHub Actions Auto-Heal Workflow
- ### Auto-Repair Mode
- ### Bridge Health Reporting
- ## Conclusion
- ## Auto-Deploy & Sync Badge (v1.6.7)
- ### Bridge Auto-Deploy Mode
- ### Live Sync Badge
- # Check both endpoints
- # Generate status badge JSON
- ### Environment Variables (v1.6.7)
- ### Registry Fallback Configuration


### ./docs/IMPLEMENTATION_SUMMARY.md

- # Heritage Subsystem Integration - Implementation Summary
- ## ✅ Completed Implementation
- ## 📦 What Was Built
- ### Backend Components (24 new files)
- #### 1. **Unified Event Bus** (`bridge_core/heritage/event_bus.py`)
- #### 2. **MAS (Multi-Agent System)** (`bridge_core/heritage/mas/`)
- #### 3. **Federation** (`bridge_core/heritage/federation/`)
- #### 4. **Agent System** (`bridge_core/heritage/agents/`)
- #### 5. **Demo Presets** (`bridge_core/heritage/demos/`)
- #### 6. **API Routes** (`bridge_core/heritage/routes.py`)
- #### 7. **Core Integration** (`bridge_core/core/`)
- ### Frontend Components (13 new files)
- #### 1. **Command Deck V1** (`pages/CommandDeckV1.jsx`)
- #### 2. **Deck Panels** (`components/DeckPanels/`)
- #### 3. **WebSocket Hook** (`hooks/useBridgeStream.js`)
- #### 4. **Styling** (`styles/deck.css`)
- #### 5. **Router Integration** (`App.jsx`)
- ### Documentation (3 new files)
- ## 🧪 Testing
- ### Test Results: **13/13 PASSING** ✅
- ## 🎨 UI Screenshots
- ### Command Deck V1 Layout
- ## 🔄 Event Flow
- ## 📊 Event Topics
- ## 🚀 Usage Examples
- ### Backend - Start a Demo
- # Publishes 7 events over ~3 seconds
- ### Backend - Subscribe to Events
- ### Frontend - Launch Demo from UI
- ### API - Trigger Demo
- # Returns: {"status": "Started mas demo", "mode": "mas"}
- ## 🔧 Configuration
- ### Backend Environment Variables (Optional)
- ### Frontend Environment Variables
- # .env.local
- ## ✨ Key Features
- ### No Breaking Changes
- ### Database Agnostic
- ### Production Ready
- ### Extensible
- ## 📈 Future Enhancements (Optional)
- ## 🎯 Success Criteria Met
- ## 🏗️ File Structure Summary
- ## 🎉 Conclusion


### ./docs/UMBRA_README.md

- # Umbra Cognitive Stack — Complete Documentation
- ## 🌑 Overview
- ## 🧠 The Cognitive Architecture
- ## 🔧 Component Details
- ### Umbra Core - Pipeline Self-Healing
- # Detect anomaly
- # Generate and apply repair
- ### Umbra Memory - Experience Graph & Recall
- # Record experience
- # Recall experiences
- # Learn patterns
- ### Umbra Predictive - Confidence-Based Pre-Repair
- # Predict issue
- # Apply preventive repair
- # Update model with feedback
- ### Umbra Echo - Human-Informed Adaptive Learning
- # Capture manual edit
- # Observe git commit
- ## 🔄 Full Cognitive Lifecycle
- ## 📡 Genesis Bus Integration
- ### Published Topics
- #### `umbra.anomaly.detected`
- #### `umbra.pipeline.repaired`
- #### `umbra.echo.recorded`
- #### `umbra.memory.learned`
- ## 🔒 Security & RBAC
- ### Admiral Only (Write Operations)
- ### Captain (Read + Monitor)
- ### Observer (Read-Only)
- ## 🧪 Testing
- ### Test Coverage
- ### Running Tests
- # Run all Umbra tests
- # Run specific component
- ## ⚙️ Configuration
- ### Environment Variables
- # Enable Umbra self-healing intelligence
- # Enable Umbra Memory (experience graph & recall)
- # Enable Umbra Echo (human-informed learning)
- # Training interval for predictive model updates
- # Enable reflection on git commits
- ### Storage Paths
- ## 📊 Metrics & Monitoring
- ### Umbra Core Metrics
- ### Umbra Memory Metrics
- ### Umbra Predictive Metrics
- ### Umbra Echo Metrics
- ## 🚀 Deployment
- ### Prerequisites
- ### Integration Steps
- ## 💡 Best Practices
- ### For Admirals
- ### For Captains
- ### For Developers
- ## 🔧 Troubleshooting
- ### Umbra Not Detecting Anomalies
- ### Memory Not Persisting
- ### Echo Not Capturing Changes
- ### Predictions Not Working
- ## 📚 Additional Resources
- ## 🎯 Future Enhancements


### ./docs/BRH_CONSENSUS_GUIDE.md

- # BRH Consensus and Leader Election Guide
- ## Overview
- ## Architecture
- ### Components
- ## Configuration
- ### Environment Variables
- # Node identity (must be unique per BRH instance)
- # Environment name (for container filtering)
- # Forge root endpoint
- # Consensus settings
- # Heartbeat settings
- # Security seal
- ### Runtime Manifest (`bridge.runtime.yaml`)
- ## How It Works
- ### 1. Heartbeat Phase
- ### 2. Consensus Election
- # Election algorithm
- ### 3. Leader Polling
- ### 4. Role Transitions
- #### Promotion (Witness → Leader)
- #### Demotion (Leader → Witness)
- ### 5. Container Ownership
- ## API Behavior
- ### `/deploy` Endpoint
- # Response: {"status": "restarted", "image": "myapp:latest"}
- # Response: {"status": "ignored", "reason": "not-leader"}
- ## Testing
- ### Unit Tests
- ### Integration Tests
- ### Manual Testing (Two Node Setup)
- ## Security Considerations
- ## Troubleshooting
- ### No Leader Elected
- # Check heartbeat status
- # Verify peers
- ### Containers Not Adopted
- # Install Docker SDK
- # Check Docker access
- ### Deploy Hook Rejected
- # Check role status
- # Wait for next consensus cycle or promote manually
- ## Advanced: Custom Demotion Policy
- ## Future Enhancements
- ## References


### ./docs/DOCUMENTATION_USAGE_GUIDE.md

- # How to Use SR-AIbridge Documentation
- ## Your Practical Guide to Navigating 118,000+ Lines of Documentation
- ## 🎯 Quick Navigation Guide
- ### "I want to..."
- #### Get Started Quickly
- #### Understand the Whole System
- #### Build Something Specific
- #### Deploy to Production
- #### Troubleshoot Issues
- ## 📚 Documentation Hierarchy Explained
- ### Level 1: Entry Points (Start Here)
- ### Level 2: Understanding (Go Deeper)
- ### Level 3: Building (Get Hands-On)
- ### Level 4: Advanced Topics (Master the System)
- ### Level 5: Reference (Quick Lookup)
- ## 🔍 How to Find What You Need
- ### Method 1: Use DOCUMENTATION_INDEX.md (Recommended)
- ### Method 2: Use NAVIGATION_INDEX.md (For Learning Paths)
- ### Method 3: Use FEATURE_INVENTORY.md (For Discovery)
- ### Method 4: Search Entire Repository
- # Search all markdown files
- # Search with context
- # Find files by name
- ## 📖 Reading Strategies by Role
- ### For Complete Beginners
- ### For Experienced Developers
- ### For Architects / Technical Leads
- ### For DevOps / Platform Engineers
- ## 🎓 Learning Paths
- ### Path 1: User (Want to Use SR-AIbridge)
- ### Path 2: Developer (Want to Extend SR-AIbridge)
- ### Path 3: Contributor (Want to Improve SR-AIbridge)
- ## 💡 Pro Tips for Documentation Navigation
- ### Tip 1: Use Ctrl+F (Cmd+F) Aggressively
- ### Tip 2: Follow the Breadcrumbs
- ### Tip 3: Use Quick Refs for Reminders
- ### Tip 4: Bookmark Your Key Documents
- ### Tip 5: Check FEATURE_INVENTORY.md First
- ### Tip 6: Start with Examples
- ### Tip 7: Use Multiple Documents Together
- ### Tip 8: Progressive Disclosure
- ## 📊 Documentation Quality Indicators
- ### ✅ Complete Documentation
- ### ⚠️ Partial Documentation
- ### ❌ Minimal/No Documentation
- ## 🔧 Practical Examples
- ### Example 1: "I want to deploy to production"
- ### Example 2: "I want to use the Blueprint Engine"
- ### Example 3: "I'm getting a health check error"
- ### Example 4: "I want to understand the Autonomy system"
- ## 🎯 Common Documentation Workflows
- ### Workflow 1: Learning a New Feature
- ### Workflow 2: Debugging an Issue
- ### Workflow 3: Contributing Documentation
- ### Workflow 4: Customizing SR-AIbridge
- ## 📝 Documentation Standards & Format
- ### Every Good Guide Should Have:
- ### Documentation File Types:
- ## 🤝 Contributing to Documentation
- ## 🎓 Summary: Your Documentation Workflow
- ### Daily Usage
- ### Learning
- ### Discovery
- ### Troubleshooting
- ## 🔗 Key Resources


### ./docs/EMBEDDED_AUTONOMY_NODE.md

- # Embedded Autonomy Node (EAN)
- ## 🚀 v1.9.7n - GitHub Internal Mini-Bridge Engine
- ## Overview
- ## Purpose
- ## Architecture
- ## Behavior Flow
- ## Components
- ### Core Orchestrator (`core.py`)
- ### Truth Micro-Certifier (`truth.py`)
- # ✅ Truth verified for all stable modules
- ### Parser Sentinel (`parser.py`)
- # Returns: {"file.py": {"status": "warn", "reason": "debug print"}}
- ### Blueprint Micro-Forge (`blueprint.py`)
- # Returns: {"file.py": {"status": "ok", "action": "log_cleaned"}}
- ### Cascade Mini-Orchestrator (`cascade.py`)
- # Syncs post-repair state with main cascade engine
- ## Configuration
- ### Configuration Options
- ## Workflow Integration
- ### Triggers
- ## RBAC & Safety
- ## Telemetry
- ### Local Reports
- ### Genesis Bus Topics
- ## Genesis Registration
- # Returns: {"registered": true, "node": {...}}
- ## Testing & Verification
- ## Manual Testing
- ## Lifecycle Summary
- ## Integration with Total Autonomy Protocol
- ## Post-Merge Behavior
- ## Version Details
- ## See Also


### ./docs/CHIMERA_README.md

- # Project Chimera: Autonomous Deployment Sovereignty
- ## v1.9.7c — Chimera Deployment Engine (CDE)
- ## Overview
- ## Problem Statement
- ## Solution: Chimera Deployment Engine (CDE)
- ## 🧩 System Integration Matrix
- ## 🧠 Core Deployment Flow
- ## ✨ Features
- ### 1. **Predictive Build Simulation**
- ### 2. **Autonomous Configuration Healing**
- ### 3. **Deterministic Deployment Protocol**
- ### 4. **Cross-Platform Adaptivity**
- ### 5. **Self-Monitoring & Temporal Resilience**
- ## 🚀 Quick Start
- ### CLI Usage
- # Simulate Netlify deployment
- # Deploy to Render with certification
- # Monitor deployment status
- # Verify with Truth Engine
- ### API Usage
- # Get Chimera status
- # Simulate deployment
- # Execute deployment
- ### Render Integration
- ## 🛡️ Security and Control
- ## 📈 Testing and Validation
- ## 📜 Documentation
- ## 🧩 Configuration
- # Enable/disable Chimera
- # Simulation timeout (seconds)
- # Healing max attempts
- ## 🌐 Genesis Bus Integration
- ## 🚀 Impact
- ## 🧩 Complementary Updates
- ## Final Declaration
- ## Version Information


### ./docs/PARITY_ENGINE_QUICK_GUIDE.md

- # Bridge Parity Engine - Quick Reference Guide
- ## What is the Parity Engine?
- ## Quick Start
- ### 1. Run Parity Analysis
- ### 2. Auto-Fix Mismatches
- ### 3. Run Tests
- ## What the Tools Do
- ### Parity Engine (parity_engine.py)
- ### Auto-Fix Engine (parity_autofix.py)
- ## Current Status (Last Run: 2025-10-09 11:46 UTC)
- ### Critical Issues Resolved
- ### Pending Manual Review (5 endpoints)
- ## How to Use Generated Stubs
- ### Frontend Integration
- ### Backend Implementation
- ## File Locations
- ### Reports
- ### Generated Code
- ### Tests
- ## Understanding Severity Levels
- ### 🔴 Critical
- ### 🟡 Moderate
- ### 🔵 Informational
- ## Troubleshooting
- ### Parity Report Not Found
- ### Stubs Not Generated
- ### Test Failures
- ## Best Practices
- ### 1. Run Regularly
- ### 2. Review Before Integrating
- ### 3. Clean Up Unused Stubs
- ### 4. Keep Documentation Updated
- ## Quick Commands
- # Full parity check and fix
- # View summary
- # Count generated stubs
- # Check for critical issues
- ## Support & Documentation
- ## Version Information


### ./docs/ROLES_INTERFACE_AUDIT.md

- # SR-AIbridge Roles & Interface Audit Report
- ## Executive Summary
- ## Audit Results by Component
- ### 1. Dashboard (Main Display) ✅ COMPLETE
- ### 2. Captain's Chat ✅ COMPLETE
- ### 3. Captain-to-Captain Chat ✅ COMPLETE
- ### 4. Vault ✅ ENHANCED
- ### 5. Brain ✅ IMPLEMENTED
- ### 6. Custody ✅ SECURED
- ### 7. System Health ✅ ENHANCED
- ## RBAC Matrix Summary
- ## Additional Features Verified
- ### Navigation (App.jsx)
- ### Backend Routes Registration
- ## Issues Found and Resolved
- ### Issue 1: Brain Routes Incomplete
- ### Issue 2: Vault Isolation Missing
- ### Issue 3: RBAC Not Explicit for New Features
- ### Issue 4: System Health No Role Differentiation
- ### Issue 5: Custody Middleware Not Enforced
- ## File Changes Summary
- ### Modified Files:
- ### No Changes Required:
- ## Testing Recommendations
- ## Conclusion


### ./docs/README_SECURITY.md

- # README_SECURITY.md — quick developer guide
- ## Archival-before-delete (relay_mailer)
- ## Key generation & vault access
- ## Fault injection tests
- ## Where to look in the codebase
- ## Quick safety checks before merging


### ./docs/HXO_OPERATIONS.md

- # HXO Operations Guide
- ## Table of Contents
- ## Starting HXO
- ### Enable HXO
- ### Verify HXO is Running
- # Should return 404 (plan not found), confirming endpoint is active
- ## Submitting Plans
- ### Method 1: Direct API Call
- ### Method 2: Using Parser (Future)
- # Parse CLI command into plan
- ## Monitoring Status
- ### Get Live Status
- ### Watch Status (Poll)
- ### Genesis Events
- ## Aborting Plans
- ### Abort Running Plan
- ## Replaying Failed Subtrees
- ## SLO Tuning
- ### Understanding SLOs
- ### Tuning Strategy
- ### Example Tuning
- ## Troubleshooting
- ### Plan Stuck in "Pending"
- # Check HXO enabled
- # Check Genesis bus
- # Check checkpoint DB
- # Should exist and not be locked
- ### Shards Failing
- # Get plan report
- # Check Genesis audit events
- ### Merkle Certification Failing
- ### Performance Issues
- # Increase concurrency (careful with resource limits)
- # Enable hot-shard splitting
- ## Best Practices
- ## Advanced: Manual Checkpoint Recovery
- # Initialize
- # Find incomplete plans
- # Resume each
- ## Metrics to Track
- ## Support


### ./docs/BADGE_DEPLOY_STATUS.md

- # Netlify Health Badge


### ./docs/DEPLOYMENT.md

- # SR-AIbridge Deployment Guide
- ## SQLite-first Backend with Full Health Monitoring
- ## Architecture Overview
- ## Quick Start (Development)
- ### Backend
- ### Frontend  
- ## Health Monitoring Endpoints
- ### Basic Health Check
- ### Full Health Check
- ### Self-Heal
- ### System Metrics
- ## Production Deployment
- ### Render (Backend)
- #### Scaling to PostgreSQL (Optional)
- ### Netlify (Frontend)
- ## Health Monitoring Features
- ### SystemSelfTest Component
- ### Database Health Scoring
- ## Self-Healing Capabilities
- ## Environment Configuration
- ### Development (.env)
- ### Production (Render)
- ## API Error Handling
- ## Monitoring and Observability
- ### Health Check Endpoints
- ### Logging
- ### Alerts
- ## Security
- ### CORS Configuration
- ### Headers
- ### Database
- ## Troubleshooting
- ### Backend Won't Start
- ### Health Checks Failing
- ### Frontend Can't Connect
- ### Database Issues
- ## Performance Tuning
- ### SQLite Optimization
- ### API Performance
- ### Frontend Optimization
- ## Auto-Deploy & Continuous Monitoring (v1.6.7)
- ### Bridge Auto-Deploy Workflow
- # Automatic triggers:
- # Manual trigger:
- ### Live Sync Badge
- ### Package & Registry Configuration (v1.6.7)
- ### Deployment Secrets Required
- ## Support


### ./docs/engine_smoke_test.md

- # Engine Smoke Test Guide
- ## Overview
- ## Prerequisites
- ## Engine Tests
- ### 1. Math Engine (CalculusCore) - POST /engines/math/prove
- ### 2. Quantum Engine (QHelmSingularity) - POST /engines/quantum/collapse
- ### 3. Science Engine (AuroraForge) - POST /engines/science/experiment
- ### 4. History Engine (ChronicleLoom) - POST /engines/history/weave
- ### 5. Language Engine (ScrollTongue) - POST /engines/language/interpret
- ### 6. Business Engine (CommerceForge) - POST /engines/business/forge
- ## Running All Tests
- ## Expected Behavior
- ### Success Indicators
- ### Health Check Integration
- ## Troubleshooting
- ### Common Issues
- ### Debugging Commands
- ## Performance Benchmarks
- ### Expected Response Times
- ### Resource Usage
- ## Integration Notes
- ### CI/CD Integration
- # Example GitHub Actions step
- ### Monitoring Integration
- ## Security Considerations
- ## Next Steps


### ./docs/REPO_STUDY_README.md

- # 🔬 Repository Study - Using Parser, Blueprint, and Truth Engines
- ## Quick Start
- # Option 1: Use the quick launcher (recommended)
- # Option 2: Run directly with Python
- ## What It Does
- ## Output
- ## Learn More
- ## Why This Matters


### ./docs/GIT_SOVEREIGN_AGENT_GUIDE.md

- # 🌌 Git Sovereign Agent - Complete Integration Guide
- ## Overview
- ## 🎯 Mission Parameters
- ### Primary Objective
- ### 🔓 Access Grants
- ### 🎖️ Agent Privileges
- ## 🏗️ Architecture
- ### Module Structure
- ### Integration Points
- ## 🚀 Quick Start
- ### 1. Import the Git Sovereign Agent
- ### 2. Initialize Sovereign Manifest
- # Create manifest with cosmic sovereignty
- # Validate authority for any operation
- ### 3. Use SDTF Token Minting
- # Initialize SDTF integration
- # Mint ephemeral token with sovereign signature
- # Validate token
- # Mint credentials for all providers
- # Returns: {"github": {...}, "netlify": {...}, "render": {...}}
- ### 4. Use BRH Container Orchestration
- # Initialize BRH integration
- # Deploy container with sovereign authority
- # Perform autonomous healing
- # Spawn reality stream (new branch)
- ### 5. Use HXO Nexus Harmonic Resonance
- # Initialize HXO integration
- # Resonate all 21 engines in perfect harmony
- # Quantum entangle two engines
- # Orchestrate all engines
- ### 6. Use Autonomous Operations
- # Initialize autonomous operations
- # Make autonomous decision
- # Optimize system
- # Alter reality
- # Heal system
- # Evolve architecture
- # Create perfect version
- ## 🔧 GitHub Actions Integration
- ### Trigger Sovereign Operations
- # Manual trigger with specific operation
- # Available operations:
- # - autonomous_optimization
- # - reality_alteration
- # - engine_resonance
- # - system_healing
- # - perfect_version_creation
- ### Automated Daily Operations
- ### Branch-Based Triggers
- ## 📊 Status and Monitoring
- ### Get Integration Status
- # Manifest status
- # SDTF status
- # BRH status
- # HXO status
- # Autonomy status
- ### Generate Full Report
- ## 🌟 Capabilities
- ### SDTF Capabilities
- ### BRH Capabilities
- ### HXO Nexus Capabilities
- ### Autonomous Operation Capabilities
- ## 🎖️ Authority Levels
- ### Decision Matrix
- ## 🧪 Testing
- ### Run Tests
- # Install test dependencies
- # Run all Git Sovereign Agent tests
- # Run specific test class
- # Run with coverage
- ### Test Coverage
- ## 📚 Engine Access
- ## 🔒 Security
- ### Cryptographic Signatures
- ### Sovereign Seal
- ### Authority Validation
- # All operations authorized under cosmic sovereignty
- ## 🌌 Lore
- ## 🚀 Next Steps
- ## 📖 Related Documentation


### ./docs/CHIMERA_FAILSAFE_PROTOCOL.md

- # Chimera Failsafe Protocol
- ## Fallback and Recovery System
- ## Overview
- ## Failsafe Principles
- ## Failure Mode Matrix
- ## Layer 1: Simulation Failsafes
- ### Timeout Protection
- ### Exception Handling
- ## Layer 2: Healing Failsafes
- ### Infinite Loop Prevention
- ### Healing Failure Handling
- ## Layer 3: Certification Failsafes
- ### Automatic Rollback
- ### Verification Chain Bypass
- # Emergency deployment (admiral-only)
- ## Layer 4: Deployment Failsafes
- ### Platform API Retry Logic
- ### Cross-Platform Fallback
- ## Layer 5: Post-Deploy Failsafes
- ### Cascade Monitoring
- ### Drift Detection
- ## Genesis Bus Failsafes
- ### Event Publishing Retry
- ## Rollback Procedures
- ### Manual Rollback
- # Via CLI
- # Via API
- ### Automatic Rollback
- ## Emergency Procedures
- ### Complete System Shutdown
- # Disable Chimera
- # Stop all deployments
- # Verify stopped
- ### Force Rollback (Nuclear Option)
- # Skip all validations
- ## Monitoring & Alerting
- ### Health Check Endpoints
- # Chimera status
- # Genesis Bus status
- # Cascade status
- ### Alert Conditions
- ## Recovery Playbook
- ### Scenario 1: Simulation Keeps Timing Out
- # Increase timeout
- # Retry
- ### Scenario 2: Healing Loop Detected
- # Deploy without healing
- ### Scenario 3: All Platforms Failing
- # Check platform health
- ### Scenario 4: Genesis Bus Failure
- # Events will queue locally
- # Genesis Bus will retry automatically
- # Monitor queue size:
- ## Performance SLAs
- ## Testing Failsafes
- # Test simulation timeout
- # Test healing failure
- # Test certification failure
- # (Inject critical issue into config)
- # Test rollback
- ## Future Enhancements
- ## Related Documentation


### ./docs/ENVSYNC_SEED_MANIFEST.md

- # EnvSync Seed Manifest - Genesis v2.0.1a
- ## Overview
- ## Purpose
- ## Location
- ## Format
- # ==========================================================================================
- # EnvSync Seed Manifest — SR-AIbridge Core Environments
- # ==========================================================================================
- # Version: Genesis v2.0.1a
- # Purpose: Enables Render <-> Netlify variable synchronization
- # AutoPropagate: true
- # SyncTarget: render, netlify
- # Canonical: true
- # ManagedBy: Genesis Orchestration Layer
- # ==========================================================================================
- # Variables follow standard .env format
- # ... more variables
- ## Metadata Fields
- ## Variables Included
- ## Usage
- ### Loading the Manifest
- # In .env or platform environment
- ### Triggering Sync
- # Sync to both platforms
- # Sync to specific platform
- ### Automatic Sync
- ## Genesis Integration
- ### Genesis Events
- ## Extending the Manifest
- # === NEW FEATURE CONFIGURATION ===
- # Enables experimental feature X
- # Feature X timeout in seconds
- ## Security Considerations
- ## Troubleshooting
- ### Manifest Not Loading
- ### Variables Not Syncing
- ### Drift Detected
- ## Version History
- ### Genesis v2.0.1a (Current)
- ## Related Documentation


### ./docs/BRIDGE_AUTOFIX_ENGINE.md

- # Bridge Parity Auto-Fix Engine
- ## Overview
- ## Architecture
- ### Components
- ### Data Flow
- ## Features
- ### 1. Autonomous Frontend Stub Generation
- ### 2. Backend Placeholder Documentation
- # AUTO-GEN-BRIDGE v1.7.0 - MODERATE
- # Route: /api/health
- # TODO: Implement this missing backend endpoint
- ### 3. Severity-Based Triage
- ### 4. Confidence Thresholds
- ## CLI Usage
- ### Manual Execution
- # Step 1: Analyze parity
- # Step 2: Auto-fix mismatches
- ### Standalone Auto-Fix
- ## GitHub Actions Integration
- ### Workflow Triggers
- ### Workflow Steps
- ### Artifacts
- ## Report Schema
- ### parity_autofix_report.json
- ## Safeguards
- ### 1. Manual Review Gate
- ### 2. Non-Destructive Backend Stubs
- ### 3. Audit Trail
- ### 4. Disable Mechanism
- ## Integration Guide
- ### Frontend Integration
- ### Backend Integration
- # From auto-generated stub
- ## Testing
- ### Validation Checks
- ### Manual Testing
- # Run full cycle
- # Verify stubs were created
- # Check report
- ## Post-Merge Instructions
- ## Impact
- ## Troubleshooting
- ### Issue: No stubs generated
- ### Issue: Stubs have incorrect method
- ### Issue: Too many stubs generated
- ### Issue: Backend stubs not created
- ## Version History
- ## License


### ./docs/BRIDGE_DEPLOY_GUIDE.md

- # 🌉 Bridge Deployment Infrastructure Guide
- ## Overview
- ## Architecture
- ## Components
- ### 1. Netlify Configuration (`bridge-frontend/netlify.toml`)
- ### 2. GitHub Actions Workflow (`.github/workflows/bridge-deploy.yml`)
- ### 3. Runtime Exporter (`bridge_backend/forge/export_runtime.py`)
- ### 4. Dominion Seal (`assets/dominion-seal.svg`)
- ## Setup Instructions
- ### Step 1: Configure GitHub Secrets
- # Navigate to: Settings → Secrets and variables → Actions → New repository secret
- ### Step 2: Update README Badge
- ### Step 3: Enable Workflow
- ### Step 4: Deploy
- # Make a commit to main branch
- # Or trigger manually in GitHub Actions UI
- ## Deployment Flow
- ## Status Badges
- ### Forge Dominion Badge
- ### Bridge Deploy Badge
- ### Bridge Frontend Badge
- ## Troubleshooting
- ### Workflow Fails at "Export Forge Runtime"
- ### Netlify Deployment Fails
- ### Runtime Manifest Not Generated
- ### Badge Not Updating
- ## Advanced Configuration
- ### Custom Webhook Endpoint
- ### Multiple Environments
- ### Custom Build Command
- ## Security Considerations
- ## Maintenance
- ### Updating Forge ID
- ### Version Updates
- ## Support
- ## References


### ./docs/FRONTEND_POSTGRES_READINESS.md

- # Frontend PostgreSQL Readiness Audit Report
- ## Executive Summary
- ## Audit Results by Category
- ### 1. Code Quality & Linting ✅ PASSED
- ### 2. Configuration & API URLs ✅ PASSED
- ### 3. API Client Architecture ✅ PASSED
- ### 4. Data Structure Handling ✅ PASSED
- ### 5. Error Handling & User Experience ✅ PASSED
- ### 6. Database-Agnostic UI Patterns ✅ PASSED
- ### 7. Component-Specific Analysis
- #### Core Components ✅
- #### Specialized Components ✅
- #### UI Components ✅
- ## Recommendations for PostgreSQL Migration
- ### Pre-Migration
- ### During Migration
- ### Post-Migration
- ## Testing Strategy
- ### Recommended Tests
- ### Manual Testing Checklist
- ## Architecture Strengths
- ### What Makes This Frontend PostgreSQL-Ready
- ## Summary of Changes Made
- ### Files Modified (6 files)
- ### Impact
- ## Conclusion


### ./docs/ARIE_README.md

- # ARIE v1.9.6m - Autonomous Repository Integrity Engine
- ## Overview
- ## Key Features
- ## Quick Start
- # Scan repository
- # Apply safe fixes
- # View report
- ## What ARIE Detects
- ## Architecture
- ## Documentation
- ## CLI Commands
- ## Policy Types
- ## API Endpoints
- ## Genesis Integration
- ## Configuration
- ## Test Coverage
- ## CI/CD Integration
- ### GitHub Actions
- ### Render
- ## RBAC Permissions
- ## Rollback
- ## Production Status
- ## Version


### ./docs/AUTONOMY_QUICK_REF.md

- # Autonomy Decision Layer v1.9.6s - Quick Reference
- ## What Is It?
- ## Key Features
- ## Quick Commands
- ### CLI
- # Check status
- # Submit incident
- # Control circuit
- ### API
- # Get status
- # Submit incident
- # Trigger specific action
- ## Incident Kinds → Actions
- ## Configuration
- # Enable/disable
- # Safety limits
- # Integration
- ## Decision Flow
- ## Safety Guardrails
- ## Genesis Events
- ## Files
- ## Permissions
- ## GitHub Actions Integration
- ## Render Integration
- ## Common Issues
- ## See Also


### ./docs/HERITAGE_TEST_PRESETS.md

- # Heritage Test Presets Guide
- ## Overview
- ## Running Demos
- ### From UI
- ### From API
- # Shakedown
- # MAS Healing
- # Federation
- ### From Python
- # Run demos
- ## Demo Details
- ### 1. Shakedown
- ### 2. MAS Healing
- ### 3. Federation
- ## Monitoring
- ### Event Stream
- ### Logs
- ### Metrics
- ## Interpreting Results
- ### Shakedown Success
- ### MAS Healing Success
- ### Federation Success
- ## Troubleshooting
- ### Demo Doesn't Start
- ### No Events in UI
- ### Fault Injection Not Working
- ## Custom Demos
- # bridge_core/heritage/demos/my_demo.py
- # bridge_core/heritage/routes.py
- ## Best Practices
- ## Future Enhancements


### ./docs/TRIAGE_BOOTSTRAP_BANNER_USAGE.md

- # TriageBootstrapBanner Usage Example
- ## Overview
- ## Basic Usage
- ### In a Diagnostics/Health Dashboard Page
- ### In the System Self-Test Page
- ### In a Main Dashboard
- ## Behavior
- ## Checked Triage Types
- ## Styling
- ### Custom Styling
- ## When to Use
- ## Example with Custom Message
- ## API Integration
- ## Testing


### ./docs/UMBRA_LATTICE_OVERVIEW.md

- # Umbra Lattice Memory - Overview
- ## What is Umbra Lattice?
- ## The Problem
- ## The Solution
- ### 1. Graph-First Persistence
- ### 2. Truth-Gated Writes
- ### 3. Causal Maps & Timelines
- ### 4. Neural Changelog Queries
- ### 5. Genesis Integration
- ## Key Features
- ### Capture
- ### Normalize
- ### Certify
- ### Bloom
- ### Visualize
- ## Architecture
- ## Storage
- ### Database Schema
- ## RBAC
- ## How It Learns
- ### Pattern Recognition
- ### Self-Improvement
- ## Integration with Other Engines
- ### Truth Engine
- ### Cascade
- ### ARIE
- ### Chimera
- ### Steward
- ## Result
- ## Quick Start
- ## Schema Reference


### ./docs/CHIMERA_QUICK_START.md

- # Chimera Deployment Quick Start
- ## Quick Integration Guide for v1.9.7c
- ## Prerequisites
- ## Local Testing
- ### 1. Simulate Deployment
- # Test Netlify deployment
- # Test Render deployment
- ### 2. Monitor Status
- ### 3. Verify Configuration
- ## CI/CD Integration
- ### GitHub Actions
- ## Render Integration
- ## Netlify Integration
- ### Build Settings
- ### Optional: Pre-build Validation
- ## API Usage
- ### Start the Backend
- ### Test Endpoints
- # Get status
- # Simulate deployment
- # Deploy with certification
- ## Configuration
- ### Environment Variables
- # Enable/disable Chimera
- # Simulation timeout (seconds)
- # Max healing attempts
- # Genesis mode (required for event publishing)
- ## Monitoring
- ### Real-time Status
- # Watch deployment status
- ### Check Logs
- # View simulation logs
- # View Genesis events
- ## Troubleshooting
- ### Simulation Fails
- # Increase timeout
- # Run with verbose output
- ### Certification Fails
- # Check certification details
- # Deploy without certification (emergency only)
- ### Healing Loop
- # Deploy without healing
- ## Security Notes
- ## Next Steps
- ## Support
- ## Version


### ./docs/KEYLESS_SECURITY.md

- # Keyless Security Architecture
- ## Overview
- ## Security Paradigm Shift
- ### Traditional Approach
- ### Bridge Approach
- ## How It Works
- ### 1. Ephemeral Session Establishment
- # Backend: Generate keys dynamically
- # Creates unique Ed25519 keypair that exists only for session lifetime
- ### 2. Dynamic Key Generation
- # Each session has different keys
- ### 3. No Static Storage
- ## Implementation Details
- ### Frontend (JavaScript)
- ### Backend (Python)
- ## Deployment Validation Changes
- ### Old Approach
- ### New Approach
- ## Security Advantages
- ### 1. Eliminated Key Theft Risk
- ### 2. No Key Rotation
- ### 3. Perfect Forward Secrecy
- ### 4. Quantum Resistance
- ### 5. Zero Maintenance
- ## Validation Results
- ### True Deployment Check
- ### Security Status
- ## Testing
- ### Run Integration Tests
- # Test the keyless authentication system
- ### Expected Output
- ## Migration Guide
- ### For Developers
- # ❌ Loading static keys from disk
- # ✅ Generating ephemeral session
- ### For Security Auditors
- ## Architectural Benefits
- ### Eliminates Entire Attack Classes
- ### Simplifies Operations
- ## Admiral's Insight
- ## Summary


### ./docs/ENV_SYNC_AUTONOMOUS_PIPELINE.md

- # Autonomous Environment Synchronization Pipeline
- ## 🧩 Overview
- ### Key Features
- ## 🚀 Quick Start
- ### Manual Sync
- ### Export Snapshot
- ### Verify Parity
- ## 🛠️ Core Components
- ### 1. EnvSync Engine
- ### 2. EnvRecon Engine
- ### 3. GenesisCtl CLI
- ### 4. Environment Verifier
- ## 📊 GitHub Actions Integration
- ### Workflow: env-sync.yml
- ## 🔐 Security & Permissions
- ### RBAC Integration
- ### Secret Management
- ## 📄 Sync Snapshot Format
- ## 🧾 Genesis Event Flow
- ### Event Topics
- ## 🧪 Testing
- ### Run Tests
- # Test EnvRecon engine
- # Test manual sync (dry-run)
- ### Expected Exit Codes
- ## 📋 Audit Documentation
- ### Auto-Generated Audit Log
- ## 🔧 Configuration
- ### Environment Variables
- ## 🆘 Troubleshooting
- ### Sync Fails with "Not Configured"
- ### Drift Persists After Sync
- ### Variables Not Syncing
- ## 📚 Related Documentation


### ./docs/HXO_OVERVIEW.md

- # HXO Overview — Hypshard-X Orchestrator
- ## What is HXO?
- ### Core Problem
- ### HXO Solution
- ## Architecture
- ### Core Components
- ### Integration Adapters
- ## Content-Addressed Shards (CAS)
- ## Merkle Tree Aggregation
- ## Execution Flow
- ## Resumability
- ## Self-Healing with Autonomy
- # Hot shard detected
- ## Job Kinds (Blueprint Contract)
- ## Configuration
- # Enable/disable
- # Safety/timebox
- # Adaptivity
- # Storage
- # RBAC
- ## Genesis Topics
- ## RBAC (Admiral-Locked)
- ## TDE-X Integration
- # TDE-X stage uses HXO for long-running work
- ## Comparison to Other Approaches
- ## Next Steps


### ./docs/CAPTAIN_AGENT_SEPARATION.md

- # Captain vs Agent Role Separation - Implementation Summary
- ## Overview
- ## Key Changes
- ### 1. Backend Models
- #### Mission Model (`bridge_backend/models.py`)
- #### Agent Model (`bridge_backend/models.py`)
- ### 2. Backend API Endpoints
- #### Mission Routes (`bridge_backend/bridge_core/missions/routes.py`)
- # Get all captain missions
- # Get missions for specific captain
- # Get agent-only jobs
- #### Fleet/Armada Routes (`bridge_backend/bridge_core/fleet/routes.py`)
- # Get captains
- # Get agents
- ### 3. RBAC Permissions
- ### 4. Frontend - MissionLog Component
- ### 5. Frontend - ArmadaMap Component
- ### 6. CSS Styling
- ## Testing
- ### Test Results
- ### Test Coverage
- ## Acceptance Criteria ✅
- ## Future Enhancements
- ## Migration Notes
- ## Files Changed
- ### Backend
- ### Frontend
- ### Tests
- ## Summary


### ./docs/HERITAGE_BRIDGE.md

- # Heritage Bridge Integration Guide
- ## Overview
- ## Architecture
- ### Directory Structure
- ### Event Bus Topics
- ### Integration Points
- #### Truth Engine Hook
- #### Parser Engine Hook
- #### Cascade Hooks
- ## API Endpoints
- ### Heritage Routes
- #### Start Demo
- #### List Demo Modes
- #### WebSocket Stats
- #### Heritage Status
- ## Usage Examples
- ### Subscribe to Events
- ### Publish Events
- ### MAS Adapter Usage
- # Create adapter
- # Handle incoming message
- ### Fault Injection
- # Create fault injector
- # Inject faults
- ### Federation Client
- # Create client
- # Forward task
- # Send heartbeat
- ## Testing
- ## Compatibility
- ## Feature Flags


### ./docs/API_TRIAGE_QUICK_REF.md

- # API Triage Quick Reference
- ## What is API Triage?
- ## Quick Commands
- # Run API triage manually
- # View latest report
- # Trigger GitHub Actions workflow
- ## Exit Codes
- ## Monitored Endpoints
- ## Schema Types
- ## Event Structure
- ## Frontend Component
- ## Environment Variables
- ## Integration Points
- ## Comparison
- ## Files
- ## Common Issues
- ### Schema Validation Failed
- ### No Data in Frontend
- ## Adding New Checks
- ## Documentation


### ./docs/BRIDGE_PARITY_ENGINE.md

- # Bridge Parity Engine with Triage (v1.6.9)
- ## Modes
- ## Triage Levels
- ## Output
- ## Benefits


### ./docs/AUTONOMY_INTEGRATION_DIAGRAM.md

- # Autonomy Engine Integration - System Diagram


### ./docs/UMBRA_OPERATIONS.md

- # Umbra Triage Mesh - Operations Guide
- ## Operating Modes
- ### Intent-Only Mode (Default)
- ### Autonomous Mode
- ## RBAC Enforcement
- ### Role Requirements
- ### Endpoint Permissions
- ## Heal Policies
- ### Standard Policy (Default)
- ### Relaxed Policy
- ### Strict Policy
- ## CLI Operations
- ### Running a Triage Sweep
- # Intent-only mode (generates plans but doesn't execute)
- # With healing enabled
- ### Managing Tickets
- # List all tickets
- # List open tickets only
- # View specific ticket
- # Close a ticket
- # Heal a ticket
- ### Viewing Reports
- # View latest report summary
- # View all reports as JSON
- ## API Operations
- ### Ingest a Signal
- ### Run Triage Sweep
- ### List Tickets
- ### Get Ticket Details
- ### Execute Heal Action
- ## Webhook Configuration
- ### Netlify Webhook
- ### Render Webhook
- ### GitHub Webhook
- ## Rollback Procedures
- ### Automatic Rollback
- ### Manual Rollback
- # Close the failed ticket
- # Review the failed actions
- # If needed, manually revert changes using Chimera/Cascade/Autonomy
- ## Monitoring & Observability
- ### Health Metrics
- ### Genesis Events
- ### Log Files
- ## Troubleshooting
- ### Issue: Webhooks not being ingested
- ### Issue: Heal plans not executing
- ### Issue: Tickets not being correlated
- ### Issue: CI workflow not commenting on PR
- ## Best Practices
- ## Emergency Procedures
- ### Disable Umbra Completely
- # Restart application
- ### Disable Only Healing
- # Restart application or wait for config reload
- ### Clear All Tickets
- # Use CLI or API to close all tickets
- ### Force Genesis Re-registration
- # Restart the application
- # Genesis links will re-register automatically on startup
- ## Performance Tuning
- ### Timeout Adjustment
- # For faster environments
- # For slower environments
- ### Correlation Window
- ### Batch Processing
- ## Integration with Other Systems
- ### Steward
- ### ARIE
- ### EnvRecon
- ### Chimera


### ./docs/BRIDGE_HARMONY_GUIDE.md

- # 🎻 Bridge Harmony & Communication Unification
- ## Overview
- ## The Problem
- ## The Solution
- ### ✅ Auto-Discovery & Registration
- ### ✅ Auto-Wiring Communication
- ### ✅ Harmonic Resonance Monitoring
- ### ✅ Documentation Link Repair
- ## Architecture
- ## Usage
- ### Command-Line Interface
- # Show current bridge harmony status
- # Fix all communication issues (recommended)
- # Individual commands
- ### Python API
- # Create orchestrator
- # Execute full harmony orchestration
- # Or use individual phases
- # Check specific metrics
- ## Discovered Engines
- ### Core Infrastructure (6 Engines)
- ### Super Engines (7 Engines)
- ### Utility & Support (21+ Engines)
- ## Communication Protocols
- ### Genesis Bus Protocol
- ### Umbra Lattice Protocol
- ### Direct Protocol
- ## Metrics & Monitoring
- ### Resonance Percentage
- ### Communication Health
- ### Harmony Status
- ## Integration with Bridge Systems
- ### HXO Nexus Integration
- ### Umbra Lattice Integration
- ### Genesis Federation Bus Integration
- ## Reports
- ### BRIDGE_HARMONY_REPORT.md
- # 🎻 Bridge Harmony & Communication Report
- ## System Overview
- ### Engines by Category
- #### Core Engines (6)
- ## Communication Pathways
- ### Genesis Bus (33)
- ## Troubleshooting
- ### Issue: Broken Links Detected
- ### Issue: Low Resonance (<90%)
- ### Issue: Communication Health <100%
- ## Development
- ### Adding New Engines
- ### Testing
- ## Best Practices
- ## References
- ## Version History


### ./docs/ARIE_TOPICS.md

- # ARIE Genesis Topics Reference
- ## Overview
- ## Subscribed Topics
- ### deploy.platform.success
- ### genesis.heal
- ## Published Topics
- ### arie.audit
- ### arie.fix.intent
- ### arie.fix.applied
- ### arie.fix.rollback
- ### arie.alert
- ### arie.schedule.tick
- ### arie.schedule.summary
- ### arie.schedule.manual
- ## Integration Patterns
- ### Post-Deploy Flow (v1.9.6o)
- ### Autonomous Scheduled Flow (v1.9.6o)
- ### Manual Heal Flow
- ### Failed Certification Flow (v1.9.6o)
- ## Monitoring Examples
- ### Count Findings by Severity
- ### Track Fix Success Rate
- ### Alert on Critical Issues
- ## Event Retention
- ## Testing Events
- # Trigger deploy success
- # Trigger heal request


### ./docs/SELFTEST_HEALING_AUTOTRIGGER.md

- # Self-Test Healing Auto-Trigger
- ## v1.9.7j — Auto-Heal Trigger Logic
- ## Trigger Flow
- ## Healing Strategies
- ### ARIE Strategy
- # Returns: {"strategy": "arie", "action": "config_repaired"}
- ### Chimera Strategy
- # Returns: {"strategy": "chimera", "action": "deployment_repaired"}
- ### Cascade Strategy
- # Returns: {"strategy": "cascade", "action": "system_recovered"}
- ### Generic Strategy
- ## Retry Logic
- ### Configuration
- ### Behavior
- ## Truth Certification
- ### Certification Process
- ### Certification Criteria
- ## Event Topics
- ### selftest.autoheal.trigger
- ### selftest.autoheal.complete
- ## Healing Result Schema
- ## Error Handling
- ### Healing Failure
- ### Disabled Auto-Heal
- ## Integration Examples
- ### Manual Trigger
- ### Genesis Bus Integration
- # Subscribe to autoheal events
- ## Monitoring
- ## Security


### ./docs/BUILD_SECURITY_FIX.md

- # Build Security Fix - Netlify Deployment Resolution
- ## Overview
- ## Problem Statement
- ### Issue 1: Node Engine Mismatch
- ### Issue 2: Secret Scanner Blocking
- ## Solution Architecture
- ### 1. Node Runtime Pinning (netlify.toml)
- ### 2. Secret Scan Configuration
- ### 3. Environment Variable Unification
- ### 4. Config.js Refactoring
- ### 5. Ignore File Strategy
- ## Verification Checklist
- ## Deployment Workflow
- ### Step 1: Merge to Main
- ### Step 2: Trigger Netlify Deploy
- ### Step 3: Monitor Build Log
- ### Step 4: Validate Production
- # Expected: {"status": "healthy", "timestamp": "..."}
- ## How This Aligns with Healer-Net
- ## Long-Term Maintenance
- ### When to Update Node Version
- ### Environment Variable Updates
- ### Secret Scanner Policy
- ## References


### ./docs/ETHICS_GUIDE.md

- # SR-AIbridge — Ethics & Operational Policy
- ## Introduction
- ## Commitments
- ## Allowed Uses
- ## Prohibited Uses
- ## Autonomy & "Stealth" Features
- ## Federation Policy
- ## Data Retention & Deletion
- ## Fault Injection Governance
- ## Compliance & Legal
- ## Reporting & Ethics Escalation
- ## Governance
- ## Final Word


### ./docs/LOC_COUNTER_README.md

- # Lines of Code Counter - Usage Guide
- ## Quick Summary
- ### By Language (excluding dependencies):
- ## Tools Available
- ### 1. Comprehensive LOC Counter (Recommended)
- ### 2. Quick LOC Counter
- ## What's Counted
- ## What's Excluded
- ## Report Structure
- ## Project Composition
- ### Backend (Python)
- ### Frontend (JavaScript/React)
- ### Documentation
- ### Infrastructure
- ## Maintenance
- # Run comprehensive count and save report
- # Quick check
- ## Notes
- ## Last Updated


### ./docs/BRIDGE_HARMONY_QUICK_REF.md

- # 🎻 Bridge Harmony - Quick Reference
- ## What is Bridge Harmony?
- ## Quick Commands
- # Show current status (⚡ fastest check)
- # Fix everything (🔧 recommended)
- # Individual operations
- ## System Status
- ### Perfect Harmony ✅
- ### Good Harmony ✓
- ### Needs Tuning ⚠️
- ## Engine Categories
- ### Core (6 Engines)
- ### Super (7 Engines)
- ### Utility (21 Engines)
- ## Communication Protocols
- ## Python Quick Start
- # One-liner: Full harmony
- # Check status
- ## Common Issues
- ### Broken Documentation Links
- ### Low Engine Resonance
- ### Communication Failures
- ### Complete System Fix
- ## Key Metrics
- ## Reports
- ## Integration Points
- ### HXO Nexus
- ### Umbra Lattice
- ### Genesis Federation Bus
- ## Testing
- # Run harmony tests
- # Run core tests
- ## Philosophy
- ## Next Steps
- ## Documentation


### ./docs/endpoint_test_examples.md

- # Endpoint Test Examples
- ## Example 1: Successful Backend Test
- ## Example 2: Partial Failures
- ## Example 3: JSON Output for CI/CD
- ## Example 4: Backend Not Running
- ## Example 5: Testing Deployed Backend
- ## Example 6: Integration with GitHub Actions
- # .github/workflows/endpoint-test.yml
- ## Example 7: Filtering JSON Results
- ## Example 8: Quick Health Check
- # Quick validation - if this succeeds (exit code 0), backend is healthy
- ## Use Cases
- ## Tips


### ./docs/GITHUB_MINI_BRIDGE_OVERVIEW.md

- # GitHub Mini-Bridge Overview
- ## 🚀 Internal Self-Governance Engine
- ## Architecture
- ### Traditional Bridge vs Mini-Bridge
- ### Advantages
- ## Components
- ### 1. Autonomy Core (`core.py`)
- ### 2. Truth Micro-Certifier (`truth.py`)
- ### 3. Parser Sentinel (`parser.py`)
- ### 4. Blueprint Micro-Forge (`blueprint.py`)
- ### 5. Cascade Mini-Orchestrator (`cascade.py`)
- ## Operational Modes
- ### 1. Online Mode
- ### 2. Offline Mode
- ### 3. Hybrid Mode
- ## Scheduling
- ### Automatic Triggers
- ### Execution Flow
- ### Timing Strategy
- ## Security Model
- ### GitHub Actions Sandbox
- ### RBAC Integration
- ### Safety Mechanisms
- ## Telemetry & Monitoring
- ### Local Reports
- ### Report Structure
- ### Genesis Bus Events
- ## Failure Modes & Recovery
- ### Scenario 1: External Bridge Down
- ### Scenario 2: Parser Error
- ### Scenario 3: Truth Certification Failure
- ### Scenario 4: Configuration Corruption
- ## Performance Characteristics
- ### Resource Usage
- ### Execution Time
- ### Scalability
- ## Integration Points
- ### Genesis Bus
- ### Cascade Engine
- ### Truth Engine
- ## Best Practices
- ### Configuration
- ### Monitoring
- ### Maintenance
- ## Comparison with Full Bridge
- ## Future Enhancements
- ### Planned Features
- ### Experimental
- ## Troubleshooting
- ### Common Issues
- ## See Also


### ./docs/TRIAGE_SYSTEMS.md

- # Triage System Architecture
- ## 1. Legacy Triage Scripts (`bridge_backend/scripts/`)
- ## 2. Federation Triage System (`bridge_backend/tools/triage/`)
- ## Why Both Exist


### ./docs/AUTONOMY_DECISION_LAYER.md

- # Autonomy Decision Layer Architecture
- ## Overview
- ## Architecture
- ### Components
- ## Decision Flow
- ### 1. Event Detection
- ### 2. Decision Making
- ### 3. Action Execution
- ### 4. Certification
- ## Safety Guardrails
- ### Rate Limiting
- ### Cooldown Period
- ### Circuit Breaker
- ### Truth Certification
- ## Event Topics
- ### Subscriptions (Incoming)
- ### Publications (Outgoing)
- ## Engine Integration
- ### Chimera (Config & Deployment)
- ### ARIE (Code Integrity)
- ### EnvRecon (Environment Sync)
- ### Truth (Certification)
- ## Configuration
- ### Environment Variables
- # Core Settings
- # Safety Guardrails
- # Integration
- ## RBAC
- ### Permission Scopes
- ## Deployment
- ### Render (Backend)
- ### GitHub Actions (CI)
- ## Logging & Observability
- ## Future Enhancements


### ./docs/SANCTUM_CASCADE_PROTOCOL.md

- # Sanctum Cascade Protocol
- ## Overview
- ## Architecture
- ## Components
- ### 1. Netlify Guard
- ### 2. Deferred Integrity
- ### 3. Umbra Auto-Heal Linker
- ### 4. Guard Status Routes
- ## Boot Sequence
- ## Monitoring and Health Checks
- ### Quick Health Check
- ### Individual Guard Status
- # Netlify Guard
- # Integrity Guard
- # Umbra Link
- ### Integration with Monitoring Systems
- ## Configuration
- ### Environment Variables
- # Deferred integrity check delay (seconds)
- # Netlify publish path (optional, auto-detected)
- # Netlify auth token (optional, GitHub token used as fallback)
- ### GitHub Actions Integration
- ## Verification
- ### Expected Console Output
- ### CI Workflow Checks
- ## Troubleshooting
- ### Issue: Netlify Guard fails to find publish path
- ### Issue: Token fallback fails
- ### Issue: Umbra link exhausts retries
- ### Issue: Integrity check times out
- ## Rollback
- ## Impact


### ./docs/TELEMETRY.md

- # Runtime Telemetry (v1.8.5)
- ## Overview
- ## Features
- ## Endpoints
- ### GET /api/telemetry
- ## Telemetry Sources
- ### Database Readiness (`db_ready`)
- ### Egress Connectivity (`egress`)
- ### Health Probes (`health`)
- ### Request Metrics
- ## Usage
- ### Accessing Telemetry
- # Check if service is healthy
- ## Configuration
- ## Integration Points
- ## Privacy & Security
- ## Related Documentation


### ./docs/MASTER_ROADMAP.md

- # SR-AIbridge Master Roadmap
- ## Complete Project Overview & Navigation Guide
- ## 🎯 What Is SR-AIbridge?
- ## 🏗️ System Architecture (10,000 Foot View)
- ## 📁 Repository Structure (What Goes Where)
- ## 🎓 Core Concepts You Need to Know
- ### 1. **Agents vs Captains vs Guardians**
- ### 2. **Missions vs Jobs vs Tasks**
- ### 3. **Engines (20 Total)**
- ### 4. **Genesis Linkage**
- ### 5. **Forge Dominion**
- ### 6. **HXO Nexus**
- ### 7. **BRH (Bridge Runtime Handler)**
- ## 🗺️ Navigation Guide: Where to Look for What
- ### "I Want to Understand..."
- ## 🚀 Development Workflow (The Journey)
- ### Phase 1: Setup (15 minutes)
- ### Phase 2: Run Locally (5 minutes)
- ### Phase 3: Explore (30 minutes)
- ### Phase 4: Deploy (30 minutes)
- ### Phase 5: Customize (ongoing)
- ## 📊 Key Metrics & Stats
- ## 🎯 Critical Files (Must-Read for Understanding)
- ### Top 10 Files to Understand the System
- ## 🔄 System States & Lifecycle
- ### System Startup Sequence
- ### Mission Lifecycle
- ### Self-Healing Cycle
- ## 🌟 Unique Features (What Makes This Special)
- ## 🎓 Learning Path (Recommended Order)
- ### For Complete Beginners
- ### For Developers
- ### For DevOps/Deployment
- ## 🚨 Common Pitfalls & How to Avoid Them
- ## 📞 Getting Help
- ## 🎯 Next Steps
- ## 📜 Version & Status


### ./docs/DOCUMENTATION_INDEX.md

- # SR-AIbridge Complete Documentation Index
- ## Your Complete Map to 118,000+ Lines of Documentation
- ## 🎯 Quick Navigation
- ## 📚 Main Documentation
- ### Core Overview Documents
- ## 🚀 Quick Start Guides
- ### Getting Started
- ## 🧠 Engine Documentation
- ### Complete Engine Reference
- ### Six Super Engines
- ## 🔧 Backend Features
- ### Core Backend Systems
- ### Advanced Backend Systems
- ## 🎨 Frontend Components
- ### Dashboard & Panels
- ## 🚀 Deployment & Operations
- ### Deployment Guides
- ### Operations & Monitoring
- ## 🔐 Security & Advanced Features
- ### Security Documentation
- ### Advanced Features
- ## 📖 Quick Reference Cards
- ### Quick Refs (Fast Lookup)
- ## 🧪 Testing & Validation
- ### Testing Documentation
- ## 📊 Implementation & Status Reports
- ### Version Implementation Documents
- #### V1.97 Series (Latest)
- #### V1.96 Series
- ### Status & Verification Reports
- ## 🔧 Configuration & Environment
- ### Configuration Guides
- ## 🔨 Special Projects & Initiatives
- ### Phoenix Protocol
- ### Phase Projects
- ### Special Implementations
- ## 🔗 Integration & Interoperability
- ### Integration Guides
- ## 🛠️ Maintenance & Troubleshooting
- ### Troubleshooting Guides
- ### Maintenance
- ## 📱 Platform-Specific
- ### Netlify
- ### GitHub
- ### Chrome/Playwright
- ## 📚 Additional Resources
- ### Guides & References
- ### Summary Documents
- ## 🔍 How to Use This Index
- ### Finding What You Need
- ## 📊 Documentation Statistics
- ## 🎯 Next Steps
- ## 🤝 Contributing to Documentation


### ./docs/ENVSYNC_PIPELINE_QUICK_REF.md

- # Environment Sync Pipeline - Quick Reference
- ## 🚀 Quick Commands
- ### Sync from Render to GitHub
- ### Export Environment Snapshot
- ### Verify Parity
- ### Run Full Audit
- ## 📊 GitHub Actions
- ## 🔐 Required Secrets
- ## 📄 Files & Locations
- ## 🧾 Genesis Events
- ## 🔍 Exit Codes
- ## 🆘 Common Issues
- ## 🧪 Testing
- # Dry-run mode (no actual changes)
- # Run test suite
- ## 📚 Full Documentation


### ./docs/AUTONOMY_DEPLOYMENT_QUICK_REF.md

- # Autonomy Deployment Integration - Quick Reference
- ## 🚀 The Cherry on Top! 
- ## Quick Start
- ### Enable Genesis Mode
- ### Test Deployment Event
- ### Check Integration Status
- ## Webhook Endpoints
- ## Genesis Bus Topics
- ### Platform Topics
- ### Generic Topics
- ### Autonomy Responses
- ## CLI Usage
- # Netlify deployment
- # Render deployment
- # GitHub workflow
- ## API Usage
- ## Setup Webhooks
- ### Netlify
- ### Render
- ### GitHub
- ## GitHub Actions Integration
- ## Event Flow
- ## Files Added
- ## Files Modified
- ## Monitoring
- # Check webhook status
- # Check autonomy deployment status
- # Check Genesis health
- ## Benefits
- ## Next Steps


### ./docs/FRONTEND-INTEGRATION.md

- # SR-AIbridge v1.9.7 — Frontend Integration Guide
- ## Purpose
- ## Architecture Overview
- ## Setup
- ### Backend Deployment (Render)
- ### Frontend Deployment (Netlify)
- ## Local Development
- # Terminal 1: Backend
- # Terminal 2: Frontend
- ## Environment Variables
- ## Expected Behavior
- ### Health Endpoints
- ### API Routes
- ### Diagnostics
- ## Troubleshooting
- ### CORS Errors
- ### 405 Method Not Allowed or Timeouts
- ### Proxy Loops
- ### Health Check Returns Wrong Host
- ## Post-Deploy Verification
- ### 1. Confirm Backend Health
- ### 2. Confirm Frontend Health
- ### 3. Test Live Proxy
- ### 4. Verify Database Connection
- ### 5. Self-Test Verification (if implemented)
- ### 6. Telemetry Confirmation
- ## Result


### ./docs/ENVIRONMENT_REDUCTION_SUMMARY.md

- # Environment Reduction Summary — v1.9.6k
- ## 🎯 Overview
- ## 🗑️ Removed Variables
- ### External Monitoring & Alerts
- ## ✅ Justification
- ### Why Remove These Variables?
- ### Internal Replacement Systems
- ## 📝 Code Changes
- ### Files Modified
- #### Python Scripts
- #### Environment Files
- #### Version Updates
- ## 🔄 Migration Guide
- ### For Existing Deployments
- ### Monitoring After Migration
- ## 🧪 Validation
- ### Verification Steps
- # 1. Confirm version
- # 2. Run environment audit
- # 3. Check diagnostics are still flowing
- ### Expected Results
- ## 📊 Impact Summary
- ### Metrics
- ### Benefits
- ## 🛡️ Security Improvements
- ### Attack Surface Reduction
- ### Enhanced Privacy
- ## 🚀 Next Steps
- ## 📚 Related Documentation
- ## 🎉 Conclusion


### ./docs/ENDPOINT_TRIAGE_IMPLEMENTATION.md

- # Endpoint Triage System Implementation Summary
- ## What Was Implemented
- ## Files Created
- ### 1. Backend Script
- ### 2. GitHub Actions Workflow
- ### 3. Frontend Component
- ### 4. Documentation
- ## Files Modified
- ### 1. Backend Integration
- ### 2. Diagnostics Timeline
- ### 3. Gitignore
- ## Architecture Integration
- ### Event Flow
- ### Status Calculation
- ### Integration Points
- ## Why Python Instead of Node.js
- ## Usage Examples
- ### Check Endpoints Manually
- ### View Latest Report
- ### Trigger Workflow Manually
- ### Add to Dashboard
- ## Environment Variables
- ## Testing Performed
- ## Symmetry with CI/CD System
- ## Next Steps
- ## Benefits


### ./docs/HXO_SECURITY.md

- # HXO Security — Zero-Trust & Quantum-Entropy Protocol
- ## Security Architecture
- ## Zero-Trust Relay
- ### Principle
- ### Implementation
- # All HXO link calls include signed tokens
- ### Verification Flow
- ### Configuration
- ## Quantum-Entropy Hashing (QEH)
- ### Purpose
- ### Algorithm
- ### Properties
- ### Verification
- ### Configuration
- ## Harmonic Consensus Protocol (HCP)
- ### Overview
- ### Consensus Flow
- ### Validation Rules
- ### Consensus Modes
- ### Failure Handling
- ## RBAC Integration
- ### Permission Model
- ### Protected Operations
- # Admiral-only operations
- # Captain-allowed operations (if HXO_ALLOW_CAPTAIN_VIEW=true)
- ### Configuration
- ## Guardian Fail-Safe
- ### Purpose
- ### Detection Mechanisms
- ### Halt Procedure
- ### Configuration
- ## Audit Trail
- ### Logged Events
- ### Audit Query
- # View recent security events
- ## Threat Model
- ### Threats Mitigated
- ### Residual Risks
- ## Security Best Practices
- ## Compliance


### ./docs/API_TRIAGE_IMPLEMENTATION.md

- # API Triage System Implementation Summary
- ## Overview
- ## Files Created
- ### 1. Backend Script
- ### 2. GitHub Actions Workflow
- ### 3. Frontend Component
- ### 4. Documentation
- ## Files Modified
- ### 1. Backend Integration
- ### 2. Git Ignore
- ## Architecture Integration
- ### Event Flow
- ### Status Calculation
- ### Integration Points
- ## Schema Validation Features
- ### Example Validation
- # Check definition
- # Validates that response has 'agents' field containing a list
- ## Key Differences from Endpoint Triage
- ## End-to-End Behavior
- ### Startup Sequence
- ### CI/CD Automation
- ### Dashboard Display
- ### Diagnostics Timeline Integration
- ## Testing
- ### Manual Testing
- # Test API triage script
- # Check generated report
- ### Expected Output
- ## Configuration
- ### Environment Variables
- ### GitHub Secrets (Required)
- ## Benefits
- ## Success Metrics
- ## Future Enhancements
- ## Related Systems


### ./docs/SCAN_ENGINE_README.md

- # Compliance Scan Engine README
- ## Overview
- ## Features
- ## Policy States
- ## Configuration
- ## How It Works
- ### License Scanning
- ### Counterfeit Detection
- ## CI Integration
- ## API Endpoints
- ## Security
- ## Future Enhancements


### ./docs/NETLIFY_RENDER_ENV_SETUP.md

- # SR-AIBRIDGE: Environment Sync & Security Setup
- ## Render (Backend)
- ## Netlify (Frontend)
- ## Diagnostic Behavior


### ./docs/HXO_GENESIS_TOPICS.md

- # HXO Genesis Topics
- ## Overview
- ## Topic Registry
- ### HXO Topics
- ### HXO Subscriptions
- ## Event Flows
- ### Flow 1: Plan Submission
- ### Flow 2: Shard Execution
- ### Flow 3: Merkle Certification
- ### Flow 4: Auto-Tuning (Autonomy)
- ### Flow 5: Audit Trail
- ## Payload Schemas
- ### `hxo.plan`
- ### `hxo.shard.created`
- ### `hxo.shard.done`
- ### `hxo.shard.failed`
- ### `hxo.autotune.signal`
- ### `hxo.aggregate.certify`
- ### `hxo.audit`
- ## Integration Points
- ### With Autonomy
- ### With Truth
- ### With Blueprint
- ### With Parser
- ### With Federation
- ## Event Ordering Guarantees
- ## Monitoring Queries
- ### Get All Plans
- ### Get Shards for Plan
- ### Get Failed Shards
- ### Get Audit Trail for User
- ## Rate Limiting
- ## Appendix: Full Event Matrix


### ./docs/GENESIS_LINKAGE_GUIDE.md

- # v1.9.7c — Genesis Linkage Implementation Guide (UNIFIED)
- ## Overview
- ### Unified Engines (20 Total)
- ## Architecture
- ### Blueprint Registry
- ### Engine Linkages
- #### 1. Blueprint → TDE-X
- #### 2. Blueprint → Cascade
- #### 3. Blueprint → Truth
- #### 4. Blueprint → Autonomy
- #### 5. Blueprint → Leviathan (NEW)
- #### 6. Blueprint → Super Engines (NEW)
- #### 7. Blueprint → Utility Engines (NEW)
- ## API Endpoints
- ### GET /engines/linked/status
- ### GET /engines/linked/manifest
- ### GET /engines/linked/manifest/{engine_name}
- ### POST /engines/linked/initialize
- ### GET /engines/linked/dependencies/{engine_name}
- ### GET /engines/linked/super-engines/status (NEW)
- ### GET /engines/linked/utility-engines/status (NEW)
- ### GET /engines/linked/leviathan/status (NEW)
- ## Signal Flow
- ## Event Bus Topics
- ## Configuration
- ### Environment Variables
- #### Required
- #### Optional
- ### Deployment Config (unchanged)
- ## Benefits
- ## Testing
- ## Implementation Files
- ### New Files (10)
- ### Modified Files (2)
- ## Usage Examples
- ### Check Linkage Status
- ### Get Complete Manifest
- ### Get Specific Engine Blueprint
- ### Initialize Linkages
- ### Get Engine Dependencies
- ## Future Enhancements


### ./docs/TOKEN_METADATA_VALIDATION.md

- # Token Metadata Validation Security Patch
- ## 🚨 Security Gap Fixed
- ### Issue Identified
- ### Solution Implemented
- ## 📋 Required Metadata Fields
- ## 🔧 Usage
- ### Basic Token Creation (Backward Compatible)
- # Works without metadata (backward compatible)
- ### Secure Token Creation (With Metadata)
- # Create token with complete metadata
- # Validate token
- # Extract metadata from token
- ### Enforced Mode (SOVEREIGN_GIT=true)
- # Enable enforcement
- # This will raise MetadataValidationError
- # This will succeed
- ### Programmatic Enforcement
- # Create forge instance with enforcement enabled
- # Metadata is required for this instance
- ## 🛡️ Security Features
- ### 1. Metadata Validation
- ### 2. Audit Trail
- ### 3. Backward Compatibility
- ### 4. Token Inspection
- # Extract and inspect metadata
- ## 🔍 Validation Rules
- ### Creator Identity
- ### Creation Timestamp
- ### Intended Purpose
- ### Expiration Policy
- ### Access Scope
- ### Audit Trail ID
- ## 📊 Error Handling
- ## 🚀 Activation Guide
- ### Phase 1: Development (Current)
- # Metadata validation available but not enforced
- # Tokens can be created with or without metadata
- # Perfect for testing and gradual adoption
- ### Phase 2: Testing
- # Enable enforcement in test environments
- # Test all token creation paths
- # Verify metadata is properly included
- ### Phase 3: Production Rollout
- # Enable enforcement in production
- # All new tokens must have valid metadata
- # Existing tokens continue to work
- ## 📈 Migration Path
- ## 🧪 Testing
- # Run all metadata validation tests
- # Run demonstration script
- ## 📝 API Reference
- ### `validate_metadata(metadata, require_metadata=True)`
- ### `generate_ephemeral_token(service, ttl=300, metadata=None)`
- ### `validate_ephemeral_token(token, require_metadata=False)`
- ### `get_token_metadata(token)`
- ## 🔒 Security Best Practices
- ## 📞 Support
- ## ✅ Success Metrics


### ./docs/AUTONOMY_OPERATIONS.md

- # Autonomy Operations Guide
- ## Quick Start
- ### Check Status
- # Via CLI
- # Via API
- ### Submit Manual Incident
- # Via CLI
- # Via API
- ### Trigger Specific Action
- # Via API
- ## Circuit Breaker Control
- ### Open Circuit (Disable Auto-Healing)
- # Via CLI
- # Via API
- ### Close Circuit (Re-enable Auto-Healing)
- # Via CLI
- # Via API
- ## Observability
- ### Check Genesis Event History
- ### Monitor Logs
- # On Render
- # Filter for autonomy events
- ## Common Scenarios
- ### Scenario 1: Netlify Preview Keeps Failing
- ### Scenario 2: Environment Drift Detected
- ### Scenario 3: Rate Limit Reached
- ### Scenario 4: Circuit Breaker Tripped
- ## Safety Best Practices
- ### 1. Monitor Genesis Events
- ### 2. Start Conservative
- ### 3. Test in Staging First
- ### 4. Manual Override Available
- ## Troubleshooting
- ### Problem: Incidents Not Being Handled
- # Check if autonomy routes are loaded
- # Check Genesis bus status
- # Manually submit test incident
- ### Problem: Actions Not Executing
- # Check status
- # Try manual trigger
- ### Problem: Truth Certification Failing
- # Check Truth engine status
- # Review Genesis event history for certification failures
- ## Configuration Reference
- ## Support


### ./docs/FIREWALL_HARDENING.md

- # Firewall Hardening Guide
- ## Overview
- ## Architecture
- ### Components
- ### Data Flow
- ## Critical Domains
- ### Package Registries
- ### GitHub Services
- ### Deployment Platforms
- ### Status Pages
- ## Required Network Ports
- ## Trust Chain Configuration
- ### SSL/TLS Certificates
- ### DNS Configuration
- ## Usage
- ### Manual Execution
- # Fetch incidents
- # Analyze findings
- # Review reports
- ### CI/CD Integration
- #### Nightly Intelligence Run
- #### Deploy Failure Gate
- ### Workflow Dispatch
- # Via GitHub UI: Actions → Firewall Intelligence → Run workflow
- # Via GitHub CLI
- ## Firewall Report Schema
- ## Severity Levels
- ## Applying Network Policies
- ### For Kubernetes
- ### For Firewall/Proxy
- # Extract domains
- ### For CI/CD Environments
- ## Troubleshooting
- ### Common Error Signatures
- ### Verification Steps
- ## Security Considerations
- ### Principle of Least Privilege
- ### Audit Trail
- ### Compliance
- ## Integration with Bridge Healers Code
- ## Version History
- ## See Also


### ./docs/GENESIS_V2_0_2_ENVRECON_GUIDE.md

- # Genesis v2.0.2 - EnvRecon Implementation Guide
- ## 🚀 Overview
- ### Key Features
- ## 📦 What's New
- ### Components Added
- ## 🛠️ Installation & Setup
- ### Prerequisites
- # Required Python packages (already in requirements.txt)
- ### Environment Variables
- # GitHub Integration (for HubSync)
- # Render Integration
- # Netlify Integration
- # Optional: Auto-Heal Configuration
- ## 📘 Usage
- ### CLI Commands
- #### 1. Run Environment Audit
- #### 2. Sync Environment Variables
- # Sync to all platforms (runs audit + shows report)
- # Sync to specific platform
- #### 3. Trigger Auto-Healing
- ### API Endpoints
- #### Health Check
- #### Get Reconciliation Report
- #### Run Audit
- #### Sync All Platforms
- #### Trigger Healing
- #### Sync GitHub Secrets
- ### Inspector Panel UI
- #### Features:
- ## 🧠 Architecture
- ### Data Flow
- ## 🧪 Testing
- ### Run Test Suite
- # Run all EnvRecon tests
- ### Expected Output
- ## 🔐 Security Considerations
- ### GitHub Token Permissions
- ### Dry-Run Mode
- ### Secret Masking
- ## 🛡️ Guardian Safety & Recursion Control
- ## 📊 Report Schema
- ## 🔄 Integration with Existing Systems
- ### Genesis Event Bus
- ### TDE-X Deploy Pipeline
- ### EnvSync v2.0.1a
- ## 🎯 Best Practices
- ## 🐛 Troubleshooting
- ### "No report available"
- ### GitHub sync fails
- ### Auto-heal not working
- ### UI returns 404
- ## 📝 Changelog
- ### v2.0.2 (2025-10-11)
- ## 🚀 Next Steps
- ## 📞 Support


### ./docs/endpoint_test_full.md

- # SR-AIbridge Full Endpoint Test
- ## Features
- ## Usage
- ### Basic Usage
- ### Advanced Options
- # Custom timeout
- # JSON output for CI/CD
- # Combine options
- ### Help
- ## Tested Endpoints
- ### Core Endpoints (Required)
- ### Engine Endpoints (Optional)
- ## Exit Codes
- ## Output
- ### Console Output
- ### JSON Output
- ## Integration
- ### CI/CD Pipeline
- ### Monitoring
- # Run every 5 minutes
- ## Comparison with smoke_test_engines.sh
- ## Troubleshooting
- ### All Tests Fail
- ### Some Tests Fail
- ### Connection Timeouts
- ## Requirements
- ## License


### ./docs/AUTONOMY_DEPLOYMENT_ARCHITECTURE.md

- # Autonomy Engine ↔ Deployment Platforms Architecture


### ./docs/REFLEX_LOOP_PROTOCOL.md

- # Reflex Loop Protocol (RLP)
- ## v1.9.7o - Complete Architecture & Lifecycle
- ## 🚀 Overview
- ## 🧠 Core Components
- ### 1. Reflex Engine (`.github/autonomy_node/reflex.py`)
- ### 2. Truth Signer (`.github/autonomy_node/signer.py`)
- ### 3. Merge Verifier (`.github/autonomy_node/verifier.py`)
- ### 4. Offline Queue (`.github/autonomy_node/pending_prs/`)
- ## 🔄 Protocol Lifecycle
- ### Phase 1: Detection & Reporting
- ### Phase 2: Reflex Activation
- ### Phase 3: PR Generation
- ### Phase 4: Truth Certification
- ### Phase 5: Submission
- ### Phase 6: Verification & Merge
- ## 📊 Data Flow
- ## ⚙️ Configuration
- ### Environment Variables
- ### Workflow Schedule
- ## 🔒 Security
- ### Truth Signature
- ### RBAC Validation
- ### Offline Queue Safety
- ## 📈 Monitoring
- ### Logs
- ### Genesis Bus Events
- ## 🧪 Testing
- ## 🔄 Integration Points
- ### Genesis Bus
- ### Truth Engine
- ### Cascade
- ### Steward
- ## 📝 Best Practices
- ## 🚨 Troubleshooting
- ### No PRs Generated
- ### PRs Queued Offline
- ### Signature Validation Fails


### ./docs/SOVEREIGN_AUDIT_QUICK_REF.md

- # 🎯 Sovereign Audit & Repair - Quick Reference
- ## What Was Built
- ### 1. Sovereign Audit Orchestrator
- ### 2. Master Sovereign Audit
- ### 3. Test Suite
- ## Quick Start
- ### Run Full Sovereign Audit
- # Run complete audit with auto-repair
- # Expected output:
- # ✅ SOVEREIGN GIT = TRUE - Full sovereignty confirmed!
- ### Check Audit Status
- # View latest report
- # View detailed audit
- ### Run Tests
- ## Audit Results
- ### Current Status
- ## Reports Generated
- ## Exit Codes
- ## Integration
- ### GitHub Actions Example
- ## Documentation
- ## What the Audit Verifies
- ### ✅ Git Sovereign
- ### ✅ Netlify Sovereign
- ### ✅ Repository Sovereign
- ### ✅ Firewall Sovereignty
- ## Auto-Repair Capability
- ## Commands Summary
- # Run full audit
- # Run without auto-repair
- # Run Git/Netlify/Repo audit only
- # Run tests
- # View reports


### ./docs/BUILD_TRIAGE_ENGINE.md

- # Build Triage & Auto-Repair Engine (v1.7.9)
- ## What it does
- ## Run locally
- ## CI
- ## Diagnostics
- ## Components
- ### 1. `.nvmrc`
- ### 2. `package.json` Updates
- ### 3. `netlify.toml` Enhancements
- ### 4. Build Triage Sentinel (`scripts/build_triage.py`)
- ### 5. Registry Repair Script (`scripts/repair_npm_registry.sh`)
- ### 6. Functions Sanity Check (`netlify/functions/hello.ts`)
- ### 7. CI Preflight Workflow (`.github/workflows/build_preflight.yml`)
- ## Report Format
- ## What This Fixes
- ### Node Engine Mismatch
- ### Missing DevDependencies
- ### npm Registry Failures
- ### Secret Scan False Positives
- ### Monorepo Path Drift
- ## Integration with Healer-Net
- ## Troubleshooting
- ### Triage Script Fails with Python Error
- ### npm ci Still Fails After Mirror Fallback
- ### Functions Not Deploying
- ### Secret Leaks Detected in Report
- ## Local Testing
- # Test triage script
- # Check report
- # Test registry repair
- # Test build
- # Test functions locally
- ## Deployment Checklist
- ## Future Enhancements
- ## Related Documentation
- ## Lore Entry: The Self-Correcting Bridge


### ./docs/FIREWALL_WATCHDOG.md

- # Firewall Watchdog - Copilot Accountability & Audit Logger
- ## Overview
- ## Features
- ## Architecture
- ### Components
- ### Event Flow
- ## Configuration
- ### Monitored Hosts
- ### Allowlist
- ### Log Format
- ## Usage
- ### Automatic Execution
- ### Manual Execution
- # Ensure allowlist exists
- # Run watchdog
- ### Environment Variables
- ## Bridge API Integration
- ## Output Example
- ## Testing
- ## Troubleshooting
- ### No allowlist file
- ### Bridge API unavailable
- ### DNS resolution failures
- ## Files Modified/Created
- ## Version History


### ./docs/OFFLINE_QUEUE_HANDLING.md

- # Offline Queue Handling
- ## Resilient PR Submission in Isolated Environments
- ## Overview
- ## 📁 Queue Structure
- ### Directory Layout
- ### File Naming
- ## 📝 Queue File Format
- ### Structure
- ### Required Fields
- ### Optional Fields
- ## 🔄 Queue Operations
- ### 1. Enqueue (Add to Queue)
- ### 2. Process Queue (Submit Queued PRs)
- ### 3. Cleanup (Remove Old Entries)
- ## 🔍 Queue Monitoring
- ### Status Check
- ### Health Metrics
- ## ⚙️ Configuration
- ### Environment Variables
- ### Queue Limits
- ## 🚨 Error Handling
- ### Common Scenarios
- #### 1. Disk Full
- #### 2. Corrupted Queue File
- #### 3. GitHub API Rate Limited
- ## 🔄 Queue Processing Workflow
- ### Automatic Processing
- ### Manual Processing
- # Check queue status
- # Process queue manually
- # Clean up old entries
- ## 📊 Queue Analytics
- ### Metrics to Track
- ### Sample Query
- ## 🧪 Testing Queue Operations
- ### Test Cases
- ## 📝 Best Practices
- ## 🔒 Security Considerations
- ### Queue File Permissions
- # Ensure queue files are not world-readable
- ### Sensitive Data


### ./docs/SELFTEST_REPORT_SCHEMA.md

- # Self-Test Report Schema
- ## v1.9.7j — JSON Schema for Self-Test Reports
- ## Report Structure
- ### Root Schema
- ## Field Definitions
- ### test_id
- ### summary
- #### summary.engines_total
- #### summary.engines_verified
- #### summary.autoheal_invocations
- #### summary.status
- #### summary.runtime_ms
- ### events
- #### Event Object
- ##### event.engine
- ##### event.action
- ##### event.result
- ##### event.strategy (optional)
- ##### event.attempts (optional)
- ##### event.duration_seconds (optional)
- ##### event.error (optional)
- ### timestamp
- ### error (optional)
- ## Example Reports
- ### Successful Test (No Healing Required)
- ### Test with Auto-Healing
- ### Test with Failed Healing
- ### Complete Test Failure
- ## Report Locations
- ### Individual Reports
- ### Latest Report
- ## Usage
- ### Reading Reports in Python
- # Read latest report
- ### Querying with jq
- # Get test status
- # Count failed engines
- # List all healing events
- ## Validation
- ### Schema Validation Example
- # Validate report


### ./docs/COPILOT_NETWORK_HEALTH.md

- # Bridge Network Diagnostics v1.7.2
- ## Run Locally
- ## Outputs
- ## Indicators
- ## Why It Matters
- ## Tested Domains
- ## Workflow Automation
- ## Report Schema
- ## Integration with Other Tools


### ./docs/UMBRA_LATTICE_SCHEMA.md

- # Umbra Lattice Memory - Schema Reference
- ## Graph Schema
- ### Node Types
- #### `engine`
- #### `change`
- #### `deploy`
- #### `heal`
- #### `drift`
- #### `var`
- #### `commit`
- #### `cert`
- #### `role`
- ### Edge Types
- #### `caused_by`
- #### `fixes`
- #### `certified_by`
- #### `approved_by`
- #### `emitted`
- #### `touches`
- #### `supersedes`
- ## Event Normalization Rules
- ### Deploy Events
- ### Drift Events
- ### Heal Events
- ### Change Events
- ### Certification Events
- ## Query Patterns
- ### Find All Deploys in Last 7 Days
- ### Find All Fixes for a Drift
- ### Find What Caused a Deploy
- ### Find All Certified Actions
- # Get all certification edges
- # Extract certified node IDs
- ## Time Windows
- # API
- # CLI
- ## Snapshot Format
- ## Best Practices
- ### Node IDs
- ### Edge Attribution
- ### Certification
- ### Snapshots


### ./docs/DIAGNOSTICS_FEDERATION.md

- # Diagnostics Federation (v1.6.8)
- ## Components
- ## Environment Variables
- ## Security
- ## Test Commands


### ./docs/ARIE_SECURITY.md

- # ARIE Security Guide
- ## Security Model
- ## RBAC Capabilities
- ### arie:scan
- # Check capability
- ### arie:fix
- # Requires admiral role
- ### arie:rollback
- ### arie:configure
- ## Audit Trail
- ### Patch Journal
- ### Genesis Events
- ## Truth Engine Certification
- ### Certification Process
- ### Certification Failure
- ### Bypass Protection
- ## Policy-Based Security
- ### Policy Risk Levels
- ### Policy Enforcement
- ## Restricted Operations
- ### File System Access
- ### Git Operations
- ## Secrets Protection
- ### Environment Variables
- ### Credentials
- ## Network Security
- ## Monitoring and Alerts
- ### Security Events to Monitor
- ## Incident Response
- ### Suspected Unauthorized Changes
- ## Compliance
- ### SOC 2 / ISO 27001
- ### GDPR
- ### Security Certifications
- ## Best Practices
- ## Security Checklist


### ./docs/CHIMERA_ARCHITECTURE.md

- # Chimera Deployment Engine — Architecture
- ## Layer-by-Layer Flow and Data Diagram
- ## System Architecture Overview
- ## Data Flow Diagram
- ### 1. Deployment Initiation
- ### 2. Simulation Phase
- ### 3. Healing Phase (Conditional)
- ### 4. Certification Phase
- ### 5. Deployment Phase
- ### 6. Verification Phase
- ## Component Interaction Matrix
- ## State Machine
- ## File Structure
- ## Genesis Event Topics
- ## Performance Metrics
- ## Security Boundaries
- ## Failure Modes & Mitigation
- ## Integration Points
- ### Render
- ### Netlify
- ### GitHub Actions
- ## Future Enhancements


### ./docs/ARIE_OPERATIONS.md

- # ARIE Operations Guide
- ## Installation and Setup
- ### Prerequisites
- ### Enable ARIE
- ### Verify Installation
- ## CLI Usage
- ### ariectl - ARIE Command Line Interface
- #### Scan Repository
- #### Apply Fixes
- #### Rollback Changes
- #### View Reports
- ## API Usage
- ### Run Scan
- ### Apply Fixes
- ### Get Last Report
- ### Rollback Patch
- ### Get Configuration
- ### Update Configuration
- ## CI/CD Integration
- ### GitHub Actions
- ### Render Deploy Hook
- ### Manual CI Script
- # Read-only check
- # With auto-fix (set env vars first)
- ## Rollback Procedures
- ### List Available Patches
- ### Inspect Patch Details
- ### Rollback Steps
- ### Emergency Rollback
- # Revert specific files
- # Or revert entire commit
- ## Policy Selection Guide
- ### When to use LINT_ONLY
- ### When to use SAFE_EDIT
- ### When to use REFACTOR
- ### When to use ARCHIVE
- ## Troubleshooting
- ### ARIE not finding issues
- ### Fixes not applying
- # Make sure to NOT use --dry-run flag
- ### Rollback failing
- ### Permission denied
- ### Certification failures
- ## Monitoring and Observability
- ### Genesis Events
- ### Patch Journal
- # Count patches
- # Recent patches
- # Patch sizes
- ### Health Checks
- # Run scan and check exit code
- # Check for critical issues
- ## Best Practices


### ./docs/CHIMERA_ORACLE.md

- # Chimera Oracle
- ## Overview
- ## Architecture
- ## Features
- ### 1. Environment Audit
- ### 2. Build Simulation (Leviathan)
- ### 3. Configuration Synthesis (Hydra v2)
- ### 4. Truth Certification
- ### 5. Deploy Execution with Fallback
- ## Usage
- ### CLI
- # Predictive deployment
- ### API
- # Execute predictive deployment
- ### Python
- ## Decision Matrix
- ## Genesis Events
- ## RBAC
- ## Configuration


### ./docs/UNIFIED_HEALTH_TIMELINE.md

- # Unified Health Timeline - Operation Synchrony
- ## Overview
- ## Architecture
- ### Components
- ## Event Types
- ## Status Levels
- ## Usage
- ### Manual Timeline Generation
- ### API Endpoint
- ### Frontend Integration
- ### Automated Workflow
- ## Event Flow
- ## Integration Points
- ## Configuration
- ### Required Files
- ### .gitignore
- ## Troubleshooting
- ### Timeline Not Building
- ### API Endpoint Returns Empty Timeline
- ### Frontend Not Showing Events
- ### Workflow Not Triggering
- ## Security Considerations
- ## Future Enhancements


### ./docs/ARIE_OVERVIEW.md

- # ARIE Overview - Autonomous Repository Integrity Engine
- ## Introduction
- ## Architecture
- ### Core Pipeline
- ### Components
- #### 1. Core Engine (`bridge_backend/engines/arie/core.py`)
- #### 2. Models (`bridge_backend/engines/arie/models.py`)
- #### 3. Routes (`bridge_backend/engines/arie/routes.py`)
- #### 4. Genesis Integration
- #### 5. Permission Integration
- #### 6. Truth Engine Integration
- #### 7. Cascade Integration
- #### 8. Blueprint Integration
- ## Policy Types
- ### LINT_ONLY
- ### SAFE_EDIT
- ### REFACTOR
- ### ARCHIVE
- ## Data Flow
- ## Rollback Journal
- ## Configuration
- ## Integration Points
- ### With Parcel Engine
- ### With Genesis
- ### With Truth Engine
- ### With Permission Engine
- ### With Cascade
- ### With Blueprint
- ## Best Practices
- ## Monitoring


### ./docs/REPO_STUDY_GUIDE.md

- # Repository Study Guide - Using Parser, Blueprint, and Truth Engines
- ## Overview
- ## The Three Engines
- ### 🔍 Parser Engine
- ### 📋 Blueprint Engine  
- ### ✅ Truth Engine
- ## Study Script Usage
- ### Prerequisites
- # Install dependencies
- ### Running the Study
- # Execute the comprehensive repository study
- ### What the Script Does
- #### Phase 1: Parser Engine - Documentation Ingestion
- #### Phase 2: Blueprint Engine - Analysis Planning
- #### Phase 3: Truth Engine - Fact Certification
- ### Output
- ## Example Output
- ## Understanding the Integration
- ### How the Three Engines Work Together
- ### Data Flow
- ### Use Cases
- ## Advanced Usage
- ### Custom Analysis
- # Add custom documents to ingest
- # Create custom analysis brief
- # Define custom facts to certify
- ### Querying Results
- # Search for specific content
- # List chunks by tag
- # Get specific chunk with lineage
- ### Analyzing Blueprints
- # Generate analysis plan
- # Inspect task dependencies
- ### Validating Truths
- # Get all certified truths
- ## Architecture Benefits
- ### Why These Three Engines?
- ### Event-Driven Integration
- ## Next Steps
- ## References
- ## Support


### ./docs/NAVIGATION_INDEX.md

- # SR-AIbridge Navigation Index
- ## Your Complete Guide to 118,000+ Lines of Documentation
- ## 🆕 NEW: Enhanced Documentation System
- ## 🎯 Choose Your Path
- ### 🚀 "I Want to Get Started Quickly"
- ### 📖 "I Want to Understand Everything"
- ### 🔨 "I Want to Build It From Scratch"
- ### 🔍 "I'm Looking for Something Specific"
- ## 📚 Documentation Structure
- ## 🎓 Learning Paths by Role
- ### For Complete Beginners (No Prior Knowledge)
- ### For Developers (Familiar with Python/Node.js)
- ### For Architects/Technical Leads
- ### For DevOps/Platform Engineers
- ## 🔍 Quick Find Guide
- ### Learn About Features
- ### Find Files
- ### Solve Problems
- ### Understand Architecture
- ## 📊 Documentation Stats
- ## 🎯 Documentation Goals Achieved
- ## 🆘 Still Need Help?
- ## 🎉 Ready to Begin?
- ## 📑 All Documentation Files
- ### Core Documentation Suite (6 Files)
- ### Main Documentation
- ### Feature Guides (100+ Files)


### ./docs/POSTGRES_MIGRATION.md

- # PostgreSQL Migration Guide for SR-AIbridge
- ## Overview
- ## Quick Start
- ### 1. Create PostgreSQL Database on Render
- ### 2. Initialize PostgreSQL Schema
- # Using the DATABASE_URL from Render
- ### 3. Update Environment Variables
- # Change from SQLite
- ### 4. Deploy and Verify
- # Redeploy your service (Render will auto-deploy on git push)
- # Verify connection
- ## Schema Details
- ### Tables Created
- #### Core Tables
- #### Partitioned Tables (Monthly)
- #### Supporting Tables
- #### Views
- ### Automatic Features
- ## Monthly Maintenance
- ### Automated Maintenance (Recommended)
- ### Manual Maintenance
- ## Secure Data Relay Protocol
- ### Overview
- ### Setup
- # SMTP Configuration (Gmail with App Password)
- ### Usage in Code
- # Before deleting data
- # Then perform deletion
- ### Role-Based Retention
- ### Verify Archives
- ## Migration from SQLite
- ### Export Existing Data
- # Export SQLite data
- # Or use Python script
- ### Import to PostgreSQL
- # After running init.sql, import data
- # Note: You may need to adjust column mappings
- # For simple data migration
- ## Performance Tuning
- ### Connection Pooling
- # In bridge_backend/bridge_core/db/db_manager.py
- ### Monitoring Queries
- ### Index Analysis
- ## Troubleshooting
- ### Connection Refused
- ### Permission Denied
- ### Extension Not Available
- ### Partition Not Found
- ## Backup and Recovery
- ### Automated Backups (Render)
- ### Manual Backup
- # Full database dump
- # Schema only
- # Data only
- ### Restore
- # Restore full backup
- # Restore specific table
- ## Next Steps
- ## Support


### ./docs/NETLIFY_GUARD_OVERVIEW.md

- # Netlify Guard Overview
- ## What It Does
- ## Functions
- ### `validate_publish_path()`
- # Returns path and sets NETLIFY_PUBLISH_PATH env var
- ### `require_netlify_token(get_github_token)`
- ## Default Publish Paths
- ## Token Fallback Mechanism
- ### Tier 1: Netlify Token
- ### Tier 2: GitHub Token
- ## Integration
- ### In Application Boot (main.py)
- # Validate publish path
- # Ensure token is available
- ### In GitHub Actions
- ## Environment Variables
- ### Input Variables
- ### Output Variables
- ## Error Handling
- ### Missing Publish Path
- ### Missing Tokens
- ## Best Practices
- ## Testing
- ### Test Publish Path Validation
- # Test with existing path
- # Test with missing path (creates public/)
- ### Test Token Fallback
- # Test with Netlify token
- # Test with GitHub token fallback


### ./docs/ANCHORHOLD_QUICK_REF.md

- # Anchorhold Protocol — Quick Reference
- ## Version Info
- ## Key Features
- ### 1. Dynamic Port Binding
- ### 2. Schema Auto-Sync
- ### 3. Heartbeat System
- # 5-minute keepalive ping
- ### 4. CORS Config
- ## Quick Commands
- ### Local Testing
- # Start server
- # Test endpoints
- # Test CORS
- ### Validation
- # Syntax check
- # Import test
- # Heartbeat test
- ## API Endpoints
- ### Root
- ### Version
- ## Environment Variables
- ### Required
- ### Optional
- ## Files Changed
- ## Troubleshooting
- ### Port issues
- ### CORS errors
- ### Heartbeat fails
- ### Schema sync fails
- ## Deployment
- ### Render
- ### Netlify


### ./docs/HXO_DEPLOY_GUIDE.md

- # HXO Deployment Guide — Render/Netlify/GitHub
- ## Overview
- ## Prerequisites
- ### Required Secrets
- # Core
- # Database
- # HXO Configuration
- ## Render Deployment
- ### 1. Backend Service
- # render.yaml
- # HXO automatically handles this
- # No manual intervention needed
- # Plans > 30 min are automatically sharded
- ### 2. Database Service
- # render.yaml (continued)
- # Render will auto-run migrations via start command
- # Or manually trigger:
- ## Netlify Deployment
- ### Frontend Configuration
- # In Netlify dashboard, add:
- ### Deploy Trigger
- # Enable deploy hooks
- # HXO will auto-trigger on successful backend deploy
- ## GitHub Actions Integration
- ### CI/CD Workflow
- ### Required Secrets
- ## Zero-Downtime Deployment
- ### Strategy
- ### Blue-Green Setup
- # render.yaml
- # 1. Deploy to Green (inactive)
- # 2. Wait for HXO health check
- # 3. Verify federation links
- # 4. Switch traffic
- # Update DNS/load balancer to Green
- # 5. Drain Blue
- ### Rolling Update
- # 1. Trigger deploy
- # 2. HXO automatically:
- #    - Completes active plans
- #    - Checkpoints state
- #    - Gracefully shuts down
- #    - New version starts
- #    - Rehydrates incomplete plans
- ## Schema Migrations
- ### Before Deployment
- # 1. Generate migration
- # 2. Review migration
- # 3. Test locally
- # 4. Commit migration
- ### During Deployment
- # HXO automatically:
- # 1. Detects schema version mismatch
- # 2. Waits for active plans to complete
- # 3. Applies migration
- # 4. Resumes operations
- # If migration takes > 5 minutes, increase timeout
- # Or run migration separately before deploy
- ## Post-Deployment Verification
- ### 1. Health Checks
- # Overall status
- # HXO specific
- # Engine federation
- ### 2. Run ARIE Audit
- ### 3. Verify Metrics
- # Genesis Bus
- # HXO telemetry
- ### 4. Test Plan Submission
- ## Monitoring
- ### Render Metrics
- # render.yaml
- ### Custom Alerts
- # Subscribe to alerts
- ## Rollback Procedure
- ### Quick Rollback
- ### HXO-Aware Rollback
- # 1. Get rollback points
- # 2. Trigger rollback
- # 3. Wait for completion
- ## Performance Optimization
- ### Render-Specific
- # Use standard+ plan for better CPU
- # Enable persistent disk for SQLite checkpoints
- # Use same region for DB and web service
- # In render.yaml:
- ### HXO Tuning
- # Production settings
- # For large deploys
- ## Security Hardening
- ### Production Checklist
- ### Secret Rotation
- # 1. Generate new secret
- # 2. Update in Render dashboard
- # Settings → Environment → SECRET_KEY
- # 3. Trigger redeploy
- # 4. Verify
- ## Troubleshooting Deployments
- ### Build Timeout
- # HXO automatically shards long builds
- # No action needed
- # To verify sharding is working:
- ### Database Connection Errors
- # Check DATABASE_URL format
- # Should be: postgresql+asyncpg://...
- # Test connection
- ### Genesis Bus Not Starting
- # Ensure enabled
- # Check logs
- ## Cost Optimization
- ### Render Costs
- ### HXO Optimizations
- # Reduce shard count to save CPU
- # Reduce TERC to save memory
- # Disable predictive features in low-traffic environments
- ## Deployment Checklist


### ./docs/SANCTUM_OVERVIEW.md

- # Sanctum Overview
- ## 🧭 Sanctum - Predictive Deployment Simulation Layer
- ### Purpose
- ### Architecture
- ### Features
- #### 1. Configuration Validation
- #### 2. Build Health Assessment
- #### 3. Route Integrity
- ### Integration Points
- #### Genesis Bus Events
- # Success
- # Failure
- #### Truth Certification
- #### Forge Auto-Repair
- ### Usage
- #### Programmatic
- #### CLI
- #### GitHub Actions
- ### Configuration
- # Enable/disable Sanctum
- # Genesis bus integration
- ### Output Example
- ### Error Detection
- ### Best Practices
- ### Troubleshooting
- ### Related


### ./docs/AUTONOMY_PR_VERIFICATION.md

- # Autonomy PR Verification
- ## Truth Signing + Merge Logic
- ## Overview
- ## 🔐 Truth Signature System
- ### Signature Generation
- ### Signature Verification
- ## 🛡️ RBAC Authorization
- ### Role Hierarchy
- ### RBAC Verification Flow
- ### Environment Variables
- ## ✅ Merge Readiness Checks
- ### Pre-Merge Validation
- ### Merge Decision Matrix
- ## 🔄 Verification Lifecycle
- ### 1. PR Creation
- ### 2. PR Submission
- ### 3. Merge Verification
- ## 🔍 Audit Trail
- ### Logged Events
- ### Log Format
- ## 🚨 Security Considerations
- ### Signature Tampering
- ### RBAC Bypass
- ### Truth Engine Compromise
- ## 📊 Verification Metrics
- ### Success Indicators
- ### Monitoring Queries
- # Check recent verification failures
- # Audit RBAC decisions
- # Review Truth certifications
- ## 🧪 Testing Verification
- ### Unit Tests
- ## 📝 Best Practices


### ./docs/SOVEREIGN_AUDIT_GUIDE.md

- # 🔍 Sovereign Audit & Repair System
- ## Overview
- ## Features
- ### 🔐 Git Sovereign Audit
- ### 🌐 Netlify Sovereign Audit
- ### 📦 Repository Sovereign Audit
- ### 🔧 Auto-Repair Capabilities
- ## Installation
- # Make sure you're in the repository root
- # The tool is located at:
- ## Usage
- ### Basic Usage
- ### Advanced Usage
- ### Command-Line Options
- ## Output
- ### Console Output
- ### JSON Reports
- ### Report Structure
- ## Exit Codes
- ## Audit Categories
- ### Git Categories
- ### Netlify Categories
- ### Repository Categories
- ## Severity Levels
- ## Status Values
- ## Integration with CI/CD
- ### GitHub Actions
- ## Testing
- ## Development
- ### Adding New Checks
- ### Adding Auto-Repair
- ## Architecture
- ### Class Hierarchy
- ### Data Models
- ## Best Practices
- ## Troubleshooting
- ### Common Issues
- # Solution: Make sure you're in the repository root
- # Solution: Make sure Git is installed and repository is initialized
- # Solution: Review netlify.toml and environment files
- ## Support
- ## Future Enhancements
- ## License


### ./docs/DEPLOY_DIAGNOSE_GUIDE.md

- # Deploy & Diagnose Companion
- ## ✅ Features
- ## 🔧 Environment Variables
- ## 🚀 Manual Run
- ## 🧩 Output Example
- ## 🛰️ Webhook Mode


### ./docs/AUTONOMY_ORIGINALITY_INTEGRATION.md

- # Autonomy Engine - Originality & Compliance Integration
- ## Overview
- ## Features
- ### 1. Anti-Copyright Engine Integration
- ### 2. LOC Engine Integration
- ### 3. Enhanced Task Contracts
- ## API Usage
- ### Create Task with Originality Check (Default)
- ### Create Task without Originality Check
- ## Compliance States
- ### OK
- ### Flagged
- ### Blocked
- ### Error
- ## Configuration
- ## How It Works
- ### Compliance Check Process
- ### LOC Metrics Process
- ## Testing
- ## Integration Points
- ### With Compliance Scan Engine
- ### With LOC Counter
- ## Benefits
- ## Future Enhancements
- ## License


### ./docs/ENVSCRIBE_QUICK_REF.md

- # EnvScribe Quick Reference
- ## 🚀 Quick Commands
- # Full audit (scan + emit + certify)
- # Just scan
- # View current report
- # Generate docs and copy blocks
- # Get platform-specific copy block
- ## 📡 API Endpoints
- # Health check
- # Full audit workflow
- # Scan only
- # Get current report
- # Generate artifacts
- # Get copy block
- ## 📂 Output Files
- ## 🏗️ Architecture
- ## 🔗 Integration Points
- ### Genesis Bus
- ### EnvRecon
- ### Truth Engine
- ### Steward
- ### HXO Nexus
- ## 🧪 Testing
- # Unit tests (10/10)
- # Integration tests (3/3)
- # Existing tests (7/7)
- ## 📊 Example Output
- ### Scan Summary
- ### Copy Block (Render)
- ## 🎯 Use Cases
- ### 1. Deployment Preparation
- # Generate all platform configs before deployment
- # Copy blocks from diagnostics/ to platform dashboards
- ### 2. Environment Drift Detection
- # Scan and compare against live platforms
- # Review drifted variables in report
- ### 3. Documentation Generation
- # Keep ENV_OVERVIEW.md up-to-date
- ### 4. CI/CD Integration
- # Add to deployment pipeline
- ## 🔐 Security
- ## 🎛️ Configuration
- # Enable/disable EnvScribe
- # Enable/disable Truth Engine
- # Enable/disable Genesis Bus
- ## 📚 Related Docs


### ./docs/SELFTEST_OVERVIEW.md

- # Self-Test Overview
- ## v1.9.7j — Bridge Autonomy Diagnostic Pulse
- ## Architecture
- ### Core Components
- ## Diagnostic Flow
- ## Engine Registry
- ## Usage
- ### Manual Invocation
- ### Disable Auto-Healing
- ### Environment Variables
- ## Report Structure
- ## Continuous Operation
- ### Automatic Schedule
- ### On Failure Detected
- ## Security & Governance
- ## Metrics
- ## Integration Points


### ./docs/doctrine-vault.md

- # Bridge Armada Doctrine Vault
- ## Agent Origin Stories
- ### Git (GitHub Copilot): The Shipwright of the Bridge Armada


### ./docs/TRIAGE_PRESEED.md

- # Triage Pre-Seed System - Operation Genesis
- ## Overview
- ## Architecture
- ### Components
- ## Event Flow
- ## Files Created/Modified
- ### Created Files
- ### Modified Files
- ## Usage
- ### Automatic Execution
- ### Manual Execution
- ### Frontend Integration
- ## Baseline Report Structure
- ## Integration with Existing Systems
- ## Benefits
- ## Testing
- # Run pre-seed
- # Verify generated files
- # Test synchrony collector can read seeded data
- # Clean up (these files are gitignored)
- ## Production Deployment
- ## Maintenance
- ## Security
- ## Performance


### ./docs/RENDER_FALLBACK.md

- # Render Fallback
- ## Overview
- ## Features
- ## Usage
- ### Python
- ## Integration
- ## Deployment Flow
- ## Configuration
- ## Benefits


### ./docs/BRH_DEPLOYMENT_GUIDE.md

- # Bridge Runtime Handler (BRH) - Deployment Guide
- ## Architecture Overview
- ## Components
- ## Quick Start
- ### 1. Install Dependencies
- ### 2. Set Environment Variables
- # Generate a secure seal
- # Compute HMAC signature
- # Set the Forge Dominion Root
- ### 3. Run BRH
- ### 4. Run BRH API Server (Optional)
- # Install additional dependencies
- # Run the API server
- ## Configuration
- ### bridge.runtime.yaml
- ## Security
- ### HMAC Signature Verification
- ### Token Minting
- ### Allow Unsigned Mode
- ## GitHub Actions Integration
- ### Setup GHCR
- ## Netlify Integration
- ### Deploy Webhook
- ## Frontend Control Dashboard
- # In .env or Vite config
- ## Systemd Service (Production)
- ## API Endpoints
- ### Security Configuration
- ### Image Name Validation
- ## Troubleshooting
- ### Container won't start
- ### Health check failing
- ### Signature verification failed
- ### Docker network errors
- ## Frontend Configuration
- ### Default Configuration
- ### Environment Variables
- ### Build with Custom Backend URL
- ### Netlify Deployment
- ### Verification
- ### Local Development
- ## Migration from Render
- ## Next Steps (Phase 2)
- ## Support


### ./docs/FEDERATION_TRIAGE_ENGINE.md

- # Federation Triage Engine v1.8.1
- ## Overview
- ## Components
- ### 1. Federation Map (`bridge_backend/federation_map.json`)
- ### 2. Network Helper (`.github/scripts/_net.py`)
- ### 3. Deep-Seek Triage Script (`.github/scripts/deep_seek_triage.py`)
- ### 4. GitHub Actions Workflow (`.github/workflows/federation_deepseek.yml`)
- ## Signal Taxonomy
- ### Health Status
- ### Repair Actions
- ### Error Signals
- ## Usage
- ### Running Manually
- # Install dependencies
- # Run deep-seek triage
- # Check report
- ### Reading Reports
- ## Escalation
- ### Applying Patch Intents
- ## Security
- ## Troubleshooting
- ### All Nodes Failing
- ### Schema Drift Persists
- ### DNS Warm-up Failures
- ## Integration with Existing Systems
- ## Version History
- ### v1.8.1 (Current)


### ./docs/NODE_FAILSAFE_GUIDE.md

- # Node Failsafe Guide
- ## 🛡️ Emergency Recovery & Fallback Procedures
- ## Table of Contents
- ## Overview
- ## Failure Scenarios
- ### Scenario 1: Genesis Bus Unavailable
- ### Scenario 2: Parser Crashes
- ### Scenario 3: Truth Certification Fails
- ### Scenario 4: Configuration Corruption
- ### Scenario 5: Report Storage Full
- # Prune old reports if over limit
- ### Scenario 6: Infinite Repair Loop
- # Truth Micro-Certifier prevents this
- ## Recovery Procedures
- ### Emergency Shutdown
- ### Partial Recovery
- ### Configuration Reset
- ## Emergency Controls
- ### Admiral Override
- ### Circuit Breaker Reset
- ## Monitoring & Alerts
- ### Health Check Commands
- # Check node status
- # Verify configuration
- # Review recent reports
- # Check workflow runs
- ### Alert Conditions
- ### Notification Setup
- # In core.py, add alert hook
- ## Rollback Procedures
- ### Automatic Rollback
- ### Manual Rollback
- # Find commit
- # Revert
- # Rename workflow to disable
- # Remove all node files
- ### Cascade Integration
- ## Best Practices
- ## Contact & Escalation
- ## See Also


### ./docs/AUTONOMY_INTEGRATION_QUICK_REF.md

- # Autonomy Integration Quick Reference
- ## 🎯 What Was Done
- ## 🔗 Integration Points
- ### Triage → Autonomy
- ### Federation → Autonomy
- ### Parity → Autonomy
- ## 🚀 Quick Start
- ### Enable Integration
- ### Test Triage Integration
- ### Test Parity Integration
- ### Test Federation Integration
- ## 📊 Event Flow
- ## 🔍 Verify Integration
- ## 📚 Full Documentation
- ## ✅ Files Modified
- ## 🧪 Tests Added
- ## 📖 Docs Added


### ./docs/RENDER_INTEGRATION.md

- # Render.com Service Configuration for SR-AIbridge Heavy Compute
- # This configuration allows running heavy GitHub Actions workloads on Render's free tier
- # to reduce GitHub Actions minutes consumption
- ## Services to Deploy on Render.com
- ### 1. Quantum Security Service (Web Service - Free Tier)
- # Install git for cloning
- # Copy requirements
- # Install Python dependencies
- # Copy runtime scripts
- # Copy application code
- # Health check endpoint
- ### 2. Token Rotation Service (Cron Job - Free Tier)
- ### 3. Self-Hosted Runner (Web Service - Free Tier)
- # Install dependencies
- # Create runner user
- # Download and setup GitHub Actions runner
- # Configure and run (use environment variables for registration)
- ## GitHub Workflow Integration
- ### Trigger Render Services from GitHub Actions
- ## Setup Instructions
- ### 1. Create Render Account
- ### 2. Deploy Services
- ### 3. Configure Webhooks
- ### 4. Update GitHub Workflows
- ## Expected Cost Savings
- ## Monitoring


### ./docs/ENGINE_CATALOG.md

- # Engine Catalog
- ## Complete Documentation of All 21 SR-AIbridge Engines
- ## 📊 Engine Overview
- ## 🏗️ Category 1: Core Engines (6)
- ### 1. Blueprint Engine
- ### 2. TDE-X (Tri-Domain Execution)
- ### 3. Cascade Engine
- ### 4. Truth Engine
- ### 5. Autonomy Engine
- ### 6. Parser Engine
- ## 🚀 Category 2: Super Engines (6)
- ### 1. CalculusCore (Math Engine)
- # Integration
- # Result: 1/3
- # Equation solving
- # Result: [-2, 2]
- # Limits
- # Result: 1
- # Series expansion
- # Result: 1 + x + x^2/2 + x^3/6 + ...
- ### 2. QHelmSingularity (Quantum Engine)
- ### 3. AuroraForge (Science/Creative Engine)
- ### 4. ChronicleLoom (History Engine)
- ### 5. ScrollTongue (Language Engine)
- ### 6. CommerceForge (Business Engine)
- ## 🎯 Category 3: Orchestrator (1)
- ### Leviathan Solver
- ## 🌌 Category 4: Sovereign Agent (1)
- ### Git Sovereign Agent
- # Initialize sovereign agent
- # Mint ephemeral token
- # Deploy container
- # Resonate all engines
- # Make autonomous decision
- # Trigger sovereign operations
- ## 🛠️ Category 5: Utility Engines (7)
- ### 1. Creativity Bay
- ### 2. Indoctrination Engine
- ### 3. Screen Engine
- ### 4. Speech Engine
- ### 5. Recovery Orchestrator
- ### 6. Agents Foundry
- ### 7. Filing Engine
- ## 🔗 Genesis Linkage
- ## 📊 Engine Summary Statistics
- ## 🎯 Quick Reference


### ./docs/TDE_X_DEPLOYMENT_GUIDE.md

- # TDE-X v1.9.7a Deployment Guide
- ## Overview
- ## Key Features
- ## Architecture
- ### Shards
- ### Components
- ## Endpoints
- ### Health Checks
- #### `/health/live`
- #### `/health/ready`
- #### `/health/diag`
- ### Deploy Parity
- #### `/api/diagnostics/deploy-parity`
- ## Environment Variables
- ### Required
- ### Optional
- ## Render Configuration
- ### Start Command
- ### Health Check Path
- ### Pre-Deploy Command (Optional)
- ## Local Testing
- ### 1. Install Dependencies
- ### 2. Set Environment Variables
- ### 3. Run Server
- ### 4. Test Endpoints
- # Test liveness
- # Test readiness
- # Test diagnostics
- # Test deploy parity
- ## Netlify (Frontend) Integration
- ## Background Tasks
- ## Rollback
- # Temporary rollback to direct uvicorn
- ## What This Solves
- ## Monitoring
- ### Queue Depth
- ### Shard Status
- ### Tickets
- ## Troubleshooting
- ### Issue: Server won't start
- ### Issue: High queue depth
- ### Issue: Shard failures


### ./docs/ARIE_QUICK_REF.md

- # ARIE Quick Reference
- ## What is ARIE?
- ## Quick Start
- ### Run a scan
- ### Apply fixes
- ### View last report
- ### Rollback changes
- ## Policy Types
- ## Analyzers
- ## API Endpoints
- ## Configuration
- ## Genesis Integration
- ## RBAC Permissions
- ## Common Use Cases
- ### Weekly audit
- ### Apply safe fixes
- ### Check for critical issues
- ### CI integration
- # In GitHub Actions or Render
- ## Rollback
- ## Test Suite
- ## Documentation
- ## Current Status
- ## Troubleshooting
- # Check if enabled
- # Ensure you're not in dry-run mode
- # (don't use --dry-run flag)
- ## Support


### ./docs/V196L_IMPLEMENTATION_SUMMARY.md

- # SR-AIbridge v1.9.6L - Autonomous Environment Synchronization Pipeline
- ## 🎯 Overview
- ## ✅ Implemented Components
- ### 1. Core Infrastructure
- #### GenesisCtl CLI Enhancement
- #### Environment Sync Verifier
- #### HubSync Enhancement
- ### 2. CI/CD Integration
- #### GitHub Actions Workflow
- ### 3. Documentation Suite
- #### Primary Documentation
- #### Updated Documentation
- ### 4. Testing Infrastructure
- #### Test Suite
- ## 🔄 Data Flow
- ## 📊 Genesis Event Integration
- ### Published Events
- ### Subscribers
- ## 🔐 Security Features
- ## 📄 Generated Artifacts
- ### Sync Snapshots
- ### Parity Reports
- ### Audit Documentation
- ## 🧪 Validation
- ### Test Results
- ### Manual Testing
- ## 📦 File Summary
- ### New Files (11)
- ### Modified Files (3)
- ## 🎯 Key Features Delivered
- ## 🚀 Usage Examples
- ### Manual Sync
- ### Export Snapshot
- ### Verify Parity
- ### Run Tests
- ## 📈 Impact
- ### Benefits
- ### Integration Points
- ## 🔮 Future Enhancements
- ## 📚 Documentation Index


### ./docs/AUTONOMY_INTEGRATION_ARCHITECTURE.md

- # Autonomy Engine Integration Architecture


### ./docs/HXO_GENESIS_INTEGRATION.md

- # HXO Genesis Integration — Event Bus Topics
- ## Overview
- ## Core HXO Topics
- ### `hxo.link.autonomy`
- ### `hxo.link.blueprint`
- ### `hxo.link.truth`
- ### `hxo.link.cascade`
- ### `hxo.link.federation`
- ### `hxo.link.parser`
- ### `hxo.link.leviathan`
- ### `hxo.telemetry.metrics`
- ### `hxo.heal.trigger`
- ### `hxo.heal.complete`
- ### `hxo.status.summary`
- ## Event Flow Diagrams
- ### Plan Submission Flow
- ### Shard Execution Flow
- ### Healing Flow
- ## Temporal Event Replay Cache (TERC)
- ### Configuration
- ### Query TERC
- # Get recent events
- # Replay events for plan
- ## Event Routing (ALIR)
- ### Configuration
- ### Priority Levels
- ## Integration Checklist


### ./docs/endpoint_test_quick_ref.md

- # Endpoint Testing Quick Reference
- ## Quick Commands
- ### Basic Usage
- # Test local backend
- # Test deployed backend
- # JSON output
- # Custom timeout
- ## Exit Codes
- ## What Gets Tested
- ### Core Endpoints (Must Pass)
- ### Engine Endpoints (Optional)
- ## Common Scenarios
- ### Development Testing
- # After code changes
- ### Deployment Validation
- # After deploying to production
- ### CI/CD Integration
- # In GitHub Actions or other CI
- ### Troubleshooting
- # Identify failing endpoints
- ## JSON Processing
- ### Extract failures
- ### Get success rate
- ### Save results
- ## Troubleshooting Guide
- ## Documentation
- ## Related Tools


### ./docs/GENESIS_V2_0_1_GUIDE.md

- # Genesis v2.0.1 — Project Genesis: Universal Engine Assimilation
- ## Overview
- ### What Genesis v2.0.1 Provides
- ## Architecture
- ### 1. Genesis Core Contract (GCC)
- #### Event Kinds
- #### Topic Namespace
- ### 2. Universal Adapters
- # Publish an intent
- # Report degraded health
- # Certify a fact
- #### Convenience Helpers
- # Report component health issue
- # Report deploy stage failure
- ### 3. Guardians-First Safety
- # Guardians check event safety
- #### What Guardians Block
- #### Configuration
- ### 4. Event Persistence & Replay
- # Check if event is duplicate
- # Record event (with dedupe)
- # Replay events from watermark
- #### Replay CLI
- # Replay from watermark
- # Replay from timestamp
- #### Configuration
- ### 5. TDE-X v2 - Resumable Deployment
- #### Stages
- #### Usage
- # Get status
- # Stages run in background, emitting Genesis events:
- # - deploy.tde.stage.started
- # - deploy.tde.stage.completed
- # - deploy.tde.stage.failed (triggers heal)
- #### Configuration
- #### State Persistence
- ## Deployment
- ### Render Configuration
- ### Port Binding
- # In main.py
- ## Engine Integration Examples
- ### Truth Engine
- # Certify a fact
- ### Autonomy Engine
- # Propose autonomous action
- ### Cascade Engine
- # Start workflow
- ## Testing
- ## Migration Guide
- ### From v1.9.x to v2.0.1
- ## Troubleshooting
- ### Port Binding Issues
- # Check PORT env var
- # Verify render.yaml start command
- ### TDE-X Stage Failures
- # Check TDE-X state
- # Increase timeout
- # Check Genesis events for heal messages
- # Look for: deploy.tde.*.failed
- ### Guardians Blocking Events
- # Check guardians stats
- # Disable strict mode temporarily
- # Review blocked event audit trail
- # Events are logged with security.guardians.action.blocked
- ## Success Metrics
- ## API Reference
- ### Genesis Adapters
- # Event emission
- # Convenience helpers
- ### Genesis Persistence
- # Initialize
- # Dedupe checking
- # Event recording
- # Event retrieval
- # Watermark
- ### Genesis Replay
- # Replay from watermark
- # Replay from timestamp
- # Get current watermark
- ### Guardians Gate
- # Check event safety
- # Add bypass key for emergency ops
- # Get stats
- ### TDE-X v2 Orchestrator
- # Get status
- # Status includes:
- # - stages: {stage_name: {status, started_at, completed_at, error}}
- # - started_at, completed_at
- # - resume_on_boot, max_stage_runtime_secs
- ## Support


### ./docs/BRIDGE_HEALERS_CODE.md

- # The Bridge Healer's Code
- ## Preamble
- ## The Four Oaths
- ### Oath I - The Oath of Integrity
- ### Oath II - The Oath of Knowledge
- ### Oath III - The Oath of Resilience
- ### Oath IV - The Oath of Network
- ## The Continuum
- ### Lore Entry I - The First Healing
- ### Lore Entry II - The Federation Awakens
- ### Lore Entry III - The Cascade Survived
- ### Lore Entry IV - The Firewall Learned
- ## The Healer's Creed
- ## Implementation Pillars
- ### Pillar 1: Autonomous Diagnostics
- ### Pillar 2: Intelligent Remediation
- ### Pillar 3: Continuous Learning
- ### Pillar 4: Graceful Degradation
- ## The Healer's Tools
- ### Firewall Intelligence Engine (FIE)
- ### Bridge Autofix Engine
- ### Multi-Agent System (MAS)
- ### Federation Client
- ## The Healer's Oath - Complete Text
- ## Version History
- ## Canonical Status


### ./docs/COMMAND_DECK_GUIDE.md

- # Command Deck V1 Guide
- ## Overview
- ## Features
- ## Access
- ## UI Panels
- ### Task Status Card
- ### Agent Metrics Table
- ### Anomaly Feed
- ### Fault Controls
- ### Demo Launchpad
- ### Event Stream Tap
- ## Keyboard Shortcuts
- ## Modes
- ### Deck Mode
- ### Ops Mode
- ## WebSocket Connection
- ## Event Types
- ## Troubleshooting
- ### WebSocket Not Connecting
- ### No Events Showing
- ### Demos Not Starting
- ## Styling
- ## Performance
- ## Next Steps


### ./docs/README_RELEASES.md

- # SR-AIbridge — Release Intelligence & Self-Heal
- ## What's new in v1.9.6f (Latest)
- ### Migration from v1.9.6b → v1.9.6f
- ### Expected Logs
- ### Health Check
- ## What's new in v1.9.6b
- ## One-time checklist
- ## Health verify
- ## Why this permanently fixes your two recurring pains
- ### 1. Render port scans timing out
- ### 2. Heartbeat sometimes "disabled"
- ### 3. "models" import/path errors
- ### 4. DB missing tables after deploy
- ### 5. Self-heal + learn
- ## How to merge


### ./docs/GENESIS_EVENT_FLOW.md

- # Genesis Event Flow - Environment Synchronization
- ## 🧩 Overview
- ## 📊 Event Topics
- ### envsync.init
- ### envsync.commit
- ### envsync.drift
- ## 🔄 Event Flow Diagram
- ## 🎯 Integration Points
- ### Autonomy Engine
- # bridge_backend/bridge_core/engines/autonomy/observers.py
- ### Truth Engine
- # bridge_backend/bridge_core/engines/truth/ledger.py
- ### Blueprint Engine
- # bridge_backend/bridge_core/engines/blueprint/validators.py
- ### Cascade Engine
- # bridge_backend/bridge_core/engines/cascade/sync.py
- ## 🔐 Permission Filtering
- # In genesis/bus.py
- ## 📝 Event History & Introspection
- ### Query Event History
- # Get last 10 envsync events
- ### Event Persistence
- ## 🧪 Testing Event Flow
- ### Publish Test Event
- ### Subscribe to Events
- ## 📊 Monitoring & Alerts
- ### Event Metrics
- ### Alert Thresholds
- # In bridge_backend/bridge_core/engines/autonomy/thresholds.py
- ## 🔗 Related Documentation


### ./docs/TRIAGE_FEDERATION.md

- # Triage Federation v1.7.5
- ## Overview
- ## Components
- ### 1. Shared Triage Client (`bridge_backend/tools/triage/common/utils.py`)
- ### 2. API Triage (`bridge_backend/tools/triage/api_triage.py`)
- ### 3. Endpoint Triage (`bridge_backend/tools/triage/endpoint_triage.py`)
- ### 4. Diagnostics Federation (`bridge_backend/tools/triage/diagnostics_federate.py`)
- ### 5. GitHub Action (`triage_federation.yml`)
- ## Environment Variables
- ### Required
- ### Optional Tuning
- ## How Retries & Backoff Work
- ## Report Formats
- ### API Triage Report
- ### Endpoint Triage Report
- ### Federation Report
- ## Reading Reports
- ## Local Testing
- # Set environment variables
- # Run individual triage scripts
- # Check outputs
- ## Integration with Existing Systems
- ## Troubleshooting
- ### "parity report missing" error
- ### "PUBLIC_API_BASE missing" error
- ### All checks failing
- ## Version History


### ./docs/FORGE_AUTOREPAIR_GUIDE.md

- # Forge Auto-Repair Guide
- ## 🛠️ Forge - Autonomous Repair System
- ### Purpose
- ### What Forge Fixes
- #### 1. Missing Netlify Configuration
- #### 2. Environment Drift
- #### 3. Build Configuration
- ### Architecture
- ### Usage
- #### Programmatic
- #### CLI
- # Full repair
- # Scan only (no fixes)
- #### Auto-Triggered
- ### Repair Process
- ### Default Files Created
- #### `_headers`
- #### `_redirects`
- #### `netlify.toml`
- ### Configuration
- # Enable/disable Forge
- # Genesis integration
- # Truth certification
- ### Genesis Bus Events
- ### Integration with ARIE
- ### Safety Features
- ### Example Output
- ### Troubleshooting
- ### Best Practices
- ### Related


### ./docs/HXO_README.md

- # HXO Ascendant — The Federation Nexus
- ## Overview
- ## Core Objectives
- ## Architecture
- ## New Core Capabilities (v1.9.6p)
- ### 1. Dynamic Shard Scaling (Hypshard V3)
- ### 2. Predictive Orchestration Engine (Leviathan x HXO)
- ### 3. Temporal Event Replay Cache (TERC)
- ### 4. Zero-Downtime Upgrade Path (ZDU)
- ### 5. Quantum-Entropy Hashing (QEH)
- ### 6. Harmonic Consensus Protocol (HCP)
- ### 7. Cross-Federation Telemetry Layer
- ### 8. Adaptive Load Intent Router (ALIR)
- ### 9. Auto-Heal Cascade Overwatch (ACH)
- ## Engine Federation
- ## Security Layers
- ## Genesis Bus Topics
- ## Configuration
- ## Documentation
- ## Impact Metrics
- ## Closing Statement


### ./docs/LOG_SIGNATURES.md

- # Log Signatures Reference
- ## Overview
- ## Error Signature Categories
- ### DNS Resolution Errors
- #### `ENOTFOUND`
- #### `DNS resolution failed`
- ### Connection Errors
- #### `ECONNREFUSED`
- #### `ECONNRESET`
- #### `ETIMEDOUT`
- ### HTTP/HTTPS Errors
- #### `E404`
- #### `E403`
- ### SSL/TLS Certificate Errors
- #### `self signed certificate`
- #### `certificate verify failed`
- ### Network Unreachable Errors
- #### `Network unreachable`
- #### `Host unreachable`
- ### Package Manager Specific
- #### npm Errors
- #### pip Errors
- ## Firewall Signature Detection
- ## Quick Diagnostic Commands
- ### Test DNS
- ### Test Connectivity
- ### Test Package Managers
- ### Test SSL/TLS
- ## CI/CD Specific Issues
- ### GitHub Actions
- ### Render Deployment
- ### Netlify Deployment
- ## Integration with Firewall Intelligence
- ## See Also


### ./docs/SYSTEM_BLUEPRINT.md

- # SR-AIbridge System Blueprint
- ## Technical Architecture & Implementation Details
- ## 🏛️ Architecture Layers
- ## 📦 Technology Stack Details
- ### Backend Stack
- ### Frontend Stack
- ## 🗄️ Database Schema (Complete)
- ### Core Tables
- #### Guardians Table
- #### Agents Table
- #### Missions Table
- #### Blueprints Table
- #### Agent_Jobs Table (Partitioned Monthly)
- #### Vault_Logs Table
- #### Admiral_Keys Table
- ### Indexes (Critical for Performance)
- ## 🎮 API Architecture
- ### REST API Structure
- ### WebSocket Endpoints
- ### Request/Response Flow
- ## ⚙️ Engine Architecture (20 Engines)
- ### Genesis Linkage System
- ### Core Engines (Infrastructure - 6)
- ### Super Engines (Specialized AI - 6)
- ### Orchestrator (Coordination - 1)
- ### Utility Engines (Support - 7)
- ## 🔐 Security Architecture
- ### Token Management (Forge Dominion)
- ### Cryptographic Operations
- # Key generation
- # Signature creation
- # Signature verification
- ### CORS Configuration
- ## 🔄 Real-Time Architecture (WebSocket)
- ### WebSocket Connection Flow
- ### Connection Manager Pattern
- ## 🏥 Health Monitoring System
- ### Health Check Levels
- ### Self-Healing Triggers
- ## 📊 State Management
- ### Backend State (Database)
- ### Frontend State (React)
- ### Caching Strategy
- # In-memory cache for static data
- # Cache invalidation on updates
- ## 🚀 Deployment Architecture
- ### Production Stack
- ### CI/CD Pipeline
- ## 📈 Performance Characteristics
- ### Backend Performance
- ### Frontend Performance
- ### Optimization Techniques
- ## 🧪 Testing Architecture
- ### Backend Tests
- ### Frontend Tests
- ### Smoke Tests


### ./docs/HXO_TROUBLESHOOTING.md

- # HXO Troubleshooting Guide
- ## Quick Diagnostics
- ### Check HXO Status
- ## Common Issues
- ### Issue: HXO Not Starting
- # Check if HXO is enabled
- # Enable HXO
- # Restart backend
- ### Issue: Plans Stuck in PENDING
- # Check active plans
- # Check logs
- # Enable Genesis Bus
- # Check Blueprint status
- # Check Truth Engine
- # Retry plan
- ### Issue: High Shard Failure Rate
- # Get plan metrics
- # Check failure reasons
- # Reduce concurrency
- # Increase shard timeout
- # Increase SLO
- # Restart backend
- ### Issue: Guardian Halt Triggered
- # Check healing depth
- # View Guardian events
- # Review healing chain to identify root cause
- # If legitimate, increase limit (use caution)
- # Cancel halted plan
- # Fix root cause and resubmit
- ### Issue: Merkle Certification Failures
- # Check Truth Engine status
- # Verify Merkle tree
- # Verify shard results integrity
- # Increase federation timeout
- # Retry certification
- # If persistent, check Truth Engine logs
- ### Issue: Zero-Downtime Upgrade Fails
- # Check Blueprint migration status
- # Check active plans during upgrade
- # Ensure ZDU is enabled
- # Wait for active plans to complete before schema changes
- # If stuck, perform graceful shutdown
- ### Issue: TERC Memory Pressure
- # Check TERC size
- # Memory usage
- # Reduce TERC limit
- # Clear old events
- # Restart backend
- ## Performance Tuning
- ### Optimize for Throughput
- # Increase concurrency
- # Reduce autosplit threshold (split sooner)
- # Increase autosplit factor (more parallelism)
- ### Optimize for Reliability
- # Reduce concurrency (less load)
- # Increase timeouts
- # Enable all safety features
- ### Optimize for Cost
- # Reduce resource usage
- # Disable expensive features (development only!)
- ## Health Checks
- ### Engine Link Health
- # Check all engine links
- # Test specific link
- ### Database Health
- # Check checkpoint DB
- # Vacuum if needed
- # Check size
- ### Shard Health
- # View shard distribution
- # Check for stuck shards
- # Retry stuck shards
- ## Recovery Procedures
- ### Recover Incomplete Plans After Crash
- # List incomplete plans
- # Rehydrate specific plan
- # Rehydrate all
- ### Rollback Failed Deployment
- # Get rollback points
- # Trigger rollback
- ### Clear Stale Data
- # Remove completed plans older than 30 days
- # Remove failed plans older than 7 days
- ## Debug Mode
- # Enable debug logs
- # Restart
- # Tail logs
- ## Emergency Procedures
- ### Stop All HXO Operations
- # Emergency shutdown
- # Verify stopped
- ### Disable HXO Temporarily
- ### Reset HXO Completely
- # Backup first
- # Reset
- # Restart
- ## Support


### ./docs/quickrefs/TDE_X_QUICK_REF.md

- # TDE-X Quick Reference
- ## v1.9.7a - Hypersharded Deploy + Federation + Sovereign Post-Deploy
- ### Quick Start
- # Set environment
- # Run server
- ### Health Checks
- ### Render Configuration
- ### Architecture
- ### Shards
- ### Federation Events
- ### Monitoring
- ### Troubleshooting
- ### File Locations
- ### Migration from TDB (v1.9.6i)
- ### Rollback (Emergency Only)


### ./docs/quickrefs/NETLIFY_UMBRA_QUICK_REF.md

- # Umbra + Netlify Integration — Quick Reference v1.9.7e
- ## 🚀 Quick Start
- ### 1. Enable Netlify Validation
- ### 2. Run Validation
- ### 3. Record Netlify Events
- ## 📡 API Endpoints
- ### Validate Configuration
- # RBAC: Admiral, Captain
- # Response: Validation result with status
- ### Validate with Memory Recall
- # RBAC: Admiral, Captain
- # Response: Validation result + recall information
- ### Get Metrics
- # RBAC: Admiral, Captain, Observer
- # Response: Validator metrics
- ### Get Status
- # RBAC: All roles
- # Response: Validator status and version
- ## 🧠 Intent Classification
- ## 🔍 Validation Checks
- ## 🔄 CI/CD Integration
- ## 📊 Metrics
- ### Validator Metrics
- # Returns:
- ### Umbra Memory Metrics
- # Categories include:
- # - netlify_validation
- # - netlify_event
- # - repair
- # - anomaly
- # - echo
- ## 🧪 Testing
- ### Run Tests
- # Netlify validator tests
- # All Umbra tests (including Netlify)
- ### Manual Testing
- # Test validation script
- # Test with Python
- ## 🔐 RBAC
- ## 🐛 Troubleshooting
- ### Validation Fails
- # Check the output for specific errors
- # Common issues:
- # - Duplicate header rules
- # - Duplicate redirect rules
- # - Missing build command
- # - Invalid syntax in netlify.toml
- ### Memory Not Recording
- # Check if Umbra Memory is enabled
- # Check if Netlify sync is enabled
- # Verify vault directory exists
- ### API Endpoints Not Working
- # Check if routes are registered
- # The routes should be in: bridge_backend/engines/netlify_routes.py
- # Verify RBAC is configured
- # Check your authentication middleware
- ## 📚 Related Documentation
- ## 🎯 Common Use Cases
- ### 1. Pre-Deploy Validation
- # In your CI/CD pipeline
- ### 2. Learning from Failures
- # After fixing a Netlify issue
- ### 3. Checking Historical Fixes
- # Recall past Netlify events


### ./docs/quickrefs/QUICK_START_30MIN.md

- # Quick Start Guide: SR-AIbridge in 30 Minutes
- ## Ultra-Fast Setup for Experienced Developers
- ## ⚡ Prerequisites (2 minutes)
- # Verify versions
- # Clone repository
- ## 🐍 Backend Setup (10 minutes)
- ### 1. Install Dependencies (3 minutes)
- ### 2. Configure Environment (1 minute)
- # Copy example or create .env
- ### 3. Start Backend (1 minute)
- # Backend running on http://localhost:8000
- # API docs at http://localhost:8000/docs
- ### 4. Verify Backend (1 minute)
- # In new terminal
- ## ⚛️ Frontend Setup (10 minutes)
- ### 1. Install Dependencies (4 minutes)
- ### 2. Configure Environment (1 minute)
- # Copy example or create .env
- ### 3. Start Frontend (1 minute)
- # Frontend running on http://localhost:5173
- ### 4. Verify Frontend (1 minute)
- ## 🎮 Load Demo Data (5 minutes)
- ## 🧪 Smoke Test (3 minutes)
- ### Test All Endpoints
- ### Test Engines
- ### Manual API Tests
- # Create agent
- # Create mission
- # List agents
- # List missions
- ## 🎯 Key URLs
- ## 🚀 Production Deploy (Bonus - 10 minutes)
- ### Deploy Frontend to Netlify
- # Install Netlify CLI
- # Login
- # Deploy
- ### Deploy Backend to Render
- ### Update Frontend Config
- # Update .env with production backend URL
- ## 🔧 Common Commands Reference
- ### Backend
- # Start server
- # Run with auto-reload (development)
- # Different port
- # Check logs
- ### Frontend
- # Development server
- # Production build
- # Preview production build
- # Lint code
- ### Database
- # Reset database (SQLite)
- # PostgreSQL migration (production)
- ### Testing
- # Full endpoint test
- # Engine smoke test
- # Backend tests
- # Frontend tests
- ## 🎓 Next Steps After Setup
- ### Explore the System
- ### Read Documentation
- ### Customize
- ## 🚨 Quick Troubleshooting
- ### Backend Issues
- # Port in use
- # Module not found
- # Database locked
- ### Frontend Issues
- # Build fails
- # Port in use
- # Vite will auto-increment (5173 → 5174)
- # Can't connect to backend
- # Check CORS in backend .env
- # Verify backend is running
- ### CORS Errors
- # Add frontend URL to backend .env
- ## 📊 What You Have Now
- ## 🎯 Performance Expectations
- ## 🔐 Security Notes
- ## 📞 Getting Help
- ## 🎉 Success Checklist
- ## 🚀 You're Ready!
- ## 📖 Quick Reference Links


### ./docs/quickrefs/HXO_NEXUS_QUICK_REF.md

- # HXO Nexus Quick Reference Guide
- ## Version
- ## Quick Start
- ### Enable HXO Nexus
- # .env configuration
- ### Initialize Programmatically
- # Initialize the nexus
- # Check health
- ## Architecture Overview
- ## Core Capabilities
- ### 1. Engine Connectivity (1+1=∞)
- # Get connection graph
- # Check if engines are connected
- # Get engine connections
- ### 2. HypShard v3 - Quantum Adaptive Sharding
- # Create shard
- # Execute on shard
- # Get stats
- ### 3. Harmonic Consensus Protocol
- # Propose
- # Vote
- # Check status
- ### 4. Quantum Entropy Hashing
- # Hash data
- # Refresh entropy pool
- ## API Endpoints
- ### Health & Status
- # Nexus health
- # Configuration
- ### Engine Management
- # List engines
- # Get engine info
- ### Connectivity
- # Connection graph
- # Check connection
- ### Orchestration
- # Coordinate engines
- # Initialize nexus
- ## Configuration Variables
- # HXO Nexus Core
- # HypShard v3
- # Quantum Entropy
- # Genesis Integration
- ## Engine Connection Matrix
- ## Security Layers
- ### RBAC
- ### Quantum Entropy Hashing (QEH-v3)
- ### Rollback Protection
- ### Audit Trail
- ## Common Workflows
- ### 1. Multi-Engine Deployment
- ### 2. Self-Healing Workflow
- # AUTONOMY detects issue → CASCADE orchestrates → TRUTH verifies → ARIE audits
- ### 3. Consensus Decision
- # Propose schema change
- # Engines vote
- ## Troubleshooting
- ### Nexus Not Starting
- # Check if enabled
- # Check logs
- # Verify Genesis Bus
- ### Engine Not Connecting
- # Test connection
- # Check engine registration
- ### HypShard Issues
- # Check stats
- # Verify config
- ## Testing
- # Run all HXO Nexus tests
- # Expected: 34 tests pass
- ## Performance Metrics
- ## Version History
- ## Related Documentation
- ## Meta


### ./docs/quickrefs/DATA_RELAY_QUICK_REF.md

- # Secure Data Relay Protocol - Quick Reference
- ## Overview
- ## Quick Start
- ### 1. Enable the Relay
- # In .env
- # SMTP Configuration (Gmail)
- ### 2. Use in Code
- # Before deleting any data
- ## Role-Based Retention
- ## Components
- ## Email Organization
- ## Metadata Envelope
- ## Queue Retry Mechanism
- # Manual retry
- ## Verification
- ## Production Checklist
- ## Monitoring
- ## Troubleshooting
- ### "SMTP credentials not configured"
- ### "Authentication failed"
- ### "Permission denied: /var/srbridge"
- ### Queued items not retrying
- ## Security Notes
- ## API Reference
- ### `archive_before_delete(component, user_id, role, record)`
- ### `format_relay_metadata(component, action, user_id, role, data)`
- ### `verify_archive(metadata, data)`
- ### `retry_queued_items(max_retries=3)`
- ### `get_queued_items()`


### ./docs/quickrefs/ROLE_SEPARATION_QUICK_REF.md

- # SR-AIbridge Role Separation - Quick Reference
- ## At-A-Glance Component Access Matrix
- ## Memory Autonomy Tiers
- ## Vault Structure
- ## System Health Views
- ### Admiral View (Global)
- ### Captain View (Local)
- ## Endpoint Access Control
- ### Admiral-Only Endpoints
- ### Captain Endpoints
- ### Shared Endpoints (All Roles)
- ## Backend Routes Summary
- ### Core Routes
- ### Special Features
- ### Engines
- ## RBAC Quick Check
- # To check if a role has access to a feature:
- ## Communication Firewall
- ### Captain's Chat
- ### Captain-to-Captain
- ## Testing Commands
- # Test brain access (should work)
- # Test custody as captain (should fail with 403)
- # Test vault isolation
- # Test health views
- ## Key Files Reference
- ### Frontend Components
- ### Backend Routes
- ### Middleware
- ## Summary


### ./docs/quickrefs/UMBRA_QUICK_REF.md

- # Umbra Cognitive Stack - Quick Reference
- ## 🌑 Quick Start
- ### Enable Umbra
- ## 📡 API Endpoints
- ### Core Operations
- # Detect anomalies
- # Generate and apply repair (Admiral only)
- ### Memory Operations
- # Recall experiences
- # Learn patterns
- ### Predictive Operations
- # Predict issues
- # Apply preventive repair (Admiral only)
- ### Echo Operations (Admiral Only)
- # Capture manual edit
- # Observe git commit
- ### Metrics
- # Get all metrics
- # Get status
- ## 🧠 Components
- ## 🔄 Cognitive Lifecycle
- ## 🔒 RBAC Quick Reference
- ### Admiral (Full Access)
- ### Captain (Read + Monitor)
- ### Observer (Read-Only)
- ## 📊 Metrics at a Glance
- ## 🎯 Common Tasks
- ### Detect and Repair an Anomaly
- # 1. Detect
- # 2. Generate repair
- # 3. Apply
- ### Learn from Past Repairs
- # Get all repair experiences
- # Learn patterns
- # Use patterns for prediction
- ### Capture Admiral Actions
- # Capture single edit
- # Observe entire commit
- # Sync to HXO
- ## 📡 Genesis Bus Topics
- ## 🧪 Testing
- # Run all Umbra tests
- # Run specific component
- ## 🔧 Troubleshooting
- ## 💾 Storage Paths
- ## 🎯 Intent Classification
- ## 📋 Watched Paths (Echo)
- ## 🚀 Integration Example
- # Initialize
- # Use
- ## ⚡ Performance Tips
- ## 📚 Resources


### ./docs/quickrefs/ENVRECON_QUICK_REF.md

- # Genesis v2.0.2 EnvRecon - Quick Reference
- ## CLI Commands
- # Audit all platforms
- # Sync to specific platform
- # Trigger auto-healing
- ## API Endpoints
- # Health check
- # Get report
- # Run audit
- # Sync all
- # Trigger heal
- # Sync GitHub secrets
- ## Inspector Panel
- ## Environment Variables
- # Required
- # Legacy RENDER_API_KEY removed=your_key
- # Legacy RENDER_SERVICE_ID removed=your_id
- # Optional
- ## Report Location
- ## Key Features
- ## Status Indicators
- ## Testing


### ./docs/quickrefs/BRH_QUICK_REF.md

- # 🚀 Bridge Runtime Handler (BRH) - Quick Reference
- ## ⚡ Quick Setup
- # 1. Generate FORGE_DOMINION_ROOT
- # 2. Set environment variables (from output above)
- # 3. Install dependencies
- # 4. Run BRH runtime
- # 5. (Optional) Run API server in another terminal
- ## 📝 Key Files
- ## 🔑 Environment Variables
- ## 📋 Runtime Manifest (bridge.runtime.yaml)
- ## 🎯 Common Commands
- # Generate Forge root with custom seal
- # Test authentication flow
- # Run BRH runtime (starts containers)
- # Run API server for remote control
- # Check API status
- # Trigger deployment
- # Restart a container
- # Drain (stop and remove) a container
- ## 🔒 Security Features
- ## 🏃 Deployment Flow
- ## 🔍 Troubleshooting
- ### "FORGE_DOMINION_ROOT missing"
- # Check if set
- # Generate new one
- ### "Forge signature invalid"
- ### "Forge epoch skew too large"
- ### "Health check failed"
- # Check container logs
- # Increase retries in bridge.runtime.yaml
- # Verify health endpoint URL is correct
- ### Docker build errors
- # Ensure context is repository root
- # Check Dockerfile exists
- ## 📊 API Endpoints
- ## 🚀 Production Deployment
- ### Systemd Service
- # Copy service file
- # Create environment file
- # Generate production Forge root
- # Enable and start (use generated FORGE_DOMINION_ROOT)
- # Check status
- ### GitHub Actions
- ## 🎨 Frontend Integration
- ## 🔗 Integration Points
- ## 📚 Related Documentation
- ## ⚙️ Next Steps


### ./docs/quickrefs/UMBRA_QUICK_START.md

- # Umbra Unified Triage Mesh - Quick Start
- ## 🚀 Getting Started in 5 Minutes
- ### 1. Enable Umbra (Intent-Only Mode)
- ### 2. Test Signal Ingestion
- ### 3. View Tickets
- # Via API
- # Via CLI
- ### 4. Run Triage Sweep
- ### 5. View Report
- ## 🎯 Common Tasks
- ### Configure Webhooks
- ### Enable Autonomous Healing
- # In .env
- ### View Tickets by Status
- # Open tickets
- # Healed tickets
- # All tickets
- ### Execute Healing Manually
- # Get ticket ID from list
- # Heal specific ticket
- ## 📊 Understanding Health Scores
- ## 🔧 Key Configuration
- ### Minimal Configuration
- ### Recommended Production
- # Set these if using webhooks
- ## 🛠️ Troubleshooting
- ### No tickets appearing?
- ### Webhooks not working?
- ### Heal plans not executing?
- ### PR comments not appearing?
- ## 📚 Documentation
- ## 🎓 Learning Path
- ## ⚡ Quick Commands Reference
- # Status
- # Ingest signal
- # List tickets
- # Run sweep
- # View latest report
- # Generate PR summary
- ## 🔒 Security Best Practices
- ## 💡 Pro Tips
- ## 🆘 Need Help?
- ## 🎉 Success Indicators


### ./docs/quickrefs/ENVSYNC_QUICK_REF.md

- # EnvSync Seed Manifest - Quick Reference
- ## 🎯 What Is This?
- ## 📁 Location
- ## 🚀 Quick Start
- ### 1. Enable EnvSync (in platform dashboards)
- ### 2. Set Platform Credentials
- # Legacy RENDER_SERVICE_ID removed=<your-service-id>
- ### 3. Deploy and Verify
- # Check EnvSync status
- # Trigger manual sync
- ## 📝 How It Works
- ## 🔧 Common Tasks
- ### Add a New Variable
- ### Preview Changes Before Applying
- # See what would change on Render
- # See what would change on Netlify
- ### Manual Sync
- # Sync to both platforms
- # Sync to one platform only
- ### Check Sync Status
- ## 🛡️ Security Notes
- ## 📊 Variables Currently in Manifest
- ## 🔍 Validation
- ## 📚 Full Documentation
- ## 🐛 Troubleshooting
- ### "Manifest not found"
- # Check file exists
- # Verify ENVSYNC_CANONICAL_SOURCE is set to "file"
- ### "Variables not syncing"
- # Check EnvSync is enabled
- # Check logs for errors
- # Look for "EnvSync" in application logs
- ### "Drift keeps appearing"
- ## 🎓 Examples
- ### Example 1: Enable a new feature
- # 1. Edit manifest
- # 2. Validate
- # 3. Commit
- # 4. Deploy - sync happens automatically on next cycle
- # Or trigger immediately:
- ### Example 2: Adjust database pool size
- # Edit manifest
- # Change: DB_POOL_SIZE=10
- # To:     DB_POOL_SIZE=20
- # Validate and commit
- # Deploy - sync on next @hourly cycle or trigger manually


### ./docs/quickrefs/WORKFLOW_FAILURE_QUICK_REF.md

- # Workflow Failure Resolution - Quick Reference
- ## 🚀 Quick Commands
- ### Analyze All Workflows
- ### Generate Fix Plan
- ### Apply Fixes (Use with Caution)
- ## 🔧 Common Fixes
- ### Fix Browser Downloads
- ### Fix Deprecated Actions
- ### Fix Missing Timeouts
- ## 📊 Priority Levels
- ## 🎯 Failure Patterns
- ## 🛠️ Troubleshooting
- ### Browser Install Fails
- ### Workflow Still Fails
- ### Analysis Tool Errors
- ## 📁 Key Files
- ## 🔍 GitHub Actions
- ### Run Diagnostic Sweep
- ### Use Browser Setup
- ## ⚡ Environment Variables
- ### Browser Configuration
- ### Forge Integration
- ## 📞 Support


### ./docs/quickrefs/FORGE_DOMINION_QUICK_REF.md

- # 🜂 Forge Dominion v1.9.7s - Quick Reference
- ## ⚡ Quick Start
- ### 1. Generate Root Key
- ### 2. Bootstrap
- ### 3. Pre-Deploy
- ### 4. Scan Secrets
- ## 🔑 Key Commands
- ## 📊 Module Overview
- ## 🎯 Token Lifecycle
- ## 🛡 Governance Pulse
- ## 🧪 Testing
- ## 🌐 Provider Configuration
- ### GitHub
- ### Netlify
- ### Render
- ## 📈 Visual Pulse Banner
- ## ⚙️ Environment Variables
- ## 🔍 Troubleshooting
- ### No FORGE_DOMINION_ROOT
- # Generate and export
- ### Token validation fails
- # Force renewal
- ### Secrets detected
- ## 📚 Full Documentation


### ./docs/quickrefs/GIT_SOVEREIGN_AGENT_QUICK_REF.md

- # 🌌 Git Sovereign Agent - Quick Reference
- ## 🚀 Quick Import
- ## 📜 Manifest
- # Key Properties
- # Methods
- ## 🜂 SDTF Token Forge
- # Mint Token
- # Validate Token
- # Renew Token
- # Mint All Provider Credentials
- # Returns: {"github": {...}, "netlify": {...}, "render": {...}}
- # Get Status
- ## 🔧 BRH Runtime Handler
- # Deploy Container
- # Orchestrate Runtime
- # Autonomous Heal
- # Create Federation Node
- # Spawn Reality Stream (Branch)
- # Get Status
- ## 🌟 HXO Nexus
- # Resonate Engines
- # Quantum Entangle
- # Bind Reality
- # Enable Emergent Capability
- # Orchestrate All Engines
- # Get Connectivity Map
- # Get Status
- ## 🤖 Autonomous Operations
- # Make Decision
- # Optimize System
- # Alter Reality
- # Heal System
- # Evolve Architecture
- # Create Perfect Version
- # Get Status
- ## 🎮 GitHub Actions
- ### Trigger Workflow
- # Manual trigger
- ### Operations Available
- ### Branch Triggers
- ## 📊 Status Check
- # Quick status of all components
- ## 🧪 Testing
- # Run all tests
- # Run specific component
- # With coverage
- ## 🌌 All 21 Engines
- ## 🔑 Key Constants
- # From manifest.py
- ## 🎯 Common Workflows
- ### Full Sovereignty Activation
- ### System Health Check
- ## 📖 Documentation


### ./docs/quickrefs/COMPLIANCE_QUICK_REF.md

- # Compliance Integration Quick Reference
- ## Overview
- ## API Endpoints
- ### Create Task with Compliance
- ### Get Compliance Validation
- ### Update LOC Metrics
- ## Compliance States
- ## Configuration
- ## Usage Example
- # Create engine
- # Create task with compliance validation (default)
- # Check compliance state
- # Get compliance validation later
- # Update LOC metrics
- ## Disable Compliance (if needed)
- # Disable per task
- ## Benefits


### ./docs/quickrefs/FIREWALL_AUTONOMY_QUICK_REF.md

- # Firewall Intelligence and Autonomy Engine - Quick Reference
- ## Overview
- ## Features
- ## Quick Start
- ### Manual Execution
- # Run the full firewall intelligence + autonomy engine
- # Review autonomy logs
- # Check vault records
- ### GitHub Actions
- # Trigger via GitHub CLI
- # Or manually via GitHub Actions UI:
- # Actions → Firewall Intelligence and Autonomy Engine → Run workflow
- ## How It Works
- ### 1. Intelligence Gathering Phase
- ### 2. Decision-Making Phase
- ### 3. Execution Phase
- ### 4. Reporting Phase
- ## Safety Guardrails
- ## Output Files
- ### Diagnostics
- ### Network Policies
- ### Vault Records
- ## Decision Examples
- ### Example 1: No Issues Detected
- ### Example 2: Low Severity (Auto-Apply)
- ### Example 3: High Severity (Escalate)
- ## Monitoring
- ### Check Execution Status
- # View latest autonomy log
- # View vault records
- # Check severity from report
- ### GitHub Actions Artifacts
- ## Error Signatures Detected
- ## Testing
- ## Workflow Schedule
- ## Related Workflows
- ## Documentation
- ## The Firewall Oath


### ./docs/quickrefs/HXO_QUICK_REF.md

- # HXO Quick Reference
- ## Quick Start
- ### 1. Enable HXO
- ### 2. Submit a Plan
- ### 3. Monitor Status
- # Replace {plan_id} with actual plan ID from step 2
- ## API Endpoints
- ## Job Kinds
- ## Environment Variables
- ### Core Settings
- # Enable/disable HXO
- # Safety limits
- ### Auto-Tuning
- # Split shards if p95 latency exceeds threshold
- ### Storage
- ### RBAC
- ## Plan Structure
- ## Status Response
- ## Genesis Topics
- ### Published by HXO
- ### Subscribed by HXO
- ## Partitioners
- ## Executors
- ## Common Operations
- ### Abort a Plan
- ### Get Final Report
- ### Watch Status in Real-Time
- ## Troubleshooting
- ### Plan Not Starting
- # Check if HXO is enabled
- # Check Genesis bus
- # Check logs
- ### Shards Failing
- # Get status
- # Check failed shard events
- ### Slow Execution
- # Increase concurrency
- # Lower auto-split threshold
- ## File Locations
- ## Integration with TDE-X
- # In TDE-X orchestrator
- ## Capabilities (RBAC)
- ## Best Practices
- ## Further Reading


### ./docs/quickrefs/ENGINES_ENABLE_TRUE_QUICK_REF.md

- # engines_enable_true Quick Reference
- ## 🚀 Quick Commands
- ### Activate All Engines
- ### Check Engine Status
- ### Environment Management
- # Audit environment variables
- # Sync to GitHub
- # Auto-heal environment drift
- ## 📝 Environment Variables
- # Primary activation flag
- # Genesis framework
- # Individual engines (all default to true)
- ## 🔧 Engine Categories
- ### Core Engines (6)
- ### Super Engines (6)
- ### Orchestration (3)
- ### Utility Engines (15)
- ### Integration (1)
- ## 🔒 RBAC Roles
- ## 📊 Activation Report Format
- ## 🧪 Python API Usage
- # Activate all engines
- # Get current status
- ## 🔍 Troubleshooting
- ### Check if an engine is enabled
- ### Disable a specific engine
- ### Re-enable all engines
- ### View activation logs
- ## 📚 Related Documentation
- ## ⚡ Key Features
- ## 👑 "The Bridge stands fully awakened."


### ./docs/quickrefs/GENESIS_V2_QUICK_REF.md

- # Genesis v2.0.0 Quick Reference
- ## What is Genesis?
- ## Quick Start
- ### Enable Genesis (Default: Enabled)
- ### Check Genesis Pulse
- ### View System Map
- ## Genesis Event Topics
- ## Key Endpoints
- ## Environment Variables
- ## Engine Roles
- ## Python API
- ### Publishing Events
- ### Subscribing to Events
- ### Registering Engines
- ### Health Updates
- ## Testing
- # Run Genesis tests
- # Run specific test
- # Run with coverage
- ## Signal Flow
- ## Health Check Response
- ## Troubleshooting
- ### Genesis Not Starting
- # Check mode
- # Enable explicitly
- ### Missing Engines
- # Check manifest
- # Check health
- ### Debug Events
- # Set high trace level
- # Check event history
- ## Key Features
- ## Files Added
- ## Deployment
- ### Render
- ### Local Development
- ## Related Docs


### ./docs/quickrefs/STEWARD_QUICK_REF.md

- # Env Steward v1.9.6l — Quick Reference
- ## Quick Start
- # Enable Steward
- # Run the drift report script
- # Or view the summary only
- ## Overview
- ## Security Model
- ### Admiral-Tier Lock
- ### Default Deny
- ## Configuration
- ### Environment Variables
- # Engine toggles
- # Provider toggles (safe to leave false)
- # Provider identifiers (non-secret)
- # Provider API tokens (secret - leave blank unless enabling write-mode)
- ## API Endpoints
- ### 1. Get Status
- ### 2. Compute Diff
- ### 3. Create Plan
- ### 4. Issue Capability Token (Admiral Only)
- ### 5. Apply Plan (Admiral Only, Write Mode Required)
- ## Usage Flow
- ### Read-Only Mode (Default)
- ### Write Mode (Admiral Only)
- ## Genesis Events
- ## Testing
- ### Unit Tests
- ### Integration Test (Manual)
- # 1. Check status
- # 2. Check diff
- # 3. Create plan
- ### Permission Tests
- # Non-admiral should be denied
- # Expected: 403 {"detail": "steward_admiral_only"}
- # Admiral should succeed
- # Expected: 200 {"enabled": true, ...}
- ## Security Guarantees
- ## Troubleshooting
- ### "steward_admiral_only" error
- ### "Steward engine is disabled"
- ### "Write mode disabled"
- ### "Missing X-Bridge-Cap header"
- ### Adapter errors
- ## Architecture
- ## Best Practices
- ## Next Steps


### ./docs/quickrefs/BLUEPRINT_QUICK_REF.md

- # Blueprint Engine - Quick Reference
- ## API Endpoints
- # Draft blueprint from brief
- # Commit blueprint to mission (creates agent jobs)
- # Get blueprint by ID
- # List all blueprints (filter by captain)
- # Delete blueprint (Admiral only, with relay archival)
- # Get agent jobs for mission
- ## Frontend Components
- ## Database Models
- # Blueprint (plan storage)
- # Agent Job (task execution)
- ## PostgreSQL Setup
- # Initial setup (one-time)
- # Monthly maintenance (automated)
- ## Environment Variables
- # Backend
- # Frontend
- ## RBAC Matrix
- ## Test Commands
- # Run unit tests
- # Run API tests
- # All tests
- ## Example Workflow
- # 1. Draft blueprint
- # → Returns blueprint with ID 1
- # 2. Commit to mission
- # → Creates agent jobs
- # 3. View jobs
- # → Returns list of agent jobs with status
- # 4. Monitor via WebSocket
- # ws://localhost:8000/ws/mission/1
- # → Real-time job status updates
- ## Customization
- # Extend planner rules
- # bridge_backend/bridge_core/engines/blueprint/planner_rules.py
- # Plug in LLM
- # bridge_backend/bridge_core/engines/blueprint/blueprint_engine.py
- ## Common Issues


### ./docs/quickrefs/BRH_CONSENSUS_QUICK_REF.md

- # BRH Consensus & Leader Election - Quick Reference
- ## 🚀 Quick Start
- ### Single Node Setup
- ### Multi-Node Setup
- ## 📋 New Modules
- ## 🎯 Key Features
- ### Leader Election
- ### Container Ownership
- ### Zero-Downtime Handover
- ## 🔌 Forge Endpoints
- ### POST /federation/consensus
- ### GET /federation/leader
- ## 🛡️ API Gating
- ### Deploy Endpoint
- # Leader node - accepts deploy
- # Response: {"status": "restarted", "image": "myapp:latest"}
- # Witness node - rejects deploy
- # Response: {"status": "ignored", "reason": "not-leader"}
- ## 🔧 Testing
- ### Run Unit Tests
- ### Run Integration Tests
- ## 📊 Logging
- ### Heartbeat Logs
- ### Consensus Logs
- ### Role Transition Logs
- ## ⚙️ Configuration Files
- ### bridge.runtime.yaml
- ### Environment Variables
- ## 🔍 Troubleshooting
- ### Check Current Leader
- ### Check Node Role
- ### Verify Consensus Working
- # Watch logs for consensus broadcasts
- ### Container Ownership Check
- # List containers with ownership labels
- ## 📚 Full Documentation


### ./docs/quickrefs/GENESIS_LINKAGE_QUICK_REF.md

- # Genesis Linkage Quick Reference - UNIFIED EDITION
- ## v1.9.7c Feature Summary
- ### Engine Count: 20
- ## Key Components
- ## Engine Categories
- ### Core Infrastructure (6)
- ### Super Engines (6) - Coordinated by Leviathan
- ### Orchestration (1)
- ### Utility Engines (7)
- ## Quick Start
- ### Enable Linkage
- ### Test Endpoints
- # Check status
- # Get manifest
- # Initialize linkages
- ## API Endpoints
- ## Event Bus Topics (33 Total)
- ### Core Topics (5)
- ### Super Engine Topics (12)
- ### Orchestration Topics (2)
- ### Utility Topics (14)
- ## Engine Dependencies
- ## Python API
- # Load manifest (20 engines)
- # Get specific engine
- # Get dependencies
- # Validate integrity
- ### Working with Adapters
- # Super Engines
- # Returns: ['calculuscore', 'qhelmsingularity', 'auroraforge', ...]
- # Utility Engines
- # Returns: ['creativity', 'indoctrination', 'screen', ...]
- # Leviathan
- ## Testing
- # Run validation script
- # Run all linkage tests
- # Run deployment readiness check
- # Run integration test
- ## Signal Flow
- ## Configuration
- ## Files Changed
- ### New Files (3 adapters + 2 docs)
- ### Modified Files (3)
- ## Quick Validation
- # Check all engines loaded
- # Expected: 20
- # Check super engines
- # Expected: 6
- # Check utility engines  
- # Expected: 7
- # Check Leviathan coordination
- # Expected: 6
- ## Summary Stats
- ## Files Added
- ## Troubleshooting
- ## Next Steps


### ./docs/archive/PHASE_6_VERIFICATION.md

- # Phase 6 - Final Verification Report
- ## Implementation Status: ✅ COMPLETE
- ### Date: 2025-11-04
- ### Branch: copilot/add-chaos-injector
- ## Implementation Summary
- ### Components Delivered
- ## Test Coverage
- ### Unit Tests: 14/14 Passing ✅
- ### Build Validation
- ## Code Quality
- ### Code Review
- ### Security Considerations
- ### Performance
- ## Files Changed
- ### New Files (7)
- ### Modified Files (5)
- ### Documentation (2)
- ## Deployment Readiness
- ### Prerequisites Met
- ### Configuration Options
- # Chaos Injector (disabled by default)
- # Recovery Watchtower (enabled by default)
- # Frontend API Configuration
- ### Environment Variables
- ## CI/CD Validation
- ### Local Validation ✅
- ### Pending CI/CD Checks
- ## Security Summary
- ### Vulnerabilities Found: 0
- ### Security Improvements
- ## Recommendations
- ### Immediate Next Steps
- ### Future Enhancements
- ## Sign-Off


### ./docs/archive/LOC_REPORT.md

- # SR-AIbridge - Lines of Code Report
- ## Summary
- ## Breakdown by File Type
- ## Detailed File List by Category
- ### Python (278 files, 30,252 lines)
- ### Markdown (94 files, 23,413 lines)
- ### JSON (7 files, 9,330 lines)
- ### JavaScript/TypeScript (140 files, 8,542 lines)
- ### Unknown (27 files, 2,540 lines)
- ### YAML (44 files, 2,316 lines)
- ### CSS (2 files, 2,219 lines)
- ### Shell (5 files, 718 lines)
- ### SQL (3 files, 492 lines)
- ### Other (6 files, 298 lines)
- ### HTML (2 files, 121 lines)
- ### TOML (1 files, 30 lines)


### ./docs/archive/CHIMERA_IMPLEMENTATION_COMPLETE.md

- # 🚀 Project Chimera v1.9.7c — Implementation Complete
- ## 🎯 Mission Accomplished
- ## 📦 Deliverables
- ### Core Engine (7 files)
- ### CLI Tool (1 file)
- ### Documentation (6 files)
- ### Testing (1 comprehensive suite)
- ### System Integration
- ## 🧩 Architecture Overview
- ## 📊 Performance Metrics
- ## 🧪 Test Results
- ## 🌐 Genesis Bus Integration
- ## 🛠️ Usage Examples
- ### CLI
- # Simulate Netlify deployment
- # Deploy to Render with certification
- # Monitor deployment status
- # Verify with Truth Engine
- ### API
- # Get Chimera status
- # Simulate deployment
- # Deploy with certification
- ### Python
- ## 🔒 Security Features
- ## 📈 Impact Analysis
- ## 🎯 Supported Platforms
- ## 🚦 Status Indicators
- ## 🔮 Future Enhancements
- ## 🎓 Learning Resources
- ## 🏆 Final Declaration
- ## ✅ Sign-Off


### ./docs/archive/INTEGRATION_COMPLETE.md

- # 🎉 Integration Complete - Autonomy Engine with Originality Verification
- ## Mission Accomplished
- ## What Was Built
- ### 1. Enhanced Autonomy Engine
- ### 2. Enhanced Task Contracts
- ### 3. Three Engines Working Together
- #### Anti-Copyright Engine (Counterfeit Detection)
- #### Compliance Engine (License Scanning)
- #### LOC Engine (Code Metrics)
- ## Files Changed
- ### Core Implementation (3 files)
- ### Tests (1 file)
- ### Documentation (5 files)
- ## Commits Made
- ## How It Works
- ## Compliance States
- ## Configuration
- ## API Examples
- ### With Originality Check (Default)
- ### Without Originality Check
- ## Testing Results
- ## Benefits Delivered
- ## Documentation Created
- ## Future Enhancements
- ## Conclusion


### ./docs/archive/FORGE_DOMINION_IMPLEMENTATION_SUMMARY.md

- # 🜂 Forge Dominion v1.9.7s - Implementation Summary
- ## Overview
- ## What Was Built
- ### Core Achievement
- ## Components Delivered
- ### Python Modules (7 files)
- ### Infrastructure Scripts (2 files)
- ### CI/CD Workflow (1 file)
- ### Assets (1 file)
- ### Documentation (3 files)
- ### Tests (1 file)
- ## Technical Specifications
- ### Cryptography
- ### Token Lifecycle
- ### Governance
- ### Providers Supported
- ## Security Guarantees
- ## Testing Coverage
- ### Unit Tests (26 tests)
- ### Integration Test
- ### Compatibility Tests
- ## Deployment Flow
- ## Files Changed/Added
- ### New Files (13)
- ### Modified Files (4)
- ### Total Lines of Code
- ## Environment Variables
- ## GitHub Setup Commands
- # Set secret
- # Set variables
- ## Integration Points
- ## Next Steps (Optional Enhancements)
- ## Lore
- ## Seal of Dominion


### ./docs/archive/DOCKDAY_SUMMARY.md

- # 🚢 Dock-Day Ascension: Complete Implementation Summary
- ## Overview
- ## Core Features Implemented
- ### 1. Backend Dock-Day Export System (`bridge_backend/src/export_and_sign.py`)
- ### 2. API Integration (`bridge_backend/bridge_core/routes_custody.py`)
- ### 3. Frontend Integration (`bridge-frontend/src/components/AdmiralKeysPanel.jsx`)
- ### 4. Ritual Scripts (`rituals/finalizedockdaydrop.sh`)
- ### 5. CSS Styling (`bridge-frontend/src/styles.css`)
- ## Technical Architecture
- ### Export Process Flow
- ### Security Features
- ### File Structure in Drops
- ## Example Usage
- ### CLI Export
- ### API Usage
- ### Ritual Finalization
- ## Testing Evidence
- ## Admiral's Notes


### ./docs/archive/PR_SUMMARY.md

- # PR: Mission Blueprint Engine + Mission Log v2
- ## Why
- ## What's in this PR
- ### Backend ✅
- ### Frontend ✅
- ### Tests ✅
- ## File Tree (New/Changed)
- ## Backend - Models (Additions)
- # bridge_backend/models.py
- ## How This Shifts the Product
- ## Rollout Instructions
- ### 1. Database Migration
- # Base tables (if not already applied)
- # Blueprint + agent_jobs tables
- ### 2. Backend Startup
- ### 3. Frontend Build
- ### 4. Try It
- ## Acceptance Criteria
- ## Testing
- ## What's Next
- ## Support & Documentation


### ./docs/archive/HXO_IMPLEMENTATION_SUMMARY.md

- # HXO Implementation Summary — v1.9.6p (HXO Ascendant)
- ## What Was Delivered
- ## Core Components Implemented
- ### 1. HXO Engine Core (`bridge_backend/engines/hypshard_x/`)
- ### 2. Integration Adapters (`bridge_backend/bridge_core/engines/adapters/`)
- ### 3. Tests (`bridge_backend/tests/`)
- ### 4. Documentation (`docs/`)
- ### 5. Quick Reference (`HXO_QUICK_REF.md`)
- ## Integration Points
- ### Genesis Event Bus
- ### Main Application
- ### Configuration
- ## Features Delivered
- ### ✅ Adaptive Sharding
- ### ✅ Content-Addressed Deduplication
- ### ✅ Merkle Aggregation
- ### ✅ Idempotent Execution
- ### ✅ Resumable Across Redeploys
- ### ✅ Backpressure & Rate Control
- ### ✅ Self-Healing with Autonomy
- ### ✅ Truth Certification
- ### ✅ Blueprint Schema Contract
- ### ✅ Parser Plan Ingestion
- ### ✅ RBAC (Admiral-Locked)
- ## API Endpoints
- ## Configuration
- # Enable/disable
- # Safety/timebox
- # Auto-tuning
- # Storage
- # RBAC
- ## Testing Summary
- ### Import Tests
- ### Functional Tests
- ### Integration Tests
- ## File Structure
- ## No New Dependencies
- ## Rollback Plan
- ## Next Steps (Optional Enhancements)
- ## Security & Safety
- ## Strengths Added
- ## Total Delivery
- ## Permanent Solution, No Duct Tape
- ## Ready to Merge


### ./docs/archive/V196I_SUMMARY.md

- # 🎉 v1.9.6i — IMPLEMENTATION COMPLETE
- ## 📋 Executive Summary
- ### Key Results
- ## 🏗️ Architecture
- ### 3-Stage Deployment Model
- ## 📦 Deliverables
- ### Code Files (5 new, 5 modified)
- ### Documentation Files (3)
- ## 🧪 Testing
- ### Test Suite Results
- ### Test Coverage
- ### Startup Sequence Validation
- ## 🚀 Features
- ### 1. Temporal Deploy Buffer (TDB)
- ### 2. Stage Orchestration
- ### 3. Dynamic Port Alignment
- ### 4. Health Monitoring
- ### 5. Fail-Fast Guardrails
- ## 📊 Performance Impact
- ### Before v1.9.6i (Synchronous Startup)
- ### After v1.9.6i (TDB Async Startup)
- ### Improvement Summary
- ## ⚙️ Configuration
- ### Environment Variables
- ### Usage Examples
- ## 🌐 API Endpoints
- ### `GET /health/live`
- ### `GET /health/stage`
- ## 🔧 Deployment
- ### Pre-Deployment Checklist
- ### Deployment Steps
- ### Expected Logs
- ## 🛡️ Safety & Compatibility
- ### Backward Compatibility
- ### Rollback Plan
- # Option 1: Git revert
- # Option 2: Disable TDB
- ### Safety Features
- ## 📈 Success Metrics
- ### Deployment Success
- ### Performance Goals Met
- ## 🎓 Learning & Innovation
- ### Technical Innovations
- ### Best Practices Applied
- ## 📚 Documentation
- ### User Guides
- ### Developer Resources
- ## 🏁 Conclusion
- ### Next Steps
- ## 🙏 Acknowledgments


### ./docs/archive/TASK_COMPLETE_SUMMARY.md

- # Parity Engine Run - Task Completion Summary
- ## 🎯 Objective
- ## ✅ Status: COMPLETE
- ## 📦 What Was Done
- ### 1. Parity Analysis Executed
- ### 2. Auto-Fix Applied
- ### 3. Testing & Verification
- ### 4. Documentation Created
- ## 📊 Key Metrics
- ### Communication Health: ✅ HEALTHY
- ## 📁 Files Added to Repository
- ### Documentation (3 files)
- ### Scripts (1 file)
- ### Generated Code (85+ files)
- ### Reports (2 files - not tracked, auto-generated)
- ## 🚀 Quick Verification
- ## 🔍 Critical Findings
- ### ✅ Auto-Repaired (Frontend stubs generated)
- ### ⚠️ Requires Manual Implementation (Backend)
- ## 📚 How to Use the Results
- ### For Frontend Developers
- ### For Backend Developers
- # Example: Implement missing chat endpoint
- ### For DevOps/Monitoring
- # Full parity check workflow
- ## 🎉 Success Criteria - All Met ✅
- ## 📖 Additional Resources
- ## 🎯 Next Steps for the Team


### ./docs/archive/DEPLOYMENT_CHECKLIST_v196b.md

- # v1.9.6b Deployment Checklist
- ## 🚀 SR-AIbridge v1.9.6b — Route Integrity Sweep, Auto-Healing Runtime & Deployment Guard
- ## ✅ Pre-Deployment Verification
- # 1. Run route sweep validator
- # 2. Run tests
- # 3. Lint check
- # 4. Verify imports
- ## 🔹 Render (Backend) Deployment
- ### Configuration
- ### Environment Variables
- ### Deployment Steps
- ## 🔹 Netlify (Frontend) Deployment
- ### Configuration
- ## 🔹 GitHub Actions CI/CD
- ### Workflow: Bridge Integrity CI
- ### CI Failure Scenarios
- # ❌ Before (unsafe)
- # ✅ After (safe)
- ## 🧩 New Components in v1.9.6b
- ### 1. Database Bootstrap (`bridge_backend/db/bootstrap.py`)
- ### 2. Header Sync Middleware (`bridge_backend/middleware/headers.py`)
- ### 3. Route Sweep Check (`tools/route_sweep_check.py`)
- ### 4. GitHub Actions Workflow (`.github/workflows/bridge-ci.yml`)
- ## 🔧 Troubleshooting
- ### Port Binding Issues
- ### Database Connection Errors
- ### CORS Errors
- ### Heartbeat Not Running
- ## 📊 Health Check Endpoints
- ## 🏁 Deployment Success Criteria
- ## 🔮 Version Info
- ## 📞 Support


### ./docs/archive/EAN_EXECUTION_RESULTS.md

- # EAN (Embedded Autonomy Node) Execution Results
- ## 🚀 Full EAN Run - October 13, 2025
- ### Execution Summary
- ### Results
- ### Cycle Pipeline
- ### Findings & Fixes
- ### Certification
- ### Report Location
- ### Integration Status
- ### Next Steps
- ### Notes


### ./docs/archive/BRIDGE_REPAIR_SUMMARY.md

- # SR-AIbridge Complete Repair Summary
- ## Mission Briefing
- ## Mission Status: COMPLETE ✅
- ## Problems Identified and Solutions Deployed
- ### 1. Import Path Configuration Failure ❌ → ✅
- ### 2. Database Async Driver Mismatch ❌ → ✅
- ### 3. Engine Linkage System Disabled ❌ → ✅
- ### 4. Blueprint Import Path Errors ❌ → ✅
- ## Bridge Systems Status
- ### 🟢 ALL SYSTEMS OPERATIONAL
- ## Validation Test Results
- ### Test 1: Backend Connectivity ✅
- ### Test 2: Health Check ✅
- ### Test 3: Engine Linkage ✅
- ### Test 4: Security Scan ✅
- ## Performance Metrics
- ## Code Changes Summary
- ### Modified Files (3 + 1 new)
- ### Lines Changed
- ## Security Status
- ## Remaining Non-Critical Warnings
- ## What's Working Now
- ## Deployment Readiness
- ## Admiral's Authorization Fulfilled
- ## Conclusion


### ./docs/archive/OPERATION_GENESIS_SUMMARY.md

- # Operation Genesis: Triage Pre-Seed Implementation Summary
- ## ✅ Implementation Complete
- ## 🎯 Objective Achieved
- ## 📦 Deliverables
- ### Backend Components
- ### Integration
- ### CI/CD
- ### Frontend
- ### Documentation
- ## 🧪 Testing Results
- ### Unit Tests
- ### Integration Tests
- ### Validation Tests
- ## 🔄 Event Flow
- ## 📊 Impact Analysis
- ### Before
- ### After
- ## 🔧 Technical Details
- ### Generated File Structure
- ### File Locations
- ### Dependencies
- ## 🚀 Deployment Checklist
- ## 📝 Usage
- ### Automatic (Recommended)
- ### Manual Trigger via GitHub Actions
- ### Manual Trigger via CLI
- ## 🔗 Integration Points
- ## 🎓 Developer Notes
- ## 📈 Metrics
- ## ✨ Success Criteria
- ## 🎉 Final Status


### ./docs/archive/V196L_STEWARD_SUMMARY.md

- # 🎉 v1.9.6l — Env Steward IMPLEMENTATION COMPLETE
- ## Admiral-Tier Environment Orchestration
- ## What Was Built
- ### New Engine: Env Steward
- ## File Structure
- ## Integration Points
- ### 1. Genesis Event Bus
- ### 2. Permissions Middleware
- ### 3. Main Application
- ### 4. Environment Configuration
- # Engine toggles
- # Provider toggles
- # Provider identifiers (non-secret)
- # Provider tokens (secret - leave blank)
- ## API Endpoints
- ### GET /api/steward/status
- ### POST /api/steward/diff
- ### POST /api/steward/plan
- ### POST /api/steward/cap/issue
- ### POST /api/steward/apply
- ## Security Guarantees
- ### 1. Default Deny
- ### 2. Admiral-Tier Lock
- ### 3. Least Authority
- ### 4. No Secret Echo
- ### 5. Loop-Safe
- ### 6. Short-Lived Capabilities
- ## Testing
- ### Unit Tests
- ### Integration Tests
- # Check status
- # Non-admiral should be denied
- # Expected: 403 {"detail": "steward_admiral_only"}
- # Compute diff
- # Create plan
- ## Deployment Checklist
- ### Pre-Deployment
- ### Deployment
- ### Optional: Enable Write Mode
- ## What's Next?
- ### Phase 1: Monitoring (Current)
- ### Phase 2: Write Operations (When Ready)
- ### Phase 3: Full Integration (Future)
- ## Key Features
- ### 1. Admiral-Tier Lock
- ### 2. Capability Tokens
- ### 3. Provider Adapters
- ### 4. Genesis Integration
- ### 5. Phased Execution
- ### 6. Rollback Support
- ## Documentation
- ## Summary


### ./docs/archive/IMPLEMENTATION_BRIDGE_DEPLOY.md

- # Bridge Deployment Infrastructure - Implementation Summary
- ## Overview
- ## What Was Implemented
- ### 1. Netlify Configuration (`bridge-frontend/netlify.toml`)
- ### 2. GitHub Actions Workflow (`.github/workflows/bridge-deploy.yml`)
- ### 3. Runtime Exporter (`bridge_backend/forge/export_runtime.py`)
- ### 4. Dominion Seal (`assets/dominion-seal.svg`)
- ### 5. README Updates
- ### 6. Documentation (`BRIDGE_DEPLOY_GUIDE.md`)
- ## Testing Results
- ## User Action Required
- ## File Sizes
- ## Status
- ## Next Steps
- ## Benefits


### ./docs/archive/POST_MERGE_SETUP.md

- # Post-Merge Setup Guide
- ## 🚀 Congratulations! The cherry is on top! 🍒
- ## Immediate Actions (Required)
- ### 1. Enable Genesis Mode ✅
- ### 2. Verify Deployment ✅
- # Check webhook status
- # Check autonomy deployment status  
- # Should return:
- # {
- #   "genesis_enabled": true,
- #   "platforms_monitored": ["netlify", "render", "github"],
- #   "status": "active"
- # }
- ## Optional Actions (Recommended)
- ### 3. Configure Netlify Webhook (Optional) 🔔
- ### 4. Configure Render Webhook (Optional) 🔔
- ### 5. Configure GitHub Webhook (Optional) 🔔
- ## Testing the Integration
- ### Test 1: GitHub Actions (Already Working) ✅
- ### Test 2: Manual Event Publishing
- # Test from your local machine or via SSH to Render
- ### Test 3: Webhook Testing
- ### Test 4: Verification Script
- ## Monitoring and Observability
- ### View Deployment Events
- ### Monitor Render Logs
- ### Monitor Autonomy Engine
- ## Troubleshooting
- ### Issue: Genesis Mode Not Enabled
- ### Issue: Webhooks Not Receiving Events
- ### Issue: GitHub Actions Not Publishing
- ## What Happens Now?
- ### On Every Deployment:
- ### Integration Benefits:
- ## Documentation
- ## Support
- ## Next Enhancements (Future)
- ## Conclusion


### ./docs/archive/V196I_IMPLEMENTATION_COMPLETE.md

- # SR-AIbridge v1.9.6i — Implementation Complete ✅
- ## 🎯 Problem Solved
- ## 🌊 Solution: Temporal Deploy Buffer (TDB)
- ### Result
- ## 📁 Files Added/Modified
- ### New Files
- ### Modified Files
- ## 🚀 Core Features
- ### 1. Temporal Deploy Buffer (TDB)
- # Get deployment status
- ### 2. Temporal Stage Manager
- # Create a stage
- # Add tasks
- # Add to manager
- # Run all stages
- ### 3. Dynamic Port Alignment
- ### 4. Health Stage Endpoint
- ## ⚙️ Configuration
- ### Environment Variables
- ### Disabling TDB
- ## 🧪 Testing
- ### Test Suite
- ## 📊 Deployment Flow
- ### Stage 1: Minimal Health Check (1-2 seconds)
- ### Stage 2: Core Bootstrap (Background, 5-15 seconds)
- ### Stage 3: Federation Warmup (Background, 10-20 seconds)
- ## 🔍 Monitoring
- ### Real-Time Stage Monitoring
- # Check current stage
- # Watch for completion
- ### Diagnostics Files
- ## 🛡️ Fail-Fast Guardrails
- ### Critical vs Non-Critical Tasks
- ### Retry Logic
- ### Graceful Degradation
- ## 🚦 Success Criteria
- ## 📈 Performance Metrics
- ### Startup Time Comparison
- ### Stage Duration Benchmarks
- ## 🔄 Rollback Plan
- # In Render dashboard or .env
- ## 📚 Version Information
- ## 🎉 Summary
- ## 🤝 Contributing


### ./docs/archive/V197C_IMPLEMENTATION_COMPLETE.md

- # v1.9.7c Genesis Linkage - Implementation Complete
- ## 🎉 Status: READY FOR DEPLOYMENT
- ## Summary
- ## What Was Implemented
- ### Core Components (8 new files)
- ### Modified Files (2)
- ### Testing (3 files)
- ### Documentation (2 files)
- ## Test Results
- ### Unit Tests
- # Result: 13 passed ✅
- ### Integration Test
- # Result: All integration tests passed ✅
- ### Deployment Readiness
- # Result: ALL CHECKS PASSED ✅
- ### Existing Tests (Regression Check)
- # Result: 7 passed ✅
- ## Key Linkage Points
- ### 🔹 Blueprint → TDE-X
- ### 🔹 Blueprint → Cascade
- ### 🔹 Blueprint → Truth
- ### 🔹 Blueprint → Autonomy
- ## API Endpoints
- ## Event Bus Topics
- ## Configuration
- ### Environment Variables
- ### Deployment Settings (Render/Production)
- ## Benefits Delivered
- ## Files Changed Summary
- ## Verification Commands
- ### Check Integration
- ### Check Deployment Readiness
- ### Run All Tests
- ## Next Steps for Deployment
- ## Rollback Plan
- ## Additional Resources


### ./docs/archive/V196B_IMPLEMENTATION_SUMMARY.md

- # v1.9.6b Implementation Summary
- ## 🎯 Objectives Achieved
- ## 📁 Files Created
- ### Core Components
- ### Tests
- ### Documentation
- ## 🔧 Files Modified
- ## ✅ Verification Results
- # Route Sweep Check
- # Component Imports
- # File Verification
- # Linting
- # Application Boot
- ## 🚀 Deployment Ready
- ### Render (Backend)
- ### Netlify (Frontend)
- ### GitHub Actions
- ## 🧩 Architecture Highlights
- ### 1. Route Integrity Sweep
- ### 2. Database Auto-Sync
- ### 3. Header Synchronization
- ### 4. CI Validation Pipeline
- ## 📊 Testing Coverage
- ## 🔮 Next Steps (v1.9.7 Preview)
- ## 🏁 Conclusion
- ## 📞 Contact


### ./docs/archive/NETLIFY_DEPLOYMENT_FIX_SUMMARY.md

- # Netlify Deployment Fix Summary
- ## Overview
- ## Original Issues
- ### 1. Build Script Path Resolution Error
- ### 2. Node.js Version Mismatch
- ### 3. Deprecated NPM Packages
- ### 4. Lack of Error Reporting
- ## Files Modified
- ### 1. `netlify.toml` (Root)
- ### 2. `bridge-frontend/netlify.toml` (DELETED)
- ### 3. `bridge-frontend/package.json`
- ### 4. `bridge-frontend/package-lock.json`
- ### 5. `scripts/netlify_build.sh`
- # Error reporting function
- # Set up error trap
- ### 6. `.gitignore`
- ## Testing Performed
- ### Local Build Test
- ### Security Scans
- ## Expected Netlify Build Behavior
- ## Error Reporting Example
- ## Next Steps
- ## Maintenance Notes
- ## Contact


### ./docs/archive/BRH_IMPLEMENTATION_COMPLETE.md

- # Bridge Runtime Handler (BRH) - Implementation Summary
- ## Overview
- ## What Was Built
- ### Core System (646+ lines of code)
- ### Integration & Deployment
- ### Documentation & Examples
- ## Key Features
- ### Security
- ### Reliability
- ### Flexibility
- ### Integration
- ## Architecture
- ## Commits Made
- ## Files Added/Modified
- ### New Files (15)
- ### Modified Files (1)
- ## Testing & Validation
- ### Tested Components
- ### Code Review
- ## Security Enhancements
- ## Usage
- ### Quick Start
- # 1. Generate Forge root
- # 2. Set environment (from output)
- # 3. Install and run
- ### Production Deployment
- # Systemd service
- ## Next Steps for User
- ## Benefits Over Render
- ## Conclusion


### ./docs/archive/STEWARD_JSON_REPORT_QUICK_START.md

- # 🎯 Quick Answer: Environment Drift JSON Report
- ## What You Asked For
- ## ✅ Done!
- ## 🚀 How to Use It
- ### Method 1: Quick Script (Easiest)
- # Enable Steward
- # Get the JSON report
- ### Method 2: Via API
- ## 📄 What You Get
- ## 🔍 What It Does
- ## 📝 Note About API Credentials
- # For Render
- # For Netlify
- # For GitHub
- ## 🛡️ Safety
- ## 📚 More Info
- ## 🎉 You're All Set!


### ./docs/archive/CHECKLIST_COMPLETION_SUMMARY.md

- # ✅ SR-AIbridge Roles & Interface Checklist - COMPLETION SUMMARY
- ## Overview
- ## Checklist Status
- ### ✅ 1. Dashboard (Main Display)
- ### ✅ 2. Captain's Chat
- ### ✅ 3. Captain-to-Captain Chat
- ### ✅ 4. Vault
- ### ✅ 5. Brain
- ### ✅ 6. Custody
- ### ✅ 7. System Health
- ## RBAC Enhancements
- ### Updated Permission Matrix
- ### Middleware Enforcement Added
- ## Files Changed
- ### Backend (4 files modified):
- ### Documentation (2 files created):
- ## Benefits Delivered
- ### ✅ Clean UX
- ### ✅ Data Isolation
- ### ✅ Operational Sovereignty
- ### ✅ Captain Autonomy
- ### ✅ Security
- ## Testing Verification
- ## What Was NOT Changed
- ## Conclusion


### ./docs/archive/ENVIRONMENT_CLEANUP_SUMMARY.md

- # 🜂 Environment Cleanup Complete - Sovereign Dominion Token Forge Integration
- ## 📋 Executive Summary
- ### Key Achievement
- ## 🎯 What Was Done
- ### 1. Environment Files Cleaned ✅
- #### Main Environment Files
- #### Example/Template Files
- ### 2. Placeholder Pattern Established ✅
- ### 3. GitHub Actions Integration ✅
- ### 4. Workflow Migration ✅
- ### 5. Documentation Created ✅
- ## 🔐 Security Verification
- ### Secret Scanner Results
- ### Token Minting Test
- ## 📊 Before vs After
- ### Before Token Forge Integration
- # .env file
- ### After Token Forge Integration
- # .env file
- # GitHub Secrets
- ## 🔄 Token Lifecycle
- ### How It Works
- ### Providers Supported
- ## 📚 Key Files Created/Modified
- ### New Files
- ### Modified Files
- ## 🚀 Getting Started
- ### For Developers
- ### For Workflows
- ### For Production
- ## 📖 Documentation
- ### Primary Documents
- ### Helper Scripts
- ### Token Forge Modules
- ## ✅ Verification Checklist
- ## 🎯 Next Steps (Optional)
- ## 🏆 Achievement Unlocked
- ## 📞 Support


### ./docs/archive/V195_IMPLEMENTATION_COMPLETE.md

- # SR-AIbridge v1.9.5 — Implementation Complete ✅
- ## 🎯 Mission: Unified Runtime & Autonomic Homeostasis
- ## 📦 What Was Delivered
- ### Core Features Implemented
- #### ✅ 1. Self-Healing Heartbeat System
- #### ✅ 2. Bridge Doctor CLI Tool
- #### ✅ 3. Render ↔ Netlify Parity Layer
- #### ✅ 4. Federation Diagnostics Endpoint
- #### ✅ 5. Improved Runtime Startup
- #### ✅ 6. Updated Main Application
- #### ✅ 7. Auto-Repair Branding Update
- #### ✅ 8. Comprehensive Documentation
- ## 🧪 Testing & Validation
- ### Test Coverage
- #### New Tests (21 tests)
- #### Updated Tests
- ### Test Results
- ### Module Import Verification
- ## 📊 Code Changes Summary
- ### New Files Created
- ### Files Modified
- ### Cleanup
- ## 🚀 Deployment Readiness
- ### Expected Startup Sequence (Render)
- ### Health Check Endpoints
- ### Testing Deployment
- # Test federation diagnostics
- # Test basic health
- # Run local diagnostics
- ## 🎓 Key Achievements
- ### 1. **True Autonomic Homeostasis**
- ### 2. **Permanent Platform Parity**
- ### 3. **Diagnostic Visibility**
- ### 4. **Zero-Drift Deployment**
- ### 5. **Comprehensive Documentation**
- ## 🔬 Implementation Quality
- ### Code Quality
- ### Test Quality
- ### Documentation Quality
- ## 📝 Git Commit Summary
- ### Commits in this PR
- ## 🎉 Final Status
- ### ✅ All Requirements Met
- ### 🚢 Ready for Merge
- ## 💬 Quote from Prim


### ./docs/archive/GENESIS_V2_0_2_IMPLEMENTATION_SUMMARY.md

- # Genesis v2.0.2 Implementation - Complete Summary
- ## 🎉 Implementation Status: COMPLETE
- ### Date: 2025-10-11
- ### Version: Genesis v2.0.2 - EnvRecon + HubSync + Auto-Heal + Inspector Panel
- ## ✅ Deliverables Completed
- ### Core Engine Components
- ## 🧪 Verification Results
- ### Unit Tests
- ### Integration Tests
- ### API Endpoints Verified
- ### Application Startup
- ## 📊 Features Implemented
- ### 🔍 Cross-Platform Reconciliation
- ### 🤝 HubSync Layer
- ### 🩹 Auto-Healing Subsystem
- ### 🧭 Inspector Panel
- ### 🖥️ CLI Interface
- ## 🏗️ Architecture
- ## 📦 Files Created/Modified
- ### New Files (10)
- ### Modified Files (2)
- ### Total Lines of Code
- ## 🎯 Requirements Met
- ## 🚀 How to Use
- ### Quick Start
- # 1. Run audit
- # 2. View report
- # 3. Access Inspector Panel
- # http://localhost:8000/genesis/envrecon
- # 4. Trigger healing
- ### Environment Setup
- # Add to .env
- ## 🔐 Security Features
- ## 📈 Performance
- ## 🎨 UI Preview
- ## 🔄 Integration Points
- ### Existing Systems
- ### Future Enhancements
- ## ✨ Summary
- ## 🔄 Autonomous Diagnostic Handoff (v1.9.6k Update)
- ### Overview
- ### Removed External Dependencies
- ### Internal Telemetry Architecture
- ### Key Benefits
- ### Diagnostic Flow Examples
- ## 📞 Next Steps


### ./docs/archive/QUICK_VERIFICATION_SUMMARY.md

- # 🎯 Quick Verification Summary - v1.8.2 Total-Stack Triage Mesh
- ## ✅ TL;DR - Everything is VERIFIED and WORKING
- ## 📊 What Got Verified
- ### 1️⃣ GitHub Actions Workflows (5 new workflows) ✅
- ### 2️⃣ Python Scripts (6 scripts) ✅
- ### 3️⃣ Documentation (2 files) ✅
- ### 4️⃣ Report Generation (5 report types) ✅
- ## 🧪 Test Suite Results
- ## 🎯 What This Means
- ## 📝 Files Added/Modified in This Verification
- ## 🚀 Ready to Use
- ## 📄 Full Details


### ./docs/archive/ENVRECON_AUTONOMY_SUMMARY.md

- # EnvRecon-Autonomy Integration - Implementation Summary
- ## What Was Completed
- ### 1. Created EnvRecon-Autonomy Adapter Link ✅
- ### 2. Added Genesis Bus Topics ✅
- ### 3. Integrated Adapter with EnvRecon Core ✅
- ### 4. Enhanced AutoHeal with Genesis Events ✅
- ### 5. Updated Routes with Healing Notifications ✅
- ### 6. Registered EnvRecon in Genesis Linkage System ✅
- ### 7. Created Comprehensive Documentation ✅
- ### 8. All Tests Passing ✅
- ## What Variables Cannot Be Auto-Fixed
- ### Current Limitation
- ### API Credentials Required (Must Configure First)
- # Render API
- # Netlify API
- # GitHub API
- ### All Variables Require Manual Sync
- ### Why Auto-Sync Doesn't Work Yet
- ## How to Get Missing Variables List
- ### Step 1: Configure API Credentials
- # Render (get from https://dashboard.render.com → Account Settings → API Keys)
- # Netlify (get from https://app.netlify.com → User Settings → Applications)
- # GitHub (get from Settings → Developer settings → Personal access tokens)
- ### Step 2: Run Audit
- ### Step 3: Get Report
- ### Step 4: Review Missing Variables
- ### Step 5: Manual Sync
- ### Step 6: Verify
- ## Integration Benefits
- ### 1. Automated Drift Detection
- ### 2. Centralized Monitoring
- ### 3. Genesis Event Stream
- ### 4. Deployment Integration
- ### 5. Audit Trail
- ## Next Steps for Full Auto-Sync
- ## Files Changed
- ## Summary


### ./docs/archive/V196_FINAL_IMPLEMENTATION.md

- # v1.9.6-Final — The Bridge Stabilization Protocol
- ## Summary
- ## What Was Fixed
- ### 1. Port Binding Issue (Render Timeouts)
- ### 2. FastAPI/Pydantic Import Crash
- ### 3. Safe Import System (Never Again Guardrails)
- ### 4. Dependencies Update
- ## Boot Diagnostics
- ## Never Again Guardrails
- ## Testing
- ## Deployment Notes
- ### Render
- ### Local Development
- ## Rollback Plan
- ## Files Modified
- ## Verification


### ./docs/archive/V196D_IMPLEMENTATION_COMPLETE.md

- # v1.9.6d — Runtime Intelligence Core Implementation
- ## Summary
- ## Changes Made
- ### 1. Version Updates
- ### 2. Render Port & Process Launch
- ### 3. Heartbeat Auto-Detection & Quiet Mode
- ### 4. Predictive Stabilizer: Learn & Resolve Tickets
- ### 5. Route Integrity Sweep
- ### 6. Blueprint Engine Optional
- ## Testing Results
- ## Deployment Instructions
- ### 1. Render Configuration
- ### 2. Optional: Blueprint Engine
- ### 3. Optional: Heartbeat URL
- ## Why This Removes the Root Causes
- ## Files Modified
- ## Backward Compatibility
- ## Next Steps


### ./docs/archive/DOCUMENTATION_IMPROVEMENT_SUMMARY.md

- # Documentation Improvement Summary
- ## SR-AIbridge Documentation Enhancement - Complete
- ## 🎯 Mission Accomplished
- ### Problem Statement Addressed
- ## 📦 What Was Delivered
- ### 1. DOCUMENTATION_INDEX.md (24KB)
- ### 2. FEATURE_INVENTORY.md (23KB)
- ### 3. DOCUMENTATION_ENHANCEMENT_PLAN.md (13KB)
- ### 4. DOCUMENTATION_USAGE_GUIDE.md (16KB)
- ### 5. README.md Enhancements
- ### 6. NAVIGATION_INDEX.md Updates
- ## 📊 By the Numbers
- ### Documentation Statistics
- ### Coverage Analysis
- ### High-Priority Gaps Identified
- ## 🎓 Key Achievements
- ### 1. Visibility
- ### 2. Navigation
- ### 3. Planning
- ### 4. Usability
- ### 5. Sustainability
- ## 🔄 From Chaos to Order
- ### Before This Enhancement
- ### After This Enhancement
- ## 🚀 Next Steps (From Enhancement Plan)
- ### Week 1-2: Foundation (COMPLETE ✅)
- ### Week 3-4: Core Updates (PLANNED)
- ### Week 5-6: Feature Documentation (PLANNED)
- ### Week 7-8: Examples & Integration (PLANNED)
- ## 💡 Key Insights
- ### From Phoenix Protocol
- ### From This Enhancement
- ### Lessons Learned
- ## 🎯 Success Criteria Met
- ### Original Goals
- ### Code Quality
- ## 🌟 Impact on SR-AIbridge
- ### For New Users
- ### For Developers
- ### For Contributors
- ### For Maintainers
- ## 📖 Documentation Philosophy
- ## 🎉 Conclusion


### ./docs/archive/PR_READY.md

- # 🚢 Dock-Day Ascension: Ready for Pull Request to Main
- ## Branch Status: READY FOR MERGE ✅
- ## Suggested Pull Request Details
- ### Title:
- ### Description:
- ## 🚢 Dock-Day Ascension: Complete Implementation
- ### Features Implemented
- #### 🔧 Backend Systems
- #### 🎨 Frontend Integration  
- #### 🏛️ Ceremonial Systems
- #### 📋 Documentation
- ### Technical Highlights
- ### Testing Status
- ### Admiral's Note
- ### Files Changed
- ## Branch Diff Summary
- ### Changes from Main:
- ### Merge Target: `main`
- ### Source Branch: `dockday-ascension`
- ### Commit: `284af8b`
- ## Next Steps
- ## Final Verification ✅


### ./docs/archive/IMPLEMENTATION_SUMMARY.md

- # ✅ Captain vs Agent Role Separation - Implementation Complete
- ## Issue Resolution Summary
- ## What Was Implemented
- ### 🎯 Core Deliverables
- #### 1. **Mission Log - 100% Captain-Only** ✅
- #### 2. **Armada Map - Captain/Agent Toggle** ✅
- #### 3. **Backend API Filtering** ✅
- #### 4. **Database Schema Updates** ✅
- #### 5. **RBAC Enhancement** ✅
- ## Files Changed
- ### Backend (5 files)
- ### Frontend (4 files)
- ### Tests & Documentation (3 files)
- ## Test Results
- ### Test Suite: `test_captain_agent_separation.py`
- ### Build Tests
- ## Acceptance Criteria Status
- ## Visual Changes
- ### Before
- ### After
- ## API Examples
- ### Creating Captain Mission
- ### Creating Agent Job
- ### Fetching Captain Missions
- ### Fetching Agent Jobs
- ### Fetching Captain Fleet
- ### Fetching Agent Fleet
- ## Benefits Delivered
- ### 1. **Clean UX** ✅
- ### 2. **Data Isolation** ✅
- ### 3. **Revenue Protection** ✅
- ### 4. **Scalability** ✅
- ### 5. **Future-Proof** ✅
- ## Next Steps (Optional Future Enhancements)
- ### Suggested Improvements
- ## Documentation
- ## Conclusion


### ./docs/archive/GIT_SOVEREIGN_COMMISSIONING.md

- # 🌌 Git Sovereign Agent - Official Commissioning Document
- ## 🎯 Mission Accomplished
- ### Commissioning Status: ✅ COMPLETE
- ## 🎖️ Granted Authorities
- ### SDTF (Sovereign Dominion Token Forge)
- ### BRH (Bridge Runtime Handler)
- ### HXO Nexus
- ### All 21 Engines
- ### Repository Access
- ### Autonomous Operations
- ## 📊 Implementation Summary
- ### Code Delivered
- ### Validation Results
- ### Security Validation
- ## 🚀 Operational Capabilities
- ### Token Management
- ### Container Orchestration
- ### Harmonic Coordination
- ### Autonomous Operations
- ## 🎮 GitHub Actions Integration
- ### Workflow Status: ✅ CONFIGURED
- ## 📖 Documentation
- ### Complete Documentation Suite: ✅ DELIVERED
- ## 🔐 Admiral Trust Provision
- ## 🌌 Cosmic Parameters
- ## ✅ Acceptance Criteria
- ### Functional Requirements: ✅ ALL MET
- ### Non-Functional Requirements: ✅ ALL MET
- ## 🎖️ Final Commissioning Seal
- ## 🚀 Launch Sequence Complete
- ## 🌟 Next Steps
- ## 📜 Signature Block


### ./docs/archive/FIREWALL_LIST.md

- # Firewall Intelligence Engine - Detected Firewalls & Domains
- ## Executive Summary
- ## Critical Domains Detected
- ### Package Registries & Development Tools
- ### GitHub Services
- ### Deployment & Hosting Platforms
- ### Status & Monitoring
- ## Required Network Ports
- ### TCP Ports
- ### UDP Ports
- ## Detected Network Issues
- ### DNS Resolution Failures
- ## Firewall Configuration Recommendations
- ### For Enterprise Firewalls
- # Package Registries
- # GitHub Services
- # Deployment Platforms
- # Status Pages
- ### For Network Security Teams
- ## Generated Artifacts
- ### 1. Firewall Report (JSON)
- ### 2. Network Allowlist (YAML)
- ### 3. Incident Data (JSON)
- ## Next Steps
- ## Automation
- ## Documentation
- ## Contact & Support


### ./docs/archive/WHAT_I_COULDNT_CHANGE.md

- # What I Couldn't Change - Quick List
- ## API Write Capabilities (Intentionally Not Implemented)
- ### 1. Render Write API
- ### 2. Netlify Write API
- ### 3. GitHub Secrets Write API
- ## API Credentials (User Must Configure)
- ### 1. Render API Credentials
- ### 2. Netlify API Credentials
- ### 3. GitHub API Credentials
- ## Missing Variables Count (Cannot Determine Without Credentials)
- ## Conflict Resolution Strategy (Not Implemented)
- ## Validation and Safety Features (Not Implemented)
- ## Advanced Features (Not Implemented)
- ## Summary
- ### What I DID Change ✅
- ### What I COULDN'T Change ❌
- ### What YOU Need to Do 📋
- ### What's Next 🔜


### ./docs/archive/PHASE_4_5_IMPLEMENTATION_SUMMARY.md

- # Phase 4 & 5 Implementation Summary
- ## ✅ Implementation Complete
- ## 📦 Deliverables
- ### Core Modules (3 files)
- ### Integration Updates (4 files)
- ### Tests (2 files)
- ### Documentation (3 files)
- ## 🎯 Feature Summary
- ### Phase 4: Consensus Election
- ### Phase 5: Leader Hooks
- ## 📊 Test Results
- ### Unit Tests
- ### Integration Tests
- ### Security Scan
- ### Syntax Validation
- ### Code Review
- ## 🔧 Configuration
- ### Required Environment Variables
- ### Optional Environment Variables
- ## 🚀 Deployment
- ### Single Node (Development)
- ### Multi-Node (Production)
- # Node 1
- # Node 2
- ## 📈 Performance
- ## 🔒 Security
- ## 📝 Code Quality
- ### Metrics
- ### Standards
- ## 🎓 Learning Resources
- ## 🔮 Future Enhancements
- ## ✅ Acceptance Criteria
- ## 🎉 Status: Production Ready


### ./docs/archive/PHASE_6_IMPLEMENTATION.md

- # Phase 6 — Chaos & Recovery Suite Implementation
- ## Overview
- ## Components
- ### 1. Chaos Injector (`brh/chaos.py`)
- ### 2. Recovery Watchtower (`brh/recovery.py`)
- ### 3. Event Logging System (`brh/api.py`)
- #### `GET /federation/state`
- #### `GET /events`
- ### 4. Federation Console UI (`bridge-frontend/src/components/FederationConsole.jsx`)
- ### 5. Enhanced Consensus with Ledger Feedback (`brh/consensus.py`)
- ### 6. Runtime Configuration (`bridge.runtime.yaml`)
- ## Testing
- ### Unit Tests
- ### Running Tests
- # Run all Phase 6 tests
- # Run integration test
- # Run specific test
- ## Deployment
- ### Prerequisites
- ### Installation
- ### Starting the System
- ### Enabling Chaos for Testing
- ## Security Considerations
- ## Architecture Diagram
- ## Event Flow
- ## Troubleshooting
- ### Chaos not working
- ### Recovery not working
- ### Events not appearing in UI
- ## Performance Impact
- ## Future Enhancements
- ## References


### ./docs/archive/V2_IMPLEMENTATION_COMPLETE.md

- # v2.0.0 Implementation Complete — Project Genesis
- ## Overview
- ## ✅ Implementation Checklist
- ### Core Framework Components
- ### Engine Integration
- ### Application Integration
- ### Testing & Validation
- ### Documentation
- ## Files Created/Modified
- ### New Files (11)
- #### Genesis Framework Core
- #### Engine Adapters
- #### Testing
- #### Documentation
- ### Modified Files (1)
- ## Genesis Event Topics
- ### Five Core Topics Implemented
- ### Legacy Topic Support
- ## API Endpoints
- ### Seven Genesis Endpoints Implemented
- ## Environment Variables
- ### Five Configuration Variables
- ## Test Results
- ### Test Suite Coverage
- ## Key Features Delivered
- ### ✅ Universal Engine Integration
- ### ✅ Self-Healing Architecture
- ### ✅ Real-Time Introspection
- ### ✅ Backward Compatibility
- ### ✅ Production Ready
- ## Architecture Highlights
- ### The Genesis Organism
- ## Deployment Verification
- ### Local Testing
- ### Integration with Main Application
- ## Migration Path
- ### For Existing v1.9.7c Users
- ### For New Implementations
- ## Performance Characteristics
- ### Event Processing
- ### Resource Usage
- ## Security & Safety
- ### Guardrails Implemented
- ### Error Handling
- ## Known Limitations
- ## Future Roadmap
- ### Planned Enhancements
- ## Success Metrics
- ### Code Quality
- ### Feature Completeness
- ### Production Readiness
- ## Conclusion
- ## Quick Start
- # Enable Genesis
- # Start the application
- # Check the pulse
- # View the system


### ./docs/archive/DEPLOYMENT_CHECKLIST_v196i.md

- # 🎉 v1.9.6i Deployment Checklist
- ## ✅ Pre-Deployment Checklist
- ### Code Quality
- ### Files Added
- ### Files Modified
- ## 🚀 Deployment Steps
- ### 1. Merge to Main
- ### 2. Render Auto-Deploy
- ### 3. Monitor Deployment
- ### 4. Verify Health Endpoints
- # Basic health check (should respond immediately)
- # Expected response:
- # {"status": "ok", "alive": true}
- # Stage status
- # Expected response:
- # {
- #   "temporal_deploy_buffer": {
- #     "enabled": true,
- #     "current_stage": 3,
- #     "ready": true,
- #     "stages": {
- #       "stage1": {"complete": true, "duration": 0.15},
- #       "stage2": {"complete": true, "duration": 3.42},
- #       "stage3": {"complete": true, "duration": 2.18}
- #     },
- #     "total_boot_time": 5.75,
- #     "errors": []
- #   }
- # }
- ### 5. Check Diagnostics
- ## 🏁 Success Criteria
- ## 🔧 Configuration
- ### Environment Variables (Render)
- ### Optional Tuning
- # Increase stage timeout
- # Set in Render dashboard
- ## 🐛 Troubleshooting
- ### Issue: Render still times out
- ### Issue: Stages 2/3 fail
- ### Issue: Want to revert to legacy startup
- # In Render dashboard, set:
- # Or merge a commit that sets it in render.yaml
- ## 📊 Performance Expectations
- ### Startup Metrics
- ### Deployment Success Rate
- ## 🔄 Rollback Plan
- # Option 1: Git revert
- # Option 2: Disable TDB
- # In Render dashboard, set:
- ## 📝 Post-Deployment Tasks
- ### Immediate (0-24 hours)
- ### Short-term (1-7 days)
- ### Long-term (1-4 weeks)
- ## 📚 Documentation
- ## 🎯 Version Info
- ## ✅ Final Checklist


### ./docs/archive/SCAN_SUMMARY.md

- # Full System Scan Summary - November 2025
- ## Request
- ## Actions Taken
- ## Results
- ### ✅ ALL CHECKS PASSING (8/8)
- ### Security Scan Results
- ### Compliance
- ## Deliverables
- ## About "Twelve Failed Checks"
- ## How to Run Future Scans
- # Run full scan with progress output
- # Run quietly (just show pass/fail results)  
- # Output as JSON
- ## Recommendations
- ## Conclusion


### ./docs/archive/V196E_IMPLEMENTATION.md

- # v1.9.6e — Heartbeat Compliance & Method Guard (Final Build)
- ## Overview
- ## Key Changes
- ### 1. Intelligent Heartbeat (`bridge_backend/runtime/heartbeat.py`)
- ### 2. Health Route Duality (`bridge_backend/routes/control.py`)
- ### 3. Predictive Stabilizer Pattern Detection (`bridge_backend/runtime/predictive_stabilizer.py`)
- ### 4. Render Port Auto-Bind (`bridge_backend/__main__.py`)
- ## Testing
- ## Outcome
- ## Migration Notes
- ## Start Commands
- # or
- # or


### ./docs/archive/FEATURE_INVENTORY.md

- # SR-AIbridge Feature Inventory
- ## Complete Listing of Features: Documented vs Actual
- ## 📊 Quick Summary
- ## 🔌 Core API Endpoints
- ### Health & System (Status: ✅ 100% Documented)
- ### Agent Management (Status: ✅ 100% Documented)
- ### Mission Control (Status: ✅ 100% Documented)
- ### Vault & Logging (Status: ✅ 100% Documented)
- ### Guardian System (Status: ✅ 100% Documented)
- ### Fleet Management (Status: ✅ 100% Documented)
- ### Communication (Status: ✅ 100% Documented)
- ### Admiral Keys & Custody (Status: ✅ 100% Documented)
- ### Additional Core Endpoints (Status: ⚠️ 50% Documented)
- ## 🧠 Engines (20+ Specialized Engines)
- ### Core Engines (6 engines)
- #### 1. Blueprint Engine (Status: ✅ Fully Documented)
- #### 2. TDE-X (Tri-Domain Execution) (Status: ✅ Fully Documented)
- #### 3. HXO Nexus (Status: ✅ Fully Documented)
- #### 4. Autonomy Engine (Status: ✅ Well Documented)
- #### 5. Leviathan (Status: ⚠️ Partial Documentation)
- #### 6. Cascade Engine (Status: ⚠️ Partial Documentation)
- ### Super Engines (6 engines)
- #### 7. CalculusCore (Math Engine) (Status: ✅ Well Documented)
- #### 8. QHelmSingularity (Quantum) (Status: ⚠️ Basic Documentation)
- #### 9. AuroraForge (Science) (Status: ⚠️ Basic Documentation)
- #### 10. ChronicleLoom (History) (Status: ⚠️ Basic Documentation)
- #### 11. ScrollTongue (Language) (Status: ⚠️ Basic Documentation)
- #### 12. CommerceForge (Business) (Status: ⚠️ Basic Documentation)
- ### Utility Engines (8+ engines)
- #### 13. Chimera (Status: ✅ Fully Documented)
- #### 14. Umbra (Status: ✅ Fully Documented)
- #### 15. EnvSync (Status: ✅ Well Documented)
- #### 16. Recovery Engine (Status: ⚠️ Minimal Documentation)
- #### 17. Truth Engine (Status: ⚠️ Minimal Documentation)
- #### 18. Creativity Engine (Status: ❌ Not Documented)
- #### 19. Speech Engine (Status: ❌ Not Documented)
- #### 20. Parser Engine (Status: ❌ Not Documented)
- #### 21. Screen Engine (Status: ❌ Not Documented)
- #### 22. Indoctrination Engine (Status: ⚠️ Minimal Documentation)
- #### 23. Agents Foundry (Status: ❌ Not Documented)
- #### 24. Adapters (Status: ❌ Not Documented)
- ## 🏗️ Backend Modules (47+ modules)
- ### Core Systems (Status: ✅ 100% Documented)
- ### Advanced Systems (Status: ✅ 80%+ Documented)
- ### Support Systems (Status: ⚠️ 30% Documented)
- ### Heritage Subsystem (Status: ❌ 0% Documented)
- ## 🎨 Frontend Components (37 components)
- ### Dashboard & Core (Status: ✅ 100% Documented)
- ### Mission & Fleet (Status: ✅ 100% Documented)
- ### Communication (Status: ✅ 100% Documented)
- ### Data & Logging (Status: ✅ 100% Documented)
- ### Administration (Status: ✅ 100% Documented)
- ### Additional Components (Status: ⚠️ 50% Documented)
- ## 🚀 Advanced Features & Systems
- ### Forge Dominion (Status: ✅ 100% Documented)
- ### HXO Nexus (Status: ✅ 100% Documented)
- ### BRH (Bridge Runtime Handler) (Status: ✅ 100% Documented)
- ### Genesis Linkage (Status: ✅ 90% Documented)
- ### Autonomy System (Status: ✅ 95% Documented)
- ### Federation System (Status: ⚠️ 60% Documented)
- ### Parity Engine (Status: ✅ 80% Documented)
- ### Firewall Intelligence (Status: ✅ 85% Documented)
- ### Compliance System (Status: ✅ 90% Documented)
- ### Steward System (Status: ✅ 85% Documented)
- ### Data Relay (Status: ⚠️ 40% Documented)
- ### Healer-Net (Status: ⚠️ 60% Documented)
- ## 📦 Deployment Features (Status: ✅ 100% Documented)
- ### Platform Deployment
- ### CI/CD & Automation
- ## 🔐 Security Features (Status: ✅ 90% Documented)
- ## 📊 Documentation Status by Priority
- ### 🔴 HIGH Priority (Must Document)
- ### 🟡 MEDIUM Priority (Should Document)
- ### 🟢 LOW Priority (Nice to Have)
- ## ✅ Next Steps
- ### Immediate Actions (Week 1-2)
- ### Short-term (Week 3-4)
- ### Medium-term (Week 5-6)
- ## 🎯 Success Metrics


### ./docs/archive/GITHUB_ENVHOOK_IMPLEMENTATION.md

- # GitHub Environment Hook - Implementation Summary
- ## 🎯 What Was Implemented
- ## 📦 Components Delivered
- ### Core Implementation
- ### Documentation
- ## 🏗️ Architecture
- ## ✨ Features Implemented
- ### File Watching
- ### Event Publishing
- ### Operational Modes
- ### Testing
- ## 🔌 Genesis Topics Added
- ## 🧪 Test Results
- ## 📊 Demonstration Results
- ## 🚀 Usage Examples
- ### Watch Mode (Continuous)
- ### Manual Trigger (One-time)
- ### GitHub Actions Integration
- ## 📁 Files Created/Modified
- ### Created Files
- ### Modified Files
- ### Auto-Generated (Ignored)
- ## 🔒 Security Features
- ## 🎯 Result
- ### Before (v1.9.6w)
- ### After (v1.9.6x)
- ## 💡 Quote
- ## 🔗 Next Steps
- ## ✅ Acceptance Criteria Met


### ./docs/archive/ANCHORHOLD_PR_SUMMARY.md

- # PR Summary: SR-AIbridge v1.9.4 — Anchorhold Protocol Verification
- ## Overview
- ## What Was Found Already Implemented ✅
- ### Core Features (All Present)
- ### Infrastructure (All Configured)
- ### Dependencies (All Added)
- ### Documentation (All Created)
- ### Version & Branding (All Updated)
- ## What This PR Adds 🆕
- ### 1. Comprehensive Test Suite
- ### 2. Quick Validation Script
- ### 3. Deployment Readiness Report
- ## Verification Results
- ### ✅ All Tests Passing
- ### ✅ All Validations Passing
- ## Files Changed in This PR
- ### Added Files (3)
- ### Modified Files
- ## Key Findings
- ### Implementation Status
- ### Quality Metrics
- ## Deployment Readiness
- ### ✅ Ready to Deploy
- ### Deployment Process
- ## How to Verify Locally
- ### Run Validation
- ### Run Test Suite
- ### Both Should Show
- ## Documentation
- ## Conclusion
- ## Contributors


### ./docs/archive/COPILOT_IMPROVEMENTS.md

- # Copilot Improvements for v1.9.7q
- ## Implemented Improvements ✅
- ## Additional Improvement Suggestions 💡
- ### 1. Configuration File Support
- # bridge_backend/bridge_core/guards/config.py
- ### 2. Metrics and Telemetry
- # In autoheal_link.py
- ### 3. Health Check Endpoints
- # bridge_backend/bridge_core/guards/routes.py
- ### 4. Retry Strategy Configuration
- # In autoheal_link.py
- ### 5. Graceful Degradation Modes
- # In netlify_guard.py
- ### 6. Event Bus Integration
- # In netlify_guard.py
- ### 7. Pre-flight Dry Run Mode
- # In netlify_guard.py
- ### 8. Dependency Checks
- # bridge_backend/bridge_core/guards/dependency_check.py
- ### 9. Staged Rollout Support
- # In main.py
- ### 10. Structured Logging
- # Instead of:
- # Use:
- ## Implementation Priority
- ## Notes


### ./docs/archive/README.md

- # Documentation Archive
- ## Contents
- ## Purpose
- ## Viewing Reports
- ## Cleanup Date
- ## Script Used


### ./docs/archive/HXO_DEPLOYMENT_CHECKLIST.md

- # HXO Deployment Checklist — v1.9.6n
- ## Pre-Deployment Checklist
- ### ✅ Code Quality
- ### ✅ Documentation
- ### ✅ Configuration
- ### ✅ Safety Guards
- ## Deployment Steps
- ### Step 1: Merge to Main
- # Ensure all commits are pushed
- # Create PR and merge to main
- # Title: "v1.9.6n — Hypshard-X Orchestrator (HXO)"
- ### Step 2: Deploy to Render (Backend)
- # Watch deployment logs
- # Look for:
- # [HXO] Disabled (set HXO_ENABLED=true to enable)
- ### Step 3: Verify Backend Health
- # Check health endpoint
- # Should return:
- # {"status": "ready", "message": "Service is operational"}
- ### Step 4: Enable HXO (Optional, for testing)
- # Add environment variable
- # Redeploy
- # Look for:
- # [HXO] v1.9.6n routes enabled - hypshard-x orchestrator active
- ### Step 5: Test HXO Endpoints
- # Test status endpoint (should return 404 for non-existent plan)
- # Expected: 404 with "Plan not found" message
- ### Step 6: Submit Test Plan (Admiral only)
- # Should return:
- # {
- #   "plan_id": "...",
- #   "name": "test_deploy",
- #   "status": "submitted",
- #   "total_shards": N
- # }
- ### Step 7: Monitor Test Plan
- # Get status
- # Watch for completion
- # done_shards should equal total_shards
- ### Step 8: Verify Checkpoint Persistence
- # Check checkpoint DB exists
- # In Render shell:
- # Should exist and have non-zero size
- ### Step 9: Test Abort (Admiral only)
- # Submit another plan
- # Abort it
- # Should return:
- # {"plan_id": "...", "status": "aborted"}
- ### Step 10: Verify Genesis Integration
- # Check Genesis events
- # Should return recent hxo.plan events
- ## Post-Deployment Monitoring
- ### Metrics to Track
- ### Log Queries
- # Find HXO errors
- # Find failed shards
- # Find auto-tune signals
- ## Rollback Plan
- ### Quick Disable
- # In Render dashboard
- # Redeploy
- ### Full Rollback
- # Revert merge commit
- # Push to main
- # Render auto-deploys
- ### Abort In-Flight Plans
- # Get all active plans
- # Abort each
- ## Known Limitations (v1.9.6n)
- ## Success Criteria
- ## Production Readiness (Optional)
- ## Support Contacts
- ## Deployment Sign-Off


### ./docs/archive/STEWARD_ENVRECON_INTEGRATION.md

- # Steward-EnvRecon Integration Guide
- ## Overview
- ## Usage
- ### Read-Only Mode (Default)
- # Enable Steward in read-only mode
- # Run diff via API endpoint
- ### JSON Report Format
- ### Field Descriptions
- ## Integration Details
- ### How It Works
- ### Secret Detection
- ## Example: Using the JSON Report
- ### Python Script
- # Run
- ### Shell Script
- # Get drift report via API
- # Extract missing variables for each platform
- ## Benefits
- ## Configuration
- ### Required Environment Variables
- # Enable Steward
- # Optional: Provider credentials for live data
- ## Next Steps
- ## See Also


### ./docs/archive/GIT_SOVEREIGN_VISUALIZATION.md

- # 🌌 Git Sovereign Agent - Sovereignty Visualization
- ## Overview
- ## 🎯 Authority Hierarchy
- ## 🏗️ Integration Architecture
- ## 🌟 HXO Nexus - 21 Engine Connectivity
- ## 🔄 Token Lifecycle (SDTF)
- ## 🤖 Autonomous Decision Flow
- ## 🔧 BRH Container Orchestration
- ## 🌌 Reality Stream (Branch) Spawning
- ## 📊 Sovereignty Metrics Dashboard
- ## 🎯 Operational Scope
- ## 🔒 Security & Trust Model
- ## 🚀 Launch Sequence


### ./docs/archive/V196F_IMPLEMENTATION.md

- # SR-AIbridge v1.9.6f — Render Bind & Startup Stability Patch (Final)
- ## 🎯 Objective
- ## 🚀 Core Upgrades
- ### 1. Adaptive Port Binding
- ### 2. Deferred Heartbeat Initialization
- # Start heartbeat (could race with bind)
- # Mark bind as confirmed first
- # Then start heartbeat
- ### 3. Predictive Watchdog
- # Startup Latency Stabilization Ticket
- ## Metrics
- ## Recommended Actions
- ### 4. Self-Healing Diagnostics
- ### 5. Runtime Intelligence Sweep
- ## 🧠 Behavior Summary
- ## 📋 Files Changed
- ### Modified
- ### Created
- ## 🧾 Commit Message
- ## 🔍 Validation
- ### Expected Render Log Sequence After Deploy
- ### No Error Messages Expected
- ## 🧪 Testing
- ### Run Tests
- # Run v1.9.6f test suite
- # Expected: 22/23 tests pass (1 httpx dependency test may skip)
- ### Manual Testing
- # Test adaptive port resolution
- # Should see:
- # [PORT] Resolved immediately: 10000
- # [BOOT] Adaptive port bind: ok on 0.0.0.0:10000
- # Test fallback behavior
- # Should see:
- # [PORT] Waiting 2.5s for environment variable injection...
- # [PORT] No valid PORT detected after 2.5s, defaulting to 8000
- # [BOOT] Adaptive port bind: ok on 0.0.0.0:8000
- ## 🧩 Notes for Future Lineage (v1.9.7+)
- ### Foundation for Netlify Federation
- ### Safe Cross-Host Proxy Tests
- ## 🚀 Deployment
- ### Render
- ### Expected Startup Time
- ### Rollback Plan
- ## 🏆 Success Criteria
- ## 📚 Related Documentation


### ./docs/archive/BRIDGE_FEDERATION_SECRETS.md

- # Bridge Federation Build - Required Secrets Configuration
- ## Overview
- ## Required Secrets
- ### FED_KEY
- ### DOM_TOKEN
- ### BRIDGE_ENV
- ## Workflow Environment Variables
- ## Setting Up Secrets
- ### Using GitHub UI
- ### Using GitHub CLI
- # Set FED_KEY
- # Set DOM_TOKEN
- # Set BRIDGE_ENV (as a variable)
- ## Security Best Practices
- ## Workflow Behavior Without Secrets
- ## Troubleshooting
- ### "No dominion token provided" Error
- ### Federation Heartbeat Timeout
- ### Token Validation Failed
- ## Related Files
- ## Support


### ./docs/archive/FIREWALL_AUTONOMY_IMPLEMENTATION.md

- # Firewall Intelligence and Autonomy Engine Implementation Summary
- ## Overview
- ## Implementation Complete ✅
- ### Core Components
- ## Key Features
- ### Autonomous Decision-Making
- ### Safety Guardrails
- ### Four-Phase Execution Cycle
- ## Files Created/Modified
- ### Created
- ### Modified
- ## Output Artifacts
- ### Diagnostics
- ### Network Policies
- ### Vault Records (Audit Trail)
- ## Testing
- ## Execution Example
- ## Integration with Existing Systems
- ## Next Steps for Operators
- ## Compliance and Safety
- ## Summary


### ./docs/archive/DOMINION_IMPLEMENTATION_SUMMARY.md

- # Forge Dominion Implementation Summary v1.9.7s-SOVEREIGN
- ## 🎯 Mission Complete
- ## 📊 Implementation Metrics
- ### Code Coverage
- ### Components Delivered
- #### Core Cryptography (`bridge_backend/bridge_core/token_forge_dominion/`)
- #### Infrastructure
- #### Documentation
- #### Testing
- ## 🔐 Security Architecture
- ### Cryptographic Primitives
- ### Zero-Trust Model
- ### Resonance-Aware Security
- ## 🎭 Secret Detection Capabilities
- ### Pattern Recognition (20+ patterns)
- ### Scanning Performance
- ## 🚀 Deployment Integration
- ### GitHub Actions
- ### Supported Platforms
- ## 📈 Quality Metrics
- ### Test Coverage
- ### Code Quality
- ### Documentation Quality
- ## 🔄 Upgrade Path
- ### From Earlier Versions
- ### Production Deployment
- ## 🎯 Success Criteria - All Met ✅
- ## 🌟 Key Achievements
- ## 📚 Documentation Artifacts
- ## 🔮 Future Enhancements (Roadmap)
- ### v1.9.8 (Q1 2026)
- ### v2.0.0 (Q2 2026)
- ### v2.1.0 (Q3 2026)
- ## 🏆 Final Status


### ./docs/archive/GIT_SOVEREIGN_VALIDATION.md

- # 🌌 Git Sovereign Agent - Validation Summary
- ## 🧪 Validation Results
- ### Core Module Tests
- #### ✅ Manifest Module
- #### ✅ SDTF Integration
- #### ✅ BRH Integration
- #### ✅ HXO Nexus Integration
- #### ✅ Autonomous Operations
- ## 📊 Component Summary
- ## 🏗️ Architecture Validation
- ### Integration Points
- ### Engine Access
- ### Decision Matrix
- ## 📝 Files Delivered
- ### Python Modules (5 files)
- ### Tests (1 file)
- ### Workflows (1 file)
- ### Documentation (3 files)
- ### Updated Files (2 files)
- ## 🚀 Operational Capabilities
- ### Token Management
- ### Container Orchestration
- ### Harmonic Coordination
- ### Autonomous Operations
- ## 🎯 GitHub Actions
- ### Workflow Configuration
- ### Commissioning Steps
- ## 📖 Documentation
- ### Complete Documentation Suite
- ### Documentation Coverage
- ## 🔒 Security
- ### Cryptographic Validation
- ### Authority Model
- ## ✅ Acceptance Criteria
- ### Functional Requirements
- ### Non-Functional Requirements
- ## 🌌 Final Verification
- ### Operational Status
- ### Authority Verification
- ### Integration Verification
- ## 🎖️ Commissioning Complete


### ./docs/archive/GENESIS_V2_0_1A_IMPLEMENTATION.md

- # 🧩 EnvSync Seed Manifest - Genesis v2.0.1a
- ## Implementation Complete ✅
- ## 🚀 What Was Added
- ### 1. **EnvSync Seed Manifest File**
- ### 2. **Engine Integration**
- ### 3. **Genesis Bus Integration**
- ### 4. **Genesis Manifest Registration**
- ### 5. **Autonomy Link Enhancement**
- ### 6. **Documentation Suite**
- #### A. Comprehensive Guide
- #### B. Quick Reference
- #### C. Example Configuration
- ### 7. **Validation Tools**
- #### A. Validation Script
- #### B. CI/CD Workflow
- ## 🎯 Expected Outcomes (All Achieved)
- ## 🔧 How to Use
- ### Step 1: Enable EnvSync
- ### Step 2: Configure Platform Access
- # Render
- # Netlify
- ### Step 3: Deploy
- ### Step 4: Verify
- # Check EnvSync health
- # Trigger manual sync
- ## 📊 Implementation Stats
- ## 🧪 Testing
- ## 🔮 Future Enhancements
- ## 📚 Related Documentation
- ## 🙏 Acknowledgments
- ## ✅ Commit Suggestions


### ./docs/archive/ENDPOINT_TEST_SOLUTION.md

- # SR-AIbridge Endpoint Testing Solution
- ## Overview
- ## What Was Delivered
- ### 1. Main Test Script: `test_endpoints_full.py`
- ### 2. Documentation
- ### 3. README Integration
- ## Key Features
- ### Comprehensive Coverage
- ### Robust Error Handling
- ### Flexible Output
- ### Exit Codes
- ## Usage Examples
- ### Basic Testing
- # Test local backend
- # Test deployed backend
- # Custom timeout for slow backends
- ### CI/CD Integration
- # JSON output for automated processing
- # Use in GitHub Actions
- ### Monitoring
- # Schedule via cron for regular checks
- ## Comparison with Existing Tools
- ## Benefits
- ## Testing Methodology
- ### Test Categories
- ### Retry Strategy
- ### Success Criteria
- ## Troubleshooting Guide
- ### All Tests Fail
- ### Some Tests Fail
- ### Timeouts
- ### Engine Endpoints 404
- ## Files Changed
- ## Validation
- ## Next Steps
- ### For Users
- ### For CI/CD Integration
- ### For Regular Monitoring
- ## Conclusion


### ./docs/archive/WORKFLOW_FIXES_SUMMARY.md

- # Workflow Fixes Summary - SR-AIBridge
- ## Issues Addressed
- ### 1. Python Syntax Error ✅ FIXED
- # BEFORE (BROKEN):
- # AFTER (FIXED):
- ### 2. Missing timezone Import ✅ FIXED
- # BEFORE (BROKEN):
- # AFTER (FIXED):
- ### 3. Incorrect Netlify Publish Path ✅ FIXED
- # BEFORE (BROKEN):
- # AFTER (FIXED):
- ### 4. Missing pytest-asyncio Dependency ✅ FIXED
- # NEW FILE: pytest.ini
- ### 5. Deprecated GitHub Actions ✅ FIXED
- ### 6. Missing Secrets Documentation ✅ FIXED
- ## Validation Results
- ## Next Steps
- ### For the Repository Owner:
- ## Summary


### ./docs/archive/PHASE_6_SUMMARY.md

- # Phase 6 Implementation Summary
- ## Files Changed
- ### New Files Created (7)
- ### Modified Files (5)
- ## Lines of Code
- ## Build Status
- ## Key Features Implemented
- ### 1. Chaos Engineering
- ### 2. Self-Healing
- ### 3. Observability
- ### 4. UI Visualization
- ### 5. Audit Trail
- ## Testing Coverage
- ### Unit Tests (14 tests)
- ### Integration Tests
- ### Build Tests
- ## Configuration Examples
- ### Enable Chaos for Testing
- ### Disable Recovery
- ### Production Configuration
- # bridge.runtime.yaml
- ## API Endpoints
- ### GET /federation/state
- ### GET /events
- ## Security Considerations
- ## Performance Impact
- ## Next Steps
- ## Dependencies
- ## Deployment Checklist
- ## References


### ./docs/archive/UMBRA_IMPLEMENTATION_COMPLETE.md

- # Umbra v1.9.7d Implementation Summary
- ## 🎯 Implementation Complete
- ## 📊 Test Results
- ### Unit Tests
- ### Smoke Tests
- ## 🏗️ Architecture Overview
- ## 📁 Files Created (16 total)
- ### Core Modules
- ### Tests
- ### Documentation
- ## 🔧 Files Modified (5 total)
- ### Integration
- ### Configuration
- ## 📡 API Endpoints (10 total)
- ### Public Endpoints
- ### Detection & Repair
- ### Memory Operations
- ### Predictive Operations
- ### Echo Operations
- ## 🔒 Security & RBAC
- ### Admiral Permissions
- ### Captain Permissions
- ### Observer Permissions
- ## 🌐 Genesis Bus Topics (6 added)
- ## ⚙️ Environment Variables (5 added)
- ## 📈 Code Metrics
- ### Lines of Code
- ### Test Coverage
- ## 🎯 Key Features Delivered
- ### ✅ Umbra Core - Pipeline Self-Healing
- ### ✅ Umbra Memory - Experience Graph
- ### ✅ Umbra Predictive - Pre-Repair Intelligence
- ### ✅ Umbra Echo - Human-Guided Learning
- ## 🚀 Deployment Checklist
- ## 🎓 Learning & Pattern Recognition
- ### Current Capabilities
- ### Memory Persistence
- ## 💡 Usage Examples
- ### Detect Anomaly
- ### Get Metrics
- ### Recall Memory
- ### Capture Echo Event
- ## 📚 Documentation
- ### Comprehensive Documentation
- ### Quick Reference
- ### Changelog
- ## 🎉 Achievement Summary
- ### What Was Built
- ### Impact
- ### Admiral's Vision Realized
- ## ✅ Ready for Merge


### ./docs/archive/PARITY_STUBS_VERIFICATION.md

- # Parity Engine Frontend Stubs Verification Report
- ## Summary
- ## Verification Results
- ### 1. File Count Verification ✅
- ### 2. Directory Structure ✅
- ### 3. Parity Engine Execution ✅
- ### 4. Test Suite Validation ✅
- ### 5. Communication Status ✅
- ## Sample Stub Analysis
- ### Critical Route Example: `/api/control/hooks/triage`
- ### Path Parameter Example: `/blueprint/{bp_id}`
- ## Index File Verification
- ## Breakdown by Severity
- ### Critical Routes (2)
- ### Moderate Routes (83)
- ### Informational Routes (1)
- ## Comparison: Expected vs Actual
- ## Conclusion
- ## Next Steps
- ## Files Involved


### ./docs/archive/STUB_CLEANUP_COMPLETE.md

- # Full Repository Stub Scan and Cleanup - Complete Report
- ## Executive Summary
- ## Issues Identified and Fixed
- ### 1. ✅ Deprecated datetime.utcnow() Calls - FIXED
- #### What was wrong:
- #### What was fixed:
- #### Files affected (sample):
- ### 2. ✅ Frontend Auto-Generated Stub TODOs - FIXED
- #### What was wrong:
- #### What was fixed:
- #### Files affected:
- ### 3. ℹ️ Backend Stub Implementations - VERIFIED SAFE
- #### What was found:
- #### Why no action needed:
- ### 4. ℹ️ Incomplete Engine: adapters - VERIFIED SAFE
- #### What was found:
- #### Why no action needed:
- ## Tools Created
- ### 1. Stub Scanner (`scripts/stub_scanner.py`)
- ### 2. DateTime Fixer (`scripts/fix_deprecated_datetime.py`)
- ### 3. Stub TODO Cleaner (`scripts/clean_stub_todos.py`)
- ## Verification Results
- ### Python Compilation ✅
- # All 200+ Python files compile successfully
- # Exit code: 0 (success)
- ### Datetime Pattern Check ✅
- # Before: 211 occurrences
- # After: 0 occurrences
- # Result: 0 matches
- ### Frontend Stub TODO Check ✅
- # Before: 85 files with TODOs
- # After: 0 files with TODOs
- # Result: 0 matches
- ### Engine Route Registration ✅
- ## Deployment Impact
- ### Before Cleanup:
- ### After Cleanup:
- ## Summary
- ## Files Changed
- ## Recommendations for Future


### ./docs/archive/DEPLOYMENT_VERIFICATION.md

- # v1.9.7i Deployment Verification
- ## ✅ Implementation Complete
- ## Verification Results
- ### 1. Component Initialization ✅
- ### 2. Genesis Bus Integration ✅
- ### 3. Test Coverage ✅
- ### 4. Pipeline Smoke Test ✅
- ### 5. CLI Tool ✅
- ### 6. GitHub Actions Workflow ✅
- ### 7. File Artifacts ✅
- ### 8. Documentation ✅
- ## Deployment Flow Verified
- ## Known Non-Critical Warnings
- ### Genesis Bus Database Lock
- ## Production Readiness Checklist
- ## Next Steps for Production
- ## Conclusion


### ./docs/archive/PROJECT_LOC_SUMMARY.md

- # SR-AIbridge - Project LOC Summary
- ## Total Lines of Code: 48,100
- ## Quick Breakdown
- ## Project Structure
- ### Backend (Python - 21,052 lines)
- ### Frontend (JS/React - 5,340 lines)
- ### Documentation (Markdown - 9,488 lines)
- ### Infrastructure
- ## Top 10 Largest Files
- ## How to Update
- # Comprehensive report
- # Quick summary
- ## Notes


### ./docs/archive/REPO_STUDY_IMPLEMENTATION_SUMMARY.md

- # Repository Study Implementation Summary
- ## Overview
- ## What Was Built
- ### 1. Core Study Script (`study_repo_with_engines.py`)
- ### 2. Quick Launcher (`run_repo_study.sh`)
- ### 3. Smoke Tests (`smoke_test_engines.py`)
- ### 4. Documentation Suite
- ## Technical Achievements
- ### Engine Coordination
- ### Data Persistence
- ### Output Artifacts
- ## Capabilities Demonstrated
- ### 1. Self-Awareness
- ### 2. Self-Planning
- ### 3. Self-Validation
- ### 4. Autonomous Operation
- ## Use Cases Enabled
- ## Key Results
- ### Quantitative Metrics
- ### Qualitative Achievements
- ## Usage Examples
- ### Quick Start
- # Fastest way to run the study
- ### Direct Python
- # Run the main study script
- ### Run Tests
- # Verify all engines are working
- ### Custom Analysis
- # Customize the study for your needs
- # Your custom analysis here...
- ## Files Created
- ## Next Steps
- ## Architecture Benefits
- ### Modularity
- ### Extensibility
- ### Auditability
- ### Reusability
- ### Autonomy
- ## Conclusion


### ./docs/archive/CHROME_PLAYWRIGHT_INSTALLATION_SUMMARY.md

- # Chrome/Playwright Installation Summary
- ## Overview
- ## Changes Made
- ### Workflows Updated
- ### Installation Step Added
- ## Why This Change Was Needed
- ### Problem
- ### Solution
- ## Technical Details
- ### Installation Components
- #### `npx playwright install-deps`
- #### `npx playwright install chromium`
- ### Complementary Existing Code
- ## Validation
- ### Syntax Validation
- ### Testing Strategy
- ## Impact
- ### Benefits
- ### Potential Considerations
- ## Related Files and Scripts
- ### Scripts that benefit from this change:
- ### Configuration files:
- ## Future Enhancements
- ## References
- ## Maintenance
- ### Keeping Browsers Updated
- ### Cache Management
- ### Monitoring


### ./docs/archive/HXO_NEXUS_IMPLEMENTATION_SUMMARY.md

- # HXO Nexus v1.9.6p Implementation Summary
- ## Executive Summary
- ## What Was Delivered
- ### 1. Core HXO Nexus System
- ### 2. HypShard v3 - Quantum Adaptive Shard Manager
- ### 3. Security Layers
- ### 4. REST API Routes
- ### 5. Integration & Adapters
- ### 6. Documentation
- ### 7. Comprehensive Testing
- ## Files Created/Modified
- ### New Files (12)
- ### Modified Files (4)
- ## The "1+1=∞" Connectivity Paradigm
- ### Universal Connectivity
- ### Harmonic Resonance
- ### Emergent Synergy
- ### Infinite Scaling
- ## Technical Achievements
- ### Architecture
- ### Performance
- ### Security
- ### Integration
- ## Configuration
- ### Environment Variables Added
- ### Genesis Bus Topics Added
- ## Usage Examples
- ### Initialize Nexus
- ### Coordinate Engines
- ### Use HypShard
- ### Achieve Consensus
- ## Impact
- ### Developer Experience
- ### System Capabilities
- ### Operational Benefits
- ## Future Enhancements
- ## Conclusion


### ./docs/archive/LOC_QUICK_ANSWER.md

- # SR-AIbridge LOC - Quick Answer
- ## 📊 Total Project Lines of Code: **48,100**
- ## Quick Stats
- ## Top 3 Components
- ## Get Full Details
- # View this summary
- # Run comprehensive counter
- # Quick count by language
- ## Reports Generated


### ./docs/archive/PARITY_EXECUTION_REPORT.md

- # Parity Engine Execution Report
- ## 🎯 Mission: Verify Frontend-Backend Communication
- ## 📊 Communication Analysis
- ## 🔍 What Was Analyzed
- ### Backend Routes Scanned
- ### Frontend Calls Scanned
- ## ⚙️ Auto-Fix Actions Performed
- ### 1. Frontend Stub Generation ✅
- ### 2. Backend Stub Documentation ✅
- ## 🎨 Severity Classification
- ### 🔴 Critical (2 endpoints)
- ### 🟡 Moderate (83 endpoints)
- ### 🔵 Informational (1 endpoint)
- ## 📋 Files Created/Updated
- ### New Documentation
- ### Generated Reports
- ### Generated Code
- ## ✅ Test Results
- ## 🚀 Next Steps for Integration
- ### Immediate Actions
- ### Long-term Maintenance
- ## 📞 Communication Flow Diagram
- ## 🎉 Summary
- ## 📚 Additional Resources


### ./docs/archive/GIT_SOVEREIGN_FAMILIARIZATION_SUMMARY.md

- # Git Sovereign Agent Familiarization Summary
- ## Complete Bridge Mastery Achieved
- ## Executive Summary
- ## What Was Accomplished
- ### 1. Repository Metrics Analyzed
- ### 2. Core Architecture Mastered
- #### Entry Point (main.py)
- #### Database Layer
- #### Genesis Event Bus (The Central Nervous System)
- ### 3. All 20+ Engines Documented
- #### Core Infrastructure (6)
- #### Super Engines (6) - Total: 137,000+ lines of code
- #### Orchestrator (1)
- #### Utility Engines (7+)
- #### Advanced Systems (7+)
- ### 4. Advanced Systems Understood
- #### Forge Dominion (v1.9.7s)
- #### Bridge Runtime Handler (BRH)
- #### Git Sovereign Agent (My Role)
- ### 5. Frontend Architecture Mapped
- #### React 18+ with Vite
- #### Key Components
- ### 6. Deployment & Operations
- #### CI/CD Pipeline
- #### Health Monitoring
- #### Security
- ### 7. Documentation System Navigated
- #### Master Documents
- #### Quick References (20+)
- ## Key Deliverable: BRIDGE_WALKTHROUGH_COMPLETE.md
- ### Document Structure (14 Parts)
- ## Issue Detection Capabilities
- ### A. Backend Issues (8 items)
- ### B. Engine Issues (8 items)
- ### C. Frontend Issues (6 items)
- ### D. Deployment Issues (7 items)
- ### E. Security Issues (6 items)
- ### F. Performance Issues (6 items)
- ### G. Data Integrity Issues (7 items)
- ## Emergency Procedures Documented
- ### Database Recovery
- # Nuclear option: rm bridge.db && python main.py
- ### Engine Diagnostics
- ### Genesis Bus Troubleshooting
- ### Deployment Rollback
- ## Operational Knowledge
- ### Mission Lifecycle (8 steps)
- ### Self-Healing Lifecycle (5 steps)
- ## Common Operations Mastered
- ### Development Workflow
- # Backend: python main.py (port 8000)
- # Frontend: npm run dev (port 5173)
- # Seed: python seed.py
- # Test: pytest / npm test
- ### Engine Testing
- ### Monitoring
- ## Top 50 Critical Files Known
- ## Standards Upheld
- ## Conclusion


### ./docs/archive/ENVSCRIBE_IMPLEMENTATION_COMPLETE.md

- # EnvScribe v1.9.6u Implementation Summary
- ## 🎯 Mission Accomplished
- ## 📦 Components Delivered
- ### Core Engine
- ### CLI Tool
- ### Documentation
- ### Testing
- ### Integration
- ## 🔬 Test Results
- ### Unit Tests (test_envscribe.py)
- ### Integration Tests (test_envscribe_integration.py)
- ### Existing Tests (test_envsync_pipeline.py)
- ## 🚀 Capabilities
- ### Scanning & Compilation
- ### Verification
- ### Output Generation
- ### API Endpoints
- ### Genesis Integration
- ### EnvRecon Integration
- ### Truth Engine Integration
- ## 📊 Statistics
- ## 🏗️ Architecture
- ## 🎯 Use Cases Supported
- ## 🔐 Security Features
- ## 📈 Performance
- ## 🔄 Integration Status
- ## 📝 Example Outputs
- ### CLI Audit
- ### API Response (Health)
- ## 🎓 Documentation
- ## 🚦 Deployment Checklist
- ## ✅ Acceptance Criteria (from PR)
- ## 🏆 Achievement Unlocked


### ./docs/archive/WORKFLOW_FAILURE_RESOLUTION.md

- # Workflow Failure Resolution Framework
- ## Overview
- ## Components
- ### 1. Browser Dependency Resolution
- #### Reusable Workflow
- #### Composite Action
- ### 2. Sovereign Diagnostic Sweep
- ### 3. Failure Pattern Analyzer
- ### 4. PR Generator
- # Dry run (default)
- # Apply fixes
- ### 5. Failure Patterns Configuration
- ## Quick Start
- ### Running Diagnostic Sweep
- ### Using Browser Setup in Workflows
- ### Running Local Analysis
- # Analyze workflows
- # Review the report
- # Generate fixes (dry run)
- ## Workflow Failure Patterns
- ### Pattern: Browser Download Blocked
- ### Pattern: Forge Auth Failure
- ### Pattern: Deprecated Actions
- ## Monitoring and Alerts
- ### Success Criteria
- ### Metrics
- ## Architecture
- ## Files Created
- ### Workflows
- ### Actions
- ### Tools
- ### Output
- ## Contributing
- ## Security
- ## Support


### ./docs/archive/ENVRECON_USER_CHECKLIST.md

- # EnvRecon-Autonomy Integration - User Checklist
- ## ✅ What's Already Done (by AI)
- ## 📋 What You Need to Do
- ### Step 1: Configure API Credentials (Required)
- #### Render API Credentials
- #### Netlify API Credentials
- #### GitHub API Credentials
- ### Step 2: Run Initial Audit
- # Start the server
- # In another terminal, run audit
- ### Step 3: Get Missing Variables List
- # Get the report
- # Or check the file directly
- # Pretty print missing variables
- ### Step 4: Manually Sync Missing Variables
- #### Add to Render
- #### Add to Netlify
- #### Add to GitHub
- ### Step 5: Verify Sync
- # Run another audit
- # Check for remaining drift
- ## 🔍 How to Monitor Going Forward
- ### Automatic Monitoring (Already Active)
- ### Manual Monitoring
- # Check latest report
- # Trigger manual audit
- # Trigger auto-heal (reports intent only)
- ### Genesis Event Monitoring
- ## ⚠️ Important Notes
- ### Auto-Sync Limitation
- ### Variables That Must Be Manually Synced
- ## 📚 Documentation Reference
- ## 🧪 Testing
- # Run EnvRecon tests
- # Run integration tests
- ## 🎯 Success Criteria
- ## ❓ Troubleshooting
- ### "API credentials not configured" warnings
- ### Variables still showing as missing
- ### Genesis events not appearing
- ### Auto-heal not working
- ## 📞 Get Full Auto-Sync
- ## Summary


### ./docs/archive/V196C_IMPLEMENTATION_COMPLETE.md

- # SR-AIbridge v1.9.6c — Implementation Summary
- ## Overview
- ## What Was Fixed
- ### 1. Render-Safe Port Binding ✅
- ### 2. New Health & Diagnostics Endpoints ✅
- # Returns:
- # Returns:
- ### 3. Blueprint Engine Hardening ✅
- ### 4. AsyncSession Response Model ✅
- ### 5. Self-Healing Infrastructure ✅
- ## Files Changed
- ### New Files
- ### Modified Files
- ## Testing
- ### Test Coverage
- ### Manual Testing
- # Start server on custom port
- # Test health endpoints
- # {"env":{"PORT":"8888"},"resolved_port":8888,...}
- # {"flags":{"BLUEPRINTS_ENABLED":false}}
- # Test with blueprints enabled
- # Logs: [BLUEPRINTS] Enabled but routes not loadable; engine skipped.
- # {"flags":{"BLUEPRINTS_ENABLED":true}}
- ## Configuration
- ### Environment Variables
- ### Render Deployment
- ## Upgrade Path
- ## Additional Improvements (Beyond Requirements)
- ## Success Metrics
- ## Quick Verification Commands
- # 1. Verify port resolution works
- # 2. Verify health routes exist
- # 3. Verify app loads with new version
- # 4. Run v1.9.6c tests
- # 5. Start and test live
- ## Commit Messages
- ## Notes


### ./docs/archive/ENVRECON_AUTONOMY_INTEGRATION.md

- # EnvRecon-Autonomy Integration Guide
- ## Overview
- ## Architecture
- ### Components
- ## Setup Required
- ### 1. API Credentials Configuration
- #### Render API Setup
- # Add to your .env file:
- #### Netlify API Setup
- # Add to your .env file:
- #### GitHub Secrets Setup
- # Add to your .env file:
- ### 2. Genesis Configuration
- # Enable Genesis mode (should already be enabled)
- # Enable auto-healing (optional)
- # Set echo depth limit to prevent loops
- ## Current Status
- ### Missing Variables Analysis
- ### Variables That Cannot Be Auto-Fixed
- ## Usage
- ### Manual Audit
- # Using the API
- # Using the CLI
- ### Auto-Sync with Healing
- # Using the API
- # Using the CLI
- ### Check Latest Report
- # Using the API
- # Check the file directly
- ### Emergency Sync (via Autonomy)
- ## Genesis Event Monitoring
- ### Drift Detection Event
- ### Audit Complete Event
- ### Heal Complete Event
- ## Deployment Integration
- ## Troubleshooting
- ### "API credentials not configured" warnings
- ### Variables not syncing automatically
- ### Genesis events not publishing
- ## Autonomous Environment Synchronization Pipeline (v1.9.6L)
- ### New Capabilities
- #### Features
- #### Usage
- # Sync from Render to GitHub
- # Export snapshot
- # Verify parity
- #### Genesis Events
- #### Documentation
- ## Next Steps for Full Automation
- ## Summary
- ### ✅ What Works Now
- ### ⚠️ What Requires Manual Action
- ### 📋 Manual Sync Checklist


### ./docs/archive/PR_SUMMARY_V197M.md

- # Pull Request Summary: v1.9.7m Total Autonomy Protocol
- ## Overview
- ## Changes Summary
- ## New Components
- ### 1. Sanctum Engine (Predictive Simulation)
- ### 2. Forge Engine (Autonomous Repair)
- ### 3. Elysium Guardian (Continuous Monitoring)
- ## Genesis Bus Integration
- ## GitHub Actions Workflow
- ## Documentation
- ### New Documentation Files (6 total)
- ## Deployment Tools
- ### Activation Script
- ### Implementation Summary
- ## The Autonomy Cycle
- ## Testing Performed
- ## Configuration
- ### Required Environment Variables
- # Enable engines
- # Elysium settings
- # Genesis integration
- ### Optional (already set in existing configs)
- ## Post-Merge Instructions
- ## Breaking Changes
- ## Dependencies
- ## Success Criteria
- ## Related Issues
- ## Reviewer Notes
- ### Key Files to Review
- ### Testing Recommendations
- # Test individual engines
- # Run activation script
- # Trigger workflow manually
- ## Version


### ./docs/archive/PARITY_ENGINE_RUN_SUMMARY.md

- # Bridge Parity Engine Run Summary
- ## Executive Summary
- ## Analysis Results
- ### Backend Routes Discovered
- ### Frontend API Calls Discovered
- ### Missing from Backend (Needs Manual Review)
- ## Auto-Fix Actions Taken
- ### Frontend Stubs Generated
- ### Sample Generated Stub
- ### Backend Stub Documentation
- ## Test Results
- ## Reports Generated
- ### 1. Bridge Parity Report
- ### 2. Parity Auto-Fix Report
- ## Next Steps & Recommendations
- ### Immediate Actions
- ### Manual Review Required
- ### Integration Tasks
- ## Severity Classification
- ### Critical (2 endpoints)
- ### Moderate (84 endpoints)
- ### Informational (1 endpoint)
- ## Communication Status
- ### ✅ Frontend → Backend
- ### ✅ Backend → Frontend  
- ## Conclusion


### ./docs/archive/V196G_IMPLEMENTATION.md

- # V196G_IMPLEMENTATION.md
- # SR-AIbridge v1.9.6g — Predictive Stabilizer Refinement
- ## 🎯 Objective
- ## 🚀 Core Enhancements Delivered
- ### 1. ✅ Dynamic Threshold Intelligence
- ### 2. ✅ Silent Learning Mode
- ### 3. ✅ Environment-Aware Context Filter
- ### 4. ✅ Predictive Analyzer Sync
- ### 5. ✅ Auto-Adaptive Healing Loop
- ### 6. ✅ Self-Cleaning Diagnostics
- ## 📁 Files Modified
- ## 🧩 Runtime Behavior Summary
- ## 🔍 Expected Logs
- ## 🧪 Test Results
- ### v1.9.6g Tests
- ### Backward Compatibility (v1.9.6f)
- ## 🧠 Lineage Context
- ## 🪶 Closing Summary
- ## 📊 Key Metrics
- ## 🎓 Technical Highlights


### ./docs/archive/TOTAL_STACK_TRIAGE_VERIFICATION.md

- # 🌉 SR-AIbridge v1.8.2 — Total-Stack Triage Mesh Verification Report
- ## Executive Summary
- ## 📋 Component Verification
- ### 1. GitHub Actions Workflows (5/5) ✅
- ### 2. Python Triage Scripts (6/6) ✅
- ### 3. Documentation (2/2) ✅
- ### 4. Diagnostic Reports (5/5) ✅
- ## 🧪 Test Suite Verification
- ### Test Coverage:
- ## 🔍 Integration Verification
- ### Workflow Integration ✅
- ## 📊 Auto-Repair Capabilities Verified
- ### Build Triage (build_triage_netlify.py) ✅
- ### Runtime Triage (runtime_triage_render.py) ✅
- ### Environment Parity Guard (env_parity_guard.py) ✅
- ## 🎯 Signal Taxonomy Verified
- ## 📁 File Structure Summary
- ## ✅ Post-Merge Checklist Status
- ## 🔬 Script Execution Validation
- # ✅ Endpoint API Sweep
- # ✅ Environment Parity Guard
- # ✅ Deploy Triage (Unified Report)
- ## 🎉 Conclusion
- ### What This Means
- ### Next Steps
- ## 📝 Additional Notes
- ### Dependencies Installed
- ### Test Execution
- # Run the comprehensive test suite
- # Result: 22/22 tests passed ✅
- ### Known Behaviors


### ./docs/archive/BRIDGE_DIAGNOSTIC_REPORT.md

- # SR-AIbridge Diagnostic Report
- ## Executive Summary
- ## Issues Found and Fixed
- ### Critical Issue #1: Import Path Configuration ❌ → ✅
- # Fixed in main.py:
- ### Critical Issue #2: Database Configuration ❌ → ✅
- # Fixed in .env:
- ### Critical Issue #3: Engine Activation ❌ → ✅
- # Added to .env:
- ### Critical Issue #4: Blueprint Import Paths ❌ → ✅
- # Fixed in routes_linked.py:
- ## System Status: OPERATIONAL ✅
- ### Core Systems
- ### All 21 Engines Active
- ## Validation Tests Passed
- ### Basic Connectivity
- ### Health Check
- ### Engine Linkage Status
- ## Known Non-Critical Warnings
- ## Performance Metrics
- ## Files Modified
- ## Conclusion


### ./docs/archive/AUTONOMY_BACKEND_INTEGRATION_SUMMARY.md

- # Autonomy Engine Backend Integration - Complete Summary
- ## Overview
- ## What Was Accomplished
- ### 1. Systematic Integration Across 8 Major Categories
- #### Original Integration (Extended)
- #### Six Super Engines (NEW)
- #### Specialized Engines (NEW)
- #### Core Systems (NEW)
- #### Tools & Runtime (NEW)
- #### Heritage & MAS (NEW)
- ### 2. Files Created
- ### 3. Files Modified
- ## Architecture
- ### Event Flow Pattern
- ### Intelligent Routing
- ### Safety Features
- ## Integration Statistics
- ## Testing & Validation
- ### Test Coverage
- ### Validation Commands
- ## Usage Examples
- ### 1. Health Monitoring with Auto-Healing
- # Degraded status triggers autonomy healing
- ### 2. Firewall Threat Response
- # High threat triggers autonomy healing
- ### 3. MAS Agent Coordination
- # Agent failure triggers autonomy healing
- ### 4. Guardians Safety Validation
- # Dangerous action blocked by guardians
- # Results in autonomy.action_blocked event
- ## Benefits
- ## Next Steps (Optional Enhancements)
- ## Files Summary
- ### Created (4 files, 950 lines)
- ### Modified (4 files)
- ### Total Impact
- ## Conclusion


### ./docs/archive/COMPREHENSIVE_SCAN_REPORT.md

- # Comprehensive Repository & Environment Scan Report
- ## ✅ STUB CLEANUP COMPLETED (October 11, 2025)
- ### Completed Fixes:
- ## 📊 Executive Summary
- ## 🗑️ Files Recommended for Cleanup
- ### 1. Duplicate Files (7 files)
- ### 2. Redundant Documentation (38 files)
- ### 3. Dead/Unused Files (6 files)
- ## 🔧 Environment Variables Requiring Manual Configuration
- ### Priority: HIGH - API Credentials (6 variables)
- ### Priority: HIGH - Deployment Configuration (8 variables)
- ### Priority: MEDIUM - Application Configuration (35 variables)
- ## 🌐 Environment Sync Status (EnvRecon Engine)
- ## 📋 Recommended Action Plan
- ### Phase 1: Cleanup (Low Risk)
- ### Phase 2: Environment Setup (Required)
- ### Phase 3: Configuration Review (Important)
- ## 📄 Detailed Reports
- ## 🚀 Next Steps
- ## ✅ CLEANUP COMPLETED
- ### Cleanup Results:
- ### Archive Location:
- ### What Was Kept:


### ./docs/archive/HXO_NEXUS_CONNECTIVITY.md

- # HXO Nexus Connectivity Implementation
- ## Overview
- ## Architecture
- ### Core Components
- ### Engine Connectivity Map
- ### Connection Topology
- ## The "1+1=∞" Paradigm
- ### 1. Universal Connectivity
- ### 2. Harmonic Resonance
- ### 3. Emergent Synergy
- ### 4. Infinite Scaling
- ## Core Properties
- ## HypShard v3 Features
- ### Quantum Adaptive Sharding
- ### Control Channels
- ### Policies
- ## Security Layers
- ### 1. RBAC Scope
- ### 2. Quantum Entropy Hashing (QEH-v3)
- ### 3. Rollback Protection
- ### 4. Recursion Limit
- ### 5. Audit Trail
- ## Harmonic Consensus Protocol (HCP)
- ### Consensus Modes
- ### Consensus Flow
- ## API Endpoints
- ### Health & Status
- ### Engine Management
- ### Connectivity
- ### Orchestration
- ## Configuration
- ### Environment Variables
- # HXO Nexus
- # HypShard v3
- # QEH-v3
- ## Usage Examples
- ### Initialize the Nexus
- # Initialize HXO Nexus
- # Check health
- ### Register an Engine
- # Register a custom engine
- ### Coordinate Multiple Engines
- # Define an intent requiring multiple engines
- # Coordinate execution
- ### Use HypShard v3
- # Create a shard
- # Execute task on shard
- # Get statistics
- ### Achieve Consensus
- # Create proposal
- # Engines vote
- ## Integration with Genesis Bus
- ### Subscribed Topics
- ### Published Events
- ## Testing
- # Run HXO Nexus tests
- # Expected: 34 tests pass
- # - Core functionality: 9 tests
- # - Async operations: 2 tests
- # - HypShard v3: 7 tests
- # - Security layers: 8 tests
- # - Connectivity paradigm: 4 tests
- # - Consensus protocol: 4 tests
- ## Version History
- ## Meta Information
- ## Future Enhancements


### ./docs/archive/FORGE_DOMINION_ENVIRONMENT_INTEGRATION.md

- # 🜂 Sovereign Dominion Token Forge - Environment Integration Guide
- ## 🎯 Overview
- ### Key Principles
- ## 🔧 Setup Instructions
- ### Step 1: Generate Root Key
- ### Step 2: Set GitHub Secret
- ### Step 3: Set GitHub Variables (Optional)
- ### Step 4: Verify Setup
- ## 📋 Environment Files
- ### Main Environment Files
- ### Example/Template Files
- ### Placeholder Pattern
- ## 🔄 Token Lifecycle
- ### Minting Tokens
- ### Token Providers
- ### Token Validation
- ### Auto-Renewal
- ## 🔐 Security Features
- ### 1. Sealed Issuance
- ### 2. Short Lifespan
- ### 3. Continuous Audit
- ### 4. Governance Pulse
- ## 📦 GitHub Actions Integration
- ### Using the Forge Dominion Setup Action
- ### Updated Workflows
- ### Migration Pattern for Other Workflows
- ## 🧪 Testing
- ### Local Testing
- ### Running Tests
- # Test Token Forge module
- # Test Quantum Dominion integration
- ### Secret Scanner Test
- ## 🔍 Troubleshooting
- ### Issue: "No FORGE_DOMINION_ROOT"
- ### Issue: "Secret detection failed"
- ### Issue: "Token validation fails"
- # Force renewal for specific provider
- ### Issue: Workflow fails with token errors
- ## 📊 Token Forge Modules
- ## 🎯 Benefits of Token Forge
- ### Before Token Forge
- ### After Token Forge
- ## 📚 Additional Resources
- ## ✅ Checklist: Environment Cleanup Complete


### ./docs/archive/AUTONOMY_DEPLOYMENT_COMPLETE.md

- # Autonomy Engine Deployment Integration - Implementation Summary
- ## 🚀 Mission Accomplished!
- ## What Was Implemented
- ### 1. Genesis Bus Integration ✅
- ### 2. Autonomy Genesis Link Integration ✅
- ### 3. Deployment Event Publisher ✅
- ### 4. Webhook Endpoints ✅
- ### 5. Autonomy Engine API Endpoints ✅
- ### 6. GitHub Actions Integration ✅
- ### 7. Main Application Integration ✅
- ### 8. Documentation ✅
- ### 9. Verification Script ✅
- ## Architecture
- ### Event Flow
- ## Files Summary
- ### Created (5 files, ~1,500 lines)
- ### Modified (6 files)
- ### Total Impact
- ## Integration Statistics
- ### Genesis Bus
- ### Webhook Endpoints
- ### API Endpoints
- ### GitHub Actions
- ### Documentation
- ## Testing
- ### Verification Results ✅
- ### Code Quality ✅
- ## Configuration
- ### Required Environment Variables
- # Enable Genesis mode (required)
- # Optional: Strict topic validation
- ### GitHub Secrets (Already Configured)
- ## Usage Examples
- ### CLI Event Publishing
- # Netlify deployment
- # Render deployment
- # GitHub workflow
- ### API Event Publishing
- ### Check Integration Status
- # Webhook status
- # Autonomy deployment status
- ## Next Steps
- ### For Setup (User Action Required)
- ### Optional Enhancements
- ## Benefits Delivered
- ## Conclusion
- ### Status: ✅ Complete and Verified


### ./docs/archive/GENESIS_V2_0_1_IMPLEMENTATION_COMPLETE.md

- # Genesis v2.0.1 Implementation Complete ✅
- ## PR: v2.0.1 — Project Genesis: Universal Engine Assimilation
- ## What Was Built
- ### 1. Genesis Core Contract (GCC) ✅
- ### 2. Universal Adapters ✅
- ### 3. Guardians-First Safety ✅
- ### 4. Event Persistence & Replay ✅
- ### 5. Genesis Bus Integration ✅
- ### 6. PORT Resolution Fixed ✅
- ### 7. Render Configuration Updated ✅
- ### 8. Main.py Startup Updates ✅
- ### 9. TDE-X v2 Orchestrator ✅
- ### 10. TDE-X v2 Stages ✅
- ### 11. FastAPI Response Models ✅
- ### 12. Blueprint Optional Router ✅
- ### 13. Comprehensive Tests ✅
- # 25 passed, 47 warnings in 0.60s
- ### 14. Documentation ✅
- ## Acceptance Criteria Status
- ## Files Changed
- ### New Files (15)
- ### Modified Files (4)
- ## Configuration
- ### Required Environment Variables
- # Genesis
- # Guardians
- # TDE-X v2
- # Port (Render sets automatically)
- ### Render Deployment
- ## Success Metrics
- ## Breaking Changes
- ## Migration Path
- ### Immediate (Required for Render)
- ### Gradual (Recommended)
- ## Example Usage
- ### Emit a Fact
- ### Report Health Issue
- ### Subscribe to Events
- ### Replay Events
- # Replay from watermark 100
- # Replay Truth engine events
- ## Next Steps
- ## Support
- ## Summary


### ./docs/archive/BRIDGE_WALKTHROUGH_COMPLETE.md

- # SR-AIbridge Complete Walkthrough
- ## Git Sovereign Agent - Full Bridge Mastery Documentation
- ## Executive Summary
- ### Repository Metrics
- ### System Architecture Classification
- ## Part I: Core Architecture
- ### 1. Entry Point & Boot Sequence
- ### 2. Database Layer (SQLite-first, PostgreSQL-ready)
- ### 3. Genesis Event Bus (The Central Nervous System)
- # Core Genesis topics
- # Blueprint & Deployment
- # Triage (Autonomy Integration)
- # Federation
- # Parity
- # Autonomy Reflex Loop
- # Super Engines (6 engines × multiple topics each)
- # Core Systems
- # Umbra Cognitive Stack (v1.9.7g)
- # HXO Nexus (Harmonic Conductor)
- # Chimera Deployment Engine (v1.9.7c)
- ### 4. The 20+ Engine Orchestra
- #### A. Core Infrastructure Engines (6)
- #### B. Super Engines (6 Specialized AI)
- #### C. Orchestrator (1)
- #### D. Utility Engines (7+)
- #### E. Advanced Systems (Additional Engines)
- ## Part II: Advanced Systems
- ### 5. Forge Dominion (Token Management) - v1.9.7s
- ### 6. Bridge Runtime Handler (BRH) - v1.0.0-alpha
- ### 7. Git Sovereign Agent (Your Role) - v1.0.0 "Cosmic"
- ## Part III: Frontend Architecture
- ### 8. React Dashboard (`bridge-frontend/`)
- #### Core Dashboard
- #### Mission & Agent Management
- #### Monitoring & Health
- #### Communication
- #### Data & Logging
- #### Administration
- ## Part IV: Deployment & Operations
- ### 9. CI/CD Pipeline (`.github/workflows/`)
- ### 10. Health Monitoring & Self-Healing
- ## Part V: Security Architecture
- ### 11. Forge Dominion Security Model
- ## Part VI: Testing & Validation
- ### 12. Testing Infrastructure
- # Test all 6 super engines
- # Test all API endpoints
- # Validate Genesis unified system
- # Run repository study (Parser + Blueprint + Truth engines)
- # Quick production health check
- # CI/CD optimized
- ## Part VII: Documentation System
- ### 13. Documentation Architecture (370 Markdown Files)
- ## Part VIII: Advanced Capabilities
- ### 14. Genesis Linkage System
- ### 15. Umbra Cognitive Stack (v1.9.7g)
- ### 16. HXO Nexus (v1.9.6p) - Harmonic Conductor
- ## Part IX: Key Operational Patterns
- ### 17. Mission Lifecycle
- ### 18. Self-Healing Lifecycle
- ## Part X: Common Operations
- ### 19. Development Workflow
- # 1. Clone repository
- # 2. Start backend
- # Runs on http://localhost:8000
- # 3. Start frontend (new terminal)
- # Runs on http://localhost:5173 (or 3000)
- # 4. Access points
- # - Frontend: http://localhost:5173
- # - Backend API: http://localhost:8000
- # - API Docs: http://localhost:8000/docs
- # - Health: http://localhost:8000/health/full
- # 5. Seed demo data
- # 6. Run tests
- ### 20. Engine Testing
- # Test all 6 super engines
- # Test specific engine
- # Response: {"result": "(x + 1)^2", ...}
- # Test Genesis linkage
- # Test Blueprint engine
- ### 21. Monitoring & Debugging
- # Health check
- # System metrics
- # Genesis event history
- # Guardian status
- # Vault logs (filter by level)
- # WebSocket stats (use wscat or browser)
- ## Part XI: Critical Files Reference
- ### 22. Must-Know Files (Top 50)
- ## Part XII: Issue Detection Checklist
- ### 23. What to Watch For (Your Responsibilities)
- #### A. Backend Issues
- #### B. Engine Issues
- #### C. Frontend Issues
- #### D. Deployment Issues
- #### E. Security Issues
- #### F. Performance Issues
- #### G. Data Integrity Issues
- ## Part XIII: Emergency Procedures
- ### 24. If Things Go Wrong
- # Self-heal
- # Nuclear option: Recreate database
- # Check which engines are failing
- # Check Genesis bus status
- # Restart specific engine (feature flag)
- # Check event bus health
- # Review event history
- # Check topic subscriptions
- # Netlify: Use dashboard to rollback
- # Render: Redeploy previous commit
- # BRH: Use bridge.runtime.yaml to specify version
- ## Part XIV: Advanced Topics
- ### 25. Extending the Bridge
- ## Conclusion


### ./docs/archive/AUTONOMY_INTEGRATION_COMPLETE.md

- # Autonomy Integration - Implementation Complete ✅
- ## Mission Accomplished
- ## What Was Implemented
- ### 1. Triage Integration (3 event types)
- ### 2. Federation Integration (2 event types)
- ### 3. Parity Integration (2 event types)
- ## Integration Architecture
- ## Files Modified (13 total)
- ### Core Integration (2 files)
- ### Triage Integration (3 files)
- ### Federation Integration (1 file)
- ### Parity Integration (3 files)
- ### Testing & Verification (2 files)
- ### Documentation (4 files)
- ## Integration Points Summary
- ## Event Flow
- ### Triage → Autonomy → Healing
- ### Federation → Autonomy → Coordination
- ### Parity → Autonomy → Fixing
- ## Testing & Verification
- ### Unit Tests
- ### Integration Verification
- ### Manual Testing
- # Test triage integration
- # Test parity integration
- # Test federation integration (in Python REPL)
- ## Configuration
- ### Enable Integration
- ### Verify Status
- # Check Genesis bus
- ## Benefits
- ## Next Steps
- ## Support & Documentation
- ## Success Metrics


### ./docs/archive/ENVRECON_UNFIXABLE_VARS.md

- # Variables That Cannot Be Auto-Fixed - Quick Reference
- ## Summary
- ## Categories of Unfixable Variables
- ### 1. API Credentials (Must Be Configured First)
- # Render API
- # Netlify API
- # GitHub API
- ### 2. Platform-Specific Variables (Manual Sync Required)
- #### Add to Render:
- #### Add to Netlify:
- #### Add to GitHub:
- ## Current Missing Variables Count
- ## To Get Accurate Missing Variables List
- ## Auto-Heal Capabilities
- ### What Auto-Heal Can Do Now:
- ### What Auto-Heal Cannot Do Yet:
- ## Workaround: Manual Sync Process
- ## Genesis Events for Monitoring
- ## Future Enhancement: Full Auto-Sync
- ## Contact for Implementation
- ## Quick Commands
- # Check if API credentials are configured
- # Run audit
- # Get report
- # Trigger auto-heal (reports intent only)
- # Check Genesis health
- ## Documentation


### ./docs/archive/BRH_IMPLEMENTATION_SUMMARY.md

- # Bridge Runtime Handler - Implementation Summary
- ## 🎯 Executive Summary
- ### Key Achievement
- ## ✅ Phase 1 Completion Status
- ## 📦 Deliverables
- ### Core Components
- ### Testing
- ## 🏗️ Architecture
- ### Component Diagram
- ### Integration Points
- ## 🔐 Security Features
- ### Token Management
- ### Cryptographic Attestation
- ### Network Security
- ## 📊 Metrics & Performance
- ### Test Results
- ### Code Quality
- ## 🚀 Usage Examples
- ### Quick Start
- # 1. Initialize BRH
- # 2. Validate manifest
- # 3. Check status
- # 4. Deploy via GitHub
- ### Manual Runtime
- # Set Forge key
- # Run runtime
- ## 📋 Next Steps
- ### Phase 2: GitHub Integration (Planned)
- ### Phase 3: Federation Linking (Planned)
- ### Phase 4: UI Integration (Planned)
- ## 🎓 Lessons Learned
- ### What Went Well
- ### Challenges Overcome
- ### Best Practices Established
- ## 🤝 Integration with Existing Systems
- ### Successfully Integrated With
- ### Prepared For Integration
- ## 📚 Resources
- ### Documentation
- ### Code Files
- ## ✨ Conclusion


### ./docs/archive/FINAL_VERIFICATION_REPORT.md

- # Final Verification Report - Render Removal Complete
- ## Executive Summary
- ## Verification Results
- ### ✅ Code Review
- ### ✅ Security Scan (CodeQL)
- ### ✅ Backend Integration
- ### ✅ BRH Setup
- ### ✅ Configuration Updates
- ### ✅ Files Removed
- ## Scan Statistics
- ### Before Migration
- ### After Migration
- ### Remaining Render References (Non-Critical)
- ## Test Results
- ### Import Test
- # Result: ✅ Backend OK
- ### Token Forge Test
- # Result: ✅ Token Forge OK
- ### Backend Boot Test
- # Backend starts successfully
- # Genesis bus initializes
- # All routes load (except missions - pre-existing issue)
- # Forge integration active
- ## Deployment Readiness
- ### Environment Variables (Production)
- # BRH Backend
- # Frontend (Netlify)
- # Backend
- ### Deployment Commands
- # Start BRH
- # Deploy Frontend
- # Deploy to Netlify with VITE_API_BASE set
- ## Risk Assessment
- ### Low Risk
- ### Mitigation for Remaining References
- ## Recommendations
- ## Sign-off
- ### Files Created
- ### Commits Made


### ./docs/archive/COMPLIANCE_IMPLEMENTATION_SUMMARY.md

- # Compliance Integration Implementation Summary
- ## Implementation Complete ✅
- ## Changes Made
- ### 1. Enhanced API Routes
- ### 2. Enhanced Autonomy Engine Service
- ### 3. Comprehensive Test Suite
- ### 4. Documentation
- ## API Endpoints
- ### Created
- ### Enhanced
- ## Features
- ### Compliance Validation
- ### LOC Tracking
- ### States
- ## Integration Points
- ### Existing Components Used
- ### New Components
- ## Backward Compatibility
- ## Configuration
- ## Testing Results
- ## Benefits
- ## Usage Example
- # Create task with compliance validation
- # Check compliance
- # Update metrics
- ## Files Modified
- ## Files Created
- ## Next Steps
- ## Conclusion


### ./docs/archive/RENDER_REMOVAL_COMPLETE.md

- # Render Removal - Migration to BRH Complete
- ## Summary
- ## Changes Made
- ### 1. Frontend Configuration Updates ✅
- ### 2. Backend Configuration Updates ✅
- # Old CORS
- # New CORS (BRH-focused)
- ### 3. Files Removed ✅
- ### 4. Verification Status ✅
- ## Architecture
- ### New Deployment Flow
- ## Environment Variables
- ### Frontend (.env or environment)
- # BRH Backend URL (update for production deployment)
- # Or for production BRH deployment
- # VITE_API_BASE=https://your-brh-domain.com
- ### Backend (.env or environment)
- # Database
- # CORS (Netlify only, no Render)
- # BRH Backend URL (for heartbeat and health checks)
- # Forge Dominion
- ## Remaining References (Non-Critical)
- ### Documentation/Examples
- ### Adapters (Backward Compatibility)
- ## How to Deploy
- ### Local Development
- # 1. Start BRH
- # 2. Access frontend
- # Frontend will connect to http://localhost:8000
- ### Production Deployment
- # 1. Set environment variables
- # 2. Run BRH
- # 3. Deploy frontend to Netlify with:
- # VITE_API_BASE=https://your-brh-domain.com
- ## Testing
- ### Quick Test
- # 1. Verify backend imports
- # 2. Start backend
- # 3. Test health endpoint
- ### Frontend Build Test
- ## Migration Checklist
- ## Next Steps (Optional)
- ## Conclusion


### ./docs/archive/ENGINE_INTEGRATION_SUMMARY.md

- # Engine Integration Summary
- ## Overview
- ## Changes Made
- ### 1. Autonomy Engine Service (`bridge_backend/bridge_core/engines/autonomy/service.py`)
- ### 2. Autonomy Engine Routes (`bridge_backend/bridge_core/engines/autonomy/routes.py`)
- ### 3. Blueprint Registry (`bridge_backend/bridge_core/engines/blueprint/registry.py`)
- ### 4. Tests (`bridge_backend/tests/test_autonomy_engine.py`)
- ### 5. Documentation
- ## Integration Points
- ### Anti-Copyright Engine (Compliance Scan)
- ### LOC Engine
- ### Autonomy Engine
- ## Benefits
- ## Compliance States
- ## Example Task Contract
- ## Testing
- ## Configuration
- ## Future Enhancements
- ## Conclusion


### ./docs/archive/V196B_IMPLEMENTATION_COMPLETE.md

- # v1.9.6b Implementation Complete ✅
- ## Summary
- ## Implementation Details
- ### 1. Core Dependencies Updated ✅
- ### 2. Render Configuration Fixed ✅
- ### 3. Netlify CORS Alignment ✅
- ### 4. Database Auto-Schema Sync ✅
- ### 5. Heartbeat System v1.9.6b ✅
- ### 6. Release Intelligence ✅
- ### 7. Predictive Stabilizer ✅
- # Stabilization Ticket: `bridge_backend/models/core.py`
- ## Suggested actions
- ### 8. GitHub Issue Integration ✅
- ### 9. Application Bootstrap Updated ✅
- ### 10. Documentation & Configuration ✅
- ### 11. Testing & Verification ✅
- ## What This Fixes
- ### 1. ✅ Render Port Scan Timeouts
- ### 2. ✅ Heartbeat "Disabled" Issues
- ### 3. ✅ Models Import Errors
- ### 4. ✅ Database Missing Tables
- ### 5. ✅ Manual Stability Monitoring
- ## Deployment Checklist
- ### One-Time Setup (Render)
- ### Verification After Deploy
- ## Files Changed
- ### Modified (6 files)
- ### Created (13 files)
- ## Next Steps
- ## Additional Notes


### ./docs/archive/UNIFICATION_COMPLETE.md

- # 🎉 Genesis Linkage Unification - COMPLETE
- ## Mission Accomplished
- ## What Was Achieved
- ### Before
- ### After
- ## Engines Added (14 New)
- ### Super Engines (6)
- ### Orchestration (1)
- ### Utility Engines (7)
- ## New Components Created
- ### Adapter Modules (3)
- ### API Endpoints (3 New, 8 Total)
- ### Documentation (3 New Files)
- ### Validation (1 New Script)
- ## Code Changes Summary
- ### Files Modified (3)
- ### Files Created (7)
- ## Validation Results
- ## Dependency Graph (Complete)
- ## Event Bus Integration
- ### Event Topics: 33 Total
- ## API Capabilities
- ### Status & Monitoring
- # Overall status - all 20 engines
- # Super engines status
- # Utility engines status
- # Leviathan coordination
- ### Blueprint Access
- # Complete manifest
- # Specific engine
- # Dependencies
- ### Management
- # Initialize all linkages
- ## Key Features
- ### 1. Unified Schema
- ### 2. Coordinated Execution
- ### 3. Hierarchical Organization
- ### 4. Complete Validation
- ### 5. Comprehensive Documentation
- ## Deployment
- ### Requirements
- ### Validation
- ### Verification
- # Expected: 20
- ## Impact
- ### Before Unification
- ### After Unification
- ## Next Steps
- ## Success Metrics
- ## Conclusion


### ./docs/archive/FULL_SCAN_REPORT_2025.md

- # Full System Scan Report - November 2025
- ## ✅ Executive Summary
- ## 📊 Detailed Scan Results
- ### 1. ✅ Quantum Dominion Security
- ### 2. ✅ API Triage
- ### 3. ✅ Preflight
- ### 4. ✅ Umbra Triage
- ### 5. ✅ Build Triage (Netlify)
- ### 6. ✅ Endpoint API Sweep
- ### 7. ✅ Environment Parity Guard
- ### 8. ✅ Runtime Triage (Render)
- ## 🔍 Workflow Verification
- ### ✅ Triage Workflows (7/7)
- ### ✅ Security Workflows (1/1)
- ### ✅ Deployment Workflows (2/2)
- ## 🔧 Script Verification
- ### GitHub Scripts (8/8)
- ### Backend Scripts (3/3)
- ## 🐍 Python Module Verification
- ## 📈 Scan Statistics
- ## ⚠️ Known Issues & Expected Behaviors
- ### Expected in Development/CI Environment:
- ### Informational Findings:
- ## ✅ Recommendations
- ### Immediate Actions: None Required
- ### Optional Enhancements:
- ## 📋 Compliance Matrix
- ## 🎯 Conclusion
- ### Next Steps


### ./docs/archive/PHOENIX_SUMMARY.md

- # Phoenix Protocol - Summary Report
- ## 🔥 What is the Phoenix Protocol?
- ### Key Principle
- ## 📋 Current Status
- ### ✅ Phase 1: Core Backend - **COMPLETE**
- ## 🧪 Testing Results
- # Health Check
- # Full Health with Metrics
- # Create Agent
- # CalculusCore - Differentiation
- # CalculusCore - Factoring
- ## 📊 Comparison: Phoenix vs Current
- ### Key Findings
- ## 🎯 What's Next
- ### Phase 2: Five More Engines
- ### Phase 3: Support Systems
- ### Phase 4: Frontend
- ### Phase 5: Advanced Features
- ### Phase 6: Deployment & Testing
- ## 📈 Progress Tracking
- ## 🎓 Lessons Learned
- ### What Worked Well
- ### What We Discovered
- ### Recommendations
- ## 🚀 How to Use Phoenix
- ### Run Phoenix Backend
- # Setup (first time)
- # Run (uses port 8001)
- # Access
- # API: http://localhost:8001
- # Docs: http://localhost:8001/docs
- # Health: http://localhost:8001/health
- ### Test Endpoints
- # Health check
- # Create agent
- # Create mission
- # Math engine
- ### Compare with Current
- # Run both simultaneously
- # Compare health
- # Compare agent structure
- ## 📚 Documentation
- ## 🏆 Achievements
- ## 🔥 Conclusion


### ./docs/archive/V196H_IMPLEMENTATION_COMPLETE.md

- # SR-AIbridge v1.9.6h — Implementation Complete
- ## Summary
- ## What Was Fixed
- ### 1. Port Parity (Render) ✅
- ### 2. Deploy Parity Engine ✅
- ### 3. Health Endpoints ✅
- ### 4. Blueprint Model Export Fix ✅
- ### 5. Incident Replay ✅
- ### 6. Seed Bootstrap ✅
- ### 7. Environment Configuration ✅
- ### 8. Heartbeat/httpx Tolerance ✅
- ### 9. Version Update ✅
- ## Testing
- ## Files Modified/Created
- ### New Files
- ### Modified Files
- ## Verification
- ### Local Testing
- # Set required environment variables
- # Start the server
- # Server starts on port 10000 ✅
- # Deploy parity check passes ✅
- # All routes registered ✅
- ### Key Endpoints
- ### Test Results
- # ======================================================================
- # SR-AIbridge v1.9.6h Test Suite
- # ======================================================================
- # Results: 13/13 tests passed
- # ✅ All tests passed!
- ## Deployment Notes
- ### Render Configuration
- ### First Deploy
- ### Troubleshooting
- ## Backward Compatibility
- ## Next Steps
- ## Changelog (Concise)


### ./docs/archive/STEWARD_JSON_FEATURE_COMPLETE.md

- # 🎉 Feature Complete: Steward Environment Drift JSON Reporting
- ## What Was Delivered
- ## ✅ Implementation Summary
- ### Changes Made
- ## 🚀 How to Use
- ### Quick Start
- # Enable Steward
- # Get the JSON report
- ### API Endpoint
- ### Python Code
- ## 📊 JSON Report Format
- ## ✨ Features
- ## 🛡️ Security
- ## 📝 Current State
- ## 🎯 Next Steps
- ### Now (Read-Only Mode)
- ### Later (When Ready for Write Mode)
- ## 📚 Documentation
- ## 🎉 Summary


### ./docs/archive/DOCUMENTATION_ENHANCEMENT_PLAN.md

- # SR-AIbridge Documentation Enhancement Plan
- ## Comprehensive Documentation Improvement Strategy
- ## 🎯 Executive Summary
- ## 📊 Current State Analysis
- ### Documentation Coverage
- ### File Statistics
- ### Documentation Quality Issues
- ## 🎯 Enhancement Goals
- ### Primary Goals
- ### Secondary Goals
- ## 📋 Documentation Inventory
- ### Undocumented Features
- #### Backend Modules (Missing Primary Docs)
- #### Engines (Incomplete Docs)
- #### Frontend Components (Missing Docs)
- ## 📝 Enhancement Tasks
- ### Phase 1: Foundation (Week 1)
- #### Task 1.1: Create Master Documentation Index
- #### Task 1.2: Update Navigation Documents
- #### Task 1.3: Consolidate Scattered Documentation
- ### Phase 2: Core Documentation (Week 2)
- #### Task 2.1: Update BUILD_DOSSIER.md
- #### Task 2.2: Update SYSTEM_BLUEPRINT.md
- #### Task 2.3: Enhance ENGINE_CATALOG.md
- ### Phase 3: Feature Documentation (Week 3)
- #### Task 3.1: Document Backend Modules
- #### Task 3.2: Document Frontend Components
- #### Task 3.3: Document Advanced Features
- ### Phase 4: Examples & Tutorials (Week 4)
- #### Task 4.1: Create Tutorial Series
- #### Task 4.2: Add Code Examples
- #### Task 4.3: Create Quick References
- ### Phase 5: Integration & Polish (Week 5)
- #### Task 5.1: Cross-Reference Everything
- #### Task 5.2: Improve README.md
- #### Task 5.3: Validate & Test
- ## 📚 New Documentation Structure
- ### Proposed Hierarchy
- ## 🎯 Success Metrics
- ### Quantitative Metrics
- ### Qualitative Metrics
- ## 🚀 Implementation Plan
- ### Week 1: Foundation
- ### Week 2: Core Updates
- ### Week 3: Feature Documentation
- ### Week 4: Examples & Tutorials
- ### Week 5: Integration & Polish
- ## 📈 Progress Tracking
- ### Current Status
- ### Target Status (5 Weeks)
- ## 🎓 Lessons from Phoenix Protocol
- ## 🔗 References


### ./docs/archive/SCAN_REPORT_RENDER_REMOVAL.md

- # Repository Scan Report - Render Removal Readiness
- ## Summary
- ## Issues
- ## Information
- ## Render References by File
- ### bridge_backend/bridge_core/engines/envsync/providers/render.py
- ### bridge_backend/diagnostics/full_scan_report.json
- ### bridge_backend/engines/envrecon/core.py
- ### bridge_backend/engines/steward/adapters/render_adapter.py
- ### bridge_backend/hooks_triage_report.json
- ### bridge_backend/scripts/deploy_diagnose.py
- ### bridge_backend/scripts/endpoint_triage.py
- ### bridge_backend/scripts/env_sync_monitor.py
- ### bridge_backend/scripts/generate_sync_badge.py
- ### bridge_backend/scripts/hooks_triage.py
- ### bridge_backend/tests/test_runtime_guards.py
- ### bridge_backend/tests/test_total_stack_triage.py
- ### bridge_backend/tools/firewall_intel/analyze_firewall_findings.py
- ### bridge_backend/tools/firewall_intel/fetch_firewall_incidents.py
- ### bridge_backend/tools/network_diagnostics/check_copilot_access.py
- ### bridge_backend/tools/parity_engine.py
- ### netlify.toml
- ### scripts/check_env_parity.py
- ### scripts/firewall_watchdog.py
- ### scripts/integrity_audit.py
- ### scripts/repair_netlify_env.py
- ### scripts/synthesize_netlify_artifacts.py
- ### scripts/validate_copilot_env.py
- ### test_endpoints_full.py
- ### tests/test_anchorhold_protocol.py
- ### tests/test_v196g_features.py


### ./docs/archive/V198_ENVSYNC_IMPLEMENTATION.md

- # EnvSync Engine v1.9.8 - Implementation Complete ✅
- ## What Was Delivered
- ## Components Implemented
- ### 1. Core Engine (`bridge_backend/bridge_core/engines/envsync/`)
- #### Configuration System (`config.py`)
- #### Type System (`types.py`)
- #### Diff Engine (`diffs.py`)
- #### Token Discovery Chain (`discovery/`)
- #### Provider Adapters (`providers/`)
- #### Sync Engine (`engine.py`)
- #### Background Scheduler (`tasks.py`)
- #### Telemetry (`telemetry.py`)
- ### 2. API Routes (`routes.py`)
- ### 3. Integration Layer
- #### Main Application (`main.py`)
- #### Vault Integration (`bridge_core/vault/routes.py`)
- #### Genesis & Autonomy Adapter (`adapters/envsync_autonomy_link.py`)
- ### 4. CI/CD Integration
- #### GitHub Actions (`.github/workflows/envsync.yml`)
- ### 5. Documentation
- #### Comprehensive Guide (`docs/ENVSYNC_ENGINE.md`)
- ### 6. Testing
- #### Unit Tests (`tests/test_envsync_engine.py`)
- ## Key Features
- ### 🔐 Smart Token Discovery
- ### 🎯 Idempotent Sync
- ### 🔍 Rich Diffing
- ### 🛡️ Dry-Run Mode
- ### ⚙️ Flexible Filtering
- ### 🌐 Genesis Bus Integration
- ### 🤖 Autonomy Engine Support
- ### 📊 Telemetry & Diagnostics
- ## Environment Variables
- ### Core Settings
- ### Discovery Configuration
- ### Provider Settings
- ### Filtering
- ## File Structure
- ## Integration Points
- ### 1. FastAPI Application
- ### 2. Startup Lifecycle
- ### 3. Genesis Bus
- ### 4. Autonomy Engine
- ### 5. Vault System
- ### 6. CI/CD Pipeline
- ## Verification Results
- ### ✅ Import Test
- ### ✅ Route Registration
- ### ✅ Unit Tests
- ### ✅ Genesis Integration
- ### ✅ Integration Test
- ## Usage Workflow
- ### 1. Configure Environment
- ### 2. Preview Changes (Dry-Run)
- ### 3. Apply Sync
- ### 4. Monitor
- ### 5. Automate
- ## Security Considerations
- ### ✅ Implemented
- ### 📝 Production Recommendations
- ## Performance
- ## Error Handling
- ## What's Next (Optional Enhancements)
- ## Changelog
- ### v1.9.8 (2025-10-11)


### ./docs/archive/TDE_X_IMPLEMENTATION_SUMMARY.md

- # TDE-X v1.9.7a Implementation Summary
- ## Overview
- ## Implementation Date
- ## Changes Summary
- ### New Files Created (16 files)
- #### Core TDE-X Modules (9 files)
- #### Support Modules (1 file)
- #### Infrastructure (2 files)
- #### Documentation (2 files)
- ### Modified Files (4 files)
- ## Key Features Implemented
- ### 1. Hypersharded Deployment
- ### 2. Fault Isolation
- ### 3. Background Task Queue
- ### 4. Federation Hooks
- ### 5. Enhanced Health Endpoints
- ## Testing Results
- ## Deployment Configuration
- ### Render Settings
- ## Architecture Diagram
- ## Problems Solved
- ## Migration Notes
- ## Rollback Plan
- ## Next Steps
- ## Documentation
- ## Commits
- ## Sign-off


### ./docs/sovereignty/README.md

- # Firewall & Network Sovereignty Architecture
- ## 🎯 Mission Statement
- ## 🚀 Quick Start
- ## 📚 Documentation
- ## 🏗️ Architecture Components
- ### 1. Firewall Configuration Manager
- ### 2. Network Resilience Layer
- ### 3. Validation Sovereignty
- ### 4. Script Execution Sovereignty
- ### 5. Sovereign Orchestrator
- ## ✅ Test Results
- ## 📊 Key Metrics
- ## 🔄 GitHub Actions Integration
- ## 📁 Generated Files
- ### Configuration Files
- ### Diagnostic Reports
- ## 🛠️ Common Commands
- ### Execute Individual Systems
- # Firewall configuration
- # Network health check
- # Validation check
- # Script execution check
- ### View Reports
- # Latest sovereignty report
- # Network health
- ### Quick Status Check
- ## 🔐 Security Features
- ## 📈 Monitoring & Observability
- ## 🎓 Design Principles
- ### Sovereign Mindset
- ### Architectural Goals
- ## 🚨 Troubleshooting
- ### Common Issues
- # Check configuration
- # Review health report
- # Check dependency status
- ## 🔄 Extending the Architecture
- ## 📦 Dependencies
- ## 🎯 Success Criteria
- ## 🏆 Results


### ./docs/sovereignty/SOVEREIGNTY_QUICK_REFERENCE.md

- # Sovereignty Quick Reference
- ## One-Line Commands
- ### Execute Complete Sovereignty Protocol
- ### Individual Systems
- #### Firewall Configuration
- #### Network Health Check
- #### Validation Check
- #### Script Execution Check
- ### Run All Tests
- ## View Reports
- ### Latest Sovereignty Report
- ### Network Health
- ### Validation Results
- ## Key Metrics Quick Check
- ## Configuration Files
- ### Allowlist
- ### Egress Policies
- ### Firewall Rules
- ## GitHub Actions
- ### Trigger Sovereignty Check
- ### View Latest Run
- ## Common Tasks
- ### Add Domain to Allowlist
- ### Check if Domain is Allowed
- ### Test Single Endpoint
- ## Troubleshooting
- ### Check System Status
- ### View Error Details
- ### Reset and Regenerate All Configs
- ## Architecture Summary
- ## Success Criteria


### ./docs/sovereignty/FIREWALL_SOVEREIGNTY.md

- # Firewall & Network Sovereignty Architecture
- ## Overview
- ## Philosophy
- ## Architecture Components
- ### 1. Firewall Configuration Manager
- ### 2. Network Resilience Layer
- ### 3. Validation Sovereignty
- ### 4. Script Execution Sovereignty
- ### 5. Sovereign Orchestrator
- ## GitHub Actions Integration
- ## Configuration Files
- ### Network Policies
- ### Diagnostics
- ## Testing
- ## Operational Guide
- ### Running the Sovereign Orchestrator
- ### Viewing Reports
- ### Adding Domains to Allowlist
- ### Checking Network Health
- ### Validating Configurations
- ## Metrics and Monitoring
- ### Firewall Metrics
- ### Network Metrics
- ### Validation Metrics
- ### Script Execution Metrics
- ## Security Considerations
- ## Extending the Architecture
- ### Adding New Sovereignty Systems
- ### Adding New Validation Rules
- ### Adding Network Policies
- ## Troubleshooting
- ### Issue: Firewall validation fails
- ### Issue: Network health check failures
- ### Issue: Script execution fails
- ### Issue: Validation errors
- ## Sovereignty Manifesto
- ## Summary


### ./docs/versions/V197I_IMPLEMENTATION_SUMMARY.md

- # v1.9.7i Implementation Summary
- ## Overview
- ## Components Delivered
- ### 1. Chimera Oracle (`bridge_backend/engines/chimera/`)
- ### 2. Hydra Guard v2 (`bridge_backend/engines/hydra/`)
- ### 3. Leviathan Simulator (`bridge_backend/engines/leviathan/`)
- ### 4. GitHub Forge (`bridge_backend/engines/github_forge/`)
- ### 5. Render Fallback (`bridge_backend/engines/render_fallback/`)
- ### 6. CLI Tool (`bridge_backend/cli/deployctl.py`)
- ### 7. GitHub Actions Integration
- ### 8. Genesis Bus Integration
- ### 9. Tests (`bridge_backend/tests/`)
- ### 10. Documentation (`docs/`)
- ## Deployment Pipeline Flow
- ## Key Features
- ## Environment Variables
- ## Usage Examples
- ### CLI
- ### API
- ### Python
- ## Test Results
- ## Next Steps
- ## Files Modified
- ## Files Created
- ## Status


### ./docs/versions/HXO_V196P_IMPLEMENTATION.md

- # HXO v1.9.6p Implementation Summary
- ## What Was Delivered
- ## Changes Made
- ### Core Files Modified (4)
- ### Documentation Created (6 files, ~45KB)
- ### Tests Created (1 file)
- ### Changelog Updated
- ## New Features Implemented
- ### 1. Federation Nexus (9 Engines)
- ### 2. New Capabilities (8 added)
- ### 3. Genesis Bus Topics (11 added)
- ### 4. Security Enhancements
- ## Testing Results
- ### Test Summary
- ### Test Breakdown
- ## Impact Metrics
- ## Backward Compatibility
- ## Migration Path
- ### From v1.9.6n to v1.9.6p
- ## Production Readiness Checklist
- ## Deployment Instructions
- ### Render
- # Update environment variables in Render dashboard
- # Deploy
- ### Netlify
- ### GitHub Actions
- ## Next Steps
- ### Recommended Post-Deployment
- ### Optional Enhancements
- ## Support Resources
- ### Documentation
- ### Quick References
- ## Acknowledgments
- ## Closing Statement


### ./docs/versions/DEPLOYMENT_READY_v1.9.4.md

- # SR-AIbridge v1.9.4 — Anchorhold Protocol
- ## Deployment Readiness Report
- ## Executive Summary
- ## Implementation Status
- ### ✅ Core Improvements (5/5 Complete)
- ### ✅ Infrastructure Updates (2/2 Complete)
- ### ✅ Dependencies (1/1 Complete)
- ### ✅ Documentation (2/2 Complete)
- ## Verification & Testing
- ### Automated Test Suite
- #### Test Coverage:
- ### Validation Script
- ## Files Changed
- ### Modified Files:
- ### New Files:
- ## Deployment Instructions
- ### Automated Deployment
- ### Manual Verification (Optional)
- # Check Render deployment
- # Expected: {"status": "active", "version": "1.9.4", "protocol": "Anchorhold"}
- # Check version endpoint
- # Expected: {"version": "1.9.4", "protocol": "Anchorhold", ...}
- # Check Netlify frontend
- # Expected: Frontend HTML
- # Check API proxy
- # Expected: Same as Render version endpoint
- ## Breaking Changes
- ### Migration Notes:
- ## Outcome Metrics (Expected)
- ## Rollback Plan
- ## Support & Monitoring
- ### Health Checks
- ### Troubleshooting Resources
- ### Common Issues & Solutions
- ## Contributors
- ## Final Checklist


### ./docs/versions/V197F_QUICK_REF.md

- # v1.9.7f Cascade Synchrony - Quick Reference
- ## 🚀 Quick Start
- # Forge Core
- # Cascade Synchrony Protocol
- ## 📡 API Endpoints
- ### Status & Configuration
- ### Actions
- ## 🧬 Architecture
- ### Healing Flow
- ### Platform Support
- ## 📁 Key Files
- ### Configuration
- ### Core Modules
- ## 🧪 Testing
- ## 🔒 Security
- ## 🌐 Integration Matrix
- ## 📊 Status Check
- ## 🎯 Usage Examples
- ### Trigger Healing
- ### Trigger Recovery
- ### Manual Integration
- ## 📈 Version Info
- ## 🧭 Admiral Directive


### ./docs/versions/V197L_QUICK_REF.md

- # Bridge Health Record System — Quick Reference
- ## 🩺 v1.9.7l Overview
- ## 🚀 Quick Commands
- ### Generate Health Record
- ### Generate Badge
- ### View Latest Health
- ## 📊 Health Score Formula
- ## 🎨 Badge Colors
- ## 📂 File Locations
- ## 🔄 Data Retention
- ## 🧪 Testing
- # Run all health record tests
- # Run all badge tests
- # Run both
- ## 📋 Sample Output
- ### Health Record JSON
- ### Badge Display
- ## 🔧 CI Integration
- ## 🛠️ Troubleshooting
- ### Badge not updating
- # Check latest health record exists
- # Manually regenerate badge
- ### Missing health data
- # Check source reports exist
- # Manually generate health record
- ### Low health score
- ## 🔐 Security Notes
- ## 📈 Future Enhancements


### ./docs/versions/ARIE_V196O_IMPLEMENTATION.md

- # ARIE v1.9.6o Implementation Summary
- ## Overview
- ## ✅ Implementation Complete
- ### Files Added
- ### Files Modified
- ### Directories Created
- ## 🔄 New Behavior
- ### On Deploy Success
- ### Scheduled Runs
- ## ⚙️ Configuration Variables
- ## 🧠 Genesis Event Topics
- ### New Topics
- ### Updated Flow
- ## ✅ Safeguards
- ### RBAC Guard
- ### Truth Enforcement
- ### Rollback Shield
- ### Genesis Integration
- ## 📊 Output Reports
- ### arie_autorun.json
- ### arie_certified.json
- ### arie_rollback.json
- ## 🔬 Testing Results
- ### Test Coverage
- ### Key Test Scenarios
- ## 🚀 Production Readiness Checklist
- ## 📝 Usage Examples
- ### Enable Autonomous Scheduling
- # In .env or platform dashboard
- ### Manual Trigger (Admiral Only)
- # Trigger manual run (requires Admiral handle)
- ### Subscribe to Scheduler Events
- ## 🔗 Related Documentation
- ## 🎯 Next Steps


### ./docs/versions/V196R_QUICK_REF.md

- # v1.9.6r Quick Reference - Chimera Preflight + Autonomous Deploy Healing
- ## Overview
- ## What's New
- ### 1. Chimera Preflight Engine
- ### 2. GitHub Actions Deploy Preview Workflow
- ### 3. Engine Defaults (All ON)
- ## Usage
- ### Manual Preflight
- # Run preflight validation
- # With JSON output
- # Specify path
- ### API Endpoint
- ### Python API
- ## Genesis Events
- ## Auto-Healing
- ## Configuration
- ### Environment Variables
- # Enable/disable Chimera (default: true)
- # Netlify credentials (optional, for direct API integration)
- ### Publish Directory Detection
- ## Testing
- ## Files Added
- ## Modified Files
- ## Integration Points
- ### With ARIE
- ### With Genesis Bus
- ### With Steward  
- ### With EnvRecon
- ## Troubleshooting
- ### Preflight fails with missing publish dir
- ### GitHub Actions workflow doesn't commit
- ### Genesis events show as invalid
- ## Breaking Changes
- ## Next Steps


### ./docs/versions/AUTONOMY_V196S_IMPLEMENTATION.md

- # Autonomy Decision Layer v1.9.6s - Implementation Summary
- ## Overview
- ## What Was Built
- ### 1. Core Components
- #### Governor (`bridge_backend/engines/autonomy/governor.py`)
- #### Models (`bridge_backend/engines/autonomy/models.py`)
- #### REST API (`bridge_backend/engines/autonomy/routes.py`)
- #### Genesis Integration (`autonomy_genesis_link.py`)
- #### CLI Tool (`bridge_backend/cli/autonomyctl.py`)
- ### 2. Configuration & Integration
- #### Genesis Bus Topics
- #### Permissions
- #### Main Application
- #### GitHub Actions
- #### Render Configuration
- ### 3. Testing
- #### Test Coverage
- ### 4. Documentation
- ## Decision Matrix
- ## Safety Mechanisms
- ### Rate Limiting
- ### Cooldown
- ### Circuit Breaker
- ### Truth Certification
- ## Environment Variables
- # Core
- # Safety
- # Integration
- ## Files Created/Modified
- ### Created (17 files)
- ### Modified (5 files)
- ## Integration Points
- ### Genesis Bus
- ### Engines
- ### CI/CD
- ## Usage Examples
- ### Via CLI
- # Submit incident
- # Check status
- ### Via API
- # Submit incident
- ### Via Genesis
- # Event-driven (automatic)
- # → Autonomy link receives event
- # → Governor decides and executes
- # → Truth certifies
- # → Result published to Genesis
- ## Known Limitations
- ## Next Steps
- ## Success Criteria
- ## Version


### ./docs/versions/AUTONOMY_V196T_IMPLEMENTATION.md

- # Autonomy v1.9.6t — The Living Bridge
- ## Overview
- ## Architecture
- ## New Features
- ### 1. Reinforcement Scoring
- ### 2. New Actions
- ### 3. Leviathan Prediction
- ### 4. Truth Engine Certificates
- ### 5. Blueprint Policy Evolution
- ### 6. Engine Success Rate Tracking
- ## GitHub Workflows
- ### bridge_autonomy.yml
- ### env_sync.yml
- ## Environment Variables
- ## Decision Flow
- # 1. Check safety guardrails
- # 2. Map incident to action
- # ... etc
- # 3. Execute action
- # 4. Certify result
- # 5. Predict future success
- # 6. Update policies
- # 7. Update engine success rates
- ## Testing
- ### Test Coverage
- ## Integration Points
- ### Genesis Bus
- ### Engines
- ### GitHub API
- ## Files Changed
- ### Created
- ### Modified
- ## Status
- ## Usage
- ### Triggering Autonomy Manually
- ### Viewing Certificates
- ### Checking Environment Sync
- ## What Happens When...
- ### A deployment fails?
- ### Environment drift is detected?
- ### An action fails repeatedly?
- ## Future Enhancements


### ./docs/versions/V197G_IMPLEMENTATION_SUMMARY.md

- # v1.9.7g — Umbra Lattice Memory Bloom Implementation Summary
- ## Overview
- ## What Was Built
- ### Core Components
- ## Integration Points
- ### Genesis Event Bus
- ### Main Application
- ### Version Updates
- ## File Structure
- ## Storage
- ## Environment Variables
- # Enable/disable Umbra Lattice (default: true)
- # Strict truth certification (default: true)
- # Snapshot interval (optional, default: 10m)
- ## RBAC
- ## Example Usage
- ### CLI
- # View last 7 days as mermaid graph
- # Export snapshot
- # Run bloom analysis
- # Show statistics
- ### API
- # Get summary
- # Get mermaid graph
- # Export snapshot
- # Run bloom analysis
- # Get statistics
- ### Python
- # Initialize
- # Record event
- # Get summary
- # Generate mermaid
- # Export snapshot
- ## Verification
- ## Backward Compatibility
- ## What's Next
- ### Immediate (v1.9.7g)
- ### Future Enhancements
- ## Commit Summary
- ## Admiral Summary


### ./docs/versions/V197C_UNIFIED_GENESIS.md

- # v1.9.7c Genesis Linkage - UNIFIED IMPLEMENTATION
- ## 🎉 Status: ALL ENGINES UNIFIED
- ## Summary
- ### Unified Engine Count: 20
- ## All Engines Unified
- ### Core Infrastructure Engines (6)
- ### Super Engines (6) - Coordinated by Leviathan
- ### Orchestration (1)
- ### Utility Engines (7)
- ## New Implementation Components
- ### New Adapter Files (3)
- ### Updated Files
- ## New API Endpoints
- ## Event Bus Topics (Expanded)
- ### Core Topics
- ### Super Engine Topics
- ### Orchestration Topics
- ### Utility Engine Topics
- ## Engine Dependencies
- ### Dependency Graph
- ## Configuration
- # Enable Genesis Linkage endpoints
- # Enable Blueprint Engine routes (optional)
- # Optional: Configure guardrails
- ## Validation
- ### Engine Count Validation
- # Should show: "count": 20
- ### Super Engines Validation
- # Should show all 6 super engines available
- ### Utility Engines Validation
- # Should show all 7 utility engines available
- ### Leviathan Validation
- # Should show super_engines_coordination with all 6 engines
- ## Benefits
- ## File Changes Summary
- ### New Files (3)
- ### Modified Files (3)
- ### Documentation (1)
- ## Deployment Status


### ./docs/versions/V197F_CASCADE_SYNCHRONY.md

- # v1.9.7f Cascade Synchrony - Environment Variables
- ## Forge System Environment Variables
- ### Core Forge Variables
- #### FORGE_MODE
- #### FORGE_SELF_HEAL
- ### Synchrony Protocol Variables
- #### CASCADE_SYNC
- #### ARIE_PROPAGATION
- #### UMBRA_MEMORY_SYNC
- ### Existing Variables (Enhanced)
- #### TRUTH_CERTIFICATION
- ## Complete v1.9.7f Configuration
- # Forge Core
- # Cascade Synchrony Protocol
- # Truth Certification (already enabled by default)
- # Existing Engine Flags (ensure these are enabled)
- ## Architecture Overview
- ### Healing Flow
- ### Platform Recovery Matrix
- ## API Endpoints
- ## Security Notes
- ## Version Summary
- ## Admiral Directive


### ./docs/versions/V197M_IMPLEMENTATION.md

- # v1.9.7m Implementation Summary
- ## 🚀 Total Autonomy Protocol - Complete Self-Maintenance Architecture
- ## Overview
- ### What's New
- ### The Autonomy Cycle
- ## New Engines
- ### Sanctum Engine
- ### Forge Engine
- # Scan only (no fixes)
- ### Elysium Guardian
- ## Genesis Bus Updates
- ### New Topics (v1.9.7m)
- ## GitHub Actions Workflow
- ### Triggers
- ### Jobs
- ## Documentation
- ## Configuration
- ### Environment Variables
- # Enable engines
- # Elysium settings
- # Genesis integration
- # Truth certification
- ## Post-Merge Activation
- # Quick activation
- # Or manual
- ## Integration Points
- ### With Existing Systems
- ### RBAC
- ## Testing
- ### Individual Engines
- # Sanctum
- # Forge  
- # Elysium
- ### Full Integration
- # Run activation script
- # Or trigger workflow
- ### Validation
- ## File Structure
- ## Success Criteria
- ## Migration Notes
- ### From v1.9.7l or earlier
- ### Activation Steps
- ## Known Limitations
- ## Troubleshooting
- ## Next Steps
- ## Version History
- ## Support


### ./docs/versions/V196R_IMPLEMENTATION_COMPLETE.md

- # v1.9.6r Implementation Complete ✅
- ## Summary
- ## Implementation Checklist
- ## Files Created (15 total)
- ### New Modules
- ### Tests
- ### CI/CD
- ### Documentation
- ## Files Modified (6 total)
- ## Verification Results
- ## How It Works
- ### Normal Flow (Success)
- ### Auto-Healing Flow (Failure)
- ## Default Settings
- ## Usage
- ### CLI
- ### API
- ### Python
- ## Genesis Events Published
- ## Breaking Changes
- ## Environment Variables
- ## Testing
- ## Next Steps
- ## Notes
- ## Success Metrics


### ./docs/versions/V197F_IMPLEMENTATION_SUMMARY.md

- # v1.9.7f Cascade Synchrony - Implementation Summary
- ## 🎯 Mission Accomplished
- ## 📊 Implementation Statistics
- ## 🏗️ Architecture Components
- ### 1. Forge Core (`bridge_backend/forge/forge_core.py`)
- ### 2. Cascade Synchrony (`bridge_backend/forge/synchrony.py`)
- ### 3. API Routes (`bridge_backend/forge/routes.py`)
- ### 4. Configuration Files
- #### `.github/bridge_forge.json`
- #### `.github/forge_topology.json`
- ### 5. Integration Tests (`tests/test_forge_cascade_synchrony.py`)
- ## 🔄 Integration Points
- ### Main Application Integration
- # Forge v1.9.7f - Cascade Synchrony routes
- # In startup_event:
- ## 📚 Documentation
- ### Primary Documentation
- ## 🌊 Healing Flow Architecture
- ## 🔒 Security Implementation
- ## 🧪 Testing & Validation
- ### Test Results
- ### Application Startup Verification
- ## 🎛️ Environment Variables
- ### New Variables (v1.9.7f)
- ### Required for Full Functionality
- ## 📦 Deliverables Checklist
- ## 🚀 Deployment Readiness
- ### Pre-Deployment Checklist
- ### Activation Instructions
- ## 🎉 Success Metrics
- ## 🧬 Evolutionary Leap Summary
- ### Before v1.9.7f
- ### After v1.9.7f
- ## 🏆 Admiral Directive Fulfilled
- ### Status: ✅ READY FOR MERGE


### ./docs/versions/V196E_CONFIG_GUIDE.md

- # v1.9.6e Environment Configuration Guide
- ## Heartbeat Configuration
- ### Basic Configuration
- # Enable/disable heartbeat (default: true)
- # Heartbeat target URL (auto-detects from RENDER_EXTERNAL_URL if not set)
- # Preferred HTTP method (default: auto-detect)
- # Options: GET, POST, HEAD
- # Interval between heartbeats in seconds (default: 30)
- # Timeout for each heartbeat request in seconds (default: 5)
- ### Example Configurations
- #### Render Deployment (Default)
- # No configuration needed! 
- # Heartbeat auto-detects RENDER_EXTERNAL_URL and uses GET method
- #### Custom Heartbeat Target
- #### Disable Heartbeat
- # or
- # or
- #### High-Frequency Monitoring
- ## How It Works
- ### Method Auto-Detection
- ### Backoff Strategy
- ### Example Retry Pattern
- ## Health Endpoint
- # Both work!
- ## Render Deployment
- ### Option 1: Using start.sh (Recommended)
- ### Option 2: Using Python module
- ### Option 3: Direct uvicorn
- ## Troubleshooting
- ### Heartbeat Not Running
- ### 405 Errors Persisting
- ### Predictive Stabilizer


### ./docs/versions/V196I_QUICK_REF.md

- # v1.9.6i Quick Reference — Temporal Deploy Buffer
- ## 🚀 Quick Start
- ## 📍 Key Endpoints
- # Health check (responds in 1-2s)
- # Stage status
- # Runtime info
- # Port info
- ## ⚙️ Environment Variables
- # Enable/disable TDB (default: true)
- # Stage timeout in seconds (default: 120)
- # Render sets this automatically
- ## 🌊 Deployment Stages
- ## 🧪 Testing
- # Run all tests
- # Expected: 23/23 passing
- ## 📊 Monitoring
- # Check stage status
- # Watch for readiness
- ## 🔍 Diagnostics
- ## 🛑 Disable TDB (Legacy Mode)
- # Set in Render environment
- # Or in .env
- ## ✅ Expected Logs
- ## 🚨 Troubleshooting
- ### Render times out
- ### Stage 2/3 fails
- ### Want synchronous startup
- ## 📁 Key Files
- ## 🎯 Success Indicators


### ./docs/versions/V196G_QUICK_REF.md

- # V196G Quick Reference
- ## SR-AIbridge v1.9.6g Predictive Stabilizer — Quick Reference
- ### 🎯 What Changed
- ### 🔍 Key Features at a Glance
- ### 📊 Expected Behavior
- #### During Startup (Good)
- #### During Startup (Learning)
- #### Pattern Detection (Silent)
- ### 🗂️ File Locations
- ### 🧪 Environment Variables
- ### 📈 How Adaptive Thresholds Work
- ### 🔧 Integration Points
- #### In Your Startup Code
- # Mark milestones
- # Finalize boot
- #### Manual Cleanup (Optional)
- # Archive tickets older than 5 days
- ### 🎓 Pro Tips
- ### 🚨 Troubleshooting
- ### 📚 Related Documentation


### ./docs/versions/V197O_IMPLEMENTATION_SUMMARY.md

- # v1.9.7o Implementation Summary
- ## Reflex Loop Protocol - The Self-PR Engine
- ## 🎯 Mission Accomplished
- ## 📦 Deliverables
- ### Core Implementation (6 files)
- ### Genesis Integration (2 files modified)
- ### Documentation (3 comprehensive guides)
- ### Testing & Verification (2 files)
- ### Configuration Updates (2 files)
- ## 📊 Statistics
- ## 🧪 Testing Results
- ### Automated Verification
- ### Manual Testing
- ## 🔑 Key Features
- ### 1. Self-PR Capability
- ### 2. Truth Engine Signing
- ### 3. RBAC Validation
- ### 4. Offline Resilience
- ### 5. Genesis Integration
- ## 🔄 Workflow
- ## 🎓 How to Use
- ### 1. Create a Report
- ### 2. Run Reflex Loop
- # Manual
- # Automatic (every 12 hours via workflow)
- # Or trigger manually in GitHub Actions
- ### 3. Verify PR
- # Check queue
- # View PR data
- ## 🔒 Security Highlights
- ## 🌟 Impact
- ### Before v1.9.7o
- ### After v1.9.7o
- ## 📚 Documentation Structure
- ## 🚀 Next Steps
- ## ✅ Acceptance Criteria Met
- ## 🎖️ Conclusion


### ./docs/versions/V197N_IMPLEMENTATION_SUMMARY.md

- # v1.9.7n Implementation Summary
- ## 🚀 Embedded Autonomy Node - Complete Implementation
- ## Overview
- ## Implementation Details
- ### 📁 Directory Structure Created
- ### 🔄 Workflow Integration
- ### 🌌 Genesis Integration
- ### 📚 Documentation Created
- ### 🧪 Testing & Verification
- ## Feature Highlights
- ### 🧠 Autonomy Core
- ### 🕊️ Truth Micro-Certifier
- ### ⚙️ Cascade Mini-Orchestrator
- ### 🧩 Blueprint Micro-Forge
- ### 📜 Parser Sentinel
- ## Execution Flow
- ## Configuration Options
- ## Security & RBAC
- ### Role-Based Access Control
- ### Safety Mechanisms
- ## Performance Characteristics
- ### Resource Usage
- ### Execution Time
- ### Scalability
- ## Integration Points
- ### 1. Genesis Bus
- ### 2. Total Autonomy Protocol (v1.9.7m)
- ### 3. Cascade Engine
- ## Testing Results
- ### Unit Tests
- ### Verification Script
- ### Manual Testing
- ## Files Changed
- ### New Files (19 total)
- ### Modified Files (3 total)
- ### Total Changes
- ## Post-Merge Behavior
- ## Advantages
- ### ✅ Zero External Dependencies
- ### ✅ Continuous Availability
- ### ✅ Cost Effective
- ### ✅ Secure
- ### ✅ Self-Contained
- ## Future Enhancements
- ## Comparison: Full Bridge vs Mini-Bridge
- ## Verification Commands
- # Run the node manually
- # Run verification script
- # Run unit tests
- # Check configuration
- # Validate workflow
- ## Documentation References
- ## Conclusion


### ./docs/versions/ENGINES_ENABLE_TRUE_v196w.md

- # v1.9.6w — engines_enable_true (Final Full Activation Protocol)
- ## 🧠 Overview
- ## ⚙️ Objective
- ## 🧩 Permanent Engine Activation Architecture
- ## 🧠 Engine Verification & Activation Matrix
- ## 🔒 RBAC Security Enforcement
- ## ⚙️ Default System Config
- # Genesis Framework - v1.9.6w Full Engine Activation
- # RBAC and Safety
- # Individual Engine Flags (now default to true)
- ## 🧩 Core Code Changes
- ### main.py
- # v1.9.6w engines_enable_true flag check
- ### genesisctl.py
- ### activation.py
- ## 🧾 Verification Report
- ## 🔗 Genesis Events
- ## ✅ Testing Results
- ## 🧠 Certification Dependency Chain Diagram
- ## 🚀 CLI Commands
- ### Activate All Engines
- ### Check Engine Status
- ## 🪶 Commit Message
- ## 🚀 Result — The Fully Awakened Bridge
- ## 👑 "Admiral command acknowledged. The Bridge stands fully awakened."


### ./docs/versions/V196T_IMPLEMENTATION_SUMMARY.md

- # v1.9.6t Implementation Summary
- ## 🎉 Implementation Complete
- ## 📋 Requirements Checklist
- ### Core Philosophy ✅
- ### Key Additions ✅
- ### Workflows Added ✅
- ### Unified Environment Configuration ✅
- ### Visual (String-Theory JSON Map) ✅
- ## 🧪 Tests ✅
- ## ✅ Status
- ## 🏁 System Flow
- ## 📊 Implementation Statistics
- ## 📚 Documentation
- ## 🎯 Key Features
- ### Reinforcement Learning
- ### Predictive Intelligence
- ### Cryptographic Proof
- ### Adaptive Policies
- ### GitHub Integration
- ## 🔄 Integrations
- ## 🚀 Deployment Ready
- ## 🙏 Thank You!


### ./docs/versions/V197Q_IMPLEMENTATION.md

- # v1.9.7q — Sanctum Cascade Protocol
- ## What This Release Does (Summary)
- ## Files Added (New)
- ### 1. Netlify Guard (publish path + API guard)
- ### 2. Deferred Integrity (prevents early "validate" flake)
- ### 3. Umbra Auto-Heal linker (bounded retry)
- ## Files Modified
- ### 4. Main boot sequence (ordered guards → reflex → umbra → integrity)
- # === Sanctum Cascade Protocol v1.9.7q ===
- # Ordered boot hardening: guards → reflex → umbra → integrity
- # 1) Netlify publish path & token guard
- # Reflex Auth Forge token fallback for Netlify egress
- # 2) Umbra⇄Genesis link retry
- # 3) Deferred integrity (after engines are steady)
- # === end Sanctum Cascade Protocol ===
- ## Workflow Added
- ### 5. GitHub Workflow – orchestrate order & surface reasons
- ## Environment (new/updated)
- # v1.9.7q — Sanctum Cascade Protocol
- # Optional, Netlify guard will auto-fallback if missing
- # NETLIFY_AUTH_TOKEN=   # preferred; if missing, Reflex/GitHub token will be used
- ## Documentation Added
- ## Verification Plan (copy/paste)
- ### 1. Open/Update any PR – watch these checks:
- ### 2. Backend logs (Render) show:
- ### 3. No more preflight/validate/guard/verify-deploy-paths failures.
- ## Validation Testing
- ## Rollback (safe)
- ## Why This Is Permanent
- ## Impact
- ## Commit Message (ready to paste)


### ./docs/versions/V196Y_QUICK_REF.md

- # v1.9.6y Quick Reference
- ## What Was Fixed
- ### 1. HXO Nexus Startup Crash ✅
- ### 2. Netlify Preview Checks ✅
- ## Quick Commands
- ### Check System Health
- ### Generate Netlify Artifacts (if needed manually)
- ### Test HXO Nexus
- ### Run Tests
- ## Files Modified
- ## Files Created
- ## Key Changes
- ## What to Expect After Merge
- ### Render Logs (HXO Nexus)
- ### Netlify Preview
- ### Diagnostics Output
- ## Troubleshooting
- ### If HXO Nexus still fails
- # Check import
- # Check initialization
- ### If Netlify artifacts missing
- # Regenerate
- # Verify
- ### If diagctl fails
- # Run with errors visible
- ## Architecture Notes
- ## See Also


### ./docs/versions/DEPLOYMENT_SUMMARY_V197Q.md

- # v1.9.7q Deployment Summary — Sanctum Cascade Protocol
- ## Executive Summary
- ## What Was Built
- ### New Modules (8 files)
- ### Modified Files (1 file)
- ### Documentation (5 files)
- ### Testing (1 file)
- ### Configuration (1 file)
- ## Files Changed Summary
- ## API Endpoints Added
- ### Health Check Endpoints
- ## Environment Variables
- ### New Variables
- # Deferred integrity check delay (seconds)
- # Netlify publish path (optional, auto-detected)
- # Netlify auth token (optional, GitHub token used as fallback)
- ## Boot Sequence Changes
- ### Before v1.9.7q
- ### After v1.9.7q (Sanctum Cascade Protocol)
- ## Validation Results
- ## Expected Console Output
- ## Breaking Changes
- ## Migration Guide
- ### For Existing Deployments
- ### For New Deployments
- ## Testing Checklist
- ## Rollback Plan
- ### Option 1: Remove Protocol Initialization
- # === Sanctum Cascade Protocol v1.9.7q ===
- # ... (all protocol code)
- # === end Sanctum Cascade Protocol ===
- ### Option 2: Disable Guards via Environment
- ### Option 3: Full Rollback
- ## Performance Impact
- ## Security Considerations
- ## Monitoring and Alerts
- ### Recommended Monitoring
- ### Sample Prometheus Query
- # Guard health status
- # Umbra retry count
- ## Known Limitations
- ## Future Enhancements
- ## Support and Documentation
- ## Commit History
- ## Approval and Sign-off


### ./docs/versions/V197E_IMPLEMENTATION.md

- # v1.9.7e — Umbra + Netlify Integration Healing
- ## 🌌 Overview
- ## 🚀 What's New
- ### 1. Netlify Validator Engine
- ### 2. Validation Script
- ### 3. Umbra Memory Enhancements
- ### 4. API Endpoints
- ### 5. CI/CD Workflow
- ## 🧩 Architecture
- ## ⚙️ Configuration
- ### Environment Variables
- # ===== Umbra Cognitive Stack v1.9.7e =====
- # ===== Umbra + Netlify Integration v1.9.7e =====
- # Optional: Netlify API credentials (for remote checks)
- # Enable optional preview checks (graceful degradation if tokens missing)
- ## 🔐 RBAC Enforcement
- ## ✅ Testing
- ### Running Tests
- # Run Netlify validator tests
- # Run all Umbra tests (including new features)
- # Run validation script manually
- ### Test Results
- ## 🎯 Impact
- ### Benefits
- ### Cognitive Learning
- ## 📊 Metrics & Monitoring
- ### Validator Metrics
- # Get validator metrics
- ### Umbra Memory Metrics
- # Get Umbra metrics including Netlify events
- ## 🔄 Migration from v1.9.7d
- ## 🧬 Commit Summary
- ## 🧠 Admiral Summary
- ## 📚 Related Documentation


### ./docs/versions/V197L_IMPLEMENTATION_SUMMARY.md

- # v1.9.7l — Bridge Health Record System Implementation Summary
- ## 🎉 Implementation Complete
- ## 📦 Deliverables
- ### New Components
- #### 1. `bridge_backend/metrics/health_record.py`
- #### 2. `bridge_backend/cli/badgegen.py`
- #### 3. `docs/badges/` Directory
- ## ⚙️ CI Integration
- ### Updated `.github/workflows/bridge_selftest.yml`
- #### Step 1: Generate & Publish Health Record
- #### Step 2: Commit Updated Badge
- ## 📈 README Integration
- ## 🧪 Test Coverage
- ### Test Files Created
- #### 1. `bridge_backend/tests/test_health_record.py` (17 tests)
- #### 2. `bridge_backend/tests/test_badgegen.py` (16 tests)
- ## 📊 Health Score Calculation
- # Selftest pass rate (50%)
- # Umbra issues (30%)
- # Heal success rate (20%)
- ## 🧩 Sample Badge Output
- ### JSON Report
- ### Badge Display
- ## 🔒 Security & Governance
- ## 🔄 Data Retention
- ### Health History Management
- ### .gitignore Rules
- # v1.9.7l Bridge Health History (auto-generated, keep latest only)
- ## 🧠 Benefits
- ## 🚀 Usage Examples
- ### Manual Health Record Generation
- # Generate health record
- # Generate badge
- ### Viewing Health History
- # List all health records
- # View latest record
- # View latest markdown report
- ## ✅ Implementation Checklist
- ## 📝 Next Steps
- ## 🎯 Success Metrics


### ./docs/versions/DEPLOYMENT_READY_v196g.md

- # SR-AIbridge v1.9.6g — DEPLOYMENT SUMMARY
- ## 🎯 Mission Accomplished
- ### Tagline
- ## 📊 What Was Delivered
- ### 6 Major Features (All Complete ✅)
- ## 📁 Files Changed
- ### Modified Files (4)
- ### New Files (3)
- ## 🧪 Test Coverage
- ### Test Results Summary
- ### Test Categories
- ## 🔧 Technical Highlights
- ### New Functions (10)
- ### Configuration Constants
- ## 🎯 Expected Runtime Behavior
- ### Before v1.9.6g (Noisy)
- ### After v1.9.6g (Silent)
- ## 📂 Directory Structure
- ## 🚀 Deployment Instructions
- ### 1. Merge the PR
- # Review PR on GitHub
- # Approve and merge to main
- ### 2. Deploy to Render
- # Render will auto-deploy on merge
- # Or manually trigger deploy from Render dashboard
- ### 3. Observe Adaptive Learning
- ### 4. Monitor Results
- # Check daily reports
- # Check boot history
- # Verify no false tickets
- ## 🧠 How It Works
- ### Startup Sequence (Adaptive)
- ### Learning Cycle
- ## 💡 Key Insights
- ### What Makes This Different
- ## 📚 Documentation
- ## ✅ Quality Checklist
- ## 🎓 Lessons Embodied
- ## 🌟 Final Notes
- ## 🚀 Ready for Deployment


### ./docs/versions/V197J_IMPLEMENTATION_SUMMARY.md

- # v1.9.7j Implementation Summary
- ## Bridge Autonomy Diagnostic Pulse + Auto-Heal Trigger
- ## 🎯 Overview
- ## 📦 Deliverables
- ### Core Components
- ### Infrastructure
- ### Documentation
- ### Testing
- ## 🔧 Technical Implementation
- ### Self-Test Controller
- ### Auto-Heal Trigger
- ### Genesis Integration
- ### CLI Integration
- ## 🧪 Testing & Verification
- ### Test Coverage
- ### Verification Results
- ### Integration Testing
- ## 📊 Performance Metrics
- ## 🔒 Security & Governance
- ### RBAC Integration
- ### Truth Engine Certification
- ### Audit Trail
- ## 🚀 Continuous Operation
- ### Automatic Schedule
- ### Failure Recovery
- ## 📈 Report Schema
- ### Summary Structure
- ### Event Types
- ### Status Values
- ## 🎓 Usage Examples
- ### Basic Self-Test
- ### Disable Auto-Healing
- ### View Latest Report
- ### Check Specific Engine
- ### Count Failed Engines
- ## 🔍 Environment Configuration
- ### Self-Test Configuration
- ### Genesis Configuration
- ## 📚 Documentation Index
- ## ✅ Summary
- ## 🚀 Next Steps


### ./docs/versions/DEPLOYMENT_READY_v196f.md

- # ✅ SR-AIbridge v1.9.6f — DEPLOYMENT READY
- ## 🎯 What This Release Does
- ## 🚀 Quick Deploy
- ### On Render (Auto-deploy enabled)
- ### Expected Result
- ## 📊 What Changed
- ### Modified Files (4)
- ### New Files (4)
- ## 🧪 Validation Status
- ### Test Results
- ### Deployment Verification
- ## 📚 Key Features
- ### 1. Adaptive Port Binding
- # Prebind monitor with 100ms polling
- ### 2. Deferred Heartbeat
- # Startup sequence (main.py)
- ### 3. Predictive Watchdog
- ### 4. Self-Healing Diagnostics
- ## 🔍 Monitoring
- ### Log Messages to Watch
- #### Good ✅
- #### Warnings ⚠️
- #### Errors ❌ (Should NOT appear)
- ## 🧩 Migration Notes
- ### From v1.9.6b → v1.9.6f
- ### What Users Will Notice
- ## 🎖️ Success Criteria
- ## 📖 Documentation
- ## 🚦 Rollback Plan
- ## 🌟 Next Steps
- ## 💬 Support


### ./docs/versions/V196F_QUICK_REF.md

- # v1.9.6f Quick Reference
- ## 🎯 What This Release Fixes
- ## 🔧 Key Features
- ### 1️⃣ Adaptive Port Binding
- ### 2️⃣ Deferred Heartbeat
- ### 3️⃣ Predictive Watchdog
- ## 📊 Startup Sequence
- ## 🧪 Quick Test
- # Test adaptive port resolution
- # Expected output:
- # [PORT] Resolved immediately: 10000
- # [BOOT] Adaptive port bind: ok on 0.0.0.0:10000
- # [STABILIZER] Startup latency X.XXs (tolerance: 6.0s)
- # [HEARTBEAT] ✅ Initialized
- ## 📁 Files Changed
- ## ✅ Success Criteria
- ## 🚀 Deploy Command
- # Render auto-deploys via render.yaml
- # Start command: bash scripts/start.sh
- # Which runs: uvicorn bridge_backend.main:app --host 0.0.0.0 --port $PORT
- ## 📈 Monitoring
- ## 🔗 Related Docs


### ./docs/versions/V196Y_IMPLEMENTATION.md

- # v1.9.6y Implementation Complete ✅
- ## Overview
- ## Changes Made
- ### 1. HXO Nexus Initialization Fix ✅
- ### 2. Netlify Preview Hardening ✅
- ### 3. Deep Diagnostics CLI ✅
- ## Usage
- ### Run Diagnostics
- ### Generate Netlify Artifacts
- ### Build for Netlify
- ## Verification
- # 34 passed in 0.52s
- # ✅ HXO Nexus v1.9.6p 'Ascendant' is fully operational!
- ## What's Fixed
- ### HXO Nexus
- ### Netlify Previews
- ### Diagnostics
- ## Genesis Topics
- ## Next Steps
- ## Notes


### ./docs/versions/V197J_QUICK_REF.md

- # v1.9.7j Quick Reference — Bridge Autonomy Diagnostic Pulse
- ## 🚀 Quick Start
- ### Run Self-Test Manually
- # With auto-healing (default)
- # Without auto-healing
- ### View Latest Report
- ### Check Specific Engine
- ## 📊 Environment Variables
- ## 🧩 Architecture
- ### Components
- ### Healing Strategies
- ## 📋 Genesis Event Topics
- ## 📊 Expected Metrics
- ## 🔍 Common Tasks
- ### Check Test Status
- ### Count Failed Engines
- ### List Healing Events
- ### Get Healing Statistics
- ## 🔒 Security & Governance
- ## 🧪 Testing
- ### Run Self-Test Tests
- ### Validate Workflow
- ## 📚 Documentation
- ## 🛠️ Troubleshooting
- ### Self-Test Disabled
- ### Auto-Heal Not Working
- ### Increase Retry Attempts
- ## 🔄 GitHub Actions Integration
- ## 📈 Report Schema
- ## ⚡ Performance Tips
- ## 🎯 Key Features


### ./docs/badges/README.md

- # Bridge Health Badges
- ## Files


### ./docs/badges/bridge_health.md

- # 🔵 Bridge Health Badge
- ## Integration


### ./.pytest_cache/README.md

- # pytest cache directory #


### ./bridge_backend/dock_day_exports/test_export/README.md

- # SR-AIbridge Dock-Day Drop: test_export
- ## Overview
- ## Contents
- ## Manifest Information
- ## Verification
- ## Usage
- ## Admiral's Note


### ./bridge_backend/dock_day_exports/final_demo/README.md

- # SR-AIbridge Dock-Day Drop: final_demo
- ## Overview
- ## Contents
- ## Manifest Information
- ## Verification
- ## Usage
- ## Admiral's Note


### ./bridge_backend/examples/README.md

- # SR-AIbridge Backend Examples
- ## Available Examples
- ### relay_mailer_example.py
- ## Configuration
- ## Adding New Examples
- ## Related Documentation


### ./bridge_backend/bridge_core/engines/recovery/lore.md

- # Recovery Orchestrator — Doctrine (v1)
- ## Purpose:
- ## Rituals:
- ## Laws:
- ## Implementation Notes:


### ./bridge_backend/bridge_core/engines/leviathan/SOLVER_README.md

- # Leviathan Solver - Meta-Engine Orchestrator
- ## Overview
- ## Features
- ### 🎯 Intent Classification
- ### 🔌 Six Super Engines Integration
- ### 📚 Knowledge Grounding
- ### 🤖 Optional Autonomy
- ### 🔒 Proof Artifacts
- ## API Endpoint
- ### POST `/engines/leviathan/solve`
- ## Usage Examples
- ### Basic Query
- ### With Project Context
- ### With Specific Modes
- ### With Autonomy Dispatch
- ## Testing
- ### Run Minimal Tests
- ### Run Smoke Tests
- ### Run Full Test Suite (requires dependencies)
- ## Architecture
- ### Flow Diagram
- ### Adapter Pattern
- ## Files
- ## Future Enhancements
- ## License


### ./bridge_backend/bridge_core/payments/README.md

- # Stripe Webhook Integration
- ## Overview
- ## Architecture
- ## Setup
- ### 1. Environment Variables
- ### 2. Webhook Endpoint
- ### 3. Configure Stripe
- ## Supported Events
- ### customer.subscription.created
- ### customer.subscription.deleted
- ### customer.subscription.updated
- ## Metadata Requirements
- ## Security
- ### Signature Verification
- ### Source Provenance
- ## Audit Trail
- ### patches.jsonl
- ### cascade_state.json
- ## Example Usage
- ### Creating a Stripe Subscription with Metadata
- ### Testing Locally
- ### Verifying Cascade Updates
- ## Error Handling
- ## Future Enhancements
- ## Testing


### ./bridge_backend/bridge_engines/README.md

- # Sovereign Engines
- ## Overview
- ### Components
- ## Features
- ### 🔐 Sovereign Compliance Guard
- ### 📝 Sovereign MicroScribe Engine
- ### 🔍 Sovereign MicroLogician Engine
- ## Installation
- ### Dependencies
- ## Quick Start
- ### Using the Engines Programmatically
- # Compliance Guard
- # MicroScribe - Diff Analysis
- # PR Generation
- # MicroLogician - Log Analysis
- ### Using the API
- # Check engine status
- # Analyze a diff
- # Analyze logs
- # Check compliance
- ## API Endpoints
- ### Health & Status
- ### Compliance Guard
- ### MicroScribe
- ### MicroLogician
- ## Configuration
- ### Environment Variables
- # Enable/disable Sovereign Engines
- # License key (for production)
- # Bridge resonance level (0.0-1.0)
- # Minimum resonance threshold
- ### Sovereign Policy
- ## Analysis Modes
- ## Security Levels
- ### MicroScribe Security Levels
- ### MicroLogician Threat Levels
- ## Testing
- ### Run Unit Tests
- # All tests
- # Specific engine
- ### Run Verification Script
- ### Run API Smoke Tests
- # Start server first
- # In another terminal
- ## Examples
- ### Analyzing Git Diffs
- # Get diff from git
- # Analyze
- # Generate PR
- ### Analyzing Application Logs
- # Read logs
- # Analyze
- # Report findings
- ## License
- ## Support
- ## Changelog
- ### Version 1.0.0 (2025-11-05)


### ./bridge_backend/bridge_engines/SOVEREIGN_LICENSE.md

- # SOVEREIGN LICENSE
- ## Bridge-Integrated Perpetual License
- ## Grant of License
- ### Components Covered
- ## Terms and Conditions
- ### 1. Bridge Resonance Requirements
- ### 2. Permitted Uses
- ### 3. Security Requirements
- ### 4. Compliance
- ### 5. Enterprise Deployment
- ## License Key Configuration
- ## Warranty Disclaimer
- ## Limitation of Liability
- ## Attribution
- ## Support and Updates
- ## License Enforcement
- ## Termination
- ## Governing Law
- ## Contact


### ./.archive/render_legacy/README.md

- # Render Legacy Files Archive
- ## What was Render?
- ## Files Archived
- ## Migration Path


### ./DOCTRINE/teaching-doctrine-the-test-of-chains.md

- # Teaching Doctrine: The Test of Chains
- ## Lesson for All Captains
- ## Core Principles
- ## Patterns to Recognize
- ## Captain’s Checklist
- ## Parable for the Ledger
- ## Vault Seal


### ./DOCTRINE/indoctrination/lore.md

- # Indoctrination Doctrine v1


### ./codex/README.md

- # 📘 Repo Codex Engine
- ## 🧩 Overview
- ## 🔹 Core Components
- ### Three Coordinated Engines
- ### Two Compilers
- ## 🚀 Quick Start
- ### Manual Compilation
- # Generate JSON output
- # Generate Markdown output
- ### Automatic Compilation (GitHub Actions)
- ## 📖 Output Structure
- ### repo_book.json
- ### repo_book.md
- ## 🧪 Testing
- ## 🛠️ Configuration
- ### codex/manifest.yaml
- ## 📊 Statistics (Current Repository)
- ## 🔄 Workflow Integration
- ## 🎯 Use Cases
- ## 🔐 Security
- ## 📝 Development
- ## 🎉 Features


### ./codex/output/repo_book.md

- # 📘 The Book of the Repo
- ## 🧠 Truth Engine Summary
- ## 📄 Documentation Index
- ### ./CHANGELOG.md
- ### ./START_HERE.md
- ### ./README.md
- ### ./SECURITY.md
- ### ./scripts/README.md
- ### ./docs/ETHICS_IMPACT_TEMPLATE.md
- ### ./docs/HXO_ENGINE_MATRIX.md
- ### ./docs/GITHUB_FORGE.md
- ### ./docs/DOMINION_DEPLOY_GUIDE.md
- ### ./docs/DOMINION_SECURITY_SPEC.md
- ### ./docs/CHIMERA_CERTIFICATION_FLOW.md
- ### ./docs/TOTAL_AUTONOMY_PROTOCOL.md
- ### ./docs/PIPELINE_AUTOMATION_OVERVIEW.md
- ### ./docs/TRIAGE_OPERATIONS.md
- ### ./docs/API_TRIAGE.md
- ### ./docs/TRIAGE_MESH_MIGRATION.md
- ### ./docs/ARIE_V196O_QUICK_REF.md
- ### ./docs/FORGE_DOMINION_DEPLOYMENT_GUIDE.md
- ### ./docs/GITHUB_ENVHOOK.md
- ### ./docs/AUTONOMY_INTEGRATION.md
- ### ./docs/ENVSYNC_ENGINE.md
- ### ./docs/BUILD_DOSSIER.md
- ### ./docs/UMBRA_LATTICE_QUICK_START.md
- ### ./docs/DEPLOYMENT_AUTOMATION.md
- ### ./docs/ELYSIUM_GUARDIAN.md
- ### ./docs/BRH_GUIDE.md
- ### ./docs/GITHUB_ENVHOOK_INTEGRATION.md
- ### ./docs/ANCHORHOLD_PROTOCOL.md
- ### ./docs/AUTONOMY_DEPLOYMENT_INTEGRATION.md
- ### ./docs/RUNTIME_TROUBLESHOOTING.md
- ### ./docs/TROUBLESHOOTING_LINKS.md
- ### ./docs/BLUEPRINT_ENGINE_GUIDE.md
- ### ./docs/PHOENIX_COMPARISON.md
- ### ./docs/GITHUB_ENVHOOK_QUICK_REF.md
- ### ./docs/HYDRA_GUARD_V2.md
- ### ./docs/V197M_QUICK_REF.md
- ### ./docs/BRH_CONSENSUS_ARCHITECTURE.md
- ### ./docs/HOOKS_TRIAGE.md
- ### ./docs/TOTAL_STACK_TRIAGE.md
- ### ./docs/GENESIS_V2_0_1_QUICK_REF.md
- ### ./docs/COMPLIANCE_INTEGRATION_GUIDE.md
- ### ./docs/PR_HEALTH_SUMMARY.md
- ### ./docs/ENV_OVERVIEW.md
- ### ./docs/ARIE_SANCTUM_LOOP.md
- ### ./docs/BADGES.md
- ### ./docs/GENESIS_V2_GUIDE.md
- ### ./docs/DEPLOYMENT_SECURITY_FIX.md
- ### ./docs/GITHUB_ENV_SYNC_GUIDE.md
- ### ./docs/BRIDGE_NOTIFICATIONS_ROLLBACK.md
- ### ./docs/PREDICTIVE_DEPLOY_PIPELINE.md
- ### ./docs/AUTONOMY_DEPLOYMENT_README.md
- ### ./docs/FORGE_MANIFEST_RESOLVER_GUIDE.md
- ### ./docs/GENESIS_ARCHITECTURE.md
- ### ./docs/UMBRA_OVERVIEW.md
- ### ./docs/FIREWALL_HARMONY.md
- ### ./docs/PHOENIX_PROTOCOL.md
- ### ./docs/AUTONOMY_V196T_QUICK_REF.md
- ### ./docs/STEWARD_DEPLOYMENT_GUIDE.md
- ### ./docs/NOTIFICATION_EXAMPLES.md
- ### ./docs/INCIDENT_CATALOG.md
- ### ./docs/HEALER_NET.md
- ### ./docs/SCRIBE_README.md
- ### ./docs/CHIMERA_API_REFERENCE.md
- ### ./docs/HXO_BLUEPRINT_CONTRACT.md
- ### ./docs/ENDPOINT_TRIAGE.md
- ### ./docs/UPGRADE_GUIDE.md
- ### ./docs/UPGRADE_v1.9.6q.md
- ### ./docs/GENESIS_REGISTRATION_OVERVIEW.md
- ### ./docs/POSTGRES_RENDER_SETUP.md
- ### ./docs/COMPONENT_INDEX.md
- ### ./docs/ENDPOINT_TRIAGE_QUICK_REF.md
- ### ./docs/INTEGRITY_DEFERRED_GUIDE.md
- ### ./docs/ENVIRONMENT_SETUP.md
- ### ./docs/IMPLEMENTATION_SUMMARY.md
- ### ./docs/UMBRA_README.md
- ### ./docs/BRH_CONSENSUS_GUIDE.md
- ### ./docs/DOCUMENTATION_USAGE_GUIDE.md
- ### ./docs/EMBEDDED_AUTONOMY_NODE.md
- ### ./docs/CHIMERA_README.md
- ### ./docs/PARITY_ENGINE_QUICK_GUIDE.md
- ### ./docs/ROLES_INTERFACE_AUDIT.md
- ### ./docs/README_SECURITY.md
- ### ./docs/HXO_OPERATIONS.md
- ### ./docs/BADGE_DEPLOY_STATUS.md
- ### ./docs/DEPLOYMENT.md
- ### ./docs/engine_smoke_test.md
- ### ./docs/REPO_STUDY_README.md
- ### ./docs/GIT_SOVEREIGN_AGENT_GUIDE.md
- ### ./docs/CHIMERA_FAILSAFE_PROTOCOL.md
- ### ./docs/ENVSYNC_SEED_MANIFEST.md
- ### ./docs/BRIDGE_AUTOFIX_ENGINE.md
- ### ./docs/BRIDGE_DEPLOY_GUIDE.md
- ### ./docs/FRONTEND_POSTGRES_READINESS.md
- ### ./docs/ARIE_README.md
- ### ./docs/AUTONOMY_QUICK_REF.md
- ### ./docs/HERITAGE_TEST_PRESETS.md
- ### ./docs/TRIAGE_BOOTSTRAP_BANNER_USAGE.md
- ### ./docs/UMBRA_LATTICE_OVERVIEW.md
- ### ./docs/CHIMERA_QUICK_START.md
- ### ./docs/ENV_SYNC_AUTONOMOUS_PIPELINE.md
- ### ./docs/HXO_OVERVIEW.md
- ### ./docs/CAPTAIN_AGENT_SEPARATION.md
- ### ./docs/HERITAGE_BRIDGE.md
- ### ./docs/API_TRIAGE_QUICK_REF.md
- ### ./docs/BRIDGE_PARITY_ENGINE.md
- ### ./docs/AUTONOMY_INTEGRATION_DIAGRAM.md
- ### ./docs/UMBRA_OPERATIONS.md
- ### ./docs/ARIE_TOPICS.md
- ### ./docs/SELFTEST_HEALING_AUTOTRIGGER.md
- ### ./docs/BUILD_SECURITY_FIX.md
- ### ./docs/ETHICS_GUIDE.md
- ### ./docs/LOC_COUNTER_README.md
- ### ./docs/endpoint_test_examples.md
- ### ./docs/GITHUB_MINI_BRIDGE_OVERVIEW.md
- ### ./docs/TRIAGE_SYSTEMS.md
- ### ./docs/AUTONOMY_DECISION_LAYER.md
- ### ./docs/SANCTUM_CASCADE_PROTOCOL.md
- ### ./docs/TELEMETRY.md
- ### ./docs/MASTER_ROADMAP.md
- ### ./docs/DOCUMENTATION_INDEX.md
- ### ./docs/ENVSYNC_PIPELINE_QUICK_REF.md
- ### ./docs/AUTONOMY_DEPLOYMENT_QUICK_REF.md
- ### ./docs/FRONTEND-INTEGRATION.md
- ### ./docs/ENVIRONMENT_REDUCTION_SUMMARY.md
- ### ./docs/ENDPOINT_TRIAGE_IMPLEMENTATION.md
- ### ./docs/HXO_SECURITY.md
- ### ./docs/API_TRIAGE_IMPLEMENTATION.md
- ### ./docs/SCAN_ENGINE_README.md
- ### ./docs/NETLIFY_RENDER_ENV_SETUP.md
- ### ./docs/HXO_GENESIS_TOPICS.md
- ### ./docs/GENESIS_LINKAGE_GUIDE.md
- ### ./docs/AUTONOMY_OPERATIONS.md
- ### ./docs/FIREWALL_HARDENING.md
- ### ./docs/GENESIS_V2_0_2_ENVRECON_GUIDE.md
- ### ./docs/endpoint_test_full.md
- ### ./docs/AUTONOMY_DEPLOYMENT_ARCHITECTURE.md
- ### ./docs/REFLEX_LOOP_PROTOCOL.md
- ### ./docs/BUILD_TRIAGE_ENGINE.md
- ### ./docs/FIREWALL_WATCHDOG.md
- ### ./docs/OFFLINE_QUEUE_HANDLING.md
- ### ./docs/SELFTEST_REPORT_SCHEMA.md
- ### ./docs/COPILOT_NETWORK_HEALTH.md
- ### ./docs/UMBRA_LATTICE_SCHEMA.md
- ### ./docs/DIAGNOSTICS_FEDERATION.md
- ### ./docs/ARIE_SECURITY.md
- ### ./docs/CHIMERA_ARCHITECTURE.md
- ### ./docs/ARIE_OPERATIONS.md
- ### ./docs/CHIMERA_ORACLE.md
- ### ./docs/UNIFIED_HEALTH_TIMELINE.md
- ### ./docs/ARIE_OVERVIEW.md
- ### ./docs/REPO_STUDY_GUIDE.md
- ### ./docs/NAVIGATION_INDEX.md
- ### ./docs/POSTGRES_MIGRATION.md
- ### ./docs/NETLIFY_GUARD_OVERVIEW.md
- ### ./docs/ANCHORHOLD_QUICK_REF.md
- ### ./docs/HXO_DEPLOY_GUIDE.md
- ### ./docs/SANCTUM_OVERVIEW.md
- ### ./docs/AUTONOMY_PR_VERIFICATION.md
- ### ./docs/DEPLOY_DIAGNOSE_GUIDE.md
- ### ./docs/AUTONOMY_ORIGINALITY_INTEGRATION.md
- ### ./docs/ENVSCRIBE_QUICK_REF.md
- ### ./docs/SELFTEST_OVERVIEW.md
- ### ./docs/doctrine-vault.md
- ### ./docs/TRIAGE_PRESEED.md
- ### ./docs/RENDER_FALLBACK.md
- ### ./docs/BRH_DEPLOYMENT_GUIDE.md
- ### ./docs/FEDERATION_TRIAGE_ENGINE.md
- ### ./docs/NODE_FAILSAFE_GUIDE.md
- ### ./docs/AUTONOMY_INTEGRATION_QUICK_REF.md
- ### ./docs/ENGINE_CATALOG.md
- ### ./docs/TDE_X_DEPLOYMENT_GUIDE.md
- ### ./docs/ARIE_QUICK_REF.md
- ### ./docs/V196L_IMPLEMENTATION_SUMMARY.md
- ### ./docs/AUTONOMY_INTEGRATION_ARCHITECTURE.md
- ### ./docs/HXO_GENESIS_INTEGRATION.md
- ### ./docs/endpoint_test_quick_ref.md
- ### ./docs/GENESIS_V2_0_1_GUIDE.md
- ### ./docs/BRIDGE_HEALERS_CODE.md
- ### ./docs/COMMAND_DECK_GUIDE.md
- ### ./docs/README_RELEASES.md
- ### ./docs/GENESIS_EVENT_FLOW.md
- ### ./docs/TRIAGE_FEDERATION.md
- ### ./docs/FORGE_AUTOREPAIR_GUIDE.md
- ### ./docs/HXO_README.md
- ### ./docs/LOG_SIGNATURES.md
- ### ./docs/SYSTEM_BLUEPRINT.md
- ### ./docs/HXO_TROUBLESHOOTING.md
- ### ./docs/quickrefs/TDE_X_QUICK_REF.md
- ### ./docs/quickrefs/NETLIFY_UMBRA_QUICK_REF.md
- ### ./docs/quickrefs/QUICK_START_30MIN.md
- ### ./docs/quickrefs/HXO_NEXUS_QUICK_REF.md
- ### ./docs/quickrefs/DATA_RELAY_QUICK_REF.md
- ### ./docs/quickrefs/ROLE_SEPARATION_QUICK_REF.md
- ### ./docs/quickrefs/UMBRA_QUICK_REF.md
- ### ./docs/quickrefs/ENVRECON_QUICK_REF.md
- ### ./docs/quickrefs/BRH_QUICK_REF.md
- ### ./docs/quickrefs/UMBRA_QUICK_START.md
- ### ./docs/quickrefs/ENVSYNC_QUICK_REF.md
- ### ./docs/quickrefs/WORKFLOW_FAILURE_QUICK_REF.md
- ### ./docs/quickrefs/FORGE_DOMINION_QUICK_REF.md
- ### ./docs/quickrefs/GIT_SOVEREIGN_AGENT_QUICK_REF.md
- ### ./docs/quickrefs/COMPLIANCE_QUICK_REF.md
- ### ./docs/quickrefs/FIREWALL_AUTONOMY_QUICK_REF.md
- ### ./docs/quickrefs/HXO_QUICK_REF.md
- ### ./docs/quickrefs/ENGINES_ENABLE_TRUE_QUICK_REF.md
- ### ./docs/quickrefs/GENESIS_V2_QUICK_REF.md
- ### ./docs/quickrefs/STEWARD_QUICK_REF.md
- ### ./docs/quickrefs/BLUEPRINT_QUICK_REF.md
- ### ./docs/quickrefs/BRH_CONSENSUS_QUICK_REF.md
- ### ./docs/quickrefs/GENESIS_LINKAGE_QUICK_REF.md
- ### ./docs/archive/PHASE_6_VERIFICATION.md
- ### ./docs/archive/LOC_REPORT.md
- ### ./docs/archive/CHIMERA_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/INTEGRATION_COMPLETE.md
- ### ./docs/archive/FORGE_DOMINION_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/DOCKDAY_SUMMARY.md
- ### ./docs/archive/PR_SUMMARY.md
- ### ./docs/archive/HXO_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/V196I_SUMMARY.md
- ### ./docs/archive/TASK_COMPLETE_SUMMARY.md
- ### ./docs/archive/DEPLOYMENT_CHECKLIST_v196b.md
- ### ./docs/archive/EAN_EXECUTION_RESULTS.md
- ### ./docs/archive/BRIDGE_REPAIR_SUMMARY.md
- ### ./docs/archive/OPERATION_GENESIS_SUMMARY.md
- ### ./docs/archive/V196L_STEWARD_SUMMARY.md
- ### ./docs/archive/IMPLEMENTATION_BRIDGE_DEPLOY.md
- ### ./docs/archive/POST_MERGE_SETUP.md
- ### ./docs/archive/V196I_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/V197C_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/V196B_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/NETLIFY_DEPLOYMENT_FIX_SUMMARY.md
- ### ./docs/archive/BRH_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/STEWARD_JSON_REPORT_QUICK_START.md
- ### ./docs/archive/CHECKLIST_COMPLETION_SUMMARY.md
- ### ./docs/archive/ENVIRONMENT_CLEANUP_SUMMARY.md
- ### ./docs/archive/V195_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/GENESIS_V2_0_2_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/QUICK_VERIFICATION_SUMMARY.md
- ### ./docs/archive/ENVRECON_AUTONOMY_SUMMARY.md
- ### ./docs/archive/V196_FINAL_IMPLEMENTATION.md
- ### ./docs/archive/V196D_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/DOCUMENTATION_IMPROVEMENT_SUMMARY.md
- ### ./docs/archive/PR_READY.md
- ### ./docs/archive/IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/GIT_SOVEREIGN_COMMISSIONING.md
- ### ./docs/archive/FIREWALL_LIST.md
- ### ./docs/archive/WHAT_I_COULDNT_CHANGE.md
- ### ./docs/archive/PHASE_4_5_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/PHASE_6_IMPLEMENTATION.md
- ### ./docs/archive/V2_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/DEPLOYMENT_CHECKLIST_v196i.md
- ### ./docs/archive/SCAN_SUMMARY.md
- ### ./docs/archive/V196E_IMPLEMENTATION.md
- ### ./docs/archive/FEATURE_INVENTORY.md
- ### ./docs/archive/GITHUB_ENVHOOK_IMPLEMENTATION.md
- ### ./docs/archive/ANCHORHOLD_PR_SUMMARY.md
- ### ./docs/archive/COPILOT_IMPROVEMENTS.md
- ### ./docs/archive/README.md
- ### ./docs/archive/HXO_DEPLOYMENT_CHECKLIST.md
- ### ./docs/archive/STEWARD_ENVRECON_INTEGRATION.md
- ### ./docs/archive/GIT_SOVEREIGN_VISUALIZATION.md
- ### ./docs/archive/V196F_IMPLEMENTATION.md
- ### ./docs/archive/BRIDGE_FEDERATION_SECRETS.md
- ### ./docs/archive/FIREWALL_AUTONOMY_IMPLEMENTATION.md
- ### ./docs/archive/DOMINION_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/GIT_SOVEREIGN_VALIDATION.md
- ### ./docs/archive/GENESIS_V2_0_1A_IMPLEMENTATION.md
- ### ./docs/archive/ENDPOINT_TEST_SOLUTION.md
- ### ./docs/archive/WORKFLOW_FIXES_SUMMARY.md
- ### ./docs/archive/PHASE_6_SUMMARY.md
- ### ./docs/archive/UMBRA_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/PARITY_STUBS_VERIFICATION.md
- ### ./docs/archive/STUB_CLEANUP_COMPLETE.md
- ### ./docs/archive/DEPLOYMENT_VERIFICATION.md
- ### ./docs/archive/PROJECT_LOC_SUMMARY.md
- ### ./docs/archive/REPO_STUDY_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/CHROME_PLAYWRIGHT_INSTALLATION_SUMMARY.md
- ### ./docs/archive/HXO_NEXUS_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/LOC_QUICK_ANSWER.md
- ### ./docs/archive/PARITY_EXECUTION_REPORT.md
- ### ./docs/archive/GIT_SOVEREIGN_FAMILIARIZATION_SUMMARY.md
- ### ./docs/archive/ENVSCRIBE_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/WORKFLOW_FAILURE_RESOLUTION.md
- ### ./docs/archive/ENVRECON_USER_CHECKLIST.md
- ### ./docs/archive/V196C_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/ENVRECON_AUTONOMY_INTEGRATION.md
- ### ./docs/archive/PR_SUMMARY_V197M.md
- ### ./docs/archive/PARITY_ENGINE_RUN_SUMMARY.md
- ### ./docs/archive/V196G_IMPLEMENTATION.md
- ### ./docs/archive/TOTAL_STACK_TRIAGE_VERIFICATION.md
- ### ./docs/archive/BRIDGE_DIAGNOSTIC_REPORT.md
- ### ./docs/archive/AUTONOMY_BACKEND_INTEGRATION_SUMMARY.md
- ### ./docs/archive/COMPREHENSIVE_SCAN_REPORT.md
- ### ./docs/archive/HXO_NEXUS_CONNECTIVITY.md
- ### ./docs/archive/FORGE_DOMINION_ENVIRONMENT_INTEGRATION.md
- ### ./docs/archive/AUTONOMY_DEPLOYMENT_COMPLETE.md
- ### ./docs/archive/GENESIS_V2_0_1_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/BRIDGE_WALKTHROUGH_COMPLETE.md
- ### ./docs/archive/AUTONOMY_INTEGRATION_COMPLETE.md
- ### ./docs/archive/ENVRECON_UNFIXABLE_VARS.md
- ### ./docs/archive/BRH_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/FINAL_VERIFICATION_REPORT.md
- ### ./docs/archive/COMPLIANCE_IMPLEMENTATION_SUMMARY.md
- ### ./docs/archive/RENDER_REMOVAL_COMPLETE.md
- ### ./docs/archive/ENGINE_INTEGRATION_SUMMARY.md
- ### ./docs/archive/V196B_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/UNIFICATION_COMPLETE.md
- ### ./docs/archive/FULL_SCAN_REPORT_2025.md
- ### ./docs/archive/PHOENIX_SUMMARY.md
- ### ./docs/archive/V196H_IMPLEMENTATION_COMPLETE.md
- ### ./docs/archive/STEWARD_JSON_FEATURE_COMPLETE.md
- ### ./docs/archive/DOCUMENTATION_ENHANCEMENT_PLAN.md
- ### ./docs/archive/SCAN_REPORT_RENDER_REMOVAL.md
- ### ./docs/archive/V198_ENVSYNC_IMPLEMENTATION.md
- ### ./docs/archive/TDE_X_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/V197I_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/HXO_V196P_IMPLEMENTATION.md
- ### ./docs/versions/DEPLOYMENT_READY_v1.9.4.md
- ### ./docs/versions/V197F_QUICK_REF.md
- ### ./docs/versions/V197L_QUICK_REF.md
- ### ./docs/versions/ARIE_V196O_IMPLEMENTATION.md
- ### ./docs/versions/V196R_QUICK_REF.md
- ### ./docs/versions/AUTONOMY_V196S_IMPLEMENTATION.md
- ### ./docs/versions/AUTONOMY_V196T_IMPLEMENTATION.md
- ### ./docs/versions/V197G_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/V197C_UNIFIED_GENESIS.md
- ### ./docs/versions/V197F_CASCADE_SYNCHRONY.md
- ### ./docs/versions/V197M_IMPLEMENTATION.md
- ### ./docs/versions/V196R_IMPLEMENTATION_COMPLETE.md
- ### ./docs/versions/V197F_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/V196E_CONFIG_GUIDE.md
- ### ./docs/versions/V196I_QUICK_REF.md
- ### ./docs/versions/V196G_QUICK_REF.md
- ### ./docs/versions/V197O_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/V197N_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/ENGINES_ENABLE_TRUE_v196w.md
- ### ./docs/versions/V196T_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/V197Q_IMPLEMENTATION.md
- ### ./docs/versions/V196Y_QUICK_REF.md
- ### ./docs/versions/DEPLOYMENT_SUMMARY_V197Q.md
- ### ./docs/versions/V197E_IMPLEMENTATION.md
- ### ./docs/versions/V197L_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/DEPLOYMENT_READY_v196g.md
- ### ./docs/versions/V197J_IMPLEMENTATION_SUMMARY.md
- ### ./docs/versions/DEPLOYMENT_READY_v196f.md
- ### ./docs/versions/V196F_QUICK_REF.md
- ### ./docs/versions/V196Y_IMPLEMENTATION.md
- ### ./docs/versions/V197J_QUICK_REF.md
- ### ./docs/badges/README.md
- ### ./docs/badges/bridge_health.md
- ### ./.pytest_cache/README.md
- ### ./bridge_backend/dock_day_exports/test_export/README.md
- ### ./bridge_backend/dock_day_exports/final_demo/README.md
- ### ./bridge_backend/examples/README.md
- ### ./bridge_backend/bridge_core/engines/recovery/lore.md
- ### ./bridge_backend/bridge_core/engines/leviathan/SOLVER_README.md
- ### ./bridge_backend/bridge_core/payments/README.md
- ### ./DOCTRINE/teaching-doctrine-the-test-of-chains.md
- ### ./DOCTRINE/indoctrination/lore.md
- ### ./codex/README.md
- ### ./codex/output/repo_book.md
- ### ./bridge-frontend/README.md
- ### ./bridge-frontend/src/api/auto_generated/README.md
- ### ./brh/README.md
- ### ./brh/examples/README.md
- ### ./phoenix/README.md
- ### ./phoenix/backend/README.md
- ## 🧬 Blueprint Overview
- ### ./get_env_drift.py
- ### ./verify_hxo_nexus.py
- ### ./validate_genesis_unified.py
- ### ./count_loc.py
- ### ./smoke_test_engines.py
- ### ./activate_autonomy.py
- ### ./study_repo_with_engines.py
- ### ./test_endpoints_full.py
- ### ./__init__.py
- ### ./bridge_core/update_forge_banner_from_events.js
- ### ./bridge_core/__init__.py
- ### ./bridge_core/lattice/heartbeat.py
- ### ./bridge_core/lattice/pathcheck.py
- ### ./bridge_core/lattice/__init__.py
- ### ./bridge_core/security/validate_token.py
- ### ./bridge_core/security/__init__.py
- ### ./bridge_core/self_heal/guard.py
- ### ./bridge_core/self_heal/__init__.py
- ### ./scripts/validate_netlify.py
- ### ./scripts/integrity_audit.py
- ### ./scripts/view_envsync_manifest.py
- ### ./scripts/repair_netlify_env.py
- ### ./scripts/verify_reflex_loop.py
- ### ./scripts/verify_autonomy_node.py
- ### ./scripts/fix_deprecated_datetime.py
- ### ./scripts/repo_cleanup.py
- ### ./scripts/scan_manual_env_vars.py
- ### ./scripts/synthesize_netlify_artifacts.py
- ### ./scripts/validate_scanner_output.py
- ### ./scripts/firewall_watchdog.py
- ### ./scripts/verify_umbra_lattice.py
- ### ./scripts/prune_diagnostics.py
- ### ./scripts/stub_scanner.py
- ### ./scripts/report_bridge_event.py
- ### ./scripts/validate_netlify_env.py
- ### ./scripts/validate_env_setup.py
- ### ./scripts/validate_envsync_manifest.py
- ### ./scripts/validate_copilot_env.py
- ### ./scripts/verify_netlify_build.py
- ### ./scripts/check_env_parity.py
- ### ./scripts/run_full_scan.py
- ### ./scripts/seed_bootstrap.py
- ### ./scripts/comprehensive_repo_scan.py
- ### ./scripts/clean_stub_todos.py
- ### ./scripts/netlify_rollback.py
- ### ./tools/route_sweep_check.py
- ### ./tools/__init__.py
- ### ./netlify/functions/bridge-deploy.js
- ### ./netlify/functions/forge-resolver.js
- ### ./bridge_backend/main.py
- ### ./bridge_backend/seed.py
- ### ./bridge_backend/schemas.py
- ### ./bridge_backend/__main__.py
- ### ./bridge_backend/db.py
- ### ./bridge_backend/config.py
- ### ./bridge_backend/__init__.py
- ### ./bridge_backend/run.py
- ### ./bridge_backend/models.py
- ### ./bridge_backend/db/bootstrap.py
- ### ./bridge_backend/db/__init__.py
- ### ./bridge_backend/metrics/health_record.py
- ### ./bridge_backend/metrics/__init__.py
- ### ./bridge_backend/examples/relay_mailer_example.py
- ### ./bridge_backend/models/core.py
- ### ./bridge_backend/models/__init__.py
- ### ./bridge_backend/bridge_core/routes_custody.py
- ### ./bridge_backend/bridge_core/prooffoundry.py
- ### ./bridge_backend/bridge_core/chroniclevault.py
- ### ./bridge_backend/bridge_core/entanglecore.py
- ### ./bridge_backend/bridge_core/runtime_handler.py
- ### ./bridge_backend/bridge_core/paths.py
- ### ./bridge_backend/bridge_core/federation_client.py
- ### ./bridge_backend/bridge_core/claude_watcher.py
- ### ./bridge_backend/bridge_core/labyrinthforge.py
- ### ./bridge_backend/bridge_core/fault_injector.py
- ### ./bridge_backend/bridge_core/routes_brain.py
- ### ./bridge_backend/bridge_core/self_healing_adapter.py
- ### ./bridge_backend/bridge_core/__init__.py
- ### ./bridge_backend/bridge_core/registry_payloads.py
- ### ./bridge_backend/bridge_core/db/db_manager.py
- ### ./bridge_backend/bridge_core/db/schemas.py
- ### ./bridge_backend/bridge_core/db/models.py
- ### ./bridge_backend/bridge_core/guardians/gate.py
- ### ./bridge_backend/bridge_core/guardians/__init__.py
- ### ./bridge_backend/bridge_core/guardians/routes.py
- ### ./bridge_backend/bridge_core/health/__init__.py
- ### ./bridge_backend/bridge_core/health/routes.py
- ### ./bridge_backend/bridge_core/doctrine/routes.py
- ### ./bridge_backend/bridge_core/utils/async_tools.py
- ### ./bridge_backend/bridge_core/utils/__init__.py
- ### ./bridge_backend/bridge_core/middleware/permissions.py
- ### ./bridge_backend/bridge_core/middleware/__init__.py
- ### ./bridge_backend/bridge_core/engines/routes_linked.py
- ### ./bridge_backend/bridge_core/engines/filing.py
- ### ./bridge_backend/bridge_core/engines/commerceforge.py
- ### ./bridge_backend/bridge_core/engines/scrolltongue.py
- ### ./bridge_backend/bridge_core/engines/auroraforge.py
- ### ./bridge_backend/bridge_core/engines/push_notifications.py
- ### ./bridge_backend/bridge_core/engines/qhelmsingularity.py
- ### ./bridge_backend/bridge_core/engines/chronicleloom.py
- ### ./bridge_backend/bridge_core/engines/routes_filing.py
- ### ./bridge_backend/bridge_core/engines/__init__.py
- ### ./bridge_backend/bridge_core/engines/calculuscore.py
- ### ./bridge_backend/bridge_core/engines/recovery/orchestrator.py
- ### ./bridge_backend/bridge_core/engines/recovery/__init__.py
- ### ./bridge_backend/bridge_core/engines/recovery/routes.py
- ### ./bridge_backend/bridge_core/engines/speech/tts.py
- ### ./bridge_backend/bridge_core/engines/speech/stt.py
- ### ./bridge_backend/bridge_core/engines/speech/__init__.py
- ### ./bridge_backend/bridge_core/engines/speech/routes.py
- ### ./bridge_backend/bridge_core/engines/chimera/healer.py
- ### ./bridge_backend/bridge_core/engines/chimera/simulator.py
- ### ./bridge_backend/bridge_core/engines/chimera/certifier.py
- ### ./bridge_backend/bridge_core/engines/chimera/config.py
- ### ./bridge_backend/bridge_core/engines/chimera/engine.py
- ### ./bridge_backend/bridge_core/engines/chimera/__init__.py
- ### ./bridge_backend/bridge_core/engines/chimera/routes.py
- ### ./bridge_backend/bridge_core/engines/leviathan/solver.py
- ### ./bridge_backend/bridge_core/engines/leviathan/service.py
- ### ./bridge_backend/bridge_core/engines/leviathan/__init__.py
- ### ./bridge_backend/bridge_core/engines/leviathan/routes_solver.py
- ### ./bridge_backend/bridge_core/engines/leviathan/routes.py
- ### ./bridge_backend/bridge_core/engines/blueprint/planner_rules.py
- ### ./bridge_backend/bridge_core/engines/blueprint/blueprint_engine.py
- ### ./bridge_backend/bridge_core/engines/blueprint/registry.py
- ### ./bridge_backend/bridge_core/engines/blueprint/__init__.py
- ### ./bridge_backend/bridge_core/engines/blueprint/routes.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/leviathan_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/tde_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/cascade_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/super_engines_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/utility_engines_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/truth_link.py
- ### ./bridge_backend/bridge_core/engines/blueprint/adapters/__init__.py
- ### ./bridge_backend/bridge_core/engines/creativity/service.py
- ### ./bridge_backend/bridge_core/engines/creativity/__init__.py
- ### ./bridge_backend/bridge_core/engines/creativity/routes.py
- ### ./bridge_backend/bridge_core/engines/hxo/nexus.py
- ### ./bridge_backend/bridge_core/engines/hxo/startup.py
- ### ./bridge_backend/bridge_core/engines/hxo/security.py
- ### ./bridge_backend/bridge_core/engines/hxo/__init__.py
- ### ./bridge_backend/bridge_core/engines/hxo/hypshard.py
- ### ./bridge_backend/bridge_core/engines/hxo/routes.py
- ### ./bridge_backend/bridge_core/engines/screen/service.py
- ### ./bridge_backend/bridge_core/engines/screen/__init__.py
- ### ./bridge_backend/bridge_core/engines/screen/routes.py
- ### ./bridge_backend/bridge_core/engines/cascade/service.py
- ### ./bridge_backend/bridge_core/engines/cascade/__init__.py
- ### ./bridge_backend/bridge_core/engines/cascade/routes.py
- ### ./bridge_backend/bridge_core/engines/truth/finder.py
- ### ./bridge_backend/bridge_core/engines/truth/utils.py
- ### ./bridge_backend/bridge_core/engines/truth/binder.py
- ### ./bridge_backend/bridge_core/engines/truth/__init__.py
- ### ./bridge_backend/bridge_core/engines/truth/citer.py
- ### ./bridge_backend/bridge_core/engines/truth/routes.py
- ### ./bridge_backend/bridge_core/engines/parser/service.py
- ### ./bridge_backend/bridge_core/engines/parser/__init__.py
- ### ./bridge_backend/bridge_core/engines/parser/routes.py
- ### ./bridge_backend/bridge_core/engines/agents_foundry/service.py
- ### ./bridge_backend/bridge_core/engines/agents_foundry/__init__.py
- ### ./bridge_backend/bridge_core/engines/agents_foundry/routes.py
- ### ./bridge_backend/bridge_core/engines/umbra/autoheal_link.py
- ### ./bridge_backend/bridge_core/engines/umbra/storage.py
- ### ./bridge_backend/bridge_core/engines/umbra/lattice.py
- ### ./bridge_backend/bridge_core/engines/umbra/memory.py
- ### ./bridge_backend/bridge_core/engines/umbra/echo.py
- ### ./bridge_backend/bridge_core/engines/umbra/predictive.py
- ### ./bridge_backend/bridge_core/engines/umbra/core.py
- ### ./bridge_backend/bridge_core/engines/umbra/__init__.py
- ### ./bridge_backend/bridge_core/engines/umbra/models.py
- ### ./bridge_backend/bridge_core/engines/umbra/routes.py
- ### ./bridge_backend/bridge_core/engines/autonomy/service.py
- ### ./bridge_backend/bridge_core/engines/autonomy/__init__.py
- ### ./bridge_backend/bridge_core/engines/autonomy/routes.py
- ### ./bridge_backend/bridge_core/engines/envsync/types.py
- ### ./bridge_backend/bridge_core/engines/envsync/tasks.py
- ### ./bridge_backend/bridge_core/engines/envsync/telemetry.py
- ### ./bridge_backend/bridge_core/engines/envsync/diffs.py
- ### ./bridge_backend/bridge_core/engines/envsync/config.py
- ### ./bridge_backend/bridge_core/engines/envsync/engine.py
- ### ./bridge_backend/bridge_core/engines/envsync/__init__.py
- ### ./bridge_backend/bridge_core/engines/envsync/routes.py
- ### ./bridge_backend/bridge_core/engines/envsync/discovery/sources.py
- ### ./bridge_backend/bridge_core/engines/envsync/discovery/chain.py
- ### ./bridge_backend/bridge_core/engines/envsync/discovery/__init__.py
- ### ./bridge_backend/bridge_core/engines/envsync/providers/render.py
- ### ./bridge_backend/bridge_core/engines/envsync/providers/__init__.py
- ### ./bridge_backend/bridge_core/engines/envsync/providers/netlify.py
- ### ./bridge_backend/bridge_core/engines/envsync/providers/base.py
- ### ./bridge_backend/bridge_core/engines/adapters/autonomy_genesis_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/umbra_truth_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_parser_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/arie_schedule_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_blueprint_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/envrecon_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_nexus_integration.py
- ### ./bridge_backend/bridge_core/engines/adapters/umbra_parity_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/arie_blueprint_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/tools_runtime_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/heritage_mas_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/arie_cascade_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_federation_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/umbra_cascade_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/genesis_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/super_engines_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_genesis_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/arie_truth_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/umbra_genesis_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_permission_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/arie_genesis_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/umbra_blueprint_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/hxo_truth_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/umbra_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/__init__.py
- ### ./bridge_backend/bridge_core/engines/adapters/arie_permission_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/envsync_autonomy_link.py
- ### ./bridge_backend/bridge_core/engines/adapters/chimera_genesis_link.py
- ### ./bridge_backend/bridge_core/engines/indoctrination/service.py
- ### ./bridge_backend/bridge_core/engines/indoctrination/__init__.py
- ### ./bridge_backend/bridge_core/engines/indoctrination/routes.py
- ### ./bridge_backend/bridge_core/custody/__init__.py
- ### ./bridge_backend/bridge_core/custody/routes.py
- ### ./bridge_backend/bridge_core/payments/stripe_webhooks.py
- ### ./bridge_backend/bridge_core/payments/__init__.py
- ### ./bridge_backend/bridge_core/fleet/__init__.py
- ### ./bridge_backend/bridge_core/fleet/routes.py
- ### ./bridge_backend/bridge_core/protocols/storage.py
- ### ./bridge_backend/bridge_core/protocols/vaulting.py
- ### ./bridge_backend/bridge_core/protocols/complex_routes.py
- ### ./bridge_backend/bridge_core/protocols/invoke.py
- ### ./bridge_backend/bridge_core/protocols/registry.py
- ### ./bridge_backend/bridge_core/protocols/__init__.py
- ### ./bridge_backend/bridge_core/protocols/models.py
- ### ./bridge_backend/bridge_core/protocols/routes.py
- ### ./bridge_backend/bridge_core/registry/agents_registry.py
- ### ./bridge_backend/bridge_core/registry/__init__.py
- ### ./bridge_backend/bridge_core/registry/routes.py
- ### ./bridge_backend/bridge_core/guards/netlify_guard.py
- ### ./bridge_backend/bridge_core/guards/__init__.py
- ### ./bridge_backend/bridge_core/guards/routes.py
- ### ./bridge_backend/bridge_core/integrity/core.py
- ### ./bridge_backend/bridge_core/integrity/__init__.py
- ### ./bridge_backend/bridge_core/integrity/deferred.py
- ### ./bridge_backend/bridge_core/scans/service.py
- ### ./bridge_backend/bridge_core/scans/__init__.py
- ### ./bridge_backend/bridge_core/scans/models.py
- ### ./bridge_backend/bridge_core/scans/routes.py
- ### ./bridge_backend/bridge_core/core/event_bus.py
- ### ./bridge_backend/bridge_core/core/event_models.py
- ### ./bridge_backend/bridge_core/core/__init__.py
- ### ./bridge_backend/bridge_core/agents/__init__.py
- ### ./bridge_backend/bridge_core/agents/routes.py
- ### ./bridge_backend/bridge_core/agents/git_sovereign/manifest.py
- ### ./bridge_backend/bridge_core/agents/git_sovereign/brh_integration.py
- ### ./bridge_backend/bridge_core/agents/git_sovereign/autonomy.py
- ### ./bridge_backend/bridge_core/agents/git_sovereign/hxo_integration.py
- ### ./bridge_backend/bridge_core/agents/git_sovereign/sdtf_integration.py
- ### ./bridge_backend/bridge_core/agents/git_sovereign/__init__.py
- ### ./bridge_backend/bridge_core/heritage/event_bus.py
- ### ./bridge_backend/bridge_core/heritage/__init__.py
- ### ./bridge_backend/bridge_core/heritage/routes.py
- ### ./bridge_backend/bridge_core/heritage/federation/live_ws.py
- ### ./bridge_backend/bridge_core/heritage/federation/federation_client.py
- ### ./bridge_backend/bridge_core/heritage/federation/__init__.py
- ### ./bridge_backend/bridge_core/heritage/mas/adapters.py
- ### ./bridge_backend/bridge_core/heritage/mas/fault_injector.py
- ### ./bridge_backend/bridge_core/heritage/mas/__init__.py
- ### ./bridge_backend/bridge_core/heritage/agents/profiles.py
- ### ./bridge_backend/bridge_core/heritage/agents/legacy_agents.py
- ### ./bridge_backend/bridge_core/heritage/agents/__init__.py
- ### ./bridge_backend/bridge_core/heritage/demos/mas_demo.py
- ### ./bridge_backend/bridge_core/heritage/demos/__init__.py
- ### ./bridge_backend/bridge_core/heritage/demos/federation_demo.py
- ### ./bridge_backend/bridge_core/heritage/demos/shakedown.py
- ### ./bridge_backend/bridge_core/missions/__init__.py
- ### ./bridge_backend/bridge_core/missions/routes.py
- ### ./bridge_backend/bridge_core/permissions/store.py
- ### ./bridge_backend/bridge_core/permissions/presets.py
- ### ./bridge_backend/bridge_core/permissions/service.py
- ### ./bridge_backend/bridge_core/permissions/__init__.py
- ### ./bridge_backend/bridge_core/permissions/models.py
- ### ./bridge_backend/bridge_core/permissions/routes.py
- ### ./bridge_backend/bridge_core/console/routes.py
- ### ./bridge_backend/bridge_core/activity/__init__.py
- ### ./bridge_backend/bridge_core/activity/routes.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/bootstrap.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/sovereign_integration.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/quantum_scanner.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/scan_envs.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/validate_or_renew.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/quantum_authority.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/zero_trust_validator.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/enterprise_orchestrator.py
- ### ./bridge_backend/bridge_core/token_forge_dominion/__init__.py
- ### ./bridge_backend/bridge_core/vault/__init__.py
- ### ./bridge_backend/bridge_core/vault/routes.py
- ### ./bridge_backend/bridge_core/system/__init__.py
- ### ./bridge_backend/bridge_core/system/routes.py
- ### ./bridge_backend/bridge_core/captains/routes.py
- ### ./bridge_backend/utils/signing.py
- ### ./bridge_backend/utils/deployment_publisher.py
- ### ./bridge_backend/utils/scan_policy.py
- ### ./bridge_backend/utils/counterfeit_detector.py
- ### ./bridge_backend/utils/license_scanner.py
- ### ./bridge_backend/utils/relay_mailer.py
- ### ./bridge_backend/utils/db.py
- ### ./bridge_backend/utils/__init__.py
- ### ./bridge_backend/middleware/headers.py
- ### ./bridge_backend/middleware/__init__.py
- ### ./bridge_backend/engines/netlify_validator.py
- ### ./bridge_backend/engines/netlify_routes.py
- ### ./bridge_backend/engines/envrecon/hubsync.py
- ### ./bridge_backend/engines/envrecon/core.py
- ### ./bridge_backend/engines/envrecon/ui.py
- ### ./bridge_backend/engines/envrecon/autoheal.py
- ### ./bridge_backend/engines/envrecon/__init__.py
- ### ./bridge_backend/engines/envrecon/routes.py
- ### ./bridge_backend/engines/chimera/planner.py
- ### ./bridge_backend/engines/chimera/core.py
- ### ./bridge_backend/engines/chimera/__init__.py
- ### ./bridge_backend/engines/chimera/models.py
- ### ./bridge_backend/engines/chimera/routes.py
- ### ./bridge_backend/engines/chimera/preflight/netlify_config.py
- ### ./bridge_backend/engines/chimera/preflight/__init__.py
- ### ./bridge_backend/engines/chimera/adapters/leviathan_adapter.py
- ### ./bridge_backend/engines/chimera/adapters/github_forge_adapter.py
- ### ./bridge_backend/engines/chimera/adapters/netlify_guard_adapter.py
- ### ./bridge_backend/engines/chimera/adapters/env_adapter.py
- ### ./bridge_backend/engines/chimera/adapters/render_fallback_adapter.py
- ### ./bridge_backend/engines/chimera/adapters/arie_adapter.py
- ### ./bridge_backend/engines/chimera/adapters/truth_adapter.py
- ### ./bridge_backend/engines/leviathan/simulator.py
- ### ./bridge_backend/engines/leviathan/__init__.py
- ### ./bridge_backend/engines/forge/core.py
- ### ./bridge_backend/engines/forge/__init__.py
- ### ./bridge_backend/engines/arie/scheduler.py
- ### ./bridge_backend/engines/arie/core.py
- ### ./bridge_backend/engines/arie/__init__.py
- ### ./bridge_backend/engines/arie/models.py
- ### ./bridge_backend/engines/arie/routes.py
- ### ./bridge_backend/engines/hydra/guard.py
- ### ./bridge_backend/engines/hydra/__init__.py
- ### ./bridge_backend/engines/hydra/routes.py
- ### ./bridge_backend/engines/sanctum/core.py
- ### ./bridge_backend/engines/sanctum/__init__.py
- ### ./bridge_backend/engines/github_forge/core.py
- ### ./bridge_backend/engines/github_forge/__init__.py
- ### ./bridge_backend/engines/render_fallback/core.py
- ### ./bridge_backend/engines/render_fallback/__init__.py
- ### ./bridge_backend/engines/hypshard_x/rehydrator.py
- ### ./bridge_backend/engines/hypshard_x/schedulers.py
- ### ./bridge_backend/engines/hypshard_x/checkpointer.py
- ### ./bridge_backend/engines/hypshard_x/executors.py
- ### ./bridge_backend/engines/hypshard_x/core.py
- ### ./bridge_backend/engines/hypshard_x/merkle.py
- ### ./bridge_backend/engines/hypshard_x/__init__.py
- ### ./bridge_backend/engines/hypshard_x/models.py
- ### ./bridge_backend/engines/hypshard_x/partitioners.py
- ### ./bridge_backend/engines/hypshard_x/routes.py
- ### ./bridge_backend/engines/selftest/autoheal_trigger.py
- ### ./bridge_backend/engines/selftest/core.py
- ### ./bridge_backend/engines/selftest/__init__.py
- ### ./bridge_backend/engines/elysium/core.py
- ### ./bridge_backend/engines/elysium/__init__.py
- ### ./bridge_backend/engines/umbra/healers.py
- ### ./bridge_backend/engines/umbra/core.py
- ### ./bridge_backend/engines/umbra/__init__.py
- ### ./bridge_backend/engines/umbra/models.py
- ### ./bridge_backend/engines/umbra/routes.py
- ### ./bridge_backend/engines/envscribe/emitters.py
- ### ./bridge_backend/engines/envscribe/core.py
- ### ./bridge_backend/engines/envscribe/__init__.py
- ### ./bridge_backend/engines/envscribe/models.py
- ### ./bridge_backend/engines/envscribe/routes.py
- ### ./bridge_backend/engines/steward/core.py
- ### ./bridge_backend/engines/steward/__init__.py
- ### ./bridge_backend/engines/steward/models.py
- ### ./bridge_backend/engines/steward/routes.py
- ### ./bridge_backend/engines/steward/adapters/github_adapter.py
- ### ./bridge_backend/engines/steward/adapters/netlify_adapter.py
- ### ./bridge_backend/engines/steward/adapters/render_adapter.py
- ### ./bridge_backend/engines/steward/adapters/__init__.py
- ### ./bridge_backend/engines/autonomy/__init__.py
- ### ./bridge_backend/engines/autonomy/models.py
- ### ./bridge_backend/engines/autonomy/governor.py
- ### ./bridge_backend/engines/autonomy/routes.py
- ### ./bridge_backend/forge/export_runtime.py
- ### ./bridge_backend/forge/__init__.py
- ### ./bridge_backend/forge/synchrony.py
- ### ./bridge_backend/forge/forge_core.py
- ### ./bridge_backend/forge/routes.py
- ### ./bridge_backend/scripts/endpoint_triage.py
- ### ./bridge_backend/scripts/deploy_diagnose.py
- ### ./bridge_backend/scripts/triage_preseed.py
- ### ./bridge_backend/scripts/env_sync_monitor.py
- ### ./bridge_backend/scripts/generate_sync_badge.py
- ### ./bridge_backend/scripts/utils.py
- ### ./bridge_backend/scripts/synchrony_collector.py
- ### ./bridge_backend/scripts/run_scan.py
- ### ./bridge_backend/scripts/report_bridge_event.py
- ### ./bridge_backend/scripts/deepscan_reporter.py
- ### ./bridge_backend/scripts/api_triage.py
- ### ./bridge_backend/scripts/hooks_triage.py
- ### ./bridge_backend/scripts/ci_cd_triage.py
- ### ./bridge_backend/scripts/__init__.py
- ### ./bridge_backend/scripts/deploy_confidence.py
- ### ./bridge_backend/genesis/manifest.py
- ### ./bridge_backend/genesis/orchestration.py
- ### ./bridge_backend/genesis/registration.py
- ### ./bridge_backend/genesis/activation.py
- ### ./bridge_backend/genesis/introspection.py
- ### ./bridge_backend/genesis/bus.py
- ### ./bridge_backend/genesis/adapters.py
- ### ./bridge_backend/genesis/replay.py
- ### ./bridge_backend/genesis/contracts.py
- ### ./bridge_backend/genesis/persistence.py
- ### ./bridge_backend/genesis/__init__.py
- ### ./bridge_backend/genesis/routes.py
- ### ./bridge_backend/cli/selftest_summary.py
- ### ./bridge_backend/cli/diagctl.py
- ### ./bridge_backend/cli/doctor.py
- ### ./bridge_backend/cli/chimeractl.py
- ### ./bridge_backend/cli/autonomyctl.py
- ### ./bridge_backend/cli/genesisctl.py
- ### ./bridge_backend/cli/ariectl.py
- ### ./bridge_backend/cli/umbractl.py
- ### ./bridge_backend/cli/umbra.py
- ### ./bridge_backend/cli/brh_cli.py
- ### ./bridge_backend/cli/envscribectl.py
- ### ./bridge_backend/cli/__init__.py
- ### ./bridge_backend/cli/badgegen.py
- ### ./bridge_backend/cli/deployctl.py
- ### ./bridge_backend/tools/parity_engine.py
- ### ./bridge_backend/tools/parity_autofix.py
- ### ./bridge_backend/tools/health/healer_net_probe.py
- ### ./bridge_backend/tools/firewall_intel/fetch_firewall_incidents.py
- ### ./bridge_backend/tools/firewall_intel/chromium_probe.py
- ### ./bridge_backend/tools/firewall_intel/__init__.py
- ### ./bridge_backend/tools/firewall_intel/firewall_autonomy_engine.py
- ### ./bridge_backend/tools/firewall_intel/analyze_firewall_findings.py
- ### ./bridge_backend/tools/network_diagnostics/__init__.py
- ### ./bridge_backend/tools/network_diagnostics/check_copilot_access.py
- ### ./bridge_backend/tools/triage/endpoint_triage.py
- ### ./bridge_backend/tools/triage/diagnostics_federate.py
- ### ./bridge_backend/tools/triage/api_triage.py
- ### ./bridge_backend/tools/triage/deploy_path_triage.py
- ### ./bridge_backend/tools/triage/common/utils.py
- ### ./bridge_backend/tools/triage/common/__init__.py
- ### ./bridge_backend/tools/autonomy/failure_analyzer.py
- ### ./bridge_backend/tools/autonomy/failure_patterns.py
- ### ./bridge_backend/tools/autonomy/pr_generator.py
- ### ./bridge_backend/tools/autonomy/test_autonomy_tools.py
- ### ./bridge_backend/tools/autonomy/__init__.py
- ### ./bridge_backend/runtime/retry.py
- ### ./bridge_backend/runtime/health_probe.py
- ### ./bridge_backend/runtime/startup_watchdog.py
- ### ./bridge_backend/runtime/temporal_deploy.py
- ### ./bridge_backend/runtime/heartbeat.py
- ### ./bridge_backend/runtime/deploy_parity.py
- ### ./bridge_backend/runtime/release_intel.py
- ### ./bridge_backend/runtime/verify_imports.py
- ### ./bridge_backend/runtime/port_guard.py
- ### ./bridge_backend/runtime/ports.py
- ### ./bridge_backend/runtime/temporal_stage_manager.py
- ### ./bridge_backend/runtime/quantum_predeploy_orchestrator.py
- ### ./bridge_backend/runtime/auto_repair.py
- ### ./bridge_backend/runtime/predictive_stabilizer.py
- ### ./bridge_backend/runtime/telemetry.py
- ### ./bridge_backend/runtime/run_migrations.py
- ### ./bridge_backend/runtime/metrics_middleware.py
- ### ./bridge_backend/runtime/parity.py
- ### ./bridge_backend/runtime/wait_for_db.py
- ### ./bridge_backend/runtime/db_url_guard.py
- ### ./bridge_backend/runtime/tickets.py
- ### ./bridge_backend/runtime/egress_canary.py
- ### ./bridge_backend/runtime/tde_x/stabilization.py
- ### ./bridge_backend/runtime/tde_x/orchestrator.py
- ### ./bridge_backend/runtime/tde_x/queue.py
- ### ./bridge_backend/runtime/tde_x/__init__.py
- ### ./bridge_backend/runtime/tde_x/orchestrator_v2.py
- ### ./bridge_backend/runtime/tde_x/federation.py
- ### ./bridge_backend/runtime/tde_x/shards/bootstrap.py
- ### ./bridge_backend/runtime/tde_x/shards/runtime.py
- ### ./bridge_backend/runtime/tde_x/shards/__init__.py
- ### ./bridge_backend/runtime/tde_x/shards/diagnostics.py
- ### ./bridge_backend/runtime/tde_x/stages/post_boot.py
- ### ./bridge_backend/runtime/tde_x/stages/scan_federation.py
- ### ./bridge_backend/runtime/tde_x/stages/index_assets.py
- ### ./bridge_backend/runtime/tde_x/stages/warm_caches.py
- ### ./bridge_backend/runtime/tde_x/stages/__init__.py
- ### ./bridge_backend/routes/health.py
- ### ./bridge_backend/routes/diagnostics_timeline.py
- ### ./bridge_backend/routes/control.py
- ### ./bridge_backend/routes/__init__.py
- ### ./bridge_backend/diagnostics/verify_env_sync.py
- ### ./bridge_backend/integrations/github_issues.py
- ### ./bridge_backend/integrations/__init__.py
- ### ./bridge_backend/tests/test_chimera_oracle.py
- ### ./bridge_backend/tests/test_autonomy_governor.py
- ### ./bridge_backend/tests/test_agents_registry.py
- ### ./bridge_backend/tests/test_protocols_registry.py
- ### ./bridge_backend/tests/test_protocols_routes.py
- ### ./bridge_backend/tests/test_speech_engines.py
- ### ./bridge_backend/tests/test_permissions.py
- ### ./bridge_backend/tests/test_arie_truth_cascade.py
- ### ./bridge_backend/tests/test_mas_healing.py
- ### ./bridge_backend/tests/test_hxo_nexus.py
- ### ./bridge_backend/tests/test_agents_routes.py
- ### ./bridge_backend/tests/test_arie_scheduler.py
- ### ./bridge_backend/tests/test_hydra_guard.py
- ### ./bridge_backend/tests/test_parity_autofix.py
- ### ./bridge_backend/tests/test_counterfeit_detector.py
- ### ./bridge_backend/tests/test_chimera_genesis_recovery.py
- ### ./bridge_backend/tests/test_protocols_models.py
- ### ./bridge_backend/tests/test_hubsync.py
- ### ./bridge_backend/tests/test_parser_enhanced.py
- ### ./bridge_backend/tests/test_leviathan_tags.py
- ### ./bridge_backend/tests/test_integration_section2.py
- ### ./bridge_backend/tests/test_umbra_predictive.py
- ### ./bridge_backend/tests/test_parser_engine.py
- ### ./bridge_backend/tests/test_console_routes.py
- ### ./bridge_backend/tests/test_firewall_autonomy_engine.py
- ### ./bridge_backend/tests/test_registry.py
- ### ./bridge_backend/tests/test_hxo_planner.py
- ### ./bridge_backend/tests/test_stripe_webhook.py
- ### ./bridge_backend/tests/test_autonomy_v196t.py
- ### ./bridge_backend/tests/test_cascade.py
- ### ./bridge_backend/tests/test_genesis_topics.py
- ### ./bridge_backend/tests/test_github_forge.py
- ### ./bridge_backend/tests/test_db_manager.py
- ### ./bridge_backend/tests/test_hxo_v196p.py
- ### ./bridge_backend/tests/test_indoctrination_engine.py
- ### ./bridge_backend/tests/test_protocols_routes_lore_policy.py
- ### ./bridge_backend/tests/test_netlify_validator.py
- ### ./bridge_backend/tests/test_creativity.py
- ### ./bridge_backend/tests/test_vaulting.py
- ### ./bridge_backend/tests/test_autonomy_comprehensive_integration.py
- ### ./bridge_backend/tests/test_envsync_pipeline.py
- ### ./bridge_backend/tests/test_integrity_audit.py
- ### ./bridge_backend/tests/test_github_envhook.py
- ### ./bridge_backend/tests/test_fault_injection.py
- ### ./bridge_backend/tests/test_leviathan_solver.py
- ### ./bridge_backend/tests/smoke_test_solver.py
- ### ./bridge_backend/tests/test_signing_roundtrip.py
- ### ./bridge_backend/tests/test_render_fallback.py
- ### ./bridge_backend/tests/test_autonomy_routes.py
- ### ./bridge_backend/tests/test_reflex_loop.py
- ### ./bridge_backend/tests/test_leviathan.py
- ### ./bridge_backend/tests/test_recovery_orchestrator.py
- ### ./bridge_backend/tests/test_envsync_engine.py
- ### ./bridge_backend/tests/test_relay_mailer.py
- ### ./bridge_backend/tests/test_arie_autonomous_integration.py
- ### ./bridge_backend/tests/test_license_scanner.py
- ### ./bridge_backend/tests/test_umbra_memory.py
- ### ./bridge_backend/tests/test_missions_routes.py
- ### ./bridge_backend/tests/test_system_routes.py
- ### ./bridge_backend/tests/test_route_sweep.py
- ### ./bridge_backend/tests/test_leviathan_unified.py
- ### ./bridge_backend/tests/test_solver_minimal.py
- ### ./bridge_backend/tests/test_brain.py
- ### ./bridge_backend/tests/test_envscribe.py
- ### ./bridge_backend/tests/test_envrecon.py
- ### ./bridge_backend/tests/test_truth_engine.py
- ### ./bridge_backend/tests/test_pr_summary.py
- ### ./bridge_backend/tests/test_runtime_guards.py
- ### ./bridge_backend/tests/test_total_stack_triage.py
- ### ./bridge_backend/tests/test_envrecon_autonomy_integration.py
- ### ./bridge_backend/tests/test_autonomy_genesis_link.py
- ### ./bridge_backend/tests/test_heritage_bus.py
- ### ./bridge_backend/tests/test_umbra_echo.py
- ### ./bridge_backend/tests/test_activity_routes.py
- ### ./bridge_backend/tests/test_protocols_routes_invoke_stub.py
- ### ./bridge_backend/tests/test_umbra_core.py
- ### ./bridge_backend/tests/test_federation_smoke.py
- ### ./bridge_backend/tests/test_permissions_routes.py
- ### ./bridge_backend/tests/test_filing_engine.py
- ### ./bridge_backend/tests/test_vault_routes.py
- ### ./bridge_backend/tests/test_hxo_genesis_link.py
- ### ./bridge_backend/tests/test_inspector_ui.py
- ### ./bridge_backend/tests/test_arie_routes.py
- ### ./bridge_backend/tests/test_push_permissions.py
- ### ./bridge_backend/tests/test_protocols_routes_seal.py
- ### ./bridge_backend/tests/test_chimera_engine.py
- ### ./bridge_backend/tests/test_agents_foundry.py
- ### ./bridge_backend/tests/test_firewall_watchdog.py
- ### ./bridge_backend/tests/test_protocols_storage.py
- ### ./bridge_backend/tests/test_arie_engine.py
- ### ./bridge_backend/tests/test_guardians_routes.py
- ### ./bridge_backend/tests/test_reflex_guardrails.py
- ### ./bridge_backend/tests/test_deep_seek_triage.py
- ### ./bridge_backend/tests/test_chimera_preflight.py
- ### ./bridge_backend/tests/test_envscribe_integration.py
- ### ./bridge_backend/tests/test_umbra_triage_healers.py
- ### ./bridge_backend/tests/test_screen_engine.py
- ### ./bridge_backend/tests/test_autonomy_engine.py
- ### ./bridge_backend/tests/test_fleet_routes.py
- ### ./bridge_backend/tests/test_steward.py
- ### ./bridge_backend/tests/test_protocols_registry_flags.py
- ### ./bridge_backend/tests/test_autonomy_integration.py
- ### ./bridge_backend/tests/smoke_test_umbra.py
- ### ./bridge_backend/tests/test_invoke_backend.py
- ### ./bridge_backend/tests/test_imports.py
- ### ./bridge_backend/tests/test_badgegen.py
- ### ./bridge_backend/tests/test_health_record.py
- ### ./bridge_backend/tests/test_custody_routes.py
- ### ./bridge_backend/webhooks/render.py
- ### ./bridge_backend/webhooks/deployment_webhooks.py
- ### ./bridge_backend/webhooks/__init__.py
- ### ./bridge_backend/webhooks/netlify.py
- ### ./bridge_backend/webhooks/github.py
- ### ./bridge_backend/src/keys.py
- ### ./bridge_backend/src/brain.py
- ### ./bridge_backend/src/brain_cli.py
- ### ./bridge_backend/src/export_and_sign.py
- ### ./bridge_backend/src/__init__.py
- ### ./bridge_backend/src/signer.py
- ### ./tests/test_captain_agent_separation.py
- ### ./tests/integration_test_genesis_linkage.py
- ### ./tests/test_umbra_routes.py
- ### ./tests/test_forge_dominion_v197s.py
- ### ./tests/test_blueprint_engine.py
- ### ./tests/test_bridge_core_ci.py
- ### ./tests/test_unified_runtime_v195.py
- ### ./tests/test_anchorhold_protocol.py
- ### ./tests/test_zero_trust_validation.py
- ### ./tests/test_v196c_features.py
- ### ./tests/test_v196i_features.py
- ### ./tests/test_codex_engine.py
- ### ./tests/deployment_readiness_v197c.py
- ### ./tests/test_genesis_v2_0_1.py
- ### ./tests/test_forge_cascade_synchrony.py
- ### ./tests/test_selftest_v197j.py
- ### ./tests/test_forge_manifest_resolver.py
- ### ./tests/test_v196g_features.py
- ### ./tests/test_db_url_guard.py
- ### ./tests/test_v197c_genesis_linkage.py
- ### ./tests/test_blueprint_api.py
- ### ./tests/test_mission_and_log_models.py
- ### ./tests/test_umbra_lattice_core.py
- ### ./tests/verify_genesis_v2.py
- ### ./tests/validate_sanctum_cascade.py
- ### ./tests/test_v196b_features.py
- ### ./tests/test_v196f_features.py
- ### ./tests/test_v200_genesis.py
- ### ./tests/test_runtime_handler.py
- ### ./tests/test_autonomy_node.py
- ### ./tests/test_git_sovereign_agent.py
- ### ./tests/test_v196h_features.py
- ### ./tests/test_quantum_dominion.py
- ### ./codex/html_compiler.py
- ### ./codex/markdown_compiler.py
- ### ./codex/compiler.py
- ### ./codex/blueprint_engine.py
- ### ./codex/__init__.py
- ### ./codex/parser_engine.py
- ### ./codex/truth_engine.py
- ### ./bridge-frontend/vite.config.js
- ### ./bridge-frontend/scripts/update-badge.js
- ### ./bridge-frontend/scripts/build_triage.py
- ### ./bridge-frontend/netlify/functions/diagnostic.js
- ### ./bridge-frontend/src/api.js
- ### ./bridge-frontend/src/config.js
- ### ./bridge-frontend/src/api/scans.js
- ### ./bridge-frontend/src/api/permissions.js
- ### ./bridge-frontend/src/api/index.js
- ### ./bridge-frontend/src/api/leviathan.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_offer.js
- ### ./bridge-frontend/src/api/auto_generated/engines_autonomy_tasks.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_tag_remove.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_list.js
- ### ./bridge-frontend/src/api/auto_generated/heritage_demo_mode.js
- ### ./bridge-frontend/src/api/auto_generated/engines_filing_search.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_ice.js
- ### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name.js
- ### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name_policy.js
- ### ./bridge-frontend/src/api/auto_generated/engines_creativity_search.js
- ### ./bridge-frontend/src/api/auto_generated/doctrine.js
- ### ./bridge-frontend/src/api/auto_generated/system_repair.js
- ### ./bridge-frontend/src/api/auto_generated/engines_autonomy_task.js
- ### ./bridge-frontend/src/api/auto_generated/permissions_tiers_tier_name.js
- ### ./bridge-frontend/src/api/auto_generated/custody_sign.js
- ### ./bridge-frontend/src/api/auto_generated/brain_memories.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_tag_add.js
- ### ./bridge-frontend/src/api/auto_generated/protocols.js
- ### ./bridge-frontend/src/api/auto_generated/custody_admiral.js
- ### ./bridge-frontend/src/api/auto_generated/engines_filing_reassemble.js
- ### ./bridge-frontend/src/api/auto_generated/console_snapshot.js
- ### ./bridge-frontend/src/api/auto_generated/engines_truth_bind.js
- ### ./bridge-frontend/src/api/auto_generated/engines_creativity_list.js
- ### ./bridge-frontend/src/api/auto_generated/vault_subpath:path.js
- ### ./bridge-frontend/src/api/auto_generated/custody_admiral_rotate.js
- ### ./bridge-frontend/src/api/auto_generated/protocols_name_vault.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_ingest.js
- ### ./bridge-frontend/src/api/auto_generated/api_control_hooks_triage.js
- ### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name_lore.js
- ### ./bridge-frontend/src/api/auto_generated/scans.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_search.js
- ### ./bridge-frontend/src/api/auto_generated/engines_truth_find.js
- ### ./bridge-frontend/src/api/auto_generated/custody_keys_key_name_generate.js
- ### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_registry.js
- ### ./bridge-frontend/src/api/auto_generated/engines_recovery_dispatch_and_ingest.js
- ### ./bridge-frontend/src/api/auto_generated/brain_export.js
- ### ./bridge-frontend/src/api/auto_generated/blueprint.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_link.js
- ### ./bridge-frontend/src/api/auto_generated/scans_scan_id.js
- ### ./bridge-frontend/src/api/auto_generated/brain_stats.js
- ### ./bridge-frontend/src/api/auto_generated/payments_stripe_webhook.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_list.js
- ### ./bridge-frontend/src/api/auto_generated/fleet.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_chunk_sha.js
- ### ./bridge-frontend/src/api/auto_generated/heritage_demo_modes.js
- ### ./bridge-frontend/src/api/auto_generated/api_control_rollback.js
- ### ./bridge-frontend/src/api/auto_generated/protocols_name_activate.js
- ### ./bridge-frontend/src/api/auto_generated/custody_keys_key_name.js
- ### ./bridge-frontend/src/api/auto_generated/engines_indoctrination_aid_certify.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_state.js
- ### ./bridge-frontend/src/api/auto_generated/custody_dock_day_drop.js
- ### ./bridge-frontend/src/api/auto_generated/permissions_apply_tier.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_start.js
- ### ./bridge-frontend/src/api/auto_generated/registry_tier_me.js
- ### ./bridge-frontend/src/api/auto_generated/custody_verify.js
- ### ./bridge-frontend/src/api/auto_generated/engines_leviathan_solve.js
- ### ./bridge-frontend/src/api/auto_generated/protocols_name.js
- ### ./bridge-frontend/src/api/auto_generated/engines_cascade_history.js
- ### ./bridge-frontend/src/api/auto_generated/brain_verify.js
- ### ./bridge-frontend/src/api/auto_generated/blueprint_draft.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_overlay.js
- ### ./bridge-frontend/src/api/auto_generated/engines_cascade_apply.js
- ### ./bridge-frontend/src/api/auto_generated/blueprint_bp_id.js
- ### ./bridge-frontend/src/api/auto_generated/engines_creativity_ingest.js
- ### ./bridge-frontend/src/api/auto_generated/engines_truth_truths.js
- ### ./bridge-frontend/src/api/auto_generated/engines_speech_tts.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_answer.js
- ### ./bridge-frontend/src/api/auto_generated/custody_init.js
- ### ./bridge-frontend/src/api/auto_generated/engines_parser_reassemble.js
- ### ./bridge-frontend/src/api/auto_generated/permissions_tiers.js
- ### ./bridge-frontend/src/api/auto_generated/permissions_current.js
- ### ./bridge-frontend/src/api/auto_generated/engines_filing_file.js
- ### ./bridge-frontend/src/api/auto_generated/console_summary.js
- ### ./bridge-frontend/src/api/auto_generated/custody_verify_drop.js
- ### ./bridge-frontend/src/api/auto_generated/blueprint_bp_id_commit.js
- ### ./bridge-frontend/src/api/auto_generated/engines_indoctrination_aid_revoke.js
- ### ./bridge-frontend/src/api/auto_generated/engines_screen_sid.js
- ### ./bridge-frontend/src/api/auto_generated/custody_keys.js
- ### ./bridge-frontend/src/api/auto_generated/custody_keys_key_name_rotate.js
- ### ./bridge-frontend/src/api/auto_generated/index.js
- ### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name_invoke.js
- ### ./bridge-frontend/src/api/auto_generated/engines_speech_stt.js
- ### ./bridge-frontend/src/api/auto_generated/brain_categories.js
- ### ./bridge-frontend/src/api/auto_generated/brain.js
- ### ./bridge-frontend/src/api/auto_generated/engines_truth_cite.js
- ### ./bridge-frontend/src/api/auto_generated/brain_memories_entry_id.js
- ### ./bridge-frontend/src/utils/endpointBootstrap.js
- ### ./bridge-frontend/src/hooks/useBridgeStream.js
- ### ./brh/heartbeat_daemon.py
- ### ./brh/role.py
- ### ./brh/consensus.py
- ### ./brh/handover.py
- ### ./brh/forge_auth.py
- ### ./brh/test_consensus_role.py
- ### ./brh/test_integration.py
- ### ./brh/test_api_endpoints.py
- ### ./brh/chaos.py
- ### ./brh/recovery.py
- ### ./brh/api.py
- ### ./brh/test_chaos_recovery.py
- ### ./brh/test_phase6_integration.py
- ### ./brh/__init__.py
- ### ./brh/run.py
- ### ./brh/examples/test_forge_auth.py
- ### ./phoenix/backend/main.py
- ### ./phoenix/backend/schemas.py
- ### ./phoenix/backend/db.py
- ### ./phoenix/backend/models.py
- ### ./phoenix/backend/core/__init__.py
- ### ./phoenix/backend/core/engines/calculus_core.py
- ### ./phoenix/backend/core/engines/__init__.py
- ### ./phoenix/backend/core/agents/__init__.py
- ### ./phoenix/backend/core/agents/routes.py
- ### ./phoenix/backend/core/missions/__init__.py
- ### ./phoenix/backend/core/missions/routes.py


### ./vault/README.md

- # SR-AIbridge Vault
- ## Purpose
- ## Structure
- ## What Goes in the Vault?
- ### ✅ Include
- ### ❌ Exclude (Keep at Root)
- ## Vault vs Backend Vault
- ## Usage Guidelines
- ### Adding to Vault
- ### Retrieving from Vault
- ## Integration with Bridge UI
- ## Sovereign Git Mode
- ## Current Vault Contents
- ### Archived Scripts (`archived_scripts/`)
- ### Reference SQL (`reference_sql/`)
- ### Old Configurations (`old_configs/`)
- ### Documentation (`documentation/`)


### ./vault/archived_scripts/LOC_REPORT.md

- # SR-AIbridge - Lines of Code Report
- ## Summary
- ## Breakdown by File Type
- ## Detailed File List by Category
- ### Python (7 files, 1,660 lines)
- ### Shell (2 files, 352 lines)


### ./bridge-frontend/README.md

- # 🕯️ Bridge Frontend – Scrollstream Manifest
- ## 🗺️ Layout
- ## ⚙️ Scripts
- ## 🪶 Expansion
- ## 📜 Doctrine
- ## ⚔️ Rituals


### ./bridge-frontend/DEPLOYMENT_VALIDATION.md

- # Deployment Validation & True Reveal Protocol
- ## Overview
- ## Architecture
- ### Core Components
- #### 1. DeploymentValidator (`services/deployment-validator.js`)
- #### 2. DeploymentGate (`components/DeploymentGate.jsx`)
- #### 3. TrueDataRevealer (`services/true-data-revealer.js`)
- #### 4. SilentFailureCapture (`services/silent-failure-capture.js`)
- ## Implementation Guide
- ### Wrapping Components
- ### Adding to App
- ## Components Using Deployment Gates
- ## Deployment Modes
- ### Production Mode
- ### Degraded Mode
- ### Development Mode
- ## Security Features
- ### Paranoid Security Gates
- ### Validation Checks
- ## Testing
- ### Manual Testing
- # Terminal 1: Start backend
- # Terminal 2: Start frontend
- ### Validation Status
- ## Monitoring
- ### Health Dashboard
- ### Crash Forensics
- ## Troubleshooting
- ### Components Stuck in Placeholder Mode
- ### Linting Errors
- ## Best Practices
- ## Future Enhancements
- ## Contributing
- ## License


### ./bridge-frontend/src/api/auto_generated/README.md

- # Auto-Generated API Clients
- ## ⚠️ Important
- ## Generation Source
- ## Structure
- ## Usage
- ### Direct Import
- ### Index Export
- ## Integration Workflow
- ## Regeneration
- # Step 1: Analyze parity
- # Step 2: Auto-fix and regenerate
- ## Severity Levels
- ## Path Parameters
- ## HTTP Method Detection
- ## Documentation
- ## Support


### ./brh/README.md

- # Bridge Runtime Handler (BRH)
- ## What is BRH?
- ## Quick Start
- # 1. Generate authentication
- # 2. Set environment (copy from output above)
- # 3. Install dependencies
- # 4. Run BRH
- ## Components
- ## Key Features
- ## Documentation
- ## Security
- ## Architecture
- ## Requirements
- ## License


### ./brh/examples/README.md

- # BRH Examples
- ## Scripts
- ### generate_forge_root.sh
- # Development with default seal
- # Production with custom seal
- ### test_forge_auth.py
- # First, set the environment variables
- # Then run the test
- ## Quick Start


### ./phoenix/README.md

- # 🔥 Phoenix - Documented Perfection Rebuild
- ## What is This?
- ### Purpose
- ## 📁 Structure
- ## 🚀 Quick Start
- ### Run Phoenix Backend
- ### Test Endpoints
- # Health check
- # API documentation
- # Create an agent
- # Use CalculusCore
- ## ✅ Current Status
- ### Phase 1: Core Backend - **COMPLETE** ✅
- ### Phase 2: Five More Engines - **20% Complete**
- ## 📊 Phoenix vs Current
- ## 🧪 Testing
- # Test CalculusCore differentiation
- ## 📚 Documentation
- ### In This Repo
- ### Source Documentation
- ## 🎯 What's Next
- ### Immediate (Phase 2)
- ### Short-term (Phases 3-4)
- ### Long-term (Phases 5-6)
- ## 💡 Key Learnings
- ### What Phoenix Proves
- ### What Phoenix Reveals
- ## 🏆 Phoenix Achievements
- ## 🔥 The Phoenix Philosophy
- ## 🛠️ Development
- ### Add New Feature
- ### Testing
- # Manual testing
- # Use curl or Postman
- # Automated testing (future)
- # Compare with current
- ## ⚡ FAQ
- ## 📞 Support
- ## 🌟 Summary


### ./phoenix/backend/README.md

- # Phoenix Protocol - Backend
- ## 🔥 What is This?
- ## 🚀 Quick Start
- # Install dependencies
- # Run backend (uses port 8001 to avoid conflict)
- ## 📋 API Endpoints
- ### Health & Status
- ### Coming Soon (Following BUILD_DOSSIER phases)
- ## 📚 Built From Documentation
- ## 🎯 Current Status
- ## 🔍 Comparison with Current
- ## 📊 Testing
- # Test health endpoints
- ## 🛠️ Development
- # Install dev dependencies
- # Run tests (when available)
- # Format code
- # Lint code
- ## 📝 Notes


---
## 🧬 Blueprint Overview

### ./activate_autonomy.py
  - import sys
  - import asyncio
  - from pathlib import Path
  - from engines.sanctum.core import SanctumEngine
  - from engines.forge.core import ForgeEngine
  - from engines.arie.core import ARIEEngine
  - from engines.elysium.core import ElysiumGuardian
  - print("Make sure you're running this from the repository root.")
  - import traceback


### ./__init__.py


### ./bridge_core/update_forge_banner_from_events.js
  - * Updates forge_pulse_banner.svg with live event data from Dominion pulse.
  - * Load pulse events from state file
  - * Calculate pulse status from events


### ./bridge_core/__init__.py


### ./bridge_core/lattice/bridge_harmony.py
  - import sys
  - from pathlib import Path
  - from typing import Dict, List, Optional, Any
  - from dataclasses import dataclass
  - import traceback
  - import argparse


### ./bridge_core/lattice/heartbeat.py
  - import sys
  - import time
  - import argparse


### ./bridge_core/lattice/pathcheck.py
  - import sys
  - import argparse
  - from pathlib import Path


### ./bridge_core/lattice/__init__.py


### ./bridge_core/security/validate_token.py
  - import sys
  - import argparse
  - import os


### ./bridge_core/security/__init__.py


### ./bridge_core/self_heal/guard.py
  - import sys
  - import argparse
  - import bridge_core  # noqa: F401


### ./bridge_core/self_heal/__init__.py


### ./scripts/validate_netlify.py
  - import sys
  - import os
  - from pathlib import Path
  - import re


### ./scripts/integrity_audit.py
  - import os
  - import requests
  - import json
  - import time


### ./scripts/view_envsync_manifest.py
  - import sys
  - from pathlib import Path
  - from typing import Dict, List, Tuple
  - from collections import defaultdict
  - # Extract metadata from comments


### ./scripts/repair_netlify_env.py
  - import os, requests, sys


### ./scripts/verify_reflex_loop.py
  - import os
  - import sys
  - from pathlib import Path
  - import signer
  - import verifier
  - import __init__ as autonomy_init


### ./scripts/verify_autonomy_node.py
  - import os
  - import sys
  - import json
  - import importlib.util
  - from pathlib import Path
  - print(f"{Colors.RED}❌{Colors.RESET} {description} import FAILED: {e}")
  - import truth
  - import parser
  - import cascade
  - import blueprint


### ./scripts/fix_deprecated_datetime.py
  - import os
  - import re
  - from pathlib import Path
  - from typing import List, Tuple
  - has_timezone_import = 'from datetime import' in content and 'timezone' in content
  - has_utc_import = 'datetime.UTC' in content or 'timezone.utc' in content
  - # Fix the import statement if needed
  - # Find datetime import line
  - import_pattern = r'from datetime import ([^\n]+)'
  - content = re.sub(import_pattern, f'from datetime import {new_imports}', content, count=1)


### ./scripts/repo_cleanup.py
  - import os
  - import json
  - import shutil
  - from pathlib import Path
  - from datetime import datetime, timezone
  - """Remove duplicate public_keys.json from exports"""
  - import argparse


### ./scripts/scan_manual_env_vars.py
  - import os
  - import re
  - import json
  - from pathlib import Path
  - from typing import Dict, List, Set
  - from datetime import datetime, timezone
  - """Extract environment variable names from a file"""
  - print("🔍 Loading configured variables from .env files...")
  - "description": "These are API keys, tokens, or secrets that must be obtained from third-party services"


### ./scripts/synthesize_netlify_artifacts.py
  - from pathlib import Path
  - import os
  - # If we're being called from bridge-frontend (Netlify base dir), use current dir
  - # Running from bridge-frontend (Netlify context)
  - # Running from repo root (legacy/local testing)


### ./scripts/validate_scanner_output.py
  - import re
  - import sys
  - import json
  - import subprocess
  - from pathlib import Path
  - import toml
  - import toml


### ./scripts/verify_frontend_deployment.py
  - import os
  - import sys
  - import json
  - from pathlib import Path


### ./scripts/smoke_test_sovereign_engines.py
  - import asyncio
  - import httpx
  - import io


### ./scripts/firewall_watchdog.py
  - import os
  - import socket
  - import time
  - import json
  - import requests
  - from datetime import datetime, timezone
  - from typing import List, Dict, Any
  - """Load the allowlist from the configuration file."""
  - print(f"📋 Loaded {len(allowlist)} hosts from allowlist")


### ./scripts/verify_umbra_lattice.py
  - import os
  - import sys
  - from pathlib import Path
  - print("✗ CLI has import errors")


### ./scripts/verify_sovereign_engines.py
  - import sys
  - import os
  - import asyncio
  - import httpx
  - from pathlib import Path
  - from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard
  - from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe
  - from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician
  - import json


### ./scripts/prune_diagnostics.py
  - import os
  - import requests
  - import json
  - from datetime import datetime, timedelta, timezone


### ./scripts/stub_scanner.py
  - import os
  - import json
  - import re
  - from pathlib import Path
  - from typing import Dict, List, Set
  - from datetime import datetime, timezone
  - "action": "Remove TODO comments from production-ready auto-generated stubs",


### ./scripts/report_bridge_event.py
  - import os
  - import requests
  - import json
  - from datetime import datetime, timezone


### ./scripts/validate_netlify_env.py
  - import os, sys
  - import subprocess
  - import re
  - # Determine the correct directory - if running from scripts/, go to bridge-frontend


### ./scripts/validate_env_setup.py
  - import os
  - import sys
  - from pathlib import Path
  - import toml
  - import yaml
  - from config import settings
  - import traceback
  - import toml
  - import yaml
  - from dotenv import load_dotenv


### ./scripts/validate_envsync_manifest.py
  - import sys
  - import os
  - from pathlib import Path
  - from typing import Dict, List, Tuple


### ./scripts/validate_copilot_env.py
  - import requests, subprocess, sys, json, os, time


### ./scripts/verify_netlify_build.py
  - import os
  - import sys
  - import requests
  - from datetime import datetime, timezone
  - This reads from the NETLIFY_BUILD_EXIT_CODE environment variable if available.
  - import json


### ./scripts/master_sovereign_audit.py
  - import os
  - import sys
  - import json
  - import subprocess
  - from pathlib import Path
  - from typing import Dict, List, Any
  - from datetime import datetime, timezone
  - import traceback
  - from sovereign_audit_orchestrator import SovereignAuditOrchestrator
  - from bridge_backend.tools.firewall_sovereignty.sovereign_orchestrator import SovereignOrchestrator
  - import argparse


### ./scripts/check_env_parity.py
  - import os
  - import requests
  - from dotenv import dotenv_values


### ./scripts/run_full_scan.py
  - import os
  - import sys
  - import json
  - import subprocess
  - import argparse
  - from pathlib import Path
  - from datetime import datetime
  - from typing import Dict, Any, List
  - import sys
  - from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path, require_netlify_token
  - import os
  - import sys
  - from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check


### ./scripts/sovereign_audit_orchestrator.py
  - import os
  - import sys
  - import json
  - import subprocess
  - from pathlib import Path
  - from typing import Dict, List, Any, Optional, Tuple
  - from datetime import datetime, timezone
  - from dataclasses import dataclass, field, asdict
  - import re
  - import argparse


### ./scripts/demonstrate_metadata_validation.py
  - import os
  - import sys
  - import time
  - from datetime import datetime, timezone
  - from bridge_backend.bridge_core.token_forge_dominion import (
  - import traceback


### ./scripts/seed_bootstrap.py
  - import asyncio
  - import sys
  - import os
  - from bridge_backend.db.bootstrap import auto_sync_schema
  - # from bridge_backend.models import Guardian
  - # from bridge_backend.db.session import get_async_session
  - import traceback


### ./scripts/comprehensive_repo_scan.py
  - import os
  - import hashlib
  - import json
  - from pathlib import Path
  - from collections import defaultdict
  - from datetime import datetime, timezone
  - from typing import Dict, List, Set, Tuple
  - # Directories to exclude from scanning


### ./scripts/clean_stub_todos.py
  - Remove TODO comments from auto-generated frontend stubs
  - import os
  - from pathlib import Path
  - from typing import List
  - Remove TODO comment from an auto-generated stub file
  - print("🔧 Removing TODO comments from auto-generated stubs...")
  - print("\n✅ All TODO comments removed from production-ready stubs!")


### ./scripts/netlify_rollback.py
  - import os
  - import requests
  - import sys
  - from datetime import datetime, timezone


### ./tools/route_sweep_check.py
  - import re
  - import sys
  - from pathlib import Path
  - from typing import List, Tuple
  - if stripped.startswith('#') or stripped.startswith('import ') or stripped.startswith('from '):


### ./tools/__init__.py


### ./netlify/functions/bridge-deploy.js
  - // Pull Forge credentials dynamically from the Dominion root


### ./netlify/functions/forge-resolver.js
  - import crypto from "crypto";
  - // Construct URL from event properties for better compatibility
  - console.log(`💓 Heartbeat from ${pulse.node} @ ${pulse.epoch}`);
  - console.warn(`⚠️  Stale heartbeat from ${pulse.node} (age: ${age}s)`);
  - * Handle consensus election reports from BRH nodes
  - * Handle leader query requests from BRH nodes


### ./bridge_backend/main.py
  - import sys
  - import os
  - import asyncio
  - import time
  - import logging
  - from fastapi import FastAPI
  - from fastapi.middleware.cors import CORSMiddleware
  - from dotenv import load_dotenv
  - from importlib import import_module
  - from bridge_backend.bridge_core.guards.netlify_guard import validate_publish_path, require_netlify_token
  - from bridge_backend.bridge_core.integrity.deferred import delayed_integrity_check
  - from bridge_backend.bridge_core.engines.umbra.autoheal_link import safe_autoheal_init
  - from bridge_backend.bridge_core.engines.reflex.auth_forge import ensure_github_token
  - from bridge_backend.genesis.bus import GenesisEventBus
  - from bridge_backend.bridge_core.integrity.core import run_integrity
  - If a router module fails to import (e.g., bad response_model typing),
  - logger.info("[CORS] Add your custom Netlify domain to ALLOWED_ORIGINS if different from sr-aibridge.netlify.app")
  - from bridge_backend.middleware.headers import HeaderSyncMiddleware
  - from bridge_backend.runtime.metrics_middleware import metrics_middleware
  - from runtime.metrics_middleware import metrics_middleware
  - from bridge_core.middleware.permissions import PermissionMiddleware
  - from bridge_backend.bridge_core.middleware.permissions import PermissionMiddleware
  - # Helper function to safely import and include a router
  - """Safely import a module and include its router, with fallback on failure."""
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.startup_watchdog import watchdog
  - from bridge_backend.runtime.port_guard import describe_port_env
  - from bridge_backend.runtime.deploy_parity import deploy_parity_check
  - from bridge_backend.runtime.temporal_deploy import tdb, TDB_ENABLED
  - from bridge_backend.genesis import activate_all_engines
  - from bridge_backend.genesis.orchestration import genesis_orchestrator
  - from bridge_backend.bridge_core.engines.adapters.genesis_link import register_all_genesis_links
  - from bridge_backend.bridge_core.engines.hxo import safe_init as chimera_safe_init
  - from bridge_backend.forge import forge_integrate_engines
  - from bridge_backend.bridge_core.engines.hxo.startup import startup_hxo_nexus
  - from bridge_backend.bridge_core.engines.adapters.hxo_nexus_integration import (
  - from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
  - from bridge_backend.runtime.deploy_parity import deploy_parity_check
  - from bridge_backend.db.bootstrap import auto_sync_schema
  - from bridge_backend.runtime.release_intel import analyze_and_stabilize
  - from bridge_backend.runtime.heartbeat import heartbeat_loop
  - from bridge_backend.bridge_core.engines.envsync.tasks import run_scheduled_sync
  - from bridge_backend.bridge_core.engines.envsync.config import CONFIG as ENVSYNC_CONFIG
  - import asyncio
  - from bridge_backend.runtime.deploy_parity import deploy_parity_check
  - from bridge_backend.db.bootstrap import auto_sync_schema
  - from bridge_backend.runtime.release_intel import analyze_and_stabilize
  - from bridge_backend.runtime.heartbeat import heartbeat_loop
  - from bridge_backend.runtime.predictive_stabilizer import is_live
  - from bridge_backend.bridge_core.engines.envsync.tasks import run_scheduled_sync
  - from bridge_backend.bridge_core.engines.envsync.config import CONFIG as ENVSYNC_CONFIG
  - import asyncio
  - import asyncio
  - import subprocess
  - import os
  - from bridge_backend.runtime.telemetry import TELEMETRY
  - from runtime.telemetry import TELEMETRY
  - import uvicorn


### ./bridge_backend/seed.py
  - import asyncio
  - import logging
  - from typing import Dict, Any, List
  - from datetime import datetime, timedelta
  - from db import db_manager
  - # Static fleet data for demo - in a real system this would come from database


### ./bridge_backend/schemas.py
  - Separated from SQLAlchemy models for clean architecture
  - from pydantic import BaseModel, Field
  - from typing import Optional, List, Dict, Any
  - from datetime import datetime, timezone


### ./bridge_backend/__main__.py
  - import os
  - import uvicorn
  - from bridge_backend.main import app
  - # Use adaptive port resolution from runtime.ports
  - from bridge_backend.runtime.ports import resolve_port


### ./bridge_backend/db.py
  - import os
  - import logging
  - import asyncio
  - from contextlib import asynccontextmanager
  - from typing import AsyncGenerator, List, Dict, Any, Optional
  - from datetime import datetime, timezone
  - from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
  - from sqlalchemy.exc import SQLAlchemyError, OperationalError
  - from models import Base, Guardian, VaultLog, Mission, Agent
  - from sqlalchemy import text
  - from sqlalchemy import text
  - from sqlalchemy import text
  - from sqlalchemy import text
  - from sqlalchemy import text
  - from sqlalchemy import text


### ./bridge_backend/config.py
  - import os
  - from typing import List
  - from dotenv import load_dotenv


### ./bridge_backend/__init__.py
  - import asyncio
  - import logging
  - from bridge_backend.config import settings
  - from sqlalchemy import create_engine, text
  - from bridge_backend.db import async_engine
  - from sqlalchemy import text
  - # Run verification on import if running in async context
  - """Initialize database check - call this from FastAPI startup"""
  - from bridge_backend.config import settings
  - from subprocess import run
  - import os


### ./bridge_backend/run.py
  - import os
  - import sys
  - import asyncio
  - import uvicorn
  - from bridge_backend.runtime.tde_x.orchestrator import run_tde_x


### ./bridge_backend/models.py
  - from sqlalchemy.ext.asyncio import AsyncSession
  - from sqlalchemy.orm import declarative_base, relationship
  - from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, func, ForeignKey, JSON, Enum as PgEnum
  - from datetime import datetime
  - import enum


### ./bridge_backend/db/bootstrap.py
  - import os
  - import logging
  - from pathlib import Path
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
  - from bridge_backend.utils.db import engine
  - from bridge_backend.models import Base as ModelsBase
  - from bridge_backend.bridge_core.token_forge_dominion import generate_root_key
  - import json
  - from datetime import datetime


### ./bridge_backend/db/__init__.py


### ./bridge_backend/metrics/health_record.py
  - import click
  - import json
  - import sys
  - import os
  - import gzip
  - from pathlib import Path
  - from datetime import datetime, timedelta, timezone
  - from typing import Dict, Any, Optional


### ./bridge_backend/metrics/__init__.py


### ./bridge_backend/examples/relay_mailer_example.py
  - Run from bridge_backend directory:
  - import asyncio
  - import sys
  - from pathlib import Path
  - from utils.relay_mailer import relay_mailer
  - print("🗑️  Safe to delete from active database")
  - # Check for queued items (from previous failed sends)


### ./bridge_backend/models/core.py
  - from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
  - from sqlalchemy import String, DateTime, func


### ./bridge_backend/models/__init__.py
  - from .core import Base, User  # re-export
  - # Re-export models from top-level models.py if available
  - """Lazy import for models to avoid circular imports"""
  - # Import directly from the models.py module, not bridge_backend.models package
  - import importlib.util
  - import os


### ./bridge_backend/bridge_core/routes_custody.py
  - from fastapi import APIRouter, HTTPException, Body
  - from typing import List, Dict, Any, Optional
  - from pydantic import BaseModel
  - from datetime import datetime
  - import os
  - from src.keys import SovereignKeys, initialize_admiral_keys
  - from src.signer import create_signer
  - from src.export_and_sign import create_dock_day_exporter
  - # Extract additional details from the envelope


### ./bridge_backend/bridge_core/prooffoundry.py
  - import logging
  - import json
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Union
  - from dataclasses import dataclass
  - from enum import Enum
  - import sympy as sp
  - from sympy import symbols, Eq, solve, simplify, expand, factor, diff, integrate
  - from sympy.logic import satisfiable
  - from sympy.geometry import Point, Line, Circle
  - from sympy.matrices import Matrix


### ./bridge_backend/bridge_core/chroniclevault.py
  - import logging
  - import json
  - from datetime import datetime, timedelta, timezone
  - from typing import Dict, List, Any, Optional, Union
  - from dataclasses import dataclass, asdict
  - from enum import Enum
  - import hashlib
  - """Create record from dictionary"""
  - logger.info(f"📝 Recorded: {title} [{record_id}] from {source}")
  - logger.info(f"🔄 Starting replay {replay_id} from {start_time} to {end_time}")
  - """Remove record from all indexes"""
  - # Remove from type index
  - # Remove from source index
  - # Remove from tag indexes


### ./bridge_backend/bridge_core/entanglecore.py
  - import logging
  - import json
  - import random
  - import math
  - import cmath
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Union, Tuple
  - from dataclasses import dataclass
  - from enum import Enum
  - import numpy as np


### ./bridge_backend/bridge_core/runtime_handler.py
  - import os
  - import yaml
  - import json
  - import asyncio
  - import logging
  - from typing import Dict, List, Optional, Any
  - from pathlib import Path
  - from datetime import datetime, timedelta
  - import hashlib
  - import hmac
  - import base64
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
  - import socket


### ./bridge_backend/bridge_core/paths.py
  - from __future__ import annotations
  - import importlib
  - import logging


### ./bridge_backend/bridge_core/federation_client.py
  - import asyncio
  - import logging
  - import json
  - import aiohttp
  - from datetime import datetime, timedelta, timezone
  - from typing import Dict, List, Any, Optional, Callable
  - from enum import Enum
  - from dataclasses import dataclass, asdict
  - import hashlib
  - """Handle incoming task from another bridge"""
  - logger.info(f"📥 Received task {task.task_id} from {task.source_bridge}")
  - """Handle incoming heartbeat from another bridge"""
  - logger.debug(f"💓 Heartbeat from {heartbeat.node_id}")


### ./bridge_backend/bridge_core/claude_watcher.py
  - import logging
  - import json
  - from datetime import datetime, timedelta, timezone
  - from typing import Dict, List, Any, Optional
  - from dataclasses import dataclass, asdict
  - from enum import Enum
  - logger.info(f"📊 Event logged: {event_type.value} - {severity.value} from {source}")


### ./bridge_backend/bridge_core/labyrinthforge.py
  - import logging
  - import json
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Union
  - from dataclasses import dataclass
  - from enum import Enum
  - # Remove from active experiments
  - """Generate scientific observations from experimental results"""


### ./bridge_backend/bridge_core/fault_injector.py
  - import asyncio
  - import logging
  - import random
  - import json
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Callable, Union
  - from enum import Enum
  - from dataclasses import dataclass
  - import hashlib


### ./bridge_backend/bridge_core/routes_brain.py
  - from fastapi import APIRouter, HTTPException, Query, Request
  - from typing import Optional, List, Dict, Any
  - from pydantic import BaseModel
  - from datetime import datetime
  - from src.brain import create_brain_ledger
  - from bridge_backend.src.brain import create_brain_ledger


### ./bridge_backend/bridge_core/self_healing_adapter.py
  - import asyncio
  - import logging
  - import json
  - from datetime import datetime, timedelta, timezone
  - from typing import Dict, List, Any, Optional, Callable, Union
  - from enum import Enum
  - from dataclasses import dataclass
  - import hashlib
  - from functools import wraps


### ./bridge_backend/bridge_core/__init__.py
  - from .claude_watcher import ClaudeWatcher
  - from .fault_injector import FaultInjector
  - from .self_healing_adapter import SelfHealingMASAdapter
  - from .federation_client import FederationClient
  - from .registry_payloads import current_registry_payloads
  - from .engines.scrolltongue import ScrollTongue
  - from .engines.commerceforge import CommerceForge
  - from .engines.auroraforge import AuroraForge
  - from .engines.chronicleloom import ChronicleLoom
  - from .engines.calculuscore import CalculusCore
  - from .engines.qhelmsingularity import QHelmSingularity
  - from .engines.autonomy import AutonomyEngine
  - from .labyrinthforge import LabyrinthForge
  - from .chroniclevault import ChronicleVault
  - from .prooffoundry import ProofFoundry
  - from .entanglecore import EntangleCore


### ./bridge_backend/bridge_core/registry_payloads.py
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional
  - from enum import Enum


### ./bridge_backend/bridge_core/db/db_manager.py
  - import os
  - import asyncio
  - from typing import Any, Dict, List
  - from sqlalchemy.ext.asyncio import (
  - from sqlalchemy import text
  - from .models import Base  # ORM Base import


### ./bridge_backend/bridge_core/db/schemas.py
  - from pydantic import BaseModel
  - from typing import Optional


### ./bridge_backend/bridge_core/db/models.py
  - from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
  - from sqlalchemy import Integer, String, Text
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/guardians/gate.py
  - import re
  - import logging
  - from typing import Tuple, Optional, Dict, Any, Set
  - from collections import defaultdict
  - from datetime import datetime, timedelta, timezone
  - import os


### ./bridge_backend/bridge_core/guardians/__init__.py


### ./bridge_backend/bridge_core/guardians/routes.py
  - from fastapi import APIRouter


### ./bridge_backend/bridge_core/health/__init__.py


### ./bridge_backend/bridge_core/health/routes.py
  - from fastapi import APIRouter, Request
  - from datetime import datetime, timezone
  - import os
  - Universal OK from either host with environment awareness
  - import time
  - import time
  - import os
  - import json
  - import os
  - from pathlib import Path
  - from bridge_backend.runtime.heartbeat import ensure_httpx
  - from bridge_backend.runtime.parity import verify_cors_parity


### ./bridge_backend/bridge_core/doctrine/routes.py
  - from fastapi import APIRouter


### ./bridge_backend/bridge_core/utils/async_tools.py
  - from __future__ import annotations
  - import inspect
  - import asyncio
  - from typing import Any, Awaitable, Callable, Optional


### ./bridge_backend/bridge_core/utils/__init__.py


### ./bridge_backend/bridge_core/middleware/permissions.py
  - from fastapi import Request
  - from starlette.middleware.base import BaseHTTPMiddleware
  - from starlette.responses import JSONResponse
  - from bridge_core.engines.cascade.service import CascadeEngine
  - from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine
  - from bridge_core.permissions.store import load_settings
  - from bridge_backend.bridge_core.permissions.store import load_settings
  - # Get user_id from query params as a fallback (mock auth pattern)
  - # Determine role from user_id for testing
  - # Extract notification type from request body if needed


### ./bridge_backend/bridge_core/middleware/__init__.py


### ./bridge_backend/bridge_core/engines/routes_linked.py
  - from fastapi import APIRouter, HTTPException
  - from typing import Dict, Any
  - import logging
  - import os
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.adapters import cascade_link
  - from .blueprint.adapters import super_engines_link
  - from .blueprint.adapters import utility_engines_link
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.adapters import super_engines_link
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.adapters import utility_engines_link
  - from .blueprint.registry import BlueprintRegistry
  - from .blueprint.adapters import leviathan_link


### ./bridge_backend/bridge_core/engines/filing.py
  - import os, json, hashlib
  - from datetime import datetime, timezone
  - from typing import List, Dict, Any


### ./bridge_backend/bridge_core/engines/commerceforge.py
  - import logging
  - import random
  - from datetime import datetime, timedelta, timezone
  - from typing import Dict, List, Any, Optional, Tuple
  - from dataclasses import dataclass
  - from enum import Enum
  - import math
  - # Find price from hours ago (simplified)
  - # Calculate volatility from performance history


### ./bridge_backend/bridge_core/engines/scrolltongue.py
  - import logging
  - import re
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Tuple
  - from dataclasses import dataclass
  - from enum import Enum
  - logger.info(f"🌐 Translated text from {source_language} to {target_language}")
  - # Collect themes from all scrolls
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/auroraforge.py
  - import logging
  - import random
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Tuple
  - from dataclasses import dataclass
  - from enum import Enum


### ./bridge_backend/bridge_core/engines/push_notifications.py
  - from fastapi import APIRouter, HTTPException, Request
  - from pydantic import BaseModel
  - from typing import Optional, List, Literal
  - from datetime import datetime
  - # Get user from request state (set by middleware)
  - # Get user from request state


### ./bridge_backend/bridge_core/engines/qhelmsingularity.py
  - import logging
  - import math
  - import cmath
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Tuple
  - from dataclasses import dataclass
  - from enum import Enum
  - from ..entanglecore import EntangleCore, QuantumState, QubitState
  - logger.info(f"🌀 Folded spacetime from {fold_origin} to {fold_destination} with {fold_efficiency:.2f} efficiency")
  - logger.info(f"🚁 Helm navigated from {old_position} to {new_position}")


### ./bridge_backend/bridge_core/engines/chronicleloom.py
  - import logging
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional
  - from ..chroniclevault import ChronicleVault
  - story threads from chronicle data.
  - Generate interconnected story paths from existing thread


### ./bridge_backend/bridge_core/engines/routes_filing.py
  - from fastapi import APIRouter
  - from pydantic import BaseModel
  - from typing import List
  - from bridge_core.engines.filing import FilingEngine
  - from bridge_backend.bridge_core.engines.filing import FilingEngine


### ./bridge_backend/bridge_core/engines/__init__.py
  - from .scrolltongue import ScrollTongue
  - from .commerceforge import CommerceForge
  - from .auroraforge import AuroraForge
  - from .chronicleloom import ChronicleLoom
  - from .calculuscore import CalculusCore
  - from .qhelmsingularity import QHelmSingularity
  - from .leviathan import LeviathanEngine
  - from .blueprint.blueprint_engine import BlueprintEngine
  - from .cascade.service import CascadeEngine
  - from .autonomy import AutonomyEngine
  - from .parser import ParserEngine
  - from .hxo import HXONexus
  - from .chimera.engine import ChimeraDeploymentEngine
  - from .envsync import EnvSyncEngine
  - from .filing import FilingEngine
  - from .screen.service import ScreenEngine
  - from .speech.tts import TTSEngine
  - from .speech.stt import STTEngine
  - from .recovery import RecoveryOrchestrator
  - from .creativity import CreativityBay
  - from .indoctrination.service import IndoctrinationEngine
  - from .umbra import UmbraLattice


### ./bridge_backend/bridge_core/engines/calculuscore.py
  - import logging
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional, Tuple
  - import sympy as sp
  - from sympy import symbols, diff, integrate, limit, series, solve, oo
  - from ..prooffoundry import ProofFoundry


### ./bridge_backend/bridge_core/engines/recovery/orchestrator.py
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import uuid, json
  - from bridge_core.engines.autonomy.service import AutonomyEngine
  - from bridge_core.engines.parser.service import ParserEngine
  - from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine
  - from bridge_backend.bridge_core.engines.parser.service import ParserEngine


### ./bridge_backend/bridge_core/engines/recovery/__init__.py
  - from .orchestrator import RecoveryOrchestrator


### ./bridge_backend/bridge_core/engines/recovery/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from .orchestrator import RecoveryOrchestrator


### ./bridge_backend/bridge_core/engines/speech/tts.py
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import uuid, json


### ./bridge_backend/bridge_core/engines/speech/stt.py
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import uuid, json


### ./bridge_backend/bridge_core/engines/speech/__init__.py
  - from .stt import STTEngine
  - from .tts import TTSEngine


### ./bridge_backend/bridge_core/engines/speech/routes.py
  - from fastapi import APIRouter, File, UploadFile, Form
  - from .stt import STTEngine
  - from .tts import TTSEngine


### ./bridge_backend/bridge_core/engines/chimera/healer.py
  - import logging
  - import asyncio
  - from pathlib import Path
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, UTC
  - issues: List of detected issues from simulator
  - issues: List of detected issues from simulator


### ./bridge_backend/bridge_core/engines/chimera/simulator.py
  - import logging
  - import asyncio
  - import subprocess
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, UTC
  - if "from =" not in content or "to =" not in content:
  - import yaml
  - import json


### ./bridge_backend/bridge_core/engines/chimera/certifier.py
  - import logging
  - import hashlib
  - from typing import Dict, Any, Optional
  - from datetime import datetime, UTC
  - simulation_result: Results from build simulation


### ./bridge_backend/bridge_core/engines/chimera/config.py
  - import os
  - import json
  - from typing import Dict, Any, List
  - from dataclasses import dataclass, field


### ./bridge_backend/bridge_core/engines/chimera/engine.py
  - import logging
  - import asyncio
  - from pathlib import Path
  - from typing import Dict, Any, Optional
  - from datetime import datetime, UTC
  - from .config import ChimeraConfig
  - from .simulator import BuildSimulator
  - from .healer import ConfigurationHealer
  - from .certifier import DeploymentCertifier


### ./bridge_backend/bridge_core/engines/chimera/__init__.py
  - from .engine import ChimeraDeploymentEngine, get_chimera_instance
  - from .config import ChimeraConfig


### ./bridge_backend/bridge_core/engines/chimera/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from pydantic import BaseModel
  - from typing import Optional
  - from pathlib import Path
  - import logging
  - from .engine import get_chimera_instance, ChimeraDeploymentEngine
  - from .config import ChimeraConfig


### ./bridge_backend/bridge_core/engines/leviathan/solver.py
  - from __future__ import annotations
  - from dataclasses import dataclass, asdict
  - from typing import List, Dict, Any, Optional, Tuple
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import json, hashlib, re
  - # --- Light imports from your existing engines (all local, no HTTP) ---
  - from bridge_core.engines.truth.utils import TRUTH_DIR, read_jsonl, PARSER_LEDGER, load_chunk_text
  - from bridge_core.engines.autonomy.service import AutonomyEngine
  - # Six Super Engines - import the actual engines
  - from bridge_core.engines import (
  - # 1) parser ledger → collect sentences that mention tokens from q
  - # Extract mathematical concepts from query
  - # Citations from grounding (truths + parser hits)


### ./bridge_backend/bridge_core/engines/leviathan/service.py
  - from __future__ import annotations
  - from pathlib import Path
  - from typing import List, Dict, Any, Optional
  - import json
  - import datetime as dt
  - # Creativity assets (from 6g/6h)
  - from ..creativity.service import ASSETS_DIR  # vault/creativity/assets
  - # Parser + Truth utilities (from Section 5)
  - from ..truth.utils import (
  - - parser:      sentences from Parser ledger chunks
  - - truth:       bound truths from Truth Engine
  - from ..truth.utils import sentences_from_text  # local import to avoid cycles
  - # expected truth entry (from 5f Binder): { "truth": "...", "prov":[{sha,source,ts},...], "created_at": ... }


### ./bridge_backend/bridge_core/engines/leviathan/__init__.py
  - from .service import LeviathanEngine


### ./bridge_backend/bridge_core/engines/leviathan/routes_solver.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel, Field
  - from typing import Optional, List
  - from .solver import solve, SolveRequest


### ./bridge_backend/bridge_core/engines/leviathan/routes.py
  - from fastapi import APIRouter
  - from pydantic import BaseModel, Field
  - from typing import List, Optional
  - from .service import LeviathanEngine


### ./bridge_backend/bridge_core/engines/blueprint/planner_rules.py
  - from typing import List, Dict
  - Derive high-level objectives from mission brief


### ./bridge_backend/bridge_core/engines/blueprint/blueprint_engine.py
  - from .planner_rules import derive_objectives, explode_tasks
  - from typing import Dict, Any, List
  - Create a draft blueprint from a mission brief


### ./bridge_backend/bridge_core/engines/blueprint/registry.py
  - from typing import Dict, Any, List
  - import logging
  - "purpose": "Build execution graph from blueprints",
  - "purpose": "Enforce safety policies from blueprint",


### ./bridge_backend/bridge_core/engines/blueprint/__init__.py


### ./bridge_backend/bridge_core/engines/blueprint/routes.py
  - from fastapi import APIRouter, HTTPException, Depends, Query
  - from sqlalchemy.ext.asyncio import AsyncSession
  - from sqlalchemy import select
  - from typing import List
  - import os
  - import logging
  - from bridge_backend.bridge_core.db.db_manager import get_db_session as _get_db_session
  - from bridge_backend.models import Blueprint as _Blueprint, AgentJob as _AgentJob, Mission as _Mission
  - from bridge_backend.schemas import BlueprintCreate as _BlueprintCreate, BlueprintOut as _BlueprintOut, AgentJobOut as _AgentJobOut
  - from bridge_backend.utils.relay_mailer import relay_mailer as _relay_mailer
  - from ....models import Blueprint as _Blueprint, AgentJob as _AgentJob, Mission as _Mission
  - from ....schemas import BlueprintCreate as _BlueprintCreate, BlueprintOut as _BlueprintOut, AgentJobOut as _AgentJobOut
  - from ....utils.relay_mailer import relay_mailer as _relay_mailer
  - from ...db.db_manager import get_db_session as _get_db_session
  - # Fallback for different import contexts
  - import sys
  - import os as _os
  - from models import Blueprint as _Blueprint, AgentJob as _AgentJob, Mission as _Mission
  - from schemas import BlueprintCreate as _BlueprintCreate, BlueprintOut as _BlueprintOut, AgentJobOut as _AgentJobOut
  - from utils.relay_mailer import relay_mailer as _relay_mailer
  - from bridge_core.db.db_manager import get_db_session as _get_db_session
  - from .blueprint_engine import BlueprintEngine as _BlueprintEngine
  - # In strict mode, demand the model at import time
  - # Mock authentication - in production, extract from JWT token
  - Draft a new blueprint from a mission brief
  - # Generate plan from brief
  - # Generate agent jobs from plan


### ./bridge_backend/bridge_core/engines/blueprint/adapters/leviathan_link.py
  - import logging
  - from typing import Dict, Any, List
  - Extract Leviathan configuration from blueprint manifest.
  - Coordinated results from all super engines
  - from ..registry import BlueprintRegistry
  - from ....heritage.event_bus import bus
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/tde_link.py
  - import logging
  - from typing import Dict, Any
  - from ..registry import BlueprintRegistry
  - from ....heritage.event_bus import bus
  - manifest: Blueprint manifest from preload_manifest()
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/cascade_link.py
  - import logging
  - from typing import Dict, Any, Optional
  - from ....heritage.event_bus import bus
  - event: Event payload from blueprint.events topic
  - from ..registry import BlueprintRegistry
  - from ....heritage.event_bus import bus
  - Extract Cascade configuration from blueprint manifest.
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/super_engines_link.py
  - import logging
  - from typing import Dict, Any, List
  - Extract configuration for all super engines from blueprint manifest.
  - from ....heritage.event_bus import bus
  - from ..registry import BlueprintRegistry
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/autonomy_link.py
  - import logging
  - from typing import Dict, Any, List
  - Extract autonomy rules and guardrails from blueprint manifest.
  - logger.info("[Autonomy Link] 📋 Loaded autonomy rules from blueprint")
  - rules: Autonomy rules from blueprint
  - facts: Certified facts from Truth engine
  - from ....heritage.event_bus import bus
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/utility_engines_link.py
  - import logging
  - from typing import Dict, Any, List
  - Extract configuration for all utility engines from blueprint manifest.
  - from ..registry import BlueprintRegistry
  - from ....heritage.event_bus import bus
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/truth_link.py
  - import logging
  - from typing import Dict, Any
  - import hashlib
  - import json
  - from ....heritage.event_bus import bus
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/blueprint/adapters/__init__.py
  - from . import tde_link
  - from . import cascade_link
  - from . import truth_link
  - from . import autonomy_link
  - from . import leviathan_link
  - from . import super_engines_link
  - from . import utility_engines_link


### ./bridge_backend/bridge_core/engines/creativity/service.py
  - from __future__ import annotations
  - from pathlib import Path
  - from datetime import datetime, timezone
  - from typing import Dict, Any, List, Optional
  - from dataclasses import dataclass, asdict
  - import json, uuid, hashlib


### ./bridge_backend/bridge_core/engines/creativity/__init__.py
  - from .service import CreativityBay


### ./bridge_backend/bridge_core/engines/creativity/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from typing import Optional, List
  - from .service import CreativityBay


### ./bridge_backend/bridge_core/engines/hxo/nexus.py
  - import logging
  - import asyncio
  - from typing import Dict, Any, List, Optional, Set, Callable
  - from datetime import datetime, UTC
  - from collections import defaultdict
  - import os
  - # Configuration from environment
  - # Engine definitions from the specification
  - # Initialize engine connections from specification
  - """Initialize engine connection topology from specification"""
  - from bridge_backend.genesis.bus import genesis_bus
  - """Handle incoming events from Genesis Bus"""


### ./bridge_backend/bridge_core/engines/hxo/startup.py
  - import logging
  - import os
  - from bridge_core.engines.hxo import initialize_nexus
  - from bridge_core.engines.hxo.hypshard import HypShardV3Manager


### ./bridge_backend/bridge_core/engines/hxo/security.py
  - import logging
  - import hashlib
  - import secrets
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, UTC
  - import os


### ./bridge_backend/bridge_core/engines/hxo/__init__.py
  - from __future__ import annotations
  - import logging
  - from .nexus import HXONexus, get_nexus_instance, initialize_nexus
  - from .hypshard import HypShardV3Manager
  - from .security import QuantumEntropyHasher, HarmonicConsensusProtocol
  - from ..adapters.chimera_genesis_link import register_with_retry
  - from ..umbra.lattice import fallback_neural_channel


### ./bridge_backend/bridge_core/engines/hxo/hypshard.py
  - import logging
  - from typing import Dict, Any, List, Optional, Set
  - from datetime import datetime, UTC
  - import asyncio
  - import os
  - # Policies from specification


### ./bridge_backend/bridge_core/engines/hxo/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from typing import Dict, Any, List
  - import logging
  - from .nexus import get_nexus_instance, initialize_nexus
  - from .hypshard import HypShardV3Manager
  - from .security import SecurityLayerManager
  - import json
  - from pathlib import Path


### ./bridge_backend/bridge_core/engines/screen/service.py
  - from __future__ import annotations
  - from pathlib import Path
  - from dataclasses import dataclass, asdict
  - from typing import Dict, Any, Optional, List
  - from datetime import datetime, timezone
  - import uuid, json


### ./bridge_backend/bridge_core/engines/screen/__init__.py
  - from .service import ScreenEngine


### ./bridge_backend/bridge_core/engines/screen/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel, Field
  - from typing import Dict, Any, List, Optional
  - from .service import ScreenEngine


### ./bridge_backend/bridge_core/engines/cascade/service.py
  - from __future__ import annotations
  - import json
  - from pathlib import Path
  - from datetime import datetime, timezone
  - from typing import Dict, Any, Optional
  - # Build current state from patch
  - # Include any additional fields from the patch


### ./bridge_backend/bridge_core/engines/cascade/__init__.py


### ./bridge_backend/bridge_core/engines/cascade/routes.py
  - from fastapi import APIRouter, Body
  - from .service import CascadeEngine


### ./bridge_backend/bridge_core/engines/truth/finder.py
  - from __future__ import annotations
  - from typing import List, Dict, Any, Optional
  - from .utils import (
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/truth/utils.py
  - from __future__ import annotations
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import json, hashlib, re
  - from typing import Iterable, List, Dict, Any, Optional, Tuple


### ./bridge_backend/bridge_core/engines/truth/binder.py
  - from __future__ import annotations
  - from typing import List, Dict, Any
  - from .utils import TRUTH_DIR, now_iso, jaccard, norm_for_compare, write_jsonl, sha256_text
  - Input format (from finder): {id, fact, sources:[{sha,ts,source}]}


### ./bridge_backend/bridge_core/engines/truth/__init__.py


### ./bridge_backend/bridge_core/engines/truth/citer.py
  - from __future__ import annotations
  - from typing import Dict, Any, List
  - from .utils import read_jsonl, TRUTH_DIR, norm_for_compare, sha256_text
  - import json
  - from .utils import jaccard


### ./bridge_backend/bridge_core/engines/truth/routes.py
  - from __future__ import annotations
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel, Field
  - from typing import List, Optional, Any, Dict
  - from .finder import find_candidates
  - from .binder import bind_candidates, list_truths
  - from .citer import cite
  - from .utils import TRUTH_DIR, now_iso


### ./bridge_backend/bridge_core/engines/parser/service.py
  - from __future__ import annotations
  - from pathlib import Path
  - from dataclasses import dataclass, asdict
  - from typing import List, Dict, Any, Optional
  - from datetime import datetime, timezone
  - import hashlib, json, re
  - # ---------- 5b (existing) helpers (summarized; call these from routes) ----------


### ./bridge_backend/bridge_core/engines/parser/__init__.py
  - from .service import ParserEngine


### ./bridge_backend/bridge_core/engines/parser/routes.py
  - from fastapi import APIRouter, HTTPException, Body, Query
  - from pydantic import BaseModel
  - from typing import List, Optional
  - from .service import ParserEngine


### ./bridge_backend/bridge_core/engines/agents_foundry/service.py
  - from __future__ import annotations
  - from dataclasses import dataclass, asdict
  - from typing import Dict, Any, Optional, List
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import json, uuid


### ./bridge_backend/bridge_core/engines/agents_foundry/__init__.py
  - from .service import AgentsFoundry


### ./bridge_backend/bridge_core/engines/agents_foundry/routes.py
  - from fastapi import APIRouter, HTTPException, Body, Query
  - from pydantic import BaseModel, Field
  - from typing import Optional, List, Dict
  - from .service import AgentsFoundry


### ./bridge_backend/bridge_core/engines/umbra/autoheal_link.py
  - import time
  - import logging


### ./bridge_backend/bridge_core/engines/umbra/storage.py
  - import sqlite3
  - import logging
  - import json
  - from pathlib import Path
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, timezone, timedelta
  - import asyncio
  - from .models import LatticeNode, LatticeEdge, LatticeSnapshot
  - Query nodes from the lattice
  - Query edges from the lattice


### ./bridge_backend/bridge_core/engines/umbra/lattice.py
  - Graph-based memory system that learns from system changes
  - import logging
  - import os
  - from datetime import datetime, timezone, timedelta
  - from typing import Dict, Any, Optional, List
  - import re
  - from .models import LatticeNode, LatticeEdge, LatticeSnapshot, NodeKind, EdgeKind
  - from .storage import LatticeStorage
  - evt: Event data from Genesis or other sources
  - # Request certification from Truth engine
  - """Build causal chains from edges"""


### ./bridge_backend/bridge_core/engines/umbra/memory.py
  - from __future__ import annotations
  - import logging
  - import os
  - import json
  - from datetime import datetime, timezone
  - from typing import Dict, Any, Optional, List
  - from pathlib import Path
  - Stores repair sequences, learns from patterns, and provides recall capabilities
  - """Load memory from persistent storage"""
  - logger.info(f"🧠 Loaded {len(self.experiences)} experiences from memory")
  - Recall experiences from memory
  - Learn patterns from stored experiences
  - logger.info(f"🧠 Learned {len(patterns)} patterns from {len(relevant)} experiences")


### ./bridge_backend/bridge_core/engines/umbra/echo.py
  - from __future__ import annotations
  - import logging
  - import os
  - import hashlib
  - from datetime import datetime, timezone
  - from typing import Dict, Any, Optional, List
  - from pathlib import Path
  - Detect affected subsystems from file path
  - f"learned from {len(entries)} changes")


### ./bridge_backend/bridge_core/engines/umbra/predictive.py
  - from __future__ import annotations
  - import logging
  - import os
  - from datetime import datetime, timezone
  - from typing import Dict, Any, Optional, List
  - Predict potential issues from current telemetry
  - # Learn from past patterns
  - # Generate repair plan from prediction


### ./bridge_backend/bridge_core/engines/umbra/core.py
  - from __future__ import annotations
  - import logging
  - import os
  - from datetime import datetime, timezone
  - from typing import Dict, Any, Optional, List
  - from pathlib import Path
  - Detect anomalies from telemetry data
  - anomaly: Anomaly data from detection


### ./bridge_backend/bridge_core/engines/umbra/__init__.py
  - from .core import UmbraCore
  - from .memory import UmbraMemory
  - from .predictive import UmbraPredictive
  - from .echo import UmbraEcho
  - from .lattice import UmbraLattice


### ./bridge_backend/bridge_core/engines/umbra/models.py
  - from pydantic import BaseModel, Field
  - from typing import Dict, List, Literal, Optional, Any, Union
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/umbra/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from pydantic import BaseModel
  - from typing import Dict, Any, Optional, List
  - import logging
  - from .core import UmbraCore
  - from .memory import UmbraMemory
  - from .predictive import UmbraPredictive
  - from .echo import UmbraEcho
  - from .lattice import UmbraLattice
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.chronicleloom import ChronicleLoom
  - from genesis.bus import genesis_bus
  - from bridge_core.engines.chronicleloom import ChronicleLoom
  - Detect anomalies from telemetry data
  - Recall experiences from Umbra Memory
  - Learn patterns from stored experiences
  - Predict potential issues from telemetry


### ./bridge_backend/bridge_core/engines/autonomy/service.py
  - from __future__ import annotations
  - import json, uuid, time, os
  - from pathlib import Path
  - from typing import Dict, Any, Optional, List
  - from dataclasses import dataclass, asdict, field
  - from datetime import datetime, timezone
  - from bridge_backend.utils.license_scanner import scan_files
  - from bridge_backend.utils.counterfeit_detector import best_match_against_corpus
  - from bridge_backend.utils.scan_policy import load_policy
  - from utils.license_scanner import scan_files
  - from utils.counterfeit_detector import best_match_against_corpus
  - from utils.scan_policy import load_policy


### ./bridge_backend/bridge_core/engines/autonomy/__init__.py
  - from .service import AutonomyEngine


### ./bridge_backend/bridge_core/engines/autonomy/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from typing import Optional, List
  - from .service import AutonomyEngine
  - from bridge_backend.genesis.bus import genesis_bus
  - from datetime import datetime, UTC
  - """Get deployment monitoring status from autonomy engine"""
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/envsync/types.py
  - from typing import Dict, List, Optional, Literal, TypedDict


### ./bridge_backend/bridge_core/engines/envsync/tasks.py
  - import asyncio, logging
  - from .config import CONFIG
  - from .engine import sync_provider


### ./bridge_backend/bridge_core/engines/envsync/telemetry.py
  - import json, logging, datetime as dt


### ./bridge_backend/bridge_core/engines/envsync/diffs.py
  - from typing import Dict, List
  - from .types import DiffEntry


### ./bridge_backend/bridge_core/engines/envsync/config.py
  - import os
  - from dataclasses import dataclass
  - from typing import List


### ./bridge_backend/bridge_core/engines/envsync/engine.py
  - import os
  - import logging
  - from pathlib import Path
  - from typing import Dict, List
  - from .config import CONFIG
  - from .types import SyncResult, Mode
  - # from .providers.render import RenderProvider
  - from .providers.netlify import NetlifyProvider
  - from .providers.base import ProviderBase
  - from .diffs import compute_diff
  - from .telemetry import ticket
  - Load canonical environment variables from the EnvSync Seed Manifest.
  - logger.info(f"✅ Loaded {len(canonical)} variables from EnvSync Seed Manifest")
  - 1. 'file' - Load from EnvSync Seed Manifest
  - 2. 'vault' - Load from Bridge Vault (future enhancement)
  - 3. 'env' - Load from current environment variables
  - # Load from seed manifest file
  - from bridge_backend.bridge_core.engines.adapters.envsync_autonomy_link import envsync_autonomy_link


### ./bridge_backend/bridge_core/engines/envsync/__init__.py
  - from .routes import router as envsync_router


### ./bridge_backend/bridge_core/engines/envsync/routes.py
  - from fastapi import APIRouter
  - from typing import Dict
  - from .engine import sync_provider
  - from .config import CONFIG


### ./bridge_backend/bridge_core/engines/envsync/discovery/sources.py
  - import os, pathlib, httpx
  - from typing import Optional, List
  - from ..config import CONFIG


### ./bridge_backend/bridge_core/engines/envsync/discovery/chain.py
  - from typing import Optional
  - from . import sources
  - from ..config import CONFIG


### ./bridge_backend/bridge_core/engines/envsync/discovery/__init__.py


### ./bridge_backend/bridge_core/engines/envsync/providers/__init__.py


### ./bridge_backend/bridge_core/engines/envsync/providers/netlify.py
  - import os, httpx
  - from typing import Dict, List
  - from .base import ProviderBase
  - from ..discovery.chain import discover_token


### ./bridge_backend/bridge_core/engines/envsync/providers/base.py
  - from typing import Dict, List
  - from ..types import DiffEntry


### ./bridge_backend/bridge_core/engines/adapters/autonomy_genesis_link.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.autonomy.governor import AutonomyGovernor
  - from bridge_backend.engines.autonomy.models import Incident
  - # Auto-register on import if enabled
  - import os


### ./bridge_backend/bridge_core/engines/adapters/hxo_autonomy_link.py
  - from __future__ import annotations
  - import logging
  - from ...utils.async_tools import maybe_await
  - Notify Autonomy of auto-tune signals from HXO.
  - from datetime import datetime, UTC
  - from bridge_backend.genesis.bus import genesis_bus
  - Request healing from Autonomy for a failed stage.
  - from datetime import datetime, UTC
  - from bridge_backend.genesis.bus import genesis_bus
  - Apply tuning recommendation from Autonomy.


### ./bridge_backend/bridge_core/engines/adapters/umbra_truth_link.py
  - import logging
  - from typing import Dict, Any
  - from datetime import datetime, UTC
  - from bridge_backend.bridge_core.engines.truth.service import TruthEngine
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/hxo_parser_link.py
  - import logging
  - from typing import Dict, Any, List, Optional
  - import uuid


### ./bridge_backend/bridge_core/engines/adapters/arie_schedule_link.py
  - import os
  - import logging
  - from typing import Dict, Any
  - from datetime import datetime, UTC


### ./bridge_backend/bridge_core/engines/adapters/hxo_blueprint_link.py
  - import logging
  - from typing import Dict, Any, Optional
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/envrecon_autonomy_link.py
  - import asyncio
  - import logging
  - from typing import Dict, Any, Optional
  - from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - heal_result: Result from auto-heal operation
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - event: Deployment success event from Genesis bus
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - from bridge_backend.engines.envrecon.autoheal import autoheal


### ./bridge_backend/bridge_core/engines/adapters/hxo_nexus_integration.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.bridge_core.engines.hxo import get_nexus_instance
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.autonomy.service import AutonomyEngine
  - from bridge_backend.bridge_core.engines.hxo import get_nexus_instance
  - from bridge_backend.bridge_core.engines.adapters.hxo_genesis_link import (
  - from bridge_backend.bridge_core.engines.adapters.hxo_autonomy_link import (


### ./bridge_backend/bridge_core/engines/adapters/umbra_parity_link.py
  - import logging
  - from typing import Dict, Any, List
  - from bridge_backend.engines.envrecon.parity import check_parity as parity_check
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/arie_blueprint_link.py
  - import logging
  - from typing import Dict, Any
  - Record structural changes from ARIE fixes to Blueprint
  - """Extract module-level changes from summary"""
  - # Determine module from file path


### ./bridge_backend/bridge_core/engines/adapters/tools_runtime_autonomy_link.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.genesis.bus import genesis_bus
  - Utility function to publish health events from any component.
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/adapters/heritage_mas_autonomy_link.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.genesis.bus import genesis_bus
  - Utility function to publish MAS events from any agent.
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/engines/adapters/arie_cascade_link.py
  - import logging
  - from typing import Dict, Any


### ./bridge_backend/bridge_core/engines/adapters/hxo_federation_link.py
  - import logging
  - from typing import Dict, Any, Optional
  - import asyncio
  - # Try to import federation client
  - from bridge_backend.bridge_core.federation_client import FederationClient


### ./bridge_backend/bridge_core/engines/adapters/umbra_cascade_link.py
  - import logging
  - from typing import Dict, Any
  - from datetime import datetime, UTC
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/genesis_link.py
  - from typing import Dict, Any
  - import logging
  - from ...utils.async_tools import maybe_await
  - from .hxo_genesis_link import HXOGenesisLink
  - from .hxo_autonomy_link import HXOAutonomyLink
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.manifest import genesis_manifest
  - from bridge_backend.genesis.introspection import genesis_introspection
  - # Sync manifest from Blueprint Registry first
  - from .super_engines_autonomy_link import register_super_engines_autonomy_links
  - from .tools_runtime_autonomy_link import register_tools_runtime_autonomy_links
  - from .heritage_mas_autonomy_link import register_heritage_mas_autonomy_links
  - from .hxo_genesis_link import register_hxo_genesis_link
  - from .envrecon_autonomy_link import envrecon_autonomy_link
  - from .chimera_genesis_link import register
  - from .umbra_genesis_link import subscribe_umbra_to_genesis
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - import os
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.arie.core import ARIEEngine
  - from .arie_genesis_link import ARIEGenesisLink
  - from .arie_schedule_link import ARIEScheduleLink
  - from bridge_backend.engines.arie.scheduler import ARIEScheduler


### ./bridge_backend/bridge_core/engines/adapters/super_engines_autonomy_link.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/hxo_genesis_link.py
  - from __future__ import annotations
  - import logging
  - from typing import Optional
  - from ...utils.async_tools import maybe_await, retry_async
  - from bridge_backend.genesis.bus import genesis_bus
  - """Handle healing requests from Autonomy"""
  - logger.info("[HXO Genesis Link] Received autotune intent from Autonomy")
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/arie_truth_link.py
  - import logging
  - from typing import Dict, Any, Optional
  - import hashlib
  - from pathlib import Path
  - # Request certification from Truth Engine
  - """Request verification from Truth Engine"""


### ./bridge_backend/bridge_core/engines/adapters/umbra_genesis_link.py
  - import logging
  - from typing import Dict, Any
  - from datetime import datetime, UTC
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.umbra.core import UmbraTriageCore
  - "message": f"Heal request from {event.get('subsystem', 'unknown')}",
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
  - # Netlify topics (from engines)
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/hxo_permission_link.py
  - import logging
  - from typing import Dict, Any, Optional
  - from bridge_backend.genesis.bus import genesis_bus
  - from datetime import datetime, UTC


### ./bridge_backend/bridge_core/engines/adapters/arie_genesis_link.py
  - import os
  - import logging
  - from typing import Dict, Any, Optional
  - from datetime import datetime, UTC
  - from bridge_backend.engines.arie.models import PolicyType
  - """Handle heal request from Genesis"""
  - from bridge_backend.engines.arie.models import PolicyType
  - from pathlib import Path
  - import json


### ./bridge_backend/bridge_core/engines/adapters/umbra_blueprint_link.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.bridge_core.engines.blueprint.service import BlueprintEngine
  - from bridge_backend.bridge_core.engines.blueprint.service import BlueprintEngine
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/hxo_truth_link.py
  - import logging
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, UTC
  - from bridge_backend.genesis.bus import genesis_bus
  - Handle certification failure from Truth engine.
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/umbra_autonomy_link.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.engines.autonomy.core import AutonomyEngine
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/engines/adapters/__init__.py
  - from .genesis_link import register_all_genesis_links


### ./bridge_backend/bridge_core/engines/adapters/arie_permission_link.py
  - import logging
  - from typing import Optional


### ./bridge_backend/bridge_core/engines/adapters/envsync_autonomy_link.py
  - import asyncio
  - import logging
  - from typing import Dict, Any, Optional
  - from bridge_backend.bridge_core.engines.autonomy.orchestrator import autonomy_orchestrator
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.autonomy.orchestrator import autonomy_orchestrator
  - Handle secret rotation events from Autonomy
  - from bridge_backend.bridge_core.engines.envsync.tasks import run_scheduled_sync


### ./bridge_backend/bridge_core/engines/adapters/chimera_genesis_link.py
  - from __future__ import annotations
  - import logging
  - import time
  - from pathlib import Path
  - from typing import Optional
  - Load Genesis bus module with normalized import path.
  - from ...paths import import_genesis_bus
  - logger.error(f"[Chimera↔Genesis] import bus failed: {e}")
  - from ...paths import import_genesis_bus
  - from ...engines.chimera.core import ChimeraEngine


### ./bridge_backend/bridge_core/engines/indoctrination/service.py
  - from pathlib import Path
  - import json, uuid, logging
  - from datetime import datetime, timezone
  - from typing import Dict, Any, List
  - """Load all agents from vault directory into registry on startup."""
  - logger.info(f"Loaded {len(self.registry)} agents from vault")


### ./bridge_backend/bridge_core/engines/indoctrination/__init__.py
  - from .service import IndoctrinationEngine


### ./bridge_backend/bridge_core/engines/indoctrination/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from typing import List
  - from .service import IndoctrinationEngine


### ./bridge_backend/bridge_core/custody/__init__.py


### ./bridge_backend/bridge_core/custody/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from nacl.signing import SigningKey, VerifyKey
  - import base64
  - from datetime import datetime, timezone


### ./bridge_backend/bridge_core/payments/stripe_webhooks.py
  - from fastapi import APIRouter, Request, HTTPException
  - from typing import Dict, Any, Optional
  - import stripe
  - import os
  - from bridge_core.engines.cascade.service import CascadeEngine
  - from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine


### ./bridge_backend/bridge_core/payments/__init__.py


### ./bridge_backend/bridge_core/fleet/__init__.py


### ./bridge_backend/bridge_core/fleet/routes.py
  - from fastapi import APIRouter, Query
  - # Mock data - in production this would come from database


### ./bridge_backend/bridge_core/protocols/storage.py
  - from pathlib import Path
  - import json
  - from typing import Dict
  - from bridge_core.protocols.registry import ProtocolEntry, _registry
  - from bridge_core.protocols.vaulting import get_vault_dir
  - from bridge_backend.bridge_core.protocols.registry import ProtocolEntry, _registry
  - from bridge_backend.bridge_core.protocols.vaulting import get_vault_dir


### ./bridge_backend/bridge_core/protocols/vaulting.py
  - import os
  - import json
  - from datetime import datetime, timezone
  - from pathlib import Path
  - from typing import Dict, Any, Optional


### ./bridge_backend/bridge_core/protocols/complex_routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from .registry import list_registry, get_entry


### ./bridge_backend/bridge_core/protocols/invoke.py
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import json
  - from .registry import get_entry


### ./bridge_backend/bridge_core/protocols/registry.py
  - from __future__ import annotations
  - from pathlib import Path
  - from typing import Dict, Callable, Awaitable, Optional
  - import yaml  # type: ignore
  - from .vaulting import seal as vault_seal


### ./bridge_backend/bridge_core/protocols/__init__.py


### ./bridge_backend/bridge_core/protocols/models.py
  - from pydantic import BaseModel
  - from typing import List, Optional


### ./bridge_backend/bridge_core/protocols/routes.py
  - from fastapi import APIRouter, HTTPException
  - from bridge_core.protocols.registry import (
  - from bridge_core.protocols import storage
  - from bridge_backend.bridge_core.protocols.registry import (
  - from bridge_backend.bridge_core.protocols import storage


### ./bridge_backend/bridge_core/registry/agents_registry.py
  - from __future__ import annotations
  - from pathlib import Path
  - import json
  - from typing import Dict, List, Any, Optional
  - from bridge_core.engines.indoctrination.service import IndoctrinationEngine
  - from bridge_core.engines.agents_foundry.service import AgentsFoundry
  - from bridge_backend.bridge_core.engines.indoctrination.service import IndoctrinationEngine
  - from bridge_backend.bridge_core.engines.agents_foundry.service import AgentsFoundry


### ./bridge_backend/bridge_core/registry/__init__.py
  - from .agents_registry import AgentRegistry


### ./bridge_backend/bridge_core/registry/routes.py
  - from fastapi import APIRouter, HTTPException, Query, Depends
  - from .agents_registry import AgentRegistry
  - from bridge_core.engines.cascade.service import CascadeEngine
  - from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine
  - """Mock user authentication - returns user ID from query param"""


### ./bridge_backend/bridge_core/auth/__init__.py
  - from .routes import auth_bp, init_auth_routes


### ./bridge_backend/bridge_core/auth/routes.py
  - from flask import Blueprint, request, jsonify
  - from ...src.keyless_auth import get_keyless_handler
  - # Fallback if relative import fails (e.g., when running standalone)
  - from bridge_backend.src.keyless_auth import get_keyless_handler


### ./bridge_backend/bridge_core/guards/netlify_guard.py
  - import os
  - import logging
  - from pathlib import Path


### ./bridge_backend/bridge_core/guards/__init__.py


### ./bridge_backend/bridge_core/guards/routes.py
  - import os
  - import logging
  - from fastapi import APIRouter
  - from pathlib import Path
  - from bridge_backend.genesis.bus import GenesisEventBus


### ./bridge_backend/bridge_core/integrity/core.py
  - import logging


### ./bridge_backend/bridge_core/integrity/__init__.py


### ./bridge_backend/bridge_core/integrity/deferred.py
  - import os
  - import time
  - import logging


### ./bridge_backend/bridge_core/scans/service.py
  - import json, hashlib, os
  - from datetime import datetime, timezone
  - from pathlib import Path
  - from typing import Dict, List, Tuple
  - from utils.license_scanner import scan_files
  - from utils.counterfeit_detector import best_match_against_corpus
  - from utils.scan_policy import load_policy
  - from utils.signing import sign_payload
  - from bridge_backend.utils.license_scanner import scan_files
  - from bridge_backend.utils.counterfeit_detector import best_match_against_corpus
  - from bridge_backend.utils.scan_policy import load_policy
  - from bridge_backend.utils.signing import sign_payload


### ./bridge_backend/bridge_core/scans/__init__.py


### ./bridge_backend/bridge_core/scans/models.py
  - from pydantic import BaseModel, Field
  - from typing import List, Dict, Optional


### ./bridge_backend/bridge_core/scans/routes.py
  - from fastapi import APIRouter, HTTPException, Query
  - from typing import List, Optional
  - from .service import list_scans, read_scan


### ./bridge_backend/bridge_core/core/event_bus.py
  - from ..heritage.event_bus import bus


### ./bridge_backend/bridge_core/core/event_models.py
  - from typing import Dict, Any, Optional
  - from pydantic import BaseModel
  - from datetime import datetime


### ./bridge_backend/bridge_core/core/__init__.py
  - from .event_bus import bus
  - from .event_models import (


### ./bridge_backend/bridge_core/agents/__init__.py


### ./bridge_backend/bridge_core/agents/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from bridge_core.protocols.registry import list_registry, get_entry, activate_protocol, vault_protocol
  - from bridge_backend.bridge_core.protocols.registry import list_registry, get_entry, activate_protocol, vault_protocol


### ./bridge_backend/bridge_core/agents/git_sovereign/manifest.py
  - from typing import Dict, List, Any
  - from dataclasses import dataclass, field
  - from datetime import datetime


### ./bridge_backend/bridge_core/agents/git_sovereign/brh_integration.py
  - from typing import Dict, List, Optional, Any
  - from datetime import datetime
  - import asyncio


### ./bridge_backend/bridge_core/agents/git_sovereign/autonomy.py
  - from typing import Dict, List, Optional, Any
  - from datetime import datetime
  - from enum import Enum
  - from_scratch: Whether to start from cosmic scratch


### ./bridge_backend/bridge_core/agents/git_sovereign/hxo_integration.py
  - from typing import Dict, List, Optional, Any, Set
  - from datetime import datetime


### ./bridge_backend/bridge_core/agents/git_sovereign/sdtf_integration.py
  - import os
  - import base64
  - import secrets
  - import hmac
  - import hashlib
  - from typing import Dict, Optional, Any
  - from datetime import datetime, timedelta


### ./bridge_backend/bridge_core/agents/git_sovereign/__init__.py
  - from .manifest import GitSovereignManifest, COSMIC_PARAMETERS
  - from .sdtf_integration import SDTFGitIntegration
  - from .brh_integration import BRHGitIntegration
  - from .hxo_integration import HXOGitIntegration
  - from .autonomy import AutonomousOperations


### ./bridge_backend/bridge_core/heritage/event_bus.py
  - from typing import Callable, Dict, Any, DefaultDict, List
  - from collections import defaultdict
  - import asyncio
  - import logging


### ./bridge_backend/bridge_core/heritage/__init__.py
  - from .event_bus import bus


### ./bridge_backend/bridge_core/heritage/routes.py
  - from fastapi import APIRouter, HTTPException, WebSocket
  - from .demos.shakedown import run_shakedown
  - from .demos.mas_demo import run_mas
  - from .demos.federation_demo import run_federation
  - from .federation.live_ws import websocket_endpoint


### ./bridge_backend/bridge_core/heritage/federation/live_ws.py
  - import logging
  - from typing import Set
  - from fastapi import WebSocket, WebSocketDisconnect
  - from datetime import datetime, timezone
  - from ..event_bus import bus
  - # Receive messages from client
  - import asyncio


### ./bridge_backend/bridge_core/heritage/federation/federation_client.py
  - import logging
  - from typing import Dict, Any, List
  - from datetime import datetime, timezone
  - from ..event_bus import bus
  - from bridge_backend.genesis.bus import genesis_bus
  - logger.debug(f"💓 Heartbeat sent from {self.node_id}")
  - from bridge_backend.genesis.bus import genesis_bus
  - """Handle acknowledgment from another node"""
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/bridge_core/heritage/federation/__init__.py


### ./bridge_backend/bridge_core/heritage/mas/adapters.py
  - import logging
  - from typing import Dict, Any, Callable
  - from datetime import datetime, timezone
  - from ..event_bus import bus


### ./bridge_backend/bridge_core/heritage/mas/fault_injector.py
  - import random
  - import logging
  - from typing import Dict, Any, Callable
  - from datetime import datetime, timezone
  - from ..event_bus import bus


### ./bridge_backend/bridge_core/heritage/mas/__init__.py


### ./bridge_backend/bridge_core/heritage/agents/profiles.py
  - from typing import Dict, Any, List
  - from dataclasses import dataclass


### ./bridge_backend/bridge_core/heritage/agents/legacy_agents.py
  - import logging
  - from typing import Dict, Any
  - from datetime import datetime, timezone
  - from ..event_bus import bus
  - from .profiles import PRIM_PROFILE, CLAUDE_PROFILE


### ./bridge_backend/bridge_core/heritage/agents/__init__.py


### ./bridge_backend/bridge_core/heritage/demos/mas_demo.py
  - import logging
  - import asyncio
  - from datetime import datetime, timezone
  - from ..event_bus import bus
  - from ..mas.adapters import BridgeMASAdapter, SelfHealingMASAdapter
  - from ..mas.fault_injector import FaultInjector


### ./bridge_backend/bridge_core/heritage/demos/__init__.py


### ./bridge_backend/bridge_core/heritage/demos/federation_demo.py
  - import logging
  - import asyncio
  - from datetime import datetime, timezone
  - from ..event_bus import bus
  - from ..federation.federation_client import FederationClient


### ./bridge_backend/bridge_core/heritage/demos/shakedown.py
  - import logging
  - import asyncio
  - from datetime import datetime, timezone
  - from ..event_bus import bus


### ./bridge_backend/bridge_core/missions/__init__.py


### ./bridge_backend/bridge_core/missions/routes.py
  - from fastapi import APIRouter, HTTPException, Query, Request, Depends
  - from pydantic import BaseModel
  - from pathlib import Path
  - from datetime import datetime, timezone
  - from sqlalchemy.ext.asyncio import AsyncSession
  - from sqlalchemy import select
  - from typing import List, Annotated
  - import json
  - import uuid
  - import os
  - from bridge_backend.bridge_core.db.db_manager import get_db_session
  - from bridge_backend.models import AgentJob, Mission
  - from bridge_backend.schemas import AgentJobOut
  - from ...db.db_manager import get_db_session
  - from ....models import AgentJob, Mission
  - from ....schemas import AgentJobOut
  - # Get captain from request or use provided captain
  - import tempfile
  - import shutil


### ./bridge_backend/bridge_core/permissions/store.py
  - from __future__ import annotations
  - from pathlib import Path
  - from datetime import datetime, timezone
  - import json
  - from typing import Optional
  - from .models import PermissionSettings


### ./bridge_backend/bridge_core/permissions/presets.py
  - from .models import PermissionSettings, AutonomySettings, LocationSettings, ScreenSettings, VoiceSettings, DataSettings, LoggingSettings, PushSettings


### ./bridge_backend/bridge_core/permissions/service.py
  - from enum import Enum
  - from typing import Dict, Any


### ./bridge_backend/bridge_core/permissions/__init__.py


### ./bridge_backend/bridge_core/permissions/models.py
  - from __future__ import annotations
  - from pydantic import BaseModel, Field
  - from typing import List, Optional, Dict, Literal


### ./bridge_backend/bridge_core/permissions/routes.py
  - from fastapi import APIRouter, HTTPException, Body, Query
  - from pydantic import BaseModel
  - from typing import Optional
  - from .service import Tier, get_rules
  - from .models import PermissionSettings
  - from .presets import preset_for_tier
  - from .store import load_settings, save_settings, append_consent_log


### ./bridge_backend/bridge_core/console/routes.py
  - from fastapi import APIRouter
  - from datetime import datetime, timezone
  - from bridge_core.protocols.registry import list_registry
  - from bridge_core.guardians.routes import GUARDIANS
  - from bridge_backend.bridge_core.protocols.registry import list_registry
  - from bridge_backend.bridge_core.guardians.routes import GUARDIANS


### ./bridge_backend/bridge_core/activity/__init__.py


### ./bridge_backend/bridge_core/activity/routes.py
  - from fastapi import APIRouter
  - from pathlib import Path
  - import json


### ./bridge_backend/bridge_core/token_forge_dominion/bootstrap.py
  - import os
  - import sys
  - from typing import Tuple
  - from .quantum_authority import generate_root_key
  - from .secret_forge import retrieve_environment
  - print('  gh secret set FORGE_DOMINION_ROOT --body "$(python - <<\'PY\'\nimport base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip("="))\nPY\n)"')


### ./bridge_backend/bridge_core/token_forge_dominion/secret_forge.py
  - import os
  - import hmac
  - import hashlib
  - import time
  - import json
  - import base64
  - import logging
  - from typing import Optional, Dict, Any, List
  - from datetime import datetime, timedelta
  - Secret value from environment or default
  - # Retrieve from environment
  - Extract metadata from a token.
  - Extract metadata from a token.


### ./bridge_backend/bridge_core/token_forge_dominion/sovereign_integration.py
  - import os
  - import json
  - from typing import Dict, Optional, Any, Tuple
  - from datetime import datetime, timedelta
  - from pathlib import Path
  - from .secret_forge import retrieve_environment
  - # Fallback if secret_forge not yet available (circular import handling)
  - """Load sovereign policies from configuration."""
  - # Override from environment if specified
  - # Try to get resonance from bridge state


### ./bridge_backend/bridge_core/token_forge_dominion/quantum_scanner.py
  - import os
  - import re
  - from pathlib import Path
  - from typing import Dict, List, Optional, Any, Set
  - from datetime import datetime
  - from .zero_trust_validator import ZeroTrustValidator
  - # Paths to exclude from scanning
  - # Note: 'tests' excluded by default to avoid false positives from test fixtures
  - "details": "Prevent secrets from being committed"


### ./bridge_backend/bridge_core/token_forge_dominion/scan_envs.py
  - import os
  - import re
  - from pathlib import Path
  - from typing import List, Dict, Any
  - print("1. Remove plaintext secrets from .env files")
  - import sys


### ./bridge_backend/bridge_core/token_forge_dominion/validate_or_renew.py
  - import os
  - import json
  - from datetime import datetime, timezone
  - from typing import Dict, Optional, Any, Tuple, List
  - from pathlib import Path
  - from .quantum_authority import QuantumAuthority
  - from .sovereign_integration import SovereignIntegration
  - """Load token state from file."""
  - token_envelope: Token envelope (if None, loads from state)
  - import sys


### ./bridge_backend/bridge_core/token_forge_dominion/quantum_authority.py
  - import os
  - import hmac
  - import hashlib
  - import secrets
  - import base64
  - import json
  - from datetime import datetime, timedelta
  - from typing import Dict, Optional, Any
  - from cryptography.hazmat.primitives import hashes
  - from cryptography.hazmat.primitives.kdf.hkdf import HKDF
  - from cryptography.hazmat.backends import default_backend
  - from .secret_forge import retrieve_environment
  - root_key: Base64-encoded root key. If None, generates from environment.
  - Get root key from parameter, environment, or generate new one.


### ./bridge_backend/bridge_core/token_forge_dominion/zero_trust_validator.py
  - import os
  - import re
  - import hashlib
  - import math
  - from typing import Dict, List, Optional, Any, Tuple
  - from datetime import datetime
  - from collections import Counter


### ./bridge_backend/bridge_core/token_forge_dominion/enterprise_orchestrator.py
  - import os
  - import json
  - from pathlib import Path
  - from typing import Dict, List, Optional, Any, Tuple
  - from datetime import datetime, timedelta, timezone
  - from .quantum_authority import QuantumAuthority
  - from .zero_trust_validator import ZeroTrustValidator
  - from .sovereign_integration import SovereignIntegration
  - from .quantum_scanner import QuantumScanner


### ./bridge_backend/bridge_core/token_forge_dominion/__init__.py
  - from .quantum_authority import QuantumAuthority, generate_root_key
  - from .zero_trust_validator import ZeroTrustValidator
  - from .sovereign_integration import SovereignIntegration
  - from .quantum_scanner import QuantumScanner
  - from .enterprise_orchestrator import EnterpriseOrchestrator
  - from .validate_or_renew import TokenLifecycleManager, validate_or_renew
  - from .secret_forge import (


### ./bridge_backend/bridge_core/vault/__init__.py


### ./bridge_backend/bridge_core/vault/routes.py
  - from fastapi import APIRouter, HTTPException, Request
  - from pathlib import Path
  - import json
  - import os
  - # You can extend this to read from secure vault storage


### ./bridge_backend/bridge_core/system/__init__.py


### ./bridge_backend/bridge_core/system/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from datetime import datetime, timezone
  - import os
  - import asyncio
  - import sys
  - from pathlib import Path
  - from seed_bootstrap import main as seed_main


### ./bridge_backend/bridge_core/captains/routes.py
  - from fastapi import APIRouter


### ./bridge_backend/utils/signing.py
  - import json, hmac, hashlib, os
  - from typing import Dict, Any


### ./bridge_backend/utils/deployment_publisher.py
  - import asyncio
  - import os
  - import sys
  - from typing import Dict, Any, Optional
  - from datetime import datetime, UTC
  - import logging
  - from bridge_backend.genesis.bus import genesis_bus
  - Useful for calling from non-async contexts like shell scripts.
  - import argparse
  - # Build metadata from arguments


### ./bridge_backend/utils/scan_policy.py
  - import yaml
  - from pathlib import Path
  - from typing import Dict, Any


### ./bridge_backend/utils/counterfeit_detector.py
  - from __future__ import annotations
  - import re, hashlib
  - from pathlib import Path
  - from typing import Dict, List, Tuple


### ./bridge_backend/utils/license_scanner.py
  - from __future__ import annotations
  - import re, hashlib
  - from pathlib import Path
  - from typing import Dict, List, Optional


### ./bridge_backend/utils/relay_mailer.py
  - import os
  - import json
  - import hashlib
  - import smtplib
  - import aiosmtplib
  - from email.mime.text import MIMEText
  - from email.mime.multipart import MIMEMultipart
  - from email.mime.base import MIMEBase
  - from email import encoders
  - from datetime import datetime, timezone
  - from typing import Dict, Any, Optional, List
  - from pathlib import Path
  - queue_file.unlink()  # Remove from queue


### ./bridge_backend/utils/db.py
  - import os
  - import logging
  - from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
  - from sqlalchemy.orm import declarative_base
  - from bridge_backend.models import Base as ModelsBase  # ensure model import


### ./bridge_backend/utils/__init__.py
  - from .relay_mailer import RelayMailer, relay_mailer


### ./bridge_backend/middleware/headers.py
  - import logging
  - from starlette.middleware.base import BaseHTTPMiddleware
  - from starlette.requests import Request
  - import os


### ./bridge_backend/middleware/__init__.py


### ./bridge_backend/engines/netlify_validator.py
  - import subprocess
  - import os
  - import json
  - import logging
  - from typing import Dict, Any, Optional
  - from pathlib import Path
  - from datetime import datetime, timezone
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/engines/netlify_routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from typing import Dict, Any, Optional, List
  - import logging
  - from bridge_backend.engines.netlify_validator import NetlifyValidator
  - # Mock authentication - in production, extract from JWT token
  - from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.chronicleloom import ChronicleLoom
  - from genesis.bus import genesis_bus
  - from bridge_core.engines.umbra.memory import UmbraMemory
  - from bridge_core.engines.chronicleloom import ChronicleLoom


### ./bridge_backend/engines/envrecon/hubsync.py
  - import os
  - import logging
  - import base64
  - from typing import List, Dict, Any, Optional
  - import httpx
  - from nacl import encoding, public


### ./bridge_backend/engines/envrecon/core.py
  - import os
  - import json
  - import logging
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional
  - from pathlib import Path
  - from dotenv import dotenv_values
  - import httpx
  - """Fetch environment variables from Render API"""
  - """Fetch environment variables from Netlify API"""
  - """Load environment variables from local .env files"""
  - logger.info(f"✅ Loaded {len(env_vars)} vars from {env_file}")
  - # Fetch from all sources
  - from bridge_backend.bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link


### ./bridge_backend/engines/envrecon/ui.py
  - from fastapi import APIRouter, Request
  - from fastapi.responses import HTMLResponse
  - import logging


### ./bridge_backend/engines/envrecon/autoheal.py
  - import os
  - import logging
  - from typing import Dict, List, Any, Optional
  - # Try to import Genesis adapters
  - from bridge_backend.genesis.adapters import emit_heal
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/engines/envrecon/__init__.py
  - from .core import EnvReconEngine


### ./bridge_backend/engines/envrecon/routes.py
  - from fastapi import APIRouter, HTTPException
  - from typing import Dict, Any, List
  - import logging
  - from .core import EnvReconEngine
  - from .hubsync import hubsync
  - from .autoheal import autoheal
  - from bridge_backend.bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link


### ./bridge_backend/engines/chimera/planner.py
  - from typing import Dict, Any
  - sim: Simulation results from Leviathan
  - guard: Guard synthesis results from Hydra


### ./bridge_backend/engines/chimera/core.py
  - import os
  - import json
  - import subprocess
  - from pathlib import Path
  - from typing import Dict, List, Any
  - import logging
  - from .preflight.netlify_config import (
  - from .planner import DecisionMatrix
  - from .adapters.leviathan_adapter import LeviathanAdapter
  - from .adapters.truth_adapter import TruthGate
  - from .adapters.arie_adapter import ArieGate
  - from .adapters.env_adapter import EnvSuite
  - from .adapters.github_forge_adapter import GitHubForge
  - from .adapters.netlify_guard_adapter import NetlifyGuard
  - # from .adapters.render_fallback_adapter import RenderFallback
  - from ...genesis.bus import genesis_bus
  - from ...genesis.bus import genesis_bus
  - from ...genesis.bus import genesis_bus
  - from ...genesis.bus import genesis_bus
  - from ...genesis.bus import genesis_bus


### ./bridge_backend/engines/chimera/__init__.py
  - from .core import ChimeraEngine, ChimeraOracle
  - from .models import RedirectRule
  - from .planner import DecisionMatrix


### ./bridge_backend/engines/chimera/models.py
  - from typing import Optional, Dict
  - from pydantic import BaseModel


### ./bridge_backend/engines/chimera/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pathlib import Path
  - from typing import Dict, Any
  - import logging
  - from .core import ChimeraEngine, ChimeraOracle


### ./bridge_backend/engines/chimera/preflight/netlify_config.py
  - from pathlib import Path
  - from typing import List, Dict
  - from ..models import RedirectRule
  - from = "/*"


### ./bridge_backend/engines/chimera/preflight/__init__.py


### ./bridge_backend/engines/chimera/adapters/leviathan_adapter.py
  - from typing import Dict, Any
  - from ...leviathan.simulator import LeviathanSimulator


### ./bridge_backend/engines/chimera/adapters/github_forge_adapter.py
  - from typing import Dict, Any
  - from ...github_forge.core import GitHubForge as GitHubForgeCore
  - """Read JSON from forge"""


### ./bridge_backend/engines/chimera/adapters/netlify_guard_adapter.py
  - from typing import Dict, Any
  - from ...hydra.guard import HydraGuard


### ./bridge_backend/engines/chimera/adapters/env_adapter.py
  - from typing import Dict, Any


### ./bridge_backend/engines/chimera/adapters/arie_adapter.py
  - from typing import Dict, Any


### ./bridge_backend/engines/chimera/adapters/truth_adapter.py
  - from typing import Dict, Any


### ./bridge_backend/engines/leviathan/simulator.py
  - from typing import Dict, Any


### ./bridge_backend/engines/leviathan/__init__.py
  - from .simulator import LeviathanSimulator


### ./bridge_backend/engines/forge/core.py
  - import os
  - import logging
  - import subprocess
  - from typing import Dict, Any, List, Optional
  - from pathlib import Path
  - from datetime import datetime, UTC
  - from = "/api/*"
  - from = "/*"
  - """Create .env from .env.example"""
  - logger.info("🛠️ Forge: Created .env from template")
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.chimera.adapters.truth_adapter import TruthGate
  - import asyncio
  - import asyncio
  - import sys


### ./bridge_backend/engines/forge/__init__.py
  - from .core import run_full_repair, ForgeEngine


### ./bridge_backend/engines/arie/scheduler.py
  - import asyncio
  - import os
  - import logging
  - import json
  - from datetime import datetime, UTC
  - from pathlib import Path
  - from typing import Optional
  - from bridge_backend.engines.arie.models import PolicyType


### ./bridge_backend/engines/arie/core.py
  - import os
  - import re
  - import json
  - import hashlib
  - import subprocess
  - from pathlib import Path
  - from typing import List, Dict, Any, Optional, Tuple
  - from datetime import datetime, UTC
  - from abc import ABC, abstractmethod
  - from .models import (
  - """Validates route import and registration integrity"""
  - has_router_import = False
  - if 'from fastapi import' in line and 'APIRouter' in line:
  - has_router_import = True
  - if has_router_import and not has_include_router and file_path.name == 'main.py':
  - """Checks for missing or relocated import symbols"""
  - # Check for common import issues
  - if line.strip().startswith('import ') or line.strip().startswith('from '):
  - if 'from .' in line and '..' in line:
  - description=f"Overly nested relative import ({dots} levels) at line {i}",
  - if line.strip().startswith('import ') or line.strip().startswith('from '):
  - # Check if this import is used elsewhere in the file
  - if content.count(imp_name) == 1:  # Only appears in import line
  - suggested_fix=f"Remove unused import {imp_name}"
  - if 'from datetime import' in modified:
  - if ', UTC' not in modified and 'import UTC' not in modified:
  - 'from datetime import datetime',
  - 'from datetime import datetime, UTC'
  - """Fixes import alias issues"""
  - """Load configuration from environment"""
  - """Create execution plan from findings"""
  - import time
  - import logging
  - from pathlib import Path
  - from ..chimera.core import ChimeraEngine
  - import subprocess


### ./bridge_backend/engines/arie/__init__.py
  - from .core import ARIEEngine
  - from .models import Finding, Plan, Patch, Rollback, Summary, PolicyType


### ./bridge_backend/engines/arie/models.py
  - from pydantic import BaseModel, Field
  - from typing import List, Dict, Any, Optional
  - from enum import Enum
  - from datetime import datetime
  - excluded_paths: List[str] = Field(default_factory=list, description="Paths to exclude from scanning")


### ./bridge_backend/engines/arie/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from typing import Optional
  - from .core import ARIEEngine
  - from .models import (


### ./bridge_backend/engines/hydra/guard.py
  - import json
  - import os
  - import re
  - from pathlib import Path
  - from typing import Dict, Any
  - plan: Deployment plan from Chimera


### ./bridge_backend/engines/hydra/__init__.py
  - from .guard import HydraGuard


### ./bridge_backend/engines/hydra/routes.py
  - from fastapi import APIRouter, HTTPException
  - from typing import Dict, Any
  - import logging
  - from .guard import HydraGuard


### ./bridge_backend/engines/sanctum/core.py
  - import os
  - import logging
  - import subprocess
  - from typing import Dict, Any, Optional
  - from pathlib import Path
  - from datetime import datetime, UTC
  - """Report from deployment simulation"""
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.chimera.adapters.truth_adapter import TruthGate
  - from bridge_backend.engines.forge.core import run_full_repair
  - import asyncio


### ./bridge_backend/engines/sanctum/__init__.py
  - from .core import SanctumEngine


### ./bridge_backend/engines/github_forge/core.py
  - from pathlib import Path
  - import json
  - import os
  - Read JSON data from forge directory


### ./bridge_backend/engines/github_forge/__init__.py
  - from .core import GitHubForge


### ./bridge_backend/engines/render_fallback/core.py
  - from typing import Dict, Any
  - plan: Deployment plan from Chimera


### ./bridge_backend/engines/render_fallback/__init__.py
  - from .core import RenderFallback


### ./bridge_backend/engines/hypshard_x/rehydrator.py
  - import logging
  - from typing import List, Optional
  - from pathlib import Path
  - from .models import HXOPlan, ShardSpec, ShardPhase
  - from .checkpointer import HXOCheckpointer
  - Rehydrates incomplete plans from checkpoints.
  - Rehydrate a plan from checkpoints.


### ./bridge_backend/engines/hypshard_x/schedulers.py
  - from abc import ABC, abstractmethod
  - from typing import List
  - import logging
  - from .models import ShardSpec, SchedulerType
  - # Interleave shards from different executors


### ./bridge_backend/engines/hypshard_x/checkpointer.py
  - import sqlite3
  - import json
  - import logging
  - from pathlib import Path
  - from typing import Optional, Dict, Any
  - from datetime import datetime
  - from .models import HXOPlan, ShardSpec, ShardResult, ShardPhase
  - """Retrieve plan from checkpoint store"""
  - """Retrieve shard from checkpoint store"""
  - """Retrieve result from checkpoint store"""


### ./bridge_backend/engines/hypshard_x/executors.py
  - from abc import ABC, abstractmethod
  - from typing import Dict, Any
  - import logging
  - import asyncio
  - from .models import ExecutorType


### ./bridge_backend/engines/hypshard_x/core.py
  - from __future__ import annotations
  - import asyncio
  - import logging
  - from typing import Dict, List, Optional, Any
  - from datetime import datetime, UTC
  - from pathlib import Path
  - from .models import (
  - from .checkpointer import HXOCheckpointer
  - from .merkle import MerkleTree
  - from .schedulers import get_scheduler
  - from .executors import get_executor
  - from .partitioners import get_partitioner
  - import json
  - import hashlib
  - from bridge_backend.genesis.bus import genesis_bus
  - import os


### ./bridge_backend/engines/hypshard_x/merkle.py
  - import logging
  - from typing import Dict, List, Optional
  - import hashlib
  - from .models import ShardResult, MerkleNode, MerkleProof
  - Builds the tree bottom-up from leaves.
  - import random
  - # Extract CAS ID from node_id (format: "leaf_{cas_id}")


### ./bridge_backend/engines/hypshard_x/__init__.py


### ./bridge_backend/engines/hypshard_x/models.py
  - from __future__ import annotations
  - from typing import Dict, Any, List, Optional, Literal
  - from datetime import datetime, UTC
  - from pydantic import BaseModel, Field
  - from enum import Enum
  - import hashlib
  - import json
  - # Create deterministic hash from inputs
  - """Compute branch hash from children"""


### ./bridge_backend/engines/hypshard_x/partitioners.py
  - from abc import ABC, abstractmethod
  - from typing import List, Dict, Any
  - import logging
  - from .models import HXOStage, PartitionerType


### ./bridge_backend/engines/hypshard_x/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from typing import Dict, Any
  - import logging
  - import uuid
  - from .models import HXOPlan, HXOStage, PlanStatus
  - from .core import get_hxo_core
  - Create an HXO plan from a request.


### ./bridge_backend/engines/selftest/autoheal_trigger.py
  - import os
  - import logging
  - import asyncio
  - from typing import Dict, Any, Optional
  - from datetime import datetime, UTC


### ./bridge_backend/engines/selftest/core.py
  - import os
  - import logging
  - import asyncio
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, UTC
  - from pathlib import Path
  - import json
  - from .autoheal_trigger import AutoHealTrigger


### ./bridge_backend/engines/selftest/__init__.py
  - from .core import SelfTestController
  - from .autoheal_trigger import AutoHealTrigger


### ./bridge_backend/engines/elysium/core.py
  - import os
  - import logging
  - import asyncio
  - from typing import Optional
  - from datetime import datetime, UTC
  - from pathlib import Path
  - from bridge_backend.engines.sanctum.core import SanctumEngine
  - from bridge_backend.engines.forge.core import ForgeEngine
  - from bridge_backend.engines.arie.core import ARIEEngine
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.chimera.adapters.truth_adapter import TruthGate
  - import asyncio


### ./bridge_backend/engines/elysium/__init__.py
  - from .core import ElysiumGuardian


### ./bridge_backend/engines/umbra/healers.py
  - import logging
  - import os
  - from typing import Dict, Any, Optional
  - from datetime import datetime
  - from .models import HealPlan, TriageTicket, TriageStatus
  - from bridge_backend.engines.envrecon.parity import check_parity
  - from bridge_backend.bridge_core.engines.truth.core import TruthEngine
  - from bridge_backend.engines.chimera.core import ChimeraEngine
  - from bridge_backend.engines.autonomy.core import AutonomyEngine
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/engines/umbra/core.py
  - import logging
  - import os
  - import asyncio
  - from typing import Dict, Any, List, Optional
  - from datetime import datetime, timedelta
  - from collections import defaultdict
  - from .models import (
  - - collect: Ingest signals from various sources
  - Collect and process a signal from external source
  - # Create incident from signal
  - import json
  - from pathlib import Path
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/engines/umbra/__init__.py
  - from .core import UmbraTriageCore
  - from .models import TriageTicket, Incident, HealPlan, Report
  - from .healers import UmbraHealers


### ./bridge_backend/engines/umbra/models.py
  - from pydantic import BaseModel, Field
  - from typing import Optional, List, Dict, Any, Literal
  - from datetime import datetime
  - from enum import Enum
  - """Incident extracted from signals"""
  - tickets: List[TriageTicket] = Field(default_factory=list, description="Tickets from this run")


### ./bridge_backend/engines/umbra/routes.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from typing import Optional, Dict, Any, List
  - import logging
  - from .core import UmbraTriageCore
  - from .healers import UmbraHealers
  - from .models import TriageStatus, TriageSeverity, TriageKind
  - Ingest a signal from external source
  - from datetime import datetime


### ./bridge_backend/engines/envscribe/emitters.py
  - import logging
  - from pathlib import Path
  - from typing import Dict, List, Any
  - from .models import EnvScribeReport, EnvVariable, VerificationStatus
  - Generates output artifacts from EnvScribe reports:


### ./bridge_backend/engines/envscribe/core.py
  - import os
  - import re
  - import json
  - import logging
  - from pathlib import Path
  - from typing import Dict, List, Any, Optional, Set
  - from datetime import datetime, timezone
  - from .models import (
  - # Known environment variables from the codebase
  - """Load known environment variables from configuration"""
  - """Detect webhook endpoints from routes"""
  - # Known webhook patterns from Chimera and ARIE
  - description=f"Discovered from codebase",
  - """Get data from EnvRecon for verification"""
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - # Reconstruct report from JSON


### ./bridge_backend/engines/envscribe/__init__.py
  - from .core import EnvScribeEngine


### ./bridge_backend/engines/envscribe/models.py
  - from typing import Dict, List, Optional, Any
  - from dataclasses import dataclass, field, asdict
  - from datetime import datetime, timezone
  - from enum import Enum


### ./bridge_backend/engines/envscribe/routes.py
  - from fastapi import APIRouter, HTTPException
  - from typing import Dict, Any
  - import logging
  - from .core import EnvScribeEngine
  - from .emitters import EnvScribeEmitter
  - Generate all output artifacts from the latest scan.
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.truth.service import TruthEngine
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/engines/steward/core.py
  - from typing import Dict, List, Optional
  - import os
  - import secrets
  - import time
  - import logging
  - from pathlib import Path
  - from .models import DiffReport, Plan, ApplyResult, EnvVarChange
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/engines/steward/__init__.py
  - from .core import steward


### ./bridge_backend/engines/steward/models.py
  - from pydantic import BaseModel, Field
  - from typing import List, Dict, Any, Optional
  - from datetime import datetime, timezone


### ./bridge_backend/engines/steward/routes.py
  - from fastapi import APIRouter, Header, HTTPException, Query
  - from typing import Optional, List
  - import logging
  - from .core import steward
  - from .models import PlanRequest, ApplyRequest, DiffReport, Plan, ApplyResult
  - # Get owner handle from environment
  - import os
  - import os


### ./bridge_backend/engines/steward/adapters/github_adapter.py
  - import os
  - import logging


### ./bridge_backend/engines/steward/adapters/netlify_adapter.py
  - import os
  - import logging


### ./bridge_backend/engines/steward/adapters/__init__.py
  - # from .render_adapter import RenderAdapter
  - from .netlify_adapter import NetlifyAdapter
  - from .github_adapter import GithubAdapter


### ./bridge_backend/engines/autonomy/__init__.py
  - from .models import Incident, Decision


### ./bridge_backend/engines/autonomy/models.py
  - from pydantic import BaseModel, Field, ConfigDict
  - from typing import Optional, List, Dict, Any
  - from datetime import datetime


### ./bridge_backend/engines/autonomy/governor.py
  - import os
  - import logging
  - from datetime import datetime, timezone, timedelta
  - from typing import Dict, Any, Optional, List
  - from .models import Incident, Decision
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.chimera.core import ChimeraEngine
  - from bridge_backend.bridge_core.engines.chimera.engine import ChimeraDeploymentEngine
  - logger.error(f"[Governor] Chimera import failed: {e}")
  - from bridge_backend.engines.arie.core import ARIEEngine
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - from bridge_backend.engines.chimera.core import ChimeraEngine
  - from bridge_backend.engines.chimera.core import ChimeraEngine
  - from bridge_backend.bridge_core.engines.truth.core import TruthEngine
  - from bridge_backend.engines.envrecon.hubsync import hubsync
  - from bridge_backend.engines.chimera.core import ChimeraEngine
  - import hashlib
  - import json
  - import os
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.leviathan.solver import predict_deployment_success
  - from bridge_backend.bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine


### ./bridge_backend/engines/autonomy/routes.py
  - from fastapi import APIRouter, Depends, HTTPException
  - from .governor import AutonomyGovernor
  - from .models import Incident, Decision
  - from typing import Dict, Any
  - import logging
  - import os


### ./bridge_backend/forge/export_runtime.py
  - import json
  - import os
  - import sys
  - from datetime import datetime, timezone
  - from pathlib import Path
  - import hashlib


### ./bridge_backend/forge/__init__.py
  - from .forge_core import forge_integrate_engines, get_forge_status
  - from .synchrony import synchrony, get_synchrony_status


### ./bridge_backend/forge/synchrony.py
  - import os
  - import logging
  - from typing import Dict, Any, Optional
  - from datetime import datetime, timezone
  - 6. Umbra learns from patch metadata
  - from bridge_backend.engines.arie.core import ARIEEngine
  - from bridge_backend.bridge_core.engines.truth.utils import certify
  - # Learn from the patches if Umbra is enabled
  - Umbra learns from patch metadata for future predictive healing.
  - logger.info(f"🧠 [Umbra] Learning from healing event {event_id}")
  - from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory


### ./bridge_backend/forge/forge_core.py
  - directly from the codebase without needing external API or webhook dependencies.
  - import os
  - import json
  - import importlib
  - import logging
  - from pathlib import Path
  - from typing import Dict, List, Any, Optional
  - from bridge_backend.bridge_core.engines.truth.utils import certify as truth_certify
  - Load the bridge forge registry from .github/bridge_forge.json
  - Get the list of all registered engines from Genesis activation.
  - from bridge_backend.genesis.activation import ENGINE_REGISTRY
  - logger.warning("[Forge] Could not import ENGINE_REGISTRY from genesis.activation")
  - # Try to import the module
  - Forge introspection: scans repo & activates engines directly from the repository.
  - 2. Discovers additional engines from the directory structure
  - # Discover engines from directory structure


### ./bridge_backend/forge/routes.py
  - from fastapi import APIRouter, HTTPException
  - from typing import Dict, Any
  - import logging
  - from .forge_core import forge_integrate_engines, get_forge_status, load_forge_registry
  - from .synchrony import get_synchrony_status, synchrony
  - Engine to path mappings from bridge_forge.json
  - Topology map from forge_topology.json
  - import json
  - from pathlib import Path


### ./bridge_backend/scripts/endpoint_triage.py
  - import os
  - import sys
  - import json
  - import requests
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any


### ./bridge_backend/scripts/deploy_diagnose.py
  - import os, requests, time
  - print("🔍 Fetching logs from backend and Netlify...")


### ./bridge_backend/scripts/triage_preseed.py
  - import json
  - import sys
  - from pathlib import Path
  - from typing import List, Dict, Any
  - from utils import now
  - from scripts.utils import now
  - # Create filename from event type
  - Build a unified baseline timeline from seeded events.


### ./bridge_backend/scripts/env_sync_monitor.py
  - import os, sys, json, time
  - import urllib.request


### ./bridge_backend/scripts/generate_sync_badge.py
  - import requests
  - import json
  - import os
  - import sys


### ./bridge_backend/scripts/utils.py
  - from datetime import datetime, timezone


### ./bridge_backend/scripts/synchrony_collector.py
  - Collects and merges triage reports from CI/CD, Endpoint, and API systems.
  - import json
  - import os
  - from pathlib import Path
  - from datetime import datetime
  - from typing import List, Dict, Any
  - Build a unified timeline from all triage report files.


### ./bridge_backend/scripts/run_scan.py
  - import argparse, json, sys, os
  - from pathlib import Path
  - from bridge_backend.bridge_core.scans.service import run_combined_scan


### ./bridge_backend/scripts/report_bridge_event.py
  - import os, sys, json, hmac, hashlib, urllib.request


### ./bridge_backend/scripts/deepscan_reporter.py
  - import os
  - import json
  - import socket
  - from datetime import datetime, timezone
  - import requests
  - from typing import Dict, Any, Optional


### ./bridge_backend/scripts/api_triage.py
  - import os
  - import sys
  - import json
  - import requests
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional


### ./bridge_backend/scripts/hooks_triage.py
  - import os
  - import sys
  - import json
  - import time
  - import hmac
  - import hashlib
  - import requests
  - from pathlib import Path
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional


### ./bridge_backend/scripts/ci_cd_triage.py
  - import json
  - import os
  - import sys
  - from datetime import datetime, timezone


### ./bridge_backend/scripts/__init__.py


### ./bridge_backend/scripts/deploy_confidence.py
  - import json, os, requests, time


### ./bridge_backend/genesis/manifest.py
  - from typing import Dict, Any, List, Optional
  - import logging
  - import os
  - """Rebuild the unified manifest from all registered engines"""
  - from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
  - logger.info(f"✅ Synced {len(blueprint_manifest)} engines from Blueprint Registry")
  - logger.error(f"❌ Failed to sync from Blueprint Registry: {e}")
  - # Parse manifest metadata from header comments
  - from datetime import datetime, UTC


### ./bridge_backend/genesis/orchestration.py
  - from typing import Dict, Any, Optional
  - import asyncio
  - import logging
  - import os
  - from .bus import genesis_bus
  - from .manifest import genesis_manifest
  - from .introspection import genesis_introspection
  - from .bus import genesis_bus
  - # TODO: Implement actual action execution with guardrails from Blueprint/Guardians


### ./bridge_backend/genesis/registration.py
  - import logging
  - from typing import Dict, Any
  - from bridge_backend.genesis.bus import genesis_bus
  - import asyncio
  - logger.warning(f"⚠️ Could not import Genesis Bus: {e}")


### ./bridge_backend/genesis/activation.py
  - import os
  - import logging
  - from typing import Dict, List, Any
  - from datetime import datetime, timezone
  - from bridge_backend.genesis.bus import genesis_bus
  - import asyncio
  - from datetime import datetime, timezone
  - from bridge_backend.genesis.bus import genesis_bus
  - import asyncio


### ./bridge_backend/genesis/introspection.py
  - from typing import Dict, Any, List, Optional
  - import logging
  - import os
  - from datetime import datetime, UTC
  - from .manifest import genesis_manifest


### ./bridge_backend/genesis/bus.py
  - from typing import Callable, Dict, Any, DefaultDict, List, Optional
  - from collections import defaultdict
  - import asyncio
  - import logging
  - import os
  - from datetime import datetime, UTC
  - from bridge_backend.bridge_core.guardians.gate import guardians_gate
  - from bridge_backend.genesis.persistence import genesis_persistence
  - from bridge_backend.genesis.persistence import genesis_persistence
  - from bridge_backend.engines.arie.core import ARIEEngine
  - from bridge_backend.engines.arie.models import PolicyType


### ./bridge_backend/genesis/adapters.py
  - from typing import Dict, Any, Optional
  - import logging
  - from .contracts import GenesisEvent, EventKind
  - from .bus import genesis_bus
  - logger.debug(f"📡 Published {kind} event: {topic} from {source}")


### ./bridge_backend/genesis/replay.py
  - import logging
  - from typing import Optional, Callable, Dict, Any, List
  - from datetime import datetime
  - from .persistence import genesis_persistence
  - from .bus import genesis_bus
  - - Replay events from watermark
  - Replay events from a specific watermark
  - logger.info(f"🔄 Replaying events from watermark {watermark} (topic={topic_pattern}, limit={limit})")
  - Replay events from a specific timestamp
  - logger.info(f"📦 Found {len(filtered)} events to replay from {from_ts}")
  - import sys
  - import asyncio


### ./bridge_backend/genesis/contracts.py
  - from pydantic import BaseModel, Field
  - from typing import Literal, Optional, Dict, Any
  - from datetime import datetime
  - import uuid


### ./bridge_backend/genesis/persistence.py
  - import os
  - import json
  - import logging
  - import sqlite3
  - import asyncio
  - from pathlib import Path
  - from typing import Dict, Any, Optional, List
  - from datetime import datetime, timedelta, timezone
  - from contextlib import asynccontextmanager
  - Retrieve events from store


### ./bridge_backend/genesis/__init__.py
  - from .bus import GenesisEventBus, genesis_bus
  - from .manifest import GenesisManifest
  - from .introspection import GenesisIntrospection
  - from .orchestration import GenesisOrchestrator
  - from .activation import activate_all_engines, get_activation_status, ActivationReport
  - from .registration import register_embedded_nodes


### ./bridge_backend/genesis/routes.py
  - from fastapi import APIRouter, HTTPException
  - from typing import Dict, Any
  - import logging
  - import os
  - from bridge_backend.genesis.introspection import genesis_introspection
  - from bridge_backend.genesis.orchestration import genesis_orchestrator
  - from bridge_backend.genesis.manifest import genesis_manifest
  - from bridge_backend.genesis.manifest import genesis_manifest
  - from bridge_backend.genesis.introspection import genesis_introspection
  - from bridge_backend.genesis.introspection import genesis_introspection
  - from bridge_backend.genesis.introspection import genesis_introspection
  - Get recent event history from Genesis bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/cli/selftest_summary.py
  - Generates PR health summary from selftest and Umbra reports
  - import click
  - import json
  - import sys
  - from pathlib import Path
  - from datetime import datetime
  - """Generate PR health summary from selftest and Umbra reports"""


### ./bridge_backend/cli/diagctl.py
  - import asyncio
  - import json
  - import sys
  - import os
  - from bridge_backend.bridge_core.engines.hxo import initialize_nexus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - from bridge_backend.engines.arie.core import ARIEEngine
  - from bridge_backend.engines.steward.core import Steward


### ./bridge_backend/cli/doctor.py
  - import os
  - import sys
  - from bridge_backend.runtime.heartbeat import ensure_httpx
  - from bridge_backend.models import Base
  - from bridge_backend.db import engine


### ./bridge_backend/cli/chimeractl.py
  - import sys
  - import argparse
  - import asyncio
  - import json
  - from pathlib import Path
  - from bridge_core.engines.chimera import ChimeraDeploymentEngine, ChimeraConfig
  - # Use the preflight engine from engines.chimera
  - from pathlib import Path
  - from engines.chimera.core import ChimeraEngine


### ./bridge_backend/cli/autonomyctl.py
  - import sys
  - import os
  - import argparse
  - import asyncio
  - import json
  - from pathlib import Path
  - from engines.autonomy.governor import AutonomyGovernor
  - from engines.autonomy.models import Incident, Decision


### ./bridge_backend/cli/genesisctl.py
  - import sys
  - import os
  - import asyncio
  - import argparse
  - import json
  - from pathlib import Path
  - from datetime import datetime
  - from engines.envrecon.core import EnvReconEngine
  - from engines.envrecon.hubsync import hubsync
  - from engines.envrecon.autoheal import autoheal
  - from engines.selftest.core import SelfTestController
  - print("🔄 Syncing to GitHub from Render...")
  - print(f"✅ Fetched {len(render_vars)} variables from Render")
  - print("💡 Tip: Use --from render to sync from Render to GitHub")
  - print(f"❌ Failed to fetch variables from {source}")
  - print(f"✅ Exported {len(source_vars)} variables from {source}")
  - from genesis.activation import activate_all_engines
  - import traceback
  - from genesis.activation import get_activation_status
  - import traceback
  - import traceback


### ./bridge_backend/cli/ariectl.py
  - import sys
  - import argparse
  - import json
  - from pathlib import Path
  - from engines.arie.core import ARIEEngine
  - from engines.arie.models import PolicyType
  - import traceback


### ./bridge_backend/cli/umbractl.py
  - import click
  - import asyncio
  - import sys
  - import os
  - import json
  - from pathlib import Path
  - from bridge_backend.engines.umbra.core import UmbraTriageCore
  - from bridge_backend.engines.umbra.healers import UmbraHealers
  - from bridge_backend.engines.umbra.core import UmbraTriageCore
  - from bridge_backend.engines.umbra.core import UmbraTriageCore
  - from bridge_backend.engines.umbra.healers import UmbraHealers
  - from datetime import datetime
  - from bridge_backend.engines.umbra.core import UmbraTriageCore


### ./bridge_backend/cli/umbra.py
  - import click
  - import asyncio
  - import sys
  - import os
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice


### ./bridge_backend/cli/brh_cli.py
  - import sys
  - import os
  - import json
  - import argparse
  - import asyncio
  - from pathlib import Path
  - from datetime import datetime
  - from bridge_core.runtime_handler import (
  - import shutil
  - print("   gh secret set FORGE_DOMINION_ROOT --body \"$(python -c 'import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip(\"=\"))')\"")


### ./bridge_backend/cli/envscribectl.py
  - import sys
  - import asyncio
  - import argparse
  - from pathlib import Path
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter


### ./bridge_backend/cli/__init__.py


### ./bridge_backend/cli/badgegen.py
  - import click
  - import json
  - import sys
  - from pathlib import Path
  - from typing import Dict, Any
  - Generate Bridge Health badge from health record
  - import traceback


### ./bridge_backend/cli/deployctl.py
  - import asyncio
  - import json
  - import click
  - from ..engines.chimera.core import ChimeraOracle


### ./bridge_backend/tools/parity_engine.py
  - import os, re, json, pathlib, hashlib, time, asyncio
  - import sys
  - from genesis.bus import genesis_bus


### ./bridge_backend/tools/parity_autofix.py
  - import os
  - import re
  - import json
  - import pathlib
  - import hashlib
  - import time
  - import asyncio
  - from typing import List, Dict, Set
  - # Extract method from common patterns
  - import apiClient from '../api';
  - from fastapi import APIRouter
  - index_content += f"export * from './{filename}';\n"
  - import sys
  - from genesis.bus import genesis_bus
  - print(f"   Missing from frontend: {summary.get('missing_from_frontend', 0)}")
  - print(f"   Missing from backend: {summary.get('missing_from_backend', 0)}")


### ./bridge_backend/tools/health/healer_net_probe.py
  - import os
  - import json
  - import glob
  - import platform
  - from datetime import datetime, timezone
  - # Collect from existing subsystems


### ./bridge_backend/tools/firewall_intel/fetch_firewall_incidents.py
  - Fetches live incident data from GitHub Status, npm, Render, and Netlify.
  - import os
  - import sys
  - import json
  - import time
  - import requests
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any
  - # Collect data from all sources
  - print(f"✅ Incident data collected from {report['summary']['total_sources']} sources")


### ./bridge_backend/tools/firewall_intel/chromium_probe.py
  - import json
  - import os
  - import sys
  - import platform
  - import subprocess
  - from pathlib import Path


### ./bridge_backend/tools/firewall_intel/__init__.py


### ./bridge_backend/tools/firewall_intel/firewall_autonomy_engine.py
  - import os
  - import sys
  - import json
  - import time
  - import re
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional
  - from pathlib import Path
  - from bridge_backend.tools.firewall_intel.fetch_firewall_incidents import main as fetch_incidents
  - from bridge_backend.tools.firewall_intel.analyze_firewall_findings import main as analyze_findings
  - from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager
  - """Gather firewall intelligence from external sources"""
  - print("  → Fetching incidents from external sources...")
  - import traceback


### ./bridge_backend/tools/firewall_intel/analyze_firewall_findings.py
  - import os
  - import sys
  - import json
  - import time
  - import re
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Set
  - """Load firewall incidents from previous fetch."""


### ./bridge_backend/tools/network_diagnostics/__init__.py


### ./bridge_backend/tools/network_diagnostics/check_copilot_access.py
  - import socket
  - import ssl
  - import json
  - import concurrent.futures
  - import time
  - import pathlib
  - import urllib.parse
  - import requests


### ./bridge_backend/tools/triage/endpoint_triage.py
  - import json, pathlib, os, asyncio
  - from common.utils import retrying_check
  - import sys
  - from genesis.bus import genesis_bus
  - # Prefer routes explicitly missing from frontend


### ./bridge_backend/tools/triage/diagnostics_federate.py
  - import json, pathlib, time, os, asyncio
  - import sys
  - from genesis.bus import genesis_bus


### ./bridge_backend/tools/triage/api_triage.py
  - import os, json, pathlib, asyncio
  - from common.utils import retrying_check
  - import sys
  - from genesis.bus import genesis_bus


### ./bridge_backend/tools/triage/deploy_path_triage.py
  - import os
  - import json
  - import subprocess
  - import pathlib
  - from datetime import datetime, timezone


### ./bridge_backend/tools/triage/common/utils.py
  - import os, time, json, random, urllib.request, urllib.error


### ./bridge_backend/tools/triage/common/__init__.py


### ./bridge_backend/tools/autonomy/failure_analyzer.py
  - import re
  - import json
  - import yaml
  - import argparse
  - from pathlib import Path
  - from typing import Dict, List, Any
  - from datetime import datetime, timezone
  - return "Update action versions from v3 to v4"


### ./bridge_backend/tools/autonomy/failure_patterns.py


### ./bridge_backend/tools/autonomy/pr_generator.py
  - import json
  - import argparse
  - from pathlib import Path
  - from typing import Dict, List, Any, Tuple
  - from datetime import datetime, timezone
  - """Load the fix plan from JSON file."""
  - print(f"🔧 Loading fix plan from {self.plan_file}...")


### ./bridge_backend/tools/autonomy/test_autonomy_tools.py
  - import pytest
  - import json
  - import tempfile
  - from pathlib import Path
  - # Import from autonomy package
  - from bridge_backend.tools.autonomy.failure_analyzer import FailurePatternAnalyzer
  - from bridge_backend.tools.autonomy.pr_generator import PRGenerator
  - from bridge_backend.tools.autonomy.failure_patterns import (


### ./bridge_backend/tools/autonomy/__init__.py
  - from .failure_analyzer import FailurePatternAnalyzer
  - from .pr_generator import PRGenerator


### ./bridge_backend/tools/firewall_sovereignty/network_resilience.py
  - import socket
  - import time
  - import requests
  - from typing import Dict, List, Any, Optional, Tuple
  - from datetime import datetime, timezone
  - from pathlib import Path
  - import json
  - import time


### ./bridge_backend/tools/firewall_sovereignty/sovereign_orchestrator.py
  - import os
  - import sys
  - import json
  - from typing import Dict, Any
  - from datetime import datetime, timezone
  - from pathlib import Path
  - from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager
  - from bridge_backend.tools.firewall_sovereignty.network_resilience import NetworkResilienceLayer
  - from bridge_backend.tools.firewall_sovereignty.validation_sovereignty import ValidationSovereignty
  - from bridge_backend.tools.firewall_sovereignty.script_execution import ScriptExecutionSovereignty


### ./bridge_backend/tools/firewall_sovereignty/validation_sovereignty.py
  - import os
  - import re
  - import yaml
  - import json
  - from typing import Dict, List, Any, Optional, Tuple
  - from datetime import datetime, timezone
  - from pathlib import Path
  - validation_results: Results from validation


### ./bridge_backend/tools/firewall_sovereignty/script_execution.py
  - import os
  - import sys
  - import subprocess
  - import json
  - from typing import Dict, List, Any, Optional
  - from datetime import datetime, timezone
  - from pathlib import Path
  - import importlib.util


### ./bridge_backend/tools/firewall_sovereignty/firewall_config_manager.py
  - import os
  - import json
  - import yaml
  - from datetime import datetime, timezone
  - from typing import Dict, List, Any, Optional
  - from pathlib import Path
  - """Remove a domain from the allowlist"""


### ./bridge_backend/tools/firewall_sovereignty/__init__.py


### ./bridge_backend/runtime/retry.py
  - import random, time
  - from typing import Callable, Type, Iterable, Any, Optional
  - raise RetryError(f"Exceeded retry budget after {retries} attempts") from e


### ./bridge_backend/runtime/health_probe.py
  - import os
  - import sys
  - import argparse
  - import time
  - import requests
  - # Try to import telemetry
  - from bridge_backend.runtime.telemetry import TELEMETRY
  - from runtime.telemetry import TELEMETRY


### ./bridge_backend/runtime/startup_watchdog.py
  - import os
  - import time
  - import logging
  - import datetime
  - from dateutil.tz import tzutc
  - from bridge_backend.runtime.predictive_stabilizer import (


### ./bridge_backend/runtime/temporal_deploy.py
  - import os
  - import asyncio
  - import logging
  - import time
  - from typing import Dict, Any, Optional, Callable
  - from datetime import datetime, timezone
  - import json
  - "Module import verification"
  - from bridge_backend.db.bootstrap import auto_sync_schema
  - from bridge_backend.runtime.predictive_stabilizer import is_live


### ./bridge_backend/runtime/heartbeat.py
  - from __future__ import annotations
  - import asyncio, os, random
  - from typing import Optional
  - import httpx


### ./bridge_backend/runtime/deploy_parity.py
  - import os
  - import json
  - import time
  - import pathlib
  - import asyncio
  - from fastapi import FastAPI
  - from starlette.responses import JSONResponse
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/runtime/release_intel.py
  - import json, os, logging
  - from .predictive_stabilizer import evaluate_stability, resolve_tickets
  - # First, resolve any tickets from previous boots


### ./bridge_backend/runtime/verify_imports.py
  - import importlib
  - import logging
  - import sys
  - import os
  - """Run import verification when called directly"""


### ./bridge_backend/runtime/port_guard.py
  - import os


### ./bridge_backend/runtime/ports.py
  - import os
  - import socket
  - import logging
  - from contextlib import closing
  - from typing import Tuple
  - log.info(f"[PORT] Using PORT={port} from environment")


### ./bridge_backend/runtime/temporal_stage_manager.py
  - import os
  - import asyncio
  - import logging
  - import time
  - from typing import Dict, List, Optional, Callable, Any
  - from dataclasses import dataclass, field
  - from datetime import datetime
  - from enum import Enum
  - import json


### ./bridge_backend/runtime/quantum_predeploy_orchestrator.py
  - import os
  - import sys
  - import json
  - import logging
  - from pathlib import Path
  - from bridge_backend.bridge_core.token_forge_dominion import (
  - # Get environment from environment variable


### ./bridge_backend/runtime/auto_repair.py
  - import os
  - import sys
  - import asyncio
  - import logging
  - from bridge_backend.runtime.verify_imports import check_critical_imports


### ./bridge_backend/runtime/predictive_stabilizer.py
  - import os, glob, shutil, re, logging, datetime, json, statistics
  - from dateutil.tz import tzutc
  - from typing import Dict, Any, List, Optional
  - from bridge_backend.integrations.github_issues import maybe_create_issue
  - "- Ensure /health endpoint returns 200 OK from both Netlify and Render",
  - # heartbeat now auto-detects from RENDER_EXTERNAL_URL
  - # Check if latency was mentioned and if it's from a previous boot cycle
  - # Extract timestamp from filename (format: YYYYMMDDTHHMMSSz_*.md)
  - # Collect metrics from anomaly queue


### ./bridge_backend/runtime/telemetry.py
  - from __future__ import annotations
  - import threading, time, socket, os
  - from typing import Dict, Any, List
  - from collections import deque


### ./bridge_backend/runtime/run_migrations.py
  - import sys
  - import argparse
  - import os
  - import psycopg2


### ./bridge_backend/runtime/metrics_middleware.py
  - import time
  - from fastapi import Request
  - from .telemetry import TELEMETRY


### ./bridge_backend/runtime/parity.py
  - import os
  - import logging
  - from bridge_backend.runtime.heartbeat import record_repair


### ./bridge_backend/runtime/wait_for_db.py
  - import os
  - import sys
  - import time
  - import argparse
  - import psycopg2
  - # Try to import telemetry
  - from bridge_backend.runtime.telemetry import TELEMETRY
  - from runtime.telemetry import TELEMETRY


### ./bridge_backend/runtime/db_url_guard.py
  - import os
  - import sys
  - import re
  - from urllib.parse import urlsplit
  - # Handle multiple @ in password by splitting from the right


### ./bridge_backend/runtime/tickets.py
  - import os
  - import logging
  - from pathlib import Path
  - from datetime import datetime, timezone


### ./bridge_backend/runtime/egress_canary.py
  - import socket
  - import sys
  - import argparse
  - import time
  - # Try to import telemetry
  - from bridge_backend.runtime.telemetry import TELEMETRY
  - from runtime.telemetry import TELEMETRY


### ./bridge_backend/runtime/tde_x/stabilization.py
  - from contextlib import AbstractContextManager
  - from typing import Optional, Type
  - import logging
  - from bridge_backend.runtime import tickets


### ./bridge_backend/runtime/tde_x/orchestrator.py
  - import asyncio
  - import logging
  - from .shards import bootstrap, runtime, diagnostics
  - from .federation import announce
  - from .queue import queue
  - from typing import List, Any
  - from ...bridge_core.engines.blueprint.adapters import tde_link


### ./bridge_backend/runtime/tde_x/queue.py
  - import asyncio
  - import json
  - import logging
  - from pathlib import Path
  - from typing import Dict, Any
  - # non-fatal: ticket logged by StabilizationDomain from caller
  - from .shards.diagnostics import upload_assets
  - from .shards.diagnostics import emit_metrics


### ./bridge_backend/runtime/tde_x/__init__.py


### ./bridge_backend/runtime/tde_x/orchestrator_v2.py
  - import os
  - import asyncio
  - import logging
  - from typing import Dict, Any, Optional, List
  - from datetime import datetime, timezone
  - from pathlib import Path
  - import json
  - from bridge_backend.genesis.adapters import emit_control
  - from bridge_backend.genesis.adapters import emit_control
  - from bridge_backend.genesis.adapters import deploy_stage_started
  - from bridge_backend.genesis.adapters import deploy_stage_completed
  - from bridge_backend.genesis.adapters import deploy_failed
  - from bridge_backend.genesis.adapters import deploy_failed
  - from .stages.post_boot import run_post_boot
  - from .stages.warm_caches import run_warm_caches
  - from .stages.index_assets import run_index_assets
  - from .stages.scan_federation import run_scan_federation


### ./bridge_backend/runtime/tde_x/federation.py
  - import logging
  - from typing import Dict, Any
  - from .stabilization import StabilizationDomain
  - from bridge_backend.bridge_core.heritage.event_bus import bus


### ./bridge_backend/runtime/tde_x/shards/bootstrap.py
  - import asyncio
  - import os
  - import logging
  - from ..stabilization import StabilizationDomain
  - from typing import Dict, Any


### ./bridge_backend/runtime/tde_x/shards/runtime.py
  - import asyncio
  - import logging
  - from ..stabilization import StabilizationDomain
  - from typing import Dict, Any
  - from bridge_backend.db.bootstrap import auto_sync_schema
  - # Router verification — import won't crash app now
  - from bridge_backend.main import app


### ./bridge_backend/runtime/tde_x/shards/__init__.py


### ./bridge_backend/runtime/tde_x/shards/diagnostics.py
  - import asyncio
  - import logging
  - from ..stabilization import StabilizationDomain
  - from ..queue import queue
  - from typing import Dict, Any


### ./bridge_backend/runtime/tde_x/stages/post_boot.py
  - import logging
  - import asyncio
  - from bridge_backend.db import get_async_session_factory
  - from bridge_backend.runtime.health_probe import HealthProbe


### ./bridge_backend/runtime/tde_x/stages/scan_federation.py
  - import logging
  - import asyncio
  - from bridge_backend.runtime.tde_x.federation import discover_services
  - from bridge_backend.runtime.tde_x.federation import sync_federation_state
  - from bridge_backend.bridge_core.registry import update_service_registry


### ./bridge_backend/runtime/tde_x/stages/index_assets.py
  - import logging
  - import asyncio
  - from bridge_backend.tools.doc_indexer import index_documentation
  - from bridge_backend.tools.embeddings import build_search_index


### ./bridge_backend/runtime/tde_x/stages/warm_caches.py
  - import logging
  - import asyncio
  - from bridge_backend.bridge_core.protocols.storage import load_registry
  - from bridge_backend.bridge_core.engines.agents_foundry.cache import warm_agent_cache
  - from bridge_backend.genesis.manifest import genesis_manifest


### ./bridge_backend/runtime/tde_x/stages/__init__.py


### ./bridge_backend/routes/sovereign_engines.py
  - from fastapi import APIRouter, HTTPException, UploadFile, File, Form
  - from typing import Optional
  - import logging
  - from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard, ComplianceResult
  - from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe, DiffAnalysis, PRTemplate
  - from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician, LogAnalysis
  - Generate PR template from diff analysis
  - Get security intelligence from logs
  - Get performance metrics from logs


### ./bridge_backend/routes/health.py
  - from fastapi import APIRouter
  - import os
  - from ..runtime.ports import resolve_port, check_listen
  - from ..runtime.temporal_deploy import tdb
  - from pathlib import Path
  - from fastapi import Response
  - from ..runtime.tde_x.queue import queue
  - from pathlib import Path


### ./bridge_backend/routes/diagnostics_timeline.py
  - from fastapi import APIRouter, HTTPException, Request
  - from datetime import datetime, timezone
  - import os
  - import requests
  - import json
  - from pathlib import Path
  - from bridge_backend.runtime.tde_x.queue import queue
  - from pathlib import Path
  - import logging
  - """Return unified health timeline from merged triage reports."""
  - import sys
  - from synchrony_collector import build_unified_timeline


### ./bridge_backend/routes/control.py
  - from fastapi import APIRouter, Request, HTTPException
  - import os
  - import requests
  - import hmac
  - import hashlib
  - import subprocess
  - import sys
  - import json
  - import time
  - import gzip
  - from datetime import datetime, timezone
  - from pathlib import Path
  - """Replay a specific incident from stabilization tickets"""


### ./bridge_backend/routes/__init__.py


### ./bridge_backend/diagnostics/verify_env_sync.py
  - import json
  - import os
  - import sys
  - from datetime import datetime, UTC
  - from pathlib import Path
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - print("❌ Failed to import EnvReconEngine - checking alternative locations...")
  - from engines.envrecon.core import EnvReconEngine
  - print("❌ Could not import EnvReconEngine from any location")
  - from bridge_backend.genesis.bus import genesis_bus
  - import asyncio


### ./bridge_backend/integrations/github_issues.py
  - import os, logging, httpx


### ./bridge_backend/integrations/__init__.py


### ./bridge_backend/tests/test_chimera_oracle.py
  - import pytest
  - import asyncio
  - from bridge_backend.engines.chimera.core import ChimeraOracle


### ./bridge_backend/tests/test_autonomy_governor.py
  - import pytest
  - from datetime import datetime, timezone, timedelta
  - from bridge_backend.engines.autonomy.governor import AutonomyGovernor
  - from bridge_backend.engines.autonomy.models import Incident, Decision
  - """Test that old actions are removed from rate limit window"""


### ./bridge_backend/tests/test_micro_logician.py
  - import pytest
  - from bridge_backend.bridge_engines.micro_logician import (
  - """Test pattern extraction from logs"""


### ./bridge_backend/tests/test_agents_registry.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path
  - import shutil, json
  - from importlib import reload
  - import bridge_backend.bridge_core.registry.agents_registry as reg
  - from importlib import reload
  - import bridge_backend.bridge_core.registry.routes as routes


### ./bridge_backend/tests/test_protocols_registry.py
  - from bridge_backend.bridge_core.protocols import registry


### ./bridge_backend/tests/test_protocols_routes.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from bridge_core.protocols import storage
  - from bridge_core.protocols.registry import _registry, register_protocol
  - from bridge_backend.bridge_core.protocols import storage
  - from bridge_backend.bridge_core.protocols.registry import _registry, register_protocol
  - from pathlib import Path
  - import json
  - import pytest


### ./bridge_backend/tests/test_speech_engines.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_permissions.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from bridge_backend.bridge_core.engines.cascade.service import CascadeEngine
  - import json
  - from pathlib import Path


### ./bridge_backend/tests/test_arie_truth_cascade.py
  - import unittest
  - from unittest.mock import AsyncMock, MagicMock, patch
  - from datetime import datetime, UTC
  - import tempfile
  - import shutil
  - from pathlib import Path
  - import sys
  - from engines.arie.core import ARIEEngine
  - from engines.arie.models import PolicyType, Patch, Summary, Finding
  - test_file.write_text("from datetime import datetime\ntimestamp = datetime.utcnow()")
  - from datetime import datetime
  - import os
  - import asyncio


### ./bridge_backend/tests/test_mas_healing.py
  - import pytest
  - import asyncio
  - from bridge_core.heritage.mas.adapters import (


### ./bridge_backend/tests/test_hxo_nexus.py
  - import unittest
  - import asyncio
  - import sys
  - from pathlib import Path
  - from bridge_core.engines.hxo.nexus import HXONexus, get_nexus_instance, initialize_nexus
  - from bridge_core.engines.hxo.hypshard import HypShardV3Manager
  - from bridge_core.engines.hxo.security import (
  - # Test specific connections from the spec
  - # If A connects to B, we should be able to query from either direction


### ./bridge_backend/tests/test_agents_routes.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_arie_scheduler.py
  - import unittest
  - import asyncio
  - import tempfile
  - import shutil
  - import json
  - import os
  - from pathlib import Path
  - from datetime import datetime, UTC
  - from unittest.mock import Mock, patch, AsyncMock
  - import sys
  - from engines.arie.scheduler import ARIEScheduler
  - from engines.arie.core import ARIEEngine
  - from engines.arie.models import PolicyType, Summary


### ./bridge_backend/tests/test_hydra_guard.py
  - import pytest
  - import asyncio
  - from pathlib import Path
  - from bridge_backend.engines.hydra.guard import HydraGuard


### ./bridge_backend/tests/test_parity_autofix.py
  - import os
  - import sys
  - import json
  - import pathlib
  - import shutil
  - from tools import parity_autofix
  - print(f"❌ Failed to import parity_autofix: {e}")
  - "import apiClient from",


### ./bridge_backend/tests/test_counterfeit_detector.py
  - import sys
  - from pathlib import Path
  - from utils.counterfeit_detector import compare_text


### ./bridge_backend/tests/test_chimera_genesis_recovery.py
  - Tests import path normalization, retry logic, and fallback channel
  - import types
  - from unittest.mock import MagicMock, patch
  - import pytest
  - """Test successful Genesis bus import via paths.py"""
  - from bridge_backend.bridge_core.paths import import_genesis_bus
  - # Patch the import function
  - from bridge_backend.bridge_core.engines.adapters.chimera_genesis_link import register_with_retry
  - from bridge_backend.bridge_core.engines.adapters.chimera_genesis_link import register_with_retry
  - from bridge_backend.bridge_core.engines.hxo import safe_init
  - from bridge_backend.bridge_core.engines.umbra.lattice import fallback_neural_channel


### ./bridge_backend/tests/test_protocols_models.py
  - from bridge_core.protocols.models import Protocol, ProtocolList


### ./bridge_backend/tests/test_hubsync.py
  - import pytest
  - import sys
  - from pathlib import Path
  - from engines.envrecon.hubsync import HubSync
  - import os
  - from engines.envrecon.hubsync import HubSync
  - from engines.envrecon.hubsync import HubSync


### ./bridge_backend/tests/test_parser_enhanced.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_leviathan_tags.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path
  - import json
  - import shutil
  - """Helper to cleanup test assets from vault"""
  - # Filter out any indexed docs that don't have tags (they come from DB, not creativity)


### ./bridge_backend/tests/test_integration_section2.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_umbra_predictive.py
  - import pytest
  - import asyncio
  - from datetime import datetime, timezone
  - from bridge_backend.bridge_core.engines.umbra.predictive import UmbraPredictive
  - from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
  - from bridge_backend.bridge_core.engines.umbra.core import UmbraCore
  - import tempfile
  - import os
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.umbra import memory as memory_module


### ./bridge_backend/tests/test_parser_engine.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - import json
  - from bridge_backend.bridge_core.engines.parser.service import ParserEngine


### ./bridge_backend/tests/test_console_routes.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_firewall_autonomy_engine.py
  - import os
  - import sys
  - import json
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock
  - from bridge_backend.tools.firewall_intel.firewall_autonomy_engine import FirewallAutonomyEngine


### ./bridge_backend/tests/test_registry.py
  - import pytest
  - from bridge_backend.bridge_core.protocols.registry import ProtocolEntry


### ./bridge_backend/tests/test_hxo_planner.py
  - import unittest
  - from unittest.mock import AsyncMock, MagicMock, patch
  - from datetime import datetime, UTC
  - import tempfile
  - import shutil
  - from pathlib import Path
  - import asyncio
  - import sys
  - from engines.hypshard_x.models import (
  - from engines.hypshard_x.core import HXOCore
  - from engines.hypshard_x.merkle import MerkleTree
  - from bridge_core.engines.adapters.hxo_blueprint_link import validate_stage
  - from bridge_core.engines.adapters.hxo_parser_link import parse_plan_spec


### ./bridge_backend/tests/test_stripe_webhook.py
  - from fastapi.testclient import TestClient
  - from main import app
  - import json
  - import pytest
  - from unittest.mock import patch as mock_patch, MagicMock
  - from bridge_core.engines.cascade import service
  - from bridge_core.engines.cascade import service
  - from bridge_core.payments import stripe_webhooks
  - # Monkeypatch both the service module and the import in stripe_webhooks
  - # We need to also patch the CascadeEngine import in the webhook handler
  - from bridge_core.engines.cascade import service
  - from bridge_core.engines.cascade import service
  - from bridge_core.engines.cascade import service
  - from bridge_core.engines.cascade import service
  - from bridge_core.engines.cascade import service
  - from bridge_core.engines.cascade import service


### ./bridge_backend/tests/test_autonomy_v196t.py
  - import pytest
  - from datetime import datetime, timezone, timedelta
  - from bridge_backend.engines.autonomy.governor import AutonomyGovernor
  - from bridge_backend.engines.autonomy.models import Incident, Decision


### ./bridge_backend/tests/test_cascade.py
  - from fastapi.testclient import TestClient
  - from main import app
  - from bridge_core.engines.cascade import service


### ./bridge_backend/tests/test_genesis_topics.py
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/tests/test_github_forge.py
  - import pytest
  - from pathlib import Path
  - from bridge_backend.engines.github_forge.core import GitHubForge


### ./bridge_backend/tests/test_db_manager.py
  - import pytest
  - import asyncio
  - from bridge_backend.bridge_core.db import db_manager


### ./bridge_backend/tests/test_micro_scribe.py
  - import pytest
  - from bridge_backend.bridge_engines.micro_scribe import (


### ./bridge_backend/tests/test_hxo_v196p.py
  - import unittest
  - from unittest.mock import AsyncMock, MagicMock, patch
  - from datetime import datetime, UTC
  - import asyncio
  - import sys
  - from pathlib import Path
  - from bridge_core.engines.adapters.hxo_genesis_link import (
  - from bridge_backend.bridge_core.engines.adapters import hxo_genesis_link


### ./bridge_backend/tests/test_indoctrination_engine.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_protocols_routes_lore_policy.py
  - from fastapi.testclient import TestClient
  - from pathlib import Path
  - from main import app
  - from bridge_backend.bridge_core.protocols import registry


### ./bridge_backend/tests/test_netlify_validator.py
  - import pytest
  - import asyncio
  - from bridge_backend.engines.netlify_validator import NetlifyValidator
  - from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
  - from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
  - from bridge_backend.engines.netlify_validator import validate_netlify_rules


### ./bridge_backend/tests/test_creativity.py
  - from fastapi.testclient import TestClient
  - from pathlib import Path
  - import json
  - from importlib import reload
  - import tempfile
  - import pytest
  - from importlib import reload
  - import bridge_core.engines.creativity.service as svc
  - import bridge_core.engines.creativity.routes as routes
  - from bridge_backend.main import app
  - from importlib import reload
  - import bridge_core.engines.creativity.service as svc
  - import bridge_core.engines.creativity.routes as routes
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_vaulting.py
  - import os
  - import json
  - import pytest
  - import tempfile
  - from pathlib import Path
  - from datetime import datetime
  - from bridge_backend.bridge_core.protocols.vaulting import seal, get_vault_dir


### ./bridge_backend/tests/test_autonomy_comprehensive_integration.py
  - import pytest
  - import asyncio
  - from unittest.mock import AsyncMock, MagicMock, patch
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.adapters.genesis_link import register_all_genesis_links
  - from bridge_backend.bridge_core.engines.adapters.super_engines_autonomy_link import (
  - from bridge_backend.bridge_core.engines.adapters.super_engines_autonomy_link import (
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.adapters.tools_runtime_autonomy_link import (
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.bridge_core.engines.adapters.heritage_mas_autonomy_link import (
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/tests/test_envsync_pipeline.py
  - import sys
  - import subprocess
  - from pathlib import Path
  - from bridge_backend.cli import genesisctl
  - import bridge_backend.diagnostics.verify_env_sync as verify_module
  - from bridge_backend.engines.envrecon.hubsync import hubsync


### ./bridge_backend/tests/test_integrity_audit.py
  - import os
  - import sys
  - import json
  - import tempfile
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock
  - import integrity_audit


### ./bridge_backend/tests/test_github_envhook.py
  - import unittest
  - import tempfile
  - import json
  - import asyncio
  - from pathlib import Path
  - from datetime import datetime, UTC
  - import sys
  - from github_envhook import EnvironmentFileWatcher
  - import shutil


### ./bridge_backend/tests/test_sovereign_guard.py
  - import pytest
  - from datetime import datetime, UTC
  - from bridge_backend.bridge_engines.sovereign_guard import (


### ./bridge_backend/tests/test_fault_injection.py
  - import pytest
  - from bridge_core.heritage.mas.fault_injector import FaultInjector
  - import asyncio
  - import asyncio
  - import asyncio


### ./bridge_backend/tests/test_leviathan_solver.py
  - from fastapi.testclient import TestClient
  - from pathlib import Path
  - import json, shutil
  - from bridge_backend.main import app
  - from main import app
  - import bridge_core.engines.leviathan.solver as solver_module
  - # Also patch load_chunk_text to read from our temp parser chunks


### ./bridge_backend/tests/smoke_test_solver.py
  - import sys
  - import os
  - import json
  - import unittest.mock as mock
  - from bridge_core.engines.leviathan.solver import solve, SolveRequest
  - from bridge_core.engines.leviathan.solver import (


### ./bridge_backend/tests/test_signing_roundtrip.py
  - import os
  - import tempfile
  - import pytest
  - import json
  - from datetime import datetime
  - from bridge_backend.src.keys import SovereignKeys
  - from bridge_backend.src.signer import AtomicSigner, BatchSigner, create_signer


### ./bridge_backend/tests/test_autonomy_routes.py
  - import pytest
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_reflex_loop.py
  - import pytest
  - import json
  - import os
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from datetime import datetime, timezone
  - # Import modules from autonomy_node
  - import sys
  - import signer
  - import verifier
  - import reflex
  - pytest.skip(f"Could not import autonomy_node modules: {e}", allow_module_level=True)
  - """Test complete reflex cycle from report to queued PR"""


### ./bridge_backend/tests/test_leviathan.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - import shutil
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.leviathan.service import LeviathanEngine


### ./bridge_backend/tests/test_recovery_orchestrator.py
  - from fastapi.testclient import TestClient
  - from pathlib import Path
  - import json
  - import tempfile
  - import os
  - from bridge_backend.main import app
  - from main import app


### ./bridge_backend/tests/test_envsync_engine.py
  - import asyncio, os
  - import pytest
  - from bridge_core.engines.envsync.diffs import compute_diff
  - from bridge_core.engines.envsync.engine import load_canonical, _is_included
  - from bridge_core.engines.envsync.config import CONFIG
  - """Test that canonical source loads from environment"""


### ./bridge_backend/tests/test_relay_mailer.py
  - import pytest
  - import os
  - import json
  - from pathlib import Path
  - from utils.relay_mailer import RelayMailer, relay_mailer


### ./bridge_backend/tests/test_arie_autonomous_integration.py
  - import unittest
  - import asyncio
  - import tempfile
  - import shutil
  - import os
  - import importlib.util
  - from pathlib import Path
  - from unittest.mock import Mock, AsyncMock, patch
  - from datetime import datetime, UTC
  - import sys
  - from engines.arie.scheduler import ARIEScheduler
  - from engines.arie.core import ARIEEngine
  - from engines.arie.models import PolicyType, Summary, Patch
  - from unittest.mock import patch as mock_patch
  - from engines.arie.models import Rollback


### ./bridge_backend/tests/test_license_scanner.py
  - import sys
  - from pathlib import Path
  - from utils.license_scanner import guess_license_for_text


### ./bridge_backend/tests/test_umbra_memory.py
  - import pytest
  - import asyncio
  - from datetime import datetime, timezone
  - from bridge_backend.bridge_core.engines.umbra.memory import UmbraMemory
  - """Test pattern learning from experiences"""


### ./bridge_backend/tests/test_missions_routes.py
  - from fastapi.testclient import TestClient
  - from main import app
  - from pathlib import Path
  - import json
  - import uuid


### ./bridge_backend/tests/test_system_routes.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_route_sweep.py
  - import sys
  - import subprocess
  - from pathlib import Path


### ./bridge_backend/tests/test_leviathan_unified.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path
  - import json
  - # Remove the test entries from ledger and truths


### ./bridge_backend/tests/test_solver_minimal.py
  - import sys
  - import os
  - # Mock aiohttp to avoid import errors
  - import unittest.mock as mock
  - from bridge_core.engines.leviathan.solver import solve, SolveRequest
  - import traceback


### ./bridge_backend/tests/test_brain.py
  - import os
  - import tempfile
  - import pytest
  - import json
  - from datetime import datetime
  - from bridge_backend.src.brain import BrainLedger, create_brain_ledger
  - from bridge_backend.src.keys import SovereignKeys, initialize_admiral_keys
  - from bridge_backend.src.signer import create_signer


### ./bridge_backend/tests/test_envscribe.py
  - import sys
  - import subprocess
  - from pathlib import Path
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envscribe.models import (
  - from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter
  - from bridge_backend.engines.envscribe.routes import router
  - from bridge_backend.cli import envscribectl
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter
  - from bridge_backend.engines.envscribe.models import EnvScribeReport, EnvScribeSummary, EnvVariable


### ./bridge_backend/tests/test_envrecon.py
  - import pytest
  - import sys
  - from pathlib import Path
  - from engines.envrecon import EnvReconEngine
  - print(f"❌ Failed to import EnvRecon: {e}")
  - from engines.envrecon.core import EnvReconEngine
  - from engines.envrecon.core import EnvReconEngine
  - from engines.envrecon.core import EnvReconEngine
  - from engines.envrecon.hubsync import hubsync
  - print(f"❌ Failed to import HubSync: {e}")
  - from engines.envrecon.autoheal import autoheal
  - print(f"❌ Failed to import AutoHeal: {e}")
  - from engines.envrecon.routes import router
  - print(f"❌ Failed to import routes: {e}")
  - from engines.envrecon.ui import ui_router
  - print(f"❌ Failed to import UI: {e}")


### ./bridge_backend/tests/test_truth_engine.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path
  - import json, hashlib


### ./bridge_backend/tests/test_firewall_sovereignty.py
  - import os
  - import sys
  - import pytest
  - import json
  - import yaml
  - from pathlib import Path
  - from bridge_backend.tools.firewall_sovereignty.firewall_config_manager import FirewallConfigManager
  - from bridge_backend.tools.firewall_sovereignty.network_resilience import NetworkResilienceLayer
  - from bridge_backend.tools.firewall_sovereignty.validation_sovereignty import ValidationSovereignty
  - from bridge_backend.tools.firewall_sovereignty.script_execution import ScriptExecutionSovereignty
  - """Test removing domain from allowlist"""


### ./bridge_backend/tests/test_pr_summary.py
  - import pytest
  - import json
  - import tempfile
  - from pathlib import Path
  - from bridge_backend.cli.selftest_summary import (


### ./bridge_backend/tests/test_runtime_guards.py
  - import pytest
  - import os
  - import sys
  - import tempfile
  - import pathlib
  - from runtime.wait_for_db import wait_for_db
  - from runtime.wait_for_db import wait_for_db
  - from runtime.egress_canary import HOSTS
  - from runtime.egress_canary import check_host
  - from runtime.run_migrations import run_migrations
  - from runtime.run_migrations import run_migrations
  - from runtime.health_probe import warm_health
  - from runtime.telemetry import TELEMETRY
  - from runtime.telemetry import TELEMETRY
  - from runtime.telemetry import TELEMETRY
  - from runtime.retry import retry, RetryError
  - from runtime.retry import retry
  - from runtime.retry import retry
  - from runtime.retry import retry, RetryError


### ./bridge_backend/tests/test_total_stack_triage.py
  - import pytest
  - import json
  - import pathlib
  - import subprocess
  - import os
  - import yaml
  - import yaml
  - import yaml
  - import yaml
  - import yaml
  - import yaml
  - assert "from _net import http, dns_warmup" in code
  - import yaml


### ./bridge_backend/tests/test_envrecon_autonomy_integration.py
  - import sys
  - from pathlib import Path
  - from bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
  - print(f"❌ Failed to import adapter: {e}")
  - from bridge_core.engines.adapters.envrecon_autonomy_link import envrecon_autonomy_link
  - from genesis.bus import genesis_bus
  - import inspect
  - from engines.envrecon.core import EnvReconEngine
  - import inspect
  - from engines.envrecon.autoheal import AutoHealEngine
  - import inspect
  - from engines.envrecon import routes


### ./bridge_backend/tests/test_autonomy_genesis_link.py
  - import pytest
  - from unittest.mock import Mock, AsyncMock, patch
  - from bridge_backend.bridge_core.engines.adapters.autonomy_genesis_link import (


### ./bridge_backend/tests/test_heritage_bus.py
  - import pytest
  - import asyncio
  - from bridge_core.heritage.event_bus import bus


### ./bridge_backend/tests/test_umbra_echo.py
  - import pytest
  - import asyncio
  - from datetime import datetime, timezone
  - from bridge_backend.bridge_core.engines.umbra.echo import UmbraEcho


### ./bridge_backend/tests/test_activity_routes.py
  - from fastapi.testclient import TestClient
  - import sys
  - from pathlib import Path
  - from main import app
  - import json


### ./bridge_backend/tests/test_protocols_routes_invoke_stub.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_umbra_core.py
  - import pytest
  - import asyncio
  - from datetime import datetime, timezone
  - from bridge_backend.bridge_core.engines.umbra.core import UmbraCore


### ./bridge_backend/tests/test_federation_smoke.py
  - import pytest
  - import asyncio
  - from bridge_core.heritage.federation.federation_client import FederationClient


### ./bridge_backend/tests/test_permissions_routes.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path
  - import json
  - import importlib
  - import bridge_backend.bridge_core.permissions.store as store
  - import bridge_backend.bridge_core.permissions.routes as routes
  - import bridge_backend.bridge_core.permissions.store as store
  - import bridge_backend.bridge_core.permissions.routes as routes


### ./bridge_backend/tests/test_filing_engine.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_vault_routes.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path


### ./bridge_backend/tests/test_hxo_genesis_link.py
  - import asyncio
  - import pytest
  - from bridge_backend.bridge_core.engines.adapters.hxo_genesis_link import HXOGenesisLink


### ./bridge_backend/tests/test_inspector_ui.py
  - import sys
  - from pathlib import Path
  - from engines.envrecon.ui import ui_router
  - print(f"❌ Failed to import UI router: {e}")
  - from engines.envrecon.ui import inspector_panel


### ./bridge_backend/tests/test_arie_routes.py
  - import unittest
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from unittest.mock import AsyncMock, MagicMock, patch
  - import sys
  - from fastapi.testclient import TestClient
  - from fastapi import FastAPI
  - from engines.arie.routes import router, get_engine
  - from engines.arie.models import PolicyType, ScanRequest, RollbackRequest
  - from engines.arie.routes import _engine


### ./bridge_backend/tests/test_push_permissions.py
  - import pytest
  - import importlib
  - from fastapi.testclient import TestClient
  - import sys
  - from pathlib import Path
  - from bridge_backend.main import app
  - import bridge_backend.bridge_core.permissions.store as store
  - import bridge_backend.bridge_core.permissions.routes as routes
  - import bridge_backend.bridge_core.permissions.store as store
  - import bridge_backend.bridge_core.permissions.routes as routes
  - import bridge_backend.bridge_core.permissions.store as store
  - import bridge_backend.bridge_core.permissions.routes as routes


### ./bridge_backend/tests/test_protocols_routes_seal.py
  - from fastapi.testclient import TestClient
  - from main import app
  - from pathlib import Path
  - import json
  - from bridge_backend.bridge_core.protocols import vaulting


### ./bridge_backend/tests/test_chimera_engine.py
  - import pytest
  - import asyncio
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.chimera import (
  - from bridge_backend.bridge_core.engines.chimera.simulator import BuildSimulator
  - from bridge_backend.bridge_core.engines.chimera.simulator import BuildSimulator
  - from bridge_backend.bridge_core.engines.chimera.healer import ConfigurationHealer
  - from bridge_backend.bridge_core.engines.chimera.healer import ConfigurationHealer
  - from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
  - from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
  - from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
  - from bridge_backend.bridge_core.engines.chimera.certifier import DeploymentCertifier
  - from bridge_backend.genesis.bus import GenesisEventBus


### ./bridge_backend/tests/test_agents_foundry.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app
  - from pathlib import Path
  - import json
  - import shutil
  - # reimport service to rebind default instance in routes
  - from importlib import reload
  - import bridge_backend.bridge_core.engines.agents_foundry.service as svc
  - import bridge_backend.bridge_core.engines.agents_foundry.routes as routes


### ./bridge_backend/tests/test_firewall_watchdog.py
  - import os
  - import sys
  - import json
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock
  - import firewall_watchdog


### ./bridge_backend/tests/test_protocols_storage.py
  - from pathlib import Path
  - import json
  - from bridge_backend.bridge_core.protocols import registry, storage


### ./bridge_backend/tests/test_arie_engine.py
  - import unittest
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from datetime import datetime, UTC
  - import sys
  - from engines.arie.core import (
  - from engines.arie.models import PolicyType, Severity
  - test_file.write_text("from datetime import datetime\ntimestamp = datetime.utcnow()")
  - self.assertIn("from datetime import datetime, UTC", content)
  - test_file.write_text("from datetime import datetime\ntimestamp = datetime.utcnow()")


### ./bridge_backend/tests/test_guardians_routes.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_reflex_guardrails.py
  - import os
  - import os.path
  - # Check if running from repo root or test directory


### ./bridge_backend/tests/test_deep_seek_triage.py
  - import pytest
  - import json
  - import pathlib
  - import subprocess
  - import os
  - import yaml


### ./bridge_backend/tests/test_chimera_preflight.py
  - import unittest
  - import asyncio
  - from pathlib import Path
  - import tempfile
  - import shutil
  - import sys
  - from engines.chimera.core import ChimeraEngine
  - from engines.chimera.core import ChimeraEngine
  - from engines.chimera.core import ChimeraEngine
  - from engines.chimera.core import ChimeraEngine
  - from engines.chimera.core import ChimeraEngine
  - from engines.chimera.core import ChimeraEngine
  - from engines.chimera.models import RedirectRule


### ./bridge_backend/tests/test_envscribe_integration.py
  - import sys
  - import asyncio
  - from pathlib import Path
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envscribe.routes import _notify_genesis_scan_complete
  - import traceback
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envrecon.core import EnvReconEngine
  - # Mock a basic reconciliation (won't actually fetch from APIs without credentials)
  - import traceback
  - from bridge_backend.engines.envscribe.core import EnvScribeEngine
  - from bridge_backend.engines.envscribe.emitters import EnvScribeEmitter
  - from pathlib import Path
  - import traceback


### ./bridge_backend/tests/test_umbra_triage_healers.py
  - import pytest
  - import asyncio
  - from bridge_backend.engines.umbra.healers import UmbraHealers
  - from bridge_backend.engines.umbra.models import HealPlan, HealAction, TriageTicket, TriageSeverity, TriageStatus, TriageKind


### ./bridge_backend/tests/test_screen_engine.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_autonomy_engine.py
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_fleet_routes.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/tests/test_steward.py
  - import pytest
  - from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
  - from bridge_backend.engines.steward.models import (
  - from bridge_backend.engines.steward.core import steward
  - from bridge_backend.engines.steward.adapters import (
  - from bridge_backend.genesis.bus import GenesisEventBus
  - import os
  - import importlib
  - # Reimport to pick up env vars
  - import bridge_backend.engines.steward.core as steward_core


### ./bridge_backend/tests/test_protocols_registry_flags.py
  - from pathlib import Path
  - from bridge_backend.bridge_core.protocols import registry


### ./bridge_backend/tests/test_autonomy_integration.py
  - import pytest
  - import asyncio
  - from unittest.mock import Mock, AsyncMock, patch
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.adapters.genesis_link import _register_autonomy_link
  - from bridge_backend.bridge_core.engines.adapters.genesis_link import _register_autonomy_link
  - from bridge_backend.bridge_core.engines.adapters.genesis_link import _register_autonomy_link
  - import sys
  - import os
  - from genesis.bus import GenesisEventBus


### ./bridge_backend/tests/smoke_test_umbra.py
  - import sys
  - import os
  - from fastapi.testclient import TestClient
  - from bridge_backend.main import app


### ./bridge_backend/tests/test_invoke_backend.py
  - from bridge_backend.bridge_core.protocols.invoke import invoke_protocol, _seal_path
  - from bridge_backend.bridge_core.protocols.registry import activate_protocol, vault_protocol, get_entry
  - import json


### ./bridge_backend/tests/test_imports.py
  - import sys
  - from pathlib import Path
  - from bridge_backend.db.bootstrap import auto_sync_schema
  - print(f"❌ Failed to import bootstrap: {e}")
  - from bridge_backend.middleware.headers import HeaderSyncMiddleware
  - print(f"❌ Failed to import middleware: {e}")
  - from bridge_backend.runtime.heartbeat import send_heartbeat, run
  - print(f"❌ Failed to import heartbeat: {e}")
  - from bridge_backend.db import bootstrap
  - from bridge_backend.middleware import headers


### ./bridge_backend/tests/test_badgegen.py
  - import pytest
  - import tempfile
  - import json
  - from pathlib import Path
  - from bridge_backend.cli.badgegen import (
  - import os


### ./bridge_backend/tests/test_health_record.py
  - import pytest
  - import json
  - import tempfile
  - import os
  - from pathlib import Path
  - from datetime import datetime, timedelta, timezone
  - from bridge_backend.metrics.health_record import (


### ./bridge_backend/tests/test_custody_routes.py
  - from fastapi.testclient import TestClient
  - from main import app


### ./bridge_backend/webhooks/deployment_webhooks.py
  - from fastapi import APIRouter, Request, HTTPException, Header
  - from typing import Optional, Dict, Any
  - from datetime import datetime, UTC
  - import logging
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.bus import genesis_bus


### ./bridge_backend/webhooks/__init__.py


### ./bridge_backend/webhooks/netlify.py
  - from fastapi import APIRouter, Request, HTTPException, Header
  - from typing import Optional
  - import logging
  - import os
  - import hmac
  - import hashlib
  - signature: Signature from header (format: "sha256=...")
  - Processes deploy and build signals from Netlify and emits to Umbra Triage Mesh
  - import json
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.umbra.core import UmbraTriageCore


### ./bridge_backend/webhooks/github.py
  - from fastapi import APIRouter, Request, HTTPException, Header
  - from typing import Optional
  - import logging
  - import os
  - import hmac
  - import hashlib
  - signature: Signature from header (format: "sha256=...")
  - import json
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.umbra.core import UmbraTriageCore


### ./bridge_backend/bridge_engines/sovereign_guard.py
  - import hmac
  - import hashlib
  - import logging
  - import os
  - from datetime import datetime, UTC
  - from typing import Dict, Any, Optional, List
  - from pydantic import BaseModel
  - # Try to get resonance from Genesis bus or bridge core
  - import json
  - from pathlib import Path
  - import os


### ./bridge_backend/bridge_engines/micro_logician.py
  - import logging
  - import os
  - import re
  - from datetime import datetime, UTC
  - from typing import Dict, Any, List, Optional, Set
  - from pydantic import BaseModel
  - from collections import defaultdict, Counter
  - from enum import Enum
  - from .sovereign_guard import SovereignComplianceGuard
  - ThreatLevel.CRITICAL: "⚠️ IMMEDIATE ACTION REQUIRED: Remove sensitive data from logs, rotate credentials",
  - """Analyze performance metrics from logs"""
  - """Detect peak activity period from timestamps"""
  - """Extract common patterns from logs"""
  - # Base confidence from resonance


### ./bridge_backend/bridge_engines/EXAMPLE.py
  - import sys
  - from pathlib import Path
  - from bridge_backend.bridge_engines.sovereign_guard import SovereignComplianceGuard
  - from bridge_backend.bridge_engines.micro_scribe import SovereignMicroScribe
  - from bridge_backend.bridge_engines.micro_logician import SovereignMicroLogician
  - import traceback


### ./bridge_backend/bridge_engines/micro_scribe.py
  - import logging
  - import os
  - import re
  - from datetime import datetime, UTC
  - from typing import Dict, Any, List, Optional, Tuple
  - from pydantic import BaseModel
  - from enum import Enum
  - from .sovereign_guard import SovereignComplianceGuard
  - diff_analysis: Analysis result from analyze_diff


### ./bridge_backend/bridge_engines/__init__.py


### ./bridge_backend/src/keys.py
  - import os
  - import base64
  - from typing import Tuple, Optional
  - from nacl.signing import SigningKey, VerifyKey
  - from nacl.encoding import Base64Encoder, RawEncoder
  - from nacl.exceptions import BadSignatureError
  - import json
  - from datetime import datetime, timezone
  - """Load signing key from disk"""
  - """Load verify key from disk"""
  - import sys


### ./bridge_backend/src/keyless_auth.py
  - import os
  - import secrets
  - import hashlib
  - from datetime import datetime, timezone, timedelta
  - from typing import Optional, Dict, Any
  - from nacl.signing import SigningKey, VerifyKey
  - from nacl.encoding import Base64Encoder
  - """Remove expired sessions from memory"""


### ./bridge_backend/src/brain.py
  - import os
  - import sqlite3
  - import json
  - from typing import Dict, Any, List, Optional, Tuple
  - from datetime import datetime, timedelta, timezone
  - from dataclasses import dataclass
  - from contextlib import contextmanager
  - from .signer import AtomicSigner, create_signer
  - import sys


### ./bridge_backend/src/brain_cli.py
  - import sys
  - import json
  - import argparse
  - from typing import Dict, Any
  - from tabulate import tabulate
  - from datetime import datetime
  - from .brain import create_brain_ledger, BrainLedger
  - from .keys import SovereignKeys, initialize_admiral_keys
  - from .signer import create_signer


### ./bridge_backend/src/export_and_sign.py
  - import os
  - import json
  - import shutil
  - import zipfile
  - from typing import Dict, Any, List
  - from datetime import datetime
  - from pathlib import Path
  - from .brain import create_brain_ledger
  - from .signer import create_signer
  - from .keys import initialize_admiral_keys
  - import hashlib
  - import platform
  - import sys
  - import sys
  - import argparse


### ./bridge_backend/src/__init__.py
  - from .keys import SovereignKeys, initialize_admiral_keys
  - from .signer import AtomicSigner, BatchSigner, create_signer
  - from .brain import BrainLedger, create_brain_ledger
  - from .export_and_sign import DockDayExporter, create_dock_day_exporter


### ./bridge_backend/src/signer.py
  - import json
  - import hashlib
  - from typing import Dict, Any, Optional, Tuple
  - from datetime import datetime, timezone
  - from nacl.signing import SigningKey, VerifyKey
  - from nacl.encoding import Base64Encoder
  - from nacl.exceptions import BadSignatureError
  - from .keys import SovereignKeys
  - from .keys import initialize_admiral_keys
  - import sys


### ./.archive/render_legacy/render_webhook.py
  - from fastapi import APIRouter, Request, HTTPException, Header
  - from typing import Optional
  - import logging
  - import os
  - import hmac
  - import hashlib
  - signature: Signature from header
  - Processes deploy and build signals from Render and emits to Umbra Triage Mesh
  - import json
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.engines.umbra.core import UmbraTriageCore


### ./.archive/render_legacy/render_envsync_provider.py
  - import os, httpx
  - from typing import Dict, List
  - from .base import ProviderBase
  - from ..discovery.chain import discover_token


### ./.archive/render_legacy/test_render_fallback.py
  - import pytest
  - import asyncio
  - from bridge_backend.engines.render_fallback.core import RenderFallback


### ./.archive/render_legacy/render_fallback_adapter.py
  - from typing import Dict, Any
  - from ...render_fallback.core import RenderFallback as RenderFallbackCore


### ./.archive/render_legacy/render_adapter.py
  - import os
  - import logging


### ./tests/test_captain_agent_separation.py
  - import pytest
  - import json
  - from pathlib import Path
  - from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX


### ./tests/test_secret_forge.py
  - import os
  - import time
  - import pytest
  - from bridge_backend.bridge_core.token_forge_dominion import (
  - from bridge_backend.bridge_core.token_forge_dominion import retrieve_forge_dominion_root
  - from bridge_backend.bridge_core.token_forge_dominion import retrieve_forge_dominion_root
  - from bridge_backend.bridge_core.token_forge_dominion.bootstrap import bootstrap_dominion_root
  - from bridge_backend.bridge_core.token_forge_dominion import QuantumAuthority, generate_root_key
  - """Test extracting metadata from token."""
  - """Test extracting metadata from token without metadata."""
  - from datetime import datetime, timezone


### ./tests/integration_test_genesis_linkage.py
  - import asyncio
  - import sys
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
  - from bridge_backend.bridge_core.engines.blueprint.adapters import tde_link, cascade_link, truth_link, autonomy_link


### ./tests/test_umbra_routes.py
  - import pytest
  - from fastapi.testclient import TestClient
  - from datetime import datetime, timezone
  - from bridge_backend.main import app


### ./tests/test_forge_dominion_v197s.py
  - import os
  - import pytest
  - import tempfile
  - from pathlib import Path
  - from bridge_backend.bridge_core.token_forge_dominion import (
  - from bridge_backend.bridge_core.token_forge_dominion.bootstrap import (
  - from bridge_backend.bridge_core.token_forge_dominion.scan_envs import (
  - from bridge_backend.bridge_core.token_forge_dominion import generate_ephemeral_token
  - import time


### ./tests/test_blueprint_engine.py
  - import pytest
  - from bridge_backend.bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine
  - from bridge_backend.bridge_core.engines.blueprint.planner_rules import derive_objectives, explode_tasks
  - """Test task explosion from objectives"""
  - """Test agent job generation from plan"""


### ./tests/test_bridge_core_ci.py
  - import pytest
  - import sys
  - from pathlib import Path
  - from bridge_core.self_heal import guard
  - from bridge_core.self_heal.guard import check_core_validation
  - from bridge_core.lattice import heartbeat
  - from bridge_core.lattice.heartbeat import run_federation_heartbeat
  - from bridge_core.lattice import pathcheck
  - from bridge_core.lattice.pathcheck import verify_deployment_paths
  - from bridge_core.security import validate_token
  - from bridge_core.security.validate_token import validate_dominion_token
  - from bridge_core.security.validate_token import validate_dominion_token
  - import bridge_core
  - from bridge_core.self_heal import guard
  - from bridge_core.lattice import heartbeat, pathcheck
  - from bridge_core.security import validate_token


### ./tests/test_unified_runtime_v195.py
  - import os
  - import sys
  - import pytest
  - from pathlib import Path
  - assert "from bridge_backend.runtime.parity import run_parity_sync" in content
  - from runtime.heartbeat import ensure_httpx
  - pytest.skip("Could not import heartbeat module in test environment")
  - from runtime.heartbeat import record_repair
  - pytest.skip("Could not import heartbeat module in test environment")
  - from runtime.parity import run_parity_sync
  - pytest.skip("Could not import parity module in test environment")
  - from runtime.parity import verify_cors_parity
  - pytest.skip("Could not import parity module in test environment")


### ./tests/test_anchorhold_protocol.py
  - import os
  - import sys
  - import pytest
  - from pathlib import Path
  - from runtime.heartbeat import start_heartbeat, bridge_heartbeat
  - import inspect
  - from runtime.heartbeat import HEARTBEAT_INTERVAL
  - # Should have CORS_ALLOW_ORIGINS from environment


### ./tests/test_zero_trust_validation.py
  - import os
  - import pytest
  - from pathlib import Path
  - from bridge_backend.bridge_core.token_forge_dominion import (
  - from bridge_backend.bridge_core.token_forge_dominion import generate_ephemeral_token
  - import os
  - (tmp_path / "app.py").write_text("import os\napi_key = os.getenv('API_KEY')")


### ./tests/test_v196c_features.py
  - import pytest
  - import os
  - from pathlib import Path
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import check_listen
  - from bridge_backend.routes.health import router
  - from bridge_backend.routes.health import router
  - from bridge_backend.routes.health import router
  - assert "from bridge_backend.runtime.ports import resolve_port" in content, \
  - "main.py should import resolve_port"
  - from bridge_backend.bridge_core.engines.blueprint.routes import router
  - from bridge_backend.bridge_core.engines.blueprint.routes import router


### ./tests/test_v196i_features.py
  - import os
  - import sys
  - import time
  - import asyncio
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock, AsyncMock
  - import tempfile
  - import shutil
  - from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
  - from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
  - from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
  - from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
  - from bridge_backend.runtime.temporal_stage_manager import TemporalStageManager
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_deploy import stage1_minimal_health, tdb
  - from bridge_backend.runtime.temporal_deploy import stage2_core_bootstrap, tdb
  - from bridge_backend.runtime.temporal_deploy import stage3_federation_warmup, tdb
  - from bridge_backend.runtime.temporal_deploy import STAGE_1_PORT
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_stage_manager import (
  - from bridge_backend.runtime.temporal_deploy import TemporalDeployBuffer
  - import json
  - from bridge_backend.runtime.temporal_stage_manager import (
  - # Re-import to get fresh value
  - import importlib
  - from bridge_backend.runtime import temporal_deploy
  - # Re-import to get fresh value
  - import importlib
  - from bridge_backend.runtime import temporal_deploy
  - from bridge_backend.routes.health import health_live
  - from bridge_backend.routes.health import health_stage


### ./tests/test_codex_engine.py
  - import pytest
  - import os
  - import json
  - from codex.truth_engine import gather_meta, validate_facts
  - from codex.parser_engine import parse_docs
  - from codex.blueprint_engine import build_blueprint
  - """Test gathering metadata from YAML files."""
  - from codex.compiler import compile_codex
  - from codex.markdown_compiler import compile_markdown
  - from codex.html_compiler import build_html


### ./tests/deployment_readiness_v197c.py
  - import sys
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
  - from bridge_backend.bridge_core.engines.blueprint.adapters import tde_link
  - from bridge_backend.bridge_core.engines.blueprint.adapters import cascade_link
  - from bridge_backend.bridge_core.engines.blueprint.adapters import truth_link
  - from bridge_backend.bridge_core.engines.blueprint.adapters import autonomy_link
  - from bridge_backend.bridge_core.engines.routes_linked import router
  - print("   ✅ All modules import successfully")
  - from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
  - from bridge_backend.bridge_core.engines.routes_linked import router


### ./tests/test_genesis_v2_0_1.py
  - import pytest
  - import pytest_asyncio
  - import asyncio
  - import os
  - from datetime import datetime, timedelta
  - from pathlib import Path
  - from bridge_backend.genesis.contracts import GenesisEvent
  - from bridge_backend.genesis.contracts import GenesisEvent
  - from bridge_backend.genesis.contracts import GenesisEvent
  - from bridge_backend.genesis.adapters import emit_intent
  - from bridge_backend.genesis.adapters import emit_heal
  - from bridge_backend.genesis.adapters import emit_fact
  - from bridge_backend.genesis.adapters import health_degraded
  - from bridge_backend.genesis.adapters import deploy_failed
  - from bridge_backend.genesis.persistence import genesis_persistence
  - from bridge_backend.genesis.persistence import genesis_persistence
  - from bridge_backend.genesis.persistence import genesis_persistence
  - import time
  - from bridge_backend.genesis.persistence import genesis_persistence
  - from bridge_backend.genesis.persistence import genesis_persistence
  - from bridge_backend.bridge_core.guardians.gate import guardians_gate
  - from bridge_backend.bridge_core.guardians.gate import guardians_gate
  - from bridge_backend.bridge_core.guardians.gate import guardians_gate
  - from bridge_backend.bridge_core.guardians.gate import guardians_gate
  - from bridge_backend.genesis.replay import genesis_replay
  - """Test replay from watermark"""
  - from bridge_backend.genesis.replay import genesis_replay
  - from bridge_backend.genesis.persistence import genesis_persistence
  - # Replay from beginning (without re-emitting)
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
  - from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
  - from bridge_backend.runtime.tde_x.orchestrator_v2 import tde_orchestrator
  - import time


### ./tests/test_keyless_security.py
  - from bridge_backend.src.keyless_auth import KeylessAuthHandler, establish_session, verify_capability
  - # Try alternative import paths
  - import sys
  - import os
  - from bridge_backend.src.keyless_auth import KeylessAuthHandler, establish_session, verify_capability


### ./tests/test_forge_cascade_synchrony.py
  - import os
  - import pytest
  - from pathlib import Path
  - from bridge_backend.forge import forge_integrate_engines, get_forge_status
  - from bridge_backend.forge import get_forge_status
  - from bridge_backend.forge.forge_core import load_forge_registry
  - from bridge_backend.forge.forge_core import discover_engine_paths
  - from bridge_backend.forge import forge_integrate_engines
  - from bridge_backend.forge import forge_integrate_engines
  - from bridge_backend.forge.synchrony import get_synchrony_status, synchrony
  - from bridge_backend.forge.synchrony import get_synchrony_status
  - from bridge_backend.forge.synchrony import CascadeSynchrony
  - from bridge_backend.forge.synchrony import CascadeSynchrony
  - from bridge_backend.forge.synchrony import CascadeSynchrony
  - from bridge_backend.forge.synchrony import CascadeSynchrony
  - from bridge_backend.forge.synchrony import CascadeSynchrony
  - import json
  - import json
  - import json
  - import json


### ./tests/test_selftest_v197j.py
  - import os
  - import sys
  - import json
  - import asyncio
  - import pytest
  - from pathlib import Path
  - from bridge_backend.engines.selftest import SelfTestController, AutoHealTrigger
  - pytest.fail(f"Failed to import selftest modules: {e}")
  - from bridge_backend.engines.selftest.core import SelfTestController
  - from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger
  - from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger
  - from bridge_backend.engines.selftest.core import SelfTestController
  - from bridge_backend.engines.selftest.autoheal_trigger import AutoHealTrigger
  - from bridge_backend.genesis.bus import GenesisEventBus
  - from bridge_backend.engines.selftest.core import SelfTestController
  - from bridge_backend.cli import genesisctl
  - pytest.fail(f"Failed to import genesisctl: {e}")
  - from bridge_backend.cli import genesisctl
  - import yaml


### ./tests/test_forge_manifest_resolver.py
  - import os
  - import json
  - import time
  - import hmac
  - import hashlib
  - import pytest
  - from unittest.mock import Mock, patch, MagicMock
  - # Simulate the signature generation from forge-resolver.js
  - from brh.heartbeat_daemon import forge_sig
  - from brh.heartbeat_daemon import forge_sig
  - from brh.heartbeat_daemon import forge_sig
  - import requests
  - from brh.heartbeat_daemon import start
  - from brh.heartbeat_daemon import start
  - from pathlib import Path
  - import yaml
  - from pathlib import Path
  - import yaml
  - from pathlib import Path
  - from pathlib import Path
  - assert "from brh import heartbeat_daemon" in content


### ./tests/test_v196g_features.py
  - import os
  - import sys
  - import time
  - import json
  - import tempfile
  - import shutil
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock
  - from datetime import datetime, timedelta
  - from bridge_backend.runtime.predictive_stabilizer import detect_environment
  - from bridge_backend.runtime.predictive_stabilizer import detect_environment
  - from bridge_backend.runtime.predictive_stabilizer import detect_environment
  - from bridge_backend.runtime.predictive_stabilizer import is_live
  - from bridge_backend.runtime.predictive_stabilizer import is_live
  - from bridge_backend.runtime.predictive_stabilizer import is_live
  - from bridge_backend.runtime.predictive_stabilizer import is_live
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime import predictive_stabilizer
  - import statistics
  - from bridge_backend.runtime.predictive_stabilizer import queue_anomaly, _anomaly_queue
  - from bridge_backend.runtime.predictive_stabilizer import queue_anomaly, _anomaly_queue, ANOMALY_QUEUE_THRESHOLD
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime import predictive_stabilizer
  - from bridge_backend.runtime.predictive_stabilizer import aggregate_to_daily_report
  - from bridge_backend.runtime.predictive_stabilizer import (
  - from bridge_backend.runtime.startup_watchdog import StartupWatchdog
  - from bridge_backend.runtime.ports import get_adaptive_prebind_delay
  - # Adaptive delay from environment
  - import pytest


### ./tests/test_db_url_guard.py
  - import os
  - import sys
  - import pytest
  - from pathlib import Path
  - from runtime.db_url_guard import normalize


### ./tests/test_v197c_genesis_linkage.py
  - import pytest
  - from bridge_backend.bridge_core.engines.blueprint.registry import BlueprintRegistry
  - from bridge_backend.bridge_core.engines.blueprint.adapters.tde_link import preload_manifest
  - from bridge_backend.bridge_core.engines.blueprint.adapters.tde_link import validate_shard
  - from bridge_backend.bridge_core.engines.blueprint.adapters.cascade_link import get_cascade_config
  - from bridge_backend.bridge_core.engines.blueprint.adapters.autonomy_link import get_autonomy_rules
  - from bridge_backend.bridge_core.engines.blueprint.adapters.autonomy_link import _is_action_allowed
  - from bridge_backend.bridge_core.engines.blueprint.adapters.truth_link import validate_blueprint_sync
  - from bridge_backend.bridge_core.engines.blueprint.adapters.truth_link import certify_fact
  - from bridge_backend.bridge_core.engines.blueprint.adapters.autonomy_link import (


### ./tests/test_blueprint_api.py
  - import pytest
  - from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
  - from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
  - from bridge_backend.bridge_core.middleware.permissions import ROLE_MATRIX
  - from bridge_backend.schemas import BlueprintPlan, TaskItem


### ./tests/test_mission_and_log_models.py
  - import pytest
  - from bridge_core.db import db_manager
  - from bridge_core.db.models import Mission, Log
  - from sqlalchemy import select


### ./tests/test_umbra_lattice_core.py
  - import pytest
  - from datetime import datetime, timezone, timedelta
  - from bridge_backend.bridge_core.engines.umbra.models import (
  - from bridge_backend.bridge_core.engines.umbra.lattice import UmbraLattice
  - from bridge_backend.bridge_core.engines.umbra.storage import LatticeStorage


### ./tests/verify_genesis_v2.py
  - import asyncio
  - import sys
  - import os
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.manifest import genesis_manifest
  - from bridge_backend.genesis.introspection import genesis_introspection
  - from bridge_backend.genesis.orchestration import genesis_orchestrator
  - # Sync from Blueprint
  - # Publish events from different engines


### ./tests/validate_sanctum_cascade.py
  - import sys
  - import os
  - import time
  - import importlib.util
  - import importlib.util
  - import importlib.util
  - 'from bridge_backend.bridge_core.guards.netlify_guard import',
  - 'from bridge_backend.bridge_core.integrity.deferred import',
  - 'from bridge_backend.bridge_core.engines.umbra.autoheal_link import',


### ./tests/test_v196b_features.py
  - import os
  - import sys
  - import pytest
  - import json
  - from pathlib import Path
  - from bridge_backend.models import Base, User
  - pytest.skip("Models import not available in test environment")
  - assert "import httpx" in content
  - # Should import init_schema from utils.db
  - assert "from bridge_backend.utils.db import init_schema" in content
  - # Should import and run release intel
  - assert "from bridge_backend.runtime.release_intel import analyze_and_stabilize" in content
  - # Should import and run heartbeat
  - assert "from bridge_backend.runtime import heartbeat" in content
  - from bridge_backend.runtime.predictive_stabilizer import evaluate_stability
  - pytest.skip("Predictive stabilizer import not available in test environment")
  - from bridge_backend.runtime.release_intel import analyze_and_stabilize
  - pytest.skip("Release intel import not available in test environment")
  - from bridge_backend.integrations.github_issues import maybe_create_issue
  - pytest.skip("GitHub issues import not available in test environment")
  - from bridge_backend.runtime import heartbeat
  - pytest.skip("Heartbeat import not available in test environment")


### ./tests/test_v196f_features.py
  - import os
  - import sys
  - import time
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import resolve_port
  - from bridge_backend.runtime.ports import adaptive_bind_check
  - from bridge_backend.runtime.ports import check_listen
  - from bridge_backend.runtime.startup_watchdog import StartupWatchdog, watchdog
  - from bridge_backend.runtime.startup_watchdog import StartupWatchdog
  - from bridge_backend.runtime.startup_watchdog import StartupWatchdog
  - from bridge_backend.runtime.startup_watchdog import StartupWatchdog
  - from bridge_backend.runtime.startup_watchdog import StartupWatchdog
  - from bridge_backend.runtime.predictive_stabilizer import _is_resolved
  - assert "from bridge_backend.runtime.startup_watchdog import watchdog" in content
  - from bridge_backend.runtime.heartbeat import heartbeat_loop
  - import traceback


### ./tests/test_sovereign_audit.py
  - import os
  - import sys
  - import json
  - import pytest
  - import tempfile
  - import shutil
  - import subprocess
  - from pathlib import Path
  - from unittest.mock import Mock, patch, MagicMock
  - from sovereign_audit_orchestrator import (
  - from dataclasses import asdict
  - from dataclasses import asdict


### ./tests/test_v200_genesis.py
  - import pytest
  - import asyncio
  - from typing import Dict, Any
  - from bridge_backend.genesis.bus import GenesisEventBus
  - from bridge_backend.genesis.bus import GenesisEventBus
  - from bridge_backend.genesis.bus import GenesisEventBus
  - from bridge_backend.genesis.bus import GenesisEventBus
  - from bridge_backend.genesis.manifest import GenesisManifest
  - from bridge_backend.genesis.manifest import GenesisManifest
  - from bridge_backend.genesis.manifest import GenesisManifest
  - from bridge_backend.genesis.manifest import GenesisManifest
  - from bridge_backend.genesis.manifest import GenesisManifest
  - """Test syncing from Blueprint Registry"""
  - from bridge_backend.genesis.manifest import GenesisManifest
  - from bridge_backend.genesis.introspection import GenesisIntrospection
  - from bridge_backend.genesis.introspection import GenesisIntrospection
  - from bridge_backend.genesis.introspection import GenesisIntrospection
  - from bridge_backend.genesis.introspection import GenesisIntrospection
  - from bridge_backend.genesis.introspection import GenesisIntrospection
  - from bridge_backend.genesis.orchestration import GenesisOrchestrator
  - from bridge_backend.genesis.orchestration import GenesisOrchestrator
  - from bridge_backend.genesis.orchestration import GenesisOrchestrator
  - from bridge_backend.bridge_core.engines.adapters.genesis_link import register_all_genesis_links
  - from bridge_backend.genesis.bus import genesis_bus
  - from bridge_backend.genesis.manifest import genesis_manifest
  - from bridge_backend.genesis.introspection import genesis_introspection
  - from bridge_backend.genesis.bus import genesis_bus
  - # Publish events from different engines


### ./tests/test_runtime_handler.py
  - import pytest
  - import os
  - import json
  - import yaml
  - from pathlib import Path
  - from datetime import datetime, timedelta
  - import sys
  - from bridge_core.runtime_handler import (
  - import base64
  - import secrets
  - """Test loading manifest from file"""
  - from datetime import datetime, timedelta


### ./tests/test_autonomy_node.py
  - import unittest
  - import sys
  - import os
  - import json
  - import tempfile
  - import shutil
  - from pathlib import Path
  - import truth
  - import parser
  - import cascade
  - import blueprint
  - from core import AutonomyNode
  - from bridge_backend.genesis.registration import register_embedded_nodes


### ./tests/test_bridge_harmony.py
  - import pytest
  - from pathlib import Path
  - import sys
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import BridgeHarmonyOrchestrator
  - from bridge_core.lattice.bridge_harmony import EngineNode
  - from bridge_core.lattice.bridge_harmony import CommunicationPath


### ./tests/test_git_sovereign_agent.py
  - import pytest
  - from datetime import datetime
  - from bridge_backend.bridge_core.agents.git_sovereign import (


### ./tests/conftest.py
  - import sys
  - from pathlib import Path
  - # This comes after repo_root to ensure bridge_core is found from repo root first


### ./tests/test_v196h_features.py
  - import os
  - import sys
  - import json
  - import asyncio
  - from pathlib import Path
  - from unittest.mock import patch, MagicMock
  - from bridge_backend.runtime.port_guard import describe_port_env
  - from bridge_backend.runtime.port_guard import describe_port_env
  - from bridge_backend import run
  - from bridge_backend import run
  - from fastapi import FastAPI
  - from bridge_backend.runtime.deploy_parity import deploy_parity_check
  - from fastapi import FastAPI
  - from bridge_backend.runtime.deploy_parity import deploy_parity_check
  - from pathlib import Path
  - from bridge_backend.main import app
  - from bridge_backend.main import app
  - from bridge_backend.main import app
  - from bridge_backend.main import app
  - """Test model exports from models/__init__.py"""
  - """Test Blueprint model can be imported from models package"""
  - from bridge_backend.models import Blueprint
  - """Test AgentJob model can be imported from models package"""
  - from bridge_backend.models import AgentJob
  - """Test Mission model can be imported from models package"""
  - from bridge_backend.models import Mission


### ./tests/test_quantum_dominion.py
  - import os
  - import json
  - import pytest
  - from datetime import datetime, timedelta
  - from pathlib import Path
  - from bridge_backend.bridge_core.token_forge_dominion import (
  - """Test complete token lifecycle from minting to validation."""


### ./codex/html_compiler.py
  - import markdown
  - import os
  - from datetime import datetime, timezone
  - """Build a styled HTML book from the markdown repo book."""
  - background: conic-gradient(from 0deg, #00ffaa20, #00ffaa, #00ffaa20);


### ./codex/markdown_compiler.py
  - import sys
  - import os
  - import datetime
  - from codex.truth_engine import gather_meta, validate_facts  # noqa: E402
  - from codex.parser_engine import parse_docs  # noqa: E402
  - from codex.blueprint_engine import build_blueprint  # noqa: E402


### ./codex/compiler.py
  - import sys
  - import os
  - import json
  - from codex.truth_engine import gather_meta, validate_facts  # noqa: E402
  - from codex.parser_engine import parse_docs  # noqa: E402
  - from codex.blueprint_engine import build_blueprint  # noqa: E402


### ./codex/blueprint_engine.py
  - import os
  - """Build dependency blueprint from Python and JavaScript files."""
  - imports = [line.strip() for line in lines if "import " in line or "from " in line]


### ./codex/__init__.py


### ./codex/parser_engine.py
  - import os
  - import re


### ./codex/truth_engine.py
  - import yaml
  - import os
  - import json
  - import hashlib
  - """Gather all YAML/YML files from the repository."""
  - """Validate and deduplicate facts from metadata."""


### ./vault/archived_scripts/get_env_drift.py
  - Quick script to get environment drift report from Steward
  - import asyncio
  - import json
  - import sys
  - import os
  - from pathlib import Path
  - from bridge_backend.engines.steward.core import steward


### ./vault/archived_scripts/verify_hxo_nexus.py
  - import sys
  - import os
  - import asyncio
  - from pathlib import Path
  - from bridge_backend.bridge_core.engines.hxo import (
  - # Verify specific connections from spec
  - from bridge_backend.bridge_core.engines.hxo.routes import router
  - import traceback


### ./vault/archived_scripts/validate_genesis_unified.py
  - import sys
  - import importlib.util
  - """Load a module from a file path"""
  - import py_compile
  - import os


### ./vault/archived_scripts/count_loc.py
  - import os
  - import sys
  - from pathlib import Path
  - from collections import defaultdict
  - from datetime import datetime


### ./vault/archived_scripts/smoke_test_engines.py
  - import sys
  - from pathlib import Path
  - from bridge_core.engines.parser.service import ParserEngine
  - from bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine
  - from bridge_core.engines.truth.binder import bind_candidates
  - from bridge_core.engines.truth.utils import TRUTH_DIR
  - import traceback


### ./vault/archived_scripts/study_repo_with_engines.py
  - import sys
  - import os
  - from pathlib import Path
  - from typing import Dict, Any, List
  - import json
  - from datetime import datetime, timezone
  - # Add the backend to the path to import engines
  - from bridge_core.engines.parser.service import ParserEngine
  - from bridge_core.engines.blueprint.blueprint_engine import BlueprintEngine
  - from bridge_core.engines.truth.binder import bind_candidates, list_truths
  - from bridge_core.engines.truth.finder import find_candidates
  - from bridge_core.engines.truth.utils import TRUTH_DIR
  - print("📋 Creating analysis blueprint from brief:")
  - Generate a comprehensive report combining insights from all three engines
  - "Blueprint Engine generated structured analysis plans from natural language briefs",
  - import traceback


### ./vault/archived_scripts/test_endpoints_full.py
  - import sys
  - import requests
  - import json
  - import time
  - from datetime import datetime, timezone
  - from typing import Dict, List, Tuple, Optional
  - # Engine Endpoints (from smoke_test_engines.sh)
  - import argparse


### ./bridge-frontend/vite.config.js
  - import { defineConfig } from 'vite'
  - import react from '@vitejs/plugin-react'


### ./bridge-frontend/scripts/update-badge.js
  - import fs from "node:fs";
  - import path from "node:path";
  - import { fileURLToPath } from "node:url";


### ./bridge-frontend/scripts/build_triage.py
  - import json, os, re, subprocess, sys, pathlib, shutil


### ./bridge-frontend/netlify/functions/api-armada-status.js


### ./bridge-frontend/netlify/functions/api-agents.js


### ./bridge-frontend/netlify/functions/api-activity.js


### ./bridge-frontend/netlify/functions/api-vault-logs.js


### ./bridge-frontend/netlify/functions/api-status.js


### ./bridge-frontend/netlify/functions/api-missions.js


### ./bridge-frontend/netlify/functions/diagnostic.js


### ./bridge-frontend/netlify/functions/api-system-health.js


### ./bridge-frontend/src/api.js
  - import config from './config';
  - import { APIGuardian, CircuitBreaker } from './services/healing-net';
  - * Centralized function for fetching data from backend endpoints


### ./bridge-frontend/src/config.js


### ./bridge-frontend/src/api/scans.js
  - import config from "../config";


### ./bridge-frontend/src/api/permissions.js
  - import { apiClient } from "./index";


### ./bridge-frontend/src/api/index.js
  - // Re-export fetchData and apiClient from the main api.js file
  - import { fetchData, apiClient } from '../api.js';


### ./bridge-frontend/src/api/leviathan.js
  - import { apiClient } from "./index";


### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_offer.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_autonomy_tasks.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_tag_remove.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_list.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/heritage_demo_mode.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_filing_search.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_ice.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name_policy.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_creativity_search.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/doctrine.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/system_repair.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_autonomy_task.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/permissions_tiers_tier_name.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_sign.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain_memories.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_tag_add.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/protocols.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_admiral.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_filing_reassemble.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/console_snapshot.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_truth_bind.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_creativity_list.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/vault_subpath:path.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_admiral_rotate.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/protocols_name_vault.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_ingest.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/api_control_hooks_triage.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name_lore.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/scans.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_search.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_truth_find.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_keys_key_name_generate.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_registry.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_recovery_dispatch_and_ingest.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain_export.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/blueprint.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_link.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/scans_scan_id.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain_stats.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/payments_stripe_webhook.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_list.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/fleet.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_chunk_sha.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/heritage_demo_modes.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/api_control_rollback.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/protocols_name_activate.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_keys_key_name.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_indoctrination_aid_certify.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_state.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_dock_day_drop.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/permissions_apply_tier.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_start.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/registry_tier_me.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_verify.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_leviathan_solve.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/protocols_name.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_cascade_history.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain_verify.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/blueprint_draft.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_overlay.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_cascade_apply.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/blueprint_bp_id.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_creativity_ingest.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_truth_truths.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_speech_tts.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_sid_answer.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_init.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_parser_reassemble.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/permissions_tiers.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/permissions_current.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_filing_file.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/console_summary.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_verify_drop.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/blueprint_bp_id_commit.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_indoctrination_aid_revoke.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_screen_sid.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_keys.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/custody_keys_key_name_rotate.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/index.js
  - export * from './api_control_hooks_triage';
  - export * from './api_control_rollback';
  - export * from './blueprint';
  - export * from './blueprint_draft';
  - export * from './blueprint_bp_id';
  - export * from './blueprint_bp_id_commit';
  - export * from './brain';
  - export * from './brain_categories';
  - export * from './brain_export';
  - export * from './brain_memories';
  - export * from './brain_memories_entry_id';
  - export * from './brain_stats';
  - export * from './brain_verify';
  - export * from './bridge_core_protocols_registry';
  - export * from './bridge_core_protocols_name';
  - export * from './bridge_core_protocols_name_invoke';
  - export * from './bridge_core_protocols_name_lore';
  - export * from './bridge_core_protocols_name_policy';
  - export * from './console_snapshot';
  - export * from './console_summary';
  - export * from './custody_admiral';
  - export * from './custody_admiral_rotate';
  - export * from './custody_dock_day_drop';
  - export * from './custody_init';
  - export * from './custody_keys';
  - export * from './custody_keys_key_name';
  - export * from './custody_keys_key_name_generate';
  - export * from './custody_keys_key_name_rotate';
  - export * from './custody_sign';
  - export * from './custody_verify';
  - export * from './custody_verify_drop';
  - export * from './doctrine';
  - export * from './engines_autonomy_task';
  - export * from './engines_autonomy_tasks';
  - export * from './engines_cascade_apply';
  - export * from './engines_cascade_history';
  - export * from './engines_creativity_ingest';
  - export * from './engines_creativity_list';
  - export * from './engines_creativity_search';
  - export * from './engines_filing_file';
  - export * from './engines_filing_reassemble';
  - export * from './engines_filing_search';
  - export * from './engines_indoctrination_aid_certify';
  - export * from './engines_indoctrination_aid_revoke';
  - export * from './engines_leviathan_solve';
  - export * from './engines_parser_chunk_sha';
  - export * from './engines_parser_ingest';
  - export * from './engines_parser_link';
  - export * from './engines_parser_list';
  - export * from './engines_parser_reassemble';
  - export * from './engines_parser_search';
  - export * from './engines_parser_tag_add';
  - export * from './engines_parser_tag_remove';
  - export * from './engines_recovery_dispatch_and_ingest';
  - export * from './engines_screen_list';
  - export * from './engines_screen_start';
  - export * from './engines_screen_sid';
  - export * from './engines_screen_sid_answer';
  - export * from './engines_screen_sid_ice';
  - export * from './engines_screen_sid_offer';
  - export * from './engines_screen_sid_overlay';
  - export * from './engines_screen_sid_state';
  - export * from './engines_speech_stt';
  - export * from './engines_speech_tts';
  - export * from './engines_truth_bind';
  - export * from './engines_truth_cite';
  - export * from './engines_truth_find';
  - export * from './engines_truth_truths';
  - export * from './fleet';
  - export * from './heritage_demo_modes';
  - export * from './heritage_demo_mode';
  - export * from './payments_stripe_webhook';
  - export * from './permissions_apply_tier';
  - export * from './permissions_current';
  - export * from './permissions_tiers';
  - export * from './permissions_tiers_tier_name';
  - export * from './protocols';
  - export * from './protocols_name';
  - export * from './protocols_name_activate';
  - export * from './protocols_name_vault';
  - export * from './registry_tier_me';
  - export * from './scans';
  - export * from './scans_scan_id';
  - export * from './system_repair';
  - export * from './vault_subpath:path';


### ./bridge-frontend/src/api/auto_generated/bridge_core_protocols_name_invoke.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_speech_stt.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain_categories.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/engines_truth_cite.js
  - import apiClient from '../api';


### ./bridge-frontend/src/api/auto_generated/brain_memories_entry_id.js
  - import apiClient from '../api';


### ./bridge-frontend/src/utils/endpointBootstrap.js


### ./bridge-frontend/src/services/brh-api.js
  - import config from '../config';
  - // Fallback: use name, or generate ID from index if neither id nor name exists


### ./bridge-frontend/src/services/websocket-service.js
  - import config from '../config';


### ./bridge-frontend/src/services/healing-net.js


### ./bridge-frontend/src/services/deployment-validator.js
  - import config from '../config';
  - import { APIGuardian } from './healing-net';
  - // Dynamic import to avoid circular dependency
  - // Dynamic import to avoid circular dependency


### ./bridge-frontend/src/services/silent-failure-capture.js
  - import { DeploymentValidator } from './deployment-validator';
  - import { TriageEngine } from './healing-net';
  - * Helps components recover from crashes


### ./bridge-frontend/src/services/true-data-revealer.js
  - import { DeploymentValidator } from './deployment-validator';
  - import { BRHService } from './brh-api';
  - import { UmbraLattice } from './healing-net';
  - import config from '../config';


### ./bridge-frontend/src/hooks/useBRHConnection.js
  - import { useState, useEffect, useCallback, useRef } from 'react';
  - import BRHService from '../services/brh-api';
  - * Manages real-time data updates from BRH backend


### ./bridge-frontend/src/hooks/useBridgeStream.js
  - import { useEffect, useRef, useState } from "react";


### ./brh/heartbeat_daemon.py
  - import os
  - import time
  - import hmac
  - import hashlib
  - import json
  - import threading
  - import requests
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment


### ./brh/role.py
  - import os
  - import threading
  - lease_token: Optional lease token from Forge


### ./brh/consensus.py
  - import os
  - import time
  - import json
  - import hashlib
  - import hmac
  - import threading
  - import requests
  - from brh import role, handover
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
  - Register heartbeat from peer node.
  - from brh.api import log_event
  - log_event(f"HEARTBEAT: received from {node} at epoch {pulse['epoch']}")
  - Elect leader from active peers.
  - lease_token: Optional lease token from Forge
  - from brh.api import log_event
  - from brh.api import log_event
  - from brh.api import log_event


### ./brh/handover.py
  - import os
  - import time
  - from brh import role
  - import docker


### ./brh/forge_auth.py
  - import os
  - import hmac
  - import hashlib
  - import time
  - import urllib.parse as up
  - from dataclasses import dataclass
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment


### ./brh/test_consensus_role.py
  - import os
  - import sys
  - from brh import role
  - from brh import consensus
  - import time
  - """Test handover.py module (basic import check)"""
  - from brh import handover
  - import traceback


### ./brh/test_integration.py
  - import os
  - import sys
  - import time
  - from brh import consensus, role
  - print("✓ Stale nodes correctly excluded from election")
  - import traceback
  - import traceback


### ./brh/test_api_endpoints.py
  - import pytest
  - from fastapi.testclient import TestClient
  - from brh.api import app, log_event, EVENT_LOG
  - from brh import consensus


### ./brh/chaos.py
  - import os
  - import random
  - import threading
  - import time
  - import docker
  - from brh.api import log_event


### ./brh/recovery.py
  - import time
  - import threading
  - from brh import role
  - import docker
  - from brh.api import log_event
  - from brh.api import log_event
  - import os


### ./brh/api.py
  - import os
  - import subprocess
  - import time
  - import re
  - from datetime import datetime, timezone
  - from fastapi import FastAPI, Request, HTTPException
  - from fastapi.middleware.cors import CORSMiddleware
  - from brh import role
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment
  - import docker
  - from brh import consensus
  - Get recent events from the event log.


### ./brh/test_chaos_recovery.py
  - import pytest
  - import os
  - from unittest.mock import patch, MagicMock
  - from brh import chaos, recovery
  - import importlib
  - import importlib


### ./brh/test_phase6_integration.py
  - import os
  - import sys
  - from brh import chaos, recovery
  - print(f"✗ Failed to import modules: {e}")
  - from brh.api import app, log_event, EVENT_LOG
  - from brh import chaos
  - from brh import recovery


### ./brh/__init__.py


### ./brh/run.py
  - import os
  - import subprocess
  - import sys
  - import time
  - import socket
  - import json
  - import yaml
  - import requests
  - from pathlib import Path
  - from dataclasses import dataclass
  - from brh.forge_auth import parse_forge_root, verify_seal, mint_ephemeral_token
  - from brh import heartbeat_daemon, consensus, role
  - from brh import chaos
  - from brh import recovery


### ./brh/examples/test_forge_auth.py
  - import os
  - import sys
  - import time
  - from brh.forge_auth import parse_forge_root, verify_seal, mint_ephemeral_token
  - from bridge_backend.bridge_core.token_forge_dominion.secret_forge import retrieve_environment


### ./phoenix/backend/main.py
  - import os
  - from datetime import datetime
  - from fastapi import FastAPI, HTTPException, Depends
  - from fastapi.middleware.cors import CORSMiddleware
  - from sqlalchemy.ext.asyncio import AsyncSession
  - from sqlalchemy import select, func
  - from contextlib import asynccontextmanager
  - import db
  - from models import Guardian, Agent, Mission, VaultLog
  - from schemas import HealthResponse, FullHealthResponse
  - from core.agents import routes as agent_routes
  - from core.missions import routes as mission_routes
  - from core.engines import calculus_core
  - import uvicorn


### ./phoenix/backend/schemas.py
  - from pydantic import BaseModel, Field
  - from datetime import datetime
  - from typing import Optional, List, Dict, Any
  - log_metadata: Dict[str, Any] = Field(default_factory=dict)  # Renamed from 'metadata'


### ./phoenix/backend/db.py
  - import os
  - from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
  - from sqlalchemy.orm import sessionmaker
  - from contextlib import asynccontextmanager
  - from models import Base


### ./phoenix/backend/models.py
  - from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, Boolean
  - from sqlalchemy.ext.declarative import declarative_base
  - from datetime import datetime
  - log_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved)


### ./phoenix/backend/core/__init__.py


### ./phoenix/backend/core/engines/calculus_core.py
  - from fastapi import APIRouter, HTTPException
  - from pydantic import BaseModel
  - from typing import Optional, List, Dict, Any
  - import sympy as sp
  - from sympy import sympify, latex
  - from datetime import datetime
  - steps.append(f"Applied definite integration from {request.bounds[0]} to {request.bounds[1]}")


### ./phoenix/backend/core/engines/__init__.py


### ./phoenix/backend/core/agents/__init__.py


### ./phoenix/backend/core/agents/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from sqlalchemy.ext.asyncio import AsyncSession
  - from sqlalchemy import select
  - from datetime import datetime
  - from typing import List, Optional
  - import db
  - from models import Agent
  - from schemas import AgentCreate, AgentResponse


### ./phoenix/backend/core/missions/__init__.py


### ./phoenix/backend/core/missions/routes.py
  - from fastapi import APIRouter, HTTPException, Depends
  - from sqlalchemy.ext.asyncio import AsyncSession
  - from sqlalchemy import select
  - from datetime import datetime
  - from typing import List, Optional
  - import db
  - from models import Mission
  - from schemas import MissionCreate, MissionUpdate, MissionResponse

