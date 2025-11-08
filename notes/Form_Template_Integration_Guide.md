# Form Template Integration & Submission Workflow
**Created:** 2025-11-07
**Purpose:** Use REAL court form templates and multi-channel submission

---

## 🎯 THE BETTER APPROACH

You're absolutely right - we should use **existing court form templates** instead of creating PDFs from scratch!

**California Courts provide fillable PDF forms:**
- JV-180: https://www.courts.ca.gov/documents/jv180.pdf
- JV-575: https://www.courts.ca.gov/documents/jv575.pdf

---

## 🔑 PART 1: WHERE TO PUT ANTHROPIC API KEY

### **Option 1: .streamlit/secrets.toml** (RECOMMENDED)

**Add to existing file:**
```bash
nano /home/user/ASEAGI/.streamlit/secrets.toml
```

**Add this line:**
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_KEY_HERE"
```

**Full file should look like:**
```toml
# Add your Supabase credentials here
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_KEY_HERE"
```

**Get your key:** https://console.anthropic.com/settings/keys

---

### **Option 2: config.toml** (Alternative)

Already created at `/home/user/ASEAGI/config.toml`

Just update:
```toml
anthropic_api_key = "sk-ant-api03-YOUR_KEY_HERE"
```

---

### **Option 3: Environment Variable** (SSH Sessions)

Add to `~/.bashrc` or `~/.profile`:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-YOUR_KEY_HERE"
```

Then reload:
```bash
source ~/.bashrc
```

---

## 📋 PART 2: USING REAL COURT FORM TEMPLATES

### **Download Official Templates**

```bash
cd /home/user/ASEAGI
mkdir -p templates/court_forms

# Download JV-180
curl -o templates/court_forms/jv180.pdf \
  https://www.courts.ca.gov/documents/jv180.pdf

# Download JV-575
curl -o templates/court_forms/jv575.pdf \
  https://www.courts.ca.gov/documents/jv575.pdf
```

### **Use PyPDF2 to Fill Forms**

**Install dependency:**
```bash
pip install PyPDF2
```

**Update requirements.txt:**
```
PyPDF2>=3.0.0
```

### **Updated Code Architecture**

Instead of creating PDFs from scratch, we:

1. **Download official fillable PDFs** from California Courts
2. **Fill in the form fields** programmatically using PyPDF2
3. **Save completed forms** to output directory
4. **Upload to multiple destinations** (Supabase, Dropbox, Email, Telegram)

---

## 📤 PART 3: COMPLETE SUBMISSION WORKFLOW

When form is generated, it should:

### **1. Save to Supabase Storage**
```python
# Upload PDF to Supabase Storage bucket
supabase.storage.from_('legal_filings').upload(
    f'case_{case_id}/JV180_JV575_{timestamp}.pdf',
    pdf_bytes
)

# Store metadata in database
supabase.table('generated_forms').insert({
    'case_id': 'J24-00478',
    'form_type': 'JV-180/JV-575',
    'generated_at': datetime.now(),
    'storage_path': f'case_{case_id}/JV180_JV575_{timestamp}.pdf',
    'status': 'generated'
})
```

### **2. Send via Telegram Bot**
```python
# Send PDF as document
telegram_bot.send_document(
    chat_id=user_chat_id,
    document=open('JV180_JV575.pdf', 'rb'),
    caption=f'✅ Forms generated for case {case_id}\n\nReview and file with court.'
)
```

### **3. Upload to Dropbox**
```python
import dropbox

dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)
dbx.files_upload(
    pdf_bytes,
    f'/Legal_Filings/Case_{case_id}/JV180_JV575_{timestamp}.pdf'
)
```

### **4. Send via Email**
```python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

msg = MIMEMultipart()
msg['Subject'] = f'Legal Forms Ready - Case {case_id}'
msg['From'] = 'noreply@aseagi.com'
msg['To'] = 'don@example.com'

# Attach PDF
attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
attachment.add_header('Content-Disposition', 'attachment',
                     filename='JV180_JV575.pdf')
msg.attach(attachment)

# Send
smtp = smtplib.SMTP('smtp.gmail.com', 587)
smtp.starttls()
smtp.login(email_user, email_pass)
smtp.send_message(msg)
```

### **5. Make Available in Streamlit Dashboard**
```python
# In dashboard
st.download_button(
    label="📥 Download JV-180/JV-575",
    data=pdf_bytes,
    file_name=f"JV180_JV575_{case_id}.pdf",
    mime="application/pdf"
)
```

---

## 🔄 COMPLETE WORKFLOW DIAGRAM

```
User Request (via Telegram/Streamlit)
         ↓
Query Supabase for Evidence
         ↓
Generate Text with Claude API
         ↓
Fill Official Court Form Templates (PyPDF2)
         ↓
Save Completed PDF
         ↓
┌────────┴────────┐
│                 │
│  Multi-Channel  │
│   Distribution  │
│                 │
└────────┬────────┘
         ↓
    ┌────┴────┬────────┬─────────┬──────────┐
    ↓         ↓        ↓         ↓          ↓
Supabase  Telegram  Dropbox   Email    Streamlit
Storage     Bot                          Dashboard
```

---

## 🛠️ UPDATED IMPLEMENTATION PLAN

### **Phase 1: Add Form Template Support**

**File:** `core/form_generation/form_filler_v2.py`

```python
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter

class FormTemplateFiller:
    def fill_jv180(self, data: dict, template_path: str, output_path: str):
        """Fill JV-180 template with generated text"""
        reader = PdfReader(template_path)
        writer = PdfWriter()

        # Fill form fields
        writer.add_page(reader.pages[0])
        writer.update_page_form_field_values(
            writer.pages[0],
            {
                'case_number': data['case_id'],
                'changed_circumstances': data['changed_circumstances'],
                'best_interest': data['best_interest'],
                # ... other fields
            }
        )

        # Save
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
```

### **Phase 2: Multi-Channel Distribution**

**File:** `core/form_generation/form_distributor.py`

```python
class FormDistributor:
    def __init__(self, config):
        self.supabase = create_client(config['supabase_url'], config['supabase_key'])
        self.telegram = TelegramBot(config['telegram_token'])
        self.dropbox = Dropbox(config['dropbox_token'])
        self.email_config = config['email']

    def distribute(self, pdf_path: str, case_id: str, channels: list):
        """Distribute form to multiple channels"""
        results = {}

        if 'supabase' in channels:
            results['supabase'] = self.upload_to_supabase(pdf_path, case_id)

        if 'telegram' in channels:
            results['telegram'] = self.send_via_telegram(pdf_path, case_id)

        if 'dropbox' in channels:
            results['dropbox'] = self.upload_to_dropbox(pdf_path, case_id)

        if 'email' in channels:
            results['email'] = self.send_via_email(pdf_path, case_id)

        return results
```

### **Phase 3: Telegram Integration**

**File:** `core/form_generation/telegram_handler.py`

```python
from telegram import Update, Bot
from telegram.ext import CommandHandler, Application

class FormFilingBot:
    def __init__(self, token, form_filler):
        self.bot = Bot(token)
        self.form_filler = form_filler

    async def generate_forms_command(self, update: Update, context):
        """Handle /generate_forms command"""
        chat_id = update.effective_chat.id
        case_id = context.args[0] if context.args else 'J24-00478'

        await update.message.reply_text(
            f"🔄 Generating forms for case {case_id}...\n"
            "This will take 2-3 minutes."
        )

        # Generate forms
        output_dir = f'/tmp/forms_{case_id}'
        self.form_filler.run(case_id, output_dir)

        # Send PDFs
        pdf_path = f'{output_dir}/{case_id}_JV180_JV575.pdf'
        await self.bot.send_document(
            chat_id=chat_id,
            document=open(pdf_path, 'rb'),
            caption=f'✅ Forms ready for case {case_id}'
        )

        await update.message.reply_text(
            "📋 Next steps:\n"
            "1. Review forms for accuracy\n"
            "2. Sign where indicated\n"
            "3. File with court clerk\n"
            "4. Serve on all parties"
        )
```

---

## 📊 SUPABASE DATABASE SCHEMA

**New table: `generated_forms`**

```sql
CREATE TABLE generated_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id VARCHAR(50) NOT NULL,
    form_type VARCHAR(100) NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    storage_path TEXT,
    dropbox_path TEXT,
    telegram_message_id BIGINT,
    email_sent_at TIMESTAMPTZ,
    status VARCHAR(50) DEFAULT 'generated',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_forms_case_id ON generated_forms(case_id);
CREATE INDEX idx_forms_status ON generated_forms(status);
```

---

## 🎨 STREAMLIT DASHBOARD INTEGRATION

**Add to existing dashboard:**

```python
import streamlit as st

st.header("📋 Generate Court Forms")

case_id = st.text_input("Case ID", value="J24-00478")

if st.button("🚀 Generate JV-180/JV-575"):
    with st.spinner("Generating forms... This will take 2-3 minutes"):
        # Run form filler
        from core.form_generation import EmergencyFormFiller

        filler = EmergencyFormFiller(
            supabase_url=st.secrets['SUPABASE_URL'],
            supabase_key=st.secrets['SUPABASE_KEY'],
            anthropic_key=st.secrets['ANTHROPIC_API_KEY']
        )

        filler.run(case_id, './output')

        st.success("✅ Forms generated!")

        # Download buttons
        with open(f'./output/{case_id}_JV180_JV575.pdf', 'rb') as f:
            st.download_button(
                "📥 Download JV-180/JV-575",
                f.read(),
                file_name=f'{case_id}_JV180_JV575.pdf'
            )

        # Distribution options
        st.subheader("📤 Distribute Forms")

        send_telegram = st.checkbox("Send to Telegram")
        send_email = st.checkbox("Send via Email")
        upload_dropbox = st.checkbox("Upload to Dropbox")

        if st.button("📤 Distribute"):
            # Use FormDistributor to send
            pass
```

---

## 🔐 CREDENTIALS NEEDED

### **Update .streamlit/secrets.toml:**

```toml
# Supabase
SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIs..."

# Anthropic (Claude API)
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_KEY_HERE"

# Telegram Bot
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Dropbox
DROPBOX_ACCESS_TOKEN = "YOUR_DROPBOX_TOKEN"

# Email (Gmail)
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
EMAIL_RECIPIENT = "don@example.com"
```

### **How to Get Each Key:**

1. **Anthropic:** https://console.anthropic.com/settings/keys
2. **Telegram Bot:** Talk to @BotFather on Telegram
3. **Dropbox:** https://www.dropbox.com/developers/apps
4. **Gmail App Password:** https://myaccount.google.com/apppasswords

---

## 🚀 QUICK IMPLEMENTATION

### **Step 1: Add Anthropic Key**

```bash
nano /home/user/ASEAGI/.streamlit/secrets.toml
```

Add:
```toml
ANTHROPIC_API_KEY = "sk-ant-api03-YOUR_KEY_HERE"
```

### **Step 2: Download Court Form Templates**

```bash
cd /home/user/ASEAGI
mkdir -p templates/court_forms

curl -o templates/court_forms/jv180.pdf \
  https://www.courts.ca.gov/documents/jv180.pdf

curl -o templates/court_forms/jv575.pdf \
  https://www.courts.ca.gov/documents/jv575.pdf
```

### **Step 3: Install Additional Dependencies**

```bash
pip install PyPDF2 python-telegram-bot dropbox
```

### **Step 4: Test Basic Form Generation**

```bash
python core/form_generation/run_form_filler.py \
  --case-id J24-00478 \
  --output ./test_output
```

---

## 💡 RECOMMENDED WORKFLOW

**For Your Use Case:**

1. **User triggers via Telegram:** `/generate_forms J24-00478`
2. **Bot queries Supabase** for evidence
3. **Claude generates** legal arguments
4. **System fills** official court form templates
5. **PDFs saved to:**
   - ✅ Supabase Storage (permanent record)
   - ✅ Sent to Telegram (immediate access)
   - ✅ Uploaded to Dropbox (backup/sharing)
   - ✅ Emailed to you (notification)
   - ✅ Available in Streamlit dashboard (web access)
6. **Metadata logged** in `generated_forms` table

**Single command, multiple distribution channels!**

---

## 🎯 NEXT STEPS

### **Immediate:**
1. Add `ANTHROPIC_API_KEY` to `.streamlit/secrets.toml`
2. Download court form templates
3. Test current system

### **Short-term:**
1. Implement PyPDF2 form filling
2. Add Telegram bot integration
3. Add Dropbox upload

### **Medium-term:**
1. Add email distribution
2. Create Streamlit form generator page
3. Track all generations in database

**Want me to implement any of these now?**

---

**Last Updated:** 2025-11-07
**Status:** Design Complete - Ready for Implementation
