# 🐑 Claude Shepherd Agent - Setup Guide

AI-powered guardian for your ASEAGI repository. Monitors code, reviews PRs, answers questions, and tracks how data impacts your legal case.

---

## 🎯 What Does the Shepherd Do?

The Claude Shepherd Agent is your AI assistant that:

1. **📊 Monitors Database**: Tracks telegram_uploads, processing_logs, and all ingestion tables
2. **🔍 Reviews Code**: Analyzes pull requests and code changes using Claude AI
3. **💬 Answers Questions**: Uses RAG (Retrieval Augmented Generation) to answer questions about your codebase
4. **📈 Generates Reports**: Creates customized reports showing how new data impacts case scope
5. **🏗️ Analyzes Architecture**: Reviews entire repository structure and identifies improvements
6. **🎥 Monitors Services**: Integrates with GitHub, n8n, Qdrant, Twelve Labs

---

## 📋 Prerequisites

You need API keys for:

- ✅ **Anthropic Claude** (required for AI features)
- ✅ **GitHub** (required for repository access)
- ✅ **Qdrant** (optional for semantic search)
- ✅ **Supabase** (required for database monitoring)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `anthropic` - Claude AI API
- `qdrant-client` - Vector database for semantic search
- `tiktoken` - Token counting for embeddings
- `PyGithub` - GitHub API access
- `supabase` - Database access

### Step 2: Get API Keys

#### A. Anthropic Claude API Key

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Go to **API Keys** section
4. Click **Create Key**
5. Copy your key (looks like: `sk-ant-api03-...`)

#### B. GitHub Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click **Generate new token (classic)**
3. Select scopes:
   - `repo` (Full control of private repositories)
   - `read:org` (Read org data)
4. Click **Generate token**
5. Copy your token immediately (you won't see it again!)

#### C. Qdrant API Key (Optional)

**For Qdrant Cloud:**
1. Go to: https://cloud.qdrant.io
2. Create account and cluster
3. Go to **Access** tab
4. Copy your **API Key** and **URL**

**For Local Qdrant:**
```bash
docker run -p 6333:6333 qdrant/qdrant
```
No API key needed for local installation.

#### D. Supabase Keys (Already Have)

You should already have these from previous setup.

### Step 3: Configure Environment Variables

#### Option A: Environment Variables (Recommended)

Add to your `.bashrc`, `.zshrc`, or `.env` file:

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'
export GITHUB_TOKEN='ghp_your-token-here'
export GITHUB_REPO='dondada876/ASEAGI'

# Qdrant (Cloud)
export QDRANT_URL='https://your-cluster.qdrant.io'
export QDRANT_API_KEY='your-qdrant-key'

# Qdrant (Local)
export QDRANT_URL='localhost'
export QDRANT_PORT='6333'

# Supabase (for database monitoring)
export SUPABASE_URL='https://jvjlhxodmbkodzmggwpu.supabase.co'
export SUPABASE_KEY='your-service-role-key'
```

#### Option B: Streamlit Secrets

Create or update `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-api03-your-key-here"
GITHUB_TOKEN = "ghp_your-token-here"
GITHUB_REPO = "dondada876/ASEAGI"
QDRANT_URL = "https://your-cluster.qdrant.io"
QDRANT_API_KEY = "your-qdrant-key"
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your-service-role-key"
```

### Step 4: Test the Setup

```bash
python claude_shepherd_agent.py
```

You should see:
```
🐑 Claude Shepherd Agent
==================================================

Commands:
1. Index repository
2. Review PR
3. Answer question
4. Analyze architecture
5. Generate documentation
6. Exit
```

---

## 🔧 Usage Guide

### 1. Index Your Repository (First Time Setup)

This creates a searchable vector database of your entire codebase:

```bash
# Run CLI
python claude_shepherd_agent.py

# Choose option 1: Index repository
Choice: 1
```

This will:
- Scan all files in your GitHub repository
- Create embeddings for semantic search
- Store in Qdrant vector database
- Take 5-10 minutes for typical repository

**Output:**
```
🔍 Indexing repository: dondada876/ASEAGI
📦 Creating collection 'aseagi_codebase'
📄 Found 47 files
✅ Indexed 47 files
🎉 Indexing complete! Total files indexed: 47
```

### 2. Review Pull Requests

Get AI-powered code reviews:

```bash
# Choose option 2: Review PR
Choice: 2
PR number: 5

# Wait for analysis...
```

**Output includes:**
- Alignment check with project architecture
- Code quality assessment
- Security review
- Integration point analysis
- Specific suggestions
- Merge recommendation

### 3. Ask Questions About Your Code

Use RAG to query your codebase:

```bash
# Choose option 3: Answer question
Choice: 3
Your question: How does document upload work in the Telegram bot?
```

**Example questions:**
- "How does document upload work in the Telegram bot?"
- "What tables store police reports?"
- "How is the n8n workflow triggered?"
- "Where are files stored after processing?"
- "What's the difference between telegram_uploads and legal_documents?"

### 4. Analyze Repository Architecture

Get comprehensive architectural analysis:

```bash
# Choose option 4: Analyze architecture
Choice: 4
```

**Output includes:**
- System architecture overview
- Component relationships
- Data flow diagrams
- Potential improvements
- Missing components

### 5. Generate Documentation

Create docs for any file:

```bash
# Choose option 5: Generate documentation
Choice: 5
File path: telegram_document_bot.py
```

**Output includes:**
- Purpose and overview
- Key functions/classes
- Dependencies
- Usage examples
- Integration points

---

## 🤖 Telegram Integration

Add shepherd commands to your Telegram bot:

### Add to telegram_monitoring_bot.py:

```python
from claude_shepherd_agent import shepherd_telegram_command

# Add command handlers
application.add_handler(CommandHandler("shepherd_review_pr", shepherd_telegram_command))
application.add_handler(CommandHandler("shepherd_ask", shepherd_telegram_command))
application.add_handler(CommandHandler("shepherd_analyze", shepherd_telegram_command))
```

### Usage in Telegram:

```
/shepherd_review_pr 5
→ Reviews pull request #5

/shepherd_ask How does document upload work?
→ Answers using repository knowledge

/shepherd_analyze
→ Provides architecture analysis
```

---

## 📊 Database Monitoring & Reports

The shepherd agent monitors your Supabase tables and generates impact reports.

### Monitor Data Ingestion

```python
from claude_shepherd_agent import ClaudeShepherdAgent

agent = ClaudeShepherdAgent()

# Monitor telegram uploads
report = await agent.monitor_ingestion_tables()
print(report)
```

### Generate Case Impact Reports

When new documents are uploaded, the shepherd analyzes how they impact your legal case:

```python
# Generate report for recent uploads
impact_report = await agent.generate_case_impact_report(
    time_period='24h'  # Last 24 hours
)
```

**Report includes:**
- New documents uploaded
- Document types and relevance
- Case timeline updates
- Evidence strength changes
- Recommendations for next steps

---

## 🛠️ Advanced Configuration

### Embedding Model Selection

By default, the agent uses a placeholder embedding. For production, update `_get_embedding()`:

#### Option A: OpenAI Embeddings (Recommended)

```python
import openai

async def _get_embedding(self, text: str) -> List[float]:
    """Get embedding using OpenAI"""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
```

Add to requirements.txt:
```
openai>=1.10.0
```

Set environment variable:
```bash
export OPENAI_API_KEY='sk-proj-...'
```

#### Option B: Local Embeddings (Free)

```python
from sentence_transformers import SentenceTransformer

class RepositoryIndexer:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding using local model"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()
```

Add to requirements.txt:
```
sentence-transformers>=2.2.0
```

**Note:** Update vector size in Qdrant to 384 for all-MiniLM-L6-v2:
```python
vectors_config=VectorParams(size=384, distance=Distance.COSINE)
```

### Custom Knowledge Base

Extend the agent's knowledge by editing `_build_knowledge_base()`:

```python
def _build_knowledge_base(self) -> str:
    kb = f"""# ASEAGI Repository Knowledge Base

    ## Custom Section
    - Your specific project details
    - Custom architecture patterns
    - Domain-specific knowledge

    {super()._build_knowledge_base()}  # Include defaults
    """
    return kb
```

---

## 🔍 Troubleshooting

### Error: "Claude API not configured"

**Problem:** Missing or invalid Anthropic API key

**Solution:**
1. Verify you have an API key from https://console.anthropic.com/
2. Check environment variable is set: `echo $ANTHROPIC_API_KEY`
3. Ensure key starts with `sk-ant-api03-`
4. Restart your terminal after setting environment variables

### Error: "GitHub not configured"

**Problem:** Missing or invalid GitHub token

**Solution:**
1. Generate token at https://github.com/settings/tokens
2. Ensure `repo` scope is selected
3. Set environment variable: `export GITHUB_TOKEN='ghp_...'`
4. Verify repository name is correct: `dondada876/ASEAGI`

### Error: "Collection not found"

**Problem:** Qdrant collection hasn't been created yet

**Solution:**
1. Run the indexing process first (option 1 in CLI)
2. Or manually create collection:
```python
from claude_shepherd_agent import qdrant_client, COLLECTION_NAME
from qdrant_client.models import Distance, VectorParams

qdrant_client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)
```

### Error: "Rate limit exceeded"

**Problem:** Too many API requests to Claude

**Solution:**
1. Wait a few minutes before retrying
2. Reduce batch sizes when indexing
3. Add rate limiting:
```python
import asyncio
await asyncio.sleep(1)  # Wait between requests
```

### Qdrant Connection Issues

**Local Qdrant:**
```bash
# Check if Qdrant is running
curl http://localhost:6333

# Start Qdrant
docker run -p 6333:6333 qdrant/qdrant
```

**Cloud Qdrant:**
1. Verify URL is correct (include https://)
2. Check API key is valid
3. Ensure cluster is active

---

## 📈 Performance Tips

1. **Index Incrementally**: Only index changed files instead of entire repo
2. **Cache Responses**: Store Claude responses to avoid redundant API calls
3. **Batch Operations**: Process multiple files in single API call when possible
4. **Use Local Embeddings**: Save costs with sentence-transformers
5. **Limit Context Size**: Truncate large files to essential parts

---

## 💰 Cost Estimates

### Claude API Costs

- **Sonnet 4**: ~$3 per million input tokens, $15 per million output tokens
- **Typical PR review**: $0.10-$0.50 depending on PR size
- **Repository indexing**: $5-$20 for full repository (one-time)
- **Q&A queries**: $0.01-$0.05 per question

### Qdrant Costs

- **Local**: Free (self-hosted)
- **Cloud Free Tier**: 1GB storage, 100k vectors
- **Cloud Paid**: Starting at $25/month for 8GB

### Estimated Monthly Costs

**Light usage** (10 PRs, 50 questions, monthly re-index):
- Claude API: ~$15-25/month
- Qdrant Cloud: Free tier sufficient
- **Total: $15-25/month**

**Heavy usage** (50 PRs, 200 questions, weekly re-index):
- Claude API: ~$60-100/month
- Qdrant Cloud: $25/month
- **Total: $85-125/month**

---

## 🔐 Security Best Practices

1. **Never commit API keys** to Git
2. **Use environment variables** or secrets management
3. **Rotate credentials** every 90 days
4. **Limit GitHub token scope** to only what's needed
5. **Use service role keys** for Supabase (not anon keys)
6. **Enable rate limiting** to prevent API abuse
7. **Monitor API usage** regularly
8. **Use RLS policies** in Supabase for data access control

---

## 🧪 Testing

### Test Individual Components

```python
import asyncio
from claude_shepherd_agent import ClaudeShepherdAgent

async def test():
    agent = ClaudeShepherdAgent()

    # Test question answering
    answer = await agent.answer_question("What tables store documents?")
    print(f"Answer: {answer}")

    # Test architecture analysis
    analysis = await agent.analyze_architecture()
    print(f"Files: {analysis['total_files']}")

asyncio.run(test())
```

### Test with Sample PR

Create a test pull request and review it:

```bash
# In your repository
git checkout -b test-shepherd
echo "# Test file" > test.md
git add test.md
git commit -m "Test shepherd review"
git push origin test-shepherd

# Create PR on GitHub
# Then review with shepherd
python claude_shepherd_agent.py
# Choose option 2, enter PR number
```

---

## 📚 Additional Resources

- **Anthropic Claude Docs**: https://docs.anthropic.com/
- **Qdrant Documentation**: https://qdrant.tech/documentation/
- **GitHub API Guide**: https://docs.github.com/en/rest
- **RAG Pattern Guide**: https://python.langchain.com/docs/use_cases/question_answering/

---

## 🆘 Getting Help

If you're stuck:

1. **Check logs** - The agent prints detailed error messages
2. **Verify API keys** - Most issues are credential-related
3. **Test components individually** - Isolate the problem
4. **Review this guide** - Common issues covered above
5. **Check API status pages**:
   - Claude: https://status.anthropic.com/
   - GitHub: https://www.githubstatus.com/
   - Qdrant: https://status.qdrant.tech/

---

## ✅ Setup Checklist

Before using in production:

- [ ] All API keys obtained and configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Environment variables set and verified
- [ ] Repository indexed in Qdrant
- [ ] Test PR review completed successfully
- [ ] Test Q&A working
- [ ] Supabase connection verified
- [ ] Cost monitoring set up
- [ ] Security best practices followed
- [ ] Telegram integration (if needed)
- [ ] Documentation generated for key files

---

## 🎉 You're Ready!

Your Claude Shepherd Agent is now configured and ready to:

✅ Monitor your repository 24/7
✅ Review every pull request with AI
✅ Answer questions about your codebase
✅ Generate case impact reports
✅ Track data ingestion and processing
✅ Provide architectural guidance

**Next Steps:**
1. Index your repository (first time)
2. Test with a PR review
3. Ask some questions to verify Q&A works
4. Integrate with Telegram bot (optional)
5. Set up automated monitoring

**Happy Shepherding! 🐑**
