# Telegram Bot Quick Start Guide

## What Happened? Why Wasn't It Working?

The issue was: **Multiple bot instances were running at the same time.**

Telegram's API only allows ONE instance of a bot to receive messages. When you have multiple instances running:
- The first instance consumes the messages
- Other instances get a `Conflict` error
- Users see no response because messages go to the "zombie" instance

### The Error You Were Seeing:
```
telegram.error.Conflict: terminated by other getUpdates request;
make sure that only one bot instance is running
```

This happened because there were old bot processes running in the background from previous attempts.

---

## Solution: Use the New Startup Script

I've created `start_telegram_bot.py` which:
- ✅ Checks for existing bot instances
- ✅ Kills old instances automatically (with your permission)
- ✅ Verifies all credentials before starting
- ✅ Tests Telegram API connection
- ✅ Shows you the exact bot username to message
- ✅ Ensures only ONE instance runs

---

## How to Use Your Telegram Bot (Step by Step)

### 1. Start the Bot (NEW METHOD)

```bash
cd ASEAGI
python start_telegram_bot.py
```

The script will:
1. Check for existing bot instances (and offer to kill them)
2. Verify your credentials from `.streamlit/secrets.toml`
3. Test the Telegram API connection
4. Show you the bot username
5. Start the bot

Example output:
```
======================================================================
TELEGRAM BOT STARTUP - DIAGNOSTIC CHECK
======================================================================

✅ All credentials found in secrets.toml
   Bot Token: 8564713661:AAFYAw8Xo...KT8rjBAhKw

======================================================================
TESTING TELEGRAM API CONNECTION
======================================================================

✅ Bot connection successful!
   Bot Username: @ASIAGI_bot
   Bot Name: ASEAGI-Mobile
   Bot ID: 8564713661

======================================================================
STARTING TELEGRAM BOT
======================================================================

📱 Your bot is ready at: @ASIAGI_bot

To use the bot:
  1. Open Telegram on your phone
  2. Search for: @ASIAGI_bot
  3. Send: /start
  4. Upload a document or photo
```

### 2. Open Telegram on Your Phone

**IMPORTANT:** Your bot username is **@ASIAGI_bot** (not @ASEAGI_bot - missing the 'E')

1. Open Telegram app on your phone
2. Tap the search bar
3. Type: `@ASIAGI_bot`
4. Tap on your bot when it appears

### 3. Start a Conversation

Send this message to your bot:
```
/start
```

You should see a welcome message with instructions.

### 4. Upload a Document

You can send:
- 📸 Photos (from camera or gallery)
- 📄 PDF files
- 📎 Other document types

The bot will guide you through:
1. Select document type (PLCR, DECL, EVID, etc.)
2. Enter date (YYYYMMDD format)
3. Add title/description
4. Add notes and context
5. Select relevancy (Critical/High/Medium/Low)
6. Confirm upload

### 5. Verify Upload

After confirming, run this to check if it saved to database:

```bash
cd ASEAGI
python check_telegram_uploads.py
```

This shows all documents uploaded in the last hour.

---

## Troubleshooting

### Problem: Bot doesn't respond when I send a message

**Check #1: Are you messaging the correct bot?**
- Your bot username is: **@ASIAGI_bot**
- NOT @ASEAGI_bot (common mistake)

**Check #2: Is the bot actually running?**
```bash
# On Windows, check task manager for python.exe running telegram_document_bot.py
# Or restart with the startup script:
cd ASEAGI
python start_telegram_bot.py
```

**Check #3: Are there multiple instances running?**
The new `start_telegram_bot.py` script will automatically detect and kill old instances.

### Problem: "Conflict: terminated by other getUpdates request"

This means multiple bot instances are running. Solution:

```bash
# Use the new startup script - it handles this automatically
cd ASEAGI
python start_telegram_bot.py
```

When prompted "Do you want to kill existing instances?", type `y`

### Problem: Bot token not found

Make sure `.streamlit/secrets.toml` exists with:

```toml
# Supabase Configuration
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your_supabase_key_here"

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8564713661:AAFYAw8XofCb6SVE3VdJMxLnKKT8rjBAhKw"
```

### Problem: How do I stop the bot?

Press `Ctrl+C` in the terminal where the bot is running.

---

## Testing Tools

### Check Bot Connection
```bash
cd ASEAGI
python test_telegram_connection.py
```

Shows:
- Bot username
- Bot status
- Pending messages

### Check Recent Uploads
```bash
cd ASEAGI
python check_telegram_uploads.py
```

Shows:
- Documents uploaded in last hour
- Total documents in database
- Document metadata

---

## Bot Username Reminder

🚨 **IMPORTANT:** Your bot username is **@ASIAGI_bot** (missing the 'E')

If you want a different username (like @ASEAGI_Mobile_Bot), you can:

1. Create a new bot with @BotFather on Telegram:
   - Send `/newbot` to @BotFather
   - Choose a name: "ASEAGI Mobile"
   - Choose a username: `aseagi_mobile_bot`

2. Update `.streamlit/secrets.toml` with the new token

3. Restart the bot with `python start_telegram_bot.py`

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python start_telegram_bot.py` | Start bot (recommended) |
| `python telegram_document_bot.py` | Start bot (old method) |
| `python test_telegram_connection.py` | Test bot connectivity |
| `python check_telegram_uploads.py` | Verify recent uploads |
| `Ctrl+C` | Stop the bot |

---

## Next Steps

1. ✅ Start the bot: `python start_telegram_bot.py`
2. ✅ Open Telegram on your phone
3. ✅ Search for: `@ASIAGI_bot`
4. ✅ Send: `/start`
5. ✅ Upload a test document
6. ✅ Verify it appears: `python check_telegram_uploads.py`
7. ✅ Check your dashboards at http://localhost:8501

---

## File Structure

```
ASEAGI/
├── telegram_document_bot.py          # Main bot code
├── start_telegram_bot.py             # New startup script (recommended)
├── test_telegram_connection.py       # Connection tester
├── check_telegram_uploads.py         # Upload verifier
├── TELEGRAM_BOT_SETUP.md            # Detailed setup guide
└── TELEGRAM_BOT_QUICK_START.md      # This file
```

---

**Ready to go!** Start the bot and try uploading a document from your phone! 📱→📊
