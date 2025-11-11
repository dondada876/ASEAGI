# 🤖 Telegram Bot Testing Guide - Document Classification

**Question:** Can you upload a document and get back its classification (legal vs personal)?

**Answer:** YES, but we need to check which version is running!

---

## 🔍 **Step 1: Check Which Bot Version You Have**

Run this on your droplet:

```bash
ssh root@137.184.1.91 << 'EOF'
echo "=========================================="
echo "🤖 Telegram Bot Version Check"
echo "=========================================="
echo ""

# Find Telegram bot processes
echo "📊 Running Telegram Bot:"
ps aux | grep -E "python.*telegram" | grep -v grep

echo ""
echo "📁 Bot Files in phase0_bug_tracker:"
ls -la /root/phase0_bug_tracker/scanners/*telegram*.py 2>/dev/null

echo ""
echo "🔍 Checking for AI Features:"
if [ -f "/root/phase0_bug_tracker/core/ai_analyzer.py" ]; then
    echo "  ✅ AI analyzer exists"
else
    echo "  ❌ AI analyzer NOT found"
fi

echo ""
echo "⚙️ Bot Configuration:"
cd /root/phase0_bug_tracker
if [ -f ".env" ]; then
    echo "  Checking .env for AI settings..."
    grep -E "USE_AI|ANTHROPIC" .env 2>/dev/null | sed 's/=.*/=***REDACTED***/' || echo "  ⚠️ No AI settings in .env"
else
    echo "  ⚠️ No .env file found"
fi
EOF
```

---

## 📊 **Two Possible Scenarios:**

### **Scenario A: OLD Bot (Manual Entry)** 🔴

**What you'll see when testing:**
```
You: [Upload document photo]
Bot: "📄 Document received!

     What type of document is this?
     1. Police Report
     2. Court Document
     3. CPS Report
     [... manual selection menu ...]"
```

**Features:**
- ❌ NO automatic classification
- ❌ NO AI analysis
- ❌ You must manually select type
- ❌ You must manually enter all metadata
- ⏱️ Takes 2-3 minutes per document

### **Scenario B: NEW AI Bot (Auto Classification)** 🟢

**What you'll see when testing:**
```
You: [Upload document photo]
Bot: "📄 Document received!
     ⏳ Analyzing document with AI... (~10-15 seconds)

     🤖 AI Analysis Complete!

     📋 Document Type: Police Report
     📅 Date: 2024-03-15
     📌 Title: Berkeley PD Incident Report #12345
     ⭐ Relevancy: 850 (High importance)
     📊 Confidence: 92%

     📝 Summary: Police report documenting incident...

     🎯 Classification: LEGAL

     What would you like to do?
     💾 Save (if confident)
     ✏️ Edit fields
     🔄 Manual Entry
     ❌ Cancel"
```

**Features:**
- ✅ Automatic AI classification
- ✅ Auto-extracts type, date, title
- ✅ Shows confidence scores
- ✅ Tells you LEGAL vs PERSONAL (via document type)
- ✅ Shows relevancy score (PROJ344)
- ⏱️ Takes ~30 seconds per document

---

## 🧪 **How to Test Your Bot:**

### **Step 1: Find Your Bot on Telegram**

1. Open Telegram on your phone
2. Search for your bot (you should have created it with @BotFather)
3. Or use the bot token to find it

**Don't know your bot name?** Run this:
```bash
ssh root@137.184.1.91 "grep TELEGRAM_BOT_TOKEN /root/phase0_bug_tracker/.env 2>/dev/null | cut -d: -f1"
```

The part before the `:` in the token is your bot's ID.

### **Step 2: Start Conversation**

1. Open your bot in Telegram
2. Send: `/start`

**Expected Response:**
- **OLD Bot:** Simple welcome message, asks you to upload document
- **NEW AI Bot:** Shows "🤖 AI-Powered Analysis: ENABLED" in welcome message

### **Step 3: Upload Test Document**

1. Take a photo of ANY document (driver's license, receipt, letter, etc.)
2. Send the photo to the bot
3. Wait for response

**What You'll See:**

**If OLD bot:**
```
Manual menu:
"What type of document is this?
 1. Police Report
 2. Court Document
 ..."
```

**If NEW AI bot:**
```
"⏳ Analyzing document with AI..."
[10-15 seconds later]
"🤖 AI Analysis Complete!

 Document Type: [Auto-detected]
 Date: [Auto-extracted]
 Classification: LEGAL or PERSONAL
 Confidence: XX%"
```

---

## 📋 **Document Classification Types:**

The AI bot can classify into **10 legal document types:**

### **Legal Documents:**
1. 🚔 **Police Report** - Law enforcement documents
2. ⚖️ **Court Document** - Filings, orders, motions
3. 📄 **Declaration** - Sworn statements
4. 📸 **Evidence** - Photos, physical evidence
5. 👶 **CPS Report** - Child Protective Services
6. 🏥 **Medical Record** - Healthcare documents
7. 🏫 **School Record** - Educational records
8. 📧 **Communication** - Emails, texts, letters
9. 📰 **News Article** - Media coverage
10. 📁 **Other** - Miscellaneous legal docs

### **Personal Documents:**
- If the AI detects it's NOT related to your legal case, it will classify as "Other" with low relevancy score

**Classification Logic:**
- **LEGAL:** relevancy_number >= 500 (case-related)
- **PERSONAL:** relevancy_number < 500 (not case-related)

---

## 🎯 **Test Example:**

**Upload:** Photo of a police report

**AI Response (NEW bot):**
```
🤖 AI Analysis Complete!

📋 Document Type: Police Report
📅 Date: 2024-03-15
📌 Title: Berkeley PD Incident Report
⭐ Relevancy: 850/1000
📊 Confidence: 92%

🎯 Classification: LEGAL (High priority)

🔍 Legal Indicators Found:
  - ✅ Official law enforcement document
  - ✅ Case-related incident
  - ✅ Contains evidence

📝 Summary: Police incident report documenting [incident details]...

What would you like to do?
💾 Save
✏️ Edit
🔄 Manual Entry
❌ Cancel
```

**Upload:** Photo of a grocery receipt

**AI Response (NEW bot):**
```
🤖 AI Analysis Complete!

📋 Document Type: Other
📅 Date: 2024-11-10
📌 Title: Grocery Receipt
⭐ Relevancy: 100/1000
📊 Confidence: 85%

🎯 Classification: PERSONAL (Not case-related)

⚠️ This document appears to be personal/non-legal.

Would you still like to save it?
💾 Save anyway
❌ Cancel
```

---

## ⚙️ **If You Have the OLD Bot - How to Upgrade:**

### **Option 1: Clone ASEAGI Repo with New Bot**

```bash
ssh root@137.184.1.91 << 'EOF'
# Clone the ASEAGI repo (has the new AI bot)
cd /root
git clone https://github.com/dondada876/ASEAGI.git
cd ASEAGI
git checkout claude/framework-comparison-guide-011CUyvuditeFNvRT8iUjHoC

# Copy AI analyzer to phase0_bug_tracker
cp ai_analyzer.py /root/phase0_bug_tracker/core/

# Copy new bot to phase0_bug_tracker
cp telegram_document_bot.py /root/phase0_bug_tracker/scanners/

# Add AI settings to .env
cat >> /root/phase0_bug_tracker/.env << 'ENVEOF'

# AI Analysis Settings
USE_AI_ANALYSIS=true
ANTHROPIC_API_KEY=your_key_here
# Or use OpenAI:
# OPENAI_API_KEY=your_key_here
ENVEOF

# Restart the bot
pkill -f telegram_document_bot.py
cd /root/phase0_bug_tracker
nohup python3 scanners/telegram_document_bot.py > logs/telegram_bot.log 2>&1 &

echo "✅ AI bot deployed!"
EOF
```

### **Option 2: Keep Using OLD Bot**

If you prefer manual entry, that's fine! The old bot works, it just doesn't have AI classification.

---

## 🔐 **Getting AI API Keys:**

### **Option A: Anthropic (Claude) - Recommended**

1. Go to https://console.anthropic.com/
2. Sign up / Log in
3. Go to API Keys
4. Create new key
5. Copy the key (starts with `sk-ant-`)
6. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-...`

**Cost:** ~$0.01 per document analyzed (very cheap)

### **Option B: OpenAI (GPT-4 Vision)**

1. Go to https://platform.openai.com/
2. Sign up / Log in
3. API Keys → Create new key
4. Copy the key (starts with `sk-`)
5. Add to `.env`: `OPENAI_API_KEY=sk-...`

**Cost:** ~$0.02-0.03 per document analyzed

---

## 📱 **Quick Test Checklist:**

- [ ] Run version check command
- [ ] Open Telegram bot
- [ ] Send `/start`
- [ ] Check if it says "AI-Powered" in welcome
- [ ] Upload a test photo
- [ ] See if it auto-analyzes (NEW) or asks for manual input (OLD)
- [ ] Report back which version you have

---

## 🎯 **Summary:**

**What you're asking:**
✅ YES - Upload document → Get classification → See if it's legal/personal

**Current status:**
❓ UNKNOWN - Need to check which bot version is running

**Next step:**
1. Run the version check command
2. Test by uploading a document
3. Tell me what response you get
4. I'll help you upgrade to AI bot if needed

---

**Run the version check command and test your bot, then show me what happens!** 🚀
