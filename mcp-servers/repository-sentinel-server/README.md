# Repository Sentinel MCP Server

**Model Context Protocol server for querying code repository inventory**

This MCP server allows Claude Desktop to query and analyze your code repository inventory, providing insights about all your codebases in one place.

---

## Available Tools

### 1. `list_repositories`
List all repositories with optional filters.

**Example:**
```
Claude, list all Python repositories
Claude, show me all active repositories with quality score above 80
```

### 2. `get_repository_details`
Get detailed information about a specific repository.

**Example:**
```
Claude, show me details for the ASEAGI repository
Claude, what are the dependencies in github-owner-repo?
```

### 3. `search_repositories`
Search repositories by keywords.

**Example:**
```
Claude, search for repositories related to "dashboard"
Claude, find repos containing "legal" in the name
```

### 4. `compare_repositories`
Compare multiple repositories side-by-side.

**Example:**
```
Claude, compare ASEAGI with my other Python projects
```

### 5. `get_repository_stats`
Get aggregate statistics across all repositories.

**Example:**
```
Claude, show me statistics for all my repositories
Claude, what's the total lines of code across all projects?
```

### 6. `find_dependencies`
Find which repositories use a specific dependency.

**Example:**
```
Claude, which repositories use Streamlit?
Claude, find all projects using React version 18
```

### 7. `get_repository_health`
Get health assessment based on best practices.

**Example:**
```
Claude, which repositories need attention?
Claude, show me repos with poor health status
```

---

## Installation

### Step 1: Install Dependencies

```bash
cd /home/user/ASEAGI/mcp-servers/repository-sentinel-server
pip install -r requirements.txt
```

### Step 2: Configure Claude Desktop

Add to your `claude_desktop_config.json`:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

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

### Step 3: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. Look for 🔌 icon indicating MCP server connected

---

## Usage Examples

### Example 1: Inventory Overview

**You:**
> Claude, how many code repositories do I have and what languages are they in?

**Claude will:**
1. Call `get_repository_stats`
2. Show total count and language breakdown
3. Provide insights about your code inventory

### Example 2: Find Specific Technology

**You:**
> Claude, which of my projects use Streamlit?

**Claude will:**
1. Call `find_dependencies` with "streamlit"
2. List all repositories using Streamlit
3. Show versions being used

### Example 3: Health Check

**You:**
> Claude, which of my repositories need tests or documentation?

**Claude will:**
1. Call `get_repository_health`
2. Identify repositories lacking best practices
3. Provide recommendations

### Example 4: Compare Projects

**You:**
> Claude, compare the ASEAGI project with my other legal tech repos

**Claude will:**
1. Call `search_repositories` to find legal repos
2. Call `compare_repositories` to compare them
3. Show side-by-side comparison

---

## Troubleshooting

### Server won't start

**Check:**
- Supabase URL and KEY are set in config
- `repositories` table exists in Supabase
- Python version is 3.10+

### No results returned

**Check:**
- Repository scanner has been run at least once
- Data exists in Supabase `repositories` table
- Database schema is up to date

---

## Related Tools

- **Repository Scanner:** `/home/user/ASEAGI/scanners/repository_scanner.py`
- **Sentinel Dashboard:** http://localhost:8506 (when running)
- **Database Schema:** `/home/user/ASEAGI/database/migrations/005_code_repository_sentinel_schema.sql`

---

**For Ashe. For Justice. For All Children.** 🛡️
