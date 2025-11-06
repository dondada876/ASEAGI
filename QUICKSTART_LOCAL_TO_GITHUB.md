# Quick Start: Push ASEAGI to GitHub & Deploy Streamlit

**Time: 15 minutes**

---

## Step 1: Check Current Git Status (2 min)

```bash
cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI
git status
```

If you see "not a git repository", run:
```bash
git init
```

---

## Step 2: Update .gitignore (1 min)

Make sure your `.gitignore` file includes:

```gitignore
# Secrets - NEVER commit these!
.streamlit/secrets.toml
.env
*.env

# Python
__pycache__/
*.pyc
venv/
env/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

Check it exists:
```bash
type .gitignore
```

If missing, create it:
```bash
cat > .gitignore << 'EOF'
.streamlit/secrets.toml
.env
*.env
__pycache__/
*.pyc
venv/
env/
.DS_Store
Thumbs.db
*.log
EOF
```

---

## Step 3: Add All Files (1 min)

```bash
# Add everything except what's in .gitignore
git add .

# Check what will be committed
git status

# IMPORTANT: Verify secrets.toml is NOT listed
# If you see .streamlit/secrets.toml, STOP and add it to .gitignore
```

---

## Step 4: Create Commit (1 min)

```bash
git commit -m "Complete legal document processing system

- Context preservation system (8 tables, 5 views, 3 functions)
- ContextManager Python API
- Truth & Justice Timeline dashboard
- WordPress document upload system with multi-LLM processing
- Amelia Booking integration
- Complete documentation and deployment guides
- All tests passing (5/5)"
```

---

## Step 5: Create GitHub Repository (3 min)

1. **Go to GitHub:**
   - Visit: https://github.com/new

2. **Configure Repository:**
   - **Name:** `ASEAGI-legal-intelligence`
   - **Description:** `Legal intelligence platform with context preservation, multi-LLM processing, and truth/justice scoring`
   - **Visibility:** Private (recommended)
   - **DO NOT** check "Initialize with README"
   - Click "Create repository"

3. **Copy the commands shown on GitHub**, they look like:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/ASEAGI-legal-intelligence.git
   git branch -M main
   git push -u origin main
   ```

---

## Step 6: Push to GitHub (2 min)

```bash
# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ASEAGI-legal-intelligence.git

# Verify remote
git remote -v

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

Enter your GitHub credentials when prompted (or use Personal Access Token).

---

## Step 7: Verify on GitHub (1 min)

1. Go to: https://github.com/YOUR_USERNAME/ASEAGI-legal-intelligence
2. You should see all your files
3. **CRITICAL CHECK:** Make sure `.streamlit/secrets.toml` is NOT visible
4. Click on a few files to verify content

---

## Step 8: Deploy to Streamlit Cloud (5 min)

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App:**
   - Click "New app"
   - **Repository:** `YOUR_USERNAME/ASEAGI-legal-intelligence`
   - **Branch:** `main`
   - **Main file path:** `truth_justice_timeline.py`
   - Click "Advanced settings"

3. **Add Secrets:**
   - In "Secrets" section, paste:
   ```toml
   SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
   SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c"
   ```

4. **Deploy:**
   - Click "Deploy"
   - Wait 2-3 minutes for deployment
   - Your app will be live at: `https://YOUR_APP.streamlit.app`

---

## Step 9: Deploy Additional Dashboards (Optional)

Repeat Step 8 for each dashboard:

**Dashboard 2: Master Dashboard**
- Main file: `proj344_master_dashboard.py`
- Same secrets

**Dashboard 3: Data Diagnostic**
- Main file: `supabase_data_diagnostic.py`
- Same secrets

---

## Future Updates: Push Changes to GitHub

After making changes locally:

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with descriptive message
git commit -m "Describe what you changed"

# 4. Push to GitHub
git push

# 5. Streamlit Cloud auto-deploys within 1-2 minutes
```

---

## Troubleshooting

### Error: "secrets.toml contains sensitive data"

```bash
# Remove from git if accidentally added
git rm --cached .streamlit/secrets.toml

# Ensure .gitignore includes it
echo ".streamlit/secrets.toml" >> .gitignore

# Commit fix
git commit -m "Remove secrets from git"
git push --force
```

### Error: "git push rejected"

```bash
# Pull first
git pull origin main --allow-unrelated-histories

# Then push
git push
```

### Streamlit App Error: "Missing secrets"

1. Go to Streamlit Cloud dashboard
2. Click your app → Settings → Secrets
3. Add your Supabase credentials
4. Save and reboot app

---

## Summary

**What You Just Did:**

1. ✅ Initialized Git repository locally
2. ✅ Created .gitignore to protect secrets
3. ✅ Committed all code
4. ✅ Created GitHub repository
5. ✅ Pushed code to GitHub
6. ✅ Deployed to Streamlit Cloud
7. ✅ App is live and accessible from anywhere

**Your URLs:**

- **GitHub Repo:** https://github.com/YOUR_USERNAME/ASEAGI-legal-intelligence
- **Streamlit App:** https://YOUR_APP.streamlit.app

**Next Time You Make Changes:**

```bash
git add .
git commit -m "Your changes"
git push
# Streamlit auto-deploys!
```

---

**Status:** ✅ Complete - Your code is on GitHub and deployed to Streamlit Cloud!
