#!/usr/bin/env python3
"""
Document Upload & Analyzer Dashboard
Upload files, get instant feedback, automatic Claude analysis, and secure storage
"""

import streamlit as st
import os
import sys
from datetime import datetime
import pandas as pd
from pathlib import Path
import hashlib
import json
import time
import base64
from io import BytesIO

try:
    from supabase import create_client
    from PIL import Image
    import anthropic
except ImportError as e:
    st.error(f"❌ Missing library: {e}")
    st.info("Install: pip3 install supabase pillow anthropic")
    st.stop()

st.set_page_config(
    page_title="Document Upload & Analyzer",
    page_icon="📤",
    layout="wide"
)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Storage configuration
UPLOAD_BASE_DIR = Path("/home/user/ASEAGI/uploads")
PROCESSED_DIR = UPLOAD_BASE_DIR / "processed"
PENDING_DIR = UPLOAD_BASE_DIR / "pending"
CHAT_HISTORY_DIR = UPLOAD_BASE_DIR / "chat_history"

# Create directories
for dir_path in [PROCESSED_DIR, PENDING_DIR, CHAT_HISTORY_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Supported file types
SUPPORTED_EXTENSIONS = {
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.heic'],
    'documents': ['.pdf', '.txt', '.rtf', '.doc', '.docx'],
    'chat': ['.txt', '.json', '.csv']
}

# ============================================================================
# SUPABASE & ANTHROPIC CONNECTION
# ============================================================================

@st.cache_resource
def init_services():
    """Initialize Supabase and Anthropic clients"""
    supabase_url = os.environ.get('SUPABASE_URL', 'https://jvjlhxodmbkodzmggwpu.supabase.co')
    supabase_key = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp2amxoeG9kbWJrb2R6bWdnd3B1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyMjMxOTAsImV4cCI6MjA3Nzc5OTE5MH0.ai65vVW816bNAV56XiuRxp5PE5IhBkMGPx3IbxfPh8c')
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY')

    try:
        supabase_client = create_client(supabase_url, supabase_key)
        anthropic_client = anthropic.Anthropic(api_key=anthropic_key) if anthropic_key else None
        return supabase_client, anthropic_client, None
    except Exception as e:
        return None, None, str(e)

# ============================================================================
# FILE HANDLING
# ============================================================================

def calculate_file_hash(file_bytes):
    """Calculate MD5 hash of file"""
    return hashlib.md5(file_bytes).hexdigest()

def check_duplicate(supabase_client, file_hash):
    """Check if file already processed"""
    try:
        result = supabase_client.table('legal_documents')\
            .select('id, document_title, processed_at')\
            .eq('content_hash', file_hash)\
            .execute()
        return result.data[0] if result.data else None
    except:
        return None

def save_file_locally(uploaded_file, directory):
    """Save uploaded file to local storage"""
    try:
        file_path = directory / uploaded_file.name
        file_path.write_bytes(uploaded_file.getvalue())
        return file_path, None
    except Exception as e:
        return None, str(e)

def image_to_base64(image_bytes):
    """Convert image bytes to base64 for Claude"""
    try:
        img = Image.open(BytesIO(image_bytes))

        # Resize if too large
        max_size = 1568
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        buffered = BytesIO()
        img.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        st.error(f"Image conversion error: {e}")
        return None

# ============================================================================
# CLAUDE ANALYSIS
# ============================================================================

def analyze_with_claude(anthropic_client, file_content, file_name, file_type):
    """Analyze document with Claude using PROJ344 scoring"""

    system_prompt = """You are a legal document intelligence analyst using PROJ344 scoring methodology.

Analyze and return ONLY JSON with PROJ344 scores:

{
  "document_type": "TEXT|TRNS|CPSR|MEDR|FORN|PLCR|ORDR|DECL|EXPA|MOTN|RESP|EVID|OTHER",
  "document_date": "YYYY-MM-DD or null",
  "document_title": "Brief descriptive title",
  "executive_summary": "2-3 sentence summary",

  "micro_number": 0-999,
  "macro_number": 0-999,
  "legal_number": 0-999,
  "category_number": 0-999,
  "relevancy_number": 0-999,

  "key_quotes": ["quote1", "quote2"],
  "smoking_guns": ["critical fact"],
  "parties": ["MOT", "FAT", "MIN"],
  "keywords": ["keyword1", "keyword2"],

  "status": "RECEIVED|UNDER_REVIEW|ANALYZED",
  "purpose": "EVIDENCE|MOTION|DISCOVERY",
  "importance": "CRITICAL|HIGH|MEDIUM|LOW",

  "contains_false_statements": false,
  "fraud_indicators": [],
  "perjury_indicators": [],

  "w388_relevance": 0-100,
  "ccp473_relevance": 0-100,
  "criminal_relevance": 0-100
}

SCORING: 900-999=CRITICAL, 800-899=IMPORTANT, 700-799=SIGNIFICANT"""

    try:
        # Prepare message based on file type
        if file_type == 'image':
            img_base64 = image_to_base64(file_content)
            if not img_base64:
                return None, "Image conversion failed"

            messages = [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": img_base64}},
                    {"type": "text", "text": f"Analyze this legal document image: {file_name}"}
                ]
            }]
        elif file_type == 'text':
            text_content = file_content.decode('utf-8', errors='ignore')[:50000]
            messages = [{
                "role": "user",
                "content": f"Analyze this legal document:\n\nFilename: {file_name}\n\n{text_content}"
            }]
        else:
            return None, f"Unsupported file type: {file_type}"

        # Call Claude API
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            temperature=0.1,
            system=system_prompt,
            messages=messages
        )

        response_text = response.content[0].text.strip()

        # Clean JSON if wrapped in code blocks
        if response_text.startswith('```'):
            response_text = response_text.split('\n', 1)[1].rsplit('```', 1)[0].strip()

        analysis = json.loads(response_text)

        # Calculate API cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        api_cost = (input_tokens / 1_000_000 * 3) + (output_tokens / 1_000_000 * 15)

        analysis['api_cost_usd'] = api_cost
        analysis['processed_by'] = 'claude-sonnet-4.5'
        analysis['input_tokens'] = input_tokens
        analysis['output_tokens'] = output_tokens

        return analysis, None

    except Exception as e:
        return None, str(e)

def upload_to_supabase(supabase_client, file_info, analysis):
    """Upload document analysis to Supabase"""
    try:
        document_data = {
            'original_filename': file_info['name'],
            'file_path': str(file_info['path']),
            'file_extension': file_info['extension'],
            'file_size_bytes': file_info['size'],
            'content_hash': file_info['hash'],

            # PROJ344 Scores
            'micro_number': analysis.get('micro_number', 0),
            'macro_number': analysis.get('macro_number', 0),
            'legal_number': analysis.get('legal_number', 0),
            'category_number': analysis.get('category_number', 0),
            'relevancy_number': analysis.get('relevancy_number', 0),

            # Document Info
            'document_type': analysis.get('document_type'),
            'document_title': analysis.get('document_title'),
            'document_date': analysis.get('document_date'),
            'executive_summary': analysis.get('executive_summary'),

            # Arrays
            'key_quotes': analysis.get('key_quotes', []),
            'smoking_guns': analysis.get('smoking_guns', []),
            'parties': analysis.get('parties', []),
            'keywords': analysis.get('keywords', []),

            # Status
            'status': analysis.get('status', 'RECEIVED'),
            'purpose': analysis.get('purpose'),
            'importance': analysis.get('importance', 'MEDIUM'),

            # Legal Relevance
            'w388_relevance': analysis.get('w388_relevance', 0),
            'ccp473_relevance': analysis.get('ccp473_relevance', 0),
            'criminal_relevance': analysis.get('criminal_relevance', 0),

            # Fraud/Perjury
            'contains_false_statements': analysis.get('contains_false_statements', False),
            'fraud_indicators': analysis.get('fraud_indicators', []),
            'perjury_indicators': analysis.get('perjury_indicators', []),

            # Processing Info
            'processed_at': datetime.now().isoformat(),
            'processed_by': analysis.get('processed_by'),
            'api_cost_usd': analysis.get('api_cost_usd', 0.0),

            # Case Info
            'case_id': 'ashe-bucknor-j24-00478',
            'case_number': 'J24-00478'
        }

        result = supabase_client.table('legal_documents').insert(document_data).execute()
        return result.data[0] if result.data else None, None

    except Exception as e:
        return None, str(e)

# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.title("📤 Document Upload & Analyzer")
    st.markdown(f"**Upload documents for automatic analysis** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize services
    supabase_client, anthropic_client, error = init_services()

    if error:
        st.error(f"❌ Service initialization failed: {error}")
        st.info("Set environment variables: SUPABASE_URL, SUPABASE_KEY, ANTHROPIC_API_KEY")
        st.stop()

    if not anthropic_client:
        st.warning("⚠️ Claude API not configured. Analysis will be disabled.")
        st.info("Set ANTHROPIC_API_KEY environment variable to enable analysis")

    st.success("✅ Connected to Supabase" + (" and Claude API" if anthropic_client else ""))
    st.markdown("---")

    # Sidebar: Upload mode selection
    st.sidebar.header("📋 Upload Mode")
    mode = st.sidebar.radio(
        "Select Upload Type",
        ["📄 Legal Documents", "💬 Chat History", "📊 Batch Upload", "📈 Upload Status"]
    )

    # ========================================================================
    # MODE: LEGAL DOCUMENTS
    # ========================================================================
    if mode == "📄 Legal Documents":
        st.header("📄 Upload Legal Documents")
        st.info("Supported: Images (JPG, PNG), PDFs, Text files (TXT, RTF)")

        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=['jpg', 'jpeg', 'png', 'gif', 'webp', 'pdf', 'txt', 'rtf']
        )

        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) selected")

            # Options
            col1, col2 = st.columns(2)
            with col1:
                auto_analyze = st.checkbox("Auto-analyze with Claude", value=True, disabled=not anthropic_client)
            with col2:
                skip_duplicates = st.checkbox("Skip duplicate files", value=True)

            if st.button("🚀 Upload & Process", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                results_container = st.container()

                results = []

                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {idx+1}/{len(uploaded_files)}: {uploaded_file.name}")
                    progress_bar.progress((idx + 1) / len(uploaded_files))

                    with results_container:
                        with st.expander(f"📄 {uploaded_file.name}", expanded=True):
                            result = {'filename': uploaded_file.name, 'status': 'processing'}

                            # Calculate hash
                            file_bytes = uploaded_file.getvalue()
                            file_hash = calculate_file_hash(file_bytes)
                            file_extension = Path(uploaded_file.name).suffix.lower()

                            st.write(f"**File:** {uploaded_file.name}")
                            st.write(f"**Size:** {len(file_bytes) / 1024:.1f} KB")
                            st.write(f"**Hash:** {file_hash[:16]}...")

                            # Check for duplicates
                            if skip_duplicates:
                                duplicate = check_duplicate(supabase_client, file_hash)
                                if duplicate:
                                    st.warning(f"⏭️ **Already processed!**")
                                    st.write(f"Existing: {duplicate.get('document_title')}")
                                    st.write(f"Processed: {duplicate.get('processed_at', 'N/A')[:10]}")
                                    result['status'] = 'duplicate'
                                    results.append(result)
                                    continue

                            # Save file locally
                            st.write("💾 Saving to local storage...")
                            file_path, save_error = save_file_locally(uploaded_file, PENDING_DIR)

                            if save_error:
                                st.error(f"❌ Save failed: {save_error}")
                                result['status'] = 'save_failed'
                                result['error'] = save_error
                                results.append(result)
                                continue

                            st.success(f"✅ Saved to: {file_path}")

                            # Analyze with Claude
                            if auto_analyze and anthropic_client:
                                st.write("🤖 Analyzing with Claude AI...")

                                # Determine file type
                                if file_extension in SUPPORTED_EXTENSIONS['images']:
                                    file_type = 'image'
                                elif file_extension in ['.txt', '.rtf']:
                                    file_type = 'text'
                                else:
                                    st.warning(f"⚠️ Analysis not supported for {file_extension}")
                                    result['status'] = 'unsupported'
                                    results.append(result)
                                    continue

                                analysis, analysis_error = analyze_with_claude(
                                    anthropic_client,
                                    file_bytes,
                                    uploaded_file.name,
                                    file_type
                                )

                                if analysis_error:
                                    st.error(f"❌ Analysis failed: {analysis_error}")
                                    result['status'] = 'analysis_failed'
                                    result['error'] = analysis_error
                                    results.append(result)
                                    continue

                                # Display analysis
                                st.success(f"✅ Analysis complete!")

                                col1, col2, col3 = st.columns(3)
                                col1.metric("Relevancy", f"{analysis['relevancy_number']}/999")
                                col2.metric("Legal", f"{analysis['legal_number']}/999")
                                col3.metric("API Cost", f"${analysis['api_cost_usd']:.4f}")

                                st.write(f"**Title:** {analysis.get('document_title')}")
                                st.write(f"**Type:** {analysis.get('document_type')}")
                                st.info(f"**Summary:** {analysis.get('executive_summary')}")

                                if analysis.get('smoking_guns'):
                                    st.error(f"🔥 **Smoking Guns:** {len(analysis['smoking_guns'])}")
                                    for sg in analysis['smoking_guns']:
                                        st.write(f"- {sg}")

                                # Upload to Supabase
                                st.write("☁️ Uploading to database...")

                                file_info = {
                                    'name': uploaded_file.name,
                                    'path': file_path,
                                    'extension': file_extension,
                                    'size': len(file_bytes),
                                    'hash': file_hash
                                }

                                db_result, db_error = upload_to_supabase(supabase_client, file_info, analysis)

                                if db_error:
                                    st.error(f"❌ Database upload failed: {db_error}")
                                    result['status'] = 'db_failed'
                                    result['error'] = db_error
                                else:
                                    st.success(f"✅ Uploaded to database! (ID: {db_result['id'][:8]}...)")

                                    # Move to processed directory
                                    processed_path = PROCESSED_DIR / uploaded_file.name
                                    file_path.rename(processed_path)

                                    result['status'] = 'success'
                                    result['analysis'] = analysis
                                    result['db_id'] = db_result['id']
                            else:
                                st.info("ℹ️ Auto-analysis disabled")
                                result['status'] = 'uploaded_only'

                            results.append(result)
                            time.sleep(0.5)  # Rate limiting

                # Summary
                status_text.text("✅ Processing complete!")
                progress_bar.progress(1.0)

                st.markdown("---")
                st.header("📊 Upload Summary")

                success_count = len([r for r in results if r['status'] == 'success'])
                duplicate_count = len([r for r in results if r['status'] == 'duplicate'])
                failed_count = len([r for r in results if r['status'] not in ['success', 'duplicate']])

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Files", len(uploaded_files))
                col2.metric("✅ Success", success_count)
                col3.metric("⏭️ Duplicates", duplicate_count)
                col4.metric("❌ Failed", failed_count)

                if success_count > 0:
                    total_cost = sum(r.get('analysis', {}).get('api_cost_usd', 0) for r in results if 'analysis' in r)
                    st.metric("💰 Total API Cost", f"${total_cost:.4f}")

    # ========================================================================
    # MODE: CHAT HISTORY
    # ========================================================================
    elif mode == "💬 Chat History":
        st.header("💬 Upload Chat History")
        st.info("Upload chat logs for analysis (TXT, JSON, CSV)")

        chat_file = st.file_uploader(
            "Choose chat history file",
            type=['txt', 'json', 'csv']
        )

        if chat_file:
            st.success(f"✅ File selected: {chat_file.name}")

            if st.button("📤 Upload & Analyze", type="primary"):
                with st.spinner("Processing chat history..."):
                    # Save file
                    file_path, error = save_file_locally(chat_file, CHAT_HISTORY_DIR)

                    if error:
                        st.error(f"❌ Upload failed: {error}")
                    else:
                        st.success(f"✅ Saved to: {file_path}")

                        # Read and display preview
                        content = chat_file.getvalue().decode('utf-8', errors='ignore')

                        st.write("**File Preview:**")
                        st.text_area("Content", content[:2000], height=300)

                        st.info("💡 Chat history analyzer coming soon! File saved for manual review.")

    # ========================================================================
    # MODE: BATCH UPLOAD
    # ========================================================================
    elif mode == "📊 Batch Upload":
        st.header("📊 Batch Upload Status")
        st.info("Monitor batch upload operations and system status")

        # Count files in directories
        pending_files = list(PENDING_DIR.glob("*"))
        processed_files = list(PROCESSED_DIR.glob("*"))
        chat_files = list(CHAT_HISTORY_DIR.glob("*"))

        col1, col2, col3 = st.columns(3)
        col1.metric("Pending Files", len(pending_files))
        col2.metric("Processed Files", len(processed_files))
        col3.metric("Chat History Files", len(chat_files))

        st.markdown("---")

        # Show pending files
        if pending_files:
            st.subheader("⏳ Pending Files")
            for file in pending_files[:10]:
                st.write(f"📄 {file.name} ({file.stat().st_size / 1024:.1f} KB)")

        # Show processed files
        if processed_files:
            st.subheader("✅ Recently Processed")
            for file in sorted(processed_files, key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
                mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                st.write(f"📄 {file.name} - {mod_time.strftime('%Y-%m-%d %H:%M')}")

    # ========================================================================
    # MODE: UPLOAD STATUS
    # ========================================================================
    elif mode == "📈 Upload Status":
        st.header("📈 System Status")

        # Database stats
        try:
            result = supabase_client.table('legal_documents')\
                .select('id, processed_at, relevancy_number, api_cost_usd')\
                .order('processed_at', desc=True)\
                .limit(100)\
                .execute()

            docs = result.data

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Documents", len(docs))
            col2.metric("Avg Relevancy", f"{sum(d['relevancy_number'] for d in docs) / len(docs):.0f}" if docs else "0")
            col3.metric("Total API Cost", f"${sum(d.get('api_cost_usd', 0) for d in docs):.2f}")

            # Recent uploads
            st.subheader("📋 Recent Uploads (Last 20)")
            recent_docs = []
            for doc in docs[:20]:
                recent_docs.append({
                    'ID': doc['id'][:8] + '...',
                    'Relevancy': doc['relevancy_number'],
                    'Processed': doc.get('processed_at', 'N/A')[:19],
                    'Cost': f"${doc.get('api_cost_usd', 0):.4f}"
                })

            st.dataframe(pd.DataFrame(recent_docs), use_container_width=True, hide_index=True)

        except Exception as e:
            st.error(f"Error fetching stats: {e}")

    # Footer
    st.markdown("---")
    st.caption(f"🔐 Secure storage: {UPLOAD_BASE_DIR} | Database: Supabase | Analysis: Claude Sonnet 4.5")

if __name__ == "__main__":
    main()
