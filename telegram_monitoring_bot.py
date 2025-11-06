#!/usr/bin/env python3
"""
Global Project Monitoring Bot for Telegram
Monitor GitHub repos, n8n workflows, Qdrant DB, Twelve Labs
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
import json
from typing import Dict, Any, List

# Telegram imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        CallbackQueryHandler,
        MessageHandler,
        ContextTypes,
        filters
    )
except ImportError:
    print("❌ Install: pip install python-telegram-bot")
    sys.exit(1)

# API clients
try:
    import requests
    from github import Github
except ImportError:
    print("❌ Install: pip install requests PyGithub")
    sys.exit(1)

# Load credentials
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_MONITORING_BOT_TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPO', 'dondada876/ASEAGI')
N8N_API_URL = os.environ.get('N8N_API_URL')
N8N_API_KEY = os.environ.get('N8N_API_KEY')
QDRANT_URL = os.environ.get('QDRANT_URL')
QDRANT_API_KEY = os.environ.get('QDRANT_API_KEY')
TWELVE_LABS_API_KEY = os.environ.get('TWELVE_LABS_API_KEY')

# Fallback to secrets
if not TELEGRAM_BOT_TOKEN:
    try:
        import toml
        secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            TELEGRAM_BOT_TOKEN = secrets.get('TELEGRAM_MONITORING_BOT_TOKEN')
            GITHUB_TOKEN = secrets.get('GITHUB_TOKEN')
            N8N_API_URL = secrets.get('N8N_API_URL')
            N8N_API_KEY = secrets.get('N8N_API_KEY')
            QDRANT_URL = secrets.get('QDRANT_URL')
            QDRANT_API_KEY = secrets.get('QDRANT_API_KEY')
            TWELVE_LABS_API_KEY = secrets.get('TWELVE_LABS_API_KEY')
    except:
        pass

# Initialize clients
github_client = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None


# ============================================================================
# GITHUB MONITORING
# ============================================================================

async def get_github_status(repo_name: str = GITHUB_REPO) -> Dict[str, Any]:
    """Get GitHub repository status"""
    try:
        if not github_client:
            return {"error": "GitHub token not configured"}

        repo = github_client.get_repo(repo_name)

        # Get recent commits (last 24 hours)
        since = datetime.now() - timedelta(hours=24)
        commits = list(repo.get_commits(since=since))

        # Get open issues and PRs
        open_issues = repo.get_issues(state='open')
        open_prs = repo.get_pulls(state='open')

        # Get latest workflow runs
        workflows = repo.get_workflow_runs()
        latest_runs = list(workflows[:5])

        return {
            "repo": repo.full_name,
            "stars": repo.stargazers_count,
            "watchers": repo.watchers_count,
            "forks": repo.forks_count,
            "open_issues": open_issues.totalCount,
            "open_prs": open_prs.totalCount,
            "recent_commits": len(commits),
            "latest_commit": {
                "message": commits[0].commit.message if commits else "No recent commits",
                "author": commits[0].commit.author.name if commits else "N/A",
                "date": commits[0].commit.author.date.isoformat() if commits else "N/A"
            },
            "workflow_runs": [
                {
                    "name": run.name,
                    "status": run.status,
                    "conclusion": run.conclusion,
                    "created_at": run.created_at.isoformat()
                }
                for run in latest_runs
            ]
        }
    except Exception as e:
        return {"error": str(e)}


async def get_github_commits(repo_name: str = GITHUB_REPO, count: int = 10) -> List[Dict]:
    """Get recent commits"""
    try:
        if not github_client:
            return []

        repo = github_client.get_repo(repo_name)
        commits = list(repo.get_commits()[:count])

        return [
            {
                "sha": commit.sha[:7],
                "message": commit.commit.message.split('\n')[0],
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.strftime("%Y-%m-%d %H:%M")
            }
            for commit in commits
        ]
    except Exception as e:
        return [{"error": str(e)}]


async def get_github_prs(repo_name: str = GITHUB_REPO) -> List[Dict]:
    """Get open pull requests"""
    try:
        if not github_client:
            return []

        repo = github_client.get_repo(repo_name)
        prs = list(repo.get_pulls(state='open'))

        return [
            {
                "number": pr.number,
                "title": pr.title,
                "author": pr.user.login,
                "created_at": pr.created_at.strftime("%Y-%m-%d %H:%M"),
                "url": pr.html_url
            }
            for pr in prs
        ]
    except Exception as e:
        return [{"error": str(e)}]


# ============================================================================
# N8N MONITORING
# ============================================================================

async def get_n8n_status() -> Dict[str, Any]:
    """Get n8n instance status"""
    try:
        if not N8N_API_URL or not N8N_API_KEY:
            return {"error": "n8n credentials not configured"}

        headers = {"X-N8N-API-KEY": N8N_API_KEY}

        # Get workflows
        workflows_response = requests.get(
            f"{N8N_API_URL}/workflows",
            headers=headers,
            timeout=10
        )
        workflows = workflows_response.json()

        # Get recent executions
        executions_response = requests.get(
            f"{N8N_API_URL}/executions",
            headers=headers,
            params={"limit": 10},
            timeout=10
        )
        executions = executions_response.json()

        active_workflows = [w for w in workflows.get('data', []) if w.get('active')]
        failed_executions = [e for e in executions.get('data', []) if e.get('status') == 'error']

        return {
            "total_workflows": len(workflows.get('data', [])),
            "active_workflows": len(active_workflows),
            "recent_executions": len(executions.get('data', [])),
            "failed_executions": len(failed_executions),
            "workflows": [
                {
                    "name": w.get('name'),
                    "active": w.get('active'),
                    "id": w.get('id')
                }
                for w in workflows.get('data', [])[:5]
            ],
            "recent_failures": [
                {
                    "workflow": e.get('workflowData', {}).get('name', 'Unknown'),
                    "error": e.get('error', 'Unknown error'),
                    "time": e.get('stoppedAt', 'N/A')
                }
                for e in failed_executions[:3]
            ]
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# QDRANT MONITORING
# ============================================================================

async def get_qdrant_status() -> Dict[str, Any]:
    """Get Qdrant vector database status"""
    try:
        if not QDRANT_URL:
            return {"error": "Qdrant URL not configured"}

        headers = {}
        if QDRANT_API_KEY:
            headers["api-key"] = QDRANT_API_KEY

        # Get collections
        collections_response = requests.get(
            f"{QDRANT_URL}/collections",
            headers=headers,
            timeout=10
        )
        collections = collections_response.json()

        collection_details = []
        for collection in collections.get('result', {}).get('collections', []):
            name = collection.get('name')

            # Get collection info
            info_response = requests.get(
                f"{QDRANT_URL}/collections/{name}",
                headers=headers,
                timeout=10
            )
            info = info_response.json()

            collection_details.append({
                "name": name,
                "vectors_count": info.get('result', {}).get('vectors_count', 0),
                "points_count": info.get('result', {}).get('points_count', 0),
                "status": info.get('result', {}).get('status', 'unknown')
            })

        return {
            "total_collections": len(collection_details),
            "collections": collection_details,
            "total_vectors": sum(c['vectors_count'] for c in collection_details)
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# TWELVE LABS MONITORING
# ============================================================================

async def get_twelve_labs_status() -> Dict[str, Any]:
    """Get Twelve Labs video AI status"""
    try:
        if not TWELVE_LABS_API_KEY:
            return {"error": "Twelve Labs API key not configured"}

        headers = {"x-api-key": TWELVE_LABS_API_KEY}

        # Get indexes
        indexes_response = requests.get(
            "https://api.twelvelabs.io/v1.2/indexes",
            headers=headers,
            timeout=10
        )
        indexes = indexes_response.json()

        # Get recent tasks
        tasks_response = requests.get(
            "https://api.twelvelabs.io/v1.2/tasks",
            headers=headers,
            params={"page_limit": 10},
            timeout=10
        )
        tasks = tasks_response.json()

        return {
            "total_indexes": len(indexes.get('data', [])),
            "indexes": [
                {
                    "id": idx.get('_id'),
                    "name": idx.get('index_name'),
                    "videos": idx.get('video_count', 0),
                    "duration": idx.get('total_duration', 0)
                }
                for idx in indexes.get('data', [])
            ],
            "recent_tasks": [
                {
                    "id": task.get('_id'),
                    "status": task.get('status'),
                    "type": task.get('type'),
                    "created_at": task.get('created_at')
                }
                for task in tasks.get('data', [])[:5]
            ]
        }
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# TELEGRAM BOT COMMANDS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Full Status", callback_data='status_all'),
            InlineKeyboardButton("🔄 GitHub", callback_data='status_github')
        ],
        [
            InlineKeyboardButton("⚙️ n8n", callback_data='status_n8n'),
            InlineKeyboardButton("🗄️ Qdrant", callback_data='status_qdrant')
        ],
        [
            InlineKeyboardButton("🎥 Twelve Labs", callback_data='status_twelve'),
            InlineKeyboardButton("📝 Recent Commits", callback_data='github_commits')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🤖 **Global Project Monitor**\n\n"
        "I monitor your entire tech stack:\n"
        "• GitHub repos\n"
        "• n8n workflows\n"
        "• Qdrant vector DB\n"
        "• Twelve Labs video AI\n\n"
        "Choose what to check:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get overall status"""
    await update.message.reply_text("⏳ Fetching status from all services...")

    # Get all statuses
    github_status = await get_github_status()
    n8n_status = await get_n8n_status()
    qdrant_status = await get_qdrant_status()
    twelve_status = await get_twelve_labs_status()

    # Build message
    message = "📊 **Global System Status**\n\n"

    # GitHub
    message += "**📦 GitHub**\n"
    if "error" in github_status:
        message += f"❌ Error: {github_status['error']}\n"
    else:
        message += f"• Repo: {github_status['repo']}\n"
        message += f"• ⭐ Stars: {github_status['stars']}\n"
        message += f"• 🍴 Forks: {github_status['forks']}\n"
        message += f"• 📝 Open Issues: {github_status['open_issues']}\n"
        message += f"• 🔀 Open PRs: {github_status['open_prs']}\n"
        message += f"• 📅 Recent Commits (24h): {github_status['recent_commits']}\n"

    message += "\n**⚙️ n8n Workflows**\n"
    if "error" in n8n_status:
        message += f"❌ Error: {n8n_status['error']}\n"
    else:
        message += f"• Total Workflows: {n8n_status['total_workflows']}\n"
        message += f"• Active: {n8n_status['active_workflows']}\n"
        message += f"• Recent Executions: {n8n_status['recent_executions']}\n"
        message += f"• Failed: {n8n_status['failed_executions']}\n"

    message += "\n**🗄️ Qdrant Vector DB**\n"
    if "error" in qdrant_status:
        message += f"❌ Error: {qdrant_status['error']}\n"
    else:
        message += f"• Collections: {qdrant_status['total_collections']}\n"
        message += f"• Total Vectors: {qdrant_status['total_vectors']}\n"

    message += "\n**🎥 Twelve Labs**\n"
    if "error" in twelve_status:
        message += f"❌ Error: {twelve_status['error']}\n"
    else:
        message += f"• Indexes: {twelve_status['total_indexes']}\n"
        message += f"• Recent Tasks: {len(twelve_status['recent_tasks'])}\n"

    message += f"\n⏰ Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    await update.message.reply_text(message, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()

    action = query.data

    if action == 'status_all':
        await query.message.reply_text("⏳ Fetching complete status...")
        # Reuse status_command logic
        await status_command(update, context)

    elif action == 'status_github':
        await query.message.reply_text("⏳ Checking GitHub...")
        github_status = await get_github_status()

        if "error" in github_status:
            await query.message.reply_text(f"❌ Error: {github_status['error']}")
            return

        message = f"**📦 GitHub: {github_status['repo']}**\n\n"
        message += f"⭐ **Stars:** {github_status['stars']}\n"
        message += f"👀 **Watchers:** {github_status['watchers']}\n"
        message += f"🍴 **Forks:** {github_status['forks']}\n"
        message += f"🐛 **Open Issues:** {github_status['open_issues']}\n"
        message += f"🔀 **Open PRs:** {github_status['open_prs']}\n"
        message += f"📝 **Recent Commits (24h):** {github_status['recent_commits']}\n\n"

        message += "**Latest Commit:**\n"
        message += f"• {github_status['latest_commit']['message']}\n"
        message += f"• By: {github_status['latest_commit']['author']}\n"
        message += f"• Date: {github_status['latest_commit']['date']}\n"

        await query.message.reply_text(message, parse_mode='Markdown')

    elif action == 'status_n8n':
        await query.message.reply_text("⏳ Checking n8n...")
        n8n_status = await get_n8n_status()

        if "error" in n8n_status:
            await query.message.reply_text(f"❌ Error: {n8n_status['error']}")
            return

        message = "**⚙️ n8n Workflows**\n\n"
        message += f"📊 **Total Workflows:** {n8n_status['total_workflows']}\n"
        message += f"✅ **Active:** {n8n_status['active_workflows']}\n"
        message += f"🔄 **Recent Executions:** {n8n_status['recent_executions']}\n"
        message += f"❌ **Failed:** {n8n_status['failed_executions']}\n\n"

        message += "**Active Workflows:**\n"
        for workflow in n8n_status['workflows']:
            status_icon = "✅" if workflow['active'] else "⏸️"
            message += f"• {status_icon} {workflow['name']}\n"

        if n8n_status['recent_failures']:
            message += "\n**Recent Failures:**\n"
            for failure in n8n_status['recent_failures']:
                message += f"• {failure['workflow']}\n"
                message += f"  Error: {failure['error'][:50]}...\n"

        await query.message.reply_text(message, parse_mode='Markdown')

    elif action == 'status_qdrant':
        await query.message.reply_text("⏳ Checking Qdrant...")
        qdrant_status = await get_qdrant_status()

        if "error" in qdrant_status:
            await query.message.reply_text(f"❌ Error: {qdrant_status['error']}")
            return

        message = "**🗄️ Qdrant Vector Database**\n\n"
        message += f"📦 **Collections:** {qdrant_status['total_collections']}\n"
        message += f"🔢 **Total Vectors:** {qdrant_status['total_vectors']:,}\n\n"

        message += "**Collections:**\n"
        for collection in qdrant_status['collections']:
            message += f"• {collection['name']}\n"
            message += f"  Vectors: {collection['vectors_count']:,}\n"
            message += f"  Status: {collection['status']}\n"

        await query.message.reply_text(message, parse_mode='Markdown')

    elif action == 'status_twelve':
        await query.message.reply_text("⏳ Checking Twelve Labs...")
        twelve_status = await get_twelve_labs_status()

        if "error" in twelve_status:
            await query.message.reply_text(f"❌ Error: {twelve_status['error']}")
            return

        message = "**🎥 Twelve Labs Video AI**\n\n"
        message += f"📚 **Indexes:** {twelve_status['total_indexes']}\n\n"

        message += "**Video Indexes:**\n"
        for idx in twelve_status['indexes']:
            message += f"• {idx['name']}\n"
            message += f"  Videos: {idx['videos']}\n"
            message += f"  Duration: {idx['duration']}s\n"

        if twelve_status['recent_tasks']:
            message += "\n**Recent Tasks:**\n"
            for task in twelve_status['recent_tasks']:
                status_icon = {"ready": "✅", "processing": "⏳", "failed": "❌"}.get(task['status'], "❓")
                message += f"• {status_icon} {task['type']} - {task['status']}\n"

        await query.message.reply_text(message, parse_mode='Markdown')

    elif action == 'github_commits':
        await query.message.reply_text("⏳ Fetching recent commits...")
        commits = await get_github_commits(count=10)

        if commits and "error" in commits[0]:
            await query.message.reply_text(f"❌ Error: {commits[0]['error']}")
            return

        message = "**📝 Recent Commits**\n\n"
        for commit in commits:
            message += f"• `{commit['sha']}` {commit['message']}\n"
            message += f"  By: {commit['author']} • {commit['date']}\n\n"

        await query.message.reply_text(message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    message = (
        "🤖 **Monitoring Bot Commands**\n\n"
        "/start - Show main menu\n"
        "/status - Get full system status\n"
        "/github - GitHub status\n"
        "/n8n - n8n workflows status\n"
        "/qdrant - Qdrant DB status\n"
        "/twelve - Twelve Labs status\n"
        "/commits - Recent GitHub commits\n"
        "/prs - Open pull requests\n"
        "/help - This message\n\n"
        "Use the buttons for quick access!"
    )
    await update.message.reply_text(message, parse_mode='Markdown')


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_MONITORING_BOT_TOKEN not set!")
        print("\nSet it in your environment:")
        print("  export TELEGRAM_MONITORING_BOT_TOKEN='your-bot-token'")
        print("\nOr add to .streamlit/secrets.toml")
        sys.exit(1)

    print("🤖 Starting Global Monitoring Bot...")
    print(f"📡 GitHub: {'✅' if GITHUB_TOKEN else '❌'}")
    print(f"⚙️ n8n: {'✅' if N8N_API_URL else '❌'}")
    print(f"🗄️ Qdrant: {'✅' if QDRANT_URL else '❌'}")
    print(f"🎥 Twelve Labs: {'✅' if TWELVE_LABS_API_KEY else '❌'}")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    # Start bot
    print("✅ Bot is running! Press Ctrl+C to stop.")
    print("📱 Open Telegram and search for your bot.")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
