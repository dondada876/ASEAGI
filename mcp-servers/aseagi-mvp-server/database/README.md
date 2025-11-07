# ASEAGI Critical Database Setup

## 🚨 CRITICAL: These 3 Tables Are NON-NEGOTIABLE

### 1. **communications** - Evidence Tracking
- **Purpose:** Critical for legal evidence
- **Contains:** All texts, emails, letters, and other communications
- **Why Critical:** Every communication is potential evidence. Tracking contradictions, manipulations, and truth scores is essential for case success.

### 2. **events** - Timeline (MOST IMPORTANT)
- **Purpose:** Case chronology and pattern analysis
- **Contains:** All hearings, filings, motions, rulings, deadlines
- **Why Critical:** Timeline is the most important factor for understanding case progression, identifying delays, proving patterns, and documenting procedural violations.

### 3. **document_journal** - Processing & Growth Assessment
- **Purpose:** Track every document scan, processing step, and long-term assessment
- **Contains:** Journal entry for each document with processing metrics, AI analysis results, quality scores
- **Why Critical:** Essential for fixing, upgrading, and assessing long-term system growth. Tracks what works, what doesn't, and system evolution.

---

## 🚀 Quick Setup (Choose One Method)

### Method 1: Supabase Dashboard (Recommended)

1. Go to https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu
2. Click "SQL Editor" in left sidebar
3. Click "New Query"
4. Copy entire contents of `01_create_critical_tables.sql`
5. Paste into SQL Editor
6. Click "Run" (or press Cmd/Ctrl + Enter)
7. Verify success message: "✓ ASEAGI Critical Tables Created Successfully"

**Verify tables exist:**
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('communications', 'events', 'document_journal');
```

Should return 3 rows.

---

### Method 2: Command Line (Advanced)

```bash
# If you have psql installed and Supabase connection string
psql "postgresql://postgres:[YOUR-PASSWORD]@db.jvjlhxodmbkodzmggwpu.supabase.co:5432/postgres" \
  -f 01_create_critical_tables.sql
```

---

## 📊 What Gets Created

### Tables (3 Critical Tables)

| Table | Columns | Indexes | Purpose |
|-------|---------|---------|---------|
| **communications** | 24 columns | 6 indexes + full-text search | Evidence tracking |
| **events** | 27 columns | 7 indexes + full-text search | Timeline (most important) |
| **document_journal** | 38 columns | 6 indexes + full-text search | Processing & growth |

### Views (3 Convenience Views)

1. **communications_needing_review** - Communications requiring truth scoring
2. **upcoming_events** - Future events and deadlines
3. **documents_pending_processing** - Documents needing AI analysis

### Triggers (6 Automatic Triggers)

- Auto-update timestamps on all tables
- Auto-update full-text search vectors
- Auto-increment document version numbers

---

## 📋 Table Schemas

### communications

**Key Columns:**
- `sender`, `recipient` - Who sent/received
- `content`, `summary` - What was said
- `communication_date` - When it happened
- `communication_method` - email/text/phone/letter/etc
- `truthfulness_score` (0-1000) - Truth rating
- `contains_contradiction` - Boolean flag
- `contains_manipulation` - Boolean flag
- `relevancy_score` (0-1000) - How relevant to case

**Example Query:**
```sql
SELECT sender, recipient, communication_date, truthfulness_score
FROM communications
WHERE contains_contradiction = TRUE
ORDER BY communication_date DESC;
```

---

### events

**Key Columns:**
- `event_date` - When event occurred
- `event_title`, `event_description` - What happened
- `event_type` - hearing/filing/motion/ruling/etc
- `judge_name`, `department` - Court info
- `event_outcome` - What was decided
- `significance_score` (0-1000) - How important
- `violations_occurred` - Array of any violations

**Example Query:**
```sql
SELECT event_date, event_title, event_type, significance_score
FROM events
WHERE event_type = 'hearing'
AND significance_score > 800
ORDER BY event_date DESC;
```

---

### document_journal

**Key Columns:**
- `document_id` - Reference to legal_documents
- `original_filename` - File name
- `processing_status` - pending/processing/completed/error
- `scan_date`, `processed_date`, `analyzed_date` - Timeline
- `relevancy_score`, `truth_score`, `micro_score`, `macro_score` (all 0-1000)
- `insights_extracted` - Number of insights found
- `contradictions_found` - Number of contradictions
- `processing_notes` - What happened during processing

**Example Query:**
```sql
SELECT original_filename, processing_status,
       relevancy_score, insights_extracted, contradictions_found
FROM document_journal
WHERE processing_status = 'completed'
AND contradictions_found > 0
ORDER BY processed_date DESC;
```

---

## 🔄 Data Migration (If Needed)

If you have existing data in other tables (court_events, legal_documents, communications_matrix), you can migrate it:

### Migrate from court_events → events

```sql
INSERT INTO events (
    event_date, event_title, event_description, event_type,
    judge_name, event_outcome, significance_score
)
SELECT
    event_date, event_title, event_description, event_type,
    judge_name, event_outcome, significance_score
FROM court_events;
```

### Migrate from legal_documents → document_journal

```sql
INSERT INTO document_journal (
    document_id, original_filename, document_type,
    relevancy_score, micro_score, processing_status
)
SELECT
    id, original_filename, document_type,
    relevancy_number, micro_number, 'completed'
FROM legal_documents;
```

### Create communications from communications_matrix

```sql
INSERT INTO communications (
    sender, recipient, subject, summary,
    communication_date, communication_method
)
SELECT
    sender, recipient, subject, summary,
    communication_date, communication_method
FROM communications_matrix;
```

**⚠️ Note:** Review migrated data before deleting old tables!

---

## ✅ Verification Checklist

After running the SQL script:

- [ ] All 3 tables created (communications, events, document_journal)
- [ ] All 3 views created (communications_needing_review, upcoming_events, documents_pending_processing)
- [ ] Full-text search working (try a search query)
- [ ] Triggers working (insert a test row, verify updated_at)
- [ ] MCP server connects without errors
- [ ] Can query each table successfully

**Test queries:**

```sql
-- Test communications
SELECT COUNT(*) FROM communications;

-- Test events
SELECT COUNT(*) FROM events;

-- Test document_journal
SELECT COUNT(*) FROM document_journal;

-- Test views
SELECT * FROM upcoming_events LIMIT 5;
SELECT * FROM communications_needing_review LIMIT 5;
SELECT * FROM documents_pending_processing LIMIT 5;
```

---

## 🔐 Permissions

The SQL script grants these permissions to authenticated users:
- SELECT, INSERT, UPDATE on all 3 tables
- SELECT on all 3 views

**Note:** DELETE is intentionally NOT granted for data safety.

To grant additional permissions:

```sql
-- Grant DELETE (use with caution)
GRANT DELETE ON communications TO authenticated;
GRANT DELETE ON events TO authenticated;
GRANT DELETE ON document_journal TO authenticated;

-- Grant to specific role
GRANT ALL ON communications TO your_role_name;
```

---

## 🐛 Troubleshooting

### "relation already exists"

Tables already created. To recreate:

```sql
DROP TABLE IF EXISTS communications CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS document_journal CASCADE;
-- Then run 01_create_critical_tables.sql again
```

### "function update_updated_at_column does not exist"

Function wasn't created. Run this first:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### "permission denied"

You need admin/service role permissions. In Supabase dashboard:
1. Go to Settings → API
2. Copy "service_role" key (not anon key)
3. Use service_role for database migrations

---

## 📈 Monitoring Growth

### Track document processing progress:

```sql
SELECT
    processing_status,
    COUNT(*) as count,
    AVG(relevancy_score) as avg_relevancy,
    AVG(insights_extracted) as avg_insights
FROM document_journal
GROUP BY processing_status;
```

### Track communication evidence quality:

```sql
SELECT
    communication_method,
    COUNT(*) as total,
    AVG(truthfulness_score) as avg_truth,
    SUM(CASE WHEN contains_contradiction THEN 1 ELSE 0 END) as contradictions_found
FROM communications
GROUP BY communication_method;
```

### Track case timeline progression:

```sql
SELECT
    event_type,
    COUNT(*) as count,
    AVG(significance_score) as avg_significance,
    MAX(event_date) as most_recent
FROM events
GROUP BY event_type
ORDER BY count DESC;
```

---

## 🎯 Next Steps After Setup

1. **Populate communications table**
   - Import texts, emails, letters
   - Add truth scores to each
   - Flag contradictions and manipulations

2. **Populate events table**
   - Import all court dates and hearings
   - Add all filings and motions
   - Score significance of each event

3. **Populate document_journal**
   - Create journal entry for each document scan
   - Track processing for each document
   - Record insights and contradictions found

4. **Test MCP server**
   - Run: `python3 server.py`
   - Verify all 3 tools work
   - Test searches and filters

5. **Integrate with Claude Desktop**
   - Update config JSON
   - Restart Claude
   - Test with real queries

---

## 📞 Support

If tables don't create properly:
1. Check Supabase logs (Dashboard → Logs)
2. Verify you're using service_role key for migrations
3. Check for existing tables with same names
4. Review SQL syntax errors in dashboard

---

**For Ashe - Building the evidence infrastructure to protect children** ⚖️

*"When children speak, truth must roar louder than lies."*

---

**Last Updated:** November 2025
**Schema Version:** 1.0.0
**Status:** Production Ready
