# Dashboard Deployment Guide for Droplet (137.184.1.91)

**Last Updated:** November 11, 2025
**Branch:** `claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC`

---

## 🎯 What Was Fixed

### Problem
Multiple dashboards were showing duplicate information:
- **proj344_master_dashboard** (8501) and **legal_intelligence_dashboard** (8503) both showed ALL documents
- **enhanced_scanning_monitor** (8504) didn't query Supabase like **scanning_monitor** (8505) did
- No system-wide health monitoring

### Solution
1. **NEW Dashboard:** System Overview (Port 8507) - System health across all tables
2. **FIXED:** Legal Intelligence (Port 8503) - Now shows ONLY high-value docs (relevancy ≥ 700)
3. **ENHANCED:** Enhanced Scanning Monitor (Port 8504) - Added Supabase queries and database tab

---

## 📊 Dashboard Purposes (No More Duplicates!)

| Port | Dashboard | Unique Purpose |
|------|-----------|----------------|
| **8501** | PROJ344 Master | ALL documents, comprehensive analysis |
| **8502** | CEO Dashboard | File organization (local files, PARA structure) |
| **8503** | Legal Intelligence | HIGH-VALUE docs only (relevancy ≥ 700) |
| **8504** | Enhanced Scanning Monitor | Scan monitoring + Supabase queries |
| **8505** | Scanning Monitor | Basic scan monitoring |
| **8506** | Timeline Violations | Court events timeline |
| **8507** | System Overview | **NEW** - Database health across ALL tables |

---

## 🚀 Deployment Instructions

### Step 1: SSH into Droplet

```bash
ssh root@137.184.1.91
```

### Step 2: Navigate to Repository

```bash
cd /root/ASEAGI  # Or wherever you cloned the repo
```

If the repository doesn't exist on the droplet, clone it first:

```bash
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI
```

### Step 3: Pull Latest Changes

```bash
# Fetch all branches
git fetch origin

# Checkout the branch with fixes
git checkout claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC

# Pull latest changes
git pull origin claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC
```

**Alternative:** If you want to merge into main:

```bash
git checkout main
git merge claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC
```

### Step 4: Verify Files Are Updated

```bash
# Check if new dashboard exists
ls -lh dashboards/system_overview_dashboard.py

# Verify modifications
git log --oneline -5
git diff HEAD~1 dashboards/legal_intelligence_dashboard.py | head -20
```

Expected output:
```
✅ dashboards/system_overview_dashboard.py exists
✅ legal_intelligence_dashboard.py shows "HIGH-VALUE DOCUMENTS ONLY"
✅ enhanced_scanning_monitor.py has Supabase imports
```

### Step 5: Set Environment Variables (If Not Already Set)

```bash
# Verify Supabase credentials are set
echo $SUPABASE_URL
echo $SUPABASE_KEY

# If not set, add them:
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_supabase_anon_key_here"

# Make permanent (add to ~/.bashrc):
echo 'export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"' >> ~/.bashrc
echo 'export SUPABASE_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Step 6: Install/Update Dependencies

```bash
# Ensure Supabase Python client is installed
pip3 install --upgrade supabase streamlit plotly pandas
```

### Step 7: Stop Existing Dashboards

```bash
# Kill all running Streamlit processes
pkill -f streamlit

# Verify they're stopped
ps aux | grep streamlit
```

### Step 8: Start Dashboards

**Option A: Start All Dashboards (Recommended)**

```bash
cd /root/ASEAGI/dashboards

# Start each dashboard in background
nohup streamlit run proj344_master_dashboard.py --server.port 8501 > /tmp/dash-8501.log 2>&1 &
nohup streamlit run ceo_dashboard.py --server.port 8502 > /tmp/dash-8502.log 2>&1 &
nohup streamlit run legal_intelligence_dashboard.py --server.port 8503 > /tmp/dash-8503.log 2>&1 &
nohup streamlit run enhanced_scanning_monitor.py --server.port 8504 > /tmp/dash-8504.log 2>&1 &
nohup streamlit run scanning_monitor_dashboard.py --server.port 8505 > /tmp/dash-8505.log 2>&1 &
nohup streamlit run timeline_violations_dashboard.py --server.port 8506 > /tmp/dash-8506.log 2>&1 &
nohup streamlit run system_overview_dashboard.py --server.port 8507 > /tmp/dash-8507.log 2>&1 &

echo "✅ All dashboards started!"
```

**Option B: Start Only Fixed/New Dashboards**

```bash
cd /root/ASEAGI/dashboards

# Start only modified dashboards
nohup streamlit run legal_intelligence_dashboard.py --server.port 8503 > /tmp/dash-8503.log 2>&1 &
nohup streamlit run enhanced_scanning_monitor.py --server.port 8504 > /tmp/dash-8504.log 2>&1 &
nohup streamlit run system_overview_dashboard.py --server.port 8507 > /tmp/dash-8507.log 2>&1 &

echo "✅ Fixed dashboards started!"
```

### Step 9: Verify Dashboards Are Running

```bash
# Check processes
ps aux | grep streamlit

# Check logs for errors
tail -20 /tmp/dash-8503.log  # Legal Intelligence
tail -20 /tmp/dash-8504.log  # Enhanced Scanning Monitor
tail -20 /tmp/dash-8507.log  # System Overview

# Test port connectivity
for port in 8501 8502 8503 8504 8505 8506 8507; do
  curl -s -o /dev/null -w "Port $port: %{http_code}\n" http://localhost:$port
done
```

Expected output:
```
Port 8501: 200
Port 8502: 200
Port 8503: 200
Port 8504: 200
Port 8505: 200
Port 8506: 200
Port 8507: 200
```

---

## 🧪 Testing the Fixes

### Test 1: Legal Intelligence Dashboard (Port 8503)

```bash
# Access from browser:
# http://137.184.1.91:8503
```

**Expected:**
- Title shows: "Legal Intelligence: High-Value Documents"
- Info message: "This dashboard shows HIGH-VALUE documents only. For ALL documents, use PROJ344 Master Dashboard (Port 8501)"
- Only documents with relevancy ≥ 700 are shown
- Navigation shows "High-Value Documents" (not "All Documents")

### Test 2: Enhanced Scanning Monitor (Port 8504)

```bash
# Access from browser:
# http://137.184.1.91:8504
```

**Expected:**
- New metrics row showing: "🗄️ In Database", "📡 Database", "📊 Upload Success Rate"
- New tab: "🗄️ Database Documents" showing recent docs from Supabase
- Documents display with color-coded relevancy scores
- Expandable summaries with smoking guns

### Test 3: System Overview Dashboard (Port 8507)

```bash
# Access from browser:
# http://137.184.1.91:8507
```

**Expected:**
- Title: "System Overview Dashboard"
- System health gauge showing percentage
- Table list showing all database tables: legal_documents, court_events, bugs, error_logs, legal_violations, legal_citations
- Row counts for each table
- Bug tracker status breakdown
- Recent activity feed across all tables

---

## 🔧 Troubleshooting

### Issue: Dashboard won't start

```bash
# Check logs
tail -50 /tmp/dash-8507.log

# Common fixes:
pip3 install --upgrade supabase streamlit plotly pandas
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"
```

### Issue: Port already in use

```bash
# Find process using port
lsof -ti :8507 | xargs kill

# Or kill all Streamlit processes
pkill -f streamlit
```

### Issue: "Connection Error" on dashboard

```bash
# Verify Supabase credentials
python3 -c "from supabase import create_client; import os; print('✅ Connected' if create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY')).table('bugs').select('count').execute() else '❌ Failed')"

# If fails, check environment variables:
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

### Issue: Legal Intelligence Dashboard still shows all documents

```bash
# Verify file was updated
grep "gte('relevancy_number', 700)" /root/ASEAGI/dashboards/legal_intelligence_dashboard.py

# Should output: .gte('relevancy_number', 700)\

# If not found, re-pull:
git pull origin claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC
pkill -f "streamlit.*8503"
nohup streamlit run dashboards/legal_intelligence_dashboard.py --server.port 8503 > /tmp/dash-8503.log 2>&1 &
```

---

## 📝 Files Modified/Created

**Created:**
- `dashboards/system_overview_dashboard.py` (NEW)

**Modified:**
- `dashboards/legal_intelligence_dashboard.py` (Added relevancy ≥ 700 filter)
- `dashboards/enhanced_scanning_monitor.py` (Added Supabase queries)

**No Deletions:** All existing functionality preserved ✅

---

## 🎯 Verification Checklist

After deployment, verify:

- [ ] All 7 dashboards are running (ports 8501-8507)
- [ ] Legal Intelligence Dashboard shows ONLY high-value docs (relevancy ≥ 700)
- [ ] Enhanced Scanning Monitor has "Database Documents" tab
- [ ] System Overview Dashboard shows all 6 tables with row counts
- [ ] No duplicate information between dashboards
- [ ] All dashboards connect to Supabase successfully
- [ ] No syntax errors in logs

---

## 🔗 Quick Access URLs

Once deployed on droplet:

- http://137.184.1.91:8501 - PROJ344 Master (ALL documents)
- http://137.184.1.91:8502 - CEO Dashboard (File organization)
- http://137.184.1.91:8503 - Legal Intelligence (High-value docs ≥ 700)
- http://137.184.1.91:8504 - Enhanced Scanning Monitor
- http://137.184.1.91:8505 - Scanning Monitor
- http://137.184.1.91:8506 - Timeline Violations
- http://137.184.1.91:8507 - System Overview (NEW!)

---

## 📊 Expected Results

After deployment, each dashboard will have a unique purpose with NO duplicates:

1. **Port 8501** queries ALL documents for comprehensive analysis
2. **Port 8503** queries ONLY docs with `relevancy_number >= 700`
3. **Port 8507** queries row counts across ALL tables (bugs, events, violations, etc.)
4. **Port 8504** now queries Supabase like 8505, but with enhanced visualizations

**Result:** Zero duplication, each dashboard serves a distinct purpose! ✅

---

**Need Help?** Check the troubleshooting section above or review logs at `/tmp/dash-*.log`
