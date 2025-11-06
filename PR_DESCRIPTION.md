## 📱 Telegram Document Ingestion Bot

This PR adds a comprehensive Telegram bot for uploading documents from your phone with form-based metadata collection.

### ✨ Features

- **📸 Upload photos/PDFs** directly from phone via Telegram
- **📝 Conversational form** to collect document metadata
- **🏷️ Document type selection** (PLCR, DECL, EVID, CPS, etc.)
- **📅 Date, title, and notes** collection
- **⭐ Relevancy scoring** (Critical/High/Medium/Low)
- **💾 Direct integration** with Supabase legal_documents table
- **🔄 Automatic filename generation** with proper formatting

### 📄 Files Added

- `telegram_document_bot.py` - Main bot implementation with conversational handlers
- `TELEGRAM_BOT_SETUP.md` - Complete setup guide with step-by-step instructions
- `requirements.txt` - Updated with `python-telegram-bot` and `toml` dependencies

### 🎯 Use Case

This solves the problem of quick document ingestion from mobile devices. Now you can:

1. Scan a document with your phone camera
2. Send it to your Telegram bot
3. Answer a few questions (type, date, notes)
4. Have it automatically uploaded to your Supabase database with proper metadata

### 🚀 How to Use

1. Create a Telegram bot with @BotFather
2. Add `TELEGRAM_BOT_TOKEN` to your `.streamlit/secrets.toml`
3. Run: `python3 telegram_document_bot.py`
4. Open Telegram and send `/start` to your bot
5. Upload documents with full context capture!

See `TELEGRAM_BOT_SETUP.md` for complete setup instructions.

### ✅ Testing

- [x] Bot successfully receives photos and PDFs
- [x] Conversational form collects all metadata
- [x] Documents upload to Supabase legal_documents table
- [x] Filenames generated correctly with relevancy scores
- [x] Error handling for invalid inputs

### 🔗 Related

This complements the existing document query tools like `count_police_reports.py` and works seamlessly with the dashboard ecosystem.

### 📊 Summary of Changes

**New Files:**
- `telegram_document_bot.py` (520 lines) - Complete bot implementation
- `TELEGRAM_BOT_SETUP.md` (237 lines) - Setup and usage documentation

**Modified Files:**
- `requirements.txt` - Added `python-telegram-bot>=20.0` and `toml>=0.10.2`

**Also in this PR:**
- `count_police_reports.py` - Fixed database schema issues (removed non-existent fraud_score column)

---

**Ready to merge!** This enables mobile-first document ingestion workflow. 📱→📊
