-- ============================================================================
-- MASTER DOCUMENT REGISTRY SCHEMA
-- Purpose: Track all documents across multiple sources with deduplication
-- Sources: Mac Mini, Laptop, Google Drive
-- ============================================================================

-- Master registry for all document sources
CREATE TABLE IF NOT EXISTS master_document_registry (
    id BIGSERIAL PRIMARY KEY,

    -- ========================================================================
    -- DEDUPLICATION KEY
    -- ========================================================================
    file_hash TEXT UNIQUE NOT NULL,  -- MD5 hash - primary deduplication key

    -- ========================================================================
    -- FILE METADATA
    -- ========================================================================
    file_name TEXT NOT NULL,
    file_type TEXT,  -- rtf, doc, docx, pdf, txt, md, mp4, mp3, etc.
    file_size BIGINT,
    file_extension TEXT,

    -- ========================================================================
    -- LOCATION TRACKING (supports multiple locations per file)
    -- ========================================================================
    source_locations JSONB,  -- Array of locations where file exists
    -- Format: [
    --   {"source": "mac_mini", "path": "/path/to/file", "discovered": "2025-11-06T10:00:00"},
    --   {"source": "laptop", "path": "/other/path", "discovered": "2025-11-06T11:00:00"}
    -- ]
    primary_location TEXT,  -- mac_mini | laptop | gdrive
    is_cloud_backed_up BOOLEAN DEFAULT FALSE,  -- True if in Google Drive

    -- ========================================================================
    -- PROCESSING STATUS
    -- ========================================================================
    processing_status TEXT DEFAULT 'pending',
    -- Values: pending | processing | complete | failed | skipped

    processed_date TIMESTAMPTZ,
    extraction_success BOOLEAN,
    extraction_error TEXT,  -- Error message if extraction failed

    -- ========================================================================
    -- CONTENT METADATA (populated after extraction)
    -- ========================================================================
    word_count INTEGER,
    char_count INTEGER,
    page_count INTEGER,
    has_images BOOLEAN,
    language TEXT DEFAULT 'en',

    -- ========================================================================
    -- LINKS TO OTHER TABLES (populated after processing)
    -- ========================================================================
    document_id BIGINT,  -- References document_repository(id)
    embedding_id BIGINT,  -- References document_embeddings(id)
    legal_doc_id BIGINT,  -- References legal_documents(id) for PROJ344
    media_analysis_id BIGINT,  -- References media_analysis(id) for video/audio

    -- ========================================================================
    -- TIMESTAMPS
    -- ========================================================================
    first_discovered TIMESTAMPTZ DEFAULT NOW(),
    last_seen TIMESTAMPTZ DEFAULT NOW(),
    last_modified TIMESTAMPTZ,  -- File modification time
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- ========================================================================
    -- CATEGORIZATION & TAGS
    -- ========================================================================
    categories TEXT[],  -- e.g., ['legal', 'court_filing', 'evidence']
    tags TEXT[],        -- e.g., ['custody', 'ashe', 'alameda_county']
    case_relevance INTEGER,  -- 0-999 score (same as legal_documents)
    is_critical BOOLEAN DEFAULT FALSE,  -- Smoking gun / critical evidence

    -- ========================================================================
    -- DOCUMENT CLASSIFICATION (populated by AI)
    -- ========================================================================
    document_class TEXT,  -- TEXT, TRNS, CPSR, MEDR, FORN, CRPT, etc.
    document_subtype TEXT,
    parties_mentioned TEXT[],  -- People/agencies mentioned
    date_references DATE[],  -- Dates mentioned in document

    -- ========================================================================
    -- SEARCH & NOTES
    -- ========================================================================
    content_preview TEXT,  -- First 500 chars of content
    notes TEXT,
    user_flags TEXT[],  -- Custom flags: ['needs_review', 'urgent', etc.]

    -- ========================================================================
    -- CONSTRAINTS
    -- ========================================================================
    CONSTRAINT unique_file_hash UNIQUE (file_hash)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Fast duplicate detection
CREATE INDEX IF NOT EXISTS idx_master_registry_hash
ON master_document_registry(file_hash);

-- Query by status
CREATE INDEX IF NOT EXISTS idx_master_registry_status
ON master_document_registry(processing_status);

-- Query by location
CREATE INDEX IF NOT EXISTS idx_master_registry_location
ON master_document_registry(primary_location);

-- Full-text search on file names
CREATE INDEX IF NOT EXISTS idx_master_registry_filename
ON master_document_registry USING gin(to_tsvector('english', file_name));

-- Query by case relevance
CREATE INDEX IF NOT EXISTS idx_master_registry_relevance
ON master_document_registry(case_relevance DESC)
WHERE case_relevance IS NOT NULL;

-- Query by critical flag
CREATE INDEX IF NOT EXISTS idx_master_registry_critical
ON master_document_registry(is_critical)
WHERE is_critical = TRUE;

-- Query by file type
CREATE INDEX IF NOT EXISTS idx_master_registry_type
ON master_document_registry(file_type);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View: Documents found in multiple locations (duplicates across sources)
CREATE OR REPLACE VIEW document_duplicates AS
SELECT
    file_hash,
    file_name,
    file_type,
    file_size,
    jsonb_array_length(source_locations) as location_count,
    source_locations,
    primary_location
FROM master_document_registry
WHERE jsonb_array_length(source_locations) > 1
ORDER BY location_count DESC, file_size DESC;

-- View: Processing queue (pending documents)
CREATE OR REPLACE VIEW documents_to_process AS
SELECT
    id,
    file_hash,
    file_name,
    file_type,
    file_size,
    primary_location,
    source_locations->0->>'path' as file_path,
    first_discovered
FROM master_document_registry
WHERE processing_status = 'pending'
ORDER BY first_discovered ASC;

-- View: Recently added documents
CREATE OR REPLACE VIEW recent_documents AS
SELECT
    id,
    file_name,
    file_type,
    file_size,
    primary_location,
    processing_status,
    first_discovered
FROM master_document_registry
ORDER BY first_discovered DESC
LIMIT 100;

-- View: Critical unprocessed documents
CREATE OR REPLACE VIEW critical_unprocessed AS
SELECT
    id,
    file_name,
    file_type,
    case_relevance,
    primary_location,
    source_locations->0->>'path' as file_path
FROM master_document_registry
WHERE processing_status = 'pending'
  AND (is_critical = TRUE OR case_relevance >= 900)
ORDER BY case_relevance DESC NULLS LAST;

-- View: Documents by source
CREATE OR REPLACE VIEW documents_by_source AS
SELECT
    primary_location as source,
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE processing_status = 'complete') as processed,
    COUNT(*) FILTER (WHERE processing_status = 'pending') as pending,
    COUNT(*) FILTER (WHERE processing_status = 'failed') as failed,
    SUM(file_size) as total_size_bytes,
    ROUND(SUM(file_size)::numeric / 1024 / 1024, 2) as total_size_mb
FROM master_document_registry
GROUP BY primary_location
ORDER BY total_documents DESC;

-- View: Documents by file type
CREATE OR REPLACE VIEW documents_by_type AS
SELECT
    file_type,
    COUNT(*) as count,
    COUNT(*) FILTER (WHERE processing_status = 'complete') as processed,
    COUNT(*) FILTER (WHERE processing_status = 'pending') as pending,
    SUM(file_size) as total_size_bytes,
    ROUND(AVG(file_size)::numeric / 1024, 2) as avg_size_kb
FROM master_document_registry
GROUP BY file_type
ORDER BY count DESC;

-- View: Processing statistics
CREATE OR REPLACE VIEW processing_stats AS
SELECT
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE processing_status = 'pending') as pending,
    COUNT(*) FILTER (WHERE processing_status = 'processing') as processing,
    COUNT(*) FILTER (WHERE processing_status = 'complete') as complete,
    COUNT(*) FILTER (WHERE processing_status = 'failed') as failed,
    COUNT(*) FILTER (WHERE is_cloud_backed_up = TRUE) as cloud_backed_up,
    COUNT(*) FILTER (WHERE is_critical = TRUE) as critical_documents,
    ROUND(AVG(case_relevance), 1) as avg_relevance,
    SUM(file_size) as total_size_bytes,
    ROUND(SUM(file_size)::numeric / 1024 / 1024 / 1024, 2) as total_size_gb
FROM master_document_registry;

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Update updated_at timestamp on changes
CREATE OR REPLACE FUNCTION update_master_registry_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_master_registry_timestamp
    BEFORE UPDATE ON master_document_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_master_registry_timestamp();

-- Function: Add location to existing document
CREATE OR REPLACE FUNCTION add_document_location(
    p_file_hash TEXT,
    p_source TEXT,
    p_path TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_locations JSONB;
BEGIN
    -- Get current locations
    SELECT source_locations INTO v_locations
    FROM master_document_registry
    WHERE file_hash = p_file_hash;

    -- Add new location if not already present
    IF v_locations IS NULL THEN
        v_locations = '[]'::jsonb;
    END IF;

    -- Check if location already exists
    IF NOT EXISTS (
        SELECT 1
        FROM jsonb_array_elements(v_locations) as loc
        WHERE loc->>'source' = p_source AND loc->>'path' = p_path
    ) THEN
        v_locations = v_locations || jsonb_build_object(
            'source', p_source,
            'path', p_path,
            'discovered', NOW()
        );

        UPDATE master_document_registry
        SET
            source_locations = v_locations,
            last_seen = NOW()
        WHERE file_hash = p_file_hash;

        RETURN TRUE;
    END IF;

    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Function: Mark document as cloud backed up
CREATE OR REPLACE FUNCTION mark_cloud_backup(p_file_hash TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE master_document_registry
    SET is_cloud_backed_up = TRUE
    WHERE file_hash = p_file_hash;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

-- Find all documents
-- SELECT * FROM master_document_registry ORDER BY first_discovered DESC;

-- Find duplicates across sources
-- SELECT * FROM document_duplicates;

-- Get processing queue
-- SELECT * FROM documents_to_process LIMIT 10;

-- Check processing stats
-- SELECT * FROM processing_stats;

-- Find documents in Google Drive
-- SELECT * FROM master_document_registry WHERE primary_location = 'gdrive';

-- Find critical unprocessed documents
-- SELECT * FROM critical_unprocessed;

-- Get documents by source
-- SELECT * FROM documents_by_source;

-- Get documents by type
-- SELECT * FROM documents_by_type;

-- ============================================================================
-- NOTES
-- ============================================================================

/*
USAGE:
1. Run this SQL in Supabase SQL Editor
2. Run multi_source_scanner.py on each machine (laptop, Mac Mini)
3. Run google_drive_scanner.py for Google Drive
4. Run consolidate_registries.py to merge all sources
5. Process documents using document_extractor.py
6. Generate embeddings with document_repository_to_supabase.py

DEDUPLICATION:
- file_hash (MD5) is the primary key for deduplication
- Same file in multiple locations = 1 row with multiple source_locations
- Updated file = new file_hash = new row (version tracking)

LOCATION TRACKING:
- source_locations: JSON array of all places file exists
- primary_location: Main/preferred location for processing
- is_cloud_backed_up: TRUE if file is in Google Drive

PROCESSING PIPELINE:
1. pending -> Waiting to be processed
2. processing -> Currently being extracted/analyzed
3. complete -> Successfully processed
4. failed -> Extraction/processing failed
5. skipped -> Intentionally skipped (e.g., duplicate content)

INTEGRATION WITH PROJ344:
- After processing, document_id links to document_repository
- legal_doc_id links to legal_documents (for court docs)
- case_relevance uses same 0-999 scoring as PROJ344
- is_critical flag matches smoking gun detection
*/
