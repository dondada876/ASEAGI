# 🖥️ Fix Your Local Terminal - ASEAGI Repository Setup

## 🔍 The Problem

Your local Mac terminal is in the **wrong directory**:
- ❌ Currently in: `/Users/dbucknor/Downloads/proj344-dashboards/`
- ✅ Should be in: The actual ASEAGI Git repository

This means files created locally won't sync with GitHub!

---

## 🎯 Quick Fix (5 minutes)

### Option 1: Clone the ASEAGI Repository (Recommended)

Open your Mac Terminal and run these commands:

```bash
# Navigate to your projects folder
cd ~/Documents

# Create a projects folder if it doesn't exist
mkdir -p Projects
cd Projects

# Clone the ASEAGI repository
git clone https://github.com/dondada876/ASEAGI.git

# Enter the repository
cd ASEAGI

# Verify you're in the right place
pwd
# Should show: /Users/dbucknor/Documents/Projects/ASEAGI

# Check git status
git status
# Should show: On branch main (or another branch)

# List files
ls -la
# Should show: error_log_uploader.py, n8n-workflows/, etc.
```

### Option 2: Navigate to Existing Clone (If you already cloned it)

```bash
# Search for existing ASEAGI folder
find ~ -name "ASEAGI" -type d 2>/dev/null

# Once you find it, navigate there
# Example: cd ~/Documents/ASEAGI
cd /path/to/ASEAGI

# Verify it's a git repo
git status
```

---

## 📋 Step-by-Step: Detailed Instructions

### Step 1: Check Your Current Location

```bash
# Open Terminal and check where you are
pwd
```

**What you'll see:**
```
/Users/dbucknor/Downloads/proj344-dashboards
```

This is **NOT** the ASEAGI repository!

### Step 2: Find or Clone ASEAGI

#### Method A: Search for Existing Repository

```bash
# Search your Mac for ASEAGI folder
mdfind -name "ASEAGI" kind:folder

# Or use find command
find ~ -name "ASEAGI" -type d 2>/dev/null
```

**If found:** Navigate to it with `cd /path/shown/ASEAGI`

**If not found:** Continue to Method B

#### Method B: Clone Fresh Copy

```bash
# Create a clean projects directory
mkdir -p ~/Documents/GitHub
cd ~/Documents/GitHub

# Clone the repository
git clone https://github.com/dondada876/ASEAGI.git

# Enter it
cd ASEAGI

# Check current branch
git branch

# Pull latest changes
git pull origin main
```

### Step 3: Verify You're in the Right Place

Run these commands to confirm:

```bash
# 1. Check you're in ASEAGI directory
pwd
# Should end with: /ASEAGI

# 2. Check git remote
git remote -v
# Should show:
# origin  https://github.com/dondada876/ASEAGI.git (fetch)
# origin  https://github.com/dondada876/ASEAGI.git (push)

# 3. List files
ls -la
# Should see:
# - error_log_uploader.py
# - n8n-workflows/
# - proj344_style.py
# - dashboard files
# - .git folder

# 4. Check git status
git status
# Should show clean working tree or current changes
```

### Step 4: Pull Latest Changes

```bash
# Make sure you have all the latest files
git checkout main
git pull origin main

# You should see the n8n-workflows folder now!
ls -la n8n-workflows/
```

---

## 🔐 Configure Git (First Time Only)

If this is your first time using Git on this Mac:

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email (same as GitHub account)
git config --global user.email "your.email@example.com"

# Check configuration
git config --list
```

---

## 🚀 Working with the Repository

### Always Start Here

Every time you open Terminal for ASEAGI work:

```bash
# Navigate to ASEAGI
cd ~/Documents/GitHub/ASEAGI  # Adjust path as needed

# Check current branch
git branch

# Pull latest changes
git pull
```

### Create an Alias for Quick Access

Add this to your `~/.zshrc` or `~/.bash_profile`:

```bash
# Open the file
nano ~/.zshrc

# Add this line at the end:
alias aseagi="cd ~/Documents/GitHub/ASEAGI && git status"

# Save: Ctrl+O, Enter, Ctrl+X

# Reload shell
source ~/.zshrc

# Now you can just type:
aseagi
```

---

## 📁 Directory Structure Comparison

### ❌ Wrong Location (Where you were)

```
/Users/dbucknor/Downloads/proj344-dashboards/
├── n8n-workflows/     ← Files created here
│   ├── 01-daily-report.json
│   ├── 02-high-priority-alerts.json
│   └── 03-weekly-statistics.json
└── (no .git folder = not a repository!)
```

### ✅ Correct Location (Where you should be)

```
/Users/dbucknor/Documents/GitHub/ASEAGI/
├── .git/              ← This proves it's a git repo!
├── error_log_uploader.py
├── n8n-workflows/     ← Files should be created here
│   ├── 01-daily-report.json
│   ├── 02-high-priority-alerts.json
│   ├── 03-weekly-statistics.json
│   ├── README.md
│   └── LOCAL_TERMINAL_SETUP.md (this file!)
├── proj344_style.py
├── dashboard files...
└── README.md
```

---

## 🔄 Sync Local and Remote

### Pull Latest Changes from GitHub

```bash
# Make sure you're in ASEAGI directory
cd ~/Documents/GitHub/ASEAGI

# Get latest changes from GitHub
git pull origin main

# Or for a specific branch:
git pull origin claude/error-log-uploader-011CUqCjDtEfuhzwnDrKJsky
```

### Check What Branch You're On

```bash
# See all branches
git branch -a

# Switch to a branch
git checkout main
# or
git checkout claude/error-log-uploader-011CUqCjDtEfuhzwnDrKJsky
```

### View Recent Commits

```bash
# See recent changes
git log --oneline -10

# See what changed in each commit
git log --stat -5
```

---

## 🆘 Troubleshooting

### "Not a git repository" Error

**Problem:** You're not in the ASEAGI folder

**Solution:**
```bash
# Find ASEAGI
find ~ -name "ASEAGI" -type d 2>/dev/null

# Navigate to it
cd /path/found/ASEAGI

# Verify
git status
```

### "Permission Denied" Error

**Problem:** Need to authenticate with GitHub

**Solution:**
```bash
# Option 1: Use Personal Access Token
# Generate at: https://github.com/settings/tokens
# Use token as password when prompted

# Option 2: Set up SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"
# Follow GitHub SSH setup guide
```

### Can't Find Cloned Repository

**Solution:**
```bash
# Search everywhere
find ~ -name ".git" -type d 2>/dev/null | grep ASEAGI

# If nothing found, clone again
cd ~/Documents
git clone https://github.com/dondada876/ASEAGI.git
```

### Files Not Syncing

**Problem:** Working in wrong folder

**Solution:**
```bash
# 1. Check you're in right place
pwd | grep ASEAGI

# 2. If not, find it
mdfind -name "ASEAGI"

# 3. Navigate there
cd /correct/path/ASEAGI

# 4. Verify
git remote -v
```

---

## ✅ Verification Checklist

Before continuing with n8n setup, verify:

- [ ] Terminal is in ASEAGI directory (`pwd` shows /ASEAGI)
- [ ] Git remote is correct (`git remote -v` shows dondada876/ASEAGI)
- [ ] Can see `.git` folder (`ls -la | grep .git`)
- [ ] Can see `error_log_uploader.py` file (`ls -la | grep error`)
- [ ] Can see `n8n-workflows` folder (`ls -la | grep n8n`)
- [ ] Git status works (`git status` shows no errors)
- [ ] Latest changes pulled (`git pull` shows "Already up to date")

---

## 📱 Access n8n Workflows

Now that you're in the correct directory:

```bash
# Navigate to workflows
cd n8n-workflows

# List the files
ls -la
# You should see:
# - 01-daily-report.json
# - 02-high-priority-alerts.json
# - 03-weekly-statistics.json
# - README.md
# - LOCAL_TERMINAL_SETUP.md

# Open README for n8n setup instructions
cat README.md

# Or open in your editor
open README.md
# or
code README.md  # If using VS Code
```

---

## 🎯 Next Steps

1. **Verify you're in correct directory** ✅
2. **Pull latest changes** ✅
3. **Navigate to n8n-workflows/** ✅
4. **Follow README.md for n8n Cloud setup** ⏭️

---

## 💡 Pro Tips

### Create a Shell Bookmark

Add to `~/.zshrc`:

```bash
# Quick navigation
alias aseagi="cd ~/Documents/GitHub/ASEAGI"
alias asn8n="cd ~/Documents/GitHub/ASEAGI/n8n-workflows"

# Quick git commands
alias gs="git status"
alias gp="git pull"
alias gl="git log --oneline -10"

# Use them:
aseagi    # Jump to ASEAGI
asn8n     # Jump to n8n workflows
gs        # Check git status
```

### Use a Better Terminal Prompt

Shows current git branch in your prompt:

```bash
# Add to ~/.zshrc
autoload -Uz vcs_info
precmd() { vcs_info }
zstyle ':vcs_info:git:*' formats ' (%b)'
setopt PROMPT_SUBST
PROMPT='%F{green}%~%f%F{yellow}${vcs_info_msg_0_}%f $ '
```

Now your terminal will show:
```
~/Documents/GitHub/ASEAGI (main) $
```

---

## 📞 Still Having Issues?

### Common Questions

**Q: Do I need to delete the old proj344-dashboards folder?**

A: No, but you can. It's not connected to Git, so it's safe to delete or keep as a backup.

**Q: Can I have multiple clones of ASEAGI?**

A: Yes, but it's confusing. Best to have just one in a consistent location.

**Q: How do I know which is the "real" repository?**

A: The one with:
1. A `.git` folder
2. `git remote -v` showing github.com/dondada876/ASEAGI
3. Latest commits from GitHub

**Q: What if I have changes in the wrong folder?**

A: Copy the files manually to the correct ASEAGI folder, then commit them there.

---

**Last Updated:** November 6, 2025
**Next:** Follow `README.md` in n8n-workflows/ folder for automation setup!
