# Document Storage Architecture - ASEAGI

## Overview
Multi-tier storage system optimized for fast viewing, AI processing, and long-term archival.

---

## Architecture

### Upload Flow
```
1. Telegram → Image received
2. Claude Vision API → Extract metadata, OCR, verify duplicates
3. Supabase Storage → Save full image + thumbnail
4. Supabase Database → Save metadata + extracted text
5. Google Drive → Nightly backup (optional)
```

---

## Storage Tiers

### Tier 1: Fast Access (Supabase Storage)
**Purpose:** Immediate viewing and reference

**What's Stored:**
- Thumbnails (200x200px) - ~20KB each
- Optimized images (1200px width) - ~200KB each
- Recent documents (last 90 days)

**Access Speed:** <100ms via CDN

**Bucket Structure:**
```
documents/
├── thumbnails/
│   └── 20240804_RichmondPD_PLCR_xxx_thumb.jpg
├── optimized/
│   └── 20240804_RichmondPD_PLCR_xxx_opt.jpg
└── originals/
    └── 20240804_RichmondPD_PLCR_xxx.jpg
```

**Cost:** Free up to 100GB, then $0.021/GB/month

---

### Tier 2: Database (Supabase PostgreSQL)
**Purpose:** Fast search, metadata, and extracted text

**What's Stored:**
- OCR extracted text (full_text_content)
- Claude Vision analysis (executive_summary)
- Metadata (dates, types, relevancy)
- File references (URLs to Supabase Storage)
- Duplicate detection (file_hash)

**Table: legal_documents**
```sql
Key columns:
- file_path: URL to original image in Supabase Storage
- thumbnail_path: URL to thumbnail
- full_text_content: OCR extracted text
- executive_summary: Claude Vision analysis
- file_hash: MD5 hash for duplicate detection
- document_date: Extracted or user-provided date
- relevancy_number: Importance score
```

**Access Speed:** <50ms for metadata queries

**Cost:** Free up to 500MB database, then $25/month (Pro tier)

---

### Tier 3: Archive (Google Drive)
**Purpose:** Legal compliance and disaster recovery

**What's Stored:**
- Monthly backups of all documents
- Original unmodified files
- Export of database (JSON/CSV)

**Folder Structure:**
```
ASEAGI Archive/
├── 2024/
│   ├── 08-August/
│   │   ├── Police Reports/
│   │   └── Declarations/
│   └── 09-September/
└── Database Exports/
    └── 2024-08-31_export.json
```

**Access Speed:** Not critical (archival only)

**Cost:** $6-12/month (Google Workspace)

---

## Claude Vision AI Integration

### What Claude Analyzes:
1. **Document Type Detection**
   - Police report, court order, declaration, etc.
   - Confidence score

2. **Date Extraction**
   - Look for dates in document
   - Format: MM/DD/YYYY, YYYYMMDD, written dates
   - If none found: "Unknown"

3. **Key Information**
   - Names mentioned
   - Incident details
   - Important quotes
   - Case numbers

4. **Duplicate Detection**
   - Compare with existing documents
   - Check similar content
   - Flag if likely duplicate

5. **Relevancy Scoring**
   - Analyze importance based on content
   - Auto-score 600-920
   - Keywords: "sexual assault", "critical", "evidence"

### Example Claude Vision Prompt:
```
Analyze this legal document image:

1. Document type (Police Report, Court Order, etc.)
2. Extract any dates (format: YYYYMMDD or "Unknown")
3. Extract key information:
   - Names mentioned
   - Case/Report numbers
   - Incident details
   - Important facts
4. Summarize in 2-3 sentences
5. Suggest relevancy score (600-920) based on:
   - Evidence of abuse/assault: 900+
   - Court orders: 800-900
   - Administrative: 700-800
   - Other: 600-700

Return JSON format.
```

---

## Workflow Improvements

### Option A: Smart Quick Upload (Recommended)
**User Experience:**
```
You: [Send image with caption]
     "Richmond PD 24-7889 - Initial sexual assault report"

Bot: 🔍 Analyzing with Claude Vision...
     ✅ Detected: Police Report
     📅 Date: 2024-08-04 (extracted from image)
     📄 Report #: 24-7889
     ⭐ Relevancy: Critical (920) - Sexual assault allegation

     Confirm upload? (Yes/No)

You: Yes

Bot: ✅ Uploaded!
     🔗 View: https://jvjlhxodmbkodzmggwpu.supabase.co/storage/...
     📊 Added to database (ID: 1234)
```

**Steps:**
1. Send image (with or without caption)
2. Claude Vision analyzes automatically
3. Bot shows extracted info
4. You confirm or edit
5. Uploaded

### Option B: Detailed Interview (Current)
Keep current 7-step process for complex documents where you want manual control.

### Option C: Hybrid (Best of Both)
```
Bot: How would you like to upload?
     1️⃣ Quick (AI analyzes)
     2️⃣ Detailed (manual entry)

You: 1

[Quick upload flow]
```

---

## Duplicate Detection Strategy

### Three-Level Check:

**Level 1: File Hash**
- MD5 hash of image bytes
- Exact duplicate detection
- Instant (database query)

**Level 2: Visual Similarity**
- Compare thumbnails with perceptual hash
- Catch rescanned/rephotographed docs
- ~500ms per comparison

**Level 3: Content Similarity**
- Compare OCR text with fuzzy matching
- Catch different scans of same document
- Uses PostgreSQL full-text search

### Example:
```
Bot: ⚠️ Possible duplicate found!

     Existing: 240804_RichmondPD_PLCR_Report_24-7889.jpg
     Uploaded: 2024-08-05
     Similarity: 95%

     Options:
     1. Skip (keep existing)
     2. Replace (use new version)
     3. Keep both (mark as versions)
```

---

## Cost Breakdown (Monthly)

### Small Scale (<100GB, <10k docs)
- Supabase Storage: **Free** (100GB included)
- Supabase Database: **Free** (500MB included)
- Claude Vision API: **$5-10** (~100 documents/month)
- Google Drive Backup: **$6** (optional)
- **Total: $5-16/month**

### Medium Scale (100-500GB, 10k-50k docs)
- Supabase Storage: **$8** (400GB)
- Supabase Database: **$25** (Pro tier)
- Claude Vision API: **$20-30** (~500 documents/month)
- Google Drive Backup: **$12** (2TB)
- **Total: $65-75/month**

### Large Scale (500GB+, 50k+ docs)
- Supabase Storage: **$21** (1TB)
- Supabase Database: **$25** (Pro tier)
- Claude Vision API: **$50** (~1000 documents/month)
- Google Drive Backup: **$12** (2TB)
- **Total: $108/month**

**Your Current: ~400 docs = Small Scale = $5-16/month**

---

## Implementation Priority

### Phase 1: Core Infrastructure (Week 1)
- [ ] Set up Supabase Storage bucket
- [ ] Configure public URL access
- [ ] Update bot to save images to Supabase
- [ ] Generate thumbnails

### Phase 2: AI Integration (Week 2)
- [ ] Add Claude Vision API
- [ ] Implement auto-extraction
- [ ] Add duplicate detection
- [ ] Smart quick upload workflow

### Phase 3: Optimization (Week 3)
- [ ] Image compression
- [ ] Thumbnail generation
- [ ] Fast dashboard preview
- [ ] Search index optimization

### Phase 4: Archive (Week 4)
- [ ] Google Drive integration
- [ ] Automated backups
- [ ] Export functionality
- [ ] Lifecycle policies

---

## Recommendation

**Use Hybrid Multi-Tier Architecture with:**

1. ✅ **Supabase Storage** for primary storage (fast, integrated)
2. ✅ **Claude Vision AI** for auto-extraction and analysis
3. ✅ **Supabase Database** for metadata and search
4. ✅ **Google Drive** for monthly backups (legal compliance)
5. ✅ **Smart Quick Upload** as default (Option A)
6. ✅ **Detailed Interview** available for complex docs

**Why This Works:**
- Fast viewing (<100ms thumbnails)
- Intelligent processing (Claude Vision)
- Duplicate detection (3-level check)
- Cost-effective ($5-16/month for your scale)
- Legally compliant (Google Drive backup)
- Scalable (handles growth to 50k+ docs)

---

## Next Steps

Would you like me to:
1. Implement the Supabase Storage integration?
2. Add Claude Vision AI processing?
3. Build the smart quick upload workflow?
4. All of the above?

Let me know and I'll start implementing!
