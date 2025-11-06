# 📋 Copy & Paste Guide - Quick Setup

Everything you need to copy and paste to get started.

---

## 🎯 What You Need to Do

1. **Run SQL in Supabase** → Creates database tables
2. **Import Workflows to n8n** → Copy-paste JSON
3. **Configure Credentials** → Connect services
4. **Start Using** → Upload documents from phone!

---

## 1️⃣ STEP 1: Create Database Tables

### Copy This SQL:

**File:** `telegram_system_schema.sql`

**Steps:**
1. Go to Supabase Dashboard: https://supabase.com/dashboard
2. Select your project
3. Click **SQL Editor** (left sidebar)
4. Click **New Query**
5. **Copy the entire contents** of `telegram_system_schema.sql`
6. **Paste** into the SQL editor
7. Click **Run** (or Ctrl+Enter)

**Expected Result:**
```
Success! Query returned successfully in XXXms
```

**Verify It Worked:**
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('telegram_uploads', 'processing_logs', 'storage_registry', 'notification_queue');
```

You should see 4 tables listed.

---

## 2️⃣ STEP 2: Import n8n Workflows

### Workflow A: Main Processing Pipeline

**File:** `n8n_telegram_processing_workflow.json`

**Steps:**
1. Open n8n
2. Click **Workflows** → **Add Workflow** → **Import from File**
3. **Copy entire contents** of `n8n_telegram_processing_workflow.json`
4. **Paste** into n8n import dialog
5. Click **Import**

**You should see:**
- 19 nodes in the workflow
- "Telegram Document Processing Pipeline" as the name

### Workflow B: Notification Sender

**File:** `n8n_notification_sender_workflow.json`

**Steps:**
1. Same as above
2. **Copy** from `n8n_notification_sender_workflow.json`
3. **Paste** and **Import**

**You should see:**
- 8 nodes in the workflow
- "Telegram Notification Sender" as the name

---

## 3️⃣ STEP 3: Set Environment Variables

### In n8n Settings:

**Go to:** Settings → Environment Variables

**Add These:**

```
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
S3_BUCKET_NAME=proj344-documents
```

### How to Get Your Bot Token:

1. Open Telegram
2. Search for **@BotFather**
3. Send: `/mybots`
4. Select your bot
5. Click **API Token**
6. **Copy** the token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
7. **Paste** as `TELEGRAM_BOT_TOKEN` value

---

## 4️⃣ STEP 4: Configure Credentials in n8n

You need to add 3 credentials:

### A. Supabase

**In n8n:**
1. Click **Credentials** → **New**
2. Search: **Supabase**
3. **Name:** `Supabase Account`
4. **Host:** `https://jvjlhxodmbkodzmggwpu.supabase.co` (or your URL)
5. **Service Role Key:** *[Get from Supabase → Settings → API]*
6. **Save**

### B. Telegram

**In n8n:**
1. Click **Credentials** → **New**
2. Search: **Telegram**
3. **Name:** `Telegram Bot`
4. **Access Token:** *[Same as TELEGRAM_BOT_TOKEN above]*
5. **Save**

### C. AWS S3

**In n8n:**
1. Click **Credentials** → **New**
2. Search: **AWS**
3. **Name:** `AWS Account`
4. **Access Key ID:** *[From AWS IAM]*
5. **Secret Access Key:** *[From AWS IAM]*
6. **Region:** `us-east-1` (or your region)
7. **Save**

---

## 5️⃣ STEP 5: Link Credentials to Workflows

### For Main Processing Pipeline:

1. Open the workflow
2. **Click each node** with a red warning icon
3. Under **Credentials**, select the matching credential:
   - Supabase nodes → `Supabase Account`
   - AWS S3 node → `AWS Account`
4. **Save** workflow (top right)

### For Notification Sender:

1. Open the workflow
2. Link credentials:
   - Supabase nodes → `Supabase Account`
   - Telegram node → `Telegram Bot`
3. **Save** workflow

---

## 6️⃣ STEP 6: Activate Workflows

**For BOTH workflows:**
1. Open workflow
2. Toggle **Active** switch (top right)
3. Should turn **green**

---

## 7️⃣ STEP 7: Get Webhook URL

**From Main Processing Pipeline:**
1. Open workflow
2. Click **"Webhook - Telegram Upload"** node
3. **Copy** the **Production URL**

Example: `https://your-n8n-instance.com/webhook/telegram-upload`

**Save this URL** - you'll need it for the Telegram bot.

---

## 8️⃣ STEP 8: Test Everything

### Quick Test with curl:

**Copy and paste this** (replace YOUR_WEBHOOK_URL):

```bash
curl -X POST YOUR_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{
    "upload_id": "00000000-0000-0000-0000-000000000001",
    "file_id": "test-file-id",
    "file_type": "photo",
    "file_size": 1024000,
    "telegram_user_id": 123456789,
    "telegram_chat_id": 123456789,
    "document_type": "EVID",
    "document_title": "Test Document",
    "storage_filename": "test.jpg",
    "uploaded_at": "2025-11-06T00:00:00Z",
    "mime_type": "image/jpeg"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Document processing completed",
  "upload_id": "00000000-0000-0000-0000-000000000001"
}
```

**Check n8n:**
- Go to **Executions** tab
- Should see a successful execution
- All nodes should be green ✅

**Check Supabase:**
```sql
SELECT * FROM telegram_uploads ORDER BY created_at DESC LIMIT 1;
SELECT * FROM processing_logs ORDER BY logged_at DESC LIMIT 5;
```

Should see your test data!

---

## ✅ Success Checklist

Before going live, verify:

- [ ] **Database tables created** (5 tables)
- [ ] **Both workflows imported** into n8n
- [ ] **3 credentials configured** (Supabase, Telegram, AWS)
- [ ] **2 environment variables set** (TELEGRAM_BOT_TOKEN, S3_BUCKET_NAME)
- [ ] **Credentials linked** to workflow nodes
- [ ] **Both workflows activated** (green toggle)
- [ ] **Webhook URL copied**
- [ ] **Test execution successful**
- [ ] **Data appears in Supabase**
- [ ] **S3 bucket exists and accessible**

---

## 🎉 You're Done!

Your system is now ready to process documents!

### What Happens Now:

1. **User uploads** document via Telegram bot
2. **Bot sends data** to your n8n webhook
3. **Workflow processes** the document
4. **File stored** in S3
5. **Metadata saved** to Supabase
6. **User notified** via Telegram

---

## 🆘 If Something Doesn't Work

### Most Common Issues:

**1. "Credential not found"**
→ Go back to Step 5 and link credentials

**2. "Table does not exist"**
→ Re-run the SQL from Step 1

**3. "Webhook 404"**
→ Make sure workflow is **Active** (green toggle)

**4. "S3 Access Denied"**
→ Check AWS credentials and bucket name

**5. "Telegram error"**
→ Verify bot token is correct

---

## 📚 Full Documentation

For detailed explanations, see:

- **PRD:** `DOCUMENT_INGESTION_PRD.md` - Complete system design
- **Schema:** `telegram_system_schema.sql` - Database structure
- **Workflows:** `N8N_WORKFLOW_GUIDE.md` - How workflows work
- **Setup:** `N8N_WORKFLOWS_SETUP.md` - Detailed setup guide
- **Dashboard:** `telegram_uploads_dashboard.py` - View uploads

---

## 🚀 Next Steps

1. **Update Telegram bot** to use webhook URL
2. **Upload test document** from phone
3. **Monitor in n8n** executions
4. **View in dashboard** → `streamlit run telegram_uploads_dashboard.py`
5. **Review data** in Supabase

---

**Happy Processing! 📱→📊→🎉**
