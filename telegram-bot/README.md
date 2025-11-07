# ASEAGI Telegram Bot API Backend

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

FastAPI backend that provides endpoints for the ASEAGI Telegram bot commands.

---

## 🎯 What This Does

Enables the Telegram bot to query the ASEAGI case database with commands:
- `/status` - Case status overview
- `/events` - Recent court events
- `/documents` - High-relevancy documents
- `/communications` - Recent communications
- `/evidence` - Critical evidence summary
- `/cases` - Case information
- `/help` - Available commands

**All querying the actual Supabase database in real-time using NON-NEGOTIABLE tables.**

---

## ✨ Critical Features

| Feature | Status |
|---------|--------|
| ✅ Uses correct table names (events, document_journal, communications) | FIXED |
| ✅ FastAPI with automatic OpenAPI docs | READY |
| ✅ Supabase integration | READY |
| ✅ Docker support | READY |
| ✅ Health checks | READY |
| ✅ CORS enabled | READY |

---

## 📁 Project Structure

```
telegram-bot/
├── api_server.py          # Main FastAPI server
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose configuration
├── .env.example           # Environment template
├── .env                   # Your actual credentials (create this)
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

---

## 🚀 Quick Start

### Option 1: Run Locally (Development)

```bash
cd /home/user/ASEAGI/telegram-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your SUPABASE_KEY

# Run server
python3 api_server.py
```

Server will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

### Option 2: Run with Docker (Production)

```bash
cd /home/user/ASEAGI/telegram-bot

# Configure environment
cp .env.example .env
nano .env  # Add your SUPABASE_KEY

# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop server
docker-compose down
```

---

## 🔧 Environment Variables

Create `.env` file with:

```bash
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGc...your-actual-key-here
PORT=8000
```

Get your `SUPABASE_KEY` from:
https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/settings/api

---

## 📊 API Endpoints

### Health & Status

**GET** `/` - Health check
```bash
curl http://localhost:8000/
```

**GET** `/health` - Detailed health check
```bash
curl http://localhost:8000/health
```

### Telegram Commands

**GET** `/telegram/status` - Case status overview
```bash
curl http://localhost:8000/telegram/status
```

**GET** `/telegram/events` - Recent court events
```bash
# Default: last 30 days, limit 10
curl http://localhost:8000/telegram/events

# Custom: last 60 days, limit 20
curl http://localhost:8000/telegram/events?days=60&limit=20
```

**GET** `/telegram/documents` - High-relevancy documents
```bash
# Default: min_relevancy 700, limit 10
curl http://localhost:8000/telegram/documents

# Custom: min_relevancy 900, limit 5
curl http://localhost:8000/telegram/documents?min_relevancy=900&limit=5
```

**GET** `/telegram/communications` - Recent communications
```bash
# Default: last 30 days, limit 10
curl http://localhost:8000/telegram/communications

# Custom: last 7 days, limit 5
curl http://localhost:8000/telegram/communications?days=7&limit=5
```

**GET** `/telegram/evidence` - Critical evidence summary
```bash
curl http://localhost:8000/telegram/evidence
```

**GET** `/telegram/help` - Available commands
```bash
curl http://localhost:8000/telegram/help
```

**GET** `/telegram/cases` - Case information
```bash
curl http://localhost:8000/telegram/cases
```

---

## 🗄️ Database Tables Used

### NON-NEGOTIABLE Tables (Critical)

1. **events** - Timeline (MOST IMPORTANT)
   - All court hearings, filings, motions, rulings, deadlines
   - `event_date`, `event_title`, `event_type`, `significance_score`

2. **document_journal** - Processing & Growth Assessment
   - Journal entry for each document scan
   - `original_filename`, `relevancy_score`, `processing_status`, `insights_extracted`

3. **communications** - Evidence Tracking
   - All texts, emails, letters, communications
   - `sender`, `recipient`, `subject`, `truthfulness_score`, `contains_contradiction`

---

## 🐛 Troubleshooting

### "Missing SUPABASE_KEY environment variable"

**Problem:** Environment variable not set

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env

# Should show:
# SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
# SUPABASE_KEY=eyJhbGc...
```

---

### "Error fetching events: relation 'events' does not exist"

**Problem:** NON-NEGOTIABLE tables not created in Supabase

**Solution:**

1. Go to Supabase dashboard: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu
2. Click "SQL Editor" → "New Query"
3. Run the SQL script: `mcp-servers/aseagi-mvp-server/database/01_create_critical_tables.sql`
4. Verify tables exist:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('communications', 'events', 'document_journal');
```

Should return 3 rows.

---

### Docker container can't connect to Supabase

**Problem:** Network issues or wrong environment variables

**Solution:**

```bash
# Check container logs
docker-compose logs api

# Verify environment variables in container
docker-compose exec api env | grep SUPABASE

# Restart with fresh environment
docker-compose down
docker-compose up -d

# Test connection manually
docker-compose exec api python3 -c "from supabase import create_client; client = create_client('$SUPABASE_URL', '$SUPABASE_KEY'); print('Connected!')"
```

---

### Telegram bot still can't reach API

**Problem:** Telegram bot needs to use correct hostname

**Solution:**

If running in Docker, the Telegram bot should connect to:
```
http://api:8000/telegram/status
```

If running locally, use:
```
http://localhost:8000/telegram/status
```

Update the Telegram bot code to use the correct hostname based on environment.

---

## 🔐 Security Notes

**This is a backend API for the Telegram bot.**

- ✅ Runs on localhost or Docker network
- ✅ CORS enabled for flexibility
- ✅ Uses Supabase anon key (read-only permissions)
- ❌ No authentication (internal service only)
- ❌ No rate limiting (single user)

**For production deployment:**
- Add authentication (API keys or JWT)
- Implement rate limiting
- Add audit logging
- Deploy behind reverse proxy (nginx)

---

## 📝 Development

### Add New Endpoint

```python
@app.get("/telegram/mycommand")
async def telegram_mycommand():
    try:
        # Query Supabase
        data = supabase.table('events').select('*').limit(5).execute()

        message = "📊 My custom data:\n\n"
        for item in data.data:
            message += f"• {item['event_title']}\n"

        return StatusResponse(
            status="success",
            message=message,
            data={"items": data.data}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Run Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (future)
pytest tests/
```

### View API Documentation

When server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🎯 Integration with Telegram Bot

### Update Telegram Bot Code

The Telegram bot should make HTTP requests to this API:

```python
import requests

# In your Telegram bot handler
def handle_status_command(update, context):
    try:
        response = requests.get('http://api:8000/telegram/status')
        data = response.json()

        # Send message to Telegram
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=data['message'],
            parse_mode='Markdown'
        )
    except Exception as e:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error: {e}"
        )
```

---

## 📊 Monitoring

### Check Server Status

```bash
# Health check
curl http://localhost:8000/health

# Get status
curl http://localhost:8000/telegram/status

# View logs (Docker)
docker-compose logs -f api

# View logs (local)
# Logs output to stdout
```

### Monitor Performance

```bash
# Check API response time
time curl http://localhost:8000/telegram/events

# Check database connection
curl http://localhost:8000/health
```

---

## 🔗 Related Documentation

- FastAPI Docs: https://fastapi.tiangolo.com
- Supabase Python: https://supabase.com/docs/reference/python
- Docker Compose: https://docs.docker.com/compose

---

## 📄 License

Part of ASEAGI - Ashe Sanctuary of Empowerment AGI
Athena Guardian of Innocence Project

*For Ashe. For All Children.* ⚖️

*"When children speak, truth must roar louder than lies."*

---

## ✅ Checklist: Is It Working?

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with actual Supabase key
- [ ] Server starts without errors (`python3 api_server.py`)
- [ ] "✓ Supabase connection verified" message appears
- [ ] Health endpoint responds: `curl http://localhost:8000/health`
- [ ] Status endpoint responds: `curl http://localhost:8000/telegram/status`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Telegram bot can connect to API

If all checked, you're ready! 🎉

---

**Last Updated:** November 2025
**Version:** 1.0.0
**Status:** Production Ready
