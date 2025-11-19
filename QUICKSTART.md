# 🚀 ASEAGI Quick Start Guide

**Get up and running in 5 minutes**

---

## What You're Getting

Two powerful systems that work together:
1. **PROJ344** - 7 interactive dashboards for legal document analysis
2. **AGI Protocol** - FastAPI backend + Telegram bot for automation

---

## Prerequisites

- Python 3.9+ installed
- Git installed
- Supabase account (free: https://supabase.com)
- Anthropic API key (free $5 credit: https://anthropic.com)

---

## Option 1: Just the Dashboards (Recommended First)

### Step 1: Clone and Install (2 minutes)

```bash
# Clone repository
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 minute)

```bash
# Create .env file
cp .env.example .env

# Edit .env with your credentials:
# nano .env  (or use your favorite editor)
```

Add these three lines to `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Step 3: Launch (1 minute)

```bash
# Launch all 6 dashboards
./scripts/launch-all-dashboards.sh
```

### Step 4: Access

Open your browser to:
- **Master Dashboard:** http://localhost:8501
- **Legal Intelligence:** http://localhost:8502
- **CEO Dashboard:** http://localhost:8503
- **Scanning Monitor:** http://localhost:8504
- **Timeline & Violations:** http://localhost:8505
- **5W+H Framework:** http://localhost:8506

**Done!** 🎉

---

## Option 2: Add AGI Protocol API (Optional)

### Step 1: Install AGI Dependencies

```bash
cd agi-protocol
pip install -r requirements.txt
```

### Step 2: Run API

```bash
cd api
python main.py
```

### Step 3: Access Swagger UI

Open: http://localhost:8000/docs

**Done!** 🎉

---

## Option 3: Everything with Docker (Advanced)

### Step 1: Set Environment Variables

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-supabase-anon-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### Step 2: Start Both Systems

```bash
# Start PROJ344 dashboards
docker-compose up -d

# Start AGI Protocol
docker-compose -f docker-compose.agi.yml up -d
```

### Step 3: Check Status

```bash
docker-compose ps
docker-compose -f docker-compose.agi.yml ps
```

**Done!** 🎉

---

## First Steps After Installation

### 1. Explore the Master Dashboard

Visit http://localhost:8501 and:
- Check system overview
- View document statistics
- Test the smoking gun filter (relevancy >= 900)

### 2. Scan Your First Document

```bash
# Navigate to scanners directory
cd scanners

# Scan a single document
python batch_scan_documents.py /path/to/your/document.jpg

# Or scan a folder
python batch_scan_documents.py /path/to/documents/
```

### 3. Test AGI Protocol API (if installed)

```bash
# Check API health
curl http://localhost:8000/health

# Get system status
curl http://localhost:8000/status
```

---

## Troubleshooting

### "Streamlit not found"

```bash
pip install streamlit
```

### "Environment variables not set"

Make sure your `.env` file has:
```env
SUPABASE_URL=https://...
SUPABASE_KEY=eyJ...
ANTHROPIC_API_KEY=sk-ant-...
```

Then:
```bash
source .env  # Load variables
```

### "Port already in use"

```bash
# Check what's using port 8501
lsof -i :8501

# Kill the process if needed
kill -9 <PID>
```

### "Can't connect to Supabase"

Test your connection:
```bash
python -c "from supabase import create_client; import os; print(create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY']).table('legal_documents').select('count').execute())"
```

---

## Next Steps

### Learn More

- **Full Documentation:** Read `CLAUDE.md`
- **Latest Session:** Read `SESSION_GUIDE_2025-11-19.md`
- **AGI Protocol:** Read `agi-protocol/README.md`

### Customize

- **Dashboard Configuration:** Edit files in `dashboards/`
- **Scanning Settings:** Edit `scanners/batch_scan_documents.py`
- **API Endpoints:** Add to `agi-protocol/api/routers/`

### Deploy

- **Local:** You're already there! ✅
- **Docker:** See above (Option 3)
- **Cloud:** See `DEPLOY_TO_STREAMLIT.md` or `DEPLOY_TO_DIGITAL_OCEAN.md`

---

## Getting Help

### Check Documentation
1. `README.md` - Overview
2. `CLAUDE.md` - Detailed guide
3. `SESSION_GUIDE_2025-11-19.md` - Latest changes
4. `BUGS_FIXED_2025-11-19.md` - Known fixes

### Common Issues
- **Port conflicts:** Use different ports in docker-compose
- **Environment variables:** Double-check .env file
- **Database issues:** Verify Supabase credentials
- **API errors:** Check logs with `docker-compose logs -f`

---

## Quick Commands Reference

### PROJ344
```bash
# Launch all dashboards
./scripts/launch-all-dashboards.sh

# Launch single dashboard
streamlit run dashboards/proj344_master_dashboard.py

# Scan documents
python scanners/batch_scan_documents.py /path/to/docs
```

### AGI Protocol
```bash
# Run API
cd agi-protocol/api && python main.py

# Test API
curl http://localhost:8000/health

# View API docs
# Open http://localhost:8000/docs
```

### Docker
```bash
# Start PROJ344
docker-compose up -d

# Start AGI Protocol
docker-compose -f docker-compose.agi.yml up -d

# Stop everything
docker-compose down
docker-compose -f docker-compose.agi.yml down

# View logs
docker-compose logs -f
```

---

## Success Checklist

- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Dashboards launching successfully
- [ ] Can access http://localhost:8501
- [ ] Can scan a test document
- [ ] (Optional) AGI Protocol API running
- [ ] (Optional) Docker containers healthy

---

**That's it! You're ready to use ASEAGI.** 🎉

For detailed information, see `README.md` and `CLAUDE.md`.

**For Ashe. For Justice. For All Children.** 🛡️
