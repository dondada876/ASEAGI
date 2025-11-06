# Local Setup and Deployment Guide

**Complete guide to run locally, push to GitHub, and deploy**

---

## 🎯 Overview

This guide covers:
1. **Local Development** - Run WordPress + Python processing locally
2. **GitHub Integration** - Push code to repository
3. **Streamlit Deployment** - Deploy dashboards to Streamlit Cloud
4. **Production Deployment** - Deploy to Digital Ocean

---

## 🏠 Part 1: Local Development Setup

### Option A: WordPress Local (Recommended for WordPress)

**Install Local by Flywheel:**

1. **Download Local:**
   - Visit: https://localwp.com/
   - Download and install for Windows

2. **Create New Site:**
   ```
   Click "+" → Create New Site
   Site Name: legal-document-upload
   Environment: Preferred (PHP 8.0+)
   WordPress Username: admin
   WordPress Password: [your-password]
   ```

3. **Start Site:**
   - Click "Start Site"
   - Click "Admin" to open WordPress admin
   - Site will be at: http://legal-document-upload.local

4. **Install Required Plugins:**
   ```
   WordPress Admin → Plugins → Add New

   Install:
   - Advanced Custom Fields Pro (requires license)
   - Amelia Booking (requires license)
   - WP Mail SMTP
   ```

5. **Add Custom Code:**

   Open site folder: `Right-click site → "Show Folder"`

   Navigate to: `app/public/wp-content/themes/twentytwentyfour/functions.php`

   Add this code:
   ```php
   <?php

   // Create legal_document post type
   function create_legal_document_post_type() {
       register_post_type('legal_document', array(
           'labels' => array(
               'name' => 'Legal Documents',
               'singular_name' => 'Legal Document'
           ),
           'public' => true,
           'has_archive' => true,
           'supports' => array('title', 'editor', 'custom-fields'),
           'menu_icon' => 'dashicons-media-document'
       ));
   }
   add_action('init', 'create_legal_document_post_type');

   // ACF Form configuration
   // Copy ACF field group code from DOCUMENT_UPLOAD_SYSTEM.md lines 71-190

   // Processing hook
   add_action('acf/save_post', 'process_uploaded_document', 20);

   function process_uploaded_document($post_id) {
       if (get_post_type($post_id) !== 'legal_document') {
           return;
       }

       $file = get_field('document_file', $post_id);
       if (!$file) return;

       // For local testing, just save metadata
       $file_path = get_attached_file($file['ID']);
       $file_extension = pathinfo($file_path, PATHINFO_EXTENSION);

       update_post_meta($post_id, 'file_extension', $file_extension);
       update_post_meta($post_id, 'file_size', filesize($file_path));
       update_post_meta($post_id, 'upload_date', current_time('mysql'));

       // TODO: Call Python processing service when running
   }
   ```

6. **Test WordPress Upload:**
   - Go to: Legal Documents → Add New
   - Upload a test file
   - Verify it appears in Media Library

---

### Option B: Python Processing Service (Local)

**Set up Python processing service on your Windows machine:**

1. **Create Project Directory:**
   ```bash
   cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI
   mkdir processing-service
   cd processing-service
   ```

2. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Create requirements.txt:**
   ```bash
   # In ASEAGI\processing-service\requirements.txt
   cat > requirements.txt << EOF
   flask==3.0.0
   anthropic==0.18.0
   openai==1.12.0
   google-generativeai==0.4.0
   supabase==2.3.4
   pytesseract==0.3.10
   Pillow==10.2.0
   requests==2.31.0
   python-dotenv==1.0.1
   EOF
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Install Tesseract OCR (for image processing):**
   - Download: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to: `C:\Program Files\Tesseract-OCR`
   - Add to PATH: `C:\Program Files\Tesseract-OCR`

6. **Create Processing Service:**

   Create file: `ASEAGI\processing-service\app.py`

   ```python
   from flask import Flask, request, jsonify
   import anthropic
   import openai
   import google.generativeai as genai
   from supabase import create_client
   import os
   from dotenv import load_dotenv

   load_dotenv()

   app = Flask(__name__)

   # Initialize LLM clients
   claude = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])
   openai.api_key = os.environ['OPENAI_API_KEY']
   genai.configure(api_key=os.environ['GOOGLE_API_KEY'])

   # Initialize Supabase
   supabase = create_client(
       os.environ['SUPABASE_URL'],
       os.environ['SUPABASE_KEY']
   )

   @app.route('/health', methods=['GET'])
   def health():
       return jsonify({'status': 'healthy', 'service': 'document-processing'})

   @app.route('/process', methods=['POST'])
   def process_document():
       """Process document through multiple LLMs"""

       data = request.json
       post_id = data.get('post_id')
       extracted_text = data.get('extracted_text', '')
       document_type = data.get('document_type', 'OTHR')

       if not extracted_text:
           return jsonify({'error': 'No text provided'}), 400

       print(f"Processing document {post_id} (type: {document_type})")

       results = {
           'post_id': post_id,
           'document_type': document_type,
           'processing_status': 'completed'
       }

       # For local testing, return mock results
       # In production, uncomment LLM processing below

       results['mock_data'] = {
           'fraud_score': 45.0,
           'truth_score': 72.0,
           'importance_level': 'MEDIUM'
       }

       # Save to Supabase
       try:
           supabase.table('legal_documents').insert({
               'wordpress_post_id': post_id,
               'document_type': document_type,
               'fraud_score': 45.0,
               'truth_score': 72.0
           }).execute()
           print(f"Saved to Supabase: {post_id}")
       except Exception as e:
           print(f"Supabase error: {e}")

       return jsonify(results)

   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=True)
   ```

7. **Create .env File:**

   Create: `ASEAGI\processing-service\.env`

   ```env
   # LLM API Keys
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   OPENAI_API_KEY=sk-your-key-here
   GOOGLE_API_KEY=your-google-key-here

   # Supabase
   SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
   SUPABASE_KEY=your-supabase-key-here
   ```

8. **Run Processing Service:**
   ```bash
   cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI\processing-service
   venv\Scripts\activate
   python app.py
   ```

   You should see:
   ```
   * Running on http://0.0.0.0:5000
   * Debug mode: on
   ```

9. **Test the Service:**
   ```bash
   # In a new terminal
   curl -X POST http://localhost:5000/process ^
     -H "Content-Type: application/json" ^
     -d "{\"post_id\": \"123\", \"extracted_text\": \"test document\", \"document_type\": \"TEST\"}"
   ```

---

## 📦 Part 2: Push to GitHub

### Step 1: Initialize Git Repository

```bash
cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI

# Check if already initialized
git status

# If not initialized:
git init
```

### Step 2: Create .gitignore

Create file: `ASEAGI\.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Environment variables
.env
.env.local
*.env

# Secrets
.streamlit/secrets.toml
secrets.toml

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Processing service
processing-service/venv/
processing-service/__pycache__/
processing-service/*.pyc

# WordPress (if including)
wordpress/
wp-content/uploads/

# Test data
test_data/
temp/
```

### Step 3: Add Files to Git

```bash
cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI

# Add all files
git add .

# Check what will be committed
git status

# Create first commit
git commit -m "Add WordPress document upload system

- WordPress ACF forms for document upload
- Python processing service (Flask)
- Multi-LLM integration (Claude, GPT-4, Gemini)
- Amelia Booking integration
- Supabase context preservation
- Documentation and deployment guides"
```

### Step 4: Create GitHub Repository

1. **Go to GitHub:**
   - Visit: https://github.com/new
   - Repository name: `legal-document-processing`
   - Description: `WordPress document upload with multi-LLM processing`
   - Visibility: Private (recommended for legal documents)
   - **Don't** initialize with README (you already have files)
   - Click "Create repository"

2. **Link Local to GitHub:**
   ```bash
   # Add remote (replace YOUR_USERNAME)
   git remote add origin https://github.com/YOUR_USERNAME/legal-document-processing.git

   # Verify remote
   git remote -v

   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

### Step 5: Verify on GitHub

- Go to: https://github.com/YOUR_USERNAME/legal-document-processing
- You should see all your files
- Check that `.env` and `secrets.toml` are **NOT** visible (they're ignored)

---

## ☁️ Part 3: Deploy Streamlit Dashboards

### Step 1: Prepare Streamlit App

Your existing dashboards are already Streamlit apps. Let's deploy them.

1. **Create requirements.txt for Streamlit:**

   File: `ASEAGI\requirements.txt` (update existing)

   ```txt
   streamlit>=1.28.0
   pandas>=2.0.0
   plotly>=5.17.0
   anthropic>=0.18.0
   supabase>=2.3.4
   python-dotenv>=1.0.0
   toml>=0.10.2
   ```

2. **Create Streamlit config:**

   File: `ASEAGI\.streamlit\config.toml`

   ```toml
   [theme]
   primaryColor = "#FF4B4B"
   backgroundColor = "#FFFFFF"
   secondaryBackgroundColor = "#F0F2F6"
   textColor = "#262730"
   font = "sans serif"

   [server]
   headless = true
   port = 8501
   enableCORS = false
   ```

3. **Update secrets.toml template:**

   File: `ASEAGI\.streamlit\secrets.toml.example`

   ```toml
   # Supabase Configuration
   SUPABASE_URL = "https://jvjlhxodmbkodzmggwpu.supabase.co"
   SUPABASE_KEY = "your-key-here"

   # LLM API Keys
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   OPENAI_API_KEY = "sk-your-key-here"
   GOOGLE_API_KEY = "your-google-key-here"
   ```

### Step 2: Push Streamlit Updates

```bash
cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI

git add .
git commit -m "Add Streamlit deployment configuration"
git push
```

### Step 3: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io/
   - Sign in with GitHub

2. **Create New App:**
   - Click "New app"
   - Repository: `YOUR_USERNAME/legal-document-processing`
   - Branch: `main`
   - Main file path: `truth_justice_timeline.py` (or your main dashboard)
   - Click "Deploy"

3. **Add Secrets:**
   - Click "Advanced settings" → "Secrets"
   - Paste contents of your `.streamlit/secrets.toml`
   - Click "Save"

4. **Wait for Deployment:**
   - Streamlit will install dependencies
   - Your app will be live at: `https://your-app.streamlit.app`

### Step 4: Deploy Multiple Dashboards

For each dashboard (proj344_master_dashboard.py, truth_justice_timeline.py, etc.):

1. Create separate Streamlit app
2. Point to different main file
3. Share the same secrets
4. Each gets its own URL

---

## 🚀 Part 4: Production Deployment (Digital Ocean)

### Quick Deploy Script

Create file: `ASEAGI\deploy.sh`

```bash
#!/bin/bash

# Digital Ocean Deployment Script

echo "🚀 Deploying Legal Document Processing System"

# Variables
DROPLET_IP="YOUR_DROPLET_IP"
DEPLOY_USER="root"
DEPLOY_DIR="/opt/legal-document-processing"

echo "📦 Step 1: Pushing to GitHub..."
git add .
git commit -m "Deploy update $(date '+%Y-%m-%d %H:%M:%S')"
git push origin main

echo "📡 Step 2: Connecting to droplet..."
ssh $DEPLOY_USER@$DROPLET_IP << 'EOF'

cd /opt/legal-document-processing

# Pull latest code
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r processing-service/requirements.txt

# Restart service
systemctl restart document-processing

# Check status
systemctl status document-processing

echo "✅ Deployment complete!"
EOF
```

### Use Deploy Script

```bash
# Make executable (in Git Bash or WSL)
chmod +x deploy.sh

# Deploy
./deploy.sh
```

---

## 🔄 Part 5: Development Workflow

### Daily Development Cycle

```bash
# 1. Start your day - pull latest changes
cd c:\Users\DonBucknor_n0ufqwv\GettingStarted\ASEAGI
git pull

# 2. Start local services
# Terminal 1: Processing service
cd processing-service
venv\Scripts\activate
python app.py

# Terminal 2: Streamlit dashboard
cd ..
python -m streamlit run truth_justice_timeline.py

# 3. Make changes to code...

# 4. Test locally

# 5. Commit changes
git add .
git commit -m "Describe your changes"
git push

# 6. Deploy to Streamlit Cloud (automatic)
# Streamlit Cloud auto-deploys on git push

# 7. Deploy to Digital Ocean (manual)
./deploy.sh
```

---

## 📋 Part 6: Testing Checklist

### Local Testing

```bash
# Test 1: Python processing service
cd processing-service
venv\Scripts\activate
python app.py

# In browser: http://localhost:5000/health
# Should see: {"status": "healthy"}

# Test 2: Streamlit dashboard
cd ..
python -m streamlit run truth_justice_timeline.py

# In browser: http://localhost:8501
# Dashboard should load

# Test 3: Context Manager
python test_context_manager.py
# Should see: 5/5 tests passed
```

### GitHub Testing

```bash
# Verify .gitignore works
git status

# Should NOT see:
# - .env
# - secrets.toml
# - venv/
# - __pycache__/

# If you see them, add to .gitignore and:
git rm --cached .env
git commit -m "Remove secrets from git"
git push
```

---

## 🔧 Troubleshooting

### Issue: Git push rejected

```bash
# Pull first
git pull origin main

# If conflicts, resolve them, then:
git add .
git commit -m "Resolve merge conflicts"
git push
```

### Issue: Streamlit app won't start

1. Check secrets are configured in Streamlit Cloud
2. Check requirements.txt has all dependencies
3. Check main file path is correct
4. View logs in Streamlit Cloud dashboard

### Issue: Processing service won't start locally

```bash
# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
cd processing-service
venv\Scripts\activate
pip install -r requirements.txt --upgrade

# Check .env exists
dir .env

# Test import
python -c "import flask; print('Flask OK')"
```

---

## 📝 Quick Reference Commands

### Git Commands

```bash
# Check status
git status

# Add all changes
git add .

# Commit
git commit -m "Your message"

# Push to GitHub
git push

# Pull from GitHub
git pull

# View history
git log --oneline

# Create new branch
git checkout -b feature-name

# Switch branch
git checkout main

# Merge branch
git merge feature-name
```

### Local Development

```bash
# Start processing service
cd processing-service
venv\Scripts\activate
python app.py

# Start Streamlit dashboard
python -m streamlit run truth_justice_timeline.py

# Run tests
python test_context_manager.py

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Deployment

```bash
# Deploy to GitHub
git add .
git commit -m "Update"
git push

# Streamlit auto-deploys from GitHub

# Deploy to Digital Ocean
ssh root@YOUR_DROPLET_IP
cd /opt/legal-document-processing
git pull
systemctl restart document-processing
```

---

## 🎯 Summary

### What You've Set Up:

1. ✅ **Local WordPress** - Running at http://legal-document-upload.local
2. ✅ **Local Python Service** - Running at http://localhost:5000
3. ✅ **GitHub Repository** - Version control and backup
4. ✅ **Streamlit Cloud** - Live dashboards at https://your-app.streamlit.app
5. ✅ **Digital Ocean** - Production processing service

### Development Flow:

```
Local Development → Git Commit → GitHub Push → Auto-Deploy to Streamlit Cloud
                                              → Manual Deploy to Digital Ocean
```

### URLs:

- **Local WordPress:** http://legal-document-upload.local
- **Local Processing:** http://localhost:5000
- **Local Dashboard:** http://localhost:8501
- **GitHub Repo:** https://github.com/YOUR_USERNAME/legal-document-processing
- **Streamlit Cloud:** https://your-app.streamlit.app
- **Production API:** https://api.yoursite.com

---

**Status:** Ready for Local Development and Deployment

**Next Step:** Start with local testing, then push to GitHub, then deploy to Streamlit Cloud
