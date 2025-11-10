# ASEAGI Telegram Bot

Telegram bot for ASEAGI Legal Case Management System.

## Setup

### 1. Get a Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the prompts:
   - Choose a name for your bot (e.g., "ASEAGI Legal Assistant")
   - Choose a username (e.g., "aseagi_legal_bot")
4. Copy the bot token that BotFather gives you

### 2. Configure Environment

Add your bot token to `.env` file in project root:

```bash
# Add to /home/user/ASEAGI/.env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

Or export it:

```bash
export TELEGRAM_BOT_TOKEN='your_bot_token_here'
```

### 3. Install Dependencies

```bash
cd /home/user/ASEAGI/bot
pip install -r requirements.txt
```

### 4. Run the Test Bot

```bash
# From bot directory
python3 test_bot.py

# Or from project root
python3 bot/test_bot.py
```

## Available Commands

### Working Commands (Mock Data)
- `/start` - Welcome message and command list
- `/help` - Show help message
- `/status` - Bot uptime and system status
- `/violations` - Show detected legal violations (mock data)
- `/timeline [days]` - Show case timeline (mock data)
- `/report` - Generate daily summary (mock data)

### Coming Soon (Requires FastAPI Backend)
- `/search <query>` - Search communications
- `/actions` - Show pending action items
- `/deadline` - Show upcoming deadlines
- `/hearing [id]` - Show hearing information
- `/motion <type> <issue>` - Generate motion outline

## Testing

1. Start the bot with `python3 test_bot.py`
2. Open Telegram and search for your bot username
3. Send `/start` to begin
4. Try commands like `/violations`, `/timeline`, `/report`

## Current Limitations

This is a **test version** with:
- ✅ Basic Telegram connectivity
- ✅ Mock data for key commands
- ❌ No FastAPI backend connection
- ❌ No real Supabase data
- ❌ No document processing

## Next Steps

To enable full functionality:

1. **Deploy FastAPI Backend** (see `docs/FRAMEWORK_DECISION_FOR_ASEAGI.md`)
   ```bash
   # Create API service on port 8000
   # Implement endpoints: /telegram/violations, /telegram/search, etc.
   ```

2. **Connect to Supabase**
   ```python
   # Add Supabase connection to fetch real data
   # Query legal_documents, court_events, legal_violations tables
   ```

3. **Docker Deployment**
   ```bash
   # Use docker-compose to run bot + API together
   # See technical guide for full docker-compose.yml
   ```

## Architecture

```
┌─────────────────────────────────┐
│   Telegram Users                │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│   ASEAGI Telegram Bot           │
│   (test_bot.py)                 │
│   Port: N/A (polling)           │
└───────────┬─────────────────────┘
            │
            ▼ (Future)
┌─────────────────────────────────┐
│   FastAPI Backend               │
│   Port: 8000                    │
│   Endpoints: /telegram/*        │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│   Supabase PostgreSQL           │
│   - legal_documents             │
│   - court_events                │
│   - legal_violations            │
└─────────────────────────────────┘
```

## For Ashe. For Justice. For All Children. 🛡️

**Case:** In re Ashe B. (J24-00478)
**Status:** Active Litigation
