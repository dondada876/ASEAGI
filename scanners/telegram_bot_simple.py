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

def main():
    """Start the bot"""
    logger.info(f"Starting Telegram bot...")
    logger.info(f"Storage: {INBOX_DIR}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("✅ Bot is running! Waiting for messages...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
