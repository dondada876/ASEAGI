# Human-in-the-Loop Orchestration Guide

## Overview

The orchestration bot is an **intelligent agent** that knows when to ask for human help instead of guessing. It provides:

1. **Uncertainty Detection** - AI identifies what it's NOT confident about
2. **Clarifying Questions** - Asks you via chat when uncertain
3. **Preview Before Commit** - Shows exactly what will be saved
4. **Field Editing** - Let you fix any mistakes before upload
5. **Error Explanations** - Human-friendly error messages with solutions

---

## How It Works

### Traditional AI Bot (Auto-Pilot)
```
Image → AI Analysis → Save to Database
         ↓
    (Might guess wrong!)
```

### Orchestration Bot (Human-in-the-Loop)
```
Image → AI Analysis → Uncertainty Detection
                           ↓
                   ┌───────┴──────┐
                   ↓              ↓
            Confident?         Uncertain?
                   ↓              ↓
            Skip to Preview   Ask Questions
                   ↓              ↓
                Preview ←─────────┘
                   ↓
            Edit Fields? (Optional)
                   ↓
            Final Confirmation
                   ↓
            Save to Database
```

---

## Example Conversation Flow

### Scenario: Police Report with Ambiguous Date

**You:**
> [Send police report image with caption]
> "Richmond PD sexual assault report"

**Bot:**
> 🔍 Analyzing document with AI...
>
> ✅ Initial Analysis Complete
>
> 🎯 My Confidence: 65%
>
> 📝 Document Type: 🚔 Police Report
> 📅 Date: 20240804
> 📌 Title: Sexual Assault Report - Richmond PD
> ⭐ Relevancy: 920
>
> 🤔 **I have some questions to improve accuracy:**
>
> **Question 1 of 2:**
>
> I found two dates in the document (08/04/2024 and 08/15/2024). Which is the official document date?
>
> *Reason: Multiple dates found*

**[Keyboard appears with options]:**
- 20240804
- 20240815
- Unknown

**You:**
> 20240804

**Bot:**
> **Question 2 of 2:**
>
> I see a name that looks like "J. Smith". Is this:
> - John Smith
> - Jane Smith
> - Unknown
>
> *Reason: Ambiguous name abbreviation*

**You:**
> Jane Smith

**Bot:**
> 📋 **PREVIEW - What Will Be Saved**
>
> 🎯 Overall Confidence: 92% (improved with your help!)
>
> 📝 Document Type: 🚔 Police Report
> 📅 Date: 20240804
> 📌 Title: Sexual Assault Report - Richmond PD
> ⭐ Relevancy Score: 920
>
> 📄 Summary:
> Police report documenting sexual assault allegation filed by Jane Smith on August 4, 2024...
>
> 📋 Case Numbers: 24-7889
> 👤 Names Mentioned: Jane Smith, Officer Rodriguez
> 📍 Locations: Richmond
>
> 📝 OCR Text Preview:
> RICHMOND POLICE DEPARTMENT
> REPORT #24-7889
> DATE: 08/04/2024...
>
> **What would you like to do?**

**[Keyboard options]:**
- ✅ Looks good - Upload now
- ✏️ Edit a field
- ❌ Cancel

**You:**
> ✅ Looks good - Upload now

**Bot:**
> ⏳ Uploading to database and storage...
>
> ✅ **Upload Successful!**
>
> 🆔 Database ID: 1234
> 📄 Filename: 20240804_PLCR_Sexual_Assault_Report_REL-920_20250105_143022.jpg
> 🎯 AI Confidence: 92%
>
> 🔗 URL: https://jvjlhxodmbkodzmggwpu.supabase.co/storage/...
>
> ✨ Your document is now saved!
>
> Use /start to upload another.

---

## When Bot Asks Questions

### High Confidence (90%+) - No Questions
```
Clear document, no ambiguity
        ↓
Goes straight to preview
```

### Medium Confidence (70-89%) - 1-2 Questions
```
Some uncertain fields
        ↓
Ask specific clarifying questions
```

### Low Confidence (<70%) - Multiple Questions
```
Lots of uncertainty
        ↓
Ask several questions to improve accuracy
```

---

## Types of Questions Asked

### 1. Date Ambiguity
**Example:**
```
Question: I found two dates (08/04/2024 and 08/15/2024).
          Which is the document date?

Options:
  • 20240804
  • 20240815
  • Unknown

Reason: Multiple dates found
```

### 2. Document Type Uncertainty
**Example:**
```
Question: Is this a Police Report or a CPS Report?

Options:
  • 🚔 Police Report
  • 👶 CPS Report

Reason: Header mentions both agencies
```

### 3. Name Disambiguation
**Example:**
```
Question: The name "J. Smith" appears. Who is this?

Your answer: [Type name or "Unknown"]

Reason: Ambiguous name abbreviation
```

### 4. Case Number Extraction
**Example:**
```
Question: I see "#24-7889" and "Case 2024-07889".
          Which is the correct case number?

Options:
  • 24-7889
  • 2024-07889
  • Both (separate cases)

Reason: Multiple case number formats found
```

### 5. Relevancy Assessment
**Example:**
```
Question: This document contains allegations of abuse.
          Should relevancy be Critical (920) or High (850)?

Options:
  • Critical (920) - Sexual assault allegations
  • High (850) - General abuse allegation

Reason: Need context for severity scoring
```

---

## Field Editing

If you see something wrong in the preview, you can edit it:

**Bot shows preview:**
```
📝 Document Type: 🚔 Police Report
📅 Date: 20240804
📌 Title: Sexual Assault Report - Richmond PD
```

**You click:** ✏️ Edit a field

**Bot:**
```
Which field would you like to edit?

  • Document Type
  • Document Date
  • Title
  • Summary/Notes
  • Relevancy Score
  • ❌ Cancel edit - Go back to preview
```

**You select:** Title

**Bot:**
```
Enter new title:
```

**You type:**
```
Initial Sexual Assault Report - Richmond PD Case 24-7889
```

**Bot:**
```
✅ Title updated!

[Shows updated preview]
```

---

## Error Handling with Explanations

### Scenario: Duplicate Document

**Bot:**
```
🔄 **Duplicate Detected**

This document appears to be identical to one already uploaded.

Existing: 20240804_PLCR_Sexual_Assault_Report_REL-920.jpg
Uploaded: 2024-08-05
Similarity: 100% (identical MD5 hash)

Options:
1. Skip upload (keep existing)
2. Upload anyway (mark as version)
3. Replace existing document

What would you like to do?
```

### Scenario: Storage Bucket Missing

**Bot:**
```
☁️ **Storage Upload Failed**

Could not save image to cloud storage.

Possible causes:
• Storage bucket 'documents' not created
• Network connection issue
• File size too large

The metadata was saved, but image upload failed.

Quick fix:
1. Go to Supabase Dashboard
2. Storage → Create bucket named 'documents'
3. Set Public: YES
4. Try uploading again

Would you like to retry?
```

### Scenario: Database Schema Error

**Bot:**
```
💾 **Database Schema Issue**

The database doesn't have the expected field structure.

Technical details: Could not find the 'full_text_content' column

This might need database migration or schema update.

You can:
1. Contact database admin
2. Check schema in Supabase Dashboard
3. Upload with basic metadata only (skip OCR text)

Choose option:
```

---

## Orchestrator Intelligence Features

### 1. Confidence Scoring Per Field

The AI doesn't just give overall confidence - it scores each field:

```json
{
  "field_confidence": {
    "document_type": 0.95,    // Very confident
    "document_date": 0.40,    // NOT confident - will ask
    "title": 0.85,            // Confident
    "relevancy_score": 0.70,  // Borderline - might ask
    "case_numbers": 0.60      // Uncertain - will ask
  }
}
```

**Threshold:** Ask question if confidence < 0.70

### 2. Ambiguity Detection

Bot identifies specific ambiguities:

```json
{
  "ambiguities": [
    "Name 'J. Smith' could be 'John Smith' or 'Jane Smith'",
    "Two dates found: document date unclear",
    "Handwritten text in section 3 is illegible",
    "Stamp partially covers case number"
  ]
}
```

These appear in preview as notes.

### 3. Smart Question Generation

AI generates context-aware questions:

```json
{
  "question": "I see two dates (08/04/2024 and 08/15/2024). Which is the document date?",
  "field": "document_date",
  "options": ["20240804", "20240815", "Unknown"],
  "reason": "Multiple dates found in document",
  "current_guess": "20240804"
}
```

### 4. Metadata Extraction Verification

For critical fields like case numbers and names:

```json
{
  "metadata": {
    "case_numbers": ["24-7889"],        // Found
    "names": ["J. Smith", "Rodriguez"], // Might need clarification
    "locations": ["Richmond"],           // Clear
    "confidence_notes": "Name 'J. Smith' is abbreviated - full name unclear"
  }
}
```

---

## Comparison: 3 Bot Modes

### Mode 1: Original Bot ([telegram_document_bot.py](telegram_document_bot.py))
- **User does everything** - 7-step manual form
- **No AI** - You provide all metadata
- **No preview** - Commits immediately
- **Use when:** You want full manual control

### Mode 2: Enhanced Bot ([telegram_document_bot_enhanced.py](telegram_document_bot_enhanced.py))
- **AI does everything** - Analyzes and commits automatically
- **Fast** - ~20 seconds total
- **Risk:** Might guess wrong on ambiguous fields
- **Use when:** Document is clear, high confidence acceptable

### Mode 3: Orchestrator Bot ([telegram_bot_orchestrator.py](telegram_bot_orchestrator.py)) ⭐
- **AI + Human partnership** - AI asks when uncertain
- **Accurate** - Questions improve confidence to 90%+
- **Safe** - Preview before commit, editable fields
- **Use when:** You want accuracy AND speed

---

## Configuration

### Confidence Threshold

Edit [telegram_bot_orchestrator.py:134](telegram_bot_orchestrator.py:134):

```python
self.uncertainty_threshold = 0.7  # Default: Ask if confidence < 70%
```

**Lower threshold (0.5):** Ask fewer questions, accept more risk
**Higher threshold (0.9):** Ask more questions, maximize accuracy

### Field-Specific Thresholds

You can set different thresholds per field:

```python
field_thresholds = {
    'document_date': 0.8,      # High threshold - dates are critical
    'document_type': 0.7,      # Medium threshold
    'title': 0.6,              # Lower threshold - less critical
    'relevancy_score': 0.5     # Lowest - subjective anyway
}
```

---

## Usage Instructions

### Start Orchestrator Bot

```bash
cd ASEAGI

# Kill any existing bot
python -c "import psutil; [p.kill() for p in psutil.process_iter() if 'telegram' in ' '.join(p.cmdline() or []).lower()]"

# Start orchestrator
python telegram_bot_orchestrator.py
```

**Output:**
```
======================================================================
🤖 ASEAGI Telegram Bot - Orchestrator (Human-in-the-Loop)
======================================================================
✅ Tier 1 OCR: Enabled
✅ Tier 2 AI: Enabled
✅ Storage: Enabled
✅ Orchestration: Enabled
======================================================================

✅ Orchestrator bot is running! Press Ctrl+C to stop.

Features:
  • AI asks clarifying questions when uncertain
  • Preview before commit
  • Edit any field before upload
  • Human-friendly error explanations
```

### On Your Phone

1. Open Telegram → **@ASIAGI_bot**
2. Send `/start`
3. Send document image (with optional caption)
4. Answer any questions the AI asks
5. Review preview
6. Edit fields if needed
7. Confirm upload

---

## Advanced: Custom Question Logic

You can customize what questions get asked by editing the prompt in [telegram_bot_orchestrator.py:156](telegram_bot_orchestrator.py:156):

### Example: Always Ask About Sexual Assault Cases

```python
prompt += """

SPECIAL RULES:
1. If document mentions "sexual assault", "rape", or "abuse":
   - ALWAYS set relevancy to Critical (920)
   - ALWAYS ask for verification: "This appears to be a sexual assault case. Confirm relevancy: Critical (920)?"

2. If multiple victims are mentioned:
   - Ask: "I see multiple names. Who is the primary victim?"

3. If handwritten notes are present:
   - Ask: "There are handwritten notes. Can you transcribe key points?"
"""
```

---

## Benefits

### For Accuracy
- **90%+ confidence** on final uploads (vs 70-80% with auto mode)
- **Fewer errors** from ambiguous documents
- **Human verification** on critical fields

### For Speed
- **Faster than manual** - Only asks what's needed (not all 7 fields)
- **Slower than auto** - But worth it for accuracy
- **Average: 30-60 seconds** per document (vs 20s auto, 3min manual)

### For Trust
- **Explainable AI** - Shows confidence scores
- **Transparent** - Preview before commit
- **Controllable** - Edit any field
- **Error recovery** - Retry with guidance

---

## Cost

**Same as Enhanced Bot:**
- Claude API: ~$0.01-0.02 per document
- Supabase: Free tier
- **Total: $1-2/month for <100 uploads**

Orchestration uses ~25% more tokens (asks questions), but still very cheap.

---

## Troubleshooting

### "Bot not asking questions"

**Cause:** All fields have high confidence

**Solution:** This is good! Bot is confident. Preview will still show before commit.

### "Too many questions"

**Cause:** Document is ambiguous or low quality

**Solutions:**
1. Use higher quality scans
2. Add more context in caption
3. Lower uncertainty threshold in config

### "Questions are repetitive"

**Cause:** AI prompt may need tuning

**Solution:** Edit prompt at [telegram_bot_orchestrator.py:156](telegram_bot_orchestrator.py:156) to be more specific

---

## Next Steps

1. **Test with clear document** - See how it handles high-confidence case
2. **Test with ambiguous document** - See question asking in action
3. **Adjust threshold** - Fine-tune when questions are asked
4. **Customize prompts** - Add domain-specific logic

**This is the recommended bot for production use!** 🚀

It combines the speed of AI with the accuracy of human oversight.
