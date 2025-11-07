# MULTI-REPOSITORY MANAGEMENT GUIDE
**Managing ASEAGI + don1_automation + n8n Repositories**

---

## 📊 CURRENT REPOSITORY LANDSCAPE

### **Discovered Repositories:**

| Repo | Status | Purpose | Language |
|------|--------|---------|----------|
| **ASEAGI** | ✅ Active | Legal case intelligence, dashboards, analysis | Python |
| **n8n** | ⚪ Empty | Workflow automation (n8n workflows) | JSON/TypeScript |
| **woocommerce** | 🔀 Fork | E-commerce (forked) | PHP |
| **don1_automation** | ❌ Not Found | (Planned?) Automation scripts | ? |

---

## 🎯 RECOMMENDED REPOSITORY ARCHITECTURE

### **Strategy 1: Separation of Concerns** (RECOMMENDED)

```
📁 ASEAGI (Current)
├─ Legal intelligence system
├─ Dashboards (Streamlit)
├─ Database schemas
├─ Analysis tools
└─ Documentation

📁 don1_automation (New - Create This)
├─ Business automation
├─ Task management
├─ General utilities
├─ Cross-system integrations
└─ Shared libraries

📁 n8n (Configure This)
├─ n8n workflow exports (.json)
├─ Telegram bot workflows
├─ Webhook handlers
├─ Integration recipes
└─ Workflow documentation
```

**Why Separate?**
- ✅ Clear boundaries
- ✅ Independent deployment
- ✅ Different teams can work on each
- ✅ Easier to open-source parts
- ✅ Better security (different access levels)

---

## 🔄 CROSS-REPO RELATIONSHIP PATTERNS

### **Pattern 1: Service Architecture** (Best for You)

```
┌─────────────────────────────────────────────┐
│  ASEAGI (Legal Intelligence)                │
│  - Legal dashboards                         │
│  - Police reports analysis                  │
│  - Court timeline tracking                  │
│  - Database: Supabase                       │
└───────────┬─────────────────────────────────┘
            │
            │ Shared: Database, APIs
            │
┌───────────┴─────────────────────────────────┐
│  don1_automation (Business Logic)           │
│  - CEO dashboard backend                    │
│  - Task automation                          │
│  - Revenue tracking                         │
│  - General utilities                        │
└───────────┬─────────────────────────────────┘
            │
            │ Triggers: Webhooks, HTTP calls
            │
┌───────────┴─────────────────────────────────┐
│  n8n (Workflow Orchestration)               │
│  - Telegram bot workflows                   │
│  - Document ingestion triggers              │
│  - Scheduled tasks                          │
│  - External integrations                    │
└─────────────────────────────────────────────┘
```

---

## 💻 WORKING WITH MULTIPLE REPOS: BEST PRACTICES

### **Method 1: Separate Claude Code Sessions** ⭐ RECOMMENDED

**Why:** Clean separation, no confusion, proper context per repo

**Setup:**
```bash
# Terminal 1: ASEAGI work
cd ~/ASEAGI
claude-code

# Terminal 2: don1_automation work
cd ~/don1_automation
claude-code

# Terminal 3: n8n work
cd ~/n8n
claude-code
```

**Pros:**
- ✅ Full context per repository
- ✅ No file confusion
- ✅ Git operations isolated
- ✅ Can work in parallel
- ✅ Each session has repo-specific history

**Cons:**
- ⚠️ Need to switch terminals
- ⚠️ Can't directly reference across repos (but can copy context)

---

### **Method 2: Parent Directory Approach**

**Setup:**
```bash
# Create parent directory
mkdir ~/projects
cd ~/projects

# Clone all repos
git clone https://github.com/dondada876/ASEAGI
git clone https://github.com/dondada876/don1_automation
git clone https://github.com/dondada876/n8n

# Single Claude session at parent level
cd ~/projects
claude-code
```

**Structure:**
```
~/projects/
├── ASEAGI/
│   ├── dashboards
│   └── utilities
├── don1_automation/
│   ├── business
│   └── integrations
└── n8n/
    └── workflows
```

**Pros:**
- ✅ See all repos in one session
- ✅ Easy to copy code between repos
- ✅ Can reference files across repos
- ✅ Single context window

**Cons:**
- ⚠️ Larger context (more tokens)
- ⚠️ Git operations need explicit repo paths
- ⚠️ More complex prompts ("in ASEAGI repo, do X")

---

### **Method 3: Git Submodules** (Advanced)

**Setup:**
```bash
cd ~/ASEAGI

# Add don1_automation as submodule
git submodule add https://github.com/dondada876/don1_automation integrations/don1_automation

# Add n8n workflows as submodule
git submodule add https://github.com/dondada876/n8n workflows/n8n
```

**Structure:**
```
ASEAGI/
├── dashboards/
├── utilities/
├── integrations/
│   └── don1_automation/  ← Submodule
└── workflows/
    └── n8n/              ← Submodule
```

**Pros:**
- ✅ Single repo view
- ✅ Version locking (submodules pinned to commits)
- ✅ Clean imports
- ✅ Single clone command

**Cons:**
- ⚠️ Git submodules are complex
- ⚠️ Nested commits can be confusing
- ⚠️ Team members need to understand submodules

---

### **Method 4: Monorepo** (Alternative)

**Setup:**
```bash
# Single repo with multiple projects
ASEAGI/
├── packages/
│   ├── legal-intelligence/    # Current ASEAGI code
│   ├── automation/             # don1_automation code
│   └── workflows/              # n8n workflows
├── shared/
│   └── common libraries
└── package.json (if using workspace)
```

**Pros:**
- ✅ Single repo to manage
- ✅ Easy code sharing
- ✅ Atomic commits across projects
- ✅ Simpler CI/CD

**Cons:**
- ⚠️ Large repo size
- ⚠️ All-or-nothing access
- ⚠️ Harder to open-source parts

---

## 🚀 RECOMMENDED SETUP FOR YOUR USE CASE

### **Best Practice: Separate Repos + Context Files**

**Step 1: Create Repository Structure**

```bash
# 1. Keep ASEAGI as-is (legal intelligence)
cd ~/ASEAGI

# 2. Create don1_automation repo
cd ~
mkdir don1_automation
cd don1_automation
git init
git remote add origin https://github.com/dondada876/don1_automation

# 3. Use n8n repo for workflows
cd ~
git clone https://github.com/dondada876/n8n
```

**Step 2: Define Repo Boundaries**

**ASEAGI Repo Contains:**
- ✅ Legal document intelligence
- ✅ Police reports analysis
- ✅ Court case tracking
- ✅ Constitutional violations
- ✅ Legal-specific dashboards
- ✅ Truth/justice scoring
- ✅ Database schemas for legal data

**don1_automation Repo Contains:**
- ✅ CEO dashboard backend
- ✅ Business revenue tracking
- ✅ Task management automation
- ✅ Personal/family document workflows
- ✅ General utilities (not legal-specific)
- ✅ Cross-system integrations
- ✅ Shared libraries

**n8n Repo Contains:**
- ✅ Telegram bot workflow JSONs
- ✅ Document ingestion workflows
- ✅ Scheduled automation workflows
- ✅ Webhook handlers
- ✅ External API integrations

**Step 3: Create Context Bridge Files**

Each repo should have a `CROSS_REPO_LINKS.md`:

```markdown
# Cross-Repository Links

## Related Repositories
- ASEAGI: https://github.com/dondada876/ASEAGI
- don1_automation: https://github.com/dondada876/don1_automation
- n8n: https://github.com/dondada876/n8n

## Shared Resources
- Database: Supabase (jvjlhxodmbkodzmggwpu.supabase.co)
- Telegram Bot: @ASEAGI_Bot
- API Endpoints: https://api.example.com

## Integration Points
- don1_automation calls ASEAGI via: REST API at /api/legal
- n8n triggers ASEAGI via: Webhook at /webhook/document-upload
- ASEAGI queries don1_automation via: Database views

## Documentation
- Architecture: See ASEAGI/ARCHITECTURE.md
- API Docs: See don1_automation/API.md
- Workflow Docs: See n8n/WORKFLOWS.md
```

---

## 🛠️ TOOLS FOR MULTI-REPO MANAGEMENT

### **Tool 1: Repo Switcher Script**

Create `~/switch-repo.sh`:

```bash
#!/bin/bash
# Quick repository switcher

case "$1" in
  aseagi|legal)
    cd ~/ASEAGI
    echo "📊 Switched to ASEAGI (Legal Intelligence)"
    ;;
  automation|auto|business)
    cd ~/don1_automation
    echo "🤖 Switched to don1_automation (Business Logic)"
    ;;
  n8n|workflows)
    cd ~/n8n
    echo "🔄 Switched to n8n (Workflows)"
    ;;
  *)
    echo "Usage: switch-repo [aseagi|automation|n8n]"
    ;;
esac

pwd
git status
```

Usage:
```bash
source ~/switch-repo.sh aseagi
source ~/switch-repo.sh automation
```

---

### **Tool 2: Multi-Repo Status Checker**

Create `~/repos-status.py`:

```python
#!/usr/bin/env python3
"""Check status of all ASEAGI-related repositories"""

import subprocess
from pathlib import Path

REPOS = {
    'ASEAGI': '~/ASEAGI',
    'don1_automation': '~/don1_automation',
    'n8n': '~/n8n',
}

def check_repo(name, path):
    path = Path(path).expanduser()

    if not path.exists():
        print(f"❌ {name}: Not found at {path}")
        return

    print(f"\n📁 {name} ({path})")
    print("─" * 60)

    # Git status
    result = subprocess.run(
        ['git', 'status', '--short'],
        cwd=path,
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print(f"  Modified files:")
        for line in result.stdout.strip().split('\n'):
            print(f"    {line}")
    else:
        print(f"  ✅ Clean working tree")

    # Current branch
    result = subprocess.run(
        ['git', 'branch', '--show-current'],
        cwd=path,
        capture_output=True,
        text=True
    )
    branch = result.stdout.strip()
    print(f"  Branch: {branch}")

    # Unpushed commits
    result = subprocess.run(
        ['git', 'log', '@{u}..', '--oneline'],
        cwd=path,
        capture_output=True,
        text=True
    )
    if result.stdout.strip():
        count = len(result.stdout.strip().split('\n'))
        print(f"  ⚠️  {count} unpushed commit(s)")

def main():
    print("=" * 60)
    print("🔍 MULTI-REPO STATUS CHECK")
    print("=" * 60)

    for name, path in REPOS.items():
        check_repo(name, path)

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
```

Usage:
```bash
python ~/repos-status.py
```

---

### **Tool 3: Cross-Repo Search**

Create `~/search-all.sh`:

```bash
#!/bin/bash
# Search across all repos

SEARCH_TERM="$1"

if [ -z "$SEARCH_TERM" ]; then
  echo "Usage: search-all.sh <search term>"
  exit 1
fi

echo "🔍 Searching for: $SEARCH_TERM"
echo "=" * 60

for repo in ~/ASEAGI ~/don1_automation ~/n8n; do
  if [ -d "$repo" ]; then
    echo ""
    echo "📁 Searching in $(basename $repo)..."
    grep -r "$SEARCH_TERM" "$repo" --include="*.py" --include="*.md" --include="*.json" 2>/dev/null | head -5
  fi
done
```

---

## 💡 CLAUDE CODE WORKFLOWS

### **Workflow 1: Working on Single Repo** (Most Common)

```bash
# Start Claude session in specific repo
cd ~/ASEAGI
claude-code

# Do work in ASEAGI
# When done, exit
```

**Transition to another repo:**
```bash
# Exit current session
# Switch directory
cd ~/don1_automation
claude-code

# Reference previous work by saying:
"I was working in ASEAGI repo on X. Now I need to implement Y in don1_automation that integrates with it."
```

---

### **Workflow 2: Cross-Repo Feature** (Occasional)

```bash
# Start at parent level
cd ~/projects
claude-code

# Be explicit in prompts:
"In ASEAGI repo, create API endpoint for police reports.
 In don1_automation repo, create client to call that endpoint."
```

---

### **Workflow 3: Using Context Transition Files** (Best)

**In ASEAGI, create:**
`TRANSITION_TO_AUTOMATION.md`:

```markdown
# Context Transition: ASEAGI → don1_automation

## What I Just Built in ASEAGI:
- Police Reports Dashboard (port 8502)
- Schema analyzer with 5W+H framework
- Context preservation system

## What Needs to Be Built in don1_automation:
- API client to query ASEAGI database
- CEO dashboard backend (separate from ASEAGI)
- Revenue tracking system
- Integration with n8n workflows

## Shared Resources:
- Database: Supabase (same instance)
- API: /api/legal/* (hosted by ASEAGI)
- Credentials: .streamlit/secrets.toml (copy to don1_automation)

## Next Steps in don1_automation:
1. Create repo structure
2. Set up virtual environment
3. Create Supabase client
4. Build CEO backend API
```

**Then in new Claude session:**
```bash
cd ~/don1_automation
claude-code

# First message:
"Please read this context file from ASEAGI: [paste TRANSITION_TO_AUTOMATION.md content]
Now let's build the don1_automation repo based on this context."
```

---

## 📋 RECOMMENDED WORKFLOW FOR YOU

Based on your projects, here's what I recommend:

### **Step 1: Create don1_automation Repo** (15 min)

```bash
# Create locally
mkdir ~/don1_automation
cd ~/don1_automation
git init

# Create on GitHub
# Go to https://github.com/new
# Name: don1_automation
# Description: "CEO automation, business logic, and cross-system integrations"

# Connect
git remote add origin https://github.com/dondada876/don1_automation
git branch -M main
```

### **Step 2: Define What Goes Where** (10 min)

**Move to don1_automation:**
- CEO dashboard business logic
- Revenue tracking backend
- Task automation (non-legal)
- General utilities
- Business document processing

**Keep in ASEAGI:**
- All legal dashboards
- Police reports system
- Court tracking
- Legal schemas
- Truth/justice scoring

**Move to n8n:**
- Export all n8n workflows as JSON
- Document each workflow
- Version control workflow configs

### **Step 3: Set Up Cross-Repo Links** (5 min)

Create `CROSS_REPO_LINKS.md` in each repo (see template above)

### **Step 4: Work Pattern** (Daily)

**Morning: Check all repos**
```bash
python ~/repos-status.py
```

**During work: One repo at a time**
```bash
# Legal work
cd ~/ASEAGI && claude-code

# Business work
cd ~/don1_automation && claude-code

# Workflow work
cd ~/n8n && code .  # Use VS Code for JSON editing
```

**End of day: Sync everything**
```bash
# In each repo
git add .
git commit -m "Daily work"
git push
```

---

## 🎯 DECISION MATRIX

| Your Need | Recommended Approach |
|-----------|---------------------|
| Work on legal dashboards | `cd ASEAGI && claude-code` |
| Work on business automation | `cd don1_automation && claude-code` |
| Edit n8n workflows | Use n8n UI, export to repo |
| Search across all repos | Use `search-all.sh` |
| Check status of all | Use `repos-status.py` |
| Deploy ASEAGI | Streamlit Cloud from ASEAGI repo |
| Deploy automation | Separate service from don1_automation |
| Telegram bot | n8n webhook (in n8n repo) |

---

## 🚀 IMMEDIATE NEXT STEPS

### **Option A: Create don1_automation Now** (30 min)
I'll help you:
1. Create the repo structure
2. Define clear boundaries
3. Set up initial files
4. Create cross-repo documentation

### **Option B: Audit Current ASEAGI** (15 min)
I'll help you:
1. Identify code that should move to don1_automation
2. Document dependencies
3. Plan the split
4. Create migration checklist

### **Option C: Set Up Multi-Repo Tools** (20 min)
I'll help you:
1. Create repo switcher script
2. Create status checker
3. Create cross-repo search
4. Set up convenience aliases

---

## 💬 ANSWERING YOUR QUESTIONS

**Q: "What's the best way to check on both?"**
**A:** Use the `repos-status.py` script (I can create it). Shows git status, branches, unpushed commits for all repos at once.

**Q: "Write to them simultaneously?"**
**A:** Not recommended. Instead:
- Work in one repo at a time with separate Claude sessions
- Use context transition files to maintain continuity
- OR use parent directory approach for related changes

**Q: "Through web/cloud code?"**
**A:** Claude Code works locally with git. For cloud:
- Push to GitHub after each session
- Each repo deploys independently
- Use shared database (Supabase) to connect them

**Q: "Best practices?"**
**A:**
1. Separate repos for separate concerns
2. One Claude session per repo (clean context)
3. Cross-repo links documentation
4. Shared database, independent code
5. Deploy each repo independently

---

**What would you like to do first?**

A) Create don1_automation repo and structure
B) Audit ASEAGI to see what should split
C) Set up multi-repo management tools
D) Something else

Let me know and I'll help you implement it!
