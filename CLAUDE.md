# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Last Updated:** November 19, 2025
**Project:** PROJ344 - Legal Case Intelligence Dashboards
**Codebase Size:** ~10,034 LOC (35 Python files, 37 Markdown docs)
**Repository:** https://github.com/dondada876/ASEAGI

---

## Project Overview

**ASEAGI** (Ashe Security Analysis and Evidence Gathering Initiative) is an AI-powered legal document intelligence system designed for child protection cases, specifically custody litigation and dependency proceedings.

**Core Mission:** Assist protective parents and legal teams in analyzing legal documents with AI-powered scoring to identify smoking gun evidence, detect perjury, and track constitutional violations.

**Case Context:** In re Ashe Bucknor (J24-00478) - A custody/child protection case

---

## Key Statistics

- **35 Python files** across 8 main components
- **7 Streamlit dashboards** running on ports 8501-8506
- **~10,034 total lines of Python code**
- **601 legal documents** in Supabase database (as of Nov 6)
- **Comprehensive CI/CD** with pre-commit hooks and GitHub Actions
- **Production-ready infrastructure** (Docker, testing, security scanning)

---

## Architecture Overview

```
ASEAGI/
├── dashboards/              # Streamlit web applications (7 dashboards, ~3,808 LOC)
│   ├── proj344_master_dashboard.py (441 LOC)         # Main case intelligence
│   ├── legal_intelligence_dashboard.py (675 LOC)    # Document-by-document analysis
│   ├── enhanced_scanning_monitor.py (714 LOC)       # Real-time scanning monitor
│   ├── master_5wh_dashboard.py (651 LOC)            # 5W+H analysis framework (NEW)
│   ├── scanning_monitor_dashboard.py (526 LOC)      # Detailed scan progress
│   ├── timeline_violations_dashboard.py (417 LOC)   # Constitutional violations tracker
│   └── ceo_dashboard.py (384 LOC)                   # File organization & system health
│
├── scanners/                # Document processing (9 files, ~2,290 LOC)
│   ├── batch_scan_documents.py (384 LOC)            # Main document scanner with PROJ344 scoring
│   ├── 2025-11-05-CH16-batch-scan-all-documents.py  # Variant for batch processing
│   └── query_legal_documents.py (247 LOC)           # Database query utility
│
├── core/                    # Error handling & tracking (4 files, ~900 LOC)
│   ├── __init__.py                                   # Package exports
│   ├── bug_tracker.py (455 LOC)                     # Automatic error detection
│   ├── bug_exports.py (402 LOC)                     # Bug export utilities
│   └── workspace_config.py (31 LOC)                 # Workspace configuration
│
├── scripts/                 # Utility scripts (4 files)
│   ├── launch-all-dashboards.sh                     # Bash script to start all 5 dashboards
│   ├── track_api_usage.py                           # Anthropic API cost tracking
│   ├── promo_credit_tracker.py                      # $1K promotional credit tracking
│   └── usage_dashboard.py                           # API usage visualization
│
├── n8n-workflows/           # Automation workflows (4 files)
│   ├── 01-daily-report.json                         # Daily case summary (8 AM)
│   ├── 02-high-priority-alerts.json                 # Hourly smoking gun alerts
│   ├── 03-weekly-statistics.json                    # Weekly case analysis
│   └── README.md                                     # n8n setup instructions
│
├── docs/                    # Documentation (5 files)
│   ├── DEPLOYMENT.md                                # Deployment guides
│   ├── GITHUB-SETUP.md                              # GitHub configuration
│   ├── PROMO_CREDIT_TRACKING.md                     # Credit tracking guide
│   ├── USAGE_TRACKING.md                            # API usage tracking
│   └── TROUBLESHOOTING_ERRORS.md                    # Error troubleshooting
│
├── requirements.txt         # Python dependencies (8 packages)
├── .env.example             # Environment variable template
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Multi-container setup
├── Procfile                 # Heroku deployment config
├── .gitignore               # Git ignore rules
├── README.md                # Main documentation
└── [Deployment guides]      # Multiple .md files for deployment
```

---

## Core Technologies

### Frontend & Visualization
- **Streamlit 1.31.0** - Dashboard framework (7 apps)
- **Plotly 5.18.0** - Interactive visualizations
- **Pandas 2.1.4** - Data manipulation

### Backend & Data
- **Supabase 2.3.4** - PostgreSQL database (601 documents)
- **PostgREST 0.13.2** - REST API client
- **Python-dotenv 1.0.0** - Environment management

### AI & Document Processing
- **Anthropic Claude API** - PROJ344 scoring algorithm
- **Pillow 10.2.0** - Image processing (JPG, PNG, HEIC)

### Infrastructure
- **Docker** - Containerization
- **n8n Cloud** - Workflow automation (Telegram alerts, scheduling)

### Python Version
- **Python 3.9+** (Dockerfile uses 3.11-slim)

---

## Dependencies

**File:** `/home/user/ASEAGI/requirements.txt`

```
streamlit==1.31.0        # Dashboard framework
pandas==2.1.4            # Data handling
plotly==5.18.0           # Interactive charts
supabase==2.3.4          # Database client
postgrest==0.13.2        # REST API
Pillow==10.2.0           # Image processing
python-dotenv==1.0.0     # Environment variables
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

## Environment Configuration

### Required Variables

**File:** `.env` (copy from `.env.example`)

```env
# Supabase (PostgreSQL database)
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Anthropic (Document scanning with Claude)
ANTHROPIC_API_KEY=sk-ant-v0-...

# Optional: Airtable integration
AIRTABLE_TOKEN=pat...
AIRTABLE_BASE_ID=appXXXXXX...

# Case Information
CASE_ID=ashe-bucknor-j24-00478
CASE_NUMBER=J24-00478
```

### Critical Security Notes
- **NEVER commit .env files** - Already in .gitignore
- Store API keys in:
  - Local `.env` for development
  - Streamlit Cloud UI secrets for deployment
  - Heroku config vars for Heroku
  - Docker environment variables for containers

---

## Project Structure Details

### 1. Dashboards (`/dashboards/`)

#### A. PROJ344 Master Dashboard (Port 8501)
- **File:** `proj344_master_dashboard.py` (441 LOC)
- **Purpose:** Main case intelligence and evidence review
- **Key Features:**
  - System overview with key metrics (total docs, smoking guns, perjury count)
  - Smoking gun filter (relevancy ≥ 900)
  - Document search with filters
  - Score distribution visualizations
  - Interactive document cards with details
  - Perjury indicator tracking
  
**Key Functions:**
- `init_supabase()` - Caches Supabase connection
- `get_all_documents()` - Fetches and caches documents
- `get_stats()` - Calculates dashboard statistics
- `render_score_gauge()` - Creates gauge charts for PROJ344 scores

#### B. Legal Intelligence Dashboard (Port 8502)
- **File:** `legal_intelligence_dashboard.py` (675 LOC)
- **Purpose:** Detailed document-by-document analysis
- **Key Features:**
  - Document breakdown by score ranges
  - Key quotes extraction
  - Fraud/perjury indicators
  - Document type classification
  - Cross-reference capabilities

#### C. Enhanced Scanning Monitor (Port 8504)
- **File:** `enhanced_scanning_monitor.py` (714 LOC)
- **Purpose:** Real-time document scanning progress tracking
- **Key Features:**
  - Queue metrics (remaining, ETA, throughput)
  - Conversion tracking with charts
  - Cost monitoring ($$ per document)
  - Recent documents feed
  - 5-second auto-refresh
  - Live log tailing

#### D. Master 5W+H Dashboard (Port 8506) **NEW**
- **File:** `master_5wh_dashboard.py` (651 LOC)
- **Purpose:** Comprehensive legal intelligence with 5W+H framework analysis
- **Key Features:**
  - Independent querying by: Who, What, When, Where, Why, How
  - Deep visual analytics with custom CSS
  - Gradient metric cards for key statistics
  - Advanced Plotly visualizations
  - Smoking gun evidence highlighting

#### E. CEO Dashboard (Port 8503)
- **File:** `ceo_dashboard.py` (384 LOC)
- **Purpose:** System administration and file organization
- **Features:**
  - PARA structure overview (Projects, Areas, Resources, Archives)
  - File organization health checks
  - Naming compliance tracking
  - Duplicate file detection
  - System statistics

#### F. Timeline & Violations Dashboard (Port 8505)
- **File:** `timeline_violations_dashboard.py` (417 LOC)
- **Purpose:** Constitutional violations tracking
- **Features:**
  - Court events timeline
  - Due process violations
  - Multi-jurisdiction tracking
  - Event frequency analysis

#### G. Scanning Monitor Dashboard
- **File:** `scanning_monitor_dashboard.py` (526 LOC)
- **Purpose:** Alternative scanning monitor with different visualizations
- **Note:** Similar to Enhanced Scanning Monitor (Port 8504)

### 2. Scanners (`/scanners/`)

#### Main Scanner: `batch_scan_documents.py` (384 LOC)

**Purpose:** Process documents with PROJ344 AI scoring

**Key Classes:**
- `BatchDocumentScanner` - Main scanning engine

**Key Methods:**
- `__init__()` - Initialize with API credentials
- `calculate_file_hash()` - MD5 hash for duplicate detection
- `check_already_processed()` - Skip duplicates in database
- `extract_text_from_image()` - Convert images to base64 for Claude
- `analyze_document()` - Send to Claude API with PROJ344 prompt
- `upload_to_supabase()` - Store results

**PROJ344 Scoring Methodology:**
- **Relevancy (0-999):** Overall case importance
  - 900-999: Smoking gun evidence
  - 800-899: Critical evidence
  - 700-799: Important evidence
  - 600-699: Useful background
  - 0-599: Reference material

- **Micro Scoring:** Detail-level importance
- **Macro Scoring:** Case-wide significance
- **Legal Scoring:** Legal weight & admissibility

**File Support:**
- ✅ `.jpg`, `.jpeg`, `.png`, `.heic` (images)
- ✅ `.txt`, `.rtf` (text files)
- ⏳ `.pdf` (coming soon)

**Cost Tracking:**
- Tracks per-document API cost
- Calculates total project cost
- Used for budget monitoring

**Usage:**
```bash
python3 scanners/batch_scan_documents.py /path/to/documents
python3 scanners/batch_scan_documents.py /path/to/documents --dry-run
python3 scanners/batch_scan_documents.py /path/to/documents --extensions .pdf,.jpg
```

#### Query Tool: `query_legal_documents.py` (247 LOC)
- Utility for querying Supabase legal_documents table
- Filters by score ranges, document types, dates
- Exports results to CSV

### 3. Core Module (`/core/`)

#### Error Tracking: `bug_tracker.py` (455 LOC)

**Purpose:** Automatic error detection and bug management

**Key Classes:**
- `BugTracker` - Automated error detection system
- `track_errors` - Decorator for error tracking

**Features:**
- Captures stack traces automatically
- Tracks error frequency and patterns
- Can save to Supabase or local files
- Provides error summaries and reports

**Configuration:**
- Workspace ID: "legal"
- Default component: "legal_document_scanner"
- Default environment: "production"

#### Export Tool: `bug_exports.py` (402 LOC)
- Export bugs/errors to various formats
- Generate reports
- CSV, JSON export support

#### Workspace Config: `workspace_config.py` (31 LOC)
```python
WORKSPACE_ID = 'legal'
WORKSPACE_NAME = 'Legal Intelligence (PROJ344)'
REPOSITORY_NAME = 'ASEAGI'
REPOSITORY_URL = 'https://github.com/dondada876/ASEAGI'
CASE_ID = 'ashe-bucknor-j24-00478'
```

### 4. Scripts (`/scripts/`)

#### Launch Script: `launch-all-dashboards.sh`
Starts all 5 dashboards with proper error checking and cleanup

**What it does:**
1. Checks if Streamlit is installed
2. Checks environment variables
3. Launches 5 dashboards on ports 8501-8505
4. Provides URLs and cleanup on Ctrl+C

**Usage:**
```bash
./scripts/launch-all-dashboards.sh
```

#### API Usage Tracking: `track_api_usage.py`
Monitors Anthropic API usage for cost analysis

#### Promo Credit Tracking: `promo_credit_tracker.py`
Tracks the $1,000 promotional credit for Claude

#### Usage Dashboard: `usage_dashboard.py`
Visualizes API usage trends

---

## Database Schema (Supabase)

### Table: `legal_documents`

**Key Columns:**
```sql
id                    UUID PRIMARY KEY
docket_number         TEXT (J24-00478)
file_name             TEXT
renamed_filename      TEXT (with conversions)
document_type         TEXT (Court Filing, Motion, Declaration, etc.)
category              TEXT (Critical, Important, Useful, Reference)
purpose               TEXT

-- PROJ344 Scoring (0-999 scale)
micro_number          INTEGER (detail-level)
macro_number          INTEGER (case-wide)
legal_number          INTEGER (legal weight)
relevancy_number      INTEGER (composite score)

-- Key Data
summary               TEXT (AI-generated summary)
key_quotes            TEXT[] (Important quotes)

-- Risk Indicators
contains_false_statements  BOOLEAN
fraud_indicators      TEXT[]
perjury_indicators    TEXT[]

-- System Fields
content_hash          TEXT (MD5 for dedup)
api_cost_usd          FLOAT
processed_at          TIMESTAMP
case_id               TEXT
```

**Connection:**
- URL: https://jvjlhxodmbkodzmggwpu.supabase.co
- Database: PostgreSQL
- API: PostgREST with JWT auth

---

## Key Workflows & Operations

### 1. Document Scanning Pipeline

```
Documents on Disk
    ↓
Batch Scanner (batch_scan_documents.py)
    ├─ Calculate MD5 hash
    ├─ Check for duplicates
    ├─ Extract text/convert image
    ├─ Send to Claude API
    ├─ Generate PROJ344 scores
    └─ Upload to Supabase
    ↓
Legal Intelligence System
    ├─ Master Dashboard displays results
    ├─ Smoking guns (900+) highlighted
    ├─ Perjury indicators flagged
    └─ Cost tracking enabled
```

### 2. Real-Time Monitoring

```
Enhanced Scanning Monitor (Port 8504)
    ├─ Queries queue metrics
    ├─ Tracks conversion rate
    ├─ Calculates ETA
    ├─ Monitors costs
    └─ Auto-refresh every 5s
```

### 3. Automation (n8n Workflows)

**Workflow 1: Daily Report (8 AM)**
- Queries Supabase
- Counts documents by category
- Sends Telegram message

**Workflow 2: Hourly Alerts (Every hour)**
- Checks for new smoking guns (≥950)
- Immediate Telegram notification
- Includes fraud/perjury indicators

**Workflow 3: Weekly Statistics (Sunday 6 PM)**
- Comprehensive case analysis
- Document breakdown by type
- Violation summary

---

## Scoring System (PROJ344)

### Four Dimensions (0-999)

| Dimension | What It Measures | Use Case |
|-----------|-----------------|----------|
| **Micro** | Detail-level importance | Specific phrase impact |
| **Macro** | Case-wide significance | Overall case importance |
| **Legal** | Legal weight & admissibility | Court admissibility |
| **Relevancy** | Composite weighted score | Primary ranking metric |

### Relevancy Score Ranges

| Range | Badge | Category | Example Use |
|-------|-------|----------|------------|
| 900-999 | 🔥 | Smoking Gun | Critical evidence, impeachment |
| 800-899 | ⚠️ | Critical | High-value evidence |
| 700-799 | 📌 | Important | Supporting documents |
| 600-699 | 📋 | Useful | Background/context |
| 0-599 | 📄 | Reference | Archive |

---

## Deployment Options

### Option 1: Local Development (Recommended for Testing)

```bash
# 1. Set environment variables
export SUPABASE_URL=https://...
export SUPABASE_KEY=...
export ANTHROPIC_API_KEY=...

# 2. Launch all dashboards
./scripts/launch-all-dashboards.sh

# Access at:
# - Master: http://localhost:8501
# - Legal Intelligence: http://localhost:8502
# - CEO: http://localhost:8503
# - Scanning Monitor: http://localhost:8504
# - Timeline: http://localhost:8505
```

### Option 2: Docker (Containerized)

```bash
# Build image
docker build -t aseagi .

# Run with compose (all 3 dashboards)
docker-compose up

# Or single dashboard
docker run -p 8501:8501 \
  -e SUPABASE_URL=... \
  -e SUPABASE_KEY=... \
  -e ANTHROPIC_API_KEY=... \
  aseagi
```

**Dockerfile Details:**
- Base: `python:3.11-slim`
- Ports: 8501, 8502, 8503 exposed
- Entrypoint: Master dashboard
- Health check: Curl to Streamlit health endpoint

### Option 3: Streamlit Cloud (Free Hosting)

1. Push to GitHub: `https://github.com/dondada876/ASEAGI`
2. Go to `share.streamlit.io`
3. Deploy each dashboard separately
4. Add secrets in Streamlit Cloud UI
5. URLs auto-generated

See `/home/user/ASEAGI/DEPLOY_TO_STREAMLIT.md` for detailed steps

### Option 4: Heroku (Alternate Cloud)

Uses Procfile for deployment configuration

### Option 5: Digital Ocean (Production)

See `DEPLOY_TO_DIGITAL_OCEAN.md` for full setup

---

## Development Workflow

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI

# 2. Create Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env with your actual credentials

# 5. Launch dashboards
./scripts/launch-all-dashboards.sh
```

### Scanning Documents

```bash
# Single directory scan
python3 scanners/batch_scan_documents.py ~/Documents/LegalDocs

# With specific extensions
python3 scanners/batch_scan_documents.py ~/Documents/LegalDocs --extensions .jpg,.png

# Dry run (no database upload)
python3 scanners/batch_scan_documents.py ~/Documents/LegalDocs --dry-run
```

### Error Tracking

Errors are automatically tracked via `core/bug_tracker.py`. They're saved locally in:
```
~/ASEAGI/data/bugs/legal/
~/ASEAGI/data/logs/legal/
```

### Testing Changes

1. Modify dashboard code
2. Streamlit auto-reloads on file changes
3. Refresh browser to see updates
4. Check console for error messages

---

## Common Commands

### Start Services

```bash
# All dashboards
./scripts/launch-all-dashboards.sh

# Individual dashboard
streamlit run dashboards/proj344_master_dashboard.py --server.port 8501

# With environment variables
export SUPABASE_URL=... && streamlit run dashboards/proj344_master_dashboard.py
```

### Docker Commands

```bash
# Build
docker build -t aseagi .

# Compose up (all services)
docker-compose up

# View logs
docker logs proj344-master-dashboard

# Stop services
docker-compose down
```

### Database Queries

```bash
# Query documents via Python
python3 scanners/query_legal_documents.py --filter smoking_guns

# Direct Supabase access
# Use Supabase dashboard: https://app.supabase.com/
```

---

## Important Files & Their Roles

| File | Purpose | Key Content |
|------|---------|------------|
| `README.md` | Main documentation | Project overview, features, quick start |
| `requirements.txt` | Python dependencies | 8 packages (streamlit, supabase, etc.) |
| `.env.example` | Template for secrets | Copy to .env for local development |
| `Dockerfile` | Container definition | Python 3.11, port 8501-8503 |
| `docker-compose.yml` | Multi-container setup | 3 services (master, legal, ceo) |
| `Procfile` | Heroku configuration | Entry point for Heroku deployment |
| `.gitignore` | Git ignore rules | Protects .env, *.pdf, documents/ |
| `DEPLOY_TO_STREAMLIT.md` | Streamlit Cloud guide | Step-by-step deployment |
| `DEPLOY_TO_DIGITAL_OCEAN.md` | DO deployment guide | Production deployment |
| `GLOBAL_ASSESSMENT_2025-11-06.md` | System status report | Metrics, progress, achievements |

---

## Git Workflow

**Current Branch:** `claude/api-vs-web-clarification-011CUuqk9SwXoeKNSzwfQq68`

**Recent Commits:**
```
e0f1396 Clarify API vs Web credit confusion in documentation
cd1f123 Add promotional credit tracking for $1,000 Claude Code credit
02c20b6 Add Claude API usage tracking and cost monitoring tools
16ee8b9 Add Vtiger API Manual notes
```

**Standard Workflow:**
1. Create feature branch
2. Make changes
3. Test locally
4. Commit with clear messages
5. Push to GitHub
6. Create PR

**Protected:** `.env` files and case documents (in .gitignore)

---

## Troubleshooting

### Dashboard Won't Start
- Check Python version (3.9+)
- Verify Streamlit installed: `pip list | grep streamlit`
- Check port availability (8501-8505)
- Ensure SUPABASE_URL and KEY are set

### Supabase Connection Failed
- Verify credentials in .env
- Check Supabase status: https://status.supabase.com/
- Test with `curl https://your-project.supabase.co/rest/v1/` (should return 404)

### Document Scanner Error
- Check ANTHROPIC_API_KEY is valid
- Verify image file formats (JPG, PNG, HEIC)
- Check file isn't already in database (hash check)
- See `/home/user/ASEAGI/docs/TROUBLESHOOTING_ERRORS.md`

### Docker Issues
- Clear dangling containers: `docker system prune`
- Rebuild image: `docker build --no-cache -t aseagi .`
- Check logs: `docker-compose logs -f`

---

## Performance Notes

### Caching Strategy
- Streamlit caches:
  - Supabase connection (`@st.cache_resource`)
  - Document queries (30-second TTL)
  - Statistics calculations (30-second TTL)
- Reduces database hits during dashboard navigation

### Scanning Performance
- Average processing time: 2-3 hours for 600 documents
- Cost: ~$0.0133 per document
- Bottleneck: Claude API response time, not file I/O

### Database Performance
- 601 documents processed
- Query response: <100ms typical
- Indexes recommended on: `relevancy_number`, `case_id`, `document_type`

---

## Security Considerations

### Secrets Management
- ✅ Use environment variables (never hardcode)
- ✅ .env files gitignored
- ✅ Supabase JWT auth for database
- ✅ API keys in separate variables

### Data Privacy
- All documents stored in private Supabase instance
- Dashboards run on localhost only
- No external data transmission
- HTTPS for all API calls

### Case Information Protection
- Case documents excluded from git
- Supabase row-level security recommended
- Backup strategy recommended for Supabase

---

## Future Development

### Planned Features
- PDF document support (currently skipped)
- Advanced search with full-text indexing
- Export reports to Word/PDF
- Integration with case management software
- Multi-case support

### Known Limitations
- PDF processing not implemented
- Single case per instance
- No user authentication in dashboards
- Streamlit Cloud rate limits on free tier

---

## Useful Links

- **Streamlit Docs:** https://docs.streamlit.io/
- **Supabase Docs:** https://supabase.com/docs/
- **Anthropic API:** https://docs.anthropic.com/
- **Plotly Documentation:** https://plotly.com/python/
- **n8n Workflows:** https://docs.n8n.io/
- **Docker Docs:** https://docs.docker.com/

---

## Key Contacts & Resources

- **GitHub Repository:** https://github.com/dondada876/ASEAGI
- **Supabase Project:** https://app.supabase.com/
- **n8n Instance:** https://yourname.app.n8n.cloud/
- **Case Number:** J24-00478
- **Docket:** In re Ashe Bucknor

---

## Quick Reference: Port Assignments

| Port | Dashboard | File | Purpose |
|------|-----------|------|---------|
| 8501 | Master | `proj344_master_dashboard.py` | Main case intelligence |
| 8502 | Legal Intelligence | `legal_intelligence_dashboard.py` | Document analysis |
| 8503 | CEO | `ceo_dashboard.py` | File organization |
| 8504 | Enhanced Monitor | `enhanced_scanning_monitor.py` | Real-time scanning |
| 8505 | Timeline & Violations | `timeline_violations_dashboard.py` | Constitutional violations |
| 8506 | Master 5W+H | `master_5wh_dashboard.py` | 5W+H analysis framework |

---

## Notes for Future Claude Instances

1. **This is an active case system** - All data relates to real litigation (J24-00478)
2. **Data sensitivity** - Documents contain privileged/confidential case information
3. **Production system** - Dashboards may be deployed and in active use
4. **Cost tracking** - Every document scanned costs ~$0.013 (Anthropic API)
5. **Deadlines matter** - Legal filings have court deadlines
6. **Error handling is critical** - System has automatic bug tracking
7. **This is specialized domain** - Requires understanding of legal document analysis

---

**Last Updated:** November 8, 2025  
**For:** Ashe Bucknor - Child Protection Case (J24-00478)  
**Mission:** Ensure children's voices are heard and perjury is documented.

---

*"No child's voice should be silenced by litigation. No protective parent should be punished for protecting."*
