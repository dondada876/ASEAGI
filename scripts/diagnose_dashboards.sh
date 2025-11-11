#!/bin/bash
# Dashboard Diagnostic Script
# Identifies duplicate dashboards and issues

echo "=========================================="
echo "🔍 Dashboard Diagnostic Report"
echo "=========================================="
echo ""

# Check all Streamlit processes
echo "📊 All Running Streamlit Processes:"
echo "-----------------------------------"
ps aux | grep streamlit | grep -v grep | while read line; do
    echo "$line"
done
echo ""

# Check for duplicate processes
echo "🔄 Checking for Duplicates:"
echo "-----------------------------------"
ps aux | grep streamlit | grep -v grep | awk '{print $NF}' | sort | uniq -c | while read count file; do
    if [ "$count" -gt 1 ]; then
        echo "⚠️  DUPLICATE: $file running $count times"
    else
        echo "✅ OK: $file (single instance)"
    fi
done
echo ""

# Check Docker containers
echo "🐳 Docker Dashboard Containers:"
echo "-----------------------------------"
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" 2>/dev/null || echo "No Docker or not running"
echo ""

# Check port usage
echo "🔌 Port Assignments:"
echo "-----------------------------------"
for port in 8501 8502 8503 8504 8505 8506; do
    process=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$process" ]; then
        cmd=$(ps -p $process -o command=)
        echo "Port $port: ✅ IN USE"
        echo "  Process: $cmd"
    else
        echo "Port $port: ❌ FREE"
    fi
    echo ""
done

# Check Streamlit directories
echo "📁 Dashboard Files:"
echo "-----------------------------------"
find /root -name "*dashboard*.py" -o -name "*monitor*.py" 2>/dev/null | while read file; do
    echo "  $file"
done
echo ""

# Test dashboard accessibility
echo "🌐 Dashboard Accessibility Test:"
echo "-----------------------------------"
for port in 8501 8502 8503 8504 8505 8506; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port --connect-timeout 2 | grep -q "200\|302"; then
        echo "Port $port: ✅ RESPONDING"
    else
        echo "Port $port: ❌ NOT RESPONDING"
    fi
done
echo ""

# Check for error logs
echo "📝 Recent Errors in Logs:"
echo "-----------------------------------"
find /root -name "*.log" -mtime -1 2>/dev/null | while read logfile; do
    if grep -i "error\|duplicate\|fail" "$logfile" 2>/dev/null | tail -5 | grep -q .; then
        echo "Found errors in: $logfile"
        grep -i "error\|duplicate\|fail" "$logfile" | tail -3
        echo ""
    fi
done

echo "=========================================="
echo "✅ Diagnostic Complete"
echo "=========================================="
