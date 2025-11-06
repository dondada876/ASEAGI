# Enhanced Telegram Bot Setup - ASEAGI

## What's New?

The enhanced bot now includes:

✅ **Tier 1: Tesseract OCR** - Fast, free, basic text extraction
✅ **Tier 2: Claude Vision AI** - Intelligent analysis, metadata extraction
✅ **Smart Quick Upload** - Send image + caption, AI analyzes automatically
✅ **Date Optional** - Can mark documents as "Unknown" date
✅ **Supabase Storage** - Images stored in the cloud, not just metadata
✅ **Thumbnail Generation** - Fast loading thumbnails (200x200)
✅ **Duplicate Detection** - MD5 hash checks prevent duplicates

---

## Setup Instructions

### Step 1: Install Dependencies

```bash
cd ASEAGI
pip install -r requirements.txt
```

This installs:
- `pytesseract` - OCR library
- `anthropic` - Claude Vision AI
- `pillow` - Image processing
- All existing dependencies

### Step 2: Add Claude API Key

Edit [.streamlit/secrets.toml](.streamlit/secrets.toml):

```toml
# Existing keys
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "your_key_here"
TELEGRAM_BOT_TOKEN = "your_token_here"

# ADD THIS:
ANTHROPIC_API_KEY = "sk-ant-api03-..."
```

**Get Claude API Key:**
1. Go to https://console.anthropic.com/
2. Create account or login
3. Go to "API Keys"
4. Create new key
5. Copy and paste into secrets.toml

**Cost:** ~$0.01 per document analysis (very cheap!)

### Step 3: Create Supabase Storage Bucket

**IMPORTANT:** Must be done manually from dashboard (anon key can't create buckets)

1. Go to https://supabase.com/dashboard/project/jvjlhxodmbkodzmggwpu

2. Click **Storage** in left sidebar

3. Click **New bucket**

4. Configure:
   - **Name:** `documents`
   - **Public:** ✅ **YES** (so URLs work)
   - **File size limit:** 50 MB
   - **Allowed MIME types:**
     - `image/jpeg`
     - `image/jpg`
     - `image/png`
     - `image/gif`
     - `application/pdf`

5. Click **Create bucket**

6. Verify bucket created:
   ```bash
   cd ASEAGI
   python setup_storage_bucket.py
   ```

   Should show: `✅ Bucket 'documents' is accessible!`

### Step 4: Optional - Install Tesseract (for Tier 1 OCR)

**Without Tesseract:** Bot will work fine using only Claude Vision (Tier 2)

**With Tesseract:** Bot uses fast local OCR first, then Claude for analysis

**Windows Installation:**

1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Run installer: `tesseract-ocr-w64-setup-5.3.x.exe`
3. Install to: `C:\Program Files\Tesseract-OCR`
4. Add to PATH or set in code

The bot will auto-detect if Tesseract is available and use it.

---

## How to Use

### Option 1: Smart Quick Upload (Recommended)

1. Start bot:
   ```bash
   cd ASEAGI
   python telegram_document_bot_enhanced.py
   ```

2. On your phone, open Telegram and message **@ASIAGI_bot**

3. Send `/start`

4. Choose **1️⃣ Smart Quick Upload**

5. Send image with caption:
   ```
   Richmond PD 24-7889 - Initial sexual assault report
   ```

6. Bot analyzes with Claude Vision AI (~10 seconds)

7. Review AI analysis:
   ```
   ✅ AI Analysis Complete!

   🤖 Confidence: 95%

   📝 Document Type: 🚔 Police Report
   📅 Date: 20240804
   📌 Title: Sexual Assault Report - Richmond PD
   ⭐ Relevancy Score: 920

   📄 Summary:
   Police report documenting sexual assault allegation...

   📋 Case Numbers: 24-7889
   👤 Names: John Doe, Jane Smith

   ✅ Type YES to upload with this analysis
   ✏️ Type EDIT to manually adjust fields
   ❌ Type NO to cancel
   ```

8. Type `YES`

9. Done! Image and metadata saved to Supabase.

### Option 2: Detailed Manual Entry

Same 7-step process as before, but now:
- Date field accepts "Unknown"
- Images are stored in Supabase
- Tesseract OCR extracts text automatically

---

## What Gets Stored

### Database (`legal_documents` table)

```json
{
  "id": 1234,
  "original_filename": "20240804_PLCR_Sexual_Assault_Report_REL-920_20250105_143022.jpg",
  "document_type": "PLCR",
  "document_title": "Sexual Assault Report - Richmond PD",
  "document_date": "20240804",
  "relevancy_number": 920,
  "executive_summary": "Police report documenting...",
  "full_text_content": "RICHMOND POLICE DEPARTMENT\nREPORT #24-7889...",
  "file_hash": "a3f7b2c1d4e5f6...",
  "file_path": "https://jvjlhxodmbkodzmggwpu.supabase.co/storage/v1/object/public/documents/originals/...",
  "thumbnail_path": "https://jvjlhxodmbkodzmggwpu.supabase.co/storage/v1/object/public/documents/thumbnails/...",
  "source": "telegram_bot",
  "uploaded_via": "phone",
  "created_at": "2025-01-05T14:30:22"
}
```

### Storage (`documents` bucket)

```
documents/
├── originals/
│   └── 20240804_PLCR_Sexual_Assault_Report_REL-920_20250105_143022.jpg
│       (Full resolution image - ~500KB-2MB)
│
└── thumbnails/
    └── 20240804_PLCR_Sexual_Assault_Report_REL-920_20250105_143022_thumb.jpg
        (200x200 thumbnail - ~20KB)
```

---

## AI Analysis Features

### Claude Vision Extracts:

1. **Document Type** - Automatically detects:
   - Police Report (PLCR)
   - Court Order (ORDR)
   - Declaration (DECL)
   - Evidence/Photo (EVID)
   - And 6 more types

2. **Document Date** - Scans image for dates:
   - Looks for MM/DD/YYYY
   - Looks for YYYYMMDD
   - Looks for written dates ("August 4, 2024")
   - Returns "Unknown" if none found

3. **Title** - Creates descriptive title:
   - Includes agency/department
   - Max 80 characters
   - Example: "Sexual Assault Report - Richmond PD"

4. **Executive Summary** - 2-3 sentence summary

5. **Full OCR Text** - Extracts ALL visible text

6. **Relevancy Score** - Auto-scores 600-920 based on:
   - Sexual assault/abuse: 900-920
   - Court orders: 850-900
   - Police reports: 800-850
   - Administrative: 700-800

7. **Metadata** - Extracts:
   - Names mentioned
   - Case/Report numbers
   - Locations
   - Incident dates

---

## Workflow Comparison

### OLD Workflow (telegram_document_bot.py):
1. Send image
2. Choose document type (7 options)
3. Enter date (required, no "Unknown")
4. Enter title
5. Enter notes
6. Choose relevancy level
7. Confirm upload
8. ❌ **Image NOT stored** (only metadata)

**Total: 7 steps, ~2-3 minutes**

### NEW Smart Workflow (telegram_document_bot_enhanced.py):
1. Send image with caption
2. AI analyzes (~10 seconds)
3. Confirm or edit
4. ✅ **Image stored in Supabase**

**Total: 3 steps, ~20 seconds**

---

## Cost Breakdown

### Small Scale (<100 uploads/month)

| Service | Cost | Notes |
|---------|------|-------|
| Supabase Storage | **Free** | First 100GB free |
| Supabase Database | **Free** | First 500MB free |
| Claude Vision API | **$1-2** | ~$0.01 per document |
| Tesseract OCR | **Free** | Local, open source |
| **Total** | **$1-2/month** | 🎉 Very cheap! |

### Medium Scale (500 uploads/month)

| Service | Cost | Notes |
|---------|------|-------|
| Supabase Storage | **Free** | Still within 100GB |
| Supabase Database | **Free** | Still within 500MB |
| Claude Vision API | **$5-10** | ~$0.01 per document |
| **Total** | **$5-10/month** | Still very affordable |

---

## Troubleshooting

### "Claude Vision not available"

**Solution:** Add `ANTHROPIC_API_KEY` to [.streamlit/secrets.toml](.streamlit/secrets.toml)

Bot will still work without Claude, but won't auto-analyze documents.

### "Storage upload failed"

**Solution:** Create `documents` bucket in Supabase dashboard (see Step 3 above)

### "Tesseract not found"

**Solution:** This is OK! Bot will work fine with just Claude Vision (Tier 2).

To enable Tesseract (optional):
1. Install Tesseract executable
2. Add to PATH
3. Restart bot

### "row-level security policy" error

**Solution:** Make sure bucket is set to **Public: YES** in dashboard.

---

## Testing

### Test Enhanced Bot:

```bash
cd ASEAGI
python telegram_document_bot_enhanced.py
```

### Check if Storage is Working:

```bash
cd ASEAGI
python -c "
from supabase import create_client
import toml
from pathlib import Path

secrets = toml.load(Path('.streamlit/secrets.toml'))
supabase = create_client(secrets['SUPABASE_URL'], secrets['SUPABASE_KEY'])

buckets = supabase.storage.list_buckets()
print('Available buckets:', [b.name for b in buckets])

if any(b.name == 'documents' for b in buckets):
    print('✅ documents bucket found!')

    # Try to list files
    files = supabase.storage.from_('documents').list('originals')
    print(f'Files in originals: {len(files)}')
else:
    print('❌ documents bucket not found - create it in dashboard!')
"
```

---

## Next Steps

1. **Test Smart Quick Upload** - Try uploading a police report with caption

2. **Verify Storage** - Check Supabase dashboard → Storage → documents → originals

3. **Check Dashboard** - View uploaded document in [proj344_master_dashboard.py](proj344_master_dashboard.py)

4. **Compare Costs** - Monitor Claude API usage at https://console.anthropic.com/

5. **Optimize Prompts** - Edit Claude Vision prompt in [telegram_document_bot_enhanced.py](telegram_document_bot_enhanced.py) lines 240-270 if needed

---

## Migration from Old Bot

**Both bots work side-by-side!**

- `telegram_document_bot.py` - Old bot (detailed workflow, no storage)
- `telegram_document_bot_enhanced.py` - New bot (smart workflow, with storage)

**To switch:**

1. Kill old bot:
   ```bash
   cd ASEAGI
   python -c "import psutil; [p.kill() for p in psutil.process_iter() if 'telegram_document_bot.py' in ' '.join(p.cmdline() or [])]"
   ```

2. Start new bot:
   ```bash
   cd ASEAGI
   python telegram_document_bot_enhanced.py
   ```

**Same bot username (@ASIAGI_bot) will work with new bot automatically!**

---

## Questions?

- Check [DOCUMENT_STORAGE_ARCHITECTURE.md](DOCUMENT_STORAGE_ARCHITECTURE.md) for architecture details
- Check [TELEGRAM_BOT_TROUBLESHOOTING.md](TELEGRAM_BOT_TROUBLESHOOTING.md) for common issues
- Bot logs show Tier 1/Tier 2 status on startup

**Enjoy your enhanced bot!** 🚀
