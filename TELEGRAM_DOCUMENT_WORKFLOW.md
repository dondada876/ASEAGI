# 📱 TELEGRAM DOCUMENT SCANNING & STORAGE WORKFLOW

**Complete Guide: Where Documents Go After Scanning**

Last Updated: November 17, 2025
Case: J24-00478 (In re Ashe Bucknor)

---

## 🎯 Quick Answer

**When you send a document via Telegram:**

1. **Telegram Bot receives** → Image/PDF/Text file
2. **Stored permanently** → `/data/telegram-inbox/YYYY-MM-DD/` folder
3. **Claude AI analyzes** → PROJ344 scoring (0-999)
4. **Uploaded to database** → Supabase tables
5. **Routed to dashboard** → Based on category
6. **Tiered storage** → Based on score (Hot/Warm/Cool/Cold)
7. **Telegram notification** → Confirms processing complete

---

## 📊 COMPLETE WORKFLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: DOCUMENT ARRIVAL                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        You send document via Telegram (@aseagi_legal_bot)
        Document types: JPG, PNG, HEIC, PDF, TXT, RTF
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: PERMANENT STORAGE (Immediate - Before Analysis)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Location: /home/user/ASEAGI/data/telegram-inbox/
        Organized by: telegram-inbox/2025-11-17/document.jpg
                              ↓
        ✅ File is NEVER deleted (permanent archive)
        ✅ Available for re-analysis anytime
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: DUPLICATE CHECK                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Calculate MD5 hash: calculate_file_hash()
        Query Supabase: WHERE content_hash = 'abc123...'
                              ↓
        ┌──────────────┬─────────────┐
        │ Duplicate?   │   New Doc?  │
        │ Skip → Exit  │  Continue ↓ │
        └──────────────┴─────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: CLAUDE AI ANALYSIS (PROJ344 Scoring)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Model: claude-sonnet-4-20250514
        System Prompt: PROJ344 Scoring Methodology
        Input: Image (base64) or Text content
                              ↓
        Analysis Returns JSON:
        ├─ micro_number: 0-999 (detail importance)
        ├─ macro_number: 0-999 (case-wide significance)
        ├─ legal_number: 0-999 (legal weight)
        ├─ relevancy_number: 0-999 (composite score)
        ├─ document_type: TEXT|TRNS|MEDR|ORDR|etc.
        ├─ smoking_guns: ["Critical fact or admission"]
        ├─ fraud_indicators: []
        ├─ perjury_indicators: []
        └─ api_cost_usd: $0.0133 (average)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: DATABASE UPLOAD (Supabase PostgreSQL)                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Primary Upload: general_documents table (intake)
                              ↓
        Data Stored:
        ├─ original_filename: "document.jpg"
        ├─ file_path: "/data/telegram-inbox/2025-11-17/document.jpg"
        ├─ content_hash: "abc123..." (MD5)
        ├─ PROJ344 scores (micro, macro, legal, relevancy)
        ├─ key_quotes: ["Important quote 1", ...]
        ├─ fraud_indicators, perjury_indicators
        ├─ processed_at: timestamp
        ├─ api_cost_usd: $0.0133
        └─ case_id: "ashe-bucknor-j24-00478"
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: CATEGORY-BASED ROUTING (Multi-Table Strategy)          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Document Category = ?
        ↓                    ↓                    ↓
    ┌───────┐          ┌──────────┐        ┌──────────┐
    │ LEGAL │          │ BUSINESS │        │  FAMILY  │
    └───────┘          └──────────┘        └──────────┘
        ↓                    ↓                    ↓
 legal_documents    ceo_business_docs    family_documents
    (J24-00478)      (CEO Dashboard)        (Personal)
        ↓
    Additional Copy to Specialized Table
    (Preserves in both general_documents + legal_documents)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 7: STORAGE TIER ASSIGNMENT (Cost Optimization)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Based on: relevancy_number (0-999)
                              ↓
        ┌──────────────────────────────────────────┐
        │ TIER 1: HOT STORAGE (900-999)            │
        │ Score: 900-999 (Smoking Gun)             │
        │ Storage: Supabase + Google Drive         │
        │ Cost: $0.021/GB/month                    │
        │ Access: <1 second (Instant)              │
        │ Replicas: 3 copies                       │
        │ Use: Critical evidence, active case      │
        └──────────────────────────────────────────┘
                    ↓
        ┌──────────────────────────────────────────┐
        │ TIER 2: WARM STORAGE (700-899)           │
        │ Score: 700-899 (Important)               │
        │ Storage: Backblaze B2                    │
        │ Cost: $0.005/GB/month                    │
        │ Access: 1-5 seconds                      │
        │ Replicas: 2 copies                       │
        │ Use: High-value evidence, transcripts    │
        └──────────────────────────────────────────┘
                    ↓
        ┌──────────────────────────────────────────┐
        │ TIER 3: COOL STORAGE (400-699)           │
        │ Score: 400-699 (Useful)                  │
        │ Storage: AWS S3 Intelligent-Tiering      │
        │ Cost: $0.0125/GB/month                   │
        │ Access: 5-60 seconds                     │
        │ Replicas: 1 copy                         │
        │ Use: Supporting documents, background    │
        └──────────────────────────────────────────┘
                    ↓
        ┌──────────────────────────────────────────┐
        │ TIER 4: COLD ARCHIVE (0-399)             │
        │ Score: 0-399 (Reference)                 │
        │ Storage: AWS Glacier Deep Archive        │
        │ Cost: $0.00099/GB/month                  │
        │ Access: 1-12 hours                       │
        │ Replicas: 1 copy                         │
        │ Use: Historical archive, rarely accessed │
        └──────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 8: DASHBOARD DISPLAY (Real-time Visibility)               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Documents visible on dashboards:
        ├─ Port 8501: PROJ344 Master Dashboard
        │   └─ Shows ALL legal documents with PROJ344 scores
        │   └─ Smoking gun filter (≥900)
        ├─ Port 8502: Legal Intelligence Dashboard
        │   └─ Document-by-document analysis
        ├─ Port 8503: CEO Dashboard
        │   └─ File organization health checks
        ├─ Port 8504: Enhanced Scanning Monitor
        │   └─ Real-time processing status
        └─ Port 8505: Scanning Monitor Dashboard
            └─ Detailed scan progress
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 9: n8n AUTOMATION WORKFLOWS                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Workflow 1: Daily Report (8 AM)
        ├─ Query: All documents processed yesterday
        ├─ Send: Telegram summary to @aseagi_legal_bot
        └─ Include: Total docs, smoking guns, critical evidence
                              ↓
        Workflow 2: Hourly Smoking Gun Alerts
        ├─ Query: New documents with score ≥950
        ├─ Send: IMMEDIATE Telegram alert
        └─ Include: Filename, score, fraud/perjury indicators
                              ↓
        Workflow 3: Weekly Statistics (Sunday 6 PM)
        ├─ Query: All documents this week
        ├─ Send: Comprehensive analysis
        └─ Include: Category breakdown, violation summary
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 10: CONFIRMATION & ACCESS                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        Telegram Bot Sends:
        ✅ "Document processed successfully!"
        ✅ Relevancy Score: 941
        ✅ Category: LEGAL
        ✅ Storage Tier: 1 (Hot - Instant Access)
        ✅ View on Dashboard: http://localhost:8501
        ✅ Cost: $0.0133
```

---

## 🗂️ FILE STORAGE LOCATIONS

### Local File System

```
/home/user/ASEAGI/
├─ data/
│  └─ telegram-inbox/          ← PRIMARY STORAGE LOCATION
│     ├─ 2025-11-17/           ← Organized by date
│     │  ├─ document_001.jpg
│     │  ├─ document_002.pdf
│     │  └─ transcript_003.txt
│     ├─ 2025-11-16/
│     └─ 2025-11-15/
```

**Key Points:**
- Files are **NEVER deleted** (permanent archive)
- Organized by **date received** (YYYY-MM-DD)
- Original filenames preserved
- Available for **re-analysis** anytime

### Database Storage (Supabase)

**Table: `general_documents` (Intake Table)**
```sql
-- Every document starts here
SELECT
    id,
    original_filename,
    file_path,  -- Points to /data/telegram-inbox/...
    content_hash,  -- MD5 for duplicate detection
    relevancy_number,  -- 0-999 score
    document_category,  -- LEGAL, BUSINESS, FAMILY
    processed_at
FROM general_documents
WHERE case_id = 'ashe-bucknor-j24-00478';
```

**Table: `legal_documents` (Legal Case Documents)**
```sql
-- Legal documents are COPIED here from general_documents
SELECT
    id,
    file_name,
    document_type,  -- TEXT, TRNS, MEDR, ORDR, etc.
    micro_number,   -- Detail-level importance (0-999)
    macro_number,   -- Case-wide significance (0-999)
    legal_number,   -- Legal weight (0-999)
    relevancy_number,  -- Composite score (0-999)
    key_quotes,
    smoking_guns,
    fraud_indicators,
    perjury_indicators,
    contains_false_statements,
    api_cost_usd,
    processed_at
FROM legal_documents
WHERE docket_number = 'J24-00478'
ORDER BY relevancy_number DESC;
```

**Table: `ceo_business_documents` (Business Documents)**
```sql
-- Business documents are COPIED here
SELECT * FROM ceo_business_documents
WHERE category = 'BUSINESS';
```

**Table: `family_documents` (Personal/Family Documents)**
```sql
-- Family documents are COPIED here
SELECT * FROM family_documents
WHERE category = 'FAMILY';
```

---

## 🎯 SCORING SYSTEM (PROJ344)

### Four Dimensions (0-999 Scale)

| Dimension | What It Measures | Example |
|-----------|-----------------|---------|
| **Micro** | Detail-level importance | Specific phrase like "mother admitted grandfather abuse" = 985 |
| **Macro** | Case-wide significance | Document affects entire case strategy = 950 |
| **Legal** | Legal weight & admissibility | Court-admissible, under oath = 980 |
| **Relevancy** | Composite weighted score | Average of above = 971 |

### Score Ranges & Actions

```
┌──────────────────────────────────────────────────────────────┐
│ 900-999: 🔥 SMOKING GUN                                      │
│ Action: Immediate Telegram alert                            │
│ Storage: Tier 1 (Hot - Instant access)                      │
│ Dashboard: Highlighted in red                               │
│ Use: Critical evidence for trial, impeachment               │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 800-899: ⚠️ CRITICAL EVIDENCE                                │
│ Action: Included in daily report                            │
│ Storage: Tier 2 (Warm - Fast access)                        │
│ Dashboard: Highlighted in orange                            │
│ Use: Strong evidence, supporting docs                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 700-799: 📌 IMPORTANT EVIDENCE                               │
│ Action: Included in weekly report                           │
│ Storage: Tier 2 (Warm - Fast access)                        │
│ Dashboard: Standard display                                 │
│ Use: Supporting documents, background                       │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 600-699: 📋 USEFUL BACKGROUND                                │
│ Action: Weekly report only                                  │
│ Storage: Tier 3 (Cool - Occasional access)                  │
│ Dashboard: Filterable view                                  │
│ Use: Context, timeline, background information              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 0-599: 📄 REFERENCE MATERIAL                                 │
│ Action: Archive only                                        │
│ Storage: Tier 4 (Cold - Rare access)                        │
│ Dashboard: Hidden by default                                │
│ Use: Historical archive, rarely needed                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 📱 EXAMPLE: Real Document Journey

### Example 1: Mother's Text Message (Smoking Gun)

**Document:** Screenshot of April 2021 text where mother admits grandfather abuse

**Telegram Upload:**
```
You: [Send image via @aseagi_legal_bot]
Bot: "Received image! Analyzing..."
```

**Processing (2-3 seconds):**
```
1. ✅ Stored: /data/telegram-inbox/2025-11-17/IMG_20211004_mother_text.jpg
2. 🔍 MD5 Hash: abc123def456... (no duplicate found)
3. 🤖 Claude Analysis:
   ├─ micro_number: 985
   ├─ macro_number: 920
   ├─ legal_number: 980
   ├─ relevancy_number: 961
   ├─ document_type: TEXT
   ├─ smoking_guns: ["Mother explicitly admits grandfather abuse"]
   ├─ fraud_indicators: []
   ├─ perjury_indicators: ["Contradicts mother's court testimony"]
   └─ api_cost_usd: $0.0127
4. 📊 Uploaded to: general_documents (ID: abc-123)
5. ➡️  Copied to: legal_documents (ID: def-456)
6. 💾 Storage Tier: 1 (Hot)
7. 📧 Telegram Alert: "🔥 SMOKING GUN DETECTED! Score: 961"
```

**Where to Find It:**
```
File System:  /data/telegram-inbox/2025-11-17/IMG_20211004_mother_text.jpg
Database:     legal_documents WHERE id='def-456'
Dashboard:    Port 8501 → "Smoking Guns" filter (≥900)
Telegram:     Hourly alert sent to @aseagi_legal_bot
Cost:         $0.0127 (one-time analysis) + $0.0001/month (storage)
```

---

### Example 2: Dr. Brown Forensic Exam

**Document:** CAL OES 2-925 form (8.2 MB PDF)

**Telegram Upload:**
```
You: [Send PDF via @aseagi_legal_bot]
Bot: "Received PDF! Analyzing..."
```

**Processing (5-7 seconds - larger file):**
```
1. ✅ Stored: /data/telegram-inbox/2025-11-17/CAL_OES_2925_Brown.pdf
2. 🔍 MD5 Hash: xyz789abc123... (no duplicate found)
3. 🤖 Claude Analysis:
   ├─ micro_number: 940
   ├─ macro_number: 960
   ├─ legal_number: 965
   ├─ relevancy_number: 955
   ├─ document_type: MEDR (Medical Record)
   ├─ smoking_guns: ["Forensic exam shows abuse evidence"]
   ├─ fraud_indicators: []
   ├─ perjury_indicators: []
   └─ api_cost_usd: $0.0189 (larger file)
4. 📊 Uploaded to: general_documents
5. ➡️  Copied to: legal_documents
6. 💾 Storage Tier: 1 (Hot) - Override: Medical = minimum Tier 2
7. 📧 Telegram Alert: "🔥 SMOKING GUN DETECTED! Score: 955"
```

**Where to Find It:**
```
File System:  /data/telegram-inbox/2025-11-17/CAL_OES_2925_Brown.pdf
Database:     legal_documents WHERE document_type='MEDR'
Dashboard:    Port 8501 → "Smoking Guns" filter
Dashboard:    Port 8502 → "Medical Records" category
Cost:         $0.0189 (analysis) + $0.00017/month (storage)
```

---

### Example 3: Low-Score Background Document

**Document:** Generic policy document

**Telegram Upload:**
```
You: [Send image via @aseagi_legal_bot]
Bot: "Received image! Analyzing..."
```

**Processing (2 seconds):**
```
1. ✅ Stored: /data/telegram-inbox/2025-11-17/policy_doc.jpg
2. 🔍 MD5 Hash: 123abc456def... (no duplicate found)
3. 🤖 Claude Analysis:
   ├─ micro_number: 220
   ├─ macro_number: 250
   ├─ legal_number: 260
   ├─ relevancy_number: 243
   ├─ document_type: DOCUMENT
   ├─ smoking_guns: []
   ├─ fraud_indicators: []
   ├─ perjury_indicators: []
   └─ api_cost_usd: $0.0112
4. 📊 Uploaded to: general_documents
5. ➡️  NOT copied to legal_documents (score < 400)
6. 💾 Storage Tier: 4 (Cold Archive)
7. 📧 No alert (score < 950)
```

**Where to Find It:**
```
File System:  /data/telegram-inbox/2025-11-17/policy_doc.jpg
Database:     general_documents ONLY (not in legal_documents)
Dashboard:    Port 8503 → CEO Dashboard → "All Documents"
Retrieval:    12 hours (Glacier - cold storage)
Cost:         $0.0112 (analysis) + $0.0000004/month (storage)
```

---

## 🚀 TELEGRAM BOT COMMANDS

### Available Commands

```
/start
    └─ Activates bot, shows welcome message

/status
    └─ Shows current case statistics
    └─ Total documents, smoking guns, critical evidence

/violations
    └─ Lists detected violations
    └─ Due process, fraud, perjury

/search [keyword]
    └─ Search documents by keyword
    └─ Returns top matches with scores

/recent
    └─ Shows last 10 documents processed
    └─ Includes scores and categories

/help
    └─ Shows all available commands
```

---

## 💰 COST BREAKDOWN

### Per-Document Costs

```
Analysis (One-time):
├─ Claude API: $0.0133/document (average)
├─ Input tokens: ~1,500 tokens × $3/M = $0.0045
└─ Output tokens: ~500 tokens × $15/M = $0.0075

Storage (Monthly - Tier 1):
├─ Supabase: $0.021/GB/month
├─ Average doc: 2.5 MB = 0.0025 GB
└─ Cost: $0.000053/month/document

Storage (Monthly - Tier 4):
├─ AWS Glacier: $0.00099/GB/month
├─ Average doc: 450 KB = 0.00045 GB
└─ Cost: $0.00000045/month/document
```

### Aggregate Costs (7TB Dataset)

```
┌────────────────────────────────────────────────────┐
│ Tier 1 (Hot):    120GB × $0.021  = $2.52/month    │
│ Tier 2 (Warm):   240GB × $0.005  = $1.20/month    │
│ Tier 3 (Cool):   380GB × $0.0125 = $4.75/month    │
│ Tier 4 (Cold):  6260GB × $0.001  = $6.26/month    │
│                                                    │
│ TOTAL: $14.73/month = $176.76/year                │
│                                                    │
│ VS Google Drive: $70/month = $840/year            │
│ SAVINGS: $663.24/year (79%)                       │
└────────────────────────────────────────────────────┘
```

---

## 🔍 MONITORING & ALERTS

### Real-Time Monitoring

**Enhanced Scanning Monitor (Port 8504):**
```
http://localhost:8504

Displays:
├─ Documents in queue
├─ Processing rate (docs/hour)
├─ ETA to completion
├─ Total API cost
├─ Recent documents (live feed)
└─ Auto-refresh every 5 seconds
```

**Master Dashboard (Port 8501):**
```
http://localhost:8501

Displays:
├─ Total documents processed
├─ Smoking guns (≥900)
├─ Critical evidence (≥800)
├─ Perjury indicators
├─ Fraud indicators
└─ Document search & filters
```

---

## ⚖️ LEGAL DOCUMENT TYPES

### Supported Types

```
TEXT  - Text messages, emails
TRNS  - Court transcripts
CPSR  - CPS reports
MEDR  - Medical records
FORN  - Forensic reports
PLCR  - Police reports
ORDR  - Court orders
DECL  - Declarations
EXPA  - Expert analysis
MOTN  - Motions
RESP  - Responses
EVID  - Evidence exhibits
OTHER - Miscellaneous
```

---

## 🛠️ TROUBLESHOOTING

### Document Not Appearing in Dashboard

**Check:**
1. ✓ File successfully uploaded to `/data/telegram-inbox/`?
2. ✓ No error in Telegram bot response?
3. ✓ Score ≥400 for `legal_documents` table?
4. ✓ Category = "LEGAL" for legal dashboard?
5. ✓ Refresh dashboard (F5) or wait 30 seconds (cache)

**Solution:**
```bash
# Check if document in database
python3 scanners/query_legal_documents.py --filter recent

# Re-scan document
python3 scanners/batch_scan_documents.py /data/telegram-inbox/2025-11-17/
```

### Duplicate Detection

**Issue:** Bot says "Already processed" but I want to re-analyze

**Solution:**
```python
# Delete from database to force re-scan
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Find document by hash
result = supabase.table('legal_documents')\
    .delete()\
    .eq('content_hash', 'abc123...')\
    .execute()

# Re-send via Telegram
```

### Storage Tier Override

**Issue:** Want to force document to Tier 1 (Hot)

**Solution:**
```python
# Manual tier override (future feature)
POST /storage/override
{
  "document_id": "abc-123",
  "force_tier": 1,
  "reason": "Referenced in active motion"
}
```

---

## 📞 TELEGRAM BOT INFO

```
Bot Name:     @aseagi_legal_bot
Bot Token:    8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI
Bot Script:   /home/user/ASEAGI/scanners/telegram_bot_enhanced.py
Status:       Active
Use:          Send documents for automatic AI analysis
```

### Start Bot

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI"
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"

# Run bot
python3 scanners/telegram_bot_enhanced.py
```

---

## 📚 RELATED DOCUMENTATION

- `/home/user/ASEAGI/CLAUDE.md` - Main project documentation
- `/home/user/ASEAGI/notes/2025-11-06-STORAGE_ROUTING_FLOWCHART.md` - Tiered storage
- `/home/user/ASEAGI/scanners/batch_scan_documents.py` - Document scanner
- `/home/user/ASEAGI/n8n-workflows/README.md` - Automation workflows
- `/home/user/ASEAGI/database/schema_types.py` - Database schema

---

**For Ashe. For Justice. For All Children.** ⚖️

*Last Updated: November 17, 2025*
