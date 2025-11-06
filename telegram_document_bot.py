#!/usr/bin/env python3
"""
Telegram Document Ingestion Bot
Upload documents from your phone with context and metadata
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import io
from typing import Dict, Any

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, ValueError):
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Telegram bot imports
try:
    from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ConversationHandler,
        ContextTypes,
        filters
    )
except ImportError:
    print("❌ Please install: pip install python-telegram-bot")
    sys.exit(1)

# Supabase import
try:
    from supabase import create_client
except ImportError:
    print("❌ Please install: pip install supabase")
    sys.exit(1)

# Load credentials
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# Fallback to secrets.toml
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        import toml
        secrets_path = Path(__file__).parent / '.streamlit' / 'secrets.toml'
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            SUPABASE_URL = secrets.get('SUPABASE_URL')
            SUPABASE_KEY = secrets.get('SUPABASE_KEY')
            TELEGRAM_BOT_TOKEN = secrets.get('TELEGRAM_BOT_TOKEN')
    except:
        pass

# Initialize Supabase
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    print("⚠️ Warning: Supabase credentials not found")
    supabase = None

# Conversation states
(DOCUMENT, DOC_TYPE, DOC_DATE, TITLE, NOTES, RELEVANCY, CONFIRM) = range(7)

# Document type options
DOC_TYPES = {
    'PLCR': '🚔 Police Report',
    'DECL': '📄 Declaration',
    'EVID': '📸 Evidence/Photo',
    'CPSR': '👶 CPS Report',
    'RESP': '📋 Response',
    'FORN': '🔬 Forensic Report',
    'ORDR': '⚖️ Court Order',
    'MOTN': '📑 Motion',
    'HEAR': '🎤 Hearing Transcript',
    'OTHR': '📎 Other'
}

# Relevancy levels
RELEVANCY_LEVELS = {
    'Critical': '🔴 Critical (900+)',
    'High': '🟠 High (800-899)',
    'Medium': '🟡 Medium (700-799)',
    'Low': '🟢 Low (600-699)'
}

RELEVANCY_SCORES = {
    'Critical': 920,
    'High': 850,
    'Medium': 750,
    'Low': 650
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and ask for document."""
    user = update.effective_user

    await update.message.reply_text(
        f"👋 Hi {user.first_name}!\n\n"
        f"📸 **Document Ingestion Bot**\n\n"
        f"I'll help you upload documents to your legal case database.\n\n"
        f"📤 **Send me a document** (photo or PDF) to get started.\n\n"
        f"Or use /cancel to stop."
    )

    return DOCUMENT


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive the document and ask for document type."""
    # Store the document
    if update.message.photo:
        # Get the largest photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        context.user_data['file_id'] = photo.file_id
        context.user_data['file_type'] = 'photo'
        context.user_data['file_size'] = photo.file_size

        await update.message.reply_text("✅ Photo received!")

    elif update.message.document:
        document = update.message.document
        file = await context.bot.get_file(document.file_id)
        context.user_data['file_id'] = document.file_id
        context.user_data['file_type'] = 'document'
        context.user_data['file_name'] = document.file_name
        context.user_data['file_size'] = document.file_size

        await update.message.reply_text(f"✅ Document received: {document.file_name}")
    else:
        await update.message.reply_text("❌ Please send a photo or document file.")
        return DOCUMENT

    # Store the file object for later download
    context.user_data['file_object'] = file

    # Ask for document type
    keyboard = [[doc_type] for doc_type in DOC_TYPES.values()]
    keyboard.append(['❌ Cancel'])

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "📝 **What type of document is this?**\n\n"
        "Choose from the options below:",
        reply_markup=reply_markup
    )

    return DOC_TYPE


async def receive_doc_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store document type and ask for date."""
    selected = update.message.text

    # Find the doc type code
    doc_type_code = None
    for code, label in DOC_TYPES.items():
        if label == selected:
            doc_type_code = code
            break

    if not doc_type_code:
        await update.message.reply_text("❌ Please select a valid document type.")
        return DOC_TYPE

    context.user_data['doc_type'] = doc_type_code

    await update.message.reply_text(
        f"✅ Document type: {selected}\n\n"
        f"📅 **When was this document created/dated?**\n\n"
        f"Enter the date in format: YYYYMMDD\n"
        f"Example: 20240804 for August 4, 2024\n\n"
        f"Or type 'today' for today's date.",
        reply_markup=ReplyKeyboardRemove()
    )

    return DOC_DATE


async def receive_doc_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store document date and ask for title."""
    date_text = update.message.text.strip()

    if date_text.lower() == 'today':
        date_str = datetime.now().strftime('%Y%m%d')
    else:
        # Validate date format
        try:
            if len(date_text) == 8 and date_text.isdigit():
                # Parse to validate
                datetime.strptime(date_text, '%Y%m%d')
                date_str = date_text
            else:
                raise ValueError()
        except:
            await update.message.reply_text(
                "❌ Invalid date format.\n\n"
                "Please use YYYYMMDD format (e.g., 20240804)\n"
                "Or type 'today'"
            )
            return DOC_DATE

    context.user_data['doc_date'] = date_str

    await update.message.reply_text(
        f"✅ Date: {date_str}\n\n"
        f"📋 **Give this document a title/description**\n\n"
        f"Example: 'Police Report - Child was Safe'\n"
        f"Or: 'Berkeley PD Report - August 10 Incident'"
    )

    return TITLE


async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store title and ask for notes."""
    title = update.message.text.strip()

    if len(title) < 5:
        await update.message.reply_text(
            "❌ Title too short. Please provide a meaningful description (at least 5 characters)."
        )
        return TITLE

    context.user_data['title'] = title

    await update.message.reply_text(
        f"✅ Title: {title}\n\n"
        f"📝 **Add notes and context**\n\n"
        f"What's important about this document?\n"
        f"Why is it relevant to your case?\n"
        f"Any key details or facts?\n\n"
        f"Type your notes below:"
    )

    return NOTES


async def receive_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store notes and ask for relevancy level."""
    notes = update.message.text.strip()

    context.user_data['notes'] = notes

    # Ask for relevancy
    keyboard = [[level] for level in RELEVANCY_LEVELS.values()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        f"✅ Notes saved!\n\n"
        f"⭐ **How important is this document?**\n\n"
        f"Choose the relevancy level:",
        reply_markup=reply_markup
    )

    return RELEVANCY


async def receive_relevancy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store relevancy and show confirmation."""
    selected = update.message.text

    # Find relevancy level
    relevancy_level = None
    for level, label in RELEVANCY_LEVELS.items():
        if label == selected:
            relevancy_level = level
            break

    if not relevancy_level:
        await update.message.reply_text("❌ Please select a valid relevancy level.")
        return RELEVANCY

    context.user_data['relevancy'] = relevancy_level
    context.user_data['relevancy_score'] = RELEVANCY_SCORES[relevancy_level]

    # Show summary
    data = context.user_data
    doc_type_label = DOC_TYPES.get(data['doc_type'], data['doc_type'])

    summary = (
        "📋 **Review Your Submission**\n\n"
        f"📄 **File:** {data.get('file_name', 'Photo')}\n"
        f"📝 **Type:** {doc_type_label}\n"
        f"📅 **Date:** {data['doc_date']}\n"
        f"📌 **Title:** {data['title']}\n"
        f"💬 **Notes:** {data['notes'][:100]}{'...' if len(data['notes']) > 100 else ''}\n"
        f"⭐ **Relevancy:** {relevancy_level} ({data['relevancy_score']})\n\n"
        f"✅ Type **YES** to upload to database\n"
        f"❌ Type **NO** to cancel"
    )

    await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove())

    return CONFIRM


async def confirm_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Confirm and upload to Supabase."""
    confirmation = update.message.text.strip().upper()

    if confirmation != 'YES':
        await update.message.reply_text(
            "❌ Upload cancelled.\n\n"
            "Use /start to begin a new upload."
        )
        return ConversationHandler.END

    # Upload to Supabase
    await update.message.reply_text("⏳ Uploading to database...")

    try:
        if not supabase:
            raise Exception("Supabase not configured")

        data = context.user_data

        # Download the file
        file_obj = data['file_object']
        file_bytes = io.BytesIO()
        await file_obj.download_to_memory(file_bytes)
        file_bytes.seek(0)

        # Generate filename
        doc_type = data['doc_type']
        doc_date = data['doc_date']
        title_slug = data['title'][:50].replace(' ', '_').replace('/', '_')
        relevancy = data['relevancy_score']

        file_ext = 'jpg' if data['file_type'] == 'photo' else data.get('file_name', 'file').split('.')[-1]

        filename = f"{doc_date}_BerkeleyPD_{doc_type}_{title_slug}_Mic-850_Mac-900_LEG-920_REL-{relevancy}.{file_ext}"

        # Calculate file hash
        file_hash = hashlib.md5(file_bytes.getvalue()).hexdigest()

        # Prepare document data
        document_data = {
            'original_filename': filename,
            'document_type': doc_type,
            'document_title': data['title'],
            'relevancy_number': data['relevancy_score'],
            'file_extension': file_ext,
            'executive_summary': data['notes'],  # Use executive_summary instead of notes
            'document_date': doc_date,
            'created_at': datetime.now().isoformat(),
            'file_hash': file_hash,
            'source': 'telegram_bot',
            'uploaded_via': 'phone'
        }

        # Insert into legal_documents table
        response = supabase.table('legal_documents').insert(document_data).execute()

        if response.data:
            await update.message.reply_text(
                "✅ **Document uploaded successfully!**\n\n"
                f"📄 Filename: {filename}\n"
                f"🆔 ID: {response.data[0].get('id', 'N/A')}\n"
                f"⭐ Relevancy: {data['relevancy_score']}\n\n"
                f"Your document is now in the database!\n\n"
                f"Use /start to upload another document."
            )
        else:
            raise Exception("No data returned from Supabase")

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Upload failed:**\n\n"
            f"Error: {str(e)}\n\n"
            f"Please check your Supabase configuration.\n\n"
            f"Use /start to try again."
        )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        "❌ Upload cancelled.\n\n"
        "Use /start when you're ready to upload a document.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    """Run the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set!")
        print("\nSet it in your environment:")
        print("  export TELEGRAM_BOT_TOKEN='your-bot-token'")
        print("\nOr add to .streamlit/secrets.toml:")
        print("  TELEGRAM_BOT_TOKEN = 'your-bot-token'")
        print("\nGet a token from @BotFather on Telegram:")
        print("  https://t.me/BotFather")
        sys.exit(1)

    print("🤖 Starting Telegram Document Bot...")
    print(f"📡 Supabase: {'✅ Connected' if supabase else '❌ Not configured'}")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DOCUMENT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receive_document)
            ],
            DOC_TYPE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_doc_type)
            ],
            DOC_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_doc_date)
            ],
            TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)
            ],
            NOTES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_notes)
            ],
            RELEVANCY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_relevancy)
            ],
            CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_upload)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)

    # Start the bot
    print("✅ Bot is running! Press Ctrl+C to stop.")
    print("📱 Open Telegram and search for your bot to start uploading documents.")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
