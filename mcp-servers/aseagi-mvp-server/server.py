#!/usr/bin/env python3
"""
ASEAGI MCP Server - MVP
Model Context Protocol server exposing ASEAGI case management tools to Claude

This is the MVP unified server. Will split into 3 specialized servers in Phase 2:
- Query Server (read-only)
- Action Server (read-write)
- Analysis Server (compute-heavy)

MVP Tools (5 core tools):
1. search_communications - Search texts/emails for contradictions
2. get_timeline - Get case event timeline
3. search_documents - Search all case documents
4. get_action_items - Get pending tasks and deadlines
5. generate_motion - Generate legal motion (placeholder for Phase 2)
"""

import asyncio
import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        ImageContent,
        EmbeddedResource,
        LoggingLevel
    )
except ImportError:
    print("ERROR: MCP SDK not installed")
    print("Install with: pip install mcp")
    exit(1)

try:
    from supabase import create_client, Client
except ImportError:
    print("ERROR: Supabase not installed")
    print("Install with: pip install supabase")
    exit(1)

# ============================================================================
# Configuration
# ============================================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set")
    print("Set them in .env file or environment variables")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize MCP server
server = Server("aseagi-mvp-server")

# ============================================================================
# Helper Functions
# ============================================================================

def safe_date_format(date_obj: Any) -> str:
    """Safely format date objects to strings"""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    if isinstance(date_obj, (date, datetime)):
        return date_obj.isoformat()
    return str(date_obj)

def format_results(results: List[Dict]) -> str:
    """Format database results for Claude"""
    if not results:
        return "No results found."

    formatted = []
    for i, row in enumerate(results, 1):
        formatted.append(f"\n--- Result {i} ---")
        for key, value in row.items():
            if value is not None:
                formatted.append(f"{key}: {value}")

    return "\n".join(formatted)

# ============================================================================
# TOOL 1: Search Communications
# ============================================================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="search_communications",
            description="""Search text messages, emails, and communications for specific content.

            Use this to:
            - Find contradictions between texts and sworn statements
            - Search for specific topics or keywords
            - Find evidence of lies or manipulation
            - Locate communications between specific people

            Returns: List of communications matching the search criteria with dates, participants, content, and truthfulness scores.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords to find in message content)"
                    },
                    "sender": {
                        "type": "string",
                        "description": "Optional: Filter by sender name"
                    },
                    "recipient": {
                        "type": "string",
                        "description": "Optional: Filter by recipient name"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional: Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional: End date (YYYY-MM-DD)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),

        Tool(
            name="get_timeline",
            description="""Get chronological timeline of case events over 2-3 years.

            Use this to:
            - Understand case history
            - See pattern of events
            - Find specific incidents
            - Prepare for hearings or motions

            Returns: List of events sorted by date with type, description, participants, and significance scores.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Optional: Start date (YYYY-MM-DD, default: 3 years ago)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional: End date (YYYY-MM-DD, default: today)"
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Filter by event types (court_hearing, incident, document_filed, etc.)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of events (default: 50)",
                        "default": 50
                    }
                }
            }
        ),

        Tool(
            name="search_documents",
            description="""Search all case documents (court filings, reports, records).

            Use this to:
            - Find specific documents
            - Search for evidence
            - Locate filings or reports
            - Review document history

            Returns: List of documents matching search with metadata, type, date, and content preview.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords to find in documents)"
                    },
                    "document_type": {
                        "type": "string",
                        "description": "Optional: Filter by document type (police_report, medical_report, court_filing, etc.)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Optional: Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "Optional: End date (YYYY-MM-DD)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),

        Tool(
            name="get_action_items",
            description="""Get list of pending action items, tasks, and deadlines.

            Use this to:
            - See what needs to be done
            - Check upcoming deadlines
            - Review suggested motions
            - Track case management tasks

            Returns: List of action items with due dates, priority, description, and suggested motion types.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "all"],
                        "description": "Filter by status (default: pending)",
                        "default": "pending"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["urgent", "high", "medium", "low", "all"],
                        "description": "Filter by priority"
                    },
                    "due_soon": {
                        "type": "boolean",
                        "description": "Only show items due within 7 days",
                        "default": False
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    }
                }
            }
        ),

        Tool(
            name="generate_motion",
            description="""Generate a legal motion with evidence and citations (PLACEHOLDER - Full implementation in Phase 2).

            Use this to:
            - Create motions for reconsideration, dismissal, etc.
            - Generate declarations
            - Prepare court filings

            Currently returns: Motion structure and evidence suggestions. Full PDF generation coming in Phase 2.

            Returns: Motion outline with factual background, legal argument, evidence list, and next steps.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "motion_type": {
                        "type": "string",
                        "enum": ["motion_for_reconsideration", "request_for_judicial_notice", "declaration", "response_to_ex_parte"],
                        "description": "Type of motion to generate"
                    },
                    "issue": {
                        "type": "string",
                        "description": "The issue or grounds for the motion"
                    },
                    "relief_requested": {
                        "type": "string",
                        "description": "What you're asking the court to do"
                    }
                },
                "required": ["motion_type", "issue"]
            }
        )
    ]

# ============================================================================
# TOOL IMPLEMENTATIONS
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "search_communications":
            return await search_communications_impl(arguments)

        elif name == "get_timeline":
            return await get_timeline_impl(arguments)

        elif name == "search_documents":
            return await search_documents_impl(arguments)

        elif name == "get_action_items":
            return await get_action_items_impl(arguments)

        elif name == "generate_motion":
            return await generate_motion_impl(arguments)

        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

# ============================================================================
# Tool: search_communications
# ============================================================================

async def search_communications_impl(args: Dict) -> List[TextContent]:
    """Search communications (texts, emails, calls)"""

    query = args.get("query")
    sender = args.get("sender")
    recipient = args.get("recipient")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    limit = args.get("limit", 20)

    # Build query
    db_query = supabase.table("communications").select("*")

    # Text search in content
    if query:
        db_query = db_query.ilike("content", f"%{query}%")

    # Filter by sender
    if sender:
        db_query = db_query.ilike("sender", f"%{sender}%")

    # Filter by recipient
    if recipient:
        db_query = db_query.ilike("recipient", f"%{recipient}%")

    # Date range
    if start_date:
        db_query = db_query.gte("sent_date", start_date)
    if end_date:
        db_query = db_query.lte("sent_date", end_date)

    # Order and limit
    db_query = db_query.order("sent_date", desc=True).limit(limit)

    # Execute query
    result = db_query.execute()

    if not result.data:
        return [TextContent(
            type="text",
            text=f"No communications found matching query: '{query}'"
        )]

    # Format results
    output = [f"Found {len(result.data)} communications:\n"]

    for i, comm in enumerate(result.data, 1):
        output.append(f"\n--- Communication {i} ---")
        output.append(f"Date: {safe_date_format(comm.get('sent_date'))}")
        output.append(f"From: {comm.get('sender', 'Unknown')}")
        output.append(f"To: {comm.get('recipient', 'Unknown')}")
        output.append(f"Type: {comm.get('communication_type', 'unknown')}")
        output.append(f"Content: {comm.get('content', '')[:200]}...")

        if comm.get('truthfulness_score'):
            output.append(f"Truth Score: {comm.get('truthfulness_score')}/100")

        if comm.get('contains_contradiction'):
            output.append(f"⚠️ Contains contradiction")

        if comm.get('contains_manipulation'):
            output.append(f"⚠️ Manipulation detected: {comm.get('manipulation_types')}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: get_timeline
# ============================================================================

async def get_timeline_impl(args: Dict) -> List[TextContent]:
    """Get case event timeline"""

    # Default: last 3 years
    end_date = args.get("end_date", datetime.now().date().isoformat())
    start_date = args.get("start_date", (datetime.now() - timedelta(days=3*365)).date().isoformat())
    event_types = args.get("event_types")
    limit = args.get("limit", 50)

    # Build query
    db_query = supabase.table("events").select("*")

    # Date range
    db_query = db_query.gte("event_date", start_date).lte("event_date", end_date)

    # Filter by event types
    if event_types:
        db_query = db_query.in_("event_type", event_types)

    # Order and limit
    db_query = db_query.order("event_date", desc=True).limit(limit)

    # Execute
    result = db_query.execute()

    if not result.data:
        return [TextContent(
            type="text",
            text=f"No events found between {start_date} and {end_date}"
        )]

    # Format timeline
    output = [f"Timeline: {len(result.data)} events from {start_date} to {end_date}\n"]

    for i, event in enumerate(result.data, 1):
        output.append(f"\n--- {event.get('event_date')} ---")
        output.append(f"Event: {event.get('event_title', 'Untitled')}")
        output.append(f"Type: {event.get('event_type', 'unknown')}")

        if event.get('event_description'):
            output.append(f"Description: {event.get('event_description')}")

        if event.get('significance_score'):
            output.append(f"Significance: {event.get('significance_score')}/100")

        if event.get('verified'):
            output.append("✓ Verified")
        elif event.get('contradicted'):
            output.append("⚠️ Contradicted")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: search_documents
# ============================================================================

async def search_documents_impl(args: Dict) -> List[TextContent]:
    """Search case documents"""

    query = args.get("query")
    document_type = args.get("document_type")
    start_date = args.get("start_date")
    end_date = args.get("end_date")
    limit = args.get("limit", 20)

    # Build query
    db_query = supabase.table("document_journal").select("*")

    # Search in filename or extracted metadata
    if query:
        db_query = db_query.or_(f"original_filename.ilike.%{query}%,extracted_metadata->>text.ilike.%{query}%")

    # Filter by document type
    if document_type:
        db_query = db_query.eq("document_type", document_type)

    # Date range
    if start_date:
        db_query = db_query.gte("date_logged", start_date)
    if end_date:
        db_query = db_query.lte("date_logged", end_date)

    # Order and limit
    db_query = db_query.order("date_logged", desc=True).limit(limit)

    # Execute
    result = db_query.execute()

    if not result.data:
        return [TextContent(
            type="text",
            text=f"No documents found matching: '{query}'"
        )]

    # Format results
    output = [f"Found {len(result.data)} documents:\n"]

    for i, doc in enumerate(result.data, 1):
        output.append(f"\n--- Document {i} ---")
        output.append(f"ID: {doc.get('journal_id')}")
        output.append(f"Filename: {doc.get('original_filename', 'Unknown')}")
        output.append(f"Type: {doc.get('document_type', 'unknown')}")
        output.append(f"Date: {safe_date_format(doc.get('date_logged'))}")
        output.append(f"Source: {doc.get('source_type', 'unknown')}")
        output.append(f"Status: {doc.get('queue_status', 'unknown')}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: get_action_items
# ============================================================================

async def get_action_items_impl(args: Dict) -> List[TextContent]:
    """Get pending action items"""

    status = args.get("status", "pending")
    priority = args.get("priority")
    due_soon = args.get("due_soon", False)
    limit = args.get("limit", 20)

    # Build query
    db_query = supabase.table("action_items").select("*")

    # Filter by status
    if status != "all":
        db_query = db_query.eq("status", status)

    # Filter by priority
    if priority and priority != "all":
        db_query = db_query.eq("priority", priority)

    # Due soon (within 7 days)
    if due_soon:
        seven_days_from_now = (datetime.now() + timedelta(days=7)).date().isoformat()
        db_query = db_query.lte("due_date", seven_days_from_now)

    # Order and limit
    db_query = db_query.order("due_date", desc=False).limit(limit)

    # Execute
    result = db_query.execute()

    if not result.data:
        return [TextContent(
            type="text",
            text="No action items found matching criteria"
        )]

    # Format results
    output = [f"Action Items ({len(result.data)}):\n"]

    for i, item in enumerate(result.data, 1):
        due_date = item.get('due_date')
        if due_date:
            days_until = (datetime.fromisoformat(due_date).date() - datetime.now().date()).days
            urgency = "🔴 OVERDUE" if days_until < 0 else f"📅 Due in {days_until} days"
        else:
            urgency = "No deadline"

        output.append(f"\n--- Item {i} ---")
        output.append(f"{urgency}")
        output.append(f"Title: {item.get('title')}")
        output.append(f"Priority: {item.get('priority', 'medium')}")
        output.append(f"Status: {item.get('status', 'pending')}")

        if item.get('description'):
            output.append(f"Description: {item.get('description')}")

        if item.get('suggested_motion_type'):
            output.append(f"Suggested Motion: {item.get('suggested_motion_type')}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: generate_motion (Placeholder)
# ============================================================================

async def generate_motion_impl(args: Dict) -> List[TextContent]:
    """Generate motion (placeholder for Phase 2)"""

    motion_type = args.get("motion_type")
    issue = args.get("issue")
    relief_requested = args.get("relief_requested", "")

    # This is a placeholder that provides structure
    # Full implementation with PDF generation in Phase 2

    output = [
        "MOTION OUTLINE (Placeholder - Full PDF generation in Phase 2)\n",
        f"\nMotion Type: {motion_type}",
        f"\nIssue: {issue}",
        f"\nRelief Requested: {relief_requested}",
        "\n\n=== MOTION STRUCTURE ===\n",
        "1. CAPTION",
        "   - Case name and number",
        "   - Court and department",
        "\n2. NOTICE OF MOTION",
        "   - What you're asking for",
        "   - Hearing date (if applicable)",
        "\n3. MEMORANDUM OF POINTS & AUTHORITIES",
        "   - Factual background",
        "   - Legal argument",
        "   - Case law citations",
        "\n4. DECLARATION IN SUPPORT",
        "   - Facts supporting the motion",
        "   - Evidence exhibits",
        "\n5. PROPOSED ORDER",
        "   - Draft order for judge to sign",
        "\n6. CERTIFICATE OF SERVICE",
        "   - Proof of service to all parties",
        "\n\n=== NEXT STEPS ===",
        "\n1. Review motion outline above",
        "2. Gather supporting evidence using search_documents and search_communications",
        "3. Full PDF generation will be available in Phase 2",
        "4. For now, use this outline to draft motion manually or wait for Phase 2"
    ]

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Resources
# ============================================================================

@server.list_resources()
async def list_resources() -> List[Any]:
    """List available resources"""
    return []

# ============================================================================
# Prompts
# ============================================================================

@server.list_prompts()
async def list_prompts() -> List[Any]:
    """List available prompts"""
    return []

# ============================================================================
# Main
# ============================================================================

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
