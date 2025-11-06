# Legal Document Upload & Processing System

**Purpose:** WordPress-based document intake system with multi-tier AI processing
**Use Case:** Upload screenshots/documents from phone/email for legal processing
**Tech Stack:** WordPress + ACF Forms + Amelia Booking + AstroPro + Multi-LLM API

---

## 🎯 System Overview

### **Workflow:**
```
User (Phone/Email)
    ↓
WordPress Upload Form (ACF)
    ↓
Tier 1: Pre-Processing (Document Classification)
    ↓
Tier 2: Multi-LLM Processing (Fraud Detection, Truth Scoring, etc.)
    ↓
Supabase Storage (Context Preservation)
    ↓
Dashboard Visualization (Streamlit)
```

---

## 📱 **Part 1: WordPress Upload Form (ACF + Amelia)**

### **ACF Form Configuration**

Create a custom ACF form for document upload:

**Form Fields:**
```php
// File: wp-content/themes/your-theme/acf-document-upload.php

<?php
// ACF Form Configuration
acf_form(array(
    'id' => 'legal-document-upload',
    'post_id' => 'new_post',
    'post_title' => true,
    'post_content' => false,
    'new_post' => array(
        'post_type' => 'legal_document',
        'post_status' => 'pending'
    ),
    'submit_value' => 'Upload & Process Document',
    'updated_message' => 'Document uploaded successfully! Processing...',
    'fields' => array(
        'field_document_file',        // File upload
        'field_document_type',         // Document type (dropdown)
        'field_document_date',         // Date of document
        'field_document_source',       // Source (email/phone/scan)
        'field_document_description',  // Brief description
        'field_case_reference',        // Case reference number
        'field_urgency_level',         // Urgency (low/medium/high/critical)
        'field_phone_email'            // Contact info
    )
));
?>
```

### **ACF Field Groups Setup**

```php
// Register ACF Field Group
if( function_exists('acf_add_local_field_group') ):

acf_add_local_field_group(array(
    'key' => 'group_legal_document_upload',
    'title' => 'Legal Document Upload',
    'fields' => array(

        // FILE UPLOAD
        array(
            'key' => 'field_document_file',
            'label' => 'Upload Document',
            'name' => 'document_file',
            'type' => 'file',
            'required' => 1,
            'return_format' => 'array',
            'library' => 'all',
            'mime_types' => 'pdf,jpg,jpeg,png,doc,docx,txt',
            'instructions' => 'Upload your document (PDF, image, or Word document)'
        ),

        // DOCUMENT TYPE
        array(
            'key' => 'field_document_type',
            'label' => 'Document Type',
            'name' => 'document_type',
            'type' => 'select',
            'required' => 1,
            'choices' => array(
                'DECL' => 'Declaration',
                'MOTN' => 'Motion',
                'ORDR' => 'Court Order',
                'CORR' => 'Correspondence',
                'EVID' => 'Evidence',
                'POLR' => 'Police Report',
                'PHOT' => 'Photo/Screenshot',
                'EMAI' => 'Email',
                'TEXT' => 'Text Message',
                'OTHR' => 'Other'
            )
        ),

        // DOCUMENT DATE
        array(
            'key' => 'field_document_date',
            'label' => 'Document Date',
            'name' => 'document_date',
            'type' => 'date_picker',
            'required' => 1,
            'display_format' => 'm/d/Y',
            'return_format' => 'Y-m-d'
        ),

        // SOURCE
        array(
            'key' => 'field_document_source',
            'label' => 'Source',
            'name' => 'document_source',
            'type' => 'radio',
            'choices' => array(
                'phone' => 'Phone Screenshot',
                'email' => 'Email Attachment',
                'scan' => 'Scanned Document',
                'digital' => 'Digital File'
            ),
            'default_value' => 'phone'
        ),

        // DESCRIPTION
        array(
            'key' => 'field_document_description',
            'label' => 'Brief Description',
            'name' => 'document_description',
            'type' => 'textarea',
            'rows' => 3,
            'instructions' => 'What is this document about?'
        ),

        // CASE REFERENCE
        array(
            'key' => 'field_case_reference',
            'label' => 'Case Reference',
            'name' => 'case_reference',
            'type' => 'text',
            'default_value' => 'PROJ344',
            'instructions' => 'Your case reference number'
        ),

        // URGENCY
        array(
            'key' => 'field_urgency_level',
            'label' => 'Urgency Level',
            'name' => 'urgency_level',
            'type' => 'select',
            'choices' => array(
                'LOW' => 'Low - Informational',
                'MEDIUM' => 'Medium - Standard Processing',
                'HIGH' => 'High - Priority Review',
                'CRITICAL' => 'Critical - Immediate Attention'
            ),
            'default_value' => 'MEDIUM'
        ),

        // CONTACT
        array(
            'key' => 'field_phone_email',
            'label' => 'Your Email/Phone',
            'name' => 'contact_info',
            'type' => 'text',
            'instructions' => 'For processing updates'
        )
    ),
    'location' => array(
        array(
            array(
                'param' => 'post_type',
                'operator' => '==',
                'value' => 'legal_document',
            ),
        ),
    ),
));

endif;
```

---

## 🔄 **Part 2: Tier 1 Pre-Processing (WordPress Backend)**

### **Process Document on Upload**

```php
// File: wp-content/themes/your-theme/functions.php

// Hook into ACF form submission
add_action('acf/save_post', 'process_uploaded_document', 20);

function process_uploaded_document($post_id) {

    // Only process legal_document post type
    if (get_post_type($post_id) !== 'legal_document') {
        return;
    }

    // Get uploaded file
    $file = get_field('document_file', $post_id);
    $document_type = get_field('document_type', $post_id);
    $urgency = get_field('urgency_level', $post_id);

    if (!$file) {
        return;
    }

    // TIER 1: PRE-PROCESSING
    $tier1_result = tier1_preprocessing($file, $document_type, $post_id);

    // Update post meta with Tier 1 results
    update_post_meta($post_id, 'tier1_status', $tier1_result['status']);
    update_post_meta($post_id, 'tier1_classification', $tier1_result['classification']);
    update_post_meta($post_id, 'file_hash', $tier1_result['file_hash']);

    // TIER 2: Queue for Multi-LLM Processing
    if ($tier1_result['status'] === 'ready') {
        queue_tier2_processing($post_id, $tier1_result, $urgency);
    }

    // Send to Supabase
    send_to_supabase($post_id, $tier1_result);
}

function tier1_preprocessing($file, $document_type, $post_id) {

    $file_path = get_attached_file($file['ID']);
    $file_extension = pathinfo($file_path, PATHINFO_EXTENSION);

    // Calculate file hash (prevent duplicates)
    $file_hash = md5_file($file_path);

    // Check for duplicate
    $existing = get_posts(array(
        'post_type' => 'legal_document',
        'meta_key' => 'file_hash',
        'meta_value' => $file_hash,
        'post__not_in' => array($post_id)
    ));

    if (!empty($existing)) {
        return array(
            'status' => 'duplicate',
            'file_hash' => $file_hash,
            'duplicate_of' => $existing[0]->ID
        );
    }

    // Extract text based on file type
    $extracted_text = '';

    if (in_array($file_extension, ['jpg', 'jpeg', 'png'])) {
        // OCR for images (requires Tesseract or cloud OCR)
        $extracted_text = perform_ocr($file_path);
    } elseif ($file_extension === 'pdf') {
        // Extract PDF text
        $extracted_text = extract_pdf_text($file_path);
    } elseif (in_array($file_extension, ['doc', 'docx'])) {
        // Extract Word text
        $extracted_text = extract_word_text($file_path);
    }

    // Basic classification
    $classification = array(
        'document_type' => $document_type,
        'file_type' => $file_extension,
        'file_size' => filesize($file_path),
        'text_length' => strlen($extracted_text),
        'has_text' => !empty($extracted_text),
        'word_count' => str_word_count($extracted_text)
    );

    // Store extracted text
    update_post_meta($post_id, 'extracted_text', $extracted_text);

    return array(
        'status' => 'ready',
        'file_hash' => $file_hash,
        'classification' => $classification,
        'extracted_text' => $extracted_text
    );
}

function perform_ocr($file_path) {
    // Option 1: Google Cloud Vision API
    // Option 2: AWS Textract
    // Option 3: Azure Computer Vision
    // Option 4: Local Tesseract

    // Example using Google Cloud Vision
    // (requires google/cloud-vision package)
    /*
    $vision = new VisionClient([
        'keyFilePath' => '/path/to/service-account.json'
    ]);

    $image = $vision->image(file_get_contents($file_path), [
        'TEXT_DETECTION'
    ]);

    $annotation = $vision->annotate($image);
    $text = $annotation->text();

    return $text ? $text->description() : '';
    */

    // Placeholder - implement based on your OCR choice
    return '';
}

function extract_pdf_text($file_path) {
    // Using Smalot PDF Parser
    // composer require smalot/pdfparser

    require_once get_template_directory() . '/vendor/autoload.php';

    $parser = new \Smalot\PdfParser\Parser();
    $pdf = $parser->parseFile($file_path);
    $text = $pdf->getText();

    return $text;
}

function extract_word_text($file_path) {
    // Using PHPWord
    // composer require phpoffice/phpword

    $phpWord = \PhpOffice\PhpWord\IOFactory::load($file_path);
    $text = '';

    foreach ($phpWord->getSections() as $section) {
        $elements = $section->getElements();
        foreach ($elements as $element) {
            if (method_exists($element, 'getText')) {
                $text .= $element->getText() . "\n";
            }
        }
    }

    return $text;
}
```

---

## 🤖 **Part 3: Tier 2 Multi-LLM Processing**

### **Queue System for Tier 2**

```php
// Queue Tier 2 processing
function queue_tier2_processing($post_id, $tier1_result, $urgency) {

    // Create processing job
    $job_data = array(
        'post_id' => $post_id,
        'tier1_result' => $tier1_result,
        'urgency' => $urgency,
        'status' => 'queued',
        'created_at' => current_time('mysql')
    );

    // Option 1: Store in WordPress options (simple)
    $queue = get_option('tier2_processing_queue', array());
    $queue[] = $job_data;
    update_option('tier2_processing_queue', $queue);

    // Option 2: Use WP-Cron for background processing
    wp_schedule_single_event(time() + 10, 'process_tier2_job', array($post_id));

    // Send notification
    send_processing_notification($post_id, 'queued');
}

// Process Tier 2 job
add_action('process_tier2_job', 'execute_tier2_processing');

function execute_tier2_processing($post_id) {

    $extracted_text = get_post_meta($post_id, 'extracted_text', true);
    $document_type = get_field('document_type', $post_id);
    $case_reference = get_field('case_reference', $post_id);

    // MULTI-LLM PROCESSING
    $llm_results = array();

    // LLM 1: Claude (Fraud Detection)
    $llm_results['claude'] = process_with_claude($extracted_text, $document_type);

    // LLM 2: GPT-4 (Truth Scoring)
    $llm_results['gpt4'] = process_with_gpt4($extracted_text, $document_type);

    // LLM 3: Gemini (Legal Analysis)
    $llm_results['gemini'] = process_with_gemini($extracted_text, $document_type);

    // Aggregate results
    $final_result = aggregate_llm_results($llm_results);

    // Update post with results
    update_post_meta($post_id, 'tier2_results', $final_result);
    update_post_meta($post_id, 'processing_status', 'completed');
    update_post_meta($post_id, 'processed_at', current_time('mysql'));

    // Send to Supabase
    update_supabase_with_tier2_results($post_id, $final_result);

    // Notify user
    send_processing_notification($post_id, 'completed');
}
```

---

## 🔌 **Part 4: API Integration - Python Processing Service**

Create a Python service to handle the heavy LLM processing:

```python
# File: wp-content/processing-service/document_processor.py

from flask import Flask, request, jsonify
import anthropic
import openai
import google.generativeai as genai
from supabase import create_client
import os

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

@app.route('/process', methods=['POST'])
def process_document():
    """
    Process document through multiple LLMs
    """
    data = request.json

    post_id = data['post_id']
    extracted_text = data['extracted_text']
    document_type = data['document_type']

    results = {
        'post_id': post_id,
        'llm_results': {}
    }

    # TIER 2: Multi-LLM Processing

    # 1. Claude - Fraud Detection
    results['llm_results']['claude'] = process_with_claude(
        extracted_text,
        document_type
    )

    # 2. GPT-4 - Truth Scoring
    results['llm_results']['gpt4'] = process_with_gpt4(
        extracted_text,
        document_type
    )

    # 3. Gemini - Legal Analysis
    results['llm_results']['gemini'] = process_with_gemini(
        extracted_text,
        document_type
    )

    # Aggregate results
    final_analysis = aggregate_results(results['llm_results'])

    # Save to Supabase
    save_to_supabase(post_id, final_analysis)

    return jsonify({
        'status': 'success',
        'results': final_analysis
    })

def process_with_claude(text, doc_type):
    """Claude: Fraud detection and pattern analysis"""

    prompt = f"""Analyze this legal document for fraud indicators:

Document Type: {doc_type}
Document Text:
{text}

Provide analysis in JSON format:
{{
    "fraud_score": 0-100,
    "fraud_indicators": ["list", "of", "red", "flags"],
    "confidence": 0-100,
    "summary": "brief summary",
    "key_findings": ["finding1", "finding2"]
}}
"""

    response = claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return parse_claude_response(response.content[0].text)

def process_with_gpt4(text, doc_type):
    """GPT-4: Truth scoring and fact verification"""

    prompt = f"""Score this legal document for truthfulness using 5W+H framework:

Document Type: {doc_type}
Document Text:
{text}

Provide analysis in JSON format:
{{
    "truth_score": 0-100,
    "when": "when did this happen",
    "where": "where did this happen",
    "who": ["list", "of", "people"],
    "what": "what occurred",
    "why": "why it occurred",
    "how": "how it occurred",
    "verifiable_facts": ["fact1", "fact2"],
    "unverifiable_claims": ["claim1", "claim2"]
}}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

def process_with_gemini(text, doc_type):
    """Gemini: Legal analysis and categorization"""

    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f"""Perform legal analysis on this document:

Document Type: {doc_type}
Document Text:
{text}

Provide analysis in JSON format:
{{
    "legal_issues": ["issue1", "issue2"],
    "relevant_laws": ["law1", "law2"],
    "importance_level": "CRITICAL/HIGH/MEDIUM/LOW",
    "category": "MOTION/FILING/EVIDENCE/etc",
    "actionable_items": ["action1", "action2"],
    "timeline_relevance": "description"
}}
"""

    response = model.generate_content(prompt)
    return parse_gemini_response(response.text)

def aggregate_results(llm_results):
    """Aggregate results from multiple LLMs"""

    aggregated = {
        'fraud_score': llm_results['claude']['fraud_score'],
        'truth_score': llm_results['gpt4']['truth_score'],
        'importance_level': llm_results['gemini']['importance_level'],
        'category': llm_results['gemini']['category'],

        # Combined analysis
        'combined_score': (
            llm_results['claude']['fraud_score'] * 0.3 +
            llm_results['gpt4']['truth_score'] * 0.4 +
            (100 if llm_results['gemini']['importance_level'] == 'CRITICAL' else 75) * 0.3
        ),

        # All findings
        'key_findings': (
            llm_results['claude']['key_findings'] +
            llm_results['gpt4']['verifiable_facts'] +
            llm_results['gemini']['legal_issues']
        ),

        # 5W+H
        'when_happened': llm_results['gpt4']['when'],
        'where_happened': llm_results['gpt4']['where'],
        'who_involved': llm_results['gpt4']['who'],
        'what_occurred': llm_results['gpt4']['what'],
        'why_occurred': llm_results['gpt4']['why'],
        'how_occurred': llm_results['gpt4']['how'],

        # Metadata
        'processed_at': datetime.now().isoformat(),
        'llm_versions': {
            'claude': 'sonnet-4',
            'gpt4': 'gpt-4-turbo',
            'gemini': 'gemini-1.5-pro'
        }
    }

    return aggregated

def save_to_supabase(post_id, analysis):
    """Save analysis to Supabase"""

    # Save to legal_documents table
    supabase.table('legal_documents').upsert({
        'wordpress_post_id': post_id,
        'document_type': analysis['category'],
        'fraud_score': analysis['fraud_score'],
        'truth_score': analysis['truth_score'],
        'importance_level': analysis['importance_level'],
        'processed_at': analysis['processed_at']
    }).execute()

    # Save to truth_score_history
    supabase.table('truth_score_history').insert({
        'item_id': str(post_id),
        'item_type': analysis['category'],
        'truth_score': analysis['truth_score'],
        'when_happened': analysis['when_happened'],
        'where_happened': analysis['where_happened'],
        'who_involved': analysis['who_involved'],
        'what_occurred': analysis['what_occurred'],
        'why_occurred': analysis['why_occurred'],
        'how_occurred': analysis['how_occurred'],
        'importance_level': analysis['importance_level']
    }).execute()

    # Log AI analysis
    from utilities.context_manager import ContextManager
    cm = ContextManager()

    cm.log_ai_analysis(
        analysis_type='document_processing',
        model_name='multi-llm',
        source_id=str(post_id),
        source_table='wordpress_uploads',
        structured_output=analysis,
        tokens_used=5000,  # Estimate
        api_cost_usd=0.15  # Estimate
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 📧 **Part 5: Email Integration**

### **Process Documents from Email**

```python
# File: email_to_wordpress.py

import imaplib
import email
from email.header import decode_header
import requests
import os

def process_email_attachments():
    """
    Check email for new attachments and upload to WordPress
    """

    # Connect to email
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login('your-email@gmail.com', os.environ['EMAIL_PASSWORD'])
    mail.select('INBOX')

    # Search for unread emails with attachments
    status, messages = mail.search(None, '(UNSEEN)')

    for msg_num in messages[0].split():
        status, msg_data = mail.fetch(msg_num, '(RFC822)')

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                # Process attachments
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    if filename:
                        # Upload to WordPress
                        upload_to_wordpress(
                            filename=filename,
                            file_data=part.get_payload(decode=True),
                            email_subject=msg['subject'],
                            email_from=msg['from'],
                            email_date=msg['date']
                        )

    mail.close()
    mail.logout()

def upload_to_wordpress(filename, file_data, email_subject, email_from, email_date):
    """
    Upload file to WordPress via REST API
    """

    wp_url = 'https://your-site.com/wp-json/wp/v2/media'
    wp_user = 'your-username'
    wp_password = 'your-app-password'

    headers = {
        'Content-Disposition': f'attachment; filename={filename}'
    }

    response = requests.post(
        wp_url,
        auth=(wp_user, wp_password),
        headers=headers,
        data=file_data
    )

    if response.status_code == 201:
        media_id = response.json()['id']

        # Create legal_document post
        create_document_post(
            media_id=media_id,
            title=email_subject,
            source='email',
            metadata={
                'email_from': email_from,
                'email_date': email_date
            }
        )
```

---

## 🔗 **Part 6: WordPress REST API Webhook**

```php
// Register REST route for processing status
add_action('rest_api_init', function () {
    register_rest_route('legal/v1', '/process-status/(?P<id>\d+)', array(
        'methods' => 'GET',
        'callback' => 'get_processing_status',
    ));

    register_rest_route('legal/v1', '/upload', array(
        'methods' => 'POST',
        'callback' => 'handle_api_upload',
    ));
});

function get_processing_status($request) {
    $post_id = $request['id'];

    $status = get_post_meta($post_id, 'processing_status', true);
    $tier1 = get_post_meta($post_id, 'tier1_status', true);
    $tier2 = get_post_meta($post_id, 'tier2_results', true);

    return new WP_REST_Response(array(
        'post_id' => $post_id,
        'status' => $status,
        'tier1_status' => $tier1,
        'tier2_results' => $tier2
    ), 200);
}

function handle_api_upload($request) {
    // Handle uploads from external sources (email, mobile app, etc.)

    $files = $request->get_file_params();
    $params = $request->get_params();

    // Process upload
    $upload = wp_handle_upload($files['file'], array('test_form' => false));

    if (!isset($upload['error'])) {
        // Create attachment
        $attachment_id = wp_insert_attachment(array(
            'post_mime_type' => $upload['type'],
            'post_title' => sanitize_file_name($upload['file']),
            'post_content' => '',
            'post_status' => 'inherit'
        ), $upload['file']);

        // Create legal_document post
        $post_id = wp_insert_post(array(
            'post_type' => 'legal_document',
            'post_title' => $params['title'] ?? 'Uploaded Document',
            'post_status' => 'pending'
        ));

        // Link attachment
        update_field('document_file', $attachment_id, $post_id);
        update_field('document_type', $params['document_type'] ?? 'OTHR', $post_id);
        update_field('document_source', $params['source'] ?? 'api', $post_id);

        // Trigger processing
        do_action('acf/save_post', $post_id);

        return new WP_REST_Response(array(
            'success' => true,
            'post_id' => $post_id,
            'message' => 'Document uploaded and queued for processing'
        ), 201);
    }

    return new WP_REST_Response(array(
        'success' => false,
        'error' => $upload['error']
    ), 400);
}
```

---

## 📱 **Part 7: Mobile Upload (Bonus)**

Create a simple mobile-friendly upload page:

```html
<!-- File: wp-content/themes/your-theme/page-mobile-upload.php -->

<?php
/* Template Name: Mobile Upload */
get_header();
?>

<div class="mobile-upload-container">
    <h1>Quick Document Upload</h1>

    <form id="mobile-upload-form" enctype="multipart/form-data">

        <div class="form-group">
            <label>Take Photo or Choose File</label>
            <input type="file"
                   name="document"
                   accept="image/*,application/pdf"
                   capture="environment"
                   required>
        </div>

        <div class="form-group">
            <label>Document Type</label>
            <select name="document_type" required>
                <option value="PHOT">Photo/Screenshot</option>
                <option value="EMAI">Email</option>
                <option value="TEXT">Text Message</option>
                <option value="EVID">Evidence</option>
                <option value="OTHR">Other</option>
            </select>
        </div>

        <div class="form-group">
            <label>Quick Description</label>
            <textarea name="description" rows="3"></textarea>
        </div>

        <div class="form-group">
            <label>Urgency</label>
            <select name="urgency">
                <option value="MEDIUM">Normal</option>
                <option value="HIGH">High Priority</option>
                <option value="CRITICAL">Urgent</option>
            </select>
        </div>

        <button type="submit" class="btn-upload">
            Upload & Process
        </button>

        <div id="upload-status"></div>
    </form>
</div>

<script>
document.getElementById('mobile-upload-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const statusDiv = document.getElementById('upload-status');

    statusDiv.innerHTML = '<p>Uploading...</p>';

    try {
        const response = await fetch('/wp-json/legal/v1/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            statusDiv.innerHTML = `
                <div class="success">
                    <h3>✅ Upload Successful!</h3>
                    <p>Your document is being processed.</p>
                    <p>Reference: #${result.post_id}</p>
                </div>
            `;
            this.reset();
        } else {
            statusDiv.innerHTML = `<p class="error">Error: ${result.error}</p>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<p class="error">Upload failed: ${error.message}</p>`;
    }
});
</script>

<style>
.mobile-upload-container {
    max-width: 500px;
    margin: 20px auto;
    padding: 20px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px;
    font-size: 16px;
}

.btn-upload {
    width: 100%;
    padding: 15px;
    background: #0073aa;
    color: white;
    border: none;
    font-size: 18px;
    cursor: pointer;
}

.success {
    padding: 20px;
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    margin-top: 20px;
}

.error {
    padding: 20px;
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 5px;
    margin-top: 20px;
}
</style>

<?php get_footer(); ?>
```

---

## 📊 **Part 8: Integration with Existing Dashboards**

Connect processed documents to your Streamlit dashboards:

```python
# File: ASEAGI/wordpress_integration.py

from supabase import create_client
import requests

class WordPressIntegration:

    def __init__(self):
        self.wp_url = "https://your-site.com"
        self.wp_user = "your-username"
        self.wp_password = "your-app-password"

        self.supabase = create_client(
            os.environ['SUPABASE_URL'],
            os.environ['SUPABASE_KEY']
        )

    def fetch_recent_uploads(self, days=7):
        """Fetch recent document uploads from WordPress"""

        url = f"{self.wp_url}/wp-json/wp/v2/legal_document"
        params = {
            'per_page': 100,
            'after': (datetime.now() - timedelta(days=days)).isoformat()
        }

        response = requests.get(
            url,
            auth=(self.wp_user, self.wp_password),
            params=params
        )

        return response.json()

    def sync_to_supabase(self):
        """Sync WordPress uploads to Supabase"""

        documents = self.fetch_recent_uploads()

        for doc in documents:
            # Check if already in Supabase
            existing = self.supabase.table('legal_documents')\
                .select('*')\
                .eq('wordpress_post_id', doc['id'])\
                .execute()

            if not existing.data:
                # Insert into Supabase
                self.supabase.table('legal_documents').insert({
                    'wordpress_post_id': doc['id'],
                    'original_filename': doc['title']['rendered'],
                    # ... other fields
                }).execute()
```

---

## 📅 **Part 9: Amelia Booking Integration**

### **Schedule Document Review Appointments**

Integrate Amelia to schedule appointments for document review meetings:

```php
// File: wp-content/themes/your-theme/amelia-integration.php

// Hook into Amelia appointment booking
add_action('AmeliaBookingAdded', 'handle_document_review_booking', 10, 3);

function handle_document_review_booking($appointment, $booking, $recurring) {

    // Check if this is a document review appointment
    $service_id = $appointment['serviceId'];
    $document_review_service_id = 1; // Your document review service ID

    if ($service_id != $document_review_service_id) {
        return;
    }

    // Get custom fields from booking
    $custom_fields = $booking['customFields'];
    $document_ids = array();

    foreach ($custom_fields as $field) {
        if ($field['label'] === 'Document IDs') {
            $document_ids = explode(',', $field['value']);
        }
    }

    // Create processing job for these documents
    if (!empty($document_ids)) {
        schedule_document_review_preparation(
            $appointment['id'],
            $document_ids,
            $appointment['bookingStart']
        );
    }
}

function schedule_document_review_preparation($appointment_id, $document_ids, $review_date) {

    // Queue all documents for priority processing
    foreach ($document_ids as $doc_id) {
        $doc_id = trim($doc_id);

        // Set priority processing
        update_post_meta($doc_id, 'scheduled_review_date', $review_date);
        update_post_meta($doc_id, 'amelia_appointment_id', $appointment_id);
        update_field('urgency_level', 'HIGH', $doc_id);

        // Trigger immediate Tier 2 processing
        do_action('process_tier2_job', $doc_id);
    }

    // Send preparation email
    send_review_preparation_email($appointment_id, $document_ids);
}

// Add custom field to Amelia service for document selection
add_filter('ameliaBookingAddCustomFields', 'add_document_selection_field');

function add_document_selection_field($custom_fields) {
    $custom_fields[] = array(
        'label' => 'Document IDs',
        'type' => 'text',
        'required' => false,
        'placeholder' => 'Enter document IDs separated by commas (e.g., 123, 456, 789)'
    );

    return $custom_fields;
}

// Create Amelia service for document reviews
function create_document_review_service() {
    // This should be done via Amelia admin UI, but here's the structure:
    /*
    Service Name: Document Review Consultation
    Duration: 60 minutes
    Price: $0 (or set your price)
    Category: Legal Services
    Buffer Time Before: 15 minutes (for document preparation)
    Custom Fields:
      - Document IDs (text field)
      - Review Focus Areas (textarea)
      - Urgency Notes (textarea)
    */
}
```

### **Amelia Service Configuration (Admin UI)**

Create a service in Amelia admin:

1. **Go to:** Amelia > Services > Add Service
2. **Configure:**
   - **Name:** Document Review Consultation
   - **Duration:** 60 minutes
   - **Buffer Time Before:** 15 minutes
   - **Capacity:** 1 person
   - **Custom Fields:**
     - Document IDs (text)
     - Review Focus (textarea)
     - Special Instructions (textarea)

3. **Notifications:**
   - **To Customer:** "Your document review is scheduled for %appointment_date_time%. Please upload documents with IDs: %custom_field_1%"
   - **To Employee:** "Document review scheduled. Process documents: %custom_field_1% before appointment."

---

## 🚀 **Part 10: Deployment Options**

### **Option 1: SiteGround Hosting (Current)**

**For WordPress + Simple Processing:**

```bash
# Install required PHP packages via Composer
cd ~/public_html/wp-content/themes/your-theme
composer require smalot/pdfparser
composer require phpoffice/phpword

# Configure WP-Cron for background processing
# Add to wp-config.php:
define('DISABLE_WP_CRON', true);

# Add to cPanel cron jobs (every 5 minutes):
*/5 * * * * cd ~/public_html && php wp-cron.php
```

**Limitations:**
- No Python processing on SiteGround shared hosting
- Must use external API for Tier 2 processing
- Use webhook to call Python service on Digital Ocean

---

### **Option 2: Digital Ocean + Docker (Recommended)**

**Complete WordPress + Python Processing Stack:**

#### **Docker Compose Setup**

```yaml
# File: docker-compose.yml

version: '3.8'

services:
  # WordPress
  wordpress:
    image: wordpress:latest
    container_name: legal-wordpress
    ports:
      - "80:80"
      - "443:443"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: ${DB_PASSWORD}
      WORDPRESS_DB_NAME: legal_documents
    volumes:
      - ./wordpress:/var/www/html
      - ./uploads:/var/www/html/wp-content/uploads
    depends_on:
      - db
    restart: always

  # MySQL Database
  db:
    image: mysql:8.0
    container_name: legal-mysql
    environment:
      MYSQL_DATABASE: legal_documents
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
    volumes:
      - db_data:/var/lib/mysql
    restart: always

  # Python Processing Service
  processing-service:
    build: ./processing-service
    container_name: legal-processing
    ports:
      - "5000:5000"
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_KEY: ${SUPABASE_KEY}
    volumes:
      - ./processing-service:/app
      - ./uploads:/uploads
    restart: always

  # Redis for queue management
  redis:
    image: redis:alpine
    container_name: legal-redis
    ports:
      - "6379:6379"
    restart: always

  # Celery worker for async processing
  celery-worker:
    build: ./processing-service
    container_name: legal-celery
    command: celery -A tasks worker --loglevel=info
    environment:
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY}
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_KEY: ${SUPABASE_KEY}
    volumes:
      - ./processing-service:/app
      - ./uploads:/uploads
    depends_on:
      - redis
    restart: always

volumes:
  db_data:
  wordpress_data:
```

#### **Processing Service Dockerfile**

```dockerfile
# File: processing-service/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "app:app"]
```

#### **Python Requirements**

```txt
# File: processing-service/requirements.txt

flask==3.0.0
gunicorn==21.2.0
anthropic==0.18.0
openai==1.12.0
google-generativeai==0.4.0
supabase==2.3.4
celery==5.3.6
redis==5.0.1
pytesseract==0.3.10
pdf2image==1.17.0
Pillow==10.2.0
requests==2.31.0
python-dotenv==1.0.1
```

#### **Environment Variables**

```bash
# File: .env

# Database
DB_PASSWORD=your_secure_password
DB_ROOT_PASSWORD=your_root_password

# LLM APIs
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
GOOGLE_API_KEY=xxxxx

# Supabase
SUPABASE_URL=https://jvjlhxodmbkodzmggwpu.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# WordPress
WP_ADMIN_USER=admin
WP_ADMIN_EMAIL=admin@example.com
```

#### **Deploy to Digital Ocean**

```bash
# 1. Create Digital Ocean Droplet
# Size: $24/month (4GB RAM, 2 vCPUs) - sufficient for this workload

# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Install Docker Compose
apt-get update
apt-get install docker-compose-plugin

# 5. Clone your repository
git clone https://github.com/yourusername/legal-document-system.git
cd legal-document-system

# 6. Create .env file
nano .env
# (paste environment variables)

# 7. Start services
docker compose up -d

# 8. Install WordPress
# Visit http://your-droplet-ip and complete WordPress setup

# 9. Install plugins
# - Advanced Custom Fields Pro
# - Amelia Booking
# - WP REST API authentication

# 10. Configure DNS
# Point your domain to droplet IP
# Enable SSL with Let's Encrypt
```

---

### **Option 3: Vast.ai GPU Processing (For Heavy AI Workloads)**

Use Vast.ai for GPU-accelerated LLM inference:

```python
# File: processing-service/vast_ai_client.py

import requests

class VastAIClient:
    """
    Use Vast.ai for GPU-accelerated LLM processing
    """

    def __init__(self, api_key, instance_id):
        self.api_key = api_key
        self.instance_id = instance_id
        self.base_url = f"http://{self.get_instance_ip()}:8000"

    def get_instance_ip(self):
        """Get Vast.ai instance IP"""
        response = requests.get(
            f"https://console.vast.ai/api/v0/instances/{self.instance_id}",
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()['public_ipaddr']

    def process_with_local_llm(self, text, model="llama-3-70b"):
        """
        Process document with local LLM on Vast.ai GPU
        """
        response = requests.post(
            f"{self.base_url}/v1/completions",
            json={
                "model": model,
                "prompt": text,
                "max_tokens": 2000,
                "temperature": 0.7
            }
        )
        return response.json()

# Use for cost-effective processing
# Vast.ai: ~$0.50/hour for RTX 4090
# vs OpenAI: ~$0.03 per 1K tokens
```

**Vast.ai Setup:**

```bash
# 1. Create Vast.ai account
# 2. Rent GPU instance (RTX 4090 recommended)
# 3. Deploy vLLM or llama.cpp server
# 4. Point processing service to Vast.ai endpoint

# Docker image for Vast.ai instance:
docker run -d \
  --gpus all \
  -p 8000:8000 \
  vllm/vllm-openai:latest \
  --model meta-llama/Llama-3-70b-chat-hf \
  --tensor-parallel-size 2
```

---

### **Option 4: Paperspace (Alternative to Vast.ai)**

```python
# File: processing-service/paperspace_client.py

import gradient

class PaperspaceClient:
    """
    Use Paperspace Gradient for LLM processing
    """

    def __init__(self, api_key):
        self.client = gradient.Gradient(api_key=api_key)

    def process_document(self, text):
        deployment = self.client.get_deployment(
            deployment_id="your-deployment-id"
        )

        response = deployment.complete(
            prompt=text,
            max_tokens=2000
        )

        return response.generated_text
```

---

## 📋 **Part 11: Complete Installation Guide**

### **Quick Start: SiteGround + Digital Ocean Hybrid**

**Step 1: WordPress on SiteGround**

```bash
# 1. Install WordPress via SiteGround Site Tools
# 2. Install plugins:
#    - Advanced Custom Fields Pro
#    - Amelia Booking
#    - WP Mail SMTP (for email processing)

# 3. Upload theme files
# Copy files from /wordpress-theme/ folder to:
# ~/public_html/wp-content/themes/legal-document-theme/

# 4. Activate theme

# 5. Configure ACF forms
# Import ACF field groups from /acf-config/legal-document-fields.json
```

**Step 2: Python Service on Digital Ocean**

```bash
# 1. Create $24/month droplet (4GB RAM)

# 2. Install dependencies
apt update && apt upgrade -y
apt install -y python3-pip python3-venv tesseract-ocr

# 3. Clone processing service
git clone https://github.com/yourusername/document-processing-service.git
cd document-processing-service

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install requirements
pip install -r requirements.txt

# 6. Configure environment
nano .env
# Add API keys

# 7. Start service with systemd
sudo nano /etc/systemd/system/document-processing.service
```

**Systemd Service File:**

```ini
[Unit]
Description=Legal Document Processing Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/document-processing-service
Environment="PATH=/root/document-processing-service/venv/bin"
ExecStart=/root/document-processing-service/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
systemctl enable document-processing
systemctl start document-processing
systemctl status document-processing

# 8. Configure firewall
ufw allow 5000/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable

# 9. Setup SSL with Certbot
apt install certbot
certbot certonly --standalone -d api.yoursite.com
```

**Step 3: Connect WordPress to Processing Service**

```php
// Add to wp-config.php
define('PROCESSING_SERVICE_URL', 'https://api.yoursite.com:5000');
define('PROCESSING_SERVICE_KEY', 'your-secure-api-key');
```

**Step 4: Configure Email Processing**

```python
# Run email processor as cron job on Digital Ocean
crontab -e

# Add line:
*/5 * * * * /root/document-processing-service/venv/bin/python /root/document-processing-service/email_processor.py >> /var/log/email-processing.log 2>&1
```

---

## 🔐 **Part 12: Security Configuration**

```php
// File: wp-content/themes/your-theme/security.php

// Add API authentication
add_filter('rest_pre_dispatch', 'verify_api_key', 10, 3);

function verify_api_key($result, $server, $request) {

    // Skip auth for non-legal routes
    if (strpos($request->get_route(), '/legal/') !== 0) {
        return $result;
    }

    // Check API key
    $api_key = $request->get_header('X-API-Key');
    $valid_key = get_option('legal_api_key');

    if ($api_key !== $valid_key) {
        return new WP_Error(
            'rest_forbidden',
            'Invalid API key',
            array('status' => 403)
        );
    }

    return $result;
}

// Rate limiting
function check_rate_limit($ip_address) {
    $cache_key = 'rate_limit_' . md5($ip_address);
    $requests = get_transient($cache_key) ?: 0;

    if ($requests > 60) { // 60 requests per hour
        return false;
    }

    set_transient($cache_key, $requests + 1, HOUR_IN_SECONDS);
    return true;
}
```

---

## 📊 **Part 13: Monitoring & Analytics**

```python
# File: processing-service/monitoring.py

from utilities.context_manager import ContextManager
import time

class ProcessingMonitor:
    """
    Monitor document processing performance and costs
    """

    def __init__(self):
        self.cm = ContextManager()

    def log_processing_metrics(self, post_id, start_time, llm_results):
        """Log processing metrics to Supabase"""

        processing_time = time.time() - start_time

        total_cost = (
            llm_results['claude']['cost'] +
            llm_results['gpt4']['cost'] +
            llm_results['gemini']['cost']
        )

        total_tokens = (
            llm_results['claude']['tokens'] +
            llm_results['gpt4']['tokens'] +
            llm_results['gemini']['tokens']
        )

        # Save to processing_jobs_log
        self.cm.supabase.table('processing_jobs_log').insert({
            'job_type': 'document_processing',
            'source_id': str(post_id),
            'processing_time_seconds': processing_time,
            'total_items_processed': 1,
            'status': 'completed',
            'metadata': {
                'llm_breakdown': llm_results,
                'total_cost': total_cost,
                'total_tokens': total_tokens
            }
        }).execute()

        # Log each LLM call separately
        for llm_name, result in llm_results.items():
            self.cm.log_ai_analysis(
                analysis_type='document_processing',
                model_name=result['model'],
                source_id=str(post_id),
                source_table='wordpress_uploads',
                tokens_used=result['tokens'],
                api_cost_usd=result['cost'],
                metadata={'llm': llm_name}
            )

    def get_daily_stats(self):
        """Get daily processing statistics"""

        result = self.cm.supabase.rpc(
            'get_processing_stats',
            {'days': 1}
        ).execute()

        return result.data
```

---

## ✅ **Part 14: Testing Checklist**

### **Test Plan:**

```markdown
## WordPress Upload Form
- [ ] Upload PDF document
- [ ] Upload JPEG screenshot
- [ ] Upload Word document
- [ ] Verify ACF fields save correctly
- [ ] Check file uploaded to media library

## Tier 1 Processing
- [ ] PDF text extraction works
- [ ] Image OCR works
- [ ] Duplicate detection works
- [ ] File hash calculated correctly
- [ ] Metadata saved to post meta

## Tier 2 Processing
- [ ] WordPress calls Python service
- [ ] Claude fraud detection returns results
- [ ] GPT-4 truth scoring returns results
- [ ] Gemini legal analysis returns results
- [ ] Results aggregated correctly
- [ ] Results saved to Supabase

## Amelia Integration
- [ ] Can book document review appointment
- [ ] Custom fields appear in booking form
- [ ] Documents queued for priority processing
- [ ] Email notifications sent

## Email Integration
- [ ] Email processor detects new messages
- [ ] Attachments extracted correctly
- [ ] Files uploaded to WordPress via API
- [ ] Processing triggered automatically

## Mobile Upload
- [ ] Mobile page loads correctly
- [ ] Camera capture works
- [ ] File upload works
- [ ] Progress indicator shows
- [ ] Success message displays

## Supabase Integration
- [ ] Documents saved to legal_documents table
- [ ] Truth scores saved to truth_score_history
- [ ] AI costs logged to ai_analysis_results
- [ ] Cache working correctly
- [ ] Snapshots saving

## Security
- [ ] API key authentication works
- [ ] Rate limiting enforces limits
- [ ] Unauthorized requests blocked
- [ ] File upload restrictions enforced
```

---

## 🎉 **Summary**

### **Complete System Includes:**

1. ✅ **WordPress Upload Form** - ACF-based document intake
2. ✅ **Tier 1 Pre-Processing** - OCR, text extraction, classification
3. ✅ **Tier 2 Multi-LLM Processing** - Claude + GPT-4 + Gemini
4. ✅ **Amelia Booking** - Schedule document review appointments
5. ✅ **Email Integration** - Auto-process email attachments
6. ✅ **Mobile Upload** - Phone-friendly quick upload
7. ✅ **Supabase Storage** - All results stored in context preservation system
8. ✅ **Multiple Deployment Options** - SiteGround, Digital Ocean, Vast.ai, Paperspace
9. ✅ **Security & Authentication** - API keys, rate limiting
10. ✅ **Monitoring & Analytics** - Cost tracking, performance metrics

### **Deployment Recommendation:**

**Best Setup for Your Use Case:**
- **WordPress:** SiteGround (current hosting)
- **Python Processing:** Digital Ocean $24/month droplet
- **Heavy AI Processing:** Vast.ai GPU instance ($0.50/hour when needed)
- **Database:** Supabase (current setup)

**Estimated Monthly Costs:**
- SiteGround: $15/month (current)
- Digital Ocean: $24/month
- LLM APIs: ~$50-200/month (depending on volume)
- Vast.ai: $0-50/month (on-demand)
- **Total: ~$90-290/month**

---

**Status:** ✅ Complete WordPress Document Upload System

**Next Steps:**
1. Set up Digital Ocean droplet
2. Deploy Python processing service
3. Install WordPress plugins
4. Configure Amelia booking
5. Test end-to-end workflow
