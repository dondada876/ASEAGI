# 🔄 n8n Workflows - Setup Guide

Complete step-by-step guide to import and configure n8n workflows for Telegram document processing.

---

## 📋 Prerequisites

Before you begin, you need:
- ✅ n8n instance (self-hosted or cloud)
- ✅ Supabase database with tables created (run `telegram_system_schema.sql`)
- ✅ Telegram bot token
- ✅ AWS S3 bucket (or alternative storage)
- ✅ Credentials for all services

---

## 🚀 Quick Start

### Step 1: Import Workflows

**You have 2 workflows to import:**

1. **Main Processing Pipeline** - `n8n_telegram_processing_workflow.json`
   - Handles document upload, validation, storage
   - Updates database, sends notifications

2. **Notification Sender** - `n8n_notification_sender_workflow.json`
   - Runs every 30 seconds
   - Sends queued notifications to users

**To Import:**
1. Open n8n
2. Click **"Workflows"** → **"Add Workflow"** → **"Import from File"**
3. Copy the JSON from the file
4. Paste into n8n
5. Click **"Import"**
6. Repeat for second workflow

---

## 🔑 Step 2: Configure Credentials

You need to set up 3 sets of credentials in n8n:

### A. Supabase Credentials

1. In n8n, go to **Credentials** → **New**
2. Search for **"Supabase"**
3. Fill in:
   - **Name:** `Supabase Account`
   - **Host:** Your Supabase URL (e.g., `https://jvjlhxodmbkodzmggwpu.supabase.co`)
   - **Service Role Key:** Your Supabase **service_role** key (NOT anon key)
4. Click **"Save"**

**Where to get Supabase keys:**
- Go to: https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api
- Copy **service_role** key (secret key)

### B. Telegram Bot Credentials

1. In n8n, go to **Credentials** → **New**
2. Search for **"Telegram"**
3. Fill in:
   - **Name:** `Telegram Bot`
   - **Access Token:** Your Telegram bot token
4. Click **"Save"**

**Where to get Telegram token:**
- Open Telegram, search for @BotFather
- Send `/mybots` → Select your bot → **API Token**

### C. AWS S3 Credentials

1. In n8n, go to **Credentials** → **New**
2. Search for **"AWS"**
3. Fill in:
   - **Name:** `AWS Account`
   - **Access Key ID:** Your AWS access key
   - **Secret Access Key:** Your AWS secret key
   - **Region:** Your S3 region (e.g., `us-east-1`)
4. Click **"Save"**

**Where to get AWS keys:**
- Go to: https://console.aws.amazon.com/iam/
- Create new IAM user with S3 permissions
- Generate access keys

---

## ⚙️ Step 3: Configure Environment Variables

Both workflows use environment variables. Set these in n8n:

### In n8n Cloud:
1. Go to **Settings** → **Environment Variables**
2. Add:
   ```
   TELEGRAM_BOT_TOKEN=your-telegram-token-here
   S3_BUCKET_NAME=your-bucket-name
   ```

### In Self-Hosted n8n (Docker):
Add to your docker-compose.yml or .env file:
```bash
N8N_TELEGRAM_BOT_TOKEN=your-telegram-token-here
N8N_S3_BUCKET_NAME=your-bucket-name
```

Or set via command line:
```bash
export N8N_TELEGRAM_BOT_TOKEN='your-telegram-token'
export N8N_S3_BUCKET_NAME='proj344-documents'
```

---

## 🔧 Step 4: Configure Each Workflow

### Workflow 1: Main Processing Pipeline

After importing, you need to link credentials to nodes:

1. **Open the workflow** in n8n
2. **For each Supabase node** (there are 7):
   - Click on the node
   - Under **Credentials**, select `Supabase Account`

3. **For the AWS S3 node**:
   - Click on "AWS S3 - Upload File"
   - Under **Credentials**, select `AWS Account`

4. **Click "Save"** (top right)

### Workflow 2: Notification Sender

1. **Open the workflow** in n8n
2. **For Supabase nodes**:
   - Select `Supabase Account` credential

3. **For Telegram node**:
   - Click on "Telegram - Send Message"
   - Select `Telegram Bot` credential

4. **Click "Save"**

---

## ✅ Step 5: Activate Workflows

1. **Activate Processing Pipeline:**
   - Open workflow
   - Toggle **"Active"** switch (top right)
   - Should turn green

2. **Activate Notification Sender:**
   - Open workflow
   - Toggle **"Active"** switch
   - Should start running every 30 seconds

---

## 🧪 Step 6: Test the Workflows

### Test Processing Pipeline

1. **Get the webhook URL:**
   - Open "Main Processing Pipeline" workflow
   - Click on "Webhook - Telegram Upload" node
   - Copy the **Production URL** (looks like: `https://your-n8n.com/webhook/telegram-upload`)

2. **Test with curl:**
   ```bash
   curl -X POST https://your-n8n.com/webhook/telegram-upload \
     -H "Content-Type: application/json" \
     -d '{
       "upload_id": "test-123-456",
       "file_id": "test-file-id",
       "file_type": "photo",
       "file_size": 1024000,
       "telegram_user_id": 123456789,
       "telegram_chat_id": 123456789,
       "document_type": "EVID",
       "document_title": "Test Document",
       "storage_filename": "test.jpg",
       "uploaded_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
     }'
   ```

3. **Check n8n execution:**
   - Go to **Executions** tab
   - You should see a new execution
   - Click to view details
   - Check each node executed successfully

4. **Verify in Supabase:**
   - Check `processing_logs` table for entries
   - Check `storage_registry` table for file record

### Test Notification Sender

1. **Manually add a notification:**
   ```sql
   INSERT INTO notification_queue (
     telegram_user_id,
     telegram_chat_id,
     notification_type,
     message,
     priority
   ) VALUES (
     YOUR_TELEGRAM_USER_ID,
     YOUR_TELEGRAM_CHAT_ID,
     'test',
     '🧪 Test notification from n8n workflow!',
     1
   );
   ```

2. **Wait 30 seconds**
   - The scheduled workflow will pick it up
   - You should receive a Telegram message

3. **Check the notification was marked as sent:**
   ```sql
   SELECT * FROM notification_queue
   WHERE notification_type = 'test'
   ORDER BY created_at DESC LIMIT 1;
   ```
   - `status` should be `'sent'`
   - `sent_at` should have a timestamp

---

## 🔍 Troubleshooting

### Webhook Not Responding

**Problem:** Webhook returns 404 or doesn't trigger workflow

**Solutions:**
1. Check workflow is **Active**
2. Verify webhook path is correct
3. Try the **Test URL** first (in webhook node)
4. Check n8n logs for errors

### Supabase Errors

**Problem:** "Authentication failed" or "Table not found"

**Solutions:**
1. Verify you're using **service_role** key (not anon key)
2. Check table names match exactly (case-sensitive)
3. Run `telegram_system_schema.sql` to create tables
4. Test Supabase connection in credentials

### S3 Upload Fails

**Problem:** "Access Denied" or "Bucket not found"

**Solutions:**
1. Verify AWS credentials have S3 permissions
2. Check bucket name is correct
3. Ensure bucket exists in specified region
4. Check IAM policy allows `s3:PutObject`

### Telegram Messages Not Sending

**Problem:** Notifications stay in "pending" status

**Solutions:**
1. Check Telegram bot token is correct
2. Verify chat_id is valid
3. Ensure notification sender workflow is **Active**
4. Check workflow execution history for errors
5. Try sending a test message manually from Telegram node

### File Download Fails

**Problem:** "Failed to download file from Telegram"

**Solutions:**
1. Verify Telegram bot token in environment variables
2. Check file_id is valid
3. Ensure file hasn't expired (Telegram files expire)
4. Try with a fresh file upload

---

## 📊 Monitoring

### Check Workflow Executions

1. Go to **Executions** tab in n8n
2. Filter by workflow name
3. Look for:
   - ✅ Green = Success
   - ❌ Red = Failed
   - ⏸️ Gray = Waiting

### View Logs

**For each execution:**
- Click on execution
- See data flow between nodes
- Check error messages
- View JSON data at each step

### Common Errors to Watch:

- **"Missing environment variable"** → Set env vars
- **"Credential not found"** → Re-link credentials
- **"Table does not exist"** → Run schema SQL
- **"Invalid file_id"** → File expired or wrong ID
- **"Network error"** → Check connectivity

---

## 🔐 Security Best Practices

1. **Use service_role key** for Supabase (better permissions)
2. **Never expose** webhook URLs publicly (use authentication)
3. **Rotate credentials** regularly
4. **Limit IAM permissions** to only what's needed
5. **Enable RLS** in Supabase for sensitive data
6. **Use HTTPS** for all webhooks
7. **Monitor executions** for suspicious activity

---

## 📈 Performance Tips

1. **Increase n8n memory** if processing large files
2. **Use queue mode** for high-volume uploads
3. **Set timeout limits** on HTTP requests
4. **Batch notifications** if sending many
5. **Monitor execution time** and optimize slow nodes
6. **Use webhooks** instead of polling where possible

---

## 🔄 Workflow Maintenance

### Regular Tasks:

**Weekly:**
- Review failed executions
- Check storage usage
- Monitor processing times

**Monthly:**
- Rotate credentials
- Review and optimize workflows
- Clean up old executions
- Update n8n if new version available

**As Needed:**
- Add new document types
- Adjust retry logic
- Optimize performance
- Add new notification types

---

## 📚 Additional Resources

- **n8n Documentation:** https://docs.n8n.io
- **Supabase Docs:** https://supabase.com/docs
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **AWS S3 Guide:** https://docs.aws.amazon.com/s3/

---

## 🆘 Getting Help

If you're stuck:

1. **Check n8n execution logs** - Usually shows the exact error
2. **Review this guide** - Most issues covered above
3. **Test each node individually** - Isolate the problem
4. **Check credentials** - 90% of errors are credential issues
5. **Verify database schema** - Tables must exist
6. **n8n Community Forum:** https://community.n8n.io

---

## ✅ Checklist

Before going to production:

- [ ] Both workflows imported
- [ ] All credentials configured
- [ ] Environment variables set
- [ ] Database schema created
- [ ] S3 bucket created and accessible
- [ ] Webhook URL configured in Telegram bot
- [ ] Test upload completed successfully
- [ ] Test notification received
- [ ] Error handling tested
- [ ] Monitoring set up
- [ ] Backup plan in place

---

## 🎉 You're Ready!

Once all checklist items are complete, your automated document processing system is live!

**Next Steps:**
1. Start uploading documents via Telegram
2. Monitor executions in n8n
3. Check Supabase for processed documents
4. Review notifications are being sent
5. Optimize as needed

**Happy Processing! 🚀**
