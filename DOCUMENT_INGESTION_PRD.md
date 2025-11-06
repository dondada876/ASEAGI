# 📱 Document Ingestion System - Product Requirements Document (PRD)

**Version:** 1.0
**Date:** November 6, 2025
**Status:** Draft
**Author:** PROJ344 System Architecture

---

## 🎯 Executive Summary

A comprehensive mobile-first document ingestion, processing, and storage system that captures legal documents via Telegram, processes them through automated workflows, stores them in cloud storage, and makes them queryable through dashboards with full audit trails and notifications.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [Storage Strategy](#storage-strategy)
5. [Processing Pipeline](#processing-pipeline)
6. [Integration Points](#integration-points)
7. [User Interface](#user-interface)
8. [Notifications & Reporting](#notifications--reporting)
9. [Security & Compliance](#security--compliance)
10. [Implementation Roadmap](#implementation-roadmap)

---

## 1. Overview

### 1.1 Problem Statement

Current challenges:
- Manual document entry is time-consuming
- Missing context when scanning documents
- No central tracking of document processing
- Files scattered across multiple storage locations
- Difficult to audit document ingestion history
- No mobile notifications for processing status

### 1.2 Solution

A unified document ingestion system that:
1. **Captures** documents from mobile via Telegram (photos, PDFs, audio, video)
2. **Processes** them through automated n8n workflows
3. **Stores** them in cloud storage (S3/Google Drive/Backblaze)
4. **Indexes** metadata in Supabase for fast querying
5. **Syncs** with Airtable for external review
6. **Tracks** every step with audit logs
7. **Notifies** users of processing status
8. **Displays** in Streamlit dashboards

### 1.3 Success Metrics

- **Upload Speed:** < 30 seconds from phone to database
- **Processing Time:** < 2 minutes for standard documents
- **Query Performance:** < 1 second to find any document
- **Uptime:** 99.5% availability
- **User Satisfaction:** Mobile upload works 100% of the time

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER LAYER                           │
├─────────────────────────────────────────────────────────────┤
│  Telegram App    │  Streamlit Dashboard  │  Airtable Web    │
│  (Mobile/Phone)  │  (Desktop Browser)    │  (External View) │
└──────┬───────────┴──────────┬────────────┴─────────┬────────┘
       │                      │                       │
       v                      v                       v
┌─────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  Telegram Bot    │  Streamlit Forms  │  API Endpoints       │
│  (Real-time)     │  (Web Upload)     │  (Programmatic)      │
└──────┬───────────┴──────────┬────────┴──────────────┬───────┘
       │                      │                        │
       v                      v                        v
┌─────────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                         │
├─────────────────────────────────────────────────────────────┤
│                     n8n Workflow Engine                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Validate   │→ │   Process    │→ │   Enhance    │     │
│  │   File Type  │  │   Metadata   │  │   with AI    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           │                 │                  │            │
│           v                 v                  v            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Extract    │  │    Store     │  │   Notify     │     │
│  │   Metadata   │  │   in Cloud   │  │    User      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────┬───────────────────┬─────────────────┬────────────────┘
       │                   │                 │
       v                   v                 v
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                             │
├─────────────────────────────────────────────────────────────┤
│           Supabase (Source of Truth)                        │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ telegram_uploads │  │ processing_logs  │               │
│  │  (Raw Uploads)   │  │ (Audit Trail)    │               │
│  └──────────────────┘  └──────────────────┘               │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ legal_documents  │  │ storage_registry │               │
│  │ (Final State)    │  │ (File Locations) │               │
│  └──────────────────┘  └──────────────────┘               │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               v
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Amazon S3  │  │ Google Drive│  │  Backblaze  │        │
│  │  (Primary)  │  │  (Backup)   │  │  (Archive)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                               │
                               v
┌─────────────────────────────────────────────────────────────┐
│                  INTEGRATION LAYER                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Airtable   │  │   Zapier    │  │   Webhooks  │        │
│  │  (Review)   │  │  (Backup)   │  │  (Custom)   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

**Upload Flow:**
1. User sends file to Telegram bot
2. Bot receives file → creates `telegram_uploads` record (status: `received`)
3. Bot uploads file to temporary storage
4. Bot adds job to n8n queue
5. n8n processes file → updates `processing_logs`
6. File stored to cloud (S3/Drive/Backblaze) → `storage_registry` updated
7. Metadata extracted → `legal_documents` created
8. User notified → status: `completed`

**Query Flow:**
1. User searches in Streamlit dashboard
2. Dashboard queries `legal_documents` table
3. Links to `storage_registry` for file location
4. User can view/download from cloud storage
5. All access logged in `processing_logs`

---

## 3. Database Schema

### 3.1 Core Tables

#### `telegram_uploads` (Source of Truth)

Primary table for all Telegram submissions.

```sql
CREATE TABLE telegram_uploads (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Telegram Metadata
    telegram_user_id BIGINT NOT NULL,
    telegram_username TEXT,
    telegram_message_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,

    -- File Information
    file_id TEXT NOT NULL, -- Telegram file_id
    file_type TEXT NOT NULL, -- 'photo', 'document', 'audio', 'video', 'voice'
    file_name TEXT,
    file_size BIGINT, -- bytes
    mime_type TEXT,
    file_extension TEXT,

    -- User-Provided Metadata (from form)
    document_type TEXT, -- PLCR, DECL, EVID, etc.
    document_date TEXT, -- YYYYMMDD format
    document_title TEXT,
    user_notes TEXT,
    relevancy_level TEXT, -- Critical, High, Medium, Low
    relevancy_score INTEGER,

    -- Processing Status
    status TEXT NOT NULL DEFAULT 'received',
        -- received, validating, processing, storing, completed, failed, partial
    processing_stage TEXT, -- current stage in pipeline
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Storage References
    temp_storage_url TEXT, -- temporary Telegram URL
    permanent_storage_url TEXT, -- final S3/Drive/Backblaze URL
    storage_provider TEXT, -- 's3', 'google_drive', 'backblaze'
    storage_path TEXT, -- path within storage

    -- Processing Metadata
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processing_duration_seconds INTEGER,

    -- Links to Other Tables
    legal_document_id UUID REFERENCES legal_documents(id),
    storage_registry_id UUID REFERENCES storage_registry(id),

    -- Timestamps
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Flags
    is_deleted BOOLEAN DEFAULT FALSE,
    needs_review BOOLEAN DEFAULT FALSE,
    is_duplicate BOOLEAN DEFAULT FALSE,

    -- Metadata JSON (flexible for future fields)
    raw_telegram_data JSONB,
    processing_metadata JSONB,

    -- Indexes
    CONSTRAINT telegram_uploads_unique_message UNIQUE (telegram_chat_id, telegram_message_id)
);

CREATE INDEX idx_telegram_uploads_status ON telegram_uploads(status);
CREATE INDEX idx_telegram_uploads_user ON telegram_uploads(telegram_user_id);
CREATE INDEX idx_telegram_uploads_uploaded_at ON telegram_uploads(uploaded_at DESC);
CREATE INDEX idx_telegram_uploads_file_type ON telegram_uploads(file_type);
CREATE INDEX idx_telegram_uploads_processing_stage ON telegram_uploads(processing_stage);
```

#### `processing_logs` (Audit Trail)

Detailed log of every processing step.

```sql
CREATE TABLE processing_logs (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Reference
    telegram_upload_id UUID REFERENCES telegram_uploads(id),
    legal_document_id UUID REFERENCES legal_documents(id),

    -- Log Entry
    stage TEXT NOT NULL, -- 'validation', 'extraction', 'storage', 'enhancement', etc.
    status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'warning'
    message TEXT,
    details JSONB, -- structured log data

    -- Error Handling
    error_code TEXT,
    error_details TEXT,
    stack_trace TEXT,

    -- Performance
    duration_ms INTEGER,

    -- Context
    triggered_by TEXT, -- 'telegram_bot', 'n8n', 'manual', 'retry'
    worker_id TEXT, -- which worker/process handled this

    -- Timestamps
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Indexes
    CREATE INDEX idx_processing_logs_upload ON processing_logs(telegram_upload_id);
    CREATE INDEX idx_processing_logs_stage ON processing_logs(stage);
    CREATE INDEX idx_processing_logs_status ON processing_logs(status);
    CREATE INDEX idx_processing_logs_logged_at ON processing_logs(logged_at DESC);
);
```

#### `storage_registry` (File Location Index)

Central registry of where files are stored.

```sql
CREATE TABLE storage_registry (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- File Identification
    file_hash TEXT NOT NULL, -- MD5 or SHA256
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT,

    -- Primary Storage
    primary_storage_provider TEXT NOT NULL, -- 's3', 'google_drive', 'backblaze'
    primary_storage_url TEXT NOT NULL,
    primary_storage_path TEXT NOT NULL,
    primary_storage_bucket TEXT,

    -- Backup Storage (optional)
    backup_storage_provider TEXT,
    backup_storage_url TEXT,
    backup_storage_path TEXT,

    -- Archive Storage (optional)
    archive_storage_provider TEXT,
    archive_storage_url TEXT,
    archive_storage_path TEXT,

    -- Access Control
    is_public BOOLEAN DEFAULT FALSE,
    access_level TEXT DEFAULT 'private', -- 'public', 'private', 'restricted'
    access_expiry TIMESTAMPTZ,

    -- Lifecycle
    storage_class TEXT DEFAULT 'standard', -- 'standard', 'infrequent', 'glacier'
    delete_after_days INTEGER,
    archived_at TIMESTAMPTZ,

    -- References
    telegram_upload_id UUID REFERENCES telegram_uploads(id),
    legal_document_id UUID REFERENCES legal_documents(id),

    -- Timestamps
    stored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    storage_metadata JSONB,

    -- Indexes
    CREATE INDEX idx_storage_registry_hash ON storage_registry(file_hash);
    CREATE INDEX idx_storage_registry_provider ON storage_registry(primary_storage_provider);
    CREATE INDEX idx_storage_registry_upload ON storage_registry(telegram_upload_id);
);
```

#### `notification_queue` (User Notifications)

Queue for sending status notifications.

```sql
CREATE TABLE notification_queue (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Recipient
    telegram_user_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,

    -- Notification Content
    notification_type TEXT NOT NULL, -- 'upload_received', 'processing_complete', 'error', etc.
    title TEXT,
    message TEXT NOT NULL,

    -- Related Data
    telegram_upload_id UUID REFERENCES telegram_uploads(id),

    -- Status
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'sent', 'failed'
    sent_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Priority
    priority INTEGER DEFAULT 5, -- 1 (urgent) to 10 (low)

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    notification_data JSONB,

    -- Indexes
    CREATE INDEX idx_notification_queue_status ON notification_queue(status, priority);
    CREATE INDEX idx_notification_queue_user ON notification_queue(telegram_user_id);
);
```

### 3.2 Updated `legal_documents` Table

Add fields to link with telegram uploads:

```sql
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS telegram_upload_id UUID REFERENCES telegram_uploads(id);
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS storage_registry_id UUID REFERENCES storage_registry(id);
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual'; -- 'telegram', 'web_upload', 'api', 'manual'
ALTER TABLE legal_documents ADD COLUMN IF NOT EXISTS processing_status TEXT DEFAULT 'pending'; -- 'pending', 'processing', 'completed', 'failed'
```

---

## 4. Storage Strategy

### 4.1 Multi-Tier Storage Architecture

**Tier 1: Primary Storage (Amazon S3)**
- **Purpose:** Fast access, primary source
- **Retention:** Permanent
- **Use Case:** Active documents, frequent access
- **Cost:** ~$0.023/GB/month
- **Path Structure:** `s3://proj344-documents/{year}/{month}/{document_type}/{filename}`

**Tier 2: Backup Storage (Google Drive)**
- **Purpose:** Redundancy, external access
- **Retention:** Permanent
- **Use Case:** Client access, sharing with attorney
- **Cost:** Included in Google Workspace
- **Path Structure:** `Legal Case/PROJ344/Documents/{year}/{document_type}/{filename}`

**Tier 3: Archive Storage (Backblaze B2)**
- **Purpose:** Long-term cold storage
- **Retention:** Permanent archive
- **Use Case:** Documents older than 1 year
- **Cost:** $0.005/GB/month (cheaper)
- **Path Structure:** `b2://proj344-archive/{year}/{filename}`

### 4.2 Storage Lifecycle

```
Upload → S3 (Primary) → [Immediately] Google Drive (Backup)
                      → [After 1 year] Backblaze (Archive)
```

### 4.3 File Naming Convention

```
{YYMMDD}_{Source}_{DocType}_{Description}_{Scores}.{ext}

Example:
240804_Telegram_PLCR_Police_Report_Child_Safe_Mic-850_Mac-900_LEG-920_REL-892.jpg
```

---

## 5. Processing Pipeline

### 5.1 n8n Workflow Stages

**Stage 1: Validation** (0-5 seconds)
- Check file type is supported
- Verify file size < 20MB
- Scan for duplicates (file hash)
- Log: `processing_logs` (stage: validation)

**Stage 2: Upload to Storage** (5-30 seconds)
- Download from Telegram
- Upload to S3
- Generate permanent URL
- Create `storage_registry` entry
- Log: `processing_logs` (stage: storage)

**Stage 3: Metadata Extraction** (10-60 seconds)
- Extract text (OCR if image)
- Identify document type
- Extract dates, names, key facts
- Log: `processing_logs` (stage: extraction)

**Stage 4: AI Enhancement** (30-120 seconds)
- Generate relevancy scores
- Extract key quotes
- Identify smoking guns
- Create executive summary
- Log: `processing_logs` (stage: enhancement)

**Stage 5: Database Insert** (1-2 seconds)
- Create `legal_documents` record
- Update `telegram_uploads` with legal_document_id
- Log: `processing_logs` (stage: finalization)

**Stage 6: Notification** (1-5 seconds)
- Queue notification to user
- Send Telegram message with status
- Log: `processing_logs` (stage: notification)

**Stage 7: External Sync** (5-15 seconds)
- Sync to Airtable (if configured)
- Update external systems
- Log: `processing_logs` (stage: sync)

### 5.2 Error Handling

**Retry Strategy:**
- Automatic retry: 3 attempts with exponential backoff (2s, 4s, 8s)
- After 3 failures: Mark as `failed`, notify user
- User can manually retry from dashboard

**Partial Processing:**
- If stages 1-2 succeed but 3-4 fail: Status = `partial`
- File is stored but not fully processed
- User can trigger reprocessing

---

## 6. Integration Points

### 6.1 n8n Workflows

**Workflow 1: Main Processing Pipeline**
- Trigger: Webhook from Telegram bot
- Nodes: Validation → Storage → Extraction → Enhancement → Notification
- Duration: 1-3 minutes

**Workflow 2: Backup to Google Drive**
- Trigger: New S3 upload
- Action: Copy to Google Drive
- Duration: 10-30 seconds

**Workflow 3: Archive to Backblaze**
- Trigger: Scheduled (weekly)
- Action: Move old files (>1 year) to Backblaze
- Duration: Batch process

**Workflow 4: Airtable Sync**
- Trigger: New legal_documents record
- Action: Create/update Airtable record
- Duration: 5-10 seconds

### 6.2 Airtable Integration

**Airtable Base: PROJ344 Legal Case**

**Table: Documents**
- Synced fields from `legal_documents`
- Links to files in Google Drive
- Allows external review/comments
- Sync: Real-time via n8n

**Use Cases:**
- Share with attorney for review
- Client access to documents
- External collaborator viewing

---

## 7. User Interface

### 7.1 Telegram Bot Enhancements

**New File Type Support:**
- 📸 Photos (existing)
- 📄 PDFs (existing)
- 🎤 Audio files (.mp3, .wav, .m4a)
- 🎥 Video files (.mp4, .mov)
- 🎙️ Voice messages

**New Commands:**
- `/status {id}` - Check processing status
- `/list` - View recent uploads
- `/retry {id}` - Retry failed upload
- `/cancel {id}` - Cancel processing

### 7.2 Streamlit Dashboard: Telegram Uploads

**Dashboard: `telegram_uploads_dashboard.py`**

**Tab 1: Upload Status**
- Real-time view of all uploads
- Filter by: status, date, file type
- Color-coded status indicators
- Progress bars for processing

**Tab 2: Processing Logs**
- Detailed audit trail
- Filter by upload ID
- Timeline visualization
- Error details

**Tab 3: Storage Management**
- View file locations
- Test storage URLs
- Backup status
- Storage usage statistics

**Tab 4: Analytics**
- Upload trends over time
- Processing success rate
- Average processing time
- Storage costs

**Tab 5: Manual Actions**
- Retry failed uploads
- Reprocess documents
- Delete uploads
- Download files

---

## 8. Notifications & Reporting

### 8.1 Real-Time Notifications

**User Notifications (via Telegram):**

1. **Upload Received** (immediate)
   ```
   ✅ Upload Received!
   📄 File: police_report.jpg
   🆔 ID: 1234
   ⏳ Processing started...
   ```

2. **Processing Complete** (1-3 min later)
   ```
   🎉 Processing Complete!
   📄 Document: Police Report - Child Safe
   ⭐ Relevancy: 892 (Critical)
   🔗 View: [Dashboard Link]
   ```

3. **Processing Failed** (if error)
   ```
   ❌ Processing Failed
   📄 File: report.pdf
   🐛 Error: Invalid file format
   🔄 Use /retry 1234 to try again
   ```

### 8.2 Summary Reports

**Daily Summary (8 PM)**
```
📊 Today's Document Activity

✅ Successful: 12 uploads
⚠️ Partial: 2 uploads
❌ Failed: 1 upload

📈 This Week: 45 documents
💾 Storage Used: 2.3 GB

🔗 View Dashboard
```

**Weekly Report (Sunday)**
```
📈 Weekly Summary

Total Uploads: 45
Police Reports: 8
Declarations: 12
Evidence Photos: 25

⭐ Critical Documents: 5
🎯 Processing Success: 96%
⚡ Avg Processing Time: 42s

🔗 Full Report
```

---

## 9. Security & Compliance

### 9.1 Data Protection

- ✅ End-to-end encryption for uploads
- ✅ Files encrypted at rest (S3 SSE)
- ✅ Access logs for all file access
- ✅ Row-level security in Supabase
- ✅ Private Telegram bot (not public)

### 9.2 Retention Policy

- **Active Documents:** Permanent (S3)
- **Processing Logs:** 2 years
- **Notification Queue:** 30 days
- **Telegram Temp Files:** 24 hours

### 9.3 Access Control

- **Supabase:** RLS policies per user
- **S3:** Presigned URLs with expiry
- **Google Drive:** Shared only with authorized users
- **Airtable:** Read-only for external reviewers

---

## 10. Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ Create database schemas
- ✅ Deploy Telegram bot with new tables
- ✅ Implement S3 storage integration
- ✅ Build basic processing pipeline

### Phase 2: Processing & Logging (Week 3-4)
- Build n8n workflows
- Implement processing logs
- Add error handling & retry logic
- Create notification system

### Phase 3: Storage & Backup (Week 5-6)
- Integrate Google Drive backup
- Set up Backblaze archive
- Implement lifecycle policies
- Build storage dashboard

### Phase 4: Enhancements (Week 7-8)
- Add audio/video support
- Build Telegram uploads dashboard
- Integrate Airtable sync
- Add analytics & reporting

### Phase 5: Testing & Polish (Week 9-10)
- End-to-end testing
- Performance optimization
- Documentation
- User training

---

## 11. Success Criteria

### Technical Metrics
- ✅ 99.5% upload success rate
- ✅ < 2 min average processing time
- ✅ < 1 sec query response time
- ✅ Zero data loss

### User Experience
- ✅ Mobile upload works every time
- ✅ Status updates within 30 seconds
- ✅ Easy to find any document
- ✅ Clear error messages

### Business Impact
- ✅ 10x faster document ingestion
- ✅ 100% audit trail for compliance
- ✅ Reduced storage costs (tiered storage)
- ✅ Better case organization

---

## 12. Cost Estimates

### Monthly Costs (Estimated)

**Storage:**
- S3 (100 GB): $2.30
- Google Drive: $0 (included)
- Backblaze (500 GB archive): $2.50
- **Total Storage:** $4.80/month

**Compute:**
- n8n Cloud: $20/month (or self-hosted: $0)
- Telegram Bot: $0 (free)
- Supabase: $25/month (Pro plan)
- **Total Compute:** $45/month

**Integrations:**
- Airtable: $20/month (Pro plan)
- **Total:** $20/month

**Grand Total:** ~$70/month

---

## 13. Open Questions

1. **AI Processing:** Which AI service for document analysis? (OpenAI, Claude, local?)
2. **OCR:** Use Tesseract (free) or AWS Textract (paid)?
3. **Video Transcription:** Whisper API or AssemblyAI?
4. **Hosting:** Self-host n8n or use cloud?
5. **Airtable Sync:** Real-time or batch (hourly)?

---

## 14. Next Steps

### Immediate (This Week)
1. Review and approve this PRD
2. Create database schemas
3. Update Telegram bot with new tables
4. Set up S3 bucket

### Short Term (Next 2 Weeks)
1. Build processing pipeline in n8n
2. Create Telegram uploads dashboard
3. Implement notifications
4. Test end-to-end flow

### Long Term (Next Month)
1. Add audio/video support
2. Integrate Airtable
3. Build analytics dashboard
4. Deploy to production

---

## 15. Appendix

### A. Glossary

- **Source of Truth:** Primary database (telegram_uploads table)
- **Processing Stage:** Current step in pipeline
- **Partial Processing:** File stored but not fully analyzed
- **Storage Registry:** Index of where files are stored
- **Audit Trail:** Complete history of processing steps

### B. Reference Links

- Telegram Bot API: https://core.telegram.org/bots/api
- n8n Documentation: https://docs.n8n.io
- Supabase Docs: https://supabase.com/docs
- AWS S3: https://aws.amazon.com/s3/
- Backblaze B2: https://www.backblaze.com/b2/

---

**Document Version Control:**
- v1.0 (2025-11-06): Initial draft
- Next Review: After team feedback

---

**Prepared by:** PROJ344 System Architecture Team
**Contact:** [Your Contact Info]
**Status:** Ready for Review & Implementation

