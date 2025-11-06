#!/usr/bin/env python3
"""
Telegram Document Ingestion Bot - Enhanced with Tiered OCR and Storage
Tier 1: Tesseract OCR (fast, free, basic text extraction)
Tier 2: Claude Vision AI (intelligent analysis, metadata extraction)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import io
import json
import base64
from typing import Dict, Any, Optional, Tuple
import re

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

# PIL for image processing
try:
    from PIL import Image
except ImportError:
    print("❌ Please install: pip install pillow")
    sys.exit(1)

# Tesseract OCR (Tier 1) - Optional
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract OCR available (Tier 1)")
except ImportError:
    print("⚠️ Tesseract not available - will use Claude Vision only")

# Claude Vision AI (Tier 2) - Optional but recommended
CLAUDE_AVAILABLE = False
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
    print("✅ Claude Vision AI available (Tier 2)")
except ImportError:
    print("⚠️ Claude Vision not available - limited analysis")

# Load credentials
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')

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
            ANTHROPIC_API_KEY = secrets.get('ANTHROPIC_API_KEY')
    except:
        pass

# Initialize Supabase
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✅ Supabase connected: {SUPABASE_URL}")
else:
    print("⚠️ Warning: Supabase credentials not found")
    supabase = None

# Initialize Claude
if CLAUDE_AVAILABLE and ANTHROPIC_API_KEY:
    claude_client = Anthropic(api_key=ANTHROPIC_API_KEY)
    print("✅ Claude Vision AI initialized")
else:
    claude_client = None
    print("⚠️ Claude Vision not initialized")

# Conversation states
(UPLOAD_MODE, DOCUMENT, DOC_TYPE, DOC_DATE, TITLE, NOTES, RELEVANCY, CONFIRM) = range(8)

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


# ==============================================================================
# TIER 1: TESSERACT OCR - Fast, Free, Basic Text Extraction
# ==============================================================================

def extract_text_tesseract(image_bytes: bytes) -> Optional[str]:
    """
    Tier 1: Extract text using Tesseract OCR
    Returns: Raw text or None if fails
    """
    if not TESSERACT_AVAILABLE:
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip() if text else None
    except Exception as e:
        print(f"⚠️ Tesseract OCR failed: {e}")
        return None


# ==============================================================================
# TIER 2: CLAUDE VISION AI - Intelligent Analysis & Metadata Extraction
# ==============================================================================

def analyze_document_claude(image_bytes: bytes, caption: Optional[str] = None) -> Dict[str, Any]:
    """
    Tier 2: Intelligent document analysis using Claude Vision AI

    Returns:
        {
            'document_type': 'PLCR',
            'document_date': '20240804',
            'title': 'Sexual Assault Report - Richmond PD',
            'executive_summary': 'Police report documenting...',
            'extracted_text': 'Full OCR text...',
            'relevancy_score': 920,
            'confidence': 0.95,
            'metadata': {
                'names': ['John Doe'],
                'case_numbers': ['24-7889'],
                'locations': ['Richmond']
            }
        }
    """
    if not CLAUDE_AVAILABLE or not claude_client:
        return {
            'document_type': 'OTHR',
            'document_date': 'Unknown',
            'title': caption if caption else 'Unknown Document',
            'executive_summary': caption if caption else 'No AI analysis available',
            'relevancy_score': 650,
            'confidence': 0.0
        }

    try:
        # Encode image to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        # Determine media type
        media_type = "image/jpeg"  # default
        try:
            img = Image.open(io.BytesIO(image_bytes))
            if img.format == 'PNG':
                media_type = "image/png"
            elif img.format in ['JPG', 'JPEG']:
                media_type = "image/jpeg"
        except:
            pass

        # Build prompt
        user_context = f"\n\nUser provided context: {caption}" if caption else ""

        prompt = f"""Analyze this legal document image and extract structured information.{user_context}

Return a JSON object with these fields:

1. document_type: Choose ONE from: PLCR (Police Report), DECL (Declaration), EVID (Evidence/Photo), CPSR (CPS Report), RESP (Response), FORN (Forensic Report), ORDR (Court Order), MOTN (Motion), HEAR (Hearing Transcript), OTHR (Other)

2. document_date: Extract the document date in YYYYMMDD format (e.g., 20240804). If no clear date found, return "Unknown".

3. title: Create a concise descriptive title (max 80 chars). Include agency/department if visible.

4. executive_summary: 2-3 sentence summary of the document's content and significance.

5. extracted_text: Full OCR text extraction from the image. Extract ALL visible text.

6. relevancy_score: Score 600-920 based on:
   - Sexual assault/abuse allegations: 900-920
   - Court orders, restraining orders: 850-900
   - Police reports (general): 800-850
   - Medical/forensic reports: 800-850
   - Administrative documents: 700-800
   - Other: 600-700

7. confidence: Your confidence in the analysis (0.0-1.0)

8. metadata: Object with:
   - names: Array of person names mentioned (if any)
   - case_numbers: Array of case/report numbers found
   - locations: Array of locations mentioned
   - incident_date: Date of incident if different from document date (YYYYMMDD or null)

Return ONLY valid JSON, no markdown or explanation."""

        # Call Claude Vision API
        message = claude_client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # Parse response
        response_text = message.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)

        result = json.loads(response_text)

        # Validate and set defaults
        result.setdefault('document_type', 'OTHR')
        result.setdefault('document_date', 'Unknown')
        result.setdefault('title', 'Unknown Document')
        result.setdefault('executive_summary', 'No summary available')
        result.setdefault('relevancy_score', 650)
        result.setdefault('confidence', 0.0)
        result.setdefault('extracted_text', '')

        return result

    except Exception as e:
        print(f"⚠️ Claude Vision analysis failed: {e}")
        return {
            'document_type': 'OTHR',
            'document_date': 'Unknown',
            'title': caption if caption else 'Analysis Failed',
            'executive_summary': f"AI analysis error: {str(e)[:100]}",
            'relevancy_score': 650,
            'confidence': 0.0,
            'error': str(e)
        }


# ==============================================================================
# SUPABASE STORAGE - Image Storage with Thumbnails
# ==============================================================================

def upload_to_supabase_storage(
    image_bytes: bytes,
    filename: str,
    bucket: str = "documents"
) -> Tuple[Optional[str], Optional[str]]:
    """
    Upload image to Supabase Storage and create thumbnail

    Returns:
        (original_url, thumbnail_url) or (None, None) if fails
    """
    if not supabase:
        return None, None

    try:
        # Upload original image
        original_path = f"originals/{filename}"
        supabase.storage.from_(bucket).upload(
            path=original_path,
            file=image_bytes,
            file_options={"content-type": "image/jpeg"}
        )

        # Get public URL for original
        original_url = supabase.storage.from_(bucket).get_public_url(original_path)

        # Create thumbnail (200x200)
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)

            thumb_bytes = io.BytesIO()
            img.save(thumb_bytes, format='JPEG', quality=85)
            thumb_bytes.seek(0)

            # Upload thumbnail
            thumb_filename = filename.replace('.', '_thumb.')
            thumb_path = f"thumbnails/{thumb_filename}"
            supabase.storage.from_(bucket).upload(
                path=thumb_path,
                file=thumb_bytes.getvalue(),
                file_options={"content-type": "image/jpeg"}
            )

            thumbnail_url = supabase.storage.from_(bucket).get_public_url(thumb_path)
        except Exception as e:
            print(f"⚠️ Thumbnail creation failed: {e}")
            thumbnail_url = original_url

        return original_url, thumbnail_url

    except Exception as e:
        print(f"❌ Storage upload failed: {e}")
        return None, None


# ==============================================================================
# TELEGRAM BOT HANDLERS
# ==============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation and choose upload mode."""
    welcome = (
        "🤖 **ASEAGI Document Upload Bot**\n\n"
        "Choose upload mode:\n\n"
        "1️⃣ **Smart Quick Upload** (Recommended)\n"
        "   • Send image with caption\n"
        "   • AI analyzes automatically\n"
        "   • Confirm and done!\n\n"
        "2️⃣ **Detailed Manual Entry**\n"
        "   • Step-by-step form\n"
        "   • Full control over metadata\n"
        "   • 7-step process\n\n"
        "Which mode do you prefer?"
    )

    keyboard = [
        ['1️⃣ Smart Quick Upload'],
        ['2️⃣ Detailed Manual Entry']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(welcome, reply_markup=reply_markup)

    return UPLOAD_MODE


async def choose_mode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store upload mode and request document."""
    mode = update.message.text

    if '1️⃣' in mode or 'Smart' in mode or 'Quick' in mode:
        context.user_data['upload_mode'] = 'smart'

        await update.message.reply_text(
            "📸 **Smart Quick Upload Mode**\n\n"
            "Send me your document image with a caption describing it.\n\n"
            "Example caption:\n"
            "\"Richmond PD 24-7889 - Initial sexual assault report\"\n\n"
            "The AI will analyze the image and extract:\n"
            "• Document type\n"
            "• Dates\n"
            "• Key information\n"
            "• Relevancy score\n\n"
            "You can then confirm or edit before uploading.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        context.user_data['upload_mode'] = 'detailed'

        await update.message.reply_text(
            "📋 **Detailed Manual Entry Mode**\n\n"
            "I'll guide you through each field step-by-step.\n\n"
            "📷 Send me a document (photo or file):",
            reply_markup=ReplyKeyboardRemove()
        )

    return DOCUMENT


async def receive_document_smart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Smart mode: Receive document and analyze with AI."""

    # Check if image is provided
    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "❌ Please send an image or document file.\n\n"
            "Use /cancel to start over."
        )
        return DOCUMENT

    # Get caption (user's description)
    caption = update.message.caption if update.message.caption else None

    await update.message.reply_text("🔍 Analyzing document with AI...\n\nThis may take 10-15 seconds...")

    try:
        # Download file
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            context.user_data['file_type'] = 'photo'
        else:
            file = await update.message.document.get_file()
            context.user_data['file_type'] = 'document'
            context.user_data['file_name'] = update.message.document.file_name

        # Download to memory
        file_bytes = io.BytesIO()
        await file.download_to_memory(file_bytes)
        file_bytes.seek(0)
        image_bytes = file_bytes.getvalue()

        # Store for later upload
        context.user_data['file_object'] = file
        context.user_data['file_bytes'] = image_bytes

        # TIER 1: Try Tesseract first (fast)
        tesseract_text = extract_text_tesseract(image_bytes)
        if tesseract_text:
            print(f"✅ Tier 1 (Tesseract): Extracted {len(tesseract_text)} characters")

        # TIER 2: Claude Vision for intelligent analysis
        analysis = analyze_document_claude(image_bytes, caption)

        # Merge Tesseract text if Claude didn't extract much
        if tesseract_text and len(analysis.get('extracted_text', '')) < 100:
            analysis['extracted_text'] = tesseract_text

        # Store analysis results
        context.user_data['ai_analysis'] = analysis
        context.user_data['doc_type'] = analysis['document_type']
        context.user_data['doc_date'] = analysis['document_date']
        context.user_data['title'] = analysis['title']
        context.user_data['notes'] = analysis['executive_summary']
        context.user_data['relevancy_score'] = analysis['relevancy_score']
        context.user_data['full_text_content'] = analysis.get('extracted_text', '')

        # Show analysis results
        doc_type_label = DOC_TYPES.get(analysis['document_type'], 'Unknown')
        confidence_pct = int(analysis.get('confidence', 0) * 100)

        result_msg = (
            "✅ **AI Analysis Complete!**\n\n"
            f"🤖 **Confidence:** {confidence_pct}%\n\n"
            f"📝 **Document Type:** {doc_type_label}\n"
            f"📅 **Date:** {analysis['document_date']}\n"
            f"📌 **Title:** {analysis['title']}\n"
            f"⭐ **Relevancy Score:** {analysis['relevancy_score']}\n\n"
            f"📄 **Summary:**\n{analysis['executive_summary']}\n\n"
        )

        # Show extracted metadata if available
        metadata = analysis.get('metadata', {})
        if metadata:
            if metadata.get('case_numbers'):
                result_msg += f"📋 **Case Numbers:** {', '.join(metadata['case_numbers'])}\n"
            if metadata.get('names'):
                result_msg += f"👤 **Names:** {', '.join(metadata['names'][:3])}\n"

        result_msg += (
            "\n\n"
            "✅ Type **YES** to upload with this analysis\n"
            "✏️ Type **EDIT** to manually adjust fields\n"
            "❌ Type **NO** to cancel"
        )

        await update.message.reply_text(result_msg)

        return CONFIRM

    except Exception as e:
        await update.message.reply_text(
            f"❌ **Analysis failed:**\n\n"
            f"{str(e)}\n\n"
            f"Use /start to try detailed mode instead."
        )
        return ConversationHandler.END


async def receive_document_detailed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Detailed mode: Store document and ask for type."""

    if update.message.photo:
        file = await update.message.photo[-1].get_file()
        context.user_data['file_type'] = 'photo'
        context.user_data['file_object'] = file
    elif update.message.document:
        file = await update.message.document.get_file()
        context.user_data['file_type'] = 'document'
        context.user_data['file_name'] = update.message.document.file_name
        context.user_data['file_object'] = file
    else:
        await update.message.reply_text(
            "❌ Please send a photo or document file.\n\n"
            "Use /cancel to start over."
        )
        return DOCUMENT

    # Download file bytes for later processing
    file_bytes = io.BytesIO()
    await file.download_to_memory(file_bytes)
    file_bytes.seek(0)
    context.user_data['file_bytes'] = file_bytes.getvalue()

    # Ask for document type
    keyboard = [[f"{code} - {label}"] for code, label in DOC_TYPES.items()]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "✅ Document received!\n\n"
        "📝 **What type of document is this?**",
        reply_markup=reply_markup
    )

    return DOC_TYPE


async def receive_doc_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store document type and ask for date."""
    doc_type = update.message.text.split()[0]
    context.user_data['doc_type'] = doc_type

    keyboard = [['Unknown']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        f"✅ Type: {DOC_TYPES.get(doc_type, doc_type)}\n\n"
        f"📅 **What is the document date?**\n\n"
        f"Format: YYYYMMDD (e.g., 20240804)\n"
        f"Or type **Unknown** if no date available",
        reply_markup=reply_markup
    )

    return DOC_DATE


async def receive_doc_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store document date and ask for title."""
    doc_date = update.message.text.strip()

    # Validate date format or accept "Unknown"
    if doc_date.upper() == 'UNKNOWN':
        context.user_data['doc_date'] = 'Unknown'
    elif len(doc_date) == 8 and doc_date.isdigit():
        context.user_data['doc_date'] = doc_date
    else:
        await update.message.reply_text(
            "❌ Invalid date format!\n\n"
            "Please use YYYYMMDD (e.g., 20240804) or type 'Unknown'"
        )
        return DOC_DATE

    await update.message.reply_text(
        f"✅ Date: {doc_date}\n\n"
        f"📌 **Give this document a title:**\n\n"
        f"Example: \"Initial Sexual Assault Report - Richmond PD\"",
        reply_markup=ReplyKeyboardRemove()
    )

    return TITLE


async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store title and ask for notes."""
    title = update.message.text.strip()
    context.user_data['title'] = title

    await update.message.reply_text(
        f"✅ Title: {title}\n\n"
        f"💬 **Add notes or description:**\n\n"
        f"What's important about this document?"
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

    # Try to extract text with Tesseract if not already done
    if 'full_text_content' not in context.user_data:
        image_bytes = context.user_data.get('file_bytes')
        if image_bytes:
            tesseract_text = extract_text_tesseract(image_bytes)
            if tesseract_text:
                context.user_data['full_text_content'] = tesseract_text

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

    if confirmation not in ['YES', 'Y']:
        await update.message.reply_text(
            "❌ Upload cancelled.\n\n"
            "Use /start to begin a new upload."
        )
        return ConversationHandler.END

    # Upload to Supabase
    await update.message.reply_text("⏳ Uploading to database and storage...")

    try:
        if not supabase:
            raise Exception("Supabase not configured")

        data = context.user_data

        # Get file bytes
        image_bytes = data['file_bytes']

        # Generate filename
        doc_type = data['doc_type']
        doc_date = data['doc_date']
        title_slug = data['title'][:50].replace(' ', '_').replace('/', '_')
        relevancy = data['relevancy_score']

        file_ext = 'jpg' if data['file_type'] == 'photo' else data.get('file_name', 'file').split('.')[-1]

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{doc_date}_{doc_type}_{title_slug}_REL-{relevancy}_{timestamp}.{file_ext}"

        # Calculate file hash for duplicate detection
        file_hash = hashlib.md5(image_bytes).hexdigest()

        # Check for duplicates
        dup_check = supabase.table('legal_documents').select('id', 'original_filename').eq('file_hash', file_hash).execute()
        if dup_check.data:
            await update.message.reply_text(
                f"⚠️ **Possible duplicate found!**\n\n"
                f"Existing file: {dup_check.data[0]['original_filename']}\n\n"
                f"Uploading anyway with unique timestamp..."
            )

        # Upload to Supabase Storage
        original_url, thumbnail_url = upload_to_supabase_storage(image_bytes, filename)

        if not original_url:
            raise Exception("Failed to upload to storage")

        # Prepare document data
        document_data = {
            'original_filename': filename,
            'document_type': doc_type,
            'document_title': data['title'],
            'relevancy_number': relevancy,
            'file_extension': file_ext,
            'executive_summary': data['notes'],
            'document_date': doc_date,
            'created_at': datetime.now().isoformat(),
            'file_hash': file_hash,
            'source': 'telegram_bot',
            'uploaded_via': 'phone',
            'file_path': original_url,
            'thumbnail_path': thumbnail_url
        }

        # Add full text if extracted
        if 'full_text_content' in data:
            document_data['full_text_content'] = data['full_text_content']

        # Add AI metadata if available
        if 'ai_analysis' in data:
            ai_meta = data['ai_analysis'].get('metadata', {})
            if ai_meta:
                document_data['ai_metadata'] = json.dumps(ai_meta)

        # Insert into legal_documents table
        response = supabase.table('legal_documents').insert(document_data).execute()

        if response.data:
            doc_id = response.data[0].get('id', 'N/A')

            result_msg = (
                "✅ **Document uploaded successfully!**\n\n"
                f"📄 **Filename:** {filename}\n"
                f"🆔 **ID:** {doc_id}\n"
                f"⭐ **Relevancy:** {relevancy}\n"
                f"🔗 **URL:** {original_url[:60]}...\n\n"
                f"Your document is now in the database!\n\n"
            )

            # Show what was extracted
            if 'full_text_content' in data:
                text_preview = data['full_text_content'][:150]
                result_msg += f"📝 **OCR Text Preview:**\n{text_preview}...\n\n"

            result_msg += "Use /start to upload another document."

            await update.message.reply_text(result_msg)
        else:
            raise Exception("No data returned from database")

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


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Start the bot."""

    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment or secrets.toml")
        sys.exit(1)

    print("\n" + "="*60)
    print("🤖 Starting ASEAGI Telegram Document Bot (Enhanced)")
    print("="*60)
    print(f"✅ Tier 1 OCR: {'Enabled (Tesseract)' if TESSERACT_AVAILABLE else 'Disabled'}")
    print(f"✅ Tier 2 AI: {'Enabled (Claude Vision)' if CLAUDE_AVAILABLE and claude_client else 'Disabled'}")
    print(f"✅ Storage: {'Enabled (Supabase)' if supabase else 'Disabled'}")
    print("="*60 + "\n")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            UPLOAD_MODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_mode)],
            DOCUMENT: [
                MessageHandler(
                    (filters.PHOTO | filters.Document.ALL) & ~filters.COMMAND,
                    lambda u, c: receive_document_smart(u, c) if c.user_data.get('upload_mode') == 'smart' else receive_document_detailed(u, c)
                )
            ],
            DOC_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_doc_type)],
            DOC_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_doc_date)],
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
            NOTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_notes)],
            RELEVANCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_relevancy)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_upload)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    # Start bot
    print("✅ Bot is running! Press Ctrl+C to stop.\n")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
