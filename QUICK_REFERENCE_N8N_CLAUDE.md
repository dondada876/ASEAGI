# 🚀 QUICK REFERENCE: N8N + CLAUDE CODE
*Print this and keep it visible during setup*

## DECISION TREE: WHICH TOOL TO USE?

```
Question to ask: "Where and when does this need to run?"

┌─ Needs to run 24/7, accessible anywhere?
│  └─→ Use n8n CLOUD ☁️
│
┌─ Needs to process local files or heavy data?
│  └─→ Use n8n LOCAL 💻 or Claude Code 🤖
│
┌─ Need to generate/modify code?
│  └─→ Use Claude Code 🤖
│
┌─ Simple routing/logic, external triggers?
│  └─→ Use n8n CLOUD ☁️
│
└─ Complex AI analysis, development work?
   └─→ Use Claude Code 🤖
```

---

## N8N CLOUD - WHEN TO USE

✅ **PERFECT FOR:**
- Telegram bot listeners (24/7)
- Email automation
- Webhook endpoints
- Simple task routing
- Team-accessible workflows
- Mobile-triggered actions
- Scheduled reminders
- External API integrations

❌ **DON'T USE FOR:**
- Heavy file processing
- Large dataset analysis
- Privacy-sensitive operations
- Development/testing

**Cost:** $20/mo (2,500 workflow executions)

---

## N8N LOCAL - WHEN TO USE

✅ **PERFECT FOR:**
- Document scanning (PROJ344)
- Large file operations
- Private/sensitive data
- Complex data transformations
- Development & testing
- Backup workflows

❌ **DON'T USE FOR:**
- Need 24/7 availability
- Team needs access
- Mobile-triggered workflows

**Cost:** Free (runs on your Mac)

---

## CLAUDE CODE - WHEN TO USE

✅ **PERFECT FOR:**
- Writing new code
- Debugging existing scripts
- Batch file operations
- Complex AI analysis
- Code refactoring
- Project-wide changes
- Generating documentation
- Creating test suites

❌ **DON'T USE FOR:**
- Simple automations (use n8n)
- 24/7 operations
- Non-development tasks

**Cost:** Uses your Claude API key (~$50-100/mo)

---

## SETUP CHECKLIST

### n8n Cloud (15 min)
- [ ] Sign up at n8n.io/cloud
- [ ] Create workspace
- [ ] Add Telegram credentials
- [ ] Add Supabase credentials
- [ ] Test simple workflow

### Claude Code (10 min)
- [ ] Install: `npm install -g @anthropic-ai/claude-code-cli`
- [ ] Add API key: `export ANTHROPIC_API_KEY='sk-ant-...'`
- [ ] Test: `claude-code "hello"`
- [ ] Create project config

### Integration (15 min)
- [ ] Set up ngrok for local→cloud
- [ ] Create webhook bridge
- [ ] Test end-to-end flow

---

## COMMON WORKFLOWS

### 1. TELEGRAM COMMAND HANDLER
**Tool:** n8n Cloud ☁️
**Why:** Must be always-on, mobile accessible
```
/status → n8n Cloud → Query DBs → Reply
```

### 2. DOCUMENT SCANNER
**Tool:** Claude Code 🤖 (or n8n Local)
**Why:** Heavy processing, local files
```
Files → Claude Code → OCR + Analysis → Save
```

### 3. TASK ENRICHMENT
**Tool:** n8n Cloud ☁️ + Claude API
**Why:** User-facing, real-time response
```
/task [text] → n8n → Claude API → Airtable
```

### 4. CODE GENERATION
**Tool:** Claude Code 🤖
**Why:** Development work
```
claude-code "create [script]" → Generated code
```

### 5. BATCH PROCESSING
**Tool:** Claude Code 🤖
**Why:** Many files, complex logic
```
For each file → Process → Save results
```

---

## QUICK START COMMANDS

### n8n Cloud
```bash
# Access your instance
https://yourname.app.n8n.cloud

# Create workflow
New → Add Telegram Trigger → Configure

# Test
Send message to bot → Check execution log
```

### n8n Local
```bash
# Start local instance
PATH="/opt/homebrew/opt/node@20/bin:$PATH" n8n start

# Access
http://localhost:5678

# Export workflow
Settings → Export (save JSON)
```

### Claude Code
```bash
# Interactive session
claude-code

# One-off command
claude-code "analyze my Python files"

# Create new file
claude-code create "script.py"

# With context
claude-code project
```

---

## COST BREAKDOWN

| Service | Monthly Cost | Worth It? |
|---------|--------------|-----------|
| n8n Cloud | $20 | ⭐⭐⭐⭐⭐ Yes! |
| n8n Local | $0 | ⭐⭐⭐⭐ Free |
| Claude API | $50-200 | ⭐⭐⭐⭐⭐ Yes! |
| Claude Code CLI | $0 | ⭐⭐⭐⭐⭐ Free tool |
| Supabase | $25 | ⭐⭐⭐⭐⭐ Yes! |
| Airtable | $20 | ⭐⭐⭐⭐ Yes |
| **TOTAL** | **$115-285** | **Priceless** |

**ROI:** Run empire from phone = Worth 100x the cost

---

## TROUBLESHOOTING

### n8n Cloud Can't Reach My Mac
```bash
# Install ngrok
brew install ngrok
ngrok http 5678

# Use ngrok URL in cloud workflows
https://abc123.ngrok.io/webhook/endpoint
```

### Claude Code Won't Start
```bash
# Check Node version
node --version  # Should be 18, 20, or 22

# Reinstall
npm uninstall -g @anthropic-ai/claude-code-cli
npm install -g @anthropic-ai/claude-code-cli

# Check API key
echo $ANTHROPIC_API_KEY
```

### n8n Workflow Fails
```bash
# Check execution log in n8n UI
# Look for red error nodes
# Click node → View details
# Common issues:
#   - Missing credentials
#   - Wrong data format
#   - Timeout (increase in settings)
```

### Claude API Rate Limit
```python
# Add retry logic to scripts
import time

for attempt in range(3):
    try:
        result = claude_api_call()
        break
    except RateLimitError:
        time.sleep(2 ** attempt)  # 1s, 2s, 4s
```

---

## YOUR FIRST 3 AUTOMATIONS

### Today: Status Dashboard (30 min)
```
1. n8n Cloud: New workflow
2. Telegram Trigger: /status
3. Supabase node: Query revenue
4. Telegram Send: Format and reply
5. Test it!
```

### Tomorrow: Task Creation (45 min)
```
1. n8n Cloud: New workflow
2. Telegram Trigger: /task
3. HTTP node: Claude API (enrich task)
4. Airtable node: Create record
5. Telegram Send: Confirmation
```

### Day 3: Document Scanner (1 hour)
```
1. Terminal: claude-code
2. "Create document scanner script"
3. Test with sample file
4. Connect to Supabase
5. Schedule to run daily
```

---

## KEYBOARD SHORTCUTS

### n8n
- `Ctrl/Cmd + K` - Quick search
- `Tab` - Connect nodes
- `Delete` - Remove node
- `Ctrl/Cmd + S` - Save workflow
- `Ctrl/Cmd + Enter` - Execute workflow

### Claude Code
- `Ctrl + C` - Stop generation
- `Ctrl + D` - Exit session
- `Up Arrow` - Previous command
- `Tab` - Autocomplete

---

## MONITORING

### Daily Checks (2 min)
- [ ] n8n Cloud: Check execution history
- [ ] Claude API: Check usage dashboard
- [ ] Supabase: Check database size
- [ ] Telegram: Test /status command

### Weekly Reviews (15 min)
- [ ] Review failed workflows
- [ ] Optimize high-cost operations
- [ ] Update workflows as needed
- [ ] Check for new features

---

## SUPPORT RESOURCES

**n8n:**
- Docs: docs.n8n.io
- Forum: community.n8n.io
- Templates: n8n.io/workflows

**Claude:**
- Docs: docs.anthropic.com
- Console: console.anthropic.com
- Discord: discord.gg/anthropic

**Your Setup:**
- Main guide: CEO_N8N_CLAUDE_SETUP.md
- Mobile guide: CEO_MOBILE_CLOUD_SETUP.md
- Project context: /mnt/project/

---

## REMEMBER

🎯 **Start Simple**
- One workflow at a time
- Test thoroughly
- Add complexity gradually

⚡ **Focus on Value**
- Automate repetitive tasks first
- Keep manual tasks that require judgment
- Measure time saved vs cost

👨‍👧 **Father First**
- Automation serves your goals
- More automation = More presence with Ashé
- Business success = Resources for reunion

---

Print this card and keep it visible!

Last updated: Nov 4, 2025
