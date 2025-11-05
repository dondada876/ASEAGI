-- ============================================================================
-- PROJ344 Error Logs Table Schema
-- ============================================================================
-- Description: Stores uploaded error log files with analysis metadata
-- Created: 2025-11-05
-- Usage: Run this SQL in your Supabase SQL Editor to create the error_logs table
-- ============================================================================

-- Create the error_logs table
CREATE TABLE IF NOT EXISTS public.error_logs (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,

    -- File metadata
    filename TEXT NOT NULL,
    file_size BIGINT NOT NULL DEFAULT 0,
    file_type TEXT DEFAULT 'text/plain',

    -- Log content
    content TEXT NOT NULL,

    -- Analysis metadata
    error_count INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    total_lines INTEGER DEFAULT 0,
    analysis_summary TEXT,

    -- Timestamps
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Optional: User tracking (if you have authentication)
    -- uploaded_by UUID REFERENCES auth.users(id),

    -- Optional: Additional metadata
    tags TEXT[],
    notes TEXT
);

-- ============================================================================
-- INDEXES for better query performance
-- ============================================================================

-- Index on uploaded_at for sorting recent logs
CREATE INDEX IF NOT EXISTS idx_error_logs_uploaded_at
    ON public.error_logs(uploaded_at DESC);

-- Index on filename for searching
CREATE INDEX IF NOT EXISTS idx_error_logs_filename
    ON public.error_logs(filename);

-- Index on error_count for filtering
CREATE INDEX IF NOT EXISTS idx_error_logs_error_count
    ON public.error_logs(error_count);

-- Full-text search index on content (for searching within logs)
CREATE INDEX IF NOT EXISTS idx_error_logs_content_search
    ON public.error_logs USING gin(to_tsvector('english', content));

-- ============================================================================
-- TRIGGERS for automatic timestamp updates
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at
DROP TRIGGER IF EXISTS set_updated_at ON public.error_logs;
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON public.error_logs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) - Optional but recommended
-- ============================================================================

-- Enable RLS on the table
ALTER TABLE public.error_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users
-- Adjust these policies based on your security requirements
CREATE POLICY "Allow all for authenticated users"
    ON public.error_logs
    FOR ALL
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- Policy: Allow read access for anonymous users (optional - remove if not needed)
CREATE POLICY "Allow read for anon users"
    ON public.error_logs
    FOR SELECT
    TO anon
    USING (true);

-- If you want to restrict to specific users, use this pattern instead:
-- CREATE POLICY "Users can view own logs"
--     ON public.error_logs
--     FOR SELECT
--     TO authenticated
--     USING (auth.uid() = uploaded_by);

-- ============================================================================
-- HELPER VIEWS (Optional)
-- ============================================================================

-- View: Recent error logs summary (last 30 days)
CREATE OR REPLACE VIEW public.error_logs_recent AS
SELECT
    id,
    filename,
    file_size,
    error_count,
    warning_count,
    total_lines,
    uploaded_at,
    ROUND(file_size::NUMERIC / 1024, 2) as file_size_kb,
    CASE
        WHEN error_count > 100 THEN 'HIGH'
        WHEN error_count > 10 THEN 'MEDIUM'
        ELSE 'LOW'
    END as severity
FROM public.error_logs
WHERE uploaded_at > NOW() - INTERVAL '30 days'
ORDER BY uploaded_at DESC;

-- View: Error statistics summary
CREATE OR REPLACE VIEW public.error_logs_stats AS
SELECT
    COUNT(*) as total_logs,
    SUM(error_count) as total_errors,
    SUM(warning_count) as total_warnings,
    SUM(file_size) as total_bytes,
    ROUND(AVG(error_count), 2) as avg_errors_per_log,
    ROUND(AVG(warning_count), 2) as avg_warnings_per_log,
    MAX(uploaded_at) as last_upload,
    MIN(uploaded_at) as first_upload
FROM public.error_logs;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Get all logs uploaded in the last 7 days
-- SELECT * FROM public.error_logs
-- WHERE uploaded_at > NOW() - INTERVAL '7 days'
-- ORDER BY uploaded_at DESC;

-- Find logs with high error counts
-- SELECT filename, error_count, warning_count, uploaded_at
-- FROM public.error_logs
-- WHERE error_count > 50
-- ORDER BY error_count DESC;

-- Search for specific text in log content
-- SELECT id, filename, uploaded_at
-- FROM public.error_logs
-- WHERE content ILIKE '%Exception%' OR content ILIKE '%Error%'
-- ORDER BY uploaded_at DESC;

-- Full-text search in log content
-- SELECT id, filename, uploaded_at, error_count
-- FROM public.error_logs
-- WHERE to_tsvector('english', content) @@ to_tsquery('english', 'database & connection')
-- ORDER BY uploaded_at DESC;

-- Get summary statistics
-- SELECT * FROM public.error_logs_stats;

-- ============================================================================
-- MAINTENANCE QUERIES
-- ============================================================================

-- Delete logs older than 90 days (cleanup)
-- DELETE FROM public.error_logs WHERE uploaded_at < NOW() - INTERVAL '90 days';

-- Find largest log files
-- SELECT filename, ROUND(file_size::NUMERIC / (1024*1024), 2) as size_mb, uploaded_at
-- FROM public.error_logs
-- ORDER BY file_size DESC
-- LIMIT 10;

-- ============================================================================
-- GRANTS (Optional - adjust based on your needs)
-- ============================================================================

-- Grant access to authenticated users
GRANT ALL ON public.error_logs TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE public.error_logs_id_seq TO authenticated;

-- Grant read-only access to anonymous users (optional)
GRANT SELECT ON public.error_logs TO anon;

-- Grant access to views
GRANT SELECT ON public.error_logs_recent TO authenticated;
GRANT SELECT ON public.error_logs_stats TO authenticated;
GRANT SELECT ON public.error_logs_recent TO anon;
GRANT SELECT ON public.error_logs_stats TO anon;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Verify table was created successfully
-- SELECT table_name, table_type
-- FROM information_schema.tables
-- WHERE table_schema = 'public'
-- AND table_name = 'error_logs';

-- Verify indexes were created
-- SELECT indexname, indexdef
-- FROM pg_indexes
-- WHERE tablename = 'error_logs';

-- Verify RLS is enabled
-- SELECT tablename, rowsecurity
-- FROM pg_tables
-- WHERE tablename = 'error_logs';

-- ============================================================================
-- NOTES
-- ============================================================================
--
-- 1. This schema supports large log files (content is TEXT, unlimited size)
-- 2. Full-text search is enabled via GIN index for fast content searching
-- 3. RLS policies are set to allow authenticated users full access
-- 4. Adjust RLS policies based on your security requirements
-- 5. The uploaded_by column is commented out - uncomment if you have user auth
-- 6. Consider adding a cleanup job to delete old logs after X days
-- 7. File size is stored in bytes, convert to KB/MB when displaying
--
-- ============================================================================
