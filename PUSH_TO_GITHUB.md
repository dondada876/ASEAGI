# Push to GitHub - Manual Steps

Your code is ready to push to GitHub! Follow these steps:

## ✅ Already Done

- ✅ Git repository initialized
- ✅ All files committed
- ✅ README.md created
- ✅ .gitignore configured
- ✅ 16 files ready to push

## 📋 Next Steps

### Option 1: Using GitHub CLI (Recommended)

**Install GitHub CLI:**
```bash
brew install gh
```

**Authenticate:**
```bash
gh auth login
```

**Create repository and push:**
```bash
cd ~/proj344-dashboard
gh repo create proj344-dashboard --private --source=. --remote=origin --push
```

### Option 2: Manual via GitHub Website

**Step 1: Create Repository on GitHub**

1. Go to https://github.com/new
2. Repository name: `proj344-dashboard`
3. Description: "PROJ344 Legal Case Intelligence Dashboard"
4. Visibility: **Private** (recommended for sensitive case data)
5. DO NOT initialize with README (we already have one)
6. Click "Create repository"

**Step 2: Push Your Code**

Copy your GitHub username, then run:

```bash
cd ~/proj344-dashboard

# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/proj344-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/donbucknor/proj344-dashboard.git
git push -u origin main
```

You'll be prompted for your GitHub credentials.

### Option 3: Using SSH (If you have SSH key set up)

```bash
cd ~/proj344-dashboard

# Replace YOUR_USERNAME with your GitHub username
git remote add origin git@github.com:YOUR_USERNAME/proj344-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔐 Security Reminder

Before pushing:

1. ✅ `.env` is in `.gitignore` (already done)
2. ✅ `secrets.toml` is in `.gitignore` (already done)
3. ✅ No API keys in code (verified)
4. ⚠️  Consider making repository **PRIVATE** (contains case information)

## 📦 What's Being Pushed

```
16 files, 5,446 lines of code

Key files:
- proj344_master_dashboard.py      (Main PROJ344 dashboard)
- ceo_global_dashboard.py          (CEO life management)
- timeline_constitutional_violations.py
- proj344_style.py                 (Shared components)
- requirements.txt                 (Dependencies)
- README.md                        (Documentation)
- .streamlit/config.toml           (Configuration)
```

## ✅ After Pushing

Your repository will be at:
```
https://github.com/YOUR_USERNAME/proj344-dashboard
```

### Deploy to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Select your GitHub repository
4. Main file: `proj344_master_dashboard.py`
5. Add secrets in Streamlit dashboard:
   ```toml
   SUPABASE_URL = "your-url"
   SUPABASE_KEY = "your-key"
   ```
6. Deploy!

## 🆘 Troubleshooting

**Authentication Error:**
```bash
# Use Personal Access Token instead of password
# Create token at: https://github.com/settings/tokens
```

**Permission Denied:**
```bash
# Set up SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"
# Add to GitHub: https://github.com/settings/keys
```

**Repository Already Exists:**
```bash
# Check existing remotes
git remote -v

# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/proj344-dashboard.git
```

## 📊 Current Status

```bash
# View repository status
cd ~/proj344-dashboard
git status
git log --oneline

# View what will be pushed
git remote -v
git branch -a
```

## 🔄 Future Updates

After making changes:

```bash
cd ~/proj344-dashboard

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push
```

---

**Repository Ready to Push!** 🚀

Choose your preferred method above and push to GitHub.
