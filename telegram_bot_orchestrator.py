#!/usr/bin/env python3
"""
Telegram Document Bot - Orchestrator with Human-in-the-Loop
Intelligent agent that asks questions when uncertain and provides previews before commits
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import hashlib
import io
import json
import base64
from typing import Dict, Any, Optional, Tuple, List
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
    from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ConversationHandler,
        ContextTypes,
        CallbackQueryHandler,
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
except ImportError:
    pass

# Claude Vision AI (Tier 2) - Required for orchestration
CLAUDE_AVAILABLE = False
try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    print("⚠️ Claude AI not available - orchestration requires anthropic package")

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
else:
    supabase = None

# Initialize Claude
if CLAUDE_AVAILABLE and ANTHROPIC_API_KEY:
    claude_client = Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    claude_client = None

# Conversation states
(DOCUMENT, PROCESSING, CLARIFICATION, FIELD_EDIT, PREVIEW, FINAL_CONFIRM) = range(6)

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
RELEVANCY_SCORES = {
    'Critical': 920,
    'High': 850,
    'Medium': 750,
    'Low': 650
}


# ==============================================================================
# ORCHESTRATION AGENT - Intelligent Question Asking
# ==============================================================================

class OrchestratorAgent:
    """
    Intelligent orchestration agent that:
    1. Analyzes documents with AI
    2. Identifies uncertainty and gaps
    3. Asks clarifying questions via chat
    4. Provides preview before commit
    5. Handles errors with explanations
    """

    def __init__(self, claude_client, context_data: Dict[str, Any]):
        self.claude = claude_client
        self.context = context_data
        self.uncertainty_threshold = 0.7  # Ask questions if confidence < 70%
        self.clarifications_needed = []
        self.analysis_result = {}

    def analyze_with_uncertainty(self, image_bytes: bytes, user_caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze document and identify areas of uncertainty.

        Returns:
            {
                'analysis': {...},  # Standard analysis
                'confidence': 0.85,
                'uncertain_fields': ['document_date', 'case_number'],
                'questions': [
                    {
                        'field': 'document_date',
                        'question': 'I see two dates (08/04/2024 and 08/15/2024). Which is the document date?',
                        'options': ['20240804', '20240815', 'Unknown'],
                        'reason': 'Multiple dates found in document'
                    }
                ],
                'needs_clarification': True
            }
        """
        if not self.claude:
            return {
                'analysis': {'error': 'Claude not available'},
                'confidence': 0.0,
                'needs_clarification': False
            }

        try:
            # Encode image
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            media_type = "image/jpeg"

            # Advanced prompt that identifies uncertainty
            prompt = f"""You are an intelligent document analysis agent with human-in-the-loop capability.

Analyze this legal document image and provide structured extraction WITH uncertainty indicators.

{"User context: " + user_caption if user_caption else ""}

Return a JSON object with:

1. **analysis**: Standard document analysis
   - document_type: Choose from PLCR, DECL, EVID, CPSR, RESP, FORN, ORDR, MOTN, HEAR, OTHR
   - document_date: YYYYMMDD or "Unknown"
   - title: Concise title (max 80 chars)
   - executive_summary: 2-3 sentence summary
   - extracted_text: Full OCR text
   - relevancy_score: 600-920
   - metadata: {{names: [], case_numbers: [], locations: []}}

2. **confidence**: Overall confidence (0.0-1.0)

3. **field_confidence**: Confidence per field
   {{
     "document_type": 0.95,
     "document_date": 0.40,  // Low confidence = uncertain
     "title": 0.85,
     "relevancy_score": 0.70
   }}

4. **uncertain_fields**: List of fields with confidence < 0.70
   ["document_date", "case_number"]

5. **questions**: Array of clarifying questions to ask user
   [
     {{
       "field": "document_date",
       "question": "I found two dates (08/04/2024 and 08/15/2024). Which is the document date?",
       "options": ["20240804", "20240815", "Unknown"],
       "reason": "Multiple dates found",
       "current_guess": "20240804"
     }}
   ]

6. **ambiguities**: List of issues that need human verification
   [
     "Name 'J. Smith' could be 'John Smith' or 'Jane Smith'",
     "Handwritten text unclear in section 3"
   ]

7. **needs_clarification**: Boolean - true if questions needed

IMPORTANT: Be honest about uncertainty. If you're not confident, ASK! Better to ask than guess wrong.

Return ONLY valid JSON."""

            # Call Claude
            message = self.claude.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
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
                            {"type": "text", "text": prompt}
                        ],
                    }
                ],
            )

            # Parse response
            response_text = message.content[0].text
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)

            result = json.loads(response_text)

            # Store analysis
            self.analysis_result = result
            self.clarifications_needed = result.get('questions', [])

            return result

        except Exception as e:
            print(f"⚠️ Orchestrator analysis failed: {e}")
            return {
                'analysis': {'error': str(e)},
                'confidence': 0.0,
                'needs_clarification': False,
                'questions': []
            }

    def apply_user_answers(self, answers: Dict[str, Any]):
        """
        Update analysis with user-provided answers to clarifying questions.

        Args:
            answers: {'document_date': '20240804', 'case_number': '24-7889'}
        """
        if 'analysis' in self.analysis_result:
            for field, value in answers.items():
                if field in ['document_date', 'document_type', 'title', 'relevancy_score']:
                    self.analysis_result['analysis'][field] = value
                elif field in ['case_numbers', 'names', 'locations']:
                    self.analysis_result['analysis']['metadata'][field] = value

    def generate_preview(self) -> str:
        """
        Generate human-readable preview of what will be committed.
        """
        analysis = self.analysis_result.get('analysis', {})
        confidence = self.analysis_result.get('confidence', 0)

        doc_type = analysis.get('document_type', 'Unknown')
        doc_type_label = DOC_TYPES.get(doc_type, doc_type)

        preview = f"""
📋 **PREVIEW - What Will Be Saved**

🎯 **Overall Confidence:** {int(confidence * 100)}%

📝 **Document Type:** {doc_type_label}
📅 **Date:** {analysis.get('document_date', 'Unknown')}
📌 **Title:** {analysis.get('title', 'Untitled')}
⭐ **Relevancy Score:** {analysis.get('relevancy_score', 650)}

📄 **Summary:**
{analysis.get('executive_summary', 'No summary available')}
"""

        # Show metadata if available
        metadata = analysis.get('metadata', {})
        if metadata.get('case_numbers'):
            preview += f"\n📋 **Case Numbers:** {', '.join(metadata['case_numbers'])}"
        if metadata.get('names'):
            preview += f"\n👤 **Names Mentioned:** {', '.join(metadata['names'][:5])}"
        if metadata.get('locations'):
            preview += f"\n📍 **Locations:** {', '.join(metadata['locations'][:3])}"

        # Show OCR preview
        extracted = analysis.get('extracted_text', '')
        if extracted:
            preview += f"\n\n📝 **OCR Text Preview:**\n{extracted[:200]}..."

        # Show any ambiguities
        ambiguities = self.analysis_result.get('ambiguities', [])
        if ambiguities:
            preview += f"\n\n⚠️ **Notes:**"
            for amb in ambiguities[:3]:
                preview += f"\n  • {amb}"

        return preview

    def explain_error(self, error: Exception) -> str:
        """
        Generate human-friendly explanation of errors.
        """
        error_str = str(error).lower()

        if 'duplicate' in error_str or 'hash' in error_str:
            return (
                "🔄 **Duplicate Detected**\n\n"
                "This document appears to be identical to one already uploaded.\n\n"
                "Options:\n"
                "1. Skip upload (keep existing)\n"
                "2. Upload anyway (mark as version)\n"
                "3. Replace existing document"
            )
        elif 'column' in error_str or 'field' in error_str:
            return (
                "💾 **Database Schema Issue**\n\n"
                "The database doesn't have the expected field structure.\n\n"
                f"Technical details: {error}\n\n"
                "This might need database migration or schema update."
            )
        elif 'storage' in error_str or 'upload' in error_str:
            return (
                "☁️ **Storage Upload Failed**\n\n"
                "Could not save image to cloud storage.\n\n"
                "Possible causes:\n"
                "• Storage bucket not created\n"
                "• Network connection issue\n"
                "• File size too large\n\n"
                "The metadata was saved, but image upload failed."
            )
        elif 'permission' in error_str or 'unauthorized' in error_str:
            return (
                "🔒 **Permission Denied**\n\n"
                "Your API key doesn't have permission for this operation.\n\n"
                "You may need to:\n"
                "• Check storage bucket is public\n"
                "• Verify API key has correct permissions\n"
                "• Update RLS policies in Supabase"
            )
        else:
            return (
                f"❌ **Unexpected Error**\n\n"
                f"{error}\n\n"
                f"Please check logs or try again."
            )


# ==============================================================================
# STORAGE FUNCTIONS
# ==============================================================================

def extract_text_tesseract(image_bytes: bytes) -> Optional[str]:
    """Tier 1: Tesseract OCR"""
    if not TESSERACT_AVAILABLE:
        return None
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip() if text else None
    except Exception as e:
        return None


def upload_to_supabase_storage(
    image_bytes: bytes,
    filename: str,
    bucket: str = "documents"
) -> Tuple[Optional[str], Optional[str]]:
    """Upload image to Supabase Storage with thumbnail"""
    if not supabase:
        return None, None

    try:
        # Upload original
        original_path = f"originals/{filename}"
        supabase.storage.from_(bucket).upload(
            path=original_path,
            file=image_bytes,
            file_options={"content-type": "image/jpeg"}
        )
        original_url = supabase.storage.from_(bucket).get_public_url(original_path)

        # Create thumbnail
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.thumbnail((200, 200), Image.Resampling.LANCZOS)
            thumb_bytes = io.BytesIO()
            img.save(thumb_bytes, format='JPEG', quality=85)
            thumb_bytes.seek(0)

            thumb_filename = filename.replace('.', '_thumb.')
            thumb_path = f"thumbnails/{thumb_filename}"
            supabase.storage.from_(bucket).upload(
                path=thumb_path,
                file=thumb_bytes.getvalue(),
                file_options={"content-type": "image/jpeg"}
            )
            thumbnail_url = supabase.storage.from_(bucket).get_public_url(thumb_path)
        except:
            thumbnail_url = original_url

        return original_url, thumbnail_url
    except Exception as e:
        print(f"❌ Storage upload failed: {e}")
        return None, None


# ==============================================================================
# TELEGRAM BOT HANDLERS WITH ORCHESTRATION
# ==============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation."""
    welcome = (
        "🤖 **ASEAGI Smart Document Bot**\n"
        "*(with Human-in-the-Loop Orchestration)*\n\n"
        "I'll analyze your documents and **ask questions when uncertain**.\n\n"
        "📸 **Send me a document image** (with optional caption)\n\n"
        "I will:\n"
        "1. Analyze with AI\n"
        "2. Ask clarifying questions if needed\n"
        "3. Show preview before saving\n"
        "4. Let you edit any field\n\n"
        "Let's get started! Send a document image."
    )

    await update.message.reply_text(welcome, reply_markup=ReplyKeyboardRemove())
    return DOCUMENT


async def receive_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive document and start orchestrated analysis."""

    if not update.message.photo and not update.message.document:
        await update.message.reply_text(
            "❌ Please send an image or document file.\n\n"
            "Use /cancel to start over."
        )
        return DOCUMENT

    # Get caption
    caption = update.message.caption if update.message.caption else None

    await update.message.reply_text(
        "🔍 **Analyzing document with AI...**\n\n"
        "I'll identify what I'm confident about and what I need to ask you.\n\n"
        "⏳ This takes ~10-15 seconds..."
    )

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

        # Store for later
        context.user_data['file_object'] = file
        context.user_data['file_bytes'] = image_bytes

        # Create orchestrator
        orchestrator = OrchestratorAgent(claude_client, context.user_data)
        context.user_data['orchestrator'] = orchestrator

        # Analyze with uncertainty detection
        result = orchestrator.analyze_with_uncertainty(image_bytes, caption)

        # Try Tesseract OCR as well
        tesseract_text = extract_text_tesseract(image_bytes)
        if tesseract_text:
            # Merge if Claude didn't get much text
            if len(result.get('analysis', {}).get('extracted_text', '')) < 100:
                result['analysis']['extracted_text'] = tesseract_text

        confidence = result.get('confidence', 0)
        needs_clarification = result.get('needs_clarification', False)
        questions = result.get('questions', [])

        # Show initial analysis
        analysis = result.get('analysis', {})
        doc_type = analysis.get('document_type', 'OTHR')
        doc_type_label = DOC_TYPES.get(doc_type, 'Unknown')

        response_msg = (
            f"✅ **Initial Analysis Complete**\n\n"
            f"🎯 **My Confidence:** {int(confidence * 100)}%\n\n"
            f"📝 **Document Type:** {doc_type_label}\n"
            f"📅 **Date:** {analysis.get('document_date', 'Unknown')}\n"
            f"📌 **Title:** {analysis.get('title', 'Unknown')}\n"
            f"⭐ **Relevancy:** {analysis.get('relevancy_score', 650)}\n\n"
        )

        # If needs clarification, ask questions
        if needs_clarification and questions:
            response_msg += (
                "🤔 **I have some questions to improve accuracy:**\n\n"
            )

            # Store questions for next state
            context.user_data['pending_questions'] = questions
            context.user_data['current_question_idx'] = 0
            context.user_data['user_answers'] = {}

            # Ask first question
            first_q = questions[0]
            response_msg += f"**Question 1 of {len(questions)}:**\n\n"
            response_msg += f"{first_q['question']}\n\n"
            response_msg += f"*Reason: {first_q.get('reason', 'Need clarification')}*\n\n"

            # Create keyboard with options
            if first_q.get('options'):
                keyboard = [[opt] for opt in first_q['options']]
                keyboard.append(['Skip this question'])
                reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            else:
                reply_markup = ReplyKeyboardMarkup([['Skip this question']], one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(response_msg, reply_markup=reply_markup)
            return CLARIFICATION

        else:
            # High confidence, go straight to preview
            response_msg += "✨ **High confidence - no questions needed!**\n\n"
            response_msg += "Preparing preview..."

            await update.message.reply_text(response_msg)

            # Show preview
            preview = orchestrator.generate_preview()
            preview += "\n\n**What would you like to do?**"

            keyboard = [
                ['✅ Looks good - Upload now'],
                ['✏️ Edit a field'],
                ['❌ Cancel']
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            await update.message.reply_text(preview, reply_markup=reply_markup)
            return PREVIEW

    except Exception as e:
        error_explanation = "❌ **Analysis Failed**\n\n" + str(e)
        await update.message.reply_text(error_explanation)
        return ConversationHandler.END


async def handle_clarification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user answers to clarifying questions."""

    answer = update.message.text.strip()
    questions = context.user_data.get('pending_questions', [])
    current_idx = context.user_data.get('current_question_idx', 0)
    user_answers = context.user_data.get('user_answers', {})

    if current_idx >= len(questions):
        # No more questions, go to preview
        return await show_preview(update, context)

    current_q = questions[current_idx]

    # Store answer (unless skipped)
    if answer != 'Skip this question':
        user_answers[current_q['field']] = answer
        context.user_data['user_answers'] = user_answers

    # Move to next question
    current_idx += 1
    context.user_data['current_question_idx'] = current_idx

    if current_idx < len(questions):
        # Ask next question
        next_q = questions[current_idx]
        msg = f"**Question {current_idx + 1} of {len(questions)}:**\n\n"
        msg += f"{next_q['question']}\n\n"
        msg += f"*Reason: {next_q.get('reason', 'Need clarification')}*\n\n"

        if next_q.get('options'):
            keyboard = [[opt] for opt in next_q['options']]
            keyboard.append(['Skip this question'])
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        else:
            reply_markup = ReplyKeyboardMarkup([['Skip this question']], one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(msg, reply_markup=reply_markup)
        return CLARIFICATION
    else:
        # All questions answered, apply answers and show preview
        orchestrator = context.user_data.get('orchestrator')
        if orchestrator:
            orchestrator.apply_user_answers(user_answers)

        return await show_preview(update, context)


async def show_preview(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show preview of what will be saved."""

    orchestrator = context.user_data.get('orchestrator')
    if not orchestrator:
        await update.message.reply_text("❌ Error: Lost orchestrator context")
        return ConversationHandler.END

    preview = orchestrator.generate_preview()
    preview += "\n\n**What would you like to do?**"

    keyboard = [
        ['✅ Looks good - Upload now'],
        ['✏️ Edit a field'],
        ['❌ Cancel']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(preview, reply_markup=reply_markup)
    return PREVIEW


async def handle_preview_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle user's choice from preview."""

    choice = update.message.text.strip()

    if 'Upload now' in choice or '✅' in choice:
        return await commit_to_database(update, context)

    elif 'Edit' in choice or '✏️' in choice:
        # Show field edit options
        msg = "**Which field would you like to edit?**"
        keyboard = [
            ['Document Type'],
            ['Document Date'],
            ['Title'],
            ['Summary/Notes'],
            ['Relevancy Score'],
            ['❌ Cancel edit - Go back to preview']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(msg, reply_markup=reply_markup)
        return FIELD_EDIT

    else:
        await update.message.reply_text(
            "❌ Upload cancelled.\n\n"
            "Use /start to upload another document."
        )
        return ConversationHandler.END


async def handle_field_edit_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle which field user wants to edit."""

    field = update.message.text.strip()

    if 'Cancel' in field or '❌' in field:
        return await show_preview(update, context)

    context.user_data['editing_field'] = field

    # Ask for new value
    if 'Document Type' in field:
        msg = "**Choose document type:**"
        keyboard = [[f"{code} - {label}"] for code, label in DOC_TYPES.items()]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    elif 'Document Date' in field:
        msg = "**Enter document date:**\n\nFormat: YYYYMMDD (e.g., 20240804)\nOr type: Unknown"
        reply_markup = ReplyKeyboardMarkup([['Unknown']], one_time_keyboard=True, resize_keyboard=True)
    elif 'Title' in field:
        msg = "**Enter new title:**"
        reply_markup = ReplyKeyboardRemove()
    elif 'Summary' in field or 'Notes' in field:
        msg = "**Enter new summary/notes:**"
        reply_markup = ReplyKeyboardRemove()
    elif 'Relevancy' in field:
        msg = "**Choose relevancy score:**"
        keyboard = [['Critical (920)'], ['High (850)'], ['Medium (750)'], ['Low (650)']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    else:
        msg = "Enter new value:"
        reply_markup = ReplyKeyboardRemove()

    await update.message.reply_text(msg, reply_markup=reply_markup)
    return FIELD_EDIT


async def commit_to_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Commit document to database with error handling."""

    await update.message.reply_text("⏳ **Uploading to database and storage...**")

    try:
        orchestrator = context.user_data.get('orchestrator')
        if not orchestrator or not supabase:
            raise Exception("Missing orchestrator or Supabase connection")

        analysis = orchestrator.analysis_result.get('analysis', {})
        image_bytes = context.user_data['file_bytes']

        # Generate filename
        doc_type = analysis.get('document_type', 'OTHR')
        doc_date = analysis.get('document_date', 'Unknown')
        title_slug = analysis.get('title', 'Document')[:50].replace(' ', '_').replace('/', '_')
        relevancy = analysis.get('relevancy_score', 650)

        file_ext = 'jpg' if context.user_data['file_type'] == 'photo' else 'jpg'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{doc_date}_{doc_type}_{title_slug}_REL-{relevancy}_{timestamp}.{file_ext}"

        # Calculate hash
        file_hash = hashlib.md5(image_bytes).hexdigest()

        # Check duplicates
        dup_check = supabase.table('legal_documents').select('id', 'original_filename').eq('file_hash', file_hash).execute()
        if dup_check.data:
            await update.message.reply_text(
                f"⚠️ **Possible duplicate found:**\n\n"
                f"Existing: {dup_check.data[0]['original_filename']}\n\n"
                f"Uploading anyway with timestamp..."
            )

        # Upload to storage
        original_url, thumbnail_url = upload_to_supabase_storage(image_bytes, filename)

        # Prepare data
        document_data = {
            'original_filename': filename,
            'document_type': doc_type,
            'document_title': analysis.get('title', 'Untitled'),
            'document_date': doc_date,
            'relevancy_number': relevancy,
            'file_extension': file_ext,
            'executive_summary': analysis.get('executive_summary', ''),
            'full_text_content': analysis.get('extracted_text', ''),
            'created_at': datetime.now().isoformat(),
            'file_hash': file_hash,
            'source': 'telegram_bot_orchestrator',
            'uploaded_via': 'phone_ai_assisted',
            'file_path': original_url,
            'thumbnail_path': thumbnail_url,
            'ai_confidence': orchestrator.analysis_result.get('confidence', 0)
        }

        # Add metadata
        metadata = analysis.get('metadata', {})
        if metadata:
            document_data['ai_metadata'] = json.dumps(metadata)

        # Insert to database
        response = supabase.table('legal_documents').insert(document_data).execute()

        if response.data:
            doc_id = response.data[0].get('id', 'N/A')

            success_msg = (
                "✅ **Upload Successful!**\n\n"
                f"🆔 **Database ID:** {doc_id}\n"
                f"📄 **Filename:** {filename}\n"
                f"🎯 **AI Confidence:** {int(orchestrator.analysis_result.get('confidence', 0) * 100)}%\n\n"
            )

            if original_url:
                success_msg += f"🔗 **URL:** {original_url[:60]}...\n\n"

            success_msg += "✨ Your document is now saved!\n\nUse /start to upload another."

            await update.message.reply_text(success_msg, reply_markup=ReplyKeyboardRemove())
        else:
            raise Exception("No data returned from database")

    except Exception as e:
        # Use orchestrator to explain error
        orchestrator = context.user_data.get('orchestrator')
        if orchestrator:
            error_msg = orchestrator.explain_error(e)
        else:
            error_msg = f"❌ **Upload failed:**\n\n{str(e)}"

        await update.message.reply_text(error_msg)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    await update.message.reply_text(
        "❌ Upload cancelled.\n\nUse /start to upload a document.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    """Start the orchestrated bot."""

    if not TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        sys.exit(1)

    print("\n" + "="*70)
    print("🤖 ASEAGI Telegram Bot - Orchestrator (Human-in-the-Loop)")
    print("="*70)
    print(f"✅ Tier 1 OCR: {'Enabled' if TESSERACT_AVAILABLE else 'Disabled (optional)'}")
    print(f"✅ Tier 2 AI: {'Enabled' if claude_client else 'DISABLED - Required!'}")
    print(f"✅ Storage: {'Enabled' if supabase else 'Disabled'}")
    print(f"✅ Orchestration: {'Enabled' if claude_client else 'Disabled'}")
    print("="*70 + "\n")

    if not claude_client:
        print("⚠️ WARNING: Claude AI required for orchestration!")
        print("   Add ANTHROPIC_API_KEY to secrets.toml\n")

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler with orchestration states
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DOCUMENT: [MessageHandler(filters.PHOTO | filters.Document.ALL, receive_document)],
            CLARIFICATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_clarification)],
            PREVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_preview_choice)],
            FIELD_EDIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_field_edit_choice)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)

    print("✅ Orchestrator bot is running! Press Ctrl+C to stop.\n")
    print("Features:")
    print("  • AI asks clarifying questions when uncertain")
    print("  • Preview before commit")
    print("  • Edit any field before upload")
    print("  • Human-friendly error explanations\n")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
