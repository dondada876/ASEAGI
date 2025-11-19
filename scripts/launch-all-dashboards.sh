#!/bin/bash
###############################################################################
# Launch All PROJ344 Dashboards
# Starts multiple Streamlit dashboards on different ports
###############################################################################

echo "======================================================================"
echo "🚀 PROJ344 DASHBOARD LAUNCHER"
echo "======================================================================"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not installed!"
    echo ""
    echo "Install with: pip3 install streamlit plotly"
    exit 1
fi

# Check environment variables
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo "⚠️  WARNING: Supabase environment variables not set"
    echo ""
    echo "Set with:"
    echo "  export SUPABASE_URL='https://jvjlhxodmbkodzmggwpu.supabase.co'"
    echo "  export SUPABASE_KEY='your-supabase-anon-key'"
    echo ""
    echo "Or load from .env file:"
    echo "  source .env"
    echo ""
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
DASHBOARD_DIR="$PROJECT_ROOT/dashboards"

echo "Starting dashboards from: $DASHBOARD_DIR"
echo ""

# Dashboard 1: PROJ344 Master (Main dashboard)
echo "📊 Port 8501: PROJ344 Master Dashboard"
cd "$DASHBOARD_DIR"
streamlit run proj344_master_dashboard.py \
    --server.headless=true \
    --server.port=8501 \
    --server.address=localhost &
PROJ344_PID=$!

sleep 2

# Dashboard 2: Legal Intelligence Dashboard
echo "⚖️  Port 8502: Legal Intelligence Dashboard"
streamlit run legal_intelligence_dashboard.py \
    --server.headless=true \
    --server.port=8502 \
    --server.address=localhost &
LEGAL_PID=$!

sleep 2

# Dashboard 3: CEO Dashboard
echo "👔 Port 8503: CEO File Organization Dashboard"
streamlit run ceo_dashboard.py \
    --server.headless=true \
    --server.port=8503 \
    --server.address=localhost &
CEO_PID=$!

sleep 2

# Dashboard 4: Enhanced Scanning Monitor
echo "📊 Port 8504: Enhanced Scanning Monitor"
streamlit run enhanced_scanning_monitor.py \
    --server.headless=true \
    --server.port=8504 \
    --server.address=localhost &
ENHANCED_PID=$!

sleep 2

# Dashboard 5: Timeline & Violations
echo "⚖️  Port 8505: Timeline & Constitutional Violations"
streamlit run timeline_violations_dashboard.py \
    --server.headless=true \
    --server.port=8505 \
    --server.address=localhost &
TIMELINE_PID=$!

sleep 2

# Dashboard 6: Master 5W+H Dashboard
echo "🔍 Port 8506: Master 5W+H Framework Dashboard"
streamlit run master_5wh_dashboard.py \
    --server.headless=true \
    --server.port=8506 \
    --server.address=localhost &
MASTER5WH_PID=$!

echo ""
echo "======================================================================"
echo "✅ ALL 6 DASHBOARDS RUNNING!"
echo "======================================================================"
echo ""
echo "Access dashboards at:"
echo "  🎯 PROJ344 Master:           http://localhost:8501"
echo "  ⚖️  Legal Intelligence:       http://localhost:8502"
echo "  👔 CEO Dashboard:            http://localhost:8503"
echo "  📊 Enhanced Scanning Monitor: http://localhost:8504"
echo "  ⚖️  Timeline & Violations:    http://localhost:8505"
echo "  🔍 Master 5W+H Framework:    http://localhost:8506"
echo ""
echo "======================================================================"
echo ""
echo "Press Ctrl+C to stop all dashboards"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping all dashboards..."
    kill $PROJ344_PID 2>/dev/null
    kill $LEGAL_PID 2>/dev/null
    kill $CEO_PID 2>/dev/null
    kill $ENHANCED_PID 2>/dev/null
    kill $TIMELINE_PID 2>/dev/null
    kill $MASTER5WH_PID 2>/dev/null
    echo "✅ All dashboards stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for all background processes
wait
