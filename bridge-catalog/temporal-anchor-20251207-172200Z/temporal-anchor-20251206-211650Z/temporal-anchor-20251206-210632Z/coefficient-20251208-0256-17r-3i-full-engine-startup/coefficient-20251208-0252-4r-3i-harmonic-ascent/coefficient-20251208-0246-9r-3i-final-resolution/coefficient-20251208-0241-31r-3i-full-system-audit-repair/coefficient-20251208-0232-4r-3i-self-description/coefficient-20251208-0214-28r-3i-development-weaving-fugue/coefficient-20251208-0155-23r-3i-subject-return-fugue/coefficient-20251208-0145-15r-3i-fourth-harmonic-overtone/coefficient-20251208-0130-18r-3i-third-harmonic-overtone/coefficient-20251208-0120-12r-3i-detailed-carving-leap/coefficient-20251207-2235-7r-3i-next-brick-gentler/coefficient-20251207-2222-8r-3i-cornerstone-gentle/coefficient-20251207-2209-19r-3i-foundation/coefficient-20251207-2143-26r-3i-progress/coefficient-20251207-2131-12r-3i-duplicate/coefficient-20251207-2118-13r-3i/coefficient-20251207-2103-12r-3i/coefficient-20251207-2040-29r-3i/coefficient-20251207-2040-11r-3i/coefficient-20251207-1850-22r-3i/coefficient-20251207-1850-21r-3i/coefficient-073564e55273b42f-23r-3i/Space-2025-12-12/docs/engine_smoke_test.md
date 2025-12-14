# Engine Smoke Test Guide

This document provides step-by-step instructions for testing all Six Super Engines in the SR-AIbridge system to confirm they are alive and functional after backend dependency fixes.

## Overview

The SR-AIbridge system includes six powerful engines that form the Sovereign Bridge Architecture:

1. **CalculusCore** - Math Engine (Advanced mathematical computations)
2. **QHelmSingularity** - Quantum Engine (Quantum navigation and spacetime physics)
3. **AuroraForge** - Science Engine (Visual synthesis and creative content)
4. **ChronicleLoom** - History Engine (Chronicle weaving and temporal documentation)
5. **ScrollTongue** - Language Engine (Natural language processing and analysis)
6. **CommerceForge** - Business Engine (Economic modeling and trading)

## Prerequisites

- Backend server running on `http://localhost:8000` (or your deployment URL)
- `curl` command-line tool available
- All engine endpoints implemented and functional

## Engine Tests

### 1. Math Engine (CalculusCore) - POST /engines/math/prove

**Purpose**: Tests mathematical computation and proof capabilities.

**Test Command**:
```bash
curl -X POST http://localhost:8000/engines/math/prove \
  -H "Content-Type: application/json" \
  -d '{
    "equation": "x^2 + 2*x + 1",
    "operation": "differentiate",
    "variable": "x",
    "prove_theorem": "quadratic_completion"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "engine": "CalculusCore",
  "operation": "prove",
  "results": {
    "equation_id": "eq_123",
    "derivative": "2*x + 2",
    "theorem_proof": "completed",
    "computation_time": "0.045s"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 2. Quantum Engine (QHelmSingularity) - POST /engines/quantum/collapse

**Purpose**: Tests quantum state manipulation and spacetime navigation.

**Test Command**:
```bash
curl -X POST http://localhost:8000/engines/quantum/collapse \
  -H "Content-Type: application/json" \
  -d '{
    "quantum_state": "superposition",
    "coordinates": [1.0, 2.0, 3.0, 4.0],
    "singularity_type": "wormhole",
    "navigation_mode": "quantum_tunneling"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "engine": "QHelmSingularity",
  "operation": "collapse",
  "results": {
    "route_id": "route_456",
    "collapsed_state": "entangled",
    "probability_amplitude": 0.87,
    "traversal_time": "2.3s",
    "waypoints": 5
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

### 3. Science Engine (AuroraForge) - POST /engines/science/experiment

**Purpose**: Tests visual synthesis and creative content generation.

**Test Command**:
```bash
curl -X POST http://localhost:8000/engines/science/experiment \
  -H "Content-Type: application/json" \
  -d '{
    "experiment_type": "visual_synthesis",
    "parameters": {
      "style": "cyberpunk",
      "dimensions": [1920, 1080],
      "complexity": 0.8
    },
    "hypothesis": "aurora_pattern_generation"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "engine": "AuroraForge",
  "operation": "experiment",
  "results": {
    "asset_id": "aurora_789",
    "visual_type": "visualization",
    "render_time": "1.2s",
    "complexity_score": 0.85,
    "file_size": 2048576
  },
  "timestamp": "2024-01-15T10:30:10Z"
}
```

### 4. History Engine (ChronicleLoom) - POST /engines/history/weave

**Purpose**: Tests chronicle weaving and temporal narrative creation.

**Test Command**:
```bash
curl -X POST http://localhost:8000/engines/history/weave \
  -H "Content-Type: application/json" \
  -d '{
    "chronicle_ids": ["chronicle_001", "chronicle_002", "chronicle_003"],
    "thread_title": "Temporal Pattern Analysis",
    "narrative_type": "causal",
    "weave_depth": "deep"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "engine": "ChronicleLoom",
  "operation": "weave",
  "results": {
    "thread_id": "thread_012",
    "narrative_complexity": 0.92,
    "temporal_coherence": 0.88,
    "patterns_detected": 7,
    "weave_quality": "excellent"
  },
  "timestamp": "2024-01-15T10:30:15Z"
}
```

### 5. Language Engine (ScrollTongue) - POST /engines/language/interpret

**Purpose**: Tests natural language processing and linguistic analysis.

**Test Command**:
```bash
curl -X POST http://localhost:8000/engines/language/interpret \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quantum consciousness bridges temporal dimensions through linguistic fractals.",
    "analysis_type": "semantic",
    "language_type": "technical",
    "interpretation_depth": "comprehensive"
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "engine": "ScrollTongue",
  "operation": "interpret",
  "results": {
    "scroll_id": "scroll_345",
    "detected_language": "en-technical",
    "complexity_score": 0.78,
    "sentiment": "neutral",
    "key_concepts": ["quantum", "consciousness", "temporal", "linguistic"]
  },
  "timestamp": "2024-01-15T10:30:20Z"
}
```

### 6. Business Engine (CommerceForge) - POST /engines/business/forge

**Purpose**: Tests economic modeling and trading optimization.

**Test Command**:
```bash
curl -X POST http://localhost:8000/engines/business/forge \
  -H "Content-Type: application/json" \
  -d '{
    "asset_symbol": "QBIT",
    "market_type": "crypto",
    "trade_strategy": "momentum",
    "portfolio_optimization": "balanced",
    "risk_tolerance": 0.6
  }'
```

**Expected Response**:
```json
{
  "status": "success",
  "engine": "CommerceForge",
  "operation": "forge",
  "results": {
    "asset_id": "asset_678",
    "trade_recommendation": "buy",
    "expected_return": 0.15,
    "risk_assessment": "moderate",
    "market_confidence": 0.82
  },
  "timestamp": "2024-01-15T10:30:25Z"
}
```

## Running All Tests

Use the provided `smoke_test_engines.sh` script to run all engine tests sequentially:

```bash
./smoke_test_engines.sh
```

Or specify a custom backend URL:

```bash
./smoke_test_engines.sh https://your-backend.onrender.com
```

## Expected Behavior

### Success Indicators
- All engines return HTTP 200 status
- Response includes `"status": "success"`
- Engine-specific results are populated
- Response times are reasonable (< 5 seconds)
- No error messages in logs

### Health Check Integration
The engine tests complement the existing health check system:
- `/health` - Basic availability
- `/health/full` - Detailed system status
- Engine smoke tests - Functional verification

## Troubleshooting

### Common Issues

**1. Engine Endpoint Not Found (404)**
- **Cause**: Engine endpoints not yet implemented
- **Solution**: Wait for backend dependency fix to add engine routes
- **Workaround**: Check `/status` endpoint for engine availability

**2. Internal Server Error (500)**
- **Cause**: Engine initialization failure or missing dependencies
- **Solution**: Check server logs for specific error details
- **Actions**: 
  - Verify all Python dependencies installed
  - Check engine configuration in `bridge_core/engines/`
  - Restart backend service

**3. Timeout Errors**
- **Cause**: Engine computation taking too long
- **Solution**: Increase timeout values or optimize engine algorithms
- **Check**: Server resource usage (CPU, memory)

**4. Invalid JSON Response**
- **Cause**: Engine returning malformed data
- **Solution**: Validate engine output format
- **Debug**: Use `curl -v` for detailed response inspection

### Debugging Commands

**Check engine status**:
```bash
curl -s http://localhost:8000/status | jq '.engines'
```

**Verify engine initialization**:
```bash
curl -s http://localhost:8000/health/full | jq '.components.engines'
```

**Monitor server logs**:
```bash
tail -f /var/log/sr-aibridge/backend.log
```

## Performance Benchmarks

### Expected Response Times
- Math Engine: < 1 second
- Quantum Engine: < 3 seconds  
- Science Engine: < 2 seconds
- History Engine: < 2 seconds
- Language Engine: < 1 second
- Business Engine: < 1 second

### Resource Usage
- Memory: < 512MB per engine
- CPU: < 50% during computation
- Disk I/O: Minimal (< 10MB/s)

## Integration Notes

### CI/CD Integration
These smoke tests are designed to integrate with existing CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Engine Smoke Tests
  run: |
    ./smoke_test_engines.sh ${{ secrets.BACKEND_URL }}
  env:
    TIMEOUT: 30
    RETRIES: 3
```

### Monitoring Integration
Results can be integrated with monitoring systems:
- Prometheus metrics collection
- Grafana dashboard visualization
- Alert triggers for failed tests

## Security Considerations

- Engine endpoints may require authentication in production
- Sensitive computational results should not be logged
- Rate limiting may apply to prevent abuse
- Test data should not contain production secrets

## Next Steps

After successful engine smoke tests:
1. Run full integration test suite
2. Verify engine performance under load
3. Test engine interconnectivity and data flow
4. Validate engine state persistence
5. Confirm security and access controls

For issues or questions, consult the main [README.md](../README.md) or system documentation.