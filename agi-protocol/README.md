# AGI Protocol - Legal Defense Multi-Agent System

**Status:** 🚧 In Development
**Integration:** Modular - Works alongside PROJ344
**Ports:** 8000 (API), 8443 (Telegram Webhook)
**Last Updated:** November 19, 2025

---

## Overview

The AGI Protocol is a multi-agent legal defense system that provides:
- **Real-time Telegram bot** for case updates and document uploads
- **FastAPI backend** for REST API and WebSocket communication
- **PROJ344 integration** via bridge modules (read-only)
- **Automated legal research** and motion drafting capabilities

### Key Features

✅ **Zero Conflicts with PROJ344**
- Separate port allocation (8000, 8443 vs 8501-8506)
- Independent Docker Compose configuration
- Shared Supabase database (read-only access to PROJ344 tables)
- Can run simultaneously or independently

✅ **Modular Architecture**
- Self-contained in `agi-protocol/` directory
- Separate dependencies (`requirements.txt`)
- Independent deployment lifecycle
- Can be removed without affecting PROJ344

---

## Directory Structure

```
agi-protocol/
├── api/                          # FastAPI Backend (Port 8000)
│   ├── main.py                   # API entry point
│   ├── routers/                  # API endpoints
│   │   ├── telegram.py           # Telegram commands
│   │   ├── documents.py          # Document management
│   │   └── analysis.py           # Legal analysis
│   ├── models/                   # Pydantic models
│   ├── services/                 # Business logic
│   └── integrations/             # External integrations
│       └── proj344_bridge.py     # PROJ344 read-only bridge
│
├── telegram-bot/                 # Telegram Bot (Port 8443)
│   ├── bot.py                    # Bot entry point
│   ├── handlers/                 # Command handlers
│   └── utils/                    # Bot utilities
│
├── tests/                        # Testing
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
│
├── docs/                         # Documentation
│   └── PRD.md                    # Product Requirements
│
├── requirements.txt              # Python dependencies (separate from PROJ344)
├── Dockerfile.api                # API container
├── Dockerfile.bot                # Bot container
└── README.md                     # This file
```

---

## Port Allocation

| Service | Port | Purpose | Conflicts |
|---------|------|---------|-----------|
| AGI API | 8000 | REST API + WebSocket | ✅ None |
| Telegram Webhook | 8443 | HTTPS webhook endpoint | ✅ None |
| Redis (optional) | 6379 | Caching layer | ✅ None |

**PROJ344 Ports (Protected):**
- 8501-8506: Streamlit Dashboards
- No conflicts with AGI Protocol

---

## Installation

### Prerequisites

1. **PROJ344 already working** (required)
2. Python 3.9+ installed
3. Docker & Docker Compose (optional)
4. Telegram Bot Token from @BotFather

### Setup

```bash
# 1. Navigate to AGI Protocol directory
cd agi-protocol

# 2. Install dependencies (in separate virtual environment)
python3 -m venv venv-agi
source venv-agi/bin/activate  # On Windows: venv-agi\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp ../.env.agi.example ../.env.agi
# Edit .env.agi with your credentials

# 4. Test API (development mode)
cd api
uvicorn main:app --reload --port 8000
# Visit http://localhost:8000/docs for Swagger UI

# 5. Test Telegram Bot (polling mode)
cd ../telegram-bot
python bot.py
```

### Docker Deployment

```bash
# From repository root

# Option 1: AGI Protocol only
docker-compose -f docker-compose.agi.yml up -d

# Option 2: PROJ344 + AGI Protocol (both systems)
docker-compose up -d  # Start PROJ344
docker-compose -f docker-compose.agi.yml up -d  # Start AGI Protocol

# Check status
docker-compose -f docker-compose.agi.yml ps

# View logs
docker-compose -f docker-compose.agi.yml logs -f agi-api
docker-compose -f docker-compose.agi.yml logs -f agi-telegram-bot

# Stop AGI Protocol (PROJ344 continues running)
docker-compose -f docker-compose.agi.yml down
```

---

## Integration with PROJ344

### Shared Resources

**Database (Supabase):**
- ✅ Shares same `SUPABASE_URL` and `SUPABASE_KEY`
- ✅ Read access to `legal_documents` table
- ✅ Read access to `court_events`, `legal_violations`
- ⚠️ NO write access to PROJ344 tables (safety)

**API Keys:**
- ✅ Shares `ANTHROPIC_API_KEY` for Claude API
- ✅ Separate rate limits (independent billing)

### Bridge Module

```python
# agi-protocol/api/integrations/proj344_bridge.py
from supabase import create_client
import os

class PROJ344Bridge:
    """Read-only bridge to PROJ344 systems"""

    def __init__(self):
        self.supabase = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_KEY']
        )

    async def get_smoking_guns(self):
        """Get documents with relevancy >= 900"""
        return self.supabase.table('legal_documents')\
            .select('*')\
            .gte('relevancy_number', 900)\
            .execute()

    async def get_violations(self):
        """Get all legal violations"""
        return self.supabase.table('legal_violations')\
            .select('*')\
            .order('severity_score', desc=True)\
            .execute()
```

**Safety Features:**
- Read-only access to PROJ344 tables
- No modifications to PROJ344 code
- Independent failure (PROJ344 continues if AGI fails)
- Separate logging and error tracking

---

## API Endpoints

### Health Check
```bash
GET /health
# Returns: {"status": "healthy", "version": "0.1.0"}
```

### Telegram Commands
```bash
GET /telegram/report          # Daily case summary
GET /telegram/violations      # Legal violations list
GET /telegram/timeline        # Case events timeline
GET /telegram/deadlines       # Upcoming deadlines
POST /telegram/upload         # Upload document via bot
```

### Document Management
```bash
GET  /documents/list          # List all documents
GET  /documents/{id}          # Get document details
POST /documents/upload        # Upload new document
GET  /documents/search        # Search documents
```

### Legal Analysis
```bash
POST /analysis/document       # Analyze single document
POST /analysis/motion         # Generate legal motion
GET  /analysis/research       # Legal research query
```

---

## Telegram Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Initialize bot | `/start` |
| `/report` | Daily case summary | `/report` |
| `/violations` | List legal violations | `/violations` |
| `/timeline` | Case events timeline | `/timeline` |
| `/deadlines` | Upcoming deadlines | `/deadlines` |
| `/upload` | Upload document | Send file to bot |
| `/search <query>` | Search documents | `/search perjury` |
| `/motion <type>` | Generate motion | `/motion dismiss` |

---

## Development

### Running Tests

```bash
# Unit tests
pytest tests/unit -v

# Integration tests
pytest tests/integration -v

# Coverage report
pytest --cov=api --cov-report=html
```

### Code Quality

```bash
# Format code
black api/ telegram-bot/

# Lint code
flake8 api/ telegram-bot/

# Type checking
mypy api/ telegram-bot/
```

---

## Safety & Rollback

### If Something Goes Wrong

```bash
# Stop AGI Protocol immediately (PROJ344 unaffected)
docker-compose -f docker-compose.agi.yml down

# Or, remove entire AGI Protocol
rm -rf agi-protocol/
# PROJ344 continues to work normally
```

### Health Monitoring

```bash
# Check API health
curl http://localhost:8000/health

# Check bot status
curl http://localhost:8000/telegram/status

# View logs
tail -f agi-protocol/logs/api.log
tail -f agi-protocol/logs/bot.log
```

---

## Troubleshooting

### Port Conflicts

**Error:** `Address already in use (port 8000)`

**Solution:**
```bash
# Check what's using port 8000
lsof -i :8000

# If nothing should be using it, change AGI Protocol port
# Edit docker-compose.agi.yml: "8001:8000" instead of "8000:8000"
```

### Database Connection Issues

**Error:** `Could not connect to Supabase`

**Solution:**
```bash
# Verify environment variables
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Test connection
python -c "from supabase import create_client; import os; print(create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY']).table('legal_documents').select('count').execute())"
```

### Telegram Bot Not Responding

**Error:** Bot doesn't respond to commands

**Solution:**
```bash
# Check bot token
echo $TELEGRAM_BOT_TOKEN

# Verify bot is running
docker logs agi-telegram-bot

# Test API endpoint
curl http://localhost:8000/telegram/report
```

---

## Roadmap

### Phase 1: Foundation (Current)
- [x] Directory structure
- [x] Configuration files
- [ ] FastAPI skeleton
- [ ] PROJ344 bridge module
- [ ] Basic health checks

### Phase 2: API Implementation
- [ ] Telegram command endpoints
- [ ] Document upload/retrieval
- [ ] WebSocket support
- [ ] Authentication & security

### Phase 3: Telegram Bot
- [ ] Command handlers
- [ ] File upload handling
- [ ] Real-time notifications
- [ ] Webhook configuration

### Phase 4: Advanced Features
- [ ] Multi-agent orchestration
- [ ] Legal research automation
- [ ] Motion drafting
- [ ] Case timeline generation

---

## Contributing

This module is part of the ASEAGI project. See main repository README for contribution guidelines.

---

## License

Same as ASEAGI main project.

---

## Support

For issues specific to AGI Protocol:
1. Check this README first
2. Review `/docs/PRD.md` for detailed requirements
3. Check logs in `agi-protocol/logs/`
4. Ensure PROJ344 is working (required dependency)

**For Ashe. For Justice. For All Children.** 🛡️
