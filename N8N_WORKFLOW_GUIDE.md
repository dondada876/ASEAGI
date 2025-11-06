# 🔄 n8n Workflow Guide for Document Processing

Complete guide for setting up n8n workflows to process Telegram uploads.

---

## 📋 Overview

n8n workflows handle the automated processing of documents uploaded via Telegram bot:

1. **Trigger:** Webhook from Telegram bot
2. **Validate:** Check file type, size, duplicates
3. **Store:** Upload to S3/Google Drive/Backblaze
4. **Extract:** OCR, metadata extraction, text analysis
5. **Enhance:** AI relevancy scoring, key quotes, summaries
6. **Notify:** Send status updates to user

---

## 🚀 Workflow 1: Main Processing Pipeline

### Trigger Node
- **Type:** Webhook
- **Path:** `/webhook/telegram-upload`
- **Method:** POST
- **Authentication:** API Key

### Node 1: Validation
**Function Node:**
```javascript
// Check file type
const allowedTypes = ['photo', 'document', 'audio', 'video'];
if (!allowedTypes.includes($input.item.json.file_type)) {
  throw new Error('Unsupported file type');
}

// Check file size (max 20MB)
if ($input.item.json.file_size > 20 * 1024 * 1024) {
  throw new Error('File too large');
}

return $input.item;
```

### Node 2: Supabase - Log Processing Start
- **Operation:** Insert
- **Table:** `processing_logs`
- **Data:**
  ```json
  {
    "telegram_upload_id": "{{$json.upload_id}}",
    "stage": "validation",
    "status": "completed",
    "message": "Validation successful"
  }
  ```

### Node 3: Download from Telegram
**HTTP Request Node:**
- **URL:** `https://api.telegram.org/bot{{$env.TELEGRAM_BOT_TOKEN}}/getFile?file_id={{$json.file_id}}`
- **Method:** GET

### Node 4: Upload to S3
**AWS S3 Node:**
- **Operation:** Upload
- **Bucket:** `proj344-documents`
- **Key:** `{{$json.year}}/{{$json.month}}/{{$json.document_type}}/{{$json.filename}}`
- **ACL:** private

### Node 5: Supabase - Update Storage Registry
- **Operation:** Insert
- **Table:** `storage_registry`
- **Data:**
  ```json
  {
    "telegram_upload_id": "{{$json.upload_id}}",
    "file_hash": "{{$json.file_hash}}",
    "original_filename": "{{$json.filename}}",
    "primary_storage_provider": "s3",
    "primary_storage_url": "{{$json.s3_url}}",
    "primary_storage_path": "{{$json.s3_key}}",
    "file_size": {{$json.file_size}}
  }
  ```

### Node 6: Supabase - Update Upload Status
- **Operation:** Update
- **Table:** `telegram_uploads`
- **Filter:** `id.eq.{{$json.upload_id}}`
- **Data:**
  ```json
  {
    "status": "completed",
    "permanent_storage_url": "{{$json.s3_url}}",
    "storage_provider": "s3",
    "processing_completed_at": "{{$now}}"
  }
  ```

### Node 7: Queue Notification
- **Operation:** Insert
- **Table:** `notification_queue`
- **Data:**
  ```json
  {
    "telegram_user_id": {{$json.telegram_user_id}},
    "telegram_chat_id": {{$json.telegram_chat_id}},
    "notification_type": "processing_complete",
    "message": "✅ Your document has been processed successfully!",
    "telegram_upload_id": "{{$json.upload_id}}",
    "priority": 3
  }
  ```

---

## 🔄 Workflow 2: Google Drive Backup

### Trigger Node
- **Type:** Supabase Trigger
- **Table:** `storage_registry`
- **Event:** INSERT

### Node 1: Download from S3
**AWS S3 Node:**
- **Operation:** Download
- **Bucket:** `proj344-documents`
- **Key:** `{{$json.primary_storage_path}}`

### Node 2: Upload to Google Drive
**Google Drive Node:**
- **Operation:** Upload
- **Folder:** Legal Case/PROJ344/Documents
- **Name:** `{{$json.original_filename}}`

### Node 3: Update Storage Registry
- **Operation:** Update
- **Table:** `storage_registry`
- **Data:**
  ```json
  {
    "backup_storage_provider": "google_drive",
    "backup_storage_url": "{{$json.drive_url}}",
    "backup_synced_at": "{{$now}}",
    "backup_storage_status": "synced"
  }
  ```

---

## 📊 Workflow 3: AI Enhancement

### Node 1: Extract Text (OCR)
**HTTP Request to AWS Textract or Tesseract**

### Node 2: AI Analysis (OpenAI/Claude)
**HTTP Request:**
- **Endpoint:** OpenAI API or Claude API
- **Prompt:**
  ```
  Analyze this legal document and provide:
  1. Relevancy score (0-1000)
  2. Key quotes
  3. Smoking guns
  4. Executive summary
  5. Document classification
  ```

### Node 3: Update Legal Documents Table
- **Operation:** Insert or Update
- **Table:** `legal_documents`
- **Data:** Results from AI analysis

---

## 🔔 Workflow 4: Notification Sender

### Trigger Node
- **Type:** Schedule
- **Interval:** Every 30 seconds

### Node 1: Get Pending Notifications
- **Operation:** Select
- **Table:** `notification_queue`
- **Filter:** `status.eq.pending`
- **Limit:** 10

### Node 2: Send Telegram Message
**Telegram Node:**
- **Operation:** Send Message
- **Chat ID:** `{{$json.telegram_chat_id}}`
- **Message:** `{{$json.message}}`

### Node 3: Mark as Sent
- **Operation:** Update
- **Table:** `notification_queue`
- **Data:**
  ```json
  {
    "status": "sent",
    "sent_at": "{{$now}}"
  }
  ```

---

## 🗄️ Workflow 5: Archive to Backblaze

### Trigger Node
- **Type:** Schedule
- **Interval:** Weekly (Sunday 2 AM)

### Node 1: Get Old Files
- **Operation:** Select
- **Table:** `storage_registry`
- **Filter:** `stored_at.lt.{{$now.minus(365, 'days')}} AND needs_archive.eq.true`

### Node 2: For Each File
**Loop through files**

### Node 3: Upload to Backblaze B2
**HTTP Request Node:**
- **Endpoint:** Backblaze B2 API
- **Operation:** Upload file

### Node 4: Update Storage Registry
- Mark as archived

---

## 🛠️ Setup Instructions

### 1. Install n8n

**Self-hosted (Docker):**
```bash
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n
```

**Or Cloud:**
https://n8n.io/pricing

### 2. Configure Credentials

Add these credentials in n8n:

- **Supabase:**
  - URL: Your Supabase URL
  - Service Key: Your Supabase service role key

- **AWS S3:**
  - Access Key ID
  - Secret Access Key
  - Region

- **Telegram Bot:**
  - Bot Token

- **Google Drive:**
  - OAuth2 credentials

- **Backblaze B2:**
  - Application Key ID
  - Application Key

### 3. Import Workflows

1. Copy workflow JSON (see below)
2. In n8n, click "Import from File" or "Import from URL"
3. Paste JSON
4. Update credentials
5. Activate workflow

### 4. Test

1. Upload a test document via Telegram
2. Watch workflow execution in n8n
3. Check Supabase tables for updates
4. Verify file appears in S3
5. Check notification received

---

## 📝 Workflow JSON Templates

### Main Processing Workflow (Basic Template)

```json
{
  "name": "Telegram Document Processing",
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "path": "/telegram-upload",
        "method": "POST",
        "authentication": "headerAuth"
      }
    },
    {
      "name": "Supabase - Log Start",
      "type": "n8n-nodes-base.supabase",
      "position": [450, 300],
      "parameters": {
        "operation": "insert",
        "table": "processing_logs"
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{ "node": "Supabase - Log Start", "type": "main", "index": 0 }]]
    }
  }
}
```

---

## 🐛 Troubleshooting

### Workflow not triggering
- Check webhook URL is correct
- Verify webhook authentication
- Check n8n is running

### Files not uploading to S3
- Verify AWS credentials
- Check S3 bucket permissions
- Verify file size within limits

### Notifications not sending
- Check Telegram bot token
- Verify chat ID is correct
- Check notification queue table

---

## 📊 Monitoring

### Key Metrics to Track

1. **Processing Time:** Average time from upload to completion
2. **Success Rate:** % of uploads that complete successfully
3. **Error Rate:** % of uploads that fail
4. **Storage Usage:** Total bytes stored per provider
5. **Queue Length:** Number of pending items in notification queue

### n8n Built-in Monitoring

- View execution history
- Check error logs
- Monitor active workflows
- Track execution time

---

## 🔒 Security Best Practices

1. **Use service role keys** for Supabase (not anon keys)
2. **Encrypt files** at rest in S3
3. **Use presigned URLs** for temporary access
4. **Rotate credentials** regularly
5. **Limit n8n access** to authorized users only
6. **Use webhook auth** to prevent unauthorized triggers

---

## 📚 Resources

- n8n Documentation: https://docs.n8n.io
- Supabase API: https://supabase.com/docs/reference/javascript
- AWS S3 API: https://docs.aws.amazon.com/s3/
- Telegram Bot API: https://core.telegram.org/bots/api

---

**Next Steps:**
1. Set up n8n instance
2. Configure credentials
3. Import main processing workflow
4. Test with sample upload
5. Monitor and optimize

