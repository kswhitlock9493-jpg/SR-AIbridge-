#!/bin/bash

# SR-AIbridge Engine Smoke Test Script
# Tests all Six Super Engines to confirm they are alive and functional
# 
# Usage: ./smoke_test_engines.sh [BASE_URL]
# Example: ./smoke_test_engines.sh https://your-backend.onrender.com

set -e  # Exit on any error

# Configuration
BASE_URL="${1:-http://localhost:8000}"
TIMEOUT="${TIMEOUT:-30}"
RETRIES="${RETRIES:-3}"
VERBOSE="${VERBOSE:-false}"
OUTPUT_FILE="${OUTPUT_FILE:-/tmp/engine_smoke_test_$(date +%s).log}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=6
PASSED_TESTS=0
FAILED_TESTS=0

echo "🚀 SR-AIbridge Engine Smoke Test Suite"
echo "========================================"
echo "Backend URL: ${BASE_URL}"
echo "Timeout: ${TIMEOUT}s"
echo "Retries: ${RETRIES}"
echo "Output Log: ${OUTPUT_FILE}"
echo ""

# Initialize log file
echo "SR-AIbridge Engine Smoke Test - $(date)" > "${OUTPUT_FILE}"
echo "Backend URL: ${BASE_URL}" >> "${OUTPUT_FILE}"
echo "=======================================" >> "${OUTPUT_FILE}"

# Function to make HTTP request with retries
make_request() {
    local url="$1"
    local payload="$2"
    local description="$3"
    local attempt=1
    
    while [ $attempt -le $RETRIES ]; do
        if [ "$VERBOSE" = "true" ]; then
            echo "  Attempt $attempt/$RETRIES..."
        fi
        
        # Make the request and capture response
        local response
        local http_code
        
        if response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST \
            -H "Content-Type: application/json" \
            -d "$payload" \
            --max-time "$TIMEOUT" \
            "$url" 2>>"${OUTPUT_FILE}"); then
            
            http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
            response_body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]*$//')
            
            # Log the full response
            echo "[$description] HTTP $http_code" >> "${OUTPUT_FILE}"
            echo "$response_body" >> "${OUTPUT_FILE}"
            echo "---" >> "${OUTPUT_FILE}"
            
            if [ "$http_code" -eq 200 ]; then
                echo -e "  ${GREEN}✓${NC} Success (HTTP $http_code)"
                if [ "$VERBOSE" = "true" ]; then
                    echo "$response_body" | jq . 2>/dev/null || echo "$response_body"
                fi
                return 0
            elif [ "$http_code" -eq 404 ]; then
                echo -e "  ${YELLOW}⚠${NC} Endpoint not found (HTTP $http_code) - Engine endpoints may not be implemented yet"
                return 1
            else
                echo -e "  ${RED}✗${NC} HTTP $http_code"
                if [ "$VERBOSE" = "true" ]; then
                    echo "$response_body"
                fi
            fi
        else
            echo -e "  ${RED}✗${NC} Request failed (attempt $attempt/$RETRIES)"
        fi
        
        attempt=$((attempt + 1))
        if [ $attempt -le $RETRIES ]; then
            echo "  Retrying in 2 seconds..."
            sleep 2
        fi
    done
    
    return 1
}

# Function to test an engine
test_engine() {
    local engine_name="$1"
    local endpoint="$2"
    local payload="$3"
    local description="$4"
    local icon="$5"
    
    echo -e "${BLUE}${icon} Testing ${engine_name}${NC}"
    echo "  Endpoint: POST ${endpoint}"
    
    if make_request "${BASE_URL}${endpoint}" "$payload" "$description"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo -e "  ${GREEN}✅ ${engine_name} is functional${NC}"
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo -e "  ${RED}❌ ${engine_name} test failed${NC}"
    fi
    echo ""
}

# Test 1: Math Engine (CalculusCore)
echo -e "${PURPLE}🔬 Starting Engine Tests...${NC}"
echo ""

test_engine \
    "Math Engine (CalculusCore)" \
    "/engines/math/prove" \
    '{
        "equation": "x^2 + 2*x + 1",
        "operation": "differentiate",
        "variable": "x",
        "prove_theorem": "quadratic_completion"
    }' \
    "Math Engine Test" \
    "🧮"

# Test 2: Quantum Engine (QHelmSingularity)
test_engine \
    "Quantum Engine (QHelmSingularity)" \
    "/engines/quantum/collapse" \
    '{
        "quantum_state": "superposition",
        "coordinates": [1.0, 2.0, 3.0, 4.0],
        "singularity_type": "wormhole",
        "navigation_mode": "quantum_tunneling"
    }' \
    "Quantum Engine Test" \
    "⚛️"

# Test 3: Science Engine (AuroraForge)
test_engine \
    "Science Engine (AuroraForge)" \
    "/engines/science/experiment" \
    '{
        "experiment_type": "visual_synthesis",
        "parameters": {
            "style": "cyberpunk",
            "dimensions": [1920, 1080],
            "complexity": 0.8
        },
        "hypothesis": "aurora_pattern_generation"
    }' \
    "Science Engine Test" \
    "🔬"

# Test 4: History Engine (ChronicleLoom)
test_engine \
    "History Engine (ChronicleLoom)" \
    "/engines/history/weave" \
    '{
        "chronicle_ids": ["chronicle_001", "chronicle_002", "chronicle_003"],
        "thread_title": "Temporal Pattern Analysis",
        "narrative_type": "causal",
        "weave_depth": "deep"
    }' \
    "History Engine Test" \
    "📚"

# Test 5: Language Engine (ScrollTongue)
test_engine \
    "Language Engine (ScrollTongue)" \
    "/engines/language/interpret" \
    '{
        "text": "The quantum consciousness bridges temporal dimensions through linguistic fractals.",
        "analysis_type": "semantic",
        "language_type": "technical",
        "interpretation_depth": "comprehensive"
    }' \
    "Language Engine Test" \
    "📜"

# Test 6: Business Engine (CommerceForge)
test_engine \
    "Business Engine (CommerceForge)" \
    "/engines/business/forge" \
    '{
        "asset_symbol": "QBIT",
        "market_type": "crypto",
        "trade_strategy": "momentum",
        "portfolio_optimization": "balanced",
        "risk_tolerance": 0.6
    }' \
    "Business Engine Test" \
    "💰"

# Summary
echo "========================================"
echo -e "${CYAN}🎯 Test Summary${NC}"
echo "========================================"
echo "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All engines are functional!${NC}"
    echo -e "✅ SR-AIbridge Super Engines are ready for operation"
    exit_code=0
else
    echo -e "\n${YELLOW}⚠️  Some engines may need attention${NC}"
    echo -e "📋 Check the detailed log: ${OUTPUT_FILE}"
    echo -e "📖 See docs/engine_smoke_test.md for troubleshooting"
    
    if [ $FAILED_TESTS -eq $TOTAL_TESTS ]; then
        echo -e "\n${RED}❌ All engine tests failed${NC}"
        echo -e "🚨 This likely means engine endpoints are not yet implemented"
        echo -e "🔧 Wait for backend dependency fix to add engine routes"
        exit_code=2
    else
        echo -e "\n${YELLOW}⚡ Partial functionality detected${NC}"
        exit_code=1
    fi
fi

echo ""
echo "Full test log saved to: ${OUTPUT_FILE}"
echo ""

# Health check as fallback
echo -e "${BLUE}🏥 Running basic health check...${NC}"
if curl -s --max-time 10 "${BASE_URL}/health" > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend is responding"
else
    echo -e "${RED}✗${NC} Backend health check failed"
    exit_code=3
fi

echo ""
echo -e "${PURPLE}🚀 Engine smoke test completed${NC}"
echo "For detailed troubleshooting, see: docs/engine_smoke_test.md"

exit $exit_code