-- Quick fix: Add missing columns to legal_documents table
-- This ensures compatibility with the Telegram bot

ALTER TABLE legal_documents
ADD COLUMN IF NOT EXISTS notes TEXT,
ADD COLUMN IF NOT EXISTS user_notes TEXT,
ADD COLUMN IF NOT EXISTS uploaded_via TEXT DEFAULT 'manual';

-- Create index for faster searches
CREATE INDEX IF NOT EXISTS idx_legal_documents_notes ON legal_documents USING gin(to_tsvector('english', notes));

-- Update comment
COMMENT ON COLUMN legal_documents.notes IS 'Internal notes about the document';
COMMENT ON COLUMN legal_documents.user_notes IS 'User-provided notes from upload (e.g., via Telegram)';
COMMENT ON COLUMN legal_documents.uploaded_via IS 'Upload source: telegram, web, api, manual';
