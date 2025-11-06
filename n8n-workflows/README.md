# 🤖 ASEAGI n8n Workflows

Complete automation workflows for the ASEAGI Legal Intelligence System.

## 📦 Workflows Included

### 1. **Daily Case Report** (`01-daily-report.json`)
- **Schedule:** Every day at 8:00 AM
- **Purpose:** Send daily summary of case status to Telegram
- **Delivers:**
  - Total document count
  - Critical evidence count (900+ relevancy)
  - Important evidence count (800+ relevancy)
  - Document breakdown by category
  - Links to dashboards

### 2. **High Priority Alerts** (`02-high-priority-alerts.json`)
- **Schedule:** Every hour
- **Purpose:** Alert immediately when critical documents are added
- **Triggers when:**
  - New documents with relevancy score ≥ 900
  - Documents added in the last hour
- **Delivers:**
  - Document names and scores
  - Categories and fraud indicators
  - Quick links to review

### 3. **Weekly Statistics** (`03-weekly-statistics.json`)
- **Schedule:** Every Sunday at 6:00 PM
- **Purpose:** Comprehensive weekly case analysis
- **Delivers:**
  - Document statistics by category
  - Document type breakdown
  - Fraud indicator summary
  - Relevancy score trends
  - Complete dashboard links

---

## 🚀 Setup Instructions

### Prerequisites

1. **n8n Cloud Account**
   - Sign up at: https://n8n.io/cloud
   - Start with free tier (5,000 executions/month)
   - Upgrade to Pro ($20/month) if needed

2. **Telegram Bot Token**
   - Token: `8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI`
   - Bot username: `@aseagi_legal_bot`

3. **Supabase Credentials**
   - URL: `https://jvjlhxodmbkodzmggwpu.supabase.co`
   - Anon Key: Available in your `.env` file

4. **Your Telegram Chat ID**
   - See "Getting Your Chat ID" below

---

## 📋 Step-by-Step Setup

### Step 1: Get Your Telegram Chat ID (2 minutes)

1. Open Telegram and send **any message** to `@aseagi_legal_bot`
   - Example: "Hello" or "Test"

2. Open this URL in your browser:
   ```
   https://api.telegram.org/bot8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI/getUpdates
   ```

3. Find your Chat ID in the response:
   ```json
   {
     "message": {
       "chat": {
         "id": 123456789,  ← This is your Chat ID!
         ...
       }
     }
   }
   ```

4. **Save this number** - you'll need it for each workflow!

### Step 2: Add Credentials to n8n Cloud (5 minutes)

#### A. Add Supabase Credentials

1. In n8n Cloud, click **Settings** (gear icon) → **Credentials**
2. Click **New Credential** → Search for "Supabase"
3. Fill in:
   - **Credential Name:** `ASEAGI Supabase`
   - **Host:** `jvjlhxodmbkodzmggwpu.supabase.co`
   - **Service Role Secret:** Your Supabase anon key from `.env`
4. Click **Save**

#### B. Add Telegram Credentials

1. Still in **Credentials**, click **New Credential**
2. Search for "Telegram"
3. Fill in:
   - **Credential Name:** `ASEAGI Bot`
   - **Access Token:** `8571988538:AAHYGNpcDYp1nuhi8_-fCXuNhw9MvcAAutI`
4. Click **Save**

### Step 3: Import Workflows (10 minutes per workflow)

For each of the 3 workflow files:

1. **Open n8n Cloud** and click **"+ Add workflow"**

2. **Import the workflow:**
   - Click the `⋯` menu (top right)
   - Select **"Import from File"**
   - Choose the JSON file (e.g., `01-daily-report.json`)
   - Click **Import**

3. **Configure Chat ID:**
   - Find the **"Send to Telegram"** node (orange Telegram icon)
   - Click on it
   - Replace `YOUR_TELEGRAM_CHAT_ID` with your actual Chat ID (from Step 1)
   - Example: Change `"YOUR_TELEGRAM_CHAT_ID"` to `"123456789"`

4. **Link Credentials:**
   - Click the **Supabase node** (green icon)
   - In the **Credentials** dropdown, select `ASEAGI Supabase`
   - Click the **Telegram node**
   - In the **Credentials** dropdown, select `ASEAGI Bot`

5. **Save the workflow:**
   - Click **Save** button (top right)
   - Give it a name if prompted

6. **Test it:**
   - Click **"Execute Workflow"** button (▶ play icon)
   - Watch nodes turn green ✅
   - Check your Telegram for the message!

7. **Activate it:**
   - Toggle the **Active** switch (top right) to ON
   - The workflow will now run on its schedule

### Step 4: Verify Everything Works (5 minutes)

1. **Test each workflow manually:**
   - Open workflow
   - Click **Execute Workflow**
   - Verify you receive Telegram message
   - Check for any red error nodes

2. **Check execution history:**
   - Click **Executions** in left sidebar
   - Verify your test runs show as "Success"
   - Click any execution to see details

3. **Wait for first scheduled run:**
   - Daily Report: Next 8 AM
   - Hourly Alerts: Next hour
   - Weekly Stats: Next Sunday 6 PM

---

## 🔧 Customization Options

### Change Schedule Times

Edit the **Schedule Trigger** node:

```javascript
// Daily Report - Change "0 8 * * *"
"0 8 * * *"   // 8 AM daily
"0 6 * * *"   // 6 AM daily
"0 20 * * *"  // 8 PM daily

// Hourly Alerts - Change "0 * * * *"
"0 * * * *"   // Every hour
"*/30 * * * *" // Every 30 minutes
"0 */2 * * *" // Every 2 hours

// Weekly Report - Change "0 18 * * 0"
"0 18 * * 0"  // Sunday 6 PM
"0 18 * * 1"  // Monday 6 PM
"0 12 * * 0"  // Sunday 12 PM
```

### Adjust Alert Thresholds

In the **Get New Critical Documents** node (Workflow 02):

```javascript
// Change relevancy_score filter
"keyValue": "900"  // Only 900+
"keyValue": "850"  // Include 850+
"keyValue": "950"  // Only 950+ (fewer alerts)
```

### Add More Recipients

Clone the **Telegram Send** node and add different Chat IDs for team members.

### Change Message Format

Edit the **Format Message** Code node:
- Add emojis
- Change text layout
- Add/remove statistics
- Modify dashboard links

---

## 🐛 Troubleshooting

### "Credentials not found" Error

**Solution:**
1. Open the node showing error
2. Click **Credentials** dropdown
3. Select `ASEAGI Supabase` or `ASEAGI Bot`
4. If not listed, go to **Settings → Credentials** and add them

### "Invalid Chat ID" Error

**Solution:**
1. Make sure you sent a message to the bot first
2. Check the `/getUpdates` URL again
3. Use only the numbers (no quotes in n8n)
4. Example: `123456789` not `"123456789"`

### Workflow Shows as "Error" in Executions

**Solution:**
1. Click the failed execution
2. Find the red node
3. Click it to see error details
4. Common fixes:
   - Check credentials are linked
   - Verify Supabase table name is correct (`documents`)
   - Ensure Chat ID is valid number
   - Check internet connectivity

### No Telegram Messages Received

**Solution:**
1. Verify bot credentials are correct
2. Check you sent a message to bot first
3. Test with **Execute Workflow** button
4. Check execution log shows success
5. Make sure Telegram is not blocking the bot

### Supabase Connection Fails

**Solution:**
1. Verify Supabase URL is correct (no `https://`)
2. Check API key in credential
3. Test connection in **Settings → Credentials**
4. Ensure database table `documents` exists
5. Check Supabase project is active

---

## 📊 Monitoring & Maintenance

### Daily Checks (30 seconds)

```bash
✅ Open Telegram
✅ Verify you received expected messages
✅ Check message content makes sense
```

### Weekly Checks (2 minutes)

1. Open n8n Cloud
2. Click **Executions**
3. Filter: **Failed executions only**
4. Investigate any failures
5. Check execution count vs your plan limits

### Monthly Reviews (10 minutes)

- Review workflow effectiveness
- Adjust schedules if needed
- Update thresholds based on usage
- Check API usage costs
- Optimize for free tier limits

---

## 💰 Cost Breakdown

### Execution Count Estimates

| Workflow | Frequency | Per Month | Notes |
|----------|-----------|-----------|-------|
| Daily Report | 1/day | 30 | Fixed |
| Hourly Alerts | 1/hour | 720 | Only sends if new docs |
| Weekly Stats | 1/week | 4 | Fixed |
| **TOTAL** | - | **~754** | Well within free tier! |

### n8n Cloud Pricing

- **Free Tier:** 5,000 executions/month
- **Pro Plan:** $20/month for 2,500 executions + extras
- **Your Usage:** ~754/month = **FREE!** 🎉

### Cost Optimization Tips

1. **Reduce hourly checks:**
   - Change to every 2 hours: saves 360 executions/month
   - Change to every 6 hours: saves 600 executions/month

2. **Use conditional logic:**
   - Workflows already stop if no new data
   - No wasted executions

3. **Monitor usage:**
   - Check **Settings → Usage** monthly
   - Set up alerts at 80% of free tier

---

## 🔗 Useful Links

- **n8n Cloud:** https://app.n8n.cloud
- **n8n Documentation:** https://docs.n8n.io
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Supabase Docs:** https://supabase.com/docs
- **Cron Expression Builder:** https://crontab.guru

---

## 📞 Support

### Issues with Workflows

1. Check **Troubleshooting** section above
2. Review execution logs in n8n
3. Test credentials in Settings
4. Verify Supabase data exists

### Need Help?

- n8n Community: https://community.n8n.io
- Telegram Bot Docs: https://core.telegram.org/bots
- ASEAGI Project: Check main README.md

---

## 🎯 Next Steps

Once these workflows are running:

1. **Add more automations:**
   - Document upload notifications
   - Court date reminders
   - Deadline alerts
   - Team notifications

2. **Connect more services:**
   - Email reports
   - Slack integration
   - Calendar events
   - SMS alerts (Twilio)

3. **Advanced features:**
   - AI analysis with Claude API
   - Document summarization
   - Automated categorization
   - Trend analysis

4. **Mobile access:**
   - Set up Telegram commands (`/status`, `/latest`)
   - Create interactive keyboards
   - Add inline buttons for actions

---

## ✅ Quick Checklist

Before marking setup as complete:

- [ ] n8n Cloud account created
- [ ] Supabase credentials added
- [ ] Telegram credentials added
- [ ] Telegram Chat ID obtained
- [ ] Workflow 01 imported and tested
- [ ] Workflow 02 imported and tested
- [ ] Workflow 03 imported and tested
- [ ] All workflows activated
- [ ] First scheduled execution verified
- [ ] Telegram notifications working
- [ ] Execution history showing success

---

**Last Updated:** November 6, 2025
**Version:** 1.0
**Maintained by:** Claude Code Agent
