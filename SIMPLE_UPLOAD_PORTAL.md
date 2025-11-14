# 📁 Simple Document Upload Portal

**Clean, minimal web interface for uploading documents**
**Optimized for Surface Pro and touch devices**

---

## 🌐 Access URL

**Open this in your browser:**

```
http://137.184.1.91:8505
```

---

## ✅ Features

- ✅ **Simple drag & drop interface**
- ✅ **Multiple file upload** (upload many files at once)
- ✅ **Instant confirmation** (see upload status immediately)
- ✅ **Progress tracking** (watch files upload one by one)
- ✅ **Recent uploads list** (see what you've uploaded)
- ✅ **Touch-friendly** (optimized for Surface Pro)
- ✅ **No login required** (just upload and go)

---

## 📂 Supported File Types

- **Documents:** PDF, TXT, DOCX, DOC, RTF
- **Images:** JPG, JPEG, PNG

---

## 🚀 How to Upload

### Method 1: Click to Browse
1. Open http://137.184.1.91:8505 in your browser
2. Click **"Choose files to upload"** button
3. Select one or more files
4. Click **"🚀 UPLOAD NOW"** button
5. Wait for confirmation ✅

### Method 2: Drag & Drop
1. Open http://137.184.1.91:8505 in your browser
2. Drag files from your File Explorer
3. Drop them on the upload area
4. Click **"🚀 UPLOAD NOW"** button
5. Wait for confirmation ✅

---

## 💾 Where Files Are Stored

All uploaded files are saved securely to:

```
/home/user/ASEAGI/uploads/web_uploads/
```

You can access them from the server at any time.

---

## 🖥️ Portal Controls

### Start Portal
```bash
cd /home/user/ASEAGI/dashboards
streamlit run simple_document_upload.py --server.port 8505 --server.address 0.0.0.0 &
```

### Stop Portal
```bash
lsof -ti:8505 | xargs kill -9
```

### Check if Running
```bash
lsof -i:8505
```

### View Logs
```bash
tail -f /tmp/simple_upload.log
```

---

## 📱 Surface Pro Tips

1. **Use Microsoft Edge** for best touch experience
2. **Enable full screen mode** (F11) for cleaner interface
3. **Use stylus or finger** to drag and drop files
4. **Bookmark the URL** for quick access

---

## 🔧 Troubleshooting

### "Connection refused" or page won't load

**Check if portal is running:**
```bash
lsof -i:8505
```

**If nothing shows, restart portal:**
```bash
cd /home/user/ASEAGI/dashboards
streamlit run simple_document_upload.py --server.port 8505 --server.address 0.0.0.0 &
```

### "Upload button doesn't appear"

1. **Hard refresh:** Ctrl+Shift+R (or Cmd+Shift+R on Mac)
2. **Clear cache:** Browser settings → Clear browsing data
3. **Try different browser:** Chrome, Edge, Firefox
4. **Check browser console:** F12 → look for errors

### Files not uploading

1. **Check file size** (files over 200MB may fail)
2. **Check file type** (only supported types work)
3. **Check disk space:**
   ```bash
   df -h /home/user/ASEAGI/uploads/
   ```

---

## 📊 View Uploaded Files

**From command line:**
```bash
ls -lh /home/user/ASEAGI/uploads/web_uploads/
```

**In portal:**
Scroll to bottom of page to see "Recent Uploads" section

---

## 🆚 Comparison with Other Options

| Method | Status | Best For |
|--------|--------|----------|
| **Simple Upload Portal (8505)** | ✅ **WORKING** | **Quick uploads from Surface Pro** |
| Upload Dashboard (8503) | ⚠️ Issue | Advanced features (if working) |
| Telegram Bot | ❌ Broken | Mobile quick uploads (when fixed) |
| Test Upload (8504) | ✅ Working | Testing only |

---

## 📝 What Happens After Upload

1. **Files are saved** to `/home/user/ASEAGI/uploads/web_uploads/`
2. **MD5 hash calculated** for file verification
3. **Upload confirmed** on screen with green checkmark ✅
4. **File appears** in "Recent Uploads" list

**Next steps you can do manually:**
- Move files to specific folders
- Run analysis scripts on uploaded files
- Upload to database (Supabase)
- Process with Claude API

---

## 🔐 Security Notes

- Portal is accessible from any device on the network
- No authentication currently (add if needed)
- Files are stored on the server (not publicly accessible)
- Consider adding password protection if needed

---

## 📞 Support

**Portal not working?**
1. Check logs: `tail -f /tmp/simple_upload.log`
2. Restart portal: See "Portal Controls" above
3. Check port is open: `lsof -i:8505`

**Need help?**
- Portal files: `/home/user/ASEAGI/dashboards/simple_document_upload.py`
- Upload directory: `/home/user/ASEAGI/uploads/web_uploads/`
- Logs: `/tmp/simple_upload.log`

---

## ✨ Features Coming Soon

- [ ] Automatic Claude AI analysis
- [ ] Upload to Supabase database
- [ ] File categorization
- [ ] Duplicate detection
- [ ] Bulk delete option
- [ ] Download uploaded files

---

**Status:** 🟢 RUNNING
**Port:** 8505
**URL:** http://137.184.1.91:8505
**Storage:** /home/user/ASEAGI/uploads/web_uploads/

**Ready to use! Open the URL and start uploading!** 🚀
