# ⚖️ ASEAGI - Legal Case Intelligence System

**AI-powered legal document intelligence with dual-system architecture for child protection cases**

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

---

## 📊 System Overview

ASEAGI consists of two complementary systems that work together:

### 1. PROJ344 - Document Intelligence Dashboards
**7 Streamlit Dashboards** for legal document analysis and case intelligence
- **Ports:** 8501-8506
- **Status:** ✅ Production-ready
- **Purpose:** Interactive document analysis and visualization

### 2. AGI Protocol - Multi-Agent Legal System
**FastAPI Backend + Telegram Bot** for automated legal research and case management
- **Ports:** 8000 (API), 8443 (Telegram)
- **Status:** 🚧 Foundation complete, ready for implementation
- **Purpose:** Real-time updates, automated analysis, Telegram interface

**Both systems:**
- Share the same Supabase database
- Work independently or together
- Zero port conflicts
- Can be deployed separately

---

## 🎯 Key Features

### PROJ344 Features

✅ **Multi-Dimensional Scoring** (0-999 scale)
  - **Micro:** Detail-level importance
  - **Macro:** Case-wide significance
  - **Legal:** Legal weight & admissibility
  - **Relevancy:** Weighted composite score

✅ **Smoking Gun Detection** (900+ relevancy)
  - Automatic identification of critical evidence
  - Perjury indicator tracking
  - Constitutional violation detection

✅ **7 Interactive Dashboards**
  - Master Dashboard (8501): Complete case overview
  - Legal Intelligence (8502): Document-by-document analysis
  - CEO Dashboard (8503): File organization & system health
  - Enhanced Scanning Monitor (8504): Real-time scan progress
  - Timeline & Violations (8505): Constitutional violations tracker
  - Master 5W+H (8506): 5W+H analysis framework
  - Scanning Monitor (alt): Alternative progress view

✅ **AI-Powered Analysis**
  - Claude Sonnet 4.5 for document intelligence
  - Automatic summarization & key quote extraction
  - Fraud/perjury indicator detection

### AGI Protocol Features (Foundation)

✅ **FastAPI REST API** (Port 8000)
  - Health check endpoints
  - PROJ344 bridge (read-only access)
  - Swagger UI documentation
  - WebSocket support ready

✅ **Telegram Bot Integration** (Port 8443)
  - Real-time case updates
  - Document upload via chat
  - Query legal database
  - Automated notifications

✅ **Read-Only Bridge to PROJ344**
  - Query documents by score
  - Search violations
  - Get statistics
  - Safe, independent access

---

## 🚀 Quick Start

### Option 1: PROJ344 Only (Dashboards)

```bash
# 1. Clone repository
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your Supabase and Anthropic credentials

# 4. Launch all dashboards
./scripts/launch-all-dashboards.sh

# Access at:
# http://localhost:8501 - Master Dashboard
# http://localhost:8502 - Legal Intelligence
# http://localhost:8503 - CEO Dashboard
# http://localhost:8504 - Enhanced Scanning Monitor
# http://localhost:8505 - Timeline & Violations
# http://localhost:8506 - Master 5W+H Framework
```

### Option 2: AGI Protocol Only (API + Bot)

```bash
# 1. Navigate to AGI directory
cd agi-protocol

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"

# 4. Run API
cd api
python main.py

# 5. Visit Swagger UI
# http://localhost:8000/docs

# 6. Test health endpoint
curl http://localhost:8000/health
```

### Option 3: Both Systems (Docker)

```bash
# 1. Set environment variables
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"

# 2. Start PROJ344 dashboards
docker-compose up -d

# 3. Start AGI Protocol
docker-compose -f docker-compose.agi.yml up -d

# 4. Check status
docker-compose ps
docker-compose -f docker-compose.agi.yml ps

# Both systems now running!
```

---

## 📦 Repository Structure

```
ASEAGI/
├── dashboards/              # PROJ344 Streamlit Dashboards (7 apps)
│   ├── proj344_master_dashboard.py
│   ├── legal_intelligence_dashboard.py
│   ├── ceo_dashboard.py
│   ├── enhanced_scanning_monitor.py
│   ├── timeline_violations_dashboard.py
│   ├── master_5wh_dashboard.py
│   └── scanning_monitor_dashboard.py
│
├── scanners/                # Document Processing
│   ├── batch_scan_documents.py
│   └── query_legal_documents.py
│
├── core/                    # Error Handling & Tracking
│   ├── bug_tracker.py
│   └── workspace_config.py
│
├── agi-protocol/            # 🆕 AGI Protocol System
│   ├── api/                 # FastAPI Backend
│   │   ├── main.py
│   │   └── integrations/proj344_bridge.py
│   ├── telegram-bot/        # Telegram Bot
│   ├── tests/               # Testing
│   ├── requirements.txt     # Separate dependencies
│   └── README.md            # AGI Protocol guide
│
├── scripts/                 # Utility Scripts
│   └── launch-all-dashboards.sh
│
├── docs/                    # Documentation
├── requirements.txt         # PROJ344 dependencies
├── docker-compose.yml       # PROJ344 Docker config
├── docker-compose.agi.yml   # 🆕 AGI Protocol Docker config
└── CLAUDE.md                # Detailed project guide
```

---

## 📖 Documentation

### Getting Started
- **Quick Start:** This README
- **Complete Guide:** `CLAUDE.md` (comprehensive project documentation)
- **Session Guide:** `SESSION_GUIDE_2025-11-19.md` (latest changes explained)

### PROJ344 Documentation
- **Bug Fixes:** `BUGS_FIXED_2025-11-19.md`
- **Deployment:** `DEPLOY_TO_DIGITAL_OCEAN.md`, `DEPLOY_TO_STREAMLIT.md`
- **Troubleshooting:** `docs/TROUBLESHOOTING_ERRORS.md`

### AGI Protocol Documentation
- **Overview:** `agi-protocol/README.md`
- **Integration Strategy:** `AGI_PROJ344_INTEGRATION_STRATEGY.md`
- **API Docs:** http://localhost:8000/docs (when running)

---

## 🔧 Environment Variables

### Required for PROJ344
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Additional for AGI Protocol
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
API_SECRET_KEY=your_secret_key
```

See `.env.example` and `.env.agi.example` for complete templates.

---

## 🎨 Dashboard Showcase

### PROJ344 Master Dashboard (8501)
- **Purpose:** Main case intelligence interface
- **Features:** Smoking gun filter, document search, score visualizations
- **Use Case:** Daily case review and evidence preparation

### Legal Intelligence Dashboard (8502)
- **Purpose:** Detailed document analysis
- **Features:** Key quotes, fraud indicators, cross-references
- **Use Case:** Deep document review

### Master 5W+H Dashboard (8506)
- **Purpose:** 5W+H framework analysis
- **Features:** Independent queries (Who, What, When, Where, Why, How)
- **Use Case:** Comprehensive legal intelligence

### AGI Protocol API (8000)
- **Purpose:** REST API for automation
- **Features:** PROJ344 bridge, Telegram integration, health checks
- **Use Case:** Real-time updates, Telegram bot, automation

---

## 🚢 Deployment

### Development (Local)
```bash
./scripts/launch-all-dashboards.sh
```

### Production (Docker)
```bash
# PROJ344 + AGI Protocol
docker-compose up -d
docker-compose -f docker-compose.agi.yml up -d
```

### Cloud Platforms
- **Streamlit Cloud:** See `DEPLOY_TO_STREAMLIT.md`
- **Digital Ocean:** See `DEPLOY_TO_DIGITAL_OCEAN.md`
- **Heroku:** See `Procfile`

---

## 📊 Statistics

### PROJ344 System
- **Python Files:** 35 files
- **Total LOC:** ~10,034 lines
- **Dashboards:** 7 applications
- **Ports:** 8501-8506
- **Documents Processed:** 601+ (as of Nov 2025)

### AGI Protocol
- **Python Files:** 11 files (foundation)
- **Total LOC:** ~1,750 lines
- **API Endpoints:** 4 (skeleton)
- **Ports:** 8000, 8443
- **Status:** Ready for implementation

---

## 🛠️ Technology Stack

### Frontend & Visualization
- **Streamlit 1.31.0** - Dashboard framework
- **Plotly 5.18.0** - Interactive visualizations
- **Pandas 2.1.4** - Data manipulation

### Backend & API
- **FastAPI** - REST API framework (AGI Protocol)
- **Uvicorn** - ASGI server
- **python-telegram-bot** - Telegram integration

### Database & Storage
- **Supabase 2.3.4** - PostgreSQL database
- **PostgREST 0.13.2** - REST API client

### AI & Processing
- **Anthropic Claude API** - Document analysis (Sonnet 4.5)
- **Pillow 10.2.0** - Image processing

### Infrastructure
- **Docker** - Containerization
- **GitHub Actions** - CI/CD
- **Pre-commit hooks** - Code quality

---

## 🧪 Testing

### PROJ344
```bash
# Test dashboard compilation
python -m py_compile dashboards/proj344_master_dashboard.py

# Launch single dashboard
streamlit run dashboards/proj344_master_dashboard.py
```

### AGI Protocol
```bash
# Test API
cd agi-protocol/api
python main.py

# Test bridge
python agi-protocol/api/integrations/proj344_bridge.py

# Run tests (when implemented)
pytest agi-protocol/tests/
```

---

## 🤝 Contributing

This is a specialized legal intelligence system for child protection cases. Contributions are welcome for:

- Bug fixes
- Documentation improvements
- New dashboard features
- AGI Protocol implementation
- Testing improvements

See `CLAUDE.md` for development guidelines.

---

## 📜 License

[Specify your license here]

---

## 🙏 Acknowledgments

Built for **Ashe Bucknor** and families navigating child protection cases.

**Case Context:** In re Ashe Bucknor (J24-00478)

---

## 📞 Support & Resources

### Documentation
- **Project Overview:** `CLAUDE.md`
- **Session Guide:** `SESSION_GUIDE_2025-11-19.md`
- **Bug Reports:** `BUGS_FIXED_2025-11-19.md`
- **Integration Guide:** `AGI_PROJ344_INTEGRATION_STRATEGY.md`

### Health Checks
```bash
# PROJ344 Dashboard
curl http://localhost:8501/_stcore/health

# AGI Protocol API
curl http://localhost:8000/health

# Database Connection
python -c "from supabase import create_client; import os; print(create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY']).table('legal_documents').select('count').execute())"
```

### Troubleshooting
See `docs/TROUBLESHOOTING_ERRORS.md` or `agi-protocol/README.md` (Troubleshooting section)

---

## 🎯 Current Status

| System | Status | Ports | Documentation |
|--------|--------|-------|---------------|
| **PROJ344** | ✅ Production-ready | 8501-8506 | Complete |
| **AGI Protocol** | 🚧 Foundation complete | 8000, 8443 | Complete |
| **Integration** | ✅ Zero conflicts | All ports available | Complete |

**Last Updated:** November 19, 2025
**Version:** 2.0 (PROJ344 + AGI Protocol)

---

**For Ashe. For Justice. For All Children.** 🛡️

---

## Quick Links

- [CLAUDE.md](CLAUDE.md) - Complete project documentation
- [SESSION_GUIDE_2025-11-19.md](SESSION_GUIDE_2025-11-19.md) - Today's session explained
- [agi-protocol/README.md](agi-protocol/README.md) - AGI Protocol guide
- [AGI_PROJ344_INTEGRATION_STRATEGY.md](AGI_PROJ344_INTEGRATION_STRATEGY.md) - Integration details
- [BUGS_FIXED_2025-11-19.md](BUGS_FIXED_2025-11-19.md) - Recent bug fixes
