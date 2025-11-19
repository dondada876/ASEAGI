# Master Timeline & Communications Hub

**Version:** 1.0
**Date:** 2025-11-17
**Status:** Development
**Purpose:** Unified timeline tracking across ALL data sources

---

## 🎯 **WHAT THIS DOES**

Creates a **master timeline** of ALL events and communications in your case:

### **Tracks:**
- ✅ Court hearings & orders
- ✅ Text messages (screenshots)
- ✅ Emails
- ✅ Police reports
- ✅ Medical records
- ✅ Declarations filed
- ✅ Incidents
- ✅ Statements made

### **Extracts:**
- Events (when something happened)
- Communications (who said what to whom)
- Statements (specific quotes)
- Participants (who was involved)
- Relationships (how events connect)

### **Analyzes:**
- Timeline gaps
- Contradictions across time
- Patterns of behavior
- Event correlations

---

## 🚀 **QUICK START**

### **1. Upload via Telegram** (Easiest)

```bash
# Start the bot
python3 telegram/timeline_bot.py

# Then in Telegram:
1. Send screenshot to bot
2. Select document type (text/email/court/police)
3. Bot processes and extracts timeline data
4. Done!
```

**Telegram Commands:**
```
/text    - Mark as text message screenshot
/email   - Mark as email screenshot
/court   - Mark as court document
/police  - Mark as police report

Then send your photo!

/timeline - View recent events
/search jamaica - Search timeline
/stats - View statistics
```

### **2. Command Line Upload**

```bash
# Process a text message screenshot
python3 processors/document_processor.py \
  /path/to/text_screenshot.jpg \
  --type TEXT_MESSAGE

# Process court document
python3 processors/document_processor.py \
  /path/to/court_order.pdf \
  --type COURT_DOC

# Process email screenshot
python3 processors/document_processor.py \
  /path/to/email.png \
  --type EMAIL
```

### **3. View Timeline** (Dashboard - Coming Soon)

```bash
streamlit run dashboards/timeline_dashboard.py --server.port 8507
```

---

## 📊 **DATABASE SCHEMA**

### **Main Tables:**

**1. `timeline_events`** - Master event timeline
- Every event logged here
- Links to source documents
- Tracks participants
- PROJ344-style importance scoring (0-999)

**2. `communications`** - Detailed communication log
- Text messages
- Emails
- Phone calls
- Links to timeline events

**3. `event_relationships`** - How events connect
- Contradictions
- Cause → Effect
- Patterns
- Timeline gaps

**4. `participants`** - People involved
- Participant codes (MOT, FAT, MIN, CPS, etc.)
- Contact info
- Activity summary

**5. `timeline_phases`** - Case periods
- Pre-detention
- Detention
- Post-detention
- Reunification

---

## 🔧 **SETUP**

### **1. Create Database Tables**

```bash
# Run schema migrations
psql -h your-supabase-host -U postgres -f database/migrations/001_create_tables.sql
```

Or use Supabase dashboard:
1. Open SQL Editor
2. Copy SQL from `database/schema.py`
3. Run each CREATE TABLE statement

### **2. Set Environment Variables**

```bash
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
export TELEGRAM_BOT_TOKEN="your_bot_token"  # For Telegram bot
```

### **3. Install Dependencies**

```bash
pip install supabase anthropic python-telegram-bot pillow
```

---

## 📱 **USAGE EXAMPLES**

### **Example 1: Upload Text Message Screenshot**

```bash
# Via Telegram:
/text
[send screenshot]

# Bot extracts:
- Date/time of each message
- Sender & recipient
- Full message text
- Detects admissions/threats
- Creates timeline events
```

### **Example 2: Upload Court Order**

```bash
# Via command line:
python3 processors/document_processor.py court_order.pdf --type COURT_DOC

# Extracts:
- Hearing date
- Judge name
- Court orders issued
- Parties present
- Deadlines
```

### **Example 3: Search Timeline**

```python
# Via Telegram:
/search jamaica

# Returns:
- All events mentioning "jamaica"
- Sorted by date
- With context
```

### **Example 4: View Timeline Range**

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get events between May and August 2024
events = supabase.table('timeline_events')\
    .select('*')\
    .gte('event_date', '2024-05-01')\
    .lte('event_date', '2024-08-31')\
    .order('event_date')\
    .execute()

for event in events.data:
    print(f"{event['event_date']}: {event['event_title']}")
```

---

## 🎨 **DASHBOARD** (Coming Soon)

Will include:
- Visual timeline with zoom
- Filter by event type
- Search functionality
- Contradiction highlighting
- Participant activity view
- Pattern detection

---

## 📊 **EVENT TYPES**

```
COURT_HEARING       - Court appearances
COURT_ORDER         - Judge's orders/rulings
DECLARATION_FILED   - Sworn declarations
TEXT_MESSAGE        - Text communications
EMAIL               - Email communications
PHONE_CALL          - Phone conversations
POLICE_REPORT       - Law enforcement reports
INCIDENT            - Incidents (abuse, neglect, etc.)
DOCUMENT_FILED      - Legal filings
STATEMENT_MADE      - Statements on record
EVIDENCE_SUBMITTED  - Evidence filed
VIOLATION_DETECTED  - Detected violations
```

---

## 👥 **PARTICIPANT CODES**

```
MOT      - Mother (Mariyam Yonas Rufael)
FAT      - Father (Don Bucknor)
MIN      - Minor (Ashe Bucknor)
CPS      - CPS social worker
JUD      - Judge
POL      - Police officer
MED      - Medical professional
ATT_MOT  - Mother's attorney
ATT_FAT  - Father's attorney
ATT_MIN  - Minor's counsel
```

---

## 🔍 **SEARCH & QUERY**

### **Search Events:**

```sql
-- Search by keyword
SELECT * FROM timeline_events
WHERE search_vector @@ to_tsquery('english', 'jamaica')
ORDER BY event_date DESC;

-- Get critical events
SELECT * FROM timeline_events
WHERE importance >= 900
ORDER BY importance DESC, event_date DESC;

-- Get events by participant
SELECT * FROM timeline_events
WHERE 'MOT' = ANY(participants)
ORDER BY event_date DESC;
```

### **Analyze Timeline Gaps:**

```sql
-- Find gaps between events
WITH event_gaps AS (
  SELECT
    event_date,
    event_title,
    LAG(event_date) OVER (ORDER BY event_date) as prev_date,
    event_date - LAG(event_date) OVER (ORDER BY event_date) as gap_days
  FROM timeline_events
  WHERE event_type = 'TEXT_MESSAGE'
)
SELECT * FROM event_gaps
WHERE gap_days > 7  -- Gaps longer than 7 days
ORDER BY gap_days DESC;
```

---

## 🔗 **INTEGRATION**

### **Link to Criminal Complaint System:**

```python
# Timeline events can reference complaints
event = {
    'event_type': 'DECLARATION_FILED',
    'event_date': '2024-08-12',
    'event_title': 'Mother files false Jamaica claim',
    'contains_false_statement': True,
    'related_complaint_id': 'FS-001-JAMAICA-FLIGHT'  # From complaint system
}
```

### **Link to Legal Documents:**

```python
# Events reference source documents
event = {
    'event_title': 'Text message sent',
    'source_document_id': 'uuid-of-legal-document',  # From legal_documents table
    'source_page_number': 2
}
```

---

## 📁 **FILE STRUCTURE**

```
v1.0-2025-11-17/
├── README.md                    (this file)
├── CHANGELOG.md                 (version history)
├── VERSION.txt                  (1.0)
│
├── database/
│   ├── schema.py               (SQL CREATE statements)
│   ├── migrations/             (schema migrations)
│   └── queries.py              (common queries)
│
├── processors/
│   └── document_processor.py   (multi-source processor)
│
├── telegram/
│   └── timeline_bot.py         (Telegram integration)
│
├── dashboards/
│   └── timeline_dashboard.py   (visualization - WIP)
│
└── cli/
    └── timeline_cli.py         (command line tools)
```

---

## 🎯 **USE CASES**

### **1. Prove Timeline Contradictions**

**Scenario:** Mother claims father "has history of ignoring court orders"

**Timeline Analysis:**
```
Query: Get all court order events
Result: Good Cause Report (Aug 7) was FIRST lawful retention
Proves: No "history" - this was the first time
Evidence: Timeline shows zero prior violations
```

### **2. Track Communication Patterns**

**Scenario:** Analyze mother's accessibility

**Timeline Analysis:**
```
Query: Count text messages by sender
Period: May 1 - Aug 7, 2024
Result: 201 texts from mother, all received and responded to
Proves: Mother was accessible (contradicts "unresponsive" claim)
```

### **3. Detect Timeline Gaps**

**Scenario:** Find suspicious gaps in communication

**Timeline Analysis:**
```
Query: Find gaps >3 days in text messages
Result: No gaps - continuous communication
Proves: No evidence of avoidance or hiding
```

### **4. Build Event Sequences**

**Scenario:** Show cause → effect relationships

**Timeline Analysis:**
```
Event 1: Aug 7 - Good Cause Report issued
Event 2: Aug 9 - Father retains child (lawful)
Event 3: Aug 12 - Mother files false declaration
Relationship: Declaration filed AFTER lawful retention
Proves: Mother knew retention was lawful but claimed otherwise
```

---

## ⚠️ **LIMITATIONS** (v1.0)

- ❌ No web upload interface yet (Telegram only)
- ❌ Dashboard not complete
- ❌ No automated relationship detection (manual linking)
- ❌ No pattern detection engine
- ❌ No multi-tier storage integration

**Planned for v1.1:**
- Web upload interface
- Complete timeline dashboard
- Automated relationship detection
- Pattern detection (recurring behaviors)
- Backblaze/Google Drive integration

---

## 🔜 **NEXT STEPS**

### **Phase 1: Data Collection** (Current)
1. Upload all text messages via Telegram
2. Upload all court documents
3. Upload all emails

### **Phase 2: Timeline Building**
1. Run analysis on all events
2. Detect relationships
3. Identify contradictions

### **Phase 3: Complaint Integration**
1. Link timeline events to complaints
2. Use timeline to prove contradictions
3. Generate evidence packages

---

## 📞 **SUPPORT**

**Issues:**
- Schema problems → Check database/schema.py
- Processing errors → Check processor logs
- Telegram bot issues → Check bot token and permissions

**Related:**
- Criminal Complaint System: `developments/criminal-complaint/`
- Document Scanner: `scanners/batch_scan_documents.py`
- Legal Documents DB: `legal_documents` table

---

**For Ashe. For Justice. For Timeline Truth.** 📅⚖️
