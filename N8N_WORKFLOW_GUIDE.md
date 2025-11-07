# N8N Workflow Integration Guide

**Complete guide for N8N workflows in the ASEAGI system**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [N8N Cloud vs Local](#n8n-cloud-vs-local)
3. [Setup Instructions](#setup-instructions)
4. [Workflow Templates](#workflow-templates)
5. [Credentials Configuration](#credentials-configuration)
6. [Testing & Debugging](#testing--debugging)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 🎯 Overview

### What N8N Does in ASEAGI

N8N provides **automation workflows** that connect your Telegram bot to the FastAPI backend and enable:

1. **24/7 Telegram Bot Operation** - Always listening for commands
2. **Scheduled Tasks** - Daily deadline checks, truth score monitoring
3. **Document Processing** - Automated AI analysis
4. **Proactive Alerts** - Push notifications to your phone
5. **Data Entry Automation** - Log events, communications from phone

### Architecture

```
┌─────────────┐
│   Telegram  │ User sends /status
│    User     │────────────────┐
└─────────────┘                │
                               ▼
                     ┌─────────────────┐
                     │  N8N CLOUD ☁️   │
                     │  (Always On)    │
                     │                 │
                     │  Telegram       │
                     │  Bot Trigger    │
                     └────────┬────────┘
                              │
                              │ HTTP Request
                              │
                    ┌─────────▼────────┐
                    │  FastAPI Backend │
                    │  (Port 8000)     │
                    │  /telegram/status│
                    └────────┬─────────┘
                             │
                             │ SQL Query
                             │
                    ┌────────▼─────────┐
                    │ Supabase DB      │
                    │ (events table)   │
                    └──────────────────┘
```

---

## ☁️ N8N Cloud vs Local

### Decision Matrix

| Use Case | N8N Cloud ☁️ | N8N Local 💻 |
|----------|--------------|--------------|
| **Telegram bot listener** | ✅ Required | ❌ Won't work |
| **Scheduled alerts (6am)** | ✅ Perfect | ⚠️ Mac must be on |
| **Document processing** | ⚠️ Limited (50MB) | ✅ Unlimited |
| **Heavy AI analysis** | ❌ Slow/expensive | ✅ Fast |
| **24/7 operation** | ✅ Yes | ❌ Only when Mac on |
| **Cost** | $20/mo | Free |
| **Setup** | 15 minutes | 30 minutes |

### Recommended Setup

**N8N Cloud ($20/mo):**
- Telegram bot listener (Workflow 1)
- Daily deadline checker (Workflow 2)
- Truth score monitor (Workflow 4)
- All scheduled workflows

**N8N Local (Free):**
- Document processing (Workflow 3)
- Heavy AI analysis
- Large file operations

**Hybrid approach = Best of both worlds**

---

## 🚀 Setup Instructions

### Part A: N8N Cloud Setup (15 minutes)

#### Step 1: Create Account

1. Go to https://n8n.io/cloud
2. Click "Start free trial"
3. Sign up with email
4. Choose plan: **Starter ($20/mo)** - 2,500 executions
5. Create workspace: "ASEAGI"

#### Step 2: Get Credentials

**Telegram Bot Token:**
1. Open Telegram
2. Search for `@BotFather`
3. Send `/newbot`
4. Name: "ASEAGI Assistant"
5. Username: `aseagi_bot` (or similar available name)
6. **Save bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Your Telegram User ID:**
1. Search for `@userinfobot` in Telegram
2. Start chat
3. **Save your user ID** (number like: `987654321`)

**FastAPI URL:**
- If running locally: `http://your-mac-ip:8000`
- If running on VPS: `http://your-vps-ip:8000`
- If using ngrok: `https://abc123.ngrok.io`

#### Step 3: Add Credentials to N8N

1. In N8N Cloud, click "Credentials" → "Add Credential"

**Telegram Credential:**
- Type: "Telegram"
- Name: "ASEAGI Telegram Bot"
- Access Token: `<paste bot token>`
- Click "Save"

**HTTP Credential (Optional):**
- Type: "HTTP Request"
- Name: "FastAPI Backend"
- Authentication: None (or Basic if you add it)
- Click "Save"

#### Step 4: Import Workflow

1. Click "Workflows" → "Add Workflow"
2. Copy JSON template (from Workflow 1 below)
3. Click "..." → "Import from File/URL"
4. Paste JSON
5. Click nodes and select credentials
6. Click "Save" → "Activate"

---

### Part B: N8N Local Setup (30 minutes)

#### Step 1: Install N8N

**macOS:**
```bash
# Install Node.js 20 (if not installed)
brew install node@20

# Add to PATH
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"

# Install N8N globally
npm install -g n8n

# Verify installation
n8n --version
```

#### Step 2: Start N8N

```bash
# Start N8N server
n8n start

# Access at: http://localhost:5678
```

#### Step 3: Configure

1. Open http://localhost:5678
2. Create account (local only, your data stays on Mac)
3. Add same credentials as N8N Cloud
4. Import Workflow 3 (Document Processing)

#### Step 4: Keep Running

**Option 1: Run in background**
```bash
# Start N8N in background
nohup n8n start &

# Check if running
ps aux | grep n8n

# Stop
pkill n8n
```

**Option 2: System service (recommended)**
```bash
# Create service file
sudo nano /Library/LaunchDaemons/com.n8n.server.plist
```

Paste:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.n8n.server</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/n8n</string>
        <string>start</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/tmp/n8n-error.log</string>
    <key>StandardOutPath</key>
    <string>/tmp/n8n-out.log</string>
</dict>
</plist>
```

```bash
# Load service
sudo launchctl load /Library/LaunchDaemons/com.n8n.server.plist

# Check status
sudo launchctl list | grep n8n
```

---

## 📋 Workflow Templates

### Workflow 1: Telegram Bot Command Handler (N8N Cloud)

**Purpose:** Listen for Telegram commands 24/7 and route to FastAPI

**JSON Template:**

```json
{
  "name": "ASEAGI Telegram Bot Handler",
  "nodes": [
    {
      "parameters": {
        "updates": [
          "message"
        ]
      },
      "name": "Telegram Trigger",
      "type": "n8n-nodes-base.telegramTrigger",
      "typeVersion": 1,
      "position": [
        240,
        300
      ],
      "credentials": {
        "telegramApi": {
          "id": "1",
          "name": "ASEAGI Telegram Bot"
        }
      }
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json[\"message\"][\"text\"]}}",
              "operation": "startsWith",
              "value2": "/status"
            }
          ]
        }
      },
      "name": "Is /status?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        460,
        300
      ]
    },
    {
      "parameters": {
        "url": "http://your-fastapi-url:8000/telegram/status",
        "options": {}
      },
      "name": "Get Status from API",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [
        680,
        200
      ]
    },
    {
      "parameters": {
        "chatId": "={{$json[\"message\"][\"chat\"][\"id\"]}}",
        "text": "={{$json[\"message\"]}}",
        "additionalFields": {
          "parse_mode": "Markdown"
        }
      },
      "name": "Send Reply",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1,
      "position": [
        900,
        200
      ],
      "credentials": {
        "telegramApi": {
          "id": "1",
          "name": "ASEAGI Telegram Bot"
        }
      }
    }
  ],
  "connections": {
    "Telegram Trigger": {
      "main": [
        [
          {
            "node": "Is /status?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is /status?": {
      "main": [
        [
          {
            "node": "Get Status from API",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Status from API": {
      "main": [
        [
          {
            "node": "Send Reply",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

**Configuration:**
1. Import JSON into N8N Cloud
2. Update "http://your-fastapi-url:8000" with actual URL
3. Select Telegram credential
4. Click "Save" → "Activate"
5. Test by sending `/status` to bot

---

### Workflow 2: Daily Deadline Checker (N8N Cloud)

**Purpose:** Check for urgent deadlines every morning at 6am and send alerts

**JSON Template:**

```json
{
  "name": "ASEAGI Daily Deadline Checker",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 6 * * *"
            }
          ]
        }
      },
      "name": "Schedule Trigger (6am daily)",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [
        240,
        300
      ]
    },
    {
      "parameters": {
        "url": "http://your-fastapi-url:8000/api/dashboard/court-events",
        "options": {}
      },
      "name": "Get Upcoming Events",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [
        460,
        300
      ]
    },
    {
      "parameters": {
        "fieldToSplitOut": "data.upcoming",
        "options": {}
      },
      "name": "Split Into Events",
      "type": "n8n-nodes-base.splitInBatches",
      "typeVersion": 1,
      "position": [
        680,
        300
      ]
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json[\"urgency\"]}}",
              "operation": "equals",
              "value2": "URGENT"
            }
          ]
        }
      },
      "name": "Is Urgent?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        900,
        300
      ]
    },
    {
      "parameters": {
        "text": "=🔴 URGENT DEADLINE\n\n*{{$json[\"event_title\"]}}*\nDue: {{$json[\"event_date\"]}}\nUrgency: {{$json[\"urgency\"]}}\n\n⚠️ Action required within 3 days!",
        "chatId": "YOUR_TELEGRAM_USER_ID",
        "additionalFields": {
          "parse_mode": "Markdown"
        }
      },
      "name": "Send Alert",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1,
      "position": [
        1120,
        200
      ],
      "credentials": {
        "telegramApi": {
          "id": "1",
          "name": "ASEAGI Telegram Bot"
        }
      }
    }
  ],
  "connections": {
    "Schedule Trigger (6am daily)": {
      "main": [
        [
          {
            "node": "Get Upcoming Events",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Upcoming Events": {
      "main": [
        [
          {
            "node": "Split Into Events",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Split Into Events": {
      "main": [
        [
          {
            "node": "Is Urgent?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Is Urgent?": {
      "main": [
        [
          {
            "node": "Send Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

**Configuration:**
1. Import JSON
2. Update FastAPI URL
3. **Replace `YOUR_TELEGRAM_USER_ID`** with your actual user ID
4. Select Telegram credential
5. Test with "Execute Workflow" button
6. Activate

**Testing:**
- Click "Execute Workflow" to test immediately
- Check Telegram for alert
- If no urgent events, add test event with close deadline

---

### Workflow 3: Document Processing (N8N Local)

**Purpose:** Process uploaded documents with AI analysis

**Simplified Template:**

```json
{
  "name": "ASEAGI Document Processor",
  "nodes": [
    {
      "parameters": {
        "path": "/webhook/document",
        "httpMethod": "POST",
        "responseMode": "lastNode"
      },
      "name": "Webhook Trigger",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [
        240,
        300
      ]
    },
    {
      "parameters": {
        "functionCode": "// Extract document URL from webhook payload\nconst documentUrl = $json.document_url;\nconst documentId = $json.document_id;\n\nreturn {\n  documentUrl,\n  documentId,\n  status: 'processing'\n};"
      },
      "name": "Extract Document Info",
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [
        460,
        300
      ]
    },
    {
      "parameters": {
        "url": "={{$json[\"documentUrl\"]}}",
        "options": {}
      },
      "name": "Download Document",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [
        680,
        300
      ]
    },
    {
      "parameters": {
        "text": "Analyze this legal document and provide:\n1. Relevancy score (0-1000)\n2. Key insights (bullet list)\n3. Any contradictions found\n4. Smoking gun quotes\n\nDocument content: {{$binary.data}}",
        "options": {
          "model": "claude-3-5-sonnet-20241022"
        }
      },
      "name": "Claude Analysis",
      "type": "@n8n/n8n-nodes-langchain.lmChatAnthropic",
      "typeVersion": 1,
      "position": [
        900,
        300
      ],
      "credentials": {
        "anthropicApi": {
          "id": "2",
          "name": "Claude API"
        }
      }
    },
    {
      "parameters": {
        "url": "http://localhost:8000/telegram/document-analyzed",
        "method": "POST",
        "jsonParameters": true,
        "options": {},
        "bodyParametersJson": "={\n  \"document_id\": \"{{$json.documentId}}\",\n  \"analysis\": \"{{$json.response}}\"\n}"
      },
      "name": "Update Database",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [
        1120,
        300
      ]
    },
    {
      "parameters": {
        "text": "=✅ Document Analysis Complete\n\n*{{$json.filename}}*\n\nRelevancy: {{$json.relevancy_score}}/1000\nInsights: {{$json.insights_count}} found\n\nCheck web dashboard for full details.",
        "chatId": "YOUR_TELEGRAM_USER_ID",
        "additionalFields": {
          "parse_mode": "Markdown"
        }
      },
      "name": "Send Notification",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1,
      "position": [
        1340,
        300
      ],
      "credentials": {
        "telegramApi": {
          "id": "1",
          "name": "ASEAGI Telegram Bot"
        }
      }
    }
  ],
  "connections": {
    "Webhook Trigger": {
      "main": [
        [
          {
            "node": "Extract Document Info",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Extract Document Info": {
      "main": [
        [
          {
            "node": "Download Document",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Download Document": {
      "main": [
        [
          {
            "node": "Claude Analysis",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Claude Analysis": {
      "main": [
        [
          {
            "node": "Update Database",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Update Database": {
      "main": [
        [
          {
            "node": "Send Notification",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

**Note:** This workflow runs on N8N Local for heavy processing

---

### Workflow 4: Truth Score Monitor (N8N Cloud)

**Purpose:** Daily check of truth/justice scores and alert on anomalies

**Simplified Template:**

```json
{
  "name": "ASEAGI Truth Score Monitor",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "cronExpression",
              "expression": "0 20 * * *"
            }
          ]
        }
      },
      "name": "Schedule (8pm daily)",
      "type": "n8n-nodes-base.scheduleTrigger",
      "typeVersion": 1,
      "position": [
        240,
        300
      ]
    },
    {
      "parameters": {
        "url": "http://your-fastapi-url:8000/api/dashboard/truth-timeline?days=7",
        "options": {}
      },
      "name": "Get Truth Data",
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 3,
      "position": [
        460,
        300
      ]
    },
    {
      "parameters": {
        "conditions": {
          "number": [
            {
              "value1": "={{$json[\"data\"][\"justice_score\"]}}",
              "operation": "smaller",
              "value2": 60
            }
          ]
        }
      },
      "name": "Justice Score Low?",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [
        680,
        300
      ]
    },
    {
      "parameters": {
        "text": "=⚠️ TRUTH SCORE ALERT\n\n*Justice Score Dropped*\nCurrent: {{$json.data.justice_score}}/100\nTarget: >60\n\n📊 Breakdown:\n✅ Truthful: {{$json.data.true_count}}\n⚠️ Questionable: {{$json.data.questionable_count}}\n❌ False: {{$json.data.false_count}}\n\nReview recent timeline items.",
        "chatId": "YOUR_TELEGRAM_USER_ID",
        "additionalFields": {
          "parse_mode": "Markdown"
        }
      },
      "name": "Send Alert",
      "type": "n8n-nodes-base.telegram",
      "typeVersion": 1,
      "position": [
        900,
        200
      ],
      "credentials": {
        "telegramApi": {
          "id": "1",
          "name": "ASEAGI Telegram Bot"
        }
      }
    }
  ],
  "connections": {
    "Schedule (8pm daily)": {
      "main": [
        [
          {
            "node": "Get Truth Data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get Truth Data": {
      "main": [
        [
          {
            "node": "Justice Score Low?",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Justice Score Low?": {
      "main": [
        [
          {
            "node": "Send Alert",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

---

## 🔑 Credentials Configuration

### Telegram Bot API

**In N8N:**
1. Go to "Credentials" → "Add Credential"
2. Type: "Telegram"
3. Name: "ASEAGI Telegram Bot"
4. Access Token: `<your bot token from @BotFather>`
5. Base URL: (leave default)
6. Click "Save"

**Testing:**
- Click "Test" button
- Should see green checkmark
- If error, verify bot token is correct

---

### HTTP Authentication (Optional)

**If FastAPI has authentication:**

1. Go to "Credentials" → "Add Credential"
2. Type: "HTTP Header Auth" or "Basic Auth"
3. Add your authentication details
4. Use this credential in HTTP Request nodes

---

### Claude API (for Workflow 3)

**In N8N Local:**
1. Get API key from https://console.anthropic.com
2. Go to "Credentials" → "Add Credential"
3. Type: "Anthropic"
4. Name: "Claude API"
5. API Key: `sk-ant-...`
6. Click "Save"

---

## 🧪 Testing & Debugging

### Test Workflow 1 (Telegram Bot)

**Manual Test:**
1. In N8N, open "ASEAGI Telegram Bot Handler"
2. Click "Execute Workflow"
3. Open Telegram, send `/status` to bot
4. Check N8N execution log
5. Verify response in Telegram

**Debug Checklist:**
- [ ] Bot token correct?
- [ ] FastAPI URL correct?
- [ ] FastAPI server running?
- [ ] Telegram credential selected?
- [ ] Workflow activated (not just saved)?

---

### Test Workflow 2 (Deadline Checker)

**Manual Test:**
1. Click "Execute Workflow" (runs immediately)
2. Check Telegram for alerts
3. Review execution log in N8N

**If No Alerts:**
- Check if any events have urgency = URGENT
- Add test event with close deadline
- Verify FastAPI endpoint returns data

---

### Common Issues

**Issue: "Workflow didn't execute"**
- Solution: Check if workflow is "Active" (toggle at top)

**Issue: "HTTP Request failed"**
- Check FastAPI server is running: `curl http://localhost:8000/health`
- Check URL is correct (no typos)
- Check CORS allows N8N's IP

**Issue: "Telegram bot not responding"**
- Check bot token is correct
- Check bot is not blocked
- Check webhook isn't set elsewhere

**Issue: "Execution limit reached"**
- N8N Cloud Starter: 2,500/month
- Optimize workflows (batch operations)
- Upgrade plan if needed

---

## 📊 Monitoring & Maintenance

### Daily Checks

**In N8N Cloud:**
1. Go to "Executions"
2. Check for any failed executions (red icons)
3. Review error messages
4. Re-run failed workflows if needed

**Check:**
- [ ] Telegram bot responding?
- [ ] Deadline checker ran this morning?
- [ ] Truth score check ran last night?
- [ ] Any error notifications?

---

### Weekly Maintenance

**Review Execution Stats:**
- Total executions this week
- Success rate (should be >99%)
- Average execution time
- Most used workflows

**Optimize:**
- Batch similar operations
- Reduce unnecessary executions
- Cache repeated API calls
- Review execution limits

---

### Monthly Review

**Cost Analysis:**
- N8N Cloud: $20/mo
- Executions used vs. limit
- Consider upgrade if hitting limits
- ROI: Time saved vs. cost

**Performance:**
- Execution time trends
- Error rate trends
- User satisfaction
- New workflow ideas

---

## ✅ Deployment Checklist

### N8N Cloud

- [ ] Account created
- [ ] Telegram credential added
- [ ] FastAPI URL configured
- [ ] Workflow 1 (Telegram Bot) imported
- [ ] Workflow 1 activated
- [ ] Workflow 1 tested with /status command
- [ ] Workflow 2 (Deadline Checker) imported
- [ ] Workflow 2 tested manually
- [ ] Workflow 2 activated
- [ ] Your Telegram user ID added to all workflows
- [ ] Workflow 4 (Truth Score) imported and activated

### N8N Local (Optional)

- [ ] N8N installed
- [ ] Running as background service
- [ ] Claude API credential added
- [ ] Workflow 3 (Document Processing) imported
- [ ] Webhook URL accessible
- [ ] Test document processed successfully

---

## 📚 Resources

**N8N Documentation:**
- Official Docs: https://docs.n8n.io
- Community Forum: https://community.n8n.io
- Workflow Templates: https://n8n.io/workflows

**ASEAGI Documentation:**
- Telegram Bot Roadmap: `TELEGRAM_BOT_ROADMAP.md`
- Product Requirements: `PRODUCT_REQUIREMENTS_DOCUMENT.md`
- API Documentation: `telegram-bot/README_EXTENDED.md`
- Deployment Guide: `DEPLOYMENT_GUIDE.md`

---

**For Ashe - Automation that never sleeps** ⚖️

*"24/7 operation, proactive alerts, never miss a deadline"*

---

**Last Updated:** November 2025
**Status:** Ready for deployment
**Next:** Import Workflow 1 into N8N Cloud
