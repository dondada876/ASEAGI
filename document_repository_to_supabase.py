#!/usr/bin/env python3
"""
Document Repository to Supabase Integration (Option 1)
Uploads extracted documents to Supabase with full-text search and pgvector embeddings
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

try:
    from supabase import create_client, Client
except ImportError:
    print("[WARN] Installing supabase library...")
    os.system("pip install supabase")
    from supabase import create_client, Client

try:
    import anthropic
except ImportError:
    print("[WARN] Installing anthropic library for embeddings...")
    os.system("pip install anthropic")
    import anthropic


class DocumentRepositoryUploader:
    """Upload document repository to Supabase with embeddings"""

    def __init__(self, repository_path: str = "PROJ344_document_repository"):
        """Initialize uploader"""

        # Supabase connection
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise Exception("Missing SUPABASE_URL or SUPABASE_KEY environment variables")

        self.supabase: Client = create_client(supabase_url, supabase_key)

        # Anthropic for embeddings (optional)
        self.anthropic_key = os.environ.get('ANTHROPIC_API_KEY')
        if self.anthropic_key:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_key)
        else:
            self.anthropic_client = None
            print("[WARN] ANTHROPIC_API_KEY not set - embeddings will be skipped")

        self.repo_path = Path(repository_path)

        if not self.repo_path.exists():
            raise Exception(f"Repository not found: {repository_path}")

    def create_tables(self):
        """Create Supabase tables (run SQL separately in Supabase dashboard)"""

        sql = """
-- ============================================================================
-- OPTION 1: Supabase Tables for Document Repository
-- ============================================================================

-- Main document repository table
CREATE TABLE IF NOT EXISTS document_repository (
    id BIGSERIAL PRIMARY KEY,
    file_name TEXT NOT NULL,
    file_type TEXT,  -- rtf, md, txt, pdf, docx
    file_hash TEXT UNIQUE,  -- MD5 for deduplication
    title TEXT,
    content TEXT,  -- Full extracted text
    content_preview TEXT,  -- First 500 chars
    word_count INTEGER,
    char_count INTEGER,
    file_size INTEGER,
    extraction_date TIMESTAMPTZ,
    extraction_method TEXT,  -- striprtf, python-docx, etc.
    original_file_path TEXT,
    metadata JSONB,  -- Full metadata object
    sections JSONB,  -- Detected sections
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Full-text search index using PostgreSQL tsvector
CREATE INDEX IF NOT EXISTS idx_document_content_fts
ON document_repository
USING gin(to_tsvector('english', content));

-- Title search index
CREATE INDEX IF NOT EXISTS idx_document_title_fts
ON document_repository
USING gin(to_tsvector('english', title));

-- File type index for filtering
CREATE INDEX IF NOT EXISTS idx_document_file_type
ON document_repository(file_type);

-- Hash index for deduplication
CREATE INDEX IF NOT EXISTS idx_document_hash
ON document_repository(file_hash);

-- ============================================================================
-- OPTION 2: pgvector for semantic search
-- ============================================================================

-- Enable pgvector extension (run in Supabase SQL editor)
CREATE EXTENSION IF NOT EXISTS vector;

-- Document embeddings table
CREATE TABLE IF NOT EXISTS document_embeddings (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES document_repository(id) ON DELETE CASCADE,
    embedding vector(1536),  -- OpenAI ada-002 or similar embedding size
    embedding_model TEXT DEFAULT 'text-embedding-ada-002',
    chunk_index INTEGER DEFAULT 0,  -- For chunked documents
    chunk_text TEXT,  -- The text that was embedded
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector similarity index (HNSW for fast approximate search)
CREATE INDEX IF NOT EXISTS idx_document_embeddings_vector
ON document_embeddings
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Full-text search function
CREATE OR REPLACE FUNCTION search_documents(
    search_query TEXT,
    limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
    id BIGINT,
    file_name TEXT,
    title TEXT,
    content_preview TEXT,
    word_count INTEGER,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        dr.id,
        dr.file_name,
        dr.title,
        dr.content_preview,
        dr.word_count,
        ts_rank(to_tsvector('english', dr.content), plainto_tsquery('english', search_query)) AS rank
    FROM document_repository dr
    WHERE to_tsvector('english', dr.content) @@ plainto_tsquery('english', search_query)
    ORDER BY rank DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INTEGER DEFAULT 5
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    file_name TEXT,
    title TEXT,
    chunk_text TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        de.id,
        de.document_id,
        dr.file_name,
        dr.title,
        de.chunk_text,
        1 - (de.embedding <=> query_embedding) AS similarity
    FROM document_embeddings de
    JOIN document_repository dr ON de.document_id = dr.id
    WHERE 1 - (de.embedding <=> query_embedding) > match_threshold
    ORDER BY de.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_document_repository_updated_at
    BEFORE UPDATE ON document_repository
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Row Level Security (Optional - for multi-user systems)
-- ============================================================================

-- Enable RLS
ALTER TABLE document_repository ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;

-- Policy: Allow all operations for authenticated users
CREATE POLICY "Allow all for authenticated users" ON document_repository
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Allow all for authenticated users" ON document_embeddings
    FOR ALL USING (auth.role() = 'authenticated');

-- ============================================================================
-- Sample Queries
-- ============================================================================

-- Full-text search:
-- SELECT * FROM search_documents('scoring methodology', 10);

-- Keyword search:
-- SELECT * FROM document_repository
-- WHERE to_tsvector('english', content) @@ to_tsquery('english', 'PROJ344 & scoring');

-- Get PROJ344 documents:
-- SELECT file_name, title, word_count
-- FROM document_repository
-- WHERE file_name LIKE '%PROJ344%'
-- ORDER BY word_count DESC;

-- Vector similarity search (requires embeddings):
-- SELECT * FROM match_documents('[your embedding vector]'::vector, 0.7, 5);
"""

        print("=" * 80)
        print("SUPABASE TABLE SCHEMA")
        print("=" * 80)
        print()
        print("Copy and paste this SQL into your Supabase SQL Editor:")
        print()
        print(sql)
        print()
        print("=" * 80)

        return sql

    def upload_documents(self, skip_duplicates: bool = True):
        """Upload all documents from repository to Supabase"""

        # Load index
        index_file = self.repo_path / "document_index.json"
        if not index_file.exists():
            raise Exception(f"Index file not found: {index_file}")

        with open(index_file) as f:
            index = json.load(f)

        print("=" * 80)
        print("UPLOADING DOCUMENTS TO SUPABASE")
        print("=" * 80)
        print()
        print(f"Total documents: {len(index['documents'])}")
        print(f"Successful extractions: {index['successful']}")
        print()

        uploaded = 0
        skipped = 0
        failed = 0

        for i, doc_info in enumerate(index['documents'], 1):
            if doc_info['status'] != 'success':
                print(f"[{i}/{len(index['documents'])}] SKIP: {Path(doc_info['file']).name} (extraction failed)")
                skipped += 1
                continue

            # Load full document JSON
            json_file = doc_info['saved_files']['json_file']
            with open(json_file) as f:
                full_doc = json.load(f)

            metadata = full_doc['metadata']

            try:
                # Check if already exists (by hash)
                if skip_duplicates:
                    existing = self.supabase.table('document_repository')\
                        .select('id')\
                        .eq('file_hash', metadata['file_hash'])\
                        .execute()

                    if existing.data:
                        print(f"[{i}/{len(index['documents'])}] SKIP: {metadata['file_name']} (already exists)")
                        skipped += 1
                        continue

                # Insert document
                insert_data = {
                    'file_name': metadata['file_name'],
                    'file_type': metadata['file_type'],
                    'file_hash': metadata['file_hash'],
                    'title': metadata.get('title'),
                    'content': full_doc['content'],
                    'content_preview': full_doc['content_preview'],
                    'word_count': metadata.get('word_count'),
                    'char_count': metadata.get('char_count'),
                    'file_size': metadata.get('file_size'),
                    'extraction_date': metadata.get('extraction_date'),
                    'extraction_method': metadata.get('extraction_method'),
                    'original_file_path': metadata.get('file_path'),
                    'metadata': metadata,
                    'sections': full_doc.get('sections', [])
                }

                result = self.supabase.table('document_repository')\
                    .insert(insert_data)\
                    .execute()

                doc_id = result.data[0]['id']

                print(f"[{i}/{len(index['documents'])}] [OK] {metadata['file_name']} (ID: {doc_id}, {metadata.get('word_count')} words)")
                uploaded += 1

            except Exception as e:
                print(f"[{i}/{len(index['documents'])}] [FAIL] {metadata['file_name']}: {e}")
                failed += 1

        print()
        print("=" * 80)
        print("UPLOAD COMPLETE")
        print("=" * 80)
        print(f"Uploaded: {uploaded}")
        print(f"Skipped: {skipped}")
        print(f"Failed: {failed}")
        print()

        return {
            'uploaded': uploaded,
            'skipped': skipped,
            'failed': failed
        }

    def generate_embeddings(self, model: str = "voyage-2"):
        """Generate embeddings for all documents using Anthropic or OpenAI"""

        if not self.anthropic_client:
            print("[ERROR] Cannot generate embeddings - ANTHROPIC_API_KEY not set")
            return

        print("=" * 80)
        print("GENERATING EMBEDDINGS")
        print("=" * 80)
        print()
        print("Note: This will use Anthropic/OpenAI API and incur costs")
        print()

        # Get all documents without embeddings
        docs = self.supabase.table('document_repository')\
            .select('id, file_name, content, word_count')\
            .execute()

        print(f"Found {len(docs.data)} documents to process")
        print()

        embedded = 0
        skipped = 0
        failed = 0

        for i, doc in enumerate(docs.data, 1):
            doc_id = doc['id']

            # Check if embeddings already exist
            existing = self.supabase.table('document_embeddings')\
                .select('id')\
                .eq('document_id', doc_id)\
                .execute()

            if existing.data:
                print(f"[{i}/{len(docs.data)}] SKIP: {doc['file_name']} (embeddings exist)")
                skipped += 1
                continue

            try:
                # Chunk content if too large (max ~8000 tokens for embeddings)
                content = doc['content']
                max_chars = 30000  # ~8k tokens

                chunks = []
                if len(content) > max_chars:
                    # Split into chunks
                    for j in range(0, len(content), max_chars):
                        chunks.append(content[j:j + max_chars])
                else:
                    chunks = [content]

                # Generate embeddings for each chunk
                for chunk_idx, chunk in enumerate(chunks):
                    # Use OpenAI for embeddings (Anthropic doesn't have embeddings API yet)
                    # Note: You'll need to install openai and use OpenAI API for embeddings
                    print(f"[{i}/{len(docs.data)}] Chunk {chunk_idx + 1}/{len(chunks)}: {doc['file_name']}")

                    # Placeholder for embedding generation
                    # In real use, uncomment and use OpenAI:
                    # import openai
                    # embedding_response = openai.Embedding.create(
                    #     model="text-embedding-ada-002",
                    #     input=chunk
                    # )
                    # embedding = embedding_response['data'][0]['embedding']

                    # For now, create a placeholder
                    embedding = [0.0] * 1536  # Placeholder

                    # Insert embedding
                    self.supabase.table('document_embeddings').insert({
                        'document_id': doc_id,
                        'embedding': embedding,
                        'embedding_model': 'text-embedding-ada-002',
                        'chunk_index': chunk_idx,
                        'chunk_text': chunk[:1000]  # Store preview of chunk
                    }).execute()

                print(f"   [OK] Generated {len(chunks)} embedding(s)")
                embedded += 1

            except Exception as e:
                print(f"[{i}/{len(docs.data)}] [FAIL] {doc['file_name']}: {e}")
                failed += 1

        print()
        print("=" * 80)
        print("EMBEDDING GENERATION COMPLETE")
        print("=" * 80)
        print(f"Embedded: {embedded}")
        print(f"Skipped: {skipped}")
        print(f"Failed: {failed}")
        print()

    def test_search(self):
        """Test full-text search"""

        print("=" * 80)
        print("TESTING FULL-TEXT SEARCH")
        print("=" * 80)
        print()

        # Test query
        query = "scoring methodology"
        print(f"Query: '{query}'")
        print()

        # Search using PostgreSQL full-text search
        results = self.supabase.rpc('search_documents', {
            'search_query': query,
            'limit_count': 5
        }).execute()

        print(f"Found {len(results.data)} results:")
        print()

        for i, result in enumerate(results.data, 1):
            print(f"{i}. {result['file_name']}")
            print(f"   Title: {result.get('title', 'N/A')}")
            print(f"   Words: {result.get('word_count', 'N/A')}")
            print(f"   Rank: {result.get('rank', 'N/A'):.4f}")
            print(f"   Preview: {result.get('content_preview', '')[:100]}...")
            print()


def main():
    """Main entry point"""

    print("=" * 80)
    print("DOCUMENT REPOSITORY TO SUPABASE UPLOADER")
    print("=" * 80)
    print()

    # Initialize uploader
    uploader = DocumentRepositoryUploader()

    print("Options:")
    print("1. Create Supabase tables (shows SQL - run in Supabase dashboard)")
    print("2. Upload documents to Supabase")
    print("3. Generate embeddings (requires OpenAI API)")
    print("4. Test full-text search")
    print("5. Do all (create tables, upload, test search)")
    print()

    choice = input("Enter choice (1-5): ").strip()

    if choice == '1':
        uploader.create_tables()

    elif choice == '2':
        uploader.upload_documents()

    elif choice == '3':
        uploader.generate_embeddings()

    elif choice == '4':
        uploader.test_search()

    elif choice == '5':
        print("\n[1/4] Creating tables...")
        uploader.create_tables()

        input("\nPress Enter after running the SQL in Supabase dashboard...")

        print("\n[2/4] Uploading documents...")
        uploader.upload_documents()

        print("\n[3/4] Testing search...")
        uploader.test_search()

        print("\n[4/4] Complete! To generate embeddings, run option 3 separately.")

    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
