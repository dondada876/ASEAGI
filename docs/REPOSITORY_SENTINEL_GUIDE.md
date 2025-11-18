# Code Repository Sentinel - Complete Guide

**Centralized inventory and monitoring system for all code repositories**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
- [Installation](#installation)
- [Usage](#usage)
- [Automation](#automation)
- [MCP Integration](#mcp-integration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Repository Sentinel is a comprehensive system that:

✅ **Scans** all your code repositories (local and remote)
✅ **Analyzes** languages, dependencies, and code quality
✅ **Stores** metadata in centralized database (Supabase)
✅ **Visualizes** inventory via Streamlit dashboard
✅ **Queries** via Claude Desktop (MCP integration)
✅ **Automates** regular scanning and reporting

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   CODE REPOSITORIES                          │
│  (ASEAGI, other projects, GitHub repos, local code)          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              REPOSITORY SCANNER                              │
│  Python script that analyzes repos and extracts metadata    │
│  • Counts files and lines                                   │
│  • Detects languages and frameworks                         │
│  • Scans dependencies (requirements.txt, package.json)      │
│  • Checks for README, tests, CI/CD, docs                    │
│  • Calculates quality score                                 │
│  • Extracts git information                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  SUPABASE DATABASE                           │
│  PostgreSQL with comprehensive schema                        │
│  • repositories table                                        │
│  • repository_files table                                   │
│  • repository_scan_history table                            │
│  • repository_dependencies table                            │
│  • repository_tags table                                    │
│  • code_analysis_metrics table                              │
│  • Views for health, stats, etc.                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    QUERY INTERFACES                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📱 STREAMLIT DASHBOARD (Port 8506)                          │
│     • Visual overview                                        │
│     • Charts and graphs                                      │
│     • Search and filter                                      │
│     • Scan new repositories                                 │
│                                                              │
│  🤖 MCP SERVER (Claude Desktop)                              │
│     • list_repositories                                      │
│     • get_repository_details                                │
│     • search_repositories                                   │
│     • compare_repositories                                  │
│     • get_repository_stats                                  │
│     • find_dependencies                                     │
│     • get_repository_health                                 │
│                                                              │
│  🔄 AUTOMATION (n8n / cron)                                  │
│     • Daily automated scans                                 │
│     • Telegram notifications                                │
│     • Health reports                                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Components

### 1. Database Schema

**Location:** `/home/user/ASEAGI/database/migrations/005_code_repository_sentinel_schema.sql`

**Tables:**
- `repositories` - Main repository metadata
- `repository_files` - File-level information
- `repository_scan_history` - Audit log of scans
- `repository_dependencies` - Dependency tracking
- `repository_tags` - Flexible tagging system
- `code_analysis_metrics` - Code quality metrics

**Views:**
- `v_active_repositories` - Active repos only
- `v_repository_health` - Health assessment
- `v_dependency_usage` - Dependencies across repos
- `v_recent_activity` - Recent changes

### 2. Repository Scanner

**Location:** `/home/user/ASEAGI/scanners/repository_scanner.py`

**Capabilities:**
- Analyzes local and git repositories
- Detects languages and frameworks
- Scans dependencies (Python, Node.js, Go, Rust)
- Checks for README, tests, CI/CD, docs
- Calculates code quality score (0-100)
- Extracts git metadata (commits, branches, etc.)
- Stores results in Supabase

**Usage:**
```bash
# Scan single repository
python3 scanners/repository_scanner.py /path/to/repo

# Scan ASEAGI project
python3 scanners/repository_scanner.py /home/user/ASEAGI

# Dry run (don't save to database)
python3 scanners/repository_scanner.py /path/to/repo --dry-run

# Quick scan (faster, less detailed)
python3 scanners/repository_scanner.py /path/to/repo --scan-type quick
```

### 3. MCP Server

**Location:** `/home/user/ASEAGI/mcp-servers/repository-sentinel-server/`

**Tools Available:**
1. `list_repositories` - List all repos with filters
2. `get_repository_details` - Detailed repo info
3. `search_repositories` - Search by keywords
4. `compare_repositories` - Compare multiple repos
5. `get_repository_stats` - Aggregate statistics
6. `find_dependencies` - Find repos using a dependency
7. `get_repository_health` - Health assessment

**Setup:**
```bash
# Install dependencies
cd mcp-servers/repository-sentinel-server
pip install -r requirements.txt

# Add to Claude Desktop config
# See README.md in that directory
```

### 4. Streamlit Dashboard

**Location:** `/home/user/ASEAGI/dashboards/repository_sentinel_dashboard.py`

**Features:**
- Overview statistics
- Language and framework breakdown
- Quality score distribution
- Repository health assessment
- Search and filter
- Scan new repositories
- Detailed repository cards

**Usage:**
```bash
# Start dashboard
streamlit run dashboards/repository_sentinel_dashboard.py --server.port 8506

# Access at: http://localhost:8506
```

### 5. Automation

#### Option A: n8n Workflow

**Location:** `/home/user/ASEAGI/n8n-workflows/04-repository-sentinel-scanner.json`

**Schedule:** Daily at 2:00 AM
**Actions:**
- Scans ASEAGI repository
- Updates database
- Sends Telegram notification with stats

**Setup:**
1. Import workflow into n8n
2. Configure Telegram credentials
3. Update repository paths
4. Activate workflow

#### Option B: Cron Script

**Location:** `/home/user/ASEAGI/scripts/auto_scan_repositories.sh`

**Setup:**
```bash
# Make executable
chmod +x scripts/auto_scan_repositories.sh

# Test manually
./scripts/auto_scan_repositories.sh

# Add to crontab
crontab -e

# Add this line (runs daily at 2:00 AM):
0 2 * * * /home/user/ASEAGI/scripts/auto_scan_repositories.sh

# Check logs
tail -f ~/ASEAGI/logs/repository_scanner.log
```

---

## 🚀 Installation

### Step 1: Apply Database Schema

```bash
# Navigate to ASEAGI directory
cd /home/user/ASEAGI

# Apply schema to Supabase
# Option 1: Via Supabase dashboard
# - Go to https://app.supabase.com
# - Open SQL Editor
# - Paste contents of database/migrations/005_code_repository_sentinel_schema.sql
# - Run

# Option 2: Via psql (if you have direct access)
psql -h your-host -U postgres -d postgres -f database/migrations/005_code_repository_sentinel_schema.sql
```

### Step 2: Scan Your First Repository

```bash
# Scan ASEAGI itself
python3 scanners/repository_scanner.py /home/user/ASEAGI

# Should output:
# 🔍 Scanning repository: /home/user/ASEAGI
# 📊 Scan type: full
# ⏰ Started at: 2025-11-18...
# 📦 Extracting git information...
# 📂 Scanning files...
# ✅ Scan completed in X seconds
# 💾 Saving to database...
# ✅ Saved to database: github-dondada876-ASEAGI
```

### Step 3: Launch Dashboard

```bash
# Start Streamlit dashboard
streamlit run dashboards/repository_sentinel_dashboard.py --server.port 8506

# Access at: http://localhost:8506
```

### Step 4: Configure MCP (Optional)

```bash
# Install MCP dependencies
cd mcp-servers/repository-sentinel-server
pip install -r requirements.txt

# Add to Claude Desktop config
# See mcp-servers/repository-sentinel-server/README.md
```

### Step 5: Set Up Automation (Optional)

Choose one:

**Option A: n8n**
- Import `/n8n-workflows/04-repository-sentinel-scanner.json`
- Configure credentials
- Activate workflow

**Option B: Cron**
```bash
chmod +x scripts/auto_scan_repositories.sh
crontab -e
# Add: 0 2 * * * /home/user/ASEAGI/scripts/auto_scan_repositories.sh
```

---

## 📖 Usage

### Scan a Repository

```bash
# Full scan
python3 scanners/repository_scanner.py /path/to/repo

# Quick scan (faster)
python3 scanners/repository_scanner.py /path/to/repo --scan-type quick

# Incremental scan (only changed files)
python3 scanners/repository_scanner.py /path/to/repo --scan-type incremental
```

### View Dashboard

```bash
streamlit run dashboards/repository_sentinel_dashboard.py --server.port 8506
```

Navigate to http://localhost:8506

**Dashboard Features:**
- 📊 Overview metrics
- 📈 Language/framework charts
- 🏥 Health assessment
- 🔍 Search and filter
- ➕ Scan new repositories

### Query via Claude Desktop

**Examples:**

```
You: "Claude, list all my Python repositories"
Claude: *calls list_repositories with language=Python*

You: "Claude, which repos use Streamlit?"
Claude: *calls find_dependencies with dependency_name=streamlit*

You: "Claude, show me repositories that need tests"
Claude: *calls get_repository_health, filters by missing tests*

You: "Claude, compare ASEAGI with my other dashboards"
Claude: *calls search_repositories, then compare_repositories*

You: "Claude, what's my total lines of code across all projects?"
Claude: *calls get_repository_stats*
```

---

## 🔄 Automation

### Daily Scanning

**Purpose:** Keep repository inventory up-to-date automatically

**Methods:**

#### 1. n8n Workflow (Recommended)

Advantages:
- ✅ Visual workflow editor
- ✅ Easy to modify
- ✅ Telegram notifications built-in
- ✅ Cloud-hosted (always running)

Setup:
1. Import `n8n-workflows/04-repository-sentinel-scanner.json`
2. Update `YOUR_TELEGRAM_CHAT_ID`
3. Activate workflow

#### 2. Cron Script (Alternative)

Advantages:
- ✅ No external dependencies
- ✅ Runs locally
- ✅ Simple and reliable

Setup:
```bash
# Edit script to add more repos
nano scripts/auto_scan_repositories.sh

# Add to crontab
crontab -e
0 2 * * * /home/user/ASEAGI/scripts/auto_scan_repositories.sh
```

### Custom Schedule

Change cron expression:

```
# Every 6 hours
0 */6 * * * /path/to/script.sh

# Every Monday at 9 AM
0 9 * * 1 /path/to/script.sh

# Twice daily (6 AM and 6 PM)
0 6,18 * * * /path/to/script.sh
```

Use https://crontab.guru/ to create custom schedules.

---

## 🤖 MCP Integration

### Claude Desktop Queries

Once configured, you can ask Claude:

**Inventory Questions:**
- "How many repositories do I have?"
- "What languages do I use most?"
- "Show me all my Python projects"
- "Which repos use React?"

**Health & Quality:**
- "Which repositories need tests?"
- "What's my average code quality score?"
- "Show me repos with poor health"
- "Which projects lack documentation?"

**Comparisons:**
- "Compare ASEAGI with my other Streamlit apps"
- "How does this repo compare to industry standards?"
- "Which of my projects is the largest?"

**Dependencies:**
- "Which repos use Streamlit 1.31?"
- "Find all projects using FastAPI"
- "What dependencies does ASEAGI have?"

**Statistics:**
- "What's my total lines of code?"
- "How many repositories are production-ready?"
- "Show me language breakdown across all repos"

---

## 🛠️ Troubleshooting

### Scanner Issues

**Problem:** Scanner fails with "Module not found"

**Solution:**
```bash
pip install supabase python-dotenv
```

---

**Problem:** Scanner can't access git info

**Solution:** Make sure you're scanning a git repository, or scan non-git repos (they'll still work, just without git metadata)

---

**Problem:** Permission denied

**Solution:**
```bash
chmod +x scanners/repository_scanner.py
```

---

### Dashboard Issues

**Problem:** Dashboard shows "No repositories"

**Solution:** Run scanner at least once:
```bash
python3 scanners/repository_scanner.py /home/user/ASEAGI
```

---

**Problem:** Dashboard can't connect to Supabase

**Solution:** Check environment variables:
```bash
echo $SUPABASE_URL
echo $SUPABASE_KEY
```

If empty, add to `.env` file or export:
```bash
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-key'
```

---

### MCP Server Issues

**Problem:** Claude Desktop can't connect

**Solution:**
1. Check `claude_desktop_config.json` syntax
2. Verify file paths are absolute
3. Restart Claude Desktop completely
4. Check Claude Desktop logs

---

**Problem:** MCP tools return no data

**Solution:** Scan repositories first:
```bash
python3 scanners/repository_scanner.py /home/user/ASEAGI
```

---

### Automation Issues

**Problem:** Cron job doesn't run

**Solution:**
1. Check crontab syntax: `crontab -l`
2. Make script executable: `chmod +x scripts/auto_scan_repositories.sh`
3. Check logs: `tail -f ~/ASEAGI/logs/repository_scanner.log`
4. Test manually first: `./scripts/auto_scan_repositories.sh`

---

**Problem:** n8n workflow fails

**Solution:**
1. Check Supabase credentials in n8n
2. Verify repository paths exist
3. Test execution manually in n8n
4. Check n8n execution logs

---

## 📊 Database Queries

### Useful SQL Queries

**List all repositories:**
```sql
SELECT repository_name, primary_language, total_lines_of_code, code_quality_score
FROM repositories
ORDER BY last_scanned_at DESC;
```

**Find repositories needing attention:**
```sql
SELECT repository_name, health_status
FROM v_repository_health
WHERE health_status IN ('fair', 'poor');
```

**Dependencies across repos:**
```sql
SELECT dependency_name, COUNT(*) as repo_count
FROM repository_dependencies
GROUP BY dependency_name
ORDER BY repo_count DESC;
```

**Recent activity:**
```sql
SELECT * FROM v_recent_activity
WHERE days_since_last_commit < 30;
```

---

## 🎯 Best Practices

### 1. Regular Scanning

**Recommended:** Scan repositories at least daily

```bash
# Add to crontab
0 2 * * * /home/user/ASEAGI/scripts/auto_scan_repositories.sh
```

### 2. Quality Monitoring

**Track:**
- Code quality scores
- Test coverage
- Documentation completeness
- Dependency vulnerabilities

### 3. Multi-Repository Management

**Organize:**
```bash
# Edit auto_scan_repositories.sh
REPOS=(
    "/home/user/ASEAGI"
    "/home/user/other-project"
    "/home/user/another-repo"
)
```

### 4. Health Alerts

**Set up notifications** for:
- Repos with quality score < 50
- Missing tests or docs
- Stale repositories (no commits in 90 days)
- Dependency vulnerabilities

---

## 🔮 Future Enhancements

Planned features:

- [ ] PDF/Word report generation
- [ ] GitHub Actions integration
- [ ] Dependency vulnerability scanning
- [ ] Code complexity analysis
- [ ] Test coverage integration
- [ ] Multi-team support
- [ ] Repository templates
- [ ] Automated code reviews
- [ ] Trend analysis over time
- [ ] Cost estimation (cloud hosting, etc.)

---

## 📚 Related Documentation

- [Database Schema](/database/migrations/005_code_repository_sentinel_schema.sql)
- [Scanner README](/scanners/repository_scanner.py)
- [MCP Server README](/mcp-servers/repository-sentinel-server/README.md)
- [Dashboard Source](/dashboards/repository_sentinel_dashboard.py)
- [n8n Workflow](/n8n-workflows/04-repository-sentinel-scanner.json)
- [Auto-Scan Script](/scripts/auto_scan_repositories.sh)

---

## 🙏 Support

For issues or questions:
1. Check this guide
2. Review component README files
3. Check logs: `~/ASEAGI/logs/repository_scanner.log`
4. Review Supabase data in dashboard

---

**For Ashe. For Justice. For All Children.** 🛡️

---

**Version:** 1.0.0
**Date:** 2025-11-18
**System:** ASEAGI Code Repository Sentinel
