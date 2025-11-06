# Vector Search API Configuration Guide
**Complete secrets.toml setup for document repository and vector search**

---

## 🔑 Required API Endpoints

### 1. Supabase (Required for Option 1)
**What it's for:** Database storage, full-text search, and pgvector embeddings

- **Endpoint:** `SUPABASE_URL`
- **Authentication:** `SUPABASE_KEY` (anon/public key)
- **Get it from:** [supabase.com/dashboard](https://supabase.com/dashboard) → Project Settings → API
- **Already configured:** Yes (used by your existing dashboards)

### 2. OpenAI API (Required for embeddings)
**What it's for:** Generating vector embeddings for semantic search

- **Endpoint:** `OPENAI_API_KEY`
- **Model used:** `text-embedding-ada-002` (1536 dimensions)
- **Cost:** ~$0.0001 per 1,000 tokens (~$0.01 for all 19 documents)
- **Get it from:** [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

### 3. Qdrant (Optional - for Option 2 self-hosted)
**What it's for:** High-performance vector database (self-hosted)

- **Endpoint:** `QDRANT_URL`
- **Default:** `http://localhost:6333` (Docker)
- **Cloud option:** `https://your-cluster.qdrant.io`
- **Get it from:** [qdrant.tech](https://qdrant.tech) or run locally with Docker

### 4. Pinecone (Optional - for Option 2 managed)
**What it's for:** Managed vector database service

- **Endpoint:** `PINECONE_API_KEY`
- **Environment:** `PINECONE_ENVIRONMENT` (e.g., "us-west1-gcp")
- **Get it from:** [app.pinecone.io](https://app.pinecone.io) → API Keys
- **Free tier:** 100K vectors

---

## 📁 secrets.toml Configuration

### Location
```
.streamlit/secrets.toml
```

### Full Template

```toml
# ============================================================================
# VECTOR SEARCH SECRETS CONFIGURATION
# File: .streamlit/secrets.toml
# ============================================================================

# ---------------------------------------------------------------------------
# SUPABASE (Required for Option 1: Hybrid Search)
# ---------------------------------------------------------------------------
# Your existing Supabase credentials
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c"

# ---------------------------------------------------------------------------
# OPENAI (Required for embeddings)
# ---------------------------------------------------------------------------
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-proj-..."  # Replace with your actual key

# Optional: Set organization if you have one
# OPENAI_ORG_ID = "org-..."

# ---------------------------------------------------------------------------
# QDRANT (Optional - for Option 2: Self-hosted Vector Search)
# ---------------------------------------------------------------------------
# Local Docker instance (default)
QDRANT_URL = "http://localhost:6333"

# OR Qdrant Cloud
# QDRANT_URL = "https://your-cluster.qdrant.io"
# QDRANT_API_KEY = "your-qdrant-cloud-key"

# ---------------------------------------------------------------------------
# PINECONE (Optional - for Option 2: Managed Vector Search)
# ---------------------------------------------------------------------------
# Get your API key from: https://app.pinecone.io
# PINECONE_API_KEY = "your-pinecone-key"
# PINECONE_ENVIRONMENT = "us-west1-gcp"  # Or your region

# ---------------------------------------------------------------------------
# DOCUMENT REPOSITORY SETTINGS
# ---------------------------------------------------------------------------
# Path to your extracted documents (relative to project root)
DOCUMENT_REPO_PATH = "PROJ344_document_repository"

# Vector search settings
EMBEDDING_MODEL = "text-embedding-ada-002"
EMBEDDING_DIMENSIONS = 1536
CHUNK_SIZE = 1000  # Words per chunk
CHUNK_OVERLAP = 200  # Word overlap between chunks

# Search settings
DEFAULT_SEARCH_LIMIT = 5
SIMILARITY_THRESHOLD = 0.7  # Minimum similarity score (0-1)
```

---

## 🚀 Setup Instructions

### Step 1: Create secrets.toml file

```bash
cd /home/user/ASEAGI

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Create secrets.toml
nano .streamlit/secrets.toml
```

### Step 2: Add your API keys

Copy the template above and replace placeholders:

1. **Supabase** - Already configured (keep existing values)
2. **OpenAI** - Replace `sk-proj-...` with your actual key
3. **Qdrant/Pinecone** - Uncomment and add if using Option 2

### Step 3: Secure the file

```bash
# Add to .gitignore (already done)
echo ".streamlit/secrets.toml" >> .gitignore

# Set proper permissions
chmod 600 .streamlit/secrets.toml
```

### Step 4: Test configuration

```python
# test_secrets.py
import streamlit as st

# Test loading secrets
try:
    print("✅ SUPABASE_URL:", st.secrets["SUPABASE_URL"])
    print("✅ SUPABASE_KEY:", st.secrets["SUPABASE_KEY"][:20] + "...")
    print("✅ OPENAI_API_KEY:", st.secrets.get("OPENAI_API_KEY", "NOT SET"))
except Exception as e:
    print("❌ Error:", e)
```

Run: `streamlit run test_secrets.py`

---

## 🔄 Alternative: Environment Variables

If you prefer environment variables over secrets.toml:

```bash
# Add to ~/.bashrc or ~/.zshrc
export SUPABASE_URL="https://jvjlhxodmbkodzmggwpu.supabase.co"
export SUPABASE_KEY="your-supabase-key"
export OPENAI_API_KEY="sk-proj-..."

# For Qdrant
export QDRANT_URL="http://localhost:6333"

# For Pinecone
export PINECONE_API_KEY="your-pinecone-key"
export PINECONE_ENVIRONMENT="us-west1-gcp"

# Reload shell
source ~/.bashrc
```

---

## 📊 Usage in Code

All scripts automatically check for secrets in this order:

1. **Streamlit secrets** (`st.secrets`)
2. **Environment variables** (`os.environ`)
3. **Hardcoded defaults** (for Supabase only)

### Example from document_repository_to_supabase.py:

```python
# Supabase connection
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except (KeyError, FileNotFoundError):
    url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    key = os.environ.get('SUPABASE_KEY', 'default-key')

# OpenAI connection
openai_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get('OPENAI_API_KEY')
if not openai_key:
    print("⚠️ OPENAI_API_KEY not set - embeddings will be skipped")
```

---

## 💰 Cost Estimates

### OpenAI Embeddings (text-embedding-ada-002)
- **Rate:** $0.0001 per 1,000 tokens
- **Your 19 documents (~21,738 words):** ~$0.01 one-time cost
- **Re-embedding:** Only needed when documents change

### Qdrant (Self-hosted)
- **Cost:** Free (runs on your server)
- **Requirements:** ~1GB RAM, 2GB disk

### Qdrant Cloud
- **Free tier:** 1GB cluster
- **Paid:** Starting at $25/month

### Pinecone
- **Free tier:** 1 index, 100K vectors
- **Paid:** Starting at $70/month

### Supabase
- **Free tier:** 500MB database, 2GB bandwidth
- **Your usage:** Well within free tier
- **Paid:** Starting at $25/month

---

## 🔒 Security Best Practices

### DO:
✅ Use secrets.toml for local development
✅ Use Streamlit Cloud secrets for production
✅ Add secrets.toml to .gitignore
✅ Rotate API keys regularly
✅ Use read-only keys when possible

### DON'T:
❌ Commit secrets.toml to git
❌ Share API keys in Slack/email
❌ Use service keys in client-side code
❌ Hardcode secrets in Python files

---

## 📝 Streamlit Cloud Deployment

When deploying to Streamlit Cloud:

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Select your app
3. Click "Settings" → "Secrets"
4. Paste your secrets.toml content (minus comments)
5. Save

**Example for Streamlit Cloud:**

```toml
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGci..."
OPENAI_API_KEY = "sk-proj-..."
```

---

## 🧪 Testing Each API Connection

### Test Supabase:
```bash
python3 -c "
from supabase import create_client
import os
client = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_KEY']
)
result = client.table('file_metadata').select('file_id').limit(1).execute()
print('✅ Supabase connected:', len(result.data), 'records')
"
```

### Test OpenAI:
```bash
python3 -c "
import openai
import os
openai.api_key = os.environ['OPENAI_API_KEY']
result = openai.Embedding.create(
    model='text-embedding-ada-002',
    input='test'
)
print('✅ OpenAI connected:', len(result['data'][0]['embedding']), 'dimensions')
"
```

### Test Qdrant:
```bash
curl http://localhost:6333/collections
# Should return: {"result":{"collections":[]},"status":"ok","time":0.0}
```

### Test Pinecone:
```bash
python3 -c "
import pinecone
import os
pinecone.init(
    api_key=os.environ['PINECONE_API_KEY'],
    environment=os.environ['PINECONE_ENVIRONMENT']
)
print('✅ Pinecone connected:', pinecone.list_indexes())
"
```

---

## 🆘 Troubleshooting

### "OPENAI_API_KEY not set"
**Solution:** Add to secrets.toml or environment:
```bash
export OPENAI_API_KEY="sk-proj-..."
```

### "Supabase connection failed"
**Check:**
1. URL format: `https://xxx.supabase.co` (no trailing slash)
2. Key is the "anon/public" key (not service role key)
3. Project is not paused

### "Qdrant connection refused"
**Check:**
1. Docker is running: `docker ps | grep qdrant`
2. Port 6333 is accessible: `curl http://localhost:6333`
3. URL has correct protocol: `http://` (not `https://`)

### "Pinecone index not found"
**Solution:** Create index first:
```python
import pinecone
pinecone.create_index(
    name="proj344-documents",
    dimension=1536,
    metric="cosine"
)
```

---

## 📚 Next Steps

1. **Create secrets.toml** using the template above
2. **Get OpenAI API key** from [platform.openai.com](https://platform.openai.com/api-keys)
3. **Choose your option:**
   - Option 1: Run `python3 document_repository_to_supabase.py`
   - Option 2: Run `python3 document_repository_to_vectors.py`
4. **Test search** with your documents

---

## 🔗 Quick Links

- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [OpenAI Pricing](https://openai.com/pricing)
- [Supabase Dashboard](https://supabase.com/dashboard)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Pinecone Console](https://app.pinecone.io)
- [Streamlit Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

**For Ashe. For Justice. For All Children.** 🛡️
