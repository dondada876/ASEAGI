# 🗄️ Set Up Database for Telegram Bot

**Time:** 5 minutes
**Goal:** Create all tables so your Telegram bot can return real data

---

## 🎯 Quick Setup (3 Steps)

### Step 1: Open Supabase SQL Editor

1. Go to: https://supabase.com/dashboard
2. Select your project: **jvjlhxodmbkodzmggwpu**
3. Click **SQL Editor** in left sidebar
4. Click **New query**

---

### Step 2: Copy & Paste SQL

1. Open the file: `telegram_bot_schema.sql` (in this folder)
2. **Copy ALL the SQL** (Ctrl+A, Ctrl+C)
3. **Paste into Supabase SQL Editor** (Ctrl+V)

**Or run this command to see the SQL:**
```bash
cat database/telegram_bot_schema.sql
```

---

### Step 3: Run the SQL

1. Click **Run** button (bottom right) in Supabase
2. Wait ~5 seconds
3. Should see: **Success. No rows returned**

✅ **Done!** Your database is ready.

---

## ✅ Verify It Worked

Run these queries in Supabase SQL Editor:

```sql
-- Should return 3
SELECT COUNT(*) FROM communications;

-- Should return 3
SELECT COUNT(*) FROM events;

-- Should return 4
SELECT COUNT(*) FROM action_items;

-- Should return 4
SELECT COUNT(*) FROM violations;

-- Should return 3
SELECT COUNT(*) FROM hearings;

-- Should return 4
SELECT COUNT(*) FROM document_journal;
```

**If all return numbers > 0, you're good!** ✅

---

## 🧪 Test Your Bot

Now go back to Telegram and try these commands:

```
/search Jamaica
/timeline 30
/actions
/violations
/hearing
/report
```

**They should all work now!** 🎉

---

## 📊 Tables Created

### 1. **communications** (Text messages, emails, calls)
Sample data includes:
- Mother's messages to social worker
- Social worker's contradictory responses
- Father's requests for missing documents

### 2. **events** (Case timeline)
Sample data includes:
- Initial detention hearing (Jan 5, 2024)
- Jurisdiction hearing (Feb 12, 2024)
- Denial of visitation incident (Mar 1, 2024)

### 3. **action_items** (Tasks & deadlines)
Sample data includes:
- File motion for reconsideration (urgent)
- Request missing documents (high priority)
- Prepare for next hearing
- File complaint against social worker

### 4. **violations** (Legal violations)
Sample data includes:
- Due process violation (missing Cal OES 2-925)
- Perjury (false testimony about notice)
- Fraud (false claims about mother)
- Denial of visitation

### 5. **hearings** (Court hearings)
Sample data includes:
- Past hearings with outcomes
- Upcoming review hearing (Nov 25, 2024)

### 6. **document_journal** (Case documents)
Sample data includes:
- Detention report
- Jurisdiction findings
- Text message evidence
- Motion for reconsideration

---

## 🔐 Security

The SQL includes Row Level Security (RLS) policies:
- All tables protected by RLS
- Service role has full access
- Your API will work seamlessly

---

## 🚨 Troubleshooting

### Error: "relation already exists"
**Meaning:** Tables already created
**Solution:** Skip this step, tables exist

### Error: "permission denied"
**Meaning:** Wrong Supabase project
**Solution:** Make sure you're in project: **jvjlhxodmbkodzmggwpu**

### Bot still returns errors
**Check API logs:**
```bash
ssh root@137.184.1.91 "docker logs aseagi-api --tail 30"
```

**Restart API service:**
```bash
ssh root@137.184.1.91 "cd /opt/ASEAGI && docker compose -f docker-compose.bot.yml restart api"
```

---

## 🎯 What Happens After

Once you run this SQL:

**Before:**
```
You: /search Jamaica
Bot: ❌ Error: 500 Server Error
```

**After:**
```
You: /search Jamaica
Bot: ✅ Found 0 communications matching 'Jamaica'
     (or shows actual results if Jamaica mentioned in data)
```

---

## 📝 Adding More Data

To add your own case data, use INSERT statements:

```sql
-- Add a communication
INSERT INTO communications (sender, recipient, sent_date, content) VALUES
('Your Name', 'Recipient Name', NOW(), 'Message content here');

-- Add an event
INSERT INTO events (event_date, event_type, title, description) VALUES
(NOW(), 'incident', 'Event Title', 'Event description');

-- Add an action item
INSERT INTO action_items (title, priority, due_date) VALUES
('Task title', 'urgent', '2024-12-01');
```

---

## 🎉 Expected Results

After setup, try in Telegram:

### `/report`
```
📊 Daily Report - 2024-11-06

🚨 4 Urgent Actions:
  • File Motion for Reconsideration (Due: 2024-11-15)
  • Request Missing Documents (Due: 2024-11-10)
  ...

⚖️ 4 Recent Violations:
  • [CRITICAL] due_process
  • [CRITICAL] perjury
  ...
```

### `/violations`
```
Found 4 violations (2 CRITICAL)

1. [CRITICAL] due_process
   Mother was never properly notified via Cal OES 2-925...

2. [CRITICAL] perjury
   Social worker testified under oath that mother was notified...
```

### `/actions`
```
Found 4 action items (1 URGENT)

1. File Motion for Reconsideration (Due: 2024-11-15) [URGENT]
2. Request Missing Documents (Due: 2024-11-10) [HIGH]
3. Prepare for Next Hearing (Due: 2024-11-20) [HIGH]
```

---

## 📞 Need Help?

If bot still shows errors after running SQL:

1. Check Supabase project is correct
2. Verify tables exist (run COUNT queries above)
3. Check API logs: `docker logs aseagi-api`
4. Restart services: `docker compose -f docker-compose.bot.yml restart`

---

**For Ashe. For Justice. For All Children.** 🛡️

---

## ⚡ Quick Command Reference

```bash
# View the SQL file
cat database/telegram_bot_schema.sql

# Check if API is running
ssh root@137.184.1.91 "docker ps | grep aseagi"

# Restart API after creating tables
ssh root@137.184.1.91 "cd /opt/ASEAGI && docker compose -f docker-compose.bot.yml restart api"

# Watch API logs
ssh root@137.184.1.91 "docker logs aseagi-api -f"
```

**Setup time: ~5 minutes**
**Difficulty: Easy** ⭐⭐☆☆☆
