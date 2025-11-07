# 📊 ASEAGI DASHBOARDS QUICK REFERENCE

**Last Updated:** 2025-11-06

---

## 🚀 QUICK START

### **Option 1: Interactive Launcher (Easiest)**
```bash
python launch_dashboards.py
```
- Menu-driven interface
- Launch any dashboard
- Launch all at once
- Check what's running
- Kill all dashboards

### **Option 2: Manual Launch**
```bash
# Launch specific dashboard
streamlit run <dashboard_name>.py --server.port=<PORT>
```

### **Option 3: Background Launch**
```bash
# Launch in background (continues running)
nohup streamlit run <dashboard_name>.py --server.port=<PORT> > /dev/null 2>&1 &
```

---

## 📋 ALL DASHBOARDS & PORTS

| # | Dashboard | Port | File | Status |
|---|-----------|------|------|--------|
| 1 | **PROJ344 Master** | 8501 | `proj344_master_dashboard.py` | ✅ Core |
| 2 | **Police Reports** | 8502 | `police_reports_dashboard.py` | ✅ New |
| 3 | **CEO Global** | 8503 | `ceo_global_dashboard.py` | ✅ Core |
| 4 | **Legal Intelligence** | 8504 | `legal_intelligence_dashboard.py` | ✅ Core |
| 5 | **Court Events** | 8505 | `court_events_dashboard.py` | ✅ Core |
| 6 | **Truth Justice Timeline** | 8506 | `truth_justice_timeline.py` | ✅ Core |
| 7 | **Timeline Constitutional** | 8507 | `timeline_constitutional_violations.py` | ✅ Core |
| 8 | **Supabase Diagnostic** | 8508 | `supabase_dashboard.py` | ✅ Core |

---

## 🎯 PRIMARY DASHBOARDS (Start Here)

### **1. PROJ344 Master Dashboard** - Port 8501
**Purpose:** Main legal case intelligence hub

```bash
streamlit run proj344_master_dashboard.py --server.port=8501
```

**Access:** http://localhost:8501

**Features:**
- Document registry with intelligence scores
- Timeline analysis
- Constitutional violations tracker
- Evidence cross-reference
- Multi-jurisdiction support

**Use When:** Need comprehensive case overview

---

### **2. Police Reports Dashboard** - Port 8502
**Purpose:** Police reports tracking and analysis

```bash
streamlit run police_reports_dashboard.py --server.port=8502
```

**Access:** http://localhost:8502

**Features:**
- Police reports filtering and search
- Page-by-page document viewer
- Source image/PDF display
- OCR text viewing
- Score analytics (REL, LEG, MIC, MAC)
- CSV export

**Use When:** Working with police reports specifically

---

### **3. CEO Global Dashboard** - Port 8503
**Purpose:** Executive overview of all systems

```bash
streamlit run ceo_global_dashboard.py --server.port=8503
```

**Access:** http://localhost:8503

**Features:**
- Unified priorities view
- Business operations tracking
- Legal matters summary
- Family documents
- Personal development
- Task management

**Use When:** Need high-level overview across all areas

---

## 🔍 SPECIALIZED DASHBOARDS

### **4. Legal Intelligence Dashboard** - Port 8504
**Purpose:** Document intelligence and scoring

```bash
streamlit run legal_intelligence_dashboard.py --server.port=8504
```

**Access:** http://localhost:8504

**Features:**
- Micro/Macro/Legal/Relevancy scoring
- Smoking guns pitch chart
- Critical documents view
- Score analysis

**Use When:** Deep dive into document intelligence

---

### **5. Court Events Dashboard** - Port 8505
**Purpose:** Court proceedings timeline

```bash
streamlit run court_events_dashboard.py --server.port=8505
```

**Access:** http://localhost:8505

**Features:**
- Court events timeline
- Hearing tracking
- Filing status
- Case progression

**Use When:** Tracking court proceedings

---

### **6. Truth Justice Timeline** - Port 8506
**Purpose:** Truth scoring with 5W+H framework

```bash
streamlit run truth_justice_timeline.py --server.port=8506
```

**Access:** http://localhost:8506

**Features:**
- Truth score calculation
- Justice score rollups
- 5W+H analysis (Who, What, When, Where, Why, How)
- Evidence vs statements

**Use When:** Analyzing credibility and truth

---

### **7. Timeline Constitutional Violations** - Port 8507
**Purpose:** Constitutional violations tracking

```bash
streamlit run timeline_constitutional_violations.py --server.port=8507
```

**Access:** http://localhost:8507

**Features:**
- Due process violations
- Constitutional issues
- Violation timeline
- Evidence documentation

**Use When:** Tracking legal violations

---

### **8. Supabase Diagnostic** - Port 8508
**Purpose:** Database monitoring and diagnostics

```bash
streamlit run supabase_dashboard.py --server.port=8508
```

**Access:** http://localhost:8508

**Features:**
- Database health check
- Table statistics
- Query performance
- Data integrity checks

**Use When:** Troubleshooting database issues

---

## 🔧 MANAGEMENT COMMANDS

### **Check What's Running**
```bash
# Option 1: Using ps
ps aux | grep streamlit

# Option 2: Using netstat
netstat -tlnp | grep 850

# Option 3: Using launcher
python launch_dashboards.py
# Then select 'l' for list
```

### **Stop Specific Dashboard**
```bash
# Find PID
ps aux | grep "streamlit.*<dashboard_name>"

# Kill PID
kill <PID>
```

### **Stop All Dashboards**
```bash
# Option 1: Kill all streamlit
pkill -f streamlit

# Option 2: Using launcher
python launch_dashboards.py
# Then select 'k' for kill all
```

### **Launch All Dashboards**
```bash
# Option 1: Using launcher
python launch_dashboards.py
# Then select 'a' for launch all

# Option 2: Manual (background)
for port in {8501..8508}; do
  file=$(ls *dashboard*.py 2>/dev/null | head -$((port-8500)) | tail -1)
  [ -f "$file" ] && nohup streamlit run "$file" --server.port=$port > /dev/null 2>&1 &
done
```

---

## 🐛 TROUBLESHOOTING

### **Port Already in Use**

**Problem:** `Port 8502 is already in use`

**Solution 1:** Kill process using that port
```bash
# Find what's using the port
lsof -i :8502

# Kill it
kill $(lsof -t -i:8502)
```

**Solution 2:** Use different port
```bash
streamlit run police_reports_dashboard.py --server.port=9502
```

---

### **Dashboard Won't Start**

**Problem:** Dashboard starts but immediately exits

**Check 1:** Missing dependencies
```bash
pip install -r requirements.txt
```

**Check 2:** Supabase credentials
```bash
# Check if .streamlit/secrets.toml exists
ls -la .streamlit/secrets.toml

# If missing, create it:
cat > .streamlit/secrets.toml << 'EOF'
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your-actual-key-here"
EOF
```

**Check 3:** Python errors
```bash
# Run without --server.headless to see errors
streamlit run <dashboard>.py --server.port=<PORT>
```

---

### **Can't Access Dashboard in Browser**

**Problem:** `localhost:8502` won't load

**Check 1:** Dashboard is running
```bash
ps aux | grep "streamlit.*8502"
```

**Check 2:** Firewall
```bash
# Check if port is listening
netstat -tlnp | grep 8502
```

**Check 3:** Try 127.0.0.1 instead
```
http://127.0.0.1:8502
```

---

### **Dashboard Shows Error Page**

**Common Errors:**

**1. "No module named 'supabase'"**
```bash
pip install supabase
```

**2. "Missing SUPABASE_KEY"**
- Add credentials to `.streamlit/secrets.toml`

**3. "Table not found"**
- Check database schema is deployed
- Verify table names in Supabase

**4. "Connection failed"**
- Check Supabase credentials
- Verify internet connection
- Check if Supabase is down

---

## 📊 PORT SUMMARY CHART

```
8501 ┤ PROJ344 Master        (Main Hub)
8502 ┤ Police Reports        (Police Focus)
8503 ┤ CEO Global            (Executive View)
8504 ┤ Legal Intelligence    (Document Scoring)
8505 ┤ Court Events          (Timeline)
8506 ┤ Truth Justice         (Truth Scoring)
8507 ┤ Timeline Violations   (Constitutional)
8508 ┤ Supabase Diagnostic   (Database)
```

---

## 💡 RECOMMENDED WORKFLOW

### **For Daily Legal Work:**
1. Launch PROJ344 Master (8501) - Main view
2. Launch Police Reports (8502) - When needed
3. Launch Truth Justice (8506) - For analysis

### **For Development/Debugging:**
1. Launch Supabase Diagnostic (8508) - Check database
2. Launch specific dashboard being tested
3. Use launcher to manage all

### **For Executive Review:**
1. Launch CEO Global (8503) - High-level overview
2. Launch PROJ344 Master (8501) - Legal details
3. Launch Truth Justice (8506) - Analysis summary

---

## 🚀 PRODUCTION DEPLOYMENT

### **Streamlit Cloud** (Recommended)
```bash
# Each dashboard gets its own URL
https://proj344-master.streamlit.app    (8501)
https://police-reports.streamlit.app     (8502)
https://ceo-global.streamlit.app         (8503)
```

**Setup:**
1. Push to GitHub
2. Connect at streamlit.io/cloud
3. Deploy each dashboard separately
4. Configure secrets in Streamlit dashboard

### **Docker** (Advanced)
```dockerfile
# See Docker deployment guide
# Runs all dashboards in containers
# Managed by docker-compose
```

### **Server** (Self-Hosted)
```bash
# Use nginx reverse proxy
# Map domains to ports
# Run dashboards as services
```

---

## 📝 NOTES

**Port Conflicts:**
- Each dashboard must use unique port
- Ports 8501-8508 reserved for ASEAGI
- If conflict, use 9501-9508 range

**Performance:**
- Running all 8 dashboards uses ~2GB RAM
- Consider launching only needed dashboards
- Use launcher's selective launch feature

**Security:**
- Dashboards accessible to anyone on local network
- For external access, use VPN or authentication
- Never expose ports directly to internet

**Updates:**
- After code changes, restart dashboard
- Streamlit auto-reloads on file save (dev mode)
- In production, restart required

---

## 🆘 QUICK HELP

**I need to:**

**View police reports** → Port 8502
```bash
streamlit run police_reports_dashboard.py --server.port=8502
```

**Check case overview** → Port 8501
```bash
streamlit run proj344_master_dashboard.py --server.port=8501
```

**See executive summary** → Port 8503
```bash
streamlit run ceo_global_dashboard.py --server.port=8503
```

**Analyze truth scores** → Port 8506
```bash
streamlit run truth_justice_timeline.py --server.port=8506
```

**Check database** → Port 8508
```bash
streamlit run supabase_dashboard.py --server.port=8508
```

**Launch everything** → Use launcher
```bash
python launch_dashboards.py
# Select 'a' for all
```

---

**For detailed dashboard documentation, see:**
- `POLICE_REPORTS_DASHBOARD.md` - Police Reports Dashboard
- `README.md` - PROJ344 Master Dashboard
- `48_HOUR_SPRINT_SUMMARY.md` - Recent additions
- `PROJ344_DASHBOARD_GUIDE.md` - General guide

---

**Last Updated:** 2025-11-06
**Version:** 1.0.0
