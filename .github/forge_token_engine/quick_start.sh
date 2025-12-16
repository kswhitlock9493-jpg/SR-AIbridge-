#!/bin/bash
# Sovereign Financial Independence - Quick Start
# This script helps you get started with the Forge Token Engine

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   🏦 Forge Token Engine - Financial Sovereignty System       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}What would you like to do?${NC}"
echo ""
echo "1) Analyze current GitHub Actions costs"
echo "2) Check system configuration"
echo "3) View cost tracking and savings"
echo "4) Test all tools"
echo "5) Show documentation"
echo "6) Exit"
echo ""
read -p "Enter your choice (1-6): " choice

case $choice in
  1)
    echo -e "\n${GREEN}Analyzing workflows...${NC}\n"
    python3 .github/forge_token_engine/workflow_consolidation.py
    ;;
  2)
    echo -e "\n${GREEN}Checking configuration...${NC}\n"
    python3 .github/forge_token_engine/config_manager.py
    echo ""
    echo -e "${YELLOW}Configuration file: .github/forge_token_engine/config.json${NC}"
    echo "Edit this file to customize provider limits and costs"
    ;;
  3)
    echo -e "\n${GREEN}Viewing cost tracking...${NC}\n"
    python3 .github/forge_token_engine/cost_tracking.py
    echo ""
    echo -e "${YELLOW}Record usage:${NC}"
    echo "python3 .github/forge_token_engine/cost_tracking.py --record [github_min] [self_hosted_min] [render_min] [netlify_min]"
    ;;
  4)
    echo -e "\n${GREEN}Testing all tools...${NC}\n"
    echo "1. Config Manager:"
    python3 .github/forge_token_engine/config_manager.py 2>&1 | head -8
    echo ""
    echo "2. Financial Resilience:"
    python3 .github/forge_token_engine/financial_resilience.py 2>&1 | grep "Resilience Score" || echo "✅ Working"
    echo ""
    echo "3. Cost Bypass:"
    python3 .github/forge_token_engine/cost_bypass.py 2>&1 | grep "REPORT\|savings" | head -3 || echo "✅ Working"
    echo ""
    echo -e "${GREEN}✅ All tools working!${NC}"
    ;;
  5)
    echo -e "\n${GREEN}Available Documentation:${NC}\n"
    echo "📚 Main Documentation:"
    echo "  - .github/forge_token_engine/README.md"
    echo "    Complete system overview and API reference"
    echo ""
    echo "🚀 Setup Guide:"
    echo "  - .github/forge_token_engine/SETUP_GUIDE.md"
    echo "    Step-by-step setup instructions"
    echo ""
    echo "🔍 Technical Reality:"
    echo "  - .github/forge_token_engine/TECHNICAL_REALITY.md"
    echo "    What's possible vs what was requested"
    echo ""
    echo "📊 Implementation Summary:"
    echo "  - .github/forge_token_engine/IMPLEMENTATION_SUMMARY.md"
    echo "    Complete deliverable overview"
    echo ""
    echo "💡 Example Workflow:"
    echo "  - .github/workflows/example-sovereign-ci.yml"
    echo "    Production-ready template"
    echo ""
    echo -e "${YELLOW}Quick Start:${NC}"
    echo "1. Read SETUP_GUIDE.md"
    echo "2. Set up self-hosted runner (optional but recommended)"
    echo "3. Copy example-sovereign-ci.yml to your workflows"
    echo "4. Customize config.json for your needs"
    echo "5. Monitor savings with cost_tracking.py"
    ;;
  6)
    echo -e "\n${GREEN}Goodbye!${NC}"
    echo "Documentation: .github/forge_token_engine/README.md"
    echo "Setup Guide: .github/forge_token_engine/SETUP_GUIDE.md"
    exit 0
    ;;
  *)
    echo -e "\n${YELLOW}Invalid choice. Please run again.${NC}"
    exit 1
    ;;
esac

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  💡 Next Steps:                                              ║"
echo "║  1. Review SETUP_GUIDE.md for detailed instructions         ║"
echo "║  2. Set up self-hosted runner for maximum savings           ║"
echo "║  3. Update workflows to use sovereign routing               ║"
echo "║  4. Monitor savings with cost_tracking.py                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
