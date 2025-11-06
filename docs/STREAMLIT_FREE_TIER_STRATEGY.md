# 🔒 Streamlit Free Tier Strategy

## ⚠️ Community Cloud Limitation

**Free Tier Allows:**
- ✅ **Unlimited PUBLIC apps**
- ⚠️ **Only 1 PRIVATE app** per workspace

---

## 🎯 Recommended Strategy

Since your dashboards contain **case-sensitive data**, here are your options:

### **Option 1: Make PROJ344 Master Dashboard Private** ⭐ RECOMMENDED

**Make PRIVATE (your 1 private app):**
- `proj344_master_dashboard.py` - Contains full case data with smoking guns

**Deploy as PUBLIC (but obscure the URLs):**
- `enhanced_scanning_monitor.py` - Shows processing stats only (no PII)
- `legal_intelligence_dashboard.py` - Could sanitize or deploy with auth
- `ceo_dashboard.py` - File organization only (no content)
- `timeline_violations_dashboard.py` - Timeline data (could be sensitive)

**Security Note:** Even public apps are hard to find unless you share the URL. Streamlit generates random URLs like:
```
https://dondada876-proj344-dashboards-dashboards-enhanced-mon-a8f2kl.streamlit.app
```

---

### **Option 2: Deploy Only Non-Sensitive Dashboards**

**Make PRIVATE:**
- `proj344_master_dashboard.py` (full case data)

**Keep LOCAL ONLY (don't deploy):**
- `legal_intelligence_dashboard.py` (contains case details)
- `timeline_violations_dashboard.py` (contains case timeline)

**Deploy as PUBLIC:**
- `enhanced_scanning_monitor.py` (just processing metrics)
- `ceo_dashboard.py` (file organization stats)

**Advantage:** Maximum privacy, minimum exposure

---

### **Option 3: Sanitize Data for Public Deployment**

Before deploying publicly, modify dashboards to:

1. **Remove case numbers** (replace "J24-00478" with "Case #XXXX")
2. **Redact names** (replace actual names with "Party A", "Party B")
3. **Hide sensitive documents** (filter out docs with high fraud scores)
4. **Show only aggregated stats** (no individual document details)

**Then deploy all as PUBLIC** (use your 1 private slot for Master Dashboard)

---

### **Option 4: Use GitHub Pages + Password Protection**

Deploy as **static HTML** with basic auth:

1. Export dashboards to HTML:
```bash
streamlit run your_dashboard.py &
# Then use browser to save as HTML
```

2. Host on **GitHub Pages** (free)
3. Add **htaccess password protection**

**Advantage:** Full control, no Streamlit limitations
**Disadvantage:** Not interactive/live data

---

### **Option 5: Upgrade to Streamlit Teams** 💰

**Streamlit Teams Plan:** $250/month
- ✅ **Unlimited private apps**
- ✅ **Custom domains**
- ✅ **SSO authentication**
- ✅ **No sleep mode**
- ✅ **Priority support**

**Worth it if:**
- You need multiple private dashboards
- You want professional domains
- You need team collaboration features

---

## 🛡️ My Recommendation for Your Case

Given this is **active litigation data (D22-03244)**, I recommend:

### **Deploy Strategy:**

#### **1. PRIVATE App (Your 1 Private Slot):**
```
dashboards/proj344_master_dashboard.py
```
**Why:** Contains full case intelligence, smoking guns, perjury indicators

#### **2. PUBLIC Apps (Safe to Deploy):**

**Enhanced Scanning Monitor:**
```
dashboards/enhanced_scanning_monitor.py
```
✅ Safe: Only shows processing metrics, no case content

**CEO Dashboard:**
```
dashboards/ceo_dashboard.py
```
✅ Safe: File organization stats only, no document content

#### **3. KEEP LOCAL (Don't Deploy Yet):**

**Legal Intelligence Dashboard:**
```
dashboards/legal_intelligence_dashboard.py
```
❌ Contains: Document-by-document analysis with case details

**Timeline Violations Dashboard:**
```
dashboards/timeline_violations_dashboard.py
```
❌ Contains: Case timeline with specific dates and events

---

## 🔐 Additional Security Measures

Even for PUBLIC apps, you can add security:

### **1. Environment-Based Access Control**

Add to your dashboard:

```python
import os
import streamlit as st

# Simple password protection
PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "default")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    password = st.text_input("Enter Password:", type="password")
    if st.button("Login"):
        if password == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")
    st.stop()

# Rest of your dashboard code...
```

Add to Streamlit Cloud secrets:
```toml
DASHBOARD_PASSWORD = "YourSecurePassword123!"
```

### **2. IP Whitelist (Code-Based)**

```python
import streamlit as st
import requests

def get_client_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "unknown"

ALLOWED_IPS = ["YOUR_IP_ADDRESS", "OFFICE_IP"]

client_ip = get_client_ip()
if client_ip not in ALLOWED_IPS:
    st.error("Access denied. Contact administrator.")
    st.stop()
```

### **3. Time-Limited Access**

```python
from datetime import datetime, timedelta

EXPIRY_DATE = datetime(2025, 12, 31)

if datetime.now() > EXPIRY_DATE:
    st.error("This dashboard has expired. Please contact administrator.")
    st.stop()
```

---

## 📋 Deployment Checklist (Free Tier)

### **Step 1: Deploy Enhanced Scanning Monitor (PUBLIC)**

1. Go to https://share.streamlit.io
2. Click "New app"
3. **Repository:** `dondada876/proj344-dashboards`
4. **Branch:** `main`
5. **Main file:** `dashboards/enhanced_scanning_monitor.py`
6. **Visibility:** ✅ PUBLIC
7. Add secrets (Supabase credentials)
8. Deploy!

### **Step 2: Deploy PROJ344 Master Dashboard (PRIVATE)**

1. Click "New app"
2. **Repository:** `dondada876/proj344-dashboards`
3. **Branch:** `main`
4. **Main file:** `dashboards/proj344_master_dashboard.py`
5. **Visibility:** 🔒 PRIVATE (use your 1 private slot)
6. Add secrets
7. Deploy!

### **Step 3: Deploy CEO Dashboard (PUBLIC)**

1. Click "New app"
2. **Repository:** `dondada876/proj344-dashboards`
3. **Branch:** `main`
4. **Main file:** `dashboards/ceo_dashboard.py`
5. **Visibility:** ✅ PUBLIC
6. Add secrets
7. Deploy!

### **Step 4: Keep Local (For Now)**

Run these locally or wait for paid plan:
- `legal_intelligence_dashboard.py`
- `timeline_violations_dashboard.py`

---

## 🎯 When to Upgrade to Paid Plan

**Upgrade if you need:**
- ✅ More than 1 private app
- ✅ Custom domain (proj344-dashboard.yoursite.com)
- ✅ No app sleep (always-on)
- ✅ SSO/SAML authentication
- ✅ Team collaboration features
- ✅ Priority support

**Pricing:**
- **Streamlit Teams:** $250/month (1 workspace, unlimited private apps)
- **Streamlit Enterprise:** Custom pricing (multiple workspaces, advanced features)

---

## 💡 Alternative: Self-Host

If you don't want to pay or expose case data:

**Run on your own server:**

```bash
# On your Mac (always on)
streamlit run dashboards/proj344_master_dashboard.py --server.port 8501

# Or use Docker
docker-compose up -d
```

**Access via:**
- **Local network:** `http://your-mac-ip:8501`
- **VPN:** Set up VPN for secure remote access
- **SSH Tunnel:** `ssh -L 8501:localhost:8501 your-mac`

---

## ✅ Final Recommendation

**For Your Case (Legal/Sensitive Data):**

1. ✅ **Deploy Scanning Monitor as PUBLIC** (safe - no case data)
2. 🔒 **Deploy Master Dashboard as PRIVATE** (your 1 private slot)
3. ✅ **Deploy CEO Dashboard as PUBLIC** (safe - file stats only)
4. 🏠 **Keep Legal & Timeline LOCAL** (too sensitive for public)
5. 🔐 **Add password protection** to public apps (see code above)
6. 💰 **Consider upgrading** to Teams ($250/mo) if you need all dashboards online

**This gives you:**
- 3 dashboards online (2 public, 1 private)
- 2 dashboards local-only (most sensitive)
- Cost: **$0/month** (free tier)
- Security: Private data protected

---

**Questions?** Check `DEPLOY_TO_STREAMLIT.md` for detailed deployment steps!

**For Ashe. For Justice. For All Children.** 🛡️
