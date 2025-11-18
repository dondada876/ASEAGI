# CRIMINAL COMPLAINT SYSTEM - QUICK REFERENCE

**Current Version:** v1.0 (Limited)
**Enhanced Version:** v2.0 (Planned)

---

## ⚡ **QUICK ANSWERS**

### **Q: How do I upload/re-upload documents with different analysis levels?**

**Current (v1.0):**
- Only full-page analysis
- Upload via Telegram bot only
- No re-analysis with different granularity

**Needed (v2.0):**
```bash
# Web interface with granularity options
curl -X POST http://your-server/upload \
  -F "file=@document.pdf" \
  -F "analysis_level=quarter_page" \
  -F "extract_statements=true"
```

### **Q: Where are documents stored?**

```
┌─────────────────────────────────────────────┐
│ CURRENT STORAGE                             │
├─────────────────────────────────────────────┤
│ Local:     /data/telegram-inbox/YYYY-MM-DD │
│ Database:  Supabase legal_documents         │
│ Cloud:     NONE                             │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ RECOMMENDED STORAGE (v2.0)                  │
├─────────────────────────────────────────────┤
│ Tier 1: Digital Ocean Droplet (hot)        │
│ Tier 2: Backblaze B2 (warm backup)         │
│ Tier 3: Google Drive (cold archive)        │
│ Database: Supabase (metadata)              │
└─────────────────────────────────────────────┘
```

### **Q: What is the core focus of this code?**

**Purpose:**
1. **Prove Perjury** - Document false statements under oath
2. **Build Criminal Case** - Evidence package for DA
3. **Automate Analysis** - Find contradictions automatically
4. **Generate Reports** - Prosecution-ready documents

**Use Cases:**
- Criminal referrals (PC §118.1 perjury)
- CCP §473 fraud motions
- Appellate briefs
- Impeachment evidence

### **Q: Where should this code be placed in the hierarchy?**

```
developments/criminal-complaint/    ← Feature-specific
  ├── v1.0-2025-11-17/             ← Current version
  └── v2.0-2025-11-18/             ← Enhanced version (planned)

NOT in:
  ❌ scanners/ (production only)
  ❌ dashboards/ (production only)
  ❌ database/ (production schemas only)
```

### **Q: Why only 5 complaints? Should be unlimited!**

**YOU'RE RIGHT!**

**Current Limitation (v1.0):**
- Hardcoded in schema.py
- Must edit code to add more
- Manual process

**Solution (v2.0):**
```python
# Automatic complaint generation
contradictions = detect_all_contradictions()
for contradiction in contradictions:
    if contradiction.is_perjury():
        complaint = generate_complaint(contradiction)
        complaints.append(complaint)

# Result: UNLIMITED complaints
```

### **Q: How to do micro-analysis on ALL statements in documents?**

**Needed: Statement Extraction Engine**

```python
# For EACH document:
statements = extract_statements(document)

for statement in statements:
    store_in_database({
        'speaker': 'MOT',  # Mother
        'text': "I'm terrified he will abscond to Jamaica",
        'type': 'claim',
        'subject': 'flight_risk',
        'date_made': '2024-08-12',
        'verifiable': True,
        'page_number': 3,
        'section': 'quarter_2'
    })

# Result: ALL statements tracked individually
```

### **Q: How to create event timeline for macro-analysis?**

**Needed: Timeline System**

```python
# Build timeline from:
timeline.add_event({
    'date': '2024-08-12',
    'type': 'declaration_filed',
    'statements_made': [stmt1_id, stmt2_id, stmt3_id]
})

timeline.add_event({
    'date': '2024-05-01',
    'type': 'text_message',
    'statements_made': [stmt4_id]
})

# Cross-reference:
contradictions = timeline.find_contradictions()
# "Statement on 8/12 contradicts 201 texts from 5/1-8/7"
```

### **Q: What's the current workflow?**

```
USER ACTION          SYSTEM PROCESS              OUTPUT
───────────────────────────────────────────────────────────
Send to Telegram  →  Store in droplet        →  File saved
                  →  Calculate hash          →  Check dups
                  →  Send to Claude          →  Full page analysis
                  →  Store in Supabase       →  Single record

Run analyzer      →  Load 5 hardcoded claims →  Search keywords
                  →  Calculate scores        →  Contradiction scores
                  →  Generate report         →  MASTER_PERJURY_REPORT.md

LIMITATIONS:
  ❌ No page granularity
  ❌ No statement extraction
  ❌ No timeline
  ❌ Only 5 complaints
  ❌ Manual everything
```

---

## 📊 **SYSTEM CAPABILITIES**

### **Current v1.0 (What It CAN Do):**

✅ Analyze documents with PROJ344 scoring
✅ Search 5 predefined false statements
✅ Calculate contradiction scores (0-999)
✅ Generate master report (markdown)
✅ Visual dashboard (port 8506)
✅ Store documents in Supabase
✅ Track via Telegram bot

### **Current v1.0 (What It CANNOT Do):**

❌ Granular analysis (quarter/half page)
❌ Extract ALL statements automatically
❌ Build event timeline
❌ Detect contradictions automatically
❌ Generate unlimited complaints
❌ Cross-reference across timeline
❌ Web upload interface
❌ Multi-tier cloud storage
❌ Re-upload for different analysis levels

---

## 🚀 **HOW TO USE (Current v1.0)**

### **Basic Analysis:**

```bash
# Set credentials
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"

# Run analysis
cd /home/user/ASEAGI
python3 developments/criminal-complaint/current/analyzer.py

# Output:
# - MASTER_PERJURY_REPORT.md
# - criminal_complaint_analysis.json
```

### **Dashboard:**

```bash
streamlit run developments/criminal-complaint/current/dashboard.py --server.port 8506

# Open: http://localhost:8506
```

### **Specific Claim:**

```bash
python3 developments/criminal-complaint/current/analyzer.py \
  --claim FS-001-JAMAICA-FLIGHT
```

---

## 🎯 **WHAT NEEDS TO BE BUILT (v2.0)**

### **Priority 1: Statement Extraction**
- Extract ALL statements from documents
- Track speaker, type, subject, date
- Store in new `document_statements` table
- **Effort:** 40 hours

### **Priority 2: Timeline System**
- Build event timeline from documents
- Cross-reference statements by date
- Detect timeline contradictions
- **Effort:** 30 hours

### **Priority 3: Dynamic Complaints**
- Automatic contradiction detection
- Unlimited complaint generation
- Evidence auto-linking
- **Effort:** 30 hours

### **Priority 4: Granular Analysis**
- Quarter/half page options
- Re-upload capability
- Web upload interface
- **Effort:** 40 hours

### **Priority 5: Storage Enhancement**
- Backblaze B2 integration
- Google Drive sync
- Multi-tier routing
- **Effort:** 30 hours

**TOTAL:** ~170 hours (4-5 weeks)

---

## 💡 **EXAMPLE: Enhanced Workflow (v2.0)**

### **Scenario: New Document Upload**

```
1. USER uploads declaration via web interface

2. SYSTEM asks: "Analysis granularity?"
   [ ] Full page only
   [X] Half page (2 sections)
   [X] Quarter page (4 sections)
   [X] Extract all statements ← ALWAYS

3. SYSTEM processes:
   - Full page → PROJ344 score: 875
   - Half page top → Score: 920 (critical)
   - Half page bottom → Score: 830 (important)
   - Statement extraction → 17 statements found

4. SYSTEM stores:
   - legal_documents table (1 record)
   - document_statements table (17 records)

5. SYSTEM analyzes statements:
   - Statement #3: "I'm terrified he will abscond to Jamaica"
   - Cross-reference timeline: 201 texts May-Aug, ZERO Jamaica mentions
   - CONTRADICTION DETECTED

6. SYSTEM generates complaint:
   - Complaint #6 (auto-generated, not hardcoded)
   - Subject: False Jamaica flight risk claim
   - Penal Code: PC §118.1
   - Evidence: 201 text messages
   - Prosecutability: 95/100

7. SYSTEM updates timeline:
   - Event added: Aug 12, 2024 - Declaration filed
   - Statements linked: #3, #7, #11
   - Contradictions flagged: 3 discrepancies

8. USER receives:
   - Auto-generated complaint report
   - Timeline visualization
   - Evidence package
   - Ready for DA submission
```

---

## 📚 **RELATED DOCUMENTATION**

- **WORKFLOW_ANALYSIS.md** - Complete technical analysis (this doc)
- **developments/criminal-complaint/current/GUIDE.md** - User guide (50 pages)
- **developments/criminal-complaint/current/README.md** - Feature overview
- **docs/DEVELOPMENT_POLICY_VERSIONING.md** - Versioning policy

---

## 🔗 **STORAGE LINKS (Planned v2.0)**

```
Backblaze B2 Setup:
  1. Create bucket: aseagi-legal-documents
  2. Generate application key
  3. Install SDK: pip install b2sdk
  4. Configure in storage_router.py

Google Drive Setup:
  1. Enable Google Drive API
  2. Create service account
  3. Download credentials.json
  4. Install SDK: pip install google-api-python-client
  5. Configure in gdrive_client.py

Supabase Link:
  - Already configured
  - URL: https://jvjlhxodmbkodzmggwpu.supabase.co
  - Stores metadata only, not files
```

---

## ⚠️ **LIMITATIONS TO KNOW**

### **v1.0 Limitations:**

1. **Only 5 Complaints** - Hardcoded in schema.py
2. **No Statement Extraction** - Document-level only
3. **No Timeline** - Can't cross-reference across time
4. **Full Page Only** - No granular analysis
5. **Single Storage** - Droplet + Supabase only
6. **Telegram Only** - No web upload
7. **Manual Detection** - No auto-contradiction finding

### **What v1.0 Does Well:**

1. ✅ Fast document-level analysis
2. ✅ PROJ344 scoring proven accurate
3. ✅ Good keyword search
4. ✅ Clean master reports
5. ✅ Visual dashboard helpful
6. ✅ Telegram integration works

---

## 🎯 **DECISION: What to Build First?**

**Option A: Statement Extraction Engine (Recommended)**
- Foundation for everything else
- Enables micro-analysis
- Unlocks timeline system
- **Start here**

**Option B: Web Upload Interface**
- Improves user experience
- Enables granularity selection
- But useless without statement extraction

**Option C: Timeline System**
- Powerful macro-analysis
- But needs statements first
- Can't build without extraction

**RECOMMENDATION: Build in this order:**
1. Statement Extraction (Week 1-2)
2. Timeline System (Week 3)
3. Contradiction Detection (Week 4)
4. Dynamic Complaints (Week 5)
5. Web Upload (Week 6)

---

**Questions? See WORKFLOW_ANALYSIS.md for full details.**
