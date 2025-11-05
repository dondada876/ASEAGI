# Police Reports Dashboard

**Comprehensive visualization and analysis dashboard for police reports**

## Overview

The Police Reports Dashboard is a specialized Streamlit application designed to provide comprehensive access to police reports stored in the PROJ344 Legal Case Intelligence System. It offers advanced filtering, search capabilities, and the ability to view source documents (images/PDFs) alongside report metadata.

## Features

### Core Functionality

1. **📊 Overview Dashboard**
   - Total police reports count
   - Total reports (all documents with "report" in filename)
   - Processing status breakdown (processed, pending, failed)
   - Score distribution (Relevancy, Legal, Micro, Macro)
   - Document type analysis
   - Recent reports quick view

2. **📄 All Police Reports View**
   - Complete list of all police reports
   - Advanced filtering:
     - By processing status
     - By document type
     - By minimum relevancy score
   - Expandable details for each report
   - Full document viewer integration

3. **📋 All Reports View**
   - Lists all documents with "report" in filename
   - Tabular view with sorting
   - CSV export functionality
   - Quick metadata overview

4. **🔍 Search Reports**
   - Keyword search across:
     - Original filenames
     - Document titles
     - Executive summaries
     - Keywords
     - Smoking guns
   - Toggle between police reports only or all reports
   - Results sorted by relevancy score

5. **📊 Analytics**
   - Score correlation visualizations
   - Legal Score vs Relevancy Score scatter plot
   - Micro Score vs Macro Score scatter plot
   - Upload timeline chart
   - Trend analysis

### Document Viewer

The integrated document viewer provides:

- **Metadata Display**
  - Original filename
  - Document type
  - Total pages
  - Creation date
  - Processing status badge
  - All scoring dimensions (REL, LEG, MIC, MAC)

- **Content Preview**
  - Executive summary
  - Keywords (styled as tags)
  - Smoking guns list

- **Page-by-Page Viewer**
  - View individual pages from `document_pages` table
  - Display source images if available
  - View OCR extracted text
  - Page metadata (file type, creation date)

- **Source Document Access**
  - Image URL display (if stored in Supabase Storage)
  - Local file path display
  - Automatic image loading from both sources

## Installation

### Prerequisites

- Python 3.11+
- Supabase account with PROJ344 database
- Streamlit
- Required Python packages

### Setup

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

2. **Configure Supabase credentials:**

Create `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-anon-key"
```

Or set environment variables:

```bash
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your-anon-key"
```

3. **Run the dashboard:**

```bash
streamlit run police_reports_dashboard.py --server.port=8502
```

Access at: http://localhost:8502

## Database Schema Requirements

The dashboard requires the following Supabase tables:

### legal_documents Table

Minimum required fields:
- `id` (UUID) - Primary key
- `original_filename` (TEXT) - Original file name
- `renamed_filename` (TEXT) - Renamed file name (optional)
- `document_title` (TEXT) - Document title
- `document_type` (TEXT) - Type of document
- `executive_summary` (TEXT) - AI-generated summary
- `keywords` (TEXT[]) - Array of keywords
- `smoking_guns` (TEXT[]) - Critical evidence points
- `relevancy_number` (INTEGER) - Relevancy score (0-999)
- `legal_number` (INTEGER) - Legal weight score (0-999)
- `micro_number` (INTEGER) - Micro-level score (0-999)
- `macro_number` (INTEGER) - Macro-level score (0-999)
- `processing_status` (TEXT) - Status: 'completed', 'processing', 'pending', 'failed'
- `total_pages` (INTEGER) - Number of pages
- `file_path` (TEXT) - Local file path (optional)
- `storage_url` (TEXT) - Supabase storage URL (optional)
- `created_at` (TIMESTAMPTZ) - Creation timestamp

### document_pages Table (Optional)

For page-by-page viewing:
- `id` (UUID) - Primary key
- `document_id` (UUID) - Foreign key to legal_documents
- `page_number` (INTEGER) - Page number
- `image_url` (TEXT) - URL to page image in Supabase Storage
- `image_path` (TEXT) - Local file path to page image
- `ocr_text` (TEXT) - Extracted text via OCR
- `file_type` (TEXT) - Image file type (png, jpg, pdf, etc.)
- `created_at` (TIMESTAMPTZ) - Creation timestamp

## Usage Guide

### Finding Police Reports

The dashboard identifies police reports in two ways:

1. **Primary method**: Documents with "police" in the `original_filename`
2. **Secondary method**: Documents with "report" in the `original_filename`

### Viewing Report Details

1. Navigate to **"📄 All Police Reports"**
2. Apply filters as needed (status, type, score)
3. Click on a report to expand
4. View metadata, scores, and keywords
5. Use page selector to view individual pages
6. View OCR text in expandable section

### Searching Reports

1. Navigate to **"🔍 Search Reports"**
2. Enter keywords (searches across multiple fields)
3. Choose "Police Reports Only" or "All Reports"
4. Click on results to view full details

### Analytics & Insights

1. Navigate to **"📊 Analytics"**
2. Review score correlations
3. Analyze upload timeline
4. Identify trends and patterns

## Status Badges

Reports display color-coded status badges:

- 🟢 **COMPLETED** - Processing finished successfully
- 🟡 **PROCESSING** - Currently being processed
- 🔵 **PENDING** - Queued for processing
- 🔴 **FAILED** - Processing encountered errors

## Score Badges

Documents are scored on four dimensions (0-999):

- **REL** (Relevancy) - Overall relevance to the case
- **LEG** (Legal) - Legal weight and admissibility
- **MIC** (Micro) - Detail-level importance
- **MAC** (Macro) - Case-wide significance

Score colors:
- 🔴 **RED** (900+) - Critical
- 🟠 **ORANGE** (800-899) - High Value
- 🔵 **BLUE** (700-799) - Strong
- ⚪ **GRAY** (<700) - Standard

## Integration with PROJ344 System

The Police Reports Dashboard integrates seamlessly with:

- **PROJ344 Master Dashboard** - Main case intelligence hub
- **Legal Intelligence Dashboard** - Document analysis system
- **Timeline & Violations Dashboard** - Chronological tracking
- **Context Preservation System** - State management

Shared styling via `proj344_style.py` ensures consistent UI/UX.

## File Structure

```
ASEAGI/
├── police_reports_dashboard.py      # Main dashboard application
├── proj344_style.py                 # Shared styling module
├── utilities/
│   └── count_police_reports.py      # CLI report counter
├── .streamlit/
│   ├── config.toml                  # Streamlit config
│   └── secrets.toml                 # Supabase credentials (not in git)
└── POLICE_REPORTS_DASHBOARD.md      # This file
```

## Troubleshooting

### "Supabase connection failed"

**Solution**: Verify your credentials in `.streamlit/secrets.toml` or environment variables.

### "No police reports found"

**Possible causes**:
1. No documents with "police" in filename uploaded yet
2. Wrong database/table name
3. Row Level Security (RLS) blocking access

**Solution**: Check database, verify RLS policies, or upload police reports.

### "No pages found in database"

**Explanation**: The `document_pages` table is optional. If not populated, source images won't display.

**Solution**: Run document processing pipeline to populate `document_pages` table.

### Images not displaying

**Possible causes**:
1. `image_url` points to invalid Supabase Storage location
2. Local `image_path` file doesn't exist
3. Browser blocking mixed content (HTTP images on HTTPS site)

**Solution**: Verify storage URLs, check file paths, ensure HTTPS for images.

## Performance Optimization

The dashboard uses several caching strategies:

- `@st.cache_resource` - Supabase client (persistent)
- `@st.cache_data(ttl=60)` - Data queries (60-second cache)

To force refresh, use the Streamlit "Clear cache" option in the menu.

## Security Considerations

1. **Never commit** `.streamlit/secrets.toml` to git
2. **Use RLS** (Row Level Security) in Supabase
3. **Rotate API keys** regularly
4. **Consider private repo** for sensitive case data
5. **Limit access** to dashboard in production

## Advanced Features

### Custom Filters

Extend filtering by modifying the filter logic in the "All Police Reports" page:

```python
# Add custom filter
relevance_range = st.slider("Relevancy Range", 0, 999, (700, 999))
filtered_reports = [r for r in filtered_reports
                    if relevance_range[0] <= r.get('relevancy_number', 0) <= relevance_range[1]]
```

### Export Functionality

Export reports to various formats:

```python
# JSON export
import json
json_data = json.dumps(filtered_reports, indent=2)
st.download_button("Download JSON", json_data, "reports.json")

# Excel export
import pandas as pd
df = pd.DataFrame(filtered_reports)
df.to_excel("reports.xlsx")
```

## Future Enhancements

Planned features:

- [ ] Bulk processing status updates
- [ ] Direct PDF upload from dashboard
- [ ] Advanced OCR text search
- [ ] Report comparison tool
- [ ] Annotation and highlighting
- [ ] AI-powered report summarization
- [ ] Export to legal case management systems
- [ ] Mobile-responsive design
- [ ] Real-time updates via WebSocket

## Support

For issues or questions:
- Review the main [README.md](README.md)
- Check [PROJ344_SYSTEM_SUMMARY.md](PROJ344_SYSTEM_SUMMARY.md)
- Report issues via GitHub Issues

## License

Private - Not for public distribution

## Author

Don Bucknor - PROJ344 Legal Case Intelligence System

---

**Last Updated:** 2025-11-05
