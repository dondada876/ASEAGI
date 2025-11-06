# 🚀 Deploy to Streamlit Cloud - Step-by-Step Guide

## ✅ Prerequisites (Already Done!)

- ✅ GitHub repository created: `https://github.com/dondada876/ASEAGI`
- ✅ All dashboards pushed to GitHub
- ✅ Requirements.txt configured
- ✅ .gitignore protecting secrets

---

## 🌐 Deploy to Streamlit Cloud (FREE!)

### Step 1: Go to Streamlit Cloud

1. Open your browser and go to: **https://share.streamlit.io**
2. Click **"Sign up"** or **"Sign in"** (if you have an account)
3. **Sign in with GitHub** (recommended - easiest option)
   - Authorize Streamlit to access your GitHub repositories

---

### Step 2: Deploy Your First Dashboard

#### **Option A: Deploy Enhanced Scanning Monitor**

1. Click **"New app"** (big button on the dashboard)
2. Fill in the deployment form:

   **Repository:** `dondada876/ASEAGI`

   **Branch:** `main`

   **Main file path:** `dashboards/enhanced_scanning_monitor.py`

   **App URL (custom):** `proj344-scanning-monitor` (or choose your own)

3. Click **"Advanced settings"**
4. In the **Secrets** section, paste this:

```toml
[secrets]
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c"
```

5. **Python version:** `3.11` (or leave default)
6. Click **"Deploy!"** 🚀

**Your app will be live at:**
```
https://dondada876-ASEAGI-dashboards-enhanced-scanning-monitor.streamlit.app
```

---

### Step 3: Deploy Other Dashboards

Repeat the process for each dashboard:

#### **PROJ344 Master Dashboard**

- **Main file path:** `dashboards/proj344_master_dashboard.py`
- **App URL:** `proj344-master`
- **Secrets:** Same as above
- **Live URL:** `https://dondada876-ASEAGI-dashboards-proj344-master-dashboard.streamlit.app`

#### **Legal Intelligence Dashboard**

- **Main file path:** `dashboards/legal_intelligence_dashboard.py`
- **App URL:** `proj344-legal-intel`
- **Secrets:** Same as above
- **Live URL:** `https://dondada876-ASEAGI-dashboards-legal-intelligence-dashboard.streamlit.app`

#### **CEO Dashboard**

- **Main file path:** `dashboards/ceo_dashboard.py`
- **App URL:** `proj344-ceo`
- **Secrets:** Same as above

#### **Timeline & Violations Dashboard**

- **Main file path:** `dashboards/timeline_violations_dashboard.py`
- **App URL:** `proj344-timeline`
- **Secrets:** Same as above

---

## 🎯 Quick Deploy Commands (If Using CLI)

If you install Streamlit CLI, you can deploy from terminal:

```bash
# Install Streamlit CLI
pip install streamlit

# Login to Streamlit Cloud
streamlit login

# Deploy app
streamlit deploy dashboards/enhanced_scanning_monitor.py
```

---

## 🔐 Managing Secrets

### To Update Secrets Later:

1. Go to https://share.streamlit.io
2. Click on your app
3. Click **"Settings"** (gear icon)
4. Go to **"Secrets"** tab
5. Edit and save

### **NEVER commit secrets to GitHub!** ✋

Your `.gitignore` already protects:
- `.env`
- `*.env`
- Credentials files
- API keys

---

## 📊 Monitoring Your Deployed Apps

### Streamlit Cloud Dashboard Features:

- ✅ **Live logs** - See real-time app logs
- ✅ **Analytics** - View visitor stats
- ✅ **Auto-deploy** - Updates when you push to GitHub
- ✅ **Custom domains** - Add your own domain (paid plans)
- ✅ **Sleep mode** - Apps sleep after inactivity (free plan)

### Wake Sleeping Apps:

Free tier apps sleep after 7 days of no visitors. They wake up when someone visits (takes ~30 seconds).

To keep apps awake:
- **Visit regularly**, or
- **Upgrade to a paid plan**, or
- **Use a uptime monitoring service** (like UptimeRobot)

---

## 🔄 Auto-Deploy on Git Push

**Already configured!** Whenever you push to GitHub:

```bash
cd /Users/dbucknor/Downloads/ASEAGI
git add .
git commit -m "Update dashboards"
git push origin main
```

Streamlit Cloud will **automatically redeploy** your apps! 🎉

---

## 🎨 Customizing Your App

### App Settings (Settings → General):

- **App name:** Display name for your app
- **Icon:** Choose an emoji icon
- **Theme:** Light/Dark mode
- **Wide mode:** Enable wide layout
- **Run on save:** Auto-reload during development

---

## 📱 Sharing Your Apps

### Public Apps (Default):

Anyone with the URL can access your apps.

**Share URLs:**
```
Enhanced Scanning Monitor:
https://dondada876-ASEAGI-dashboards-enhanced-scanning-monitor.streamlit.app

Master Dashboard:
https://dondada876-ASEAGI-dashboards-proj344-master-dashboard.streamlit.app
```

### Private Apps (Paid Plans):

Restrict access to specific email addresses or domains.

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"

**Fix:** Make sure all dependencies are in `requirements.txt`

```bash
cd /Users/dbucknor/Downloads/ASEAGI
cat requirements.txt
```

Should include:
```
streamlit==1.31.0
pandas==2.1.4
plotly==5.18.0
supabase==2.3.4
Pillow==10.2.0
python-dotenv==1.0.0
```

### "App is Sleeping"

**Fix:** Visit the app URL - it will wake up in ~30 seconds.

### "Secrets Not Found"

**Fix:**
1. Go to app Settings → Secrets
2. Add your Supabase credentials
3. Save and reboot app

### "Build Failed"

**Fix:** Check the logs in Streamlit Cloud dashboard for the error message.

Common issues:
- Missing requirement in `requirements.txt`
- Python version mismatch
- Syntax error in code

---

## 💡 Pro Tips

### 1. Use Branches for Testing

```bash
# Create test branch
git checkout -b test-feature

# Make changes and push
git push origin test-feature

# Deploy test branch to see changes before merging to main
```

### 2. Add Status Badge to README

Add this to your `README.md`:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
```

### 3. Monitor with UptimeRobot

Keep your app awake for free:
1. Sign up at https://uptimerobot.com
2. Add your Streamlit app URL
3. Set check interval to 5 minutes
4. App will never sleep!

---

## 📞 Need Help?

- **Streamlit Docs:** https://docs.streamlit.io
- **Community Forum:** https://discuss.streamlit.io
- **GitHub Issues:** https://github.com/streamlit/streamlit/issues

---

## ✅ Deployment Checklist

- [ ] Streamlit Cloud account created
- [ ] GitHub repository connected
- [ ] Enhanced Scanning Monitor deployed
- [ ] PROJ344 Master Dashboard deployed
- [ ] Legal Intelligence Dashboard deployed
- [ ] CEO Dashboard deployed
- [ ] Timeline Dashboard deployed
- [ ] Secrets configured for all apps
- [ ] Apps tested and working
- [ ] URLs shared with team

---

## 🎉 You're Done!

Your dashboards are now live on the internet! 🌐

**Next Steps:**
1. Visit your deployed apps
2. Share URLs with your team
3. Monitor usage in Streamlit Cloud dashboard
4. Keep pushing updates to GitHub for auto-deploy

---

**For Ashe. For Justice. For All Children.** 🛡️
