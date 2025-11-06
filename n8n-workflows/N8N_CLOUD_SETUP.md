# 🤖 n8n Cloud Setup for ASEAGI

**Time:** 20 minutes
**Goal:** Automate Telegram notifications for case updates

---

## 📋 What These Workflows Do

### 1. **Daily Report** (8 AM every day)
- Calls `/telegram/report` API
- Sends summary to your Telegram
- Shows: urgent actions, deadlines, hearings, violations

### 2. **Deadline Alerts** (9 AM every day)
- Calls `/telegram/deadline` API
- Alerts if deadlines coming up
- Only sends if there are deadlines

### 3. **Violation Monitor** (Every 4 hours)
- Calls `/telegram/violations?severity=critical`
- Immediate alerts for critical violations
- Runs 6 times per day

---

## ⚠️ IMPORTANT: Workflows Need Modification

The workflows in this folder call `http://api:8000` which only works **inside Docker**.

For **n8n Cloud**, you need to call `http://137.184.1.91:8000` (your public IP).

I've created modified versions below that work with n8n Cloud.

---

## 🚀 Setup Steps

### Step 1: Get Your Telegram Chat ID (2 minutes)

1. Open Telegram
2. Search for: **@userinfobot**
3. Send: `/start`
4. Bot will reply with your **Chat ID** (looks like: `123456789`)
5. **Copy this number** - you'll need it!

---

### Step 2: Create n8n Cloud Account (3 minutes)

1. Go to: https://n8n.io/cloud
2. Click **"Start free"**
3. Sign up (free tier includes 5,000 executions/month)
4. Verify email
5. Log in to: https://app.n8n.cloud/

---

### Step 3: Add Telegram Credentials (5 minutes)

1. In n8n Cloud, click **Settings** (bottom left)
2. Click **Credentials**
3. Click **+ Add Credential**
4. Search for: **Telegram**
5. Click **Telegram API**
6. Enter:
   - **Access Token**: `8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI`
   - **Name**: `ASEAGI Bot`
7. Click **Save**

---

### Step 4: Import Workflows (10 minutes)

#### Workflow 1: Daily Report

1. Click **+ Add Workflow** (top right)
2. Click the **three dots menu** → **Import from URL**
3. Paste this workflow JSON (see below)
4. **IMPORTANT**: Replace `YOUR_CHAT_ID_HERE` with your actual Chat ID from Step 1
5. Click **Save** (top right)
6. Toggle **Active** (top right)

#### Workflow 2: Deadline Alerts

1. Repeat above steps with Workflow 2 JSON
2. Replace Chat ID
3. Save and activate

#### Workflow 3: Violation Monitor

1. Repeat above steps with Workflow 3 JSON
2. Replace Chat ID
3. Save and activate

---

## 📝 Modified Workflows (n8n Cloud Compatible)

### Workflow 1: Daily Report (8 AM)

Copy this entire JSON and import:

```json
{
  "name": "ASEAGI Daily Report",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 8 * * *"}]
        }
      },
      "name": "Every Day at 8 AM",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://137.184.1.91:8000/telegram/report",
        "options": {}
      },
      "name": "Get Daily Report from API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "boolean": [{"value1": "={{$json.success}}", "value2": true}]
        }
      },
      "name": "Check if Success",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "chatId": "YOUR_CHAT_ID_HERE",
        "text": "=📊 **ASEAGI Daily Report - {{$json.data.date}}**\n\n🚨 **Urgent Actions:** {{$json.data.urgent_actions.length}}\n⚠️ **Upcoming Deadlines:** {{$json.data.upcoming_deadlines.length}}\n📅 **Upcoming Hearings:** {{$json.data.upcoming_hearings.length}}\n⚖️ **Recent Violations:** {{$json.data.recent_violations.length}}\n\nUse /report in @aseagi_legal_bot for full details.",
        "additionalFields": {"parse_mode": "Markdown"}
      },
      "name": "Send to Telegram",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1.2,
      "position": [850, 250],
      "credentials": {"telegramApi": "ASEAGI Bot"}
    }
  ],
  "connections": {
    "Every Day at 8 AM": {"main": [[{"node": "Get Daily Report from API", "type": "main", "index": 0}]]},
    "Get Daily Report from API": {"main": [[{"node": "Check if Success", "type": "main", "index": 0}]]},
    "Check if Success": {"main": [[{"node": "Send to Telegram", "type": "main", "index": 0}]]}
  }
}
```

**Remember to replace `YOUR_CHAT_ID_HERE` with your actual Telegram Chat ID!**

---

### Workflow 2: Deadline Alerts (9 AM)

```json
{
  "name": "ASEAGI Deadline Alerts",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 9 * * *"}]
        }
      },
      "name": "Every Day at 9 AM",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://137.184.1.91:8000/telegram/deadline",
        "options": {}
      },
      "name": "Get Upcoming Deadlines",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [{"value1": "={{$json.data.count}}", "operation": "larger", "value2": 0}]
        }
      },
      "name": "Has Deadlines",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "chatId": "YOUR_CHAT_ID_HERE",
        "text": "=⚠️ **DEADLINE ALERT**\n\nYou have {{$json.data.count}} deadlines in the next 7 days!\n\nUse /deadline in @aseagi_legal_bot for details.",
        "additionalFields": {"parse_mode": "Markdown"}
      },
      "name": "Send Alert",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1.2,
      "position": [850, 250],
      "credentials": {"telegramApi": "ASEAGI Bot"}
    }
  ],
  "connections": {
    "Every Day at 9 AM": {"main": [[{"node": "Get Upcoming Deadlines", "type": "main", "index": 0}]]},
    "Get Upcoming Deadlines": {"main": [[{"node": "Has Deadlines", "type": "main", "index": 0}]]},
    "Has Deadlines": {"main": [[{"node": "Send Alert", "type": "main", "index": 0}]]}
  }
}
```

---

### Workflow 3: Critical Violation Monitor (Every 4 hours)

```json
{
  "name": "ASEAGI Violation Monitor",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [{"field": "cronExpression", "expression": "0 */4 * * *"}]
        }
      },
      "name": "Every 4 Hours",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://137.184.1.91:8000/telegram/violations",
        "qs": {"severity": "critical"},
        "options": {}
      },
      "name": "Get Critical Violations",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 4,
      "position": [450, 300]
    },
    {
      "parameters": {
        "conditions": {
          "number": [{"value1": "={{$json.data.critical_count}}", "operation": "larger", "value2": 0}]
        }
      },
      "name": "Has Critical Violations",
      "type": "n8n-nodes-base.if",
      "typeVersion": 2,
      "position": [650, 300]
    },
    {
      "parameters": {
        "chatId": "YOUR_CHAT_ID_HERE",
        "text": "=🚨 **CRITICAL VIOLATION ALERT**\n\n{{$json.data.critical_count}} critical violations detected!\n\nUse /violations critical in @aseagi_legal_bot for details.",
        "additionalFields": {"parse_mode": "Markdown"}
      },
      "name": "Send Urgent Alert",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1.2,
      "position": [850, 250],
      "credentials": {"telegramApi": "ASEAGI Bot"}
    }
  ],
  "connections": {
    "Every 4 Hours": {"main": [[{"node": "Get Critical Violations", "type": "main", "index": 0}]]},
    "Get Critical Violations": {"main": [[{"node": "Has Critical Violations", "type": "main", "index": 0}]]},
    "Has Critical Violations": {"main": [[{"node": "Send Urgent Alert", "type": "main", "index": 0}]]}
  }
}
```

---

## 🧪 Test Your Workflows

### Test Daily Report:
1. Open workflow in n8n
2. Click **Execute Workflow** button
3. Should send you a Telegram message!

### Test Deadline Alerts:
1. Same as above
2. Only sends if deadlines exist

### Test Violation Monitor:
1. Same as above
2. Only sends if critical violations exist

---

## ✅ Success Checklist

- [ ] Got Telegram Chat ID from @userinfobot
- [ ] Created n8n Cloud account
- [ ] Added Telegram credentials in n8n
- [ ] Imported Workflow 1 (Daily Report)
- [ ] Replaced Chat ID in Workflow 1
- [ ] Activated Workflow 1
- [ ] Imported Workflow 2 (Deadline Alerts)
- [ ] Replaced Chat ID in Workflow 2
- [ ] Activated Workflow 2
- [ ] Imported Workflow 3 (Violation Monitor)
- [ ] Replaced Chat ID in Workflow 3
- [ ] Activated Workflow 3
- [ ] Tested all 3 workflows

---

## 🔧 Troubleshooting

### "Failed to connect to API"
**Problem:** Port 8000 not accessible from internet
**Fix:** Open port on droplet:
```bash
ssh root@137.184.1.91 "ufw allow 8000/tcp"
```

### "Unauthorized" error
**Problem:** Wrong Telegram bot token
**Fix:** Double-check token in n8n credentials

### "No response" when testing
**Problem:** API container not running
**Fix:**
```bash
ssh root@137.184.1.91 "docker ps | grep aseagi-api"
```

---

## 📊 What You'll Receive

### Daily (8 AM):
```
📊 ASEAGI Daily Report - 2024-11-06

🚨 Urgent Actions: 4
⚠️ Upcoming Deadlines: 2
📅 Upcoming Hearings: 1
⚖️ Recent Violations: 4

Use /report in @aseagi_legal_bot for full details.
```

### Daily (9 AM, if deadlines):
```
⚠️ DEADLINE ALERT

You have 2 deadlines in the next 7 days!

Use /deadline in @aseagi_legal_bot for details.
```

### Every 4 Hours (if critical violations):
```
🚨 CRITICAL VIOLATION ALERT

2 critical violations detected!

Use /violations critical in @aseagi_legal_bot for details.
```

---

**For Ashe. For Justice. For All Children.** 🛡️
