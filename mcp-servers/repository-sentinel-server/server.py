#!/usr/bin/env python3
"""
Code Repository Sentinel - MCP Server
======================================
Model Context Protocol server for querying code repository inventory

This MCP server exposes tools to query and manage code repository metadata,
allowing Claude Desktop to answer questions about your codebase inventory.

Tools:
1. list_repositories - List all repositories with optional filters
2. get_repository_details - Get detailed information about a specific repository
3. search_repositories - Search repositories by keywords
4. compare_repositories - Compare multiple repositories
5. get_repository_stats - Get statistics across all repositories
6. find_dependencies - Find which repositories use a specific dependency
7. get_repository_health - Get health assessment of repositories

Author: ASEAGI Team
Date: 2025-11-18
Version: 1.0.0
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
server = Server("repository-sentinel-server")

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

def format_repository(repo: Dict) -> str:
    """Format a single repository for display"""
    lines = []
    lines.append(f"📦 {repo.get('repository_name', 'Unknown')}")
    lines.append(f"   ID: {repo.get('repository_id')}")

    if repo.get('primary_language'):
        lines.append(f"   Language: {repo.get('primary_language')}")

    if repo.get('framework'):
        lines.append(f"   Framework: {repo.get('framework')}")

    if repo.get('total_lines_of_code'):
        lines.append(f"   Lines of Code: {repo.get('total_lines_of_code'):,}")

    if repo.get('total_files'):
        lines.append(f"   Files: {repo.get('total_files')}")

    if repo.get('current_status'):
        lines.append(f"   Status: {repo.get('current_status')}")

    if repo.get('code_quality_score') is not None:
        lines.append(f"   Quality Score: {repo.get('code_quality_score')}/100")

    if repo.get('repository_url'):
        lines.append(f"   URL: {repo.get('repository_url')}")

    return "\n".join(lines)

# ============================================================================
# Tool Definitions
# ============================================================================

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="list_repositories",
            description="""List all code repositories in the inventory with optional filters.

            Use this to:
            - See all tracked repositories
            - Filter by language, framework, status
            - Find repositories matching specific criteria
            - Get overview of code inventory

            Returns: List of repositories with key metadata.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "language": {
                        "type": "string",
                        "description": "Filter by primary language (Python, JavaScript, etc.)"
                    },
                    "framework": {
                        "type": "string",
                        "description": "Filter by framework (Streamlit, React, Django, etc.)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "archived", "deprecated", "experimental", "production"],
                        "description": "Filter by repository status"
                    },
                    "min_quality_score": {
                        "type": "integer",
                        "description": "Minimum code quality score (0-100)"
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
            name="get_repository_details",
            description="""Get detailed information about a specific repository.

            Use this to:
            - View complete repository metadata
            - See dependencies and language breakdown
            - Check git information
            - Review quality metrics

            Returns: Comprehensive repository information.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_id": {
                        "type": "string",
                        "description": "Repository ID (e.g., 'github-owner-repo')"
                    }
                },
                "required": ["repository_id"]
            }
        ),

        Tool(
            name="search_repositories",
            description="""Search repositories by keywords in name, description, or tags.

            Use this to:
            - Find repositories by name
            - Search by description keywords
            - Look for specific topics or tags
            - Fuzzy search across metadata

            Returns: Matching repositories.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),

        Tool(
            name="compare_repositories",
            description="""Compare multiple repositories side-by-side.

            Use this to:
            - Compare code size and complexity
            - Compare quality scores
            - Compare technology stacks
            - Analyze similarities and differences

            Returns: Comparison table of repositories.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of repository IDs to compare"
                    }
                },
                "required": ["repository_ids"]
            }
        ),

        Tool(
            name="get_repository_stats",
            description="""Get aggregate statistics across all repositories.

            Use this to:
            - See total number of repositories
            - Get breakdown by language/framework
            - Calculate total lines of code
            - View quality score distribution

            Returns: Statistical summary of entire code inventory.""",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="find_dependencies",
            description="""Find which repositories use a specific dependency.

            Use this to:
            - Track dependency usage across projects
            - Identify upgrade needs
            - Find security vulnerabilities
            - Analyze technology adoption

            Returns: List of repositories using the dependency.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "dependency_name": {
                        "type": "string",
                        "description": "Name of dependency (e.g., 'streamlit', 'react')"
                    }
                },
                "required": ["dependency_name"]
            }
        ),

        Tool(
            name="get_repository_health",
            description="""Get health assessment of repositories based on best practices.

            Use this to:
            - Identify repositories needing attention
            - See which repos lack tests/docs
            - Find stale repositories
            - Assess overall code health

            Returns: Health report with recommendations.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "min_health": {
                        "type": "string",
                        "enum": ["excellent", "good", "fair", "poor"],
                        "description": "Minimum health level to show"
                    }
                }
            }
        )
    ]

# ============================================================================
# Tool Implementations
# ============================================================================

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""

    try:
        if name == "list_repositories":
            return await list_repositories_impl(arguments)

        elif name == "get_repository_details":
            return await get_repository_details_impl(arguments)

        elif name == "search_repositories":
            return await search_repositories_impl(arguments)

        elif name == "compare_repositories":
            return await compare_repositories_impl(arguments)

        elif name == "get_repository_stats":
            return await get_repository_stats_impl(arguments)

        elif name == "find_dependencies":
            return await find_dependencies_impl(arguments)

        elif name == "get_repository_health":
            return await get_repository_health_impl(arguments)

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
# Tool: list_repositories
# ============================================================================

async def list_repositories_impl(args: Dict) -> List[TextContent]:
    """List repositories with optional filters"""

    language = args.get("language")
    framework = args.get("framework")
    status = args.get("status")
    min_quality = args.get("min_quality_score")
    limit = args.get("limit", 20)

    # Build query
    query = supabase.table("repositories").select("*")

    if language:
        query = query.ilike("primary_language", language)

    if framework:
        query = query.ilike("framework", framework)

    if status:
        query = query.eq("current_status", status)

    if min_quality:
        query = query.gte("code_quality_score", min_quality)

    # Order and limit
    query = query.order("last_modified_date", desc=True).limit(limit)

    # Execute
    result = query.execute()

    if not result.data:
        return [TextContent(
            type="text",
            text="No repositories found matching criteria."
        )]

    # Format results
    output = [f"Found {len(result.data)} repositories:\n"]

    for i, repo in enumerate(result.data, 1):
        output.append(f"\n{i}. {format_repository(repo)}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: get_repository_details
# ============================================================================

async def get_repository_details_impl(args: Dict) -> List[TextContent]:
    """Get detailed repository information"""

    repo_id = args.get("repository_id")

    # Query repository
    result = supabase.table("repositories")\
        .select("*")\
        .eq("repository_id", repo_id)\
        .single()\
        .execute()

    if not result.data:
        return [TextContent(
            type="text",
            text=f"Repository not found: {repo_id}"
        )]

    repo = result.data
    output = []

    # Basic info
    output.append("=" * 60)
    output.append(f"REPOSITORY: {repo.get('repository_name')}")
    output.append("=" * 60)
    output.append(f"\nID: {repo.get('repository_id')}")
    output.append(f"Type: {repo.get('repository_type', 'local')}")
    output.append(f"Status: {repo.get('current_status', 'unknown')}")

    if repo.get('repository_url'):
        output.append(f"URL: {repo.get('repository_url')}")

    if repo.get('local_path'):
        output.append(f"Path: {repo.get('local_path')}")

    # Description
    if repo.get('description'):
        output.append(f"\nDescription: {repo.get('description')}")

    # Technology stack
    output.append("\n--- Technology Stack ---")
    output.append(f"Primary Language: {repo.get('primary_language', 'Unknown')}")

    if repo.get('framework'):
        output.append(f"Framework: {repo.get('framework')}")

    # Language breakdown
    if repo.get('language_breakdown'):
        output.append("\nLanguage Breakdown:")
        for lang, lines in repo['language_breakdown'].items():
            output.append(f"  {lang}: {lines:,} lines")

    # Statistics
    output.append("\n--- Statistics ---")
    output.append(f"Total Files: {repo.get('total_files', 0):,}")
    output.append(f"Lines of Code: {repo.get('total_lines_of_code', 0):,}")

    if repo.get('total_commits'):
        output.append(f"Total Commits: {repo.get('total_commits'):,}")

    if repo.get('total_branches'):
        output.append(f"Total Branches: {repo.get('total_branches')}")

    # Git info
    if repo.get('latest_commit_hash'):
        output.append("\n--- Git Information ---")
        output.append(f"Latest Commit: {repo.get('latest_commit_hash')[:8]}")
        output.append(f"Commit Date: {safe_date_format(repo.get('latest_commit_date'))}")
        output.append(f"Message: {repo.get('latest_commit_message', 'N/A')}")
        output.append(f"Default Branch: {repo.get('default_branch', 'main')}")

    # Quality metrics
    output.append("\n--- Quality Metrics ---")
    output.append(f"Code Quality Score: {repo.get('code_quality_score', 0)}/100")
    output.append(f"Has README: {'✓' if repo.get('has_readme') else '✗'}")
    output.append(f"Has Tests: {'✓' if repo.get('has_tests') else '✗'}")
    output.append(f"Has CI/CD: {'✓' if repo.get('has_ci_cd') else '✗'}")
    output.append(f"Has Documentation: {'✓' if repo.get('has_documentation') else '✗'}")

    # Dependencies
    if repo.get('dependencies'):
        output.append("\n--- Dependencies ---")
        deps = repo['dependencies']
        for dep, version in list(deps.items())[:10]:
            output.append(f"  {dep}: {version}")
        if len(deps) > 10:
            output.append(f"  ... and {len(deps) - 10} more")

    # Dates
    output.append("\n--- Dates ---")
    if repo.get('first_commit_date'):
        output.append(f"First Commit: {safe_date_format(repo.get('first_commit_date'))}")
    output.append(f"Last Modified: {safe_date_format(repo.get('last_modified_date'))}")
    output.append(f"Last Scanned: {safe_date_format(repo.get('last_scanned_at'))}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: search_repositories
# ============================================================================

async def search_repositories_impl(args: Dict) -> List[TextContent]:
    """Search repositories by keywords"""

    query_text = args.get("query")
    limit = args.get("limit", 10)

    # Search in repository_name and description
    result = supabase.table("repositories")\
        .select("*")\
        .or_(f"repository_name.ilike.%{query_text}%,description.ilike.%{query_text}%")\
        .limit(limit)\
        .execute()

    if not result.data:
        return [TextContent(
            type="text",
            text=f"No repositories found matching '{query_text}'"
        )]

    output = [f"Found {len(result.data)} repositories matching '{query_text}':\n"]

    for i, repo in enumerate(result.data, 1):
        output.append(f"\n{i}. {format_repository(repo)}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: compare_repositories
# ============================================================================

async def compare_repositories_impl(args: Dict) -> List[TextContent]:
    """Compare multiple repositories"""

    repo_ids = args.get("repository_ids", [])

    if len(repo_ids) < 2:
        return [TextContent(
            type="text",
            text="Please provide at least 2 repository IDs to compare"
        )]

    # Fetch all repositories
    result = supabase.table("repositories")\
        .select("*")\
        .in_("repository_id", repo_ids)\
        .execute()

    if not result.data:
        return [TextContent(
            type="text",
            text="No repositories found with provided IDs"
        )]

    repos = result.data
    output = []
    output.append("=" * 80)
    output.append("REPOSITORY COMPARISON")
    output.append("=" * 80)

    # Comparison metrics
    metrics = [
        ('Repository Name', 'repository_name'),
        ('Language', 'primary_language'),
        ('Framework', 'framework'),
        ('Lines of Code', 'total_lines_of_code'),
        ('Total Files', 'total_files'),
        ('Total Commits', 'total_commits'),
        ('Quality Score', 'code_quality_score'),
        ('Has Tests', 'has_tests'),
        ('Has CI/CD', 'has_ci_cd'),
        ('Status', 'current_status'),
    ]

    for metric_name, metric_key in metrics:
        output.append(f"\n{metric_name}:")
        for repo in repos:
            value = repo.get(metric_key, 'N/A')
            if isinstance(value, bool):
                value = '✓' if value else '✗'
            elif isinstance(value, int):
                value = f"{value:,}"
            output.append(f"  {repo.get('repository_name')}: {value}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: get_repository_stats
# ============================================================================

async def get_repository_stats_impl(args: Dict) -> List[TextContent]:
    """Get aggregate statistics"""

    # Fetch all repositories
    result = supabase.table("repositories").select("*").execute()

    if not result.data:
        return [TextContent(
            type="text",
            text="No repositories in inventory"
        )]

    repos = result.data
    output = []
    output.append("=" * 60)
    output.append("CODE REPOSITORY INVENTORY STATISTICS")
    output.append("=" * 60)

    # Total repositories
    output.append(f"\nTotal Repositories: {len(repos)}")

    # By language
    languages = {}
    for repo in repos:
        lang = repo.get('primary_language', 'Unknown')
        languages[lang] = languages.get(lang, 0) + 1

    output.append("\nBy Language:")
    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        output.append(f"  {lang}: {count}")

    # By framework
    frameworks = {}
    for repo in repos:
        fw = repo.get('framework')
        if fw:
            frameworks[fw] = frameworks.get(fw, 0) + 1

    if frameworks:
        output.append("\nBy Framework:")
        for fw, count in sorted(frameworks.items(), key=lambda x: x[1], reverse=True):
            output.append(f"  {fw}: {count}")

    # Total lines of code
    total_loc = sum(repo.get('total_lines_of_code', 0) for repo in repos)
    output.append(f"\nTotal Lines of Code: {total_loc:,}")

    # Average quality score
    scores = [repo.get('code_quality_score', 0) for repo in repos if repo.get('code_quality_score') is not None]
    if scores:
        avg_score = sum(scores) / len(scores)
        output.append(f"Average Quality Score: {avg_score:.1f}/100")

    # Health indicators
    has_tests = sum(1 for repo in repos if repo.get('has_tests'))
    has_docs = sum(1 for repo in repos if repo.get('has_documentation'))
    has_cicd = sum(1 for repo in repos if repo.get('has_ci_cd'))

    output.append("\nBest Practices:")
    output.append(f"  With Tests: {has_tests}/{len(repos)} ({has_tests/len(repos)*100:.1f}%)")
    output.append(f"  With Documentation: {has_docs}/{len(repos)} ({has_docs/len(repos)*100:.1f}%)")
    output.append(f"  With CI/CD: {has_cicd}/{len(repos)} ({has_cicd/len(repos)*100:.1f}%)")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: find_dependencies
# ============================================================================

async def find_dependencies_impl(args: Dict) -> List[TextContent]:
    """Find repositories using a specific dependency"""

    dep_name = args.get("dependency_name")

    # Query repositories with this dependency
    result = supabase.table("repositories")\
        .select("repository_id, repository_name, dependencies")\
        .execute()

    matching_repos = []
    for repo in result.data:
        deps = repo.get('dependencies', {})
        if dep_name in deps:
            matching_repos.append({
                'name': repo.get('repository_name'),
                'id': repo.get('repository_id'),
                'version': deps[dep_name]
            })

    if not matching_repos:
        return [TextContent(
            type="text",
            text=f"No repositories found using dependency '{dep_name}'"
        )]

    output = [f"Found {len(matching_repos)} repositories using '{dep_name}':\n"]

    for i, repo in enumerate(matching_repos, 1):
        output.append(f"\n{i}. {repo['name']}")
        output.append(f"   ID: {repo['id']}")
        output.append(f"   Version: {repo['version']}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Tool: get_repository_health
# ============================================================================

async def get_repository_health_impl(args: Dict) -> List[TextContent]:
    """Get repository health assessment"""

    min_health = args.get("min_health")

    # Use the view
    result = supabase.table("v_repository_health").select("*").execute()

    if not result.data:
        return [TextContent(
            type="text",
            text="No repositories found"
        )]

    repos = result.data

    # Filter by health level if specified
    if min_health:
        health_order = {'excellent': 4, 'good': 3, 'fair': 2, 'poor': 1}
        min_level = health_order.get(min_health, 0)
        repos = [r for r in repos if health_order.get(r.get('health_status', 'poor'), 0) >= min_level]

    output = []
    output.append("=" * 60)
    output.append("REPOSITORY HEALTH REPORT")
    output.append("=" * 60)

    # Group by health status
    by_health = {}
    for repo in repos:
        status = repo.get('health_status', 'poor')
        if status not in by_health:
            by_health[status] = []
        by_health[status].append(repo)

    for health in ['excellent', 'good', 'fair', 'poor']:
        if health in by_health:
            repos_in_category = by_health[health]
            emoji = {'excellent': '🟢', 'good': '🟡', 'fair': '🟠', 'poor': '🔴'}
            output.append(f"\n{emoji[health]} {health.upper()} ({len(repos_in_category)} repos):")

            for repo in repos_in_category:
                output.append(f"\n  📦 {repo.get('repository_name')}")
                output.append(f"     Quality Score: {repo.get('code_quality_score', 0)}/100")

                issues = []
                if not repo.get('has_readme'):
                    issues.append("Missing README")
                if not repo.get('has_tests'):
                    issues.append("No tests")
                if not repo.get('has_ci_cd'):
                    issues.append("No CI/CD")
                if not repo.get('has_documentation'):
                    issues.append("No docs")
                if repo.get('has_vulnerabilities'):
                    issues.append(f"{repo.get('vulnerability_count', 0)} vulnerabilities")

                if issues:
                    output.append(f"     Issues: {', '.join(issues)}")

    return [TextContent(type="text", text="\n".join(output))]

# ============================================================================
# Resources and Prompts
# ============================================================================

@server.list_resources()
async def list_resources() -> List[Any]:
    """List available resources"""
    return []

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
