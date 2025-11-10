# Document Upload & Analyzer Dashboard

**Problem Solved:** Your existing dashboards were read-only. This dashboard provides **full upload functionality** with instant confirmation, automatic Claude analysis, and secure storage.

## Features

✅ **File Upload Interface**
- Drag & drop or browse to upload
- Support for: Images (JPG, PNG), PDFs, Text files (TXT, RTF)
- Multiple file upload support

✅ **Instant Confirmation & Feedback**
- Real-time upload progress
- File validation and duplicate detection
- Visual confirmation for each upload

✅ **Automatic Document Analysis**
- Claude Sonnet 4.5 AI analysis
- PROJ344 scoring (micro, macro, legal, relevancy)
- Smoking gun detection
- Perjury indicator identification

✅ **Secure Storage**
- Local file storage on droplet: `/home/user/ASEAGI/uploads/`
- Organized directories: `pending/`, `processed/`, `chat_history/`
- Database backup in Supabase
- MD5 hash-based duplicate detection

✅ **Chat History Analyzer**
- Upload chat logs (TXT, JSON, CSV)
- Secure storage for analysis
- Coming: Automatic conversation analysis

## Quick Start

### 1. Launch the Dashboard

```bash
cd /home/user/ASEAGI/dashboards
./launch_upload_dashboard.sh
```

Or manually:
```bash
streamlit run document_upload_analyzer.py --server.port 8503
```

### 2. Access the Dashboard

Open your browser to:
```
http://localhost:8503
```

Or if running on a server:
```
http://YOUR_SERVER_IP:8503
```

### 3. Upload Documents

1. Select "📄 Legal Documents" mode
2. Click "Browse files" or drag & drop
3. Choose one or multiple files
4. Click "🚀 Upload & Process"
5. Watch real-time progress and confirmation!

## Upload Modes

### 📄 Legal Documents
Upload legal files for automatic PROJ344 analysis
- Supports: JPG, PNG, PDF, TXT, RTF
- Auto-analysis with Claude AI
- Duplicate detection
- Instant feedback with scores

### 💬 Chat History
Upload chat logs for review and analysis
- Supports: TXT, JSON, CSV
- Secure storage
- Manual review enabled

### 📊 Batch Upload
Monitor upload queue and processing status
- View pending files
- Track processed files
- System statistics

### 📈 Upload Status
View system statistics and recent uploads
- Total documents processed
- Average relevancy scores
- API costs
- Recent upload history

## Storage Locations

All uploads are stored securely on your droplet:

```
/home/user/ASEAGI/uploads/
├── pending/          # Files waiting for processing
├── processed/        # Successfully analyzed files
└── chat_history/     # Chat log uploads
```

Database backup: All analyzed documents are automatically uploaded to Supabase `legal_documents` table.

## Configuration

### Required Environment Variables

```bash
# Supabase (for database storage)
export SUPABASE_URL="your_supabase_url"
export SUPABASE_KEY="your_supabase_key"

# Claude API (for document analysis)
export ANTHROPIC_API_KEY="your_anthropic_key"
```

### Optional: Load from file

```bash
source ~/.supabase_file_system
```

## Troubleshooting

### "No confirmation when uploading"
**Solution:** The old dashboards had no upload feature! Use this new dashboard instead.

### "Analysis disabled"
**Cause:** ANTHROPIC_API_KEY not set
**Solution:** Set the environment variable:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Database connection failed"
**Cause:** Supabase credentials missing
**Solution:** Set SUPABASE_URL and SUPABASE_KEY

### "Files not showing up"
**Check:**
1. Upload completed with green checkmark ✅
2. File saved to `/home/user/ASEAGI/uploads/processed/`
3. Check Supabase database for entry
4. Refresh the "Upload Status" page

## API Costs

- Claude Sonnet 4.5 pricing:
  - Input: $3 / 1M tokens
  - Output: $15 / 1M tokens
- Average document: $0.01 - $0.10
- Cost shown for each upload
- Total costs tracked in dashboard

## Next Steps

1. **Test the upload**: Try uploading a sample image or PDF
2. **Check confirmation**: Verify you see the green checkmarks ✅
3. **View results**: Check the "Upload Status" tab
4. **Review storage**: Verify files in `/home/user/ASEAGI/uploads/`
5. **Check database**: Confirm entries in Supabase

## Support

If you still don't see confirmations:
1. Check browser console for errors
2. Verify file permissions on upload directory
3. Check Streamlit terminal output for errors
4. Ensure network connectivity to Supabase/Claude APIs

---

**Created:** 2025-11-10
**Version:** 1.0
**Status:** Production Ready ✅
