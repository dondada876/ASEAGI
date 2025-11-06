# Configuration Management Guide

**Universal secret management system for PROJ344 across all repositories**

Created: 2025-11-06
Status: Production Ready

---

## Overview

Industry-standard configuration management system that works across:
- ✅ Streamlit apps (secrets.toml)
- ✅ Python scripts (.env files)
- ✅ Multiple repositories (shared secrets directory)
- ✅ Production environments (environment variables)
- ✅ Cloud deployments (AWS, Azure, GCP)

---

## Quick Start (2 Minutes)

### Step 1: Setup Shared Secrets (Already Done!)

```bash
cd ASEAGI
python setup_shared_secrets.py
```

**Created:**
- `~/.proj344_secrets/.env` - Shared secrets directory
- All secrets converted from Streamlit secrets.toml

### Step 2: Use in Any Script

```python
from config_loader import get_secret

# Get secrets (works everywhere!)
supabase_url = get_secret('SUPABASE_URL')
openai_key = get_secret('OPENAI_API_KEY')
anthropic_key = get_secret('ANTHROPIC_API_KEY')
```

### Step 3: Copy to Other Repos

```bash
# Copy config_loader.py to any other repo
cp config_loader.py ../other_repo/

# Use immediately - secrets load automatically!
```

---

## How It Works

### Priority Order (Automatic)

1. **Streamlit secrets** - If running in Streamlit app
2. **Specified .env file** - If you provide a path
3. **Local .env** - In current directory
4. **Shared secrets** - `~/.proj344_secrets/.env`
5. **Environment variables** - System-wide

**No configuration needed!** The loader automatically finds your secrets.

---

## Files Created

### 1. config_loader.py (Universal Loader)

**Purpose:** Load secrets from any source
**Usage:** Works with all scripts, all repos, all environments

```python
from config_loader import ConfigLoader

# Load configuration
config = ConfigLoader()
secrets = config.load()

# Get individual secrets
supabase_url = config.get('SUPABASE_URL')

# Or use convenience function
from config_loader import get_secret
api_key = get_secret('OPENAI_API_KEY')
```

### 2. setup_shared_secrets.py (Setup Script)

**Purpose:** Create shared secrets directory
**Usage:** Run once to setup

```bash
python setup_shared_secrets.py
```

**What it does:**
- Creates `~/.proj344_secrets/` directory
- Converts Streamlit secrets to .env format
- Tests the config loader
- Displays status

### 3. .env.example (Template)

**Purpose:** Template for new repos
**Usage:** Copy to .env and fill in values

```bash
cp .env.example .env
# Edit .env with your actual secrets
```

---

## Usage Examples

### Example 1: Simple Script

```python
# my_script.py
from config_loader import get_secret
from supabase import create_client

# Secrets load automatically!
supabase = create_client(
    get_secret('SUPABASE_URL'),
    get_secret('SUPABASE_KEY')
)

documents = supabase.table('documents').select('*').execute()
print(f"Found {len(documents.data)} documents")
```

### Example 2: Streamlit App

```python
# streamlit_app.py
import streamlit as st
from config_loader import get_secret

# Works with both secrets.toml and shared secrets!
st.title("PROJ344 Dashboard")

supabase_url = get_secret('SUPABASE_URL')
st.write(f"Connected to: {supabase_url}")
```

### Example 3: Check Configuration Status

```python
from config_loader import print_config_status

# Print detailed status
print_config_status()
```

**Output:**
```
================================================================================
CONFIGURATION STATUS
================================================================================
Source: Streamlit secrets.toml
Secrets loaded: 5

Available secrets:
  ANTHROPIC_API_KEY: sk-ant-api...A-Z6RI0AAA
  OPENAI_API_KEY: sk-proj-Tj...3BO3t8-SoA
  SUPABASE_KEY: eyJhbGciOi...x3IbxfPh8c
  SUPABASE_URL: https://jv...upabase.co
  TELEGRAM_BOT_TOKEN: 8564713661...KT8rjBAhKw
================================================================================
```

---

## Cross-Repository Setup

### Scenario: New Repository Needs Secrets

**Option 1: Copy config_loader.py (Recommended)**

```bash
# In new repo
cp ~/path/to/ASEAGI/config_loader.py .

# Use immediately
from config_loader import get_secret
supabase_url = get_secret('SUPABASE_URL')  # Works!
```

**Option 2: Create Local .env**

```bash
# In new repo
cp ~/path/to/ASEAGI/.env.example .env
# Edit .env with your values
```

**Option 3: Use Shared Secrets (Already Setup)**

```bash
# Nothing to do!
# config_loader.py automatically reads from ~/.proj344_secrets/.env
```

---

## Industry Best Practices

### ✅ Security Best Practices

1. **Never commit secrets to git**
   ```bash
   # .gitignore (already configured)
   .env
   .env.local
   .streamlit/secrets.toml
   config.local.yaml
   ```

2. **Use different secrets for dev/staging/production**
   ```python
   # config_loader.py supports environment-specific files
   config = ConfigLoader(env_file='.env.production')
   ```

3. **Rotate secrets regularly**
   - Change API keys every 90 days
   - Immediately rotate if compromised
   - Keep rotation log in secure location

4. **Use secret management services for production**
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Cloud Secret Manager
   - HashiCorp Vault

### ✅ Development Best Practices

1. **Always use .env.example for documentation**
   ```bash
   # Commit .env.example (no real secrets)
   git add .env.example
   git commit -m "Add environment template"
   ```

2. **Use type hints**
   ```python
   def connect_to_db() -> Client:
       url: str = get_secret('SUPABASE_URL')
       key: str = get_secret('SUPABASE_KEY')
       return create_client(url, key)
   ```

3. **Validate secrets on startup**
   ```python
   required_secrets = ['SUPABASE_URL', 'SUPABASE_KEY', 'OPENAI_API_KEY']

   for secret in required_secrets:
       if not get_secret(secret):
           raise ValueError(f"Missing required secret: {secret}")
   ```

---

## Cloud Deployment

### Streamlit Community Cloud

1. Deploy app to Streamlit Cloud
2. Go to app settings → Secrets
3. Paste your secrets:

```toml
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOi..."
OPENAI_API_KEY = "sk-proj-..."
ANTHROPIC_API_KEY = "sk-ant-..."
TELEGRAM_BOT_TOKEN = "8564713661:..."
```

4. App automatically uses these secrets (config_loader.py detects Streamlit)

### AWS Lambda / EC2

```bash
# Set environment variables
export SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
export SUPABASE_KEY=eyJhbGciOi...
export OPENAI_API_KEY=sk-proj-...

# config_loader.py automatically reads from environment
```

### Docker

```dockerfile
# Dockerfile
FROM python:3.11

# Copy code
COPY . /app
WORKDIR /app

# Secrets passed as environment variables at runtime
# docker run -e SUPABASE_URL=... -e SUPABASE_KEY=... myapp
```

### Heroku

```bash
# Set config vars
heroku config:set SUPABASE_URL=https://...
heroku config:set SUPABASE_KEY=eyJhbGciOi...
heroku config:set OPENAI_API_KEY=sk-proj-...
```

---

## Available Secrets

Your system currently has these secrets configured:

| Secret | Description | Usage |
|--------|-------------|-------|
| `SUPABASE_URL` | Supabase project URL | Database connection |
| `SUPABASE_KEY` | Supabase anon key | Database authentication |
| `OPENAI_API_KEY` | OpenAI API key | Embeddings, GPT models |
| `ANTHROPIC_API_KEY` | Anthropic API key | Claude models |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | Bot communication |
| `NEO4J_URI` | Neo4j connection URI | Graph database (optional) |
| `NEO4J_USER` | Neo4j username | Graph database (optional) |
| `NEO4J_PASSWORD` | Neo4j password | Graph database (optional) |
| `QDRANT_URL` | Qdrant API URL | Vector search (optional) |
| `QDRANT_API_KEY` | Qdrant API key | Vector search (optional) |
| `PINECONE_API_KEY` | Pinecone API key | Vector search (optional) |
| `PINECONE_ENVIRONMENT` | Pinecone environment | Vector search (optional) |

---

## Troubleshooting

### Issue: "No secrets found"

**Solution:**
```bash
# Check where config loader is looking
python config_loader.py

# Output shows priority order and what was found
```

### Issue: "Can't find config_loader.py"

**Solution:**
```bash
# Copy from ASEAGI repo
cp ~/path/to/ASEAGI/config_loader.py .
```

### Issue: "Secrets work locally but not in production"

**Solution:**
```python
# Debug in production
from config_loader import print_config_status
print_config_status()

# Shows which source was used and what secrets were found
```

### Issue: "Need different secrets for different environments"

**Solution:**
```python
# Use environment-specific files
import os
env = os.getenv('ENVIRONMENT', 'development')
config = ConfigLoader(env_file=f'.env.{env}')

# Then:
# .env.development
# .env.staging
# .env.production
```

---

## Migration Guide

### From Streamlit Secrets Only

**Before:**
```python
import streamlit as st
supabase_url = st.secrets['SUPABASE_URL']  # Only works in Streamlit
```

**After:**
```python
from config_loader import get_secret
supabase_url = get_secret('SUPABASE_URL')  # Works everywhere!
```

### From Environment Variables Only

**Before:**
```python
import os
supabase_url = os.getenv('SUPABASE_URL')  # Must set in environment
```

**After:**
```python
from config_loader import get_secret
supabase_url = get_secret('SUPABASE_URL')  # Tries multiple sources
```

### From Hardcoded Secrets (Never Do This!)

**Before:**
```python
api_key = "sk-proj-abc123..."  # ❌ NEVER DO THIS
```

**After:**
```python
from config_loader import get_secret
api_key = get_secret('OPENAI_API_KEY')  # ✅ Industry best practice
```

---

## Summary

**What You Have Now:**

✅ **Universal config loader** - Works with Streamlit, scripts, any repo
✅ **Shared secrets directory** - `~/.proj344_secrets/.env`
✅ **Industry best practices** - Follows standard patterns
✅ **Zero breaking changes** - Existing code still works
✅ **Production ready** - Works in cloud deployments

**Setup Time:** 2 minutes
**Maintenance:** Zero - it just works!

**Usage:**
```python
from config_loader import get_secret

# That's it! Use anywhere, anytime
supabase_url = get_secret('SUPABASE_URL')
```

---

## For Ashe. For Justice. For All Children. 🛡️

Secure configuration management ensures your secrets stay safe while being easily accessible across all your PROJ344 systems.

**Created:** 2025-11-06
**Files:** config_loader.py, setup_shared_secrets.py, .env.example
**Status:** Production Ready
**Shared Secrets:** ~/.proj344_secrets/.env
