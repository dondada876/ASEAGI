# Telegram Bot Troubleshooting Guide

## Issue: Bot Not Responding to Messages

### Root Cause Discovered
Your bot has a **typo in the username**: It's **@ASIAGI_bot** (missing the 'E' from ASEAGI)

### Checklist to Fix

1. **Verify Bot Username**
   ```bash
   cd ASEAGI
   python test_telegram_connection.py
   ```

   Look for the line: `Bot Username: @ASIAGI_bot`

   **This is the exact username you must message.**

2. **On Your Phone - Open Telegram**
   - Tap the search icon
   - Type EXACTLY: `@ASIAGI_bot`
   - **NOT** @ASEAGI_bot
   - **NOT** @ASEAGI-Mobile
   - Must be: **@ASIAGI_bot**

3. **Start Conversation**
   - Tap on @ASIAGI_bot when it appears in search
   - Send: `/start`
   - Bot should respond with a welcome message

4. **Send Test Image**
   - Send any image or document
   - Bot will guide you through the upload process

5. **Verify Upload**
   ```bash
   cd ASEAGI
   python check_telegram_uploads.py
   ```

   You should see your document in the list.

---

## Common Issues

### Issue: "I'm messaging the bot but no response"

**Solution A: Wrong Bot Username**
- You might be messaging @ASEAGI_bot (with E)
- Correct username is @ASIAGI_bot (without E)
- Search again and make sure it's spelled correctly

**Solution B: Haven't sent /start**
- Telegram bots require `/start` to initialize
- Send `/start` first, then try your image

**Solution C: Multiple Bot Instances Running**
```bash
cd ASEAGI
python -c "
import psutil
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = proc.info.get('cmdline', [])
        if cmdline and 'telegram_document_bot.py' in ' '.join(cmdline):
            print(f'Found bot: PID {proc.info[\"pid\"]}')
    except:
        pass
"
```

If you see multiple PIDs, kill them all:
```bash
python -c "
import psutil
for proc in psutil.process_iter():
    try:
        if 'telegram_document_bot.py' in ' '.join(proc.cmdline()):
            proc.kill()
    except:
        pass
"
```

### Issue: "Bot was working, now it's not"

**Solution: Restart Bot**
```bash
# Kill any existing instances
python -c "import psutil; [p.kill() for p in psutil.process_iter() if 'telegram_document_bot.py' in ' '.join(p.cmdline() or [])]"

# Start fresh
cd ASEAGI
python telegram_document_bot.py
```

---

## How to Create New Bot with Preferred Username

If you want a different username (like @ASEAGI_Mobile_Bot):

1. **Open Telegram**, search for: `@BotFather`

2. **Send**: `/newbot`

3. **Bot Name**: Type `ASEAGI Mobile` (display name)

4. **Bot Username**: Type `aseagi_mobile_bot` (must end with 'bot')

5. **Copy Token**: BotFather will give you a token like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

6. **Update secrets.toml**:
   ```toml
   TELEGRAM_BOT_TOKEN = "your_new_token_here"
   ```

7. **Restart Bot**:
   ```bash
   cd ASEAGI
   python telegram_document_bot.py
   ```

---

## Diagnostic Commands

### Check if bot is reachable
```bash
cd ASEAGI
python test_telegram_connection.py
```

### Check for recent uploads
```bash
cd ASEAGI
python check_telegram_uploads.py
```

### Check Telegram API directly
```bash
cd ASEAGI
python -c "
import requests, toml
from pathlib import Path
secrets = toml.load(Path('.streamlit/secrets.toml'))
token = secrets.get('TELEGRAM_BOT_TOKEN')
url = f'https://api.telegram.org/bot{token}/getUpdates'
response = requests.get(url)
data = response.json()
print(f'Messages waiting: {len(data.get(\"result\", []))}')
"
```

### Find running bot processes
```bash
tasklist | findstr python
```

---

## Quick Fix: Start Fresh

If nothing works, start completely fresh:

```bash
cd ASEAGI

# 1. Kill all bot instances
python -c "import psutil; [p.kill() for p in psutil.process_iter() if 'telegram' in ' '.join(p.cmdline() or []).lower()]"

# 2. Test connection
python test_telegram_connection.py

# 3. Note the bot username shown (likely @ASIAGI_bot)

# 4. On phone: Search for that EXACT username in Telegram

# 5. Send /start to that bot

# 6. Start the bot
python telegram_document_bot.py

# 7. Send test image from phone

# 8. Verify upload
python check_telegram_uploads.py
```

---

## Still Not Working?

**Check these:**

1. **Bot Token Valid?**
   - Go to @BotFather on Telegram
   - Send `/mybots`
   - Select your bot
   - Check token is correct in secrets.toml

2. **Network/Firewall Issues?**
   - Can you access api.telegram.org?
   - Try: `curl https://api.telegram.org/`

3. **Wrong Bot?**
   - You might have created multiple bots with @BotFather
   - Check `/mybots` to see all your bots
   - Make sure you're using the right token

---

## Success Checklist

- [ ] Bot username verified: @ASIAGI_bot
- [ ] Searched for exact username in Telegram
- [ ] Sent `/start` command
- [ ] Bot responded with welcome message
- [ ] Sent test image
- [ ] Bot guided through upload process
- [ ] Confirmed upload in database with `check_telegram_uploads.py`

**Once all checked, you're good to go!** 🚀
