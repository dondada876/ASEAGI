# 🔍 Docker Container Diagnostics & Health Monitoring

**Why are containers stopping/restarting?**

This guide helps you diagnose and fix container stability issues.

---

## 🚨 Quick Diagnosis Commands

Run these on your droplet to see what's happening:

```bash
ssh root@137.184.1.91

# 1. Check which containers are running
docker ps -a

# 2. Check container health status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}"

# 3. Check container restart counts
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.RestartCount}}"

# 4. Check system resources (RAM/CPU)
docker stats --no-stream

# 5. Check Docker system health
docker system df
```

---

## 📊 Understanding Container Status

### **Healthy States:**
```
STATUS                          MEANING
Up X minutes (healthy)          ✅ Running and healthy
Up X hours                      ✅ Running (no health check defined)
```

### **Unhealthy States:**
```
STATUS                          MEANING                    ACTION NEEDED
Restarting                      🔄 Crash loop              Check logs immediately
Up X minutes (unhealthy)        ❌ Running but failing     Check health endpoint
Exited (0)                      ⚠️ Stopped normally        May need restart
Exited (1)                      ❌ Crashed with error      Check logs
Exited (137)                    💀 Killed (out of memory)  Increase RAM
Created                         ⏸️ Not started yet         Run: docker start
```

---

## 📁 Where Are Logs Located?

### **1. Docker Container Logs** (Primary)

Each container has its own log:

```bash
# View API logs (last 50 lines)
docker logs aseagi-api --tail 50

# View bot logs (last 50 lines)
docker logs aseagi-telegram --tail 50

# View dashboard logs
docker logs proj344-master-dashboard --tail 50
docker logs legal-intelligence-dashboard --tail 50
docker logs ceo-dashboard --tail 50

# Follow logs in real-time (live updates)
docker logs -f aseagi-api

# View logs with timestamps
docker logs --timestamps aseagi-api --tail 50

# View ALL logs (entire history)
docker logs aseagi-api

# Save logs to file for review
docker logs aseagi-api > /tmp/api-logs.txt
docker logs aseagi-telegram > /tmp/bot-logs.txt
```

### **2. System Logs** (DigitalOcean Level)

```bash
# System-wide Docker logs
journalctl -u docker.service --no-pager -n 100

# Kernel messages (if containers killed by OOM)
dmesg | grep -i "killed process"

# Check if out-of-memory killer ran
grep -i "out of memory" /var/log/syslog

# System resource usage
free -h
df -h
top -bn1 | head -20
```

### **3. Application Logs** (Inside Containers)

```bash
# If your app writes to log files inside container
docker exec aseagi-api cat /app/logs/error.log
docker exec aseagi-api ls -la /app/logs/
```

---

## 🔍 Diagnosing Common Issues

### **Issue 1: Container Keeps Restarting (Crash Loop)**

**Symptoms:**
- Container status shows "Restarting"
- Restart count keeps increasing

**Diagnose:**
```bash
# Check logs to see what's crashing
docker logs aseagi-api --tail 100

# Look for these error patterns:
# - "ModuleNotFoundError" → Missing Python package
# - "connection refused" → Can't connect to database
# - "EADDRINUSE" → Port already in use
# - "Killed" → Out of memory
```

**Common Causes:**
1. **Missing environment variables**
   ```bash
   # Check .env file
   cat /opt/ASEAGI/.env | grep -E "SUPABASE|TELEGRAM"
   ```

2. **Port conflict**
   ```bash
   # Check if port 8000 already in use
   netstat -tlnp | grep 8000
   ```

3. **Out of memory**
   ```bash
   # Check available memory
   free -h
   docker stats --no-stream
   ```

---

### **Issue 2: Container Unhealthy**

**Symptoms:**
- Status shows "Up X minutes (unhealthy)"
- Container running but health check failing

**Diagnose:**
```bash
# Check what health check is failing
docker inspect aseagi-api --format='{{json .State.Health}}' | jq

# Test health endpoint manually
curl http://localhost:8000/health

# Check API is responding
docker exec aseagi-api curl -f http://localhost:8000/health
```

**Fix:**
```bash
# Restart the unhealthy container
docker restart aseagi-api

# Or rebuild and restart
cd /opt/ASEAGI
docker compose -f docker-compose.bot.yml up -d --build api
```

---

### **Issue 3: Out of Memory (OOM Killed)**

**Symptoms:**
- Container exits with code 137
- System logs show "Out of memory"
- Containers randomly stop

**Diagnose:**
```bash
# Check available memory
free -h

# Check Docker memory usage
docker stats --no-stream

# Check if OOM killer ran
dmesg | tail -50 | grep -i "killed process"
grep "Out of memory" /var/log/syslog | tail -20
```

**Fix:**

**Option 1: Add swap space**
```bash
# Check current swap
swapon --show

# Add 4GB swap if none
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

**Option 2: Limit container memory**
```bash
# Edit docker-compose.bot.yml
# Add memory limits:
services:
  api:
    mem_limit: 1g
  telegram:
    mem_limit: 512m
```

**Option 3: Upgrade droplet**
- Current: 16GB RAM
- If using >14GB consistently, upgrade to 32GB

---

### **Issue 4: Network Issues (Can't Resolve 'api')**

**Symptoms:**
- Bot can't connect to API
- Error: "Failed to resolve 'api'"

**Diagnose:**
```bash
# Check Docker network exists
docker network ls | grep aseagi

# Check containers on same network
docker network inspect aseagi_aseagi-network

# Test connectivity between containers
docker exec aseagi-telegram ping -c 2 api
docker exec aseagi-telegram curl http://api:8000/health
```

**Fix:**
```bash
# Recreate network and containers
cd /opt/ASEAGI
docker compose -f docker-compose.bot.yml down
docker network prune -f
docker compose -f docker-compose.bot.yml up -d
```

---

## 📈 Monitoring Container Health

### **Real-Time Monitoring**

```bash
# Watch container status (updates every 2 seconds)
watch -n 2 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}"'

# Monitor resource usage in real-time
docker stats

# Watch logs live
docker logs -f aseagi-api
```

### **Health Check Script**

Create a monitoring script:

```bash
# Create health check script
cat > /root/check-containers.sh << 'EOF'
#!/bin/bash
echo "=== Container Health Check ==="
echo "Time: $(date)"
echo ""

echo "=== Running Containers ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.State}}"
echo ""

echo "=== Resource Usage ==="
docker stats --no-stream
echo ""

echo "=== Recent Errors ==="
docker logs aseagi-api --tail 5 2>&1 | grep -i error || echo "No errors"
docker logs aseagi-telegram --tail 5 2>&1 | grep -i error || echo "No errors"
echo ""

echo "=== Memory Usage ==="
free -h
echo ""

echo "=== Disk Usage ==="
df -h /
EOF

chmod +x /root/check-containers.sh

# Run it
/root/check-containers.sh
```

### **Automated Monitoring (Optional)**

```bash
# Run health check every 5 minutes
crontab -e

# Add this line:
*/5 * * * * /root/check-containers.sh >> /var/log/container-health.log 2>&1

# View monitoring log
tail -f /var/log/container-health.log
```

---

## 🔧 Comprehensive Log Review

### **Review All Logs at Once**

```bash
# Create comprehensive log dump
cat > /root/dump-all-logs.sh << 'EOF'
#!/bin/bash
LOG_DIR="/tmp/aseagi-logs-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$LOG_DIR"

echo "Collecting logs to: $LOG_DIR"

# Container logs
docker logs aseagi-api > "$LOG_DIR/api.log" 2>&1
docker logs aseagi-telegram > "$LOG_DIR/telegram.log" 2>&1
docker logs proj344-master-dashboard > "$LOG_DIR/dashboard1.log" 2>&1
docker logs legal-intelligence-dashboard > "$LOG_DIR/dashboard2.log" 2>&1
docker logs ceo-dashboard > "$LOG_DIR/dashboard3.log" 2>&1

# System logs
docker ps -a > "$LOG_DIR/container-status.txt"
docker stats --no-stream > "$LOG_DIR/resource-usage.txt"
free -h > "$LOG_DIR/memory.txt"
df -h > "$LOG_DIR/disk.txt"

# Docker network info
docker network ls > "$LOG_DIR/networks.txt"
docker network inspect aseagi_aseagi-network > "$LOG_DIR/network-details.json" 2>&1

# System logs
journalctl -u docker.service -n 100 --no-pager > "$LOG_DIR/docker-system.log" 2>&1
dmesg | tail -100 > "$LOG_DIR/kernel.log" 2>&1

echo "Logs collected in: $LOG_DIR"
ls -lh "$LOG_DIR"
EOF

chmod +x /root/dump-all-logs.sh

# Run it
/root/dump-all-logs.sh

# Review collected logs
ls -la /tmp/aseagi-logs-*
```

---

## 🎯 Quick Troubleshooting Checklist

Run these commands in order and note any errors:

```bash
# 1. Check container status
docker ps -a | grep aseagi

# 2. Check for errors in API
docker logs aseagi-api --tail 20 2>&1 | grep -i error

# 3. Check for errors in bot
docker logs aseagi-telegram --tail 20 2>&1 | grep -i error

# 4. Check memory usage
free -h

# 5. Check disk space
df -h

# 6. Check network connectivity
docker exec aseagi-telegram ping -c 2 api

# 7. Test API health
curl http://localhost:8000/health

# 8. Check restart counts
docker ps -a --format "table {{.Names}}\t{{.RestartCount}}"
```

---

## 📊 Expected Healthy State

When everything is working correctly:

```bash
$ docker ps --format "table {{.Names}}\t{{.Status}}"

NAMES                           STATUS
aseagi-telegram                 Up 2 hours
aseagi-api                      Up 2 hours (healthy)
proj344-master-dashboard        Up 5 hours (healthy)
legal-intelligence-dashboard    Up 5 hours (healthy)
ceo-dashboard                   Up 5 hours (healthy)
aseagi-redis                    Up 2 hours (healthy)
```

```bash
$ docker stats --no-stream

CONTAINER          CPU %    MEM USAGE / LIMIT     MEM %
aseagi-api         2.5%     850MB / 16GB          5.3%
aseagi-telegram    0.5%     120MB / 16GB          0.75%
dashboards         3%       1.2GB / 16GB          7.5%
```

---

## 🚨 Red Flags to Watch For

### **Immediate Action Needed:**
- Restart count > 5
- Memory usage > 90%
- Disk usage > 85%
- Status shows "Exited" or "Restarting"
- Logs show "Killed" or "OOM"

### **Investigate Soon:**
- Status shows "unhealthy"
- Memory usage > 75%
- Containers keep restarting
- Logs show frequent errors

---

## 📞 What to Share for Help

If you need help diagnosing, share these outputs:

```bash
# Run all diagnostics
docker ps -a
docker stats --no-stream
free -h
docker logs aseagi-api --tail 50 2>&1
docker logs aseagi-telegram --tail 50 2>&1
```

---

**For Ashe. For Justice. For All Children.** 🛡️
