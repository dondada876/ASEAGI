# Quick Fix: Deploy All 5 Dashboards

## Problem
- Ports 8501-8503: Duplicates or working
- Port 8504: Not functioning
- Port 8505: Not functioning

## Solution
I've fixed your `docker-compose.yml` with proper configuration for all 5 dashboards.

---

## Deploy Now (5 minutes)

### Step 1: SSH into your droplet

```bash
ssh root@137.184.1.91
```

### Step 2: Navigate to project

```bash
cd /opt/ASEAGI
```

### Step 3: Pull latest changes

```bash
git pull origin main
```

If you get merge conflicts, just force update:
```bash
git fetch origin main
git reset --hard origin/main
```

### Step 4: Stop current containers

```bash
docker compose down
```

### Step 5: Remove old images (clean slate)

```bash
docker system prune -f
```

### Step 6: Build fresh images

```bash
docker compose build --no-cache
```

This will take 2-3 minutes.

### Step 7: Start all dashboards

```bash
docker compose up -d
```

### Step 8: Verify all running

```bash
docker compose ps
```

You should see:
```
NAME                          STATUS
proj344-master-dashboard      Up (healthy)
legal-intelligence-dashboard  Up (healthy)
ceo-dashboard                 Up (healthy)
scanning-monitor-dashboard    Up (healthy)
timeline-dashboard            Up (healthy)
```

### Step 9: Check logs for errors

```bash
docker compose logs -f
```

Press `Ctrl+C` to exit logs.

### Step 10: Test each dashboard

Open in browser:
- http://137.184.1.91:8501 (Master)
- http://137.184.1.91:8502 (Legal Intelligence)
- http://137.184.1.91:8503 (CEO)
- http://137.184.1.91:8504 (Scanning Monitor)
- http://137.184.1.91:8505 (Timeline)

---

## Troubleshooting

### If a container shows "Unhealthy"

```bash
# Check specific logs
docker compose logs container-name

# Example:
docker compose logs proj344-master-dashboard
```

### If port is already in use

```bash
# Find what's using the port
lsof -i :8501

# Kill the process
kill -9 PID
```

### If containers won't start

```bash
# Check environment variables
cat .env

# Make sure these are set:
# SUPABASE_URL=...
# SUPABASE_KEY=...
```

### If you see "No such file or directory"

```bash
# You might be in wrong directory
pwd

# Should show: /opt/ASEAGI
# If not:
cd /opt/ASEAGI
```

---

## What Was Fixed

1. **Master Dashboard (8501)**
   - Added missing `streamlit run` command
   - Now properly launches

2. **Legal Intelligence (8502)**
   - Already working, no changes

3. **CEO Dashboard (8503)**
   - Already working, no changes

4. **Scanning Monitor (8504)**
   - Added to docker-compose (was missing)
   - Uses `enhanced_scanning_monitor.py`
   - Added health checks

5. **Timeline Dashboard (8505)**
   - Added to docker-compose (was missing)
   - Uses `timeline_violations_dashboard.py`
   - Added health checks

---

## After Deployment

All 5 dashboards will be accessible:

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| Master | http://137.184.1.91:8501 | Main case intelligence |
| Legal Intel | http://137.184.1.91:8502 | Document analysis |
| CEO | http://137.184.1.91:8503 | File organization |
| Monitor | http://137.184.1.91:8504 | Scanning progress |
| Timeline | http://137.184.1.91:8505 | Violations tracking |

---

## Complete Command Sequence

Copy-paste this entire block:

```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
git pull origin main
docker compose down
docker compose build --no-cache
docker compose up -d
docker compose ps
```

Then test in browser: http://137.184.1.91:8501

---

## Next Steps (Optional)

See `ARCHITECTURE_COMPARISON.md` for:
- How to consolidate to ONE dashboard (multi-page app)
- Why Flask/Django is overkill
- Resource usage comparison
