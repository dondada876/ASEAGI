"""
ASEAGI Telegram Bot
===================

Telegram bot client for ASEAGI case management system.

This bot receives commands from Telegram and calls the FastAPI endpoints
to retrieve data from the ASEAGI system.

Supported Commands:
    /start - Welcome message
    /help - Show available commands
    /search <query> - Search communications
    /timeline [days] - Show case timeline
    /actions - Show pending action items
    /violations - Show detected violations
    /deadline - Show upcoming deadlines
    /report - Daily summary report
    /hearing [id] - Show hearing information
    /motion <type> <issue> - Generate motion outline
"""

import os
import logging
from typing import Optional
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN must be set")


# ============================================================================
# Helper Functions
# ============================================================================

def call_api(endpoint: str, method: str = "GET", json_data: dict = None, params: dict = None) -> dict:
    """Call FastAPI endpoint and return response"""
    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=json_data, params=params, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(f"API call failed: {e}")
        return {
            "success": False,
            "message": "Failed to connect to ASEAGI system",
            "error": str(e)
        }


def format_response(response: dict) -> str:
    """Format API response for Telegram message"""
    if not response.get("success"):
        return f"❌ Error: {response.get('error', 'Unknown error')}"

    message = f"✅ {response['message']}\n\n"

    # Add data if present
    data = response.get("data", {})

    if "results" in data and data["results"]:
        message += "Results:\n"
        for i, item in enumerate(data["results"][:10], 1):  # Limit to 10 items
            message += f"\n{i}. "

            # Format based on item type
            if "title" in item:
                message += f"{item['title']}"
                if "due_date" in item:
                    message += f" (Due: {item['due_date']})"
                if "priority" in item:
                    message += f" [{item['priority'].upper()}]"

            elif "type" in item and "date" in item:
                message += f"{item['date']} - {item['type']}: {item.get('title', 'Event')}"

            elif "from" in item:
                message += f"{item['from']} → {item['to']} ({item['date'][:10]})"
                if item.get("has_contradictions"):
                    message += " ⚠️ CONTRADICTION"
                message += f"\n   {item.get('content', '')[:100]}"

            else:
                message += str(item)

        # Show if there are more results
        total = data.get("count", len(data["results"]))
        if total > 10:
            message += f"\n\n... and {total - 10} more"

    return message


# ============================================================================
# Command Handlers
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🛡️ **ASEAGI Case Management System**

Welcome! This bot provides access to your case data.

Available Commands:
/help - Show this message
/search <query> - Search communications
/timeline [days] - Case timeline
/actions - Pending action items
/violations - Detected violations
/deadline - Upcoming deadlines
/report - Daily summary
/hearing [id] - Hearing information
/motion <type> <issue> - Generate motion

For Ashe. For Justice. For All Children. 🛡️
    """
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
**ASEAGI Bot Commands**

📱 **Search & Query**
/search <query> - Search communications for specific content
   Example: `/search visitation denial`

📅 **Timeline**
/timeline [days] - Show case events (default 30 days)
   Example: `/timeline 60`

✅ **Action Items**
/actions - Show pending action items
/deadline - Show upcoming deadlines (next 7 days)

⚖️ **Legal**
/violations - Show detected legal violations
/hearing [id] - Show upcoming hearings or specific hearing
/motion <type> <issue> - Generate motion outline
   Example: `/motion reconsideration "Cal OES 2-925 not verified"`

📊 **Reports**
/report - Daily summary report

Need help? Contact your legal team.
    """
    await update.message.reply_text(help_message)


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /search command"""
    if not context.args:
        await update.message.reply_text("Usage: /search <query>\nExample: /search visitation denial")
        return

    query = " ".join(context.args)
    await update.message.reply_text(f"🔍 Searching for: {query}...")

    response = call_api(
        "/telegram/search",
        method="POST",
        json_data={"query": query, "limit": 10}
    )

    formatted = format_response(response)
    await update.message.reply_text(formatted)


async def timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /timeline command"""
    days = 30
    if context.args:
        try:
            days = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid number of days. Using default: 30")

    await update.message.reply_text(f"📅 Getting timeline for last {days} days...")

    response = call_api("/telegram/timeline", params={"days": days})

    formatted = format_response(response)
    await update.message.reply_text(formatted)


async def actions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /actions command"""
    await update.message.reply_text("✅ Getting pending action items...")

    priority = None
    due_soon = False

    if context.args:
        arg = context.args[0].lower()
        if arg in ["urgent", "high", "medium", "low"]:
            priority = arg
        elif arg == "due_soon":
            due_soon = True

    params = {}
    if priority:
        params["priority"] = priority
    if due_soon:
        params["due_soon"] = "true"

    response = call_api("/telegram/actions", params=params)

    formatted = format_response(response)
    await update.message.reply_text(formatted)


async def violations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /violations command"""
    await update.message.reply_text("⚖️ Getting detected violations...")

    params = {}
    if context.args:
        arg = context.args[0].lower()
        if arg in ["critical", "high", "medium", "low"]:
            params["severity"] = arg
        else:
            params["violation_type"] = arg

    response = call_api("/telegram/violations", params=params)

    formatted = format_response(response)
    await update.message.reply_text(formatted)


async def deadline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /deadline command"""
    await update.message.reply_text("⚠️ Checking upcoming deadlines...")

    response = call_api("/telegram/deadline")

    formatted = format_response(response)
    await update.message.reply_text(formatted)


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /report command"""
    await update.message.reply_text("📊 Generating daily report...")

    response = call_api("/telegram/report")

    if response.get("success"):
        data = response.get("data", {})

        report = f"📊 **Daily Report - {data.get('date')}**\n\n"

        # Urgent actions
        urgent = data.get("urgent_actions", [])
        if urgent:
            report += f"🚨 **{len(urgent)} Urgent Actions:**\n"
            for item in urgent[:5]:
                report += f"  • {item['title']} (Due: {item['due_date']})\n"
            report += "\n"

        # Upcoming deadlines
        deadlines = data.get("upcoming_deadlines", [])
        if deadlines:
            report += f"⚠️ **{len(deadlines)} Upcoming Deadlines:**\n"
            for item in deadlines[:5]:
                report += f"  • {item['title']} (Due: {item['due_date']})\n"
            report += "\n"

        # Upcoming hearings
        hearings = data.get("upcoming_hearings", [])
        if hearings:
            report += f"📅 **{len(hearings)} Upcoming Hearings:**\n"
            for item in hearings[:3]:
                report += f"  • {item['hearing_date']} - {item['hearing_type']}\n"
            report += "\n"

        # Recent violations
        violations = data.get("recent_violations", [])
        if violations:
            report += f"⚖️ **{len(violations)} Recent Violations:**\n"
            for item in violations[:3]:
                report += f"  • [{item['severity'].upper()}] {item['type']}\n"
            report += "\n"

        # Contradictions
        contradictions = data.get("recent_contradictions", [])
        if contradictions:
            report += f"⚠️ **{len(contradictions)} Recent Contradictions:**\n"
            for item in contradictions[:3]:
                report += f"  • {item['sender']} ({item['date'][:10]})\n"

        if not any([urgent, deadlines, hearings, violations, contradictions]):
            report += "✅ All clear - no urgent items"

        await update.message.reply_text(report)
    else:
        formatted = format_response(response)
        await update.message.reply_text(formatted)


async def hearing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /hearing command"""
    hearing_id = None
    if context.args:
        try:
            hearing_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Invalid hearing ID")
            return

    await update.message.reply_text("📅 Getting hearing information...")

    params = {}
    if hearing_id:
        params["hearing_id"] = hearing_id

    response = call_api("/telegram/hearing", params=params)

    formatted = format_response(response)
    await update.message.reply_text(formatted)


async def motion_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /motion command"""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /motion <type> <issue>\n"
            "Example: /motion reconsideration \"Cal OES 2-925 not verified\""
        )
        return

    motion_type = context.args[0]
    issue = " ".join(context.args[1:])

    await update.message.reply_text(f"📝 Generating motion for {motion_type}...")

    response = call_api(
        "/telegram/motion",
        method="POST",
        params={"motion_type": motion_type, "issue": issue}
    )

    if response.get("success"):
        data = response.get("data", {})
        message = f"📝 **Motion for {motion_type.title()}**\n\n"
        message += f"Issue: {issue}\n\n"

        structure = data.get("structure", {})
        message += "Structure:\n"
        for key, value in structure.items():
            message += f"  • {key.replace('_', ' ').title()}\n"

        next_steps = data.get("next_steps", [])
        if next_steps:
            message += "\nNext Steps:\n"
            for step in next_steps:
                message += f"  • {step}\n"

        await update.message.reply_text(message)
    else:
        formatted = format_response(response)
        await update.message.reply_text(formatted)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands"""
    await update.message.reply_text(
        "Unknown command. Type /help to see available commands."
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again or contact support."
        )


# ============================================================================
# Main
# ============================================================================

def main():
    """Start the Telegram bot"""
    logger.info("Starting ASEAGI Telegram bot...")

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("timeline", timeline_command))
    application.add_handler(CommandHandler("actions", actions_command))
    application.add_handler(CommandHandler("violations", violations_command))
    application.add_handler(CommandHandler("deadline", deadline_command))
    application.add_handler(CommandHandler("report", report_command))
    application.add_handler(CommandHandler("hearing", hearing_command))
    application.add_handler(CommandHandler("motion", motion_command))

    # Add error handler
    application.add_error_handler(error_handler)

    # Add handler for unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # Start bot
    logger.info("Bot started successfully. Polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
