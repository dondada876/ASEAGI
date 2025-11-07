# ASEAGI MVP MCP Server

**For Ashe - Protecting children through intelligent legal assistance** ⚖️

Model Context Protocol (MCP) server that gives Claude direct access to your ASEAGI case database via 5 powerful tools.

---

## 🎯 What This Does

Enables Claude Desktop to:
- 🔍 Search 601 legal documents with relevancy scoring
- 📅 Get chronological case timeline from court events
- 💬 Search communications (texts, emails, letters)
- ✅ Track action items and deadlines
- 📝 Generate motion outlines

**All querying your actual Supabase database in real-time.**

---

## ✨ What's Fixed in This Version

| Issue | Status |
|-------|--------|
| ✅ Supabase version 2.3.0 → 2.12.0 | FIXED (no more proxy error) |
| ✅ Schema adapted to existing tables | FIXED (uses legal_documents, court_events) |
| ✅ Missing .env.example | FIXED (template included) |
| ✅ Ready for Claude Desktop | READY TO TEST |

---

## 📁 Project Structure

```
aseagi-mvp-server/
├── server.py          # Main MCP server (655+ lines, 5 tools)
├── requirements.txt   # Python dependencies (supabase>=2.12.0)
├── .env.example       # Environment template
├── .env               # Your actual credentials (create this)
└── README.md          # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd /home/user/ASEAGI/mcp-servers/aseagi-mvp-server

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env and add your Supabase key
nano .env  # or use your favorite editor
```

Your `.env` should look like:
```bash
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUz...your-actual-key-here
```

### 3. Test the Server

```bash
# Test connection
python3 server.py
```

You should see:
```
INFO - Starting ASEAGI MVP MCP Server...
INFO - For Ashe - Protecting children through intelligent legal assistance
INFO - ✓ Supabase connection verified
INFO - ✓ MCP server ready - waiting for connections...
```

Press `Ctrl+C` to stop.

---

## 🔧 Claude Desktop Integration

### macOS / Linux

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aseagi": {
      "command": "python3",
      "args": [
        "/home/user/ASEAGI/mcp-servers/aseagi-mvp-server/server.py"
      ],
      "env": {
        "SUPABASE_URL": "https://jvjlhxodmbkodzmggwpu.supabase.co",
        "SUPABASE_KEY": "your-supabase-anon-key-here"
      }
    }
  }
}
```

### Windows

Edit: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "aseagi": {
      "command": "python",
      "args": [
        "C:\\Users\\YourName\\ASEAGI\\mcp-servers\\aseagi-mvp-server\\server.py"
      ],
      "env": {
        "SUPABASE_URL": "https://jvjlhxodmbkodzmggwpu.supabase.co",
        "SUPABASE_KEY": "your-supabase-anon-key-here"
      }
    }
  }
}
```

### Restart Claude Desktop

After saving the config, **fully quit and restart** Claude Desktop.

---

## 🛠️ Available Tools

### 1. search_documents

Search 601 legal documents with relevancy and micro scoring.

**Example Claude prompts:**
```
"Search for documents about custody evaluation"
"Find all filings by the mother from 2024"
"Show me documents with relevancy score above 800"
```

**Parameters:**
- `query` - Search term for filename or content
- `category` - Filter by document category
- `min_relevancy` - Minimum score (0-1000)
- `party` - Filter by party (mother/father/court)
- `limit` - Max results (default: 20)

**Database:** Uses `legal_documents` table (601 docs)

---

### 2. get_timeline

Get chronological case events from court database.

**Example Claude prompts:**
```
"Show me the case timeline"
"What court events happened in March 2024?"
"Get all hearings from the timeline"
```

**Parameters:**
- `start_date` - Events after (YYYY-MM-DD)
- `end_date` - Events before (YYYY-MM-DD)
- `event_type` - Filter type (hearing/filing/motion)
- `limit` - Max events (default: 100)

**Database:** Uses `court_events` table

---

### 3. search_communications

Search texts, emails, and other communications.

**Example Claude prompts:**
```
"Find communications from the mother about visitation"
"Search emails sent between March 1 and March 15"
"Show me texts mentioning 'custody'"
```

**Parameters:**
- `query` - Search content
- `sender` - Filter by sender
- `recipient` - Filter by recipient
- `start_date` / `end_date` - Date range
- `limit` - Max results (default: 50)

**Database:** Uses `communications_matrix` table (if available)

**Note:** If table doesn't exist yet, returns helpful message about Phase 2.

---

### 4. get_action_items

Get pending tasks and court deadlines.

**Example Claude prompts:**
```
"What action items do I have?"
"Show me high priority tasks"
"What deadlines are coming up?"
```

**Status:** Phase 1 returns informative message. Phase 2 will connect to `action_items` table.

---

### 5. generate_motion

Generate motion outline with legal structure.

**Example Claude prompts:**
```
"Generate a W&I 388 motion outline for changed circumstances"
"Create a CCP 473(d) motion based on fraud"
"Draft an RFO for custody modification"
```

**Parameters:**
- `motion_type` - Type (W&I 388, CCP 473(d), RFO, etc.)
- `grounds` - Legal/factual basis
- `relief_requested` - What you're asking for
- `supporting_evidence` - Document IDs or references

**Status:** Phase 1 returns structured template. Phase 2 will generate full PDF.

---

## 💡 Usage Examples

### Example 1: Research Case Timeline

**You:** "Can you show me all court events from 2024 and identify any concerning patterns?"

**Claude will:**
1. Call `get_timeline(start_date="2024-01-01")`
2. Analyze the events
3. Identify patterns (delays, bias, procedural issues)
4. Summarize findings

---

### Example 2: Find Evidence for Motion

**You:** "I need to file a W&I 388 motion. Find documents showing changed circumstances regarding the mother's mental health."

**Claude will:**
1. Call `search_documents(query="mental health", party="mother")`
2. Review relevancy scores
3. Call `get_timeline(event_type="evaluation")` for context
4. Call `generate_motion()` with findings
5. Provide structured outline with evidence references

---

### Example 3: Track Communications

**You:** "Search for any emails from the mother where she contradicts herself about her whereabouts."

**Claude will:**
1. Call `search_communications(sender="mother", query="whereabouts")`
2. Analyze content for contradictions
3. Cross-reference with `get_timeline()` for dates
4. Identify specific contradictions with timestamps

---

## 🗄️ Database Schema

### Tables Used

| Table | Status | Purpose |
|-------|--------|---------|
| `legal_documents` | ✅ EXISTS (601 docs) | search_documents |
| `court_events` | ✅ EXISTS | get_timeline |
| `legal_violations` | ✅ EXISTS | (Future: violation analysis) |
| `communications_matrix` | ⚠️ TBD | search_communications |
| `action_items` | 📅 Phase 2 | get_action_items |

### Expected Columns

**legal_documents:**
- original_filename
- document_type
- party_author
- relevancy_number (0-1000)
- micro_number (0-1000)
- categories (array)
- created_at
- supabase_path

**court_events:**
- event_date
- event_type
- event_title
- event_description
- judge_name
- event_outcome

**communications_matrix:**
- sender
- recipient
- subject
- summary
- communication_date
- communication_method

---

## 🐛 Troubleshooting

### "Missing Supabase credentials"

**Problem:** SUPABASE_URL or SUPABASE_KEY not set

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify contents
cat .env

# Should show:
# SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
# SUPABASE_KEY=eyJhbGc...
```

---

### "ModuleNotFoundError: No module named 'mcp'"

**Problem:** Dependencies not installed

**Solution:**
```bash
pip install -r requirements.txt

# Or install individually
pip install mcp>=0.9.0
pip install supabase>=2.12.0
```

---

### "Table does not exist"

**Problem:** Database table missing

**Solution:**
- `legal_documents` - Should exist (601 docs)
- `court_events` - Should exist
- `communications_matrix` - May not exist yet (tool will handle gracefully)
- `action_items` - Phase 2 feature

If `legal_documents` or `court_events` are missing, check:
1. Supabase dashboard at https://supabase.com/dashboard
2. Verify table names match exactly
3. Check anon key has read permissions

---

### "Proxy parameter error"

**Problem:** Using old supabase version (2.3.0)

**Solution:** Already fixed in requirements.txt!
```bash
pip install --upgrade supabase>=2.12.0
```

---

### Claude Desktop doesn't show tools

**Problem:** Config file not found or malformed

**Solution:**
1. Verify config file location:
   - macOS/Linux: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Validate JSON syntax at https://jsonlint.com

3. Fully quit Claude Desktop (not just close window):
   - macOS: `Cmd+Q`
   - Windows: Right-click taskbar → Quit

4. Restart Claude Desktop

5. Look for 🔧 icon in chat interface

---

## 📊 Phase 1 vs Phase 2

### Phase 1 (Current - MVP)

✅ **Working:**
- search_documents (legal_documents table)
- get_timeline (court_events table)
- search_communications (graceful fallback if table missing)
- Basic motion outline generation

⏳ **Limited:**
- get_action_items (returns helpful message)
- generate_motion (template only, not PDF)

### Phase 2 (Future)

🎯 **Planned:**
- Full action_items table integration
- PDF generation for motions
- Communications table fully populated
- 3-server architecture (query/action/analysis)
- Redis caching
- Audit logging
- Rate limiting

---

## 🔐 Security Notes

**This is a localhost-only MVP.**

- ✅ Runs on your machine only
- ✅ No remote access
- ✅ Claude Desktop communicates via stdio
- ❌ No authentication (local trust model)
- ❌ No rate limiting (single user)
- ❌ No audit logging (Phase 2)

**For production (Phase 2):**
- Add authentication
- Implement rate limiting
- Add audit logging
- Deploy to secure server

---

## 📝 Development

### Run Tests

```bash
# Test Supabase connection
python3 -c "from server import get_supabase_client; get_supabase_client(); print('✓ Connected')"

# Test each tool (requires Claude API or Desktop)
# Use Claude Desktop with test prompts from "Usage Examples" section
```

### Enable Debug Logging

Edit `server.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### View Logs

Server logs to stdout. In Claude Desktop, check:
- macOS/Linux: `~/Library/Logs/Claude/mcp-server-aseagi.log`
- Windows: `%APPDATA%\Claude\logs\mcp-server-aseagi.log`

---

## 🎯 Architecture Alignment

This implementation follows **"Option 4 (Hybrid)"** from the MCP Architecture Assessment:

✅ **Week 1-2 MVP:** Unified server with 5 tools (current)

📅 **Phase 2 Split:**
- Query Server: search_documents, get_timeline, search_communications, get_action_items
- Action Server: generate_motion, create_action_item, upload_document
- Analysis Server: micro_analyze, macro_analyze, detect_violations

Code is structured for easy refactoring when ready to split.

---

## 🔗 Related Documentation

- MCP Protocol: https://modelcontextprotocol.io
- Supabase Docs: https://supabase.com/docs
- Claude Desktop: https://claude.ai/desktop

---

## 📄 License

Part of ASEAGI - Ashe Sanctuary of Empowerment AGI
Athena Guardian of Innocence Project

*For Ashe. For All Children.* ⚖️

*"When children speak, truth must roar louder than lies."*

---

## ✅ Checklist: Is It Working?

- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] .env file created with actual Supabase key
- [ ] Server starts without errors (`python3 server.py`)
- [ ] "✓ Supabase connection verified" message appears
- [ ] Claude Desktop config file updated
- [ ] Claude Desktop fully quit and restarted
- [ ] 🔧 Tools icon visible in Claude Desktop chat
- [ ] Test prompt works: "Search for documents about custody"

If all checked, you're ready! 🎉

---

**Last Updated:** November 2025
**Version:** 1.0.0 (MVP - Phase 1)
**Status:** Ready for Testing
