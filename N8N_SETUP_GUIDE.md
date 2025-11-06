# 🔧 n8n Setup Guide for ASEAGI
**Complete guide to setting up automation workflows**

---

## ✅ **Yes! n8n Works With API Tokens**

**Answer to your question:** You don't even need API tokens! n8n can call your FastAPI endpoints directly because they're on the same Docker network.

**Three ways n8n can access ASEAGI:**

1. **Internal Docker Network** (Recommended) ✅
   - URL: `http://api:8000/telegram/*`
   - No authentication needed (internal network)
   - Fastest and simplest

2. **External API** (If n8n is elsewhere)
   - URL: `http://137.184.1.91:8000/telegram/*`
   - Could add API key authentication later
   - Accessible from outside

3. **With API Keys** (Future enhancement)
   - Add API key to FastAPI
   - Pass in n8n HTTP headers
   - More secure for production

**For now: Use Option 1 (internal network) - it just works!**

---

## 🚀 **Access n8n**

### **URL:** `http://137.184.1.91:5678`

### **Login:**
- Username: `admin` (or what you set in .env)
- Password: (your `N8N_PASSWORD` from .env)

**To find your password:**
```bash
ssh root@137.184.1.91
cd /opt/ASEAGI
cat .env | grep N8N_PASSWORD
```

---

## 📋 **Pre-Made Workflows**

I've created 3 ready-to-use workflows for you in `/opt/ASEAGI/n8n-workflows/`:

### **1. Daily Report** 📊
**File:** `01-daily-report.json`
**Schedule:** Every day at 8:00 AM
**What it does:**
- Calls `GET /telegram/report`
- Gets daily summary (urgent actions, deadlines, hearings, violations)
- Sends Telegram notification
- Shows counts and highlights

### **2. Deadline Alerts** ⚠️
**File:** `02-deadline-alerts.json`
**Schedule:** Every day at 9:00 AM
**What it does:**
- Calls `GET /telegram/deadline`
- Checks for deadlines in next 7 days
- Only sends alert if deadlines exist
- Lists each deadline with priority

### **3. Critical Violation Monitor** 🚨
**File:** `03-violation-monitor.json`
**Schedule:** Every 4 hours
**What it does:**
- Calls `GET /telegram/violations?severity=critical`
- Monitors for critical legal violations
- Immediate alert if found
- Includes violation details

---

## 📥 **How to Import Workflows**

### **Method 1: Via n8n UI** (Recommended)

1. **Open n8n:** `http://137.184.1.91:5678`
2. **Login** with admin credentials
3. Click **"Workflows"** in left sidebar
4. Click **"Import from File"** button (top right)
5. Select workflow JSON file
6. Click **"Import"**
7. Repeat for each workflow

### **Method 2: Copy Files to n8n Container**

```bash
# Copy workflows to n8n container
docker cp /opt/ASEAGI/n8n-workflows/01-daily-report.json aseagi-n8n:/home/node/.n8n/

# Access n8n UI and import from there
```

---

## ⚙️ **Configure Each Workflow**

After importing, you need to configure:

### **Step 1: Get Your Telegram User ID**

1. Open Telegram
2. Message: `@userinfobot`
3. It will reply with your user ID (e.g., `123456789`)
4. **Copy this number!**

### **Step 2: Set Up Telegram Credentials in n8n**

1. In n8n, go to **Settings** → **Credentials**
2. Click **"Create New"**
3. Select **"Telegram"**
4. Name it: `ASEAGI Telegram Bot`
5. Paste your **Telegram Bot Token** (same one from .env)
6. Click **"Save"**

### **Step 3: Update Each Workflow**

For **each imported workflow:**

1. Click on the workflow to open it
2. Find the **"Send Telegram Alert"** node
3. Click on it
4. Change `"YOUR_TELEGRAM_USER_ID"` to your actual user ID
5. Select the Telegram credential you just created
6. Click **"Save"**
7. Click **"Activate"** toggle (top right)

---

## 🧪 **Test Workflows**

### **Test Daily Report:**

1. Open `01-daily-report` workflow
2. Click **"Execute Workflow"** button (bottom)
3. Check if you receive Telegram message
4. If successful: Activate the workflow!

### **Test Deadline Alerts:**

1. Open `02-deadline-alerts` workflow
2. Click **"Execute Workflow"**
3. Should alert if deadlines exist
4. If successful: Activate!

### **Test Violation Monitor:**

1. Open `03-violation-monitor` workflow
2. Click **"Execute Workflow"**
3. Should alert if critical violations exist
4. If successful: Activate!

---

## 📊 **Understanding the Workflows**

### **Workflow Structure:**

```
Trigger Node → HTTP Request → If Condition → Action Node
     ↓              ↓              ↓              ↓
  Schedule      Call API      Check Data    Send Alert
```

### **Example: Daily Report Workflow**

```
┌─────────────────┐
│ Trigger:        │
│ Every day 8 AM  │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ HTTP Request:   │
│ GET /report     │
└────────┬────────┘
         │
         v
┌─────────────────┐
│ If: Success?    │
└───┬─────────┬───┘
    │         │
   Yes       No
    │         │
    v         v
┌────────┐ ┌────────┐
│ Send   │ │ Log    │
│ Alert  │ │ Error  │
└────────┘ └────────┘
```

---

## 🎨 **Creating Custom Workflows**

### **Example: Weekly Summary**

Create a workflow that runs every Friday:

1. **Trigger:** Schedule Trigger
   - Cron: `0 17 * * 5` (5 PM every Friday)

2. **HTTP Request:**
   - Method: `GET`
   - URL: `http://api:8000/telegram/timeline?days=7`

3. **HTTP Request 2:**
   - Method: `GET`
   - URL: `http://api:8000/telegram/actions`

4. **Function Node:**
   - Combine both responses

5. **Telegram Node:**
   - Send formatted summary

---

## 🔌 **All Available API Endpoints for n8n**

You can call ANY of these from n8n:

### **GET Endpoints:**

```
GET http://api:8000/telegram/timeline?days=30
GET http://api:8000/telegram/actions?priority=urgent
GET http://api:8000/telegram/violations?severity=critical
GET http://api:8000/telegram/deadline
GET http://api:8000/telegram/report
GET http://api:8000/telegram/hearing?hearing_id=123
GET http://api:8000/telegram/hearing?days=30
GET http://api:8000/health
```

### **POST Endpoints:**

```
POST http://api:8000/telegram/search
Body: {"query": "Cal OES 2-925", "limit": 10}

POST http://api:8000/telegram/motion?motion_type=reconsideration&issue=issue_here
```

---

## 💡 **Workflow Ideas**

### **1. Morning Briefing** ☀️
**Time:** 7:00 AM
**Calls:**
- `/telegram/deadline` (urgent deadlines)
- `/telegram/actions?priority=urgent` (urgent tasks)
- `/telegram/violations?severity=critical` (critical issues)
**Sends:** Combined morning briefing

### **2. Evening Summary** 🌙
**Time:** 6:00 PM
**Calls:**
- `/telegram/timeline?days=1` (today's events)
- `/telegram/actions` (completed/pending tasks)
**Sends:** End-of-day summary

### **3. Pre-Hearing Reminder** 📅
**Time:** 1 day before hearing
**Calls:**
- `/telegram/hearing?hearing_id=X` (hearing details)
- `/telegram/violations` (issues to raise)
- `/telegram/search` (relevant communications)
**Sends:** Hearing prep checklist

### **4. Document Analysis Alert** 📄
**Trigger:** Webhook when new document uploaded
**Calls:**
- `/telegram/search?query=new_doc_keywords` (related content)
- `/telegram/violations` (check for new violations)
**Sends:** Analysis results

### **5. Weekly Report** 📊
**Time:** Friday 5 PM
**Calls:**
- `/telegram/timeline?days=7` (week's events)
- `/telegram/actions` (week's tasks)
- `/telegram/violations` (week's findings)
**Sends:** Comprehensive weekly summary

---

## 🔧 **Advanced: API Authentication (Future)**

If you want to add API key authentication later:

### **Step 1: Add to FastAPI**

Update `api-service/main.py`:

```python
from fastapi import Header, HTTPException

API_KEY = os.environ.get("API_KEY", "your-secure-api-key")

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/telegram/"):
        api_key = request.headers.get("X-API-Key")
        if api_key != API_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API key"}
            )
    response = await call_next(request)
    return response
```

### **Step 2: Configure in n8n**

In HTTP Request node:
- Go to "Headers"
- Add header: `X-API-Key: your-secure-api-key`

---

## 📊 **Monitoring n8n Workflows**

### **Check Execution History:**

1. Go to **"Executions"** in n8n sidebar
2. See all workflow runs
3. Click any execution to see details
4. Check for errors

### **View Logs:**

```bash
# Check n8n logs
docker logs aseagi-n8n

# Follow logs in real-time
docker logs -f aseagi-n8n
```

---

## 🚨 **Troubleshooting**

### **Problem: Workflow doesn't trigger**

**Check:**
1. Is workflow activated? (toggle in top right)
2. Is n8n container running? `docker ps | grep n8n`
3. Check schedule/trigger configuration

**Fix:**
```bash
# Restart n8n
docker-compose -f docker-compose.full.yml restart n8n
```

---

### **Problem: HTTP Request fails**

**Error:** "ECONNREFUSED" or "Cannot connect"

**Check:**
1. Is API container running? `docker ps | grep api`
2. Is URL correct? `http://api:8000` (NOT `http://localhost:8000`)
3. Is API healthy? `curl http://137.184.1.91:8000/health`

**Fix:**
```bash
# Check API logs
docker logs aseagi-api

# Restart API
docker-compose -f docker-compose.full.yml restart api
```

---

### **Problem: Telegram node fails**

**Error:** "Unauthorized" or "Invalid token"

**Check:**
1. Is bot token correct in n8n credentials?
2. Is bot token same as in .env?
3. Is chat ID correct?

**Fix:**
1. Verify token: `cat .env | grep TELEGRAM_BOT_TOKEN`
2. Get your user ID from @userinfobot
3. Update workflow with correct user ID

---

## ✅ **Workflow Activation Checklist**

Before activating workflows:

- [ ] n8n is accessible at `http://137.184.1.91:5678`
- [ ] Logged into n8n with admin credentials
- [ ] Telegram credentials configured in n8n
- [ ] Got my Telegram user ID from @userinfobot
- [ ] Imported all 3 workflows
- [ ] Updated each workflow with my user ID
- [ ] Tested each workflow manually
- [ ] All tests successful
- [ ] Activated workflows

---

## 🎯 **Quick Start Commands**

```bash
# Copy workflows to droplet (from your Mac)
scp -r /local/path/to/n8n-workflows root@137.184.1.91:/opt/ASEAGI/

# Or pull from git (on droplet)
cd /opt/ASEAGI
git pull origin claude/create-truth-score-charts-011CUqV28kW1jcpJE1z2B5rM

# Check workflows directory
ls -la n8n-workflows/

# Access n8n
# Open browser: http://137.184.1.91:5678

# Check n8n is running
docker ps | grep n8n

# View n8n logs
docker logs -f aseagi-n8n
```

---

## 📚 **Resources**

### **n8n Documentation:**
- Main docs: https://docs.n8n.io/
- Workflow templates: https://n8n.io/workflows/
- HTTP Request node: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/

### **ASEAGI API Documentation:**
- Swagger UI: `http://137.184.1.91:8000/docs`
- ReDoc: `http://137.184.1.91:8000/redoc`

---

## 🎬 **Next Steps**

1. ✅ Deploy full stack (if not done)
2. ✅ Access n8n at `http://137.184.1.91:5678`
3. ✅ Import 3 pre-made workflows
4. ✅ Configure Telegram credentials
5. ✅ Update workflows with your user ID
6. ✅ Test each workflow
7. ✅ Activate workflows
8. ✅ Monitor execution history
9. ✅ Create custom workflows as needed

---

**For Ashe. For Justice. For All Children.** 🛡️
