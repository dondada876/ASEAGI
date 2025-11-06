# 🚀 Deploy Telegram Bot - 5 Minute Setup

**Goal:** Get @aseagi_legal_bot responding to messages in 5 minutes

---

## ✅ What You Already Have

- ✅ Bot created (@aseagi_legal_bot)
- ✅ Bot token in .env file
- ✅ Supabase configured
- ✅ Code deployed to droplet
- ✅ Dashboards working

**Missing:** Bot service isn't running yet!

---

## 🚀 Quick Deployment (5 Minutes)

### Step 1: Connect to Droplet
```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
```

### Step 2: Pull Latest Code
```bash
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM
```

### Step 3: Verify .env Has Bot Token
```bash
# Check token exists (hides actual value for security)
cat .env | grep TELEGRAM_BOT_TOKEN | sed 's/=.*/=***HIDDEN***/'

# Should show:
# TELEGRAM_BOT_TOKEN=***HIDDEN***
```

**If token is missing:**
```bash
nano .env

# Add this line (get token from @BotFather with /token command):
TELEGRAM_BOT_TOKEN=paste-your-actual-token-here

# Save: Ctrl+X, Y, Enter
```

### Step 4: Deploy Bot Service
```bash
# Deploy bot + API (minimal setup)
docker-compose -f docker-compose.bot.yml up -d --build

# This will:
# - Build the API service
# - Build the Telegram bot service
# - Connect to your Supabase database
# - Start responding to messages
```

### Step 5: Watch It Start
```bash
# Watch the logs (wait ~30 seconds for startup)
docker-compose -f docker-compose.bot.yml logs -f

# Look for these success messages:
# ✅ "ASEAGI API Started Successfully"
# ✅ "Starting ASEAGI Telegram bot..."
# ✅ "Bot started successfully. Polling for updates..."

# Press Ctrl+C to stop watching logs
```

### Step 6: Test Your Bot! 🎉
1. Open **Telegram** app on your phone
2. Search for: **@aseagi_legal_bot**
3. Send: **/start**
4. **You should get a welcome message!** ✅

---

## 🧪 Test Commands

Once deployed, try these commands in Telegram:

```
/start       - Welcome message
/help        - List all commands
/timeline    - Recent case events
/actions     - Pending tasks
/violations  - Legal violations detected
/report      - Daily summary
```

---

## 🔍 Troubleshooting

### Problem: Bot doesn't respond

**Check logs:**
```bash
docker logs aseagi-telegram --tail 50
```

**Common errors:**

**Error:** "TELEGRAM_BOT_TOKEN must be set"
```bash
# Add token to .env file
nano .env
# Add: TELEGRAM_BOT_TOKEN=your-token-here
# Restart: docker-compose -f docker-compose.bot.yml restart
```

**Error:** "Unauthorized"
```bash
# Token is wrong - get new one from @BotFather
# Send: /token to @BotFather
# Update .env with new token
# Restart bot
```

**Error:** "Connection refused"
```bash
# API service not running
docker-compose -f docker-compose.bot.yml up -d api
# Wait 30 seconds, then restart bot
docker-compose -f docker-compose.bot.yml restart telegram
```

---

### Problem: Container keeps restarting

**Check what's wrong:**
```bash
# See exit reason
docker logs aseagi-telegram 2>&1 | tail -20

# Check API logs too
docker logs aseagi-api 2>&1 | tail -20
```

---

## ✅ Verify Deployment Success

**Check containers are running:**
```bash
docker ps | grep aseagi

# Should show:
# aseagi-api         Up X minutes   0.0.0.0:8000->8000/tcp
# aseagi-telegram    Up X minutes
```

**Test API directly:**
```bash
curl http://localhost:8000/health

# Should return:
# {"status":"healthy","service":"ASEAGI API",...}
```

**Test bot token:**
```bash
TOKEN=$(cat .env | grep TELEGRAM_BOT_TOKEN | cut -d'=' -f2)
curl "https://api.telegram.org/bot${TOKEN}/getMe"

# Should return:
# {"ok":true,"result":{"id":...,"first_name":"ASEAGI_Legal_Assistant",...}}
```

---

## 📊 What's Running After Deployment

### Before:
```
✅ proj344-master-dashboard (port 8501)
✅ legal-intelligence-dashboard (port 8502)
✅ ceo-dashboard (port 8503)
```

### After:
```
✅ proj344-master-dashboard (port 8501)
✅ legal-intelligence-dashboard (port 8502)
✅ ceo-dashboard (port 8503)
✅ aseagi-api (port 8000) ← NEW!
✅ aseagi-telegram ← NEW!
```

---

## 🔧 Management Commands

**View logs:**
```bash
# Bot logs
docker logs aseagi-telegram -f

# API logs
docker logs aseagi-api -f

# Both
docker-compose -f docker-compose.bot.yml logs -f
```

**Restart bot:**
```bash
docker-compose -f docker-compose.bot.yml restart telegram
```

**Restart everything:**
```bash
docker-compose -f docker-compose.bot.yml restart
```

**Stop bot:**
```bash
docker-compose -f docker-compose.bot.yml down
```

**Rebuild after code changes:**
```bash
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM
docker-compose -f docker-compose.bot.yml up -d --build
```

---

## 🎯 Expected Behavior

### In Telegram:
```
You: /start

@aseagi_legal_bot:
🛡️ ASEAGI Case Management System

Welcome! This bot provides access to your case data.

Available Commands:
/help - Show this message
/search <query> - Search communications
/timeline [days] - Case timeline
/actions - Pending action items
/violations - Detected violations
/deadline - Upcoming deadlines
/report - Daily summary

For Ashe. For Justice. For All Children. 🛡️
```

### In Terminal:
```bash
$ docker ps | grep aseagi
aseagi-telegram    Up 2 minutes
aseagi-api         Up 2 minutes    0.0.0.0:8000->8000/tcp

$ docker logs aseagi-telegram --tail 3
2025-11-06 15:30:45 - INFO - Starting ASEAGI Telegram bot...
2025-11-06 15:30:46 - INFO - Bot started successfully. Polling for updates...
```

---

## 🚀 Ready to Deploy?

**Just run these 4 commands on your droplet:**

```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM
docker-compose -f docker-compose.bot.yml up -d --build
```

**Then test in Telegram:**
1. Open Telegram app
2. Search: @aseagi_legal_bot
3. Send: /start
4. **Should get welcome message!** ✅

---

## 📞 Need Help?

**If bot doesn't respond after 2 minutes:**

Share this output:
```bash
# Container status
docker ps -a | grep aseagi

# Bot logs
docker logs aseagi-telegram --tail 30

# API logs
docker logs aseagi-api --tail 30
```

---

**For Ashe. For Justice. For All Children.** 🛡️

**Deployment time: ~5 minutes**
**Difficulty: Easy** ⭐⭐☆☆☆
