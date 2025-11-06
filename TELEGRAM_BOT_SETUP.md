# 📱 Telegram Document Bot Setup Guide

Upload documents from your phone to your Supabase legal documents database with automatic metadata collection.

---

## 🎯 What This Bot Does

- **📸 Scan documents** from your phone camera
- **📝 Collect metadata** through conversational forms
- **⚡ Upload instantly** to your Supabase database
- **🏷️ Auto-categorize** with relevancy scores
- **💬 Add context** with notes about each document

---

## 📋 Prerequisites

- Python 3.8+
- Telegram account
- Supabase account (already configured)
- Server or computer to run the bot (can be your local machine)

---

## 🚀 Quick Start

### Step 1: Create Your Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` to BotFather
3. Follow the prompts:
   - **Bot name:** "Legal Document Uploader" (or your choice)
   - **Username:** `your_legal_docs_bot` (must end in 'bot')
4. **Save the token** BotFather gives you (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Configure Credentials

#### Option A: Environment Variables (Recommended)

```bash
export TELEGRAM_BOT_TOKEN='your-telegram-bot-token-here'
export SUPABASE_URL='https://jvjlhxodmbkodzmggwpu.supabase.co'
export SUPABASE_KEY='your-supabase-anon-key'
```

#### Option B: Add to `.streamlit/secrets.toml`

```toml
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"

# Supabase (already configured)
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your-anon-key-here"
```

### Step 3: Install Dependencies

```bash
cd /home/user/ASEAGI
pip3 install python-telegram-bot supabase toml
```

### Step 4: Run the Bot

```bash
python3 telegram_document_bot.py
```

You should see:
```
🤖 Starting Telegram Document Bot...
📡 Supabase: ✅ Connected
✅ Bot is running! Press Ctrl+C to stop.
```

### Step 5: Start Using the Bot

1. **Open Telegram** on your phone
2. **Search** for your bot by username (e.g., `@your_legal_docs_bot`)
3. **Send** `/start` to begin
4. **Follow the prompts** to upload a document!

---

## 📱 How to Use

### Upload Flow:

1. **Send `/start`** - Bot greets you
2. **Send a photo or PDF** - Take a photo or upload a file
3. **Select document type** - Choose from:
   - 🚔 Police Report
   - 📄 Declaration
   - 📸 Evidence/Photo
   - 👶 CPS Report
   - 📋 Response
   - 🔬 Forensic Report
   - ⚖️ Court Order
   - 📑 Motion
   - 🎤 Hearing Transcript
   - 📎 Other

4. **Enter date** - Format: YYYYMMDD (e.g., `20240804`)
5. **Add title** - Brief description (e.g., "Police Report - Child was Safe")
6. **Add notes** - Context and why it's important
7. **Select relevancy** - How critical is this document?
   - 🔴 Critical (900+)
   - 🟠 High (800-899)
   - 🟡 Medium (700-799)
   - 🟢 Low (600-699)

8. **Confirm** - Type `YES` to upload
9. **Done!** - Document is in your database

---

## 🔧 Running as a Background Service (Linux)

To keep the bot running 24/7:

### Create systemd service:

```bash
sudo nano /etc/systemd/system/telegram-doc-bot.service
```

Add this content:

```ini
[Unit]
Description=Telegram Document Ingestion Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/user/ASEAGI
Environment="TELEGRAM_BOT_TOKEN=your-token"
Environment="SUPABASE_URL=your-url"
Environment="SUPABASE_KEY=your-key"
ExecStart=/usr/bin/python3 /home/user/ASEAGI/telegram_document_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-doc-bot
sudo systemctl start telegram-doc-bot
```

### Check status:

```bash
sudo systemctl status telegram-doc-bot
```

### View logs:

```bash
sudo journalctl -u telegram-doc-bot -f
```

---

## 🎨 Document Types Reference

| Code | Description | Use For |
|------|-------------|---------|
| `PLCR` | Police Report | Official police reports |
| `DECL` | Declaration | Sworn declarations |
| `EVID` | Evidence/Photo | Photos, screenshots, evidence |
| `CPSR` | CPS Report | Child Protective Services reports |
| `RESP` | Response | Responses to motions/orders |
| `FORN` | Forensic Report | Forensic analysis, expert reports |
| `ORDR` | Court Order | Judge's orders |
| `MOTN` | Motion | Legal motions filed |
| `HEAR` | Hearing Transcript | Court hearing transcripts |
| `OTHR` | Other | Miscellaneous documents |

---

## ⭐ Relevancy Scoring Guide

**🔴 Critical (900+):**
- Evidence that proves your case
- Documents showing false statements
- Key police reports (like August 10, 2024)
- Court orders affecting custody

**🟠 High (800-899):**
- Important evidence
- CPS reports
- Declarations with crucial information
- Timeline-critical documents

**🟡 Medium (700-799):**
- Supporting evidence
- Standard filings
- Background documents
- Context-providing materials

**🟢 Low (600-699):**
- General reference
- Routine correspondence
- Administrative documents

---

## 🔒 Security & Privacy

- ✅ Bot runs on **your server** (not a third party)
- ✅ Documents go **directly to your Supabase**
- ✅ No data stored by Telegram permanently
- ✅ Bot token is private to you
- ⚠️ Keep your bot token secure - it's like a password
- ⚠️ Only share your bot username with trusted people

---

## 🐛 Troubleshooting

### Bot doesn't respond:
1. Check bot is running: `ps aux | grep telegram_document_bot`
2. Check logs: `tail -f ~/telegram_bot.log`
3. Verify token is correct

### Can't upload to Supabase:
1. Check Supabase credentials
2. Verify internet connection
3. Check Supabase dashboard for errors

### Bot stops working:
1. Restart: `sudo systemctl restart telegram-doc-bot`
2. Check logs: `sudo journalctl -u telegram-doc-bot -n 50`

---

## 💡 Tips & Best Practices

1. **Take clear photos** - Make sure text is readable
2. **Add detailed notes** - Future you will thank you
3. **Use correct date** - Use the document's date, not today
4. **Be consistent** - Use similar formatting for titles
5. **Upload immediately** - Don't wait - upload while context is fresh
6. **Review in dashboard** - Check uploaded docs in Streamlit dashboards

---

## 📊 Viewing Your Documents

After uploading, view your documents in:

1. **Count Police Reports:**
   ```bash
   python3 count_police_reports.py
   ```

2. **Timeline Dashboard:**
   ```bash
   streamlit run timeline_constitutional_violations.py
   ```

3. **Master Dashboard:**
   ```bash
   streamlit run proj344_master_dashboard.py
   ```

---

## 🔗 Related Files

- `telegram_document_bot.py` - Main bot script
- `.streamlit/secrets.toml` - Configuration file
- `count_police_reports.py` - Query uploaded documents
- `timeline_constitutional_violations.py` - View timeline

---

## 📞 Getting Help

If you need help:
1. Check this guide first
2. Review error messages carefully
3. Check Telegram BotFather documentation
4. Verify Supabase connection

---

## ✅ Next Steps

1. ✅ Set up bot with BotFather
2. ✅ Configure credentials
3. ✅ Run the bot
4. ✅ Upload a test document
5. ✅ Check it appears in your database
6. ✅ Set up as background service (optional)

---

**Your documents are now just a photo away from being properly cataloged! 📱→📊**
