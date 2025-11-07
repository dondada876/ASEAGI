# 🎤 Voice-Activated Case Management Workflow

**Complete architecture for Airtable → Supabase → Telegram integration**

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA ENTRY                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Airtable (Pretty UI)          OR          Direct Supabase      │
│  ├─ Communications                         ├─ SQL Editor        │
│  ├─ Events                                 ├─ Table Editor      │
│  ├─ Actions                                └─ API               │
│  ├─ Violations                                                  │
│  └─ Hearings                                                    │
│                                                                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA SYNC (n8n)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  n8n Workflow (Every 5 minutes)                                 │
│  1. Fetch new/updated records from Airtable                     │
│  2. Transform to Supabase schema                                │
│  3. Insert/Update in Supabase                                   │
│  4. Send notification if critical data added                    │
│                                                                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CENTRAL DATABASE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Supabase (PostgreSQL)                                          │
│  ├─ communications                                              │
│  ├─ events                                                      │
│  ├─ action_items                                                │
│  ├─ violations                                                  │
│  ├─ hearings                                                    │
│  └─ document_journal                                            │
│                                                                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API LAYER                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  FastAPI (http://137.184.1.91:8000)                            │
│  ├─ /telegram/* endpoints                                       │
│  ├─ /claude/analyze (AI analysis)                              │
│  ├─ /claude/generate-motion (AI generation)                    │
│  └─ /claude/insights (AI insights)                             │
│                                                                  │
└────┬──────────────────────────────────┬─────────────────────────┘
     │                                  │
     ▼                                  ▼
┌─────────────────────┐     ┌─────────────────────────────────────┐
│  VOICE INTERFACE    │     │     TEXT INTERFACE                  │
├─────────────────────┤     ├─────────────────────────────────────┤
│                     │     │                                     │
│ Telegram Voice Msg  │     │ Telegram Text Commands             │
│       ↓             │     │ ├─ /report                         │
│ Whisper API         │     │ ├─ /violations                     │
│       ↓             │     │ ├─ /timeline                       │
│ Transcribe to text  │     │ ├─ /actions                        │
│       ↓             │     │ └─ /search                         │
│ Parse command       │     │                                     │
│       ↓             │     │                                     │
│ Execute via API  ───┴─────┴─────────────────────────────────── │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎤 Voice Command Flow

### Example: "Check my violations"

```
1. User sends voice message to @aseagi_legal_bot

2. Telegram Bot receives voice file
   ├─ Download .ogg file
   └─ Send to OpenAI Whisper API

3. Whisper transcribes: "check my violations"

4. Bot parses command:
   ├─ Action: "check"
   ├─ Target: "violations"
   └─ Maps to: /violations

5. Bot calls FastAPI:
   GET http://api:8000/telegram/violations

6. FastAPI queries Supabase:
   SELECT * FROM violations WHERE severity='critical'

7. Bot formats response:
   "⚖️ Found 4 violations (2 CRITICAL)"

8. Bot sends text response + optional voice reply
```

---

## 📊 Airtable → Supabase Sync Flow

### Workflow: Airtable Data Entry

```
┌──────────────────────────────────────────────────────────────┐
│  Airtable Base: ASEAGI Case Management                       │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Table: Communications                                        │
│  ┌───────────┬──────────┬─────────────┬──────────────────┐  │
│  │ Sender    │ Date     │ Content     │ Truthfulness     │  │
│  ├───────────┼──────────┼─────────────┼──────────────────┤  │
│  │ Mother    │ 1/15/24  │ Ready to... │ 0.85            │  │
│  │ SW Turner │ 1/15/24  │ Cannot...   │ 0.65 ⚠️         │  │
│  └───────────┴──────────┴─────────────┴──────────────────┘  │
│                                                               │
│  ✅ Pretty forms                                             │
│  ✅ Attachments                                              │
│  ✅ Linked records                                           │
│  ✅ Views/filters                                            │
│                                                               │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            │ n8n Automation (Every 5 min)
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  n8n Workflow: Airtable → Supabase Sync                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Airtable Trigger (new/modified records)                  │
│     ├─ Get last sync timestamp                               │
│     └─ Fetch records modified since last sync                │
│                                                               │
│  2. Transform Node                                            │
│     ├─ Map Airtable fields → Supabase columns                │
│     ├─ Convert date formats                                   │
│     └─ Handle attachments                                     │
│                                                               │
│  3. Supabase Insert/Update                                    │
│     ├─ Check if record exists (by airtable_id)               │
│     ├─ Insert if new                                          │
│     └─ Update if exists                                       │
│                                                               │
│  4. Notification (if critical)                                │
│     └─ Send Telegram alert for urgent items                  │
│                                                               │
└───────────────────────────┬──────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  Supabase (Single Source of Truth)                           │
│  ├─ All data synced                                          │
│  ├─ Available to API                                         │
│  └─ Available to dashboards                                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🤖 Claude AI Integration

### Option 1: AI Analysis via API

```python
# Add to FastAPI (api-service/main.py)

from anthropic import Anthropic

@app.post("/claude/analyze")
async def analyze_case(request: AnalysisRequest):
    """Use Claude to analyze case data"""

    # Get case data from Supabase
    violations = supabase.table("violations").select("*").execute()
    communications = supabase.table("communications").select("*").execute()

    # Build prompt
    prompt = f"""
    Analyze this legal case data:

    Violations: {violations.data}
    Communications: {communications.data}

    Provide:
    1. Case strength assessment
    2. Key legal issues
    3. Recommended actions
    4. Evidence gaps
    """

    # Call Claude
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return {"analysis": response.content[0].text}
```

### Telegram Voice Command:
```
User: "Analyze my case strength"
  ↓
Bot: Calls /claude/analyze
  ↓
Returns: "Case Strength: 7/10. Key issues: Missing Cal OES 2-925..."
```

---

## 🎯 Recommended Implementation Order

### **Week 1: Airtable Setup**
1. Create Airtable base matching Supabase schema
2. Import existing data from Supabase
3. Add pretty views, forms, automations

### **Week 2: n8n Sync**
1. Create n8n workflow for Airtable → Supabase
2. Test sync (every 5 minutes)
3. Add error handling and notifications

### **Week 3: Voice Commands**
1. Add voice message handler to Telegram bot
2. Integrate Whisper API for transcription
3. Map voice commands to existing endpoints

### **Week 4: Claude AI**
1. Add Claude API integration to FastAPI
2. Create analysis endpoints
3. Add voice command: "Analyze my case"

---

## 📝 Why NOT Use Markdown Files?

**You asked about:**
> "Create markdown file → Claude Desktop → Repo → Claude Code → Supabase"

**Problems with this approach:**
❌ Too many manual steps
❌ Not real-time (requires exports)
❌ No version control benefits for data
❌ Breaks with voice commands (need automation)
❌ Git repos shouldn't store data (just code)

**Better approach:**
✅ Direct API integration (Airtable → n8n → Supabase)
✅ Real-time sync
✅ Voice commands work automatically
✅ Claude analyzes live data via API
✅ No manual intervention needed

---

## 🎤 Voice Command Examples

### **Reports:**
- "Check my daily report" → `/report`
- "Show violations" → `/violations`
- "What are my deadlines?" → `/deadline`

### **Search:**
- "Search for Jamaica" → `/search Jamaica`
- "Find communications about visitation" → `/search visitation`

### **AI Analysis:**
- "Analyze my case" → Calls Claude API
- "What's my case strength?" → Claude analyzes data
- "Suggest next steps" → Claude recommends actions

### **Document Generation:**
- "Generate motion for reconsideration" → Calls Claude to draft
- "Create declaration about Cal OES violation" → AI generates doc

---

## 💡 Best Practices

### **1. Single Source of Truth: Supabase**
- Don't duplicate data across systems
- Sync everything TO Supabase
- All queries FROM Supabase

### **2. Airtable as Entry UI Only**
- Use for pretty data entry
- Auto-sync to Supabase
- Don't query Airtable directly from bot

### **3. Voice Commands = Text Commands**
- Transcribe voice → text
- Parse as normal command
- Reuse existing API endpoints

### **4. Claude AI via API Only**
- Don't use Claude Desktop for data (use for code)
- Call Claude API from FastAPI
- Analyze live data from Supabase

---

## 🚀 Next Steps

**Want me to build this?**

I can create:
1. ✅ Voice handler for Telegram bot
2. ✅ n8n workflow for Airtable → Supabase sync
3. ✅ Claude AI analysis endpoint
4. ✅ Airtable base template

**Which would you like first?**

---

**For Ashe. For Justice. For All Children.** 🛡️
