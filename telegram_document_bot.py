#!/usr/bin/env python3
"""
ASEAGI Smart Document Bot
AI-powered document analysis + manual verification
Upload documents from your phone with automatic metadata extraction
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import io
from typing import Dict, Any
import tempfile

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

# AI Analyzer import
try:
    from ai_analyzer import DocumentAnalyzer, LEGAL_DOC_TYPES
    AI_AVAILABLE = True
except ImportError:
    print("⚠️  AI analyzer not found. Install: pip install anthropic")
    AI_AVAILABLE = False

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
(DOCUMENT, AI_ANALYSIS, AI_REVIEW, DOC_TYPE, DOC_DATE, TITLE, NOTES, RELEVANCY, CONFIRM, EDIT_FIELD) = range(10)

# AI mode setting
USE_AI = os.getenv("USE_AI_ANALYSIS", "true").lower() == "true" and AI_AVAILABLE

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

    ai_status = "🤖 **AI-Powered Analysis: ENABLED**" if USE_AI else "📝 **Manual Entry Mode**"

    await update.message.reply_text(
        f"👋 Hi {user.first_name}!\n\n"
        f"⚖️ **ASEAGI Smart Document Bot**\n"
        f"*For Ashe. For Justice. For All Children.* 🛡️\n\n"
        f"{ai_status}\n\n"
        f"I'll help you upload legal documents to your case database.\n\n"
        f"📤 **Send me a document** (photo or PDF) to get started.\n\n"
        f"{'🤖 AI will analyze it automatically and extract metadata!' if USE_AI else '📝 You will enter metadata manually.'}\n\n"
        f"Or use /cancel to stop."
    )

    return DOCUMENT


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive the document and trigger AI analysis or manual entry."""
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

    # If AI is enabled, run analysis
    if USE_AI:
        await update.message.reply_text("⏳ Analyzing document with AI... (~10-15 seconds)")
        return await run_ai_analysis(update, context)
    else:
        # Fall back to manual entry
        await update.message.reply_text("ℹ️ AI analysis disabled. Manual entry mode.")
        return await ask_document_type(update, context)


async def run_ai_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Run AI analysis on the uploaded document."""
    try:
        # Download file to temp location
        file_obj = context.user_data['file_object']

        # Create temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            await file_obj.download_to_drive(tmp_file.name)
            temp_path = tmp_file.name

        context.user_data['temp_file_path'] = temp_path

        # Run AI analysis
        analyzer = DocumentAnalyzer(
            provider="anthropic",  # Use Claude by default
            confidence_threshold=70
        )

        result = analyzer.analyze_document(temp_path)
        context.user_data['ai_result'] = result

        # Show AI results
        confidence = result.get('overall_confidence', 0)
        doc_type = result.get('document_type', 'unknown')
        title = result.get('title', 'Unknown')
        relevancy = result.get('relevancy', 0)
        summary = result.get('summary', 'N/A')

        # Map to ASEAGI format
        doc_type_code = result.get('document_type_code', 'OTHR')
        doc_type_label = DOC_TYPES.get(doc_type_code, '📎 Other')

        message = f"""
🤖 **AI Analysis Complete**

**Confidence: {confidence}%**

📝 **Type:** {doc_type_label}
📅 **Date:** {result.get('date', 'Not found')}
📌 **Title:** {title}
⭐ **Relevancy:** {relevancy}/1000
📄 **Summary:** {summary}

"""

        # Add confidence breakdown
        if 'confidence_scores' in result:
            scores = result['confidence_scores']
            message += "**Field Confidence:**\n"
            message += f"  • Type: {scores.get('type', 0)}%\n"
            message += f"  • Date: {scores.get('date', 0)}%\n"
            message += f"  • Title: {scores.get('title', 0)}%\n"
            message += f"  • Relevancy: {scores.get('relevancy', 0)}%\n\n"

        # Check if clarification needed
        if result.get('needs_clarification') or confidence < 70:
            message += "⚠️ **AI is uncertain.** I'll ask some questions to clarify.\n"
            await update.message.reply_text(message)

            # Store questions for later
            context.user_data['ai_questions'] = result.get('questions', [])

            # Go to manual entry but pre-fill with AI suggestions
            return await ask_document_type(update, context, ai_suggestion=doc_type_label)
        else:
            message += "✅ **AI is confident!** Review and confirm or edit."

            # Show action buttons
            keyboard = [
                ["💾 Save", "✏️ Edit"],
                ["🔄 Manual Entry", "❌ Cancel"]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(message, reply_markup=reply_markup)
            return AI_REVIEW

    except Exception as e:
        await update.message.reply_text(
            f"❌ AI analysis failed: {str(e)}\n\n"
            "Switching to manual entry mode..."
        )
        return await ask_document_type(update, context)


async def handle_ai_review(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's response to AI analysis."""
    choice = update.message.text

    if choice == "💾 Save":
        # Use AI results and save
        return await save_with_ai_data(update, context)

    elif choice == "✏️ Edit":
        # Show which field to edit
        keyboard = [
            ["Edit Type", "Edit Date"],
            ["Edit Title", "Edit Relevancy"],
            ["Edit Summary", "🔙 Back to Review"]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(
            "Which field would you like to edit?",
            reply_markup=reply_markup
        )
        return EDIT_FIELD

    elif choice == "🔄 Manual Entry":
        # Switch to full manual entry
        await update.message.reply_text("Switching to manual entry mode...")
        return await ask_document_type(update, context)

    elif choice == "❌ Cancel":
        return await cancel(update, context)

    else:
        await update.message.reply_text("Please choose an option from the buttons.")
        return AI_REVIEW


async def save_with_ai_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Save document using AI-extracted data."""
    await update.message.reply_text("⏳ Uploading to database...")

    try:
        if not supabase:
            raise Exception("Supabase not configured")

        ai_result = context.user_data.get('ai_result', {})
        file_obj = context.user_data['file_object']

        # Download the file
        file_bytes = io.BytesIO()
        await file_obj.download_to_memory(file_bytes)
        file_bytes.seek(0)

        # Generate filename using AI data
        doc_type_code = ai_result.get('document_type_code', 'OTHR')
        doc_date = ai_result.get('date', datetime.now().strftime('%Y%m%d')).replace('-', '')
        title_slug = ai_result.get('title', 'Untitled')[:50].replace(' ', '_').replace('/', '_')
        relevancy = ai_result.get('relevancy', 500)

        file_ext = 'jpg' if context.user_data['file_type'] == 'photo' else context.user_data.get('file_name', 'file').split('.')[-1]

        filename = f"{doc_date}_BerkeleyPD_{doc_type_code}_{title_slug}_Mic-850_Mac-900_LEG-920_REL-{relevancy}.{file_ext}"

        # Calculate file hash
        file_hash = hashlib.md5(file_bytes.getvalue()).hexdigest()

        # Prepare document data
        document_data = {
            'original_filename': filename,
            'document_type': doc_type_code,
            'document_title': ai_result.get('title', 'Untitled'),
            'relevancy_number': relevancy,
            'file_extension': file_ext,
            'notes': ai_result.get('summary', ''),
            'created_at': datetime.now().isoformat(),
            'file_hash': file_hash,
            'source': 'telegram_bot',
            'uploaded_via': 'phone',
            'ai_extracted': True,
            'ai_confidence': ai_result.get('overall_confidence', 0),
            'ai_summary': ai_result.get('summary', ''),
            'ai_provider': 'anthropic'
        }

        # Insert into legal_documents table
        response = supabase.table('legal_documents').insert(document_data).execute()

        if response.data:
            await update.message.reply_text(
                "✅ **Document uploaded successfully!**\n\n"
                f"📄 Filename: {filename}\n"
                f"🆔 ID: {response.data[0].get('id', 'N/A')}\n"
                f"⭐ Relevancy: {relevancy}\n"
                f"🤖 AI Confidence: {ai_result.get('overall_confidence', 0)}%\n\n"
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

    # Clean up temp file
    temp_path = context.user_data.get('temp_file_path')
    if temp_path and Path(temp_path).exists():
        Path(temp_path).unlink()

    return ConversationHandler.END


async def ask_document_type(update: Update, context: ContextTypes.DEFAULT_TYPE, ai_suggestion: str = None) -> int:
    """Ask for document type (used as fallback when AI fails or is disabled)."""
    keyboard = [[doc_type] for doc_type in DOC_TYPES.values()]
    keyboard.append(['❌ Cancel'])

    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    message = "📝 **What type of document is this?**\n\n"
    if ai_suggestion:
        message += f"💡 AI suggested: {ai_suggestion}\n\n"
    message += "Choose from the options below:"

    await update.message.reply_text(message, reply_markup=reply_markup)

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
            'notes': data['notes'],
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
            AI_REVIEW: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_review)
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
