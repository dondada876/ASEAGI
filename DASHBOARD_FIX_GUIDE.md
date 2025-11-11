# 🔧 Dashboard Fix Guide - Duplicate and Not Working Issues

**Issue:** Dashboard not working and being duplicated
**System:** PROJ344 with 745 documents, 253 court events

---

## 🔍 **Step 1: Diagnose the Issue**

Run this diagnostic on your droplet:

```bash
ssh root@137.184.1.91 << 'EOF'
echo "=========================================="
echo "🔍 Dashboard Status Check"
echo "=========================================="
echo ""

# Check all Streamlit processes
echo "📊 Running Streamlit Dashboards:"
ps aux | grep streamlit | grep -v grep | awk '{print $2, $NF}' | while read pid file; do
    port=$(lsof -p $pid 2>/dev/null | grep LISTEN | awk '{print $9}' | cut -d: -f2)
    echo "  PID: $pid | Port: $port | File: $file"
done
echo ""

# Check for duplicates
echo "🔄 Duplicate Check:"
ps aux | grep streamlit | grep -v grep | awk '{print $NF}' | sort | uniq -c | while read count file; do
    if [ "$count" -gt 1 ]; then
        echo "  ⚠️  DUPLICATE: $file ($count instances)"
    fi
done
echo ""

# Check Docker
echo "🐳 Docker Containers:"
docker ps --format "{{.Names}}: {{.Ports}} - {{.Status}}" 2>/dev/null
echo ""

# Test ports
echo "🔌 Port Status:"
for port in 8501 8502 8503 8504 8505 8506; do
    if lsof -ti:$port > /dev/null 2>&1; then
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port --connect-timeout 2)
        if [ "$response" = "200" ] || [ "$response" = "302" ]; then
            echo "  Port $port: ✅ Working (HTTP $response)"
        else
            echo "  Port $port: ⚠️  Running but not responding (HTTP $response)"
        fi
    else
        echo "  Port $port: ❌ Not in use"
    fi
done

echo ""
echo "=========================================="
EOF
```

---

## 🎯 **Common Issues and Fixes:**

### **Issue 1: Duplicate Dashboards Running**

**Symptom:** Same dashboard running multiple times on different ports

**Cause:** Dashboard was started multiple times without stopping previous instance

**Fix:**
```bash
ssh root@137.184.1.91 << 'EOF'
# Kill all duplicate Streamlit processes
echo "🔪 Stopping all Streamlit dashboards..."
pkill -f streamlit

# Wait for processes to stop
sleep 3

# Verify they're stopped
if ps aux | grep streamlit | grep -v grep; then
    echo "⚠️  Some processes didn't stop. Force killing..."
    pkill -9 -f streamlit
else
    echo "✅ All Streamlit processes stopped"
fi

# Restart only the dashboards you need
echo ""
echo "🚀 Restart your dashboards manually or with Docker"
EOF
```

### **Issue 2: Dashboard Not Responding**

**Symptom:** Dashboard process running but page won't load

**Cause:** Port conflict, crashed dashboard, or network issue

**Fix:**
```bash
ssh root@137.184.1.91 << 'EOF'
# Find the problematic dashboard
PROBLEM_PORT=8501  # Change to your problem port

echo "🔍 Checking port $PROBLEM_PORT..."

# Kill process on that port
PID=$(lsof -ti:$PROBLEM_PORT)
if [ ! -z "$PID" ]; then
    echo "Found process $PID, stopping it..."
    kill -9 $PID
    sleep 2
fi

# Check if it's a Docker container
CONTAINER=$(docker ps | grep $PROBLEM_PORT | awk '{print $1}')
if [ ! -z "$CONTAINER" ]; then
    echo "Found Docker container $CONTAINER, restarting..."
    docker restart $CONTAINER
fi

echo "✅ Port $PROBLEM_PORT cleared"
EOF
```

### **Issue 3: Docker Container Duplicates**

**Symptom:** Multiple containers with same name or on same port

**Fix:**
```bash
ssh root@137.184.1.91 << 'EOF'
echo "🐳 Cleaning up Docker containers..."

# Stop all dashboard containers
docker ps --filter "name=dashboard" --filter "name=monitor" -q | xargs -r docker stop

# Remove stopped containers
docker ps -a --filter "name=dashboard" --filter "name=monitor" -q | xargs -r docker rm

# Restart from docker-compose
cd /root/phase0_bug_tracker  # Or wherever your docker-compose.yml is
docker-compose up -d

echo "✅ Docker containers restarted"
EOF
```

---

## 📋 **Specific Dashboard Fixes:**

### **For "ceo-dashboard" Issues:**
```bash
ssh root@137.184.1.91 << 'EOF'
# Stop CEO dashboard
docker stop ceo-dashboard 2>/dev/null
docker rm ceo-dashboard 2>/dev/null

# Restart it
docker run -d \
  --name ceo-dashboard \
  -p 8503:8501 \
  -v /root/phase0_bug_tracker:/app \
  -e SUPABASE_URL="$SUPABASE_URL" \
  -e SUPABASE_KEY="$SUPABASE_KEY" \
  your-image-name \
  streamlit run dashboards/ceo_dashboard.py

echo "✅ CEO dashboard restarted on port 8503"
EOF
```

### **For "scanning-monitor" Issues:**
```bash
ssh root@137.184.1.91 << 'EOF'
# Stop scanning monitors (both regular and enhanced)
docker stop scanning-monitor enhanced-scanning-monitor 2>/dev/null
docker rm scanning-monitor enhanced-scanning-monitor 2>/dev/null

# Restart scanning-monitor only
docker run -d \
  --name scanning-monitor \
  -p 8505:8501 \
  -v /root/phase0_bug_tracker:/app \
  your-image-name \
  streamlit run dashboards/scanning_monitor.py

echo "✅ Scanning monitor restarted on port 8505"
EOF
```

### **For "timeline-violations" Issues:**
```bash
ssh root@137.184.1.91 << 'EOF'
# Restart timeline dashboard
docker restart timeline-violations

# If that doesn't work, recreate it
if [ $? -ne 0 ]; then
    docker stop timeline-violations
    docker rm timeline-violations
    docker run -d \
      --name timeline-violations \
      -p 8504:8501 \
      -v /root/phase0_bug_tracker:/app \
      your-image-name \
      streamlit run dashboards/timeline_violations.py
fi

echo "✅ Timeline violations dashboard restarted on port 8504"
EOF
```

---

## 🧹 **Complete Clean Slate Fix:**

If you want to stop everything and start fresh:

```bash
ssh root@137.184.1.91 << 'EOF'
echo "🧹 Complete Dashboard Reset"
echo "=========================================="

# 1. Stop all Streamlit processes
echo "1️⃣ Stopping Streamlit processes..."
pkill -9 -f streamlit
sleep 2

# 2. Stop all Docker containers
echo "2️⃣ Stopping Docker containers..."
docker stop $(docker ps -q) 2>/dev/null

# 3. Remove stopped containers
echo "3️⃣ Removing stopped containers..."
docker rm $(docker ps -a -q) 2>/dev/null

# 4. Check what's using ports
echo "4️⃣ Checking ports..."
for port in 8501 8502 8503 8504 8505 8506; do
    PID=$(lsof -ti:$port)
    if [ ! -z "$PID" ]; then
        echo "  Killing process on port $port (PID: $PID)"
        kill -9 $PID
    fi
done

# 5. Restart Docker Compose
echo "5️⃣ Restarting dashboards..."
cd /root/phase0_bug_tracker
docker-compose up -d

# 6. Verify
echo ""
echo "✅ Reset complete!"
echo ""
echo "📊 Running dashboards:"
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"

echo ""
echo "🌐 Access your dashboards at:"
echo "  http://137.184.1.91:8501"
echo "  http://137.184.1.91:8502"
echo "  http://137.184.1.91:8503"
echo "  http://137.184.1.91:8504"
echo "  http://137.184.1.91:8505"
echo "  http://137.184.1.91:8506"
EOF
```

---

## 🎯 **Quick Troubleshooting Checklist:**

Run through these checks:

```bash
ssh root@137.184.1.91 << 'EOF'
echo "✓ Checklist:"
echo ""

# Check 1: Duplicate processes
DUPES=$(ps aux | grep streamlit | grep -v grep | awk '{print $NF}' | sort | uniq -d)
if [ -z "$DUPES" ]; then
    echo "✅ No duplicate processes"
else
    echo "❌ Found duplicates: $DUPES"
fi

# Check 2: Port conflicts
CONFLICTS=0
for port in 8501 8502 8503 8504 8505 8506; do
    COUNT=$(lsof -ti:$port 2>/dev/null | wc -l)
    if [ "$COUNT" -gt 1 ]; then
        echo "❌ Port $port has $COUNT processes (conflict)"
        CONFLICTS=$((CONFLICTS + 1))
    fi
done
if [ $CONFLICTS -eq 0 ]; then
    echo "✅ No port conflicts"
fi

# Check 3: Dashboard responsiveness
DEAD=0
for port in 8501 8502 8503 8504 8505 8506; do
    if lsof -ti:$port > /dev/null 2>&1; then
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port --connect-timeout 2)
        if [ "$RESPONSE" != "200" ] && [ "$RESPONSE" != "302" ]; then
            echo "❌ Port $port not responding (HTTP $RESPONSE)"
            DEAD=$((DEAD + 1))
        fi
    fi
done
if [ $DEAD -eq 0 ]; then
    echo "✅ All dashboards responding"
fi

# Check 4: Docker health
UNHEALTHY=$(docker ps --filter "health=unhealthy" -q | wc -l)
if [ "$UNHEALTHY" -gt 0 ]; then
    echo "❌ $UNHEALTHY unhealthy containers"
    docker ps --filter "health=unhealthy" --format "{{.Names}}: {{.Status}}"
else
    echo "✅ All Docker containers healthy"
fi

echo ""
echo "=========================================="
EOF
```

---

## 🔍 **Specific "Details Results Dashboard" Fix:**

If you have a dashboard specifically called "details results dashboard":

```bash
ssh root@137.184.1.91 << 'EOF'
# Search for the dashboard
echo "🔍 Searching for 'details' or 'results' dashboard..."

# Find the file
DASHBOARD=$(find /root -name "*detail*" -o -name "*result*" 2>/dev/null | grep -i dashboard | head -1)

if [ ! -z "$DASHBOARD" ]; then
    echo "Found: $DASHBOARD"

    # Kill any running instances
    pkill -f "$DASHBOARD"

    # Find which port it should use
    PORT=$(grep -oP '(?<=port=)\d+' "$DASHBOARD" 2>/dev/null || echo "8501")

    # Start it fresh
    cd $(dirname "$DASHBOARD")
    nohup streamlit run $(basename "$DASHBOARD") --server.port=$PORT > /tmp/details_dashboard.log 2>&1 &

    echo "✅ Started on port $PORT"
    echo "📝 Log: /tmp/details_dashboard.log"
else
    echo "❌ Dashboard file not found"
    echo ""
    echo "Available dashboards:"
    find /root -name "*dashboard*.py" 2>/dev/null
fi
EOF
```

---

## 📞 **What Information Do I Need?**

To give you a more specific fix, please run the diagnostic and tell me:

1. **Which dashboard is the problem?**
   - ceo-dashboard?
   - scanning-monitor?
   - timeline-violations?
   - enhanced-scanning-monitor?
   - Or a different one?

2. **What's the exact error?**
   - Dashboard won't load (blank page)?
   - Shows error message?
   - Shows old/stale data?
   - Shows duplicate data?

3. **Run this and show me output:**
```bash
ssh root@137.184.1.91 "docker ps && echo '' && ps aux | grep streamlit | grep -v grep"
```

Once I see the diagnostic output, I can give you an exact fix! 🔧

---

**Run the diagnostic and paste the results here, and I'll give you the precise solution!** 🚀
