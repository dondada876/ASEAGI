#!/usr/bin/env python3
"""
Timeline Hub Telegram Bot
=========================

Easy document upload to timeline system via Telegram.

Commands:
    /text     - Upload text message screenshot
    /email    - Upload email screenshot
    /court    - Upload court document
    /police   - Upload police report
    /medical  - Upload medical record
    /generic  - Upload generic document

    /timeline - View recent timeline
    /search <keyword> - Search timeline
    /stats    - View timeline statistics

Usage:
    export TELEGRAM_BOT_TOKEN="your_token"
    export SUPABASE_URL="your_url"
    export SUPABASE_KEY="your_key"
    export ANTHROPIC_API_KEY="your_key"

    python3 telegram/timeline_bot.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from processors.document_processor import DocumentProcessor
from supabase import create_client

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global processor instance
processor = None
supabase = None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message"""
    await update.message.reply_text(
        "📅 **Timeline Hub Bot**\n\n"
        "Upload documents to build your master timeline!\n\n"
        "**Commands:**\n"
        "/text - Text message screenshot\n"
        "/email - Email screenshot\n"
        "/court - Court document\n"
        "/police - Police report\n"
        "/medical - Medical record\n"
        "/generic - Other document\n\n"
        "/timeline - View timeline\n"
        "/search - Search events\n"
        "/stats - Statistics\n\n"
        "Just send a photo and I'll ask what type it is!",
        parse_mode='Markdown'
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo uploads"""
    # Get the largest photo
    photo = update.message.photo[-1]

    # Check if user specified document type in context
    doc_type = context.user_data.get('waiting_for_doc_type')

    if not doc_type:
        # Ask user what type of document this is
        keyboard = [
            [
                InlineKeyboardButton("📱 Text Message", callback_data="type:TEXT_MESSAGE"),
                InlineKeyboardButton("📧 Email", callback_data="type:EMAIL")
            ],
            [
                InlineKeyboardButton("⚖️ Court Doc", callback_data="type:COURT_DOC"),
                InlineKeyboardButton("👮 Police Report", callback_data="type:POLICE_REPORT")
            ],
            [
                InlineKeyboardButton("🏥 Medical", callback_data="type:MEDICAL"),
                InlineKeyboardButton("📄 Generic", callback_data="type:GENERIC")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Store photo file_id for later
        context.user_data['pending_photo'] = photo.file_id

        await update.message.reply_text(
            "What type of document is this?",
            reply_markup=reply_markup
        )
        return

    # Process the document
    await process_uploaded_photo(update, context, photo.file_id, doc_type)


async def handle_document_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document type button click"""
    query = update.callback_query
    await query.answer()

    # Get selected type
    doc_type = query.data.split(':')[1]

    # Get stored photo
    photo_file_id = context.user_data.get('pending_photo')

    if not photo_file_id:
        await query.edit_message_text("Error: Photo not found. Please upload again.")
        return

    await query.edit_message_text(f"Processing as {doc_type}...")

    # Process the photo
    await process_uploaded_photo(update, context, photo_file_id, doc_type, query=query)


async def process_uploaded_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo_file_id: str,
    doc_type: str,
    query=None
):
    """Download and process uploaded photo"""
    try:
        # Download photo
        file = await context.bot.get_file(photo_file_id)

        # Create temp directory
        temp_dir = Path("/tmp/timeline-uploads")
        temp_dir.mkdir(exist_ok=True)

        # Save file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = temp_dir / f"{doc_type}_{timestamp}.jpg"
        await file.download_to_drive(file_path)

        # Send processing message
        if query:
            await query.edit_message_text(
                f"⏳ Processing {doc_type}...\n"
                "Extracting events, communications, and statements..."
            )
        else:
            processing_msg = await update.message.reply_text(
                f"⏳ Processing {doc_type}...\n"
                "Extracting events, communications, and statements..."
            )

        # Process with DocumentProcessor
        global processor
        results = processor.process_document(
            str(file_path),
            doc_type,
            extract_events=True,
            extract_communications=True,
            extract_statements=True
        )

        # Build result message
        result_text = (
            f"✅ **Processing Complete!**\n\n"
            f"**Document Type:** {doc_type}\n\n"
            f"**Extracted:**\n"
            f"• Events: {len(results['events'])}\n"
            f"• Communications: {len(results['communications'])}\n"
            f"• Statements: {len(results['statements'])}\n\n"
            f"Use /timeline to view the updated timeline!"
        )

        if query:
            await query.edit_message_text(result_text, parse_mode='Markdown')
        else:
            await processing_msg.edit_text(result_text, parse_mode='Markdown')

        # Clean up
        file_path.unlink()

    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        error_msg = f"❌ Error processing document: {str(e)}"

        if query:
            await query.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)


async def cmd_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set document type to text message"""
    context.user_data['waiting_for_doc_type'] = 'TEXT_MESSAGE'
    await update.message.reply_text(
        "📱 Ready to receive **text message screenshot**.\n"
        "Send the photo now!",
        parse_mode='Markdown'
    )


async def cmd_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set document type to email"""
    context.user_data['waiting_for_doc_type'] = 'EMAIL'
    await update.message.reply_text(
        "📧 Ready to receive **email screenshot**.\n"
        "Send the photo now!",
        parse_mode='Markdown'
    )


async def cmd_court(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set document type to court document"""
    context.user_data['waiting_for_doc_type'] = 'COURT_DOC'
    await update.message.reply_text(
        "⚖️ Ready to receive **court document**.\n"
        "Send the photo now!",
        parse_mode='Markdown'
    )


async def cmd_police(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set document type to police report"""
    context.user_data['waiting_for_doc_type'] = 'POLICE_REPORT'
    await update.message.reply_text(
        "👮 Ready to receive **police report**.\n"
        "Send the photo now!",
        parse_mode='Markdown'
    )


async def cmd_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent timeline events"""
    try:
        global supabase

        # Get recent events
        result = supabase.table('timeline_events')\
            .select('event_date, event_time, event_title, event_type, importance')\
            .order('event_date', desc=True)\
            .order('event_time', desc=True)\
            .limit(10)\
            .execute()

        if not result.data:
            await update.message.reply_text("No events in timeline yet.")
            return

        # Format timeline
        text = "📅 **Recent Timeline Events:**\n\n"

        for event in result.data:
            date = event['event_date']
            time = event.get('event_time', '')
            title = event['event_title']
            importance = event['importance']

            # Emoji based on importance
            if importance >= 900:
                emoji = "🔥"
            elif importance >= 800:
                emoji = "⚠️"
            elif importance >= 700:
                emoji = "📌"
            else:
                emoji = "📄"

            text += f"{emoji} **{date} {time}**\n"
            text += f"   {title}\n\n"

        await update.message.reply_text(text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error fetching timeline: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search timeline events"""
    if not context.args:
        await update.message.reply_text(
            "Usage: /search <keyword>\n"
            "Example: /search jamaica"
        )
        return

    keyword = ' '.join(context.args)

    try:
        global supabase

        # Search events
        result = supabase.table('timeline_events')\
            .select('event_date, event_title, event_description')\
            .ilike('event_title', f'%{keyword}%')\
            .order('event_date', desc=True)\
            .limit(10)\
            .execute()

        if not result.data:
            await update.message.reply_text(f"No events found matching '{keyword}'")
            return

        text = f"🔍 **Search results for '{keyword}':**\n\n"

        for event in result.data:
            text += f"📅 {event['event_date']}\n"
            text += f"   {event['event_title']}\n\n"

        await update.message.reply_text(text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error searching: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show timeline statistics"""
    try:
        global supabase

        # Count events by type
        result = supabase.rpc('get_event_type_counts').execute()

        # Count total events
        total = supabase.table('timeline_events').select('id', count='exact').execute()

        # Count critical events
        critical = supabase.table('timeline_events')\
            .select('id', count='exact')\
            .gte('importance', 900)\
            .execute()

        text = (
            "📊 **Timeline Statistics:**\n\n"
            f"**Total Events:** {total.count}\n"
            f"**Critical Events:** {critical.count}\n\n"
            "Use /timeline to view recent events!"
        )

        await update.message.reply_text(text, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


def main():
    """Start the bot"""
    global processor, supabase

    # Get credentials
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    ANTHROPIC_KEY = os.getenv('ANTHROPIC_API_KEY')

    if not all([TELEGRAM_TOKEN, SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_KEY]):
        logger.error("Missing environment variables!")
        sys.exit(1)

    # Initialize processor and supabase
    processor = DocumentProcessor(SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_KEY)
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Create application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("text", cmd_text))
    application.add_handler(CommandHandler("email", cmd_email))
    application.add_handler(CommandHandler("court", cmd_court))
    application.add_handler(CommandHandler("police", cmd_police))
    application.add_handler(CommandHandler("timeline", cmd_timeline))
    application.add_handler(CommandHandler("search", cmd_search))
    application.add_handler(CommandHandler("stats", cmd_stats))

    # Photo handler
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Callback query handler for buttons
    application.add_handler(CallbackQueryHandler(handle_document_type_selection, pattern="^type:"))

    # Start bot
    logger.info("🤖 Timeline Hub Bot started!")
    logger.info("Ready to receive documents...")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
