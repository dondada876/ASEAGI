# GitHub Setup Guide for PROJ344 Dashboards

## 🚀 Quick Setup

### Step 1: Initialize Git Repository

```bash
cd /Users/dbucknor/Downloads/proj344-dashboards

# Initialize git
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: PROJ344 Legal Intelligence Dashboards

- Multi-dimensional document scoring system
- PROJ344 Master Dashboard
- Legal Intelligence Dashboard
- CEO Dashboard
- Document scanning tools
- Supabase integration
- Complete documentation"
```

### Step 2: Create GitHub Repository

**Option A: Via GitHub Website**

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `proj344-dashboards`
3. Description: `AI-powered legal document intelligence system with multi-dimensional scoring`
4. **Visibility:**
   - ⚠️ **Private** (recommended for case data)
   - Or **Public** (if sanitized)
5. DO NOT initialize with README (we already have one)
6. Click "Create repository"

**Option B: Via GitHub CLI**

```bash
# Install GitHub CLI (if not installed)
brew install gh

# Login
gh auth login

# Create private repository
gh repo create proj344-dashboards --private --source=. --remote=origin --push

# Or create public repository
gh repo create proj344-dashboards --public --source=. --remote=origin --push
```

### Step 3: Push to GitHub

```bash
# Add remote (if created via website)
git remote add origin https://github.com/YOUR_USERNAME/proj344-dashboards.git

# Or use SSH
git remote add origin git@github.com:YOUR_USERNAME/proj344-dashboards.git

# Set main branch
git branch -M main

# Push
git push -u origin main
```

---

## 🔐 Security Checklist

### Before Pushing to GitHub

**✅ VERIFY these files are in .gitignore:**

```bash
# Check gitignore
cat .gitignore

# Should include:
# .env
# .env.local
# *.env
# credentials.json
# secrets.json
# *.pdf, *.jpg, *.png (case documents)
```

**✅ REMOVE any committed secrets:**

```bash
# Search for potential secrets
grep -r "SUPABASE_KEY" .
grep -r "ANTHROPIC_API_KEY" .
grep -r "sk-" .  # Anthropic keys start with sk-
grep -r "eyJ" .  # JWT tokens start with eyJ

# If found, remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/secret/file" \
  --prune-empty --tag-name-filter cat -- --all
```

**✅ CHECK for case-specific data:**

```bash
# Search for potentially sensitive info
grep -r "Ashe B" .
grep -r "J24-00478" .
grep -r "Bucknor" .

# If found in code, replace with variables
```

---

## 📝 .env File Safety

### Create .env (Local Only)

```bash
# Copy example
cp .env.example .env

# Edit with actual values
nano .env
```

**IMPORTANT:** The `.env` file is in `.gitignore` and will **NOT** be pushed to GitHub.

### For Team Members

Share credentials securely via:
- 1Password / LastPass (recommended)
- Encrypted email
- Secure messaging (Signal, etc.)

**NEVER:**
- Email plaintext credentials
- Post in Slack/Discord
- Commit to GitHub
- Share in screenshots

---

## 👥 Repository Settings

### Access Control

**For Private Repo:**

1. Go to `Settings` → `Collaborators`
2. Add team members with appropriate permissions:
   - **Read:** View code only
   - **Write:** Can push changes
   - **Admin:** Full control

### Branch Protection (Recommended)

1. Go to `Settings` → `Branches`
2. Add rule for `main` branch:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require conversation resolution
   - ✅ Include administrators

### Secrets (For GitHub Actions)

1. Go to `Settings` → `Secrets and variables` → `Actions`
2. Add:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `ANTHROPIC_API_KEY`

---

## 📦 Repository Structure

Your GitHub repo will look like this:

```
proj344-dashboards/
├── .github/
│   └── workflows/          # CI/CD (optional)
├── dashboards/
│   ├── proj344_master_dashboard.py
│   ├── legal_intelligence_dashboard.py
│   └── ceo_dashboard.py
├── scanners/
│   ├── batch_scan_documents.py
│   └── query_legal_documents.py
├── scripts/
│   └── launch-all-dashboards.sh
├── supabase/
│   └── schema.sql          # Database schema
├── docs/
│   ├── DEPLOYMENT.md
│   ├── GITHUB-SETUP.md
│   ├── DASHBOARD-GUIDE.md
│   └── SCANNING-GUIDE.md
├── .gitignore              # Security: excludes sensitive files
├── .env.example            # Template for environment variables
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Multi-container setup
├── Procfile                # Heroku deployment
└── README.md               # Main documentation
```

---

## 🔄 Daily Workflow

### Making Changes

```bash
# Pull latest changes
git pull origin main

# Create feature branch
git checkout -b feature/new-dashboard

# Make your changes
# ... edit files ...

# Stage changes
git add dashboards/new_dashboard.py

# Commit with descriptive message
git commit -m "Add new dashboard for timeline visualization

- Timeline chart with Plotly
- Filter by date range
- Export to PDF functionality"

# Push to GitHub
git push origin feature/new-dashboard

# Create Pull Request on GitHub
# Go to github.com/YOUR_USERNAME/proj344-dashboards
# Click "Compare & pull request"
```

### Updating from Main

```bash
# Switch to main
git checkout main

# Pull latest
git pull origin main

# Switch back to feature branch
git checkout feature/new-dashboard

# Merge main into feature branch
git merge main

# Resolve any conflicts
# ... fix conflicts ...

git add .
git commit -m "Merge main into feature branch"
git push origin feature/new-dashboard
```

---

## 🏷️ Releases & Versioning

### Creating a Release

```bash
# Tag a version
git tag -a v1.0.0 -m "Initial release: PROJ344 Dashboard System

Features:
- PROJ344 Master Dashboard
- Legal Intelligence Dashboard
- CEO Dashboard
- Document scanner with AI
- Multi-dimensional scoring (0-999)
- Supabase integration
"

# Push tag
git push origin v1.0.0

# Create GitHub Release
# Go to github.com/YOUR_USERNAME/proj344-dashboards/releases
# Click "Draft a new release"
# Select tag v1.0.0
# Add release notes
# Publish
```

### Version Numbering

Use [Semantic Versioning](https://semver.org/):

- **v1.0.0** - Major release
- **v1.1.0** - New features
- **v1.1.1** - Bug fixes

---

## 🔍 Repository Badges

Add to top of README.md:

```markdown
[![License](https://img.shields.io/badge/License-Private-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)
![Last Commit](https://img.shields.io/github/last-commit/YOUR_USERNAME/proj344-dashboards)
```

---

## 📊 GitHub Actions (Optional CI/CD)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 dashboards/ scanners/ --count --max-line-length=127

    - name: Check for secrets
      run: |
        if grep -r "sk-" .; then
          echo "Found potential API key!"
          exit 1
        fi
```

---

## 🚨 If You Accidentally Commit Secrets

### Remove from Git History

```bash
# Install BFG Repo-Cleaner
brew install bfg

# Remove file with secrets
bfg --delete-files secrets.env

# Or replace text
bfg --replace-text passwords.txt

# Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push (⚠️ destructive!)
git push origin --force --all
```

### Rotate Compromised Secrets

1. **Supabase:** Generate new anon key
2. **Anthropic:** Create new API key
3. **GitHub:** Regenerate personal access token
4. Update `.env` files for all team members

---

## 📚 Additional Resources

- [GitHub Docs](https://docs.github.com)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

## ✅ Setup Checklist

- [ ] Git initialized
- [ ] .gitignore configured
- [ ] No secrets in git history
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] README.md displays correctly
- [ ] Branch protection enabled
- [ ] Team members added
- [ ] Secrets configured (if using Actions)
- [ ] Repository badges added
- [ ] License file added (if needed)

---

**Ready to push to GitHub?** Run:

```bash
cd /Users/dbucknor/Downloads/proj344-dashboards
git init
git add .
git commit -m "Initial commit: PROJ344 dashboards"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/proj344-dashboards.git
git push -u origin main
```

**Then deploy to Streamlit Cloud!** See [DEPLOYMENT.md](DEPLOYMENT.md)
