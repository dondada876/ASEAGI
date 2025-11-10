# Telegram Bot Testing Guide for ASEAGI

**Bot File:** `telegram_document_bot.py`
**Branch:** `merge-telegram-bot`
**Last Updated:** November 10, 2025

---

## ✅ YES - Telegram Bot Exists!

The ASEAGI repository contains a **fully functional Telegram Document Ingestion Bot** on the `merge-telegram-bot` branch.

---

## 📋 Bot Capabilities

### Document Upload Flow

1. **Upload Photo or PDF** from your phone
2. **Select Document Type:**
   - 🚔 Police Report (PLCR)
   - 📄 Declaration (DECL)
   - 📸 Evidence/Photo (EVID)
   - 👶 CPS Report (CPSR)
   - 📋 Response (RESP)
   - 🔬 Forensic Report (FORN)
   - ⚖️ Court Order (ORDR)
   - 📑 Motion (MOTN)
   - 🎤 Hearing Transcript (HEAR)
   - 📎 Other (OTHR)

3. **Enter Document Date** (YYYYMMDD format or "today")
4. **Add Title/Description** (e.g., "Police Report - Child was Safe")
5. **Add Notes & Context** (why is this document relevant?)
6. **Choose Relevancy Level:**
   - 🔴 Critical (900+)
   - 🟠 High (800-899)
   - 🟡 Medium (700-799)
   - 🟢 Low (600-699)

7. **Confirm & Upload** to Supabase

### Auto-Generated Filename

The bot creates PROJ344-compliant filenames:
```
{date}_BerkeleyPD_{type}_{title}_Mic-850_Mac-900_LEG-920_REL-{score}.{ext}

Example:
20241106_BerkeleyPD_PLCR_Police_Report_Child_Safe_Mic-850_Mac-900_LEG-920_REL-920.jpg
```

---

## 🧪 How to Test the Bot

### Prerequisites

1. **Telegram Account**
2. **Bot Token from @BotFather**
3. **Supabase Credentials** (URL + anon key)
4. **Python 3.11+**

### Step 1: Get Bot Token

```
1. Open Telegram app
2. Search for: @BotFather
3. Send: /newbot
4. Name: ASEAGI Legal Assistant
5. Username: aseagi_legal_bot (or your choice)
6. Copy the token BotFather gives you
```

### Step 2: Prepare Environment

```bash
# Switch to telegram bot branch
cd /home/user/ASEAGI
git checkout merge-telegram-bot

# Create .env file
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=your_bot_token_here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
EOF

# Install dependencies (in a clean environment)
# Note: If you get cryptography errors, use a virtual environment:
python3 -m venv venv
source venv/bin/activate
pip install python-telegram-bot==20.7 supabase python-dotenv
```

### Step 3: Run the Bot

```bash
# Make sure you're in the ASEAGI directory
cd /home/user/ASEAGI
git checkout merge-telegram-bot

# Activate virtual environment if using one
source venv/bin/activate

# Set environment variables (if not in .env)
export TELEGRAM_BOT_TOKEN='your_token_here'
export SUPABASE_URL='your_supabase_url'
export SUPABASE_KEY='your_supabase_key'

# Run the bot
python3 telegram_document_bot.py

# You should see:
# 🤖 Starting Telegram Document Bot...
# 📡 Supabase: ✅ Connected
# ✅ Bot is running! Press Ctrl+C to stop.
```

### Step 4: Test in Telegram

1. Open Telegram on your phone
2. Search for your bot username (e.g., @aseagi_legal_bot)
3. Send `/start`
4. Upload a photo or PDF
5. Follow the prompts to add metadata
6. Confirm upload
7. Check Supabase `legal_documents` table for the new entry

---

## 🔧 Troubleshooting

### Issue 1: `ModuleNotFoundError: No module named '_cffi_backend'`

**Cause:** System-level cryptography library conflict

**Solution:**
```bash
# Use a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install python-telegram-bot==20.7 supabase python-dotenv
python3 telegram_document_bot.py
```

### Issue 2: `TELEGRAM_BOT_TOKEN not set`

**Solution:**
```bash
# Option 1: Environment variable
export TELEGRAM_BOT_TOKEN='your_token_here'

# Option 2: .env file
echo "TELEGRAM_BOT_TOKEN=your_token_here" > .env

# Option 3: .streamlit/secrets.toml
mkdir -p .streamlit
cat > .streamlit/secrets.toml << EOF
TELEGRAM_BOT_TOKEN = "your_token_here"
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
EOF
```

### Issue 3: `Supabase not configured`

**Solution:**
```bash
# Set Supabase credentials
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-anon-key-here'

# Or add to .env file
echo "SUPABASE_URL=https://your-project.supabase.co" >> .env
echo "SUPABASE_KEY=your-anon-key-here" >> .env
```

### Issue 4: Bot doesn't respond in Telegram

**Check:**
1. Bot is running (check terminal output)
2. Bot token is correct
3. Bot username is correct when searching
4. No firewall blocking Telegram API

---

## 📊 Expected Database Schema

The bot uploads to Supabase `legal_documents` table with these fields:

```sql
{
  "original_filename": "20241106_BerkeleyPD_PLCR_...",
  "document_type": "PLCR",
  "document_title": "Police Report - Child was Safe",
  "relevancy_number": 920,
  "file_extension": "jpg",
  "notes": "This police report shows...",
  "created_at": "2025-11-10T12:00:00Z",
  "file_hash": "abc123...",
  "source": "telegram_bot",
  "uploaded_via": "phone"
}
```

---

## 🆚 Comparison: Two Bots Available

### Bot 1: `telegram_document_bot.py` (merge-telegram-bot branch) ⭐

**Features:**
- ✅ Full document upload from phone
- ✅ Interactive metadata collection
- ✅ Auto-generated PROJ344 filenames
- ✅ Direct Supabase upload
- ✅ File hash validation
- ✅ Self-contained (no API backend needed)

**Use Cases:**
- Upload documents from phone while in court
- Quick evidence capture with context
- Mobile-first document management

**Limitations:**
- ❌ No search/query commands
- ❌ No violation tracking
- ❌ No timeline viewing
- (These require FastAPI backend - see framework guide)

### Bot 2: `bot/test_bot.py` (framework-comparison branch)

**Features:**
- ✅ Mock data for testing
- ✅ Basic command testing
- ✅ No Supabase required

**Use Cases:**
- Test Telegram API connectivity
- Demo bot functionality
- Development/testing

**Limitations:**
- ❌ No document upload
- ❌ No real data
- ❌ Mock responses only

---

## 🎯 Recommended Testing Order

1. **First:** Test `bot/test_bot.py` to verify Telegram connectivity
   ```bash
   git checkout claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC
   pip install -r bot/requirements.txt
   export TELEGRAM_BOT_TOKEN='your_token'
   python3 bot/test_bot.py
   ```

2. **Second:** Test `telegram_document_bot.py` for real uploads
   ```bash
   git checkout merge-telegram-bot
   # Set up .env with Supabase credentials
   python3 telegram_document_bot.py
   ```

3. **Third:** Implement FastAPI backend for full functionality
   - See `docs/FRAMEWORK_DECISION_FOR_ASEAGI.md`
   - Add `/telegram/*` endpoints for search/violations/timeline

---

## 📈 Next Steps After Testing

Once the Telegram bot is working:

1. **Merge to main branch**
   ```bash
   git checkout main
   git merge merge-telegram-bot
   ```

2. **Add to docker-compose.yml**
   ```yaml
   telegram-bot:
     build: .
     command: python3 telegram_document_bot.py
     environment:
       - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
       - SUPABASE_URL=${SUPABASE_URL}
       - SUPABASE_KEY=${SUPABASE_KEY}
     restart: unless-stopped
   ```

3. **Deploy to Digital Ocean**
   - Run bot as a service
   - Always-on document ingestion
   - Mobile access from anywhere

4. **Add FastAPI backend** (optional but recommended)
   - Enable `/search`, `/violations`, `/timeline` commands
   - WebSocket for real-time updates
   - Query existing documents

---

## 🔐 Security Notes

### ⚠️ Never Commit:
- `.env` files
- Bot tokens
- Supabase keys
- API credentials

### ✅ Always:
- Use `.env.example` as template
- Add `.env` to `.gitignore`
- Use environment variables in production
- Rotate tokens if exposed

---

## 📞 Support

### If Bot Doesn't Work:

1. Check terminal output for errors
2. Verify bot token is correct
3. Test bot with @userinfobot in Telegram
4. Check Supabase credentials
5. Review this guide's troubleshooting section

### Getting Help:

- **Telegram Bot API Docs:** https://core.telegram.org/bots/api
- **python-telegram-bot Docs:** https://docs.python-telegram-bot.org/
- **Supabase Docs:** https://supabase.com/docs
- **ASEAGI Docs:** `docs/` directory in repo

---

## ✅ Test Checklist

Before considering bot "tested":

- [ ] Got bot token from @BotFather
- [ ] Set environment variables
- [ ] Installed dependencies
- [ ] Bot starts without errors
- [ ] `/start` command works in Telegram
- [ ] Can upload a photo
- [ ] Can select document type
- [ ] Can enter date
- [ ] Can add title and notes
- [ ] Can choose relevancy level
- [ ] Upload completes successfully
- [ ] Document appears in Supabase `legal_documents` table
- [ ] Filename follows PROJ344 format

---

**For Ashe. For Justice. For All Children.** 🛡️

*Last Updated: November 10, 2025*
