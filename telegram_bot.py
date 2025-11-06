#!/usr/bin/env python3
"""
ASEAGI Telegram Bot
Integrates with FastAPI backend for document processing
Runs in separate Docker container to avoid port conflicts
"""

import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
API_URL = os.environ.get('API_URL', 'http://api:8000')  # Docker network
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

if not TELEGRAM_BOT_TOKEN:
    raise Exception("TELEGRAM_BOT_TOKEN not set")


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start(update: Update, context):
    """Handle /start command"""
    await update.message.reply_text(
        "🛡️ *ASEAGI Document Scanner*\n\n"
        "Send me documents and I'll process them with AI.\n\n"
        "*Commands:*\n"
        "/start - Show this message\n"
        "/upload - Upload a document\n"
        "/search <query> - Search documents\n"
        "/stats - Show processing stats\n"
        "/help - Get help\n\n"
        "Just send me a document (photo or file) to process it!",
        parse_mode='Markdown'
    )


async def help_command(update: Update, context):
    """Handle /help command"""
    await update.message.reply_text(
        "*How to use:*\n\n"
        "1. *Upload Document*\n"
        "   - Take photo or send file\n"
        "   - I'll process it with AI\n"
        "   - Get scores instantly\n\n"
        "2. *Search Documents*\n"
        "   - /search protective orders\n"
        "   - I'll find similar documents\n\n"
        "3. *Check Stats*\n"
        "   - /stats\n"
        "   - See processing statistics\n\n"
        "*For Ashe. For Justice. For All Children.* 🛡️",
        parse_mode='Markdown'
    )


async def upload_document(update: Update, context):
    """Handle document upload"""

    # Check if document or photo
    if update.message.document:
        file = await update.message.document.get_file()
        file_name = update.message.document.file_name
    elif update.message.photo:
        file = await update.message.photo[-1].get_file()
        file_name = f"photo_{update.message.message_id}.jpg"
    else:
        await update.message.reply_text("Please send a document or photo.")
        return

    # Show processing message
    processing_msg = await update.message.reply_text(
        "⏳ Processing document...\n"
        "This may take 5-10 seconds."
    )

    try:
        # Download file
        file_bytes = await file.download_as_bytearray()

        # Send to FastAPI backend (via Docker network)
        response = requests.post(
            f"{API_URL}/api/upload",
            files={"file": (file_name, bytes(file_bytes))},
            data={"source": "telegram"},
            timeout=60
        )

        result = response.json()

        # Edit processing message with results
        if result.get("status") == "duplicate":
            await processing_msg.edit_text(
                "⚠️ *Duplicate Detected*\n\n"
                f"Match Type: {result['match_type']}\n"
                f"Similarity: {result['similarity']:.0%}\n"
                f"Original: {result['matched_document']['file_name']}\n\n"
                "Skipped processing to save costs.",
                parse_mode='Markdown'
            )

        elif result.get("status") == "success":
            scores = result.get("scores", {})
            await processing_msg.edit_text(
                "✅ *Document Processed Successfully*\n\n"
                f"📄 *File:* {file_name}\n"
                f"🎯 *Truth Score:* {scores.get('truth_score', 'N/A')}/100\n"
                f"⚖️ *Justice Score:* {scores.get('justice_score', 'N/A')}/100\n"
                f"💳 *Legal Credit:* {scores.get('legal_credit_score', 'N/A')}/850\n\n"
                f"Document ID: {result.get('document_id')}",
                parse_mode='Markdown'
            )

        else:
            await processing_msg.edit_text(
                f"❌ Error: {result.get('error', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Upload error: {e}")
        await processing_msg.edit_text(
            f"❌ Upload failed: {str(e)}\n\n"
            "Please try again or contact support."
        )


async def search_documents(update: Update, context):
    """Handle document search"""

    if not context.args:
        await update.message.reply_text(
            "Usage: /search <query>\n"
            "Example: /search protective order violations"
        )
        return

    query = " ".join(context.args)

    # Show searching message
    search_msg = await update.message.reply_text(f"🔍 Searching for: *{query}*...", parse_mode='Markdown')

    try:
        # Search via FastAPI
        response = requests.get(
            f"{API_URL}/api/search",
            params={"query": query, "limit": 5},
            timeout=30
        )

        results = response.json().get("results", [])

        if not results:
            await search_msg.edit_text("No documents found.")
            return

        # Format results
        message = f"🔍 *Found {len(results)} documents:*\n\n"

        for i, doc in enumerate(results, 1):
            message += f"{i}. *{doc['file_name']}*\n"
            message += f"   Similarity: {doc.get('similarity', 0):.0%}\n"
            if doc.get('truth_score'):
                message += f"   Truth Score: {doc['truth_score']}/100\n"
            message += "\n"

        await search_msg.edit_text(message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Search error: {e}")
        await search_msg.edit_text(f"❌ Search failed: {str(e)}")


async def show_stats(update: Update, context):
    """Show processing statistics"""

    try:
        # Get stats from FastAPI
        response = requests.get(f"{API_URL}/api/stats", timeout=10)
        stats = response.json()

        message = (
            "📊 *Processing Statistics*\n\n"
            f"Total Checks: {stats['total_checks']}\n"
            f"Duplicates: {stats['total_duplicates']}\n"
            f"New Documents: {stats['new_documents']}\n\n"
            f"Cost Saved: ${stats['total_duplicates'] * 0.01:.2f}"
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Stats error: {e}")
        await update.message.reply_text(f"❌ Failed to get stats: {str(e)}")


# ============================================================================
# HEALTH CHECK SERVER
# ============================================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for health checks"""

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"healthy"}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logs


def run_health_server():
    """Run health check server in background thread"""
    server = HTTPServer(('0.0.0.0', 8443), HealthCheckHandler)
    logger.info("Health check server started on port 8443")
    server.serve_forever()


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the bot"""

    logger.info("=" * 80)
    logger.info("ASEAGI TELEGRAM BOT STARTING")
    logger.info("=" * 80)
    logger.info(f"API URL: {API_URL}")
    logger.info(f"Webhook URL: {WEBHOOK_URL}")
    logger.info("")

    # Start health check server in background
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_documents))
    application.add_handler(CommandHandler("stats", show_stats))

    # Handle documents and photos
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO,
        upload_document
    ))

    # Set webhook if URL provided
    if WEBHOOK_URL:
        logger.info(f"Setting webhook: {WEBHOOK_URL}")
        # application.run_webhook(
        #     listen="0.0.0.0",
        #     port=8443,
        #     url_path="webhook",
        #     webhook_url=WEBHOOK_URL
        # )

    # Run polling (simpler for development)
    logger.info("Starting bot with polling...")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
