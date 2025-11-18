# 🚀 Repository Sentinel - Quick Start

**Get your code inventory system running in 5 minutes!**

---

## Step 1: Apply Database Schema (2 minutes)

```bash
# Navigate to ASEAGI
cd /home/user/ASEAGI

# Copy the SQL schema
cat database/migrations/005_code_repository_sentinel_schema.sql
```

**Then:**
1. Go to https://app.supabase.com
2. Open your project
3. Click "SQL Editor" in sidebar
4. Click "New Query"
5. Paste the SQL schema
6. Click "Run" (bottom right)
7. Wait for "Success" message

---

## Step 2: Scan Your First Repository (1 minute)

```bash
# Scan the ASEAGI repository itself
python3 scanners/repository_scanner.py /home/user/ASEAGI
```

**Expected output:**
```
🔍 Scanning repository: /home/user/ASEAGI
📊 Scan type: full
...
✅ Scan completed in 15.32 seconds
💾 Saving to database...
✅ Saved to database: github-dondada876-ASEAGI
✅ Repository scan complete!
```

---

## Step 3: Launch Dashboard (1 minute)

```bash
# Start the Streamlit dashboard
streamlit run dashboards/repository_sentinel_dashboard.py --server.port 8506
```

**Access at:** http://localhost:8506

You should see:
- ✅ Total Repositories: 1
- ✅ Overview statistics
- ✅ Language breakdown
- ✅ Repository cards

---

## Step 4: Configure Claude Desktop (Optional - 1 minute)

**Edit your Claude Desktop config:**

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
Linux: `~/.config/Claude/claude_desktop_config.json`
Windows: `%APPDATA%\Claude\claude_desktop_config.json`

**Add this:**
```json
{
  "mcpServers": {
    "repository-sentinel": {
      "command": "python",
      "args": [
        "/home/user/ASEAGI/mcp-servers/repository-sentinel-server/server.py"
      ],
      "env": {
        "SUPABASE_URL": "https://jvjlhxodmbkodzmggwpu.supabase.co",
        "SUPABASE_KEY": "your-supabase-key-here"
      }
    }
  }
}
```

**Restart Claude Desktop**

Then ask:
```
Claude, list all my repositories
Claude, show me details for the ASEAGI repository
Claude, which repositories use Streamlit?
```

---

## Step 5: Set Up Automation (Optional - 2 minutes)

### Option A: Cron (Simple)

```bash
# Make script executable
chmod +x scripts/auto_scan_repositories.sh

# Test it
./scripts/auto_scan_repositories.sh

# Add to crontab (runs daily at 2 AM)
crontab -e
```

Add this line:
```
0 2 * * * /home/user/ASEAGI/scripts/auto_scan_repositories.sh
```

### Option B: n8n (Advanced)

1. Go to https://n8n.io/
2. Sign up for free
3. Import `n8n-workflows/04-repository-sentinel-scanner.json`
4. Configure credentials
5. Activate workflow

---

## 🎉 You're Done!

**What you have now:**

✅ **Database:** Centralized repository inventory in Supabase
✅ **Scanner:** Python tool to analyze any repository
✅ **Dashboard:** Visual interface at http://localhost:8506
✅ **Claude Integration:** Query via Claude Desktop (if configured)
✅ **Automation:** Daily scans (if configured)

---

## 🔥 Try These Next

### Scan More Repositories

```bash
# Scan any repository
python3 scanners/repository_scanner.py /path/to/your/other/project

# The dashboard will automatically update!
```

### Query Your Inventory

**Via Dashboard:**
- Use filters in sidebar
- Search by name/description
- View health assessments
- Click repository cards for details

**Via Claude Desktop:**
- "Claude, list all Python repositories"
- "Claude, which repos need tests?"
- "Claude, show me my code statistics"

### Customize Automation

**Edit scan schedule:**
```bash
nano scripts/auto_scan_repositories.sh
```

Add more repositories to scan:
```bash
REPOS=(
    "/home/user/ASEAGI"
    "/home/user/other-project"
    "/home/user/another-repo"
)
```

---

## 📖 Full Documentation

For complete details, see:
- [Full Guide](/docs/REPOSITORY_SENTINEL_GUIDE.md)
- [Scanner README](/scanners/repository_scanner.py)
- [MCP Server README](/mcp-servers/repository-sentinel-server/README.md)
- [Database Schema](/database/migrations/005_code_repository_sentinel_schema.sql)

---

## 🆘 Quick Troubleshooting

**Dashboard shows "No repositories"**
```bash
# Run scanner first
python3 scanners/repository_scanner.py /home/user/ASEAGI
```

**"SUPABASE_URL not set" error**
```bash
# Check .env file
cat .env

# Or export manually
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your-key'
```

**Claude can't connect to MCP**
- Check config file syntax (valid JSON)
- Use absolute paths, not relative
- Restart Claude Desktop completely

---

**For Ashe. For Justice. For All Children.** 🛡️
