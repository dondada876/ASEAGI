# Streamlit Cloud Deployment Setup Guide

## Overview
This guide walks you through deploying the PROJ344 dashboards to Streamlit Cloud at https://proj344-dashboards.streamlit.app/

---

## Step 1: Access Streamlit Cloud

1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account (dondada876)
3. Navigate to your app: https://proj344-dashboards.streamlit.app/

---

## Step 2: Configure Secrets in Streamlit Cloud

**IMPORTANT**: Your dashboards need Supabase credentials to connect to the database. These must be configured in Streamlit Cloud's secrets management.

### How to Add Secrets:

1. In Streamlit Cloud dashboard, click on your app
2. Click the **"⚙️ Settings"** button (top right)
3. Select **"Secrets"** from the left sidebar
4. Copy and paste the following into the secrets editor:

```toml
# Supabase Configuration
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c"
```

5. Click **"Save"**
6. Your app will automatically restart with the new secrets

---

## Step 3: Verify Entry Point

Make sure your Streamlit Cloud app is configured to run the correct file:

**Main Entry Point**: `proj344_master_dashboard.py`

To check/update:
1. Go to app settings
2. Under **"Main file path"**, ensure it shows: `proj344_master_dashboard.py`
3. If different, update and save

---

## Step 4: Verify Deployment

After configuring secrets and pushing the latest code:

1. Wait 1-2 minutes for Streamlit Cloud to rebuild
2. Visit https://proj344-dashboards.streamlit.app/
3. You should see the dashboard load successfully
4. Check that data from Supabase is displaying properly

---

## Troubleshooting

### Issue: "Missing SUPABASE_URL or SUPABASE_KEY"

**Solution**: Secrets not configured properly
1. Go to app Settings → Secrets
2. Verify the exact format shown in Step 2
3. Ensure no extra spaces or formatting issues
4. Save and wait for restart

### Issue: "Module not found" errors

**Solution**: Dependencies not installed
1. Check that `requirements.txt` is in repository root
2. Verify all packages are listed:
   ```
   streamlit>=1.31.0
   pandas>=2.1.0
   numpy>=1.24.0
   supabase>=2.3.0
   plotly>=5.17.0
   python-dotenv>=1.0.0
   ```
3. Force rebuild: Settings → "Reboot app"

### Issue: App shows old version

**Solution**: Cache or deployment lag
1. Clear cache: Click hamburger menu → "Clear cache"
2. Force restart: Settings → "Reboot app"
3. Hard refresh browser: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

### Issue: Python version errors

**Solution**: Python version mismatch
- Repository now includes `.python-version` file set to 3.11
- Streamlit Cloud will automatically use this version
- If issues persist, check Settings → Advanced → Python version

---

## Files Deployed

All dashboard files have been updated to support Streamlit Cloud secrets:

1. ✅ `proj344_master_dashboard.py` - Main 8-page dashboard
2. ✅ `supabase_dashboard.py` - File system cross-reference
3. ✅ `court_events_dashboard.py` - Court timeline
4. ✅ `legal_intelligence_dashboard.py` - Deep document analysis
5. ✅ `ceo_global_dashboard.py` - Holistic life management
6. ✅ `error_log_uploader.py` - System monitoring
7. ✅ `timeline_constitutional_violations.py` - Violation tracking

---

## Architecture

### Credential Loading Priority:
1. **Streamlit Cloud**: Reads from `st.secrets` (configured in Cloud UI)
2. **Local Development**: Reads from `.streamlit/secrets.toml` file
3. **Fallback**: Environment variables or defaults (for backward compatibility)

### Code Pattern:
```python
# Try Streamlit secrets first, then environment variables
url = st.secrets.get('SUPABASE_URL') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_URL')
key = st.secrets.get('SUPABASE_KEY') if hasattr(st, 'secrets') else os.environ.get('SUPABASE_KEY')
```

---

## Data Flow

```
Mac Mini (Processing)
      ↓
  Supabase Cloud Database
      ↓
Streamlit Cloud Dashboard ← You are here
      ↓
Web Browser (Users)
```

### Key Points:
- **Mac Mini** processes documents and uploads to Supabase
- **Supabase** is the central cloud database (PostgreSQL)
- **Streamlit Cloud** reads from Supabase in real-time
- **Both machines** (Mac and Cloud) connect to same database
- **Updates are instant** across all platforms

---

## Security Notes

⚠️ **IMPORTANT**: The secrets shown above contain your Supabase API key:
- This is the **anon/public** key (safe for client-side use)
- It has Row-Level Security (RLS) enabled in Supabase
- Never commit `.streamlit/secrets.toml` to Git (already in .gitignore)
- Streamlit Cloud secrets are encrypted at rest

---

## Monitoring

After deployment, monitor your app:

1. **Logs**: Settings → "Manage app" → "Logs" tab
2. **Metrics**: Check resource usage and errors
3. **Analytics**: Settings → "Analytics" for usage stats

---

## Need Help?

If issues persist after following this guide:

1. Check Streamlit Cloud logs for specific error messages
2. Verify Supabase connection by testing queries manually
3. Ensure Mac Mini is still processing and uploading data
4. Review commit history: latest commit should include secrets support

---

## Latest Deployment

**Commit**: `39f145e` - "Update dashboards for Streamlit Cloud deployment"

**Changes Included**:
- ✅ Streamlit secrets support in all dashboards
- ✅ Python 3.11 version specification
- ✅ Comprehensive documentation (PROJ344_DASHBOARD_GUIDE.md)
- ✅ Backward compatibility with environment variables

**Deployment Status**:
- Code pushed to GitHub: ✅
- Secrets configured: ⚠️ **YOU NEED TO DO THIS** (Step 2 above)
- App should auto-rebuild: ✅ (after secrets are added)

---

*Once you complete Step 2 (adding secrets), your Streamlit Cloud dashboard should work perfectly!*
