# 🤖 Global Project Monitoring Bot - Setup Guide

Monitor your entire tech stack from Telegram: GitHub, n8n, Qdrant, Twelve Labs.

---

## 🎯 What This Bot Does

**Real-time monitoring via Telegram for:**
- 📦 **GitHub** - Repos, commits, PRs, issues, workflow runs
- ⚙️ **n8n** - Workflow status, executions, failures
- 🗄️ **Qdrant** - Vector database collections, vector counts
- 🎥 **Twelve Labs** - Video AI indexes, processing tasks

---

## 🚀 Quick Setup

### Step 1: Create Monitoring Bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Name: `Project Monitor` (or your choice)
4. Username: `your_monitor_bot` (must end in 'bot')
5. **Save the token** BotFather gives you

### Step 2: Get API Keys

You need API keys/tokens for each service you want to monitor:

#### A. GitHub Token

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Name: `Monitoring Bot`
4. Select scopes:
   - `repo` (full control of private repositories)
   - `workflow` (update GitHub Action workflows)
5. Click **Generate token**
6. **Copy the token** (starts with `ghp_`)

#### B. n8n API Key

**If using n8n Cloud:**
1. Go to: https://app.n8n.cloud/settings
2. Click **API** tab
3. Generate new API key
4. **Copy** the key

**If self-hosted:**
1. Set in environment: `N8N_API_KEY_PREFIX=your-api-key`
2. Restart n8n
3. Use the key you set

#### C. Qdrant API Key (if using Qdrant Cloud)

1. Go to: https://cloud.qdrant.io
2. Select your cluster
3. Go to **Access** tab
4. **Copy API key**

**If self-hosted:** No API key needed (leave empty)

#### D. Twelve Labs API Key

1. Go to: https://dashboard.twelvelabs.io
2. Click your profile → **API Key**
3. **Copy** your API key

### Step 3: Configure Credentials

**Option A: Environment Variables**

```bash
# Telegram Bot
export TELEGRAM_MONITORING_BOT_TOKEN='your-bot-token-from-botfather'

# GitHub
export GITHUB_TOKEN='ghp_your-github-token'
export GITHUB_REPO='dondada876/ASEAGI'  # your repo

# n8n
export N8N_API_URL='https://your-n8n-instance.com/api/v1'
export N8N_API_KEY='your-n8n-api-key'

# Qdrant
export QDRANT_URL='https://your-cluster.qdrant.io'
export QDRANT_API_KEY='your-qdrant-api-key'

# Twelve Labs
export TWELVE_LABS_API_KEY='your-twelve-labs-key'
```

**Option B: Add to `.streamlit/secrets.toml`**

```toml
# Telegram Bot
TELEGRAM_MONITORING_BOT_TOKEN = "your-bot-token"

# GitHub
GITHUB_TOKEN = "ghp_your-token"
GITHUB_REPO = "dondada876/ASEAGI"

# n8n
N8N_API_URL = "https://your-n8n-instance.com/api/v1"
N8N_API_KEY = "your-n8n-api-key"

# Qdrant
QDRANT_URL = "https://your-cluster.qdrant.io"
QDRANT_API_KEY = "your-qdrant-api-key"

# Twelve Labs
TWELVE_LABS_API_KEY = "your-twelve-labs-key"
```

### Step 4: Install Dependencies

```bash
pip install python-telegram-bot requests PyGithub
```

### Step 5: Run the Bot

```bash
python3 telegram_monitoring_bot.py
```

You should see:
```
🤖 Starting Global Monitoring Bot...
📡 GitHub: ✅
⚙️ n8n: ✅
🗄️ Qdrant: ✅
🎥 Twelve Labs: ✅
✅ Bot is running! Press Ctrl+C to stop.
```

### Step 6: Test It!

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Click buttons to check status!

---

## 📱 How to Use

### Commands

- `/start` - Show main menu with buttons
- `/status` - Get complete system status
- `/github` - GitHub repository status
- `/n8n` - n8n workflows status
- `/qdrant` - Qdrant database status
- `/twelve` - Twelve Labs video AI status
- `/commits` - Recent GitHub commits (last 10)
- `/prs` - Open pull requests
- `/help` - Show help message

### Button Menu

The `/start` command shows a menu with quick access buttons:

```
📊 Full Status | 🔄 GitHub
⚙️ n8n        | 🗄️ Qdrant
🎥 Twelve Labs | 📝 Recent Commits
```

---

## 📊 What You'll See

### GitHub Status

```
📦 GitHub: dondada876/ASEAGI

⭐ Stars: 12
👀 Watchers: 3
🍴 Forks: 2
🐛 Open Issues: 5
🔀 Open PRs: 2
📝 Recent Commits (24h): 8

Latest Commit:
• Add monitoring bot for global system
• By: Don Bucknor
• Date: 2025-11-06T19:00:00Z
```

### n8n Status

```
⚙️ n8n Workflows

📊 Total Workflows: 12
✅ Active: 8
🔄 Recent Executions: 45
❌ Failed: 2

Active Workflows:
• ✅ Telegram Document Processing
• ✅ Notification Sender
• ⏸️ Google Drive Backup

Recent Failures:
• Document Processing
  Error: Connection timeout to S3...
```

### Qdrant Status

```
🗄️ Qdrant Vector Database

📦 Collections: 3
🔢 Total Vectors: 15,432

Collections:
• legal_documents
  Vectors: 8,234
  Status: green
• case_evidence
  Vectors: 5,198
  Status: green
```

### Twelve Labs Status

```
🎥 Twelve Labs Video AI

📚 Indexes: 2

Video Indexes:
• Legal Case Videos
  Videos: 15
  Duration: 3600s
• Evidence Footage
  Videos: 8
  Duration: 1200s

Recent Tasks:
• ✅ indexing - ready
• ⏳ indexing - processing
```

---

## 🔔 Automated Alerts (Optional)

You can set up automated alerts for important events:

### Add to your crontab:

```bash
# Check every 5 minutes and send alert if issues found
*/5 * * * * python3 /path/to/check_and_alert.py
```

### Create `check_and_alert.py`:

```python
import asyncio
from telegram import Bot

async def check_and_alert():
    # Check n8n for failures
    # Check GitHub for new issues
    # Send alert if problems found
    pass

asyncio.run(check_and_alert())
```

---

## 🔧 Advanced Configuration

### Custom GitHub Repo

Monitor a different repo:

```bash
export GITHUB_REPO='username/other-repo'
```

Or in bot code, change the default:
```python
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'dondada876/OTHER_REPO')
```

### Multiple Repos

Modify the bot to accept repo as parameter:

```python
@app.command()
async def github_status(repo: str = 'dondada876/ASEAGI'):
    status = await get_github_status(repo)
    # ...
```

### n8n Self-Hosted

If self-hosting n8n:

```bash
export N8N_API_URL='http://localhost:5678/api/v1'
export N8N_API_KEY='your-api-key'
```

---

## 🐛 Troubleshooting

### Bot doesn't respond
- Check bot token is correct
- Verify bot is running
- Check logs for errors

### "GitHub token not configured"
- Verify `GITHUB_TOKEN` environment variable is set
- Check token has correct permissions
- Token might be expired - regenerate

### "n8n Error: Connection refused"
- Check `N8N_API_URL` is correct
- Verify n8n is running
- Check API key is valid

### "Qdrant Error: Unauthorized"
- Check `QDRANT_API_KEY` is set
- Verify cluster URL is correct
- Check API key permissions

### "Twelve Labs Error: Invalid key"
- Check `TWELVE_LABS_API_KEY` is correct
- Verify account is active
- Check API quota not exceeded

---

## 🔒 Security Best Practices

1. **Never commit tokens** to GitHub
2. **Use environment variables** or secrets.toml
3. **Rotate keys regularly** (monthly)
4. **Limit API key permissions** to what's needed
5. **Keep bot private** - don't share username publicly
6. **Monitor bot usage** - check logs for suspicious activity
7. **Use service accounts** where possible

---

## 📈 Monitoring Dashboard (Bonus)

Want a web dashboard too? Create `monitoring_dashboard.py`:

```python
import streamlit as st
import asyncio

st.title("🤖 Global System Monitor")

if st.button("Check All Systems"):
    # Call monitoring functions
    github_status = asyncio.run(get_github_status())
    st.json(github_status)
```

Run with:
```bash
streamlit run monitoring_dashboard.py
```

---

## 🔄 Running as Service

### Linux (systemd)

Create `/etc/systemd/system/monitoring-bot.service`:

```ini
[Unit]
Description=Global Monitoring Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/user/ASEAGI
EnvironmentFile=/home/user/ASEAGI/.env
ExecStart=/usr/bin/python3 telegram_monitoring_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable monitoring-bot
sudo systemctl start monitoring-bot
```

Check status:
```bash
sudo systemctl status monitoring-bot
```

View logs:
```bash
sudo journalctl -u monitoring-bot -f
```

---

## 📚 API Documentation

- **GitHub API:** https://docs.github.com/en/rest
- **n8n API:** https://docs.n8n.io/api/
- **Qdrant API:** https://qdrant.tech/documentation/
- **Twelve Labs API:** https://docs.twelvelabs.io/

---

## ✅ Success Checklist

Before going live:

- [ ] Monitoring bot created in @BotFather
- [ ] All API keys collected
- [ ] Credentials configured (env vars or secrets.toml)
- [ ] Dependencies installed
- [ ] Bot tested with `/start`
- [ ] Each service responds correctly
- [ ] Bot set up as service (optional)
- [ ] Automated alerts configured (optional)

---

## 🎉 You're Done!

Your global monitoring system is live! You can now check your entire tech stack from Telegram.

**Pro Tips:**
- Set up a group for team notifications
- Schedule regular status checks
- Create custom alerts for critical events
- Use buttons for quick access

---

## 🆘 Need Help?

Common issues:
1. **Token errors** → Double-check token format
2. **Connection errors** → Verify URLs and network
3. **Permission errors** → Check API key scopes
4. **Bot offline** → Check systemd service status

**Happy Monitoring! 📊🚀**
