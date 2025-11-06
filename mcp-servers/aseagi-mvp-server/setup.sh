#!/bin/bash
# ASEAGI MCP Server - Quick Setup Script

set -e

echo "=========================================="
echo "ASEAGI MCP Server - MVP Setup"
echo "=========================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your Supabase credentials:"
    echo "   nano .env"
    echo ""
fi

# Test import
echo "Testing server..."
python3 -c "import server; print('✓ Server module loads successfully')"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials:"
echo "   nano .env"
echo ""
echo "2. Test the server:"
echo "   python server.py"
echo ""
echo "3. Configure Claude Desktop:"
echo "   Edit: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "4. Restart Claude Desktop"
echo ""
echo "For detailed instructions, see README.md"
echo ""
