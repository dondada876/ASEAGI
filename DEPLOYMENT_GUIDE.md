# ASEAGI Complete Deployment Guide

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

Complete guide for deploying the ASEAGI legal case intelligence system.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Prerequisites](#prerequisites)
4. [Database Setup](#database-setup)
5. [MCP Server Setup](#mcp-server-setup)
6. [Telegram Bot API Setup](#telegram-bot-api-setup)
7. [Timeline Dashboards Setup](#timeline-dashboards-setup)
8. [Testing & Verification](#testing--verification)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The ASEAGI system consists of 4 major components:

1. **Supabase Database** - PostgreSQL database with 3 NON-NEGOTIABLE tables
2. **MCP Server** - Model Context Protocol server for Claude Desktop integration
3. **Telegram Bot API** - FastAPI backend for Telegram bot commands
4. **Timeline Dashboards** - Streamlit dashboards for visualization

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     ASEAGI System                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐
│ Claude Desktop  │────────>│   MCP Server    │
│   (localhost)   │  stdio  │  (Python 3.11)  │
└─────────────────┘         └────────┬────────┘
                                     │
┌─────────────────┐         ┌───────▼─────────┐
│ Telegram Bot    │────────>│  FastAPI Server │
│   (anywhere)    │  HTTP   │  (port 8000)    │
└─────────────────┘         └────────┬────────┘
                                     │
┌─────────────────┐                  │
│   Streamlit     │                  │
│   Dashboards    │                  │
│  (port 8501)    │                  │
└────────┬────────┘                  │
         │                           │
         │      ┌────────────────────▼────────────────┐
         └─────>│    Supabase PostgreSQL Database     │
                │  (NON-NEGOTIABLE TABLES)            │
                │  • events (timeline)                │
                │  • document_journal (processing)    │
                │  • communications (evidence)        │
                └─────────────────────────────────────┘
```

---

## ✅ Prerequisites

### Required Software

- Python 3.11+ ([python.org](https://python.org))
- Git ([git-scm.com](https://git-scm.com))
- Docker Desktop (optional, for containerized deployment)
- Claude Desktop (optional, for MCP server)

### Required Accounts

- Supabase account ([supabase.com](https://supabase.com))
- Telegram Bot Token (optional, from [@BotFather](https://t.me/botfather))

### Required Keys

- Supabase URL: `https://jvjlhxodmbkodzmggwpu.supabase.co`
- Supabase Anon Key: Get from [Supabase Dashboard](https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/settings/api)

---

## 🗄️ Database Setup

### Step 1: Create NON-NEGOTIABLE Tables

These 3 tables are **CRITICAL and NON-NEGOTIABLE**:

1. **communications** - Evidence tracking
2. **events** - Timeline (MOST IMPORTANT)
3. **document_journal** - Processing & growth assessment

#### Execute SQL Script

1. Go to [Supabase SQL Editor](https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql)
2. Click "New Query"
3. Copy entire contents of `mcp-servers/aseagi-mvp-server/database/01_create_critical_tables.sql`
4. Paste into SQL Editor
5. Click "Run" (or press Cmd/Ctrl + Enter)
6. Verify success message: "✓ ASEAGI Critical Tables Created Successfully"

#### Verify Tables Exist

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('communications', 'events', 'document_journal');
```

Should return 3 rows.

### Step 2: Review Table Structure

#### communications (Evidence)
- Tracks all texts, emails, letters, communications
- Critical columns: `sender`, `recipient`, `truthfulness_score`, `contains_contradiction`
- **Why critical:** Every communication is potential evidence

#### events (Timeline - MOST IMPORTANT)
- Tracks all hearings, filings, motions, rulings, deadlines
- Critical columns: `event_date`, `event_title`, `event_type`, `significance_score`
- **Why critical:** Timeline is the most important factor for case progression

#### document_journal (Processing & Growth)
- Journal entry for each document scan or processing step
- Critical columns: `original_filename`, `relevancy_score`, `processing_status`, `insights_extracted`
- **Why critical:** Essential to fix, upgrade, and assess long-term growth

---

## 🔌 MCP Server Setup

The MCP server enables Claude Desktop to query your Supabase database.

### Step 1: Install Dependencies

```bash
cd /home/user/ASEAGI/mcp-servers/aseagi-mvp-server

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and add your Supabase key
nano .env
```

Your `.env` should contain:
```bash
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGc...your-actual-key-here
```

### Step 3: Test the Server

```bash
python3 server.py
```

You should see:
```
INFO - Starting ASEAGI MVP MCP Server...
INFO - For Ashe - Protecting children through intelligent legal assistance
INFO - ✓ Supabase connection verified
INFO - ✓ MCP server ready - waiting for connections...
```

Press `Ctrl+C` to stop.

### Step 4: Configure Claude Desktop

#### macOS / Linux
Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aseagi": {
      "command": "python3",
      "args": [
        "/home/user/ASEAGI/mcp-servers/aseagi-mvp-server/server.py"
      ],
      "env": {
        "SUPABASE_URL": "https://jvjlhxodmbkodzmggwpu.supabase.co",
        "SUPABASE_KEY": "your-supabase-anon-key-here"
      }
    }
  }
}
```

#### Windows
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aseagi": {
      "command": "python",
      "args": [
        "C:\\Users\\YourName\\ASEAGI\\mcp-servers\\aseagi-mvp-server\\server.py"
      ],
      "env": {
        "SUPABASE_URL": "https://jvjlhxodmbkodzmggwpu.supabase.co",
        "SUPABASE_KEY": "your-supabase-anon-key-here"
      }
    }
  }
}
```

### Step 5: Restart Claude Desktop

Fully quit and restart Claude Desktop:
- macOS: `Cmd+Q`
- Windows: Right-click taskbar → Quit

Look for 🔧 icon in Claude Desktop chat interface.

---

## 🤖 Telegram Bot API Setup

### Step 1: Navigate to Directory

```bash
cd /home/user/ASEAGI/telegram-bot
```

### Step 2: Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and add your Supabase key
nano .env
```

Your `.env` should contain:
```bash
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGc...your-actual-key-here
PORT=8000
```

### Option A: Run Locally (Development)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run server
python3 api_server.py
```

Server available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

### Option B: Run with Docker (Production)

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop server
docker-compose down
```

### Step 3: Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Status command
curl http://localhost:8000/telegram/status

# Events command
curl http://localhost:8000/telegram/events

# Documents command
curl http://localhost:8000/telegram/documents
```

---

## 📊 Timeline Dashboards Setup

Three Streamlit dashboards for visualizing case data.

### Step 1: Install Streamlit

```bash
cd /home/user/ASEAGI

# If using virtual environment
python3 -m venv venv
source venv/bin/activate

# Install streamlit
pip install streamlit supabase pandas plotly numpy
```

### Step 2: Configure Environment

Set environment variables for Supabase connection:

```bash
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="eyJhbGc...your-actual-key-here"
```

Or create `.streamlit/secrets.toml`:

```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml <<EOF
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGc...your-actual-key-here"
EOF
```

### Step 3: Launch Dashboards

#### Dashboard 1: Truth & Justice Timeline
```bash
streamlit run truth_justice_timeline.py
```
- URL: http://localhost:8501
- Features: Truth scoring, justice score, 5W+H analysis

#### Dashboard 2: Timeline & Constitutional Violations
```bash
streamlit run timeline_constitutional_violations.py
```
- URL: http://localhost:8501
- Features: Timeline matrix, August 2024 incident analysis

#### Dashboard 3: Court Events Dashboard
```bash
streamlit run court_events_dashboard.py
```
- URL: http://localhost:8501
- Features: Event timeline, upcoming deadlines, case overview

---

## ✅ Testing & Verification

### Database Verification

```sql
-- Check all 3 tables exist
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('communications', 'events', 'document_journal');

-- Count records
SELECT COUNT(*) FROM communications;
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM document_journal;

-- Test queries
SELECT * FROM communications LIMIT 5;
SELECT * FROM events ORDER BY event_date DESC LIMIT 5;
SELECT * FROM document_journal WHERE processing_status = 'completed' LIMIT 5;
```

### MCP Server Verification

1. Start Claude Desktop
2. Look for 🔧 icon in chat
3. Type: "Search for documents about custody"
4. Verify Claude can access your database

### Telegram Bot API Verification

```bash
# Test all endpoints
curl http://localhost:8000/health
curl http://localhost:8000/telegram/status
curl http://localhost:8000/telegram/events
curl http://localhost:8000/telegram/documents
curl http://localhost:8000/telegram/communications
curl http://localhost:8000/telegram/evidence
curl http://localhost:8000/telegram/help
```

### Timeline Dashboard Verification

1. Launch dashboard: `streamlit run truth_justice_timeline.py`
2. Open browser to http://localhost:8501
3. Verify data loads without errors
4. Check all visualizations render correctly

---

## 🐛 Troubleshooting

### "relation 'events' does not exist"

**Problem:** NON-NEGOTIABLE tables not created

**Solution:**
1. Run `mcp-servers/aseagi-mvp-server/database/01_create_critical_tables.sql` in Supabase SQL Editor
2. Verify tables exist with SQL query above

---

### "Missing Supabase credentials"

**Problem:** SUPABASE_URL or SUPABASE_KEY not set

**Solution:**
```bash
# Check .env file
cat .env

# Should show both URL and KEY
# If missing, edit .env and add them
```

---

### MCP Server not showing in Claude Desktop

**Problem:** Config file not found or malformed

**Solution:**
1. Verify config location:
   - macOS/Linux: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Validate JSON at https://jsonlint.com
3. Fully quit Claude Desktop (Cmd+Q / Right-click Quit)
4. Restart Claude Desktop
5. Look for 🔧 icon

---

### Telegram Bot can't reach API

**Problem:** API server not running or wrong URL

**Solution:**

If running locally:
```bash
# Start API server
python3 telegram-bot/api_server.py

# Telegram bot should use:
http://localhost:8000/telegram/status
```

If running in Docker:
```bash
# Start Docker container
docker-compose up -d

# Telegram bot should use:
http://api:8000/telegram/status
```

---

### Timeline Dashboard shows no data

**Problem:** Database tables are empty

**Solution:**
1. Check if tables have data:
```sql
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM document_journal;
SELECT COUNT(*) FROM communications;
```

2. If counts are 0, you need to populate the tables:
   - Add events manually or import from existing data
   - Process documents to populate document_journal
   - Add communications manually or import

---

## 📊 Data Migration (If Needed)

If you have existing data in old tables, migrate it:

### From court_events → events

```sql
INSERT INTO events (
    event_date, event_title, event_description, event_type,
    judge_name, event_outcome, significance_score
)
SELECT
    event_date, event_title, event_description, event_type,
    judge_name, event_outcome, significance_score
FROM court_events;
```

### From legal_documents → document_journal

```sql
INSERT INTO document_journal (
    original_filename, document_type,
    relevancy_score, micro_score, processing_status
)
SELECT
    original_filename, document_type,
    relevancy_number, micro_number, 'completed'
FROM legal_documents;
```

### From communications_matrix → communications

```sql
INSERT INTO communications (
    sender, recipient, subject, summary,
    communication_date, communication_method
)
SELECT
    sender, recipient, subject, summary,
    communication_date, communication_method
FROM communications_matrix;
```

---

## 🔐 Security Checklist

- [ ] `.env` files never committed to Git (check `.gitignore`)
- [ ] Supabase anon key has read-only permissions
- [ ] API server only accessible from localhost or Docker network
- [ ] No sensitive data in log files
- [ ] Backup system configured

---

## 📋 System Health Checklist

### Daily Checks (2 min)
- [ ] Database connection working
- [ ] MCP server responding to Claude
- [ ] API server health endpoint: `curl http://localhost:8000/health`
- [ ] Timeline dashboards loading data

### Weekly Reviews (15 min)
- [ ] Review failed queries in logs
- [ ] Check database table sizes
- [ ] Verify backup system working
- [ ] Update documentation as needed

---

## 🎯 Next Steps After Deployment

1. **Populate Database**
   - Add court events to `events` table
   - Process documents to populate `document_journal`
   - Add communications to `communications` table

2. **Test MCP Server**
   - Use Claude Desktop to search documents
   - Query timeline
   - Test all 5 tools

3. **Test Telegram Bot**
   - Send `/status` command
   - Send `/events` command
   - Send `/documents` command
   - Verify all responses

4. **Review Dashboards**
   - Launch each dashboard
   - Verify visualizations
   - Check for data quality issues

---

## 📞 Support Resources

**Documentation:**
- MCP Server: `mcp-servers/aseagi-mvp-server/README.md`
- Telegram Bot API: `telegram-bot/README.md`
- Database Schema: `mcp-servers/aseagi-mvp-server/database/README.md`

**External Resources:**
- Supabase Docs: https://supabase.com/docs
- MCP Protocol: https://modelcontextprotocol.io
- FastAPI Docs: https://fastapi.tiangolo.com
- Streamlit Docs: https://docs.streamlit.io

---

## ✅ Deployment Checklist

### Database
- [ ] Supabase account created
- [ ] Supabase anon key obtained
- [ ] 3 NON-NEGOTIABLE tables created (communications, events, document_journal)
- [ ] Tables verified with SQL query
- [ ] Sample data inserted (optional)

### MCP Server
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with Supabase key
- [ ] Server starts without errors
- [ ] Supabase connection verified
- [ ] Claude Desktop config updated
- [ ] Claude Desktop restarted
- [ ] 🔧 Tools icon visible in Claude

### Telegram Bot API
- [ ] Dependencies installed
- [ ] `.env` file created with Supabase key
- [ ] Server starts (locally or Docker)
- [ ] Health endpoint responds
- [ ] All 7 endpoints tested
- [ ] API docs accessible at /docs

### Timeline Dashboards
- [ ] Streamlit installed
- [ ] Environment variables set
- [ ] Dashboard 1 (Truth & Justice) launches
- [ ] Dashboard 2 (Constitutional Violations) launches
- [ ] Dashboard 3 (Court Events) launches
- [ ] All dashboards show data

### Final Verification
- [ ] All components running simultaneously
- [ ] Database queries working from all services
- [ ] No errors in logs
- [ ] Documentation updated
- [ ] System backed up

---

**Deployment Complete!** 🎉

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

*"When children speak, truth must roar louder than lies."*

---

**Last Updated:** November 2025
**Version:** 1.0.0
**Status:** Production Ready
