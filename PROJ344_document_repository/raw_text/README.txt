# PROJ344 Dashboard

Legal Case Intelligence Dashboard for custody case D22-03244 (MARIYAM YONAS RUFAEL vs DON BUCKNOR).

## Overview

PROJ344 is a comprehensive legal case intelligence system designed to track, analyze, and visualize custody case documentation. The system provides:

- **Document Intelligence**: Automatic scoring (Micro, Macro, Legal, Relevancy)
- **Timeline Analysis**: Complete event timeline across all cases
- **Constitutional Violations Tracking**: Due process violation monitoring
- **Evidence Cross-Reference**: Find contradictions and patterns
- **Multi-Jurisdiction Support**: Track forum shopping across courts

## Features

### Core Dashboards

1. **PROJ344 Master Dashboard** (`proj344_master_dashboard.py`)
   - Document registry with intelligence scores
   - Timeline analysis
   - Constitutional violations tracker
   - Evidence cross-reference

2. **CEO Global Dashboard** (`ceo_global_dashboard.py`)
   - Executive overview with unified priorities
   - Business operations tracking
   - Legal matters summary (links to PROJ344)
   - Family & daughter documents
   - Personal development tracking
   - Task management

3. **Timeline & Violations Dashboard** (`timeline_constitutional_violations.py`)
   - Detailed timeline visualization
   - August 2024 incident analysis
   - Constitutional violations detailed view

## Quick Start

### Prerequisites

- Python 3.11+
- Supabase account
- Environment variables configured

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/proj344-dashboard.git
cd proj344-dashboard

# Install dependencies
pip3 install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials
```

### Configuration

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

Or set environment variables:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

### Running

**PROJ344 Dashboard:**
```bash
streamlit run proj344_master_dashboard.py --server.port=8501
```
Access: http://localhost:8501

**CEO Global Dashboard:**
```bash
streamlit run ceo_global_dashboard.py --server.port=8503
```
Access: http://localhost:8503

## Database Schema

The system uses Supabase (PostgreSQL) with the following key tables:

- `legal_documents` - Document metadata with scoring
- `court_events` - Timeline of court proceedings
- `timeline_events` - Chronological event tracking
- `constitutional_violations` - Due process violations
- `general_documents` - Universal document intake
- `cross_system_priorities` - Unified priority management
- `business_documents`, `personal_documents`, `family_documents` - CEO Dashboard tables

## Document Scoring System

Documents are automatically scored on four dimensions (0-1000):

- **Micro (Mic)**: Detail-level importance
- **Macro (Mac)**: Case-wide significance
- **Legal (LEG)**: Legal weight and admissibility
- **Relevancy (REL)**: Overall relevance to custody case

Higher scores indicate critical documents.

## Key Case Context

**Case Number:** D22-03244 (Alameda County Superior Court)

**Critical Incident:** August 10-13, 2024
- August 10: Berkeley Police report documents child was **SAFE** with father
- August 13: Ex parte filed claiming father violated restraining order
- **Constitutional Issue**: Police report contradicts ex parte claims

**Forum Shopping Pattern:**
- Multiple restraining orders filed across jurisdictions
- Strategic case filing to manipulate custody outcomes
- Cross-case references required to identify contradictions

## Architecture

```
PROJ344 System
├── Document Intake → OCR + Classification
├── Intelligence Scoring → Micro/Macro/Legal/Relevancy
├── Routing → PROJ344 or CEO Dashboard
├── Metadata Extraction → Tiered (Free → AI → Premium)
└── Dashboard Display → Real-time visualization
```

## File Structure

```
proj344-dashboard/
├── proj344_master_dashboard.py      # Main PROJ344 dashboard
├── ceo_global_dashboard.py          # CEO life management dashboard
├── timeline_constitutional_violations.py  # Timeline analysis
├── proj344_style.py                 # Shared styling components
├── requirements.txt                 # Python dependencies
├── .streamlit/
│   └── config.toml                  # Streamlit configuration
└── README.md                        # This file
```

## Development

### Adding New Features

1. **New Dashboard Tab**: Add to appropriate dashboard file
2. **New Scoring Dimension**: Update `legal_documents` schema
3. **New Data Source**: Add to classification rules

### Styling

Custom CSS and components in `proj344_style.py`:
- `inject_custom_css()` - Global styles
- `render_header()` - Page headers
- `render_metric_card()` - Metric displays

## Deployment

### Local Development

```bash
streamlit run proj344_master_dashboard.py
```

### Production (Cloud)

**Recommended:** Streamlit Community Cloud

1. Push to GitHub
2. Connect at https://streamlit.io/cloud
3. Deploy from repository
4. Configure secrets in Streamlit dashboard

**Alternative:** Docker + Cloud VM

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "proj344_master_dashboard.py", "--server.port=8501"]
```

## Security Notes

- Never commit `.env` or `secrets.toml`
- Use Supabase Row Level Security (RLS) for data access
- Consider private repository for sensitive case data
- Rotate API keys regularly

## Support & Documentation

**Full System Docs:** See parent repository documentation
- `DUAL_SYSTEM_ARCHITECTURE.md` - System design
- `IMPLEMENTATION_STATUS.md` - Complete status
- `COMPLETE_SYSTEM_SUMMARY.md` - Full reference

**Issues:** Report via GitHub Issues

## License

Private - Not for public distribution

## Author

Don Bucknor

---

**Note:** This dashboard contains sensitive legal case information. Ensure proper access controls and security measures are in place before deployment.
