# ASEAGI n8n Workflows

Complete automation workflows for the ASEAGI Legal Intelligence System.

## Workflows Included

### 1. Daily Case Report (`01-daily-report.json`)
- **Schedule:** Every day at 8:00 AM
- **Purpose:** Send daily summary of case status
- **Delivers:**
  - Total document count
  - Critical evidence count (900+ score)
  - Important evidence count (800+ score)
  - Last update timestamp
  - Links to all dashboards

### 2. High Priority Document Alerts (`02-high-priority-alerts.json`)
- **Schedule:** Every hour
- **Purpose:** Immediate alerts for smoking gun evidence
- **Triggers When:** New documents with relevancy score ≥ 950
- **Delivers:**
  - Document filename
  - Relevancy score
  - Category
  - Fraud indicators
  - Perjury indicators
  - Direct link to review

### 3. Weekly Statistics Report (`03-weekly-statistics.json`)
- **Schedule:** Every Sunday at 6:00 PM
- **Purpose:** Comprehensive weekly case analysis
- **Delivers:**
  - Document breakdown by category
  - Priority distribution (Critical/Important/Significant)
  - Violation indicator summary
  - Fraud and perjury statistics

---

## Setup Instructions

### Step 1: Sign Up for n8n Cloud

1. Go to **https://n8n.io/**
2. Click **"Start for Free"**
3. Create your account (GitHub, Google, or email)
4. You'll get a URL like: `https://yourname.app.n8n.cloud`

### Step 2: Configure Credentials

#### Add Supabase Credentials

1. In n8n, click **Settings** (gear icon, bottom left)
2. Click **Credentials** → **New Credential**
3. Search for and select **"Supabase"**
4. Fill in:
   - **Name:** `ASEAGI Supabase`
   - **Host:** `jvjlhxodmbkodzmggwpu.supabase.co`
   - **Service Role Key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c`
5. Click **Save**

#### Add Telegram Bot Credentials

1. Still in **Credentials** → **New Credential**
2. Search for and select **"Telegram"**
3. Fill in:
   - **Name:** `ASEAGI Bot`
   - **Access Token:** `8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI`
4. Click **Save**

### Step 3: Get Your Telegram Chat ID

You need this to receive messages from your bot.

**Method 1: Use Web Browser**
1. Send any message to **@aseagi_legal_bot** on Telegram (e.g., "Hello")
2. Open this URL in your browser:
   ```
   https://api.telegram.org/bot8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI/getUpdates
   ```
3. Look for `"chat":{"id":123456789` in the response
4. Copy that number (your Chat ID)

**Method 2: Use @userinfobot**
1. Search for **@userinfobot** on Telegram
2. Start a chat with it
3. It will send you your Chat ID

### Step 4: Import Workflows

For each workflow file:

1. In n8n, click **"+ Add workflow"** (top right)
2. Click the **3 dots menu** (⋮) → **"Import from File"**
3. Select the workflow JSON file:
   - `01-daily-report.json`
   - `02-high-priority-alerts.json`
   - `03-weekly-statistics.json`
4. The workflow will open in the editor

### Step 5: Configure Each Workflow

For **EACH** imported workflow:

1. **Update Telegram Chat ID:**
   - Click on the **Telegram node** (pink/purple color)
   - Find the field **"Chat ID"**
   - Replace `YOUR_TELEGRAM_CHAT_ID` with your actual Chat ID from Step 3

2. **Select Credentials:**
   - Click on the **Supabase node** (green)
   - In the "Credential to connect with" dropdown, select **"ASEAGI Supabase"**
   - Click on the **Telegram node**
   - In the "Credential to connect with" dropdown, select **"ASEAGI Bot"**

3. **Save the Workflow:**
   - Click **Save** button (top right)
   - Give it a name if prompted

4. **Activate the Workflow:**
   - Toggle the switch at the top from **Inactive** to **Active**
   - You should see a green "Active" indicator

### Step 6: Test Your Workflows

Before waiting for scheduled runs, test them manually:

1. **Open a workflow** (e.g., Daily Report)
2. Click **"Execute Workflow"** button (top right, play icon)
3. Watch the nodes light up as they execute
4. Check your Telegram for the message!
5. If successful, you'll see green checkmarks on all nodes

---

## Troubleshooting

### Workflow doesn't send Telegram messages

**Check:**
- [ ] Telegram Chat ID is correct (not `YOUR_TELEGRAM_CHAT_ID`)
- [ ] Bot token is correct in credentials
- [ ] Telegram node has credential selected
- [ ] You've sent at least one message to @aseagi_legal_bot first

### Supabase query fails

**Check:**
- [ ] Supabase credentials are configured correctly
- [ ] Service Role Key is the full token (starts with `eyJh...`)
- [ ] Supabase node has credential selected
- [ ] Your Supabase database has the `legal_documents` table

### Workflow never runs automatically

**Check:**
- [ ] Workflow is **Active** (toggle switch is on)
- [ ] Schedule trigger has correct cron expression
- [ ] n8n Cloud account is active (not paused/expired)

### Need to change schedule times

Edit the **Schedule Trigger** node:
- Daily Report: `0 8 * * *` = 8:00 AM daily
- Hourly Alerts: `0 * * * *` = Every hour
- Weekly Report: `0 18 * * 0` = Sunday 6:00 PM

Use **https://crontab.guru/** to create custom schedules.

---

## Customization Ideas

### Add Email Notifications
- Add an **Email** node after Telegram
- Configure SMTP credentials
- Send reports to multiple recipients

### Query Specific Document Types
Modify Supabase queries to filter:
```sql
WHERE document_category = 'Court Filings'
  AND relevancy_score >= 900
```

### Add Deadline Monitoring
Create a new workflow to check:
```sql
SELECT * FROM legal_documents
WHERE deadline_date <= CURRENT_DATE + INTERVAL '7 days'
```

### Integrate with WordPress
- Use **HTTP Request** node
- POST data to WordPress REST API
- Auto-update your website with case stats

---

## Workflow Files Location

These JSON files are saved in:
```
/Users/dbucknor/Downloads/proj344-dashboards/n8n-workflows/
```

You can edit them directly or re-import modified versions.

---

## Support

- **n8n Documentation:** https://docs.n8n.io/
- **n8n Community:** https://community.n8n.io/
- **Supabase REST API:** https://supabase.com/docs/guides/api
- **Telegram Bot API:** https://core.telegram.org/bots/api

---

## Case Information

- **Case:** Ashe Bucknor v. Mother & CPS
- **Docket:** J24-00478
- **Documents:** 601 analyzed legal documents
- **Dashboards:** http://137.184.1.91:8501-8503

---

**For Ashe. For Justice. For All Children.** ⚖️
