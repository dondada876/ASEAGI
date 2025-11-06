-- ============================================================================
-- TELEGRAM DOCUMENT INGESTION SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- Description: Complete schema for Telegram-based document ingestion with
--              processing logs, storage registry, and notifications
-- Version: 1.0
-- Date: 2025-11-06
-- Usage: Run this SQL in your Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- TABLE 1: telegram_uploads (Source of Truth)
-- ============================================================================
-- Primary table for all Telegram submissions

CREATE TABLE IF NOT EXISTS public.telegram_uploads (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Telegram Metadata
    telegram_user_id BIGINT NOT NULL,
    telegram_username TEXT,
    telegram_first_name TEXT,
    telegram_last_name TEXT,
    telegram_message_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,

    -- File Information
    file_id TEXT NOT NULL, -- Telegram file_id
    file_unique_id TEXT, -- Telegram file_unique_id
    file_type TEXT NOT NULL, -- 'photo', 'document', 'audio', 'video', 'voice'
    file_name TEXT,
    file_size BIGINT, -- bytes
    mime_type TEXT,
    file_extension TEXT,
    file_hash TEXT, -- MD5 hash for duplicate detection

    -- User-Provided Metadata (from conversational form)
    document_type TEXT, -- PLCR, DECL, EVID, CPSR, RESP, FORN, ORDR, MOTN, HEAR, OTHR
    document_date TEXT, -- YYYYMMDD format
    document_title TEXT,
    user_notes TEXT,
    relevancy_level TEXT, -- Critical, High, Medium, Low
    relevancy_score INTEGER,

    -- Processing Status
    status TEXT NOT NULL DEFAULT 'received',
        -- 'received', 'validating', 'processing', 'storing', 'completed', 'failed', 'partial'
    processing_stage TEXT, -- current stage in pipeline
    error_message TEXT,
    error_code TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Storage References
    temp_storage_url TEXT, -- temporary Telegram URL (expires)
    permanent_storage_url TEXT, -- final S3/Drive/Backblaze URL
    storage_provider TEXT, -- 's3', 'google_drive', 'backblaze'
    storage_path TEXT, -- path within storage provider
    storage_bucket TEXT, -- bucket/container name

    -- Processing Metadata
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processing_duration_seconds INTEGER,

    -- Links to Other Tables
    legal_document_id UUID, -- will reference legal_documents(id)
    storage_registry_id UUID, -- will reference storage_registry(id)

    -- Timestamps
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Flags
    is_deleted BOOLEAN DEFAULT FALSE,
    needs_review BOOLEAN DEFAULT FALSE,
    is_duplicate BOOLEAN DEFAULT FALSE,
    notification_sent BOOLEAN DEFAULT FALSE,

    -- Metadata JSON (flexible for future fields)
    raw_telegram_data JSONB, -- full Telegram message object
    processing_metadata JSONB, -- processing details
    user_metadata JSONB, -- additional user-provided data

    -- Constraints
    CONSTRAINT telegram_uploads_unique_message UNIQUE (telegram_chat_id, telegram_message_id),
    CONSTRAINT telegram_uploads_status_check CHECK (status IN
        ('received', 'validating', 'processing', 'storing', 'completed', 'failed', 'partial'))
);

-- Indexes for telegram_uploads
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_status ON public.telegram_uploads(status) WHERE is_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_user ON public.telegram_uploads(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_uploaded_at ON public.telegram_uploads(uploaded_at DESC);
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_file_type ON public.telegram_uploads(file_type);
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_processing_stage ON public.telegram_uploads(processing_stage) WHERE status NOT IN ('completed', 'failed');
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_document_type ON public.telegram_uploads(document_type);
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_file_hash ON public.telegram_uploads(file_hash) WHERE file_hash IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_telegram_uploads_legal_doc ON public.telegram_uploads(legal_document_id) WHERE legal_document_id IS NOT NULL;

-- ============================================================================
-- TABLE 2: processing_logs (Audit Trail)
-- ============================================================================
-- Detailed log of every processing step

CREATE TABLE IF NOT EXISTS public.processing_logs (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- References
    telegram_upload_id UUID REFERENCES public.telegram_uploads(id) ON DELETE CASCADE,
    legal_document_id UUID, -- reference to legal_documents(id)

    -- Log Entry
    stage TEXT NOT NULL, -- 'validation', 'extraction', 'storage', 'enhancement', 'notification', etc.
    status TEXT NOT NULL, -- 'started', 'completed', 'failed', 'warning', 'info'
    message TEXT NOT NULL,
    details JSONB, -- structured log data

    -- Error Handling
    error_code TEXT,
    error_details TEXT,
    stack_trace TEXT,

    -- Performance Metrics
    duration_ms INTEGER,
    memory_usage_mb NUMERIC(10,2),

    -- Context
    triggered_by TEXT, -- 'telegram_bot', 'n8n', 'manual', 'retry', 'scheduled'
    worker_id TEXT, -- which worker/process handled this
    workflow_id TEXT, -- n8n workflow execution ID

    -- Timestamps
    logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT processing_logs_status_check CHECK (status IN ('started', 'completed', 'failed', 'warning', 'info'))
);

-- Indexes for processing_logs
CREATE INDEX IF NOT EXISTS idx_processing_logs_upload ON public.processing_logs(telegram_upload_id);
CREATE INDEX IF NOT EXISTS idx_processing_logs_stage ON public.processing_logs(stage);
CREATE INDEX IF NOT EXISTS idx_processing_logs_status ON public.processing_logs(status);
CREATE INDEX IF NOT EXISTS idx_processing_logs_logged_at ON public.processing_logs(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_processing_logs_legal_doc ON public.processing_logs(legal_document_id) WHERE legal_document_id IS NOT NULL;

-- ============================================================================
-- TABLE 3: storage_registry (File Location Index)
-- ============================================================================
-- Central registry of where files are stored

CREATE TABLE IF NOT EXISTS public.storage_registry (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- File Identification
    file_hash TEXT NOT NULL, -- MD5 or SHA256
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL, -- bytes
    mime_type TEXT,
    file_extension TEXT,

    -- Primary Storage
    primary_storage_provider TEXT NOT NULL, -- 's3', 'google_drive', 'backblaze'
    primary_storage_url TEXT NOT NULL,
    primary_storage_path TEXT NOT NULL,
    primary_storage_bucket TEXT,
    primary_storage_region TEXT,

    -- Backup Storage (optional)
    backup_storage_provider TEXT,
    backup_storage_url TEXT,
    backup_storage_path TEXT,
    backup_storage_status TEXT, -- 'pending', 'synced', 'failed'
    backup_synced_at TIMESTAMPTZ,

    -- Archive Storage (optional, for old files)
    archive_storage_provider TEXT,
    archive_storage_url TEXT,
    archive_storage_path TEXT,
    archive_storage_class TEXT, -- 'glacier', 'deep_archive'
    archived_at TIMESTAMPTZ,

    -- Access Control
    is_public BOOLEAN DEFAULT FALSE,
    access_level TEXT DEFAULT 'private', -- 'public', 'private', 'restricted'
    presigned_url TEXT, -- temporary access URL
    presigned_url_expires_at TIMESTAMPTZ,

    -- Lifecycle Management
    storage_class TEXT DEFAULT 'standard', -- 'standard', 'infrequent_access', 'archive'
    lifecycle_policy TEXT, -- e.g., 'archive_after_365_days'
    delete_after_days INTEGER,
    scheduled_deletion_at TIMESTAMPTZ,

    -- References
    telegram_upload_id UUID REFERENCES public.telegram_uploads(id) ON DELETE CASCADE,
    legal_document_id UUID, -- reference to legal_documents(id)

    -- Usage Tracking
    access_count INTEGER DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    last_accessed_by TEXT,

    -- Timestamps
    stored_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Flags
    is_deleted BOOLEAN DEFAULT FALSE,
    needs_backup BOOLEAN DEFAULT TRUE,
    needs_archive BOOLEAN DEFAULT FALSE,

    -- Metadata
    storage_metadata JSONB,

    -- Constraints
    CONSTRAINT storage_registry_provider_check CHECK (primary_storage_provider IN ('s3', 'google_drive', 'backblaze', 'local')),
    CONSTRAINT storage_registry_access_check CHECK (access_level IN ('public', 'private', 'restricted'))
);

-- Indexes for storage_registry
CREATE INDEX IF NOT EXISTS idx_storage_registry_hash ON public.storage_registry(file_hash);
CREATE INDEX IF NOT EXISTS idx_storage_registry_provider ON public.storage_registry(primary_storage_provider);
CREATE INDEX IF NOT EXISTS idx_storage_registry_upload ON public.storage_registry(telegram_upload_id);
CREATE INDEX IF NOT EXISTS idx_storage_registry_legal_doc ON public.storage_registry(legal_document_id) WHERE legal_document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_storage_registry_backup_status ON public.storage_registry(backup_storage_status) WHERE backup_storage_status = 'pending';
CREATE INDEX IF NOT EXISTS idx_storage_registry_needs_archive ON public.storage_registry(needs_archive) WHERE needs_archive = TRUE;

-- ============================================================================
-- TABLE 4: notification_queue (User Notifications)
-- ============================================================================
-- Queue for sending status notifications to users

CREATE TABLE IF NOT EXISTS public.notification_queue (
    -- Primary Key
    id BIGSERIAL PRIMARY KEY,

    -- Recipient
    telegram_user_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,
    telegram_username TEXT,

    -- Notification Content
    notification_type TEXT NOT NULL, -- 'upload_received', 'processing_complete', 'processing_failed', 'error', 'warning', 'daily_summary', 'weekly_report'
    title TEXT,
    message TEXT NOT NULL,
    action_buttons JSONB, -- optional inline keyboard buttons

    -- Related Data
    telegram_upload_id UUID REFERENCES public.telegram_uploads(id) ON DELETE CASCADE,
    legal_document_id UUID, -- reference to legal_documents(id)

    -- Status
    status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'sent', 'failed', 'cancelled'
    sent_at TIMESTAMPTZ,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,

    -- Priority (1 = urgent, 10 = low)
    priority INTEGER DEFAULT 5,

    -- Scheduling
    scheduled_for TIMESTAMPTZ, -- if NULL, send immediately
    send_after TIMESTAMPTZ DEFAULT NOW(),

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    notification_data JSONB,

    -- Constraints
    CONSTRAINT notification_queue_status_check CHECK (status IN ('pending', 'sent', 'failed', 'cancelled')),
    CONSTRAINT notification_queue_priority_check CHECK (priority BETWEEN 1 AND 10)
);

-- Indexes for notification_queue
CREATE INDEX IF NOT EXISTS idx_notification_queue_status_priority ON public.notification_queue(status, priority, send_after) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_notification_queue_user ON public.notification_queue(telegram_user_id);
CREATE INDEX IF NOT EXISTS idx_notification_queue_type ON public.notification_queue(notification_type);
CREATE INDEX IF NOT EXISTS idx_notification_queue_upload ON public.notification_queue(telegram_upload_id) WHERE telegram_upload_id IS NOT NULL;

-- ============================================================================
-- TABLE 5: user_preferences (User Settings)
-- ============================================================================
-- User preferences for notifications and processing

CREATE TABLE IF NOT EXISTS public.user_preferences (
    -- Primary Key
    telegram_user_id BIGINT PRIMARY KEY,
    telegram_username TEXT,

    -- Notification Preferences
    notify_on_upload BOOLEAN DEFAULT TRUE,
    notify_on_complete BOOLEAN DEFAULT TRUE,
    notify_on_error BOOLEAN DEFAULT TRUE,
    notify_daily_summary BOOLEAN DEFAULT TRUE,
    notify_weekly_report BOOLEAN DEFAULT FALSE,
    notification_quiet_hours_start TIME, -- e.g., '22:00'
    notification_quiet_hours_end TIME, -- e.g., '08:00'

    -- Processing Preferences
    auto_process BOOLEAN DEFAULT TRUE,
    auto_backup BOOLEAN DEFAULT TRUE,
    auto_archive_after_days INTEGER DEFAULT 365,
    default_relevancy_level TEXT DEFAULT 'Medium',

    -- Storage Preferences
    preferred_storage_provider TEXT DEFAULT 's3',
    enable_backup BOOLEAN DEFAULT TRUE,
    enable_archive BOOLEAN DEFAULT TRUE,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Metadata
    preferences_json JSONB
);

-- Index for user_preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_username ON public.user_preferences(telegram_username);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Recent uploads with processing status
CREATE OR REPLACE VIEW public.telegram_uploads_recent AS
SELECT
    tu.id,
    tu.telegram_username,
    tu.file_name,
    tu.file_type,
    tu.document_type,
    tu.document_title,
    tu.status,
    tu.processing_stage,
    tu.uploaded_at,
    tu.processing_duration_seconds,
    tu.error_message,
    CASE
        WHEN tu.status = 'completed' THEN '✅'
        WHEN tu.status = 'failed' THEN '❌'
        WHEN tu.status = 'processing' THEN '⏳'
        WHEN tu.status = 'partial' THEN '⚠️'
        ELSE '📥'
    END as status_icon
FROM public.telegram_uploads tu
WHERE tu.uploaded_at > NOW() - INTERVAL '7 days'
  AND tu.is_deleted = FALSE
ORDER BY tu.uploaded_at DESC;

-- View: Processing statistics
CREATE OR REPLACE VIEW public.processing_statistics AS
SELECT
    DATE_TRUNC('day', uploaded_at) as day,
    COUNT(*) as total_uploads,
    COUNT(*) FILTER (WHERE status = 'completed') as completed,
    COUNT(*) FILTER (WHERE status = 'failed') as failed,
    COUNT(*) FILTER (WHERE status = 'partial') as partial,
    COUNT(*) FILTER (WHERE status IN ('processing', 'validating', 'storing')) as in_progress,
    ROUND(AVG(processing_duration_seconds)) as avg_processing_seconds,
    SUM(file_size) as total_bytes
FROM public.telegram_uploads
WHERE uploaded_at > NOW() - INTERVAL '30 days'
  AND is_deleted = FALSE
GROUP BY DATE_TRUNC('day', uploaded_at)
ORDER BY day DESC;

-- View: Storage usage by provider
CREATE OR REPLACE VIEW public.storage_usage AS
SELECT
    primary_storage_provider,
    COUNT(*) as file_count,
    SUM(file_size) as total_bytes,
    ROUND(SUM(file_size)::NUMERIC / (1024*1024*1024), 2) as total_gb,
    MAX(stored_at) as last_upload
FROM public.storage_registry
WHERE is_deleted = FALSE
GROUP BY primary_storage_provider
ORDER BY total_bytes DESC;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: Log processing stage
CREATE OR REPLACE FUNCTION log_processing_stage(
    p_upload_id UUID,
    p_stage TEXT,
    p_status TEXT,
    p_message TEXT,
    p_details JSONB DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
    v_log_id BIGINT;
BEGIN
    INSERT INTO public.processing_logs (
        telegram_upload_id,
        stage,
        status,
        message,
        details,
        triggered_by
    ) VALUES (
        p_upload_id,
        p_stage,
        p_status,
        p_message,
        p_details,
        'system'
    ) RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Function: Queue notification
CREATE OR REPLACE FUNCTION queue_notification(
    p_user_id BIGINT,
    p_chat_id BIGINT,
    p_type TEXT,
    p_message TEXT,
    p_upload_id UUID DEFAULT NULL,
    p_priority INTEGER DEFAULT 5
)
RETURNS BIGINT AS $$
DECLARE
    v_notification_id BIGINT;
    v_username TEXT;
BEGIN
    -- Get username from upload or preferences
    SELECT telegram_username INTO v_username
    FROM public.telegram_uploads
    WHERE id = p_upload_id
    LIMIT 1;

    INSERT INTO public.notification_queue (
        telegram_user_id,
        telegram_chat_id,
        telegram_username,
        notification_type,
        message,
        telegram_upload_id,
        priority
    ) VALUES (
        p_user_id,
        p_chat_id,
        v_username,
        p_type,
        p_message,
        p_upload_id,
        p_priority
    ) RETURNING id INTO v_notification_id;

    RETURN v_notification_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger: Auto-update updated_at on telegram_uploads
DROP TRIGGER IF EXISTS set_telegram_uploads_updated_at ON public.telegram_uploads;
CREATE TRIGGER set_telegram_uploads_updated_at
    BEFORE UPDATE ON public.telegram_uploads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-update updated_at on storage_registry
DROP TRIGGER IF EXISTS set_storage_registry_updated_at ON public.storage_registry;
CREATE TRIGGER set_storage_registry_updated_at
    BEFORE UPDATE ON public.storage_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger: Auto-update updated_at on user_preferences
DROP TRIGGER IF EXISTS set_user_preferences_updated_at ON public.user_preferences;
CREATE TRIGGER set_user_preferences_updated_at
    BEFORE UPDATE ON public.user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.telegram_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.storage_registry ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notification_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all for authenticated users (adjust based on your needs)
CREATE POLICY "Allow all for authenticated users" ON public.telegram_uploads
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON public.processing_logs
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON public.storage_registry
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON public.notification_queue
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users" ON public.user_preferences
    FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- Policy: Allow service role full access
CREATE POLICY "Allow service role full access" ON public.telegram_uploads
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Allow service role full access" ON public.processing_logs
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Allow service role full access" ON public.storage_registry
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Allow service role full access" ON public.notification_queue
    FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Allow service role full access" ON public.user_preferences
    FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant access to authenticated users
GRANT ALL ON public.telegram_uploads TO authenticated;
GRANT ALL ON public.processing_logs TO authenticated;
GRANT ALL ON public.storage_registry TO authenticated;
GRANT ALL ON public.notification_queue TO authenticated;
GRANT ALL ON public.user_preferences TO authenticated;

-- Grant access to service role
GRANT ALL ON public.telegram_uploads TO service_role;
GRANT ALL ON public.processing_logs TO service_role;
GRANT ALL ON public.storage_registry TO service_role;
GRANT ALL ON public.notification_queue TO service_role;
GRANT ALL ON public.user_preferences TO service_role;

-- Grant sequence usage
GRANT USAGE, SELECT ON SEQUENCE public.processing_logs_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.notification_queue_id_seq TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.processing_logs_id_seq TO service_role;
GRANT USAGE, SELECT ON SEQUENCE public.notification_queue_id_seq TO service_role;

-- Grant view access
GRANT SELECT ON public.telegram_uploads_recent TO authenticated;
GRANT SELECT ON public.processing_statistics TO authenticated;
GRANT SELECT ON public.storage_usage TO authenticated;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get all uploads from last 24 hours
-- SELECT * FROM telegram_uploads_recent WHERE uploaded_at > NOW() - INTERVAL '24 hours';

-- Get processing logs for a specific upload
-- SELECT * FROM processing_logs WHERE telegram_upload_id = 'your-uuid-here' ORDER BY logged_at DESC;

-- Get failed uploads that need retry
-- SELECT * FROM telegram_uploads WHERE status = 'failed' AND retry_count < max_retries;

-- Get storage usage summary
-- SELECT * FROM storage_usage;

-- Get pending notifications
-- SELECT * FROM notification_queue WHERE status = 'pending' ORDER BY priority, created_at;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify all tables were created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('telegram_uploads', 'processing_logs', 'storage_registry', 'notification_queue', 'user_preferences')
ORDER BY table_name;

-- Verify indexes
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename LIKE 'telegram_%' OR tablename LIKE 'processing_%' OR tablename = 'storage_registry' OR tablename = 'notification_queue'
ORDER BY tablename, indexname;

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- 1. This schema provides complete audit trail for all document processing
-- 2. Storage registry allows multi-cloud storage with backup/archive tiers
-- 3. Notification queue enables async user notifications
-- 4. Processing logs track every step for debugging
-- 5. User preferences allow customization per user
-- 6. Views provide quick access to common queries
-- 7. Functions simplify common operations
-- 8. RLS policies should be adjusted based on your security requirements
--
-- ============================================================================
