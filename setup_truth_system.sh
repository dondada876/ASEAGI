#!/bin/bash

##############################################################################
# Truth Score & Justice Analysis System - Quick Setup Script
# Automates deployment of enhanced truth scoring system
##############################################################################

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════════"
echo "  Truth Score & Justice Analysis System - Quick Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}[1/6]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Found: $PYTHON_VERSION"
echo ""

# Check pip
echo -e "${BLUE}[2/6]${NC} Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}✗ pip3 not found. Please install pip${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} pip3 is installed"
echo ""

# Install Python dependencies
echo -e "${BLUE}[3/6]${NC} Installing Python dependencies..."
if [ -f "requirements_truth_system.txt" ]; then
    pip3 install -r requirements_truth_system.txt
    echo -e "${GREEN}✓${NC} Dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} requirements_truth_system.txt not found, skipping..."
fi
echo ""

# Check for Anthropic API key
echo -e "${BLUE}[4/6]${NC} Checking environment variables..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} ANTHROPIC_API_KEY not set"
    echo "   To use the police report scanner, set your API key:"
    echo "   export ANTHROPIC_API_KEY='your-key-here'"
else
    echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY is set"
fi

if [ -z "$SUPABASE_URL" ]; then
    echo -e "${YELLOW}⚠${NC} SUPABASE_URL not set (will use default)"
else
    echo -e "${GREEN}✓${NC} SUPABASE_URL is set"
fi

if [ -z "$SUPABASE_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} SUPABASE_KEY not set (will use default)"
else
    echo -e "${GREEN}✓${NC} SUPABASE_KEY is set"
fi
echo ""

# Check for schema file
echo -e "${BLUE}[5/6]${NC} Checking database schema..."
if [ -f "master_timeline_schema.sql" ]; then
    echo -e "${GREEN}✓${NC} Schema file found: master_timeline_schema.sql"
    echo ""
    echo "   To deploy schema to Supabase:"
    echo "   1. Go to: https://supabase.com/dashboard/project/YOUR_PROJECT/sql"
    echo "   2. Copy contents of master_timeline_schema.sql"
    echo "   3. Paste and run in SQL Editor"
    echo ""
else
    echo -e "${RED}✗${NC} master_timeline_schema.sql not found"
fi
echo ""

# Check for Python scripts
echo -e "${BLUE}[6/6]${NC} Checking system files..."

SCRIPTS=(
    "police_report_scanner.py"
    "enhanced_truth_score_dashboard.py"
    "master_timeline_schema.sql"
    "TRUTH_SCORE_SYSTEM_README.md"
)

ALL_FOUND=true
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo -e "${GREEN}✓${NC} Found: $script"
    else
        echo -e "${RED}✗${NC} Missing: $script"
        ALL_FOUND=false
    fi
done
echo ""

# Final status
echo "═══════════════════════════════════════════════════════════════"
if [ "$ALL_FOUND" = true ]; then
    echo -e "${GREEN}✓ Setup Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Deploy database schema to Supabase"
    echo "   (Copy master_timeline_schema.sql to Supabase SQL Editor)"
    echo ""
    echo "2. Scan police reports:"
    echo "   python3 police_report_scanner.py /path/to/reports --rename"
    echo ""
    echo "3. Launch dashboard:"
    echo "   streamlit run enhanced_truth_score_dashboard.py"
    echo ""
    echo "4. Access dashboard at:"
    echo "   http://localhost:8501"
    echo ""
    echo "📚 See TRUTH_SCORE_SYSTEM_README.md for complete guide"
else
    echo -e "${RED}✗ Setup incomplete - some files are missing${NC}"
    echo "   Please check the errors above"
fi
echo "═══════════════════════════════════════════════════════════════"
