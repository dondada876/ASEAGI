# Vector Search Integration Guide
**Complete Setup for Document Repository with Qdrant, pgvector, and Pinecone**

---

## 🎯 Overview

This guide will help you set up advanced vector search capabilities for your PROJ344 document repository. You'll be able to perform semantic search (find documents by meaning, not just keywords) across all your RTF files and documentation.

**What You Get:**
- ✅ Extract and index 8 RTF files + all markdown docs
- ✅ **Option 1**: Supabase + pgvector (hybrid keyword + semantic search)
- ✅ **Option 2**: Qdrant/Pinecone (pure vector search, high performance)
- ✅ Natural language queries ("find documents about legal scoring")
- ✅ Similar document discovery
- ✅ Q&A system with RAG (Retrieval-Augmented Generation)

---

## 📋 Quick Start (5 Steps)

### Step 1: Extract Documents

```bash
cd /home/user/ASEAGI

# Install dependencies
pip install striprtf python-docx PyPDF2

# Run extractor
python3 document_extractor.py
```

**Expected Output:**
```
Found 46 documents to process

[1/46] Processing: PROJ344-Multi-dimensional-legal-document-scoring-S10.rtf
   [OK] Success - 125 words, 753 chars
   Method: striprtf

[2/46] Processing: PROJ344-Multi-dimensional-legal-document-scoring-system-s11.rtf
   [OK] Success - 6017 words, 63131 chars
   Method: striprtf

...

[OK] Index created: PROJ344_document_repository/document_index.json
   Total: 46
   Success: 46
   Failed: 0
```

### Step 2: Choose Your Option

**Option 1 (Recommended): Supabase + pgvector**
- Hybrid search (keyword + semantic)
- SQL queries
- Already integrated with your system
- Free tier sufficient

**Option 2 (Advanced): Qdrant/Pinecone**
- Pure vector search
- High performance
- Self-hosted (Qdrant) or managed (Pinecone)

### Step 3: Set Environment Variables

```bash
# For Supabase (Option 1)
export SUPABASE_URL='https://jvjlhxodmbkodzmggwpu.supabase.co'
export SUPABASE_KEY='your-supabase-key'
export OPENAI_API_KEY='sk-your-openai-key'  # For embeddings

# For Qdrant (Option 2)
export QDRANT_URL='http://localhost:6333'  # Or your Qdrant Cloud URL
export OPENAI_API_KEY='sk-your-openai-key'

# For Pinecone (Option 2)
export PINECONE_API_KEY='your-pinecone-key'
export OPENAI_API_KEY='sk-your-openai-key'
```

### Step 4: Run Setup Script

**Option 1: Supabase**
```bash
python3 document_repository_to_supabase.py
# Choose option 5 (do all)
```

**Option 2: Qdrant**
```bash
# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Upload documents
python3 document_repository_to_vectors.py
# Choose option 1 (Upload to Qdrant)
```

### Step 5: Test Search

```python
# Option 1: Supabase
python3 document_repository_to_supabase.py
# Choose option 4 (Test search)

# Option 2: Qdrant
python3 document_repository_to_vectors.py
# Choose option 4 (Search Qdrant)
```

---

## 📊 Option 1: Supabase + pgvector (Recommended)

### Features
- **Full-Text Search**: Fast keyword search using PostgreSQL
- **Vector Search**: Semantic similarity using pgvector
- **Hybrid Search**: Combine both for best results
- **SQL Queries**: Complex filtering and analysis
- **Cost**: Free tier sufficient for 46 documents

### Setup Steps

#### 1. Run Extractor (if not done)
```bash
python3 document_extractor.py
```

#### 2. Get SQL Schema
```bash
python3 document_repository_to_supabase.py
# Choose option 1
# Copy the SQL output
```

#### 3. Create Tables in Supabase
1. Go to: https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu/sql
2. Paste the SQL schema
3. Click "Run"

**Tables Created:**
- `document_repository` - Full-text search enabled
- `document_embeddings` - Vector embeddings (pgvector)

#### 4. Upload Documents
```bash
python3 document_repository_to_supabase.py
# Choose option 2 (Upload documents)
```

**Expected Output:**
```
[1/46] [OK] PROJ344-Multi-dimensional-legal-document-scoring-S10.rtf (ID: 1, 125 words)
[2/46] [OK] PROJ344-Multi-dimensional-legal-document-scoring-system-s11.rtf (ID: 2, 6017 words)
...

UPLOAD COMPLETE
Uploaded: 46
Skipped: 0
Failed: 0
```

#### 5. Generate Embeddings (Optional)
```bash
python3 document_repository_to_supabase.py
# Choose option 3 (Generate embeddings)
```

**Cost**: ~$0.01 for all 46 documents (one-time)

#### 6. Test Search
```bash
python3 document_repository_to_supabase.py
# Choose option 4 (Test search)
# Enter query: "scoring methodology"
```

### Usage Examples

#### Keyword Search (SQL)
```sql
-- Search for "scoring methodology"
SELECT * FROM search_documents('scoring methodology', 10);

-- Results ranked by relevance
-- Fast and precise
```

#### Semantic Search (Python)
```python
import openai
from supabase import create_client

# Generate embedding
query = "how to evaluate legal documents"
embedding = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=query
)['data'][0]['embedding']

# Search by meaning
supabase = create_client(url, key)
results = supabase.rpc('match_documents', {
    'query_embedding': embedding,
    'match_count': 5
}).execute()

# Returns PROJ344 scoring docs even though
# they don't contain those exact words!
```

#### Hybrid Search (Best Results)
```python
# 1. Keyword search (fast, precise)
keyword_results = supabase.rpc('search_documents', {
    'search_query': 'PROJ344 scoring',
    'limit_count': 20
}).execute()

# 2. Semantic search (smart, flexible)
vector_results = supabase.rpc('match_documents', {
    'query_embedding': embedding,
    'match_threshold': 0.7,
    'match_count': 20
}).execute()

# 3. Merge results
# Combine and re-rank based on your criteria
```

---

## 🚀 Option 2: Qdrant / Pinecone

### Features
- **Pure Vector Search**: Optimized for semantic similarity
- **High Performance**: HNSW algorithm for fast search
- **Scalable**: Handles millions of vectors
- **Document Chunking**: Automatic text splitting for accuracy
- **Self-Hosted or Managed**: Choose Qdrant (free) or Pinecone (paid)

### Option 2A: Qdrant (Self-Hosted, Free)

#### 1. Start Qdrant
```bash
# Using Docker (recommended)
docker run -p 6333:6333 qdrant/qdrant

# Or download binary from:
# https://github.com/qdrant/qdrant/releases
```

#### 2. Install Dependencies
```bash
pip install qdrant-client openai
```

#### 3. Upload Documents
```bash
export OPENAI_API_KEY='sk-your-key'
python3 document_repository_to_vectors.py
# Choose option 1 (Upload to Qdrant)
```

**What Happens:**
- Documents are chunked (1000 words with 200 overlap)
- OpenAI generates embeddings for each chunk
- Chunks uploaded to Qdrant
- ~51 chunks total for 46 documents

**Cost**: ~$0.01 for embeddings (one-time)

#### 4. Search
```bash
python3 document_repository_to_vectors.py
# Choose option 4 (Search Qdrant)
# Enter query: "legal document evaluation methods"
```

#### 5. Advanced Search (Python)
```python
from qdrant_client import QdrantClient
import openai

# Connect
qdrant = QdrantClient(url="http://localhost:6333")

# Generate query embedding
query = "PROJ344 legal scoring system"
embedding = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=query
)['data'][0]['embedding']

# Search
results = qdrant.search(
    collection_name="proj344_documents",
    query_vector=embedding,
    limit=5
)

# Filter by metadata
results_rtf_only = qdrant.search(
    collection_name="proj344_documents",
    query_vector=embedding,
    query_filter={
        "must": [
            {"key": "file_type", "match": {"value": "rtf"}}
        ]
    },
    limit=5
)
```

### Option 2B: Pinecone (Managed, Paid)

#### 1. Create Account
Sign up at https://www.pinecone.io/

#### 2. Install Dependencies
```bash
pip install pinecone-client openai
```

#### 3. Set API Keys
```bash
export PINECONE_API_KEY='your-key'
export OPENAI_API_KEY='sk-your-key'
```

#### 4. Upload Documents
```bash
python3 document_repository_to_vectors.py
# Choose option 2 (Upload to Pinecone)
```

#### 5. Search
```bash
python3 document_repository_to_vectors.py
# Choose option 5 (Search Pinecone)
# Enter query: "perjury detection methodology"
```

---

## 💰 Cost Comparison

| Option | Setup Cost | Monthly Cost | Embedding Cost | Total (First Month) |
|--------|------------|--------------|----------------|---------------------|
| **Supabase** | Free | $0-25 | ~$0.01 | $0-25 |
| **Qdrant (Self-Host)** | Free | $0-5 (VPS) | ~$0.01 | $0-5 |
| **Qdrant Cloud** | Free | $0-25 | ~$0.01 | $0-25 |
| **Pinecone** | Free tier | $0-70 | ~$0.01 | $0-70 |

**Recommendation**: Start with Supabase (Option 1) - free tier sufficient, already integrated.

---

## 🔧 Advanced Usage

### Integration with PROJ344 Dashboard

```python
import streamlit as st
from supabase import create_client
import openai

# Add to your dashboard
st.title("📚 Document Semantic Search")

query = st.text_input("Search documents:")

if query:
    # Generate embedding
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=query
    )['data'][0]['embedding']

    # Search
    supabase = create_client(url, key)
    results = supabase.rpc('match_documents', {
        'query_embedding': embedding,
        'match_count': 10
    }).execute()

    # Display results
    for doc in results.data:
        st.markdown(f"### {doc['file_name']}")
        st.write(f"**Similarity**: {doc['similarity']:.0%}")
        st.write(doc['chunk_text'][:300])
        st.markdown("---")
```

### RAG (Retrieval-Augmented Generation) Q&A System

```python
from anthropic import Anthropic

def ask_question_about_docs(question: str) -> str:
    """Answer questions using your document repository"""

    # 1. Find relevant documents
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=question
    )['data'][0]['embedding']

    results = supabase.rpc('match_documents', {
        'query_embedding': embedding,
        'match_count': 3  # Top 3 most relevant
    }).execute()

    # 2. Build context from results
    context = "\n\n".join([
        f"Document: {doc['file_name']}\n{doc['chunk_text']}"
        for doc in results.data
    ])

    # 3. Ask Claude with context
    client = Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Based on these documents:

{context}

Answer this question: {question}

Cite which documents you're referencing."""
        }]
    )

    return response.content[0].text

# Example usage
answer = ask_question_about_docs(
    "How does PROJ344 scoring methodology work?"
)
print(answer)
# Claude answers using YOUR actual documentation!
```

### Similar Document Discovery

```python
def find_similar_documents(file_name: str, limit: int = 5):
    """Find documents similar to a given document"""

    # Get the document's content
    doc = supabase.table('document_repository')\
        .select('content')\
        .eq('file_name', file_name)\
        .single()\
        .execute()

    # Generate embedding
    embedding = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=doc.data['content'][:30000]
    )['data'][0]['embedding']

    # Find similar
    similar = supabase.rpc('match_documents', {
        'query_embedding': embedding,
        'match_count': limit + 1  # +1 to exclude self
    }).execute()

    # Filter out the original document
    return [
        d for d in similar.data
        if d['file_name'] != file_name
    ][:limit]

# Example
similar_docs = find_similar_documents(
    "PROJ344-Multi-dimensional-legal-document-scoring-system-s3.rtf"
)
for doc in similar_docs:
    print(f"- {doc['file_name']} (similarity: {doc['similarity']:.0%})")
```

---

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY='sk-your-key-here'
# Get key from: https://platform.openai.com/api-keys
```

### Issue: "Repository not found"
```bash
# Make sure you've run the extractor first
python3 document_extractor.py
# Creates PROJ344_document_repository/
```

### Issue: "Supabase RPC function not found"
1. Go to Supabase SQL Editor
2. Run the SQL schema from option 1
3. Verify tables and functions created

### Issue: "Qdrant connection failed"
```bash
# Make sure Qdrant is running
docker run -p 6333:6333 qdrant/qdrant

# Check connection
curl http://localhost:6333/collections
```

### Issue: "Embeddings too expensive"
- Process only important documents (filter by file type)
- Use larger chunks (reduce chunk count)
- Use Supabase full-text search instead (no embeddings needed)

---

## ✅ Quick Reference

### Extract Documents
```bash
python3 document_extractor.py
```

### Upload to Supabase
```bash
python3 document_repository_to_supabase.py
# Option 5 (do all)
```

### Upload to Qdrant
```bash
docker run -p 6333:6333 qdrant/qdrant
python3 document_repository_to_vectors.py
# Option 1
```

### Search Supabase (Keyword)
```sql
SELECT * FROM search_documents('scoring methodology', 10);
```

### Search Supabase (Semantic)
```python
results = supabase.rpc('match_documents', {
    'query_embedding': embedding,
    'match_count': 5
}).execute()
```

### Search Qdrant
```python
results = qdrant.search(
    collection_name="proj344_documents",
    query_vector=embedding,
    limit=5
)
```

---

## 📚 What's Created

### After Extraction:
```
PROJ344_document_repository/
├── raw_text/               # 46 .txt files
│   ├── PROJ344-...-S10.txt
│   ├── PROJ344-...-s3.txt
│   └── ...
├── metadata/               # 46 .json files (metadata)
├── json/                   # 46 .json files (full documents)
└── document_index.json     # Master index
```

### After Upload (Supabase):
```
Supabase Tables:
- document_repository (46 rows)
- document_embeddings (~51 chunks with embeddings)

Functions:
- search_documents() - keyword search
- match_documents() - semantic search
```

### After Upload (Qdrant):
```
Qdrant Collection: proj344_documents
- ~51 vectors (document chunks)
- Metadata included
- Ready for semantic search
```

---

## 🎯 Next Steps

1. **Extract Documents**: Run `document_extractor.py`
2. **Choose Option**: Supabase (recommended) or Qdrant/Pinecone
3. **Upload Documents**: Run respective integration script
4. **Test Search**: Try keyword and semantic searches
5. **Integrate**: Add to PROJ344 dashboards
6. **Build RAG**: Create Q&A system with your docs

---

**For Ashe. For Justice. For All Children. 🛡️**

This system ensures that critical legal documentation is searchable not just by exact keywords, but by meaning and context - making evidence discovery faster and more comprehensive.

---

**Created**: 2025-11-06
**Files**: 3 Python scripts + this guide
**Documents**: 8 RTF files + 38 markdown files = 46 total
**Status**: ✅ Ready to use
