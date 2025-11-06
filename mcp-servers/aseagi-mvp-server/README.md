# ASEAGI MCP Server - MVP

**Model Context Protocol server for ASEAGI case management system**

This MCP server exposes ASEAGI tools to Claude Desktop, enabling Claude to directly query your case database, search communications, track actions, and more.

---

## Overview

**Phase:** MVP (Unified Server)
**Tools:** 5 core tools
**Status:** Ready for testing

This is the MVP implementation. In Phase 2, this will split into 3 specialized servers:
- Query Server (read-only)
- Action Server (read-write)
- Analysis Server (compute-heavy)

---

## Available Tools

### 1. `search_communications`
Search text messages, emails, and communications for specific content.

**Use cases:**
- Find contradictions between texts and sworn statements
- Search for evidence of lies or manipulation
- Locate communications about specific topics

**Example:**
```
Claude, search my communications for mentions of "visitation denial"
```

### 2. `get_timeline`
Get chronological timeline of case events over 2-3 years.

**Use cases:**
- Understand case history
- Find patterns of behavior
- Prepare for hearings

**Example:**
```
Claude, show me the timeline of court hearings from 2023
```

### 3. `search_documents`
Search all case documents (court filings, reports, records).

**Use cases:**
- Find specific documents
- Locate evidence
- Review filing history

**Example:**
```
Claude, find all police reports from January 2023
```

### 4. `get_action_items`
Get list of pending action items, tasks, and deadlines.

**Use cases:**
- See what needs to be done
- Check upcoming deadlines
- Track case management

**Example:**
```
Claude, what are my urgent action items due this week?
```

### 5. `generate_motion` (Placeholder)
Generate legal motion structure (full PDF generation in Phase 2).

**Use cases:**
- Create motion outlines
- Plan legal filings

**Example:**
```
Claude, generate a motion for reconsideration about Cal OES 2-925
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- Claude Desktop app
- Supabase database with ASEAGI schema deployed

### Step 1: Install Dependencies

```bash
cd /home/user/ASEAGI/mcp-servers/aseagi-mvp-server

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

Set your Supabase credentials:
```
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=your-actual-supabase-anon-key
```

### Step 3: Test the Server

```bash
# Test server startup
python server.py

# If no errors, the server is ready
# Press Ctrl+C to stop
```

---

## Claude Desktop Configuration

### Step 1: Locate Config File

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Add MCP Server

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "aseagi": {
      "command": "python",
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

**Important:** Replace paths and credentials with your actual values.

### Step 3: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Look for 🔌 icon indicating MCP server connected

---

## Usage Examples

### Example 1: Find Contradicting Text Messages

**You:**
> Claude, search my communications for messages about "visitation" sent by Father in January 2023

**Claude will:**
1. Call `search_communications` tool with parameters
2. Query Supabase communications table
3. Return matching messages with dates and content
4. Analyze for contradictions

### Example 2: Check Upcoming Deadlines

**You:**
> Claude, what do I need to do this week? Show me urgent action items.

**Claude will:**
1. Call `get_action_items` with `due_soon=true` and `priority=urgent`
2. Query action_items table
3. Return list sorted by due date
4. Suggest next steps

### Example 3: Search for Evidence

**You:**
> Claude, find the police report from the incident on 2023-01-15

**Claude will:**
1. Call `search_documents` with date filter
2. Query document_journal and police_reports tables
3. Return matching documents
4. Show metadata and excerpts

### Example 4: Review Case Timeline

**You:**
> Claude, show me all court hearings from 2023 to present

**Claude will:**
1. Call `get_timeline` with date range and event_type filter
2. Query events table
3. Return chronological list
4. Highlight significant events

### Example 5: Plan a Motion

**You:**
> Claude, I need to file a motion for reconsideration because the social worker never verified Cal OES 2-925 pickup

**Claude will:**
1. Call `generate_motion` with motion_type and issue
2. Return structured motion outline
3. Suggest evidence to gather (via search tools)
4. Provide next steps

---

## Troubleshooting

### Server Won't Start

**Error:** `SUPABASE_URL and SUPABASE_KEY must be set`

**Solution:** Check your .env file has correct credentials

---

**Error:** `ModuleNotFoundError: No module named 'mcp'`

**Solution:** Install requirements:
```bash
pip install -r requirements.txt
```

---

### Claude Can't Connect

**Error:** Server not showing in Claude Desktop

**Solution:**
1. Check claude_desktop_config.json syntax (valid JSON)
2. Verify file paths are absolute (not relative)
3. Restart Claude Desktop completely
4. Check Claude Desktop logs

---

### No Results Returned

**Error:** Tools return "No results found"

**Solution:**
1. Verify Supabase tables exist (run schema SQL)
2. Check Supabase credentials have correct permissions
3. Verify data exists in tables
4. Try querying Supabase directly to confirm

---

## Development

### Project Structure

```
aseagi-mvp-server/
├── server.py          # Main MCP server implementation
├── requirements.txt   # Python dependencies
├── .env.example       # Example environment variables
├── .env              # Your actual credentials (git-ignored)
└── README.md         # This file
```

### Adding New Tools

To add a new tool:

1. Add tool definition in `list_tools()`:
```python
Tool(
    name="your_tool_name",
    description="What the tool does",
    inputSchema={...}
)
```

2. Implement handler in `call_tool()`:
```python
elif name == "your_tool_name":
    return await your_tool_impl(arguments)
```

3. Create implementation function:
```python
async def your_tool_impl(args: Dict) -> List[TextContent]:
    # Your logic here
    return [TextContent(type="text", text="Result")]
```

---

## Roadmap

### Phase 1: MVP (✅ Current)
- [x] 5 core tools implemented
- [x] Supabase integration
- [x] Claude Desktop configuration
- [ ] User testing

### Phase 2: Split into 3 Servers (Week 3-4)
- [ ] Query Server (read-only, 12 tools)
- [ ] Action Server (read-write, 10 tools)
- [ ] Analysis Server (compute-heavy, 10 tools)
- [ ] Full motion generation (PDF output)
- [ ] Advanced security (RLS, audit logging)

### Phase 3: Production (Week 5-6)
- [ ] Docker deployment
- [ ] Monitoring and logging
- [ ] Performance optimization
- [ ] Documentation

---

## Security Notes

**Current (MVP):**
- Uses Supabase anon key (read-only safe)
- Credentials in environment variables
- No authentication layer (assumes trusted Claude Desktop)

**Future (Phase 2):**
- Separate database users per server
- Row-level security policies
- Audit logging for all mutations
- Rate limiting
- API key authentication

---

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review MCP documentation: https://modelcontextprotocol.io
3. Check Supabase dashboard for data verification

---

## License

For Ashe. For Justice. For All Children. 🛡️
