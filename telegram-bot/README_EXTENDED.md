# ASEAGI Extended API Server - DEFINITIVE SOLUTION

**The Complete Answer to: Flask vs Streamlit**

This is the **production-ready solution** that replaces your 3 duplicate Streamlit dashboards with a unified, error-checked, FastAPI-based web interface.

---

## 🎯 What This Solves

### Your Problem
- 3 Streamlit dashboards (ports 8501-8503) showing **duplicate information**
- No error checking for NON-NEGOTIABLE table schema
- Not production-ready
- Limited multi-user support

### The Solution
✅ **Single FastAPI server** with both Telegram bot API and Web interface
✅ **Comprehensive schema validation** on startup
✅ **Distinct data views** for each dashboard purpose
✅ **Production-ready** with error handling & monitoring
✅ **Modern frontend** with responsive design

---

## 📁 Files in This Solution

```
telegram-bot/
├── api_server_extended.py     # Main FastAPI server (PRODUCTION VERSION)
├── schema_validator.py         # Database schema validation
├── static/
│   └── dashboard.html          # Modern web interface
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Production deployment
├── docker-compose.yml          # Easy orchestration
└── README_EXTENDED.md          # This file
```

---

## 🚀 Quick Start

### Option 1: Run Extended Server (Recommended)

```bash
cd /home/user/ASEAGI/telegram-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your SUPABASE_KEY

# Run EXTENDED server (replaces old api_server.py)
python3 api_server_extended.py
```

**Server will be available at:**
- Web Interface: http://localhost:8000/static/dashboard.html
- Telegram API: http://localhost:8000/telegram/*
- Web API: http://localhost:8000/api/dashboard/*
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Schema Validation: http://localhost:8000/schema/validate

### Option 2: Validate Schema Only

```bash
# Test schema validation
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-key-here"
python3 schema_validator.py
```

---

## 📊 API Endpoints

### Schema Validation Endpoints (NEW)

**GET** `/schema/validate` - Validate NON-NEGOTIABLE tables
```bash
curl http://localhost:8000/schema/validate
```

**GET** `/schema/status` - Get schema validation status
```bash
curl http://localhost:8000/schema/status
```

### Telegram Bot API (Existing)

All `/telegram/*` endpoints from original `api_server.py`:
- `/telegram/status` - Case status
- `/telegram/events` - Recent events
- `/telegram/documents` - High-relevancy documents
- `/telegram/communications` - Recent communications
- `/telegram/evidence` - Critical evidence
- `/telegram/help` - Available commands

### Web Interface API (NEW)

**GET** `/api/dashboard/overview` - Overview metrics
- Total counts (events, docs, communications)
- Critical items (significance/relevancy ≥ 900)
- **DISTINCT:** General overview, not specialized

**GET** `/api/dashboard/truth-timeline?days=90` - Truth & Justice Timeline
- Timeline with truth scoring
- Justice score calculation
- True/Questionable/False counts
- **DISTINCT:** Focuses on truth scoring and justice metrics

**GET** `/api/dashboard/violations` - Constitutional Violations
- Violations by type
- Critical violations (significance ≥ 800)
- **DISTINCT:** Focuses on legal violations only

**GET** `/api/dashboard/court-events` - Court Events Management
- Upcoming events requiring action
- Recent completed events
- Urgency classification (URGENT/HIGH/NORMAL)
- **DISTINCT:** Focuses on case management and deadlines

---

## ✅ Schema Validation

### What It Validates

The `schema_validator.py` checks:

1. **Table Existence**
   - ✅ `communications` exists
   - ✅ `events` exists
   - ✅ `document_journal` exists

2. **Required Columns**
   - Each table has all required columns
   - Critical columns are present

3. **Data Quality**
   - Column completeness (% non-null)
   - Score ranges (0-1000 validation)
   - Sample data analysis

### Example Output

```
╔═══════════════════════════════════════╗
║  ASEAGI DATABASE SCHEMA VALIDATOR     ║
╚═══════════════════════════════════════╝

🔍 Starting NON-NEGOTIABLE table validation...
✅ Table 'communications' validated successfully
✅ Table 'events' validated successfully
✅ Table 'document_journal' validated successfully
✅ All NON-NEGOTIABLE tables validated successfully

📋 SCHEMA SUMMARY
──────────────────────────────────────

📋 communications
   Description: Evidence tracking - CRITICAL for legal case
   Why Critical: Every communication is potential evidence
   ✅ Exists: Yes
   📊 Records: 127
   ⭐ Quality: good
   📈 Completeness:
      ✅ sender: 100.0%
      ✅ recipient: 100.0%
      ✅ communication_date: 98.4%
      ✅ truthfulness_score: 87.3%

📋 events
   Description: Timeline - MOST IMPORTANT for case progression
   Why Critical: Events are the most important timeline factor
   ✅ Exists: Yes
   📊 Records: 243
   ⭐ Quality: good
   📈 Completeness:
      ✅ event_date: 100.0%
      ✅ event_title: 100.0%
      ✅ event_type: 95.9%
      ⚠️ significance_score: 73.2%

Overall Status: ✅ VALID
```

---

## 🎨 Web Interface Features

### 4 Distinct Dashboards

1. **Overview Dashboard**
   - Total counts (events, documents, communications)
   - Critical items (top 5 each)
   - General metrics

2. **Truth & Justice Timeline**
   - Justice score calculation
   - Truth score distribution chart
   - Timeline with truth scoring
   - True/Questionable/False breakdown

3. **Constitutional Violations**
   - Total violations count
   - Violations by type chart
   - Critical violations list
   - Legal focus

4. **Court Events Management**
   - Urgency classification (URGENT/HIGH/NORMAL)
   - Upcoming events requiring action
   - Recent completed events
   - Deadline management

### Why Each Dashboard is DISTINCT

**Problem:** Your Streamlit dashboards showed duplicate info

**Solution:** Each API endpoint has unique logic:

| Dashboard | Unique Logic | Filters |
|-----------|--------------|---------|
| **Overview** | General metrics | Top 5 critical items only |
| **Truth Timeline** | Calculate truth scores | Shows items with truth implications |
| **Violations** | Filter by violations | Only events with `violations_occurred = True` |
| **Court Events** | Urgency calculation | Only events with `requires_action = True` |

---

## 🛡️ Error Handling

### Database Connection Errors

```json
{
  "error": "CRITICAL: Table 'events' does not exist",
  "detail": "This is a NON-NEGOTIABLE table that must exist. Please run: mcp-servers/aseagi-mvp-server/database/01_create_critical_tables.sql",
  "path": "/api/dashboard/overview",
  "timestamp": "2025-11-07T12:34:56"
}
```

### Schema Validation Errors

```json
{
  "status": "invalid",
  "errors": [
    "❌ Table 'communications' missing REQUIRED columns: {'truthfulness_score'}",
    "🚨 CRITICAL: Table 'events' missing CRITICAL columns: {'significance_score'}"
  ]
}
```

---

## 🔄 Migration from Streamlit

### Before (3 Duplicate Streamlit Dashboards)

```bash
# Port 8501
streamlit run truth_justice_timeline.py

# Port 8502
streamlit run timeline_constitutional_violations.py

# Port 8503
streamlit run court_events_dashboard.py
```

**Issues:**
- ❌ All showing similar data
- ❌ No error checking
- ❌ Separate processes
- ❌ No shared state

### After (1 Unified FastAPI Server)

```bash
# Single server handles everything
python3 api_server_extended.py
```

**Benefits:**
- ✅ Distinct data views
- ✅ Comprehensive error checking
- ✅ Single codebase
- ✅ Shared Telegram bot logic
- ✅ Production-ready

---

## 📈 Deployment

### Development

```bash
python3 api_server_extended.py
```

### Production (Docker)

```bash
docker-compose up -d
```

### Production (Systemd Service)

```bash
sudo nano /etc/systemd/system/aseagi-api.service
```

```ini
[Unit]
Description=ASEAGI API Server
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/user/ASEAGI/telegram-bot
Environment="SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co"
Environment="SUPABASE_KEY=your-key-here"
ExecStart=/home/user/ASEAGI/telegram-bot/venv/bin/python3 api_server_extended.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable aseagi-api
sudo systemctl start aseagi-api
sudo systemctl status aseagi-api
```

---

## 🧪 Testing

### Test Schema Validation

```bash
curl http://localhost:8000/schema/validate
```

### Test Web API Endpoints

```bash
# Overview
curl http://localhost:8000/api/dashboard/overview

# Truth Timeline
curl http://localhost:8000/api/dashboard/truth-timeline?days=90

# Violations
curl http://localhost:8000/api/dashboard/violations

# Court Events
curl http://localhost:8000/api/dashboard/court-events
```

### Test Telegram Bot API

```bash
curl http://localhost:8000/telegram/status
```

---

## 🔧 Configuration

### Environment Variables

```bash
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-supabase-anon-key
PORT=8000
```

### Server Configuration

Edit `api_server_extended.py`:

```python
# Change port
port = int(os.environ.get('PORT', 8000))

# Change validation strictness
validate_schema(supabase, strict=False)  # Warn only
validate_schema(supabase, strict=True)   # Fail on errors
```

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "schema": {
    "overall_status": "valid",
    "tables": {
      "communications": {"exists": true, "record_count": 127},
      "events": {"exists": true, "record_count": 243},
      "document_journal": {"exists": true, "record_count": 601}
    }
  },
  "timestamp": "2025-11-07T12:34:56"
}
```

### Logging

Logs include:
- Schema validation results
- API endpoint access
- Database queries
- Error details

---

## ✅ Checklist: Complete Migration

- [ ] Run `schema_validator.py` to verify tables exist
- [ ] Fix any schema errors found
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Configure `.env` with SUPABASE_KEY
- [ ] Run `python3 api_server_extended.py`
- [ ] Test schema validation: `curl http://localhost:8000/schema/validate`
- [ ] Test web interface: http://localhost:8000/static/dashboard.html
- [ ] Test Telegram API: `curl http://localhost:8000/telegram/status`
- [ ] Stop old Streamlit dashboards (ports 8501-8503)
- [ ] Update Telegram bot to use http://api:8000 (if using Docker)

---

## 🎯 The Definitive Answer

### Question: "Should we use Flask instead of Streamlit?"

**Answer: No. Use your existing FastAPI server extended with web interface endpoints.**

**Why:**
1. ✅ You already have FastAPI for Telegram bot
2. ✅ Shared codebase = less maintenance
3. ✅ Better than Flask (modern async support)
4. ✅ Schema validation built-in
5. ✅ Production-ready from day 1

---

## 📞 Support

**Documentation:**
- FLASK_VS_STREAMLIT_ANALYSIS.md - Detailed comparison
- DEPLOYMENT_GUIDE.md - Full deployment guide
- This file - Extended API documentation

**For Issues:**
Check schema validation first:
```bash
python3 schema_validator.py
```

---

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

*"When children speak, truth must roar louder than lies."*

---

**Version:** 2.0.0
**Status:** Production Ready
**Last Updated:** November 2025
