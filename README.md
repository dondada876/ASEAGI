# ⚖️ PROJ344: Legal Case Intelligence Dashboards

AI-powered legal document intelligence system with multi-dimensional scoring for child protection cases.

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com)

## 🎯 Overview

**PROJ344** is a comprehensive legal intelligence system that uses AI to analyze legal documents with multi-dimensional scoring (Micro, Macro, Legal, Relevancy) to identify smoking gun evidence, detect perjury, and track constitutional violations.

**Built For:** Child protection cases, custody litigation, dependency proceedings

### Key Features

- 📊 **Multi-Dimensional Scoring** (0-999 scale)
  - Micro: Detail-level importance
  - Macro: Case-wide significance
  - Legal: Legal weight & admissibility
  - Relevancy: Weighted composite score

- 🔥 **Smoking Gun Detection** (900+ relevancy)
  - Automatic identification of critical evidence
  - Perjury indicator tracking
  - Constitutional violation detection

- 📈 **Interactive Dashboards**
  - Master Dashboard: Complete case overview
  - Legal Intelligence: Document-by-document analysis
  - CEO Dashboard: File organization & system health

- 🤖 **AI-Powered Analysis**
  - Claude Sonnet 4.5 for document intelligence
  - Automatic summarization & key quote extraction
  - Fraud/perjury indicator detection

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Supabase account (free tier works)
- Anthropic API key (for document scanning)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ASEAGI.git
cd ASEAGI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

4. **Set up Supabase database**
```bash
# Run the schema SQL file in your Supabase SQL editor
# File: supabase/schema.sql
```

5. **Launch dashboards**
```bash
# Launch all dashboards
./scripts/launch-all-dashboards.sh

# Or launch individually
streamlit run dashboards/proj344_master_dashboard.py --server.port 8501
```

6. **Access dashboards**
- PROJ344 Master: http://localhost:8501
- Legal Intelligence: http://localhost:8502
- CEO Dashboard: http://localhost:8503

## 📊 Dashboards

### 1. PROJ344 Master Dashboard (Port 8501)

Main dashboard for case intelligence and evidence review.

**Features:**
- System overview with key metrics
- Smoking gun documents (900+ relevancy)
- Perjury indicator tracking
- Document intelligence with filters
- Search & analytics

**Use Cases:**
- Daily case review
- Evidence preparation
- Motion planning
- Appellate record building

### 2. Legal Intelligence Dashboard (Port 8502)

Detailed document analysis with PROJ344 scoring.

**Features:**
- Document-by-document breakdown
- Score distribution analysis
- Key quotes & smoking guns
- Cross-reference capabilities

**Use Cases:**
- Deep document review
- Evidence package assembly
- Legal research

### 3. CEO Dashboard (Port 8503)

System administration and file organization.

**Features:**
- PARA structure overview
- File organization health
- Naming compliance tracking
- Duplicate detection

**Use Cases:**
- System monitoring
- File management
- Quality assurance

## 🔬 Document Scanning

### Scan Documents

```bash
# Scan all documents in directory
python3 scanners/batch_scan_documents.py /path/to/documents

# Scan with filters
python3 scanners/batch_scan_documents.py /path/to/documents --extensions .pdf,.jpg,.png

# Dry run (no database upload)
python3 scanners/batch_scan_documents.py /path/to/documents --dry-run
```

### Scoring Methodology

**Score Range: 0-999**

| Range | Category | Badge | Use Case |
|-------|----------|-------|----------|
| 900-999 | 🔥 Smoking Gun | Critical evidence | Motion exhibits, impeachment |
| 800-899 | ⚠️ Critical | High-value evidence | Supporting documents |
| 700-799 | 📌 Important | Strong evidence | Case building |
| 600-699 | 📋 Useful | Background | Context & discovery |
| 0-599 | 📄 Reference | General | Archive |

## 🏗️ Architecture

```
ASEAGI/
├── dashboards/              # Streamlit dashboards
│   ├── proj344_master_dashboard.py
│   ├── legal_intelligence_dashboard.py
│   └── ceo_dashboard.py
├── scanners/                # Document scanning tools
│   ├── batch_scan_documents.py
│   └── query_legal_documents.py
├── supabase/                # Database schemas
│   └── schema.sql
├── scripts/                 # Utility scripts
│   └── launch-all-dashboards.sh
├── docs/                    # Documentation
├── requirements.txt
├── .env.example
└── README.md
```

## 🗄️ Database Schema

### Core Tables

**legal_documents**
- Document metadata & PROJ344 scores
- Key quotes & smoking guns
- Perjury/fraud indicators
- W&I 388, CCP 473, criminal relevance

**court_events**
- Timeline of court proceedings
- Multi-jurisdiction tracking

**legal_violations**
- Constitutional violation tracker
- Due process monitoring

## 🔐 Security

### Environment Variables

**NEVER commit:**
- `.env` files
- API keys
- Supabase credentials
- Case documents

**Always use:**
- `.env.example` as template
- Environment variables for secrets
- `.gitignore` for sensitive files

### Data Privacy

- All case data stays in your Supabase instance
- Dashboards run locally (localhost only)
- No external data transmission
- API calls encrypted (HTTPS)

## 🌐 Deployment Options

### Option 1: Streamlit Community Cloud (Free)

1. Push to GitHub (public or private repo)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud UI
5. Deploy!

**Secrets to add in Streamlit Cloud:**
```toml
SUPABASE_URL = "your-url"
SUPABASE_KEY = "your-key"
```

### Option 2: Heroku

```bash
# Create Procfile
echo "web: streamlit run dashboards/proj344_master_dashboard.py --server.port \$PORT" > Procfile

# Deploy
heroku create proj344-dashboard
git push heroku main
heroku config:set SUPABASE_URL=your-url
heroku config:set SUPABASE_KEY=your-key
```

### Option 3: Docker

```bash
# Build
docker build -t ASEAGI .

# Run
docker run -p 8501:8501 \
  -e SUPABASE_URL=your-url \
  -e SUPABASE_KEY=your-key \
  ASEAGI
```

## 📖 Documentation

- [Dashboard Guide](docs/DASHBOARD-GUIDE.md)
- [Scanning Guide](docs/SCANNING-GUIDE.md)
- [API Documentation](docs/API.md)
- [PROJ344 Methodology](docs/PROJ344-METHODOLOGY.md)

## 🤝 Contributing

This is a private tool for legal case management. If you're working on a similar child protection case and would like to adapt this system, please reach out.

## ⚖️ Legal Notice

**Disclaimer:** This tool provides document analysis and intelligence for legal cases. It does NOT:
- Provide legal advice
- Replace qualified attorneys
- Make custody recommendations
- Guarantee legal outcomes

**Use Case:** Legal research, document organization, evidence preparation, case management.

## 📜 License

**Private Use Only** - This system contains case-specific code and methodologies for active litigation.

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Review documentation in `/docs`
- Check troubleshooting guides

## 🛡️ Mission Statement

**"No child's voice should be silenced by litigation. No protective parent should be punished for protecting."**

This system was built to ensure:
- Children's disclosures are heard
- Perjury is documented and prosecuted
- Protective parents have professional-grade tools
- Truth prevails over legal manipulation

---

**For Ashe. For Justice. For All Children.** 🛡️

## 🏆 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io) - Dashboard framework
- [Supabase](https://supabase.com) - PostgreSQL database
- [Anthropic Claude](https://anthropic.com) - AI analysis
- [Plotly](https://plotly.com) - Interactive visualizations

---

**Version:** 2.0
**Last Updated:** November 2025
**Case:** In re Ashe B. (J24-00478)
