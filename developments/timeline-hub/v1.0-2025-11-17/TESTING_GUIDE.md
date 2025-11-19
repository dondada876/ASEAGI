# Timeline Hub v1.0 - Complete Testing Guide

**Version:** 1.0
**Date:** 2025-11-17
**Purpose:** Step-by-step testing instructions for isolated timeline hub deployment
**Time Required:** 15-20 minutes

---

## 🎯 Testing Objectives

This guide will help you:

1. ✅ Deploy timeline hub schema to Supabase
2. ✅ Verify complete isolation from other ASEAGI systems
3. ✅ Insert realistic test data
4. ✅ Run queries to verify functionality
5. ✅ Test rollback safety
6. ✅ Prepare for production use

---

## 📋 Prerequisites

Before you begin, ensure you have:

- [ ] Supabase account access
- [ ] Supabase project URL and service key
- [ ] SQL Editor access in Supabase dashboard
- [ ] Basic familiarity with PostgreSQL

**No other ASEAGI systems required!** Timeline hub is completely self-contained.

---

## 🚀 Step 1: Deploy Database Schema (5 minutes)

### 1.1 Open Supabase SQL Editor

1. Go to https://app.supabase.com/
2. Select your project
3. Click "SQL Editor" in left sidebar
4. Click "+ New query"

### 1.2 Run Schema Creation Script

1. Open `database/001_create_schema.sql` from this directory
2. Copy the entire contents (600+ lines)
3. Paste into Supabase SQL Editor
4. Click "Run" (or press Ctrl+Enter)

### 1.3 Verify Schema Creation

You should see output like:

```
NOTICE:  Created table: timeline_events
NOTICE:  Created table: timeline_communications
NOTICE:  Created table: timeline_participants
NOTICE:  Created table: timeline_relationships
NOTICE:  Created table: timeline_phases
NOTICE:  Created table: timeline_processing_queue
NOTICE:  Created table: timeline_schema_version
NOTICE:  Created function: update_participant_stats
NOTICE:  Created function: calculate_time_gap
NOTICE:  ✅ Timeline Hub Schema v1.0 Deployed Successfully!
```

### 1.4 Confirm Tables Exist

In the Supabase "Table Editor":

- [ ] `timeline_events`
- [ ] `timeline_communications`
- [ ] `timeline_participants`
- [ ] `timeline_relationships`
- [ ] `timeline_phases`
- [ ] `timeline_processing_queue`
- [ ] `timeline_schema_version`

**All tables should have the `timeline_` prefix.**

---

## ✅ Step 2: Verify Isolation (3 minutes)

### 2.1 Run Isolation Verification Script

1. Open `database/004_verify_isolation.sql`
2. Copy entire contents
3. Paste into new SQL Editor query
4. Click "Run"

### 2.2 Review Test Results

You should see 12 tests passing:

```
✅ TEST 1: No external foreign key dependencies
✅ TEST 2: Self-contained participant registry (9 participants)
✅ TEST 3: Timeline events query independence
✅ TEST 4: Communication tracking independence
✅ TEST 5: Relationship tracking independence
✅ TEST 6: Timeline phase tracking independence
✅ TEST 7: Complex join queries work independently
✅ TEST 8: Full-text search works independently
✅ TEST 9: Helper functions work independently
✅ TEST 10: Optional external linking (nullable field)
✅ TEST 11: No dependencies on ASEAGI production tables
✅ TEST 12: Rollback safety simulation

✅ ISOLATION VERIFICATION COMPLETE
```

### 2.3 Confirm Initial Data

Check `timeline_participants` table:

```sql
SELECT participant_code, full_name, role
FROM timeline_participants
ORDER BY participant_code;
```

**Expected:** 9 participants (MOT, FAT, MIN, CPS, JUD, POL, MED, ATT_MOT, ATT_FAT, ATT_MIN)

---

## 📊 Step 3: Insert Test Data (2 minutes)

### 3.1 Run Test Data Script

1. Open `database/003_test_data.sql`
2. Copy entire contents
3. Paste into new SQL Editor query
4. Click "Run"

### 3.2 Verify Test Data Inserted

You should see:

```
NOTICE:  Test Events Inserted: 5
NOTICE:  ✅ All 5 test events inserted successfully
NOTICE:  Test Communications Inserted: 3
NOTICE:  ✅ All 3 test communications inserted successfully
NOTICE:  Test Relationships Inserted: 3
NOTICE:  ✅ All 3 test relationships inserted successfully
NOTICE:  Test Phases Inserted: 2
NOTICE:  ✅ All 2 test phases inserted successfully
NOTICE:  ✅ TEST DATA INSERTION COMPLETE
```

### 3.3 Browse Test Data

**View Events:**
```sql
SELECT
    event_date,
    event_time,
    event_title,
    importance,
    participants
FROM timeline_events
ORDER BY event_date, event_time;
```

**Expected:** 5 events from August 2024 custody scenario

**View Communications:**
```sql
SELECT
    comm_date,
    comm_time,
    sender,
    recipients,
    message_body,
    contains_threat,
    contains_false_statement
FROM timeline_communications
ORDER BY comm_date, comm_time;
```

**Expected:** 3 communications (2 texts, 1 email)

**View Relationships:**
```sql
SELECT
    relationship_type,
    strength,
    description,
    legal_significance
FROM timeline_relationships
ORDER BY strength DESC;
```

**Expected:** 3 relationships (CAUSES, CONTRADICTS, TIMELINE_GAP)

---

## 🔍 Step 4: Test Query Functionality (5 minutes)

### 4.1 Timeline Query (Basic)

Get all events in chronological order:

```sql
SELECT
    event_date,
    event_time,
    event_title,
    event_type,
    importance
FROM timeline_events
ORDER BY event_date ASC, event_time ASC;
```

**Expected:** 5 events from Aug 7-12, 2024

### 4.2 Smoking Gun Query

Find critical evidence (importance ≥ 900):

```sql
SELECT
    event_date,
    event_title,
    importance,
    contains_false_statement
FROM timeline_events
WHERE importance >= 900
ORDER BY importance DESC;
```

**Expected:** 3-4 events with high importance scores

### 4.3 Contradiction Detection Query

Find contradictory relationships:

```sql
SELECT
    e1.event_title AS event_1,
    e2.event_title AS event_2,
    r.relationship_type,
    r.strength,
    r.legal_significance
FROM timeline_relationships r
JOIN timeline_events e1 ON r.event_id_1 = e1.id
JOIN timeline_events e2 ON r.event_id_2 = e2.id
WHERE r.relationship_type = 'CONTRADICTS'
ORDER BY r.strength DESC;
```

**Expected:** At least 1 contradiction relationship

### 4.4 Communication Pattern Analysis

Count messages by sender:

```sql
SELECT
    sender,
    COUNT(*) AS message_count,
    SUM(CASE WHEN contains_threat THEN 1 ELSE 0 END) AS threat_count,
    SUM(CASE WHEN contains_false_statement THEN 1 ELSE 0 END) AS false_statement_count
FROM timeline_communications
GROUP BY sender
ORDER BY message_count DESC;
```

**Expected:** Message counts for MOT and FAT

### 4.5 Timeline Gap Detection

Find gaps between events:

```sql
WITH event_gaps AS (
    SELECT
        event_date,
        event_title,
        LAG(event_date) OVER (ORDER BY event_date) AS prev_date,
        event_date - LAG(event_date) OVER (ORDER BY event_date) AS gap_days
    FROM timeline_events
)
SELECT *
FROM event_gaps
WHERE gap_days > 0
ORDER BY gap_days DESC;
```

**Expected:** Gaps between Aug 7, 8, 9, 12

### 4.6 Full-Text Search

Search for "Jamaica" mentions:

```sql
SELECT
    event_date,
    event_title,
    event_description,
    keywords
FROM timeline_events
WHERE search_vector @@ to_tsquery('english', 'jamaica')
ORDER BY event_date DESC;
```

**Expected:** Mother's declaration mentioning Jamaica

### 4.7 Participant Activity Summary

Check participant involvement:

```sql
SELECT
    participant_code,
    full_name,
    activity_summary
FROM timeline_participants
WHERE activity_summary IS NOT NULL
ORDER BY participant_code;
```

**Expected:** Activity summaries for participants in test events

---

## 🧪 Step 5: Test Isolation from Production (2 minutes)

### 5.1 Verify No Impact on ASEAGI Production Tables

**If you have `legal_documents` table:**

```sql
-- This should work even with timeline hub deployed
SELECT COUNT(*) FROM legal_documents;
```

**Expected:** Query succeeds, returns your document count (or error if table doesn't exist - that's also fine!)

### 5.2 Verify Timeline Hub Works Without legal_documents

```sql
-- This should work even if legal_documents doesn't exist
SELECT COUNT(*) FROM timeline_events;
```

**Expected:** Query succeeds, returns 5 (test events)

### 5.3 Confirm No Cross-Table Dependencies

```sql
-- This query should return 0 rows (no FK constraints to external tables)
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    ccu.table_name AS references_table
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name LIKE 'timeline_%'
    AND ccu.table_name NOT LIKE 'timeline_%';
```

**Expected:** 0 rows (no foreign keys to external tables)

---

## 🔄 Step 6: Test Rollback Safety (3 minutes)

### 6.1 Record Current State

Before rollback, record current counts:

```sql
-- Timeline hub counts
SELECT 'timeline_events' AS table_name, COUNT(*) AS count FROM timeline_events
UNION ALL
SELECT 'timeline_communications', COUNT(*) FROM timeline_communications
UNION ALL
SELECT 'timeline_participants', COUNT(*) FROM timeline_participants;
```

**Note these numbers.**

### 6.2 Record Production Table State (if applicable)

If you have production tables:

```sql
-- Production table counts (should be unaffected by rollback)
SELECT 'legal_documents' AS table_name, COUNT(*) AS count FROM legal_documents
UNION ALL
SELECT 'bugs', COUNT(*) FROM bugs;
```

**Note these numbers.**

### 6.3 Run Rollback Script

1. Open `database/002_rollback.sql`
2. Copy entire contents
3. Paste into new SQL Editor query
4. Click "Run"

### 6.4 Verify Timeline Hub Removed

```sql
-- This should fail (table doesn't exist)
SELECT COUNT(*) FROM timeline_events;
```

**Expected:** Error: `relation "timeline_events" does not exist`

### 6.5 Verify Production Tables Unaffected

If you have production tables:

```sql
-- This should still work and return the same count as before
SELECT COUNT(*) FROM legal_documents;
```

**Expected:** Same count as Step 6.2 (production tables untouched)

### 6.6 Re-deploy Schema (Optional)

To restore timeline hub after testing rollback:

1. Re-run `001_create_schema.sql`
2. Re-run `003_test_data.sql`
3. Verify tables restored

---

## 📱 Step 7: Test Application Integrations (Optional)

### 7.1 Test Document Processor

If you want to test the document processor:

```bash
# Set environment variables
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"

# Process a test image
python3 processors/document_processor.py \
    /path/to/test_image.jpg \
    --type TEXT_MESSAGE
```

**Expected:** Events and communications extracted and inserted into timeline_events and timeline_communications

### 7.2 Test Telegram Bot

If you want to test the Telegram bot:

```bash
# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"

# Start bot
python3 telegram/timeline_bot.py
```

**Then in Telegram:**
- Send `/start` to bot
- Send a photo
- Select document type
- Verify processing completes

### 7.3 Test Dashboard (When Implemented)

```bash
streamlit run dashboards/timeline_dashboard.py --server.port 8507
```

**Expected:** Dashboard loads and displays timeline data

---

## ✅ Testing Checklist Summary

After completing this guide, you should have verified:

- [x] Schema deployed successfully (6 tables + 2 functions)
- [x] All 12 isolation tests passed
- [x] Test data inserted (5 events, 3 communications, 3 relationships, 2 phases)
- [x] Timeline queries work independently
- [x] Smoking gun detection works
- [x] Contradiction detection works
- [x] Communication pattern analysis works
- [x] Full-text search works
- [x] No foreign key dependencies on external tables
- [x] Production tables unaffected by timeline hub
- [x] Rollback removes timeline hub cleanly
- [x] Production tables survive rollback
- [x] Schema can be re-deployed after rollback

---

## 🐛 Troubleshooting

### Issue: Schema creation fails

**Symptom:** Errors during `001_create_schema.sql` execution

**Solutions:**
1. Check Supabase service status
2. Verify you have sufficient permissions
3. Check for existing tables with same names (use `002_rollback.sql` first)
4. Review error message for specific issues

### Issue: Test data insertion fails

**Symptom:** Errors during `003_test_data.sql` execution

**Solutions:**
1. Ensure schema was deployed first (`001_create_schema.sql`)
2. Check for constraint violations in error message
3. Verify participants table has initial data

### Issue: Foreign key errors

**Symptom:** Errors about missing foreign keys

**Solutions:**
1. This should NOT happen - timeline hub has no external FK dependencies
2. If you see FK errors, check SEGMENTATION_VERIFICATION.md
3. Report as potential bug

### Issue: Production table queries fail after rollback

**Symptom:** `legal_documents` queries fail after running `002_rollback.sql`

**Solutions:**
1. This should NOT happen - rollback only affects timeline_ tables
2. Check rollback script ran correctly
3. Verify production tables still exist: `\dt` in psql or check Table Editor

### Issue: Timeline queries return 0 results

**Symptom:** Queries work but return no data

**Solutions:**
1. Run `003_test_data.sql` to insert sample data
2. Verify test data script completed successfully
3. Check for errors during insertion

---

## 📊 Expected Test Results Summary

| Test | Expected Result |
|------|----------------|
| Schema Deployment | 6 tables, 2 functions, 1 version table created |
| Isolation Verification | 12/12 tests passed |
| Test Data Insertion | 5 events, 3 comms, 3 relationships, 2 phases |
| Timeline Query | 5 events from Aug 7-12, 2024 |
| Smoking Gun Query | 3-4 high-importance events |
| Contradiction Query | 1+ contradiction relationships |
| Communication Analysis | Message counts by sender |
| Full-Text Search | Jamaica-related events found |
| Production Impact | 0 (no changes to external tables) |
| Rollback | Timeline hub removed, production unaffected |
| Re-deployment | Schema restores successfully |

---

## 🎯 Next Steps After Testing

Once testing is complete and all checks pass:

1. **For Development:**
   - Start building custom queries for your case
   - Upload real documents via Telegram or processor
   - Create timeline phases for your case periods

2. **For Production:**
   - Remove test data: `DELETE FROM timeline_events WHERE created_by = 'test_data_script';`
   - Configure environment variables
   - Deploy Telegram bot
   - Start uploading case documents

3. **For Integration:**
   - Review SEGMENTATION_VERIFICATION.md for integration guidelines
   - Consider optional linking to legal_documents via source_external_id
   - Plan criminal complaint system integration (optional)

---

## 📞 Support

**Issues or Questions:**
- Review SEGMENTATION_VERIFICATION.md for isolation details
- Check README.md for usage examples
- Review CHANGELOG.md for version history
- See QUICK_START.md for rapid setup

**Related Documentation:**
- `SEGMENTATION_VERIFICATION.md` - Detailed isolation verification
- `README.md` - Complete system documentation
- `CHANGELOG.md` - Version history and features
- `QUICK_START.md` - 10-minute setup guide

---

**Testing completed successfully?** You're ready to start building your master timeline!

**For Ashe. For Justice. For Timeline Truth.** 📅⚖️
