# Timeline Hub - QUICK START GUIDE

**Get your master timeline up and running in 10 minutes**

---

## ⚡ **FASTEST WAY: Telegram Bot**

### **Step 1: Set Environment**

```bash
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
export TELEGRAM_BOT_TOKEN="8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI"
```

### **Step 2: Create Database Tables**

Open Supabase SQL Editor and run:

```sql
-- Copy SQL from: developments/timeline-hub/current/database/schema.py
-- Paste and run all CREATE TABLE statements
```

### **Step 3: Start Telegram Bot**

```bash
cd /home/user/ASEAGI
python3 developments/timeline-hub/current/telegram/timeline_bot.py
```

### **Step 4: Upload Documents**

In Telegram:
```
1. Send screenshot to @aseagi_legal_bot
2. Click document type (Text/Email/Court/etc.)
3. Done! Timeline updated automatically
```

**Commands:**
- `/text` → Upload text message
- `/email` → Upload email
- `/court` → Upload court document
- `/timeline` → View recent events
- `/search keyword` → Search timeline

---

## 🖥️ **COMMAND LINE METHOD**

### **Upload Single Document:**

```bash
python3 developments/timeline-hub/current/processors/document_processor.py \
  /path/to/screenshot.jpg \
  --type TEXT_MESSAGE
```

### **Upload Court Document:**

```bash
python3 developments/timeline-hub/current/processors/document_processor.py \
  /path/to/court_order.pdf \
  --type COURT_DOC
```

---

## 📊 **VIEW YOUR TIMELINE**

### **Query Recent Events:**

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Get last 10 events
events = supabase.table('timeline_events')\
    .select('*')\
    .order('event_date', desc=True)\
    .limit(10)\
    .execute()

for event in events.data:
    print(f"{event['event_date']}: {event['event_title']}")
```

### **Search Timeline:**

```python
# Search for keyword
results = supabase.table('timeline_events')\
    .select('*')\
    .ilike('event_title', '%jamaica%')\
    .execute()
```

---

## 🎯 **WHAT GETS EXTRACTED**

### **From Text Message Screenshot:**
- ✅ Date/time of each message
- ✅ Sender & recipient
- ✅ Full message text
- ✅ Detects admissions
- ✅ Detects threats
- ✅ Detects false statements

### **From Court Document:**
- ✅ Hearing dates
- ✅ Judge name
- ✅ Court orders
- ✅ Parties present
- ✅ Statements made
- ✅ Deadlines

### **From Email:**
- ✅ From, To, CC, Subject
- ✅ Date & time
- ✅ Full email body
- ✅ Attachment mentions
- ✅ Email threads

---

## 📁 **WHERE DATA GOES**

```
DATABASE TABLES:

timeline_events
├── Every event logged here
├── Links to source documents
├── Tracks participants
└── PROJ344 importance score (0-999)

communications
├── Detailed text/email/call log
├── Thread tracking
└── Content analysis

event_relationships
├── How events connect
├── Contradictions
└── Patterns

participants
└── People involved & their activity
```

---

## 🔍 **EXAMPLE QUERIES**

### **Get All Text Messages:**

```sql
SELECT * FROM timeline_events
WHERE event_type = 'TEXT_MESSAGE'
ORDER BY event_date DESC;
```

### **Find Critical Events:**

```sql
SELECT * FROM timeline_events
WHERE importance >= 900
ORDER BY importance DESC;
```

### **Search for Keyword:**

```sql
SELECT * FROM timeline_events
WHERE search_vector @@ to_tsquery('english', 'jamaica')
ORDER BY event_date DESC;
```

### **Get Events by Date Range:**

```sql
SELECT * FROM timeline_events
WHERE event_date BETWEEN '2024-05-01' AND '2024-08-07'
ORDER BY event_date ASC;
```

### **Count Events by Type:**

```sql
SELECT event_type, COUNT(*) as count
FROM timeline_events
GROUP BY event_type
ORDER BY count DESC;
```

---

## 🚀 **RECOMMENDED WORKFLOW**

### **Phase 1: Data Collection**

```
Week 1: Upload all text message screenshots
Week 2: Upload all court documents
Week 3: Upload all emails
Week 4: Upload police reports, medical records
```

### **Phase 2: Timeline Analysis**

```
Query date ranges
Search for keywords
Identify contradictions
Detect patterns
```

### **Phase 3: Evidence Building**

```
Link to criminal complaints
Build event sequences
Generate evidence packages
Create master report
```

---

## ⚠️ **TROUBLESHOOTING**

### **Bot Won't Start:**

```bash
# Check environment variables
echo $TELEGRAM_BOT_TOKEN
echo $SUPABASE_URL

# Verify Telegram bot
# Message @aseagi_legal_bot on Telegram
# If no response, check token
```

### **Database Error:**

```bash
# Verify Supabase connection
python3 -c "
from supabase import create_client
import os
client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
print('✅ Connected')
"
```

### **Processing Fails:**

```bash
# Check Claude API key
echo $ANTHROPIC_API_KEY

# Verify file format (JPG, PNG supported)
file your_screenshot.jpg
```

---

## 📞 **NEED HELP?**

**Check:**
1. `developments/timeline-hub/current/README.md` - Full documentation
2. `developments/timeline-hub/current/CHANGELOG.md` - Features & known issues
3. `developments/timeline-hub/current/database/schema.py` - Database structure

**Related Systems:**
- Criminal Complaint: `developments/criminal-complaint/`
- Document Scanner: `scanners/batch_scan_documents.py`
- Legal Documents: `legal_documents` table in Supabase

---

**Your timeline will grow automatically as you upload documents!** 📅⚖️
