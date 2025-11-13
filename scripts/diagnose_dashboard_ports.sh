#!/bin/bash
"""
Dashboard Port Diagnostic Script
Checks what's running on each Streamlit port and verifies no duplicates
"""

echo "================================================================================"
echo "🔍 ASEAGI DASHBOARD PORT DIAGNOSTIC"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check each dashboard port
PORTS=(8501 8502 8503 8504 8505 8506 8507)
PORT_NAMES=(
    "8501:PROJ344 Master Dashboard (ALL documents)"
    "8502:CEO Dashboard (File organization)"
    "8503:Legal Intelligence (High-value docs ≥700)"
    "8504:Enhanced Scanning Monitor"
    "8505:Scanning Monitor"
    "8506:Timeline Violations"
    "8507:System Overview (Database health)"
)

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 PORT STATUS CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

for port in "${PORTS[@]}"; do
    # Get port name
    port_info=$(echo "${PORT_NAMES[@]}" | tr ' ' '\n' | grep "^$port:")
    port_name=$(echo "$port_info" | cut -d':' -f2-)

    echo -e "${BLUE}Port $port${NC}: $port_name"

    # Check if port is listening
    if lsof -i :$port > /dev/null 2>&1; then
        echo -e "  Status: ${GREEN}✅ RUNNING${NC}"

        # Get process info
        pid=$(lsof -ti :$port)
        cmd=$(ps -p $pid -o command= 2>/dev/null)

        echo "  PID: $pid"
        echo "  Command: $cmd"

        # Extract which dashboard file
        dashboard_file=$(echo "$cmd" | grep -o '[^ ]*\.py' | head -1)
        if [ ! -z "$dashboard_file" ]; then
            echo "  Dashboard: $dashboard_file"
        fi

        # Test HTTP response
        http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port --connect-timeout 2 --max-time 5)
        if [ "$http_code" == "200" ]; then
            echo -e "  HTTP: ${GREEN}✅ 200 OK${NC}"
        else
            echo -e "  HTTP: ${RED}❌ $http_code${NC}"
        fi

        # Get page title to verify uniqueness
        title=$(curl -s http://localhost:$port --connect-timeout 2 --max-time 5 | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g' | head -1)
        if [ ! -z "$title" ]; then
            echo "  Page Title: $title"
        fi

    else
        echo -e "  Status: ${RED}❌ NOT RUNNING${NC}"
    fi

    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔄 DUPLICATE PROCESS CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check for duplicate Streamlit processes
echo "All Streamlit processes:"
ps aux | grep streamlit | grep -v grep | while read line; do
    echo "  $line"
done
echo ""

# Count processes per dashboard file
echo "Processes per dashboard:"
ps aux | grep streamlit | grep -v grep | awk '{for(i=11;i<=NF;i++)print $i}' | grep '\.py$' | sort | uniq -c | while read count file; do
    if [ "$count" -gt 1 ]; then
        echo -e "  ${RED}⚠️  $file: $count processes (DUPLICATE!)${NC}"
    else
        echo -e "  ${GREEN}✅ $file: $count process${NC}"
    fi
done
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📂 DASHBOARD FILES CHECK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if dashboard files exist
DASHBOARD_DIR="/root/ASEAGI/dashboards"
if [ -d "$DASHBOARD_DIR" ]; then
    echo "Dashboard directory: $DASHBOARD_DIR"
    echo ""

    EXPECTED_FILES=(
        "proj344_master_dashboard.py"
        "ceo_dashboard.py"
        "legal_intelligence_dashboard.py"
        "enhanced_scanning_monitor.py"
        "scanning_monitor_dashboard.py"
        "timeline_violations_dashboard.py"
        "system_overview_dashboard.py"
    )

    for file in "${EXPECTED_FILES[@]}"; do
        filepath="$DASHBOARD_DIR/$file"
        if [ -f "$filepath" ]; then
            echo -e "  ${GREEN}✅${NC} $file"

            # Check file size
            size=$(stat -f%z "$filepath" 2>/dev/null || stat -c%s "$filepath" 2>/dev/null)
            echo "     Size: $size bytes"

            # Check last modified
            modified=$(stat -f%Sm "$filepath" 2>/dev/null || stat -c%y "$filepath" 2>/dev/null)
            echo "     Modified: $modified"

            # Check for unique identifiers in file
            if grep -q "High-Value Documents" "$filepath" 2>/dev/null; then
                echo "     ✅ Contains unique content: High-Value Documents filter"
            fi

            if grep -q "System Overview Dashboard" "$filepath" 2>/dev/null; then
                echo "     ✅ Contains unique content: System Overview"
            fi

        else
            echo -e "  ${RED}❌${NC} $file (MISSING!)"
        fi
        echo ""
    done
else
    echo -e "${RED}❌ Dashboard directory not found: $DASHBOARD_DIR${NC}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🧪 QUERY UNIQUENESS TEST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Checking for unique queries in each dashboard..."
echo ""

# Check legal_intelligence_dashboard has filter
if grep -q "gte('relevancy_number', 700)" "$DASHBOARD_DIR/legal_intelligence_dashboard.py" 2>/dev/null; then
    echo -e "${GREEN}✅${NC} legal_intelligence_dashboard.py: HAS relevancy ≥ 700 filter"
else
    echo -e "${RED}❌${NC} legal_intelligence_dashboard.py: MISSING relevancy filter (will show ALL docs!)"
fi

# Check system_overview_dashboard exists
if [ -f "$DASHBOARD_DIR/system_overview_dashboard.py" ]; then
    echo -e "${GREEN}✅${NC} system_overview_dashboard.py: File exists"
else
    echo -e "${RED}❌${NC} system_overview_dashboard.py: FILE MISSING!"
fi

# Check enhanced_scanning_monitor has Supabase
if grep -q "init_supabase" "$DASHBOARD_DIR/enhanced_scanning_monitor.py" 2>/dev/null; then
    echo -e "${GREEN}✅${NC} enhanced_scanning_monitor.py: HAS Supabase integration"
else
    echo -e "${RED}❌${NC} enhanced_scanning_monitor.py: MISSING Supabase integration"
fi

echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 RECOMMENDATIONS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Count issues
issues=0

# Check for missing ports
for port in "${PORTS[@]}"; do
    if ! lsof -i :$port > /dev/null 2>&1; then
        ((issues++))
    fi
done

# Check for duplicate processes
duplicate_count=$(ps aux | grep streamlit | grep -v grep | awk '{for(i=11;i<=NF;i++)print $i}' | grep '\.py$' | sort | uniq -c | awk '$1 > 1' | wc -l)
if [ "$duplicate_count" -gt 0 ]; then
    ((issues++))
fi

if [ $issues -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Dashboards are running correctly.${NC}"
else
    echo -e "${YELLOW}⚠️  Found $issues issue(s). Recommended actions:${NC}"
    echo ""
    echo "1. Stop all Streamlit processes:"
    echo "   pkill -f streamlit"
    echo ""
    echo "2. Pull latest code:"
    echo "   cd /root/ASEAGI"
    echo "   git pull origin claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC"
    echo ""
    echo "3. Restart all dashboards:"
    echo "   cd /root/ASEAGI/dashboards"
    echo "   nohup streamlit run proj344_master_dashboard.py --server.port 8501 > /tmp/dash-8501.log 2>&1 &"
    echo "   nohup streamlit run ceo_dashboard.py --server.port 8502 > /tmp/dash-8502.log 2>&1 &"
    echo "   nohup streamlit run legal_intelligence_dashboard.py --server.port 8503 > /tmp/dash-8503.log 2>&1 &"
    echo "   nohup streamlit run enhanced_scanning_monitor.py --server.port 8504 > /tmp/dash-8504.log 2>&1 &"
    echo "   nohup streamlit run scanning_monitor_dashboard.py --server.port 8505 > /tmp/dash-8505.log 2>&1 &"
    echo "   nohup streamlit run timeline_violations_dashboard.py --server.port 8506 > /tmp/dash-8506.log 2>&1 &"
    echo "   nohup streamlit run system_overview_dashboard.py --server.port 8507 > /tmp/dash-8507.log 2>&1 &"
    echo ""
    echo "4. Verify all are running:"
    echo "   ps aux | grep streamlit"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 LOG FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Check dashboard logs for errors:"
for port in "${PORTS[@]}"; do
    logfile="/tmp/dash-$port.log"
    if [ -f "$logfile" ]; then
        errors=$(grep -i "error" "$logfile" 2>/dev/null | wc -l)
        if [ "$errors" -gt 0 ]; then
            echo -e "  Port $port: ${RED}$errors errors found${NC} - tail -50 $logfile"
        else
            echo -e "  Port $port: ${GREEN}No errors${NC}"
        fi
    else
        echo -e "  Port $port: ${YELLOW}No log file${NC}"
    fi
done

echo ""
echo "================================================================================"
echo "✅ DIAGNOSTIC COMPLETE"
echo "================================================================================"
