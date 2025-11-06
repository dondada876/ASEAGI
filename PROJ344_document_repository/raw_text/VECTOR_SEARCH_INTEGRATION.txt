# Vector Search Integration Guide

## Overview

Integration tools for uploading your document repository to vector databases for advanced semantic search capabilities.

**Created:** 2025-11-06
**Documents:** 46 files, ~51,000 words from PROJ344 repository
**Embedding Model:** OpenAI text-embedding-ada-002 (1536 dimensions)

---

## Options Available

### Option 1: Supabase with pgvector
- **File:** `document_repository_to_supabase.py`
- **Features:** Full-text search + vector embeddings
- **Best For:** SQL queries, full-text search, PostgreSQL integration
- **Cost:** Supabase free tier + OpenAI embeddings

### Option 2: Qdrant / Pinecone
- **File:** `document_repository_to_vectors.py`
- **Features:** Pure vector search, semantic similarity
- **Best For:** Advanced semantic search, high-performance vector operations
- **Cost:** Qdrant (self-hosted free) or Pinecone (paid)

---

## Option 1: Supabase with pgvector

### Features

✅ **Full-Text Search** - PostgreSQL tsvector/tsquery
✅ **Vector Embeddings** - pgvector extension for semantic search
✅ **SQL Queries** - Complex filtering and joins
✅ **Metadata Storage** - Structured JSON fields
✅ **Hybrid Search** - Combine keyword + semantic search

### Setup

#### 1. Install Dependencies

```bash
pip install supabase openai
```

#### 2. Set Environment Variables

```bash
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-supabase-anon-key'
export OPENAI_API_KEY='sk-your-openai-key'  # Optional, for embeddings
```

#### 3. Create Tables

```bash
cd ASEAGI
python document_repository_to_supabase.py

# Choose option 1 to see SQL schema
# Copy SQL and run in Supabase SQL Editor
```

**Tables Created:**
- `document_repository` - Main document table with full-text search
- `document_embeddings` - Vector embeddings (pgvector)

#### 4. Upload Documents

```bash
python document_repository_to_supabase.py

# Choose option 2 to upload documents
# Or option 5 to do everything
```

### Usage

#### Full-Text Search (Keyword-Based)

```sql
-- Search for "scoring methodology"
SELECT * FROM search_documents('scoring methodology', 10);

-- Manual query with ranking
SELECT
    file_name,
    title,
    word_count,
    ts_rank(to_tsvector('english', content), to_tsquery('english', 'PROJ344 & scoring')) AS rank
FROM document_repository
WHERE to_tsvector('english', content) @@ to_tsquery('english', 'PROJ344 & scoring')
ORDER BY rank DESC
LIMIT 10;
```

#### Semantic Search (Vector-Based)

```python
import openai
from supabase import create_client

# Generate query embedding
query = "legal document scoring methodology"
embedding_response = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=query
)
query_embedding = embedding_response['data'][0]['embedding']

# Search by vector similarity
supabase = create_client(supabase_url, supabase_key)
results = supabase.rpc('match_documents', {
    'query_embedding': query_embedding,
    'match_threshold': 0.7,
    'match_count': 5
}).execute()

for doc in results.data:
    print(f"{doc['file_name']} (similarity: {doc['similarity']:.2f})")
    print(f"  {doc['chunk_text'][:200]}...")
```

#### Hybrid Search (Best of Both)

```python
# 1. Get keyword matches (fast, precise)
keyword_results = supabase.rpc('search_documents', {
    'search_query': 'PROJ344 scoring',
    'limit_count': 20
}).execute()

# 2. Get semantic matches (smart, flexible)
vector_results = supabase.rpc('match_documents', {
    'query_embedding': query_embedding,
    'match_threshold': 0.7,
    'match_count': 20
}).execute()

# 3. Merge and rank
# Use your own ranking algorithm to combine both result sets
```

### Cost Estimation

**Supabase:**
- Free tier: 500 MB database, 2 GB bandwidth/month
- Paid: $25/month for Pro tier (8 GB database, 50 GB bandwidth)

**OpenAI Embeddings:**
- $0.0001 per 1,000 tokens
- 46 documents (~51,000 words = ~68,000 tokens)
- Cost to embed all: ~$0.007 (less than 1 cent)
- Chunked (1000 words/chunk): ~51 chunks = ~$0.005

**Total:** ~$0-25/month depending on Supabase tier

---

## Option 2: Qdrant / Pinecone

### Features

✅ **Pure Vector Search** - Optimized for semantic similarity
✅ **High Performance** - HNSW algorithm for fast approximate search
✅ **Scalable** - Handles millions of vectors
✅ **Document Chunking** - Automatic text splitting for better search
✅ **Flexible** - Choose Qdrant (self-hosted) or Pinecone (managed)

### Setup

#### Option 2A: Qdrant (Self-Hosted, Free)

**1. Install Qdrant**

```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or install locally (Rust binary)
# Download from: https://github.com/qdrant/qdrant/releases
```

**2. Install Python Libraries**

```bash
pip install qdrant-client openai
```

**3. Set Environment Variables**

```bash
export QDRANT_URL='http://localhost:6333'  # Or your Qdrant cloud URL
export QDRANT_API_KEY='your-api-key'  # If using Qdrant Cloud
export OPENAI_API_KEY='sk-your-openai-key'
```

**4. Upload Documents**

```bash
cd ASEAGI
python document_repository_to_vectors.py

# Choose option 1 (Upload to Qdrant)
```

#### Option 2B: Pinecone (Managed, Paid)

**1. Create Pinecone Account**

Sign up at https://www.pinecone.io/

**2. Install Python Libraries**

```bash
pip install pinecone-client openai
```

**3. Set Environment Variables**

```bash
export PINECONE_API_KEY='your-pinecone-key'
export PINECONE_ENVIRONMENT='us-west1-gcp'  # Or your region
export OPENAI_API_KEY='sk-your-openai-key'
```

**4. Upload Documents**

```bash
cd ASEAGI
python document_repository_to_vectors.py

# Choose option 2 (Upload to Pinecone)
# Or option 3 (Upload to both)
```

### Usage

#### Search Qdrant

```python
from qdrant_client import QdrantClient
import openai

# Initialize
qdrant = QdrantClient(url="http://localhost:6333")

# Generate query embedding
query = "PROJ344 legal scoring system"
embedding_response = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=query
)
query_vector = embedding_response['data'][0]['embedding']

# Search
results = qdrant.search(
    collection_name="proj344_documents",
    query_vector=query_vector,
    limit=5
)

for result in results:
    print(f"{result.payload['file_name']} (score: {result.score:.4f})")
    print(f"  {result.payload['chunk_text'][:200]}...")
```

#### Search Pinecone

```python
import pinecone
import openai

# Initialize
pinecone.init(api_key=pinecone_api_key, environment='us-west1-gcp')
index = pinecone.Index('proj344-documents')

# Generate query embedding
query = "PROJ344 legal scoring system"
embedding_response = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=query
)
query_vector = embedding_response['data'][0]['embedding']

# Search
results = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True
)

for match in results['matches']:
    meta = match['metadata']
    print(f"{meta['file_name']} (score: {match['score']:.4f})")
    print(f"  {meta['chunk_text'][:200]}...")
```

#### Filter by Metadata

```python
# Qdrant - filter by file type
results = qdrant.search(
    collection_name="proj344_documents",
    query_vector=query_vector,
    query_filter={
        "must": [
            {
                "key": "file_type",
                "match": {"value": "rtf"}
            }
        ]
    },
    limit=5
)

# Pinecone - filter by file type
results = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True,
    filter={"file_type": {"$eq": "rtf"}}
)
```

### Cost Estimation

**Qdrant (Self-Hosted):**
- Free forever (run on your own server)
- Server costs depend on hosting (Docker: $0, VPS: $5-20/month)

**Qdrant Cloud:**
- Free tier: 1 GB storage
- Paid: $25/month for 2 GB

**Pinecone:**
- Free tier: 1 index, 100K vectors, 1 pod
- Starter: $70/month for 1 pod (100K-2M vectors)
- Standard: $140/month for 2 pods

**OpenAI Embeddings:**
- Same as Option 1: ~$0.005-0.01 total

**Total:**
- Qdrant self-hosted: $0-20/month
- Qdrant Cloud: $0-25/month
- Pinecone: $0-70/month

---

## Comparison: Option 1 vs Option 2

| Feature | Supabase (Option 1) | Qdrant (Option 2A) | Pinecone (Option 2B) |
|---------|---------------------|--------------------|--------------------|
| **Full-Text Search** | ✅ Built-in | ❌ No | ❌ No |
| **Vector Search** | ✅ pgvector | ✅ Native | ✅ Native |
| **SQL Queries** | ✅ PostgreSQL | ❌ No | ❌ No |
| **Metadata Filtering** | ✅ SQL WHERE | ✅ JSON filters | ✅ JSON filters |
| **Hybrid Search** | ✅ Easy | ❌ Need separate system | ❌ Need separate system |
| **Self-Hosted** | ❌ Cloud only | ✅ Yes (Docker) | ❌ Cloud only |
| **Free Tier** | ✅ 500 MB | ✅ Unlimited (self-host) | ✅ 100K vectors |
| **Performance** | ⚡ Good | ⚡⚡ Excellent | ⚡⚡ Excellent |
| **Scalability** | ⚡ Good | ⚡⚡ Excellent | ⚡⚡ Excellent |
| **Ease of Setup** | ⚡⚡ Easy | ⚡ Medium | ⚡⚡ Easy |
| **Cost (Small)** | $0-25/mo | $0-5/mo | $0-70/mo |
| **Best For** | Hybrid search, SQL | Self-hosted, OSS | Managed, enterprise |

---

## Recommended Strategy

### For Your Use Case (PROJ344 Documents):

#### **Immediate: Option 1 (Supabase)**

**Reasons:**
- You're already using Supabase
- Supports both keyword + semantic search
- SQL queries for complex filtering
- Free tier sufficient for 46 documents
- Easy integration with existing dashboards

**Usage:**
```bash
cd ASEAGI
python document_repository_to_supabase.py
# Choose option 5 (do all)
```

#### **Future: Option 2 (Qdrant Self-Hosted)**

**When to add:**
- When you have 10,000+ documents (better performance)
- When you need pure semantic search
- When you want full control (self-hosted)

**Usage:**
```bash
# Run Qdrant in Docker
docker run -p 6333:6333 qdrant/qdrant

# Upload documents
python document_repository_to_vectors.py
# Choose option 1 (Upload to Qdrant)
```

---

## Integration with Existing Systems

### With PROJ344 Dashboards

```python
import streamlit as st
from supabase import create_client
import openai

# Semantic search widget
st.title("PROJ344 Document Search")

query = st.text_input("Search documents (semantic):")

if query:
    # Generate embedding
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=query
    )['data'][0]['embedding']

    # Search Supabase
    supabase = create_client(supabase_url, supabase_key)
    results = supabase.rpc('match_documents', {
        'query_embedding': embedding,
        'match_threshold': 0.7,
        'match_count': 10
    }).execute()

    # Display results
    for doc in results.data:
        st.markdown(f"### {doc['file_name']}")
        st.write(f"Similarity: {doc['similarity']:.2%}")
        st.write(doc['chunk_text'][:500])
        st.markdown("---")
```

### With Bulk Ingestion

```python
from document_extractor import DocumentExtractor
from document_repository_to_supabase import DocumentRepositoryUploader

# Extract new document
extractor = DocumentExtractor()
doc = extractor.extract_document("path/to/new_file.rtf")

# Generate embedding
embedding = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=doc.content[:30000]  # Truncate if needed
)['data'][0]['embedding']

# Upload to Supabase
uploader = DocumentRepositoryUploader()
uploader.supabase.table('document_repository').insert({
    'file_name': doc.metadata.file_name,
    'content': doc.content,
    # ... other fields
}).execute()

# Upload embedding
uploader.supabase.table('document_embeddings').insert({
    'document_id': inserted_id,
    'embedding': embedding
}).execute()
```

---

## Example Use Cases

### 1. Find Similar Documents

```python
# User uploads a new document
new_doc_embedding = generate_embedding(new_doc_content)

# Find similar existing documents
similar_docs = supabase.rpc('match_documents', {
    'query_embedding': new_doc_embedding,
    'match_count': 10
}).execute()

# Show user: "This is similar to these existing documents..."
```

### 2. Smart Search for Lawyers

```python
# Natural language query
query = "Find all documents about perjury detection and false statements"

# Semantic search (understands intent)
results = search_semantic(query)

# Returns relevant docs even if they don't contain exact keywords
# E.g., finds docs about "misleading testimony", "contradictory statements"
```

### 3. Knowledge Base RAG (Retrieval-Augmented Generation)

```python
# User asks question
question = "How does PROJ344 scoring methodology work?"

# 1. Find relevant documents
docs = search_semantic(question, limit=3)
context = "\n\n".join([d['content'] for d in docs])

# 2. Send to Claude with context
response = anthropic_client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{
        "role": "user",
        "content": f"Based on these documents:\n\n{context}\n\nAnswer: {question}"
    }]
)

# Claude answers using your actual documentation
```

---

## Next Steps

1. **Choose Option 1 or 2** (or both!)

2. **Run Setup Scripts:**
   ```bash
   # Option 1
   python document_repository_to_supabase.py

   # Option 2
   python document_repository_to_vectors.py
   ```

3. **Test Searches:**
   - Try keyword search (Option 1)
   - Try semantic search (both options)
   - Compare results

4. **Integrate with Dashboards:**
   - Add search widgets
   - Show similar documents
   - Build Q&A system

5. **Monitor Costs:**
   - Track OpenAI API usage
   - Monitor database/vector DB size
   - Optimize chunk sizes if needed

---

## Troubleshooting

### Issue: "OPENAI_API_KEY not set"

```bash
export OPENAI_API_KEY='sk-your-key'
# Get key from: https://platform.openai.com/api-keys
```

### Issue: "Supabase RPC function not found"

Run the SQL schema in Supabase SQL Editor first (option 1 in the script)

### Issue: "Qdrant connection failed"

```bash
# Start Qdrant if not running
docker run -p 6333:6333 qdrant/qdrant

# Or check URL
export QDRANT_URL='http://localhost:6333'
```

### Issue: "Embeddings too expensive"

- Chunk documents more aggressively (larger chunks = fewer embeddings)
- Use only Option 1 with full-text search (no embeddings needed)
- Generate embeddings only for important documents

---

## For Ashe. For Justice. For All Children. 🛡️

Advanced search capabilities ensure that critical evidence can be found instantly, even when the exact keywords aren't known.

**Created:** 2025-11-06
**Tools:** Option 1 (Supabase), Option 2 (Qdrant/Pinecone)
**Status:** Ready to use
