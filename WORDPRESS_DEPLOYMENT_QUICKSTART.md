# WordPress Document Upload System - Quick Start Guide

**Time to Deploy:** 2-3 hours
**Cost:** ~$90-150/month
**Difficulty:** Intermediate

---

## Overview

This system allows you to:
- Upload screenshots from your phone
- Process documents from email attachments
- Automatically analyze documents with Claude, GPT-4, and Gemini
- Store results in Supabase with context preservation
- Schedule document review appointments with Amelia

---

## Architecture

```
Phone/Email → WordPress (SiteGround) → Python Service (Digital Ocean) → Multi-LLM Processing → Supabase
```

---

## Quick Start: 3-Step Deployment

### Step 1: WordPress Setup (30 minutes)

1. **Install Required Plugins:**
   - Go to WordPress Admin → Plugins → Add New
   - Install:
     - Advanced Custom Fields Pro (ACF Pro)
     - Amelia Booking
     - WP Mail SMTP (optional, for email integration)

2. **Create Custom Post Type:**
   - Add to `functions.php`:
   ```php
   function create_legal_document_post_type() {
       register_post_type('legal_document', array(
           'labels' => array(
               'name' => 'Legal Documents',
               'singular_name' => 'Legal Document'
           ),
           'public' => true,
           'has_archive' => true,
           'supports' => array('title', 'editor', 'custom-fields')
       ));
   }
   add_action('init', 'create_legal_document_post_type');
   ```

3. **Import ACF Configuration:**
   - Copy the ACF field group code from `DOCUMENT_UPLOAD_SYSTEM.md` (lines 71-190)
   - Paste into `functions.php`
   - Or import via ACF → Tools → Import

4. **Create Upload Form Page:**
   - Create new page: "Upload Document"
   - Add shortcode: `[acf_form id="legal-document-upload"]`
   - Save and publish

---

### Step 2: Digital Ocean Droplet (45 minutes)

1. **Create Droplet:**
   - Log into Digital Ocean
   - Create Droplet
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** Basic - $24/month (4GB RAM, 2 vCPUs)
   - **Datacenter:** Choose closest to you
   - Add SSH key

2. **SSH into Droplet:**
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

3. **Install Python Environment:**
   ```bash
   # Update system
   apt update && apt upgrade -y

   # Install Python and dependencies
   apt install -y python3-pip python3-venv tesseract-ocr git nginx certbot python3-certbot-nginx

   # Create project directory
   mkdir -p /opt/document-processing
   cd /opt/document-processing

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Python Packages:**
   ```bash
   # Create requirements.txt
   cat > requirements.txt << EOF
   flask==3.0.0
   gunicorn==21.2.0
   anthropic==0.18.0
   openai==1.12.0
   google-generativeai==0.4.0
   supabase==2.3.4
   pytesseract==0.3.10
   Pillow==10.2.0
   requests==2.31.0
   python-dotenv==1.0.1
   EOF

   pip install -r requirements.txt
   ```

5. **Create Processing Service:**
   ```bash
   # Copy the document_processor.py code from DOCUMENT_UPLOAD_SYSTEM.md (lines 432-676)
   nano app.py
   # Paste the Python processing service code
   ```

6. **Configure Environment:**
   ```bash
   nano .env
   ```

   Add:
   ```
   ANTHROPIC_API_KEY=sk-ant-YOUR_KEY_HERE
   OPENAI_API_KEY=sk-YOUR_KEY_HERE
   GOOGLE_API_KEY=YOUR_GOOGLE_KEY_HERE
   SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
   SUPABASE_KEY=YOUR_SUPABASE_KEY_HERE
   ```

7. **Create Systemd Service:**
   ```bash
   nano /etc/systemd/system/document-processing.service
   ```

   Add:
   ```ini
   [Unit]
   Description=Legal Document Processing Service
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/document-processing
   Environment="PATH=/opt/document-processing/venv/bin"
   ExecStart=/opt/document-processing/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 300 app:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   systemctl enable document-processing
   systemctl start document-processing
   systemctl status document-processing
   ```

8. **Configure Nginx Reverse Proxy:**
   ```bash
   nano /etc/nginx/sites-available/document-processing
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name api.yoursite.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_read_timeout 300s;
       }
   }
   ```

   Enable:
   ```bash
   ln -s /etc/nginx/sites-available/document-processing /etc/nginx/sites-enabled/
   nginx -t
   systemctl restart nginx
   ```

9. **Add SSL Certificate:**
   ```bash
   certbot --nginx -d api.yoursite.com
   ```

10. **Configure Firewall:**
    ```bash
    ufw allow 'Nginx Full'
    ufw allow OpenSSH
    ufw enable
    ```

---

### Step 3: Connect WordPress to Processing Service (15 minutes)

1. **Add to WordPress `wp-config.php`:**
   ```php
   // Legal Document Processing
   define('PROCESSING_SERVICE_URL', 'https://api.yoursite.com');
   define('PROCESSING_SERVICE_KEY', 'your-secure-random-key');
   ```

2. **Add Processing Hook to `functions.php`:**
   ```php
   add_action('acf/save_post', 'process_uploaded_document', 20);

   function process_uploaded_document($post_id) {
       if (get_post_type($post_id) !== 'legal_document') {
           return;
       }

       $file = get_field('document_file', $post_id);
       if (!$file) return;

       // Get extracted text (add OCR/PDF extraction here)
       $extracted_text = file_get_contents(get_attached_file($file['ID']));

       // Call processing service
       $response = wp_remote_post(PROCESSING_SERVICE_URL . '/process', array(
           'headers' => array(
               'X-API-Key' => PROCESSING_SERVICE_KEY,
               'Content-Type' => 'application/json'
           ),
           'body' => json_encode(array(
               'post_id' => $post_id,
               'extracted_text' => $extracted_text,
               'document_type' => get_field('document_type', $post_id)
           )),
           'timeout' => 300
       ));

       if (!is_wp_error($response)) {
           $result = json_decode(wp_remote_retrieve_body($response), true);
           update_post_meta($post_id, 'tier2_results', $result);
       }
   }
   ```

---

## Step 4: Configure Amelia Booking (15 minutes)

1. **Create Service:**
   - Go to Amelia → Services → Add New
   - **Name:** Document Review Consultation
   - **Duration:** 60 minutes
   - **Price:** $0 (or your rate)
   - **Capacity:** 1 person

2. **Add Custom Fields:**
   - Go to Amelia → Customize → Custom Fields
   - Add field:
     - **Label:** Document IDs
     - **Type:** Text Field
     - **Required:** No

3. **Configure Notifications:**
   - Customer email: "Your document review is scheduled. Please upload documents before appointment."
   - Employee email: "Process documents before appointment."

---

## Step 5: Mobile Upload Page (10 minutes)

1. **Create Page Template:**
   - Create file: `wp-content/themes/your-theme/page-mobile-upload.php`
   - Copy mobile upload code from `DOCUMENT_UPLOAD_SYSTEM.md` (lines 855-998)

2. **Create Page:**
   - WordPress Admin → Pages → Add New
   - **Title:** "Mobile Upload"
   - **Template:** Mobile Upload
   - Save and publish

3. **Test:**
   - Visit page on your phone
   - Try uploading a photo
   - Verify processing starts

---

## Step 6: Email Integration (Optional - 30 minutes)

1. **Create Email Processor:**
   ```bash
   # On Digital Ocean droplet
   cd /opt/document-processing
   nano email_processor.py
   ```

   Copy email integration code from `DOCUMENT_UPLOAD_SYSTEM.md` (lines 684-767)

2. **Configure Environment:**
   ```bash
   nano .env
   ```

   Add:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   WORDPRESS_URL=https://yoursite.com
   WORDPRESS_USER=admin
   WORDPRESS_PASSWORD=your-app-password
   ```

3. **Add Cron Job:**
   ```bash
   crontab -e
   ```

   Add:
   ```
   */5 * * * * /opt/document-processing/venv/bin/python /opt/document-processing/email_processor.py >> /var/log/email-processing.log 2>&1
   ```

---

## Testing Checklist

### Basic Upload Test
- [ ] Upload PDF from WordPress admin
- [ ] Upload image from mobile page
- [ ] Verify file appears in Media Library
- [ ] Check ACF fields saved correctly

### Processing Test
- [ ] Check Digital Ocean service is running: `systemctl status document-processing`
- [ ] Upload test document
- [ ] Check processing service logs: `tail -f /var/log/syslog | grep gunicorn`
- [ ] Verify results saved to WordPress post meta
- [ ] Check Supabase for saved data

### Amelia Test
- [ ] Book a test appointment
- [ ] Add document ID to custom field
- [ ] Verify email notifications sent

### Mobile Test
- [ ] Open mobile upload page on phone
- [ ] Take photo and upload
- [ ] Verify upload succeeds
- [ ] Check document appears in admin

---

## Troubleshooting

### Issue: Processing service not starting
```bash
# Check logs
journalctl -u document-processing -n 50

# Check if port is in use
netstat -tulpn | grep 5000

# Restart service
systemctl restart document-processing
```

### Issue: WordPress can't reach processing service
```bash
# Test from command line
curl -X POST https://api.yoursite.com/process \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"post_id": "123", "extracted_text": "test", "document_type": "TEST"}'
```

### Issue: Uploads failing
- Check file size limits in `php.ini`
- Verify WordPress upload directory is writable
- Check nginx client_max_body_size

### Issue: OCR not working
```bash
# Install Tesseract
apt install tesseract-ocr tesseract-ocr-eng

# Test
tesseract test.jpg output
```

---

## Monitoring

### Check Processing Service Status
```bash
systemctl status document-processing
```

### View Logs
```bash
# Service logs
journalctl -u document-processing -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Check Database Stats
```sql
-- In Supabase SQL editor
SELECT COUNT(*) FROM legal_documents WHERE created_at > NOW() - INTERVAL '24 hours';
SELECT SUM(api_cost_usd) FROM ai_analysis_results WHERE created_at > NOW() - INTERVAL '24 hours';
```

---

## Cost Breakdown

### Monthly Costs
- **SiteGround Hosting:** $15-30/month (current)
- **Digital Ocean Droplet:** $24/month
- **LLM API Costs:**
  - Claude: ~$3 per 1M tokens
  - GPT-4: ~$30 per 1M tokens
  - Gemini: ~$1.50 per 1M tokens
  - Estimated: $50-200/month depending on volume
- **Domain/SSL:** $0 (Let's Encrypt free)
- **Total:** $90-250/month

### Per-Document Cost
- Tier 1 Processing: $0 (local)
- Tier 2 Multi-LLM: ~$0.10-0.30 per document
- Storage (Supabase): $0 (free tier)

---

## Security Checklist

- [ ] Change default WordPress admin password
- [ ] Install WordPress security plugin (Wordfence)
- [ ] Enable 2FA on WordPress
- [ ] Set strong API key in wp-config.php
- [ ] Configure firewall on Digital Ocean
- [ ] Enable SSL on both WordPress and API
- [ ] Set up regular backups
- [ ] Restrict file upload types in ACF

---

## Next Steps

1. **Week 1:**
   - Deploy basic system
   - Test with 10-20 documents
   - Monitor costs and performance

2. **Week 2:**
   - Configure Amelia booking
   - Set up email integration
   - Train users on mobile upload

3. **Month 1:**
   - Optimize LLM prompts
   - Add custom analysis rules
   - Integrate with Streamlit dashboards

4. **Ongoing:**
   - Monitor AI costs
   - Review processed documents
   - Refine truth scoring algorithms
   - Expand to additional document types

---

## Support Resources

- **Full Documentation:** [DOCUMENT_UPLOAD_SYSTEM.md](DOCUMENT_UPLOAD_SYSTEM.md)
- **Context Preservation Guide:** [README_DEPLOYMENT.md](README_DEPLOYMENT.md)
- **WordPress Codex:** https://codex.wordpress.org/
- **ACF Documentation:** https://www.advancedcustomfields.com/resources/
- **Digital Ocean Guides:** https://www.digitalocean.com/community/tutorials

---

**Status:** Ready to Deploy

**Estimated Setup Time:** 2-3 hours

**Difficulty:** Intermediate (requires basic server admin knowledge)

**Support:** Review full documentation in DOCUMENT_UPLOAD_SYSTEM.md for detailed code and examples
