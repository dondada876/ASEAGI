#!/usr/bin/env python3
"""
SIMPLE TELEGRAM BOT - Direct to Legal Documents
Receives images/documents via Telegram and immediately:
1. Stores permanently in telegram-inbox/
2. OCRs and analyzes for violations
3. Uploads directly to legal_documents table
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import asyncio
import logging

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Supabase
from supabase import create_client

# Bug Tracker
from core.bug_tracker import BugTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bug tracker
bug_tracker = BugTracker()

# Config
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

if not all([TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY]):
    logger.error("Missing environment variables!")
    sys.exit(1)

# Initialize
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
PROJECT_ROOT = Path(__file__).parent.parent
INBOX_DIR = PROJECT_ROOT / "data" / "telegram-inbox"
INBOX_DIR.mkdir(parents=True, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    await update.message.reply_text(
        "📱 PROJ344 Legal Document Bot\n\n"
        "Send me images of legal documents and I'll:\n"
        "✅ Store them permanently\n"
        "✅ Extract text (OCR)\n"
        "✅ Analyze for violations\n"
        "✅ Upload to PROJ344 database\n\n"
        "Just send an image to get started!"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    try:
        bug_tracker.log('info', 'Photo upload started', 'telegram_bot',
                       workspace_id='legal')
        # Get largest photo
        photo = update.message.photo[-1]

        # Create today's folder
        today = datetime.now().strftime('%Y-%m-%d')
        today_folder = INBOX_DIR / today
        today_folder.mkdir(exist_ok=True)

        # Download file
        timestamp = datetime.now().strftime('%H%M%S')
        filename = f"photo_{timestamp}.jpg"
        file_path = today_folder / filename

        file = await context.bot.get_file(photo.file_id)
        await file.download_to_drive(file_path)

        logger.info(f"Downloaded: {file_path}")

        # Acknowledge receipt
        await update.message.reply_text(
            f"✅ Received and stored!\n"
            f"📁 Location: telegram-inbox/{today}/{filename}\n"
            f"🔍 Analyzing... (this may take 30-60 seconds)"
        )

        # Store in database immediately
        doc_data = {
            'case_id': 'ashe-bucknor-j24-00478',
            'original_filename': filename,
            'file_path': str(file_path),
            'document_type': 'TEXT',  # Will be updated after OCR
            'document_date': today,
            'document_title': f'Telegram Upload - {today} {timestamp}',
            'executive_summary': 'Document uploaded via Telegram bot, pending OCR analysis',
            'status': 'RECEIVED',
            'purpose': 'EVIDENCE',
            'relevancy_number': 750,
            'legal_number': 750,
            'macro_number': 750,
            'micro_number': 750,
        }

        response = supabase.table('legal_documents').insert(doc_data).execute()
        doc_id = response.data[0]['id'] if response.data else None

        await update.message.reply_text(
            f"💾 Saved to database!\n"
            f"🆔 Document ID: {doc_id}\n"
            f"📊 View in dashboard: http://137.184.1.91:8501"
        )

        logger.info(f"Saved to database: {doc_id}")
        bug_tracker.log('info', f'Photo uploaded successfully: {filename}', 'telegram_bot',
                       details={'doc_id': doc_id, 'filename': filename},
                       workspace_id='legal')

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        bug_tracker.log('critical', f'Photo upload failed: {str(e)}', 'telegram_bot',
                       error=e, workspace_id='legal')
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document uploads (PDF, etc)"""
    try:
        bug_tracker.log('info', 'Document upload started', 'telegram_bot',
                       workspace_id='legal')
        document = update.message.document

        # Create today's folder
        today = datetime.now().strftime('%Y-%m-%d')
        today_folder = INBOX_DIR / today
        today_folder.mkdir(exist_ok=True)

        # Download file
        file_path = today_folder / document.file_name

        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(file_path)

        logger.info(f"Downloaded: {file_path}")

        await update.message.reply_text(
            f"✅ Received: {document.file_name}\n"
            f"📁 Stored in: telegram-inbox/{today}/\n"
            f"💾 Processing..."
        )

        # Store in database
        doc_data = {
            'case_id': 'ashe-bucknor-j24-00478',
            'original_filename': document.file_name,
            'file_path': str(file_path),
            'document_type': 'TEXT',
            'document_date': today,
            'document_title': f'Telegram Upload - {document.file_name}',
            'executive_summary': 'Document uploaded via Telegram bot',
            'status': 'RECEIVED',
            'purpose': 'EVIDENCE',
            'relevancy_number': 750,
            'legal_number': 750,
            'macro_number': 750,
            'micro_number': 750,
        }

        response = supabase.table('legal_documents').insert(doc_data).execute()
        doc_id = response.data[0]['id'] if response.data else None

        await update.message.reply_text(
            f"💾 Saved to database!\n"
            f"🆔 ID: {doc_id}\n"
            f"📊 Dashboard: http://137.184.1.91:8501"
        )

        bug_tracker.log('info', f'Document uploaded successfully: {document.file_name}', 'telegram_bot',
                       details={'doc_id': doc_id, 'filename': document.file_name},
                       workspace_id='legal')

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        bug_tracker.log('critical', f'Document upload failed: {str(e)}', 'telegram_bot',
                       error=e, workspace_id='legal')
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message with available commands"""
    help_text = """
**ASEAGI Bot Commands**

📱 **Document Upload**
Just send an image or document - no command needed!

📊 **Query Commands**
/violations - Show recent constitutional violations detected
/search <query> - Search documents for specific content
   Example: `/search ex parte`

📅 **Timeline & Actions**
/timeline [days] - Show case events (default: last 30 days)
/actions - Show pending action items
/deadline - Show upcoming deadlines

📈 **Reports**
/report - Daily summary of case activity

📌 **Other**
/help - Show this message
/start - Welcome message

Need help? All documents are stored permanently at:
http://137.184.1.91:8501
"""
    await update.message.reply_text(help_text)

async def violations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent violations detected in documents"""
    try:
        # Query legal_violations table
        result = supabase.table('legal_violations')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(10)\
            .execute()

        if not result.data:
            await update.message.reply_text(
                "📊 No violations detected yet.\n\n"
                "Upload documents and they will be automatically analyzed for:\n"
                "• Constitutional violations\n"
                "• Perjury indicators\n"
                "• Fraud indicators\n"
                "• Procedural violations"
            )
            return

        violations_text = "⚖️ **Recent Violations Detected**\n\n"

        for i, violation in enumerate(result.data[:5], 1):
            violations_text += f"**{i}. {violation.get('violation_type', 'Unknown')}**\n"
            violations_text += f"📄 Document: {violation.get('document_title', 'N/A')}\n"
            violations_text += f"⚠️ Severity: {violation.get('severity', 'Unknown')}\n"
            violations_text += f"📝 {violation.get('description', '')[:100]}...\n\n"

        violations_text += f"\n📊 Total: {len(result.data)} violations found\n"
        violations_text += "View all: http://137.184.1.91:8501"

        await update.message.reply_text(violations_text)

    except Exception as e:
        logger.error(f"Error fetching violations: {e}")
        await update.message.reply_text(
            f"❌ Error fetching violations: {str(e)}\n\n"
            "Try checking the dashboard at: http://137.184.1.91:8501"
        )

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search documents for specific content"""
    if not context.args:
        await update.message.reply_text(
            "🔍 **Search Documents**\n\n"
            "Usage: `/search <query>`\n\n"
            "Examples:\n"
            "• `/search ex parte`\n"
            "• `/search visitation denial`\n"
            "• `/search 2024-08-13`"
        )
        return

    query = ' '.join(context.args)

    try:
        # Search in legal_documents table
        result = supabase.table('legal_documents')\
            .select('id, document_title, document_date, executive_summary')\
            .or_(f'document_title.ilike.%{query}%,executive_summary.ilike.%{query}%,full_text.ilike.%{query}%')\
            .order('document_date', desc=True)\
            .limit(10)\
            .execute()

        if not result.data:
            await update.message.reply_text(
                f"🔍 No results found for: **{query}**\n\n"
                "Try:\n"
                "• Different keywords\n"
                "• Partial matches\n"
                "• Check spelling"
            )
            return

        search_results = f"🔍 **Search Results for: {query}**\n\n"
        search_results += f"Found {len(result.data)} documents:\n\n"

        for i, doc in enumerate(result.data[:5], 1):
            search_results += f"**{i}. {doc.get('document_title', 'Untitled')}**\n"
            search_results += f"📅 Date: {doc.get('document_date', 'N/A')}\n"
            summary = doc.get('executive_summary', '')
            if summary:
                search_results += f"📝 {summary[:100]}...\n"
            search_results += f"🆔 ID: {doc['id'][:8]}\n\n"

        if len(result.data) > 5:
            search_results += f"\n... and {len(result.data) - 5} more results\n"

        search_results += "\n📊 View all: http://137.184.1.91:8501"

        await update.message.reply_text(search_results)

    except Exception as e:
        logger.error(f"Error searching: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def timeline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show case timeline"""
    days = 30
    if context.args and context.args[0].isdigit():
        days = int(context.args[0])

    try:
        from datetime import timedelta
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

        result = supabase.table('legal_documents')\
            .select('document_date, document_title, document_type')\
            .gte('document_date', cutoff_date)\
            .order('document_date', desc=True)\
            .limit(20)\
            .execute()

        if not result.data:
            await update.message.reply_text(
                f"📅 No events in the last {days} days.\n\n"
                "Upload documents to build your case timeline!"
            )
            return

        timeline_text = f"📅 **Case Timeline** (Last {days} days)\n\n"
        timeline_text += f"Found {len(result.data)} events:\n\n"

        current_date = None
        for event in result.data[:15]:
            event_date = event.get('document_date')
            if event_date != current_date:
                current_date = event_date
                timeline_text += f"\n**{event_date}**\n"

            timeline_text += f"  • {event.get('document_title', 'Untitled')}\n"

        timeline_text += f"\n📊 Dashboard: http://137.184.1.91:8501"

        await update.message.reply_text(timeline_text)

    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def actions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show pending action items"""
    await update.message.reply_text(
        "✅ **Pending Actions**\n\n"
        "1. Upload any new ex parte documents\n"
        "2. Review violation analysis on dashboard\n"
        "3. Check for upcoming deadlines\n\n"
        "📊 Dashboard: http://137.184.1.91:8501\n"
        "🔍 Use /violations to see detected issues"
    )

async def deadline_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show upcoming deadlines"""
    await update.message.reply_text(
        "📅 **Upcoming Deadlines**\n\n"
        "Deadline tracking coming soon!\n\n"
        "For now, check:\n"
        "• Dashboard: http://137.184.1.91:8501\n"
        "• Case calendar\n"
        "• Court filings"
    )

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate daily summary report"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')

        # Get today's documents
        docs_result = supabase.table('legal_documents')\
            .select('*', count='exact')\
            .eq('document_date', today)\
            .execute()

        # Get today's violations
        violations_result = supabase.table('legal_violations')\
            .select('*', count='exact')\
            .gte('created_at', f'{today}T00:00:00')\
            .execute()

        report_text = f"📊 **Daily Report** - {today}\n\n"
        report_text += f"📄 Documents: {len(docs_result.data) if docs_result.data else 0}\n"
        report_text += f"⚖️ Violations: {len(violations_result.data) if violations_result.data else 0}\n"
        report_text += f"\n🔍 Use /violations for details\n"
        report_text += f"📊 Dashboard: http://137.184.1.91:8501"

        await update.message.reply_text(report_text)

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    """Start the bot"""
    logger.info(f"Starting Telegram bot...")
    logger.info(f"Storage: {INBOX_DIR}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("violations", violations_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("timeline", timeline_command))
    app.add_handler(CommandHandler("actions", actions_command))
    app.add_handler(CommandHandler("deadline", deadline_command))
    app.add_handler(CommandHandler("report", report_command))

    # Document handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("✅ Bot is running with all commands enabled!")
    logger.info("Available commands: /start /help /violations /search /timeline /actions /deadline /report")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
